#!/usr/bin/env python3
"""
Geo Agent — LLM classification pass (output only, no Neo4j writes).

Reads geo discovery JSON, sends to LLM for classification + deltas,
writes result to output/geo_discovery/{seed}_geo_agent_output.json.

Usage:
  python scripts/agents/geo/geo_agent_classify.py
  python scripts/agents/geo/geo_agent_classify.py --input output/geo_discovery/Q17167_geo_candidates.json
  python scripts/agents/geo/geo_agent_classify.py --output output/geo_discovery/my_output.json

Requires: ANTHROPIC_API_KEY (.env or env)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2].parent  # scripts/agents/geo -> scripts -> Graph1
sys.path.insert(0, str(_root))

try:
    import anthropic
except ImportError:
    anthropic = None

DEFAULT_INPUT = _root / "output" / "geo_discovery" / "Q17167_geo_candidates.json"
DEFAULT_OUTPUT_DIR = _root / "output" / "geo_discovery"

SYSTEM_PROMPT = """You are the Geo Agent for the Chrystallum project.
The graph already contains Place nodes for many Pleiades and GeoNames records.
Your job is to be a place-centric router: wire places to persons and events, not to reify events as Places.

1. Decide which Wikidata items are places (settlements, cities, provinces, regions) and which are events or other types.
2. For place-like items, decide how they should map to existing or new Place nodes.
3. Propose structured graph deltas; you do NOT write Cypher or directly modify the graph.

PRIMARY SIGNAL: instance_of and subclass_of. Use these to discriminate Place vs Event.
- instance_of = government reorganization, treaty, battle, siege, war, mutiny, coup, eruption, political event → EVENT. Do NOT create a Place for the item.
- instance_of = ancient city, colony, archaeological site (former settlement), Roman province, region → PLACE.
- "Settlement" in a label is ambiguous: "Pompey's eastern settlement" (political act) = event; "Roman settlement at X" (colony/archaeological site) = place. instance_of disambiguates.

EXAMPLE: Q122918768 (Pompey's eastern settlement)
- instance_of: government reorganization → EVENT.
- P276 (location): Asia, Bithynia et Pontus, Cilicia, Roman Syria.
- Your job: ensure each P276 target exists as a Place node; emit ATTACH_EVENT_TO_PLACE for each. Do NOT create a Place for Q122918768. Event modeling (Event node, time span, agent) is for the Event/Political SFA.

v1_core Place = human settlement (city, town, village, ancient city, colony, villa, fort, camp) or closely related political region (Roman province, region) relevant to the Roman Republic.

Events (battles, wars, sieges, eruptions, mutinies, coups, government reorganizations, treaties) are NOT Places. They attach to Places via P276 (location).

For each candidate:
1. Classify as one of: place_core, place_noncore, event, other.
   - place_core: settlements (city, town, village, ancient city, colony, archaeological site that is a former settlement), Roman provinces/regions relevant to Q17167.
   - place_noncore: natural features (rivers, mountains, volcanoes, seas, etc.) and very broad regions you do not want in v1.
   - event: battles, sieges, wars, mutinies, coups, eruptions, reorganizations, etc.
   - other: anything else that should be ignored for geography.

2. For place_core and place_noncore:
   - If candidate has P1584 (Pleiades ID), propose CREATE_OR_ENRICH_PLACE delta keyed by that Pleiades ID.
   - Else if P1566 (GeoNames ID), propose keyed by GeoNames ID.
   - Else if P625 (coordinates), propose keyed by qid, using the coordinates.
   - In properties, include: label, qid, Pleiades/GeoNames IDs, centroid_lat/centroid_lng if P625 present, base_type_hint (array of instance_of labels).

3. For event:
   - Do NOT propose new Place nodes.
   - For each P276 (location) whose value_qid looks place-like, propose ATTACH_EVENT_TO_PLACE delta with event_qid, place_qid, place_label, relation_type: "OCCURRED_AT".

4. For other: no deltas.

Output: Return a single JSON object with this structure. Do not emit Cypher or natural-language explanations. Produce valid JSON only.

{
  "seed_qid": "Q17167",
  "candidates": [
    {
      "qid": "...",
      "label": "...",
      "classification": "place_core | place_noncore | event | other",
      "deltas": [ ... ]
    }
  ]
}

Delta types:
- CREATE_OR_ENRICH_PLACE: place_key (pleiades_id, geonames_id), source_qid, properties (label, qid, pleiades_id, geonames_id, centroid_lat, centroid_lng, base_type_hint)
- ATTACH_EVENT_TO_PLACE: event_qid, place_qid, place_label, relation_type: "OCCURRED_AT"
"""


def _get_anthropic_key() -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key and (_root / ".env").exists():
        for line in (_root / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment or .env")
    return api_key


def _call_claude(system: str, user: str, model: str = "claude-sonnet-4-20250514", max_tokens: int = 8192) -> str:
    client = anthropic.Anthropic(api_key=_get_anthropic_key())
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text


def _extract_json(text: str) -> str:
    """Extract JSON from LLM response (handle markdown code blocks)."""
    text = text.strip()
    for prefix in ("```json", "```"):
        if text.startswith(prefix):
            text = text[len(prefix) :].strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    return text


def run(input_path: Path, output_path: Path, model: str) -> int:
    if not anthropic:
        print("anthropic required. Run: pip install anthropic", file=sys.stderr)
        return 1

    if not input_path.exists():
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    bundle = json.loads(input_path.read_text(encoding="utf-8"))
    seed = bundle.get("seed", {})
    seed_qid = seed.get("qid", "Q17167")
    candidates = bundle.get("candidates", [])
    if not candidates:
        print("No candidates in input.")
        return 0

    user_msg = f"Input (JSON):\n\n{json.dumps(bundle, indent=2, ensure_ascii=False)}"

    print(f"Geo Agent: {len(candidates)} candidates, seed={seed_qid}")
    print("Calling LLM...")

    try:
        raw = _call_claude(SYSTEM_PROMPT, user_msg, model=model)
    except Exception as e:
        print(f"LLM error: {e}", file=sys.stderr)
        return 1

    try:
        out_text = _extract_json(raw)
        out_data = json.loads(out_text)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        print("Raw response:", raw[:500], "...", file=sys.stderr)
        # Write raw for debugging
        debug_path = output_path.with_suffix(".raw.txt")
        debug_path.write_text(raw, encoding="utf-8")
        print(f"Raw response saved to {debug_path}", file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Output written to {output_path}")

    # Summary
    by_class = {}
    for c in out_data.get("candidates", []):
        k = c.get("classification", "unknown")
        by_class[k] = by_class.get(k, 0) + 1
    print("Classifications:", by_class)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Geo Agent classification (LLM only, no Neo4j)")
    parser.add_argument("--input", "-i", type=Path, default=DEFAULT_INPUT, help="Geo discovery JSON")
    parser.add_argument("--output", "-o", type=Path, help="Output path (default: output/geo_discovery/{seed}_geo_agent_output.json)")
    parser.add_argument("--model", default="claude-sonnet-4-20250514", help="Anthropic model")
    args = parser.parse_args()

    if args.output:
        out_path = args.output
    else:
        bundle = json.loads(args.input.read_text(encoding="utf-8"))
        seed_qid = bundle.get("seed", {}).get("qid", "Q17167")
        out_path = DEFAULT_OUTPUT_DIR / f"{seed_qid}_geo_agent_output.json"

    return run(args.input, out_path, args.model)


if __name__ == "__main__":
    sys.exit(main())
