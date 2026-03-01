// ============================================================================
// CHRYSTALLUM: DM RULES EXTRACTED FROM CODE
// ============================================================================
// File: 16_dm_rules_from_code.cypher
// Purpose: Pull hardcoded business rules from Python scripts into queryable
//          decision tables and enriched SYS_ nodes. Replaces code-as-spec
//          with graph-as-spec.
// Sources:
//   scripts/federation/federation_scorer.py   (WEIGHTS, STATES, scoring rules)
//   scripts/federation/dprr_import.py         (DPRR_REL_MAP 37 entries)
//   scripts/sca/sca_federation_positioning.py (POSITIONING_PROPERTIES,
//                                              CLASSIFICATION_PROPS,
//                                              ANCHOR_TYPE_MAP)
// Safe: All MERGE — idempotent
// Run after: scripts 10-15
// ============================================================================


// ============================================================================
// PART 1: FEDERATION STATE CLASSIFICATION (D15)
// Extracted from: FederationScorer.STATES
// ============================================================================

MERGE (dt:SYS_DecisionTable {table_id: 'D15_DETERMINE_federation_state'})
SET dt.label        = 'Determine Federation State from Score',
    dt.description  = 'Maps a numeric federation score (0-100) to a FS-tier state label. Extracted from FederationScorer.STATES in scripts/federation/federation_scorer.py.',
    dt.hit_policy   = 'FIRST',
    dt.source_file  = 'scripts/federation/federation_scorer.py',
    dt.source_symbol = 'FederationScorer.STATES',
    dt.status       = 'active';

// Wire into D10 (claim promotion uses federation state as a factor)
MATCH (d15:SYS_DecisionTable {table_id: 'D15_DETERMINE_federation_state'})
MATCH (d10:SYS_DecisionTable {table_id: 'D10_DETERMINE_claim_promotion_eligibility'})
MERGE (d15)-[:FEEDS_INTO]->(d10);

MERGE (r1:SYS_DecisionRow {row_id: 'D15_r1_well_federated'})
SET r1.priority     = 1,
    r1.conditions   = 'score >= 80 AND score <= 100',
    r1.action       = 'assign_state',
    r1.action_detail = 'FS3_WELL_FEDERATED',
    r1.score_min    = 80,
    r1.score_max    = 100;

MERGE (r2:SYS_DecisionRow {row_id: 'D15_r2_federated'})
SET r2.priority     = 2,
    r2.conditions   = 'score >= 60 AND score <= 79',
    r2.action       = 'assign_state',
    r2.action_detail = 'FS2_FEDERATED',
    r2.score_min    = 60,
    r2.score_max    = 79;

MERGE (r3:SYS_DecisionRow {row_id: 'D15_r3_base'})
SET r3.priority     = 3,
    r3.conditions   = 'score >= 40 AND score <= 59',
    r3.action       = 'assign_state',
    r3.action_detail = 'FS1_BASE',
    r3.score_min    = 40,
    r3.score_max    = 59;

MERGE (r4:SYS_DecisionRow {row_id: 'D15_r4_unfederated'})
SET r4.priority     = 4,
    r4.conditions   = 'score >= 0 AND score <= 39',
    r4.action       = 'assign_state',
    r4.action_detail = 'FS0_UNFEDERATED',
    r4.score_min    = 0,
    r4.score_max    = 39;

MATCH (dt:SYS_DecisionTable {table_id: 'D15_DETERMINE_federation_state'})
MATCH (r:SYS_DecisionRow) WHERE r.row_id STARTS WITH 'D15_'
MERGE (dt)-[:HAS_ROW]->(r);


// ============================================================================
// PART 2: PLACE FEDERATION SCORING (D16)
// Extracted from: FederationScorer.score_place_simple()
// hit_policy=ALL: evaluate every row and sum the points
// ============================================================================

MERGE (dt:SYS_DecisionTable {table_id: 'D16_SCORE_place_federation'})
SET dt.label        = 'Score Place Federation Completeness',
    dt.description  = 'Component scoring rubric for Place nodes. Each condition adds points toward federation state. Total possible = 100. Extracted from FederationScorer.score_place_simple().',
    dt.hit_policy   = 'ALL',
    dt.source_file  = 'scripts/federation/federation_scorer.py',
    dt.source_symbol = 'FederationScorer.score_place_simple',
    dt.status       = 'active';

