"""
Migrate the DEPENDS_ON relationship from SubjectConcept to Domain nodes
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'),
    auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
)

with driver.session() as session:
    print("\nMigrating dependencies from SubjectConcept to Domain...")
    print("="*70)
    
    # Check for SubjectConcept dependencies
    result = session.run("""
        MATCH (sc1:SubjectConcept)-[dep:DEPENDS_ON]->(sc2:SubjectConcept)
        RETURN sc1.subject_id as dependent,
               sc2.subject_id as dependency,
               dep.version_spec as spec,
               dep.pinned as pinned
    """)
    
    deps = list(result)
    if not deps:
        print("  No SubjectConcept dependencies found")
    else:
        print(f"  Found {len(deps)} SubjectConcept dependencies")
        
        for dep in deps:
            print(f"\n  Migrating: {dep['dependent']} -> {dep['dependency']}")
            
            # Create Domain dependency
            session.run("""
                MATCH (d1:Domain {domain_id: $dependent})
                MATCH (d2:Domain {domain_id: $dependency})
                MERGE (d1)-[new_dep:DEPENDS_ON]->(d2)
                SET new_dep.version_spec = $spec,
                    new_dep.pinned = $pinned,
                    new_dep.migrated_from = 'SubjectConcept'
            """,
            dependent=dep['dependent'],
            dependency=dep['dependency'],
            spec=dep['spec'],
            pinned=dep['pinned']
            )
            
            print(f"    [OK] Created Domain dependency")
            
            # Remove SubjectConcept dependency
            session.run("""
                MATCH (sc1:SubjectConcept {subject_id: $dependent})
                      -[dep:DEPENDS_ON]->
                      (sc2:SubjectConcept {subject_id: $dependency})
                DELETE dep
            """,
            dependent=dep['dependent'],
            dependency=dep['dependency']
            )
            
            print(f"    [OK] Removed SubjectConcept dependency")
    
    # Verify
    print("\n\nVerifying Domain dependencies:")
    print("="*70)
    result = session.run("""
        MATCH (d1:Domain)-[dep:DEPENDS_ON]->(d2:Domain)
        RETURN d1.domain_id as dependent,
               d2.domain_id as dependency,
               dep.version_spec as spec
    """)
    
    for r in result:
        print(f"  {r['dependent']} depends on {r['dependency']} @ {r['spec']}")
    
    print()

driver.close()
