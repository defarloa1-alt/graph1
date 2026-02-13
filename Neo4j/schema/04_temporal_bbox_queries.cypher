// ============================================================================
// CHRYSTALLUM NEO4J: TEMPORAL BOUNDING-BOX QUERY PATTERNS
// ============================================================================
// File: 04_temporal_bbox_queries.cypher
// Purpose: Canonical overlap/sanity query templates for uncertain dates
// ============================================================================

// ----------------------------------------------------------------------------
// Q1) Events active during a target year (robust overlap logic)
// ----------------------------------------------------------------------------
// Example target year: -44 (44 BCE)
WITH "-0044-01-01" AS target_start, "-0044-12-31" AS target_end
MATCH (e:Event)
WHERE e.start_date_min <= target_end
  AND e.end_date_max >= target_start
RETURN e.label, e.start_date_min, e.start_date_max, e.end_date_min, e.end_date_max
ORDER BY e.start_date_min;

// ----------------------------------------------------------------------------
// Q2) Periods overlapping a target interval
// ----------------------------------------------------------------------------
WITH "-0050-01-01" AS q_start, "-0025-12-31" AS q_end
MATCH (p:Period)
WHERE p.start_date_min <= q_end
  AND p.end_date_max >= q_start
RETURN p.label, p.start_date_min, p.start_date_max, p.end_date_min, p.end_date_max
ORDER BY p.start_date_min;

// ----------------------------------------------------------------------------
// Q3) Human lifespans overlapping a target interval
// ----------------------------------------------------------------------------
WITH "-0100-01-01" AS q_start, "-0040-12-31" AS q_end
MATCH (h:Human)
WHERE h.birth_date_min <= q_end
  AND h.death_date_max >= q_start
RETURN h.name, h.birth_date_min, h.birth_date_max, h.death_date_min, h.death_date_max
ORDER BY h.birth_date_min;

// ----------------------------------------------------------------------------
// Q4) Sanity checks: invalid temporal bounds (should return 0 rows)
// ----------------------------------------------------------------------------
MATCH (e:Event)
WHERE e.start_date_min > e.start_date_max
   OR e.end_date_min > e.end_date_max
RETURN e.label, e.start_date_min, e.start_date_max, e.end_date_min, e.end_date_max;

MATCH (p:Period)
WHERE p.start_date_min > p.start_date_max
   OR p.end_date_min > p.end_date_max
RETURN p.label, p.start_date_min, p.start_date_max, p.end_date_min, p.end_date_max;

MATCH (h:Human)
WHERE h.birth_date_min > h.birth_date_max
   OR h.death_date_min > h.death_date_max
RETURN h.name, h.birth_date_min, h.birth_date_max, h.death_date_min, h.death_date_max;

// ----------------------------------------------------------------------------
// Q5) Alias consistency checks (earliest/latest vs min/max)
// ----------------------------------------------------------------------------
MATCH (p:Period)
WHERE (p.earliest_start IS NOT NULL AND p.start_date_min IS NOT NULL AND p.earliest_start <> p.start_date_min)
   OR (p.latest_start IS NOT NULL AND p.start_date_max IS NOT NULL AND p.latest_start <> p.start_date_max)
   OR (p.earliest_end IS NOT NULL AND p.end_date_min IS NOT NULL AND p.earliest_end <> p.end_date_min)
   OR (p.latest_end IS NOT NULL AND p.end_date_max IS NOT NULL AND p.latest_end <> p.end_date_max)
RETURN p.label, p.earliest_start, p.start_date_min, p.latest_start, p.start_date_max, p.earliest_end, p.end_date_min, p.latest_end, p.end_date_max;

