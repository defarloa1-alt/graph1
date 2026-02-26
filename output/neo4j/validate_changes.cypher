// ============================================================
// NEO4J VALIDATION — Changes from Backbone + Federation Work
// Run these in order to validate what's present in your graph
// ============================================================

// --- 1. PREREQUISITES: Chrystallum + Federation structure ---
// SYS_FederationRegistry -> SYS_FederationSource (post-rebuild)
MATCH (c:Chrystallum)
OPTIONAL MATCH (c)-[:HAS_FEDERATION]->(fr:SYS_FederationRegistry)
OPTIONAL MATCH (fr)-[:CONTAINS]->(f:SYS_FederationSource)
RETURN
  c.name AS system,
  c.version AS version,
  fr.label AS federation_registry,
  count(f) AS federation_count
LIMIT 1;
// Expected: federation_count 13 (post-rebuild)


// --- 2. SYSTEM DESCRIPTION: Does it exist? Is it stale? ---
// Run this BEFORE generate_system_description to see if you need to run it
MATCH (c:Chrystallum)
OPTIONAL MATCH (c)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
RETURN
  c.name AS system,
  c.version AS current_version,
  CASE WHEN sd IS NULL THEN false ELSE true END AS has_description,
  toString(sd.generated_at) AS last_generated,
  sd.federation_count AS fed_count_in_desc,
  sd.subject_concept_count AS sc_count_in_desc,
  sd.entity_count AS entity_count_in_desc,
  CASE
    WHEN sd IS NULL THEN 'NEEDS_RUN'
    WHEN sd.generated_from_version <> c.version THEN 'STALE_VERSION'
    WHEN duration.between(sd.generated_at, datetime()).hours >= 24 THEN 'STALE_AGE'
    ELSE 'OK'
  END AS status
LIMIT 1;


// --- 3. FEDERATION SOURCES: Operational/planned/partial ---
// SYS_FederationSource nodes (post-rebuild)
MATCH (fr:SYS_FederationRegistry)-[:CONTAINS]->(f:SYS_FederationSource)
RETURN f.name AS name, f.status AS status, f.scoping_role AS scoping_role, f.phase1_complete AS phase1
ORDER BY f.status, f.name;
// Expected: 13 rows, status mix of operational/planned/partial


// --- 4. CROSSWALK ENRICHMENT: Do Entity nodes have prosopographic IDs? ---
// Run prosopographic_crosswalk.py --write first if all zeros
MATCH (e:Entity)
RETURN
  count(e) AS total_entities,
  count(e.trismegistos_id) AS with_trismegistos,
  count(e.lgpn_id) AS with_lgpn,
  count(e.viaf_id) AS with_viaf,
  count(e.crosswalk_enriched_at) AS crosswalk_enriched
LIMIT 1;


// --- 5. MEMBER_OF EDGES: Did cluster_assignment run? ---
MATCH (e:Entity)-[r:MEMBER_OF]->(sc:SubjectConcept)
RETURN
  count(r) AS member_of_edges,
  count(DISTINCT e) AS unique_entities,
  count(DISTINCT sc) AS subject_concepts_populated
LIMIT 1;


// --- 6. SUBJECT CONCEPTS: Anchor pipeline state ---
MATCH (sc:SubjectConcept)
RETURN
  count(sc) AS total,
  count(sc.qid) AS with_anchor,
  count(CASE WHEN sc.source = 'wikidata' THEN 1 END) AS wikidata_anchored,
  count(CASE WHEN sc.source = 'synthetic' THEN 1 END) AS synthetic
LIMIT 1;


// --- 7. QUICK HEALTH DASHBOARD (Neo4j 4.4+ with CALL subqueries) ---
MATCH (c:Chrystallum)
OPTIONAL MATCH (c)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
CALL {
  MATCH (fr:SYS_FederationRegistry)-[:CONTAINS]->(f:SYS_FederationSource)
  RETURN count(f) AS fc
}
CALL {
  MATCH (e:Entity) RETURN count(e) AS ec
}
CALL {
  MATCH ()-[r:MEMBER_OF]->() RETURN count(r) AS mc
}
CALL {
  MATCH (sc:SubjectConcept) RETURN count(sc) AS scc
}
RETURN
  c.name AS system,
  c.version AS version,
  fc AS federations,
  scc AS subject_concepts,
  ec AS entities,
  mc AS member_of_edges,
  CASE WHEN sd IS NOT NULL THEN 'yes' ELSE 'no' END AS has_system_description,
  toString(sd.generated_at) AS desc_generated_at
LIMIT 1;

// --- 7b. DASHBOARD FALLBACK (if CALL subqueries fail, run queries 1-6 instead) ---
