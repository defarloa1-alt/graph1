#!/usr/bin/env python3
"""
Create Canonical Global Era Spine
8 top-level eras covering 2000 BCE to present
Links existing periods via PART_OF relationships
"""
import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Canonical global eras
CANONICAL_ERAS = [
    {
        'id': 'ERA_ANCIENT',
        'qid': 'Q41493',  # Wikidata: ancient history
        'label': 'Ancient History',
        'start': -2000,
        'end': 500,
        'description': 'Ancient civilizations from 2000 BCE to fall of Rome'
    },
    {
        'id': 'ERA_CLASSICAL',
        'qid': 'Q486761',  # Wikidata: classical antiquity
        'label': 'Classical Antiquity',
        'start': -500,
        'end': 500,
        'description': 'Classical Greece and Rome'
    },
    {
        'id': 'ERA_POSTCLASSICAL',
        'qid': 'Q12554',  # Wikidata: Middle Ages
        'label': 'Post-Classical / Medieval',
        'start': 500,
        'end': 1500,
        'description': 'Medieval period globally'
    },
    {
        'id': 'ERA_EARLYMODERN',
        'qid': 'Q5308718',  # Wikidata: early modern period
        'label': 'Early Modern',
        'start': 1450,
        'end': 1800,
        'description': 'Renaissance to Industrial Revolution'
    },
    {
        'id': 'ERA_LONG19TH',
        'qid': 'Q1368990',  # Wikidata: long nineteenth century
        'label': 'Long 19th Century',
        'start': 1789,
        'end': 1914,
        'description': 'French Revolution to World War I'
    },
    {
        'id': 'ERA_SHORT20TH',
        'qid': 'Q3769095',  # Wikidata: short twentieth century
        'label': 'Short 20th Century',
        'start': 1914,
        'end': 1991,
        'description': 'World Wars and Cold War'
    },
    {
        'id': 'ERA_CONTEMPORARY',
        'qid': 'Q6958377',  # Contemporary history
        'label': 'Contemporary',
        'start': 1991,
        'end': 2026,
        'description': 'Post-Cold War to present'
    }
]

def create_canonical_spine(uri="bolt://localhost:7687", user="neo4j", password="Chrystallum"):
    """Create canonical era spine and link existing periods."""
    
    print("="*80)
    print("Creating Canonical Global Era Spine")
    print("="*80)
    print(f"Neo4j: {uri}")
    print()
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Create era nodes
        print("[STEP 1] Creating canonical era nodes...")
        for era in CANONICAL_ERAS:
            print(f"  Creating: {era['label']} ({era['start']} to {era['end']})")
            
            session.run("""
                MERGE (era:Period:Era {qid: $qid})
                SET era.label = $label,
                    era.start_year = $start,
                    era.end_year = $end,
                    era.description = $description,
                    era.canonical_era = $id,
                    era.importance_rank = 1
            """, **era)
        
        print(f"✅ Created {len(CANONICAL_ERAS)} canonical eras")
        print()
        
        # Link existing periods to eras
        print("[STEP 2] Linking existing periods to eras...")
        linked_count = 0
        
        result = session.run("""
            MATCH (p:Period)
            WHERE p.canonical_era IS NULL
            RETURN p.label, p.start_year, p.end_year, p.qid
        """)
        
        for record in result:
            label = record['p.label']
            start = record['p.start_year']
            end = record['p.end_year']
            qid = record['p.qid']
            
            # Find best matching era(s)
            for era in CANONICAL_ERAS:
                # Check if period overlaps with era
                if start is not None and end is not None:
                    # Period overlaps if it starts before era ends and ends after era starts
                    if start <= era['end'] and end >= era['start']:
                        session.run("""
                            MATCH (p:Period {qid: $period_qid})
                            MATCH (era:Era {qid: $era_qid})
                            MERGE (p)-[:PART_OF]->(era)
                        """, period_qid=qid, era_qid=era['qid'])
                        
                        linked_count += 1
                        print(f"  Linked: {label} → {era['label']}")
                        break  # Link to primary era only
        
        print(f"\n✅ Linked {linked_count} periods to eras")
        print()
        
        # Verification
        print("="*80)
        print("Verification")
        print("="*80)
        
        result = session.run("""
            MATCH (era:Era)
            OPTIONAL MATCH (p:Period)-[:PART_OF]->(era)
            WITH era, count(p) as period_count
            RETURN era.label as era_label, era.start_year as start_year, period_count
            ORDER BY start_year
        """)
        
        print("Periods per era:")
        for record in result:
            print(f"  {record['era_label']:30s}: {record['period_count']:>3} periods")
        
        print("\n✅ Canonical spine created!")
        print("="*80)
    
    driver.close()

if __name__ == "__main__":
    create_canonical_spine()

