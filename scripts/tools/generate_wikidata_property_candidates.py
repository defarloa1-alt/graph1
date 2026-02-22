#!/usr/bin/env python3
"""Generate Wikidata property candidates for unmapped relationship types via API."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import time
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import requests


API_URL = "https://www.wikidata.org/w/api.php"
UA = "Graph1RelationshipMapper/1.0 (local automation)"
TOKEN_RE = re.compile(r"[a-z0-9]+", re.ASCII)


def norm_text(s: str) -> str:
    return " ".join(TOKEN_RE.findall((s or "").lower()))


def tokens(s: str) -> set[str]:
    return set(TOKEN_RE.findall((s or "").lower()))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def humanize_rel(rel: str) -> str:
    return rel.replace("_", " ").lower().strip()


def alt_queries(rel: str, desc: str) -> list[str]:
    q: list[str] = []
    rel_h = humanize_rel(rel)
    if rel_h:
        q.append(rel_h)
    if desc and desc.strip():
        q.append(desc.strip())

    # Heuristic variants for inverse-like keys.
    for suff in (" by", " of", " to", " from"):
        if rel_h.endswith(suff):
            q.append(rel_h[: -len(suff)].strip())
    if rel_h.startswith("has "):
        q.append(rel_h[4:].strip())
    if rel_h.startswith("is "):
        q.append(rel_h[3:].strip())

    # Deduplicate preserving order.
    out: list[str] = []
    seen = set()
    for item in q:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out[:3]


def api_search(query: str, limit: int = 10) -> list[dict[str, Any]]:
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "type": "property",
        "search": query,
        "limit": limit,
    }
    headers = {"User-Agent": UA}
    r = requests.get(API_URL, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json().get("search", [])


def score_candidate(
    rel_text: str,
    desc_text: str,
    query: str,
    cand_label: str,
    cand_desc: str,
    match_type: str,
) -> float:
    rel_n = norm_text(rel_text)
    desc_n = norm_text(desc_text)
    qry_n = norm_text(query)
    lab_n = norm_text(cand_label)
    ctext = f"{cand_label} {cand_desc}".strip()

    rel_tokens = tokens(rel_n)
    desc_tokens = tokens(desc_n)
    cand_tokens = tokens(ctext)

    sim_label = SequenceMatcher(None, rel_n, lab_n).ratio() if rel_n and lab_n else 0.0
    sim_query = SequenceMatcher(None, qry_n, lab_n).ratio() if qry_n and lab_n else 0.0
    ov_rel = jaccard(rel_tokens, cand_tokens)
    ov_desc = jaccard(desc_tokens, cand_tokens)
    match_bonus = 0.10 if match_type == "label" else 0.0

    score = (0.35 * sim_label) + (0.20 * sim_query) + (0.25 * ov_rel) + (0.20 * ov_desc) + match_bonus
    return max(0.0, min(1.0, score))


def confidence(score: float) -> str:
    if score >= 0.80:
        return "high"
    if score >= 0.65:
        return "medium"
    return "low"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--master",
        default=r"c:\Projects\Graph1\Relationships\relationship_types_registry_master.csv",
    )
    parser.add_argument(
        "--out",
        default="",
        help="Output CSV path (default: Relationships/wikidata_p_api_candidates_YYYY-MM-DD.csv)",
    )
    parser.add_argument("--top", type=int, default=3, help="Top candidates per relationship")
    parser.add_argument("--sleep-ms", type=int, default=80, help="Delay between API calls")
    args = parser.parse_args()

    master_path = Path(args.master)
    if not master_path.exists():
        raise FileNotFoundError(master_path)

    out_path = (
        Path(args.out)
        if args.out
        else master_path.parent / f"wikidata_p_api_candidates_{dt.date.today().isoformat()}.csv"
    )

    rows = list(csv.DictReader(master_path.open(encoding="utf-8", newline="")))
    unmapped = [r for r in rows if not (r.get("wikidata_property") or "").strip()]

    output_rows: list[dict[str, str]] = []
    api_calls = 0

    for r in unmapped:
        rel = (r.get("relationship_type") or "").strip()
        cat = (r.get("category") or "").strip()
        desc = (r.get("description") or "").strip()
        queries = alt_queries(rel, desc)

        by_pid: dict[str, dict[str, Any]] = {}
        for q in queries:
            try:
                results = api_search(q, limit=10)
                api_calls += 1
            except Exception:
                continue
            for cand in results:
                pid = (cand.get("id") or "").strip()
                if not pid:
                    continue
                label = (cand.get("label") or "").strip()
                cdesc = (cand.get("description") or "").strip()
                mtype = ((cand.get("match") or {}).get("type") or "").strip()
                score = score_candidate(rel, desc, q, label, cdesc, mtype)
                prev = by_pid.get(pid)
                if not prev or score > prev["score"]:
                    by_pid[pid] = {
                        "pid": pid,
                        "label": label,
                        "description": cdesc,
                        "score": score,
                        "query": q,
                        "match_type": mtype,
                    }
            time.sleep(max(0, args.sleep_ms) / 1000.0)

        ranked = sorted(by_pid.values(), key=lambda x: x["score"], reverse=True)[: max(1, args.top)]
        for i, cand in enumerate(ranked, start=1):
            output_rows.append(
                {
                    "relationship_type": rel,
                    "category": cat,
                    "description": desc,
                    "rank": str(i),
                    "suggested_wikidata_property": cand["pid"],
                    "suggested_wikidata_label": cand["label"],
                    "suggested_wikidata_description": cand["description"],
                    "score": f"{cand['score']:.3f}",
                    "confidence": confidence(cand["score"]),
                    "query_used": cand["query"],
                    "match_type": cand["match_type"],
                    "review_status": "pending_review",
                }
            )

    with out_path.open("w", encoding="utf-8", newline="") as f:
        fields = [
            "relationship_type",
            "category",
            "description",
            "rank",
            "suggested_wikidata_property",
            "suggested_wikidata_label",
            "suggested_wikidata_description",
            "score",
            "confidence",
            "query_used",
            "match_type",
            "review_status",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(output_rows)

    rels_with_candidates = len({r["relationship_type"] for r in output_rows})
    print(f"unmapped_relationships={len(unmapped)}")
    print(f"relationships_with_candidates={rels_with_candidates}")
    print(f"api_calls={api_calls}")
    print(f"candidate_rows={len(output_rows)}")
    print(f"output={out_path}")


if __name__ == "__main__":
    main()
