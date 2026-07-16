#!/usr/bin/env python3
"""Patch CorpusWork.title in Neo4j from enriched proposal bibliography."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "agents" / "domain_initiator"))

from config_loader import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME  # noqa: E402
from neo4j import GraphDatabase  # noqa: E402
from proposal_backbone import (  # noqa: E402
    build_work_index,
    normalize_corpus_work,
    title_quality,
)


def main() -> int:
    seed = "Q17167"
    work_index = build_work_index(ROOT / "output" / "di_training", seed)
    enriched = ROOT / "output" / "di_proposals" / f"{seed}_proposals_enriched.json"
    doc = json.loads(enriched.read_text(encoding="utf-8"))

    by_id: dict[str, dict] = {}
    for proposal in doc.get("proposals", []):
        for work in proposal.get("supporting_works") or []:
            if not isinstance(work, dict):
                continue
            row = normalize_corpus_work(work)
            wid = row.get("work_id")
            if not wid:
                continue
            if title_quality(row.get("title", ""), wid) > title_quality(
                by_id.get(wid, {}).get("title", ""), wid
            ):
                by_id[wid] = row

    for wid, row in work_index.items():
        if title_quality(row.get("title", ""), wid) > title_quality(
            by_id.get(wid, {}).get("title", ""), wid
        ):
            by_id[wid] = row

    updates = [
        (wid, row["title"])
        for wid, row in by_id.items()
        if title_quality(row.get("title", ""), wid) > 0
    ]
    print(f"Patching up to {len(updates)} CorpusWork titles")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    patched = 0
    try:
        with driver.session() as session:
            for wid, title in updates:
                result = session.run(
                    """
                    MATCH (cw:CorpusWork {work_id: $work_id})
                    WHERE cw.title = $work_id
                       OR cw.title STARTS WITH 'openalex:'
                       OR cw.title STARTS WITH 'ia:'
                    SET cw.title = $title
                    RETURN count(cw) AS n
                    """,
                    work_id=wid,
                    title=title,
                ).single()
                patched += int(result["n"]) if result else 0
    finally:
        driver.close()

    print(f"Neo4j CorpusWork nodes patched: {patched}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
