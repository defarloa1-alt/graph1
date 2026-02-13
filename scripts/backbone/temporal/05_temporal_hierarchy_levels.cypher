// ============================================================================
// CHRYSTALLUM NEO4J SCHEMA: TEMPORAL GRANULARITY HIERARCHY
// ============================================================================
// File: 05_temporal_hierarchy_levels.cypher
// Purpose: Add Decade/Century/Millennium nodes and PART_OF hierarchy links
// Created: 2026-02-13
// Status: Migration-safe (non-destructive by default)
//
// Canonical pattern:
//   Year -[:PART_OF]-> Decade -[:PART_OF]-> Century -[:PART_OF]-> Millennium
//   FOLLOWED_BY is the canonical sequential edge.
// ============================================================================

// ----------------------------------------------------------------------------
// 0) Normalize Year numeric key (compat with older year_value property)
// ----------------------------------------------------------------------------
MATCH (y:Year)
WHERE y.year IS NULL AND y.year_value IS NOT NULL
SET y.year = y.year_value;

// ----------------------------------------------------------------------------
// 1) Constraints and indexes
// ----------------------------------------------------------------------------
CREATE CONSTRAINT decade_start_unique IF NOT EXISTS
FOR (d:Decade) REQUIRE d.start_year IS UNIQUE;

CREATE CONSTRAINT century_start_unique IF NOT EXISTS
FOR (c:Century) REQUIRE c.start_year IS UNIQUE;

CREATE CONSTRAINT millennium_start_unique IF NOT EXISTS
FOR (m:Millennium) REQUIRE m.start_year IS UNIQUE;

CREATE INDEX decade_label_index IF NOT EXISTS
FOR (d:Decade) ON (d.label);

CREATE INDEX century_label_index IF NOT EXISTS
FOR (c:Century) ON (c.label);

CREATE INDEX millennium_label_index IF NOT EXISTS
FOR (m:Millennium) ON (m.label);

// ----------------------------------------------------------------------------
// 2) Create Decade nodes from Year range
// ----------------------------------------------------------------------------
MATCH (y:Year)
WITH DISTINCT toInteger(floor(toFloat(y.year) / 10.0) * 10) AS start_year
MERGE (d:Decade {start_year: start_year})
SET d.end_year = start_year + 9,
    d.entity_type = 'Decade',
    d.era = CASE WHEN start_year < 0 THEN 'BCE' ELSE 'CE' END,
    d.range_label = toString(start_year) + ' to ' + toString(start_year + 9),
    d.label = CASE
        WHEN start_year < 0 THEN toString(abs(start_year)) + 's BCE'
        ELSE toString(start_year) + 's CE'
    END;

// ----------------------------------------------------------------------------
// 3) Create Century nodes from Year range
// ----------------------------------------------------------------------------
MATCH (y:Year)
WITH DISTINCT toInteger(floor(toFloat(y.year) / 100.0) * 100) AS start_year
MERGE (c:Century {start_year: start_year})
WITH c, start_year, (start_year + 99) AS end_year,
     CASE
         WHEN start_year < 0 THEN toInteger(abs(start_year) / 100)
         ELSE toInteger(start_year / 100) + 1
     END AS ordinal_num,
     CASE WHEN start_year < 0 THEN 'BCE' ELSE 'CE' END AS era
SET c.end_year = end_year,
    c.entity_type = 'Century',
    c.era = era,
    c.ordinal = ordinal_num,
    c.range_label = toString(start_year) + ' to ' + toString(end_year),
    c.label = toString(ordinal_num) +
        CASE
            WHEN ordinal_num % 100 IN [11, 12, 13] THEN 'th'
            WHEN ordinal_num % 10 = 1 THEN 'st'
            WHEN ordinal_num % 10 = 2 THEN 'nd'
            WHEN ordinal_num % 10 = 3 THEN 'rd'
            ELSE 'th'
        END +
        ' Century ' + era;

// ----------------------------------------------------------------------------
// 4) Create Millennium nodes from Year range
// ----------------------------------------------------------------------------
MATCH (y:Year)
WITH DISTINCT toInteger(floor(toFloat(y.year) / 1000.0) * 1000) AS start_year
MERGE (m:Millennium {start_year: start_year})
WITH m, start_year, (start_year + 999) AS end_year,
     CASE
         WHEN start_year < 0 THEN toInteger(abs(start_year) / 1000)
         ELSE toInteger(start_year / 1000) + 1
     END AS ordinal_num,
     CASE WHEN start_year < 0 THEN 'BCE' ELSE 'CE' END AS era
SET m.end_year = end_year,
    m.entity_type = 'Millennium',
    m.era = era,
    m.ordinal = ordinal_num,
    m.range_label = toString(start_year) + ' to ' + toString(end_year),
    m.label = toString(ordinal_num) +
        CASE
            WHEN ordinal_num % 100 IN [11, 12, 13] THEN 'th'
            WHEN ordinal_num % 10 = 1 THEN 'st'
            WHEN ordinal_num % 10 = 2 THEN 'nd'
            WHEN ordinal_num % 10 = 3 THEN 'rd'
            ELSE 'th'
        END +
        ' Millennium ' + era;

// ----------------------------------------------------------------------------
// 5) Wire PART_OF hierarchy
// ----------------------------------------------------------------------------
MATCH (y:Year)
WITH y, toInteger(floor(toFloat(y.year) / 10.0) * 10) AS decade_start
MATCH (d:Decade {start_year: decade_start})
MERGE (y)-[:PART_OF]->(d);

MATCH (d:Decade)
WITH d, toInteger(floor(toFloat(d.start_year) / 100.0) * 100) AS century_start
MATCH (c:Century {start_year: century_start})
MERGE (d)-[:PART_OF]->(c);

MATCH (c:Century)
WITH c, toInteger(floor(toFloat(c.start_year) / 1000.0) * 1000) AS millennium_start
MATCH (m:Millennium {start_year: millennium_start})
MERGE (c)-[:PART_OF]->(m);

// ----------------------------------------------------------------------------
// 6) Sequential edges at each granularity (FOLLOWED_BY only)
// ----------------------------------------------------------------------------
MATCH (a:Decade), (b:Decade)
WHERE b.start_year = a.start_year + 10
MERGE (a)-[:FOLLOWED_BY]->(b);

MATCH (a:Century), (b:Century)
WHERE b.start_year = a.start_year + 100
MERGE (a)-[:FOLLOWED_BY]->(b);

MATCH (a:Millennium), (b:Millennium)
WHERE b.start_year = a.start_year + 1000
MERGE (a)-[:FOLLOWED_BY]->(b);

// ----------------------------------------------------------------------------
// 7) Verification
// ----------------------------------------------------------------------------
MATCH (y:Year) RETURN count(y) AS years;
MATCH (d:Decade) RETURN count(d) AS decades;
MATCH (c:Century) RETURN count(c) AS centuries;
MATCH (m:Millennium) RETURN count(m) AS millennia;

MATCH (:Year)-[r:PART_OF]->(:Decade) RETURN count(r) AS year_to_decade_links;
MATCH (:Decade)-[r:PART_OF]->(:Century) RETURN count(r) AS decade_to_century_links;
MATCH (:Century)-[r:PART_OF]->(:Millennium) RETURN count(r) AS century_to_millennium_links;