MATCH (d16:SYS_DecisionTable {table_id: 'D16_SCORE_place_federation'})
MATCH (d15:SYS_DecisionTable {table_id: 'D15_DETERMINE_federation_state'})
MERGE (d16)-[:FEEDS_INTO]->(d15);

MERGE (r:SYS_DecisionRow {row_id: 'D16_r1_pleiades'})
SET r.priority      = 1,
    r.conditions    = 'pleiades_id IS NOT NULL',
    r.action        = 'add_score',
    r.action_detail = '20',
    r.score_points  = 20,
    r.dimension     = 'place_authority';

MERGE (r:SYS_DecisionRow {row_id: 'D16_r2_qid'})
SET r.priority      = 2,
    r.conditions    = 'qid IS NOT NULL',
    r.action        = 'add_score',
    r.action_detail = '50',
    r.score_points  = 50,
    r.dimension     = 'wikidata_alignment';

MERGE (r:SYS_DecisionRow {row_id: 'D16_r3_temporal'})
SET r.priority      = 3,
    r.conditions    = 'min_date IS NOT NULL OR max_date IS NOT NULL',
    r.action        = 'add_score',
    r.action_detail = '20',
    r.score_points  = 20,
    r.dimension     = 'temporal_bounds';

MERGE (r:SYS_DecisionRow {row_id: 'D16_r4_coords'})
SET r.priority      = 4,
    r.conditions    = 'lat IS NOT NULL AND long IS NOT NULL',
    r.action        = 'add_score',
    r.action_detail = '10',
    r.score_points  = 10,
    r.dimension     = 'geospatial';

MATCH (dt:SYS_DecisionTable {table_id: 'D16_SCORE_place_federation'})
MATCH (r:SYS_DecisionRow) WHERE r.row_id STARTS WITH 'D16_'
MERGE (dt)-[:HAS_ROW]->(r);


// ============================================================================
// PART 3: PERIOD FEDERATION SCORING (D17)
// Extracted from: FederationScorer.score_period_simple()
// ============================================================================

MERGE (dt:SYS_DecisionTable {table_id: 'D17_SCORE_period_federation'})
SET dt.label        = 'Score Period Federation Completeness',
    dt.description  = 'Component scoring rubric for Period nodes. Total possible = 100. Extracted from FederationScorer.score_period_simple().',
    dt.hit_policy   = 'ALL',
    dt.source_file  = 'scripts/federation/federation_scorer.py',
    dt.source_symbol = 'FederationScorer.score_period_simple',
    dt.status       = 'active';

MATCH (d17:SYS_DecisionTable {table_id: 'D17_SCORE_period_federation'})
MATCH (d15:SYS_DecisionTable {table_id: 'D15_DETERMINE_federation_state'})
MERGE (d17)-[:FEEDS_INTO]->(d15);

MERGE (r:SYS_DecisionRow {row_id: 'D17_r1_periodo'})
SET r.priority      = 1,
    r.conditions    = 'authority = "PeriodO" OR periodo_id IS NOT NULL',
    r.action        = 'add_score',
    r.action_detail = '30',
    r.score_points  = 30,
    r.dimension     = 'period_authority';

MERGE (r:SYS_DecisionRow {row_id: 'D17_r2_qid'})
SET r.priority      = 2,
    r.conditions    = 'qid IS NOT NULL',
    r.action        = 'add_score',
    r.action_detail = '50',
    r.score_points  = 50,
    r.dimension     = 'wikidata_alignment';

MERGE (r:SYS_DecisionRow {row_id: 'D17_r3_temporal'})
SET r.priority      = 3,
    r.conditions    = 'start_year IS NOT NULL OR start IS NOT NULL OR end_year IS NOT NULL OR end IS NOT NULL',
    r.action        = 'add_score',
    r.action_detail = '20',
    r.score_points  = 20,
    r.dimension     = 'temporal_bounds';

MATCH (dt:SYS_DecisionTable {table_id: 'D17_SCORE_period_federation'})
MATCH (r:SYS_DecisionRow) WHERE r.row_id STARTS WITH 'D17_'
MERGE (dt)-[:HAS_ROW]->(r);


// ============================================================================
// PART 4: SUBJECT AUTHORITY SCORING (D18)
// Extracted from: FederationScorer.score_subject_concept()
// Also: authority_jump = has_lcsh OR has_fast → enables authority jumping
// ============================================================================

