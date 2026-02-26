#!/usr/bin/env python3
"""
Score all Place nodes and add federation properties
"""
import sys
from pathlib import Path
from neo4j import GraphDatabase

# Add federation scorer to path
sys.path.insert(0, str(Path(__file__).parent / "scripts" / "federation"))
from federation_scorer import FederationScorer

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

print("=" * 80)
print("SCORING ALL PLACES - Federation Vertex Jump Analysis")
print("=" * 80)
print()

scorer = FederationScorer()
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Fetch all places
print("Loading places from Neo4j...")
with driver.session() as session:
    result = session.run("""
        MATCH (p:Place)
        RETURN 
            p.place_id AS place_id,
            p.pleiades_id AS pleiades_id,
            p.qid AS qid,
            p.label AS label,
            p.min_date AS min_date,
            p.max_date AS max_date,
            p.lat AS lat,
            p.long AS long
        ORDER BY p.place_id
    """)
    
    places = list(result)

print(f"Loaded {len(places):,} places")
print()

# Score each place
print("Scoring places...")
scored_places = []
score_distribution = {
    'FS0_UNFEDERATED': 0,
    'FS1_BASE': 0,
    'FS2_FEDERATED': 0,
    'FS3_WELL_FEDERATED': 0
}

for place in places:
    score_result = scorer.score_place_simple(dict(place))
    
    scored_places.append({
        'place_id': place['place_id'],
        'pleiades_id': place['pleiades_id'],
        'qid': place['qid'],
        'label': place['label'],
        'score': score_result['federation_score'],
        'state': score_result['federation_state'],
        'cipher': score_result['federation_cipher_key'],
        'vertex_jump': score_result['vertex_jump_enabled']
    })
    
    score_distribution[score_result['federation_state']] += 1

print(f"Scored {len(scored_places):,} places")
print()

# Show distribution
print("Federation State Distribution:")
print("-" * 80)
for state, count in score_distribution.items():
    pct = (count / len(scored_places) * 100) if scored_places else 0
    print(f"  {state:25} {count:>10,} ({pct:>5.1f}%)")
print()

# Update Neo4j with scores
print("Updating Neo4j with federation properties...")

def update_batch(tx, batch):
    query = """
    UNWIND $batch AS row
    MATCH (p:Place {place_id: row.place_id})
    SET p.federation_score = row.score,
        p.federation_state = row.state,
        p.federation_cipher_key = row.cipher,
        p.vertex_jump_enabled = row.vertex_jump
    """
    tx.run(query, batch=batch)

batch = []
batch_size = 500
count = 0

for scored in scored_places:
    batch.append({
        'place_id': scored['place_id'],
        'score': scored['score'],
        'state': scored['state'],
        'cipher': scored['cipher'],
        'vertex_jump': scored['vertex_jump']
    })
    
    if len(batch) >= batch_size:
        with driver.session() as session:
            session.execute_write(update_batch, batch)
        count += len(batch)
        print(f"  Updated {count:,} places...")
        batch = []

# Final batch
if batch:
    with driver.session() as session:
        session.execute_write(update_batch, batch)
    count += len(batch)

print(f"Update complete: {count:,} places scored")
print()

# Verification
print("Verification:")
print("-" * 80)
with driver.session() as session:
    result = session.run("""
        MATCH (p:Place)
        WHERE p.federation_score IS NOT NULL
        RETURN 
            count(p) AS scored_count,
            avg(p.federation_score) AS avg_score,
            min(p.federation_score) AS min_score,
            max(p.federation_score) AS max_score
    """)
    
    stats = result.single()
    print(f"  Places scored: {stats['scored_count']:,}")
    print(f"  Average score: {stats['avg_score']:.1f}")
    print(f"  Score range: {stats['min_score']:.0f} - {stats['max_score']:.0f}")
    print()
    
    # Sample well-federated places
    result = session.run("""
        MATCH (p:Place)
        WHERE p.federation_state = 'FS3_WELL_FEDERATED'
        RETURN p.label, p.qid, p.federation_score, p.vertex_jump_enabled
        LIMIT 10
    """)
    
    print("Sample FS3_WELL_FEDERATED places (vertex jump ready):")
    for record in result:
        vj_status = "JUMP" if record['p.vertex_jump_enabled'] else "NO"
        print(f"  [{vj_status}] {record['p.label']:40} QID: {record['p.qid']:12} Score: {record['p.federation_score']}")

driver.close()

print()
print("=" * 80)
print("FEDERATION SCORING COMPLETE")
print("=" * 80)
print()
print("All places now have:")
print("  - federation_score (0-100)")
print("  - federation_state (FS0-FS3)")
print("  - federation_cipher_key (subgraph primary key)")
print("  - vertex_jump_enabled (bool)")
print()
print("Agents can now:")
print("  - Navigate by federation quality")
print("  - Vertex jump between federated nodes (what+when+where)")
print("  - Prioritize well-federated subgraphs for claims")

