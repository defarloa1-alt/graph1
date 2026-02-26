#!/usr/bin/env python3
"""
Verify anchor QIDs against Wikidata.

Fetches the actual Wikidata label for each anchor QID and reports mismatches.
Run before harvest to catch wrong QIDs (e.g. Q3952=Plauen not Late Republic).

Usage:
    python scripts/analysis/verify_anchor_qids.py
    python scripts/analysis/verify_anchor_qids.py --anchors output/subject_concepts/subject_concept_anchors_qid_canonical.json
"""
import argparse
import json
import sys
import time
from pathlib import Path

import requests

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Graph1AnchorVerifier/1.0"


def _labels_compatible(our: str, wd: str) -> bool:
    """Heuristic: do labels refer to same concept?"""
    our_l, wd_l = our.lower(), wd.lower()
    # Shared significant word
    our_words = {w for w in our_l.split() if len(w) > 3}
    wd_words = {w for w in wd_l.split() if len(w) > 3}
    return bool(our_words & wd_words) or our_l in wd_l or wd_l in our_l


def fetch_wikidata_label(qid: str) -> str | None:
    """Get English label for QID from Wikidata API."""
    resp = requests.get(
        WIKIDATA_API,
        params={
            "action": "wbgetentities",
            "ids": qid,
            "props": "labels",
            "languages": "en",
            "format": "json",
        },
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    entities = data.get("entities", {})
    ent = entities.get(qid)
    if not ent or "labels" not in ent:
        return None
    en = ent["labels"].get("en")
    return en["value"] if en else None


def run_verification(anchors_path: Path, verbose: bool = True) -> list[dict]:
    """
    Verify anchor QIDs against Wikidata. Returns list of mismatches.
    Empty list = all OK.
    """
    with open(anchors_path, encoding="utf-8") as f:
        anchors = json.load(f)
    if isinstance(anchors, dict) and "anchors" in anchors:
        anchors = anchors["anchors"]

    mismatches = []
    for a in anchors:
        qid = a.get("qid")
        if not qid:
            continue
        our_label = (a.get("label") or "")[:50]
        wd_label = fetch_wikidata_label(qid)
        time.sleep(0.2)  # Be nice to API
        if wd_label and not _labels_compatible(our_label, wd_label):
            mismatches.append({"qid": qid, "our": our_label, "wd": wd_label or "(no label)"})
        if verbose:
            match = "MISMATCH" if (wd_label and not _labels_compatible(our_label, wd_label)) else "OK"
            print(f"  {qid}  {match}  our: {our_label}")
            print(f"         wd:  {wd_label or '(none)'}")
    return mismatches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--anchors",
        default="output/subject_concepts/subject_concept_anchors_qid_canonical.json",
        help="Anchors JSON path",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    path = root / args.anchors

    print("QID verification against Wikidata\n" + "=" * 60)
    mismatches = run_verification(path, verbose=True)
    print("=" * 60)
    if mismatches:
        print(f"\n{len(mismatches)} potential mismatches - verify before harvest:")
        for m in mismatches:
            print(f"  {m['qid']}: we say '{m['our']}' but Wikidata says '{m['wd']}'")
        sys.exit(1)
    else:
        print("\nAll labels appear to match.")


if __name__ == "__main__":
    main()
