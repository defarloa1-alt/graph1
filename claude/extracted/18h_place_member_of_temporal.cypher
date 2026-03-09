// ============================================================
// Script 18h — Temporal bounds on Place→SC MEMBER_OF edges
// ============================================================
// Pleiades places carry min_date / max_date (BCE = negative).
// Propagate these onto the MEMBER_OF edge so the edge itself
// is time-bounded — consistent with Person→SC temporal enrichment.
//
// Applies to all place_type and place_type_default MEMBER_OF edges.
// Places without min_date/max_date: leave earliest_year/latest_year null.
// ============================================================

MATCH (pl:Place)-[mo:MEMBER_OF]->(:SubjectConcept)
WHERE mo.source IN ['place_type', 'place_type_default']
  AND pl.min_date IS NOT NULL
SET mo.earliest_year = pl.min_date
  , mo.latest_year   = pl.max_date
RETURN count(mo) AS place_edges_enriched;

// ── Verify: sample a few enriched edges ──────────────────────────────────────
MATCH (pl:Place)-[mo:MEMBER_OF]->(sc:SubjectConcept)
WHERE mo.earliest_year IS NOT NULL
  AND mo.source IN ['place_type', 'place_type_default']
RETURN pl.label AS place, sc.subject_id AS sc
     , mo.earliest_year AS earliest, mo.latest_year AS latest
ORDER BY mo.earliest_year
LIMIT 10;
