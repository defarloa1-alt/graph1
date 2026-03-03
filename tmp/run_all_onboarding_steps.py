"""
Execute all 14 onboarding protocol steps sequentially
"""
from neo4j import GraphDatabase

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
            RETURN s.step_number as step, s.description as desc, s.cypher_query as query
            ORDER BY s.step_number
            """
            
            steps = list(session.run(steps_query))
            
            for record in steps:
                step_num = record["step"]
                desc = record["desc"]
                query = record["query"]
                
                print(f"\n{'='*80}")
                print(f"STEP {step_num}: {desc}")
                print(f"{'='*80}\n")
                
                if query:
                    try:
                        result = session.run(query)
                        records = list(result)
                        
                        if records:
                            print(f"Found {len(records)} records:")
                            # Show first 5 for brevity
                            for i, r in enumerate(records[:5], 1):
                                row_dict = dict(r)
                                # Format the output nicely
                                if len(row_dict) == 1:
                                    print(f"  {list(row_dict.values())[0]}")
                                else:
                                    print(f"  {i}. {row_dict}")
                            if len(records) > 5:
                                print(f"  ... and {len(records) - 5} more")
                        else:
                            print("No results returned")
                    except Exception as e:
                        print(f"Error executing query: {e}")
                else:
                    print("No query defined for this step")
    
    finally:
        driver.close()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("EXECUTING CHRYSTALLUM ONBOARDING PROTOCOL")
    print("="*80)
    execute_all_steps()
    print("\n" + "="*80)
    print("ONBOARDING COMPLETE")
    print("="*80 + "\n")
