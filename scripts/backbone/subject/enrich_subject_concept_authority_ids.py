#!/usr/bin/env python3
"""
Enrich SubjectConcept nodes with authority IDs from Wikidata.

SPARQL VALUES queries (batched) for all 61 QIDs — fetches P244 (LCSH), P2163 (FAST),
P1149 (LCC) from Wikidata. Writes lcsh_id, fast_id, lcc_id back to each
SubjectConcept. Uses SET with CASE so it never nulls out a property that
already has a value.

Q1234567 and Q3952 are automatically skipped (flagged as suspects). Fix those
QIDs first, then re-run.

Supersedes: output/subject_concepts/subject_concept_fast_resolution.json
(manual mapping). Discard that file — this script derives from Wikidata.

Usage:
    # Step 1 — dry run first
    python scripts/backbone/subject/enrich_subject_concept_authority_ids.py --dry-run

    # Step 2 — write to Neo4j
    python scripts/backbone/subject/enrich_subject_concept_authority_ids.py --write

    # Offline dry-run (no Neo4j read)
    python scripts/backbone/subject/enrich_subject_concept_authority_ids.py --dry-run --offline
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_REVIEW = PROJECT_ROOT / "output" / "subject_concepts" / "authority_enrichment_review.md"
ANCHORS_PATH = PROJECT_ROOT / "output" / "subject_concepts" / "subject_concept_anchors_qid_canonical.json"

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"

# QIDs known to be placeholders or wrong — skip write, flag in report
SUSPECT_QIDS = frozenset({"Q1234567", "Q3952"})

# Hardcoded 61 QIDs (confirmed from live graph) for --offline
OFFLINE_QIDS = [
    "Q104867898", "Q105427", "Q11019", "Q11469", "Q1200427", "Q1234567", "Q1243998",
    "Q131416", "Q1363254", "Q1367629", "Q1392538", "Q15265460", "Q1541", "Q15800869",
    "Q1593880", "Q17167", "Q172845", "Q1747183", "Q1764124", "Q1812526", "Q182547",
    "Q185816", "Q186916", "Q1944199", "Q19895241", "Q1993655", "Q201452", "Q2063299",
    "Q2065169", "Q2067204", "Q1887031", "Q20720797", "Q207544", "Q337547", "Q211364",
    "Q212943", "Q213810", "Q2277", "Q2345364", "Q236885", "Q2576746", "Q271108",
    "Q2817119", "Q2862991", "Q2916317", "Q3277005", "Q3932035", "Q2815472", "Q39686",
    "Q4119583", "Q46303", "Q6106068", "Q657326", "Q726929", "Q838930", "Q7188",
    "Q8464", "Q859980", "Q899409", "Q9070", "Q952064",
]


def _get_qids(offline: bool, neo4j_uri: str, neo4j_password: str) -> list[str]:
    """Get QID list: from anchors JSON, Neo4j, or hardcoded."""
    if offline:
        return list(OFFLINE_QIDS)

    # Try anchors JSON first
    if ANCHORS_PATH.exists():
        with open(ANCHORS_PATH, encoding="utf-8") as f:
            anchors = json.load(f)
        return [a["qid"] for a in anchors]

    # Fallback: read from Neo4j
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(neo4j_uri, auth=("neo4j", neo4j_password or ""))
        with driver.session() as session:
            result = session.run(
                "MATCH (sc:SubjectConcept) WHERE sc.qid IS NOT NULL RETURN sc.qid AS qid ORDER BY sc.qid"
            )
            return [r["qid"] for r in result]
    except Exception as e:
        print(f"Could not read from Neo4j: {e}", file=sys.stderr)
        return list(OFFLINE_QIDS)


def _normalize_lcsh(val: str | None) -> str | None:
    """Extract LCSH ID from URI or raw value."""
    if not val:
        return None
    return val.split("/")[-1].strip() or None


def _normalize_fast(val: str | None) -> str | None:
    """Normalize FAST to fst + 8 digits."""
    if not val:
        return None
    raw = re.sub(r"^fst", "", str(val).strip())
    if not raw.isdigit():
        return val if val.startswith("fst") else None
    return "fst" + raw.zfill(8)


def _normalize_lcc(val: str | None) -> str | None:
    """LCC as-is."""
    return (val or "").strip() or None


def fetch_authority_ids(qids: list[str]) -> dict[str, dict]:
    """SPARQL VALUES query for QIDs. Batches of 20. Returns {qid: {lcsh_id, fast_id, lcc_id}}."""
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "ChrystallumBot/1.0 (federated-graph-framework; research project)",
    }
    out: dict[str, dict] = {}
    batch_size = 20
    for i in range(0, len(qids), batch_size):
        batch = qids[i : i + batch_size]
        values = " ".join(f"wd:{q}" for q in batch)
        # Compact query, no extra newlines
        query = (
            "SELECT ?item ?lcsh ?fast ?lcc WHERE { "
            f"VALUES ?item {{ {values} }} "
            "OPTIONAL { ?item wdt:P244 ?lcsh . } "
            "OPTIONAL { ?item wdt:P2163 ?fast . } "
            "OPTIONAL { ?item wdt:P1149 ?lcc . } "
            "}"
        )
        try:
            resp = requests.get(
                WIKIDATA_ENDPOINT,
                params={"query": query},
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            bindings = data.get("results", {}).get("bindings", [])
            for b in bindings:
                item_uri = b.get("item", {}).get("value", "")
                qid = item_uri.split("/")[-1] if item_uri else ""
                if not qid:
                    continue
                lcsh_raw = b.get("lcsh", {}).get("value")
                fast_raw = b.get("fast", {}).get("value")
                lcc_raw = b.get("lcc", {}).get("value")
                out[qid] = {
                    "lcsh_id": _normalize_lcsh(lcsh_raw),
                    "fast_id": _normalize_fast(fast_raw),
                    "lcc_id": _normalize_lcc(lcc_raw),
                }
        except Exception as e:
            print(f"  Batch failed ({batch[0]}..{batch[-1]}): {e}", file=sys.stderr)
            for qid in batch:
                out[qid] = {"lcsh_id": None, "fast_id": None, "lcc_id": None}
    return out


def classify_row(qid: str, row: dict) -> str:
    """FULL | PARTIAL | MISSING | FLAGGED."""
    if qid in SUSPECT_QIDS:
        return "FLAGGED"
    n = sum(1 for v in row.values() if v)
    if n == 3:
        return "FULL"
    if n > 0:
        return "PARTIAL"
    return "MISSING"


def write_review_report(results: dict[str, dict], labels: dict[str, str]) -> None:
    """Write output/subject_concepts/authority_enrichment_review.md."""
    OUTPUT_REVIEW.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Authority Enrichment Review",
        "",
        "**Source:** Wikidata SPARQL (P244 LCSH, P2163 FAST, P1149 LCC)",
        "",
        "| QID | Label | LCSH | FAST | LCC | Status |",
        "|-----|-------|------|------|-----|--------|",
    ]

    full_list, partial_list, missing_list, flagged_list = [], [], [], []
    for qid, row in sorted(results.items()):
        status = classify_row(qid, row)
        label = (labels.get(qid) or "")[:50]
        lcsh = row.get("lcsh_id") or "—"
        fast = row.get("fast_id") or "—"
        lcc = row.get("lcc_id") or "—"
        lines.append(f"| {qid} | {label} | {lcsh} | {fast} | {lcc} | {status} |")
        if status == "FULL":
            full_list.append(qid)
        elif status == "PARTIAL":
            partial_list.append(qid)
        elif status == "MISSING":
            missing_list.append(qid)
        else:
            flagged_list.append(qid)

    lines.extend([
        "",
        "---",
        "",
        f"**FULL:** {len(full_list)} | **PARTIAL:** {len(partial_list)} | **MISSING:** {len(missing_list)} | **FLAGGED:** {len(flagged_list)}",
        "",
    ])
    if flagged_list:
        lines.extend([
            "## FLAGGED (fix QID before re-run)",
            "",
            "These QIDs are known placeholders or wrong mappings. Do not write until fixed.",
            "",
        ])
        for qid in flagged_list:
            lines.append(f"- **{qid}** — {labels.get(qid, '')}")
        lines.append("")

    OUTPUT_REVIEW.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote: {OUTPUT_REVIEW}")


def write_to_neo4j(
    results: dict[str, dict],
    uri: str,
    user: str,
    password: str,
) -> int:
    """Write authority IDs to SubjectConcept nodes. Skips FLAGGED. Never nulls existing values."""
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(user, password or ""))
    written = 0
    with driver.session() as session:
        for qid, row in results.items():
            if qid in SUSPECT_QIDS:
                continue
            lcsh = row.get("lcsh_id")
            fast = row.get("fast_id")
            lcc = row.get("lcc_id")
            if not lcsh and not fast and not lcc:
                continue
            # SET only when we have a value; use CASE to avoid nulling existing
            session.run("""
                MATCH (sc:SubjectConcept {qid: $qid})
                SET sc.lcsh_id = CASE WHEN $lcsh IS NOT NULL AND $lcsh <> '' THEN $lcsh ELSE sc.lcsh_id END,
                    sc.fast_id = CASE WHEN $fast IS NOT NULL AND $fast <> '' THEN $fast ELSE sc.fast_id END,
                    sc.lcc_id = CASE WHEN $lcc IS NOT NULL AND $lcc <> '' THEN $lcc ELSE sc.lcc_id END
            """, qid=qid, lcsh=lcsh or None, fast=fast or None, lcc=lcc or None)
            written += 1
    driver.close()
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich SubjectConcept authority IDs from Wikidata")
    parser.add_argument("--dry-run", action="store_true", help="Query Wikidata, write review, no Neo4j write")
    parser.add_argument("--write", action="store_true", help="Write to Neo4j")
    parser.add_argument("--offline", action="store_true", help="Use hardcoded QID list, no Neo4j read")
    parser.add_argument("--neo4j-uri", default=os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    parser.add_argument("--neo4j-user", default=os.getenv("NEO4J_USERNAME", "neo4j"))
    parser.add_argument("--neo4j-password", default=os.getenv("NEO4J_PASSWORD"))
    args = parser.parse_args()

    # Load .env
    try:
        from dotenv import load_dotenv
        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        pass
    password = args.neo4j_password or os.getenv("NEO4J_PASSWORD", "")

    qids = _get_qids(args.offline, args.neo4j_uri, password)
    labels: dict[str, str] = {}
    if ANCHORS_PATH.exists():
        with open(ANCHORS_PATH, encoding="utf-8") as f:
            for a in json.load(f):
                labels[a["qid"]] = a.get("label", "")

    print(f"Fetching authority IDs for {len(qids)} QIDs...")
    results = fetch_authority_ids(qids)
    print(f"  Got {len(results)} rows from Wikidata")

    write_review_report(results, labels)

    if args.write:
        written = write_to_neo4j(results, args.neo4j_uri, args.neo4j_user, password)
        print(f"Wrote {written} SubjectConcept nodes (skipped {len(SUSPECT_QIDS)} FLAGGED)")
    else:
        print("Dry run. Use --write to persist.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
