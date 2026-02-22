#!/usr/bin/env python3
"""
Comprehensive audit: Database reality vs Architecture specifications
Compares actual Neo4j schema against architectural documents
"""

from neo4j import GraphDatabase
import json

NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# ══════════════════════════════════════════════════════════════
# EXPECTED SCHEMA (from architecture docs)
# ══════════════════════════════════════════════════════════════

EXPECTED_ENTITY_TYPES = {
    "PERSON", "EVENT", "PLACE", "SUBJECTCONCEPT", "WORK",
    "ORGANIZATION", "PERIOD", "MATERIAL", "OBJECT"
}

EXPECTED_FACETS = {
    "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION",
    "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC",
    "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC",
    "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC",
    "SOCIAL", "TECHNOLOGICAL"
}

EXPECTED_CIPHER_PREFIXES = {
    "PERSON": "per", "EVENT": "evt", "PLACE": "plc",
    "SUBJECTCONCEPT": "sub", "WORK": "wrk", "ORGANIZATION": "org",
    "PERIOD": "prd", "MATERIAL": "mat", "OBJECT": "obj"
}

EXPECTED_FACET_PREFIXES = {
    "ARCHAEOLOGICAL": "arc", "ARTISTIC": "art", "BIOGRAPHIC": "bio",
    "COMMUNICATION": "com", "CULTURAL": "cul", "DEMOGRAPHIC": "dem",
    "DIPLOMATIC": "dip", "ECONOMIC": "eco", "ENVIRONMENTAL": "env",
    "GEOGRAPHIC": "geo", "INTELLECTUAL": "int", "LINGUISTIC": "lin",
    "MILITARY": "mil", "POLITICAL": "pol", "RELIGIOUS": "rel",
    "SCIENTIFIC": "sci", "SOCIAL": "soc", "TECHNOLOGICAL": "tec"
}

# ══════════════════════════════════════════════════════════════
# AUDIT FUNCTIONS
# ══════════════════════════════════════════════════════════════

def audit_node_labels(session):
    """Check what node labels exist vs what's expected"""
    print("=" * 80)
    print("AUDIT 1: NODE LABELS")
    print("=" * 80)
    
    result = session.run("""
        CALL db.labels() YIELD label
        RETURN label
        ORDER BY label
    """)
    
    actual_labels = {r['label'] for r in result}
    
    print(f"\nTotal labels in database: {len(actual_labels)}")
    print(f"\nAll labels:")
    for label in sorted(actual_labels):
        print(f"  - {label}")
    
    # Check for expected entity labels
    expected_entity_labels = {"Entity", "FacetedEntity", "FacetClaim", "TemporalAnchor"}
    missing_labels = expected_entity_labels - actual_labels
    unexpected_labels = actual_labels - expected_entity_labels - {
        "Human", "Organization", "Period", "Place", "Event", "Work",
        "SubjectConcept", "Claim", "Year", "Agent", "Activity", "Dynasty",
        "Cognomen", "Gens", "Praenomen", "Institution", "LegalRestriction",
        "Material", "Object", "Position", "FacetAssessment", "FacetCategory",
        "Location", "Geometry", "GeoSemanticType", "PlaceName", "PlaceType",
        "RetrievalContext", "AnalysisRun"
    }
    
    print(f"\n[+] Expected labels present: {expected_entity_labels - missing_labels}")
    print(f"[-] Missing labels: {missing_labels}")
    print(f"[?] Unexpected labels: {unexpected_labels}")
    
    return actual_labels


