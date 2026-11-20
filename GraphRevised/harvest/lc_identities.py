"""Library identities from Wikidata, in the authority's own words: LCNAF, LCSH and FAST.

    python -m GraphRevised.harvest.lc_identities [--apply]

Curator, 2026-11-19: an entity the Library of Congress or OCLC holds a record for should carry
it, so a book about a person or a place is one hop from them. For every Entity with a preserved
Wikidata identity payload, its Library of Congress (P244: `sh...` is LCSH, `n...` is LCNAF) and
FAST (P2163) identifiers become AuthorityRecords, matched by identifier, never by name. Each
record is fetched once from id.loc.gov or OCLC and preserved (adapters/library_headings.py), and
its label is the authority's own heading (the LCNAF heading's name and dates, with its code beside it), so
a code is never shown without its words.

Records already in the graph whose label was composed from our name ("Battle of Philippi in
LCSH (LCSH sh2008009949)", harvest/apply.py before this) are relabelled the same way.

The links are crosswalks (closeMatch), accepted by rule: the identifier is Wikidata's statement,
read by code (D-145). A deprecated statement is skipped. Without --apply it reports and rolls
back; fetched records stay preserved either way. Retry-safe.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.adapters.library_headings import HeadingError, display, preserved_heading
from GraphRevised.operations import load_operations, run_write
from GraphRevised import localdb

GRAPH_REVISED = Path(__file__).resolve().parents[1]
REPOSITORY = GRAPH_REVISED.parent
RUNS = GRAPH_REVISED / "runs"
PROPERTIES = {"P244": None, "P2163": "FAST"}  # P244's system is read from the identifier's prefix
OUR_WORDS = re.compile(r".* in (LCSH|LCNAF|FAST) \(")
PAUSE = 0.4  # seconds between fetches, to be polite to id.loc.gov and OCLC

IDENTITIES = """
MATCH (e:Entity)-[l:HAS_AUTHORITY_RECORD]->(w:AuthorityRecord {system: 'Wikidata'})
WHERE l.role = 'entity_identity' AND w.rawPayloadUri IS NOT NULL AND e.status <> 'deprecated'
RETURN e.id AS entity, e.label AS label, w.identifier AS qid, w.rawPayloadUri AS payload ORDER BY e.id
"""
RECORD = "MATCH (a:AuthorityRecord {system: $system, identifier: $identifier}) RETURN a.id AS id, a.label AS label"
IN_OUR_WORDS = """
MATCH (e:Entity)-[:HAS_AUTHORITY_RECORD]->(a:AuthorityRecord)
WHERE a.system IN ['LCSH', 'LCNAF', 'FAST'] AND a.label =~ '.* in (LCSH|LCNAF|FAST) \\\\(.*'
RETURN e.id AS entity, a.id AS id, a.system AS system, a.identifier AS identifier
"""


def system_of(pid: str, value: str) -> str | None:
    if pid == "P244":
        return "LCSH" if value.startswith("sh") else "LCNAF" if value.startswith("n") else None
    return PROPERTIES[pid]


def identifiers(payload_path: Path, qid: str) -> list[dict[str, Any]]:
    """The entity's LC and FAST statements: system, identifier, rank, reference count."""
    entity = json.loads(payload_path.read_bytes())["entities"][qid]
    found = []
    for pid in PROPERTIES:
        for claim in entity.get("claims", {}).get(pid, []):
            value = claim.get("mainsnak", {}).get("datavalue", {}).get("value")
            if not isinstance(value, str) or claim.get("rank") == "deprecated":
                continue
            system = system_of(pid, value)
            if system:
                found.append({"system": system, "identifier": value, "rank": claim.get("rank"),
                              "references": len(claim.get("references", []))})
    return found


