#!/usr/bin/env python3
"""
Enrich SubjectConcept Ontology with Library Authority Federation

Maps Roman Republic SubjectConcepts to LCSH, FAST, LCC and scores them.
"""
import sys
from pathlib import Path
from neo4j import GraphDatabase

# Import federation scorer
sys.path.insert(0, r'C:\Projects\Graph1\scripts\federation')
from federation_scorer import FederationScorer

# Aura connection
URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

print("=" * 80)
print("ENRICHING ROMAN REPUBLIC ONTOLOGY WITH LIBRARY AUTHORITIES")
print("=" * 80)
print()

# Manual authority mappings for key concepts
# TODO: Automate this via LCSH/FAST API lookups
AUTHORITY_MAPPINGS = {
    'subj_roman_republic_q17167': {
        'lcsh_id': 'sh85115055',
        'lcsh_heading': 'Rome--History--Republic, 510-30 B.C.',
        'fast_id': 'fst01204885',
        'lcc_class': 'DG',
        'lcc_subclass': 'DG254',
        'qid': 'Q17167'
    },
    'subj_rr_governance': {
        'lcsh_id': 'sh85115062',
        'lcsh_heading': 'Rome--Politics and government--510-30 B.C.',
        'fast_id': 'fst01204903',
        'lcc_class': 'DG',
        'lcc_subclass': 'DG254'
    },
    'subj_rr_military': {
        'lcsh_id': 'sh85115068',
        'lcsh_heading': 'Rome--History, Military',
        'fast_id': 'fst01353235',
        'lcc_class': 'DG',
        'lcc_subclass': 'DG89'
    },
    'subj_rr_society': {
        'lcsh_id': 'sh85115073',
        'lcsh_heading': 'Rome--Social conditions',
        'fast_id': 'fst01204924',
        'lcc_class': 'DG',
        'lcc_subclass': 'DG78'
    },
    'subj_rr_economy': {
        'lcsh_id': 'sh85115056',
        'lcsh_heading': 'Rome--Economic conditions',
        'fast_id': 'fst01204878',
        'lcc_class': 'DG',
        'lcc_subclass': 'DG77'
    },
    'subj_rr_religion': {
        'lcsh_id': 'sh85115072',
        'lcsh_heading': 'Rome--Religion',
        'fast_id': 'fst01204923',
        'lcc_class': 'BL',
        'lcc_subclass': 'BL802'
    },
    # Add more mappings as discovered...
}

scorer = FederationScorer()
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

print("[1/2] Applying authority mappings...")

def update_authorities_batch(tx, batch):
    """Add authority properties to SubjectConcept nodes"""
    query = """
    UNWIND $batch AS row
    MATCH (s:SubjectConcept {subject_id: row.subject_id})
    SET s.lcsh_id = row.lcsh_id,
        s.lcsh_heading = row.lcsh_heading,
        s.fast_id = row.fast_id,
        s.lcc_class = row.lcc_class,
        s.lcc_subclass = row.lcc_subclass,
        s.authority_federation_score = row.score,
        s.authority_federation_state = row.state,
        s.authority_federation_cipher = row.cipher,
        s.authority_jump_enabled = row.jump_enabled
    """
    tx.run(query, batch=batch)

batch = []
count = 0

for subject_id, authorities in AUTHORITY_MAPPINGS.items():
    # Score the concept
    score_result = scorer.score_subject_concept(authorities)
    
    batch.append({
        'subject_id': subject_id,
        'lcsh_id': authorities.get('lcsh_id'),
        'lcsh_heading': authorities.get('lcsh_heading'),
        'fast_id': authorities.get('fast_id'),
        'lcc_class': authorities.get('lcc_class'),
        'lcc_subclass': authorities.get('lcc_subclass'),
        'score': score_result['authority_federation_score'],
        'state': score_result['authority_federation_state'],
        'cipher': score_result['authority_federation_cipher'],
        'jump_enabled': score_result['authority_jump_enabled']
    })
    count += 1

# Apply updates
with driver.session() as session:
    session.execute_write(update_authorities_batch, batch)

print(f"  Enriched {count} SubjectConcept nodes with authorities")
print()

# Verification
print("[2/2] Verification...")
with driver.session() as session:
    result = session.run("""
        MATCH (s:SubjectConcept)
        WHERE s.subject_id STARTS WITH 'subj_rr_'
        RETURN 
            count(s) AS total,
            count(s.lcsh_id) AS with_lcsh,
            count(s.fast_id) AS with_fast,
            count(s.lcc_class) AS with_lcc,
            count(s.qid) AS with_qid,
            count(s.authority_federation_score) AS with_score
    """)
    
    stats = result.single()
    
    print("Authority Federation Coverage:")
    print(f"  Total SubjectConcepts: {stats['total']}")
    print(f"  With LCSH: {stats['with_lcsh']} ({stats['with_lcsh']/stats['total']*100:.1f}%)")
    print(f"  With FAST: {stats['with_fast']} ({stats['with_fast']/stats['total']*100:.1f}%)")
    print(f"  With LCC: {stats['with_lcc']} ({stats['with_lcc']/stats['total']*100:.1f}%)")
    print(f"  With QID: {stats['with_qid']} ({stats['with_qid']/stats['total']*100:.1f}%)")
    print(f"  With federation score: {stats['with_score']} ({stats['with_score']/stats['total']*100:.1f}%)")
    print()
    
    # Show federated concepts
    result = session.run("""
        MATCH (s:SubjectConcept)
        WHERE s.authority_federation_score IS NOT NULL
        RETURN 
            s.label AS label,
            s.authority_federation_score AS score,
            s.authority_federation_state AS state,
            s.lcsh_id AS lcsh,
            s.fast_id AS fast,
            s.lcc_class AS lcc
        ORDER BY score DESC
    """)
    
    print("Enriched SubjectConcepts (by federation score):")
    for record in result:
        print(f"  [{record['score']:3}] {record['label']:50} "
              f"LCSH:{record['lcsh'] or 'N/A':12} "
              f"FAST:{record['fast'] or 'N/A':12} "
              f"LCC:{record['lcc'] or 'N/A'}")

driver.close()

print()
print("=" * 80)
print("AUTHORITY ENRICHMENT COMPLETE")
print("=" * 80)
print()
print(f"Enriched {count} key concepts with library authorities")
print()
print("Next steps:")
print("  1. Map remaining SubjectConcepts to LCSH/FAST")
print("  2. Use auto-suggestion to fill gaps")
print("  3. Validate facet alignment with FAST categories")
print()
print("SubjectConcepts now have:")
print("  - Library authority IDs (LCSH, FAST, LCC)")
print("  - Authority federation scores")
print("  - Authority jump capability")
print("  - Same pattern as Place/Period federation!")

