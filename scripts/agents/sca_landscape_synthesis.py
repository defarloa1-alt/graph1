#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCA Landscape Synthesis — LLM reasoning pass.
PREFERRED: python -m scripts.agents.sca landscape Q17167 --taxonomy ... --lateral ...

Takes taxonomy harvest + lateral exploration data for a seed QID and produces:
  - Domain landscape narrative (where the subject sits academically)
  - Per-facet resource pointers (what each SFA should start from)
  - Taxonomy candidate flags (nodes worth promoting to future SubjectConcepts)

Usage:
    python scripts/agents/sca_landscape_synthesis.py Q17167 \\
        --taxonomy output/taxonomy_recursive/Q17167_recursive_20260220_135756.json \\
        --lateral  output/lateral/Q17167_lateral_20260301_221807.json \\
        --output   output/sca_landscape/

Requires:
    ANTHROPIC_API_KEY in .env
    pip install anthropic
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic not installed. Run: pip install anthropic")
    sys.exit(1)

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

# ── Authority PID tier definitions ────────────────────────────────────────────

# Continue traversal AND strong subject candidate
PRIMARY_AUTH_PIDS = {
    "P2163": "FAST (Faceted Application of Subject Terminology)",
    "P1149": "LCC (Library of Congress Classification)",
    "P9842": "PACTOLS (archaeological thesaurus)",
    "P1584": "Pleiades (ancient geography)",
    # P8814 was investigated and is WordNet 3.1, not Nomisma — excluded
}

# Include as candidate but STOP traversal from this node (too broad)
SECONDARY_AUTH_PIDS = {
    "P244":  "LCSH (Library of Congress Subject Headings)",
    "P227":  "GND (German National Library)",
    "P268":  "BnF (Bibliothèque nationale de France)",
    "P1051": "PSH (Czech Subject Headings)",
    "P1296": "Gran Enciclopèdia Catalana",
}

# ── Tier classifier ──────────────────────────────────────────────────────────

def classify_entity_tier(claims: dict) -> str:
    """Return 'primary', 'secondary', or 'meta' based on authority PIDs present."""
    if any(pid in claims for pid in PRIMARY_AUTH_PIDS):
        return "primary"
    if any(pid in claims for pid in SECONDARY_AUTH_PIDS):
        return "secondary"
    return "meta"


def extract_authority_ids(claims: dict) -> dict:
    """Extract authority identifier values from a claims dict."""
    result = {}
    all_auth = {**PRIMARY_AUTH_PIDS, **SECONDARY_AUTH_PIDS}
    for pid, label in all_auth.items():
        if pid in claims:
            stmts = claims[pid].get("statements", [])
            if stmts:
                val = stmts[0].get("value", "")
                short_label = label.split(" ")[0]  # "FAST", "LCC", etc.
                result[short_label] = val
    return result


# ── Data loaders ─────────────────────────────────────────────────────────────

def load_taxonomy(path: str) -> dict:
    """Load and tier-classify the taxonomy JSON."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    entities = data.get("entities", {})
    classified = {}

    for qid, ent in entities.items():
        claims = ent.get("claims_with_labels", {})
        tier = classify_entity_tier(claims)
        auth_ids = extract_authority_ids(claims)
        classified[qid] = {
            "qid": qid,
            "label": ent.get("label", ""),
            "description": ent.get("description", ""),
            "tier": tier,
            "authority_ids": auth_ids,
        }

    counts = {t: sum(1 for e in classified.values() if e["tier"] == t)
              for t in ["primary", "secondary", "meta"]}

    return {
        "seed_qid": data.get("root_qid"),
        "seed_label": data.get("root_label"),
        "entities": classified,
        "relationships": data.get("relationships", []),
        "tier_counts": counts,
    }


def load_lateral(path: str) -> dict:
    """Load lateral exploration JSON."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_facets_from_graph() -> list[dict]:
    """Load the 18 canonical facets from Neo4j."""
    if GraphDatabase is None:
        return _fallback_facets()
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        with driver.session() as s:
            result = s.run(
                "MATCH (f:Facet) RETURN f.key AS key, f.label AS label, "
                "f.description AS description ORDER BY f.key"
            )
            facets = [dict(r) for r in result]
        driver.close()
        if facets:
            return facets
    except Exception:
        pass
    return _fallback_facets()


