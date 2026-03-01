#!/usr/bin/env python3
"""
Survey LCC (Library of Congress Classification) for Roman Republic domain.

Reads Subjects/lcc_flat.csv (from LCC JSON hierarchy files) and optionally
Subjects/LCC/*_schedule.csv stubs. DG, DE, DF are not in lcc_flat — merged
from dg_schedule.csv, de_schedule.csv, df_schedule.csv when needed.

Output: FederationSurvey to output/nodes/lcc_roman_republic.json + CSV.

Output (FederationNode per LCC class):
  - concept_ref: https://id.loc.gov/authorities/classification/{code}
  - temporal_range: parsed from label where possible (e.g. "Late Republic")
  - spatial_anchor: None (alignment pass)

Usage:
  python scripts/backbone/subject/survey_lcc.py
  python scripts/backbone/subject/survey_lcc.py --prefix DG,DE,DF,PA,KJA
  python scripts/backbone/subject/survey_lcc.py --csv Subjects/lcc_flat.csv --prefix DA
  python scripts/backbone/subject/survey_lcc.py --prefix all
"""
import argparse
import csv
import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from federation_node_schema import (
    Federation,
    FederationSurvey,
    new_node,
    new_survey,
    parse_temporal_from_lcsh,
    validate_survey,
)

# Constants
DOMAIN_ROMAN = "roman_republic"  # when prefix is DG,DE,DF,PA,KJA
DOMAIN_FULL = "lcc"              # when prefix is all
SEED_ID = "DG261-269"
SEED_LABEL = "Late Republic"
LCC_BASE_URI = "https://id.loc.gov/authorities/classification"
DEFAULT_LCC_CSV = Path("Subjects/lcc_flat.csv")
STUB_CSVS = {
    "DG": Path("Subjects/LCC/dg_schedule.csv"),
    "DE": Path("Subjects/LCC/de_schedule.csv"),
    "DF": Path("Subjects/LCC/df_schedule.csv"),
    "KJA": Path("Subjects/LCC/kja_schedule.csv"),
}
# Roman Republic–relevant: DG (Italy), DE (Greco-Roman), DF (Greece), PA (Classical), KJA (Roman Law)
DEFAULT_PREFIXES = "DG,DE,DF,PA,KJA"


def _parse_float(val) -> float | None:
    if val is None or (isinstance(val, str) and not val.strip()):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _parse_temporal_from_label(label: str) -> tuple[int, int] | None:
    """Parse temporal range from LCC label (e.g. 'Late Republic', '510-30 B.C.')."""
    if not label:
        return None
    # Reuse LCSH-style patterns
    tr = parse_temporal_from_lcsh(label)
    if tr:
        return tr
    # DG-specific: "Late Republic" → -509 to -27
    if "late republic" in label.lower() or "republic" in label.lower():
        return (-509, -27)
    if "early republic" in label.lower():
        return (-509, -265)
    if "middle republic" in label.lower():
        return (-264, -133)
    if "early empire" in label.lower():
        return (-27, 96)
    if "regal" in label.lower():
        return (-753, -509)
    # DF (Greece): Hellenistic, Roman epoch
    if "hellenistic" in label.lower():
        return (-323, -146)
    if "roman epoch" in label.lower() and "greece" not in label.lower():
        return (-140, 476)
    if "alexander" in label.lower():
        return (-336, -323)
    if "persian wars" in label.lower():
        return (-499, -479)
    if "peloponnesian" in label.lower():
        return (-431, -404)
    return None


def load_csv(csv_path: Path, prefixes: list[str] | None) -> list[dict]:
    """Load LCC CSV, filter by prefix(es). Returns list of {id, code, prefix, start, end, label}."""
    rows = []
    prefix_set = {p.strip().upper() for p in prefixes} if prefixes else None
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = (row.get("code") or row.get("id") or "").strip()
            if not code:
                continue
            row_prefix = (row.get("prefix") or "").strip()
            if not row_prefix:
                m = re.match(r"^([A-Za-z]+)", code)
                row_prefix = m.group(1) if m else ""
            if prefix_set and row_prefix.upper() not in prefix_set:
                continue
            start = _parse_float(row.get("start"))
            end = _parse_float(row.get("end"))
            label = (row.get("label") or "").strip() or code
            rows.append({
                "id": code,
                "code": code,
                "prefix": row_prefix,
                "start": start,
                "end": end,
                "label": label,
            })
    return rows


