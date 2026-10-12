"""Local-first identity: existing entities that a new one might duplicate.

    python -m GraphRevised.identity.local_candidates "unconventional warfare" [--kind Concept]

Before a new Entity is created (a curated identity, a Concept, a depicted
event), its label is compared with the labels, short labels, and Wikidata
aliases of existing Entities of the same kind. Candidates are reported for
the curator; nothing is merged or created here.
"""

from __future__ import annotations

import argparse
import os
import re
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.adapters.wikidata_context import entity_context

STOPWORDS = {"the", "of", "a", "an", "and", "at", "in", "on", "for", "to", "by", "versus", "vs"}


def tokens(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in STOPWORDS}


def similarity(a: str, b: str) -> float:
    """1.0 for the same words; 0.8 when one name's words contain the other's; else word overlap (Jaccard)."""
    left, right = tokens(a), tokens(b)
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    if left <= right or right <= left:
        return 0.8
    return len(left & right) / len(left | right)


def candidates(tx: Any, label: str, kind: str | None = None, *, exclude: str | None = None,
               threshold: float = 0.5, limit: int = 5) -> list[dict[str, Any]]:
    rows = tx.run(
        """
        MATCH (entity:Entity) WHERE ($kind IS NULL OR entity.kind = $kind) AND entity.id <> coalesce($exclude, '')
        OPTIONAL MATCH (entity)-[link:HAS_AUTHORITY_RECORD]->(record:AuthorityRecord {system: "Wikidata"})
        WHERE link.role = "entity_identity"
        RETURN entity.id AS id, entity.label AS label, entity.shortLabel AS shortLabel, entity.kind AS kind,
               head(collect(record.identifier)) AS qid, head(collect(record.rawPayloadUri)) AS payloadUri
        """,
        kind=kind, exclude=exclude,
    ).data()
    found = []
    for row in rows:
        names = [row["label"], row["shortLabel"]]
        if row["payloadUri"]:
            names += entity_context(row["payloadUri"], row["qid"]).get("aliases", [])
        scored = [(similarity(label, name), name) for name in names if name]
        if not scored:
            continue
        score, matched = max(scored)
        if score >= threshold:
            found.append({"id": row["id"], "label": row["label"], "kind": row["kind"], "score": round(score, 2),
                          "matched": matched})
    return sorted(found, key=lambda item: (-item["score"], item["id"]))[:limit]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("label")
    parser.add_argument("--kind")
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args(argv)
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            found = session.execute_read(lambda tx: candidates(tx, args.label, args.kind, threshold=args.threshold))
    finally:
        driver.close()
    for item in found:
        print(f"{item['score']:.2f}  {item['id']}  {item['label']} ({item['kind']})  matched: {item['matched']}")
    if not found:
        print("no local candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
