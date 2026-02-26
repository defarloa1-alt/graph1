// ============================================================
// SYSTEM DESCRIPTION — READ QUERIES FOR MCP AGENTS
// Generated: 2026-02-23
//
// These queries are what MCP tools / agents use to read the
// self-description. Write is handled by generate_system_description.py
// ============================================================


// -- 1. Full description read (agent bootstrap) -----------------------
// Call this when an agent first connects to understand the graph.
MATCH (c:Chrystallum)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
RETURN
  toString(sd.generated_at)    AS generated_at,
  sd.generated_from_version    AS version,
  sd.federation_count          AS federation_count,
  sd.subject_concept_count     AS subject_concept_count,
  sd.entity_count              AS entity_count,
  sd.member_of_edge_count      AS member_of_edge_count,
  sd.anchor_coverage_pct       AS anchor_coverage_pct,
  sd.narrative                 AS narrative,
  sd.narrative_llm             AS narrative_llm,
  sd.federations_json          AS federations_json,
  sd.subject_concepts_json     AS subject_concepts_json,
  sd.entities_json             AS entities_json,
  sd.epistemic_state_json      AS epistemic_state_json
LIMIT 1;


// -- 2. Quick metrics only (lightweight ping) -------------------------
MATCH (c:Chrystallum)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
RETURN
  sd.federation_count          AS federations,
  sd.subject_concept_count     AS subject_concepts,
  sd.entity_count              AS entities,
  sd.anchor_coverage_pct       AS anchor_coverage_pct,
  toString(sd.generated_at)    AS as_of
LIMIT 1;


// -- 3. Narrative only ------------------------------------------------
MATCH (c:Chrystallum)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
RETURN sd.narrative AS narrative, sd.narrative_llm AS llm
LIMIT 1;


// -- 4. Staleness check -----------------------------------------------
// Returns true if description needs regeneration:
//   - never generated
//   - version mismatch
//   - older than 24 hours
MATCH (c:Chrystallum)
OPTIONAL MATCH (c)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
RETURN
  c.version                              AS current_version,
  sd.generated_from_version             AS description_version,
  toString(sd.generated_at)             AS last_generated,
  CASE
    WHEN sd IS NULL                                              THEN true
    WHEN sd.generated_from_version <> c.version                 THEN true
    WHEN duration.between(sd.generated_at, datetime()).hours >= 24 THEN true
    ELSE false
  END                                    AS is_stale
LIMIT 1;


// -- 5. Federation summary from description ---------------------------
// Parses federations_json to list all federations.
// Requires APOC; if APOC unavailable use the raw JSON and parse client-side.
MATCH (c:Chrystallum)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
RETURN apoc.convert.fromJsonMap(sd.federations_json) AS federations
LIMIT 1;

// Without APOC — return raw and parse client-side:
MATCH (c:Chrystallum)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
RETURN sd.federations_json AS federations_json LIMIT 1;


// -- 6. Epistemic state from description ------------------------------
MATCH (c:Chrystallum)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
RETURN sd.epistemic_state_json AS epistemic_state_json LIMIT 1;


// -- 7. Check if description exists at all ----------------------------
MATCH (c:Chrystallum)
OPTIONAL MATCH (c)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
RETURN
  c.name AS system,
  CASE WHEN sd IS NOT NULL THEN true ELSE false END AS has_description,
  toString(sd.generated_at) AS last_generated
LIMIT 1;
