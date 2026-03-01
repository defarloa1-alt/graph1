// ============================================================================
// CHRYSTALLUM: AGENT-FACING META-SCHEMA (Self-Describing Layer)
// ============================================================================
// File: 10_agent_meta_schema.cypher
// Purpose: Make the graph self-describing so agents can introspect
//          schema, authority tiers, valid operations, and constraints
//          BEFORE performing any work.
// Depends: Existing EntityType, Facet, SYS_Policy, SYS_Threshold nodes
// Safe: All MERGE - idempotent, non-destructive
// ============================================================================

// ============================================================================
// SECTION 1: AUTHORITY TIER DEFINITIONS (5.5-Layer Stack)
// ============================================================================
// These are the conceptual gates every piece of knowledge must pass through.
// An agent reads these to understand WHY confidence thresholds exist.

MERGE (tier1:SYS_AuthorityTier {tier: 1})
SET tier1.layer_name = 'Library Science Authority',
    tier1.position = 'Canonical Gate',
    tier1.description = 'Concepts must pass LCSH/LCC/FAST validation before entering the graph. This is the highest-confidence gate: if a concept has a Library of Congress subject heading, it is a real subject worthy of scholarly attention.',
    tier1.gates = ['LCSH', 'LCC', 'FAST', 'Dewey'],
    tier1.confidence_floor = 0.95,
    tier1.purpose = 'Is this a valid subject for a library catalog?',
    tier1.validation_method = 'Authority file lookup + fuzzy match',
    tier1.example = 'sh85115055 = Rome--History validates Roman history subjects',
    tier1.updated = datetime();

MERGE (tier2:SYS_AuthorityTier {tier: 2})
SET tier2.layer_name = 'Federation Authority',
    tier2.position = 'Linked Data Gate',
    tier2.description = 'Concepts should have a Wikidata QID and ideally a Wikipedia article. This anchors concepts to the global knowledge graph and enables property extraction for semantic reasoning.',
    tier2.gates = ['Wikidata', 'Wikipedia', 'VIAF', 'DBpedia'],
    tier2.confidence_floor = 0.90,
    tier2.purpose = 'Is this linked to the global knowledge graph?',
    tier2.validation_method = 'QID lookup + property extraction',
    tier2.example = 'Q17167 = Roman Republic provides P279/P361 hierarchy data',
    tier2.updated = datetime();

MERGE (tier2_5:SYS_AuthorityTier {tier: 2.5})
SET tier2_5.layer_name = 'Hierarchy Query Engine',
    tier2_5.position = 'Semantic Integration',
    tier2_5.description = 'Transitive Wikidata property queries that enable semantic expansion. P279 (subclass of) chains build type hierarchies. P361 (part of) chains build mereological containment. These enable contradiction detection and query expansion.',
    tier2_5.wikidata_properties = ['P31', 'P279', 'P361', 'P101', 'P2578', 'P921', 'P1269'],
    tier2_5.confidence_floor = 0.95,
    tier2_5.purpose = 'Enable semantic query expansion and contradiction detection',
    tier2_5.validation_method = 'Property traversal with transitive closure',
    tier2_5.example = 'P279 chain: battle → conflict → event (transitive subclass)',
    tier2_5.updated = datetime();

MERGE (tier3:SYS_AuthorityTier {tier: 3})
SET tier3.layer_name = 'Facet Authority',
    tier3.position = 'Discipline-Specific Knowledge',
    tier3.description = 'Queries are routed to domain expert agents via facet assignment. Each facet has specialized Wikidata anchors, terminology, and validation standards. An agent assigned to the Military facet knows different things than one assigned to Religious.',
    tier3.confidence_floor = 0.80,
    tier3.purpose = 'Route queries to domain experts with specialized terminology',
    tier3.validation_method = 'FacetReference keyword matching + Wikidata anchor alignment',
    tier3.example = 'Military facet: Q8473 (military), Q198 (war), Q192781 (military history)',
    tier3.updated = datetime();

MERGE (tier4:SYS_AuthorityTier {tier: 4})
SET tier4.layer_name = 'Subject Concept Hierarchy',
    tier4.position = 'Instance Authority',
    tier4.description = 'SubjectConcept nodes sit at the intersection of all prior tiers. Each one carries multi-tier confidence scores. These are the actual concepts agents work with day-to-day: Roman Republic, Battle of Cannae, etc.',
    tier4.node_label = 'SubjectConcept',
    tier4.confidence_floor = 0.70,
    tier4.purpose = 'Central authority-aligned concept nodes in the graph',
    tier4.validation_method = 'Authority tier scoring: Tier 1 + Tier 2 + Tier 3',
    tier4.example = 'Roman Republic: LCSH sh85115055 + Wikidata Q17167 + Political facet',
    tier4.updated = datetime();