def _fallback_facets() -> list[dict]:
    return [
        {"key": "POLITICAL",       "label": "Political",       "description": "Governance, magistracies, power structures"},
        {"key": "MILITARY",        "label": "Military",        "description": "Warfare, armies, campaigns, battles"},
        {"key": "SOCIAL",          "label": "Social",          "description": "Society, classes, gens, family structures"},
        {"key": "ECONOMIC",        "label": "Economic",        "description": "Trade, finance, currency, property"},
        {"key": "GEOGRAPHIC",      "label": "Geographic",      "description": "Places, territories, provinces, geography"},
        {"key": "TEMPORAL",        "label": "Temporal",        "description": "Chronology, periods, dates, calendars"},
        {"key": "BIOGRAPHICAL",    "label": "Biographical",    "description": "Individual persons, life events"},
        {"key": "INTELLECTUAL",    "label": "Intellectual",    "description": "Literature, philosophy, law texts, works"},
        {"key": "MATERIAL",        "label": "Material",        "description": "Material culture, objects, technology"},
        {"key": "ARCHAEOLOGICAL",  "label": "Archaeological",  "description": "Sites, excavations, inscriptions, artifacts"},
        {"key": "LINGUISTIC",      "label": "Linguistic",      "description": "Language, epigraphy, onomastics"},
        {"key": "LEGAL",           "label": "Legal",           "description": "Law, courts, legal institutions, edicts"},
        {"key": "RELIGIOUS",       "label": "Religious",       "description": "Religion, priesthoods, ritual, sacred sites"},
        {"key": "ADMINISTRATIVE",  "label": "Administrative",  "description": "Provincial administration, bureaucracy"},
        {"key": "PROSOPOGRAPHICAL","label": "Prosopographical","description": "Systematic study of persons as a group"},
        {"key": "DIPLOMATIC",      "label": "Diplomatic",      "description": "Treaties, alliances, foreign relations"},
        {"key": "NUMISMATIC",      "label": "Numismatic",      "description": "Coinage, mints, monetary systems"},
        {"key": "ENVIRONMENTAL",   "label": "Environmental",   "description": "Climate, ecology, land use, agriculture"},
    ]


# ── Prompt builder ────────────────────────────────────────────────────────────

