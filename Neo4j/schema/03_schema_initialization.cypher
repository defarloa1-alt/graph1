// ============================================================================
// CHRYSTALLUM NEO4J SCHEMA: INITIALIZATION & BACKBONE CREATION
// ============================================================================
// File: 03_schema_initialization.cypher
// Purpose: Initialize Year backbone, foundational nodes, and basic entities
// Created: 2026-02-13
// Status: Production Schema - Run once to bootstrap database
// ============================================================================

// ============================================================================
// YEAR BACKBONE INITIALIZATION
// ============================================================================
// Creates continuous linked list of Year nodes from -2000 to 2025
// Critical for all temporal reasoning in Chrystallum
// This is a FOUNDATIONAL OPERATION - run only once
// ============================================================================

// Create Year nodes with forward linkage (FOLLOWED_BY)
// Using UNWIND to batch create 4025 nodes efficiently
UNWIND range(-2000, 2025) AS year_num
WITH year_num,
     toString(abs(year_num)) AS abs_year,
     CASE WHEN year_num < 0 THEN '-' + toString(abs_year) ELSE toString(year_num) END AS iso_year,
     CASE WHEN year_num < 0 THEN toString(abs_year) + ' BCE' ELSE toString(year_num) + ' CE' END AS label
CREATE (y:Year {
  entity_id: 'year_' + iso_year,
  year: year_num,
  iso: iso_year,
  label: label,
  entity_type: 'Year'
})
WITH collect(y) AS years
// Link years sequentially using apoc (if available) or manual linking
// For small sequential operations, use FOREACH
UNWIND range(0, size(years)-2) AS idx
WITH years[idx] AS current, years[idx+1] AS next
CREATE (current)-[:FOLLOWED_BY]->(next)
CREATE (next)-[:PRECEDED_BY]->(current)

// Note: If apoc is not available, use this alternative:
// MATCH (y1:Year), (y2:Year)
// WHERE y1.year + 1 = y2.year
// CREATE (y1)-[:FOLLOWED_BY]->(y2);

// Verify Year backbone creation
MATCH (y:Year) 
RETURN count(*) AS total_years, 
       min(y.year) AS earliest_year, 
       max(y.year) AS latest_year;
       
// Expected result: total_years=4026, earliest_year=-2000, latest_year=2025

---

// ============================================================================
// FACET BOOTSTRAP NODES
// ============================================================================
// Create the 16 FacetCategory nodes and example Facet nodes
// These are canonical and referenced by all facet-aware queries
// ============================================================================

// Create FacetCategory nodes (organizing facets into UI/agent teams)
UNWIND [
  {key: "GEOGRAPHIC", label: "Geographic", color: "#1f77b4"},
  {key: "POLITICAL", label: "Political", color: "#ff7f0e"},
  {key: "CULTURAL", label: "Cultural", color: "#2ca02c"},
  {key: "TECHNOLOGICAL", label: "Technological", color: "#d62728"},
  {key: "RELIGIOUS", label: "Religious", color: "#9467bd"},
  {key: "ECONOMIC", label: "Economic", color: "#8c564b"},
  {key: "MILITARY", label: "Military", color: "#e377c2"},
  {key: "ENVIRONMENTAL", label: "Environmental", color: "#7f7f7f"},
  {key: "DEMOGRAPHIC", label: "Demographic", color: "#bcbd22"},
  {key: "INTELLECTUAL", label: "Intellectual", color: "#17becf"},
  {key: "SCIENTIFIC", label: "Scientific", color: "#1f77b4"},
  {key: "ARTISTIC", label: "Artistic", color: "#ff7f0e"},
  {key: "SOCIAL", label: "Social", color: "#2ca02c"},
  {key: "LINGUISTIC", label: "Linguistic", color: "#d62728"},
  {key: "ARCHAEOLOGICAL", label: "Archaeological", color: "#9467bd"},
  {key: "DIPLOMATIC", label: "Diplomatic", color: "#8c564b"}
] AS facet_category
CREATE (fc:FacetCategory {
  key: facet_category.key,
  label: facet_category.label,
  color: facet_category.color,
  entity_type: 'FacetCategory'
})

// Verify FacetCategory creation
MATCH (fc:FacetCategory)
RETURN count(*) AS total_categories,
       collect(fc.key) AS category_keys
ORDER BY fc.key;

// Expected result: 16 categories

---

// ============================================================================
// FOUNDATIONAL PLACE NODES
// ============================================================================
// Create stable Place identities for key Mediterranean/Republican locations
// These enable place-based entity linking (BORN_IN, LOCATED_IN, etc.)
// ============================================================================