MERGE (tier5:SYS_AuthorityTier {tier: 5})
SET tier5.layer_name = 'Agent-Discovered Concepts',
    tier5.position = 'Inference Authority',
    tier5.description = 'Claims are proposed by agents and must be validated before promotion to first-class edges. This is the discovery layer where new knowledge enters the system under human oversight. Claims carry cipher-encoded propositions, confidence scores, and full provenance.',
    tier5.node_label = 'Claim',
    tier5.confidence_floor = 0.60,
    tier5.purpose = 'Enable agent-driven knowledge discovery with human oversight',
    tier5.validation_method = 'Posterior probability + historian review',
    tier5.example = 'Battle of Cannae IN Second Punic War (posterior 0.98, promoted)',
    tier5.updated = datetime();

// Wire FEEDS_INTO chain
MATCH (t1:SYS_AuthorityTier {tier: 1})
MATCH (t2:SYS_AuthorityTier {tier: 2})
MERGE (t1)-[:FEEDS_INTO]->(t2);

MATCH (t2:SYS_AuthorityTier {tier: 2})
MATCH (t25:SYS_AuthorityTier {tier: 2.5})
MERGE (t2)-[:FEEDS_INTO]->(t25);

MATCH (t25:SYS_AuthorityTier {tier: 2.5})
MATCH (t3:SYS_AuthorityTier {tier: 3})
MERGE (t25)-[:FEEDS_INTO]->(t3);

MATCH (t3:SYS_AuthorityTier {tier: 3})
MATCH (t4:SYS_AuthorityTier {tier: 4})
MERGE (t3)-[:FEEDS_INTO]->(t4);

MATCH (t4:SYS_AuthorityTier {tier: 4})
MATCH (t5:SYS_AuthorityTier {tier: 5})
MERGE (t4)-[:FEEDS_INTO]->(t5);


// ============================================================================
// SECTION 2: ENRICH EntityType NODES WITH AGENT-READABLE METADATA
// ============================================================================
// EntityType nodes exist but only have name + description.
// Agents need: tier, required_properties, canonical_relationships,
//              identity_pattern, temporal awareness.

MATCH (et:EntityType {name: 'Human'})
SET et.tier = 4,
    et.required_properties = ['entity_id', 'name', 'qid', 'entity_type'],
    et.optional_properties = ['viaf_id', 'birth_date', 'death_date', 'gender', 'birth_date_min', 'birth_date_max', 'death_date_min', 'death_date_max'],
    et.identity_keys = ['entity_id', 'qid', 'viaf_id', 'id_hash'],
    et.canonical_outbound = ['LIVED_IN', 'LIVED_DURING', 'BORN_IN_YEAR', 'DIED_IN_YEAR', 'PART_OF_GENS', 'MEMBER_OF'],
    et.temporal = true,
    et.temporal_bbox_fields = ['birth_date_min', 'birth_date_max', 'death_date_min', 'death_date_max'],
    et.authority_sources = ['Wikidata', 'VIAF'],
    et.description = 'Individual person (historical or contemporary). Each Human has a lifespan bounding box for uncertain dates. Linked to Places, Periods, Gens, and Organizations.',
    et.updated = datetime();

MATCH (et:EntityType {name: 'Place'})
SET et.tier = 4,
    et.required_properties = ['entity_id', 'label', 'qid', 'entity_type'],
    et.optional_properties = ['pleiades_id', 'tgn_id', 'latitude', 'longitude', 'place_type', 'modern_country'],
    et.identity_keys = ['entity_id', 'qid', 'pleiades_id', 'tgn_id', 'id_hash'],
    et.canonical_outbound = ['LOCATED_IN', 'HAS_GEO_SEMANTIC_TYPE', 'INSTANCE_OF_PLACE_TYPE'],
    et.temporal = true,
    et.temporal_bbox_fields = [],
    et.authority_sources = ['Wikidata', 'Pleiades', 'TGN', 'GeoNames'],
    et.description = 'Geographic location: cities, regions, territories, natural features. Place hierarchy via LOCATED_IN. Temporal versioning via PlaceVersion for name/boundary changes.',
    et.updated = datetime();

