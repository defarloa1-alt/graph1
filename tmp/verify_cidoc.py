from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'Chrystallum'))

query = """
MATCH (n) 
WHERE n:CIDOC_Class OR n:CIDOC_Property OR n:CRMinf_Class OR n:CRMinf_Property 
RETURN labels(n)[0] AS label, COUNT(*) AS count 
ORDER BY label
"""

with driver.session() as session:
    result = session.run(query)
    print("\nCIDOC/CRMinf Reference Node Verification:")
    print("=" * 50)
    total = 0
    for record in result:
        count = record['count']
        total += count
        print(f"{record['label']}: {count}")
    print("=" * 50)
    print(f"TOTAL: {total}")
    print()

driver.close()
