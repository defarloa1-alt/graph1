// Link Person to Year backbone via ACTIVE_IN_YEAR (derived from POSITION_HELD years)
// Run after: enrich_position_held_temporal (so r.start_year, r.end_year exist)
// Idempotent: MERGE so re-run is safe

// 1. Create ACTIVE_IN_YEAR for each year in each position's range
// Uses r.start_year, r.end_year, or r.year fallback
// Matches any node with POSITION_HELD (Person or Entity)
MATCH (p)-[r:POSITION_HELD]->()
WITH p, r,
     coalesce(r.start_year, toInteger(r.year)) AS start_yr,
     coalesce(r.end_year, r.start_year, toInteger(r.year)) AS end_yr
WHERE start_yr IS NOT NULL
WITH p, start_yr, coalesce(end_yr, start_yr) AS end_yr
WITH p, start_yr, end_yr, range(min(start_yr, end_yr), max(start_yr, end_yr)) AS years
UNWIND years AS yr
MATCH (y:Year {year: yr})
MERGE (p)-[:ACTIVE_IN_YEAR {source: 'position_held'}]->(y)
RETURN count(*) AS active_in_year_edges;
