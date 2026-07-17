"""Check legacy Claim node structure."""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'),
    auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
)

with driver.session() as session:
    # Check Claim node structure
    result = session.run('MATCH (c:Claim) RETURN c LIMIT 3')
    
    print('Sample Claim nodes:')
    print()
    
    for i, record in enumerate(result, 1):
        claim_node = dict(record['c'])
        print(f'Claim node {i}:')
        for key, value in sorted(claim_node.items()):
            val_str = str(value)[:60] if value else 'None'
            print(f'  {key:25s} {val_str}')
        print()
    
    # Count Claim nodes
    result = session.run('MATCH (c:Claim) RETURN count(c) as total')
    total = result.single()['total']
    print(f'Total Claim nodes: {total:,}')
    print()
    
    # Check relationship patterns
    result = session.run('''
        MATCH (c:Claim)-[r]-(other)
        RETURN type(r) as rel_type, labels(other)[0] as other_label, count(*) as count
        ORDER BY count DESC
        LIMIT 10
    ''')
    
    print('Claim node relationship patterns:')
    for record in result:
        rel_type = record['rel_type']
        other_label = record['other_label']
        count = record['count']
        print(f'  {rel_type:25s} -> {other_label:20s} ({count:,})')

driver.close()
