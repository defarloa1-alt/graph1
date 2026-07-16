#!/usr/bin/env python3
"""
wiki_ingest.py — Wikipedia article → SubjectConcept + entity proposals.

Fetches a Wikipedia article, parses its section structure and wikilinks,
then uses Claude to map sections to SubjectConcepts with facet weights,
LCC anchors, and member entity candidates.

Usage:
  # Review proposals (no graph write):
  python scripts/agents/wiki_ingest.py --url "https://en.wikipedia.org/wiki/Roman_army"

  # With seed QID to scope MEMBER_OF edges:
  python scripts/agents/wiki_ingest.py --url "https://en.wikipedia.org/wiki/Roman_army" --seed Q17167

  # Write approved proposals to Neo4j:
  python scripts/agents/wiki_ingest.py --url "https://en.wikipedia.org/wiki/Roman_army" --seed Q17167 --write
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, unquote

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    import anthropic
except ImportError:
    anthropic = None


# ---------------------------------------------------------------------------
# Layer 1: Fetch + parse Wikipedia article (deterministic, no LLM)
# ---------------------------------------------------------------------------

def fetch_wikipedia(url: str) -> dict:
    """Fetch a Wikipedia article via the Action API.

    Returns structured content: title, summary, sections (with text + wikilinks).
    """
    parsed = urlparse(url)
    # Extract page title from URL path
    path = unquote(parsed.path)
    title = path.split("/wiki/")[-1].replace("_", " ")
    lang = parsed.hostname.split(".")[0] if parsed.hostname else "en"

    api = f"https://{lang}.wikipedia.org/w/api.php"
    headers = {"User-Agent": "Chrystallum/1.0 (research project)"}

    # Fetch section structure
    resp = requests.get(api, params={
        "action": "parse", "page": title,
        "prop": "sections|wikitext|links",
        "format": "json",
    }, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json().get("parse", {})

    raw_title = data.get("title", title)
    wikitext = data.get("wikitext", {}).get("*", "")
    sections_meta = data.get("sections", [])
    all_links = [l.get("*", "") for l in data.get("links", []) if l.get("ns", 0) == 0]

    # Split wikitext into sections
    section_texts = _split_wikitext_sections(wikitext)

    sections = []
    for s in sections_meta:
        level = int(s.get("level", 2))
        heading = s.get("line", "").strip()
        # Skip nav/meta sections
        if heading.lower() in {"see also", "references", "notes", "bibliography",
                                "further reading", "external links", "footnotes"}:
            continue
        idx = int(s.get("index", 0))
        text = section_texts.get(idx, "")
        links = _extract_wikilinks(text)
        sections.append({
            "heading": heading,
            "level": level,
            "index": idx,
            "text": text[:1500],
            "wikilinks": links[:40],
        })

    # Summary via REST API
    summary = ""
    try:
        rest = requests.get(
            f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}",
            headers=headers, timeout=15,
        )
        if rest.ok:
            summary = rest.json().get("extract", "")[:800]
    except Exception:
        pass

    print(f"  [Wikipedia] '{raw_title}': {len(sections)} sections, {len(all_links)} links")
    return {
        "title": raw_title,
        "url": url,
        "summary": summary,
        "sections": sections,
        "all_links": all_links[:200],
    }


def _split_wikitext_sections(wikitext: str) -> Dict[int, str]:
    """Split raw wikitext into sections by == heading ==, indexed by order."""
    # Find all section headings and their positions
    pattern = re.compile(r'^(={2,})\s*(.+?)\s*\1\s*$', re.MULTILINE)
    matches = list(pattern.finditer(wikitext))

    sections = {}
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(wikitext)
        sections[i + 1] = wikitext[start:end].strip()

    return sections


def _extract_wikilinks(text: str) -> List[str]:
    """Extract [[wikilink]] targets from wikitext."""
    raw = re.findall(r'\[\[([^\]\|#]+)', text)
    cleaned = []
    for r in raw:
        r = r.strip()
        if r and not r.startswith("File:") and not r.startswith("Image:") \
                and not r.startswith("Category:") and len(r) < 80:
            cleaned.append(r)
    return list(dict.fromkeys(cleaned))  # deduplicate, preserve order


# ---------------------------------------------------------------------------
# Layer 2: Claude enrichment — sections → SC proposals with facet weights
# ---------------------------------------------------------------------------

ENRICHMENT_PROMPT = """You are building a knowledge graph for the domain: {domain_label}

