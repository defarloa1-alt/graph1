#!/usr/bin/env python3
"""
Step 1 of Minimal Fix: Find best Wikidata anchor per QID-less SubjectConcept.

1. Curated anchors (high-value concepts)
2. Wikidata search API (exact/semantic match)
3. Perplexity LLM (for remaining 73 - research theme -> best Wikidata QID)

Domain prefix: Uses subject_domain_config.ROOT_SUBJECT_QID (no hardcoded "rr").

Usage:
    python scripts/backbone/subject/find_subject_concept_anchors.py
    python scripts/backbone/subject/find_subject_concept_anchors.py --use-perplexity  # for the 73

Output:
    output/subject_concepts/subject_concept_wikidata_anchors.json
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

# Add project root for imports
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from scripts.config_loader import PERPLEXITY_API_KEY
except ImportError:
    PERPLEXITY_API_KEY = os.getenv("PPLX_API_KEY") or os.getenv("PERPLEXITY_API_KEY")

# Extract ONTOLOGY from load script via AST (no execution)
import ast

def extract_qid_less_concepts():
    path = PROJECT_ROOT / "scripts" / "backbone" / "subject" / "load_roman_republic_ontology.py"
    with open(path) as f:
        tree = ast.parse(f.read())
    ontology = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "ONTOLOGY" and isinstance(node.value, ast.Dict):
                    for k, v in zip(node.value.keys, node.value.values):
                        if isinstance(k, ast.Constant) and isinstance(v, ast.Dict):
                            sid = k.value
                            label = qid = None
                            for k2, v2 in zip(v.keys, v.values):
                                if isinstance(k2, ast.Constant):
                                    if k2.value == "label" and isinstance(v2, ast.Constant):
                                        label = v2.value
                                    elif k2.value == "qid" and isinstance(v2, ast.Constant):
                                        qid = v2.value  # None or 'Q17167'
                            if sid and label and not qid:
                                ontology[sid] = label
                    return ontology
    return {}

ontology = extract_qid_less_concepts()

# Fallback if ast parsing fails
if not ontology:
    ontology = {
        "subj_rr_governance": "Government and Constitutional Structure",
        "subj_rr_military": "Warfare and Military Systems",
        "subj_rr_society": "Society and Social Structure",
        "subj_rr_economy": "Economy and Resource Systems",
        "subj_rr_gov_institutions": "Institutions: Senate, Assemblies, Magistracies",
        "subj_rr_soc_patronage": "Patronage, Clientage, and Elite Networks",
        "subj_rr_soc_slavery_labor": "Slavery, Labor, and Dependency",
        "subj_rr_factions_civil_wars": "Civil wars and internal conflicts",
        "subj_rr_econ_land_agriculture": "Landholding, Agriculture, and Estates",
    }

WIKIDATA_SEARCH_URL = "https://www.wikidata.org/w/api.php"

# Curated anchors for high-value concepts (from pipeline analysis)
# Keys match ontology subject_id (legacy subj_rr_* for this domain; see subject_domain_config)
CURATED_ANCHORS = {
    "subj_rr_gov_institutions": "Q105427",   # Roman Senate
    "subj_rr_gov_senate": "Q105427",         # Roman Senate
    "subj_rr_gov_assemblies": "Q859980",     # Popular assemblies (Comitia)
    "subj_rr_gov_offices": "Q39686",         # Consul
    "subj_rr_off_consul_praetor": "Q39686", # Consul
    "subj_rr_mil_wars_campaigns": "Q46303",  # Punic Wars
    "subj_rr_factions_civil_wars": "Q1993655", # Civil war (Roman context)
    "subj_rr_soc_patronage": "Q1993655",     # Patron-client relationship
    "subj_rr_econ_land_agriculture": "Q11469", # ager publicus
    "subj_rr_econ_land_reform": "Q1363254",  # Agrarian law
    "subj_rr_soc_slavery_labor": "Q8464",    # Slavery in ancient Rome
    "subj_rr_battles_naval": "Q185816",      # Punic Wars (naval)
    "subj_rr_time_late_crisis": "Q1993655",  # Civil war
}


def search_wikidata(label: str, limit: int = 5, add_roman: bool = True) -> list[dict]:
    """Search Wikidata by label. Returns list of {qid, label, description}."""
    # Roman Republic concepts: add "Roman" or "Rome" to disambiguate
    search_term = f"{label} Roman" if add_roman and "roman" not in label.lower() and "rome" not in label.lower() else label
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "type": "item",
        "search": search_term,
        "limit": limit,
    }
    headers = {"User-Agent": "ChrystallumBot/1.0 (research project)"}
    try:
        r = requests.get(WIKIDATA_SEARCH_URL, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        results = []
        for item in data.get("search", []):
            results.append({
                "qid": item.get("id"),
                "label": item.get("label"),
                "description": item.get("description"),
            })
        return results
    except Exception as e:
        print(f"  [ERROR] {e}", file=sys.stderr)
        return []


def pick_best_candidate(candidates: list[dict], subject_label: str) -> dict | None:
    """Pick best Wikidata match. Prefer exact label match, then description relevance."""
    if not candidates:
        return None
    # First: exact or close label match
    subject_lower = subject_label.lower()
    for c in candidates:
        if c["label"] and subject_lower in c["label"].lower():
            return c
    for c in candidates:
        if c["label"] and c["label"].lower() in subject_lower:
            return c
    # Fallback: first result (Wikidata search is relevance-ranked)
    return candidates[0]


def perplexity_find_wikidata_anchor(label: str, domain_context: str = "Roman Republic") -> dict | None:
    """
    Use Perplexity to find the best Wikidata QID for a research theme label.
    
    Prompt: PID-to-facet style - return ONLY {qid, label, confidence}.
    NOT entity classification - no SubjectConcept creation.
    """
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY == "your_perplexity_key_here":
        return None
    url = "https://api.perplexity.ai/chat/completions"
    prompt = f"""Given this historiography research theme from {domain_context}:

