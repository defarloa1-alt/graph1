"""Draw each live fact as a direct edge, so the graph can be walked (D-144).

    python -m GraphRevised.export.fact_layer [--apply]

Claims stay the source of truth: one Assertion per statement, with its
voices, evidence and review. The Assertion sits between an entity and the
things it says about it, so a reader walking the graph sees an event with
little on it. This layer is a derived, rebuildable view on top of it:

- One edge per fact, from subject to object, named after the predicate
  (`occurredAt` -> OCCURRED_AT, `partOf` -> PART_OF). It is the same fact
  the explorer draws (export/cytoscape.projection): all the voices that
  share a predicate, subject, object and category become one edge. The edge
  carries the status, attestation, sentence, times, roles, "according to"
  and the assertion ids behind it.
- A unary fact with Year links (`occurred`, `born`, `died`) becomes an edge
  from the entity to each Year it is tied to (OCCURRED, BORN, DIED), with
  `as` (during, start, end, earliest, latest).
- Short summary properties on the node: `when` (from `occurred`), `where`
  (from `occurredAt`) and `partOf`. One answer, not a survey: our own
  statement if there is one, else the accepted voices, else the proposed
  ones (a normalised date before a source's wording), each followed by who
  says it. Every voice stays on the edges and the claims.

Every edge is marked `derived: "fact-layer"`. Each run wipes the layer and
redraws it from the accepted and proposed claims, so it is never edited by
hand; rerun it after a review. Without --apply it reports and rolls back.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.export.confidence import LIVE
from GraphRevised.export.cytoscape import AUTHORS, projection

MARK = "fact-layer"
SUMMARY = {"occurred": "when", "occurredAt": "where", "partOf": "partOf"}
OURS = "Chrystallum"

CLEAR_EDGES = "MATCH (:Entity)-[r {derived: $mark}]->() DELETE r RETURN count(r) AS removed"
CLEAR_SUMMARY = ("MATCH (e:Entity) WHERE e.when IS NOT NULL OR e.where IS NOT NULL OR e.partOf IS NOT NULL "
                 "REMOVE e.when, e.where, e.partOf RETURN count(e) AS cleared")
DRAW_EDGES = """
UNWIND $rows AS row
MATCH (s:Entity {id: row.source}), (o:Entity {id: row.target})
CREATE (s)-[r:$(row.type)]->(o)
SET r = row.properties
RETURN count(r) AS drawn
"""
YEAR_LINKS = """
MATCH (a:Assertion)-[link:IN_YEAR]->(y:Year) WHERE a.status IN $live AND NOT (a)-[:ASSERTION_OBJECT]->()
MATCH (a)-[:ASSERTION_SUBJECT]->(e:Entity)
OPTIONAL MATCH (a)-[:ATTRIBUTED_TO]->(w:Entity)
RETURN e.id AS entity, a.predicate AS predicate, y.year AS year, link.as AS as, a.status AS status, a.id AS claim,
       w.label AS according