MATCH (et:EntityType {name: 'Event'})
SET et.tier = 4,
    et.required_properties = ['entity_id', 'label', 'qid', 'event_type', 'start_date', 'entity_type'],
    et.optional_properties = ['end_date', 'start_date_min', 'start_date_max', 'end_date_min', 'end_date_max'],
    et.identity_keys = ['entity_id', 'qid', 'id_hash'],
    et.canonical_outbound = ['OCCURRED_IN_YEAR', 'LOCATED_IN', 'DURING_PERIOD'],
    et.temporal = true,
    et.temporal_bbox_fields = ['start_date_min', 'start_date_max', 'end_date_min', 'end_date_max'],
    et.authority_sources = ['Wikidata'],
    et.description = 'Historical event with temporal bounds: battles, treaties, elections, disasters. Use bounding-box overlap queries for uncertain dates.',
    et.updated = datetime();

MATCH (et:EntityType {name: 'Period'})
SET et.tier = 4,
    et.required_properties = ['entity_id', 'label', 'qid', 'start', 'end', 'entity_type'],
    et.optional_properties = ['culture', 'facet', 'earliest_start', 'latest_start', 'earliest_end', 'latest_end', 'start_date_min', 'start_date_max', 'end_date_min', 'end_date_max'],
    et.identity_keys = ['entity_id', 'qid', 'id_hash'],
    et.canonical_outbound = ['STARTS_IN_YEAR', 'ENDS_IN_YEAR', 'NARROWER_THAN'],
    et.temporal = true,
    et.temporal_bbox_fields = ['start_date_min', 'start_date_max', 'end_date_min', 'end_date_max'],
    et.authority_sources = ['Wikidata', 'PeriodO'],
    et.description = 'Historical period with named boundaries. Periods nest via NARROWER_THAN. Each period has a facet assignment (Political, Military, etc.) and culture tag.',
    et.updated = datetime();

MATCH (et:EntityType {name: 'SubjectConcept'})
SET et.tier = 4,
    et.required_properties = ['subject_id', 'label', 'id_hash', 'facet'],
    et.optional_properties = ['wikidata_qid', 'lcsh_id', 'fast_id', 'lcc_id', 'authority_tier', 'authority_confidence', 'confidence_tier_1', 'confidence_tier_2', 'confidence_tier_3'],
    et.identity_keys = ['subject_id', 'id_hash'],
    et.canonical_outbound = ['HAS_FACET', 'BROADER_THAN', 'NARROWER_THAN', 'RELATED_TO'],
    et.temporal = false,
    et.authority_sources = ['LCSH', 'FAST', 'LCC', 'Wikidata'],
    et.description = 'Authority-aligned subject/concept at the intersection of all tiers. Each SubjectConcept carries multi-tier confidence scores showing how well it is validated across Library Science, Federation, and Facet authority layers.',
    et.updated = datetime();

MATCH (et:EntityType {name: 'Claim'})
SET et.tier = 5,
    et.required_properties = ['claim_id', 'cipher', 'text', 'label', 'confidence', 'status', 'source_agent', 'timestamp', 'authority_source', 'claim_type'],
    et.optional_properties = ['posterior', 'review_status', 'reviewer', 'promoted_at'],
    et.identity_keys = ['claim_id', 'cipher', 'id_hash'],
    et.canonical_outbound = ['ABOUT_SUBJECT', 'HAS_TRACE', 'PROPOSED_BY'],
    et.temporal = false,
    et.authority_sources = [],
    et.description = 'Agent-proposed knowledge assertion with cipher-encoded proposition. Claims go through a lifecycle: proposed → reviewed → promoted/rejected. Each claim must have full provenance via RetrievalContext.',
    et.updated = datetime();

MATCH (et:EntityType {name: 'Organization'})
SET et.tier = 4,
    et.required_properties = ['entity_id', 'label', 'qid', 'entity_type'],
    et.optional_properties = ['organization_type'],
    et.identity_keys = ['entity_id', 'qid', 'id_hash'],
    et.canonical_outbound = ['LOCATED_IN'],
    et.temporal = false,
    et.authority_sources = ['Wikidata'],
    et.description = 'Political bodies, military units, religious orders, trade guilds. Human → MEMBER_OF → Organization.',
    et.updated = datetime();

