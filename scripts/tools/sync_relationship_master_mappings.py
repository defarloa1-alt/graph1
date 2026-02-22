#!/usr/bin/env python3
"""Sync CIDOC/CRMinf/Wikidata mapping fields into the master relationship registry.

Source of mappings:
  Relationships/relationship_types_seed.cypher

Target:
  Relationships/relationship_types_registry_master.csv
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
from pathlib import Path


SEED_PATTERN = re.compile(
    r'^\s*\{key:"(?P<key>[A-Z0-9_]+)".*?'
    r'reify_as:"(?P<reify_as>[^"]*)".*?'
    r'crm_code:(?P<crm_code>null|"[^"]*").*?'
    r'crm_kind:(?P<crm_kind>null|"[^"]*").*?'
    r'wikidata_pid:(?P<wikidata_pid>null|"[^"]*").*?'
    r'wikidata_label:(?P<wikidata_label>null|"[^"]*")',
    flags=re.ASCII,
)

CRMINF_REL_PATTERN = re.compile(r"^I\d+_", flags=re.ASCII)
CRMINF_CODE_PATTERN = re.compile(r"\b[IJ]\d+\b|I\d+_", flags=re.ASCII)


def _strip_token(token: str) -> str:
    token = token.strip()
    if token == "null":
        return ""
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    return token


def load_seed_map(seed_path: Path) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    for line in seed_path.read_text(encoding="utf-8").splitlines():
        m = SEED_PATTERN.match(line)
        if not m:
            continue
        key = m.group("key")
        mapping[key] = {
            "reify_as": _strip_token(m.group("reify_as")),
            "cidoc_crm_code": _strip_token(m.group("crm_code")),
            "cidoc_crm_kind": _strip_token(m.group("crm_kind")),
            "wikidata_pid": _strip_token(m.group("wikidata_pid")),
            "wikidata_label": _strip_token(m.group("wikidata_label")),
        }
    return mapping


def infer_crminf_applicable(row: dict[str, str]) -> str:
    rel = (row.get("relationship_type") or "").strip()
    cat = (row.get("category") or "").strip().lower()
    crm = (row.get("cidoc_crm_code") or "").strip()
    note = (row.get("note") or "").strip()

    if cat == "reasoning":
        return "true"
    if CRMINF_REL_PATTERN.match(rel):
        return "true"
    if CRMINF_CODE_PATTERN.search(crm):
        return "true"
    if "CRMinf" in note:
        return "true"
    return "false"


def ensure_columns(fieldnames: list[str]) -> list[str]:
    out = list(fieldnames)
    for col in (
        "reify_as",
        "cidoc_crm_code",
        "cidoc_crm_kind",
        "wikidata_label",
        "crminf_applicable",
        "mapping_source",
    ):
        if col not in out:
            out.append(col)
    return out


def sync_registry(master_path: Path, seed_map: dict[str, dict[str, str]]) -> dict[str, str | int]:
    with master_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not reader.fieldnames:
            raise RuntimeError(f"No header found in {master_path}")
        fieldnames = ensure_columns(reader.fieldnames)

    stats = {
        "rows_total": len(rows),
        "rows_seed_overlap": 0,
        "wikidata_filled_from_seed": 0,
        "reify_filled": 0,
        "crm_code_filled": 0,
        "crm_kind_filled": 0,
        "wikidata_label_filled": 0,
    }

    for row in rows:
        rel = (row.get("relationship_type") or "").strip()
        source = (row.get("source") or "").strip()
        seed = seed_map.get(rel)

        row.setdefault("reify_as", "")
        row.setdefault("cidoc_crm_code", "")
        row.setdefault("cidoc_crm_kind", "")
        row.setdefault("wikidata_label", "")
        row.setdefault("crminf_applicable", "")
        row.setdefault("mapping_source", "")

        if seed:
            stats["rows_seed_overlap"] += 1

            if seed["reify_as"] and not row["reify_as"]:
                stats["reify_filled"] += 1
            if seed["cidoc_crm_code"] and not row["cidoc_crm_code"]:
                stats["crm_code_filled"] += 1
            if seed["cidoc_crm_kind"] and not row["cidoc_crm_kind"]:
                stats["crm_kind_filled"] += 1
            if seed["wikidata_label"] and not row["wikidata_label"]:
                stats["wikidata_label_filled"] += 1
            if seed["wikidata_pid"] and not (row.get("wikidata_property") or "").strip():
                stats["wikidata_filled_from_seed"] += 1
                row["wikidata_property"] = seed["wikidata_pid"]

            row["reify_as"] = seed["reify_as"] or row["reify_as"]
            row["cidoc_crm_code"] = seed["cidoc_crm_code"] or row["cidoc_crm_code"]
            row["cidoc_crm_kind"] = seed["cidoc_crm_kind"] or row["cidoc_crm_kind"]
            row["wikidata_label"] = seed["wikidata_label"] or row["wikidata_label"]
            row["mapping_source"] = "relationship_types_seed.cypher"
        elif source == "crminf_alignment":
            row["mapping_source"] = "crminf_alignment"

        row["crminf_applicable"] = infer_crminf_applicable(row)

    backup = (
        master_path.parent
        / f"{master_path.stem}.pre_mapping_sync_{dt.date.today().isoformat()}{master_path.suffix}"
    )
    if not backup.exists():
        backup.write_text(master_path.read_text(encoding="utf-8"), encoding="utf-8")

    wrote_path = master_path
    try:
        with master_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
    except PermissionError:
        pending = master_path.with_name(master_path.stem + ".pending.csv")
        with pending.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        wrote_path = pending

    stats["backup_created"] = 1 if backup.exists() else 0
    stats["wrote_path"] = str(wrote_path)
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--master",
        default=r"c:\Projects\Graph1\Relationships\relationship_types_registry_master.csv",
        help="Path to master relationships CSV",
    )
    parser.add_argument(
        "--seed",
        default=r"c:\Projects\Graph1\Relationships\relationship_types_seed.cypher",
        help="Path to relationship seed cypher",
    )
    args = parser.parse_args()

    master_path = Path(args.master)
    seed_path = Path(args.seed)
    if not master_path.exists():
        raise FileNotFoundError(master_path)
    if not seed_path.exists():
        raise FileNotFoundError(seed_path)

    seed_map = load_seed_map(seed_path)
    stats = sync_registry(master_path, seed_map)

    print(f"seed_keys={len(seed_map)}")
    for k in (
        "rows_total",
        "rows_seed_overlap",
        "wikidata_filled_from_seed",
        "reify_filled",
        "crm_code_filled",
        "crm_kind_filled",
        "wikidata_label_filled",
        "backup_created",
    ):
        print(f"{k}={stats[k]}")
    print(f"wrote_path={stats['wrote_path']}")


if __name__ == "__main__":
    main()
