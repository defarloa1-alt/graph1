// ============================================================================
// CHRYSTALLUM: DISCIPLINE KERNEL + SCORING PATCH
// ============================================================================
// File: 17_discipline_scoring_and_kernel_patch.cypher
// Purpose:
//   1) Preserve Discipline subgraph while removing relationship-name ambiguity
//   2) Add D20 authority scoring for Discipline nodes (D18-style)
//   3) Add weighted predicate signal scoring (D21)
//   4) Wire D20/D21 to D15 federation-state mapping
//   5) Make D9 return machine-usable constitution_doc_ids
//
// Safety:
//   - MERGE-only for metadata and decision tables
//   - Relationship migration only rewrites rel type names between Discipline nodes
//   - No node deletes; Discipline subgraph topology preserved
// ============================================================================


// ============================================================================
// PART 1: DISCIPLINE RELATIONSHIP KERNEL (explicit, non-ambiguous)
// ============================================================================

UNWIND [
  {
    name: 'DISCIPLINE_SUBCLASS_OF',
    semantic: 'taxonomy',
    source: 'Discipline',
    target: 'Discipline',
    cardinality: 'many_to_one',
    description: 'Discipline taxonomy parent (subclass-of).',
    wikidata_property: 'P279'
  },
  {
    name: 'DISCIPLINE_BROADER_THAN',
    semantic: 'hierarchy',
    source: 'Discipline',
    target: 'Discipline',
    cardinality: 'many_to_one',
    description: 'Broader-term hierarchy (library/subject-heading style).',
    wikidata_property: null
  },
  {
    name: 'DISCIPLINE_PART_OF',
    semantic: 'mereology',
    source: 'Discipline',
    target: 'Discipline',
    cardinality: 'many_to_one',
    description: 'Discipline is part of a broader discipline.',
    wikidata_property: 'P361'
  },
  {
    name: 'DISCIPLINE_HAS_PART',
    semantic: 'mereology',
    source: 'Discipline',
    target: 'Discipline',
    cardinality: 'one_to_many',
    description: 'Discipline contains a sub-discipline (inverse of part-of).',
    wikidata_property: 'P527'
  }
] AS rel
MERGE (r:SYS_RelationshipType {name: rel.name})
SET r.semantic = rel.semantic,
    r.source_label = rel.source,
    r.target_label = rel.target,
    r.cardinality = rel.cardinality,
    r.description = rel.description,
    r.wikidata_property = rel.wikidata_property,
    r.kernel_category = 'discipline',
    r.kernel_version = 'v1.0',
    r.updated = datetime();


// -----------------------------------------------------------------------------
// Preserve Discipline subgraph while normalizing relationship type names
// -----------------------------------------------------------------------------

// SUBCLASS_OF -> DISCIPLINE_SUBCLASS_OF
MATCH (a:Discipline)-[r:SUBCLASS_OF]->(b:Discipline)
MERGE (a)-[:DISCIPLINE_SUBCLASS_OF]->(b)
DELETE r;

// BROADER_THAN -> DISCIPLINE_BROADER_THAN
MATCH (a:Discipline)-[r:BROADER_THAN]->(b:Discipline)
MERGE (a)-[:DISCIPLINE_BROADER_THAN]->(b)
DELETE r;

// PART_OF -> DISCIPLINE_PART_OF (avoids temporal PART_OF ambiguity)
MATCH (a:Discipline)-[r:PART_OF]->(b:Discipline)
MERGE (a)-[:DISCIPLINE_PART_OF]->(b)
DELETE r;

// HAS_PART -> DISCIPLINE_HAS_PART
MATCH (a:Discipline)-[r:HAS_PART]->(b:Discipline)
MERGE (a)-[:DISCIPLINE_HAS_PART]->(b)
DELETE r;


// ============================================================================
// PART 2: D20 SCORE DISCIPLINE AUTHORITY (presence-based, D18-style)
// ============================================================================

MERGE (dt20:SYS_DecisionTable {table_id: 'D20_SCORE_discipline_authority'})
SET dt20.label = 'Score Discipline Authority Federation',
    dt20.description = 'Component scoring rubric for Discipline nodes. Presence-based authority IDs, D18-style. Score capped at 100 by policy.',
    dt20.hit_policy = 'ALL',
    dt20.inputs = ['lcsh_id', 'fast_id', 'ddc', 'gnd_id', 'aat_id', 'qid'],
    dt20.outputs = ['authority_score', 'authority_jump'],
    dt20.status = 'active',
    dt20.version = '1.0',
    dt20.updated = datetime();

