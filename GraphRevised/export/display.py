"""Display rules for the exploration projection: what a view shows, decided once for every view.

The rules mark lines and entities; they never remove them. Every fact stays in the projection with
its voices, because the fact layer (export/fact_layer.py), the coverage report and the audit read
the same projection. A view hides a line with a `fold` reason, and says how many it folded
(display only, never stored as a claim: D-039). From "Explorer Fixes on the Stage Design" (2026-11-18):

1. A part reached through a part: when A is part of B and B is part of C, the line "A part of C"
   folds into the route through B ("via-part"). The battle's moments then sit in its phases
   instead of 162 lines on the battle itself.
2. Kind of statement: each entity counts its lines by category, and an entity whose every line
   is imaginative is marked `imaginedOnly`, so a view with fiction off hides it as well.
3. Same name, different thing: two entities with one name get a short `hint` to tell them apart.
3b. "Distinct from" beside "part of": when a pair has both, the part-of line already says they
   differ, so distinctFrom folds ("part-says-distinct").
5a. Reference works: describedBy lines to tertiary Works fold into a count, "Also in 5 reference
   works" ("reference-work"). Each Work carries its standing, as ancient, modern or reference.
5b. A description that is only a web address is not shown.
6. Subject access (curator, 2026-11-19): an entity with no library heading of its own (LCSH, LCNAF,
   FAST) is reached through the nearest whole it is part of that has one: a moment of a battle
   shows the battle's own heading via the battle. Derived here, never stored on the moment, so
   it follows the part-of chain if a moment moves. Imagined parts inherit nothing.
7. Elsewhere (2026-11-20, D-168): where an entity sits in each outside network, grouped and ordered
   by the federation profile (curation/authorities.json "networks"). Each record keeps its code
   beside its label and a link to open it, and says how it is held: a proposed link as proposed,
   an identity as a close match, a gazetteer location as its location, and a crosswalk as checked
   at the system itself or as stated by the payload it was read from (by the hosts the profile
   lists). A network the profile expects for the entity's kind, with no record, says "none held".
8. Kinds of evidence (2026-11-20): which kinds of evidence each fact rests on, read from the forms
   and standing of the Works its voices cite: ancient texts, coins, inscriptions. Modern studies,
   reference works and imaginative works (any creative form, rule 11) are listed beside them but
   are not a kind of their own (D-148; 42 §4). Interim: 41 §3.3 wants the kind on the evidence
   itself, where coin catalogue records are still `observationKind: record` like any catalogue record.
"""

from __future__ import annotations

import re
from typing import Any

LIVE_LINES = ("accepted", "proposed")

FOLD_VIA_PART = "via-part"
FOLD_PART_SAYS_DISTINCT = "part-says-distinct"
FOLD_REFERENCE = "reference-work"

# Work.standing in the graph, in the words a reader sees.
STANDING_WORDS = {"primary": "ancient", "secondary": "modern", "tertiary": "reference"}

KIND_WORDS = {"Person": "person", "Event": "event", "Place": "place", "Group": "group", "Office": "office",
              "Work": "work", "Concept": "idea", "Period": "period", "Polity": "state", "Type": "type",
              "Question": "question", "Position": "position"}

ONLY_A_LINK = re.compile(r"\s*https?://\S+\s*")
YEAR = re.compile(r"\b(\d{1,4})\s*(BCE|BC|CE|AD)\b")
HINT_WORDS = 8


def _live(edge: dict[str, Any]) -> bool:
    return edge["status"] in LIVE_LINES


def fold_parts_through_parts(edges: list[dict[str, Any]]) -> None:
    """Rule 1: fold "A partOf C" when a live route A partOf B partOf C exists."""
    parts = [e for e in edges if e["predicate"] == "partOf" and _live(e)]
    wholes: dict[str, set[str]] = {}
    for edge in parts:
        wholes.setdefault(edge["source"], set()).add(edge["target"])
    for edge in parts:
        via = sorted(b for b in wholes.get(edge["source"], ())
                     if b != edge["target"] and edge["target"] in wholes.get(b, ()))
        if via:
            edge["fold"], edge["foldVia"] = FOLD_VIA_PART, via[0]


