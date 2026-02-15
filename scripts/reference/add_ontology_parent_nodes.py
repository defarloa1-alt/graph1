#!/usr/bin/env python3
"""
Add Ontology parent nodes for CIDOC-CRM and CRMinf reference vocabularies.

Creates:
- (:Ontology {name: "CIDOC-CRM", ...})
- (:Ontology {name: "CRMinf", ...})
- Relationships: (Ontology)-[:HAS_CLASS|HAS_PROPERTY]->(Class/Property nodes)

This enables ontology-level queries and visualization.
"""
import argparse
from datetime import datetime
from neo4j import GraphDatabase


def main():
    parser = argparse.ArgumentParser(description="Add Ontology parent nodes")
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--user", default="neo4j", help="Neo4j username")
    parser.add_argument("--password", default="Chrystallum", help="Neo4j password")
    
    args = parser.parse_args()
    
    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    
    print("=" * 80)
    print("ADD ONTOLOGY PARENT NODES")
    print("=" * 80)
    
    try:
        with driver.session() as session:
            # Step 1: Create CIDOC-CRM Ontology parent node
            print("\n[1/4] Creating CIDOC-CRM Ontology node...")
            cidoc_result = session.run("""
                MERGE (o:Ontology {name: "CIDOC-CRM"})
                SET o.version = "7.1.2",
                    o.full_name = "CIDOC Conceptual Reference Model",
                    o.source_url = "http://www.cidoc-crm.org/",
                    o.spec_date = "2021-04",
                    o.loaded_date = $loaded_date,
                    o.description = "ISO 21127:2014 - Cultural Heritage Information Standard",
                    o.license = "Creative Commons Attribution 4.0",
                    o.maintained_by = "CIDOC CRM Special Interest Group"
                RETURN o.name AS name, o.version AS version
            """, loaded_date=datetime.now().isoformat())
            cidoc = cidoc_result.single()
            print(f"   ✓ Created: {cidoc['name']} v{cidoc['version']}")
            
            # Step 2: Create CRMinf Ontology parent node
            print("\n[2/4] Creating CRMinf Ontology node...")
            crminf_result = session.run("""
                MERGE (o:Ontology {name: "CRMinf"})
                SET o.version = "0.7",
                    o.full_name = "CIDOC-CRM Inference Extension",
                    o.source_url = "http://www.ics.forth.gr/isl/CRMinf/",
                    o.spec_date = "2015",
                    o.loaded_date = $loaded_date,
                    o.description = "Extension for argumentation and inference modeling",
                    o.extends = "CIDOC-CRM",
                    o.maintained_by = "FORTH-ICS"
                RETURN o.name AS name, o.version AS version
            """, loaded_date=datetime.now().isoformat())
            crminf = crminf_result.single()
            print(f"   ✓ Created: {crminf['name']} v{crminf['version']}")
            
            # Step 3: Link CIDOC-CRM Ontology to its classes and properties
            print("\n[3/4] Linking CIDOC-CRM to classes and properties...")
            cidoc_links_result = session.run("""
                MATCH (o:Ontology {name: "CIDOC-CRM"})
                MATCH (c:CIDOC_Class)
                MERGE (o)-[:HAS_CLASS]->(c)
                WITH o, count(*) AS class_count
                MATCH (o)-[:HAS_CLASS]->(c)
                WITH o, class_count
                MATCH (p:CIDOC_Property)
                MERGE (o)-[:HAS_PROPERTY]->(p)
                RETURN class_count, count(p) AS prop_count
            """)
            cidoc_links = cidoc_links_result.single()
            print(f"   ✓ Linked {cidoc_links['class_count']} classes")
            print(f"   ✓ Linked {cidoc_links['prop_count']} properties")
            
            # Step 4: Link CRMinf Ontology to its classes and properties
            print("\n[4/4] Linking CRMinf to classes and properties...")
            crminf_links_result = session.run("""
                MATCH (o:Ontology {name: "CRMinf"})
                MATCH (c:CRMinf_Class)
                MERGE (o)-[:HAS_CLASS]->(c)
                WITH o, count(*) AS class_count
                MATCH (o)-[:HAS_CLASS]->(c)
                WITH o, class_count
                MATCH (p:CRMinf_Property)
                MERGE (o)-[:HAS_PROPERTY]->(p)
                RETURN class_count, count(p) AS prop_count
            """)
            crminf_links = crminf_links_result.single()
            print(f"   ✓ Linked {crminf_links['class_count']} classes")
            print(f"   ✓ Linked {crminf_links['prop_count']} properties")
            
            # Verification query
            print("\n" + "=" * 80)
            print("VERIFICATION")
            print("=" * 80)
            verify_result = session.run("""
                MATCH (o:Ontology)
                OPTIONAL MATCH (o)-[:HAS_CLASS]->(c)
                OPTIONAL MATCH (o)-[:HAS_PROPERTY]->(p)
                RETURN o.name AS ontology, 
                       o.version AS version,
                       count(DISTINCT c) AS classes,
                       count(DISTINCT p) AS properties
                ORDER BY o.name
            """)
            
            for record in verify_result:
                print(f"\n{record['ontology']} v{record['version']}:")
                print(f"  Classes: {record['classes']}")
                print(f"  Properties: {record['properties']}")
            
            print("\n" + "=" * 80)
            print("[OK] Ontology parent nodes created successfully!")
            print("=" * 80)
            
    finally:
        driver.close()


if __name__ == "__main__":
    main()
