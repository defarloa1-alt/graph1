#!/usr/bin/env python3
"""Curate LCSH/FAST/LCC crosswalk seeds into Chrystal_2/federations/crosswalks/."""

from __future__ import annotations

import csv
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "Chrystal_2" / "federations" / "crosswalks"


def extract_rr_sc_rows() -> list[dict[str, str]]:
    """Parse Neo path-export strings that embed SubjectConcept property maps."""
    text = (ROOT / "CSV" / "neo4j_query_table_data_2026-2-20.csv").read_text(
        encoding="utf-8", errors="replace"
    )
    pat = re.compile(r":SubjectConcept \{([^}]+)\}")
    want = {
        "subject_id",
        "label",
        "qid",
        "lcsh_id",
        "lcsh_heading",
        "fast_id",
        "lcc_class",
        "lcc_subclass",
        "primary_facet",
        "authority_federation_score",
    }
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for m in pat.finditer(text):
        blob = m.group(1)
        props = {
            k: v.strip()
            for k, v in re.findall(
                r"([A-Za-z_][A-Za-z0-9_]*): (.+?)(?=, [A-Za-z_][A-Za-z0-9_]*: |\Z)",
                blob,
            )
            if k in want
        }
        sid = props.get("subject_id", "")
        if not sid or sid in seen:
            continue
        if not any(props.get(k) for k in ("lcsh_id", "fast_id", "lcc_subclass", "lcc_class")):
            continue
        seen.add(sid)
        rows.append(
            {
                "subject_id": sid,
                "label": props.get("label", ""),
                "qid": props.get("qid", ""),
                "lcsh_id": props.get("lcsh_id", ""),
                "lcsh_heading": props.get("lcsh_heading", ""),
                "fast_id": props.get("fast_id", ""),
                "lcc_class": props.get("lcc_class", ""),
                "lcc_subclass": props.get("lcc_subclass", ""),
                "primary_facet": props.get("primary_facet", ""),
                "authority_federation_score": props.get(
                    "authority_federation_score", ""
                ),
                "provenance": "production_neo_snapshot_2026-02-20",
                "source_path": "CSV/neo4j_query_table_data_2026-2-20.csv",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise SystemExit(f"no rows for {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    sc_rows = extract_rr_sc_rows()
    write_csv(OUT / "roman_republic_sc_lcsh_fast_lcc.csv", sc_rows)

    disc_rows: list[dict] = []
    with (ROOT / "Disciplines" / "disciplines_with_authority.csv").open(
        encoding="utf-8", newline=""
    ) as f:
        for r in csv.DictReader(f):
            n = sum(1 for k in ("lcsh_id", "fast_id", "lcc") if (r.get(k) or "").strip())
            if n < 2:
                continue
            disc_rows.append(
                {
                    "qid": r.get("qid", ""),
                    "label": r.get("label", ""),
                    "lcsh_id": r.get("lcsh_id", ""),
                    "fast_id": r.get("fast_id", ""),
                    "lcc": r.get("lcc", ""),
                    "ddc": r.get("ddc", ""),
                    "strand_count": n,
                    "provenance": "disciplines_with_authority",
                    "source_path": "Disciplines/disciplines_with_authority.csv",
                }
            )
    write_csv(OUT / "qid_lcsh_fast_lcc_disciplines.csv", disc_rows)

    shutil.copy2(
        ROOT / "Subjects" / "CIP" / "cip_code,cip_title,lcc_classes,lcsh_term.csv",
        OUT / "cip_lcc_lcsh.csv",
    )
    shutil.copy2(
        ROOT / "Facets" / "lcc_fast_seed_mappings_legacy.json",
        OUT / "lcc_fast_seed_mappings_legacy.json",
    )

    seed_rows = [
        {
            "entity_kind": "SubjectDomain",
            "domain_id": "roman_republic",
            "qid": "Q17167",
            "label": "Roman Republic",
            "lcsh_id": "sh85115114",
            "lcsh_heading": "Rome--History--Republic, 510-30 B.C.",
            "fast_id": "",
            "lcc_class": "",
            "lcc_subclass": "",
            "confidence": "high",
            "role": "wd_p244_canonical_for_pack",
            "provenance": "wikidata_P244 + id.loc.gov resolve 2026-07-19",
            "note": "Chrystal_2 Librarian Domain tether used this LCSH",
        },
        {
            "entity_kind": "SubjectConcept_legacy",
            "domain_id": "roman_republic",
            "qid": "Q17167",
            "label": "Roman Republic",
            "lcsh_id": "sh85115055",
            "lcsh_heading": "Rome--History--Republic, 510-30 B.C.",
            "fast_id": "fst01204885",
            "lcc_class": "DG",
            "lcc_subclass": "DG254",
            "confidence": "medium",
            "role": "production_sc_props_2026-02-20",
            "provenance": "CSV/neo4j_query_table_data_2026-2-20.csv",
            "note": (
                "Same display heading text but different LCSH id than WD P244; "
                "FAST id is geographic soft facet Rome (Empire) on OCLC"
            ),
        },
    ]
    write_csv(OUT / "roman_republic_domain_authority_candidates.csv", seed_rows)

    fast_res = json.loads(
        (
            ROOT / "output" / "subject_concepts" / "subject_concept_fast_resolution.json"
        ).read_text(encoding="utf-8")
    )
    (OUT / "roman_republic_fast_resolution_candidates.json").write_text(
        json.dumps(fast_res, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote crosswalks to {OUT}")
    for p in sorted(OUT.iterdir()):
        print(f"  {p.name:55} {p.stat().st_size:>8} bytes")
    print(f"sc_rows={len(sc_rows)} disc_rows={len(disc_rows)}")


if __name__ == "__main__":
    main()
