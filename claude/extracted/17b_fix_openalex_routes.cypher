// ============================================================
// Script 17b — Fix stale universal ROUTES_TO open_alex edges
// ============================================================
// Problem: 259 no_id disciplines have ROUTES_TO open_alex with
//   scope_basis='universal' from prior wiring. No concept_id on
//   the node means an SFA can't know what to query.
//
// Fix:
//   1. 231 have lcsh_id → set query_mode='lcsh_fallback', corpus_capable=true
//   2. 28 have neither  → DELETE the edge (pure noise, no query possible)
// ============================================================

// ── 1. Mark lcsh-fallback edges ───────────────────────────────────────────────
MATCH (d:Discipline)-[r:ROUTES_TO]->(oa:SYS_FederationSource {source_id:'open_alex'})
WHERE r.scope_basis = 'universal'
  AND d.openalex_status = 'no_id'
  AND d.lcsh_id IS NOT NULL
SET r.scope_basis    = 'lcsh_fallback'
  , r.query_mode     = 'lcsh'
  , r.corpus_capable = true
  , r.note           = 'No openalex_id; SFA must query OpenAlex via lcsh_id subject filter'
RETURN count(r) AS lcsh_fallback_marked;

// ── 2. Delete noise edges (no concept_id AND no lcsh_id) ─────────────────────
MATCH (d:Discipline)-[r:ROUTES_TO]->(oa:SYS_FederationSource {source_id:'open_alex'})
WHERE r.scope_basis = 'universal'
  AND d.openalex_status = 'no_id'
  AND d.lcsh_id IS NULL
DELETE r
RETURN count(*) AS noise_edges_deleted;

// ── 3. Verify final ROUTES_TO open_alex breakdown ────────────────────────────
MATCH (d:Discipline)-[r:ROUTES_TO]->(oa:SYS_FederationSource {source_id:'open_alex'})
RETURN r.scope_basis AS scope_basis, r.query_mode AS query_mode,
       count(d) AS disciplines
ORDER BY count(d) DESC;
