"""Follow a Wikipedia article's footnotes to the ancient passages its claims rest on (D-148, 42 §5).

    python -m GraphRevised.harvest.wikipedia_footnotes <Wikipedia Work id> [--apply]

For each live claim attributed to the article's Work, the footnote that follows
the claim's quotation in the article (in the same sentence, or right after it)
is read. A citation of an ancient Work we hold (curation/citation-aliases.json),
such as "Livy 21.4" (book 21, chapter 4), is followed to our passages with that locator, and
the claim gets a RESTS_ON link to each and basis `reports`. When we hold the
Work but not the passage, the link goes to the Work (shown, not counted). A
citation of a Work we do not hold, and every modern citation, is listed as a
source to acquire.

This is a code-made extraction, accepted by rule (D-145): nothing is inferred,
only a footnote's own words are followed. Without --apply it reports and rolls
back. Retry-safe: existing links are kept.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.adapters.wikipedia_passages import footnote_positions, footnotes
from GraphRevised.operations import load_operations, run_write
from GraphRevised import localdb

GRAPH_REVISED = Path(__file__).resolve().parents[1]
ALIASES = GRAPH_REVISED / "curation" / "citation-aliases.json"
RUNS = GRAPH_REVISED / "runs"
RULE = "rule: code-made extraction (D-145): a Wikipedia footnote followed to the passage it cites"
BY = "wikipedia-footnote-harvest-v1"
ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10}
LOCATOR = re.compile(r"^\s*,?\s*(?P<start>(?:[ivx]+|\d+)(?:\.\d+)*)(?:\s*[–-]\s*(?P<end>\d+(?:\.\d+)*))?", re.I)
OBSERVATION_REF = re.compile(r":(\d+(?:\.\d+)+):[0-9a-z]+$")
SENTENCE_BREAK = re.compile(r"[.!?]\s+\S")

CLAIMS = """
MATCH (a:Assertion)-[:ATTRIBUTED_TO]->(:Entity:Work {id: $work})
WHERE a.status IN ["accepted", "proposed"]
CALL (a) {
  MATCH (a)-[l:SUPPORTED_BY]->(o:SourceObservation)-[:IN_WORK]->(:Entity {id: $work})
  RETURN o.id AS observation, o.rawPayloadUri AS payload, l.quotation AS quotation
  UNION
  MATCH (p:Proposal)-[:PROPOSES]->(a)
  MATCH (p)-[l:PROPOSES_EVIDENCE]->(o:SourceObservation)-[:IN_WORK]->(:Entity {id: $work})
  RETURN o.id AS observation, o.rawPayloadUri AS payload, l.quotation AS quotation
}
RETURN a.id AS claim, a.label AS label, observation, payload, quotation
"""

HELD = "MATCH (o:SourceObservation)-[:IN_WORK]->(:Entity {id: $work}) RETURN o.id AS id"


def _numbers(text: str) -> tuple[int, ...]:
    head, *rest = text.split(".")
    first = ROMAN.get(head.lower()) if not head.isdigit() else int(head)
    return (first, *map(int, rest)) if first else ()


def citations(note: str, aliases: dict[str, list[str]], not_held: list[str]) -> list[dict[str, Any]]:
    """Each citation in one footnote: an ancient Work we hold with its locator range, an ancient
    Work we do not hold, or a modern citation."""
    names = sorted(((alias, work) for work, names in aliases.items() for alias in names), key=lambda x: -len(x[0]))
    found = []
    for part in (p.strip(" .") for p in re.split(r";", note) if p.strip(" .")):
        part = re.sub(r"\s+([.,])", r"\1", part)
        match = next(((alias, work) for alias, work in names if part.startswith(alias)), None)
        if match:
            loc = LOCATOR.match(part[len(match[0]):])
            start = _numbers(loc.group("start")) if loc else ()
            end = start[:len(start) - len(loc.group("end").split("."))] + _numbers(loc.group("end")) \
                if loc and loc.group("end") else start
            found.append({"kind": "held", "work": match[1], "citation": part, "start": start, "end": end})
        elif any(part.startswith(name) for name in not_held):
            found.append({"kind": "ancient not held", "citation": part})
        else:
            found.append({"kind": "modern", "citation": part})
    return found


def within(ref: tuple[int, ...], start: tuple[int, ...], end: tuple[int, ...]) -> bool:
    return bool(start) and ref[:len(start)] >= start and ref[:len(end)] <= end


def supporting(text: str, quotation: str, clusters: list[tuple[int, tuple[str, ...]]]) -> list[str]:
    """The footnotes that support a quotation: those inside it, and the first cluster after it in
    the same sentence (Wikipedia places a footnote after the clause or sentence it supports)."""
    begin = text.find(quotation)
    if begin < 0 or not quotation:
        return []
    finish = begin + len(quotation)
    notes = [n for offset, ids in clusters if begin < offset <= finish for n in ids]
    after = next(((offset, ids) for offset, ids in clusters if offset > finish), None)
    if after and not SENTENCE_BREAK.search(text[finish:after[0]]):
        notes += list(after[1])
    return list(dict.fromkeys(notes))


def plan(tx, work: str) -> dict[str, Any]:
    table = json.loads(ALIASES.read_text(encoding="utf-8"))
    rows = tx.run(CLAIMS, work=work).data()
    articles: dict[str, tuple[dict, dict, dict]] = {}
    held: dict[str, list[tuple[tuple[int, ...], str]]] = {}
    links, cited, unplaced = [], Counter(), 0
    for row in rows:
        if not row["payload"] or not row["quotation"]:
            continue
        if row["payload"] not in articles:
            html = json.loads((GRAPH_REVISED.parent / row["payload"]).read_bytes())["parse"]["text"]
            html = html["*"] if isinstance(html, dict) else html
            from GraphRevised.adapters.wikipedia_passages import parse_html
            articles[row["payload"]] = (parse_html(html)[0], footnote_positions(html), footnotes(html))
        passages, positions, notes = articles[row["payload"]]
        ref = re.search(r":(\d+\.\d+):r\d+$", row["observation"])
        if not ref or ref.group(1) not in passages:
            continue
        ids = supporting(passages[ref.group(1)].text, row["quotation"], positions.get(ref.group(1), []))
        if not ids:
            unplaced += 1
        for note_id in ids:
            for c in citations(notes.get(note_id, ""), table["works"], table["notHeld"]):
                if c["kind"] != "held":
                    cited[(c["kind"], c["citation"])] += 1
                    continue
                if c["work"] not in held:
                    held[c["work"]] = [(_numbers(m.group(1)), r["id"]) for r in tx.run(HELD, work=c["work"])
                                       for m in [OBSERVATION_REF.search(r["id"])] if m]
                targets = [oid for nums, oid in held[c["work"]] if within(nums, c["start"], c["end"])] or [c["work"]]
                for target in targets:
                    links.append({"assertionId": row["claim"], "label": row["label"], "targetId": target,
                                  "citation": c["citation"], "quotation": row["quotation"],
                                  "toPassage": target != c["work"]})
    unique = {(l["assertionId"], l["targetId"]): l for l in links}
    return {"claims": len({r["claim"] for r in rows}), "links": list(unique.values()), "cited": cited,
            "quotationsWithoutFootnote": unplaced}


def apply(tx, operations, found: dict[str, Any], at: str) -> int:
    for link in found["links"]:
        run_write(tx, operations, "link_rests_on", {**{k: link[k] for k in ("assertionId", "targetId", "citation",
                                                                             "quotation")},
                                                    "decidedAt": at, "decidedBy": BY, "decisionBasis": RULE})
    for claim in {l["assertionId"] for l in found["links"]}:
        run_write(tx, operations, "set_claim_basis", {"assertionId": claim, "basis": "reports",
                                                      "decidedAt": at, "decidedBy": BY})
    return len(found["links"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("work", help="the Wikipedia article's Work id")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(localdb.uri(),
                                  auth=localdb.auth(),
                                  notifications_min_severity="OFF")
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                found = plan(tx, args.work)
                written = apply(tx, load_operations(), found, at)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    to_passage = sum(l["toPassage"] for l in found["links"])
    print(f"{found['claims']} claims; {'wrote' if args.apply else 'would write'} {written} rests-on links "
          f"({to_passage} to a passage we hold, {written - to_passage} to a Work only) on "
          f"{len({l['assertionId'] for l in found['links']})} claims; "
          f"{found['quotationsWithoutFootnote']} quotations have no footnote in their sentence")
    by_citation = defaultdict(set)
    for l in found["links"]:
        by_citation[l["citation"]].add(l["targetId"].rsplit(":", 2)[-2] if l["toPassage"] else "(Work only)")
    for citation, refs in sorted(by_citation.items()):
        print(f"  {citation} -> {', '.join(sorted(refs))}")
    print("cited, not held (sources to acquire):")
    for (kind, citation), n in sorted(found["cited"].items(), key=lambda kv: (kv[0][0], kv[0][1])):
        print(f"  [{kind}] {citation} ({n})")
    RUNS.mkdir(exist_ok=True)
    out = RUNS / f"wikipedia-footnotes-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    out.write_text(json.dumps({"work": args.work, "applied": args.apply, "links": found["links"],
                               "cited": [{"kind": k, "citation": c, "n": n} for (k, c), n in found["cited"].items()]},
                              indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
