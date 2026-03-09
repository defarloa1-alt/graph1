// ============================================================
// Script 18j — SYS_RoutingRule nodes for domain_roman_republic
// ============================================================
// Promotes PERSON_ROUTES and PLACE_ROUTES from hardcoded Python
// dicts → first-class graph nodes. populate_member_of.py reads
// from these nodes — routing rules are now queryable, versionable,
// and domain-swappable without code changes.
//
// SYS_RoutingRule schema:
//   rule_id      : unique string key
//   domain       : 'roman_republic'
//   source_type  : 'position_held' | 'place_type'
//   sc_id        : target SubjectConcept.subject_id
//   match_value  : position label (exact) | place_type substring (contains) | '*' (catch_all)
//   match_mode   : 'exact' | 'contains' | 'catch_all'
//   rank         : 'primary' | 'inferred'
//   priority     : integer — ordering for place routes (catch_all = 99)
//
// Edge: (SYS_RoutingRule)-[:TARGETS]->(SubjectConcept)
// ============================================================

// ── Person routes — sc_constitution ──────────────────────────────────────────
UNWIND [
  'consul', 'praetor', 'quaestor', 'censor',
  'aedilis curulis', 'aedilis plebis',
  'tribunus plebis', 'interrex',
  'princeps senatus', 'senator - office unknown',
  'decemvir consulari imperio legibus scribundis',
  'tribunus militum consulari potestate',
  'proquaestor',
  'repulsa (cos.)', 'repulsa (cens.)', 'repulsa (pr.)',
  'dictator',
  'dictator comitiorum habendorum causa',
  'dictator legibus faciendis et rei publicae constituendae causa',
  'dictator perpetuus'
] AS val
MERGE (r:SYS_RoutingRule {rule_id: 'rr_rr_ph_constitution_' + apoc.text.slug(val)})
SET r.domain       = 'roman_republic'
  , r.source_type  = 'position_held'
  , r.sc_id        = 'sc_constitution'
  , r.match_value  = val
  , r.match_mode   = 'exact'
  , r.rank         = 'primary'
  , r.priority     = 1
WITH r
MATCH (sc:SubjectConcept {subject_id: 'sc_constitution'})
MERGE (r)-[:TARGETS]->(sc)
RETURN count(r) AS constitution_rules;

// ── Person routes — sc_military ───────────────────────────────────────────────
UNWIND [
  'tribunus militum', 'legatus (lieutenant)',
  'triumphator', 'praefectus', 'promagistrate',
  'proconsul', 'propraetor', 'magister equitum',
  'officer (title not preserved)'
] AS val
MERGE (r:SYS_RoutingRule {rule_id: 'rr_rr_ph_military_' + apoc.text.slug(val)})
SET r.domain       = 'roman_republic'
  , r.source_type  = 'position_held'
  , r.sc_id        = 'sc_military'
  , r.match_value  = val
  , r.match_mode   = 'exact'
  , r.rank         = 'primary'
  , r.priority     = 1
WITH r
MATCH (sc:SubjectConcept {subject_id: 'sc_military'})
MERGE (r)-[:TARGETS]->(sc)
RETURN count(r) AS military_rules;

// ── Person routes — sc_religion ───────────────────────────────────────────────
UNWIND [
  'augur', 'pontifex', 'pontifex maximus',
  'flamen Martialis', 'decemvir sacris faciundis'
] AS val
MERGE (r:SYS_RoutingRule {rule_id: 'rr_rr_ph_religion_' + apoc.text.slug(val)})
SET r.domain       = 'roman_republic'
  , r.source_type  = 'position_held'
  , r.sc_id        = 'sc_religion'
  , r.match_value  = val
  , r.match_mode   = 'exact'
  , r.rank         = 'primary'
  , r.priority     = 1
WITH r
MATCH (sc:SubjectConcept {subject_id: 'sc_religion'})
MERGE (r)-[:TARGETS]->(sc)
RETURN count(r) AS religion_rules;

// ── Person routes — sc_diplomacy ──────────────────────────────────────────────
UNWIND ['legatus (ambassador)', 'legatus (envoy)'] AS val
MERGE (r:SYS_RoutingRule {rule_id: 'rr_rr_ph_diplomacy_' + apoc.text.slug(val)})
SET r.domain       = 'roman_republic'
  , r.source_type  = 'position_held'
  , r.sc_id        = 'sc_diplomacy'
  , r.match_value  = val
  , r.match_mode   = 'exact'
  , r.rank         = 'primary'
  , r.priority     = 1
WITH r
MATCH (sc:SubjectConcept {subject_id: 'sc_diplomacy'})
MERGE (r)-[:TARGETS]->(sc)
RETURN count(r) AS diplomacy_rules;

// ── Person routes — sc_economy ────────────────────────────────────────────────
UNWIND ['monetalis', 'moneyer'] AS val
MERGE (r:SYS_RoutingRule {rule_id: 'rr_rr_ph_economy_' + apoc.text.slug(val)})
SET r.domain       = 'roman_republic'
  , r.source_type  = 'position_held'
  , r.sc_id        = 'sc_economy'
  , r.match_value  = val
  , r.match_mode   = 'exact'
  , r.rank         = 'primary'
  , r.priority     = 1
WITH r
MATCH (sc:SubjectConcept {subject_id: 'sc_economy'})
MERGE (r)-[:TARGETS]->(sc)
RETURN count(r) AS economy_rules;