"""
DRAW_YEARS = """
UNWIND $rows AS row
MATCH (e:Entity {id: row.entity}), (y:Year {year: row.year})
CREATE (e)-[r:$(row.type)]->(y)
SET r = row.properties
RETURN count(r) AS drawn
"""
SET_SUMMARY = """
UNWIND $rows AS row
MATCH (e:Entity {id: row.id})
SET e += row.properties
RETURN count(e) AS summarised
"""


def relationship_type(predicate: str) -> str:
    """`occurredAt` -> OCCURRED_AT. Registry predicates are camelCase words; anything else is refused."""
    if not re.fullmatch(r"[a-z][A-Za-z]*", predicate):
        raise ValueError(f"not a predicate name: {predicate!r}")
    return re.sub(r"(?<!^)(?=[A-Z])", "_", predicate).upper()


def _short(labels: dict[str, str], according: str | None) -> str:
    return labels.get(according, according) if according else OURS


def source_names(nodes: dict[str, dict[str, Any]], authors: dict[str, str]) -> dict[str, str]:
    """A source Work's full label -> how a summary names it: its author from an `authorOf` claim,
    else the author before the comma of an "Author, Title" label ("Gibbon, The History of the
    Decline and Fall" -> Gibbon), else its short label."""
    names = {}
    for id_, data in nodes.items():
        full, short = data["fullLabel"], data["label"]
        if authors.get(id_) in nodes:
            names[full] = nodes[authors[id_]]["label"]
        elif ", " in full and short != full and full.endswith(short.removeprefix("The ")):
            names[full] = full.split(", ", 1)[0]
        else:
            names[full] = short
    return names


def summarise(entries: list[tuple[int, str, str]]) -> str:
    """One answer, not a survey (curator, 2026-11-13): keep only the best-ranked voices (0 ours,
    1 accepted, 2 proposed; +1 when a date is not normalised), one value per line with who says it."""
    best = min(rank for rank, _, _ in entries)
    grouped: dict[str, list[str]] = {}
    for rank, value, who in entries:
        if rank == best:
            names = grouped.setdefault(value, [])
            if who and who not in names:
                names.append(who)
    return "; ".join(value + (f" ({', '.join(names)})" if names and best > 0 else "")
                     for value, names in grouped.items())


def _rank(voice: dict[str, Any], dated: bool = True) -> int:
    rank = 0 if voice["accordingTo"] is None else 1 if voice["status"] == "accepted" else 2
    return rank * 2 + (0 if dated else 1)


def _clean(properties: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in properties.items() if value not in (None, [], "")}


def plan(view: dict[str, Any], year_links: list[dict[str, Any]],
         authors: dict[str, str] | None = None) -> dict[str, list[dict[str, Any]]]:
    """The layer to draw, from the explorer's projection, the claims' Year links, and each Work's author."""
    authors = authors or {}
    nodes = {node["data"]["id"]: node["data"] for node in view["elements"]["nodes"]}
    short = source_names(nodes, authors)
    dated = {link["claim"] for link in year_links}
    summary: dict[str, dict[str, list[tuple[int, str, str]]]] = {}

    def remember(entity: str, key: str, rank: int, value: str, voice: dict[str, Any]) -> None:
        who = _short(short, voice["accordingTo"]) if voice["accordingTo"] else ""
        summary.setdefault(entity, {}).setdefault(key, []).append((rank, value, who))

    edges = []
    for edge in view["elements"]["edges"]:
        fact = edge["data"]
        voices = fact["voices"]
        live = [v for v in voices if v["status"] in LIVE]
        edges.append({"source": fact["source"], "target": fact["target"],
                      "type": relationship_type(fact["predicate"]),
                      "properties": _clean({
                          "derived": MARK, "predicate": fact["predicate"], "status": fact["status"],
                          "mode": fact["mode"], "category": fact["category"],
                          "attestation": fact["attestation"], "sentence": fact["sentence"],
                          "when": "; ".join(fact["times"]),
                          "role": sorted({v["role"] for v in live if v["role"]}),
                          "accordingTo": sorted({_short(short, v["accordingTo"]) for v in live}),
                          "assertions": [v["claimId"] for v in voices]})})
        key = SUMMARY.get(fact["predicate"])
        if key:
            target = nodes[fact["target"]]["label"]
            for voice in live:
                remember(fact["source"], key, _rank(voice), target, voice)

    for data in nodes.values():
        for fact in data["facts"]:
            if SUMMARY.get(fact["predicate"]) == "when":
                for voice in fact["voices"]:
                    if voice["status"] in LIVE and voice["time"]:
                        remember(data["id"], "when", _rank(voice, voice["claimId"] in dated), voice["time"], voice)

    years: dict[tuple[str, str, int, str | None], dict[str, Any]] = {}
    for link in year_links:
        key = (link["entity"], link["predicate"], link["year"], link["as"])
        row = years.setdefault(key, {"entity": link["entity"], "year": link["year"],
                                     "type": relationship_type(link["predicate"]),
                                     "properties": {"derived": MARK, "predicate": link["predicate"], "as": link["as"],
                                                    "status": "proposed", "accordingTo": [], "assertions": []}})
        properties = row["properties"]
        if link["status"] == "accepted":
            properties["status"] = "accepted"
        according = _short(short, link["according"])
        if according not in properties["accordingTo"]:
            properties["accordingTo"].append(according)
        properties["assertions"].append(link["claim"])
    for row in years.values():
        row["properties"] = _clean(row["properties"])
        row["properties"]["accordingTo"] = sorted(row["properties"]["accordingTo"])

    return {"edges": edges, "years": list(years.values()),
            "summary": [{"id": entity, "properties": {key: summarise(entries) for key, entries in fields.items()}}
                        for entity, fields in summary.items()]}


def rebuild(tx: Any) -> dict[str, int]:
    """Wipe the layer and redraw it in the caller's transaction."""
    view = projection(tx)
    year_links = tx.run(YEAR_LINKS, live=list(LIVE)).data()
    authors = dict(tx.run(AUTHORS, live=list(LIVE)).values("work", "author"))
    layer = plan(view, year_links, authors)
    removed = tx.run(CLEAR_EDGES, mark=MARK).single()["removed"]
    cleared = tx.run(CLEAR_SUMMARY).single()["cleared"]
    drawn = tx.run(DRAW_EDGES, rows=layer["edges"]).single()["drawn"]
    dated = tx.run(DRAW_YEARS, rows=layer["years"]).single()["drawn"]
    summarised = tx.run(SET_SUMMARY, rows=layer["summary"]).single()["summarised"]
    return {"removed": removed, "cleared": cleared, "factEdges": drawn, "yearEdges": dated,
            "summarised": summarised}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                counts = rebuild(tx)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print(("" if args.apply else "(dry run, rolled back) ") + ", ".join(f"{k} {v}" for k, v in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