def fold_distinct_beside_part(edges: list[dict[str, Any]]) -> None:
    """Rule 3b: a pair joined by partOf needs no distinctFrom line as well."""
    pairs = {frozenset((e["source"], e["target"])) for e in edges if e["predicate"] == "partOf" and _live(e)}
    for edge in edges:
        if edge["predicate"] == "distinctFrom" and frozenset((edge["source"], edge["target"])) in pairs:
            edge["fold"] = FOLD_PART_SAYS_DISTINCT


def fold_reference_works(edges: list[dict[str, Any]], nodes: dict[str, dict[str, Any]]) -> None:
    """Rule 5a: describedBy lines to reference (tertiary) Works become a count on the entity."""
    for edge in edges:
        if edge["predicate"] == "describedBy" and nodes[edge["target"]].get("standing") == "tertiary":
            edge["fold"] = FOLD_REFERENCE
            entity = nodes[edge["source"]]
            entity["referenceWorks"] = entity.get("referenceWorks", 0) + 1


def count_lines(edges: list[dict[str, Any]], nodes: dict[str, dict[str, Any]]) -> None:
    """Rule 2: each entity's live lines by category; imaginedOnly when fiction is all there is."""
    for edge in edges:
        if not _live(edge):
            continue
        for end in {edge["source"], edge["target"]}:
            lines = nodes[end].setdefault("lines", {})
            lines[edge["category"]] = lines.get(edge["category"], 0) + 1
    for data in nodes.values():
        lines = data.get("lines") or {}
        data["imaginedOnly"] = bool(lines) and set(lines) == {"imaginative"}


DATED_FIRST = {"Event", "Period"}  # a battle is told apart by when; a person by who they were


def _year(data: dict[str, Any]) -> str | None:
    """The first dated time on the entity's own facts, with its verb ("born 77 BCE"); a span is too vague."""
    for fact in data.get("facts") or []:
        verb = fact.get("sentence", "").replace(data.get("fullLabel") or "", "", 1).replace(" was ", " ").strip()
        for time in fact.get("times") or []:
            if YEAR.search(time) and "–" not in time:
                return time if fact.get("predicate") == "occurred" or not verb else f"{verb} {time}"
    match = YEAR.search(data.get("description") or "")
    return match.group(0) if match else None


def _gist(description: str | None) -> str | None:
    if not description:
        return None
    first = re.split(r"[;,(]", description, maxsplit=1)[0].strip()
    words = first.split()
    return " ".join(words[:HINT_WORDS]) + ("…" if len(words) > HINT_WORDS else "") if words else None


def name_hints(nodes: dict[str, dict[str, Any]]) -> None:
    """Rule 3: a short hint on every entity that shares its name with another.

    The kind when the kinds differ (a period and a state); for an event or period its date, for
    anything else the gist of its description, each falling back to the other; else a plain
    "another <kind>". Never an authority code (doc 26)."""
    same: dict[str, list[dict[str, Any]]] = {}
    for data in nodes.values():
        same.setdefault((data.get("fullLabel") or data["label"]).casefold(), []).append(data)
    for group in same.values():
        if len(group) < 2:
            continue
        kinds = {d["kind"] for d in group}
        for data in group:
            if len(kinds) > 1:
                hint = KIND_WORDS.get(data["kind"], data["kind"].lower())
            elif data["kind"] in DATED_FIRST:
                hint = _year(data) or _gist(data.get("description"))
            else:
                hint = _gist(data.get("description")) or _year(data)
            data["hint"] = hint or f"another {KIND_WORDS.get(data['kind'], 'entity')}"
        hints = [d["hint"] for d in group]
        for data in group:  # two hints alike tell nothing apart: fall back to the description's gist
            if hints.count(data["hint"]) > 1:
                data["hint"] = _gist(data.get("description")) or data["hint"]


LIBRARY_SYSTEMS = ("LCSH", "LCNAF", "FAST")
MAX_DEPTH = 4  # a moment, its phase, the battle, the war: far enough


