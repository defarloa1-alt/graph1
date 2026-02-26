#!/usr/bin/env python3
"""
LGPN Forward SPARQL Harvest

Fetches persons with LGPN ID via forward SPARQL — structurally different from
backlink harvest. Backlink from Q899409 (gens) returns 0 LGPN entities because
LGPN-attested persons are not backlinked to Q899409 in Wikidata.

LGPN Wikidata property: P1047 (D-023). P1838 is PSS-archi (buildings), not LGPN.

Usage:
    python scripts/tools/wikidata_lgpn_forward_harvest.py
    python scripts/tools/wikidata_lgpn_forward_harvest.py --limit 500 --output output/lgpn/lgpn_persons.json
    python scripts/tools/wikidata_lgpn_forward_harvest.py --domain-ancestor Q1747689  # Ancient Rome citizenship
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

import requests

ROOT = Path(__file__).resolve().parents[2]
SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "ChrystallumLGPNHarvest/1.0"
QID_RE = re.compile(r"Q\d+$", re.IGNORECASE)


def _wd_uri_to_id(uri: str) -> str:
    if "/entity/" in uri:
        return uri.split("/")[-1]
    return uri


def fetch_lgpn_persons(
    property_id: str = "P1047",
    limit: int = 1000,
    domain_ancestor: str | None = None,
    timeout_s: int = 60,
) -> list[dict]:
    """
    Forward SPARQL: persons with given property (LGPN ID).
    Default P1838 — verify: Wikidata P1838 is PSS-archi; LGPN may use different PID.
    Optional domain_ancestor: filter by P27 (citizenship) or P31/P279 (instance/subclass).
    """
    pid = property_id.strip().upper()
    if not re.match(r"^P\d+$", pid):
        raise ValueError(f"Invalid property ID: {property_id}")

    # Base: humans with external ID property
    where = f"""
    ?person wdt:P31 wd:Q5 .
    ?person wdt:{pid} ?lgpn .
    """
    if domain_ancestor:
        # Optional: citizenship of domain (e.g. Q1747689 Ancient Rome)
        where += f"""
    OPTIONAL {{ ?person wdt:P27 ?citizenship . ?citizenship wdt:P31/wdt:P279* wd:{domain_ancestor} . }}
    FILTER (BOUND(?citizenship))
    """

    query = f"""
SELECT ?person ?personLabel ?lgpn WHERE {{
  {where}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
LIMIT {max(1, limit)}
"""
    try:
        r = requests.get(
            SPARQL_URL,
            params={"query": query, "format": "json"},
            headers={"User-Agent": USER_AGENT},
            timeout=timeout_s,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        raise RuntimeError(f"SPARQL request failed: {e}") from e

    bindings = data.get("results", {}).get("bindings", [])
    out = []
    for b in bindings:
        uri = b.get("person", {}).get("value", "")
        qid = _wd_uri_to_id(uri)
        if not QID_RE.fullmatch(qid):
            continue
        label = (b.get("personLabel", {}).get("value", "") or "").strip()
        lgpn = (b.get("lgpn", {}).get("value", "") or "").strip()
        out.append({
            "qid": qid,
            "label": label,
            "external_ids": {pid: lgpn},
            "scoping_status": "temporal_scoped",
            "scoping_confidence": 0.95,
        })
    return out


def main():
    parser = argparse.ArgumentParser(description="Forward SPARQL harvest for LGPN persons")
    parser.add_argument("--property", "-p", default="P1047", help="Wikidata property for LGPN ID (default P1047)")
    parser.add_argument("--limit", type=int, default=1000, help="Max persons to fetch (default 1000)")
    parser.add_argument("--domain-ancestor", help="Optional: filter by citizenship/type ancestor QID (e.g. Q1747689 Ancient Rome)")
    parser.add_argument("--output", "-o", default="output/lgpn/lgpn_persons.json", help="Output JSON path")
    parser.add_argument("--timeout", type=int, default=60, help="SPARQL timeout (seconds)")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("LGPN FORWARD SPARQL HARVEST")
    print("=" * 60)
    print(f"Query: persons with {args.property}")
    if args.domain_ancestor:
        print(f"Domain filter: citizenship/type ancestor {args.domain_ancestor}")
    print(f"Limit: {args.limit}")
    print("=" * 60)

    persons = fetch_lgpn_persons(
        property_id=args.property,
        limit=args.limit,
        domain_ancestor=args.domain_ancestor,
        timeout_s=args.timeout,
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "forward_sparql",
        "property": args.property,
        "federation": "LGPN",
        "domain_ancestor": args.domain_ancestor,
        "count": len(persons),
        "accepted": persons,
    }

    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nFetched {len(persons)} persons with {args.property}")
    print(f"Output: {output_path}")
    print("\nNote: Output format compatible with cluster_assignment enrichment.")
    print("      Merge with Q899409 MEMBER_OF edges via entity_qid for domain linkage.")


if __name__ == "__main__":
    main()
