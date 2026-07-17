"""
Audit existing Neo4j claims against Phase 2 schema.

Checks:
1. Total claim count
2. Claim property structure
3. Distribution by facet
4. Distribution by status
5. Schema compatibility with Phase 2
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'),
    auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
)

print("="*70)
print("  Neo4j Claims Audit - Phase 2 Schema Compatibility")
print("="*70)
print()

with driver.session() as session:
    # 1. Count total claims
    result = session.run('MATCH ()-[c:ASSERTS]->() RETURN count(c) as total')
    total = result.single()['total']
    print(f'Total :ASSERTS claims: {total:,}')
    print()
    
    # 2. Sample claim properties
    result = session.run('MATCH ()-[c:ASSERTS]->() RETURN c LIMIT 1')
    record = result.single()
    
    if record:
        claim = dict(record['c'])
        print('Sample claim properties:')
        for key, value in sorted(claim.items()):
            val_type = type(value).__name__
            val_preview = str(value)[:50] if value else 'None'
            print(f'  {key:25s} {val_type:15s} {val_preview}')
        print()
    
    # 3. Count by facet
    result = session.run('''
        MATCH ()-[c:ASSERTS]->() 
        RETURN c.facet as facet, count(*) as count 
        ORDER BY count DESC 
        LIMIT 20
    ''')
    print('Claims by facet:')
    for record in result:
        facet = record['facet'] or 'NULL'
        count = record['count']
        print(f'  {facet:25s} {count:>6,}')
    print()
    
    # 4. Count by status
    result = session.run('''
        MATCH ()-[c:ASSERTS]->() 
        RETURN c.status as status, count(*) as count 
        ORDER BY count DESC
    ''')
    print('Claims by status:')
    for record in result:
        status = record['status'] or 'NULL'
        count = record['count']
        print(f'  {status:25s} {count:>6,}')
    print()
    
    # 5. Check for Agent nodes
    result = session.run('MATCH (a:Agent) RETURN count(a) as total')
    agent_count = result.single()['total']
    print(f'Total Agent nodes: {agent_count:,}')
    
    if agent_count > 0:
        result = session.run('''
            MATCH (a:Agent) 
            RETURN a.agent_id as agent_id, a.facet as facet 
            LIMIT 10
        ''')
        print('Sample agents:')
        for record in result:
            agent_id = record['agent_id'] or 'NULL'
            facet = record['facet'] or 'NULL'
            print(f'  {agent_id:35s} facet={facet}')
    print()
    
    # 6. Check entity ciphers
    result = session.run('''
        MATCH (e)<-[:ASSERTS]-()
        WHERE e.entity_cipher IS NOT NULL
        RETURN count(DISTINCT e.entity_cipher) as cipher_count,
               count(DISTINCT e.qid) as qid_count
    ''')
    record = result.single()
    if record:
        print(f'Entities with entity_cipher: {record["cipher_count"]:,}')
        print(f'Entities with qid: {record["qid_count"]:,}')
        print()
    
    # 7. Phase 2 schema compatibility check
    print('Phase 2 Schema Compatibility:')
    
    # Required Phase 2 properties
    phase2_props = ['facet', 'predicate', 'confidence', 'status', 'submitted_at']
    result = session.run('''
        MATCH ()-[c:ASSERTS]->()
        RETURN 
            count(c) as total,
            count(c.facet) as has_facet,
            count(c.predicate) as has_predicate,
            count(c.confidence) as has_confidence,
            count(c.status) as has_status,
            count(c.submitted_at) as has_submitted_at,
            count(c.review_count) as has_review_count,
            count(c.agreement_score) as has_agreement_score
    ''')
    
    record = result.single()
    if record:
        total = record['total']
        for prop in phase2_props:
            has_count = record.get(f'has_{prop}', 0)
            pct = (has_count / total * 100) if total > 0 else 0
            status = '[OK]' if pct == 100 else '[MISSING]'
            print(f'  {status} {prop:20s} {has_count:>6,} / {total:>6,} ({pct:>5.1f}%)')
        
        # Optional Phase 2 properties
        review_count = record.get('has_review_count', 0)
        agreement_score = record.get('has_agreement_score', 0)
        print(f'  [OPT] review_count         {review_count:>6,} / {total:>6,}')
        print(f'  [OPT] agreement_score      {agreement_score:>6,} / {total:>6,}')

driver.close()

print()
print("Audit complete!")
