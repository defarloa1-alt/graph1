// ============================================================================
// SEED COMPLETION: Roman Republic SubjectConcept (Q17167)
// ============================================================================
// Date: 2026-03-04
// Context: ADR-013, SCA gap analysis
//
// Problem: bootstrap_subject_concept_agents.cypher targeted subject_id
// 'subj_roman_republic_q17167' but the actual node created by the SCA
// federation positioning script has subject_id 'subj_q17167'. The MERGE
// never matched, so LCSH, FAST, LCC, facet, temporal, and bibliography
// links were never written. This script completes the seed.
//
// Prerequisites: Run against a graph that already has:
//   - SubjectConcept {subject_id: 'subj_q17167'}
//   - LCC_Class nodes with prefix 'DG'
//   - Year nodes for -509 and -27
//   - BibliographySource nodes (DPRR, Broughton_MRR, Zmeskal_Adfinitas)
//
// Idempotent: All operations use MERGE. Safe to re-run.
// ============================================================================


// ============================================================================
// STEP 1: AUTHORITY FEDERATION — LCSH, FAST
// ============================================================================

// LCSH: Rome--History--Republic, 265-30 B.C.
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MERGE (lcsh:LCSH_Subject {lcsh_id: 'sh85115087'})
ON CREATE SET
  lcsh.heading = 'Rome--History--Republic, 265-30 B.C.',
  lcsh.uri = 'http://id.loc.gov/authorities/subjects/sh85115087',
  lcsh.created_at = datetime()
MERGE (sc)-[:HAS_LCSH_AUTHORITY]->(lcsh)
RETURN 'LCSH linked' AS step, lcsh.heading AS detail;


// FAST: Rome--History--Republic, 265-30 B.C.
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MERGE (fast:FAST_Subject {fast_id: 'fst01204885'})
ON CREATE SET
  fast.preferred_label = 'Rome--History--Republic, 265-30 B.C.',
  fast.uri = 'http://id.worldcat.org/fast/1204885',
  fast.created_at = datetime()
MERGE (sc)-[:HAS_FAST_AUTHORITY]->(fast)
RETURN 'FAST linked' AS step, fast.preferred_label AS detail;


// ============================================================================
// STEP 2: LCC CLASSIFICATION
// ============================================================================

// Primary classification: DG201-365 Roman History by period (broadest)
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'DG201-365'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'primary'}]->(lcc)
RETURN 'LCC primary linked' AS step, lcc.code AS detail;

// Narrower: DG221-239 Early Republic
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'DG221-239'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'period_subdivision'}]->(lcc)
RETURN 'LCC Early Republic linked' AS step, lcc.code AS detail;

// Narrower: DG241-259 Middle Republic
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'DG241-259'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'period_subdivision'}]->(lcc)
RETURN 'LCC Middle Republic linked' AS step, lcc.code AS detail;

// Narrower: DG261-269 Late Republic
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'DG261-269'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'period_subdivision'}]->(lcc)
RETURN 'LCC Late Republic linked' AS step, lcc.code AS detail;

// Cross-discipline: DG89 Constitution, DG91 Political institutions,
// DG95 Magistracies, DG99 Senate, DG105 Army
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'DG89'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'thematic'}]->(lcc)
RETURN 'LCC Constitution linked' AS step, lcc.code AS detail;

MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'DG91'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'thematic'}]->(lcc)
RETURN 'LCC Political institutions linked' AS step, lcc.code AS detail;

MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'DG95'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'thematic'}]->(lcc)
RETURN 'LCC Magistracies linked' AS step, lcc.code AS detail;

MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'DG99'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'thematic'}]->(lcc)
RETURN 'LCC Senate linked' AS step, lcc.code AS detail;

MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'DG105'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'thematic'}]->(lcc)
RETURN 'LCC Army linked' AS step, lcc.code AS detail;

MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'DG125'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'thematic'}]->(lcc)
RETURN 'LCC Family linked' AS step, lcc.code AS detail;

// Roman Law (cross-schedule)
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'KJA2-3660'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'cross_schedule'}]->(lcc)
RETURN 'LCC Roman Law linked' AS step, lcc.code AS detail;

// Ancient state (political theory)
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'JC51-93'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'cross_schedule'}]->(lcc)
RETURN 'LCC Ancient state linked' AS step, lcc.code AS detail;

// Ancient numismatics
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'CJ201-1397.22'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'cross_schedule'}]->(lcc)
RETURN 'LCC Ancient numismatics linked' AS step, lcc.code AS detail;

// Ancient inscriptions
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (lcc:LCC_Class {code: 'CN120-741.22'})
MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'cross_schedule'}]->(lcc)
RETURN 'LCC Ancient inscriptions linked' AS step, lcc.code AS detail;