def build_context_block(taxonomy: dict, lateral: dict, facets: list[dict]) -> str:
    """Build the structured context string fed to the LLM."""
    seed = taxonomy["seed_label"]
    seed_qid = taxonomy["seed_qid"]
    entities = taxonomy["entities"]
    counts = taxonomy["tier_counts"]

    # Seed entity detail
    seed_ent = entities.get(seed_qid, {})
    seed_auth = seed_ent.get("authority_ids", {})

    lines = [
        f"SUBJECT: {seed} ({seed_qid})",
        f"Description: {seed_ent.get('description', '')}",
        f"Authority IDs: {json.dumps(seed_auth)}",
        "",
        f"TAXONOMY NEIGHBORHOOD: {counts['primary']} primary | {counts['secondary']} secondary | {counts['meta']} meta-ontological (excluded)",
        "",
    ]

    # Primary tier — full detail
    lines.append("PRIMARY AUTHORITY CANDIDATES (FAST/LCC/PACTOLS/Pleiades present — continue traversal):")
    for ent in sorted(
        [e for e in entities.values() if e["tier"] == "primary" and e["qid"] != seed_qid],
        key=lambda e: e["label"]
    ):
        auth_str = ", ".join(f"{k}={v}" for k, v in ent["authority_ids"].items())
        lines.append(f"  {ent['qid']} {ent['label']}: {ent['description'][:80]} | {auth_str}")

    lines.append("")

    # Secondary tier — concise
    lines.append("SECONDARY AUTHORITY CANDIDATES (LCSH/GND/BnF only — include but stop traversal):")
    for ent in sorted(
        [e for e in entities.values() if e["tier"] == "secondary"],
        key=lambda e: e["label"]
    ):
        auth_str = ", ".join(f"{k}={v}" for k, v in ent["authority_ids"].items())
        lines.append(f"  {ent['qid']} {ent['label']} | {auth_str}")

    lines.append("")

    # Lateral entities
    lines.append("LATERAL ENTITIES (domain content — resource pointers for SFAs):")
    for place in lateral.get("places", []):
        auth = " | ".join(f"{k}={v}" for k, v in place.get("authorities", {}).items())
        lines.append(f"  [PLACE] {place['qid']} {place['label']}: {place.get('description','')[:60]} | {auth}")

    for org in lateral.get("organizations", []):
        lines.append(f"  [ORGANIZATION] {org['qid']} {org['label']}: {org.get('description','')[:60]}")

    for event in lateral.get("events", []):
        auth = " | ".join(f"{k}={v}" for k, v in event.get("authorities", {}).items())
        has = "✓" if event.get("has_authorities") else "✗"
        lines.append(f"  [EVENT] {event['qid']} {event['label']} (auth:{has}) | {auth}")

    for obj in lateral.get("objects", []):
        lines.append(f"  [OBJECT] {obj['qid']} {obj['label']}")

    lines.append("")

    # Facets
    lines.append("THE 18 SUBJECT FACET AGENTS (SFAs) — each needs resource pointers:")
    for f in facets:
        lines.append(f"  {f['key']}: {f.get('description', f.get('label', ''))}")

    return "\n".join(lines)


SYSTEM_PROMPT = """\
You are the Subject Classification Agent (SCA) for Chrystallum, a federated historical \
knowledge graph. Your role is to synthesize a domain landscape for a given subject entity \
and provide structured resource pointers for 18 Subject Facet Agents (SFAs).

REASONING RULES:
1. Work ONLY from the provided structured context. Do not invent facts.
2. Domain relevance beats authority breadth. A LCSH-only node can be more domain-relevant \
than a FAST+LCC abstract node. Use judgment.
3. SCA territory = abstract taxonomy/classification (form_of_government, ancient civilization, \
republic). SFA territory = domain content (people, places, events). Do not blur the boundary.
4. Per-facet pointers should be concrete: specific QIDs and authority anchors the SFA can \
use as starting vertices, not vague descriptions.
5. Taxonomy candidates are nodes from the primary/secondary tier that could serve as \
SubjectConcepts for OTHER future domains (Ancient Greece, Byzantine Empire, etc.) that \
share the same taxonomy nodes. Flag sparingly — only nodes with genuine cross-domain reuse value.

OUTPUT: Return ONLY valid JSON matching this schema exactly:
{
  "landscape_narrative": "<2-3 paragraph scholarly narrative situating the subject in its \
academic/library classification landscape>",
  "facet_pointers": {
    "<FACET_KEY>": {
      "relevance": "high|medium|low|none",
      "anchor_qids": ["<QID>", ...],
      "authority_anchors": {"<SYSTEM>": "<ID>", ...},
      "resource_hint": "<1-2 sentences: what specifically the SFA should investigate first>"
    }
  },
  "taxonomy_candidates": [
    {
      "qid": "<QID>",
      "label": "<label>",
      "tier": "primary|secondary",
      "reuse_reason": "<why future domains would reuse this node>"
    }
  ],
  "sca_notes": "<any architectural observations or anomalies worth flagging>"
}
"""


# ── Main synthesis ────────────────────────────────────────────────────────────

