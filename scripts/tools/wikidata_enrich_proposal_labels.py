#!/usr/bin/env python3
"""Enrich a claim subgraph proposal so every QID has a human label."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.tools.wikidata_label_utils import (  # noqa: E402
    apply_labels_to_proposal,
    is_bare_qid_label,
    resolve_labels,
)

QID_RE = re.compile(r"^Q\d+$", re.IGNORECASE)


def _collect_qids(proposal: dict) -> set[str]:
    qids: set[str] = set()
    seed = (proposal.get("seed") or {}).get("qid")
    if seed:
        qids.add(seed.upper())
    for node in proposal.get("nodes") or []:
        q = node.get("qid")
        if q:
            qids.add(q.upper())
    for key in ("relationship_claim_proposals", "attribute_claim_proposals"):
        for row in proposal.get(key) or []:
            for side in ("subject", "object"):
                q = row.get(f"{side}_qid")
                if q:
                    qids.add(q.upper())
    for row in proposal.get("timeline_entries") or []:
        for k in ("subject_qid", "related_object_qid"):
            q = row.get(k)
            if q:
                qids.add(q.upper())
    return qids


def _count_bare(proposal: dict) -> int:
    n = 0
    for node in proposal.get("nodes") or []:
        if is_bare_qid_label(node.get("label"), node.get("qid", "")):
            n += 1
    for key in ("relationship_claim_proposals", "attribute_claim_proposals"):
        for row in proposal.get(key) or []:
            for side in ("subject", "object"):
                qid = row.get(f"{side}_qid")
                if qid and is_bare_qid_label(row.get(f"{side}_label"), qid):
                    n += 1
    return n


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", required=True, help="Proposal JSON path")
    parser.add_argument("--seed-index", help="Optional seed index for label hints")
    parser.add_argument(
        "--statement-dirs",
        nargs="*",
        default=[
            "JSON/wikidata/statements",
            "JSON/wikidata/statements/expansion",
        ],
    )
    parser.add_argument("--in-place", action="store_true", help="Overwrite input file")
    parser.add_argument("--output", help="Output path (default: <input>_labeled.json)")
    args = parser.parse_args()

    proposal_path = Path(args.proposal)
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    seed_qid = (proposal.get("seed") or {}).get("qid", "Q17167").upper()

    seed_index = None
    seed_index_path = Path(args.seed_index or f"JSON/wikidata/derived/{seed_qid}_seed_index.json")
    if seed_index_path.exists():
        seed_index = json.loads(seed_index_path.read_text(encoding="utf-8"))

    before = _count_bare(proposal)
    qids = _collect_qids(proposal)
    labels = resolve_labels(
        qids,
        seed_index=seed_index,
        statement_dirs=[Path(p) for p in args.statement_dirs],
        fetch_missing=True,
    )
    stats = apply_labels_to_proposal(proposal, labels)
    after = _count_bare(proposal)

    out_path = proposal_path if args.in_place else Path(args.output or proposal_path.with_name(proposal_path.stem + "_labeled.json"))
    out_path.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"qids={len(qids)} labels_resolved={len(labels)} patched_fields={stats['patched']}")
    print(f"bare_labels_before={before} bare_labels_after={after}")
    print(f"output={out_path}")
    if after > 0:
        print(f"WARNING: {after} endpoints still lack labels — re-run after rate limit clears or add to label cache")


if __name__ == "__main__":
    main()
