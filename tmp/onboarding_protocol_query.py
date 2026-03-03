"""
Execute the onboarding protocol query against Neo4j
"""
from neo4j import GraphDatabase
import json

# Neo4j connection details
NEO4J_URI = "neo4j+s://ac63a8e5.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "eY1ljfhesY9AdRwbTlo1_mSAyKKvdcr5cEIwhj_FzbQ"
NEO4J_DATABASE = "neo4j"

def run_onboarding_query():
    """Execute the onboarding protocol query"""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    query = """
    MATCH (p:SYS_OnboardingProtocol) 
    OPTIONAL MATCH (p)-[:HAS_STEP]->(s:SYS_OnboardingStep) 
    RETURN p.description, s.step_number, s.description 
    ORDER BY s.step_number
    """
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query)
            records = list(result)
            
            print(f"\n{'='*80}")
            print("ONBOARDING PROTOCOL RESULTS")
            print(f"{'='*80}\n")
            
            if not records:
                print("No onboarding protocol found in graph.")
                return
            
            protocol_desc = records[0]["p.description"] if records else None
            print(f"Protocol: {protocol_desc}\n")
            print(f"{'='*80}\n")
            
            for record in records:
                step_num = record["s.step_number"]
                step_desc = record["s.description"]
                
                if step_num is not None:
                    print(f"Step {step_num}: {step_desc}\n")
            
            print(f"{'='*80}")
            print(f"Total steps: {len([r for r in records if r['s.step_number'] is not None])}")
            print(f"{'='*80}\n")
            
    except Exception as e:
        print(f"Error executing query: {e}")
        print("\nMake sure Neo4j is running on bolt://localhost:7687")
    finally:
        driver.close()

if __name__ == "__main__":
    run_onboarding_query()
