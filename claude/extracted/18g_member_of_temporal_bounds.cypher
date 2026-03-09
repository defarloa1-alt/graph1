// ============================================================
// Script 18g — Temporal bounds on Person→SC MEMBER_OF edges
// ============================================================
// Adds earliest_year, latest_year, position_count to MEMBER_OF
// edges where source='position_held'.
//
// For each (person)-[mo:MEMBER_OF]->(sc), find all POSITION_HELD
// edges whose position label routes to that SC, then set:
//   mo.earliest_year  = min(ph.year_start)
//   mo.latest_year    = max(ph.year_end)
//   mo.position_count = count of matching positions
//
// Does NOT touch dprr_default, floruit, career_bounds, place_type edges.
// ============================================================

// ── sc_constitution ───────────────────────────────────────────────────────────
MATCH (p:Person)-[mo:MEMBER_OF]->(sc:SubjectConcept {subject_id: 'sc_constitution'})
WHERE mo.source = 'position_held'
MATCH (p)-[ph:POSITION_HELD]->(pos:Position)
WHERE pos.label IN [
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
  ]
  AND ph.year_start IS NOT NULL
WITH mo, min(ph.year_start) AS ey, max(ph.year_end) AS ly, count(ph) AS pc
SET mo.earliest_year  = ey
  , mo.latest_year    = ly
  , mo.position_count = pc
RETURN count(mo) AS sc_constitution_edges_enriched;

// ── sc_military ───────────────────────────────────────────────────────────────
MATCH (p:Person)-[mo:MEMBER_OF]->(sc:SubjectConcept {subject_id: 'sc_military'})
WHERE mo.source = 'position_held'
MATCH (p)-[ph:POSITION_HELD]->(pos:Position)
WHERE pos.label IN [
    'tribunus militum', 'legatus (lieutenant)',
    'triumphator', 'praefectus', 'promagistrate',
    'proconsul', 'propraetor', 'magister equitum',
    'officer (title not preserved)'
  ]
  AND ph.year_start IS NOT NULL
WITH mo, min(ph.year_start) AS ey, max(ph.year_end) AS ly, count(ph) AS pc
SET mo.earliest_year  = ey
  , mo.latest_year    = ly
  , mo.position_count = pc
RETURN count(mo) AS sc_military_edges_enriched;

// ── sc_religion ───────────────────────────────────────────────────────────────
MATCH (p:Person)-[mo:MEMBER_OF]->(sc:SubjectConcept {subject_id: 'sc_religion'})
WHERE mo.source = 'position_held'
MATCH (p)-[ph:POSITION_HELD]->(pos:Position)
WHERE pos.label IN [
    'augur', 'pontifex', 'pontifex maximus',
    'flamen Martialis', 'decemvir sacris faciundis'
  ]
  AND ph.year_start IS NOT NULL
WITH mo, min(ph.year_start) AS ey, max(ph.year_end) AS ly, count(ph) AS pc
SET mo.earliest_year  = ey
  , mo.latest_year    = ly
  , mo.position_count = pc
RETURN count(mo) AS sc_religion_edges_enriched;

// ── sc_diplomacy ──────────────────────────────────────────────────────────────
MATCH (p:Person)-[mo:MEMBER_OF]->(sc:SubjectConcept {subject_id: 'sc_diplomacy'})
WHERE mo.source = 'position_held'
MATCH (p)-[ph:POSITION_HELD]->(pos:Position)
WHERE pos.label IN [
    'legatus (ambassador)', 'legatus (envoy)'
  ]
  AND ph.year_start IS NOT NULL
WITH mo, min(ph.year_start) AS ey, max(ph.year_end) AS ly, count(ph) AS pc
SET mo.earliest_year  = ey
  , mo.latest_year    = ly
  , mo.position_count = pc
RETURN count(mo) AS sc_diplomacy_edges_enriched;

// ── sc_economy ────────────────────────────────────────────────────────────────
MATCH (p:Person)-[mo:MEMBER_OF]->(sc:SubjectConcept {subject_id: 'sc_economy'})
WHERE mo.source = 'position_held'
MATCH (p)-[ph:POSITION_HELD]->(pos:Position)
WHERE pos.label IN ['monetalis', 'moneyer']
  AND ph.year_start IS NOT NULL
WITH mo, min(ph.year_start) AS ey, max(ph.year_end) AS ly, count(ph) AS pc
SET mo.earliest_year  = ey
  , mo.latest_year    = ly
  , mo.position_count = pc
RETURN count(mo) AS sc_economy_edges_enriched;

// ── Verify Sulla's enriched edges ─────────────────────────────────────────────
MATCH (p:Person {entity_id: 'person_q483783'})-[mo:MEMBER_OF]->(sc:SubjectConcept)
RETURN sc.subject_id          AS subject_concept
     , mo.source               AS source
     , mo.rank                 AS rank
     , mo.earliest_year        AS earliest_year
     , mo.latest_year          AS latest_year
     , mo.position_count       AS position_count
ORDER BY mo.source, sc.subject_id;
