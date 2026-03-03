"""
Execute all 14 onboarding protocol steps using the 'query' property
"""
from neo4j import GraphDatabase
import json

NEO4J_URI = "neo4j+s://ac63a8e5.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "eY1ljfhesY9AdRwbTlo1_mSAyKKvdcr5cEIwhj_FzbQ"
NEO4J_DATABASE = "neo4j"

def execute_all_steps():
    """Execute all onboarding steps in sequence"""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            # Get all onboarding steps with their queries
            steps_query = """
            MATCH (p:SYS_OnboardingProtocol)-[:HAS_STEP]->(s:SYS_OnboardingStep)
            RETURN s.step_number as step, 
                   s.description as desc, 
                   s.query as query,
                   s.query_hint as hint,
                   s.label as label,
                   s.learns as learns
            ORDER BY s.step_number
            """
            
            steps = list(session.run(steps_query))
            
            for record in steps:
                step_num = record["step"]
                desc = record["desc"]
                label = record["label"]
                learns = record["learns"]
                query = record["query"]
                hint = record["hint"]
                
                print(f"\n{'='*80}")
                print(f"STEP {step_num}: {label}")
                print(f"{'='*80}")
                print(f"Description: {desc}")
                print(f"Learns: {learns}")
                print(f"\n")
                
                # Use hint query if available (simpler/non-parameterized)
                actual_query = hint if hint else query
                
                if actual_query:
                    print(f"Query: {actual_query[:200]}...")
                    try:
                        result = session.run(actual_query)
                        records = list(result)
                        
                        if records:
                            print(f"\n✓ Found {len(records)} records:\n")
                            # Show first 5 for brevity
                            for i, r in enumerate(records[:5], 1):
                                row_dict = dict(r)
                                # Format nicely
                                if len(row_dict) == 1:
                                    val = list(row_dict.values())[0]
                                    print(f"  • {val}")
                                else:
                                    formatted = ", ".join([f"{k}={v}" for k, v in row_dict.items() if v is not None])
                                    print(f"  {i}. {formatted}")
                            if len(records)> 5:
                                print(f"\n  ... and {len(records) - 5} more")
                        else:
                            print("\n⚠ No results returned")
                    except Exception as e:
                        print(f"\n✗ Error: {e}")
                else:
                    print("⚠ No query defined for this step")
    
    finally:
        driver.close()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CHRYSTALLUM ONBOARDING PROTOCOL")
    print("Self-Describing Knowledge Graph Architecture")
    print("="*80)
    execute_all_steps()
    print("\n" + "="*80)
    print("✓ ONBOARDING PROTOCOL COMPLETE")
    print("="*80 + "\n")