MERGE (dt:SYS_DecisionTable {table_id: 'D18_SCORE_subject_authority'})
SET dt.label        = 'Score SubjectConcept Authority Federation',
    dt.description  = 'Component scoring rubric for SubjectConcept nodes. Total possible = 100. LCSH OR FAST enables authority_jump. Extracted from FederationScorer.score_subject_concept().',
    dt.hit_policy   = 'ALL',
    dt.source_file  = 'scripts/federation/federation_scorer.py',
    dt.source_symbol = 'FederationScorer.score_subject_concept',
    dt.status       = 'active';

MATCH (d18:SYS_DecisionTable {table_id: 'D18_SCORE_subject_authority'})
MATCH (d15:SYS_DecisionTable {table_id: 'D15_DETERMINE_federation_state'})
MERGE (d18)-[:FEEDS_INTO]->(d15);

MERGE (r:SYS_DecisionRow {row_id: 'D18_r1_lcsh'})
SET r.priority      = 1,
    r.conditions    = 'lcsh_id IS NOT NULL',
    r.action        = 'add_score',
    r.action_detail = '30',
    r.score_points  = 30,
    r.dimension     = 'lcsh_authority',
    r.note          = 'Also enables authority_jump when combined with has_fast';

MERGE (r:SYS_DecisionRow {row_id: 'D18_r2_fast'})
SET r.priority      = 2,
    r.conditions    = 'fast_id IS NOT NULL',
    r.action        = 'add_score',
    r.action_detail = '30',
    r.score_points  = 30,
    r.dimension     = 'fast_authority',
    r.note          = 'Also enables authority_jump when combined with has_lcsh';

MERGE (r:SYS_DecisionRow {row_id: 'D18_r3_lcc'})
SET r.priority      = 3,
    r.conditions    = 'lcc_class IS NOT NULL',
    r.action        = 'add_score',
    r.action_detail = '20',
    r.score_points  = 20,
    r.dimension     = 'lcc_classification';

MERGE (r:SYS_DecisionRow {row_id: 'D18_r4_qid'})
SET r.priority      = 4,
    r.conditions    = 'qid IS NOT NULL',
    r.action        = 'add_score',
    r.action_detail = '20',
    r.score_points  = 20,
    r.dimension     = 'wikidata_alignment';

MERGE (r:SYS_DecisionRow {row_id: 'D18_r5_authority_jump'})
SET r.priority      = 5,
    r.conditions    = 'lcsh_id IS NOT NULL OR fast_id IS NOT NULL',
    r.action        = 'set_flag',
    r.action_detail = 'authority_jump = true',
    r.score_points  = 0,
    r.dimension     = 'authority_jump_gate';

MATCH (dt:SYS_DecisionTable {table_id: 'D18_SCORE_subject_authority'})
MATCH (r:SYS_DecisionRow) WHERE r.row_id STARTS WITH 'D18_'
MERGE (dt)-[:HAS_ROW]->(r);


// ============================================================================
// PART 5: DPRR RELATIONSHIP NORMALIZATION (D19)
// Extracted from: DPRR_REL_MAP in scripts/federation/dprr_import.py
// hit_policy=FIRST (each label matches exactly one row)
// ============================================================================

MERGE (dt:SYS_DecisionTable {table_id: 'D19_NORMALIZE_dprr_relationship'})
SET dt.label        = 'Normalize DPRR Relationship Label to Canonical Type',
    dt.description  = 'Maps DPRR prosopographic relationship labels to canonical Chrystallum edge types. swap=true means reverse subject/object order (DPRR stores child-first for some relations). Extracted from DPRR_REL_MAP in scripts/federation/dprr_import.py.',
    dt.hit_policy   = 'FIRST',
    dt.source_file  = 'scripts/federation/dprr_import.py',
    dt.source_symbol = 'DPRR_REL_MAP',
    dt.status       = 'active';