MATCH (et:EntityType {name: 'Work'})
SET et.tier = 4,
    et.required_properties = ['qid'],
    et.optional_properties = ['entity_id', 'title', 'author_qid'],
    et.identity_keys = ['qid'],
    et.canonical_outbound = ['ABOUT', 'AUTHORED_BY'],
    et.temporal = false,
    et.authority_sources = ['Wikidata', 'WorldCat'],
    et.description = 'Scholarly or literary work. Used as evidence source for Claims via RetrievalContext chains.',
    et.updated = datetime();

MATCH (et:EntityType {name: 'Year'})
SET et.tier = 1,
    et.required_properties = ['year', 'label', 'entity_id'],
    et.optional_properties = ['iso', 'entity_type'],
    et.identity_keys = ['entity_id', 'year'],
    et.canonical_outbound = ['FOLLOWED_BY', 'PART_OF'],
    et.temporal = true,
    et.authority_sources = [],
    et.description = 'Temporal backbone spine node. 4025 year nodes from -2000 to 2025, no year 0. Sequential via FOLLOWED_BY. Hierarchical via PART_OF → Decade → Century → Millennium.',
    et.updated = datetime();

MATCH (et:EntityType {name: 'Decade'})
SET et.tier = 1,
    et.required_properties = ['start_year', 'end_year', 'label'],
    et.canonical_outbound = ['FOLLOWED_BY', 'PART_OF'],
    et.temporal = true,
    et.description = 'Decade-granularity temporal node. Year -[:PART_OF]-> Decade. Sequential via FOLLOWED_BY.',
    et.updated = datetime();

MATCH (et:EntityType {name: 'Century'})
SET et.tier = 1,
    et.required_properties = ['start_year', 'end_year', 'ordinal', 'label'],
    et.canonical_outbound = ['FOLLOWED_BY', 'PART_OF'],
    et.temporal = true,
    et.description = 'Century-granularity temporal node. Decade -[:PART_OF]-> Century.',
    et.updated = datetime();

MATCH (et:EntityType {name: 'Millennium'})
SET et.tier = 1,
    et.required_properties = ['start_year', 'end_year', 'ordinal', 'label'],
    et.canonical_outbound = ['FOLLOWED_BY'],
    et.temporal = true,
    et.description = 'Millennium-granularity temporal node. Century -[:PART_OF]-> Millennium.',
    et.updated = datetime();


// ============================================================================
// SECTION 3: CANONICAL RELATIONSHIP CATALOG
// ============================================================================
// Every valid edge type in the graph, with semantic meaning and constraints.

