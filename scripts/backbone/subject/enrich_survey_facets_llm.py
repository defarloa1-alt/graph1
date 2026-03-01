#!/usr/bin/env python3
"""
Enrich federation survey nodes with semantic facet via LLM.

Reads survey JSON (e.g. output/nodes/lcsh_roman_republic.json), calls OpenAI
or Perplexity to assign primary facet per label, writes semantic_facet into
node.properties. Overwrites the survey file.

LLM-first with automatic fallback: tries LLM for each batch; on failure or
empty response, uses heuristic (or federation default) so every node gets a
semantic_facet. Logs LLM-assigned vs heuristic/default counts.

Usage:
  python scripts/backbone/subject/enrich_survey_facets_llm.py
  python scripts/backbone/subject/enrich_survey_facets_llm.py -i output/nodes/pleiades_roman_republic.json
  python scripts/backbone/subject/enrich_survey_facets_llm.py --provider perplexity
  python scripts/backbone/subject/enrich_survey_facets_llm.py --dry-run

Env: OPENAI_API_KEY or PPLX_API_KEY/PERPLEXITY_API_KEY (omit to use heuristic for all)
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

_PROJECT = Path(__file__).resolve().parents[3]
if str(_PROJECT) not in sys.path:
    sys.path.insert(0, str(_PROJECT))

from scripts.config_loader import get_config, OPENAI_API_KEY, PERPLEXITY_API_KEY
from scripts.federation_node_schema import FederationSurvey

# 18 canonical facets (exclude TEMPORAL — it's structural)
FACETS = [
    "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION", "CULTURAL",
    "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC", "ENVIRONMENTAL", "GEOGRAPHIC",
    "INTELLECTUAL", "LINGUISTIC", "MILITARY", "POLITICAL", "RELIGIOUS",
    "SCIENTIFIC", "SOCIAL", "TECHNOLOGICAL",
]

# Short descriptions so the LLM can reason about facet choice
FACET_DESCRIPTIONS = {
    "ARCHAEOLOGICAL": "Material-culture periods, stratigraphy, typologies, excavations",
    "ARTISTIC": "Art movements, architectural styles, aesthetic regimes",
    "BIOGRAPHIC": "Personal history, biography, life events, careers, genealogy",
    "COMMUNICATION": "Information exchange, media, communication technologies",
    "CULTURAL": "Cultural eras, shared practices, identity, literature, arts",
    "DEMOGRAPHIC": "Population structure, migration, urbanization waves",
    "DIPLOMATIC": "International systems, alliances, treaty regimes",
    "ECONOMIC": "Economic systems, trade regimes, financial structures, ports, mines",
    "ENVIRONMENTAL": "Climate regimes, ecological shifts, environmental phases",
    "GEOGRAPHIC": "Spatial organization, territorial control, regions, places, settlements",
    "INTELLECTUAL": "Schools of thought, philosophy, historiography, scholarship",
    "LINGUISTIC": "Language families, scripts, linguistic shifts",
    "MILITARY": "Warfare, conquests, military systems, forts, campaigns",
    "POLITICAL": "States, regimes, dynasties, governance, offices, magistracies",
    "RELIGIOUS": "Religious movements, institutions, temples, cults, rituals",
    "SCIENTIFIC": "Scientific paradigms, revolutions, epistemic frameworks",
    "SOCIAL": "Social norms, class structures, social movements, patronage",
    "TECHNOLOGICAL": "Tool regimes, production technologies, industrial phases",
}

CHUNK_SIZE = 20
DEFAULT_INPUT = _PROJECT / "output" / "nodes" / "lcsh_roman_republic.json"

# Heuristic keyword → facet (fallback when no API)
FACET_KEYWORDS = {
    "ARCHAEOLOGICAL": ["archaeolog", "excavat", "antiquit", "artifact", "inscription"],
    "MILITARY": ["military", "war", "battle", "army", "navy", "campaign", "legion", "naval"],
    "DIPLOMATIC": ["diplomac", "treaty", "embassy", "international", "alliance"],
    "RELIGIOUS": ["religion", "cult", "priest", "ritual", "church", "biblical"],
    "GEOGRAPHIC": ["geograph", "province", "region", "place", "territory", "colonial", "colonies", "city", "port", "sanctuary", "temple", "forum"],
    "POLITICAL": ["politic", "government", "senate", "magistrate", "constitution", "republic"],
    "ECONOMIC": ["economic", "trade", "commerce", "agriculture", "finance", "tax"],
    "SOCIAL": ["social", "society", "patronage", "slavery", "class"],
    "INTELLECTUAL": ["historiograph", "intellectual", "criticism", "interpretation", "doctrine"],
}

# Federation-specific default when no heuristic/LLM match (avoids INTELLECTUAL for places)
FEDERATION_FACET_DEFAULT = {
    "pleiades": "GEOGRAPHIC",   # Place gazetteer — all nodes are geographic
    "periodo": "ENVIRONMENTAL", # Period definitions — temporal (ENVIRONMENTAL = climate/ecological phases)
    "dprr": "POLITICAL",        # Office assertions — political
}


def _assign_facet_heuristic(label: str, federation: str = "") -> str:
    """Keyword-based facet fallback. Uses federation default when no keyword matches."""
    label_lower = (label or "").lower()
    scores = {}
    for facet, keywords in FACET_KEYWORDS.items():
        scores[facet] = sum(1 for k in keywords if k in label_lower)
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best
    return FEDERATION_FACET_DEFAULT.get(federation, "INTELLECTUAL")


def _item_for_prompt(node) -> dict:
    """Build item dict with id, label, and any extra context for LLM reasoning."""
    d = {"id": node.id, "label": node.label}
    props = getattr(node, "properties", None) or {}
    if props.get("place_type"):
        d["place_type"] = props["place_type"]  # Pleiades: temple, settlement, region, port, fort, etc.
    if getattr(node, "scope_note", None) and str(node.scope_note).strip():
        d["scope_note"] = str(node.scope_note).strip()[:200]  # Truncate long notes
    return d


def _format_item(item: dict) -> str:
    """Format one item for the prompt (id, label, optional place_type/scope_note)."""
    parts = [f"{item['id']}: {item['label']}"]
    if item.get("place_type"):
        parts.append(f" (place_type: {item['place_type']})")
    if item.get("scope_note"):
        parts.append(f" — {item['scope_note']}")
    return "".join(parts)


def build_prompt(chunk: list[dict], domain: str = "unknown", federation: str = "") -> str:
    """Build LLM prompt for one batch of labels."""
    domain_label = domain.replace("_", " ").title()
    items = "\n".join(f"- {_format_item(c)}" for c in chunk)
    facet_block = "\n".join(f"- {k}: {v}" for k, v in FACET_DESCRIPTIONS.items())
    fed_hint = ""
    if federation == "pleiades":
        fed_hint = "\n## IMPORTANT: These are Pleiades PLACE names (cities, regions, sites). Default to GEOGRAPHIC unless the label clearly indicates another facet (e.g. temple/sanctuary → RELIGIOUS, port → ECONOMIC)."
    elif federation == "periodo":
        fed_hint = "\n## IMPORTANT: These are PeriodO temporal period definitions. Prefer ENVIRONMENTAL (climate/ecological phases) or CULTURAL (cultural eras); default to ENVIRONMENTAL."
    elif federation == "dprr":
        fed_hint = "\n## IMPORTANT: These are DPRR office titles (Consul, Praetor, etc.). Default to POLITICAL."
    return f"""You are a library science expert mapping subject labels to Chrystallum research facets for the {domain_label} domain. {fed_hint}

