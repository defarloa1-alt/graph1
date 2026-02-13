#!/usr/bin/env python3
"""Generate Wikidata property candidates for unmapped relationships from local catalog CSV.

Catalog source expected:
  CSV/wikiPvalues.csv

Master source:
  Relationships/relationship_types_registry_master.csv
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
from difflib import SequenceMatcher
from pathlib import Path


TOKEN_RE = re.compile(r"[a-z0-9]+", re.ASCII)
PID_RE = re.compile(r"/(P\d+)$", re.ASCII)


def norm_text(s: str) -> str:
    return " ".join(TOKEN_RE.findall((s or "").lower()))


def tokset(s: str) -> set[str]:
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
    for suff in (" by", " of", " to", " from"):
        if rel_h.endswith(suff):
            q.append(rel_h[: -len(suff)].strip())
    if rel_h.startswith("has "):
        q.append(rel_h[4:].strip())
    seen = set()
    out = []
    for item in q:
        item = item.strip()
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out[:3]


def parse_catalog(catalog_path: Path) -> list[dict[str, str]]:
    rows = list(csv.DictReader(catalog_path.open(encoding="utf-8", newline="")))
    out: list[dict[str, str]] = []
    for r in rows:
        prop_uri = (r.get("property") or "").strip()
        m = PID_RE.search(prop_uri)
        if not m:
            continue
        pid = m.group(1)
        out.append(
            {
                "pid": pid,
                "label": (r.get("propertyLabel") or "").strip(),
                "description": (r.get("propertyDescription") or "").strip(),
                "type": (r.get("type") or "").strip(),
            }
        )
    return out


def score(rel: str, rel_desc: str, query: str, cand: dict[str, str]) -> float:
    rel_n = norm_text(rel)
    desc_n = norm_text(rel_desc)
    qry_n = norm_text(query)
    lab_n = norm_text(cand["label"])
    cdesc_n = norm_text(cand["description"])
    c_tokens = tokset(f"{cand['label']} {cand['description']}")

    sim_rel = SequenceMatcher(None, rel_n, lab_n).ratio() if rel_n and lab_n else 0.0
    sim_qry = SequenceMatcher(None, qry_n, lab_n).ratio() if qry_n and lab_n else 0.0
    ov_rel = jaccard(tokset(rel_n), c_tokens)
    ov_desc = jaccard(tokset(desc_n), c_tokens)

    dtype_bonus = 0.05 if cand["type"].endswith("#WikibaseItem") else 0.0
    out = (0.40 * sim_rel) + (0.25 * sim_qry) + (0.20 * ov_rel) + (0.15 * ov_desc) + dtype_bonus
    return max(0.0, min(1.0, out))


def confidence(s: float) -> str:
    if s >= 0.82:
        return "high"
    if s >= 0.68:
        return "medium"
    return "low"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--master",
        default=r"c:\Projects\Graph1\Relationships\relationship_types_registry_master.csv",
    )
    parser.add_argument(
        "--catalog",
        default=r"c:\Projects\Graph1\CSV\wikiPvalues.csv",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Top candidates per unmapped relationship",
    )
    parser.add_argument(
        "--out",
        default="",
        help="Output path (default: Relationships/wikidata_p_catalog_candidates_YYYY-MM-DD.csv)",
    )
    args = parser.parse_args()

    master_path = Path(args.master)
    catalog_path = Path(args.catalog)
    if not master_path.exists():
        raise FileNotFoundError(master_path)
    if not catalog_path.exists():
        raise FileNotFoundError(catalog_path)

    out_path = (
        Path(args.out)
        if args.out
        else master_path.parent / f"wikidata_p_catalog_candidates_{dt.date.today().isoformat()}.csv"
    )

    master_rows = list(csv.DictReader(master_path.open(encoding="utf-8", newline="")))
    catalog = parse_catalog(catalog_path)
    unmapped = [r for r in master_rows if not (r.get("wikidata_property") or "").strip()]

    result_rows: list[dict[str, str]] = []
    for r in unmapped:
        rel = (r.get("relationship_type") or "").strip()
        cat = (r.get("category") or "").strip()
        rel_desc = (r.get("description") or "").strip()
        queries = alt_queries(rel, rel_desc)

        by_pid: dict[str, dict[str, str | float]] = {}
        for q in queries:
            qn = norm_text(q)
            if not qn:
                continue
            # Pre-filter: keep candidates where at least one query token appears in label or desc.
            q_tokens = tokset(qn)
            for cand in catalog:
                c_text_tokens = tokset(f"{cand['label']} {cand['description']}")
                if not (q_tokens & c_text_tokens):
                    continue
                s = score(rel, rel_desc, q, cand)
                prev = by_pid.get(cand["pid"])
                if not prev or s > float(prev["score"]):
                    by_pid[cand["pid"]] = {
                        "pid": cand["pid"],
                        "label": cand["label"],
                        "description": cand["description"],
                        "type": cand["type"],
                        "score": s,
                        "query_used": q,
                    }

        ranked = sorted(by_pid.values(), key=lambda x: float(x["score"]), reverse=True)[: max(1, args.top)]
        for idx, cand in enumerate(ranked, start=1):
            sc = float(cand["score"])
            result_rows.append(
                {
                    "relationship_type": rel,
                    "category": cat,
                    "description": rel_desc,
                    "rank": str(idx),
                    "suggested_wikidata_property": str(cand["pid"]),
                    "suggested_wikidata_label": str(cand["label"]),
                    "suggested_wikidata_description": str(cand["description"]),
                    "suggested_wikidata_type": str(cand["type"]),
                    "score": f"{sc:.3f}",
                    "confidence": confidence(sc),
                    "query_used": str(cand["query_used"]),
                    "method": "local_catalog_similarity",
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
            "suggested_wikidata_type",
            "score",
            "confidence",
            "query_used",
            "method",
            "review_status",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(result_rows)

    rels_with_candidates = len({r["relationship_type"] for r in result_rows})
    print(f"catalog_rows={len(catalog)}")
    print(f"unmapped_relationships={len(unmapped)}")
    print(f"relationships_with_candidates={rels_with_candidates}")
    print(f"candidate_rows={len(result_rows)}")
    print(f"output={out_path}")


if __name__ == "__main__":
    main()