MERGE (r:SYS_DecisionRow {row_id: 'D19_father_of'})        SET r.priority=1,  r.conditions='dprr_label = "father of"',          r.action='create_edge', r.action_detail='FATHER_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_mother_of'})        SET r.priority=2,  r.conditions='dprr_label = "mother of"',          r.action='create_edge', r.action_detail='MOTHER_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_son_of'})           SET r.priority=3,  r.conditions='dprr_label = "son of"',             r.action='create_edge', r.action_detail='FATHER_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_daughter_of'})      SET r.priority=4,  r.conditions='dprr_label = "daughter of"',        r.action='create_edge', r.action_detail='MOTHER_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_brother_of'})       SET r.priority=5,  r.conditions='dprr_label = "brother of"',         r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_sister_of'})        SET r.priority=6,  r.conditions='dprr_label = "sister of"',          r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_married_to'})       SET r.priority=7,  r.conditions='dprr_label = "married to"',         r.action='create_edge', r.action_detail='SPOUSE_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_divorced_from'})    SET r.priority=8,  r.conditions='dprr_label = "divorced from"',      r.action='create_edge', r.action_detail='SPOUSE_OF', r.swap=false, r.note='treated same as married_to; add DIVORCED_FROM if needed';
MERGE (r:SYS_DecisionRow {row_id: 'D19_grandfather_of'})   SET r.priority=9,  r.conditions='dprr_label = "grandfather of"',     r.action='create_edge', r.action_detail='FATHER_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_grandson_of'})      SET r.priority=10, r.conditions='dprr_label = "grandson of"',        r.action='create_edge', r.action_detail='FATHER_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_grandmother_of'})   SET r.priority=11, r.conditions='dprr_label = "grandmother of"',     r.action='create_edge', r.action_detail='MOTHER_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_granddaughter_of'}) SET r.priority=12, r.conditions='dprr_label = "granddaughter of"',   r.action='create_edge', r.action_detail='MOTHER_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_related_to'})       SET r.priority=13, r.conditions='dprr_label = "related to"',         r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=false, r.note='fallback approximation';
MERGE (r:SYS_DecisionRow {row_id: 'D19_adopted_son_of'})   SET r.priority=14, r.conditions='dprr_label = "adopted son of"',     r.action='create_edge', r.action_detail='FATHER_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_adoptive_father_of'}) SET r.priority=15, r.conditions='dprr_label = "adoptive father of"', r.action='create_edge', r.action_detail='FATHER_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_nephew_of'})        SET r.priority=16, r.conditions='dprr_label = "nephew of"',          r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=false, r.note='approximate';
MERGE (r:SYS_DecisionRow {row_id: 'D19_uncle_of'})         SET r.priority=17, r.conditions='dprr_label = "uncle of"',           r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_cousin_of'})        SET r.priority=18, r.conditions='dprr_label = "cousin of"',          r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_betrothed_to'})     SET r.priority=19, r.conditions='dprr_label = "betrothed to"',       r.action='create_edge', r.action_detail='SPOUSE_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_great_grandfather_of'}) SET r.priority=20, r.conditions='dprr_label = "great grandfather of"', r.action='create_edge', r.action_detail='FATHER_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_stepbrother_of'})   SET r.priority=21, r.conditions='dprr_label = "stepbrother of"',    r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_great_grandson_of'}) SET r.priority=22, r.conditions='dprr_label = "great grandson of"', r.action='create_edge', r.action_detail='FATHER_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_stepfather_of'})    SET r.priority=23, r.conditions='dprr_label = "stepfather of"',     r.action='create_edge', r.action_detail='FATHER_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_stepson_of'})       SET r.priority=24, r.conditions='dprr_label = "stepson of"',        r.action='create_edge', r.action_detail='FATHER_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_adoptive_brother_of'}) SET r.priority=25, r.conditions='dprr_label = "adoptive brother of"', r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_halfbrother_of'})   SET r.priority=26, r.conditions='dprr_label = "halfbrother of"',    r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_halfsister_of'})    SET r.priority=27, r.conditions='dprr_label = "halfsister of"',     r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_stepsister_of'})    SET r.priority=28, r.conditions='dprr_label = "stepsister of"',     r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_adoptive_mother_of'}) SET r.priority=29, r.conditions='dprr_label = "adoptive mother of"', r.action='create_edge', r.action_detail='MOTHER_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_aunt_of'})          SET r.priority=30, r.conditions='dprr_label = "aunt of"',           r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_niece_of'})         SET r.priority=31, r.conditions='dprr_label = "niece of"',          r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_great_uncle_of'})   SET r.priority=32, r.conditions='dprr_label = "great uncle of"',    r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_great_nephew_of'})  SET r.priority=33, r.conditions='dprr_label = "great nephew of"',   r.action='create_edge', r.action_detail='SIBLING_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_adoptive_grandfather'}) SET r.priority=34, r.conditions='dprr_label = "adoptive grandfather"', r.action='create_edge', r.action_detail='FATHER_OF', r.swap=false;
MERGE (r:SYS_DecisionRow {row_id: 'D19_adopted_grandson_of'}) SET r.priority=35, r.conditions='dprr_label = "adopted grandson of"', r.action='create_edge', r.action_detail='FATHER_OF', r.swap=true;
MERGE (r:SYS_DecisionRow {row_id: 'D19_great_granddaughter_of'}) SET r.priority=36, r.conditions='dprr_label = "great granddaughter of"', r.action='create_edge', r.action_detail='MOTHER_OF', r.swap=true;
// Fallback row: label not in map
MERGE (r:SYS_DecisionRow {row_id: 'D19_unmapped_fallback'}) SET r.priority=99, r.conditions='dprr_label NOT IN known_labels', r.action='skip_and_warn', r.action_detail='log_unmapped_label', r.swap=false;

