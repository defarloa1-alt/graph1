"""
Show Military Theory Status

Query what theories exist in MILITARY_THEORY and how they're being used.
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def show_status():
    """Show current state of MILITARY_THEORY."""
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    print("\n" + "="*70)
    print("  MILITARY_THEORY STATUS")
    print("="*70)
    
    try:
        with driver.session() as session:
            # Count principles by category
            print("\n[1] Principles by Category:\n")
            result = session.run("""
                MATCH (mp:MilitaryPrinciple)
                RETURN mp.category as category, count(*) as count
                ORDER BY count DESC
            """)
            
            total = 0
            for record in result:
                count = record['count']
                total += count
                print(f"    {record['category']:<25} {count} principle(s)")
            
            print(f"\n    {'TOTAL':<25} {total} principles")
            
            # List all principles with details
            print("\n\n[2] All Principles:\n")
            result = session.run("""
                MATCH (mp:MilitaryPrinciple)
                RETURN 
                    mp.label as label,
                    mp.category as category,
                    mp.theorist as theorist,
                    mp.applicability as applicability,
                    mp.discovered_from as source
                ORDER BY mp.discovered_at ASC
            """)
            
            for idx, record in enumerate(result, 1):
                print(f"    {idx}. {record['label']}")
                print(f"       Theorist: {record['theorist']}")
                print(f"       Category: {record['category']}")
                print(f"       Applicability: {record['applicability']}")
                print(f"       Source: {record['source']}")
                print()
            
            # Show cross-domain links
            print("[3] Applications to Roman History:\n")
            result = session.run("""
                MATCH (a:Agent)-[claim:ASSERTS]->(event:EVENT)
                WHERE claim.predicate = 'exemplifies_principle'
                  AND claim.principle_applied IS NOT NULL
                MATCH (mp:MilitaryPrinciple {principle_id: claim.principle_applied})
                RETURN 
                    event.label as battle,
                    mp.label as theory,
                    claim.confidence as confidence,
                    substring(claim.framework_analysis, 0, 100) as analysis
            """)
            
            links = list(result)
            if links:
                for idx, record in enumerate(links, 1):
                    print(f"    {idx}. {record['battle']}")
                    print(f"       Exemplifies: {record['theory']}")
                    print(f"       Confidence: {record['confidence']}")
                    print(f"       Analysis: {record['analysis']}...")
                    print()
            else:
                print("    (No cross-domain links yet)")
            
            print("="*70)
            print("  Military SFA has theory knowledge and can apply it to history!")
            print("="*70 + "\n")
            
    finally:
        driver.close()


if __name__ == "__main__":
    show_status()
