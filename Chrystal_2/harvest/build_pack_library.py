#!/usr/bin/env python3
"""Assemble Chrystal 2 pack library JSON from WD harvest artifacts.

Combines:
  - labeled statements (all seed properties)
  - external-id values on the seed
  - forward item links (1 hop)
  - accepted backlinks report

See chrystal_2/harvest/PACK_LIBRARY_CONTRACT.md.

Usage (repo root):
  python chrystal_2/harvest/build_pack_library.py --qid Q17167
  python chrystal_2/harvest/build_pack_library.py --qid Q17167 --refresh-statements
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_external_ids(claims: dict[str, list]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for pid, stmts in claims.items():
        for stmt in stmts:
            m = stmt.get("mainsnak") or {}
            if m.get("datatype") != "external-id" and m.get("value_type") != "external-id":
                continue
            val = m.get("value")
            if val is None or val == "":
                continue
            out.append(
                {
                    "pid": pid,
                    "property_label": m.get("property_label") or pid,
                    "value": val,
                    "statement_id": stmt.get("statement_id"),
                    "rank": stmt.get("rank"),
                }
            )
    return out


def _extract_forward_links(claims: dict[str, list]) -> list[dict[str, Any]]:
    by_qid: dict[str, dict[str, Any]] = {}
    for pid, stmts in claims.items():
        for stmt in stmts:
            m = stmt.get("mainsnak") or {}
            val = m.get("value")
            if not (isinstance(val, str) and val.startswith("Q")):
                continue
            entry = by_qid.setdefault(
                val,
                {
                    "qid": val,
                    "label": m.get("value_label") or val,
                    "via": [],
                },
            )
            if not entry.get("label") or entry["label"] == val:
                if m.get("value_label"):
                    entry["label"] = m["value_label"]
            via = {
                "pid": pid,
                "property_label": m.get("property_label") or pid,
                "statement_id": stmt.get("statement_id"),
                "rank": stmt.get("rank"),
            }
            if via not in entry["via"]:
                entry["via"].append(via)
            # Qualifier item values also count as forward context (not primary hop)
            for qpid, qsnaks in (stmt.get("qualifiers") or {}).items():
                for qs in qsnaks:
                    qv = qs.get("value")
                    if isinstance(qv, str) and qv.startswith("Q"):
                        qe = by_qid.setdefault(
                            qv,
                            {
                                "qid": qv,
                                "label": qs.get("value_label") or qv,
                                "via": [],
                            },
                        )
                        qvia = {
                            "pid": qpid,
                            "property_label": qs.get("property_label") or qpid,
                            "role": "qualifier",
                            "on_statement": stmt.get("statement_id"),
                            "parent_pid": pid,
                        }
                        if qvia not in qe["via"]:
                            qe["via"].append(qvia)
    return sorted(by_qid.values(), key=lambda x: x["qid"])


def _normalize_backlinks(report: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in report.get("accepted") or []:
        if not isinstance(row, dict):
            continue
        out.append(
            {
                "qid": row.get("qid"),
                "label": row.get("label"),
                "via_properties": row.get("properties") or [],
                "p31": row.get("p31") or [],
                "matched_classes": row.get("matched_classes") or [],
                "backlink_hits": row.get("backlink_hits"),
                "statement_profile": row.get("statement_profile"),
            }
        )
    return out


def build_pack(
    qid: str,
    statements_path: Path,
    backlinks_path: Path,
) -> dict[str, Any]:
    statements = _load(statements_path)
    if statements.get("qid") != qid:
        raise SystemExit(
            f"Statements qid {statements.get('qid')} != requested {qid}"
        )
    meta = statements.get("_meta") or {}
    if not meta.get("labeled"):
        raise SystemExit(f"Statements not labeled: {statements_path}")

    claims = statements.get("claims") or {}
    external_ids = _extract_external_ids(claims)
    forward_links = _extract_forward_links(claims)

    backlinks: list[dict[str, Any]] = []
    backlink_meta: dict[str, Any] = {}
    if backlinks_path.exists():
        report = _load(backlinks_path)
        backlinks = _normalize_backlinks(report)
        backlink_meta = {
            "generated_at": report.get("generated_at"),
            "counts": report.get("counts"),
            "path": str(backlinks_path.relative_to(ROOT)).replace("\\", "/"),
        }
    else:
        print(f"WARNING: missing backlinks report: {backlinks_path}")

    return {
        "_meta": {
            "rule": "Never pass PID or QID without label",
            "labeled": True,
            "contract": "chrystal_2/harvest/PACK_LIBRARY_CONTRACT.md",
            "pack_kind": "subject_domain_library",
            "generated_at": _now(),
            "pid_labels_resolved": meta.get("pid_labels_resolved"),
            "qid_labels_resolved": meta.get("qid_labels_resolved"),
            "sources": {
                "statements": str(statements_path.relative_to(ROOT)).replace(
                    "\\", "/"
                ),
                "backlinks": backlink_meta.get("path"),
                "backlinks_report_generated_at": backlink_meta.get(
                    "generated_at"
                ),
            },
        },
        "seed": {
            "qid": statements.get("qid"),
            "label": statements.get("label"),
            "description": statements.get("description"),
        },
        "statements": {
            "statement_count": statements.get("statement_count"),
            "property_count": statements.get("property_count"),
            "property_labels": statements.get("property_labels"),
            "claims": claims,
        },
        "external_ids": external_ids,
        "forward_links": forward_links,
        "backlinks": backlinks,
        "counts": {
            "statements": statements.get("statement_count"),
            "properties": statements.get("property_count"),
            "external_ids": len(external_ids),
            "forward_links": len(forward_links),
            "backlinks_accepted": len(backlinks),
            "backlink_report_counts": backlink_meta.get("counts"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qid", required=True)
    parser.add_argument(
        "--refresh-statements",
        action="store_true",
        help="Re-fetch labeled statements before assemble",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Default: JSON/wikidata/packs/{qid}_pack_library.json",
    )
    args = parser.parse_args()
    qid = args.qid.strip().upper()
    if not qid.startswith("Q"):
        print("qid must look like Q17167")
        return 2

    statements_path = (
        ROOT / "JSON" / "wikidata" / "statements" / f"{qid}_statements_full.json"
    )
    backlinks_path = (
        ROOT
        / "JSON"
        / "wikidata"
        / "backlinks"
        / f"{qid}_backlink_harvest_report.json"
    )
    out_path = args.output or (
        ROOT / "JSON" / "wikidata" / "packs" / f"{qid}_pack_library.json"
    )

    if args.refresh_statements or not statements_path.exists():
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "tools" / "wikidata_fetch_all_statements.py"),
            "--qid",
            qid,
            "--output",
            str(statements_path),
            "--summary-only",
        ]
        print("Refreshing statements:", " ".join(cmd))
        subprocess.check_call(cmd, cwd=str(ROOT))

    if not statements_path.exists():
        print(f"Missing statements: {statements_path}")
        return 2

    pack = build_pack(qid, statements_path, backlinks_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(pack, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    rel = str(out_path.relative_to(ROOT)).replace("\\", "/")
    c = pack["counts"]
    print(
        f"Wrote {rel} | statements={c['statements']} props={c['properties']} "
        f"external_ids={c['external_ids']} forward={c['forward_links']} "
        f"backlinks={c['backlinks_accepted']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
