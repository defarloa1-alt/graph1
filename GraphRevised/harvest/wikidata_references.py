"""The works a Wikidata statement cites, as voices of their own (curator, 2026-11-16).

    python -m GraphRevised.harvest.wikidata_references [--apply]

A Wikidata statement can carry references: "stated in" (P248) a work, with a
page (P304), a URL (P854), the name the work uses (P1810). For each Wikidata
statement behind a live claim, the preserved payload is read again and each
work it is stated in is looked up in curation/wikidata-reference-works.json:

- a work classed `scholarship`, `prosopography` or `encyclopedia` becomes a second
  voice: the same claim, attributed to that work, with the Wikidata statement as
  its evidence and the reference (page, URL, name used) in the rationale. A
  code-made extraction, accepted by rule (D-145). Its standing (D-148) decides
  what it adds: a reference work shows but does not count.
- a work classed `authority file` or `not a source` adds no voice (an identifier
  file, a bulk import, a question-and-answer site);
- an unclassified work is listed for the curator, never used.

"Imported from Wikimedia project" (P143) says where a bot copied from, not a
source, and is never read as one. Without --apply it reports and rolls back.
Retry-safe: a voice already proposed is not proposed again.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.rule_accept import accept_by_rule
from GraphRevised.proposals.store import Neo4jReader, submit
from GraphRevised.proposals.validator import Outcome
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation
from GraphRevised.slices.add_entity import persist_identity, preserved_identity_payload

GRAPH_REVISED = Path(__file__).resolve().parents[1]
REPOSITORY = GRAPH_REVISED.parent
WORKS = GRAPH_REVISED / "curation" / "wikidata-reference-works.json"
RUNS = GRAPH_REVISED / "runs"
PROPOSER = "wikidata-reference-proposer-v1"
VOICES = ("scholarship", "prosopography", "encyclopedia")
SILENT = ("authority file", "not a source")

LIVE = """
MATCH (o:SourceObservation {sourceSystem: "Wikidata"})
WHERE o.externalStatementId IS NOT NULL
  AND (EXISTS { MATCH (a:Assertion)-[:SUPPORTED_BY]->(o) WHERE a.status IN ["proposed", "accepted"] }
       OR EXISTS { MATCH (p:Proposal)-[:PROPOSES_EVIDENCE]->(o) MATCH (p)-[:PROPOSES]->(a:Assertion)
                   WHERE a.status IN ["proposed", "accepted"] })
