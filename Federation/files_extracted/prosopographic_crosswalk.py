"""
prosopographic_crosswalk.py
---------------------------
Enriches Entity nodes (PERSON type) in Neo4j Aura with identifiers
from Trismegistos and LGPN by crosswalking from existing Wikidata QIDs.

Pipeline position: AFTER cluster_assignment, as an enrichment step.

Strategy:
  1. Find Entity nodes in graph with primary_facet = BIOGRAPHICAL
  2. For each entity that has a Wikidata QID:
     a. Query Wikidata P1696 (Trismegistos person ID) if present
     b. Query Wikidata P1838 (LGPN ID) if present
  3. If TM ID found: fetch Trismegistos PerResponder for full person data
  4. Store crosswalk IDs as properties on Entity node
  5. Create (:CrosswalkRecord) nodes linking to federation sources

Output modes:
  --cypher    Write enrichment Cypher file
  --write     Write directly to Neo4j Aura

Usage:
    python prosopographic_crosswalk.py \\
        --input output/cluster_assignment/member_of_edges.json \\
        --output-dir output/crosswalk \\
        --cypher

    # With direct Aura write:
    python prosopographic_crosswalk.py \\
        --input output/cluster_assignment/member_of_edges.json \\
        --output-dir output/crosswalk \\
        --write \\
        --neo4j-uri neo4j+s://YOUR_AURA_URI \\
        --neo4j-user neo4j \\
        --neo4j-password YOUR_PASSWORD

Dependencies:
    pip install requests neo4j
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional

import requests


# ---------------------------------------------------------------------------
# Wikidata property IDs for prosopographic crosswalks
# ---------------------------------------------------------------------------

# These are the Wikidata properties that link to prosopographic authorities
WIKIDATA_CROSSWALK_PROPS = {
    "P1696":  "trismegistos_person_id",   # Trismegistos person ID
    "P1838":  "lgpn_id",                  # LGPN ID
    "P1605":  "viaf_id",                  # VIAF (person authority)
    "P245":   "ulan_id",                  # ULAN (Getty)
    "P2959":  "lgpn_id_alt",              # LGPN alternate
}

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
TM_PERSON_API = "https://www.trismegistos.org/dataservices/per/index.php"

_wikidata_cache: dict = {}
_tm_cache: dict = {}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CrosswalkResult:
    entity_qid: str
    entity_label: str
    trismegistos_id: Optional[str] = None
    trismegistos_name: Optional[str] = None
    trismegistos_dates: Optional[str] = None
    trismegistos_place: Optional[str] = None
    lgpn_id: Optional[str] = None
    viaf_id: Optional[str] = None
    crosswalk_sources: list = field(default_factory=list)
    enriched: bool = False


# ---------------------------------------------------------------------------
# Wikidata crosswalk lookup
# ---------------------------------------------------------------------------

def fetch_wikidata_crosswalk(qid: str) -> dict:
    """
    Fetch prosopographic crosswalk IDs from Wikidata for a given QID.
    Returns dict of {property_label: value}.
    """
    if qid in _wikidata_cache:
        return _wikidata_cache[qid]

    try:
        resp = requests.get(
            WIKIDATA_API,
            params={
                "action": "wbgetentities",
                "ids": qid,
                "props": "claims|labels",
                "languages": "en",
                "format": "json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        entity = data.get("entities", {}).get(qid, {})

        if entity.get("missing") == "":
            _wikidata_cache[qid] = {}
            return {}

        result = {}
        claims = entity.get("claims", {})

        for prop_id, prop_label in WIKIDATA_CROSSWALK_PROPS.items():
            prop_claims = claims.get(prop_id, [])
            for claim in prop_claims:
                try:
                    val = claim["mainsnak"]["datavalue"]["value"]
                    if isinstance(val, str) and val:
                        result[prop_label] = val
                        break
                    elif isinstance(val, dict):
                        # Some props return structured values
                        str_val = val.get("text") or val.get("id") or str(val)
                        if str_val:
                            result[prop_label] = str_val
                            break
                except (KeyError, TypeError):
                    continue

        _wikidata_cache[qid] = result
        return result

    except Exception as e:
        print(f"  [warn] Wikidata fetch failed for {qid}: {e}", file=sys.stderr)
        _wikidata_cache[qid] = {}
        return {}

    finally:
        time.sleep(0.1)


# ---------------------------------------------------------------------------
# Trismegistos person lookup
# ---------------------------------------------------------------------------

def fetch_trismegistos_person(tm_id: str) -> dict:
    """
    Fetch person data from Trismegistos PerResponder API.
    Returns parsed person dict or empty dict on failure.
    """
    if tm_id in _tm_cache:
        return _tm_cache[tm_id]

    try:
        resp = requests.get(
            TM_PERSON_API,
            params={"id": tm_id, "format": "json"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        _tm_cache[tm_id] = data
        return data

    except Exception as e:
        print(f"  [warn] Trismegistos fetch failed for TM {tm_id}: {e}", file=sys.stderr)
        _tm_cache[tm_id] = {}
        return {}

    finally:
        time.sleep(0.15)


def parse_tm_person(data: dict) -> dict:
    """
    Extract useful fields from Trismegistos PerResponder JSON response.
    Field names may vary — be defensive.
    """
    if not data:
        return {}

    return {
        "name":   data.get("name") or data.get("label") or data.get("Name", ""),
        "dates":  data.get("dates") or data.get("date") or data.get("Date", ""),
        "place":  data.get("place") or data.get("Place", ""),
        "gender": data.get("gender") or data.get("Gender", ""),
        "uri":    data.get("uri") or data.get("URI", ""),
    }


# ---------------------------------------------------------------------------
# Core enrichment
# ---------------------------------------------------------------------------

def enrich_entities(
    entities: list[dict],
    biographical_only: bool = True,
) -> list[CrosswalkResult]:
    """
    For each entity, attempt Wikidata crosswalk → Trismegistos/LGPN lookup.
    """
    results = []

    # Filter to BIOGRAPHICAL entities if requested
    if biographical_only:
        targets = [e for e in entities if
                   e.get("primary_facet") == "BIOGRAPHICAL" or
                   "PERSON" in e.get("entity_types", []) or
                   e.get("primary_facet") == ""]
        # If no facet data, process all
        if not targets:
            targets = entities
    else:
        targets = entities

    # Deduplicate by entity_qid
    seen_qids = set()
    unique_targets = []
    for e in targets:
        qid = e.get("entity_qid")
        if qid and qid not in seen_qids:
            seen_qids.add(qid)
            unique_targets.append(e)

    print(f"Enriching {len(unique_targets)} unique entities via Wikidata crosswalk...")

    for i, entity in enumerate(unique_targets, 1):
        qid = entity.get("entity_qid", "")
        label = entity.get("entity_label", qid)

        result = CrosswalkResult(
            entity_qid=qid,
            entity_label=label,
        )

        # Step 1: Wikidata crosswalk
        crosswalk = fetch_wikidata_crosswalk(qid)

        tm_id = crosswalk.get("trismegistos_person_id")
        lgpn_id = crosswalk.get("lgpn_id")
        viaf_id = crosswalk.get("viaf_id")

        result.lgpn_id = lgpn_id
        result.viaf_id = viaf_id

        # Step 2: Trismegistos enrichment if TM ID found
        if tm_id:
            result.trismegistos_id = tm_id
            result.crosswalk_sources.append("Trismegistos")

            tm_data = fetch_trismegistos_person(tm_id)
            parsed = parse_tm_person(tm_data)
            result.trismegistos_name = parsed.get("name")
            result.trismegistos_dates = parsed.get("dates")
            result.trismegistos_place = parsed.get("place")

        if lgpn_id:
            result.crosswalk_sources.append("LGPN")

        if viaf_id:
            result.crosswalk_sources.append("VIAF")

        result.enriched = bool(tm_id or lgpn_id or viaf_id)

        results.append(result)

        if i % 20 == 0:
            print(f"  {i}/{len(unique_targets)} processed...", file=sys.stderr)

    return results


# ---------------------------------------------------------------------------
# Cypher generation
# ---------------------------------------------------------------------------

CYPHER_HEADER = """\
// ============================================================
// PROSOPOGRAPHIC CROSSWALK ENRICHMENT
// Generated: {generated_at}
// Entities processed: {total}
// Enriched: {enriched} ({enriched_pct}%)
// Sources: Trismegistos, LGPN, VIAF
// ============================================================