You have a Wikipedia article: "{article_title}"

Article summary:
{summary}

Sections and their wikilinks:
{sections_json}

Your task: propose SubjectConcept nodes for this article's domain structure.

Rules:
1. Each top-level section (or coherent cluster of sub-sections) becomes one SubjectConcept.
2. Skip navigation sections (See Also, References, etc.).
3. Each SubjectConcept needs:
   - label: short, specific (not generic like "Overview" or "History")
   - description: 1-2 sentences on what this SC covers
   - facet_weights: score all 18 facets 0.0–1.0 (archaeological, artistic, biographic,
     communication, cultural, demographic, diplomatic, economic, environmental, geographic,
     intellectual, linguistic, military, political, religious, scientific, social, technological)
   - lcc_suggestion: best Library of Congress Classification code (e.g. "DG254" for Roman army)
   - member_candidates: wikilinks from that section that are distinct entities belonging IN this SC
     (NOT sub-concepts — only leaf entities: specific battles, persons, units, places, events)
   - confidence: 0.0–1.0

4. member_candidates must be ENTITIES (Battle of Cannae, Julius Caesar, Legio X Equestris),
   NOT sub-concepts (those become their own SCs). Max 15 per SC.

5. If a section is too broad, split it. If two sections are too narrow, merge them.

Return ONLY valid JSON:
{{
  "subject_concepts": [
    {{
      "label": "Wars & Military Campaigns",
      "description": "Major armed conflicts of the Roman Republic including the Punic, Macedonian, and Civil Wars",
      "source_section": "History > Wars",
      "facet_weights": {{
        "archaeological": 0.2, "artistic": 0.0, "biographic": 0.3,
        "communication": 0.0, "cultural": 0.2, "demographic": 0.2,
        "diplomatic": 0.4, "economic": 0.2, "environmental": 0.0,
        "geographic": 0.5, "intellectual": 0.0, "linguistic": 0.0,
        "military": 1.0, "political": 0.6, "religious": 0.0,
        "scientific": 0.0, "social": 0.3, "technological": 0.2
      }},
      "lcc_suggestion": "DG241",
      "member_candidates": ["Battle of Cannae", "Battle of Zama", "Punic Wars"],
      "confidence": 0.92
    }}
  ],
  "article_notes": "Brief note on what this article covers well vs. what's missing"
}}"""


def enrich_with_claude(article: dict, seed_label: str, api_key: Optional[str] = None) -> dict:
    """Call Claude to map article sections → SC proposals with facet weights."""
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

    client = anthropic.Anthropic(api_key=key)

    sections_json = json.dumps(
        [{"heading": s["heading"], "level": s["level"],
          "wikilinks": s["wikilinks"][:20]} for s in article["sections"]],
        indent=2
    )

    prompt = ENRICHMENT_PROMPT.format(
        domain_label=seed_label,
        article_title=article["title"],
        summary=article["summary"],
        sections_json=sections_json,
    )

    print("  [Claude] Enriching sections -> SC proposals...")
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    text = msg.content[0].text.strip()
    # Extract JSON from response
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    result = json.loads(text)
    print(f"  [Claude] Proposed {len(result.get('subject_concepts', []))} SubjectConcepts")
    return result


# ---------------------------------------------------------------------------
# Layer 3: Build final proposals
# ---------------------------------------------------------------------------

def build_proposals(enriched: dict, article: dict, seed_qid: str, seed_label: str) -> List[dict]:
    """Convert Claude's SC proposals into the standard proposal format."""
    proposals = []
    for sc in enriched.get("subject_concepts", []):
        label = sc.get("label", "")
        cipher_input = f"{seed_qid}:wiki:{label}"
        cipher = hashlib.sha256(cipher_input.encode()).hexdigest()[:16]

        proposals.append({
            "proposal_type": "wiki_ingest",
            "source_article": article["url"],
            "source_section": sc.get("source_section", ""),
            "label": label,
            "description": sc.get("description", ""),
            "seed_qid": seed_qid,
            "seed_label": seed_label,
            "facet_weights": sc.get("facet_weights", {}),
            "lcc_suggestion": sc.get("lcc_suggestion", ""),
            "member_candidates": sc.get("member_candidates", []),
            "confidence": sc.get("confidence", 0.8),
            "concept_cipher": cipher,
        })
    return proposals


# ---------------------------------------------------------------------------
# Layer 4: Graph write
# ---------------------------------------------------------------------------