// ── Place routes — GEO_SETTLEMENTS (priority 1) ───────────────────────────────
UNWIND ['settlement', 'villa', 'station'] AS val
MERGE (r:SYS_RoutingRule {rule_id: 'rr_rr_pt_settlements_' + val})
SET r.domain       = 'roman_republic'
  , r.source_type  = 'place_type'
  , r.sc_id        = 'GEO_SETTLEMENTS'
  , r.match_value  = val
  , r.match_mode   = 'contains'
  , r.rank         = 'primary'
  , r.priority     = 1
WITH r
MATCH (sc:SubjectConcept {subject_id: 'GEO_SETTLEMENTS'})
MERGE (r)-[:TARGETS]->(sc)
RETURN count(r) AS settlements_rules;

// ── Place routes — GEO_HIST_PLACES (priority 2) ───────────────────────────────
UNWIND [
  'temple', 'sanctuary', 'tomb', 'cemetery',
  'monument', 'amphitheatre', 'theatre', 'bath',
  'aqueduct', 'tumulus', 'church', 'mine',
  'quarry', 'bridge', 'road', 'fort', 'archaeological'
] AS val
MERGE (r:SYS_RoutingRule {rule_id: 'rr_rr_pt_hist_places_' + val})
SET r.domain       = 'roman_republic'
  , r.source_type  = 'place_type'
  , r.sc_id        = 'GEO_HIST_PLACES'
  , r.match_value  = val
  , r.match_mode   = 'contains'
  , r.rank         = 'primary'
  , r.priority     = 2
WITH r
MATCH (sc:SubjectConcept {subject_id: 'GEO_HIST_PLACES'})
MERGE (r)-[:TARGETS]->(sc)
RETURN count(r) AS hist_places_rules;

// ── Place routes — GEO_HYDROGRAPHY (priority 3) ───────────────────────────────
UNWIND [
  'river', 'lake', 'harbor', 'harbour',
  'bay', 'spring', 'sea', 'estuary', 'pool', 'channel'
] AS val
MERGE (r:SYS_RoutingRule {rule_id: 'rr_rr_pt_hydro_' + val})
SET r.domain       = 'roman_republic'
  , r.source_type  = 'place_type'
  , r.sc_id        = 'GEO_HYDROGRAPHY'
  , r.match_value  = val
  , r.match_mode   = 'contains'
  , r.rank         = 'primary'
  , r.priority     = 3
WITH r
MATCH (sc:SubjectConcept {subject_id: 'GEO_HYDROGRAPHY'})
MERGE (r)-[:TARGETS]->(sc)
RETURN count(r) AS hydro_rules;

// ── Place routes — GEO_PHYS_FEATURES (priority 4) ────────────────────────────
UNWIND [
  'mountain', 'island', 'cape', 'valley',
  'hill', 'plain', 'forest', 'promontory'
] AS val
MERGE (r:SYS_RoutingRule {rule_id: 'rr_rr_pt_phys_' + val})
SET r.domain       = 'roman_republic'
  , r.source_type  = 'place_type'
  , r.sc_id        = 'GEO_PHYS_FEATURES'
  , r.match_value  = val
  , r.match_mode   = 'contains'
  , r.rank         = 'primary'
  , r.priority     = 4
WITH r
MATCH (sc:SubjectConcept {subject_id: 'GEO_PHYS_FEATURES'})
MERGE (r)-[:TARGETS]->(sc)
RETURN count(r) AS phys_rules;

// ── Place routes — GEO_ADMIN_DIVISIONS (priority 5) ───────────────────────────
UNWIND ['region', 'province'] AS val
MERGE (r:SYS_RoutingRule {rule_id: 'rr_rr_pt_admin_' + val})
SET r.domain       = 'roman_republic'
  , r.source_type  = 'place_type'
  , r.sc_id        = 'GEO_ADMIN_DIVISIONS'
  , r.match_value  = val
  , r.match_mode   = 'contains'
  , r.rank         = 'primary'
  , r.priority     = 5
WITH r
MATCH (sc:SubjectConcept {subject_id: 'GEO_ADMIN_DIVISIONS'})
MERGE (r)-[:TARGETS]->(sc)
RETURN count(r) AS admin_rules;

// ── Place routes — GEO_POLITICAL_ENTITIES (priority 6) ───────────────────────
MERGE (r:SYS_RoutingRule {rule_id: 'rr_rr_pt_political_people'})
SET r.domain       = 'roman_republic'
  , r.source_type  = 'place_type'
  , r.sc_id        = 'GEO_POLITICAL_ENTITIES'
  , r.match_value  = 'people'
  , r.match_mode   = 'contains'
  , r.rank         = 'primary'
  , r.priority     = 6
WITH r
MATCH (sc:SubjectConcept {subject_id: 'GEO_POLITICAL_ENTITIES'})
MERGE (r)-[:TARGETS]->(sc)
RETURN count(r) AS political_rules;

// ── Place routes — GEO_GENERAL catch-all (priority 99) ───────────────────────
MERGE (r:SYS_RoutingRule {rule_id: 'rr_rr_pt_general_catchall'})
SET r.domain       = 'roman_republic'
  , r.source_type  = 'place_type'
  , r.sc_id        = 'GEO_GENERAL'
  , r.match_value  = '*'
  , r.match_mode   = 'catch_all'
  , r.rank         = 'inferred'
  , r.priority     = 99
WITH r
MATCH (sc:SubjectConcept {subject_id: 'GEO_GENERAL'})
MERGE (r)-[:TARGETS]->(sc)
RETURN count(r) AS general_rules;

// ── Verify ────────────────────────────────────────────────────────────────────
MATCH (r:SYS_RoutingRule {domain: 'roman_republic'})
RETURN r.source_type AS source_type, r.sc_id AS sc_id,
       count(r) AS rules, min(r.priority) AS priority
ORDER BY source_type, priority, sc_id;
