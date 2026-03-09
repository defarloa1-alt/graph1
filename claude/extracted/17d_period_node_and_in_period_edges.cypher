// ============================================================
// Script 17d — Period node upgrade + IN_PERIOD edge build
// ============================================================
// 1. Upgrade Roman Republic HistoricalPolity → add :Period label + date bounds
// 2. Flag 385 no-dprr_id Person nodes as out_of_domain
// 3. Build IN_PERIOD edges from DPRR persons via floruit_start/end
// ============================================================

// ── 1. Upgrade Roman Republic node ────────────────────────────────────────────
// Add :Period label and date boundaries to the existing Q17167 node.
// Canonical span: -509 (expulsion of kings) to -27 (Augustus becomes emperor).
// DPRR floruit range is -509 to -13 — Period spans slightly wider to cover
// transitional figures active through end of Republic.
MATCH (rr:HistoricalPolity {qid: 'Q17167'})
SET rr:Period
  , rr.start        = -509
  , rr.end          = -27
  , rr.period_label = 'Roman Republic'
  , rr.period_note  = 'Traditional: -509 (Tarquin expelled) to -27 (Augustus). DPRR coverage -509 to -13.'
RETURN rr.label AS label, labels(rr) AS labels, rr.start AS start, rr.end AS end;

// ── 2. Flag out-of-domain persons ─────────────────────────────────────────────
// 385 Person nodes have qid but no dprr_id — modern politicians, 19th/20th c.
// scholars, mythological figures. They came from over-broad Wikidata backlink
// queries. Mark them; do not delete (preserve qid reference integrity).
MATCH (p:Person)
WHERE p.dprr_id IS NULL
  AND p.source IS NULL
  AND p.qid IS NOT NULL
SET p.in_domain       = false
  , p.scoping_status  = 'out_of_domain'
  , p.scoping_note    = 'No dprr_id — entered via over-broad Wikidata backlink harvest. Not Roman Republic prosopography.'
RETURN count(p) AS flagged_out_of_domain;

// ── 3. Build IN_PERIOD edges ───────────────────────────────────────────────────
// Wire all DPRR persons (floruit_start known, in Republic range) to
// the Roman Republic Period node.
// Candidacy rule:
//   floruit_start IS NOT NULL  — DPRR-derived, reliable
//   floruit_start >= -509      — within or after Republic founding
//   floruit_start <= 0         — clearly BCE (excludes contamination)
// Edge properties record the floruit span used to assert candidacy.
MATCH (rr:Period {qid: 'Q17167'})
MATCH (p:Person)
WHERE p.floruit_start IS NOT NULL
  AND p.floruit_start >= -509
  AND p.floruit_start <= 0
MERGE (p)-[r:IN_PERIOD]->(rr)
SET r.floruit_start = p.floruit_start
  , r.floruit_end   = p.floruit_end
  , r.basis         = 'dprr_floruit'
  , r.asserted_at   = date()
RETURN count(r) AS in_period_edges_written;

// ── 4. Verify ─────────────────────────────────────────────────────────────────
MATCH (rr:Period {qid: 'Q17167'})
OPTIONAL MATCH (p:Person)-[:IN_PERIOD]->(rr)
RETURN rr.label AS period
     , rr.start_year AS start_year
     , rr.end_year AS end_year
     , count(p) AS persons_in_period;

MATCH (p:Person)
RETURN p.in_domain AS in_domain, p.scoping_status AS status, count(p) AS n
ORDER BY n DESC;