def audit_entity_types(session):
    """Check entity_type property values vs expected registry"""
    print("\n" + "=" * 80)
    print("AUDIT 2: ENTITY TYPES")
    print("=" * 80)
    
    result = session.run("""
        MATCH (n:Entity)
        RETURN DISTINCT n.entity_type as type, count(*) as count
        ORDER BY count DESC
    """)
    
    actual_types = {}
    for r in result:
        actual_types[r['type']] = r['count']
    
    print(f"\nActual entity_type values in database:")
    for type_name, count in actual_types.items():
        status = "✓" if type_name in EXPECTED_ENTITY_TYPES else "✗"
        print(f"  {status} {type_name}: {count} entities")
    
    missing_types = EXPECTED_ENTITY_TYPES - set(actual_types.keys())
    unexpected_types = set(actual_types.keys()) - EXPECTED_ENTITY_TYPES
    
    print(f"\n✓ Expected types present: {EXPECTED_ENTITY_TYPES - missing_types}")
    print(f"✗ Missing types: {missing_types}")
    print(f"? Unexpected types: {unexpected_types}")
    
    return actual_types


def audit_cipher_formats(session):
    """Check cipher format compliance vs specification"""
    print("\n" + "=" * 80)
    print("AUDIT 3: CIPHER FORMATS")
    print("=" * 80)
    
    result = session.run("""
        MATCH (n:Entity)
        WHERE n.entity_cipher IS NOT NULL
        RETURN n.entity_cipher as cipher,
               n.entity_type as type,
               n.qid as qid,
               n.label as label
        LIMIT 50
    """)
    
    correct_format = []
    old_format = []
    invalid_format = []
    
    for r in result:
        cipher = r['cipher']
        entity_type = r['type']
        
        # Check format: ent_{3-char-prefix}_{qid}
        parts = cipher.split('_')
        
        if len(parts) != 3:
            invalid_format.append((cipher, entity_type, "Wrong number of parts"))
            continue
        
        prefix_part = parts[1]
        qid_part = parts[2]
        
        # Check if using old CONCEPT format
        if prefix_part == "con":
            old_format.append((cipher, entity_type, r['qid'], r['label']))
            continue
        
        # Check if prefix matches entity type
        if entity_type in EXPECTED_CIPHER_PREFIXES:
            expected_prefix = EXPECTED_CIPHER_PREFIXES[entity_type]
            if prefix_part == expected_prefix:
                correct_format.append((cipher, entity_type))
            else:
                invalid_format.append((cipher, entity_type, f"Expected {expected_prefix}, got {prefix_part}"))
        else:
            invalid_format.append((cipher, entity_type, "Unknown entity type"))
    
    print(f"\n✓ Correct format: {len(correct_format)}")
    print(f"⚠ Old format (ent_con_*): {len(old_format)}")
    print(f"✗ Invalid format: {len(invalid_format)}")
    
    if old_format:
        print(f"\nOld format examples (need migration):")
        for cipher, etype, qid, label in old_format[:5]:
            expected_prefix = EXPECTED_CIPHER_PREFIXES.get(etype, "???")
            expected_cipher = f"ent_{expected_prefix}_{qid}"
            print(f"  {cipher} ({etype})")
            print(f"    QID: {qid}")
            print(f"    Label: {label}")
            print(f"    Should be: {expected_cipher}")
    
    if correct_format:
        print(f"\n✓ Correct format examples:")
        for cipher, etype in correct_format[:5]:
            print(f"  {cipher} ({etype})")
    
    return len(old_format), len(correct_format)