def run_survey(
    out_path: Path,
    csv_path: Path | None = None,
    prefix: str = DEFAULT_PREFIXES,
    domain: str | None = None,
) -> int:
    project_root = Path(__file__).resolve().parents[3]
    csv_file = csv_path or (project_root / DEFAULT_LCC_CSV)
    if not csv_file.is_absolute():
        csv_file = project_root / csv_file

    prefixes = None if prefix.strip().lower() == "all" else [p.strip() for p in prefix.split(",") if p.strip()]
    if prefixes:
        prefix_set = {p.upper() for p in prefixes}
    else:
        prefix_set = None

    if not csv_file.exists():
        print(f"ERROR: CSV not found: {csv_file}")
        print("  Build with: python Subjects/2-10-26-latten_lcc.py")
        return 1

    # Default domain: lcc for full survey, roman_republic for scoped
    if domain is None:
        domain = DOMAIN_FULL if prefix.strip().lower() == "all" else DOMAIN_ROMAN

    rows = load_csv(csv_file, prefixes)
    seen = {r["code"] for r in rows}

    # DG, DE, DF are not in lcc_flat; merge from Subjects/LCC stubs when requested
    for stub_prefix, stub_path in STUB_CSVS.items():
        if prefix_set and stub_prefix in prefix_set:
            stub_file = project_root / stub_path
            if stub_file.exists():
                stub_rows = load_csv(stub_file, [stub_prefix])
                for r in stub_rows:
                    if r["code"] not in seen:
                        rows.append(r)
                        seen.add(r["code"])
                if stub_rows:
                    print(f"  Merged {len(stub_rows)} {stub_prefix} rows from {stub_path}")

    if not rows:
        print(f"WARN: No rows matching prefix={prefix} in {csv_file}")
        return 1

    survey = new_survey(
        Federation.LCC,
        domain,
        seed_id=SEED_ID,
        seed_label=SEED_LABEL,
        meta={"source": str(csv_file), "prefix": prefix, "prefixes": list(prefix_set) if prefix_set else "all"},
    )

    seed_found = False
    for r in rows:
        code = r["code"]
        label = r["label"]
        uri = f"{LCC_BASE_URI}/{code}"
        tr = _parse_temporal_from_label(label)
        is_seed = (code == SEED_ID)

        node = new_node(
            id=code,
            label=label,
            federation=Federation.LCC,
            domain=domain,
            uri=uri,
            depth=0,
            is_seed=is_seed,
            concept_ref=uri,
            temporal_range=tr,
            spatial_anchor=None,
            properties={
                "prefix": r["prefix"],
                "start": r["start"],
                "end": r["end"],
            },
        )
        survey.add_node(node)
        if is_seed:
            seed_found = True

    if seed_found and survey.nodes:
        seed_node = next(n for n in survey.nodes if n.is_seed)
        survey.seed_id = seed_node.id
        survey.seed_label = seed_node.label

    for w in validate_survey(survey):
        print(f"  [WARN] {w}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    survey.save(out_path)
    _write_survey_csv(survey, out_path.with_suffix(".csv"))
    return 0


def _write_survey_csv(survey: FederationSurvey, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id", "label", "federation", "domain", "uri", "concept_ref",
        "temporal_start", "temporal_end", "survey_depth", "is_seed",
        "prefix", "start", "end",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for n in survey.nodes:
            row = {
                "id": n.id,
                "label": n.label,
                "federation": n.federation,
                "domain": n.domain,
                "uri": n.uri,
                "concept_ref": n.concept_ref or "",
                "temporal_start": n.temporal_range[0] if n.temporal_range else "",
                "temporal_end": n.temporal_range[1] if n.temporal_range else "",
                "survey_depth": n.survey_depth,
                "is_seed": n.is_seed,
                "prefix": n.properties.get("prefix", ""),
                "start": n.properties.get("start", ""),
                "end": n.properties.get("end", ""),
            }
            w.writerow(row)
    print(f"  CSV: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Survey LCC (full or scoped)")
    parser.add_argument("--out", type=Path, default=Path("output/nodes/lcc_roman_republic.json"))
    parser.add_argument("--csv", type=Path, help=f"LCC CSV (default: {DEFAULT_LCC_CSV})")
    parser.add_argument(
        "--prefix",
        default=DEFAULT_PREFIXES,
        help="Comma-separated prefixes (default: DG,DE,DF,PA,KJA). Use 'all' for full LCC.",
    )
    parser.add_argument(
        "--domain",
        default=None,
        help="Domain (default: 'lcc' when prefix=all, 'roman_republic' otherwise)",
    )
    args = parser.parse_args()
    return run_survey(
        args.out,
        csv_path=args.csv,
        prefix=args.prefix,
        domain=args.domain,
    )


if __name__ == "__main__":
    raise SystemExit(main())