UNWIND [
  // Temporal backbone
  {name: 'FOLLOWED_BY', semantic: 'temporal_sequence', source: 'Year', target: 'Year', description: 'Sequential temporal link. Year→Year, Decade→Decade, Century→Century, Millennium→Millennium. Canonical ordering spine.', cardinality: 'one_to_one'},
  {name: 'PART_OF', semantic: 'temporal_hierarchy', source: 'Year', target: 'Decade', description: 'Temporal granularity containment. Year→Decade→Century→Millennium.', cardinality: 'many_to_one'},
  // Entity → Temporal
  {name: 'BORN_IN_YEAR', semantic: 'temporal_anchor', source: 'Human', target: 'Year', description: 'Birth year of a person.', cardinality: 'many_to_one'},
  {name: 'DIED_IN_YEAR', semantic: 'temporal_anchor', source: 'Human', target: 'Year', description: 'Death year of a person.', cardinality: 'many_to_one'},
  {name: 'STARTS_IN_YEAR', semantic: 'temporal_anchor', source: 'Period', target: 'Year', description: 'Period start year.', cardinality: 'many_to_one'},
  {name: 'ENDS_IN_YEAR', semantic: 'temporal_anchor', source: 'Period', target: 'Year', description: 'Period end year.', cardinality: 'many_to_one'},
  {name: 'OCCURRED_IN_YEAR', semantic: 'temporal_anchor', source: 'Event', target: 'Year', description: 'Event temporal anchor.', cardinality: 'many_to_one'},
  // Entity → Entity
  {name: 'LIVED_IN', semantic: 'spatial', source: 'Human', target: 'Place', description: 'Person associated with a place (residence, activity).', cardinality: 'many_to_many'},
  {name: 'LIVED_DURING', semantic: 'temporal_context', source: 'Human', target: 'Period', description: 'Person active during a historical period.', cardinality: 'many_to_many'},
  {name: 'LOCATED_IN', semantic: 'spatial_hierarchy', source: 'Place', target: 'Place', description: 'Spatial containment: Rome LOCATED_IN Italy.', cardinality: 'many_to_one'},
  {name: 'DURING_PERIOD', semantic: 'temporal_context', source: 'Event', target: 'Period', description: 'Event occurred during a named period.', cardinality: 'many_to_many'},
  {name: 'NARROWER_THAN', semantic: 'hierarchy', source: 'Period', target: 'Period', description: 'Sub-period containment: Late Republic NARROWER_THAN Republic.', cardinality: 'many_to_one'},
  {name: 'PART_OF_GENS', semantic: 'kinship', source: 'Human', target: 'Gens', description: 'Roman clan membership.', cardinality: 'many_to_one'},
  {name: 'MEMBER_OF', semantic: 'institutional', source: 'Human', target: 'Organization', description: 'Institutional membership.', cardinality: 'many_to_many'},
  // Claims pipeline
  {name: 'ABOUT_SUBJECT', semantic: 'reference', source: 'Claim', target: 'SubjectConcept', description: 'Claim references a subject concept.', cardinality: 'many_to_one'},
  {name: 'HAS_TRACE', semantic: 'provenance', source: 'Claim', target: 'RetrievalContext', description: 'Claim provenance chain: what evidence was retrieved.', cardinality: 'one_to_many'},
  {name: 'PROPOSED_BY', semantic: 'authorship', source: 'Claim', target: 'Agent', description: 'Which agent created this claim.', cardinality: 'many_to_one'},
  {name: 'EVIDENCED_BY', semantic: 'provenance', source: 'ProposedEdge', target: 'Claim', description: 'Proposed edge backed by a claim.', cardinality: 'many_to_one'},
  // Agent pipeline
  {name: 'PERFORMED', semantic: 'execution', source: 'Agent', target: 'AnalysisRun', description: 'Agent executed an analysis run.', cardinality: 'one_to_many'},
  {name: 'PRODUCED', semantic: 'output', source: 'AnalysisRun', target: 'FacetAssessment', description: 'Run produced facet assessments.', cardinality: 'one_to_many'},
  {name: 'ASSIGNED_TO_FACET', semantic: 'capability', source: 'Agent', target: 'Facet', description: 'Agent is a domain specialist for this facet.', cardinality: 'many_to_one'},
  // Geo-semantic
  {name: 'HAS_GEO_SEMANTIC_TYPE', semantic: 'classification', source: 'Place', target: 'GeoSemanticType', description: 'Semantic classification of a place: man-made, physical feature, or settlement.', cardinality: 'many_to_one'},
  {name: 'INSTANCE_OF_PLACE_TYPE', semantic: 'classification', source: 'Place', target: 'PlaceType', description: 'Specific place type classification.', cardinality: 'many_to_one'}
] AS rel
MERGE (r:SYS_RelationshipType {name: rel.name})
SET r.semantic = rel.semantic,
    r.source_label = rel.source,
    r.target_label = rel.target,
    r.description = rel.description,
    r.cardinality = rel.cardinality,
    r.updated = datetime();


// ============================================================================
// SECTION 4: WIKIDATA PROPERTY MAPPINGS (Layer 2.5 reference)
// ============================================================================

UNWIND [
  {pid: 'P31',  label: 'instance of',   semantic: 'classification',    transitive: false, usage: 'Classify individual entities by type'},
  {pid: 'P279', label: 'subclass of',   semantic: 'taxonomy',          transitive: true,  usage: 'Build type hierarchies with transitive closure'},
  {pid: 'P361', label: 'part of',       semantic: 'mereology',         transitive: true,  usage: 'Mereological containment (component-whole)'},
  {pid: 'P101', label: 'field of work', semantic: 'expertise',         transitive: false, usage: 'Map person to discipline specialization'},
  {pid: 'P2578',label: 'studies',       semantic: 'domain_definition', transitive: false, usage: 'Define what a discipline studies'},
  {pid: 'P921', label: 'main subject',  semantic: 'aboutness',         transitive: false, usage: 'Map work/source to primary topic'},
  {pid: 'P1269',label: 'facet of',      semantic: 'facet_hierarchy',   transitive: false, usage: 'Map aspect to broader concept'}
] AS wp
MERGE (w:SYS_WikidataProperty {property: wp.pid})
SET w.label = wp.label,
    w.semantic = wp.semantic,
    w.transitive = wp.transitive,
    w.usage = wp.usage,
    w.updated = datetime();


// ============================================================================
// SECTION 5: TEMPORAL QUERY PATTERNS (Agent Reference)
// ============================================================================

