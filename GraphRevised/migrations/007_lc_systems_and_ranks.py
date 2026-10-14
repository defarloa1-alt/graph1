"""Migration 007 (2026-10-14): LC identifiers named by their file; crosswalk links carry rank and references.

    python -m GraphRevised.migrations.007_lc_systems_and_ranks [--apply]

1. The harvest stored every Wikidata P244 (Library of Congress Authorities
   ID) under one system, "Library of Congress", so the Battle of Actium's
   sh85000736 was a second record beside the LCSH heading the Subject holds.
   P244 holds both LC files; the system now follows the identifier's prefix
   (harvest rules, federations): sh is LCSH, n the LC Name Authority File
   (LCNAF). A record whose identifier already has a record under the new
   system is retired into it (merge_authority_into: its links move, the
   heading keeps its own words); the others are renamed in place
   (rename_authority_system), their former ID kept.
2. Every crosswalk link records the Wikidata statement's rank and reference
   count (link_authority), read from the preserved payload, so a card can
   show one identifier per system, the best-supported first.

Without --apply it reports and rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from neo4j import GraphDatabase

from GraphRevised.harvest.apply import _slug, federation_system
from GraphRevised.harvest.wikidata_harvest import load_rules
from GraphRevised.operations import load_operations, run_write

REPOSITORY = Path(__file__).resolve().parents[2]

LC_RECORDS = """
MATCH (record:AuthorityRecord {system: "Library of Congress"})<-[:HAS_AUTHORITY_RECORD]-(entity:Entity)
OPTIONAL MATCH (existing:AuthorityRecord {identifier: record.identifier}) WHERE existing <> record
RETURN record {.id, .identifier} AS record, entity.label AS entity,
       collect(existing {.id, .system}) AS existing
ORDER BY record.id
"""
CROSSWALK_LINKS = """
MATCH (entity:Entity)-[link:HAS_AUTHORITY_RECORD {role: "crosswalk"}]->(record:AuthorityRecord)
OPTIONAL MATCH (entity)-[:HAS_AUTHORITY_RECORD {role: "entity_identity"}]->(identity:AuthorityRecord {system: "Wikidata"})
RETURN entity.id AS entityId, identity.identifier AS qid, link {.role, .relation, .status} AS link,
       record {.system, .identifier, .rawPayloadUri} AS record, identity.rawPayloadUri AS identityPayload
ORDER BY entityId, record.system, record.identifier
"""


def rename_lc(tx, operations, rules, apply: bool) -> list[str]:
    lines = []
    for row in tx.run(LC_RECORDS).data():
        record = row["record"]
        system = federation_system(rules, "P244", record["identifier"])
        target = next((e for e in row["existing"] if e["system"] == system), None)
        if target:
            lines.append(f"retire {record['id']} into {target['id']}")
            if apply:
                run_write(tx, operations, "merge_authority_into", {"id": record["id"], "targetId": target["id"]})
            continue
        new_id = f"chr:authority:{_slug(system)}:{_slug(record['identifier'])}"
        lines.append(f"rename {record['id']} -> {new_id}")
        if apply:
            run_write(tx, operations, "rename_authority_system", {
                "id": record["id"], "newId": new_id, "system": system,
                "label": f"{row['entity']} in {system} ({system} {record['identifier']})",
                "shortLabel": f"{system}: {row['entity']}"})
    return lines


def _statement(payload: Path, qid: str, rules, system: str, identifier: str) -> tuple[str, int] | None:
    """The rank and reference count of the non-deprecated statement that gave this identifier."""
    if not (payload.name.startswith("wikidata-") and payload.suffix == ".json" and payload.exists()):
        return None  # a heading's own record (LCSH, FAST) is not a Wikidata payload
    entity = json.loads(payload.read_bytes()).get("entities", {}).get(qid)
    if entity is None:
        return None
    for pid in rules["federations"]:
        for claim in entity.get("claims", {}).get(pid, []):
            value = claim["mainsnak"].get("datavalue", {}).get("value")
            if (claim.get("rank") != "deprecated" and value == identifier
                    and federation_system(rules, pid, value) == system):
                return claim.get("rank", "normal"), len(claim.get("references", []))
    return None


def backfill_ranks(tx, operations, rules, apply: bool) -> tuple[list[str], list[str]]:
    lines, missing = [], []
    for row in tx.run(CROSSWALK_LINKS).data():
        record, found = row["record"], None
        for uri in (record["rawPayloadUri"], row["identityPayload"]):
            if uri and row["qid"]:
                found = _statement(REPOSITORY / uri, row["qid"], rules, record["system"], record["identifier"])
                if found:
                    break
        if found is None:
            missing.append(f"{row['entityId']} {record['system']} {record['identifier']}")
            continue
        lines.append(f"{row['entityId']} {record['system']} {record['identifier']}: {found[0]}, {found[1]} ref(s)")
        if apply:
            run_write(tx, operations, "link_authority", {
                "entityId": row["entityId"], "system": record["system"], "identifier": record["identifier"],
                "role": row["link"]["role"], "relation": row["link"]["relation"], "linkStatus": row["link"]["status"],
                "statementRank": found[0], "statementReferences": found[1]})
    return lines, missing


def migrate(tx, apply: bool) -> dict[str, list[str]]:
    operations, rules = load_operations(), load_rules()
    systems = rename_lc(tx, operations, rules, apply)
    if not apply:
        # The dry run reads ranks as they would be after the renames, in the same rolled-back transaction.
        rename_lc(tx, operations, rules, True)
    ranks, missing = backfill_ranks(tx, operations, rules, True)
    return {"systems": systems, "ranks": ranks, "missing": missing}


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
                result = migrate(tx, args.apply)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    verb = "" if args.apply else "would "
    print(f"{verb}move {len(result['systems'])} LC record(s):")
    print("\n".join(f"  {line}" for line in result["systems"]))
    print(f"{verb}record rank and references on {len(result['ranks'])} crosswalk link(s)")
    print("\n".join(f"  {line}" for line in result["ranks"]))
    if result["missing"]:
        print(f"no statement found for {len(result['missing'])} link(s):")
        print("\n".join(f"  {line}" for line in result["missing"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