MATCH (dt:SYS_DecisionTable {table_id: 'D19_NORMALIZE_dprr_relationship'})
MATCH (r:SYS_DecisionRow) WHERE r.row_id STARTS WITH 'D19_'
MERGE (dt)-[:HAS_ROW]->(r);


// ============================================================================
// PART 6: ENRICH SYS_WikidataProperty WITH SEMANTIC ROLES
// Extracted from: POSITIONING_PROPERTIES + CLASSIFICATION_PROPS
//   in scripts/sca/sca_federation_positioning.py
// ============================================================================

// Positioning properties (Layer 1 traversal)
MERGE (p:SYS_WikidataProperty {pid: 'P31'})
SET p.semantic_role = 'INSTANCE_OF_CLASS',
    p.traversal_layer = 1,
    p.property_name = 'instance of',
    p.use_in_positioning = true;

MERGE (p:SYS_WikidataProperty {pid: 'P279'})
SET p.semantic_role = 'CLASSIFICATION_PARENT',
    p.traversal_layer = 1,
    p.property_name = 'subclass of',
    p.use_in_positioning = true;

MERGE (p:SYS_WikidataProperty {pid: 'P361'})
SET p.semantic_role = 'COMPOSITIONAL_PARENT',
    p.traversal_layer = 1,
    p.property_name = 'part of',
    p.use_in_positioning = true;

MERGE (p:SYS_WikidataProperty {pid: 'P122'})
SET p.semantic_role = 'TYPE_ANCHOR',
    p.traversal_layer = 1,
    p.property_name = 'basic form of government',
    p.use_in_positioning = true;

MERGE (p:SYS_WikidataProperty {pid: 'P527'})
SET p.semantic_role = 'COMPOSITIONAL_CHILD',
    p.traversal_layer = 1,
    p.property_name = 'has part',
    p.use_in_positioning = true;

MERGE (p:SYS_WikidataProperty {pid: 'P460'})
SET p.semantic_role = 'SAME_AS_CANDIDATE',
    p.traversal_layer = 1,
    p.property_name = 'said to be same as',
    p.use_in_positioning = true;

MERGE (p:SYS_WikidataProperty {pid: 'P1269'})
SET p.semantic_role = 'ASSOCIATIVE',
    p.traversal_layer = 1,
    p.property_name = 'facet of',
    p.use_in_positioning = true;

// Classification properties (authority ID harvest)
MERGE (p:SYS_WikidataProperty {pid: 'P1036'})
SET p.semantic_role = 'CLASSIFICATION_ID',
    p.classification_scheme = 'dewey',
    p.property_name = 'Dewey Decimal Classification',
    p.use_in_positioning = false,
    p.use_in_classification = true;

MERGE (p:SYS_WikidataProperty {pid: 'P1149'})
SET p.semantic_role = 'CLASSIFICATION_ID',
    p.classification_scheme = 'lcc',
    p.property_name = 'Library of Congress Classification',
    p.use_in_positioning = false,
    p.use_in_classification = true;

MERGE (p:SYS_WikidataProperty {pid: 'P244'})
SET p.semantic_role = 'AUTHORITY_ID',
    p.classification_scheme = 'lcsh_id',
    p.property_name = 'Library of Congress authority ID',
    p.use_in_positioning = false,
    p.use_in_classification = true;