UNWIND [
  {row_id: 'D20_R01', priority: 1, conditions: 'lcsh_id IS NOT NULL', action: 'add_score', detail: '30', score_points: 30, dimension: 'lcsh_authority'},
  {row_id: 'D20_R02', priority: 2, conditions: 'fast_id IS NOT NULL', action: 'add_score', detail: '20', score_points: 20, dimension: 'fast_authority'},
  {row_id: 'D20_R03', priority: 3, conditions: 'ddc IS NOT NULL', action: 'add_score', detail: '15', score_points: 15, dimension: 'ddc_classification'},
  {row_id: 'D20_R04', priority: 4, conditions: 'gnd_id IS NOT NULL', action: 'add_score', detail: '15', score_points: 15, dimension: 'gnd_authority'},
  {row_id: 'D20_R05', priority: 5, conditions: 'aat_id IS NOT NULL', action: 'add_score', detail: '10', score_points: 10, dimension: 'aat_authority'},
  {row_id: 'D20_R06', priority: 6, conditions: 'qid IS NOT NULL', action: 'add_score', detail: '10', score_points: 10, dimension: 'wikidata_alignment'},
  {row_id: 'D20_R07', priority: 7, conditions: 'lcsh_id IS NOT NULL OR fast_id IS NOT NULL', action: 'set_flag', detail: 'authority_jump = true', score_points: 0, dimension: 'authority_jump'},
  {row_id: 'D20_R08', priority: 99, conditions: 'authority_score > 100', action: 'cap_score', detail: 'authority_score = 100', score_points: 0, dimension: 'score_cap'}
] AS row
MERGE (r:SYS_DecisionRow {row_id: row.row_id})
SET r.table_id = 'D20_SCORE_discipline_authority',
    r.priority = row.priority,
    r.conditions = row.conditions,
    r.action = row.action,
    r.action_detail = row.detail,
    r.score_points = row.score_points,
    r.dimension = row.dimension,
    r.updated = datetime();

