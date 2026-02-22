#!/usr/bin/env python3
"""Verify Neo4j nodes align with canonical architecture"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

print("=" * 80)
print("ARCHITECTURE ALIGNMENT VERIFICATION")
print("=" * 80)
print()

# Canonical first-class nodes from architecture
CANONICAL_NODES = {
    'SubjectConcept', 'Human', 'Gens', 'Praenomen', 'Cognomen',
    'Event', 'Place', 'Period', 'Dynasty', 'Institution',
    'LegalRestriction', 'Claim', 'Organization', 'Year',
    'Work', 'Material', 'Object', 'ConditionState',
    # Federation metadata
    'FederationRoot', 'FederationType', 'AuthoritySource',
    'Policy', 'Threshold', 'Facet',
    # Supporting nodes
    'PlaceType', 'PlaceTypeTokenMap', 'GeoSemanticType',
    'PeriodCandidate', 'GeoCoverageCandidate',
    'Decade', 'Century', 'Millennium'
}

# Deprecated/non-canonical nodes
DEPRECATED_NODES = {
    'Position',  # Deprecated 2026-02-16
    'Activity',  # Deprecated 2026-02-16
    'RetrievalContext',  # Agent-specific, not in canonical arch
    'AnalysisRun',  # Agent-specific, not in canonical arch
    'FacetAssessment',  # Agent-specific, not in canonical arch
    'FacetCategory'  # Agent-specific, not in canonical arch
}

with driver.session() as session:
    # Get all labels
    result = session.run("CALL db.labels() YIELD label RETURN label ORDER BY label")
    all_labels = [record['label'] for record in result]
    
    print(f"Total labels in Neo4j: {len(all_labels)}")
    print()
    
    # Check each label
    canonical = []
    deprecated = []
    unknown = []
    
    for label in all_labels:
        # Count nodes
        count_result = session.run(f"MATCH (n:{label}) RETURN count(n) AS count")
        count = count_result.single()['count']
        
        if label in CANONICAL_NODES:
            canonical.append((label, count))
        elif label in DEPRECATED_NODES:
            deprecated.append((label, count))
        else:
            unknown.append((label, count))
    
    # Report canonical
    print("CANONICAL NODES (Aligned with Architecture):")
    print("-" * 80)
    for label, count in sorted(canonical):
        print(f"  {label:30} {count:>10,} nodes")
    print()
    
    # Report deprecated
    if deprecated:
        print("DEPRECATED NODES (Should be removed or migrated):")
        print("-" * 80)
        for label, count in sorted(deprecated):
            print(f"  {label:30} {count:>10,} nodes  ⚠️")
        print()
    
    # Report unknown
    if unknown:
        print("UNKNOWN NODES (Not in canonical architecture):")
        print("-" * 80)
        for label, count in sorted(unknown):
            print(f"  {label:30} {count:>10,} nodes  ❓")
        print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Canonical: {len(canonical)} labels")
    print(f"  Deprecated: {len(deprecated)} labels")
    print(f"  Unknown: {len(unknown)} labels")
    print()
    
    if deprecated or unknown:
        print("RECOMMENDATIONS:")
        if deprecated:
            print(f"  ⚠️ {len(deprecated)} deprecated node types found - consider migration/cleanup")
        if unknown:
            print(f"  ❓ {len(unknown)} unknown node types - verify if these should be canonical")

driver.close()