def subject_access(edges: list[dict[str, Any]], nodes: dict[str, dict[str, Any]]) -> None:
    """Rule 6: headings inherited through live, non-imaginative part-of links, from the nearest whole."""
    wholes: dict[str, list[str]] = {}
    for edge in edges:
        if edge["predicate"] == "partOf" and _live(edge) and edge["category"] != "imaginative":
            wholes.setdefault(edge["source"], []).append(edge["target"])

    def headings(data: dict[str, Any]) -> list[str]:
        return [a["label"] for a in data.get("authority") or [] if a.get("system") in LIBRARY_SYSTEMS]

    for data in nodes.values():
        if headings(data) or data["id"] not in wholes:
            continue
        seen, level = {data["id"]}, wholes[data["id"]]
        for _ in range(MAX_DEPTH):
            found = [(w, headings(nodes[w])) for w in sorted(set(level)) if w in nodes and headings(nodes[w])]
            if found:
                data["subjectAccess"] = [{"heading": h, "via": w, "viaLabel": nodes[w]["fullLabel"]}
                                         for w, hs in found for h in hs]
                break
            seen |= set(level)
            level = [p for w in level for p in wholes.get(w, []) if p not in seen]
            if not level:
                break


def _host(uri: str | None) -> str | None:
    return uri.split("/")[2] if uri and "://" in uri else None


def _held_words(record: dict[str, Any], systems: dict[str, dict[str, Any]]) -> tuple[str, str]:
    """How a record is held, in words, and a sentence saying why (rule 7)."""
    status = record.get("status") or "accepted"
    if status != "accepted":
        return status, f"This link is {status}, not accepted."
    if record.get("gazetteer"):
        return "its location", record.get("basis") or "Linked as where this place lies."
    if record.get("role") == "entity_identity":
        if record.get("relation") == "exactMatch":
            return "its identity", "Linked as the same thing, by an exact match."
        return "its identity · close match", "Linked as the same thing, by a close match, not an exact one."
    system, host = record["system"], _host(record.get("sourceUri"))
    if host is None:
        return "", "Where this record was read is not recorded."
    if host in systems.get(system, {}).get("hosts", ()):
        return "checked there", f"Read from {system}'s own record."
    owner = next((name for name, spec in systems.items() if host in spec.get("hosts", ())), host)
    return f"per {owner}", f"{owner} states this link; not yet checked at {system} itself."


def elsewhere(nodes: dict[str, dict[str, Any]], networks: dict[str, Any]) -> None:
    """Rule 7: the entity's records in each outside network, in the profile's order and words."""
    systems, order = networks.get("systems", {}), networks.get("order", [])
    hub, expected = networks.get("hub"), networks.get("expected", {})
    for data in nodes.values():
        located = {(g["system"], g["identifier"]): g for g in data.get("gazetteer") or []}
        # a crosswalk the gazetteer also holds was read at the source: it is the place's location
        records = [{**a, "gazetteer": True, "status": located[(a["system"], a["identifier"])].get("status"),
                    "basis": located[(a["system"], a["identifier"])].get("basis")}
                   if (a["system"], a["identifier"]) in located else dict(a) for a in data.get("authority") or []]
        held = {(r["system"], r["identifier"]) for r in records}
        records += [{**g, "gazetteer": True, "label": f"{g.get('label') or g['identifier']} ({g['system']} {g['identifier']})"}
                    for g in data.get("gazetteer") or [] if (g["system"], g["identifier"]) not in held]
        missing = [s for s in expected.get(data["kind"], []) if s not in {r["system"] for r in records}]
        if not records and not missing:
            continue
        groups: dict[str, list[dict[str, Any]]] = {}
        per_hub = 0
        for record in records:
            spec = systems.get(record["system"], {})
            link = spec.get("linkByKind", {}).get(data["kind"]) or spec.get("link")
            words, why = _held_words(record, systems)
            per_hub += words == f"per {hub}"
            groups.setdefault(spec.get("network", "Other"), []).append({
                "system": record["system"], "identifier": record["identifier"], "label": record["label"],
                "url": link.format(id=record["identifier"]) if link else None,
                "note": spec.get("noteByKind", {}).get(data["kind"]), "others": record.get("others") or 0,
                "status": record.get("status") or "accepted", "words": words, "why": why})
        for system in missing:
            groups.setdefault(systems.get(system, {}).get("network", "Other"), []).append(
                {"system": system, "missing": True, "words": "none held", "why": "No record held here yet."})
        count, nets = len(records), len({systems.get(r["system"], {}).get("network", "Other") for r in records})
        summary = (f"{count} record{'' if count == 1 else 's'} in {nets} network{'' if nets == 1 else 's'}"
                   + (f", {per_hub} per {hub} only" if per_hub else "") + ".") if records else "No records held."
        data["elsewhere"] = {"summary": summary, "networks": [
            {"network": name, "rows": groups[name]} for name in [*order, *sorted(set(groups) - set(order))]
            if name in groups]}