def write_to_graph(proposals: List[dict], seed_qid: str):
    """Write proposals to Neo4j."""
    from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    written = 0
    try:
        with driver.session() as session:
            for p in proposals:
                session.run("""
                    MERGE (sc:SubjectConcept {concept_cipher: $cipher})
                    SET sc.label = $label,
                        sc.description = $description,
                        sc.seed_qid = $seed_qid,
                        sc.proposal_type = $proposal_type,
                        sc.source_article = $source_article,
                        sc.lcc_suggestion = $lcc_suggestion,
                        sc.confidence = $confidence,
                        sc.bootstrap_source = 'wiki_ingest',
                        sc.proposed_date = datetime()
                    WITH sc
                    MATCH (seed) WHERE seed.qid = $seed_qid
                    MERGE (sc)-[:SCOPED_TO]->(seed)
                """, cipher=p["concept_cipher"], label=p["label"],
                   description=p["description"], seed_qid=seed_qid,
                   proposal_type=p["proposal_type"],
                   source_article=p["source_article"],
                   lcc_suggestion=p["lcc_suggestion"],
                   confidence=p["confidence"])

                # HAS_FACET edges
                for facet_key, weight in p.get("facet_weights", {}).items():
                    if weight >= 0.3:
                        session.run("""
                            MATCH (sc:SubjectConcept {concept_cipher: $cipher})
                            MATCH (f:Facet {key: $key})
                            MERGE (sc)-[r:HAS_FACET]->(f)
                            SET r.weight = $weight
                        """, cipher=p["concept_cipher"], key=facet_key, weight=weight)

                written += 1

        print(f"  Wrote {written} SubjectConcepts to graph")
    finally:
        driver.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Wikipedia article → SC proposals")
    parser.add_argument("--url", required=True, help="Wikipedia article URL")
    parser.add_argument("--seed", default="Q17167", help="Seed domain QID")
    parser.add_argument("--seed-label", default="Roman Republic", help="Seed domain label")
    parser.add_argument("--output", type=Path, default=ROOT / "output" / "wiki_proposals")
    parser.add_argument("--write", action="store_true", help="Write to Neo4j")
    parser.add_argument("--no-llm", action="store_true", help="Skip Claude enrichment, show raw sections only")
    args = parser.parse_args()

    print(f"\nIngesting: {args.url}")
    print(f"Seed: {args.seed} ({args.seed_label})")

    # Fetch article
    article = fetch_wikipedia(args.url)

    print(f"\n--- Article Structure ---")
    for s in article["sections"]:
        indent = "  " * (s["level"] - 2)
        print(f"  {indent}[{s['level']}] {s['heading']}  ({len(s['wikilinks'])} links)")

    if args.no_llm:
        print("\n--no-llm: skipping enrichment.")
        return

    # Claude enrichment
    enriched = enrich_with_claude(article, args.seed_label)

    # Build proposals
    proposals = build_proposals(enriched, article, args.seed, args.seed_label)

    # Display
    print(f"\n--- SubjectConcept Proposals ({len(proposals)}) ---")
    for i, p in enumerate(proposals, 1):
        top_facets = sorted(p["facet_weights"].items(), key=lambda x: x[1], reverse=True)[:3]
        facet_str = ", ".join(f"{f}={w:.1f}" for f, w in top_facets if w > 0)
        print(f"\n  {i}. {p['label']}  (conf={p['confidence']:.2f})")
        print(f"     {p['description'][:90]}")
        print(f"     LCC: {p['lcc_suggestion']}  |  facets: {facet_str}")
        print(f"     members ({len(p['member_candidates'])}): {', '.join(p['member_candidates'][:6])}")

    print(f"\n  article_notes: {enriched.get('article_notes', '')}")

    # Save
    args.output.mkdir(parents=True, exist_ok=True)
    slug = args.url.split("/wiki/")[-1][:40]
    out_path = args.output / f"{args.seed}_{slug}_proposals.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "url": args.url,
            "seed_qid": args.seed,
            "seed_label": args.seed_label,
            "generated": datetime.now(timezone.utc).isoformat(),
            "article_title": article["title"],
            "proposals": proposals,
        }, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {out_path}")

    if args.write:
        print("\nWriting to graph...")
        write_to_graph(proposals, args.seed)
    else:
        print("\n(Review above. Add --write to commit to Neo4j.)")


if __name__ == "__main__":
    main()