// ============================================================================
// STEP 3: BIBLIOGRAPHY SOURCES
// ============================================================================

// DPRR — primary authority for person prosopography
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (bib:BibliographySource {id: 'DPRR'})
MERGE (sc)-[:HAS_BIBLIOGRAPHY_AUTHORITY {
  scope: 'primary',
  domain: 'person_prosopography',
  note: 'Digital Prosopography of the Roman Republic — primary for offices, dates, relationships'
}]->(bib)
RETURN 'DPRR linked' AS step;

// Broughton MRR — secondary authority for magistracies
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (bib:BibliographySource {id: 'Broughton_MRR'})
MERGE (sc)-[:HAS_BIBLIOGRAPHY_AUTHORITY {
  scope: 'secondary_academic',
  domain: 'magistracies',
  note: 'Broughton Magistrates of the Roman Republic — canonical office-holder list'
}]->(bib)
RETURN 'Broughton MRR linked' AS step;

// Zmeskal Adfinitas — secondary authority for family networks
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (bib:BibliographySource {id: 'Zmeskal_Adfinitas'})
MERGE (sc)-[:HAS_BIBLIOGRAPHY_AUTHORITY {
  scope: 'secondary_academic',
  domain: 'family_networks',
  note: 'Zmeskal Adfinitas — kinship and marriage networks among Roman elite'
}]->(bib)
RETURN 'Zmeskal linked' AS step;


// ============================================================================
// STEP 4: FACET ASSIGNMENTS
// ============================================================================

// Primary facet: POLITICAL (republic = political entity)
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
SET sc.primary_facet = 'POLITICAL',
    sc.related_facets = ['MILITARY', 'LEGAL', 'RELIGIOUS', 'SOCIAL', 'ECONOMIC'],
    sc.facet_assigned_at = datetime(),
    sc.facet_assignment_source = 'seed_completion_adr013'
RETURN 'Facets assigned' AS step, sc.primary_facet AS primary, sc.related_facets AS related;


// ============================================================================
// STEP 5: TEMPORAL TETHERING (SubjectConcept → Year backbone)
// ============================================================================

// The Entity node already has STARTS_IN_YEAR/ENDS_IN_YEAR.
// The SubjectConcept node does not. Wire it.
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
MATCH (start_year:Year {year: -509})
MATCH (end_year:Year {year: -27})
MERGE (sc)-[:STARTS_IN_YEAR]->(start_year)
MERGE (sc)-[:ENDS_IN_YEAR]->(end_year)
RETURN 'Temporal tethered' AS step, start_year.label AS start, end_year.label AS end;


// ============================================================================
// STEP 6: ENRICHMENT PROPERTIES
// ============================================================================

MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
SET sc.wikidata_instance_of = ['Q11514315', 'Q3024240', 'Q1307214'],
    sc.wikidata_part_of = 'Q1747689',
    sc.wikidata_start_time = '-0509-01-01',
    sc.wikidata_end_time = '-0027-01-01',
    sc.lcc_primary = 'DG201-365',
    sc.lcsh_primary = 'sh85115087',
    sc.fast_primary = 'fst01204885',
    sc.bibliography_authorities = ['DPRR', 'Broughton_MRR', 'Zmeskal_Adfinitas'],
    sc.seed_completed_at = datetime(),
    sc.seed_completed_by = 'seed_roman_republic_subject_concept.cypher'
RETURN 'Properties enriched' AS step;


// ============================================================================
// STEP 7: VERIFICATION QUERIES
// ============================================================================

// Count all edges from SubjectConcept
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})-[r]->(n)
RETURN type(r) AS relationship, count(*) AS count
ORDER BY count DESC;

// Verify LCSH/FAST/LCC exist
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167'})
OPTIONAL MATCH (sc)-[:HAS_LCSH_AUTHORITY]->(lcsh)
OPTIONAL MATCH (sc)-[:HAS_FAST_AUTHORITY]->(fast)
OPTIONAL MATCH (sc)-[:CLASSIFIED_BY_LCC]->(lcc)
OPTIONAL MATCH (sc)-[:HAS_BIBLIOGRAPHY_AUTHORITY]->(bib)
OPTIONAL MATCH (sc)-[:STARTS_IN_YEAR]->(sy)
OPTIONAL MATCH (sc)-[:ENDS_IN_YEAR]->(ey)
RETURN sc.label AS subject,
       lcsh.heading AS lcsh,
       fast.preferred_label AS fast,
       collect(DISTINCT lcc.code) AS lcc_codes,
       collect(DISTINCT bib.id) AS bibliography,
       sy.label AS start_year,
       ey.label AS end_year,
       sc.primary_facet AS facet;