Label: "{label}"

Find the single best Wikidata entity (QID) that anchors this theme. Prefer:
- Specific concepts (e.g. Roman Senate, Punic Wars, ager publicus)
- Over broad categories (e.g. "history", "war")
- Entities that would have backlinks useful for populating this SubjectConcept

Return ONLY valid JSON, no other text:
{{"qid": "Q12345", "label": "Exact Wikidata label", "confidence": 0.0-1.0}}

If no suitable Wikidata entity exists, return: {{"qid": null, "label": null, "confidence": 0.0}}
"""
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a scholarly historian. Respond ONLY with valid JSON."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        # Strip markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        data = json.loads(content)
        if data.get("qid") and data.get("confidence", 0) >= 0.5:
            return {"qid": data["qid"], "label": data.get("label"), "confidence": data.get("confidence", 0.7)}
        return None
    except Exception as e:
        print(f"  [Perplexity ERROR] {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Find Wikidata anchors for QID-less SubjectConcepts")
    parser.add_argument(
        "--use-perplexity",
        action="store_true",
        help="Use Perplexity LLM for concepts without Wikidata search match (the 73)",
    )
    parser.add_argument(
        "--domain",
        default="Roman Republic",
        help="Domain context for Perplexity (default: Roman Republic)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit processing to N concepts (0=all, for testing Perplexity)",
    )
    args = parser.parse_args()

    try:
        from scripts.backbone.subject.subject_domain_config import ROOT_SUBJECT_QID
        domain_note = f" (root={ROOT_SUBJECT_QID})"
    except ImportError:
        domain_note = ""

    out_dir = PROJECT_ROOT / "output" / "subject_concepts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "subject_concept_wikidata_anchors.json"

    items = list(ontology.items())
    if args.limit > 0:
        items = items[: args.limit]
        print("=" * 70)
        print(f"Step 1: Find Wikidata anchors (limit={args.limit})")
    else:
        print("=" * 70)
        print("Step 1: Find Wikidata anchors for QID-less SubjectConcepts")
    print("=" * 70)
    print(f"Concepts to resolve: {len(items)}{domain_note}")
    if args.use_perplexity:
        print("Mode: Perplexity LLM enabled for unresolved concepts")
    print()

    results = []
    for i, (subject_id, label) in enumerate(items, 1):
        disp = label[:55] + "..." if len(label) > 55 else label
        print(f"[{i}/{len(items)}] {subject_id}: {disp}")
        # Check curated anchors first
        if subject_id in CURATED_ANCHORS:
            qid = CURATED_ANCHORS[subject_id]
            results.append({
                "subject_id": subject_id,
                "label": label,
                "anchor_qid": qid,
                "anchor_label": f"(curated: {qid})",
                "confidence": "curated",
            })
            print(f"  -> {qid} [curated]")
            continue
        candidates = search_wikidata(label, limit=5)
        best = pick_best_candidate(candidates, label)
        if best:
            results.append({
                "subject_id": subject_id,
                "label": label,
                "anchor_qid": best["qid"],
                "anchor_label": best["label"],
                "anchor_description": best.get("description"),
                "confidence": "high" if best["label"] and label.lower() in best["label"].lower() else "medium",
            })
            print(f"  -> {best['qid']} ({best['label']})")
        elif args.use_perplexity and PERPLEXITY_API_KEY:
            # Perplexity fallback for the 73
            llm_result = perplexity_find_wikidata_anchor(label, args.domain)
            if llm_result:
                results.append({
                    "subject_id": subject_id,
                    "label": label,
                    "anchor_qid": llm_result["qid"],
                    "anchor_label": llm_result.get("label"),
                    "confidence": f"llm:{llm_result.get('confidence', 0.7):.2f}",
                })
                print(f"  -> {llm_result['qid']} ({llm_result.get('label', '')}) [Perplexity]")
            else:
                results.append({
                    "subject_id": subject_id,
                    "label": label,
                    "anchor_qid": None,
                    "anchor_label": None,
                    "confidence": "none",
                })
                print(f"  -> [no match]")
            time.sleep(1)  # Perplexity rate limit
        else:
            results.append({
                "subject_id": subject_id,
                "label": label,
                "anchor_qid": None,
                "anchor_label": None,
                "confidence": "none",
            })
            print(f"  -> [no match]")
        time.sleep(0.3)  # Wikidata rate limit

    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    matched = sum(1 for r in results if r["anchor_qid"])
    print()
    print(f"Done. {matched}/{len(results)} concepts have Wikidata anchors.")
    print(f"Output: {out_file}")
    if matched < len(results) and not args.use_perplexity:
        print()
        print("Tip: Run with --use-perplexity to resolve remaining concepts via LLM.")


if __name__ == "__main__":
    main()
