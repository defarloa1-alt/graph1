"""Seed Type entities from a curation list, each with its Wikidata identity where one exists (43 §4).

    python -m GraphRevised.slices.seed_types GraphRevised/curation/military-types.json [--apply]

Each Type gets our label and description, its category (set_type_category,
D-039), and, when the list names a Wikidata item, that item as its identity: the
payload preserved once in phase-5-source/ and linked like any identity (the
slices.add_entity route). A Type with no Wikidata item is a local Type. Identity
only: what a Type was, and when, comes from sources as dated claims. Without
--apply it reports and rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.slices.add_entity import persist_identity, persist_local_entity, preserved_identity_payload

BY = "seed-types-v1 (curator's list, 43 §4)"


def seed(tx, operations, types: list[dict], categories: frozenset[str], payloads: dict[str, tuple], at: str) -> list[str]:
    lines = []
    for t in types:
        if t["category"] not in categories:
            raise ValueError(f"{t['id']}: category {t['category']!r} is not in the registry's typeCategories")
        exists = tx.run("MATCH (e:Entity {id: $id}) RETURN e.status AS status", id=t["id"]).single()
        status = exists["status"] if exists else "provisional"
        if t.get("qid"):
            path, metadata = payloads[t["qid"]]
            persist_identity(tx, operations, entity_id=t["id"], kind="Type", payload_path=path, metadata=metadata,
                             status=status)
            note = f"{metadata['entityLabel']} ({t['qid']})"
        else:
            persist_local_entity(tx, operations, entity_id=t["id"], kind="Type", label=t["label"],
                                 description=t["description"], status=status)
            note = "local, no Wikidata item"
        # Our wording over Wikidata's: upsert_entity overwrites a label or description it is given.
        run_write(tx, operations, "upsert_entity", {"id": t["id"], "kind": "Type", "label": t["label"],
                                                    "shortLabel": t["label"], "description": t["description"],
                                                    "status": None})
        run_write(tx, operations, "set_type_category", {"id": t["id"], "category": t["category"],
                                                        "allowedCategories": sorted(categories), "decidedAt": at,
                                                        "decidedBy": BY, "decisionBasis": "the curator's Type list"})
        lines.append(f"{t['category']:14} {t['label']}: {note}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("types", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    types = json.loads(args.types.read_text(encoding="utf-8"))["types"]
    payloads = {t["qid"]: preserved_identity_payload(t["qid"]) for t in types if t.get("qid")}
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                lines = seed(tx, load_operations(), types, load_registry().type_categories, payloads, at)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print(("seeded" if args.apply else "would seed") + f" {len(lines)} Types:")
    print("\n".join(f"  {line}" for line in lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
