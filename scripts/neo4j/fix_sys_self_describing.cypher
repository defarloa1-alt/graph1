// ============================================================================
// FIX SYS_ SELF-DESCRIBING SUBGRAPH
// ============================================================================
// Purpose: Wire SYS_Threshold → SYS_DecisionTable, link orphan SYS_FederationSource,
//          normalize SYS_DecisionTable (table_id/name), add SYS_SchemaRegistry.
// Run: python scripts/neo4j/run_cypher_file.py scripts/neo4j/fix_sys_self_describing.cypher
// ============================================================================

// ---------------------------------------------------------------------------
// 1. Normalize SYS_DecisionTable: set table_id from name where table_id is null
// ---------------------------------------------------------------------------
MATCH (dt:SYS_DecisionTable)
WHERE dt.table_id IS NULL AND dt.name IS NOT NULL
SET dt.table_id = dt.name;

// ---------------------------------------------------------------------------
// 2. Link SYS_Threshold to SYS_DecisionTable via USES_THRESHOLD
//    (dt)-[:USES_THRESHOLD]->(t)
// ---------------------------------------------------------------------------
MATCH (t:SYS_Threshold)
WHERE t.decision_table IS NOT NULL
MATCH (dt:SYS_DecisionTable {table_id: t.decision_table})
MERGE (dt)-[:USES_THRESHOLD]->(t);

// ---------------------------------------------------------------------------
// 3. Link orphan SYS_FederationSource to SYS_FederationRegistry
//    (Open Syllabus, Open Library, OpenAlex, Perseus Digital Library)
// ---------------------------------------------------------------------------
MATCH (fr:SYS_FederationRegistry)
MATCH (fs:SYS_FederationSource)
WHERE NOT (fr)-[:CONTAINS]->(fs)
MERGE (fr)-[:CONTAINS]->(fs);

// ---------------------------------------------------------------------------
// 4. Add SYS_SchemaRegistry and connect Chrystallum
// ---------------------------------------------------------------------------
MERGE (sr:SYS_SchemaRegistry {system: true, label: 'SchemaRegistry'})
WITH sr
MATCH (c:Chrystallum)
WHERE NOT (c)-[:HAS_SCHEMA]->(sr)
MERGE (c)-[:HAS_SCHEMA]->(sr);

// ---------------------------------------------------------------------------
// 5. Create SYS_NodeType for core domain labels (minimal data dictionary)
// ---------------------------------------------------------------------------
UNWIND [
  {name: 'Entity', description: 'Core entity (person, place, work, etc.)'},
  {name: 'Place', description: 'Geographic location'},
  {name: 'SubjectConcept', description: 'Subject concept in Roman Republic ontology'},
  {name: 'Position', description: 'Office or magistracy'},
  {name: 'Discipline', description: 'Academic discipline'},
  {name: 'Year', description: 'Temporal year node'},
  {name: 'Periodo_Period', description: 'PeriodO period'},
  {name: 'Pleiades_Place', description: 'Pleiades place'},
  {name: 'Facet', description: 'Facet dimension'},
  {name: 'Claim', description: 'Proposed or promoted claim'}
] AS spec
MERGE (nt:SYS_NodeType {name: spec.name})
SET nt.description = spec.description, nt.system = true
WITH nt
MATCH (sr:SYS_SchemaRegistry)
MERGE (sr)-[:CONTAINS]->(nt);

// ---------------------------------------------------------------------------
// 6. Create SYS_EdgeType for key relationship types
// ---------------------------------------------------------------------------
UNWIND [
  {name: 'MEMBER_OF', from_label: 'Entity', to_label: 'SubjectConcept'},
  {name: 'POSITION_HELD', from_label: 'Entity', to_label: 'Position'},
  {name: 'BROADER_THAN', from_label: 'SubjectConcept', to_label: 'SubjectConcept'},
  {name: 'ALIGNED_WITH_GEO_BACKBONE', from_label: 'Pleiades_Place', to_label: 'Place'},
  {name: 'HAS_PRIMARY_FACET', from_label: 'SYS_PropertyMapping', to_label: 'Facet'},
  {name: 'GOVERNED_BY', from_label: 'SYS_Policy', to_label: 'SYS_DecisionTable'},
  {name: 'USES_THRESHOLD', from_label: 'SYS_DecisionTable', to_label: 'SYS_Threshold'},
  {name: 'CONTAINS', from_label: 'SYS_FederationRegistry', to_label: 'SYS_FederationSource'}
] AS spec
MERGE (et:SYS_EdgeType {name: spec.name})
SET et.from_label = spec.from_label, et.to_label = spec.to_label, et.system = true
WITH et
MATCH (sr:SYS_SchemaRegistry)
MERGE (sr)-[:CONTAINS]->(et);