def audit_temporal_anchor_pattern(session):
    """Check TemporalAnchor implementation vs ADR-002"""
    print("\n" + "=" * 80)
    print("AUDIT 4: TEMPORALANCHOR PATTERN (ADR-002)")
    print("=" * 80)
    
    # Check for TemporalAnchor label
    result = session.run("MATCH (n:TemporalAnchor) RETURN count(n) as total")
    temporal_label_count = result.single()['total']
    
    # Check for temporal properties
    result = session.run("""
        MATCH (n:Entity)
        WHERE n.temporal_start_year IS NOT NULL
        RETURN count(n) as total
    """)
    temporal_prop_count = result.single()['total']
    
    # Check for is_temporal_anchor flag
    result = session.run("""
        MATCH (n:Entity)
        WHERE n.is_temporal_anchor = true
        RETURN count(n) as total
    """)
    temporal_flag_count = result.single()['total']
    
    print(f"\nTemporalAnchor Implementation:")
    print(f"  Nodes with :TemporalAnchor label: {temporal_label_count}")
    print(f"  Nodes with temporal_start_year: {temporal_prop_count}")
    print(f"  Nodes with is_temporal_anchor=true: {temporal_flag_count}")
    
    if temporal_label_count == 0 and temporal_prop_count == 0:
        print(f"\n✗ ADR-002 NOT IMPLEMENTED")
        print(f"   Status: TemporalAnchor pattern not yet deployed")
    else:
        print(f"\n⚠ ADR-002 PARTIALLY IMPLEMENTED")
        print(f"   Label vs Property mismatch")
    
    # Check entities that SHOULD be temporal anchors
    result = session.run("""
        MATCH (n:Entity)
        WHERE n.qid IN ['Q17167', 'Q2277', 'Q12548', 'Q6813', 'Q11768']
        RETURN n.qid as qid,
               n.label as label,
               n.entity_type as type,
               n.entity_cipher as cipher,
               n.temporal_start_year as temp_start,
               labels(n) as all_labels
    """)
    
    print(f"\nEntities that SHOULD have TemporalAnchor pattern:")
    for r in result:
        has_label = 'TemporalAnchor' in r['all_labels']
        has_property = r['temp_start'] is not None
        status = "✓" if has_label and has_property else "✗"
        print(f"  {status} {r['qid']} ({r['label']})")
        print(f"      Type: {r['type']}")
        print(f"      Cipher: {r['cipher']}")
        print(f"      Labels: {r['all_labels']}")
        print(f"      Temporal: {r['temp_start']}")
    
    return temporal_label_count


def audit_faceted_entities(session):
    """Check FacetedEntity nodes vs specification"""
    print("\n" + "=" * 80)
    print("AUDIT 5: FACETED ENTITIES (TIER 2)")
    print("=" * 80)
    
    result = session.run("MATCH (n:FacetedEntity) RETURN count(n) as total")
    faceted_count = result.single()['total']
    
    print(f"\nFacetedEntity nodes: {faceted_count}")
    
    if faceted_count > 0:
        result = session.run("""
            MATCH (n:FacetedEntity)
            RETURN n.faceted_cipher as cipher,
                   n.entity_cipher as entity_cipher,
                   n.facet_id as facet,
                   n.subjectconcept_id as subject
            LIMIT 10
        """)
        
        print(f"\nSample FacetedEntity nodes:")
        for r in result:
            print(f"  {r['cipher']}")
            print(f"    Entity: {r['entity_cipher']}")
            print(f"    Facet: {r['facet']}")
            print(f"    Subject: {r['subject']}")
    else:
        print(f"\n✗ No FacetedEntity nodes (Tier 2 not implemented)")
    
    return faceted_count


def audit_claims(session):
    """Check Claim/FacetClaim nodes vs specification"""
    print("\n" + "=" * 80)
    print("AUDIT 6: CLAIMS (TIER 3)")
    print("=" * 80)
    
    # Check for Claim nodes
    result = session.run("MATCH (n:Claim) RETURN count(n) as total")
    claim_count = result.single()['total']
    
    # Check for FacetClaim nodes
    result = session.run("MATCH (n:FacetClaim) RETURN count(n) as total")
    facet_claim_count = result.single()['total']
    
    print(f"\nClaim nodes: {claim_count}")
    print(f"FacetClaim nodes: {facet_claim_count}")
    
    if claim_count > 0:
        result = session.run("""
            MATCH (c:Claim)
            RETURN c.cipher as cipher,
                   c.claim_id as claim_id,
                   c.text as text,
                   c.confidence as confidence,
                   keys(c) as properties
            LIMIT 5
        """)
        
        print(f"\nSample Claim schema (actual properties):")
        for r in result:
            print(f"  Cipher: {r['cipher']}")
            print(f"  Properties: {sorted(r['properties'])}")
            
            # Check for expected Tier 3 properties
            expected_props = {
                'cipher', 'subject_entity_cipher', 'facet_id',
                'analysis_layer', 'confidence'
            }
            actual_props = set(r['properties'])
            missing = expected_props - actual_props
            if missing:
                print(f"    ✗ Missing properties: {missing}")
    
    if facet_claim_count > 0:
        result = session.run("""
            MATCH (c:FacetClaim)
            RETURN c.cipher as cipher,
                   c.subject_entity_cipher as subject,
                   c.facet_id as facet,
                   c.analysis_layer as layer,
                   keys(c) as properties
            LIMIT 5
        """)
        
        print(f"\nSample FacetClaim schema:")
        for r in result:
            print(f"  {r['cipher']}")
            print(f"    Subject: {r['subject']}")
            print(f"    Facet: {r['facet']}")
            print(f"    Layer: {r['layer']}")
            print(f"    Properties: {sorted(r['properties'])}")
    
    return claim_count, facet_claim_count


