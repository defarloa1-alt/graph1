"""First-contact Wikidata harvest (25-LIVES-AND-PLAYGROUND.md section 10), increment 1: a report.

    python -m GraphRevised.harvest.wikidata_harvest <QID> [--out GraphRevised/exports/harvest-<QID>.md]

Reads the entity's preserved Wikidata record (fetched once into
phase-5-source/ if missing) and classes every statement by the rules in
harvest/wikidata_rules.v1.json and the predicate registry:

    identifier     an external identifier: the quiet federation crosswalk
    attribute      a value about the entity alone (gender, occupation, a name)
    dated          a date about the entity alone (born, died): becomes a dated claim, never a bare property
    relationship   a link to another entity, with its qualifiers mapped: time span, uncertain
                   window, colleague, jurisdiction, ordinal, end cause
    housekeeping   Wikimedia internals, ignored

Deprecated statements are left out and preferred ones marked. Every date is
read with its precision (proposals/temporal.py) and tethered to the Year
backbone: "during" for a point or a definite span (each Year, or its start
and end Years when longer than the link limit), "within" for an uncertain
window (its earliest and latest Years). Every identifier is shown with its
label (labels cached in cache/wikidata-labels.json). Nothing is written to
the graph: this increment shows what the harvest would propose.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from GraphRevised.adapters.wikidata_identity import USER_AGENT
from GraphRevised.proposals.registry import PredicateRegistry, load_registry
from GraphRevised.proposals.temporal import (
    MAX_LINKED_YEARS, TimeValueError, display_edtf, parse_edtf, wikidata_time,
)
from GraphRevised.slices.add_entity import preserved_identity_payload

GRAPH_REVISED = Path(__file__).resolve().parents[1]
RULES_PATH = Path(__file__).resolve().parent / "wikidata_rules.v1.json"
LABEL_CACHE = GRAPH_REVISED / "cache" / "wikidata-labels.json"
BACKBONE = (-2000, 2025)


def load_rules(path: Path = RULES_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class Labels:
    """English labels and descriptions for QIDs and PIDs, cached; a code is never shown alone."""

    def __init__(self, path: Path = LABEL_CACHE) -> None:
        self.path = path
        self.known: dict[str, dict[str, Any]] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def resolve(self, ids: set[str]) -> None:
        missing = sorted(i for i in ids if i not in self.known)
        for start in range(0, len(missing), 50):
            batch = missing[start:start + 50]
            response = requests.get("https://www.wikidata.org/w/api.php", params={
                "action": "wbgetentities", "ids": "|".join(batch), "props": "labels|descriptions",
                "languages": "en", "format": "json"}, headers={"User-Agent": USER_AGENT}, timeout=30)
            response.raise_for_status()
            retrieved = datetime.now(timezone.utc).isoformat()
            for identifier, entity in response.json()["entities"].items():
                self.known[identifier] = {
                    "label": entity.get("labels", {}).get("en", {}).get("value"),
                    "description": entity.get("descriptions", {}).get("en", {}).get("value"),
                    "retrievedAt": retrieved,
                }
        if missing:
            self.path.parent.mkdir(exist_ok=True)
            self.path.write_text(json.dumps(self.known, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")

    def label(self, identifier: str) -> str:
        return (self.known.get(identifier) or {}).get("label") or "(no English label)"

    def show(self, identifier: str) -> str:
        return f"{self.label(identifier)} ({identifier})"


@dataclass
class Statement:
    pid: str
    kind: str  # identifier, attribute, dated, relationship, housekeeping
    value: Any  # a QID for items, the raw value otherwise
    datatype: str
    rank: str
    references: int
    event: str | None = None  # for dated statements: born, died, ...
    predicates: list[tuple[str, str]] = field(default_factory=list)  # (predicate, direction) for relationships
    time: dict[str, Any] | None = None  # {edtf, calendar, mode, display, tether}
    carried: dict[str, list[Any]] = field(default_factory=dict)
    unmapped_qualifiers: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)


def _value(snak: dict[str, Any]) -> Any:
    value = snak.get("datavalue", {}).get("value")
    if isinstance(value, dict) and "id" in value:
        return value["id"]
    return value


def tether(edtf: str, calendar: str, mode: str) -> dict[str, Any]:
    """How a time value tethers to the Year backbone, in Chrystallum years."""
    bounds = parse_edtf(edtf, calendar)
    first, last = bounds.earliest_year, bounds.latest_year
    outside = sorted({y for y in (first, last) if y is not None and not BACKBONE[0] <= y <= BACKBONE[1]})
    if outside:
        return {"how": "outside the backbone", "years": outside}
    if first is None or last is None:
        return {"how": "start only" if last is None else "end only", "years": [first if last is None else last]}
    if mode == "within":
        return {"how": "within", "years": [first] if first == last else [first, last]}
    count = len([y for y in range(first, last + 1) if y != 0])
    if count > MAX_LINKED_YEARS:
        return {"how": "start and end", "years": [first, last]}
    return {"how": "during", "years": [first] if first == last else [first, last], "count": count}


def _time(values: dict[str, Any]) -> dict[str, Any]:
    """Assemble one time qualifier from Wikidata point, start/end, or earliest/latest values."""
    def part(raw: dict[str, Any], side: str) -> tuple[str, str]:
        edtf, calendar = wikidata_time(raw)
        if "/" in edtf:  # a decade or century: its first year opens, its last year closes
            edtf = edtf.split("/")[0 if side == "start" else 1]
        return edtf, calendar

    if "point" in values:
        edtf, calendar = wikidata_time(values["point"])
        mode = "during"
    elif "start" in values or "end" in values:
        start = part(values["start"], "start") if "start" in values else ("..", None)
        end = part(values["end"], "end") if "end" in values else ("..", None)
        calendar = start[1] or end[1]
        edtf, mode = f"{start[0]}/{end[0]}", "during"
    else:
        earliest = part(values["earliest"], "start") if "earliest" in values else ("..", None)
        latest = part(values["latest"], "end") if "latest" in values else ("..", None)
        calendar = earliest[1] or latest[1]
        edtf, mode = f"{earliest[0]}/{latest[0]}", "within"
    return {"edtf": edtf, "calendar": calendar, "mode": mode, "display": display_edtf(edtf),
            "tether": tether(edtf, calendar, mode)}


def classify(entity: dict[str, Any], rules: dict[str, Any], registry: PredicateRegistry) -> tuple[list[Statement], int]:
    """Every non-deprecated statement of the entity, classed; and the number of deprecated ones left out."""
    statements, deprecated = [], 0
    time_qualifiers, carried = rules["qualifiers"]["time"], rules["qualifiers"]["carried"]
    for pid, claims in entity.get("claims", {}).items():
        for claim in claims:
            if claim.get("rank") == "deprecated":
                deprecated += 1
                continue
            snak = claim["mainsnak"]
            datatype = snak.get("datatype", "")
            statement = Statement(pid=pid, kind="attribute", value=_value(snak), datatype=datatype,
                                  rank=claim.get("rank", "normal"), references=len(claim.get("references", [])))
            if snak.get("snaktype") != "value":
                statement.problems.append(f"{snak.get('snaktype')}: Wikidata records an unknown or no value")
            if pid in rules["housekeeping"]:
                statement.kind = "housekeeping"
            elif datatype == "external-id":
                statement.kind = "identifier"
            elif datatype == "time":
                statement.kind, statement.event = "dated", rules["datedEvents"].get(pid)
                if statement.value:
                    try:
                        statement.time = _time({"point": statement.value})
                    except TimeValueError as error:
                        statement.problems.append(str(error))
            elif datatype == "wikibase-item" and pid not in rules["attributeItems"]:
                statement.kind = "relationship"
                statement.predicates = [(d.id, m.direction) for d, m in registry.for_wikidata(pid)]
            if statement.kind == "relationship":
                values: dict[str, Any] = {}
                for qualifier, snaks in claim.get("qualifiers", {}).items():
                    if qualifier in time_qualifiers:
                        raw = _value(snaks[0])
                        if isinstance(raw, dict):
                            values[time_qualifiers[qualifier]] = raw
                    elif qualifier in carried:
                        statement.carried[qualifier] = [_value(s) for s in snaks]
                    else:
                        statement.unmapped_qualifiers.append(qualifier)
                if values:
                    try:
                        statement.time = _time(values)
                    except TimeValueError as error:
                        statement.problems.append(str(error))
            statements.append(statement)
    return statements, deprecated


def _ids(statements: list[Statement]) -> set[str]:
    ids = set()
    for s in statements:
        ids.add(s.pid)
        ids.update(s.carried)
        ids.update(s.unmapped_qualifiers)
        if isinstance(s.value, str) and s.value[:1] == "Q" and s.datatype.startswith("wikibase"):
            ids.add(s.value)
        for values in s.carried.values():
            ids.update(v for v in values if isinstance(v, str) and v[:1] == "Q")
    return ids


def _shown_value(s: Statement, labels: Labels) -> str:
    if s.datatype.startswith("wikibase") and isinstance(s.value, str):
        return labels.show(s.value)
    if isinstance(s.value, dict):
        if "text" in s.value:
            return f"{s.value['text']} [{s.value.get('language')}]"
        if "latitude" in s.value:
            return f"{s.value['latitude']}, {s.value['longitude']}"
        if "amount" in s.value:
            return s.value["amount"]
    return str(s.value)


def _tether_text(time: dict[str, Any]) -> str:
    t = time["tether"]
    years = " and ".join(str(y) for y in t["years"]) if t["how"] != "during" else (
        str(t["years"][0]) if len(t["years"]) == 1 else f"{t['years'][0]}..{t['years'][1]} ({t['count']} Years)")
    return f"{time['display']} → {t['how']}: {years}"


def report(qid: str, entity: dict[str, Any], statements: list[Statement], deprecated: int, labels: Labels,
           local: dict[str, list[str]] | None = None) -> str:
    title = labels.show(qid)
    by_kind: dict[str, list[Statement]] = {}
    for s in statements:
        by_kind.setdefault(s.kind, []).append(s)
    lines = [f"# Harvest report: {title}", "",
             f"Revision {entity.get('lastrevid')}. {len(statements)} statements kept, {deprecated} deprecated left out. "
             + ", ".join(f"{k}: {len(v)}" for k, v in sorted(by_kind.items())), ""]

    def mark(s: Statement) -> str:
        bits = ["preferred"] if s.rank == "preferred" else []
        bits.append(f"{s.references} ref" + ("" if s.references == 1 else "s"))
        return f" _({', '.join(bits)})_" + ("".join(f" ⚠ {p}" for p in s.problems))

    lines += ["## Dated (each becomes a dated claim tethered to Years)", ""]
    for s in by_kind.get("dated", []):
        event = s.event or "date"
        shown = _tether_text(s.time) if s.time else "unreadable"
        lines.append(f"- **{event}** · {labels.show(s.pid)}: {shown}{mark(s)}")
    lines += ["", "## Attributes (shown on the card, from Wikidata)", ""]
    for s in by_kind.get("attribute", []):
        lines.append(f"- {labels.show(s.pid)}: {_shown_value(s, labels)}{mark(s)}")
    lines += ["", "## Relationships (each becomes a claim according to Wikidata)", ""]
    for s in sorted(by_kind.get("relationship", []), key=lambda s: (not s.predicates, s.pid)):
        mapped = ", ".join(f"{p}" + (" (inverse)" if d == "inverse" else "") for p, d in s.predicates) or "**unmapped**"
        line = f"- {labels.show(s.pid)} → {_shown_value(s, labels)} · predicate: {mapped}"
        if s.time:
            line += f" · {_tether_text(s.time)}"
        for qualifier, values in s.carried.items():
            line += f" · {labels.label(qualifier)}: " + ", ".join(
                labels.show(v) if isinstance(v, str) and v[:1] == "Q" else str(v) for v in values)
        if s.unmapped_qualifiers:
            line += " · unmapped qualifiers: " + ", ".join(labels.show(q) for q in s.unmapped_qualifiers)
        if local is not None and isinstance(s.value, str):
            line += f" · local: {', '.join(local.get(s.value, [])) or 'none'}"
        lines.append(line + mark(s))
    lines += ["", "## Identifiers (the federation crosswalk, quiet)", ""]
    for s in sorted(by_kind.get("identifier", []), key=lambda s: labels.label(s.pid).lower()):
        lines.append(f"- {labels.show(s.pid)}: {s.value}")
    lines += ["", "## Housekeeping (ignored)", ""]
    lines += [f"- {labels.show(s.pid)}" for s in by_kind.get("housekeeping", [])]
    targets = sorted({s.value for s in by_kind.get("relationship", []) if isinstance(s.value, str)})
    lines += ["", f"## One hop: {len(targets)} entities the relationships reach", ""]
    for target in targets:
        description = (labels.known.get(target) or {}).get("description") or ""
        state = "" if local is None else (" · in the graph" if local.get(target) else " · would be proposed")
        lines.append(f"- {labels.show(target)}: {description}{state}")
    return "\n".join(lines) + "\n"


def local_matches(qids: list[str]) -> dict[str, list[str]] | None:
    """Local Entities with an accepted identity for each QID; None without a database password."""
    if not os.environ.get("NEO4J_PASSWORD"):
        return None
    from neo4j import GraphDatabase

    from GraphRevised.proposals.store import Neo4jReader

    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            return session.execute_read(lambda tx: {q: Neo4jReader(tx).entity_ids_for_wikidata(q) for q in qids})
    finally:
        driver.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("qid")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    path, _ = preserved_identity_payload(args.qid)
    entity = json.loads(path.read_bytes())["entities"][args.qid]
    statements, deprecated = classify(entity, load_rules(), load_registry())
    labels = Labels()
    labels.resolve(_ids(statements) | {args.qid})
    targets = sorted({s.value for s in statements if s.kind == "relationship" and isinstance(s.value, str)})
    text = report(args.qid, entity, statements, deprecated, labels, local_matches(targets))
    out = args.out or GRAPH_REVISED / "exports" / f"harvest-{args.qid}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"{out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
