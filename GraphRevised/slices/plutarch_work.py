"""Plutarch and his Life of Antony as entities, approved by the curator on 2026-10-12.

    python -m GraphRevised.slices.plutarch_work

Adds Plutarch (Person, Q41523) and his Life of Antony (Work, Q12902608) with
their Wikidata identity links, links the preserved Life of Antony passage
observations to the Work (IN_WORK), and submits "Plutarch author of Life of
Antony" from Wikidata's P50 statement as a Proposal for the curator. It
accepts nothing. Every write is a guarded operation, so a rerun is a no-op.
"""

from __future__ import annotations

import os

from neo4j import GraphDatabase

from GraphRevised.adapters.wikidata_statements import statement_observation
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.store import Neo4jReader, submit
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation
from GraphRevised.slices.add_entity import persist_identity, preserved_identity_payload

PLUTARCH = ("chr:entity:plutarch", "Q41523")
LIFE = ("chr:entity:plutarch-life-of-antony", "Q12902608")
# The curator's local label; the AuthorityRecord keeps Wikidata's "Life of Mark Antony".
LIFE_LABEL, LIFE_SHORT_LABEL = "Plutarch, Life of Antony", "Life of Antony"
# The edition already read: Perseus TEI of Plutarch's Antony (tlg0007.tlg058).
PASSAGE_ID_PREFIX = "chr:observation:perseus:tlg0007.tlg058."


def apply(tx, operations, registry) -> dict:
    plutarch_path, plutarch_meta = preserved_identity_payload(PLUTARCH[1])
    life_path, life_meta = preserved_identity_payload(LIFE[1])
    persist_identity(tx, operations, entity_id=PLUTARCH[0], kind="Person",
                     payload_path=plutarch_path, metadata=plutarch_meta)
    persist_identity(tx, operations, entity_id=LIFE[0], kind="Work", payload_path=life_path, metadata=life_meta)
    run_write(tx, operations, "upsert_entity", {
        "id": LIFE[0], "kind": "Work", "label": LIFE_LABEL, "description": None,
        "status": None, "shortLabel": LIFE_SHORT_LABEL,
    })

    passages = tx.run(
        "MATCH (o:SourceObservation {observationKind: 'passage'}) WHERE o.id STARTS WITH $prefix "
        "RETURN o.id AS id ORDER BY id",
        prefix=PASSAGE_ID_PREFIX,
    ).value("id")
    for passage_id in passages:
        run_write(tx, operations, "link_observation_work", {"observationId": passage_id, "workId": LIFE[0]})

    statement_id = _author_statement(life_path)
    observation = statement_observation(
        life_path, statement_id,
        label="Wikidata observation: Plutarch author of Life of Mark Antony",
        short_label="Wikidata: Plutarch -> Life of Antony",
    )
    run_write(tx, operations, "upsert_observation", observation)
    reader = Neo4jReader(tx)
    result = drafts_from_observation(reader.observation(observation["id"]), reader, registry)
    outcomes = []
    for draft in result.drafts:
        submission = submit(tx, draft, registry, operations)
        outcomes.append((submission.validation.outcome.value, submission.validation.proposal_id, submission.stored))
    return {"passages": len(passages), "observation": observation["id"], "unresolved": result.unresolved,
            "proposals": outcomes}


def _author_statement(payload_path) -> str:
    import json

    entity = json.loads(payload_path.read_bytes())["entities"][LIFE[1]]
    statements = [c for c in entity["claims"].get("P50", [])
                  if c["mainsnak"].get("datavalue", {}).get("value", {}).get("id") == PLUTARCH[1]]
    if len(statements) != 1:
        raise RuntimeError(f"expected one P50 statement naming {PLUTARCH[1]}, found {len(statements)}")
    return statements[0]["id"]


def main() -> int:
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            summary = session.execute_write(apply, load_operations(), load_registry())
    finally:
        driver.close()
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