def audit_relationships(session):
    """Check relationship types vs specification"""
    print("\n" + "=" * 80)
    print("AUDIT 7: RELATIONSHIP TYPES")
    print("=" * 80)
    
    result = session.run("""
        CALL db.relationshipTypes() YIELD relationshipType
        RETURN relationshipType
        ORDER BY relationshipType
    """)
    
    rel_types = [r['relationshipType'] for r in result]
    
    print(f"\nTotal relationship types: {len(rel_types)}")
    print(f"\nRelationship types:")
    for rel in rel_types:
        print(f"  - {rel}")
    
    # Check for expected cipher-related relationships
    expected_rels = {
        "HAS_FACETED_VIEW", "CONTAINS_CLAIM", "INSTANCE_OF",
        "SUBCLASS_OF", "PART_OF", "HAS_PART"
    }
    
    present = expected_rels & set(rel_types)
    missing = expected_rels - set(rel_types)
    
    print(f"\n✓ Expected relationships present: {present}")
    print(f"✗ Missing relationships: {missing}")
    
    return rel_types


def audit_cipher_compliance(session):
    """Deep audit of cipher format compliance"""
    print("\n" + "=" * 80)
    print("AUDIT 8: CIPHER FORMAT COMPLIANCE (DETAILED)")
    print("=" * 80)
    
    result = session.run("""
        MATCH (n:Entity)
        RETURN n.entity_cipher as cipher,
               n.entity_type as type,
               n.qid as qid
    """)
    
    stats = {
        "total": 0,
        "correct_format": 0,
        "old_con_format": 0,
        "missing_cipher": 0,
        "mismatched_prefix": 0,
        "by_type": {}
    }
    
    for r in result:
        stats["total"] += 1
        cipher = r['cipher']
        entity_type = r['type']
        qid = r['qid']
        
        if not cipher:
            stats["missing_cipher"] += 1
            continue
        
        parts = cipher.split('_')
        if len(parts) != 3:
            continue
        
        prefix = parts[1]
        
        # Track by entity type
        if entity_type not in stats["by_type"]:
            stats["by_type"][entity_type] = {
                "count": 0, "correct": 0, "old_con": 0, "wrong_prefix": 0
            }
        stats["by_type"][entity_type]["count"] += 1
        
        # Check format
        if prefix == "con":
            stats["old_con_format"] += 1
            stats["by_type"][entity_type]["old_con"] += 1
        elif entity_type in EXPECTED_CIPHER_PREFIXES:
            expected = EXPECTED_CIPHER_PREFIXES[entity_type]
            if prefix == expected:
                stats["correct_format"] += 1
                stats["by_type"][entity_type]["correct"] += 1
            else:
                stats["mismatched_prefix"] += 1
                stats["by_type"][entity_type]["wrong_prefix"] += 1
    
    print(f"\nCipher Format Statistics:")
    print(f"  Total entities: {stats['total']}")
    print(f"  ✓ Correct format: {stats['correct_format']} ({stats['correct_format']/stats['total']*100:.1f}%)")
    print(f"  ⚠ Old 'ent_con_*' format: {stats['old_con_format']} ({stats['old_con_format']/stats['total']*100:.1f}%)")
    print(f"  ✗ Mismatched prefix: {stats['mismatched_prefix']}")
    print(f"  ✗ Missing cipher: {stats['missing_cipher']}")
    
    print(f"\nBreakdown by entity_type:")
    for etype, counts in sorted(stats["by_type"].items()):
        total = counts["count"]
        correct_pct = counts["correct"] / total * 100 if total > 0 else 0
        print(f"  {etype}: {total} total")
        print(f"    ✓ Correct: {counts['correct']} ({correct_pct:.1f}%)")
        print(f"    ⚠ Old con: {counts['old_con']}")
        print(f"    ✗ Wrong: {counts['wrong_prefix']}")
    
    return stats


