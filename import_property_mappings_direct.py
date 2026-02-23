#!/usr/bin/env python3
"""
Direct Python import of property mappings to Neo4j

Uses parameterized queries (no escaping issues)
"""

import csv
from pathlib import Path
from neo4j import GraphDatabase

# Neo4j connection
URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

INPUT_CSV = Path("CSV/property_mappings/property_facet_mapping_HYBRID.csv")

print("="*80)
print("IMPORTING PROPERTY MAPPINGS TO NEO4J")
print("="*80)
print()

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

try:
    with driver.session() as session:
        # Step 1: Create indexes
        print("Step 1: Creating indexes...")
        
        indexes = [
            "CREATE INDEX property_mapping_pid_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.property_id)",
            "CREATE INDEX property_mapping_facet_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.primary_facet)",
            "CREATE INDEX property_mapping_confidence_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.confidence)",
        ]
        
        for idx_query in indexes:
            session.run(idx_query)
        
        print("  Created 3 indexes")
        print()
        
        # Step 2: Load CSV
        print("Step 2: Loading property mappings...")
        
        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            properties = list(reader)
        
        print(f"  Read {len(properties)} properties")
        print()
        
        # Step 3: Create PropertyMapping nodes
        print("Step 3: Creating PropertyMapping nodes...")
        
        create_query = """
        CREATE (pm:PropertyMapping {
          property_id: $property_id,
          property_label: $property_label,
          property_description: $property_description,
          primary_facet: $primary_facet,
          secondary_facets: $secondary_facets,
          all_facets: $all_facets,
          confidence: $confidence,
          resolved_by: $resolved_by,
          is_historical: $is_historical,
          is_authority_control: $is_authority_control,
          type_count: $type_count,
          imported_at: datetime()
        })
        """
        
        created = 0
        failed = 0
        
        for i, prop in enumerate(properties, 1):
            try:
                params = {
                    'property_id': prop['property_id'],
                    'property_label': prop['property_label'],
                    'property_description': prop['property_description'],
                    'primary_facet': prop['primary_facet'],
                    'secondary_facets': prop['secondary_facets'],
                    'all_facets': prop['all_facets'],
                    'confidence': float(prop['confidence']),
                    'resolved_by': prop.get('resolved_by', 'base_mapping'),
                    'is_historical': prop['is_historical'] == 'True',
                    'is_authority_control': prop['is_authority_control'] == 'True',
                    'type_count': int(prop['type_count']),
                }
                
                session.run(create_query, params)
                created += 1
                
                if i % 100 == 0:
                    print(f"  Created {i}/{len(properties)}...")
                
            except Exception as e:
                failed += 1
                print(f"  Failed: {prop['property_id']} - {e}")
        
        print(f"\n  Created: {created}")
        print(f"  Failed: {failed}")
        print()
        
        # Step 4: Link to Facet nodes
        print("Step 4: Linking to Facet nodes...")
        
        # Primary facets
        link_primary = """
        MATCH (pm:PropertyMapping)
        WHERE pm.primary_facet IS NOT NULL AND pm.primary_facet <> 'UNKNOWN'
        WITH pm
        MATCH (f:Facet {key: pm.primary_facet})
        MERGE (pm)-[:HAS_PRIMARY_FACET]->(f)
        """
        
        result = session.run(link_primary)
        summary = result.consume()
        print(f"  Primary facet links: {summary.counters.relationships_created}")
        
        # Secondary facets
        link_secondary = """
        MATCH (pm:PropertyMapping)
        WHERE pm.secondary_facets IS NOT NULL AND pm.secondary_facets <> ''
        UNWIND split(pm.secondary_facets, ',') AS facet_key
        MATCH (f:Facet {key: facet_key})
        MERGE (pm)-[:HAS_SECONDARY_FACET]->(f)
        """
        
        result = session.run(link_secondary)
        summary = result.consume()
        print(f"  Secondary facet links: {summary.counters.relationships_created}")
        print()
        
        # Verification
        print("Step 5: Verification...")
        
        result = session.run("MATCH (pm:PropertyMapping) RETURN count(pm) as total")
        total = result.single()['total']
        print(f"  Total PropertyMapping nodes: {total}")
        
        result = session.run("""
            MATCH (pm:PropertyMapping)
            RETURN pm.primary_facet as facet, count(pm) as count
            ORDER BY count DESC
            LIMIT 5
        """)
        
        print("\n  Top 5 facets:")
        for record in result:
            print(f"    {record['facet']:20} {record['count']:>4}")
        
        print()
        print("="*80)
        print("IMPORT COMPLETE!")
        print("="*80)
        print()
        print(f"Successfully imported {created} PropertyMapping nodes")
        print("Run verification queries from IMPORT_PROPERTY_MAPPINGS_GUIDE.md")

finally:
    driver.close()
