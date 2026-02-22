from neo4j import GraphDatabase

driver = GraphDatabase.driver('neo4j+s://f7b612a3.databases.neo4j.io', auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM'))

with driver.session() as session:
    result = session.run('MATCH (n:Entity) RETURN count(n) as total')
    total = result.single()['total']
    print(f'Total Entity nodes: {total}')

driver.close()
