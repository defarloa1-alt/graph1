#!/usr/bin/env python3
"""
Canonicalize PID Edges - Add Semantic Properties

Stamp canonical properties on existing PID edges:
- canonical_type (INSTANCE_OF, PART_OF, etc.)
- canonical_category (Hierarchical, Temporal, etc.)
- cidoc_crm_property
- in_registry flag

Preserves Wikidata structure (PIDs remain as edge types).
Adds our semantic interpretation layer as properties.

Usage:
    python canonicalize_edges.py
    python canonicalize_edges.py --dry-run   # Report only, no writes
"""

import argparse
import csv
import sys
from pathlib import Path
from datetime import datetime

from neo4j import GraphDatabase

# Project root
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

# Neo4j config: prefer config_loader / .env
try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    import os
    NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j+s://f7b612a3.databases.neo4j.io")
    NEO4J_USERNAME = os.environ.get("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

parser = argparse.ArgumentParser(description="Stamp canonical properties on PID edges")
parser.add_argument("--dry-run", action="store_true", help="Report only, no writes")
parser.add_argument("--registry", default=str(ROOT / "Relationships/relationship_types_registry_master.csv"),
                    help="Path to relationship registry CSV")
args = parser.parse_args()

print("="*80)
print("EDGE CANONICALIZATION - Add Semantic Properties")
print("="*80)
print(f"Start: {datetime.now()}")
if args.dry_run:
    print("  [DRY RUN] No writes will be performed")
print()

# Neo4j connection
if not NEO4J_PASSWORD:
    print("Error: NEO4J_PASSWORD not set. Use .env or config_loader.")
    sys.exit(1)
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# Load relationship registry
print("Loading relationship registry...")
registry = {}
registry_path = Path(args.registry)
if not registry_path.exists():
    print(f"  Error: Registry not found: {registry_path}")
    sys.exit(1)
with open(registry_path, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        pid = row.get('wikidata_property', '').strip()
        if not pid:
            continue
        
        registry[pid] = {
            'canonical_type': row.get('relationship_type', '').strip(),
            'category': row.get('category', '').strip(),
            'cidoc_crm': row.get('cidoc_crm_code', '').strip(),
            'lifecycle': row.get('lifecycle_status', '').strip()
        }

print(f"  Registry loaded: {len(registry)} PID mappings")
print()

# Get all PID edge types in database
print("Querying edge types in database...")
with driver.session() as session:
    result = session.run("""
        CALL db.relationshipTypes() YIELD relationshipType
        WHERE relationshipType STARTS WITH 'P'
        RETURN relationshipType as pid
        ORDER BY pid
    """)
    
    db_pids = [r['pid'] for r in result]

print(f"  PID edge types in database: {len(db_pids)}")
print()

# Canonicalize each PID
print("Stamping canonical properties on edges...")
print()

stamped = 0
skipped = 0

for i, pid in enumerate(db_pids):
    if pid in registry:
        mapping = registry[pid]
        if not args.dry_run:
            with driver.session() as session:
                result = session.run(f"""
                    MATCH ()-[r:{pid}]->()
                    SET r.canonical_type = $canonical_type,
                        r.canonical_category = $category,
                        r.cidoc_crm_property = $cidoc_crm,
                        r.in_registry = true,
                        r.canonicalized_at = datetime()
                    RETURN count(r) as updated
                """,
                canonical_type=mapping['canonical_type'],
                category=mapping['category'],
                cidoc_crm=mapping['cidoc_crm'])
                count = result.single()['updated']
        else:
            with driver.session() as session:
                count = session.run(f"MATCH ()-[r:{pid}]->() RETURN count(r) as c", {}).single()['c']
        stamped += count
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(db_pids)} PIDs processed, {stamped:,} edges {'would be ' if args.dry_run else ''}stamped")
    else:
        if not args.dry_run:
            with driver.session() as session:
                result = session.run(f"""
                    MATCH ()-[r:{pid}]->()
                    SET r.in_registry = false,
                        r.needs_mapping = true
                    RETURN count(r) as updated
                """)
                count = result.single()['updated']
        else:
            with driver.session() as session:
                count = session.run(f"MATCH ()-[r:{pid}]->() RETURN count(r) as c", {}).single()['c']
        skipped += count

driver.close()

print()
print("="*80)
print("CANONICALIZATION COMPLETE")
print("="*80)
print(f"End: {datetime.now()}")
print()
print(f"Edges stamped with canonical properties: {stamped:,}")
print(f"Edges marked unmapped: {skipped:,}")
print(f"Total edges processed: {stamped + skipped:,}")
print()
print("Canonical properties added:")
print("  - canonical_type (INSTANCE_OF, PART_OF, etc.)")
print("  - canonical_category (Hierarchical, Temporal, etc.)")
print("  - cidoc_crm_property")
print("  - in_registry (true/false)")
print()
print("Query example:")
print("  MATCH ()-[r]->() WHERE r.canonical_type = 'INSTANCE_OF' RETURN count(r)")
print()
