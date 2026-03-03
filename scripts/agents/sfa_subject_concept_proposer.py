#!/usr/bin/env python3
"""
sfa_subject_concept_proposer.py
--------------------------------
Subject Facet Agent (SFA) — SubjectConcept Proposer

Consumes the SCA landscape output for a seed QID and proposes concrete
SubjectConcepts for a specific facet. Does NOT write to the graph — output
goes to output/sfa_proposals/ for human review (Phase D).

Pipeline position:
    SCA landscape synthesis (DONE) → sfa_subject_concept_proposer.py → human curation → graph writes

Usage:
    python scripts/agents/sfa_subject_concept_proposer.py --facet POLITICAL [--seed Q17167]

Supported facets (evidence gathering wired):
    POLITICAL — full evidence: magistracy stats, LCC DG89-DG99, WorldCat filter
    (Others: SCA pointer only, no facet-specific graph queries yet)
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

# ---------------------------------------------------------------------------
# Claude API
# ---------------------------------------------------------------------------

def _get_api_key() -> str:
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        env_path = _root / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment or .env")
    return api_key


def call_claude(system_prompt: str, user_message: str,
                model: str = "claude-sonnet-4-6", max_tokens: int = 8000) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=_get_api_key())
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    text = message.content[0].text
    print(f"  Claude response: {len(text)} chars "
          f"(in={message.usage.input_tokens}, out={message.usage.output_tokens})")
    return text


# ---------------------------------------------------------------------------
# SCA landscape loader
# ---------------------------------------------------------------------------

def load_sca_landscape(seed_qid: str, landscape_dir: Path) -> dict:
    """Load most recent SCA landscape output for seed_qid."""
    files = sorted(landscape_dir.glob(f"{seed_qid}_landscape_*.json"))
    if not files:
        raise FileNotFoundError(
            f"No SCA landscape found for {seed_qid} in {landscape_dir}. "
            f"Run sca_landscape_synthesis.py first."
        )
    path = files[-1]  # most recent
    print(f"  Loading SCA landscape: {path.name}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["landscape"]  # inner landscape object


# ---------------------------------------------------------------------------
# Survey loaders
# ---------------------------------------------------------------------------

def load_worldcat_nodes(seed_qid: str, survey_dir: Path) -> list:
    path = survey_dir / "worldcat_roman_republic.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("nodes", [])


def load_lcc_nodes(seed_qid: str, survey_dir: Path) -> list:
    path = survey_dir / "lcc_roman_republic.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("nodes", [])


# ---------------------------------------------------------------------------
# Facet-specific evidence gathering
# ---------------------------------------------------------------------------

def gather_evidence(facet: str, seed_qid: str, landscape: dict,
                    worldcat_nodes: list, lcc_nodes: list) -> dict:
    """Dispatch to facet-specific evidence gathering. Returns evidence dict."""
    facet_pointer = landscape.get("facet_pointers", {}).get(facet, {})

    if facet == "POLITICAL":
        return _gather_political(facet_pointer, worldcat_nodes, lcc_nodes)
    elif facet == "MILITARY":
        return _gather_military(facet_pointer, worldcat_nodes, lcc_nodes)
    elif facet == "GEOGRAPHIC":
        return _gather_geographic(facet_pointer, worldcat_nodes, lcc_nodes)
    else:
        # Generic: SCA pointer + WorldCat/LCC filtered by facet keyword
        return _gather_generic(facet, facet_pointer, worldcat_nodes, lcc_nodes)


def _gather_political(facet_pointer: dict, worldcat_nodes: list, lcc_nodes: list) -> dict:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as s:
        # Top positions by POSITION_HELD count
        r = s.run("""
            MATCH (p:Position)<-[r:POSITION_HELD]-()
            RETURN p.label AS position, p.dprr_office_id AS id, count(r) AS holders
            ORDER BY holders DESC LIMIT 30
        """)
        magistracies = [{"position": rec["position"], "id": rec["id"],
                         "holders": rec["holders"]} for rec in r]

        # Total POSITION_HELD
        r2 = s.run("MATCH ()-[r:POSITION_HELD]->() RETURN count(r) AS total")
        total_ph = r2.single()["total"]

        # Distinct positions
        r3 = s.run("MATCH (p:Position) RETURN count(p) AS n")
        distinct_positions = r3.single()["n"]

    driver.close()

    # Filter WorldCat for POLITICAL topics
    political_terms = [
        "senate", "magistrat", "consul", "praetor", "republic", "govern",
        "constitu", "assembl", "tribune", "election", "politic", "law",
        "caesar", "senate", "civil war", "reform", "gracchi"
    ]
    wc_political = [
        n["label"] for n in worldcat_nodes
        if any(t in n.get("label", "").lower() or t in str(n.get("scope_note", "")).lower()
               for t in political_terms)
    ]

    # Filter LCC for POLITICAL headings
    political_lcc_ids = {
        "DG89", "DG91", "DG95", "DG99", "DG155", "DG167",
        "DG221-239", "DG241-259", "DG261-269",
        "KJA2095-2100", "KJA285-365", "KJA2-3660"
    }
    lcc_political = [
        {"id": n.get("id", ""), "label": n["label"]}
        for n in lcc_nodes
        if n.get("id", "") in political_lcc_ids or
           any(t in n.get("label", "").lower()
               for t in ["constitu", "magistr", "senate", "republic", "law", "politic"])
    ]

    return {
        "sca_pointer": facet_pointer,
        "magistracies": magistracies,
        "total_position_held_edges": total_ph,
        "distinct_positions": distinct_positions,
        "worldcat_political_titles": wc_political[:30],
        "lcc_political_headings": lcc_political,
    }


def _gather_military(facet_pointer: dict, worldcat_nodes: list, lcc_nodes: list) -> dict:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as s:
        # Military positions from DPRR
        r = s.run("""
            MATCH (p:Position)<-[r:POSITION_HELD]-()
            WHERE p.label IN ['legatus (lieutenant)', 'tribunus militum',
                              'tribunus militum consulari potestate', 'praefectus',
                              'magister equitum', 'propraetor', 'proconsul']
            RETURN p.label AS position, count(r) AS holders
            ORDER BY holders DESC
        """)
        military_positions = [{"position": rec["position"], "holders": rec["holders"]} for rec in r]

    driver.close()

    military_terms = ["war", "battle", "army", "legion", "militar", "campaign",
                      "conquest", "siege", "soldier", "punic", "gallic"]
    wc_military = [
        n["label"] for n in worldcat_nodes
        if any(t in n.get("label", "").lower() for t in military_terms)
    ]
    lcc_military = [
        {"id": n.get("id", ""), "label": n["label"]}
        for n in lcc_nodes
        if any(t in n.get("label", "").lower() for t in ["military", "war", "army"])
    ]

    return {
        "sca_pointer": facet_pointer,
        "military_positions": military_positions,
        "worldcat_military_titles": wc_military[:20],
        "lcc_military_headings": lcc_military,
    }


def _gather_geographic(facet_pointer: dict, worldcat_nodes: list, lcc_nodes: list) -> dict:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as s:
        r = s.run("MATCH (p:Place) RETURN count(p) AS total, count(p.lat) AS with_coords")
        place_stats = dict(r.single())

    driver.close()

    return {
        "sca_pointer": facet_pointer,
        "place_stats": place_stats,
    }


def _gather_generic(facet: str, facet_pointer: dict,
                    worldcat_nodes: list, lcc_nodes: list) -> dict:
    """Generic fallback: SCA pointer + keyword-filtered WorldCat."""
    keyword = facet.lower()
    wc_relevant = [
        n["label"] for n in worldcat_nodes
        if keyword in n.get("label", "").lower() or keyword in str(n.get("scope_note", "")).lower()
    ]
    return {
        "sca_pointer": facet_pointer,
        "worldcat_titles": wc_relevant[:20],
        "note": f"Generic evidence — no facet-specific graph queries wired for {facet}",
    }


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_TEMPLATE = """\
You are SFA_{facet}, the Subject Facet Agent for the {facet} facet of Chrystallum — a federated \
historical knowledge graph covering the Roman Republic (509–27 BCE).

