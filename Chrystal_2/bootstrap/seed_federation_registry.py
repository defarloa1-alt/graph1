#!/usr/bin/env python3
"""Seed SYS_FederationRegistry + global federation sources for Chrystal 2.

Loads FederationCards from chrystal_2/federations/*.json into Neo summary
properties + model_path. Sources are global / unattached to any Domain.

Refuses unless NEO4J_URI hosts 7fe339d2.

Usage (repo root):
  python chrystal_2/bootstrap/seed_federation_registry.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase

from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

CARDS_DIR = ROOT / "Chrystal_2" / "federations"
if not CARDS_DIR.exists():
    CARDS_DIR = ROOT / "chrystal_2" / "federations"

# Bootstrap order — global only (pack-scoped federations attach later)
GLOBAL_CARDS = [
    "wikidata.json",
    "viaf.json",
    "openalex.json",
    "lcsh_fast_lcc.json",
    "periodo.json",
    "pleiades.json",
]


def main() -> int:
    if "7fe339d2" not in (NEO4J_URI or ""):
        print(f"Refusing: NEO4J_URI is not chrystal_2 (7fe339d2): {NEO4J_URI}")
        return 2

    cards: list[tuple[Path, dict]] = []
    for name in GLOBAL_CARDS:
        path = CARDS_DIR / name
        if not path.exists():
            print(f"Missing card: {path}")
            return 2
        cards.append((path, json.loads(path.read_text(encoding="utf-8"))))

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    db = NEO4J_DATABASE or "neo4j"
    try:
        with driver.session(database=db) as session:
            session.run(
                """
                MERGE (fr:SYS_FederationRegistry {system: true})
                SET fr.label = 'FederationRegistry',
                    fr.instance = 'chrystal_2',
                    fr.version = '0.1',
                    fr.description = $desc
                WITH fr
                OPTIONAL MATCH (sr:SYS_SchemaRegistry {system: true})
                FOREACH (_ IN CASE WHEN sr IS NULL THEN [] ELSE [1] END |
                  MERGE (sr)-[:HAS_FEDERATION_REGISTRY]->(fr)
                )
                """,
                desc=(
                    "Global federation catalog for Chrystal 2. Domain packs attach "
                    "additional sources later. Each source has a FederationCard JSON."
                ),
            )
            print("SYS_FederationRegistry: ok")

            for path, card in cards:
                source_id = card["source_id"]
                rel_path = str(path.relative_to(ROOT)).replace("\\", "/")
                tools = card.get("tool_names") or []
                caps = card.get("query_capabilities") or []
                entities = card.get("entity_types") or []
                session.run(
                    """
                    MERGE (fs:SYS_FederationSource {source_id: $source_id})
                    SET fs.label = $label,
                        fs.status = $status,
                        fs.scope = $scope,
                        fs.access_pattern = $access_pattern,
                        fs.endpoint = $endpoint,
                        fs.auth = $auth,
                        fs.license = $license,
                        fs.description = $notes,
                        fs.entity_types = $entity_types,
                        fs.query_capabilities = $capabilities,
                        fs.tool_names = $tools,
                        fs.model_path = $model_path,
                        fs.has_federation_card = true,
                        fs.system = true,
                        fs.ship_set = 'chrystal_2_global',
                        fs.instance = 'chrystal_2'
                    WITH fs
                    MATCH (fr:SYS_FederationRegistry {system: true})
                    MERGE (fr)-[:CONTAINS]->(fs)
                    """,
                    source_id=source_id,
                    label=card.get("label") or source_id,
                    status=card.get("status") or "planned",
                    scope=card.get("scope") or "global",
                    access_pattern=card.get("access_pattern"),
                    endpoint=card.get("endpoint"),
                    auth=card.get("auth"),
                    license=card.get("license"),
                    notes=card.get("notes") or card.get("description"),
                    entity_types=entities,
                    capabilities=caps,
                    tools=tools,
                    model_path=rel_path,
                )
                print(f"  + {source_id:16} card={rel_path}")

            n = session.run(
                "MATCH (fs:SYS_FederationSource) RETURN count(fs) AS c"
            ).single()["c"]
            linked = session.run(
                """
                MATCH (:SYS_FederationRegistry)-[:CONTAINS]->(fs:SYS_FederationSource)
                RETURN count(fs) AS c
                """
            ).single()["c"]
            print(f"SYS_FederationSource: {n}; CONTAINS: {linked}")
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