MERGE (tqp:SYS_QueryPattern {name: 'temporal_bbox_overlap'})
SET tqp.description = 'Standard overlap query for uncertain dates. Use this pattern whenever querying events, periods, or lifespans with bounding-box temporal fields.',
    tqp.cypher_template = 'WHERE entity.start_date_min <= $target_end AND entity.end_date_max >= $target_start',
    tqp.applicable_to = ['Event', 'Period', 'Human'],
    tqp.field_mapping = 'Event: start_date_min/end_date_max | Period: start_date_min/end_date_max OR earliest_start/latest_end | Human: birth_date_min/death_date_max',
    tqp.updated = datetime();

MERGE (tqp2:SYS_QueryPattern {name: 'year_backbone_traversal'})
SET tqp2.description = 'Walk the FOLLOWED_BY chain between Year nodes to find all years in a range. Use PART_OF to jump to coarser granularity.',
    tqp2.cypher_template = 'MATCH (start:Year {year: $from})-[:FOLLOWED_BY*0..]->(y:Year) WHERE y.year <= $to RETURN y',
    tqp2.applicable_to = ['Year'],
    tqp2.updated = datetime();


// ============================================================================
// SECTION 6: VALIDATION RULES (Agent Self-Checks)
// ============================================================================

UNWIND [
  {name: 'entity_id_uniqueness', applies_to: 'ALL', severity: 'CRITICAL', rationale: 'Every first-class entity must have unique entity_id or subject_id.', check: 'Verify no duplicate entity_id values within a label.'},
  {name: 'claim_cipher_required', applies_to: 'Claim', severity: 'CRITICAL', rationale: 'Claims must carry a cipher-encoded machine-parseable proposition.', check: 'All Claim nodes must have non-null cipher property.'},
  {name: 'year_uniqueness', applies_to: 'Year', severity: 'CRITICAL', rationale: 'Each year exists exactly once in the temporal spine.', check: 'No duplicate Year.year values.'},
  {name: 'no_year_zero', applies_to: 'Year', severity: 'CRITICAL', rationale: 'Historical convention: year 0 does not exist.', check: 'MATCH (y:Year {year:0}) should return 0 rows.'},
  {name: 'year_chain_integrity', applies_to: 'Year', severity: 'HIGH', rationale: 'Every year except the last (2025) must have a FOLLOWED_BY successor.', check: 'MATCH (y:Year) WHERE NOT (y)-[:FOLLOWED_BY]->() AND y.year <> 2025 should return 0.'},
  {name: 'claim_provenance_required', applies_to: 'Claim', severity: 'HIGH', rationale: 'Every claim must link to at least one RetrievalContext for auditability.', check: 'MATCH (c:Claim) WHERE NOT (c)-[:HAS_TRACE]->() should return 0.'},
  {name: 'agent_facet_assignment', applies_to: 'Agent', severity: 'HIGH', rationale: 'Every active agent must be assigned to at least one facet.', check: 'MATCH (a:Agent) WHERE NOT (a)-[:ASSIGNED_TO_FACET]->() should return 0.'},
  {name: 'temporal_bbox_consistency', applies_to: 'Event', severity: 'MEDIUM', rationale: 'Temporal min must not exceed temporal max.', check: 'start_date_min <= start_date_max AND end_date_min <= end_date_max.'},
  {name: 'facet_count', applies_to: 'Facet', severity: 'MEDIUM', rationale: 'Chrystallum defines exactly 18 canonical facets.', check: 'MATCH (f:Facet) RETURN count(f) = 18.'}
] AS vr
MERGE (v:SYS_ValidationRule {name: vr.name})
SET v.applies_to = vr.applies_to,
    v.severity = vr.severity,
    v.rationale = vr.rationale,
    v.check_description = vr.check,
    v.updated = datetime();


// ============================================================================
// VERIFICATION
// ============================================================================

MATCH (at:SYS_AuthorityTier) RETURN 'AuthorityTiers' AS type, count(at) AS count
UNION ALL
MATCH (rt:SYS_RelationshipType) RETURN 'RelationshipTypes' AS type, count(rt) AS count
UNION ALL
MATCH (wp:SYS_WikidataProperty) RETURN 'WikidataProperties' AS type, count(wp) AS count
UNION ALL
MATCH (qp:SYS_QueryPattern) RETURN 'QueryPatterns' AS type, count(qp) AS count
UNION ALL
MATCH (vr:SYS_ValidationRule) RETURN 'ValidationRules' AS type, count(vr) AS count;
