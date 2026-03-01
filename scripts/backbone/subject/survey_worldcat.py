#!/usr/bin/env python3
"""
Survey LC bibliographic records (via SRU) for Roman Republic domain.

Uses LC SRU at http://lx2.loc.gov:210/LCDB (not WorldCat API).
Query: dc.subject="Rome History Republic" (or cql.anywhere for broader match)

Extracts: 650/651 LCSH ($0 URI), 050 LCC, 245 title, 035 OCLC, 010 LCCN.
new_node() with concept_ref from 650/651 $0, text_ref from WorldCat OCLC or LCCN.

Outputs FederationSurvey to output/nodes/worldcat_roman_republic.json + CSV.

Usage:
  python scripts/backbone/subject/survey_worldcat.py
  python scripts/backbone/subject/survey_worldcat.py --out output/nodes/worldcat_roman_republic.json --max 500
"""
import argparse
import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

_SCRIPTS = Path(__file__).resolve().parents[2]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from federation_node_schema import (
    Federation,
    FederationNode,
    FederationSurvey,
    new_node,
    new_survey,
    validate_survey,
)

# Constants
LC_SRU_URL = "http://lx2.loc.gov:210/LCDB"
USER_AGENT = "Chrystallum/1.0 (LC SRU survey)"
DOMAIN = "roman_republic"
DEFAULT_QUERY = 'dc.subject=Rome History Republic'
PAGE_SIZE = 50
MARC_NS = "{http://www.loc.gov/MARC21/slim}"


def _get_subfields(datafield) -> list[tuple[str, str]]:
    out = []
    for sf in datafield.findall(f"{MARC_NS}subfield"):
        code = sf.get("code")
        if code and sf.text:
            out.append((code, sf.text.strip()))
    return out


def _get_first(datafield, code: str) -> str | None:
    for c, v in _get_subfields(datafield):
        if c == code:
            return v
    return None


def _query_sru(query: str, start: int = 1, maximum: int = PAGE_SIZE) -> tuple[list, int]:
    params = {
        "operation": "searchRetrieve",
        "version": "1.1",
        "query": query,
        "startRecord": start,
        "maximumRecords": maximum,
        "recordSchema": "marcxml",
    }
    url = f"{LC_SRU_URL}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=60) as r:
        body = r.read().decode("utf-8")

    import xml.etree.ElementTree as ET
    root = ET.fromstring(body)
    ns = {"zs": "http://www.loc.gov/zing/srw/"}
    total = 0
    for n in root.findall(".//zs:numberOfRecords", ns):
        try:
            total = int(n.text)
        except (ValueError, TypeError):
            pass
        break

    records = []
    for rec in root.findall(f".//{MARC_NS}record"):
        records.append(rec)
    return records, total


def _extract_record(rec) -> dict | None:
    out = {"control_id": None, "oclc": None, "lccn": None, "title": None, "lcc": None, "concept_refs": []}

    for cf in rec.findall(f"{MARC_NS}controlfield"):
        if cf.get("tag") == "001" and cf.text:
            out["control_id"] = cf.text.strip()

    for df in rec.findall(f"{MARC_NS}datafield"):
        tag = df.get("tag")
        sfs = _get_subfields(df)

        if tag == "035":
            for c, v in sfs:
                if c == "a":
                    out["control_id"] = out["control_id"] or v
                if "(OCoLC)" in (v or "").upper():
                    m = re.search(r"\(OCoLC\)\s*0*(\d+)", v, re.I)
                    if m:
                        out["oclc"] = m.group(1)

        if tag == "010":
            a = _get_first(df, "a")
            if a:
                out["lccn"] = a.strip().replace(" ", "")

        if tag == "050":
            a = _get_first(df, "a")
            b = _get_first(df, "b")
            if a:
                out["lcc"] = f"{a} {b or ''}".strip()

        if tag == "245":
            a = _get_first(df, "a")
            b = _get_first(df, "b")
            if a:
                out["title"] = f"{a} {b or ''}".strip().rstrip("/")

        if tag in ("650", "651"):
            uri = _get_first(df, "0")
            if uri and ("id.loc.gov" in uri or "loc.gov" in uri):
                out["concept_refs"].append(uri)

    return out if (out["control_id"] or out["lccn"] or out["oclc"]) else None


def run_survey(
    out_path: Path,
    query: str = DEFAULT_QUERY,
    max_records: int = 500,
    domain: str = DOMAIN,
) -> int:
    survey = new_survey(
        Federation.WORLDCAT,
        domain,
        seed_id="",
        seed_label="Roman Republic bibliography",
        meta={"source": "LC SRU LCDB", "query": query},
    )

    seen = set()
    start = 1
    total_fetched = 0

    while total_fetched < max_records:
        records, total_available = _query_sru(query, start=start, maximum=min(PAGE_SIZE, max_records - total_fetched))
        if not records:
            break

        for rec in records:
            row = _extract_record(rec)
            if not row:
                continue

            node_id = row["oclc"] or row["lccn"] or row["control_id"]
            if not node_id or node_id in seen:
                continue
            seen.add(node_id)

            title = (row["title"] or "").strip() or f"Work {node_id}"
            concept_ref = row["concept_refs"][0] if row["concept_refs"] else None

            if row["oclc"]:
                text_ref = f"http://www.worldcat.org/oclc/{row['oclc']}"
            elif row["lccn"]:
                text_ref = f"http://lccn.loc.gov/{row['lccn']}"
            else:
                text_ref = None

            uri = text_ref or f"http://lccn.loc.gov/{node_id}" if node_id.isdigit() and len(node_id) >= 8 else ""

            node = new_node(
                id=str(node_id),
                label=title[:500],
                federation=Federation.WORLDCAT,
                domain=domain,
                uri=uri,
                depth=0,
                is_seed=False,
                concept_ref=concept_ref,
                text_ref=text_ref,
                properties={
                    "lcc": row["lcc"] or "",
                    "oclc": row["oclc"] or "",
                    "lccn": row["lccn"] or "",
                },
            )
            survey.add_node(node)
            total_fetched += 1
            if total_fetched >= max_records:
                break

        start += len(records)
        if len(records) < PAGE_SIZE:
            break

    if survey.nodes:
        survey.seed_id = survey.nodes[0].id
        survey.seed_label = survey.nodes[0].label[:80]

    for w in validate_survey(survey):
        print(f"  [WARN] {w}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    survey.save(out_path)
    _write_survey_csv(survey, out_path.with_suffix(".csv"))
    return 0


def _write_survey_csv(survey: FederationSurvey, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id", "label", "federation", "domain", "uri", "concept_ref", "text_ref",
        "survey_depth", "is_seed", "lcc", "oclc", "lccn",
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
                "text_ref": n.text_ref or "",
                "survey_depth": n.survey_depth,
                "is_seed": n.is_seed,
                "lcc": n.properties.get("lcc", ""),
                "oclc": n.properties.get("oclc", ""),
                "lccn": n.properties.get("lccn", ""),
            }
            w.writerow(row)
    print(f"  CSV: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Survey LC SRU for Roman Republic bibliography")
    parser.add_argument("--out", type=Path, default=Path("output/nodes/worldcat_roman_republic.json"))
    parser.add_argument("--query", default=DEFAULT_QUERY, help="CQL query (default: dc.subject=Rome History Republic)")
    parser.add_argument("--max", type=int, default=500, help="Max records to fetch")
    parser.add_argument("--domain", default=DOMAIN)
    args = parser.parse_args()
    return run_survey(args.out, query=args.query, max_records=args.max, domain=args.domain)


if __name__ == "__main__":
    raise SystemExit(main())