"""

CYPHER_ENRICH = """\
// {entity_label} ({entity_qid})
MATCH (e:Entity {{qid: '{entity_qid}'}})
SET
  e.trismegistos_id    = {tm_id},
  e.trismegistos_name  = {tm_name},
  e.trismegistos_dates = {tm_dates},
  e.trismegistos_place = {tm_place},
  e.lgpn_id            = {lgpn_id},
  e.viaf_id            = {viaf_id},
  e.crosswalk_sources  = {sources},
  e.crosswalk_enriched_at = datetime();

"""


def cypher_str(val) -> str:
    """Format a Python value as a Cypher literal."""
    if val is None:
        return "null"
    if isinstance(val, list):
        items = ", ".join(f"'{v}'" for v in val)
        return f"[{items}]"
    return f"'{str(val).replace(chr(39), chr(92) + chr(39))}'"


def generate_crosswalk_cypher(
    results: list[CrosswalkResult],
    output_path: Path,
):
    enriched = [r for r in results if r.enriched]
    total = len(results)
    enriched_pct = round(len(enriched) / total * 100, 1) if total else 0

    lines = [CYPHER_HEADER.format(
        generated_at=datetime.now(timezone.utc).isoformat(),
        total=total,
        enriched=len(enriched),
        enriched_pct=enriched_pct,
    )]

    for r in enriched:
        lines.append(CYPHER_ENRICH.format(
            entity_label=r.entity_label,
            entity_qid=r.entity_qid,
            tm_id=cypher_str(r.trismegistos_id),
            tm_name=cypher_str(r.trismegistos_name),
            tm_dates=cypher_str(r.trismegistos_dates),
            tm_place=cypher_str(r.trismegistos_place),
            lgpn_id=cypher_str(r.lgpn_id),
            viaf_id=cypher_str(r.viaf_id),
            sources=cypher_str(r.crosswalk_sources),
        ))

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"  Cypher written: {output_path} ({len(enriched)} enriched entities)")


# ---------------------------------------------------------------------------
# Neo4j direct write
# ---------------------------------------------------------------------------

WRITE_QUERY = """
MATCH (e:Entity {qid: $entity_qid})
SET
  e.trismegistos_id    = $trismegistos_id,
  e.trismegistos_name  = $trismegistos_name,
  e.trismegistos_dates = $trismegistos_dates,
  e.trismegistos_place = $trismegistos_place,
  e.lgpn_id            = $lgpn_id,
  e.viaf_id            = $viaf_id,
  e.crosswalk_sources  = $crosswalk_sources,
  e.crosswalk_enriched_at = datetime()