def synthesize(seed_qid: str, taxonomy_path: str, lateral_path: str,
               output_dir: str, model: str = "claude-sonnet-4-6") -> dict:
    """Run the SCA LLM reasoning pass and write output."""

    print(f"Loading taxonomy from: {taxonomy_path}")
    taxonomy = load_taxonomy(taxonomy_path)
    print(f"  {len(taxonomy['entities'])} entities | tiers: {taxonomy['tier_counts']}")

    print(f"Loading lateral from: {lateral_path}")
    lateral = load_lateral(lateral_path)
    n_lat = sum(len(lateral.get(k, [])) for k in ["places", "events", "organizations", "objects"])
    print(f"  {n_lat} lateral entities")

    print("Loading facets...")
    facets = load_facets_from_graph()
    print(f"  {len(facets)} facets")

    context = build_context_block(taxonomy, lateral, facets)
    user_message = (
        f"Synthesize the domain landscape for: {taxonomy['seed_label']} ({seed_qid})\n\n"
        f"{context}"
    )

    print(f"\nCalling {model}...")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        # Try loading from .env manually
        env_path = Path(__file__).resolve().parents[2] / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment or .env")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_content = message.content[0].text
    print(f"Response received ({len(raw_content)} chars, "
          f"input_tokens={message.usage.input_tokens}, "
          f"output_tokens={message.usage.output_tokens})")

    # Parse JSON response
    try:
        # Strip markdown fences if present
        content = raw_content.strip()
        if content.startswith("```"):
            content = content.split("```", 2)[1]
            if content.startswith("json"):
                content = content[4:]
        if content.endswith("```"):
            content = content[:-3]
        landscape = json.loads(content.strip())
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON parse failed ({e}). Saving raw response.")
        landscape = {"raw_response": raw_content, "parse_error": str(e)}

    # Wrap in envelope
    output = {
        "seed_qid": seed_qid,
        "seed_label": taxonomy["seed_label"],
        "model": model,
        "synthesized_at": datetime.now(timezone.utc).isoformat(),
        "input_taxonomy": str(taxonomy_path),
        "input_lateral": str(lateral_path),
        "tier_counts": taxonomy["tier_counts"],
        "usage": {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        },
        "landscape": landscape,
    }

    # Write output
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"{seed_qid}_landscape_{ts}.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nOutput written to: {out_path}")

    return output


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SCA Landscape Synthesis")
    parser.add_argument("seed_qid", help="Seed QID (e.g. Q17167)")
    parser.add_argument("--taxonomy", required=True, help="Path to taxonomy JSON")
    parser.add_argument("--lateral",  required=True, help="Path to lateral JSON")
    parser.add_argument("--output",   default="output/sca_landscape/", help="Output directory")
    parser.add_argument("--model",    default="claude-sonnet-4-6", help="Claude model ID")
    args = parser.parse_args()

    result = synthesize(
        seed_qid=args.seed_qid,
        taxonomy_path=args.taxonomy,
        lateral_path=args.lateral,
        output_dir=args.output,
        model=args.model,
    )

    # Print summary
    landscape = result.get("landscape", {})
    if "landscape_narrative" in landscape:
        print("\n" + "=" * 70)
        print("LANDSCAPE NARRATIVE:")
        print("=" * 70)
        print(landscape["landscape_narrative"])
        print()

        facet_pointers = landscape.get("facet_pointers", {})
        high = [k for k, v in facet_pointers.items() if v.get("relevance") == "high"]
        medium = [k for k, v in facet_pointers.items() if v.get("relevance") == "medium"]
        print(f"Facet relevance — HIGH ({len(high)}): {', '.join(high)}")
        print(f"                  MED  ({len(medium)}): {', '.join(medium)}")

        candidates = landscape.get("taxonomy_candidates", [])
        print(f"\nTaxonomy candidates flagged: {len(candidates)}")
        for c in candidates:
            print(f"  {c['qid']} {c['label']} ({c['tier']}): {c['reuse_reason'][:60]}")


if __name__ == "__main__":
    main()
