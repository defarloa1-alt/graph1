#!/usr/bin/env python3
"""
enrich_position_labels.py
--------------------------
Enriches Position nodes (formerly Office) with human-readable label
by loading from a static JSON mapping derived from the DPRR RDF Turtle dump.
Matches by dprr_office_id (integer), sets p.label = human name.

Static mapping source: scripts/federation/dprr_office_labels.json
  - Extracted from gillisandrew/dprr-mcp data/dprr.ttl (2026-03-01)
  - 204 office entries; ID = integer from <.../rdf/entity/Office/N>
  - Falls back to live DPRR SPARQL endpoint with --live flag

Usage:
    python scripts/federation/enrich_position_labels.py [--dry-run] [--live]

Requirements:
    pip install requests neo4j
"""
import sys
import json
import requests
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

STATIC_LABELS = Path(__file__).parent / "dprr_office_labels.json"
DPRR_ENDPOINT = "http://romanrepublic.ac.uk/rdf/endpoint/"
DPRR_ONTOLOGY = "http://romanrepublic.ac.uk/rdf/ontology#"


# ---------------------------------------------------------------------------
# Label sources
# ---------------------------------------------------------------------------

def load_static_labels() -> dict[str, str]:
    """Load office labels from the bundled static JSON (no network required)."""
    with open(STATIC_LABELS, encoding="utf-8") as f:
        return json.load(f)


def fetch_live_labels() -> dict[str, str]:
    """
    Query live DPRR SPARQL for PostType labels.
    NOTE: endpoint is behind Anubis/within.website bot protection as of 2026-03-01.
    Returns {office_id_str: label_name}.
    """
    sparql = f"""
    PREFIX vocab: <{DPRR_ONTOLOGY}>
    SELECT DISTINCT ?office ?officeLabel WHERE {{
      ?post a vocab:PostAssertion ;
            vocab:hasOffice ?office .
      OPTIONAL {{ ?office rdfs:label ?officeLabel }}
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
        raw_label = b.get("officeLabel", {}).get("value", "") if b.get("officeLabel") else ""
        # Strip "Office: " prefix if present (mirrors Turtle rdfs:label format)
        label = raw_label.removeprefix("Office: ").strip()
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
        result = session.run("MATCH (p:Position) RETURN p.dprr_office_id AS dprr_id")
        positions = [r["dprr_id"] for r in result]
        stats["found"] = len(positions)

        for dprr_id in positions:
            label_name = mapping.get(str(dprr_id))
            if not label_name:
                stats["missing_label"] += 1
                continue
            if not dry_run:
                session.run(
                    """
                    MATCH (p:Position {dprr_office_id: $dprr_id})
                    SET p.label = $label_name
                    """,
                    dprr_id=dprr_id,
                    label_name=label_name,
                )
            stats["enriched"] += 1
            print(f"  Position {dprr_id} -> '{label_name}'" + (" [dry-run]" if dry_run else ""))

    driver.close()
    return stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enrich Position nodes with DPRR label_name")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated, no writes")
    parser.add_argument("--live", action="store_true", help="Use live DPRR SPARQL endpoint instead of static JSON")
    args = parser.parse_args()

    if args.live:
        print("Fetching live DPRR office labels from SPARQL endpoint...")
        try:
            mapping = fetch_live_labels()
        except Exception as e:
            print(f"ERROR fetching live DPRR labels: {e}")
            print("Hint: DPRR endpoint may be behind Anubis bot protection.")
            sys.exit(1)
        print(f"Got {len(mapping)} office label mappings from live SPARQL")
    else:
        print(f"Loading static DPRR office labels from {STATIC_LABELS.name}...")
        mapping = load_static_labels()
        print(f"Loaded {len(mapping)} office label mappings")

    print("\nEnriching Position nodes...")
    stats = enrich_positions(mapping, dry_run=args.dry_run)

    print(f"\nResult: {stats['found']} positions found, {stats['enriched']} enriched, "
          f"{stats['missing_label']} without DPRR label")
    if args.dry_run:
        print("[DRY RUN] No writes performed.")


if __name__ == "__main__":
    main()
