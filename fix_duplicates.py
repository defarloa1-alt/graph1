from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

with driver.session() as session:
    # Find duplicates
    print("Finding duplicates...")
    result = session.run("""
        MATCH (n:Entity)
        WITH n.qid as qid, collect(n) as nodes
        WHERE size(nodes) > 1
        RETURN qid, size(nodes) as count
        ORDER BY qid
    """)
    
    dupes = list(result)
    print(f"  Found {len(dupes)} QIDs with duplicates\n")
    
    # Show samples
    print("Sample duplicates:")
    for r in dupes[:5]:
        print(f"  {r['qid']}: {r['count']} copies")
    print()
    
    # Delete duplicates (keep first by internal ID)
    print("Deleting duplicates (keeping first instance)...\n")
    
    deleted_total = 0
    for dupe in dupes:
        qid = dupe['qid']
        
        # For this QID, keep the first node, delete the rest
        result = session.run("""
            MATCH (n:Entity {qid: $qid})
            WITH n
            ORDER BY id(n)
            WITH collect(n) as nodes
            WITH nodes[1..] as to_delete
            UNWIND to_delete as node
            DETACH DELETE node
            RETURN count(node) as deleted
        """, qid=qid)
        
        deleted = result.single()['deleted']
        deleted_total += deleted
        print(f"  {qid}: deleted {deleted} duplicate(s)")
    
    print(f"\nTotal deleted: {deleted_total}\n")
    
    # Verify
    result = session.run("""
        MATCH (n:Entity)
        RETURN count(n) as total, count(DISTINCT n.qid) as unique_qids
    """)
    
    rec = result.single()
    print(f"VERIFICATION:")
    print(f"  Total entities: {rec['total']}")
    print(f"  Unique QIDs: {rec['unique_qids']}")
    print(f"  Match: {rec['total'] == rec['unique_qids']}\n")

driver.close()
