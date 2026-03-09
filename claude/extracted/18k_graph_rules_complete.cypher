// ============================================================
// Script 18k — Complete rules-in-graph: domain_default + PIDs
// ============================================================
// Removes last hardcoded rules from Python/Cypher:
//
// 1. SYS_RoutingRule domain_default → sc_constitution
//    (was hardcoded in wire_person_default())
//
// 2. SYS_WikidataProperty P1566 + P131
//    (was hardcoded in qid_resolver.py)
//
// 3. Period SC routing rewritten to read period_start/period_end
//    from SubjectConcept nodes — no hardcoded dates anywhere.
//    (period_start/period_end already confirmed on all 3 period SCs)
// ============================================================

// ── 1. domain_default SYS_RoutingRule ────────────────────────────────────────
MERGE (r:SYS_RoutingRule {rule_id: 'rr_rr_person_domain_default'})
SET r.domain       = 'roman_republic'
  , r.source_type  = 'person'
  , r.sc_id        = 'sc_constitution'
  , r.match_value  = '*'
  , r.match_mode   = 'domain_default'
  , r.rank         = 'inferred'
  , r.priority     = 99
WITH r
MATCH (sc:SubjectConcept {subject_id: 'sc_constitution'})
MERGE (r)-[:TARGETS]->(sc)
RETURN count(r) AS domain_default_rule;

// ── 2. SYS_WikidataProperty — P1566 (Pleiades ID) ────────────────────────────
MERGE (w:SYS_WikidataProperty {pid: 'P1566'})
SET w.label         = 'Pleiades ID'
  , w.semantic_role = 'GEO_AUTHORITY_ID'
  , w.usage         = 'qid_resolver: strategy 2 — direct Pleiades lookup on stub QID'
RETURN w.pid AS pid, w.label AS label;

// ── 3. SYS_WikidataProperty — P131 (located in) ──────────────────────────────
MERGE (w:SYS_WikidataProperty {pid: 'P131'})
SET w.label         = 'located in the administrative territorial entity'
  , w.semantic_role = 'GEO_CONTAINMENT'
  , w.usage         = 'qid_resolver: strategy 3 — walk up to parent, then check P1566'
RETURN w.pid AS pid, w.label AS label;

// ── 4. Period SC routing — data-driven (reads period_start/period_end) ────────
// Replaces hardcoded date ranges in 18d + 18f.
// Any SC with period_start/period_end gets career_bounds routing applied.
// A person can span multiple periods — MERGE allows multiple MEMBER_OF edges.
MATCH (sc:SubjectConcept)
WHERE sc.period_start IS NOT NULL
  AND sc.period_end   IS NOT NULL
MATCH (p:Person)
WHERE p.dprr_id IS NOT NULL
  AND p.career_start IS NOT NULL
  AND p.career_start <= sc.period_end
  AND coalesce(p.career_end, p.career_start) >= sc.period_start
MERGE (p)-[r:MEMBER_OF]->(sc)
ON CREATE SET r.source = 'career_bounds', r.rank = 'primary'
ON MATCH  SET r.source = 'career_bounds'
RETURN sc.subject_id AS subject_id, sc.period_start AS period_start, count(r) AS members
ORDER BY sc.period_start;

// ── 5. Verify all rule types now in graph ─────────────────────────────────────
MATCH (r:SYS_RoutingRule {domain: 'roman_republic'})
RETURN r.match_mode AS match_mode, count(r) AS rules
ORDER BY rules DESC;
