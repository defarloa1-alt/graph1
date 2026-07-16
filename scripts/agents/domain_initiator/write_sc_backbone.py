#!/usr/bin/env python3
"""
Write SubjectConcept backbone + CorpusWork biblio layer to Chrystallum 2.0.

Reads:
  - output/di_proposals/Q17167_proposals.json   (43 SubjectConcept nodes)
  - output/di_training/Q17167_*_corpus.json     (CorpusWork biblio nodes)
  - output/di_training/Q17167_*_training.json   (discovered_works + key_works)

Writes to Neo4j 2.0:
  - SubjectConcept nodes (label, description, confidence, lcsh_id, lcsh_label,
                          candidate_qids, concept_cipher, source_facet)
  - CorpusWork nodes for all 13 facets (skips duplicates via MERGE on work_id+facet)
  - (SubjectConcept)-[:HAS_FACET {weight}]->(Facet)
  - (CorpusWork)-[:SUPPORTS]->(SubjectConcept) by facet_key match

Usage:
  python scripts/agents/domain_initiator/write_sc_backbone.py
  python scripts/agents/domain_initiator/write_sc_backbone.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

TRAINING_DIR = ROOT / "output" / "di_training"
PROPOSALS_PATH = ROOT / "output" / "di_proposals" / "Q17167_proposals.json"

FACETS = [
    "archaeological", "artistic", "communication", "cultural", "demographic",
    "economic", "intellectual", "linguistic", "military", "political",
    "religious", "scientific", "social",
]


def load_proposals() -> list[dict]:
    with open(PROPOSALS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data["proposals"]


def load_corpus(facet: str) -> list[dict]:
    path = TRAINING_DIR / f"Q17167_{facet.upper()}_corpus.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_training(facet: str) -> dict:
    path = TRAINING_DIR / f"Q17167_{facet.upper()}_training.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_backbone(dry_run: bool = False):
    proposals = load_proposals()
    print(f"Proposals: {len(proposals)}")

    if not dry_run:
        from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    else:
        driver = None

    def run(session: Any, query: str, **params):
        if dry_run:
            return
        session.run(query, **params)

    # -----------------------------------------------------------------------
    # 1. SubjectConcept nodes
    # -----------------------------------------------------------------------
    print("\n--- SubjectConcept nodes ---")
    sc_written = 0

    ctx = driver.session() if driver else None

    for p in proposals:
        cipher = p.get("concept_cipher", "")
        if not cipher:
            print(f"  SKIP (no cipher): {p.get('label')}")
            continue

        props = {
            "cipher": cipher,
            "label": p.get("label", ""),
            "description": p.get("description", ""),
            "seed_qid": p.get("seed_qid", "Q17167"),
            "source_facet": p.get("source_facet", ""),
            "proposal_type": p.get("proposal_type", "decomposition"),
            "confidence": float(p.get("confidence") or 0.0),
            "scope_key": p.get("scope_key", ""),
            "estimated_concepts": int(p.get("estimated_concepts") or 0),
            "needs": p.get("needs", ""),
            "lcsh_id": p.get("lcsh_id", ""),
            "lcsh_label": p.get("lcsh_label", ""),
            "candidate_qids": json.dumps(p.get("candidate_qids", [])),
            "status": "proposed",
        }

        if not dry_run:
            ctx.run("""
                MERGE (sc:SubjectConcept {concept_cipher: $cipher})
                SET sc.label = $label,
                    sc.description = $description,
                    sc.seed_qid = $seed_qid,
                    sc.source_facet = $source_facet,
                    sc.proposal_type = $proposal_type,
                    sc.confidence = $confidence,
                    sc.scope_key = $scope_key,
                    sc.estimated_concepts = $estimated_concepts,
                    sc.needs = $needs,
                    sc.lcsh_id = $lcsh_id,
                    sc.lcsh_label = $lcsh_label,
                    sc.candidate_qids = $candidate_qids,
                    sc.status = $status
            """, **props)

        # HAS_FACET edges from facet_weights
        facet_weights = p.get("facet_weights", {})
        primary = p.get("source_facet", "")
        # Ensure primary facet has weight=1.0
        if primary and primary not in facet_weights:
            facet_weights[primary] = 1.0

        for facet_key, weight in facet_weights.items():
            if weight and float(weight) > 0.1:
                if not dry_run:
                    ctx.run("""
                        MATCH (sc:SubjectConcept {concept_cipher: $cipher})
                        MATCH (f:Facet) WHERE toLower(f.label) = $facet_key
                        MERGE (sc)-[r:HAS_FACET]->(f)
                        SET r.weight = $weight
                    """, cipher=cipher, facet_key=facet_key.lower(), weight=float(weight))

        sc_written += 1
        print(f"  {'[DRY]' if dry_run else 'OK'} [{p.get('source_facet'):12s}] {p.get('label')}"
              + (f" | lcsh={p.get('lcsh_id', '-')}" if p.get('lcsh_id') else "")
              + (f" | {len(p.get('candidate_qids',[]))} QIDs" if p.get('candidate_qids') else ""))

    print(f"SubjectConcepts: {sc_written} written")

    # -----------------------------------------------------------------------
    # 2. CorpusWork nodes (biblio layer)
    # -----------------------------------------------------------------------
    print("\n--- CorpusWork biblio layer ---")
    cw_written = 0
    cw_skipped = 0

    for facet in FACETS:
        works = load_corpus(facet)
        training = load_training(facet)

        # Merge corpus + discovered_works from training
        all_works: list[dict] = list(works)
        for w in training.get("discovered_works", []):
            if not any(x.get("work_id") == w.get("work_id") for x in all_works):
                all_works.append(w)

        # Annotate key_works with relevance
        key_work_ids = {kw["work_id"]: kw for kw in training.get("key_works", [])}

        print(f"  {facet:15s}: {len(all_works)} works")

        for w in all_works:
            work_id = w.get("work_id", "")
            if not work_id:
                cw_skipped += 1
                continue

            kw_meta = key_work_ids.get(work_id, {})
            props = {
                "work_id": work_id,
                "facet_key": facet.upper(),
                "seed_qid": "Q17167",
                "title": str(w.get("title", ""))[:500],
                "authors": str(w.get("authors", ""))[:300],
                "year": int(w["year"]) if w.get("year") and str(w["year"]).lstrip("-").isdigit() else None,
                "citation_count": int(w.get("citation_count") or 0),
                "abstract": str(w.get("abstract", ""))[:1000],
                "doi": str(w.get("doi", ""))[:200],
                "source": str(w.get("source", "")),
                "source_url": str(w.get("source_url", ""))[:500],
                "is_oa": bool(w.get("is_oa", False)),
                "oa_url": str(w.get("oa_url", ""))[:500],
                "facet_relevance": kw_meta.get("relevance", w.get("relevance", "")),
                "facet_contribution": str(kw_meta.get("facet_contribution", w.get("facet_contribution", "")))[:500],
            }

            if not dry_run:
                ctx.run("""
                    MERGE (cw:CorpusWork {work_id: $work_id, facet_key: $facet_key})
                    SET cw.seed_qid = $seed_qid,
                        cw.title = $title,
                        cw.authors = $authors,
                        cw.year = $year,
                        cw.citation_count = $citation_count,
                        cw.abstract = $abstract,
                        cw.doi = $doi,
                        cw.source = $source,
                        cw.source_url = $source_url,
                        cw.is_oa = $is_oa,
                        cw.oa_url = $oa_url,
                        cw.facet_relevance = $facet_relevance,
                        cw.facet_contribution = $facet_contribution
                """, **props)
            cw_written += 1

        # Wire CorpusWork → SubjectConcept (SUPPORTS) by facet_key
        if not dry_run:
            ctx.run("""
                MATCH (cw:CorpusWork {facet_key: $facet_key, seed_qid: 'Q17167'})
                MATCH (sc:SubjectConcept {source_facet: $source_facet, seed_qid: 'Q17167'})
                MERGE (cw)-[:SUPPORTS]->(sc)
            """, facet_key=facet.upper(), source_facet=facet)

    print(f"CorpusWork: {cw_written} written, {cw_skipped} skipped")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    if not dry_run:
        ctx.close()
        driver.close()

        # Verify
        from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
        from neo4j import GraphDatabase
        d2 = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        with d2.session() as s:
            r = s.run("MATCH (n) WHERE n:SubjectConcept OR n:CorpusWork RETURN labels(n)[0], count(*)")
            print("\n--- Verification ---")
            for row in r:
                print(f"  {row[0]}: {row[1]}")
            r = s.run("MATCH (sc:SubjectConcept)-[:HAS_FACET]->(f:Facet) RETURN count(*)")
            print(f"  HAS_FACET edges: {r.single()[0]}")
            r = s.run("MATCH (cw:CorpusWork)-[:SUPPORTS]->(sc:SubjectConcept) RETURN count(*)")
            print(f"  SUPPORTS edges: {r.single()[0]}")
        d2.close()

    print("\nDone.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    write_backbone(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