Your role in the pipeline:
- The SCA (Subject Classification Agent) has already mapped the domain landscape and identified \
that the {facet} facet has HIGH relevance for this domain.
- You must propose concrete SubjectConcept nodes that the {facet} facet needs to represent its \
scope of the Roman Republic.

What is a SubjectConcept?
A SubjectConcept is a controlled, scoped node in the knowledge graph. It defines:
- The bounded topic area (e.g., "Roman Magistracies", "Senate", "Electoral Assemblies")
- The set of entities that will be MEMBER_OF it
- The facet it belongs to
- Its relationship to other SubjectConcepts (NARROWER_THAN)

SubjectConcept design rules (from D12):
- If a concept would have >12 direct child entities OR a crosslink_ratio >= 0.3 with \
another SubjectConcept, recommend splitting
- Each concept must have a clear scope boundary — entities in it belong to THIS facet scope
- Prefer 3–8 proposals rather than collapsing everything into 1 or exploding into 20+

Evidence quality hierarchy:
1. Library of Congress (LCC/LCSH) headings — strongest bibliographic signal
2. DPRR data (prosopographic database) — strongest empirical signal for Roman Republic
3. Wikidata anchor QIDs — classification backbone
4. WorldCat titles — broad coverage signal

OUTPUT: Return ONLY valid JSON matching this schema exactly — no prose, no markdown fences:
{{
  "facet": "{facet}",
  "seed_qid": "{seed_qid}",
  "seed_label": "{seed_label}",
  "proposals": [
    {{
      "proposed_label": "concise label for this SubjectConcept",
      "proposed_scope": "1–2 sentence description of what this concept covers",
      "evidence_basis": ["bullet 1", "bullet 2"],
      "anchor_qid": "Q-id or null",
      "lcc_anchor": "LCC heading id or null",
      "d12_split_recommended": true or false,
      "d12_note": "if split recommended: suggest child concepts; else empty string",
      "confidence": 0.0 to 1.0
    }}
  ],
  "sfa_notes": "1–3 sentences on key observations, boundary decisions, or risks"
}}"""


def build_user_message(facet: str, seed_qid: str, seed_label: str, evidence: dict) -> str:
    sca_ptr = evidence.get("sca_pointer", {})
    lines = [
        f"DOMAIN: {seed_label} ({seed_qid})",
        f"FACET: {facet}",
        "",
        "── SCA LANDSCAPE POINTER ───────────────────────────────────────────────",
        f"Relevance: {sca_ptr.get('relevance', 'unknown')}",
        f"Anchor QIDs: {sca_ptr.get('anchor_qids', [])}",
        f"Authority anchors: {sca_ptr.get('authority_anchors', {})}",
        f"Resource hint from SCA: {sca_ptr.get('resource_hint', 'none')}",
        "",
    ]

    # Facet-specific evidence blocks
    if facet == "POLITICAL":
        lines += [
            "── DPRR MAGISTRACY DATA ─────────────────────────────────────────────────",
            f"Total POSITION_HELD edges in graph: {evidence.get('total_position_held_edges')}",
            f"Distinct positions: {evidence.get('distinct_positions')}",
            "",
            "Top 30 positions by holder count:",
        ]
        for m in evidence.get("magistracies", []):
            lines.append(f"  [{m['id']:>3}] {m['position']:<40} {m['holders']} holders")

        lines += [
            "",
            "── LCC HEADINGS (POLITICAL) ─────────────────────────────────────────────",
        ]
        for h in evidence.get("lcc_political_headings", []):
            lines.append(f"  {h['id']:<20} {h['label']}")

        lines += [
            "",
            f"── WORLDCAT POLITICAL TITLES (sample, {len(evidence.get('worldcat_political_titles', []))}) ─",
        ]
        for t in evidence.get("worldcat_political_titles", [])[:20]:
            lines.append(f"  {t}")

    elif facet == "MILITARY":
        lines += ["── DPRR MILITARY POSITIONS ──────────────────────────────────────────────"]
        for m in evidence.get("military_positions", []):
            lines.append(f"  {m['position']:<40} {m['holders']} holders")
        lines += ["", "── WORLDCAT MILITARY TITLES ─────────────────────────────────────────────"]
        for t in evidence.get("worldcat_military_titles", []):
            lines.append(f"  {t}")

    elif facet == "GEOGRAPHIC":
        ps = evidence.get("place_stats", {})
        lines += [
            "── PLACE NODE STATS ─────────────────────────────────────────────────────",
            f"Total Place nodes: {ps.get('total')}",
            f"With coordinates: {ps.get('with_coords')}",
        ]
    else:
        lines += [
            f"── EVIDENCE (generic) ───────────────────────────────────────────────────",
            evidence.get("note", ""),
        ]
        for t in evidence.get("worldcat_titles", []):
            lines.append(f"  {t}")

    lines += [
        "",
        "──────────────────────────────────────────────────────────────────────────",
        "Based on this evidence, propose the SubjectConcept nodes needed for the "
        f"{facet} facet of Roman Republic. Apply D12 split rules. Return JSON only.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def propose(facet: str, seed_qid: str = "Q17167",
            landscape_dir: Path = None, survey_dir: Path = None,
            output_dir: Path = None, model: str = "claude-sonnet-4-6") -> dict:

    landscape_dir = landscape_dir or _root / "output" / "sca_landscape"
    survey_dir = survey_dir or _root / "output" / "nodes"
    output_dir = output_dir or _root / "output" / "sfa_proposals"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"SFA_{facet}: proposing SubjectConcepts for {seed_qid}")

    print("  Loading SCA landscape...")
    landscape = load_sca_landscape(seed_qid, landscape_dir)
    seed_label = "Roman Republic"  # could be loaded from landscape metadata if needed

    print("  Loading survey data...")
    worldcat_nodes = load_worldcat_nodes(seed_qid, survey_dir)
    lcc_nodes = load_lcc_nodes(seed_qid, survey_dir)

    print(f"  Gathering {facet} evidence...")
    evidence = gather_evidence(facet, seed_qid, landscape, worldcat_nodes, lcc_nodes)

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        facet=facet, seed_qid=seed_qid, seed_label=seed_label
    )
    user_message = build_user_message(facet, seed_qid, seed_label, evidence)

    print(f"  Calling Claude ({model})...")
    raw = call_claude(system_prompt, user_message, model=model)

    # Strip markdown fences if present
    stripped = raw.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        stripped = "\n".join(lines[1:])  # remove ```json line
        if stripped.endswith("```"):
            stripped = stripped[: stripped.rfind("```")]

    # Parse JSON
    try:
        proposals = json.loads(stripped)
    except json.JSONDecodeError as e:
        print(f"  WARNING: JSON parse failed ({e}) — saving raw response")
        proposals = {"parse_error": str(e), "raw": raw}

    # Save output
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"{facet}_{seed_qid}_{timestamp}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "facet": facet,
            "seed_qid": seed_qid,
            "model": model,
            "proposed_at": datetime.utcnow().isoformat(),
            "proposals_count": len(proposals.get("proposals", [])),
            "output": proposals,
        }, f, indent=2, ensure_ascii=False)

    print(f"  Saved: {out_path.name}")
    n = len(proposals.get("proposals", []))
    print(f"  Proposals: {n}")
    return proposals


def main():
    parser = argparse.ArgumentParser(
        description="SFA SubjectConcept Proposer — proposes SubjectConcepts for a facet"
    )
    parser.add_argument("--facet", required=True,
                        choices=[
                            "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHICAL", "COMMUNICATION",
                            "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC",
                            "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC",
                            "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC",
                            "SOCIAL", "TECHNOLOGICAL",
                        ],
                        help="Facet to propose SubjectConcepts for")
    parser.add_argument("--seed", default="Q17167",
                        help="Seed QID (default: Q17167 = Roman Republic)")
    parser.add_argument("--model", default="claude-sonnet-4-6",
                        help="Claude model (default: claude-sonnet-4-6)")
    args = parser.parse_args()

    result = propose(facet=args.facet, seed_qid=args.seed, model=args.model)

    proposals = result.get("proposals", [])
    if proposals:
        print()
        print(f"-- {args.facet} PROPOSALS " + "-" * 50)
        for i, p in enumerate(proposals, 1):
            split_flag = " [SPLIT RECOMMENDED]" if p.get("d12_split_recommended") else ""
            print(f"  {i}. {p['proposed_label']}{split_flag}")
            print(f"     Scope: {p['proposed_scope'][:100]}...")
            print(f"     Confidence: {p.get('confidence', '?')}")
            print(f"     Anchor: {p.get('anchor_qid', 'none')} | LCC: {p.get('lcc_anchor', 'none')}")
            if p.get("d12_note"):
                print(f"     D12: {p['d12_note'][:100]}...")
            print()
        sfa_notes = result.get("sfa_notes", "")
        if sfa_notes:
            print(f"SFA notes: {sfa_notes}")


if __name__ == "__main__":
    main()