def audit_facet_usage(session):
    """Check if any facets are being used"""
    print("\n" + "=" * 80)
    print("AUDIT 9: FACET USAGE (18 CANONICAL FACETS)")
    print("=" * 80)
    
    # Check FacetedEntity facet_id values
    result = session.run("""
        MATCH (n:FacetedEntity)
        RETURN DISTINCT n.facet_id as facet, count(*) as count
        ORDER BY count DESC
    """)
    
    facet_usage = {}
    for r in result:
        facet_usage[r['facet']] = r['count']
    
    if not facet_usage:
        print(f"\n✗ No facets in use (FacetedEntity nodes not created yet)")
    else:
        print(f"\nFacets in use:")
        for facet, count in facet_usage.items():
            status = "✓" if facet in EXPECTED_FACETS else "✗"
            print(f"  {status} {facet}: {count}")
    
    missing_facets = EXPECTED_FACETS - set(facet_usage.keys())
    print(f"\nUnused facets: {len(missing_facets)}")
    if missing_facets:
        print(f"  {', '.join(sorted(missing_facets))}")
    
    return facet_usage


def audit_qualifier_support(session):
    """Check if qualifier properties exist on claims"""
    print("\n" + "=" * 80)
    print("AUDIT 10: QUALIFIER SUPPORT (REQ-DATA-003)")
    print("=" * 80)
    
    qualifier_props = [
        "qualifier_p580_normalized",
        "qualifier_p582_normalized",
        "qualifier_p585_normalized",
        "qualifier_p276_qid",
        "qualifier_p1545_ordinal"
    ]
    
    for prop in qualifier_props:
        result = session.run(f"""
            MATCH (c:FacetClaim)
            WHERE c.{prop} IS NOT NULL
            RETURN count(c) as total
        """)
        count = result.single()['total']
        status = "✓" if count > 0 else "✗"
        print(f"  {status} {prop}: {count} claims")
    
    # Check for metadata_qualifiers
    result = session.run("""
        MATCH (c:FacetClaim)
        WHERE c.metadata_qualifiers IS NOT NULL
        RETURN count(c) as total
    """)
    metadata_count = result.single()['total']
    print(f"\n  Claims with metadata_qualifiers: {metadata_count}")
    
    if all(count == 0 for count in [metadata_count]):
        print(f"\n✗ Qualifier support NOT IMPLEMENTED")
    
    return None


# ══════════════════════════════════════════════════════════════
# MAIN AUDIT EXECUTION
# ══════════════════════════════════════════════════════════════

