// ============================================================
// Script 17f — SCOPED_TO edges: DPRR persons → backbone disciplines
// ============================================================
// Wire all DPRR persons (dprr_id IS NOT NULL) to the two backbone
// disciplines that define their scholarly domain:
//   - prosopography (Q783287)  — the discipline that studies them
//   - history of Rome (Q646206) — the historical domain they belong to
//
// SCOPED_TO semantics: "this entity is primary material for this discipline"
// Distinct from FIELD_OF_WORK (Person's own research field, Wikidata P101).
// ============================================================

// ── 1. Person → prosopography ─────────────────────────────────────────────────
MATCH (d:Discipline {qid:'Q783287'})
MATCH (p:Person) WHERE p.dprr_id IS NOT NULL
MERGE (p)-[r:SCOPED_TO]->(d)
SET r.basis      = 'dprr_membership'
  , r.scope      = 'subject_of_study'
  , r.asserted_at = date()
RETURN count(r) AS scoped_to_prosopography;

// ── 2. Person → history of Rome ───────────────────────────────────────────────
MATCH (d:Discipline {qid:'Q646206'})
MATCH (p:Person) WHERE p.dprr_id IS NOT NULL
MERGE (p)-[r:SCOPED_TO]->(d)
SET r.basis      = 'dprr_membership'
  , r.scope      = 'historical_domain'
  , r.asserted_at = date()
RETURN count(r) AS scoped_to_history_of_rome;

// ── 3. Verify ─────────────────────────────────────────────────────────────────
MATCH (p:Person)-[r:SCOPED_TO]->(d:Discipline)
RETURN d.label AS discipline, r.scope AS scope, count(p) AS persons
ORDER BY persons DESC;
