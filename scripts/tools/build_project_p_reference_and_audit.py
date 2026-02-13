#!/usr/bin/env python3
"""Build canonical project P-value reference list and audit mismatches.

Scope is intentionally curated toward active docs/code and excludes:
- bulk source dumps (e.g., FAST/LCSH raw exports),
- generated audit artifacts,
- snapshot/backup registry files.
"""

from __future__ import annotations

import csv
import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PID_TOKEN = r"P(?:[1-9]\d*)"
PID_RE = re.compile(rf"(?<!crm:)\b({PID_TOKEN})\b(?![-.]\d)")
PID_LABEL_RE = re.compile(rf"(?<!crm:)\b({PID_TOKEN})\s*\(([^)\n]{{2,80}})\)")
REL_TABLE_RE = re.compile(r"^\|\s*\*\*([A-Z0-9_]+)\*\*\s*\|\s*(P\d+)\b", re.ASCII)
TOKEN_RE = re.compile(r"[a-z0-9]+", re.ASCII)


@dataclass
class LabelMismatch:
    path: str
    line: int
    pid: str
    found_label: str
    expected_label: str
    text: str


def norm(s: str) -> str:
    return " ".join(TOKEN_RE.findall((s or "").lower())).strip()


def iter_text_files(root: Path) -> Iterable[Path]:
    skip_dirs = {
        ".git",
        ".obsidian",
        "Archive",
        "__pycache__",
        ".venv",
        "venv",
        "FAST",
        "LCSH",
        "CIDOC",
    }
    skip_suffixes = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".pdf",
        ".xlsx",
        ".xls",
        ".zip",
        ".pyc",
        ".marcxml",
        ".jsonld",
        ".gz",
        ".db",
        ".out",
    }
    skip_names = {
        "wikiPvalues.csv",
        "wikiPvalues_enriched.csv",
        "wikiPvalues_alias_index.csv",
        "project_p_values_canonical.csv",
        "project_p_values_canonical_enriched.csv",
    }
    skip_rel_fragments = {
        str(Path("Python") / "fast" / ""),
        str(Path("md") / "Reference" / "P_VALUE_AUDIT_"),
        str(Path("Relationships") / "relationship_types_registry_master.pre_"),
        str(Path("Relationships") / "wikidata_p_unmapped_backlog_"),
        str(Path("Subjects") / "CIP" / ""),
    }
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        rel_parts = set(rel.parts)
        if rel_parts & skip_dirs:
            continue
        if p.name in skip_names:
            continue
        rel_str = str(rel).replace("/", "\\")
        if any(frag in rel_str for frag in skip_rel_fragments):
            continue
        if p.suffix.lower() in skip_suffixes:
            continue
        yield p


def load_catalog(catalog_path: Path) -> tuple[dict[str, dict[str, str]], dict[str, set[str]]]:
    rows = list(csv.DictReader(catalog_path.open(encoding="utf-8", newline="")))
    by_pid: dict[str, dict[str, str]] = {}
    aliases_by_pid: dict[str, set[str]] = {}
    for r in rows:
        pid = (r.get("pid") or "").strip().upper()
        if not pid:
            continue
        by_pid[pid] = r
        alias_norms = set()
        for raw in (r.get("propertyAltLabels") or "").split("|"):
            n = norm(raw)
            if n:
                alias_norms.add(n)
        aliases_by_pid[pid] = alias_norms
    return by_pid, aliases_by_pid


