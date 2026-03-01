#!/usr/bin/env python3
"""
Map LCC classes to Chrystallum facets via LLM (OpenAI or Perplexity).

Step 1 of LCC→Facet pipeline. Reads lcc_roman_republic.csv, batches classes,
calls LLM for facet mapping + material_type (primary/secondary), outputs JSON.

Usage:
  python scripts/backbone/subject/map_lcc_to_facets_llm.py --provider openai
  python scripts/backbone/subject/map_lcc_to_facets_llm.py --provider perplexity
  python scripts/backbone/subject/map_lcc_to_facets_llm.py --dry-run  # no API calls

Env: OPENAI_API_KEY or PERPLEXITY_API_KEY
Output: output/subject_concepts/lcc_facet_mappings.json
"""

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

import requests

# Project root (parent of scripts/)
_PROJECT = Path(__file__).resolve().parents[3]
if str(_PROJECT) not in sys.path:
    sys.path.insert(0, str(_PROJECT))

# 18 canonical facets (ADR-004)
FACETS = [
    "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION", "CULTURAL",
    "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC", "ENVIRONMENTAL", "GEOGRAPHIC",
    "INTELLECTUAL", "LINGUISTIC", "MILITARY", "POLITICAL", "RELIGIOUS",
    "SCIENTIFIC", "SOCIAL", "TECHNOLOGICAL",
]

CHUNK_SIZE = 35  # classes per API call
DEFAULT_INPUT = _PROJECT / "output" / "nodes" / "lcc_roman_republic.csv"
DEFAULT_OUTPUT = _PROJECT / "output" / "subject_concepts" / "lcc_facet_mappings.json"


def load_lcc_classes(csv_path: Path) -> list[dict]:
    """Load LCC classes from CSV."""
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "code": r["id"],
                "label": r["label"],
                "prefix": r.get("prefix", ""),
                "uri": r.get("uri", ""),
            })
    return rows


def build_prompt(chunk: list[dict]) -> str:
    """Build LLM prompt for one batch of LCC classes."""
    classes_text = "\n".join(
        f"- {c['code']}: {c['label']}" for c in chunk
    )
    return f"""You are a library science expert mapping LCC (Library of Congress Classification) classes to Chrystallum research facets for the Roman Republic domain.

## Context
- LCC "Sources" = primary materials (original texts, laws, inscriptions). "Historiography", "Criticism" = secondary works.
- A class may map to multiple facets with different weights (0.0-1.0).
- material_type: "primary" | "secondary" | "both" | "unclear"

## Facets
{", ".join(FACETS)}

## LCC classes to map
{classes_text}

## Examples
- DG105 Army → MILITARY (0.95), material_type: secondary
- DG31 Sources → INTELLECTUAL (0.85), material_type: primary
- KJA190-2152 Sources → INTELLECTUAL (0.8), material_type: primary (legal source materials)
- DG91 Political institutions → POLITICAL (0.95), material_type: secondary
- DG155 Law (general) → INTELLECTUAL (0.6), POLITICAL (0.5), material_type: secondary

## Output
Return ONLY valid JSON array. One object per class. No other text.
[
  {{"code": "DG105", "label": "Army", "facets": [{{"facet": "MILITARY", "weight": 0.95, "reason": "Military organization"}}], "material_type": "secondary", "material_reason": "Secondary scholarship on army"}},
  ...
]
"""


def call_openai(prompt: str, model: str = "gpt-4o-mini") -> str:
    """Call OpenAI API. Returns raw content."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY not set")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a library science expert. Respond ONLY with valid JSON."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }
    r = requests.post(url, json=payload, headers=headers, timeout=90)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def call_perplexity(prompt: str, model: str = "llama-3.1-sonar-large-128k-online") -> str:
    """Call Perplexity API. Returns raw content."""
    key = os.getenv("PERPLEXITY_API_KEY")
    if not key:
        raise ValueError("PERPLEXITY_API_KEY not set")
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a library science expert. Respond ONLY with valid JSON."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }
    r = requests.post(url, json=payload, headers=headers, timeout=90)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def extract_json(content: str) -> list:
    """Extract JSON array from LLM response (handles markdown code blocks)."""
    text = content.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    # Find first [ and last ]
    start = text.find("[")
    end = text.rfind("]") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return json.loads(text)


def main():
    parser = argparse.ArgumentParser(description="Map LCC classes to facets via LLM")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="LCC CSV path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSON path")
    parser.add_argument("--provider", choices=["openai", "perplexity"], default="openai")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE)
    parser.add_argument("--dry-run", action="store_true", help="Print prompt, no API call")
    parser.add_argument("--limit", type=int, default=0, help="Limit classes (0=all, for testing)")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}")
        sys.exit(1)

    classes = load_lcc_classes(args.input)
    if args.limit:
        classes = classes[: args.limit]
    print(f"Loaded {len(classes)} LCC classes from {args.input}")

    if args.dry_run:
        prompt = build_prompt(classes[:5])
        print("--- DRY RUN: First 5 classes ---")
        print(prompt[:500] + "...")
        return

    all_mappings = []
    for i in range(0, len(classes), args.chunk_size):
        chunk = classes[i : i + args.chunk_size]
        prompt = build_prompt(chunk)
        print(f"Calling {args.provider} for batch {i // args.chunk_size + 1} ({len(chunk)} classes)...")
        try:
            if args.provider == "openai":
                content = call_openai(prompt)
            else:
                content = call_perplexity(prompt)
            mappings = extract_json(content)
            if not isinstance(mappings, list):
                mappings = [mappings]
            all_mappings.extend(mappings)
            print(f"  Got {len(mappings)} mappings")
        except Exception as e:
            print(f"  ERROR: {e}")
            raise

    output = {
        "source": str(args.input),
        "provider": args.provider,
        "total_classes": len(classes),
        "total_mappings": len(all_mappings),
        "mappings": all_mappings,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {args.output}")
    print(f"  Classes: {len(classes)}, Mappings: {len(all_mappings)}")


if __name__ == "__main__":
    main()