def heading(system: str, identifier: str, fetched: dict) -> tuple[Path, dict[str, Any]] | None:
    key = (system, identifier)
    if key not in fetched:
        try:
            path, metadata = preserved_heading(system, identifier)
            fetched[key] = (path, metadata)
            time.sleep(PAUSE)
        except (HeadingError, OSError) as error:  # requests' errors are OSErrors
            fetched[key] = None
            print(f"  {system} {identifier}: {error}")
    return fetched[key]


def record_params(entity: str, system: str, identifier: str, existing_id: str | None,
                  path: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    label = metadata["label"]
    return {"entityId": entity, "id": existing_id or f"chr:authority:{system.lower()}:{identifier.lower()}",
            "system": system, "identifier": identifier, "label": display(system, identifier, label),
            "shortLabel": f"{system}: {label}", "description": None,
            "retrievedAt": metadata["retrievedAt"], "sourceUri": metadata["sourceUri"], "sourceRevision": None,
            "contentHash": metadata["contentHash"],
            "rawPayloadUri": path.resolve().relative_to(REPOSITORY).as_posix(),
            "role": "crosswalk", "relation": "closeMatch", "linkStatus": "accepted"}


def harvest(tx, operations, fetched: dict) -> dict[str, Any]:
    report: dict[str, Any] = {"linked": [], "relabelled": [], "alreadyHeld": 0, "unfetched": []}
    for row in tx.run(IDENTITIES).data():
        path = REPOSITORY / row["payload"]
        if not path.exists():
            continue
        for found in identifiers(path, row["qid"]):
            system, identifier = found["system"], found["identifier"]
            existing = tx.run(RECORD, system=system, identifier=identifier).single()
            held = existing and not OUR_WORDS.match(existing["label"] or "")
            link = {"entityId": row["entity"], "system": system, "identifier": identifier, "role": "crosswalk",
                    "relation": "closeMatch", "linkStatus": "accepted", "statementRank": found["rank"],
                    "statementReferences": found["references"]}
            if held:  # the record already has the authority's words: only link it
                linked = tx.run("MATCH (:Entity {id: $e})-[:HAS_AUTHORITY_RECORD]->(:AuthorityRecord {system: $s, "
                                "identifier: $i}) RETURN count(*) > 0 AS linked", e=row["entity"], s=system,
                                i=identifier).single()["linked"]
                run_write(tx, operations, "link_authority", link)
                if linked:
                    report["alreadyHeld"] += 1
                else:
                    report["linked"].append(f"{row['label']}: {existing['label']}")
                continue
            got = heading(system, identifier, fetched)
            if got is None:
                report["unfetched"].append(f"{row['label']}: {system} {identifier}")
                continue
            params = record_params(row["entity"], system, identifier, existing and existing["id"], *got)
            run_write(tx, operations, "upsert_authority", params)
            run_write(tx, operations, "link_authority", link)
            report["relabelled" if existing else "linked"].append(f"{row['label']}: {params['label']}")
    for row in tx.run(IN_OUR_WORDS).data():  # what no payload restated: relabel from the authority
        got = heading(row["system"], row["identifier"], fetched)
        if got is None:
            report["unfetched"].append(f"{row['entity']}: {row['system']} {row['identifier']}")
            continue
        params = record_params(row["entity"], row["system"], row["identifier"], row["id"], *got)
        run_write(tx, operations, "upsert_authority", params)
        report["relabelled"].append(f"{row['entity']}: {params['label']}")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    driver = GraphDatabase.driver(
        localdb.uri(),
        auth=localdb.auth(),
        notifications_min_severity="OFF",
    )
    fetched: dict = {}
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                report = harvest(tx, load_operations(), fetched)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                tx.rollback()
                raise
    finally:
        driver.close()
    report["applied"] = args.apply
    RUNS.mkdir(exist_ok=True)
    out = RUNS / f"lc-identities-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"linked {len(report['linked'])}, relabelled {len(report['relabelled'])}, already held "
          f"{report['alreadyHeld']}, unfetched {len(report['unfetched'])}; report {out.relative_to(REPOSITORY)}")
    print("applied" if args.apply else "dry run: rolled back")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