MERGE (p:SYS_WikidataProperty {pid: 'P2163'})
SET p.semantic_role = 'AUTHORITY_ID',
    p.classification_scheme = 'fast_id',
    p.property_name = 'FAST subject heading ID',
    p.use_in_positioning = false,
    p.use_in_classification = true;

MERGE (p:SYS_WikidataProperty {pid: 'P227'})
SET p.semantic_role = 'AUTHORITY_ID',
    p.classification_scheme = 'gnd_id',
    p.property_name = 'GND ID',
    p.use_in_positioning = false,
    p.use_in_classification = true;


// ============================================================================
// PART 7: ANCHOR TYPE MAP
// Extracted from: ANCHOR_TYPE_MAP in scripts/sca/sca_federation_positioning.py
// Purpose: Maps known parent QIDs of the domain root (Q17167 Roman Republic)
//          to Chrystallum anchor_type labels. Agents use this to classify
//          what kind of concept they are positioning against.
// ============================================================================

MERGE (n:SYS_AnchorTypeMapping {qid: 'Q1307214'})
SET n.anchor_type   = 'FormOfGovernment',
    n.wikidata_label = 'form of government',
    n.source_file   = 'scripts/sca/sca_federation_positioning.py',
    n.source_symbol = 'ANCHOR_TYPE_MAP';

MERGE (n:SYS_AnchorTypeMapping {qid: 'Q11514315'})
SET n.anchor_type   = 'HistoricalPeriod',
    n.wikidata_label = 'historical period',
    n.source_file   = 'scripts/sca/sca_federation_positioning.py',
    n.source_symbol = 'ANCHOR_TYPE_MAP';

MERGE (n:SYS_AnchorTypeMapping {qid: 'Q3024240'})
SET n.anchor_type   = 'HistoricalCountry',
    n.wikidata_label = 'historical country',
    n.source_file   = 'scripts/sca/sca_federation_positioning.py',
    n.source_symbol = 'ANCHOR_TYPE_MAP';

MERGE (n:SYS_AnchorTypeMapping {qid: 'Q48349'})
SET n.anchor_type   = 'Empire',
    n.wikidata_label = 'empire',
    n.source_file   = 'scripts/sca/sca_federation_positioning.py',
    n.source_symbol = 'ANCHOR_TYPE_MAP';

MERGE (n:SYS_AnchorTypeMapping {qid: 'Q666680'})
SET n.anchor_type   = 'FormOfGovernmentType',
    n.wikidata_label = 'aristocratic republic',
    n.source_file   = 'scripts/sca/sca_federation_positioning.py',
    n.source_symbol = 'ANCHOR_TYPE_MAP';

MERGE (n:SYS_AnchorTypeMapping {qid: 'Q7270'})
SET n.anchor_type   = 'FormOfGovernmentType',
    n.wikidata_label = 'republic',
    n.source_file   = 'scripts/sca/sca_federation_positioning.py',
    n.source_symbol = 'ANCHOR_TYPE_MAP';

MERGE (n:SYS_AnchorTypeMapping {qid: 'Q1747689'})
SET n.anchor_type   = 'CivilisationContext',
    n.wikidata_label = 'Ancient Rome',
    n.source_file   = 'scripts/sca/sca_federation_positioning.py',
    n.source_symbol = 'ANCHOR_TYPE_MAP';

MERGE (n:SYS_AnchorTypeMapping {qid: 'Q28108'})
SET n.anchor_type   = 'PoliticalSystem',
    n.wikidata_label = 'political system',
    n.source_file   = 'scripts/sca/sca_federation_positioning.py',
    n.source_symbol = 'ANCHOR_TYPE_MAP';

MERGE (n:SYS_AnchorTypeMapping {qid: 'Q2277'})
SET n.anchor_type   = 'HistoricalPeriod',
    n.wikidata_label = 'Roman Empire (successor)',
    n.source_file   = 'scripts/sca/sca_federation_positioning.py',
    n.source_symbol = 'ANCHOR_TYPE_MAP';


// ============================================================================
// VALIDATION
// ============================================================================

MATCH (dt:SYS_DecisionTable) WHERE dt.table_id STARTS WITH 'D1' OR dt.table_id STARTS WITH 'D2'
RETURN dt.table_id AS table, dt.hit_policy AS policy,
       size([(dt)-[:HAS_ROW]->() | 1]) AS row_count
ORDER BY dt.table_id;
