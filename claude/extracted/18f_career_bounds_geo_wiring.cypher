// ============================================================
// Script 18f — Career bounds backfill + BORN_IN geo wiring
// ============================================================
// Fixes identified via Sulla reality test (2026-03-09):
//
//  1. career_start/career_end from POSITION_HELD min/max year_start/year_end
//     — floruit is DPRR's "peak prominence" estimate, NOT career bounds
//     — Sulla floruit: -100 to -98 | career: -107 to -78 (13x more precise)
//
//  2. BORN_IN → Place edge from birth_place_qid property
//     — 1,635 DPRR persons have birth_place_qid; ~N match a Place node
//     — gives Person → geo backbone connection
//
//  3. Re-route period SCs using career_start (preferred over floruit_start)
//     — career_start derived from attested positions, not estimate
//     — run AFTER step 1 so career_start is populated
// ============================================================

// ── 1. Backfill career_start / career_end from POSITION_HELD ─────────────────
MATCH (p:Person)-[ph:POSITION_HELD]->(:Position)
WHERE p.dprr_id IS NOT NULL
  AND ph.year_start IS NOT NULL
WITH p, min(ph.year_start) AS cs, max(ph.year_end) AS ce
SET p.career_start = cs
  , p.career_end   = ce
RETURN count(p) AS persons_updated
     , min(cs) AS earliest_career
     , max(ce) AS latest_career;

// ── 2. BORN_IN → Place from birth_place_qid ──────────────────────────────────
// Only wire where a matching Place node exists in graph.
// ON CREATE only — do not overwrite if edge already exists.
MATCH (p:Person)
WHERE p.dprr_id IS NOT NULL
  AND p.birth_place_qid IS NOT NULL
MATCH (pl:Place {qid: p.birth_place_qid})
MERGE (p)-[r:BORN_IN]->(pl)
ON CREATE SET r.source = 'wikidata_p19', r.created_at = date()
RETURN count(r) AS born_in_edges_created;

// ── 3. Re-route period SCs using career_start (better temporal signal) ────────
// Removes old floruit-based edges and re-creates with career_start.
// A person may span multiple periods — allow multiple MEMBER_OF period SCs.
//
// sc_early_republic  : career active any part of -509 to -264
MATCH (sc:SubjectConcept {subject_id: 'sc_early_republic'})
MATCH (p:Person)
WHERE p.dprr_id IS NOT NULL
  AND p.career_start IS NOT NULL
  AND p.career_start <= -264
  AND coalesce(p.career_end, p.career_start) >= -509
MERGE (p)-[r:MEMBER_OF]->(sc)
ON CREATE SET r.source = 'career_bounds', r.rank = 'primary'
ON MATCH  SET r.source = 'career_bounds'
RETURN count(r) AS early_republic;

// sc_middle_republic : career active any part of -264 to -133
MATCH (sc:SubjectConcept {subject_id: 'sc_middle_republic'})
MATCH (p:Person)
WHERE p.dprr_id IS NOT NULL
  AND p.career_start IS NOT NULL
  AND p.career_start <= -133
  AND coalesce(p.career_end, p.career_start) >= -264
MERGE (p)-[r:MEMBER_OF]->(sc)
ON CREATE SET r.source = 'career_bounds', r.rank = 'primary'
ON MATCH  SET r.source = 'career_bounds'
RETURN count(r) AS middle_republic;

// sc_late_republic   : career active any part of -133 to -27
MATCH (sc:SubjectConcept {subject_id: 'sc_late_republic'})
MATCH (p:Person)
WHERE p.dprr_id IS NOT NULL
  AND p.career_start IS NOT NULL
  AND p.career_start <= -27
  AND coalesce(p.career_end, p.career_start) >= -133
MERGE (p)-[r:MEMBER_OF]->(sc)
ON CREATE SET r.source = 'career_bounds', r.rank = 'primary'
ON MATCH  SET r.source = 'career_bounds'
RETURN count(r) AS late_republic;

// ── 4. Verify Sulla ───────────────────────────────────────────────────────────
MATCH (p:Person {entity_id: 'person_q483783'})
OPTIONAL MATCH (p)-[:BORN_IN]->(pl:Place)
OPTIONAL MATCH (p)-[mo:MEMBER_OF]->(sc:SubjectConcept)
RETURN p.label AS person
     , p.career_start AS career_start
     , p.career_end AS career_end
     , p.floruit_start AS floruit_start
     , p.floruit_end AS floruit_end
     , pl.label AS born_in
     , collect(DISTINCT sc.subject_id + '(' + mo.source + ')') AS member_of;
