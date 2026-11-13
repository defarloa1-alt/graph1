"""The queue of predicates the lens specialists ask for, each with its precedents (39 §7).

    python -m GraphRevised.proposals.predicate_needs collect GraphRevised/runs/lens-reader-*.jsonl [...]
    python -m GraphRevised.proposals.predicate_needs list

A lens reading (proposals/passage_reader.py --lens) or a lens analysis (discovery/lens_analyst.py)
reports relationships the registry lacks. `collect` merges them into curation/predicate-needs.json:
one request per name, with every specialist that asked, every quotation that shows it, and the
precedents found for it, so the curator reviews a request with its evidence already at hand:

    registry   predicates already in the active registry that may cover it
    legacy     rows of the February 2026 relationship registry (../Relationships/), with their
               Wikidata property, direction, reification hint, and CIDOC CRM code
    cidoc      CIDOC CRM properties from the legacy mapping (../CIDOC/)

Precedents are matched by the words of the name and the definition, not the name alone: one
specialist's `wentOverTo` is another's `defectedTo`. A precedent is a lead, never a decision, and
legacy Wikidata ids are checked at Wikidata before any use. Requests with the same name merge;
similar requests are listed beside each other, never merged silently.

The reader shows the open requests to each lens reading, so a specialist reuses a name that fits.
Nothing here writes the graph or the registry.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from .registry import PredicateRegistry, load_registry

GRAPH_REVISED = Path(__file__).resolve().parents[1]
NEEDS_PATH = GRAPH_REVISED / "curation" / "predicate-needs.json"
LEGACY_RELATIONSHIPS = GRAPH_REVISED.parent / "Relationships" / "relationship_types_registry_master.csv"
LEGACY_WIKIDATA_CANDIDATES = GRAPH_REVISED.parent / "Relationships" / "wikidata_p_catalog_candidates_2026-02-13.csv"
LEGACY_CIDOC = GRAPH_REVISED.parent / "CIDOC" / "cidoc_wikidata_mapping_validated.csv"

STOP = frozenset("""a an and as at be by for from in into is it its of on or other than that the their
them this to was with who whom which one ones another some any person people entity thing over went
made took gave has had have been being upon""".split())
MIN_SCORE = 0.5  # weighted shared words over the shorter text, with the name bonuses
NAME_BONUS = 0.3  # the two names share a word
NAMED_IN_BONUS = 0.15  # the other's name words all appear in the need's name or definition
FLOOR_WORDS = 3  # a text shorter than this many average words is scored as if it had them
SIMILAR_SCORE = 0.4  # lower for "see also" between requests: listed, never merged
LIMIT = 3  # precedents kept per source


def words(*texts: str | None) -> frozenset[str]:
    """Content words, roughly stemmed, from camelCase names, SNAKE_NAMES, and prose."""
    found: set[str] = set()
    for text in texts:
        if not text:
            continue
        spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text).replace("_", " ")
        for word in re.findall(r"[a-z]+", spaced.lower()):
            if word in STOP or len(word) < 3:
                continue
            for suffix in ("ation", "ing", "ion", "ed", "es", "s"):
                if word.endswith(suffix) and len(word) - len(suffix) >= 4:
                    word = word[: -len(suffix)]
                    break
            found.add(word)
    return frozenset(found)


@lru_cache(maxsize=None)
def rarity() -> dict[str, float]:
    """How rare each word is across the precedent texts (inverse document frequency): a shared
    rare word (defect) says more than a shared common one (enemy, command)."""
    texts = [all_words for (_, all_words), _ in (*legacy_relationships(), *cidoc_properties())]
    texts += [words(d.id, d.display, d.definition) for d in load_registry().predicates.values()]
    counts: dict[str, int] = {}
    for text in texts:
        for word in text:
            counts[word] = counts.get(word, 0) + 1
    total = len(texts) or 1
    return {word: math.log((total + 1) / (count + 1)) + 1 for word, count in counts.items()}


def _weight(text: frozenset[str], weights: dict[str, float], unseen: float) -> float:
    return sum(weights.get(word, unseen) for word in text)


def score(need: tuple[frozenset[str], frozenset[str]], other: tuple[frozenset[str], frozenset[str]]) -> float:
    """Rarity-weighted shared words over the shorter text (never shorter than FLOOR_WORDS), plus
    a bonus when the names share a word, or the other's name is in the need's own words."""
    (need_name, need_all), (other_name, other_all) = need, other
    weights = rarity()
    unseen = max(weights.values(), default=1.0)
    average = sum(weights.values()) / len(weights) if weights else 1.0
    shorter = max(min(_weight(need_all, weights, unseen), _weight(other_all, weights, unseen)), FLOOR_WORDS * average)
    shared = _weight(need_all & other_all, weights, unseen) / shorter
    if need_name & other_name:
        shared += NAME_BONUS
    elif other_name and other_name <= need_all:
        shared += NAMED_IN_BONUS
    return min(1.0, shared)


def terms(name: str, *texts: str | None) -> tuple[frozenset[str], frozenset[str]]:
    """The words of a name, and of the name with its texts."""
    return words(name), words(name, *texts)


def _ranked(need: tuple[frozenset[str], frozenset[str]],
            rows: Iterable[tuple[tuple[frozenset[str], frozenset[str]], dict[str, Any]]]) -> list[dict[str, Any]]:
    scored = [(score(need, row_terms), row) for row_terms, row in rows]
    kept = sorted((pair for pair in scored if pair[0] >= MIN_SCORE), key=lambda pair: -pair[0])[:LIMIT]
    return [{**row, "score": round(value, 2)} for value, row in kept]


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


@lru_cache(maxsize=None)
def legacy_relationships(path: Path = LEGACY_RELATIONSHIPS,
                         candidates_path: Path = LEGACY_WIKIDATA_CANDIDATES) -> tuple[tuple[tuple[frozenset[str], frozenset[str]], dict], ...]:
    """Legacy rows that carry a description, with the only Wikidata suggestions worth showing:
    curated properties on the row, or catalogue suggestions above low confidence."""
    suggested: dict[str, list[str]] = {}
    for row in _read_csv(candidates_path):
        if row.get("confidence") != "low" and row.get("suggested_wikidata_property"):
            suggested.setdefault(row["relationship_type"], []).append(
                f"{row['suggested_wikidata_property']} ({row['suggested_wikidata_label']}, "
                f"{row['confidence']} confidence, unreviewed)")
    rows = []
    for row in _read_csv(path):
        name, description = row.get("relationship_type", ""), row.get("description", "")
        if not name or not description:
            continue
        wikidata = row.get("wikidata_property") or ""
        rows.append((terms(name, description), {
            "name": name, "description": description, "category": row.get("category") or None,
            "direction": row.get("directionality") or None,
            "wikidata": f"{wikidata} ({row['wikidata_label']})" if wikidata and row.get("wikidata_label") else wikidata or None,
            "wikidataSuggested": suggested.get(name) or None,
            "reifyAs": row.get("reify_as") or None, "cidoc": row.get("cidoc_crm_code") or None,
            "status": row.get("lifecycle_status") or None,
        }))
    return tuple(rows)


@lru_cache(maxsize=None)
def cidoc_properties(path: Path = LEGACY_CIDOC) -> tuple[tuple[tuple[frozenset[str], frozenset[str]], dict], ...]:
    """The CRM properties (P...) and classes (E..., I...) of the legacy mapping, with its Wikidata counterpart."""
    rows = []
    for row in _read_csv(path):
        code = row.get("cidoc_class", "")
        if not code:
            continue
        label = re.sub(r"^[A-Z]+\d+i?_", "", code).replace("_", " ")
        rows.append((terms(label, row.get("notes")), {
            "code": code, "wikidata": row.get("wikidata_property") or row.get("wikidata_qid") or None,
            "mapping": row.get("mapping_type") or None, "note": row.get("notes") or None,
        }))
    return tuple(rows)


def precedents(need: dict[str, Any], registry: PredicateRegistry) -> dict[str, list[dict[str, Any]]]:
    """Leads for one requested predicate: what already exists that may cover it, or show how to map it."""
    need_words = terms(need["name"], need.get("definition"))
    active = ((terms(d.id, d.display, d.definition), {"id": d.id, "display": d.display,
                                                      "subjectKinds": sorted(d.subject_kinds),
                                                      "objectKinds": sorted(d.object_kinds)})
              for d in registry.predicates.values())
    return {
        "registry": _ranked(need_words, active),
        "legacy": _ranked(need_words, legacy_relationships()),
        "cidoc": _ranked(need_words, cidoc_properties()),
    }


def needs_from_run(path: Path) -> list[dict[str, Any]]:
    """Predicate needs from a lens reading's run log (JSONL) or a lens analysis (JSON), as one shape:
    name, definition, subjectKinds, objectKinds, specialist, evidence."""
    text = path.read_text(encoding="utf-8")
    found: list[dict[str, Any]] = []
    if path.suffix == ".jsonl":
        lines = [json.loads(line) for line in text.splitlines() if line.strip()]
        lenses = [line["lens"] for line in lines if line.get("lens")]
        specialist = lenses[0]["specialist"] if lenses else None
        for line in lines:
            for need in line.get("predicateNeeds") or []:
                found.append({"name": need["name"], "definition": need["definition"],
                              "subjectKinds": need.get("subject_kinds", []), "objectKinds": need.get("object_kinds", []),
                              "specialist": specialist,
                              "evidence": {"observationId": need.get("observationId"), "quotation": need["quotation"],
                                           "ref": line.get("ref"), "run": path.name}})
        return found
    data = json.loads(text)
    scope = (data.get("polity") or "unknown").lower().replace(" ", "-")
    readings = [(lens, reading) for lens, reading in (data.get("readings") or {}).items()]
    if data.get("general"):
        readings.append(("general", data["general"]))
    for lens, reading in readings:
        for need in reading.get("predicate_needs") or []:
            found.append({"name": need["name"], "definition": need["definition"],
                          "subjectKinds": need.get("subject_kinds", []), "objectKinds": need.get("object_kinds", []),
                          "specialist": f"lens-analyst:{lens}/{scope}",
                          "evidence": {"example": need.get("example"), "run": path.name}})
    return found


def load_queue(path: Path = NEEDS_PATH) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"description": "Predicates the lens specialists ask for, with precedents (proposals/predicate_needs.py; "
                           "39 §7). A request is a lead for the curator, never a registry change.",
            "version": 1, "requests": []}


def merge(queue: dict[str, Any], found: list[dict[str, Any]], registry: PredicateRegistry,
          now: str | None = None) -> dict[str, int]:
    """Merge needs into the queue: same name, one request; precedents and similar requests refreshed."""
    now = now or datetime.now(timezone.utc).isoformat(timespec="seconds")
    by_name = {request["name"]: request for request in queue["requests"]}
    counts = {"new": 0, "merged": 0, "known": 0}
    for need in found:
        if need["name"] in registry.predicates:
            counts["known"] += 1
            continue
        request = by_name.get(need["name"])
        if request is None:
            request = {"name": need["name"], "status": "open", "definitions": [], "subjectKinds": [],
                       "objectKinds": [], "requestedBy": [], "evidence": [], "firstRequested": now}
            queue["requests"].append(request)
            by_name[need["name"]] = request
            counts["new"] += 1
        else:
            counts["merged"] += 1
        if need["definition"] not in request["definitions"]:
            request["definitions"].append(need["definition"])
        for key in ("subjectKinds", "objectKinds"):
            request[key] = sorted(set(request[key]) | set(need[key]))
        if need["specialist"] and need["specialist"] not in request["requestedBy"]:
            request["requestedBy"].append(need["specialist"])
        if need["evidence"] not in request["evidence"]:
            request["evidence"].append(need["evidence"])
        request["lastRequested"] = now
    for request in queue["requests"]:
        if request["status"] != "open":
            continue
        need = {"name": request["name"], "definition": " ".join(request["definitions"])}
        request["precedents"] = precedents(need, registry)
        mine = terms(need["name"], need["definition"])
        request["similarRequests"] = [
            other["name"] for other in queue["requests"]
            if other is not request and other["status"] == "open"
            and score(mine, terms(other["name"], " ".join(other["definitions"]))) >= SIMILAR_SCORE
        ]
    queue["requests"].sort(key=lambda request: (-len(request["requestedBy"]), request["name"]))
    return counts


SHAPES = ("event", "state", "quantity", "qualifier")  # D-138: what a request becomes


def set_shape(queue: dict[str, Any], name: str, shape: str, basis: str, by: str) -> dict[str, Any]:
    """Classify a request under D-138: an act becomes a depicted event, a state a predicate, a number
    a quantity on a claim, a bound (an end of office) a qualifier. Recorded with who and why."""
    if shape not in SHAPES:
        raise ValueError(f"a shape is one of {', '.join(SHAPES)}, not {shape!r}")
    request = next((r for r in queue["requests"] if r["name"] == name), None)
    if request is None:
        raise ValueError(f"no request named {name!r}")
    request["shape"] = {"value": shape, "basis": basis, "by": by,
                        "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    return request


def _shape(request: dict[str, Any]) -> str | None:
    return (request.get("shape") or {}).get("value")


def open_requests_text(queue: dict[str, Any]) -> str:
    """What the reader shows a lens reading: the open state requests, to reuse a name that fits, and
    the acts already ruled events (D-138), to depict rather than request."""
    open_requests = [request for request in queue["requests"] if request["status"] == "open"]
    states = [f"- {r['name']}: {r['definitions'][0]}" for r in open_requests if _shape(r) in (None, "state")]
    acts = [r["name"] for r in open_requests if _shape(r) == "event"]
    parts = []
    if states:
        parts.append("Predicates already requested and awaiting the registry (under predicate_needs, reuse one "
                     "of these names when it fits rather than coining another):\n" + "\n".join(states))
    if acts:
        parts.append("Acts ruled events, never predicates (depict them; do not request them): "
                     + ", ".join(acts) + ".")
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    collect = commands.add_parser("collect", help="merge the needs of run logs into the queue")
    collect.add_argument("runs", nargs="+", type=Path)
    commands.add_parser("list", help="the open requests, most requested first")
    shape = commands.add_parser("shape", help="classify a request under D-138")
    shape.add_argument("name")
    shape.add_argument("shape", choices=SHAPES)
    shape.add_argument("--basis", required=True, help="why, in one sentence")
    shape.add_argument("--by", default="curator")
    args = parser.parse_args(argv)
    queue = load_queue()
    if args.command == "shape":
        set_shape(queue, args.name, args.shape, args.basis, args.by)
        NEEDS_PATH.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.command == "collect":
        found = [need for run in args.runs for need in needs_from_run(run)]
        counts = merge(queue, found, load_registry())
        NEEDS_PATH.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{len(found)} need(s) from {len(args.runs)} run(s): {json.dumps(counts)}")
    for request in queue["requests"]:
        if request["status"] != "open":
            continue
        p = request.get("precedents", {})
        leads = [f"registry {', '.join(x['id'] for x in p.get('registry', []))}" if p.get("registry") else "",
                 f"legacy {', '.join(x['name'] for x in p.get('legacy', []))}" if p.get("legacy") else "",
                 f"CIDOC {', '.join(x['code'] for x in p.get('cidoc', []))}" if p.get("cidoc") else ""]
        similar = f"; similar: {', '.join(request['similarRequests'])}" if request.get("similarRequests") else ""
        similar += f"; shape: {_shape(request) or 'unclassified'}"
        sys.stdout.write(f"{request['name']} x{len(request['requestedBy'])}: {request['definitions'][0][:70]}\n"
                         f"    {'; '.join(x for x in leads if x) or 'no precedent'}{similar}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