// Rome (Urbs aeterna) - the anchor place for Roman historical reasoning
CREATE (rome:Place {
  entity_id: 'plc_rome_001',
  label: 'Rome',
  qid: 'Q220',
  place_type: 'city',
  latitude: 41.9028,
  longitude: 12.4964,
  modern_country: 'Italy',
  entity_type: 'Place'
});

// Italy (Italic Peninsula)
CREATE (italy:Place {
  entity_id: 'plc_italy_001',
  label: 'Italy',
  qid: 'Q38',
  place_type: 'region',
  latitude: 41.87,
  longitude: 12.56,
  modern_country: 'Italy',
  entity_type: 'Place'
});

// Mediterranean Sea
CREATE (med:Place {
  entity_id: 'plc_mediterranean_001',
  label: 'Mediterranean Sea',
  qid: 'Q4918',
  place_type: 'natural_feature',
  latitude: 35.0,
  longitude: 18.0,
  entity_type: 'Place'
});

// Link places hierarchically
MATCH (rome:Place {qid: 'Q220'})
MATCH (italy:Place {qid: 'Q38'})
CREATE (rome)-[:LOCATED_IN]->(italy);

// Verify Place creation
MATCH (p:Place)
RETURN count(*) AS total_places,
       collect(p.label) AS place_labels;

---

// ============================================================================
// FOUNDATIONAL PERIOD NODES
// ============================================================================
// Create historical periods for Roman timeline (bootstrap for testing)
// Real data loads will import from time_periods.csv + periodo-dataset.csv
// ============================================================================

// Roman Republic Period
MATCH (year_start:Year {year: -510})
MATCH (year_end:Year {year: -27})
CREATE (republic:Period {
  entity_id: 'prd_republic_001',
  label: 'Roman Republic',
  qid: 'Q17167',
  start: '-0510',
  end: '-0027',
  earliest_start: '-0520',
  latest_start: '-0500',
  earliest_end: '-0035',
  latest_end: '-0020',
  culture: 'Roman',
  facet: 'Political',
  entity_type: 'Period'
})
CREATE (republic)-[:STARTS_IN_YEAR]->(year_start)
CREATE (republic)-[:ENDS_IN_YEAR]->(year_end);

// Roman Empire Period
MATCH (year_start:Year {year: -27})
MATCH (year_end:Year {year: 1453})
CREATE (empire:Period {
  entity_id: 'prd_empire_001',
  label: 'Roman Empire',
  qid: 'Q12544',
  start: '-0027',
  end: '1453',
  culture: 'Roman',
  facet: 'Political',
  entity_type: 'Period'
})
CREATE (empire)-[:STARTS_IN_YEAR]->(year_start)
CREATE (empire)-[:ENDS_IN_YEAR]->(year_end);

// Late Republic Period (sub-period)
MATCH (year_start:Year {year: -133})
MATCH (year_end:Year {year: -27})
MATCH (republic:Period {qid: 'Q17167'})
CREATE (late_republic:Period {
  entity_id: 'prd_late_republic_001',
  label: 'Late Republic',
  qid: 'Q17167_late',
  start: '-0133',
  end: '-0027',
  culture: 'Roman',
  facet: 'Political',
  entity_type: 'Period'
})
CREATE (late_republic)-[:STARTS_IN_YEAR]->(year_start)
CREATE (late_republic)-[:ENDS_IN_YEAR]->(year_end)
CREATE (late_republic)-[:NARROWER_THAN]->(republic);

// Verify Period creation
MATCH (p:Period)
RETURN count(*) AS total_periods,
       collect(p.label) AS period_labels,
       min(p.start) AS earliest_start,
       max(p.end) AS latest_end;

---

// ============================================================================
// FOUNDATIONAL HUMAN ENTITY (EXAMPLE)
// ============================================================================
// Create Julius Caesar as anchor entity for testing & documentation
// Real entity loads will use import_fast_subjects_to_neo4j.py pipeline
// ============================================================================

CREATE (caesar:Human {
  entity_id: 'hum_julius_caesar_001',
  name: 'Gaius Julius Caesar',
  qid: 'Q1048',
  birth_date: '-0100-07-12',
  death_date: '-0044-03-15',
  date_precision: 'day',
  gender: 'male',
  viaf_id: '286265178',
  backbone_lcc: 'DG',
  backbone_fast: ['fst00868944', 'fst00891474'],
  backbone_lcsh: ['sh85020891', 'sh85115055'],
  cidoc_crm_class: 'E21_Person',
  entity_type: 'Human'
});

