// ============================================================
// Script 17g — SCOPED_TO + IN_PERIOD edges for Place nodes
// ============================================================
// Wire Pleiades places to backbone disciplines (geo dimension)
// and to the Roman Republic period node where temporally active.
//
// Candidacy rules:
//   SCOPED_TO: all places with pleiades_id (42,065)
//     → archaeology (Q23498)  — Pleiades is an archaeological gazetteer
//     → topography (Q134435)  — Pleiades is a historical topography source
//   IN_PERIOD: places where min_date <= -27 AND max_date >= -509
//     i.e. active during any part of the Roman Republic span (32,565)
//
// Note: classical archaeology and ancient history are not yet in the
// discipline set. archaeology + topography are the correct available
// anchors. Add classical archaeology (Q184128) when it is loaded.
// ============================================================

// ── 1. Place → archaeology ────────────────────────────────────────────────────
MATCH (d:Discipline {qid:'Q23498'})
MATCH (p:Place) WHERE p.pleiades_id IS NOT NULL
MERGE (p)-[r:SCOPED_TO]->(d)
SET r.basis       = 'pleiades_membership'
  , r.scope       = 'subject_of_study'
  , r.asserted_at = date()
RETURN count(r) AS scoped_to_archaeology;

// ── 2. Place → topography ─────────────────────────────────────────────────────
MATCH (d:Discipline {qid:'Q134435'})
MATCH (p:Place) WHERE p.pleiades_id IS NOT NULL
MERGE (p)-[r:SCOPED_TO]->(d)
SET r.basis       = 'pleiades_membership'
  , r.scope       = 'subject_of_study'
  , r.asserted_at = date()
RETURN count(r) AS scoped_to_topography;

// ── 3. Place → IN_PERIOD → Roman Republic ─────────────────────────────────────
// Overlap rule: place was active (min_date <= period.end AND max_date >= period.start)
MATCH (rr:Period {qid:'Q17167'})
MATCH (p:Place)
WHERE p.pleiades_id IS NOT NULL
  AND p.min_date <= -27
  AND p.max_date >= -509
MERGE (p)-[r:IN_PERIOD]->(rr)
SET r.min_date    = p.min_date
  , r.max_date    = p.max_date
  , r.basis       = 'pleiades_date_overlap'
  , r.asserted_at = date()
RETURN count(r) AS places_in_period;

// ── 4. Verify ─────────────────────────────────────────────────────────────────
MATCH (p:Place)-[r:SCOPED_TO]->(d:Discipline)
RETURN d.label AS discipline, count(p) AS places ORDER BY places DESC;

MATCH (rr:Period {qid:'Q17167'})
OPTIONAL MATCH (p:Place)-[:IN_PERIOD]->(rr)
OPTIONAL MATCH (pe:Person)-[:IN_PERIOD]->(rr)
RETURN rr.label AS period, count(DISTINCT p) AS places, count(DISTINCT pe) AS persons;
