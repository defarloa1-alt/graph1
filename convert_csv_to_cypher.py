#!/usr/bin/env python3
"""
Convert property mapping CSV to embedded Cypher CREATE statements

For Neo4j Aura which doesn't allow CSV file imports
"""

import csv
from pathlib import Path

INPUT_CSV = Path("CSV/property_mappings/property_facet_mapping_HYBRID.csv")
OUTPUT_CYPHER = Path("output/neo4j/import_property_mappings_embedded.cypher")

print("Converting CSV to embedded Cypher statements...")

# Read CSV
with open(INPUT_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    properties = list(reader)

print(f"Read {len(properties)} properties")

# Generate Cypher
lines = []

# Header
lines.append("// ============================================================================")
lines.append("// PROPERTY FACET MAPPING - NEO4J IMPORT (Embedded Data)")
lines.append("// ============================================================================")
lines.append("// Generated from: property_facet_mapping_HYBRID.csv")
lines.append(f"// Total properties: {len(properties)}")
lines.append("// Coverage: 100%")
lines.append("// For Neo4j Aura (no CSV file import)")
lines.append("// ============================================================================")
lines.append("")

# Indexes
lines.append("// STEP 1: CREATE INDEXES")
lines.append("CREATE INDEX property_mapping_pid_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.property_id);")
lines.append("CREATE INDEX property_mapping_facet_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.primary_facet);")
lines.append("CREATE INDEX property_mapping_confidence_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.confidence);")
lines.append("")

# Create statements
lines.append("// STEP 2: CREATE PROPERTY MAPPING NODES")
lines.append("")

for i, prop in enumerate(properties, 1):
    # Escape single quotes and backslashes
    label = prop['property_label'].replace("\\", "\\\\").replace("'", "\\'")
    desc = prop['property_description'].replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
    
    cypher = f"""// {i}. {prop['property_id']} - {label[:50]}
CREATE (:PropertyMapping {{
  property_id: '{prop['property_id']}',
  property_label: '{label}',
  property_description: '{desc}',
  primary_facet: '{prop['primary_facet']}',
  secondary_facets: '{prop['secondary_facets']}',
  all_facets: '{prop['all_facets']}',
  confidence: {prop['confidence']},
  resolved_by: '{prop.get('resolved_by', 'base_mapping')}',
  is_historical: {str(prop['is_historical']).lower()},
  is_authority_control: {str(prop['is_authority_control']).lower()},
  type_count: {prop['type_count']},
  imported_at: datetime()
}});
"""
    lines.append(cypher)

# Facet linking
lines.append("\n// STEP 3: LINK TO FACET NODES")
lines.append("""
MATCH (pm:PropertyMapping)
WHERE pm.primary_facet IS NOT NULL AND pm.primary_facet <> 'UNKNOWN'
MATCH (f:Facet {key: pm.primary_facet})
MERGE (pm)-[:HAS_PRIMARY_FACET]->(f);
""")

lines.append("""
MATCH (pm:PropertyMapping)
WHERE pm.secondary_facets IS NOT NULL AND pm.secondary_facets <> ''
UNWIND split(pm.secondary_facets, ',') AS facet_key
MATCH (f:Facet {key: facet_key})
MERGE (pm)-[:HAS_SECONDARY_FACET]->(f);
""")

# Write
with open(OUTPUT_CYPHER, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"\nGenerated: {OUTPUT_CYPHER}")
print(f"Lines: {len(lines):,}")
print(f"Size: {OUTPUT_CYPHER.stat().st_size / 1024:.1f} KB")
print()
print("This file contains embedded CREATE statements (no CSV required)")
print("Ready for Neo4j Aura import!")
