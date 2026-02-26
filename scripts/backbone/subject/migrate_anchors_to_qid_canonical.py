#!/usr/bin/env python3
"""
migrate_anchors_to_qid_canonical.py
-----------------------------------
Converts legacy subject_id-based anchors to QID-canonical format.

Canonical model:
  - qid is the identity (no slug)
  - domain_qid scopes via DOMAIN_OF edge (not embedded in string)
  - One SubjectConcept per unique QID (shared anchors collapse)
  - Hierarchy via BROADER_THAN edges

Input:  output/subject_concepts/subject_concept_wikidata_anchors.json (legacy)
Output: output/subject_concepts/subject_concept_anchors_qid_canonical.json

Usage:
    python scripts/backbone/subject/migrate_anchors_to_qid_canonical.py
    python scripts/backbone/subject/migrate_anchors_to_qid_canonical.py --output path/to/new_anchors.json
"""
import argparse
import json
import sys
from pathlib import Path

# Ontology: subject_id -> parent subject_id (for hierarchy)
# Import ONTOLOGY only (load_roman_republic_ontology guards driver with __main__)
_scripts_dir = Path(__file__).resolve().parents[2]
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))
try:
    from backbone.subject.load_roman_republic_ontology import ONTOLOGY
except ImportError:
    ONTOLOGY = {}

ROOT_QID = "Q17167"
DOMAIN_LABEL = "Roman Republic"


def load_legacy_anchors(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, dict) and "anchors" in raw:
        raw = raw["anchors"]
    elif isinstance(raw, dict):
        raw = [{"subject_id": k, **v} for k, v in raw.items()]
    return raw if isinstance(raw, list) else []


def build_subject_id_to_qid(anchors: list[dict]) -> dict[str, str]:
    """Map legacy subject_id -> anchor_qid (for hierarchy resolution)."""
    out = {}
    for a in anchors:
        sid = a.get("subject_id")
        qid = a.get("anchor_qid") or a.get("qid")
        if sid and qid:
            out[sid] = qid
    # Root
    out["subj_roman_republic_q17167"] = ROOT_QID
    return out


def migrate(anchors: list[dict], ontology: dict) -> tuple[list[dict], list[dict]]:
    """
    Returns (anchors_canonical, hierarchy).
    anchors_canonical: one row per unique QID, qid as identity
    hierarchy: list of (child_qid, parent_qid) for BROADER_THAN
    """
    sid_to_qid = build_subject_id_to_qid(anchors)

    # One row per unique QID; for shared QIDs, keep first label (prefer curated)
    # Label: prefer ontology domain label over raw "(curated: Q...)" fallback
    by_qid: dict[str, dict] = {}
    for a in anchors:
        qid = a.get("anchor_qid") or a.get("qid")
        if not qid:
            continue
        label = a.get("label") or a.get("anchor_label", "")
        # Replace placeholder curated labels with ontology domain label
        if (not label or label.startswith("(curated: Q")) and a.get("subject_id") and a.get("subject_id") in ontology:
            label = ontology[a["subject_id"]].get("label", label)
        if qid not in by_qid:
            by_qid[qid] = {
                "qid": qid,
                "label": label,
                "domain_qid": ROOT_QID,
                "confidence": a.get("confidence", "unknown"),
                "primary_facet": _facet_from_ontology(a.get("subject_id"), ontology),
            }
        # Prefer curated label if we see one (and it's not a placeholder)
        al = a.get("anchor_label", "")
        if a.get("confidence") == "curated" and al and not str(al).startswith("(curated:"):
            by_qid[qid]["label"] = al

    # Add root
    by_qid[ROOT_QID] = {
        "qid": ROOT_QID,
        "label": DOMAIN_LABEL,
        "domain_qid": ROOT_QID,
        "confidence": "root",
        "primary_facet": "POLITICAL",
    }

    # Hierarchy: (child_qid, parent_qid) for BROADER_THAN; parent is broader
    # Exclude entries where child_qid == ROOT_QID (root must never be a child)
    hierarchy: list[tuple[str, str]] = []
    for sid, data in ontology.items():
        parent_sid = data.get("parent")
        if not parent_sid:
            continue
        child_qid = sid_to_qid.get(sid)
        parent_qid = sid_to_qid.get(parent_sid)
        if child_qid and parent_qid and child_qid != parent_qid and child_qid != ROOT_QID:
            hierarchy.append((child_qid, parent_qid))

    anchors_list = sorted(by_qid.values(), key=lambda x: x["qid"])
    hierarchy_list = [{"child_qid": c, "parent_qid": p} for c, p in hierarchy]
    return anchors_list, hierarchy_list


def _facet_from_ontology(subject_id: str, ontology: dict) -> str:
    if subject_id and subject_id in ontology:
        return ontology[subject_id].get("primary_facet", "")
    return ""


def main():
    parser = argparse.ArgumentParser(description="Migrate anchors to QID-canonical format")
    parser.add_argument(
        "--input", "-i",
        default="output/subject_concepts/subject_concept_wikidata_anchors.json",
        help="Legacy anchors file",
    )
    parser.add_argument(
        "--output", "-o",
        default="output/subject_concepts/subject_concept_anchors_qid_canonical.json",
        help="Output path for canonical anchors",
    )
    parser.add_argument(
        "--hierarchy-output",
        default="output/subject_concepts/subject_concept_hierarchy.json",
        help="Output path for BROADER_THAN hierarchy",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]  # Graph1/
    input_path = project_root / args.input
    output_path = project_root / args.output
    hierarchy_path = project_root / args.hierarchy_output

    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    anchors = load_legacy_anchors(input_path)
    anchors_canonical, hierarchy = migrate(anchors, ONTOLOGY)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(anchors_canonical, f, indent=2)

    with open(hierarchy_path, "w", encoding="utf-8") as f:
        json.dump({"broader_than": hierarchy}, f, indent=2)

    print(f"Migrated {len(anchors)} legacy anchors -> {len(anchors_canonical)} unique QIDs")
    print(f"Hierarchy: {len(hierarchy)} BROADER_THAN edges")
    print(f"Anchors:   {output_path}")
    print(f"Hierarchy: {hierarchy_path}")


if __name__ == "__main__":
    main()
