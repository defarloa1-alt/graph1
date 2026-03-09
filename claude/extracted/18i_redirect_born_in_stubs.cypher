// ============================================================
// Script 18i — Redirect BORN_IN stub places → Pleiades nodes
// ============================================================
// Problem: 1,499 persons born in "Ancient Rome" (Q1747689) —
// a Wikidata conceptual entity with no Pleiades data.
// Real node: Roma (Q220, Pleiades 423025, min_date=-750).
//
// Strategy: for known QID redirects, delete old BORN_IN edge
// and MERGE a new one pointing to the canonical Pleiades place.
// Preserves all other edges on the stub nodes (they may be
// referenced elsewhere).
// ============================================================

// ── 1. Q1747689 "Ancient Rome" → Q220 "Roma" (Pleiades 423025) ───────────────
MATCH (p:Person)-[old:BORN_IN]->(stub:Place {qid: 'Q1747689'})
MATCH (canonical:Place {qid: 'Q220'})
MERGE (p)-[r:BORN_IN]->(canonical)
  ON CREATE SET r.source = old.source
             , r.created_at = old.created_at
             , r.redirected_from = 'Q1747689'
DELETE old
RETURN count(r) AS redirected_ancient_rome;

// ── 2. Verify Roma now has the connections ─────────────────────────────────────
MATCH (pl:Place {qid: 'Q220'})
OPTIONAL MATCH (pl)<-[:BORN_IN]-(p:Person)
OPTIONAL MATCH (pl)-[:MEMBER_OF]->(sc:SubjectConcept)
RETURN pl.label AS place, pl.pleiades_id AS pleiades
     , pl.place_type AS place_type
     , pl.min_date AS min_date, pl.max_date AS max_date
     , count(DISTINCT p) AS born_in_count
     , collect(DISTINCT sc.subject_id) AS geo_subjects;

// ── 3. Remaining stubs — places with BORN_IN but no pleiades_id ───────────────
MATCH (p:Person)-[:BORN_IN]->(pl:Place)
WHERE pl.pleiades_id IS NULL
RETURN pl.label AS place, pl.qid AS qid, count(p) AS persons
ORDER BY persons DESC;
