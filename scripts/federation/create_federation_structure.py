#!/usr/bin/env python3
"""
Create Federation Subcluster Structure
- Creates Chrystallum root node
- Creates Federation category node
- Links potential federations as children
"""
import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Define potential federations
POTENTIAL_FEDERATIONS = [
    {
        'id': 'FED_EARTH',
        'label': 'Earth Federation',
        'type': 'planetary',
        'description': 'Global planetary federation of Earth'
    },
    {
        'id': 'FED_UNITED_NATIONS',
        'label': 'United Nations',
        'type': 'international',
        'description': 'International organization for cooperation'
    },
    {
        'id': 'FED_EUROPEAN_UNION',
        'label': 'European Union',
        'type': 'regional',
        'description': 'Political and economic union of European states'
    },
    {
        'id': 'FED_AFRICAN_UNION',
        'label': 'African Union',
        'type': 'regional',
        'description': 'Continental union of African states'
    },
    {
        'id': 'FED_ASEAN',
        'label': 'ASEAN',
        'type': 'regional',
        'description': 'Association of Southeast Asian Nations'
    },
    # Add more as needed
]

def create_federation_structure(uri="bolt://localhost:7687", user="neo4j", password="Chrystallum"):
    """Create the federation hierarchy."""
    
    print("="*80)
    print("Creating Federation Subcluster Structure")
    print("="*80)
    print(f"Neo4j: {uri}")
    print()
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Step 1: Create Chrystallum root node
        print("[STEP 1] Creating Chrystallum root node...")
        session.run("""
            MERGE (c:Chrystallum:Root {
                id: 'CHRYSTALLUM_ROOT',
                label: 'Chrystallum',
                type: 'knowledge_graph_root',
                description: 'Root node of the Chrystallum knowledge graph',
                created: datetime()
            })
        """)
        print("  ✅ Created Chrystallum root node")
        print()
        
        # Step 2: Create Federation category node
        print("[STEP 2] Creating Federation category node...")
        session.run("""
            MERGE (f:Federation:Category {
                id: 'FEDERATION_CATEGORY',
                label: 'Federation',
                type: 'organizational_category',
                description: 'Category node for all federation entities'
            })
        """)
        print("  ✅ Created Federation category node")
        print()
        
        # Step 3: Link Chrystallum to Federation
        print("[STEP 3] Linking Chrystallum → Federation...")
        session.run("""
            MATCH (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
            MATCH (f:Federation:Category {id: 'FEDERATION_CATEGORY'})
            MERGE (c)-[:HAS_SUBCLUSTER {
                cluster_type: 'federation',
                description: 'Federation organizational subcluster'
            }]->(f)
        """)
        print("  ✅ Created HAS_SUBCLUSTER relationship")
        print()
        
        # Step 4: Create potential federation instances
        print("[STEP 4] Creating potential federation instances...")
        for fed in POTENTIAL_FEDERATIONS:
            print(f"  Creating: {fed['label']} ({fed['type']})")
            
            session.run("""
                MERGE (fed:Federation:Organization {
                    id: $id,
                    label: $label,
                    type: $type,
                    description: $description,
                    federation_status: 'potential'
                })
            """, **fed)
        
        print(f"  ✅ Created {len(POTENTIAL_FEDERATIONS)} federation instances")
        print()
        
        # Step 5: Link Federation category to instances
        print("[STEP 5] Creating IS_COMPOSED_OF relationships...")
        for fed in POTENTIAL_FEDERATIONS:
            session.run("""
                MATCH (category:Federation:Category {id: 'FEDERATION_CATEGORY'})
                MATCH (instance:Federation:Organization {id: $id})
                MERGE (category)-[:IS_COMPOSED_OF {
                    member_type: $type,
                    added: datetime()
                }]->(instance)
            """, id=fed['id'], type=fed['type'])
        
        print(f"  ✅ Created {len(POTENTIAL_FEDERATIONS)} IS_COMPOSED_OF relationships")
        print()
        
        # Verification
        print("="*80)
        print("Verification")
        print("="*80)
        
        result = session.run("""
            MATCH (c:Chrystallum)-[:HAS_SUBCLUSTER]->(cat:Category)-[:IS_COMPOSED_OF]->(fed:Organization)
            RETURN count(DISTINCT c) as chrystallum_nodes,
                   count(DISTINCT cat) as category_nodes,
                   count(DISTINCT fed) as federation_instances
        """)
        
        record = result.single()
        print(f"Chrystallum nodes: {record['chrystallum_nodes']}")
        print(f"Category nodes: {record['category_nodes']}")
        print(f"Federation instances: {record['federation_instances']}")
        
        print("\nFederation instances:")
        result = session.run("""
            MATCH (fed:Federation:Organization)
            RETURN fed.label, fed.type, fed.federation_status
            ORDER BY fed.type, fed.label
        """)
        for r in result:
            print(f"  - {r['fed.label']:30s} ({r['fed.type']:15s}) [{r['fed.federation_status']}]")
        
        print("\n✅ Federation structure created!")
        print("="*80)
    
    driver.close()

if __name__ == "__main__":
    create_federation_structure()

