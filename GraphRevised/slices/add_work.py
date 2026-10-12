"""Add a curator-approved author and Work, and link a source's passages to the Work.

    python -m GraphRevised.slices.add_work --author-qid <QID> --author-id chr:entity:<author> \
        --work-qid <QID> --work-id chr:entity:<work> --work-label "<Author, Title>" \
        --work-short-label "<Title>" --passage-prefix chr:observation:<system>:<work slug>:

Prefer a `works` entry in a curation manifest (slices/apply_curation.py).

Identity setup only, after the curator approves both identities: it creates
the two Entities with their Wikidata identity links (payloads preserved in
phase-5-source/), sets the Work's local label, links every preserved passage
whose ID starts with the prefix to the Work (IN_WORK), and submits "author
of" from the Work's Wikidata P50 statement as a Proposal for the curator. It
accepts nothing, and a rerun is a no-op.
"""

from __future__ import annotations

import argparse
import json
import os

from neo4j import GraphDatabase

from GraphRevised.adapters.wikidata_statements import statement_observation
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.store import Neo4jReader, submit
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation
from GraphRevised.slices.add_entity import persist_identity, persist_local_entity, preserved_identity_payload


def apply_work(tx, operations, registry, item: dict) -> dict:
    """Apply one manifest `works` entry: authorId, authorQid, workId, workQid, workLabel,
    workShortLabel, passagePrefix. A Work with no Wikidata record omits workQid and gives
    workDescription instead: it becomes a local Work, and no "author of" is proposed. An author
    with no Wikidata record likewise omits authorQid and gives authorLabel and authorDescription."""
    if item.get("authorQid"):
        author_path, author_meta = preserved_identity_payload(item["authorQid"])
        persist_identity(tx, operations, entity_id=item["authorId"], kind="Person",
                         payload_path=author_path, metadata=author_meta)
    else:
        persist_local_entity(tx, operations, entity_id=item["authorId"], kind="Person",
                             label=item["authorLabel"], description=item["authorDescription"])
    if not item.get("workQid"):
        persist_local_entity(tx, operations, entity_id=item["workId"], kind="Work", label=item["workLabel"],
                             description=item["workDescription"])
        run_write(tx, operations, "upsert_entity", {
            "id": item["workId"], "kind": "Work", "label": item["workLabel"], "description": None,
            "status": None, "shortLabel": item["workShortLabel"],
        })
        return {"passagesLinked": 0, "authorStatements": 0, "proposals": [], "localWork": True}
    work_path, work_meta = preserved_identity_payload(item["workQid"])
    persist_identity(tx, operations, entity_id=item["workId"], kind="Work", payload_path=work_path, metadata=work_meta)
    run_write(tx, operations, "upsert_entity", {
        "id": item["workId"], "kind": "Work", "label": item["workLabel"], "description": None,
        "status": None, "shortLabel": item["workShortLabel"],
    })

    passages = tx.run(
        "MATCH (o:SourceObservation {observationKind: 'passage'}) WHERE o.id STARTS WITH $prefix "
        "RETURN o.id AS id ORDER BY id",
        prefix=item["passagePrefix"],
    ).value("id")
    for passage_id in passages:
        run_write(tx, operations, "link_observation_work", {"observationId": passage_id, "workId": item["workId"]})

    entity = json.loads(work_path.read_bytes())["entities"][item["workQid"]]
    statements = [c["id"] for c in entity["claims"].get("P50", [])
                  if c["mainsnak"].get("datavalue", {}).get("value", {}).get("id") == item["authorQid"]]
    outcomes = []
    if len(statements) == 1:
        observation = statement_observation(
            work_path, statements[0],
            label=f"Wikidata observation: {author_meta['entityLabel']} author of {work_meta['entityLabel']}",
            short_label=f"Wikidata: {author_meta['entityLabel']} -> {item['workShortLabel']}",
        )
        run_write(tx, operations, "upsert_observation", observation)
        reader = Neo4jReader(tx)
        result = drafts_from_observation(reader.observation(observation["id"]), reader, registry)
        for draft in result.drafts:
            submission = submit(tx, draft, registry, operations)
            outcomes.append((submission.validation.outcome.value, submission.validation.proposal_id, submission.stored))
    return {"passagesLinked": len(passages), "authorStatements": len(statements), "proposals": outcomes}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ("author-qid", "author-id", "work-qid", "work-id", "work-label", "work-short-label"):
        parser.add_argument(f"--{name}", required=True)
    parser.add_argument("--passage-prefix", required=True, help="ID prefix of the passage observations of this Work")
    args = parser.parse_args(argv)
    item = {"authorQid": args.author_qid, "authorId": args.author_id, "workQid": args.work_qid,
            "workId": args.work_id, "workLabel": args.work_label, "workShortLabel": args.work_short_label,
            "passagePrefix": args.passage_prefix}
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            print(session.execute_write(apply_work, load_operations(), load_registry(), item))
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
