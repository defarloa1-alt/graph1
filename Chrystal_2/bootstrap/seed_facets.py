#!/usr/bin/env python3
"""Seed 18 Facet nodes + FacetRegistry on Chrystal 2 (empty / Years-only graph).

Reads Facets/facet_registry_master.csv (dedupe by facet_key).
Uses UPPERCASE keys to match Domain Initiator / training contract.

Usage (from repo root, .env → 7fe339d2):
  python chrystal_2/bootstrap/seed_facets.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase

from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

CSV_PATH = ROOT / "Facets" / "facet_registry_master.csv"

# Discipline-grounding QIDs (history-of / field), from backfill_facet_qids.py
FACET_QIDS: dict[str, tuple[str, str]] = {
    "ARCHAEOLOGICAL": ("Q23498", "archaeology"),
    "ARTISTIC": ("Q50637", "art history"),
    "BIOGRAPHIC": ("Q36279", "biography"),
    "COMMUNICATION": ("Q11680831", "communication studies"),
    "CULTURAL": ("Q858517", "cultural history"),
    "DEMOGRAPHIC": ("Q37732", "demography"),
    "DIPLOMATIC": ("Q2177756", "diplomatic history"),
    "ECONOMIC": ("Q47398", "economic history"),
    "ENVIRONMENTAL": ("Q1561862", "environmental history"),
    "GEOGRAPHIC": ("Q384001", "historical geography"),
    "INTELLECTUAL": ("Q1195695", "intellectual history"),
    "LINGUISTIC": ("Q190375", "historical linguistics"),
    "MILITARY": ("Q192781", "military history"),
    "POLITICAL": ("Q1147507", "political history"),
    "RELIGIOUS": ("Q846742", "history of religions"),
    "SCIENTIFIC": ("Q201486", "history of science"),
    "SOCIAL": ("Q908604", "social history"),
    "TECHNOLOGICAL": ("Q465352", "history of technology"),
}

DESCRIPTIONS: dict[str, str] = {
    "ARCHAEOLOGICAL": "Material remains, excavation, and the physical traces of past societies.",
    "ARTISTIC": "Visual arts, architecture, aesthetics, and cultural production.",
    "BIOGRAPHIC": "Individual lives, careers, identity, and prosopographical methods.",
    "COMMUNICATION": "Rhetoric, writing, oral tradition, and channels of information exchange.",
    "CULTURAL": "Mentalities, worldviews, cultural exchange, and symbolic systems.",
    "DEMOGRAPHIC": "Population size, structure, migration, family, and mortality patterns.",
    "DIPLOMATIC": "Foreign policy, treaties, international relations, and diplomacy.",
    "ECONOMIC": "Trade, finance, labor, markets, and economic institutions.",
    "ENVIRONMENTAL": "Climate, ecology, disease, land use, and human-environment interaction.",
    "GEOGRAPHIC": "Place, territory, landscape, cartography, and spatial analysis.",
    "INTELLECTUAL": "Philosophy, history of ideas, and the development of thought.",
    "LINGUISTIC": "Language change, multilingualism, epigraphy, and literacy.",
    "MILITARY": "Warfare, strategy, command, logistics, and the military-political nexus.",
    "POLITICAL": "Governance, state formation, political thought, and institutions.",
    "RELIGIOUS": "Ritual, theology, scripture, and the intersection of religion and power.",
    "SCIENTIFIC": "Natural philosophy, scientific method, and the history of science.",
    "SOCIAL": "Class, gender, community, family, and social theory.",
    "TECHNOLOGICAL": "Innovation, infrastructure, military technology, and diffusion of techniques.",
}


def load_facets_from_csv(path: Path) -> list[dict[str, str]]:
    by_key: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            raw = (row.get("facet_key") or "").strip().lower()
            if not raw:
                continue
            key = raw.upper()
            if key in by_key:
                continue
            by_key[key] = {
                "key": key,
                "label": (row.get("facet_label") or key.title()).strip(),
                "facet_class": (row.get("facet_class") or "").strip(),
            }
    return [by_key[k] for k in sorted(by_key)]


def main() -> int:
    if "7fe339d2" not in (NEO4J_URI or ""):
        print(f"Refusing: NEO4J_URI is not chrystal_2 (7fe339d2): {NEO4J_URI}")
        return 2
    if not CSV_PATH.exists():
        print(f"Missing {CSV_PATH}")
        return 2

    facets = load_facets_from_csv(CSV_PATH)
    print(f"CSV unique facets: {len(facets)}")
    if len(facets) != 18:
        print(f"WARNING: expected 18, got {len(facets)}")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    db = NEO4J_DATABASE or "neo4j"
    try:
        with driver.session(database=db) as session:
            session.run(
                """
                MERGE (fr:FacetRegistry {key: 'chrystallum_facets_v1'})
                SET fr.label = 'Chrystallum Facet Registry',
                    fr.version = '1.0',
                    fr.description = $desc,
                    fr.facet_count = $n,
                    fr.instance = 'chrystal_2'
                """,
                desc=(
                    "Authoritative set of analytical facets for decomposing historical "
                    "and global-discipline domains. Chrystal 2 bootstrap."
                ),
                n=len(facets),
            )
            for row in facets:
                key = row["key"]
                qid, wlabel = FACET_QIDS.get(key, (None, None))
                session.run(
                    """
                    MERGE (f:Facet {key: $key})
                    SET f.label = $label,
                        f.facet_class = $facet_class,
                        f.description = $description,
                        f.facet_type = 'subject_domain',
                        f.di_trainable = true,
                        f.qid = $qid,
                        f.wikidata_label = $wlabel
                    WITH f
                    MATCH (fr:FacetRegistry {key: 'chrystallum_facets_v1'})
                    MERGE (fr)-[:CONTAINS]->(f)
                    """,
                    key=key,
                    label=row["label"],
                    facet_class=row["facet_class"],
                    description=DESCRIPTIONS.get(key, ""),
                    qid=qid,
                    wlabel=wlabel,
                )
                print(f"  {key:16} {row['label']:16} {qid or ''}")

            n = session.run("MATCH (f:Facet) RETURN count(f) AS c").single()["c"]
            wired = session.run(
                """
                MATCH (:FacetRegistry {key: 'chrystallum_facets_v1'})-[:CONTAINS]->(f:Facet)
                RETURN count(f) AS c
                """
            ).single()["c"]
            print(f"Facet nodes: {n}; registry CONTAINS: {wired}")
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
