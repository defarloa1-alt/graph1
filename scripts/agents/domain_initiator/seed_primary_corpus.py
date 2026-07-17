#!/usr/bin/env python3
"""
Seed primary CorpusWork nodes and wire HAS_BIBLIO to biographic SubjectConcepts (ADR-021).

Usage:
  python scripts/agents/domain_initiator/seed_primary_corpus.py --dry
  python scripts/agents/domain_initiator/seed_primary_corpus.py --write
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME  # noqa: E402
from neo4j import GraphDatabase  # noqa: E402

from scripts.agents.domain_initiator.proposal_backbone import normalize_corpus_work  # noqa: E402

CATALOG = Path(__file__).resolve().parent / "primary_corpus_catalog.json"

SCOPE_TO_SUBJECT: dict[str, str] = {
    "senatorial_elite_careers": "sc_q17167_senatorial_elite_careers",
    "populist_political_figures": "sc_q17167_populist_political_figures",
    "military_commanders": "sc_q17167_military_commanders",
    "late_republic_leaders": "sc_q17167_late_republic_leaders",
    "women_and_non_elite": "sc_q17167_women_and_non_elite",
    "onomastics_nomenclature": "sc_q17167_onomastics_nomenclature",
    "ancient_biographical_sources": "sc_q17167_ancient_biographical_sources",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed primary corpus works for biographic SCs")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry", action="store_true")
    args = parser.parse_args()
    dry = not args.write

    if not CATALOG.exists():
        print(f"Catalog not found: {CATALOG}", file=sys.stderr)
        return 1
    if not NEO4J_PASSWORD:
        print("NEO4J_PASSWORD not configured", file=sys.stderr)
        return 1

    with open(CATALOG, encoding="utf-8") as f:
        catalog = json.load(f)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    works_written = 0
    biblio_edges = 0

    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            for raw in catalog.get("works", []):
                work = normalize_corpus_work(raw)
                if not work.get("work_id"):
                    continue
                work["corpus_tier"] = raw.get("corpus_tier") or work.get("corpus_tier") or "primary"
                work["source_era"] = raw.get("source_era") or work.get("source_era") or "near_contemporary"
                work["seed_qid"] = catalog.get("seed_qid", "Q17167")
                work["facet_key"] = "BIOGRAPHIC"

                if not dry:
                    session.run(
                        """
                        MERGE (cw:CorpusWork {work_id: $work_id})
                        SET cw.title = $title,
                            cw.authors = $authors,
                            cw.year = $year,
                            cw.source = $source,
                            cw.source_url = $source_url,
                            cw.corpus_tier = $corpus_tier,
                            cw.source_era = $source_era,
                            cw.seed_qid = $seed_qid,
                            cw.facet_key = $facet_key
                        """,
                        **{k: work.get(k) for k in (
                            "work_id", "title", "authors", "year", "source", "source_url",
                            "corpus_tier", "source_era", "seed_qid", "facet_key",
                        )},
                    )
                works_written += 1

                for rank, scope_key in enumerate(raw.get("scope_keys") or [], start=1):
                    subject_id = SCOPE_TO_SUBJECT.get(scope_key)
                    if not subject_id:
                        continue
                    if not dry:
                        session.run(
                            """
                            MATCH (cw:CorpusWork {work_id: $work_id})
                            MATCH (sc:SubjectConcept {subject_id: $subject_id})
                            MERGE (sc)-[r:HAS_BIBLIO]->(cw)
                            SET r.rank = $rank,
                                r.corpus_tier = $corpus_tier,
                                r.source_era = $source_era
                            """,
                            work_id=work["work_id"],
                            subject_id=subject_id,
                            rank=rank,
                            corpus_tier=work["corpus_tier"],
                            source_era=work["source_era"],
                        )
                    biblio_edges += 1

    finally:
        driver.close()

    print(f"CorpusWork nodes: {works_written}  HAS_BIBLIO edges: {biblio_edges}  dry={dry}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