RETURN e.qid AS qid
"""


def write_crosswalk_to_neo4j(
    results: list[CrosswalkResult],
    uri: str,
    user: str,
    password: str,
):
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("Error: pip install neo4j", file=sys.stderr)
        sys.exit(1)

    driver = GraphDatabase.driver(uri, auth=(user, password))
    enriched = [r for r in results if r.enriched]
    created = 0
    failed = 0

    try:
        with driver.session() as session:
            for r in enriched:
                try:
                    session.run(
                        WRITE_QUERY,
                        entity_qid=r.entity_qid,
                        trismegistos_id=r.trismegistos_id,
                        trismegistos_name=r.trismegistos_name,
                        trismegistos_dates=r.trismegistos_dates,
                        trismegistos_place=r.trismegistos_place,
                        lgpn_id=r.lgpn_id,
                        viaf_id=r.viaf_id,
                        crosswalk_sources=r.crosswalk_sources,
                    )
                    created += 1
                except Exception as e:
                    failed += 1
                    if failed <= 5:
                        print(f"  [warn] {r.entity_qid}: {e}", file=sys.stderr)
    finally:
        driver.close()

    print(f"  Neo4j write: {created} enriched, {failed} failed")
    return created, failed


# ---------------------------------------------------------------------------
# Input loading
# ---------------------------------------------------------------------------

def load_entities(input_path: Path) -> list[dict]:
    """
    Load entity list from member_of_edges.json or all_facet_classifications.json.
    Accepts either format.
    """
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict) and "entities" in data:
        return data["entities"]

    return []


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Enrich PERSON entities with Trismegistos and LGPN identifiers"
    )
    parser.add_argument("--input", "-i", required=True,
        help="Path to member_of_edges.json or all_facet_classifications.json")
    parser.add_argument("--output-dir", "-o", default="output/crosswalk",
        help="Output directory (default: output/crosswalk)")
    parser.add_argument("--all-entities", action="store_true",
        help="Process all entities, not just BIOGRAPHICAL facet")
    parser.add_argument("--cypher", action="store_true",
        help="Generate Cypher enrichment file")
    parser.add_argument("--write", action="store_true",
        help="Write directly to Neo4j Aura")
    parser.add_argument("--neo4j-uri", default=None)
    parser.add_argument("--neo4j-user", default="neo4j")
    parser.add_argument("--neo4j-password", default=None)

    args = parser.parse_args()

    if not args.cypher and not args.write:
        print("Error: specify --cypher, --write, or both", file=sys.stderr)
        sys.exit(1)

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    if args.write and not args.neo4j_uri:
        print("Error: --write requires --neo4j-uri", file=sys.stderr)
        sys.exit(1)

    if args.write and not args.neo4j_password:
        import getpass
        args.neo4j_password = getpass.getpass("Neo4j password: ")

    print(f"\n{'='*70}")
    print("PROSOPOGRAPHIC CROSSWALK ENRICHMENT")
    print(f"{'='*70}")

    entities = load_entities(input_path)
    print(f"Loaded {len(entities)} entity records from {input_path.name}")

    results = enrich_entities(entities, biographical_only=not args.all_entities)

    enriched = [r for r in results if r.enriched]
    tm_count = sum(1 for r in results if r.trismegistos_id)
    lgpn_count = sum(1 for r in results if r.lgpn_id)
    viaf_count = sum(1 for r in results if r.viaf_id)

    print(f"\nEnrichment results:")
    print(f"  Total processed      : {len(results)}")
    print(f"  Enriched             : {len(enriched)} ({round(len(enriched)/len(results)*100,1) if results else 0}%)")
    print(f"  Trismegistos matches : {tm_count}")
    print(f"  LGPN matches         : {lgpn_count}")
    print(f"  VIAF matches         : {viaf_count}")

    # Save full results JSON
    results_path = output_dir / "crosswalk_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    print(f"\nFull results saved: {results_path}")

    if args.cypher:
        cypher_path = output_dir / "crosswalk_enrichment.cypher"
        generate_crosswalk_cypher(results, cypher_path)

    if args.write:
        write_crosswalk_to_neo4j(
            results,
            uri=args.neo4j_uri,
            user=args.neo4j_user,
            password=args.neo4j_password,
        )

    print(f"\n{'='*70}\nCROSSWALK COMPLETE\n{'='*70}")


if __name__ == "__main__":
    main()
