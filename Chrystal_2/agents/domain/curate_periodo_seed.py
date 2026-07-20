#!/usr/bin/env python3
"""Curate tiny Rome PeriodO seed + write crosswalk CSV for Domain tools."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "CSV" / "periodo_roman_republic_clean2.csv"
OUT = ROOT / "Chrystal_2" / "federations" / "crosswalks" / "periodo_roman_republic_seed.csv"

# Curated: Q17167 LCSH-authority trio + Late RR soft + one Middle-Republic frame.
# Prefer Rome/Q17167 spatial; Late RR is Italy-spatial but historically useful soft.
SEED_SPECS = [
    {
        "periodo_id": "p06c6g3p3g3",
        "role": "chrono_full_republic_lcsh",
        "confidence": "high",
        "soft": False,
        "note": "LCSH-derived full Republic 510-30; aligns with Domain LCSH chrono strand",
    },
    {
        "periodo_id": "p06c6g3hb99",
        "role": "chrono_middle_late_lcsh",
        "confidence": "high",
        "soft": True,
        "note": "LCSH 265-30 variant; multi-aboutness sibling of 510-30 — keep both",
    },
    {
        "periodo_id": "p06c6g36mkq",
        "role": "chrono_early_lcsh",
        "confidence": "high",
        "soft": True,
        "note": "LCSH 510-265 Early Republic slice",
    },
    {
        "periodo_id": "p0jrrjbchh2",
        "role": "chrono_late_roman_republic",
        "confidence": "medium",
        "soft": True,
        "note": "Late Roman Republic; spatial Q38 in dump — soft enrichment only",
    },
]


def main() -> int:
    if not SRC.exists():
        raise SystemExit(f"Missing {SRC}")
    by_id: dict[str, dict] = {}
    with SRC.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            by_id[(row.get("id") or "").strip()] = row

    out_rows: list[dict] = []
    for spec in SEED_SPECS:
        pid = spec["periodo_id"]
        src = by_id.get(pid)
        if not src:
            print(f"WARN missing {pid} in {SRC.name}")
            continue
        spat = (src.get("spatial_anchor") or "").strip()
        qid = spat.rsplit("/", 1)[-1] if "wikidata.org" in spat else spat
        out_rows.append(
            {
                "periodo_id": pid,
                "label": src.get("label", ""),
                "start_year": src.get("temporal_start", ""),
                "end_year": src.get("temporal_end", ""),
                "spatial_qid": qid,
                "spatial_coverage_description": src.get(
                    "spatial_coverage_description", ""
                ),
                "authority_id": src.get("authority_id", ""),
                "uri": src.get("uri")
                or f"https://n2t.net/ark:/99152/{pid}",
                "domain_id": "roman_republic",
                "pack_qid": "Q17167",
                "role": spec["role"],
                "confidence": spec["confidence"],
                "soft": str(spec["soft"]).lower(),
                "note": spec["note"],
                "source_path": "CSV/periodo_roman_republic_clean2.csv",
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"Wrote {len(out_rows)} rows -> {OUT}")
    for r in out_rows:
        print(
            f"  {r['periodo_id']} {r['label']} "
            f"[{r['start_year']}…{r['end_year']}] soft={r['soft']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
