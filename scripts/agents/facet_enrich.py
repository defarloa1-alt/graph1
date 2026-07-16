#!/usr/bin/env python3
"""
facet_enrich.py — Enrich Facet nodes with canonical discipline knowledge.

For each of the 18 facets, asks Claude:
  1. What are the canonical topic areas of this discipline?
  2. What free online resources ground a student in this discipline?

Stores both on the Facet node in Neo4j. This knowledge is domain-agnostic —
it lives on the Facet, reused across any seed domain that activates it.

Usage:
  # Preview all 18 facets (no graph write):
  python scripts/agents/facet_enrich.py

  # Single facet:
  python scripts/agents/facet_enrich.py --facets military

  # Write to graph:
  python scripts/agents/facet_enrich.py --write

  # Single facet + write:
  python scripts/agents/facet_enrich.py --facets military --write
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    import anthropic
except ImportError:
    anthropic = None

CANONICAL_FACETS = [
    "archaeological", "artistic", "biographic", "communication",
    "cultural", "demographic", "diplomatic", "economic",
    "environmental", "geographic", "intellectual", "linguistic",
    "military", "political", "religious", "scientific",
    "social", "technological",
]

DISCIPLINE_PROMPT = """You are a curriculum designer for a university library classification system.

For the academic discipline of {facet_label} studies/history, provide:

1. CANONICAL_TOPICS: The 6-10 major recurring topic areas that any serious study of this
   discipline would cover. These are the standard organizing categories used by scholars,
   encyclopaedias, and university syllabi — not specific to any era or region.

2. DISCIPLINE_SOURCES: The best FREE online resources that would ground a student in this
   discipline. Include: open courseware, reputable encyclopaedias, open-access journals,
   digitized primary source collections, and major online archives. Prioritize resources
   that are genuinely free (not just previews), academically credible, and comprehensive.

Return ONLY valid JSON with this exact structure:
{{
  "facet_key": "{facet_key}",
  "facet_label": "{facet_label}",
  "canonical_topics": [
    {{
      "topic_key": "short_snake_case_key",
      "topic_label": "Human Readable Label",
      "description": "One sentence: what scholars in this topic study",
      "example_questions": ["Sample research question 1", "Sample research question 2"]
    }}
  ],
  "discipline_sources": [
    {{
      "label": "Resource name",
      "url": "https://...",
      "type": "ocw|encyclopedia|journal|archive|course|database",
      "description": "What it contains and why it is useful for this discipline",
      "is_free": true
    }}
  ],
  "discipline_note": "1-2 sentences on the current state of the discipline and its main debates"
}}"""


def _get_client(api_key: Optional[str] = None):
    if not anthropic:
        raise ImportError("pip install anthropic")
    key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not key:
        env_path = ROOT / ".env"
        if env_path.exists():
            for line in open(env_path):
                if line.startswith("ANTHROPIC_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"\'')
                    break
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not found")
    return anthropic.Anthropic(api_key=key)


def enrich_facet(facet_key: str, client) -> dict:
    """Ask Claude for canonical topics + discipline sources for one facet."""
    facet_label = facet_key.capitalize()

    prompt = DISCIPLINE_PROMPT.format(
        facet_key=facet_key,
        facet_label=facet_label,
    )

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    text = msg.content[0].text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    return json.loads(text)


def write_to_graph(results: List[dict]):
    """Store canonical_topics and discipline_sources on Facet nodes."""
    from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    written = 0
    try:
        with driver.session() as session:
            for r in results:
                session.run("""
                    MATCH (f:Facet {key: $key})
                    SET f.canonical_topics = $topics,
                        f.discipline_sources = $sources,
                        f.discipline_note = $note,
                        f.enriched_date = datetime()
                """,
                    key=r["facet_key"],
                    topics=json.dumps(r["canonical_topics"], ensure_ascii=False),
                    sources=json.dumps(r["discipline_sources"], ensure_ascii=False),
                    note=r.get("discipline_note", ""),
                )
                written += 1
        print(f"\nWrote discipline knowledge to {written} Facet nodes in graph.")
    finally:
        driver.close()


def display_result(r: dict):
    print(f"\n{'='*60}")
    print(f"FACET: {r['facet_label'].upper()}")
    print(f"{'='*60}")

    print(f"\n  Discipline note: {r.get('discipline_note', '')}")

    print(f"\n  Canonical Topics ({len(r.get('canonical_topics', []))}):")
    for t in r.get("canonical_topics", []):
        print(f"    [{t['topic_key']}] {t['topic_label']}")
        print(f"      {t['description']}")

    print(f"\n  Free Discipline Sources ({len(r.get('discipline_sources', []))}):")
    for s in r.get("discipline_sources", []):
        print(f"    [{s['type']}] {s['label']}")
        print(f"      {s['url']}")
        print(f"      {s['description'][:80]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--facets", type=str, default=None,
                        help="Comma-separated facets (default: all 18)")
    parser.add_argument("--write", action="store_true",
                        help="Write to Neo4j Facet nodes")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "output" / "facet_discipline")
    args = parser.parse_args()

    facets = CANONICAL_FACETS
    if args.facets:
        facets = [f.strip().lower() for f in args.facets.split(",")]

    client = _get_client()
    args.output.mkdir(parents=True, exist_ok=True)

    results = []
    for i, facet_key in enumerate(facets):
        print(f"\n[{i+1}/{len(facets)}] Enriching: {facet_key}...")
        try:
            r = enrich_facet(facet_key, client)
            results.append(r)
            display_result(r)

            # Save per-facet
            out = args.output / f"{facet_key}_discipline.json"
            with open(out, "w", encoding="utf-8") as f:
                json.dump(r, f, indent=2, ensure_ascii=False)

            if i < len(facets) - 1:
                time.sleep(0.5)  # gentle rate limit

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"facet_key": facet_key, "error": str(e)})

    # Save combined
    combined_path = args.output / "all_facets_discipline.json"
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {combined_path}")

    if args.write:
        write_to_graph([r for r in results if "error" not in r])
    else:
        print("\n(Review above. Add --write to store on Facet nodes in Neo4j.)")


if __name__ == "__main__":
    main()