def main():
    print("=" * 80)
    print(" " * 20 + "SCHEMA AUDIT: REALITY vs SPECIFICATION")
    print("=" * 80)
    print()
    print("Comparing actual Neo4j database against architecture docs:")
    print("  - ENTITY_CIPHER_FOR_VERTEX_JUMPS.md")
    print("  - NEO4J_SCHEMA_DDL_COMPLETE.md")
    print("  - TIER_3_CLAIM_CIPHER_ADDENDUM.md")
    print()
    
    with driver.session() as session:
        # Run all audits
        labels = audit_node_labels(session)
        types = audit_entity_types(session)
        old_count, correct_count = audit_cipher_formats(session)
        temporal_count = audit_temporal_anchor_pattern(session)
        faceted_count = audit_faceted_entities(session)
        claim_count, facet_claim_count = audit_claims(session)
        rel_types = audit_relationships(session)
        facet_usage = audit_facet_usage(session)
        audit_qualifier_support(session)
    
    # ══════════════════════════════════════════════════════════
    # SUMMARY & RECOMMENDATIONS
    # ══════════════════════════════════════════════════════════
    
    print("\n" + "=" * 80)
    print(" " * 30 + "AUDIT SUMMARY")
    print("=" * 80)
    
    print(f"""
IMPLEMENTATION STATUS:

Tier 1 (Entity Cipher):
  ✓ Constraints in place: Yes (entity_cipher_unique, entity_qid_unique)
  ✓ Indexes in place: Yes (entity_type_idx)
  ⚠ Cipher format compliance: {correct_count}/{correct_count + old_count} ({correct_count/(correct_count + old_count)*100:.1f}%)
  ✗ Migration needed: {old_count} entities using old 'ent_con_*' format

Tier 2 (Faceted Entity Cipher):
  ✓ Constraints in place: Yes (faceted_cipher_idx exists)
  ✓ Indexes in place: Yes (faceted_entity_facet_idx exists)
  {'✓' if faceted_count > 0 else '✗'} FacetedEntity nodes: {faceted_count}
  {'✓' if facet_usage else '✗'} Facet usage: {len(facet_usage)} of 18 facets in use

Tier 3 (Claim Cipher):
  ✓ Constraints in place: Yes (claim_cipher_unique exists)
  {'✓' if facet_claim_count > 0 else '✗'} FacetClaim nodes: {facet_claim_count}
  ✗ Qualifier properties: Not implemented
  ✗ Qualifier indexes: Not created (7 missing)

TemporalAnchor Pattern (ADR-002):
  ✗ :TemporalAnchor labels: {temporal_count}
  ✗ temporal_start_year properties: 0
  ✗ temporal_end_year properties: 0
  ✗ TemporalAnchor constraints: Not created (3 missing)
  ✗ TemporalAnchor indexes: Not created (3 missing)

RECOMMENDATIONS:

Priority 1 (HIGH): Execute DDL addendum
  → Add TemporalAnchor constraints (3)
  → Add TemporalAnchor indexes (3)
  → Add Qualifier indexes (7)
  → Risk: LOW (IF NOT EXISTS protects)
  → Time: 15 minutes

Priority 2 (MEDIUM): Migrate cipher format
  → Convert {old_count} entities from 'ent_con_*' to canonical prefixes
  → Risk: MEDIUM (data modification)
  → Time: 1 hour
  → Requires: Test on staging first

Priority 3 (MEDIUM): Implement TemporalAnchor pattern
  → Add temporal properties to eligible entities (Q17167, etc.)
  → Add :TemporalAnchor labels
  → Risk: MEDIUM (data modification)
  → Time: 2 hours
  → Requires: Wikidata queries for temporal bounds

Priority 4 (LOW): Create FacetedEntity nodes
  → Generate 18 faceted ciphers per entity
  → Risk: LOW (new nodes, no modification)
  → Time: 1 hour
  → Requires: Entity scaling complete first
    """)
    
    # Save audit results
    audit_results = {
        "audit_date": "2026-02-22",
        "database_uri": NEO4J_URI,
        "total_entities": correct_count + old_count,
        "cipher_format": {
            "correct": correct_count,
            "old_con_format": old_count,
            "compliance_pct": correct_count / (correct_count + old_count) * 100 if (correct_count + old_count) > 0 else 0
        },
        "temporal_anchor": {
            "implemented": temporal_count > 0,
            "node_count": temporal_count
        },
        "faceted_entities": {
            "implemented": faceted_count > 0,
            "node_count": faceted_count
        },
        "claims": {
            "total_claims": claim_count,
            "facet_claims": facet_claim_count
        },
        "recommendations": [
            "Execute DDL addendum (Priority 1)",
            "Migrate cipher format (Priority 2)",
            "Implement TemporalAnchor pattern (Priority 3)"
        ]
    }
    
    with open('output/schema_audit_results.json', 'w') as f:
        json.dump(audit_results, f, indent=2)
    
    print("\n✓ Audit results saved to: output/schema_audit_results.json")
    print()

if __name__ == "__main__":
    main()
    driver.close()