def main() -> None:
    root = Path(r"c:\Projects\Graph1")
    catalog = root / "CSV" / "wikiPvalues_enriched.csv"
    master_rel = root / "Relationships" / "relationship_types_registry_master.csv"
    consolidated = root / "Key Files" / "2-12-26 Chrystallum Architecture - CONSOLIDATED.md"

    if not catalog.exists():
        raise FileNotFoundError(catalog)
    if not master_rel.exists():
        raise FileNotFoundError(master_rel)

    by_pid, aliases_by_pid = load_catalog(catalog)
    usage: dict[str, dict[str, object]] = {}
    label_mismatches: list[LabelMismatch] = []

    for p in iter_text_files(root):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            try:
                text = p.read_text(encoding="utf-8-sig")
            except Exception:
                continue
        lines = text.splitlines()

        # PID usage collection
        for pid in PID_RE.findall(text):
            pid = pid.upper()
            info = usage.setdefault(pid, {"count": 0, "files": set()})
            info["count"] = int(info["count"]) + 1
            cast_files = info["files"]
            assert isinstance(cast_files, set)
            cast_files.add(str(p.relative_to(root)))

        # Parenthetical label mismatch audit
        for i, line in enumerate(lines, start=1):
            for m in PID_LABEL_RE.finditer(line):
                pid = m.group(1).upper()
                found_label = m.group(2).strip()
                cat = by_pid.get(pid)
                if not cat:
                    continue
                expected = (cat.get("propertyLabel") or "").strip()
                if not expected:
                    continue
                fn = norm(found_label)
                en = norm(expected)
                if not fn:
                    continue
                # Accept if exact label or listed alt label.
                if fn == en:
                    continue
                if fn in aliases_by_pid.get(pid, set()):
                    continue
                # Accept if near-exact containment.
                if en and (en in fn or fn in en):
                    continue
                label_mismatches.append(
                    LabelMismatch(
                        path=str(p.relative_to(root)),
                        line=i,
                        pid=pid,
                        found_label=found_label,
                        expected_label=expected,
                        text=line.strip(),
                    )
                )

    # Relationship table mismatch audit in consolidated doc
    rel_rows = list(csv.DictReader(master_rel.open(encoding="utf-8", newline="")))
    rel_to_pid = {
        (r.get("relationship_type") or "").strip().upper(): (r.get("wikidata_property") or "").strip().upper()
        for r in rel_rows
        if (r.get("relationship_type") or "").strip()
    }
    table_mismatches: list[tuple[int, str, str, str]] = []
    if consolidated.exists():
        for ln, line in enumerate(consolidated.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            m = REL_TABLE_RE.match(line)
            if not m:
                continue
            rel, pid = m.group(1).upper(), m.group(2).upper()
            expected = rel_to_pid.get(rel, "")
            if expected and expected != pid:
                table_mismatches.append((ln, rel, pid, expected))

    # Write canonical project P reference list.
    ref_out = root / "CSV" / "project_p_values_canonical.csv"
    ref_rows = []
    for pid, info in sorted(usage.items(), key=lambda kv: int(kv[0][1:])):
        cat = by_pid.get(pid, {})
        files = sorted(info["files"])  # type: ignore[index]
        ref_rows.append(
            {
                "pid": pid,
                "propertyLabel": cat.get("propertyLabel", ""),
                "propertyDescription": cat.get("propertyDescription", ""),
                "datatype": cat.get("datatype", ""),
                "occurrences": info["count"],
                "file_count": len(files),
                "sample_files": " | ".join(files[:5]),
                "in_catalog": "yes" if pid in by_pid else "no",
            }
        )
    with ref_out.open("w", encoding="utf-8", newline="") as f:
        fields = [
            "pid",
            "propertyLabel",
            "propertyDescription",
            "datatype",
            "occurrences",
            "file_count",
            "sample_files",
            "in_catalog",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(ref_rows)

    # Write audit markdown report.
    report_out = root / "md" / "Reference" / f"P_VALUE_AUDIT_{dt.date.today().isoformat()}.md"
    report_out.parent.mkdir(parents=True, exist_ok=True)
    unknown = [r for r in ref_rows if r["in_catalog"] == "no"]
    with report_out.open("w", encoding="utf-8", newline="") as f:
        f.write("# P Value Audit\n\n")
        f.write(f"- Date: {dt.date.today().isoformat()}\n")
        f.write(f"- Total unique P values in active files: {len(ref_rows)}\n")
        f.write(f"- Unknown P values (not in catalog): {len(unknown)}\n")
        f.write(f"- Parenthetical label mismatches: {len(label_mismatches)}\n")
        f.write(f"- Consolidated relationship-table mismatches: {len(table_mismatches)}\n")
        f.write(f"- Canonical list: `CSV/project_p_values_canonical.csv`\n\n")

        if unknown:
            f.write("## Unknown P Values\n\n")
            for r in unknown:
                f.write(f"- `{r['pid']}` in {r['sample_files']}\n")
            f.write("\n")

        if table_mismatches:
            f.write("## Consolidated Table Mismatches\n\n")
            f.write("| Line | Relationship | Found PID | Expected PID |\n")
            f.write("|---:|---|---|---|\n")
            for ln, rel, found, exp in table_mismatches:
                f.write(f"| {ln} | `{rel}` | `{found}` | `{exp}` |\n")
            f.write("\n")

        if label_mismatches:
            f.write("## Parenthetical Label Mismatches (Sample)\n\n")
            f.write("| File | Line | PID | Found Label | Expected Label |\n")
            f.write("|---|---:|---|---|---|\n")
            for m in label_mismatches[:200]:
                f.write(
                    f"| `{m.path}` | {m.line} | `{m.pid}` | `{m.found_label}` | `{m.expected_label}` |\n"
                )
            f.write("\n")

    print(f"project_unique_p={len(ref_rows)}")
    print(f"unknown_p={len(unknown)}")
    print(f"label_mismatches={len(label_mismatches)}")
    print(f"table_mismatches={len(table_mismatches)}")
    print(f"canonical_list={ref_out}")
    print(f"audit_report={report_out}")


if __name__ == "__main__":
    main()