RETURN o.id AS id, o.rawPayloadUri AS uri, o.externalStatementId AS statement ORDER BY o.id
"""


def _value(snak: dict[str, Any]) -> Any:
    value = snak.get("datavalue", {}).get("value")
    if isinstance(value, dict):
        return value.get("id") or value.get("text") or value.get("time")
    return value


def references(payload: dict[str, Any], statement_id: str) -> list[dict[str, Any]]:
    """Each reference block of one statement: {statedIn: [qid], page, url, namedAs}."""
    for entity in payload.get("entities", {}).values():
        for claims in entity.get("claims", {}).values():
            for claim in claims:
                if claim.get("id") != statement_id:
                    continue
                found = []
                for block in claim.get("references", []):
                    snaks = block.get("snaks", {})
                    first = lambda p: next((_value(s) for s in snaks.get(p, []) if _value(s)), None)  # noqa: E731
                    found.append({"statedIn": [_value(s) for s in snaks.get("P248", []) if _value(s)],
                                  "page": first("P304"), "url": first("P854"), "namedAs": first("P1810")})
                return found
    return []


def reference_text(work_label: str, ref: dict[str, Any]) -> str:
    bits = [work_label] + [f"{k} {ref[v]}" for k, v in (("p.", "page"), ("as", "namedAs"), ("at", "url")) if ref.get(v)]
    return ", ".join(bits)


def ensure_works(tx, operations, registry, works: dict[str, dict[str, Any]], at: str) -> None:
    for qid, w in works.items():
        if w["class"] not in VOICES:
            continue
        exists = tx.run("MATCH (e:Entity {id: $id}) RETURN e.status AS status", id=w["work"]).single()
        # The Work's Wikidata identity, so the validator can check that a statement cites exactly this Work.
        path, metadata = preserved_identity_payload(qid)
        persist_identity(tx, operations, entity_id=w["work"], kind="Work", payload_path=path, metadata=metadata,
                         status=exists["status"] if exists else "provisional")
        run_write(tx, operations, "upsert_entity", {"id": w["work"], "kind": "Work", "label": w["label"],
                                                    "shortLabel": w.get("shortLabel", w["label"]),
                                                    "description": w["description"], "status": None})
        run_write(tx, operations, "set_work_form", {"workId": w["work"], "form": w["form"],
                                                    "allowedForms": sorted(registry.work_forms)})
        standing = tx.run("MATCH (e:Work {id: $id}) RETURN e.standing AS s", id=w["work"]).single()["s"]
        if standing is None:
            run_write(tx, operations, "set_work_standing", {
                "id": w["work"], "standing": w["standing"], "decidedAt": at,
                "decidedBy": "the curator's list of works Wikidata cites (curation/wikidata-reference-works.json)",
                "decisionBasis": f"cited by Wikidata as a {w['class']} ({qid})"})


def harvest(tx, operations, registry, works: dict[str, dict[str, Any]], at: str) -> dict[str, Any]:
    ensure_works(tx, operations, registry, works, at)
    reader = Neo4jReader(tx)
    cited, unclassified, outcomes, reasons = Counter(), Counter(), Counter(), Counter()
    payloads: dict[str, dict] = {}
    for row in tx.run(LIVE).data():
        if row["uri"] not in payloads:
            payloads[row["uri"]] = json.loads((REPOSITORY / row["uri"]).read_text(encoding="utf-8"))
        refs = references(payloads[row["uri"]], row["statement"])
        if refs:
            run_write(tx, operations, "record_statement_references", {
                "id": row["id"], "statedIn": sorted({q for r in refs for q in r["statedIn"]}),
                "references": json.dumps(refs, ensure_ascii=False, sort_keys=True)})
        for ref in refs:
            for qid in ref["statedIn"]:
                cited[qid] += 1
                work = works.get(qid)
                if work is None:
                    unclassified[qid] += 1
                    continue
                if work["class"] not in VOICES:
                    continue
                for draft in drafts_from_observation(reader.observation(row["id"]), reader, registry).drafts:
                    voice = draft.model_copy(update={
                        "attributed_to": work["work"], "proposed_by": PROPOSER,
                        "rationale": (f"Wikidata statement {row['statement']} is stated in "
                                      f"{reference_text(work['label'], ref)} ({qid}); the claim is that work's, "
                                      f"as Wikidata cites it.")})
                    result = submit(tx, voice, registry, operations)
                    outcomes[(work["label"], result.validation.outcome.value)] += 1
                    if result.validation.reasons:
                        reasons[result.validation.reasons[0][:140]] += 1
    return {"cited": cited, "unclassified": unclassified, "outcomes": outcomes, "reasons": reasons,
            "accepted": accept_by_rule(tx, at) if outcomes else None}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    table = json.loads(WORKS.read_text(encoding="utf-8"))["works"]
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                report = harvest(tx, load_operations(), load_registry(), table, at)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print(("applied" if args.apply else "dry run, rolled back") + f": works cited {sum(report['cited'].values())} times")
    for (label, outcome), n in sorted(report["outcomes"].items()):
        print(f"  {outcome:13} {n:4}  {label}")
    for reason, n in report["reasons"].most_common(6):
        print(f"    why ({n}): {reason}")
    if report["accepted"]:
        print(f"  accepted by rule: {dict(report['accepted']['accepted'])}")
    named = {q: w for q, w in table.items()}
    print("  cited and classified, no voice:",
          ", ".join(f"{named[q]['label']} ({n})" for q, n in report["cited"].most_common()
                    if q in named and named[q]["class"] in SILENT) or "none")
    if report["unclassified"]:
        print("  unclassified (for the curator; look up the labels before use):")
        for q, n in report["unclassified"].most_common():
            print(f"    {q} {n}")
    RUNS.mkdir(exist_ok=True)
    (RUNS / f"wikidata-references-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json").write_text(json.dumps(
        {"applied": args.apply, "cited": report["cited"], "unclassified": report["unclassified"],
         "outcomes": {f"{k[0]} | {k[1]}": v for k, v in report["outcomes"].items()}}, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
