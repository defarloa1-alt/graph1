// ============================================================
// Script 17e — Fix DPRR ROUTES_TO discipline edges
// ============================================================
// Problem: 50 Discipline→DPRR edges from wire_discipline_federation_scope.py
//   used loose keyword/pattern matching. All 50 have identical scope_basis.
//   48 are wrong (Canadian studies, Chinese historiography, military history,
//   etc.). Only 2 are legitimate (history of Rome, classical philology).
//   Prosopography — the most critical — is missing entirely.
//
// Fix:
//   1. Delete all 50 existing Discipline→DPRR edges
//   2. Create 3 correct edges with precise scope_basis values:
//      - prosopography (Q783287)  — DPRR is a prosopographic database
//      - history of Rome (Q646206) — primary domain
//      - classical philology (Q495527) — Latin primary source analysis
// ============================================================

// ── 1. Delete all stale ROUTES_TO dprr edges ──────────────────────────────────
MATCH (d:Discipline)-[r:ROUTES_TO]->(fs:SYS_FederationSource {source_id:'dprr'})
DELETE r
RETURN count(*) AS deleted;

// ── 2. Wire prosopography → DPRR ──────────────────────────────────────────────
MATCH (d:Discipline {qid:'Q783287'})
MATCH (fs:SYS_FederationSource {source_id:'dprr'})
MERGE (d)-[r:ROUTES_TO]->(fs)
SET r.scope_basis    = 'domain_primary'
  , r.query_mode     = 'entity_lookup'
  , r.corpus_capable = true
  , r.note           = 'DPRR is a prosopographic database — direct domain match. SFA queries by person name or dprr_id.'
RETURN d.label AS discipline, r.scope_basis AS basis;

// ── 3. Wire history of Rome → DPRR ────────────────────────────────────────────
MATCH (d:Discipline {qid:'Q646206'})
MATCH (fs:SYS_FederationSource {source_id:'dprr'})
MERGE (d)-[r:ROUTES_TO]->(fs)
SET r.scope_basis    = 'domain_primary'
  , r.query_mode     = 'entity_lookup'
  , r.corpus_capable = true
  , r.note           = 'DPRR persons, offices and political careers are primary source material for Roman history.'
RETURN d.label AS discipline, r.scope_basis AS basis;

// ── 4. Wire classical philology → DPRR ────────────────────────────────────────
MATCH (d:Discipline {qid:'Q495527'})
MATCH (fs:SYS_FederationSource {source_id:'dprr'})
MERGE (d)-[r:ROUTES_TO]->(fs)
SET r.scope_basis    = 'domain_adjacent'
  , r.query_mode     = 'entity_lookup'
  , r.corpus_capable = true
  , r.note           = 'Classical philology uses DPRR as authority for Latin text attributions, magistrate dating, and office identification.'
RETURN d.label AS discipline, r.scope_basis AS basis;

// ── 5. Verify ─────────────────────────────────────────────────────────────────
MATCH (d:Discipline)-[r:ROUTES_TO]->(fs:SYS_FederationSource {source_id:'dprr'})
RETURN d.label AS discipline, r.scope_basis AS basis, r.note AS note
ORDER BY r.scope_basis;