MATCH (dt:SYS_DecisionTable {table_id: 'D20_SCORE_discipline_authority'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt.table_id
MERGE (dt)-[:HAS_ROW]->(r);


// ============================================================================
// PART 3: SYS_WikidataProperty signal weights + D21 weighted link scoring
// ============================================================================

UNWIND [
  {pid: 'P279', weight: 25, role: 'taxonomy'},
  {pid: 'P31',  weight: 20, role: 'taxonomy'},
  {pid: 'P361', weight: 15, role: 'mereology'},
  {pid: 'P527', weight: 15, role: 'mereology'},
  {pid: 'P101', weight: 10, role: 'domain_definition'},
  {pid: 'P2578', weight: 10, role: 'domain_definition'},
  {pid: 'P921', weight: 5, role: 'aboutness'},
  {pid: 'P1269', weight: 5, role: 'aboutness'}
] AS p
MERGE (wp:SYS_WikidataProperty {pid: p.pid})
SET wp.signal_weight = p.weight,
    wp.semantic_role = coalesce(wp.semantic_role, p.role),
    wp.updated = datetime();

MERGE (dt21:SYS_DecisionTable {table_id: 'D21_SCORE_weighted_link_signals'})
SET dt21.label = 'Score Weighted Link Signals',
    dt21.description = 'Compute normalized link-signal score from role-specific evidence counts (taxonomy, mereology, domain_definition, aboutness).',
    dt21.hit_policy = 'ALL',
    dt21.inputs = ['cnt_taxonomy_norm', 'cnt_mereology_norm', 'cnt_domain_def_norm', 'cnt_aboutness_norm'],
    dt21.outputs = ['link_signal_score'],
    dt21.status = 'active',
    dt21.version = '1.0',
    dt21.updated = datetime();

UNWIND [
  {row_id: 'D21_R01', priority: 1, conditions: 'cnt_taxonomy_norm >= 1',  action: 'add_score', detail: '25', score_points: 25, dimension: 'taxonomy'},
  {row_id: 'D21_R02', priority: 2, conditions: 'cnt_taxonomy_norm >= 10', action: 'add_score', detail: '10', score_points: 10, dimension: 'taxonomy'},
  {row_id: 'D21_R03', priority: 3, conditions: 'cnt_mereology_norm >= 1',  action: 'add_score', detail: '15', score_points: 15, dimension: 'mereology'},
  {row_id: 'D21_R04', priority: 4, conditions: 'cnt_mereology_norm >= 10', action: 'add_score', detail: '10', score_points: 10, dimension: 'mereology'},
  {row_id: 'D21_R05', priority: 5, conditions: 'cnt_domain_def_norm >= 1',  action: 'add_score', detail: '10', score_points: 10, dimension: 'domain_definition'},
  {row_id: 'D21_R06', priority: 6, conditions: 'cnt_domain_def_norm >= 10', action: 'add_score', detail: '10', score_points: 10, dimension: 'domain_definition'},
  {row_id: 'D21_R07', priority: 7, conditions: 'cnt_aboutness_norm >= 10', action: 'add_score', detail: '5', score_points: 5, dimension: 'aboutness'},
  {row_id: 'D21_R08', priority: 8, conditions: 'cnt_aboutness_norm >= 50', action: 'add_score', detail: '5', score_points: 5, dimension: 'aboutness'},
  {row_id: 'D21_R09', priority: 99, conditions: 'link_signal_score > 100', action: 'cap_score', detail: 'link_signal_score = 100', score_points: 0, dimension: 'score_cap'}
] AS row
MERGE (r:SYS_DecisionRow {row_id: row.row_id})
SET r.table_id = 'D21_SCORE_weighted_link_signals',
    r.priority = row.priority,
    r.conditions = row.conditions,
    r.action = row.action,
    r.action_detail = row.detail,
    r.score_points = row.score_points,
    r.dimension = row.dimension,
    r.updated = datetime();

MATCH (dt:SYS_DecisionTable {table_id: 'D21_SCORE_weighted_link_signals'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt.table_id
MERGE (dt)-[:HAS_ROW]->(r);


// ============================================================================
// PART 4: Pipeline wiring (D20/D21 -> D15)
// ============================================================================

MATCH (d20:SYS_DecisionTable {table_id: 'D20_SCORE_discipline_authority'})
MATCH (d15:SYS_DecisionTable {table_id: 'D15_DETERMINE_federation_state'})
MERGE (d20)-[:FEEDS_INTO]->(d15);

MATCH (d21:SYS_DecisionTable {table_id: 'D21_SCORE_weighted_link_signals'})
MATCH (d15:SYS_DecisionTable {table_id: 'D15_DETERMINE_federation_state'})
MERGE (d21)-[:FEEDS_INTO]->(d15);


// ============================================================================
// PART 5: D9 machine-usable outputs
// ============================================================================

MERGE (d9:SYS_DecisionTable {table_id: 'D9_DETERMINE_SFA_constitution_layer'})
SET d9.outputs = ['constitution_doc_ids'],
    d9.hit_policy = coalesce(d9.hit_policy, 'UNIQUE'),
    d9.status = coalesce(d9.status, 'active'),
    d9.updated = datetime();

UNWIND [
  {row_id: 'D9_R01', facet: 'POLITICAL', docs: '["constitution_political_rr_v1"]'},
  {row_id: 'D9_R02', facet: 'MILITARY', docs: '["constitution_military_rr_v1"]'},
  {row_id: 'D9_R03', facet: 'SOCIAL', docs: '["constitution_social_rr_v1"]'}
] AS row
MERGE (r:SYS_DecisionRow {row_id: row.row_id})
SET r.table_id = 'D9_DETERMINE_SFA_constitution_layer',
    r.priority = 1,
    r.conditions = '{"facet": "' + row.facet + '"}',
    r.outputs = '{"constitution_doc_ids": ' + row.docs + '}',
    r.action = 'set_constitution_docs',
    r.action_detail = 'Return machine-usable constitution_doc_ids for ' + row.facet,
    r.updated = datetime();

MATCH (d9:SYS_DecisionTable {table_id: 'D9_DETERMINE_SFA_constitution_layer'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = d9.table_id
MERGE (d9)-[:HAS_ROW]->(r);


// ============================================================================
// VERIFICATION QUERIES
// ============================================================================

// A) Discipline kernel relationship types
MATCH (rt:SYS_RelationshipType)
WHERE rt.name STARTS WITH 'DISCIPLINE_'
RETURN rt.name, rt.source_label, rt.target_label, rt.semantic, rt.cardinality
ORDER BY rt.name;

// B) Remaining legacy Discipline rel types should be 0
MATCH (:Discipline)-[r]->(:Discipline)
WHERE type(r) IN ['SUBCLASS_OF', 'BROADER_THAN', 'PART_OF', 'HAS_PART']
RETURN type(r) AS rel_type, count(*) AS cnt;

// C) Confirm preserved Discipline connectivity in canonical names
MATCH (:Discipline)-[r]->(:Discipline)
WHERE type(r) IN ['DISCIPLINE_SUBCLASS_OF', 'DISCIPLINE_BROADER_THAN', 'DISCIPLINE_PART_OF', 'DISCIPLINE_HAS_PART']
RETURN type(r) AS rel_type, count(*) AS cnt
ORDER BY rel_type;

// D) D20 and D21 tables + rows
MATCH (dt:SYS_DecisionTable)
WHERE dt.table_id IN ['D20_SCORE_discipline_authority', 'D21_SCORE_weighted_link_signals']
OPTIONAL MATCH (dt)-[:HAS_ROW]->(r:SYS_DecisionRow)
RETURN dt.table_id, count(r) AS row_count
ORDER BY dt.table_id;

// E) D20/D21 feed into D15
MATCH (a:SYS_DecisionTable)-[:FEEDS_INTO]->(b:SYS_DecisionTable {table_id: 'D15_DETERMINE_federation_state'})
WHERE a.table_id IN ['D20_SCORE_discipline_authority', 'D21_SCORE_weighted_link_signals']
RETURN a.table_id AS feeder, b.table_id AS target;

// F) Weighted property catalog
MATCH (p:SYS_WikidataProperty)
WHERE p.pid IN ['P279','P31','P361','P527','P101','P2578','P921','P1269']
RETURN p.pid, p.semantic_role, p.signal_weight
ORDER BY p.signal_weight DESC, p.pid;
