// ============================================================
// Script 18d — Sync entity_count on SubjectConcepts from MEMBER_OF
// Also: route persons to period SCs via floruit_start/end overlap
// ============================================================

// ── 1. Update entity_count from MEMBER_OF edges ──────────────────────────────
MATCH (sc:SubjectConcept)
OPTIONAL MATCH (sc)<-[r:MEMBER_OF]-()
WITH sc, count(r) AS n
SET sc.entity_count = n
  , sc.split_candidate = (n > 12)
RETURN sc.subject_id AS id, sc.entity_count AS entity_count
ORDER BY entity_count DESC;

// ── 2. Wire persons to period SCs via floruit_start/end ──────────────────────
// sc_early_republic  : -509 to -264
// sc_middle_republic : -264 to -133
// sc_late_republic   : -133 to -27
// A person can belong to multiple periods (career spans a boundary).
MATCH (sc:SubjectConcept {subject_id: 'sc_early_republic'})
MATCH (p:Person)
WHERE p.dprr_id IS NOT NULL
  AND p.floruit_start IS NOT NULL
  AND p.floruit_start <= -264
  AND coalesce(p.floruit_end, p.floruit_start) >= -509
MERGE (p)-[r:MEMBER_OF]->(sc)
ON CREATE SET r.source = 'floruit', r.rank = 'primary'
RETURN count(r) AS early_republic_persons;

MATCH (sc:SubjectConcept {subject_id: 'sc_middle_republic'})
MATCH (p:Person)
WHERE p.dprr_id IS NOT NULL
  AND p.floruit_start IS NOT NULL
  AND p.floruit_start <= -133
  AND coalesce(p.floruit_end, p.floruit_start) >= -264
MERGE (p)-[r:MEMBER_OF]->(sc)
ON CREATE SET r.source = 'floruit', r.rank = 'primary'
RETURN count(r) AS middle_republic_persons;

MATCH (sc:SubjectConcept {subject_id: 'sc_late_republic'})
MATCH (p:Person)
WHERE p.dprr_id IS NOT NULL
  AND p.floruit_start IS NOT NULL
  AND p.floruit_start <= -27
  AND coalesce(p.floruit_end, p.floruit_start) >= -133
MERGE (p)-[r:MEMBER_OF]->(sc)
ON CREATE SET r.source = 'floruit', r.rank = 'primary'
RETURN count(r) AS late_republic_persons;

// ── 3. Re-sync entity_count after floruit routing ────────────────────────────
MATCH (sc:SubjectConcept)
WHERE sc.subject_id IN ['sc_early_republic','sc_middle_republic','sc_late_republic']
OPTIONAL MATCH (sc)<-[r:MEMBER_OF]-()
WITH sc, count(r) AS n
SET sc.entity_count = n, sc.split_candidate = (n > 12)
RETURN sc.subject_id AS id, sc.entity_count AS entity_count;
