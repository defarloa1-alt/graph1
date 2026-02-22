#!/usr/bin/env python3
"""Enrich relationship registry rows from local Wikidata property catalog.

Safe operations:
1) For rows already mapped to wikidata_property (P###), fill metadata columns:
   - wikidata_label
   - wikidata_description
   - wikidata_datatype
   - wikidata_alt_labels
2) Generate strict exact-match suggestions for currently unmapped rows based on:
   - relationship_type humanized text matching property label or aliases
   - optional datatype gating (default: wikibase-item only)
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
from pathlib import Path


PID_RE = re.compile(r"^(P\d+)$", re.IGNORECASE)
TOKEN_RE = re.compile(r"[a-z0-9]+", re.ASCII)


def norm(s: str) -> str:
    return " ".join(TOKEN_RE.findall((s or "").lower())).strip()


def parse_aliases(raw: str) -> list[str]:
    if not raw:
        return []
    return [x.strip() for x in raw.split("|") if x.strip()]


def ensure_cols(fieldnames: list[str]) -> list[str]:
    out = list(fieldnames)
    for c in ("wikidata_description", "wikidata_datatype", "wikidata_alt_labels"):
        if c not in out:
            out.append(c)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--master",
        default=r"c:\Projects\Graph1\Relationships\relationship_types_registry_master.csv",
    )
    parser.add_argument(
        "--catalog",
        default=r"c:\Projects\Graph1\CSV\wikiPvalues_enriched.csv",
    )
    parser.add_argument(
        "--suggestions-out",
        default="",
        help="Optional suggestions output path",
    )
    parser.add_argument(
        "--allow-all-datatypes",
        action="store_true",
        help="Do not gate exact-match suggestions by wikibase-item datatype",
    )
    args = parser.parse_args()

    master_path = Path(args.master)
    cat_path = Path(args.catalog)
    if not master_path.exists():
        raise FileNotFoundError(master_path)
    if not cat_path.exists():
        raise FileNotFoundError(cat_path)

    if args.suggestions_out:
        sugg_path = Path(args.suggestions_out)
    else:
        sugg_path = (
            master_path.parent
            / f"relationship_type_p_suggestions_exact_alias_{dt.date.today().isoformat()}.csv"
        )

    master_rows = list(csv.DictReader(master_path.open(encoding="utf-8", newline="")))
    if not master_rows:
        raise RuntimeError("Master registry is empty.")
    master_fields = ensure_cols(list(master_rows[0].keys()))

    cat_rows = list(csv.DictReader(cat_path.open(encoding="utf-8", newline="")))
    cat_by_pid: dict[str, dict[str, str]] = {}
    label_index: dict[str, list[dict[str, str]]] = {}
    alias_index: dict[str, list[dict[str, str]]] = {}

    for r in cat_rows:
        pid = (r.get("pid") or "").strip().upper()
        if not PID_RE.match(pid):
            continue
        if (r.get("enrich_status") or "").strip() not in ("ok", ""):
            continue
        cat_by_pid[pid] = r

        lbl = norm(r.get("propertyLabel", ""))
        if lbl:
            label_index.setdefault(lbl, []).append(r)
        for a in parse_aliases(r.get("propertyAltLabels", "")):
            an = norm(a)
            if an:
                alias_index.setdefault(an, []).append(r)

    # 1) Enrich existing mapped rows
    metadata_updates = 0
    mapped_missing_catalog = 0
    for row in master_rows:
        pid = (row.get("wikidata_property") or "").strip().upper()
        if not PID_RE.match(pid):
            continue
        cat = cat_by_pid.get(pid)
        if not cat:
            mapped_missing_catalog += 1
            continue

        new_label = (cat.get("propertyLabel") or "").strip()
        new_desc = (cat.get("propertyDescription") or "").strip()
        new_type = (cat.get("datatype") or "").strip()
        new_alias = (cat.get("propertyAltLabels") or "").strip()

        changed = False
        if row.get("wikidata_label", "") != new_label and new_label:
            row["wikidata_label"] = new_label
            changed = True
        if row.get("wikidata_description", "") != new_desc:
            row["wikidata_description"] = new_desc
            changed = True
        if row.get("wikidata_datatype", "") != new_type:
            row["wikidata_datatype"] = new_type
            changed = True
        if row.get("wikidata_alt_labels", "") != new_alias:
            row["wikidata_alt_labels"] = new_alias
            changed = True
        if changed:
            metadata_updates += 1

    # 2) Strict exact alias/label suggestions for unmapped rows
    suggestions: list[dict[str, str]] = []
    for row in master_rows:
        if (row.get("wikidata_property") or "").strip():
            continue
        rel = (row.get("relationship_type") or "").strip()
        rel_text = norm(rel.replace("_", " "))
        if not rel_text:
            continue

        matches = []
        for cand in label_index.get(rel_text, []):
            matches.append(("label_exact", cand))
        for cand in alias_index.get(rel_text, []):
            matches.append(("alias_exact", cand))

        # De-duplicate by PID with best method precedence
        best_by_pid: dict[str, tuple[str, dict[str, str]]] = {}
        precedence = {"label_exact": 2, "alias_exact": 1}
        for method, cand in matches:
            pid = (cand.get("pid") or "").strip().upper()
            if not pid:
                continue
            prev = best_by_pid.get(pid)
            if not prev or precedence[method] > precedence[prev[0]]:
                best_by_pid[pid] = (method, cand)

        # Optional strict datatype gate
        filtered = []
        for pid, (method, cand) in best_by_pid.items():
            dtype = (cand.get("datatype") or "").strip()
            if not args.allow_all_datatypes and not dtype.endswith("#WikibaseItem"):
                continue
            filtered.append((pid, method, cand))

        # Keep only unique deterministic candidate
        if len(filtered) == 1:
            pid, method, cand = filtered[0]
            suggestions.append(
                {
                    "relationship_type": rel,
                    "category": row.get("category", ""),
                    "description": row.get("description", ""),
                    "suggested_wikidata_property": pid,
                    "suggested_wikidata_label": cand.get("propertyLabel", ""),
                    "suggested_wikidata_description": cand.get("propertyDescription", ""),
                    "suggested_wikidata_datatype": cand.get("datatype", ""),
                    "method": method,
                    "match_text": rel_text,
                    "review_status": "pending_review",
                }
            )

    # Backup + write master
    backup = (
        master_path.parent
        / f"{master_path.stem}.pre_property_catalog_enrichment_{dt.date.today().isoformat()}{master_path.suffix}"
    )
    if not backup.exists():
        backup.write_text(master_path.read_text(encoding="utf-8"), encoding="utf-8")

    with master_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=master_fields)
        w.writeheader()
        for r in master_rows:
            w.writerow({k: r.get(k, "") for k in master_fields})

    with sugg_path.open("w", encoding="utf-8", newline="") as f:
        fields = [
            "relationship_type",
            "category",
            "description",
            "suggested_wikidata_property",
            "suggested_wikidata_label",
            "suggested_wikidata_description",
            "suggested_wikidata_datatype",
            "method",
            "match_text",
            "review_status",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(sorted(suggestions, key=lambda x: (x["category"], x["relationship_type"])))

    print(f"master_rows={len(master_rows)}")
    print(f"catalog_rows={len(cat_rows)}")
    print(f"metadata_updates={metadata_updates}")
    print(f"mapped_missing_catalog={mapped_missing_catalog}")
    print(f"suggestions_exact={len(suggestions)}")
    print(f"suggestions_output={sugg_path}")
    print(f"backup={backup}")


if __name__ == "__main__":
    main()

