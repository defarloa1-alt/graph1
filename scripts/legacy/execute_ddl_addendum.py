#!/usr/bin/env python3
"""Execute DDL addendum (TemporalAnchor + Qualifiers)"""

from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

ddl_statements = [
    # TemporalAnchor constraints (3)
    "CREATE CONSTRAINT temporal_start_year_exists IF NOT EXISTS FOR (n:TemporalAnchor) REQUIRE n.temporal_start_year IS NOT NULL",
    "CREATE CONSTRAINT temporal_end_year_exists IF NOT EXISTS FOR (n:TemporalAnchor) REQUIRE n.temporal_end_year IS NOT NULL",
    "CREATE CONSTRAINT temporal_scope_exists IF NOT EXISTS FOR (n:TemporalAnchor) REQUIRE n.temporal_scope IS NOT NULL",
    
    # TemporalAnchor indexes (3)
    "CREATE INDEX temporal_range_idx IF NOT EXISTS FOR (n:TemporalAnchor) ON (n.temporal_start_year, n.temporal_end_year)",
    "CREATE INDEX temporal_nesting_idx IF NOT EXISTS FOR (n:TemporalAnchor) ON (n.temporal_start_year)",
    "CREATE INDEX temporal_calendar_idx IF NOT EXISTS FOR (n:TemporalAnchor) ON (n.temporal_calendar)",
    
    # Qualifier indexes for Tier 3 (7)
    "CREATE INDEX claim_wikidata_triple_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.subject_entity_cipher, c.wikidata_pid, c.object_qid)",
    "CREATE INDEX claim_temporal_start_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p580_normalized)",
    "CREATE INDEX claim_temporal_end_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p582_normalized)",
    "CREATE INDEX claim_temporal_point_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p585_normalized)",
    "CREATE INDEX claim_location_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p276_qid)",
    "CREATE INDEX claim_ordinal_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p1545_ordinal)",
    "CREATE INDEX claim_temporal_scope_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.temporal_scope)",
]

with driver.session() as session:
    print("Executing DDL addendum...\n")
    created = []
    skipped = []
    
    for i, ddl in enumerate(ddl_statements, 1):
        print(f"[{i}/{len(ddl_statements)}] Executing...", end=" ")
        try:
            session.run(ddl)
            created.append(ddl.split()[2])
            print("SUCCESS")
        except Exception as e:
            if "already exists" in str(e).lower():
                skipped.append(ddl.split()[2])
                print("Skipped (exists)")
            else:
                print(f"Error: {e}")
    
    print(f"\nSummary: {len(created)} created, {len(skipped)} skipped\n")

driver.close()
print("DDL addendum complete!")
