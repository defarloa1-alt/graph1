"""Add a curator-approved author and Work, and link a source's passages to the Work.

    python -m GraphRevised.slices.add_work --author-qid Q185223 --author-id chr:entity:cassius-dio \\
        --work-qid Q3974431 --work-id chr:entity:cassius-dio-roman-history \\
        --work-label "Cassius Dio, Roman History" --work-short-label "Roman History" \\
        --passage-prefix chr:observation:lacuscurtius:cassius-dio:

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
from GraphRevised.slices.add_entity import persist_identity, preserved_identity_payload


def apply(tx, operations, registry, args) -> dict:
    author_path, author_meta = preserved_identity_payload(args.author_qid)
    work_path, work_meta = preserved_identity_payload(args.work_qid)
    persist_identity(tx, operations, entity_id=args.author_id, kind="Person",
                     payload_path=author_path, metadata=author_meta)
    persist_identity(tx, operations, entity_id=args.work_id, kind="Work", payload_path=work_path, metadata=work_meta)
    run_write(tx, operations, "upsert_entity", {
        "id": args.work_id, "kind": "Work", "label": args.work_label, "description": None,
        "status": None, "shortLabel": args.work_short_label,
    })

    passages = tx.run(
        "MATCH (o:SourceObservation {observationKind: 'passage'}) WHERE o.id STARTS WITH $prefix "
        "RETURN o.id AS id ORDER BY id",
        prefix=args.passage_prefix,
    ).value("id")
    for passage_id in passages:
        run_write(tx, operations, "link_observation_work", {"observationId": passage_id, "workId": args.work_id})

    entity = json.loads(work_path.read_bytes())["entities"][args.work_qid]
    statements = [c["id"] for c in entity["claims"].get("P50", [])
                  if c["mainsnak"].get("datavalue", {}).get("value", {}).get("id") == args.author_qid]
    outcomes = []
    if len(statements) == 1:
        observation = statement_observation(
            work_path, statements[0],
            label=f"Wikidata observation: {author_meta['entityLabel']} author of {work_meta['entityLabel']}",
            short_label=f"Wikidata: {author_meta['entityLabel']} -> {args.work_short_label}",
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
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            print(session.execute_write(apply, load_operations(), load_registry(), args))
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