// Link Caesar to Rome (birthplace/deathplace not precisely known, but capital)
MATCH (caesar:Human {qid: 'Q1048'})
MATCH (rome:Place {qid: 'Q220'})
CREATE (caesar)-[:LIVED_IN]->(rome);

// Link Caesar to periods
MATCH (caesar:Human {qid: 'Q1048'})
MATCH (late_republic:Period {qid: 'Q17167_late'})
MATCH (empire:Period {qid: 'Q12544'})
CREATE (caesar)-[:LIVED_DURING]->(late_republic)
CREATE (caesar)-[:LIVED_DURING]->(empire);

// Link Caesar to Year nodes (birth & death)
MATCH (caesar:Human {qid: 'Q1048'})
MATCH (year_birth:Year {year: -100})
MATCH (year_death:Year {year: -44})
CREATE (caesar)-[:BORN_IN_YEAR]->(year_birth)
CREATE (caesar)-[:DIED_IN_YEAR]->(year_death);

// Verify Human creation
MATCH (h:Human)
RETURN count(*) AS total_humans,
       collect(h.name) AS human_names;

---

// ============================================================================
// FOUNDATIONAL ROMAN GENS (FAMILY CLAN)
// ============================================================================

CREATE (gens_julia:Gens {
  entity_id: 'gens_julia_001',
  label: 'Julia',
  entity_type: 'Gens'
});

// Link Caesar to Julia gens
MATCH (caesar:Human {qid: 'Q1048'})
MATCH (gens_julia:Gens {label: 'Julia'})
CREATE (caesar)-[:PART_OF_GENS]->(gens_julia);

---

// ============================================================================
// FOUNDATIONAL ORGANIZATION (ROMAN SENATE)
// ============================================================================

CREATE (senate:Organization {
  entity_id: 'org_roman_senate_001',
  label: 'Roman Senate',
  qid: 'Q41410',
  organization_type: 'political_body',
  entity_type: 'Organization'
});

// Link Senate to Rome
MATCH (senate:Organization {qid: 'Q41410'})
MATCH (rome:Place {qid: 'Q220'})
CREATE (senate)-[:LOCATED_IN]->(rome);

// Link Caesar to Senate membership
MATCH (caesar:Human {qid: 'Q1048'})
MATCH (senate:Organization {qid: 'Q41410'})
CREATE (caesar)-[:MEMBER_OF]->(senate);

---

// ============================================================================
// VERIFICATION QUERIES
// ============================================================================
// Run these to confirm successful initialization
// ============================================================================

// Summary statistics
MATCH (n) RETURN labels(n)[0] AS label, count(*) AS count
ORDER BY count DESC;

// Temporal backbone verification
MATCH (y1:Year)-[:FOLLOWED_BY]->(y2:Year)
RETURN count(*) AS year_linkages,
       min(y1.year) AS min_year,
       max(y2.year) AS max_year;

// Caesar entity verification
MATCH (caesar:Human {qid: 'Q1048'})
OPTIONAL MATCH (caesar)-[:LIVED_DURING]->(period:Period)
OPTIONAL MATCH (caesar)-[:PART_OF_GENS]->(gens:Gens)
OPTIONAL MATCH (caesar)-[:MEMBER_OF]->(org:Organization)
RETURN caesar.name, collect(period.label) AS periods,
       collect(gens.label) AS gentes,
       collect(org.label) AS organizations;

// Facet category verification
MATCH (fc:FacetCategory)
RETURN count(*) AS facet_categories,
       collect(fc.key) AS keys;

// Place hierarchy verification
MATCH (p1:Place)-[:LOCATED_IN]->(p2:Place)
RETURN p1.label + ' is located in ' + p2.label AS hierarchy;

---

// ============================================================================
// SCHEMA INITIALIZATION COMPLETE
// ============================================================================
// Successfully created:
// - Year backbone (4026 nodes, -2000 to 2025)
// - 16 FacetCategory nodes
// - Foundational places (Rome, Italy, Mediterranean)
// - Foundational periods (Republic, Empire, Late Republic)
// - Example human entity (Julius Caesar)
// - Roman organizational structures (Senate, Gens)
// ============================================================================
// Next steps:
// 1. Load FAST subjects via import_fast_subjects_to_neo4j.py
// 2. Import events, works, and additional entities
// 3. Build claims layer with evidence linkage
// 4. Deploy multi-agent evaluation infrastructure
// ============================================================================
