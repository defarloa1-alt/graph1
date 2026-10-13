"""Apply a curation manifest: curator-approved identities and local entities, as data.

    python -m GraphRevised.slices.apply_curation GraphRevised/curation/actium.json [--dry-run]

A manifest records curator decisions; this runner holds no subject knowledge.
Sections, applied in this order in one transaction:

    identities          {id, kind, qid, label?, shortLabel?}       Entity + Wikidata identity link
    localEntities       {id, kind, label, description}             Entity with no external identity
    works               {authorId, authorQid, workId, workQid, workLabel, workShortLabel, passagePrefix,
                         form?}
    statementProposals  {payload, statementId, label, shortLabel}  a Wikidata statement, proposed
                                                                     through the deterministic proposer
    subjectHeadings     {subjectId, system, identifier, relation?}  a library subject heading (LCSH or
                                                                     FAST) on a Subject; its label is read
                                                                     from the preserved authority record

Identity payloads are fetched once and preserved in phase-5-source/. Every
write is a guarded operation and nothing is accepted, so applying a manifest
again changes nothing. --dry-run applies it in a transaction that is rolled
back and reports what would change, with any existing Entity a new one might
duplicate (identity/local_candidates.py).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.adapters.library_headings import display, preserved_heading
from GraphRevised.adapters.wikidata_statements import statement_observation
from GraphRevised.identity.local_candidates import candidates
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.store import Neo4jReader, submit
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation
from GraphRevised.slices.add_entity import persist_identity, persist_local_entity, preserved_identity_payload
from GraphRevised.slices.add_work import apply_work

GRAPH_REVISED = Path(__file__).resolve().parents[1]

SNAPSHOT = """
CALL () { MATCH (n) WHERE NOT n:Year RETURN collect([labels(n), properties(n)]) AS nodes }
CALL () { MATCH (a)-[r]->(b) WHERE NOT a:Year
          RETURN collect([coalesce(a.id, a.year), type(r), properties(r), coalesce(b.id, b.year)]) AS relationships }
RETURN nodes, relationships
"""


def apply_manifest(tx: Any, manifest: dict[str, Any], operations: dict[str, str], registry) -> dict[str, Any]:
    summary: dict[str, Any] = {"identities": 0, "localEntities": 0, "works": [], "statementProposals": [],
                               "subjectHeadings": []}
    for item in manifest.get("identities", []):
        payload_path, metadata = preserved_identity_payload(item["qid"])
        persist_identity(tx, operations, entity_id=item["id"], kind=item["kind"],
                         payload_path=payload_path, metadata=metadata)
        if item.get("label") or item.get("shortLabel"):
            run_write(tx, operations, "upsert_entity", {
                "id": item["id"], "kind": item["kind"], "label": item.get("label"), "description": None,
                "status": None, "shortLabel": item.get("shortLabel"),
            })
        summary["identities"] += 1
    for item in manifest.get("localEntities", []):
        persist_local_entity(tx, operations, entity_id=item["id"], kind=item["kind"], label=item["label"],
                             description=item["description"])
        summary["localEntities"] += 1
    for item in manifest.get("works", []):
        summary["works"].append(apply_work(tx, operations, registry, item))
    for item in manifest.get("statementProposals", []):
        observation = statement_observation(GRAPH_REVISED / item["payload"], item["statementId"],
                                            label=item["label"], short_label=item["shortLabel"])
        run_write(tx, operations, "upsert_observation", observation)
        reader = Neo4jReader(tx)
        proposed = drafts_from_observation(reader.observation(observation["id"]), reader, registry)
        for draft in proposed.drafts:
            result = submit(tx, draft, registry, operations).validation
            summary["statementProposals"].append((result.outcome.value, result.proposal_id))
        summary["statementProposals"].extend(("unresolved", reason) for reason in proposed.unresolved)
    for item in manifest.get("subjectHeadings", []):
        summary["subjectHeadings"].append(apply_subject_heading(tx, operations, item))
    return summary


def apply_subject_heading(tx: Any, operations: dict[str, str], item: dict[str, Any]) -> str:
    """Attach a curator-approved library subject heading to a Subject (role subject_access)."""
    system, identifier = item["system"], item["identifier"]
    path, metadata = preserved_heading(system, identifier)
    shown = display(system, identifier, metadata["label"])
    run_write(tx, operations, "upsert_subject_authority", {
        "subjectId": item["subjectId"],
        "id": f"chr:authority:{system.lower()}:{identifier}",
        "system": system,
        "identifier": identifier,
        "label": f"{system} heading: {shown}",
        "shortLabel": shown,
        "description": metadata["uri"],
        "retrievedAt": metadata["retrievedAt"],
        "sourceUri": metadata["sourceUri"],
        "contentHash": metadata["contentHash"],
        "rawPayloadUri": path.resolve().relative_to(GRAPH_REVISED.parent).as_posix(),
        "license": metadata["license"],
        "role": "subject_access",
        "relation": item.get("relation", "closeMatch"),
        "linkStatus": "accepted",
    })
    return shown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="apply in a rolled-back transaction and report changes")
    args = parser.parse_args(argv)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                before = tx.run(SNAPSHOT).single().data() if args.dry_run else None
                summary = apply_manifest(tx, manifest, load_operations(), load_registry())
                if args.dry_run:
                    after = tx.run(SNAPSHOT).single().data()
                    added = [item for item in after["nodes"] if item not in before["nodes"]]
                    removed = [item for item in before["nodes"] if item not in after["nodes"]]
                    new_relationships = [r for r in after["relationships"] if r not in before["relationships"]]
                    print(f"dry run: {len(added)} node(s) new or changed, {len(removed)} replaced, "
                          f"{len(new_relationships)} relationship(s) new or changed")
                    for labels, properties in added:
                        print(f"  {labels[0]} {properties.get('id')}: {properties.get('label')}")
                        if labels[0] == "Entity" and properties.get("label"):
                            for match in candidates(tx, properties["label"], properties.get("kind"),
                                                    exclude=properties["id"]):
                                print(f"      possible duplicate ({match['score']:.2f}): {match['id']} "
                                      f"{match['label']} (matched {match['matched']!r})")
                    tx.rollback()
                else:
                    tx.commit()
            except BaseException:
                if tx.closed() is False:
                    tx.rollback()
                raise
    finally:
        driver.close()
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
