"""
Restructure SubjectConcept Hierarchy

Problem: All 105 SubjectConcept nodes are flat with no hierarchy.
Solution: Create top-level Domain nodes and organize SubjectConcepts under them.

Domain hierarchy:
  Domain:ROMAN_REPUBLIC (versioned)
    ├── :CONTAINS sc_military
    ├── :CONTAINS sc_diplomacy
    ├── :CONTAINS sc_*
    └── :CONTAINS sc_q17167_* (all republic-specific)
  
  Domain:MILITARY_THEORY (versioned)
    ├── :CONTAINS MilitaryPrinciple nodes
    └── :CONTAINS theory SPO nodes
  
  Domain:GEOGRAPHY (new, versioned)
    ├── :CONTAINS GEO_ADMIN_DIVISIONS
    ├── :CONTAINS GEO_HYDROGRAPHY
    ├── :CONTAINS GEO_PHYS_FEATURES
    └── :CONTAINS GEO_POLITICAL_ENTITIES
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def restructure_domains(driver):
    """Restructure flat SubjectConcepts into domain hierarchy."""
    
    with driver.session() as session:
        print("DOMAIN HIERARCHY RESTRUCTURE")
        print("="*70)
        
        # 1. Ensure ROMAN_REPUBLIC domain exists with proper metadata
        print("\n[1] Setting up ROMAN_REPUBLIC domain...")
        session.run("""
            MERGE (d:Domain {domain_id: 'roman_republic'})
            SET d.label = 'Roman Republic',
                d.scope = 'historical',
                d.period = '509-27 BCE',
                d.description = 'Complete knowledge graph of the Roman Republic',
                d.version = COALESCE(d.version, '0.1.0'),
                d.versioned = true,
                d.updated_at = datetime()
        """)
        print("    [OK] ROMAN_REPUBLIC domain ready")
        
        # 2. Link all sc_* and sc_q17167_* to ROMAN_REPUBLIC
        print("\n[2] Organizing SubjectConcepts under ROMAN_REPUBLIC...")
        result = session.run("""
            MATCH (domain:Domain {domain_id: 'roman_republic'})
            MATCH (sc:SubjectConcept)
            WHERE sc.subject_id STARTS WITH 'sc_'
              AND sc.subject_id <> 'roman_republic'
              AND NOT EXISTS((domain)-[:CONTAINS]->(sc))
            WITH domain, sc
            CREATE (domain)-[:CONTAINS]->(sc)
            RETURN count(sc) as count
        """)
        count = result.single()['count']
        print(f"    [OK] Linked {count} SubjectConcepts to ROMAN_REPUBLIC")
        
        # 3. Ensure MILITARY_THEORY domain exists
        print("\n[3] Setting up MILITARY_THEORY domain...")
        session.run("""
            MERGE (d:Domain {domain_id: 'military_theory'})
            SET d.label = 'Military Theory',
                d.scope = 'theoretical',
                d.period = 'timeless',
                d.description = 'Universal principles of military strategy and tactics',
                d.version = COALESCE(d.version, '1.1.0'),
                d.versioned = true,
                d.discovery_based = true,
                d.updated_at = datetime()
        """)
        print("    [OK] MILITARY_THEORY domain ready")
        
        # 4. Link all theory nodes to MILITARY_THEORY
        print("\n[4] Organizing theory nodes under MILITARY_THEORY...")
        result = session.run("""
            MATCH (domain:Domain {domain_id: 'military_theory'})
            MATCH (n)
            WHERE n:MilitaryPrinciple 
               OR n:Concept 
               OR n:Mechanism 
               OR n:Effect 
               OR n:Condition 
               OR n:Process 
               OR n:Target
            WITH domain, n
            WHERE NOT EXISTS((domain)-[:CONTAINS]->(n))
            CREATE (domain)-[:CONTAINS]->(n)
            RETURN count(n) as count
        """)
        count = result.single()['count']
        print(f"    [OK] Linked {count} theory nodes to MILITARY_THEORY")
        
        # 5. Geography domain — out of scope (geo SubjectConcepts remain; no Domain wrapper)
        print("\n[5] Skipping GEOGRAPHY domain (out of scope; geo SCs remain in graph)")
        
        # 6. Link domains to SubjectConceptRegistry
        print("\n[6] Linking domains to SubjectConceptRegistry...")
        result = session.run("""
            MATCH (scr:SubjectConceptRegistry)
            MATCH (d:Domain)
            WHERE NOT EXISTS((scr)-[:TRACKS_DOMAIN]->(d))
            WITH scr, d
            CREATE (scr)-[:TRACKS_DOMAIN]->(d)
            RETURN count(d) as count
        """)
        count = result.single()['count']
        print(f"    [OK] Linked {count} domains to registry")
        
        # 7. Summary
        print("\n[7] Current domain structure:")
        print("="*70)
        result = session.run("""
            MATCH (d:Domain)
            OPTIONAL MATCH (d)-[:CONTAINS]->(child)
            RETURN d.domain_id as domain,
                   d.label as label,
                   d.version as version,
                   d.scope as scope,
                   count(child) as children
            ORDER BY domain
        """)
        
        for record in result:
            print(f"\n  Domain: {record['domain']}")
            print(f"    Label: {record['label']}")
            print(f"    Version: {record['version']}")
            print(f"    Scope: {record['scope']}")
            print(f"    Children: {record['children']}")
        
        print("\n" + "="*70)
        print("RESTRUCTURE COMPLETE")
        print("="*70)


if __name__ == "__main__":
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    try:
        restructure_domains(driver)
    finally:
        driver.close()