EVIDENCE_KINDS = (("text", "ancient text"), ("coin", "coin"), ("inscription", "inscription"))
EVIDENCE_ALSO = (("modern", "modern study", "modern studies"), ("reference", "reference work", "reference works"),
                 ("imagined", "imaginative work", "imaginative works"))
FORM_KINDS = {"coinage": "coin", "inscription": "inscription"}
STANDING_KINDS = {"primary": "text", "secondary": "modern"}


def _evidence_kind(work: dict[str, Any] | None, creative_forms: frozenset[str]) -> str:
    if work is None:
        return "reference"
    if work.get("form") in creative_forms:
        return "imagined"  # imaginative by its form: never evidence for a fact (rule 11)
    return FORM_KINDS.get(work.get("form")) or STANDING_KINDS.get(work.get("standing"), "reference")


def evidence_of(fact: dict[str, Any], works: dict[str, dict[str, Any]], creative_forms: frozenset[str]) -> dict[str, Any]:
    """Rule 8: the fact's kinds of evidence, the later works beside them, and a sentence."""
    by: dict[str, set[str]] = {}
    for voice in fact.get("voices") or []:
        for name in {voice.get("accordingTo"), *(q.get("source") for q in voice.get("quotes") or [])} - {None}:
            by.setdefault(_evidence_kind(works.get(name), creative_forms), set()).add(name)
    kinds = [{"kind": k, "words": w, "count": len(by[k]), "sources": sorted(by[k])} for k, w in EVIDENCE_KINDS if k in by]
    if not kinds:
        sentence = "No ancient evidence held: only later writers say it."
    elif len(kinds) == 1:
        sentence = f"One kind of evidence: {kinds[0]['words']}."
    else:
        sentence = f"{len(kinds)} independent kinds of evidence: {' and '.join(k['words'] for k in kinds)}."
    also = [f"{len(by[k])} {one if len(by[k]) == 1 else many}" for k, one, many in EVIDENCE_ALSO if k in by]
    return {"kinds": kinds, "missing": [w for k, w in EVIDENCE_KINDS if k not in by], "also": also,
            "sentence": sentence}


def evidence_kinds(edges: list[dict[str, Any]], nodes: dict[str, dict[str, Any]], creative_forms: frozenset[str]) -> None:
    works: dict[str, dict[str, Any]] = {}
    for data in nodes.values():
        if data["kind"] == "Work":
            works.setdefault(data["fullLabel"], data)
            works.setdefault(data["label"], data)
    for fact in [*edges, *(f for data in nodes.values() for f in data.get("facts") or [])]:
        fact["evidence"] = evidence_of(fact, works, creative_forms)


def apply(elements: dict[str, Any], standing: dict[str, str], networks: dict[str, Any] | None = None,
          creative_forms: frozenset[str] = frozenset()) -> dict[str, Any]:
    """Mark the projection's elements in place with every display rule, and return them."""
    nodes = {n["data"]["id"]: n["data"] for n in elements["nodes"]}
    edges = [e["data"] for e in elements["edges"]]
    for node_id, data in nodes.items():
        if node_id in standing:
            data["standing"] = standing[node_id]
            data["standingWords"] = STANDING_WORDS.get(standing[node_id])
        if data.get("description") and ONLY_A_LINK.fullmatch(data["description"]):
            data["description"] = None  # 5b: the address is not a description
    fold_parts_through_parts(edges)
    fold_distinct_beside_part(edges)
    fold_reference_works(edges, nodes)
    count_lines(edges, nodes)
    name_hints(nodes)
    subject_access(edges, nodes)
    if networks:
        elsewhere(nodes, networks)
    evidence_kinds(edges, nodes, creative_forms)
    for edge in edges:  # each end says how many of its lines a view folds, and why
        if edge.get("fold"):
            for end in {edge["source"], edge["target"]}:
                folded = nodes[end].setdefault("folded", {})
                folded[edge["fold"]] = folded.get(edge["fold"], 0) + 1
    return elements
