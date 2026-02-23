// ============================================================================
// CHRYSTALLUM NEO4J SCHEMA: SIMPLE INITIALIZATION (Neo4j 5.0+ compatible)
// ============================================================================

// Create Year nodes (-2000 to 2025, skipping year 0)
UNWIND [y IN range(-2000, 2025) WHERE y <> 0] AS year_num
WITH year_num,
     CASE WHEN year_num < 0 THEN (-1 * year_num) ELSE year_num END AS abs_year, 
     CASE WHEN year_num < 0 THEN (-1 * year_num) + ' BCE' ELSE toString(year_num) + ' CE' END AS label
CREATE (y:Year {
  entity_id: 'year_' + toString(abs_year) + (CASE WHEN year_num < 0 THEN '_bce' ELSE '_ce' END),
  year: year_num,
  label: label,
  entity_type: 'Year'
});

// Create Facet Categories (17 facets)
UNWIND [
  'genealogical', 'military', 'political', 'social', 'demographic',
  'diplomatic', 'cultural', 'communication', 'religious', 'intellectual',
  'economic', 'temporal', 'classification', 'spatial', 'technological',
  'organizational', 'patronage'
] AS facet_name
CREATE (fc:FacetCategory {
  key: facet_name,
  label: facet_name,
  entity_type: 'FacetCategory'
});

// Create foundational Places
CREATE (rome:Place {
  entity_id: 'place_rome',
  qid: 'Q220',
  label: 'Rome',
  entity_type: 'Place'
});

CREATE (actium:Place {
  entity_id: 'place_actium',
  qid: 'Q41747',
  label: 'Actium',
  entity_type: 'Place'
});

CREATE (egypt:Place {
  entity_id: 'place_egypt',
  qid: 'Q79',
  label: 'Egypt',
  entity_type: 'Place'
});

// Create foundational Periods
CREATE (republic:Period {
  entity_id: 'period_roman_republic',
  qid: 'Q17167',
  label: 'Roman Republic',
  start: -509,
  entity_type: 'Period'
});

CREATE (empire:Period {
  entity_id: 'period_roman_empire',
  qid: 'Q12544',
  label: 'Roman Empire',
  start: -27,
  entity_type: 'Period'
});

CREATE (early:Period {
  entity_id: 'period_roman_early_rep',
  qid: 'Q9749',
  label: 'Early Roman Republic',
  start: -509,
  entity_type: 'Period'
});

// Create foundational Humans
CREATE (caesar:Human {
  entity_id: 'human_caesar',
  qid: 'Q1048',
  name: 'Julius Caesar',
  birth_year: -100,
  death_year: -44,
  entity_type: 'Human'
});

// Create SubjectConcept anchors
CREATE (scivilwar:SubjectConcept {
  subject_id: 'subject_roman_civil_war',
  label: 'Roman Civil War',
  entity_type: 'SubjectConcept'
});

// Create relationships

// Link Periods to Years
MATCH (p:Period {label: 'Roman Republic'}), (y:Year {year: -509})
CREATE (p)-[:STARTS_IN_YEAR]->(y);

MATCH (p:Period {label: 'Roman Empire'}), (y:Year {year: -27})
CREATE (p)-[:STARTS_IN_YEAR]->(y);

// Link Human to Period
MATCH (h:Human {name: 'Julius Caesar'}), (p:Period {label: 'Roman Republic'})
CREATE (h)-[:PARTICIPATED_IN]->(p);

// Verify initialization
MATCH (y:Year) RETURN count(*) AS year_count;
MATCH (fc:FacetCategory) RETURN count(*) AS facet_count;
MATCH (p:Place) RETURN count(*) AS place_count;
MATCH (per:Period) RETURN count(*) AS period_count;
MATCH (h:Human) RETURN count(*) AS human_count;
