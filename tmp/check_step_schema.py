"""
Check what properties exist on SYS_OnboardingStep nodes
"""
from neo4j import GraphDatabase

NEO4J_URI = "neo4j+s://ac63a8e5.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "eY1ljfhesY9AdRwbTlo1_mSAyKKvdcr5cEIwhj_FzbQ"
NEO4J_DATABASE = "neo4j"

def check_step_properties():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            # Get one step to see its properties
            query = """
            MATCH (s:SYS_OnboardingStep)
            WHERE s.step_number = 1
            RETURN s
            """
            
            result = session.run(query)
            record = result.single()
            
            if record:
                step_node = record["s"]
                print("Properties on SYS_OnboardingStep node:")
                for key, value in step_node.items():
                    print(f"  {key}: {value}")
    
    finally:
        driver.close()

if __name__ == "__main__":
    check_step_properties()
