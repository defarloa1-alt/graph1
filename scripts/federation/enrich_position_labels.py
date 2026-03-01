#!/usr/bin/env python3
"""
enrich_position_labels.py
--------------------------
Enriches Position nodes (formerly Office) with human-readable label_name
and wikidata_qid by querying the DPRR SPARQL endpoint.

DPRR endpoint is behind CloudFlare bot protection as of 2026-03-01.
This script will work when the endpoint is accessible again.

Usage:
    python scripts/federation/enrich_position_labels.py [--dry-run]

Requirements:
    pip install requests neo4j
"""
import sys
import requests
from pathlib import Path

_scripts = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_scripts))
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

DPRR_ENDPOINT = "http://romanrepublic.ac.uk/rdf/endpoint/"
DPRR_ONTOLOGY = "http://romanrepublic.ac.uk/rdf/ontology#"

# ---------------------------------------------------------------------------
# SPARQL fetch
# ---------------------------------------------------------------------------

def fetch_dprr_office_labels() -> dict[str, str]:
    """
    Query DPRR SPARQL for all PostType labels.
    Returns {office_id_str: label_name} e.g. {"3": "Consul", "42": "Senator"}
    """
    sparql = f"""
    PREFIX vocab: <{DPRR_ONTOLOGY}>
    SELECT DISTINCT ?office ?officeLabel WHERE {{
      ?post a vocab:PostAssertion ;
            vocab:hasOffice ?office .
      OPTIONAL {{ ?office vocab:hasName ?officeLabel }}
    }}
    ORDER BY ?office
    LIMIT 500
    """
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "Chrystallum-Research/1.0 (historical-knowledge-graph; academic research)",
    }
    r = requests.get(DPRR_ENDPOINT, params={"query": sparql}, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()
    bindings = data.get("results", {}).get("bindings", [])

    mapping = {}
    for b in bindings:
        uri = b.get("office", {}).get("value", "")
        label = b.get("officeLabel", {}).get("value", "") if b.get("officeLabel") else ""
        office_id = uri.split("/")[-1]
        if office_id and label:
            mapping[office_id] = label
    return mapping


# ---------------------------------------------------------------------------
# Neo4j update
# ---------------------------------------------------------------------------

def enrich_positions(mapping: dict[str, str], dry_run: bool = False) -> dict:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    stats = {"found": 0, "enriched": 0, "missing_label": 0}

    with driver.session() as session:
        # Get all Position nodes
        result = session.run("MATCH (p:Position) RETURN p.label AS label")
        positions = [r["label"] for r in result]
        stats["found"] = len(positions)

        for pos_label in positions:
            label_name = mapping.get(str(pos_label))
            if not label_name:
                stats["missing_label"] += 1
                continue
            if not dry_run:
                session.run(
                    """
                    MATCH (p:Position {label: $label})
                    SET p.label_name = $label_name
                    """,
                    label=pos_label,
                    label_name=label_name,
                )
            stats["enriched"] += 1
            print(f"  Position {pos_label} -> '{label_name}'" + (" [dry-run]" if dry_run else ""))

    driver.close()
    return stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enrich Position nodes with DPRR label_name")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated, no writes")
    args = parser.parse_args()

    print("Fetching DPRR office labels...")
    try:
        mapping = fetch_dprr_office_labels()
    except Exception as e:
        # Check if bot-protected
        if "bot" in str(e).lower() or "cloudflare" in str(e).lower():
            print(f"ERROR: DPRR endpoint is behind CloudFlare bot protection.")
            print("Run this script from a browser session or wait for the protection to clear.")
        else:
            print(f"ERROR fetching DPRR labels: {e}")
        sys.exit(1)

    print(f"Got {len(mapping)} office label mappings from DPRR")

    print("\nEnriching Position nodes...")
    stats = enrich_positions(mapping, dry_run=args.dry_run)

    print(f"\nResult: {stats['found']} positions found, {stats['enriched']} enriched, "
          f"{stats['missing_label']} without DPRR label")
    if args.dry_run:
        print("[DRY RUN] No writes performed.")


if __name__ == "__main__":
    main()