## Facets (choose ONE primary per item)
{facet_block}

## Items to map
{items}

## Examples
- History, Military → MILITARY
- Diplomatic history → DIPLOMATIC
- Church history → RELIGIOUS
- Historical geography → GEOGRAPHIC
- Colonial history → POLITICAL
- History (general) → INTELLECTUAL
- Rome--History--Republic, 510-30 B.C. → POLITICAL
- Roma, Athens, Pompeii (place names) → GEOGRAPHIC
- Tempio Grande at Vulci (place_type: temple-2) → RELIGIOUS
- Ostia (place_type: port) → ECONOMIC
- Consul, Praetor (office titles) → POLITICAL

## Output
Return ONLY a valid JSON array. One object per item. No other text.
[{{"id": "sh00005863", "label": "History, Military", "facet": "MILITARY"}}, ...]
"""


def call_openai(prompt: str, model: str = "gpt-4o-mini") -> str:
    """Call OpenAI API. Returns raw content."""
    key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
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


def call_perplexity(prompt: str, model: str = "sonar-pro") -> str:
    """Call Perplexity API. Returns raw content."""
    key = PERPLEXITY_API_KEY or os.getenv("PPLX_API_KEY") or os.getenv("PERPLEXITY_API_KEY")
    if not key:
        raise ValueError("PPLX_API_KEY or PERPLEXITY_API_KEY not set (check .env or config.py)")
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


def extract_json(text: str) -> list:
    """Extract JSON array from LLM response (handles markdown code blocks)."""
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    start = text.find("[")
    if start < 0:
        return []
    end = text.rfind("]") + 1
    if end > start:
        return json.loads(text[start:end])
    return []


def _has_api_key(provider: str) -> bool:
    if provider == "openai":
        return bool(OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"))
    return bool(
        PERPLEXITY_API_KEY
        or os.getenv("PPLX_API_KEY")
        or os.getenv("PERPLEXITY_API_KEY")
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--provider", choices=["openai", "perplexity"], default="openai")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}")
        return 1

    survey = FederationSurvey.load(args.input)
    nodes = survey.nodes
    if not nodes:
        print("No nodes to enrich")
        return 0

    # Build chunks (include place_type, scope_note for LLM context)
    chunks = []
    for i in range(0, len(nodes), CHUNK_SIZE):
        chunk = [_item_for_prompt(n) for n in nodes[i : i + CHUNK_SIZE]]
        chunks.append(chunk)

    domain = getattr(survey, "domain", "unknown") or "unknown"
    federation = getattr(survey, "federation", "") or "unknown"

    if args.dry_run:
        print(f"Would enrich {len(nodes)} nodes in {len(chunks)} API call(s) (federation={federation})")
        for c in chunks[:1]:
            print("Sample prompt:")
            print(build_prompt(c, domain=domain, federation=federation)[:600] + "...")
        return 0

    id_to_facet = {}
    llm_assigned = 0

    if not _has_api_key(args.provider):
        print("No API key found — using heuristic for all nodes")
        for node in nodes:
            id_to_facet[node.id] = _assign_facet_heuristic(node.label, federation=federation)
    else:
        for i, chunk in enumerate(chunks):
            prompt = build_prompt(chunk, domain=domain, federation=federation)
            print(f"Calling {args.provider} for batch {i + 1}/{len(chunks)} ({len(chunk)} nodes)...")
            try:
                result = call_openai(prompt) if args.provider == "openai" else call_perplexity(prompt)
                parsed = extract_json(result)
            except Exception as e:
                print(f"  LLM failed for batch {i + 1}: {e} — falling back to heuristic")
                parsed = []

            if parsed:
                for item in parsed:
                    if isinstance(item, dict) and item.get("facet") in FACETS:
                        id_to_facet[item["id"]] = item["facet"]
                        llm_assigned += 1
            else:
                for c in chunk:
                    id_to_facet[c["id"]] = _assign_facet_heuristic(c["label"], federation=federation)

    # Apply to nodes (use federation default when LLM/heuristic didn't assign)
    default_facet = FEDERATION_FACET_DEFAULT.get(federation, "INTELLECTUAL")
    for node in nodes:
        facet = id_to_facet.get(node.id) or default_facet
        node.properties["semantic_facet"] = facet

    survey.save(args.input)
    heuristic_default = len(nodes) - llm_assigned
    print(f"Enriched {len(nodes)} nodes: LLM-assigned={llm_assigned}, heuristic/default={heuristic_default}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
