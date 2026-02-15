// ================================================================
// META-SCHEMA GRAPH: Self-Describing Architecture Layer
// ================================================================
// Purpose: Enable agent introspection of Chrystallum architecture
// Date: 2026-02-15
// Status: Foundation for agent self-awareness
//
// Architecture: Option 3 (Meta-Graph) + Option 1 (Curated Docs)
// - Agents query this graph to understand available schema
// - Documentation explains WHY decisions were made
// - This graph describes WHAT the schema IS
//
// Usage by agents:
//   MATCH (n:_Schema:NodeLabel) RETURN n             // What labels exist?
//   MATCH (r:_Schema:RelationshipType) RETURN r      // What relationships?
//   MATCH (f:_Schema:FacetReference) RETURN f        // What facets?
//   MATCH (t:_Schema:AuthorityTier) RETURN t         // What layers?
// ================================================================

// ================================================================
// SECTION 1: AUTHORITY TIER DEFINITIONS (5.5-Layer Stack)
// ================================================================

// Layer 1: Library Science Authority (Canonical Gate)
CREATE (tier1:_Schema:AuthorityTier {
  tier: 1,
  layer_name: "Library Science Authority",
  position: "Canonical Gate",
  description: "Concepts must pass LCSH/LCC/FAST validation",
  gates: ["LCSH", "LCC", "FAST", "Dewey"],
  confidence_floor: 0.95,
  purpose: "Is this a valid subject for a library catalog?",
  validation_method: "Authority file lookup + fuzzy match",
  example: "sh85115055 = Rome--History validates Roman history subjects"
})

// Layer 2: Federation Authority (Linked Data Gate)
CREATE (tier2:_Schema:AuthorityTier {
  tier: 2,
  layer_name: "Federation Authority",
  position: "Linked Data Gate",
  description: "Concepts should have Wikidata QID + Wikipedia article",
  gates: ["Wikidata", "Wikipedia", "VIAF", "DBpedia"],
  confidence_floor: 0.90,
  purpose: "Is this linked to the global knowledge graph?",
  validation_method: "QID lookup + property extraction",
  example: "Q17167 = Roman Republic provides P279/P361 hierarchy data"
})

// Layer 2.5: Hierarchy Query Engine (Semantic Integration)
CREATE (tier2_5:_Schema:AuthorityTier {
  tier: 2.5,
  layer_name: "Hierarchy Query Engine",
  position: "Semantic Integration",
  description: "Transitive Wikidata property queries for semantic expansion",
  wikidata_properties: ["P31", "P279", "P361", "P101", "P2578", "P921", "P1269"],
  confidence_floor: 0.95,
  purpose: "Enable semantic query expansion and contradiction detection",
  validation_method: "Property traversal with transitive closure",
  example: "P279 chain: battle → conflict → event (transitive subclass)"
})

// Layer 3: Facet Authority (Discipline-Specific Knowledge)
CREATE (tier3:_Schema:AuthorityTier {
  tier: 3,
  layer_name: "Facet Authority",
  position: "Discipline-Specific Knowledge",
  description: "17 domain experts with specialized Wikidata anchors",
  facets: ["military", "political", "economic", "religious", "social", "cultural", "artistic", "intellectual", "linguistic", "geographic", "environmental", "technological", "demographic", "diplomatic", "scientific", "archaeological", "communication"],
  confidence_floor: 0.80,
  purpose: "Route queries to domain experts with specialized terminology",
  validation_method: "FacetReference keyword matching + Wikidata anchor alignment",
  example: "Military facet: Q8473 (military), Q198 (war), Q192781 (military history)"
})

// Layer 4: Subject Concept Hierarchy (Instance Authority)
CREATE (tier4:_Schema:AuthorityTier {
  tier: 4,
  layer_name: "Subject Concept Hierarchy",
  position: "Instance Authority",
  description: "SubjectConcept nodes with multi-tier authority alignment",
  node_label: "SubjectConcept",
  confidence_floor: 0.70,
  purpose: "Central authority-aligned concept nodes in the graph",
  validation_method: "Authority tier scoring: Tier 1 + Tier 2 + Tier 3",
  example: "Roman Republic: LCSH sh85115055 + Wikidata Q17167 + Political facet"
})

// Layer 5: Agent-Discovered Concepts (Inference Authority)
CREATE (tier5:_Schema:AuthorityTier {
  tier: 5,
  layer_name: "Agent-Discovered Concepts",
  position: "Inference Authority",
  description: "Claims proposed by agents, validated by historians",
  node_label: "Claim",
  confidence_floor: 0.60,
  purpose: "Enable agent-driven knowledge discovery with human oversight",
  validation_method: "Posterior probability + historian review",
  example: "Battle of Cannae IN Second Punic War (posterior 0.98, promoted)"
})

// Link tier relationships
MATCH (t1:_Schema:AuthorityTier {tier: 1})
MATCH (t2:_Schema:AuthorityTier {tier: 2})
MATCH (t2_5:_Schema:AuthorityTier {tier: 2.5})
MATCH (t3:_Schema:AuthorityTier {tier: 3})
MATCH (t4:_Schema:AuthorityTier {tier: 4})
MATCH (t5:_Schema:AuthorityTier {tier: 5})
CREATE (t1)-[:FEEDS_INTO]->(t2)
CREATE (t2)-[:FEEDS_INTO]->(t2_5)
CREATE (t2_5)-[:FEEDS_INTO]->(t3)
CREATE (t3)-[:FEEDS_INTO]->(t4)
CREATE (t4)-[:FEEDS_INTO]->(t5);

// ================================================================
// SECTION 2: NODE LABEL DEFINITIONS (First-Class Labels)
// ================================================================
// Source: Key Files/Main nodes.md (canonical)
// Status: 14 first-class node labels (verified 2026-02-14)

CREATE (nl_subject:_Schema:NodeLabel {
  name: "SubjectConcept",
  tier: 4,
  definition: "Authority-aligned subject/concept from LCSH/Wikidata/FAST",
  purpose: "Central concept nodes with multi-tier authority validation",
  required_properties: ["id_hash", "label", "description"],
  optional_properties: ["wikidata_qid", "lcsh_id", "fast_id", "lcc_id", "confidence_tier_1", "confidence_tier_2", "confidence_tier_3"],
  example: "Roman Republic: sh85115055 + Q17167",
  cardinality: "many",
  temporal: false,
  authority_sources: ["LCSH", "Wikidata", "FAST"]
})

CREATE (nl_human:_Schema:NodeLabel {
  name: "Human",
  tier: 4,
  definition: "Individual person (historical or contemporary)",
  purpose: "Represent people as agents, experts, authors, subjects",
  required_properties: ["id_hash", "name"],
  optional_properties: ["wikidata_qid", "birth_year", "death_year", "p101_field_of_work"],
  example: "Julius Caesar: Q1048",
  cardinality: "many",
  temporal: true,
  authority_sources: ["Wikidata", "VIAF"]
})

CREATE (nl_event:_Schema:NodeLabel {
  name: "Event",
  tier: 4,
  definition: "Historical event with temporal bounds",
  purpose: "Represent occurrences in time (battles, treaties, elections)",
  required_properties: ["id_hash", "label", "event_type"],
  optional_properties: ["wikidata_qid", "start_year", "end_year", "location"],
  example: "Battle of Cannae: Q13377",
  cardinality: "many",
  temporal: true,
  authority_sources: ["Wikidata"]
})

CREATE (nl_place:_Schema:NodeLabel {
  name: "Place",
  tier: 4,
  definition: "Geographic location (cities, regions, territories)",
  purpose: "Represent spatial entities with temporal versioning potential",
  required_properties: ["id_hash", "name"],
  optional_properties: ["wikidata_qid", "lat", "lon", "tgn_id", "pleiades_id"],
  example: "Rome: Q220",
  cardinality: "many",
  temporal: true,
  authority_sources: ["Wikidata", "TGN", "Pleiades", "GeoNames"]
})

CREATE (nl_period:_Schema:NodeLabel {
  name: "Period",
  tier: 4,
  definition: "Historical period with named boundaries",
  purpose: "Represent eras, ages, epochs (broader than single events)",
  required_properties: ["id_hash", "label", "start_year", "end_year"],
  optional_properties: ["wikidata_qid", "period_type"],
  example: "Roman Republic: Q17167",
  cardinality: "many",
  temporal: true,
  authority_sources: ["Wikidata", "PeriodO"]
})

CREATE (nl_year:_Schema:NodeLabel {
  name: "Year",
  tier: 1,
  definition: "Temporal backbone spine node (calendrical)",
  purpose: "Anchor events to precise years (-2000 to 2025, no year 0)",
  required_properties: ["year", "label"],
  optional_properties: ["decade", "century", "millennium"],
  example: "Year -216 (216 BCE)",
  cardinality: 4025,
  temporal: true,
  authority_sources: ["Internal calendrical logic"]
})

CREATE (nl_claim:_Schema:NodeLabel {
  name: "Claim",
  tier: 5,
  definition: "Agent-proposed statement with validation lifecycle",
  purpose: "Agent-discovered knowledge pending historian review",
  required_properties: ["claim_id", "cipher", "status", "posterior", "proposed_by_agent"],
  optional_properties: ["promoted_at", "rejected_at", "reviewed_by", "evidence"],
  example: "Claim: Cannae IN Second_Punic_War (posterior 0.98)",
  cardinality: "many",
  temporal: true,
  authority_sources: ["Agent inference + historian validation"]
})

CREATE (nl_organization:_Schema:NodeLabel {
  name: "Organization",
  tier: 4,
  definition: "Formal organization or institution",
  purpose: "Represent groups, institutions, administrative bodies",
  required_properties: ["id_hash", "name"],
  optional_properties: ["wikidata_qid", "founded_year", "dissolved_year"],
  example: "Roman Senate: Q82277",
  cardinality: "many",
  temporal: true,
  authority_sources: ["Wikidata"]
})

CREATE (nl_institution:_Schema:NodeLabel {
  name: "Institution",
  tier: 4,
  definition: "Long-standing social/political institution",
  purpose: "Represent enduring social structures (Senate, Church, Universities)",
  required_properties: ["id_hash", "name"],
  optional_properties: ["wikidata_qid", "institution_type"],
  example: "Roman Republic (institution): Q17167",
  cardinality: "many",
  temporal: true,
  authority_sources: ["Wikidata"]
})

CREATE (nl_dynasty:_Schema:NodeLabel {
  name: "Dynasty",
  tier: 4,
  definition: "Hereditary succession line",
  purpose: "Represent ruling families and succession patterns",
  required_properties: ["id_hash", "name"],
  optional_properties: ["wikidata_qid", "start_year", "end_year"],
  example: "Julio-Claudian dynasty: Q170284",
  cardinality: "few",
  temporal: true,
  authority_sources: ["Wikidata"]
})

CREATE (nl_gens:_Schema:NodeLabel {
  name: "Gens",
  tier: 4,
  definition: "Roman clan/family group",
  purpose: "Represent Roman social kinship structures",
  required_properties: ["id_hash", "name"],
  optional_properties: ["wikidata_qid"],
  example: "Gens Julia: Q232976",
  cardinality: "few",
  temporal: false,
  authority_sources: ["Wikidata"]
})

CREATE (nl_praenomen:_Schema:NodeLabel {
  name: "Praenomen",
  tier: 4,
  definition: "Roman first name",
  purpose: "Represent Roman naming conventions (given name)",
  required_properties: ["id_hash", "name"],
  optional_properties: ["abbreviation"],
  example: "Gaius (C.)",
  cardinality: "few",
  temporal: false,
  authority_sources: ["Historical"]
})

CREATE (nl_cognomen:_Schema:NodeLabel {
  name: "Cognomen",
  tier: 4,
  definition: "Roman family name/nickname",
  purpose: "Represent Roman naming conventions (family branch)",
  required_properties: ["id_hash", "name"],
  optional_properties: ["meaning"],
  example: "Caesar",
  cardinality: "few",
  temporal: false,
  authority_sources: ["Historical"]
})

CREATE (nl_legal:_Schema:NodeLabel {
  name: "LegalRestriction",
  tier: 4,
  definition: "Legal constraint or prohibition",
  purpose: "Represent laws, edicts, legal codes, restrictions",
  required_properties: ["id_hash", "description"],
  optional_properties: ["wikidata_qid", "enacted_year", "repealed_year"],
  example: "Lex Canuleia: Q844753",
  cardinality: "few",
  temporal: true,
  authority_sources: ["Wikidata"]
});

// Link node labels to authority tiers
MATCH (nl:_Schema:NodeLabel)
MATCH (tier:_Schema:AuthorityTier {tier: nl.tier})
CREATE (nl)-[:VALIDATED_BY]->(tier);

// ================================================================
// SECTION 3: RELATIONSHIP TYPE DEFINITIONS
// ================================================================
// Source: Relationships/relationship_types_registry_master.csv

CREATE (rt_aligned_lcsh:_Schema:RelationshipType {
  name: "ALIGNED_WITH_LCSH",
  source_label: "SubjectConcept",
  target_label: "SubjectConcept",
  cardinality: "many-to-one",
  direction: "outgoing",
  required_properties: ["lcsh_id", "confidence"],
  semantic: "authority_alignment",
  tier: 1,
  description: "Links SubjectConcept to LCSH authority file",
  example: "[Roman_Republic]-[:ALIGNED_WITH_LCSH {lcsh_id: 'sh85115055'}]->[LCSH_Node]"
})

CREATE (rt_aligned_wikidata:_Schema:RelationshipType {
  name: "ALIGNED_WITH_WIKIDATA",
  source_label: "SubjectConcept",
  target_label: "SubjectConcept",
  cardinality: "many-to-one",
  direction: "outgoing",
  required_properties: ["wikidata_qid", "confidence"],
  semantic: "federation_alignment",
  tier: 2,
  description: "Links SubjectConcept to Wikidata entity",
  example: "[Roman_Republic]-[:ALIGNED_WITH_WIKIDATA {qid: 'Q17167'}]->[Wikidata_Node]"
})

CREATE (rt_instance_of:_Schema:RelationshipType {
  name: "INSTANCE_OF",
  source_label: "SubjectConcept",
  target_label: "SubjectConcept",
  cardinality: "many-to-many",
  direction: "outgoing",
  required_properties: ["wikidata_property"],
  semantic: "classification",
  tier: 2.5,
  wikidata_property: "P31",
  transitive: false,
  description: "Instance-of relationship (non-transitive)",
  example: "[Battle_of_Cannae]-[:INSTANCE_OF {p: 'P31'}]->[Battle]"
})

CREATE (rt_subclass_of:_Schema:RelationshipType {
  name: "SUBCLASS_OF",
  source_label: "SubjectConcept",
  target_label: "SubjectConcept",
  cardinality: "many-to-many",
  direction: "outgoing",
  required_properties: ["wikidata_property"],
  semantic: "taxonomy",
  tier: 2.5,
  wikidata_property: "P279",
  transitive: true,
  description: "Subclass hierarchy (transitive)",
  example: "[Battle]-[:SUBCLASS_OF {p: 'P279'}]->[Conflict]"
})

CREATE (rt_part_of:_Schema:RelationshipType {
  name: "PART_OF",
  source_label: "Year|Event|Place",
  target_label: "Decade|Period|Place",
  cardinality: "many-to-one",
  direction: "outgoing",
  required_properties: [],
  semantic: "mereology",
  tier: 1,
  wikidata_property: "P361",
  transitive: true,
  description: "Part-of hierarchy (transitive mereological)",
  example: "[Year_-216]-[:PART_OF]->[Decade_-210]"
})

CREATE (rt_occurred_in:_Schema:RelationshipType {
  name: "OCCURRED_IN",
  source_label: "Event",
  target_label: "Year|Period|Place",
  cardinality: "many-to-many",
  direction: "outgoing",
  required_properties: [],
  semantic: "temporal_spatial_grounding",
  tier: 4,
  description: "Event grounding to time/space",
  example: "[Battle_of_Cannae]-[:OCCURRED_IN]->[Year_-216]"
})

CREATE (rt_field_of_work:_Schema:RelationshipType {
  name: "FIELD_OF_WORK",
  source_label: "Human",
  target_label: "SubjectConcept",
  cardinality: "many-to-many",
  direction: "outgoing",
  required_properties: [],
  semantic: "expertise",
  tier: 2.5,
  wikidata_property: "P101",
  description: "Person's area of specialization",
  example: "[Polybius]-[:FIELD_OF_WORK {p: 'P101'}]->[Military_History]"
})

CREATE (rt_main_subject:_Schema:RelationshipType {
  name: "MAIN_SUBJECT",
  source_label: "SubjectConcept",
  target_label: "SubjectConcept",
  cardinality: "many-to-many",
  direction: "outgoing",
  required_properties: [],
  semantic: "aboutness",
  tier: 2.5,
  wikidata_property: "P921",
  description: "Work/source primary topic",
  example: "[Histories_Polybius]-[:MAIN_SUBJECT {p: 'P921'}]->[Second_Punic_War]"
})

CREATE (rt_proposed_by:_Schema:RelationshipType {
  name: "PROPOSED_BY",
  source_label: "Claim",
  target_label: "SubjectConcept",
  cardinality: "many-to-one",
  direction: "outgoing",
  required_properties: ["agent_id", "timestamp"],
  semantic: "provenance",
  tier: 5,
  description: "Claim authorship attribution",
  example: "[Claim_123]-[:PROPOSED_BY {agent: 'military_agent'}]->[Agent_Node]"
})

CREATE (rt_facet_reference:_Schema:RelationshipType {
  name: "HAS_FACET",
  source_label: "SubjectConcept",
  target_label: "FacetReference",
  cardinality: "many-to-many",
  direction: "outgoing",
  required_properties: ["confidence"],
  semantic: "facet_classification",
  tier: 3,
  description: "Link concept to discipline facet",
  example: "[Roman_Military]-[:HAS_FACET {confidence: 0.95}]->[Military_Facet]"
})

CREATE (rt_followed_by:_Schema:RelationshipType {
  name: "FOLLOWED_BY",
  source_label: "Year",
  target_label: "Year",
  cardinality: "one-to-one",
  direction: "outgoing",
  required_properties: [],
  semantic: "temporal_sequence",
  tier: 1,
  description: "Year chain (unidirectional temporal spine)",
  example: "[Year_-217]-[:FOLLOWED_BY]->[Year_-216]"
});

// Link relationship types to node labels
MATCH (rt:_Schema:RelationshipType)
MATCH (nl_source:_Schema:NodeLabel)
WHERE nl_source.name IN split(rt.source_label, "|")
CREATE (rt)-[:SOURCE_LABEL]->(nl_source)
WITH rt
MATCH (nl_target:_Schema:NodeLabel)
WHERE nl_target.name IN split(rt.target_label, "|")
CREATE (rt)-[:TARGET_LABEL]->(nl_target);

// ================================================================
// SECTION 4: TAG EXISTING FACET REFERENCES AS META-SCHEMA
// ================================================================
// FacetReference nodes already exist from facet_registry_master.json
// Tag them as _Schema nodes for agent introspection

MATCH (f:FacetReference)
SET f:_Schema
SET f.tier = 3
SET f.layer = "Facet Authority"
SET f.purpose = "Domain-specific query routing and terminology expertise";

// ================================================================
// SECTION 5: PROPERTY DEFINITIONS (Required vs Optional)
// ================================================================

// SubjectConcept properties
MATCH (nl:_Schema:NodeLabel {name: "SubjectConcept"})
CREATE (nl)-[:HAS_REQUIRED_PROPERTY]->(:_Schema:Property {
  name: "id_hash",
  type: "String",
  purpose: "Unique identifier (SHA256 hash)",
  example: "sha256('Roman_Republic')"
})
CREATE (nl)-[:HAS_REQUIRED_PROPERTY]->(:_Schema:Property {
  name: "label",
  type: "String",
  purpose: "Human-readable name",
  example: "Roman Republic"
})
CREATE (nl)-[:HAS_REQUIRED_PROPERTY]->(:_Schema:Property {
  name: "description",
  type: "String",
  purpose: "Brief definition",
  example: "Ancient Roman state (509-27 BCE)"
})
CREATE (nl)-[:HAS_OPTIONAL_PROPERTY]->(:_Schema:Property {
  name: "wikidata_qid",
  type: "String",
  purpose: "Wikidata entity identifier",
  example: "Q17167"
})
CREATE (nl)-[:HAS_OPTIONAL_PROPERTY]->(:_Schema:Property {
  name: "lcsh_id",
  type: "String",
  purpose: "Library of Congress Subject Heading",
  example: "sh85115055"
})
CREATE (nl)-[:HAS_OPTIONAL_PROPERTY]->(:_Schema:Property {
  name: "fast_id",
  type: "String",
  purpose: "FAST authority identifier",
  example: "fst01352255"
});

// Claim properties
MATCH (nl:_Schema:NodeLabel {name: "Claim"})
CREATE (nl)-[:HAS_REQUIRED_PROPERTY]->(:_Schema:Property {
  name: "claim_id",
  type: "String",
  purpose: "Unique claim identifier",
  example: "claim_military_20260215_001"
})
CREATE (nl)-[:HAS_REQUIRED_PROPERTY]->(:_Schema:Property {
  name: "cipher",
  type: "String",
  purpose: "Structured claim format: [subject]-[predicate]-[object]",
  example: "Cannae-OCCURRED_IN-Second_Punic_War"
})
CREATE (nl)-[:HAS_REQUIRED_PROPERTY]->(:_Schema:Property {
  name: "status",
  type: "String",
  purpose: "Lifecycle status: proposed|validated|promoted|rejected",
  example: "proposed"
})
CREATE (nl)-[:HAS_REQUIRED_PROPERTY]->(:_Schema:Property {
  name: "posterior",
  type: "Float",
  purpose: "Bayesian confidence score (0.0-1.0)",
  example: "0.95"
})
CREATE (nl)-[:HAS_REQUIRED_PROPERTY]->(:_Schema:Property {
  name: "proposed_by_agent",
  type: "String",
  purpose: "Agent identifier that generated claim",
  example: "military_agent"
});

// Year properties
MATCH (nl:_Schema:NodeLabel {name: "Year"})
CREATE (nl)-[:HAS_REQUIRED_PROPERTY]->(:_Schema:Property {
  name: "year",
  type: "Integer",
  purpose: "Year number (BCE negative, no zero)",
  example: "-216"
})
CREATE (nl)-[:HAS_REQUIRED_PROPERTY]->(:_Schema:Property {
  name: "label",
  type: "String",
  purpose: "Human-readable year label",
  example: "216 BCE"
});

// ================================================================
// SECTION 6: VALIDATION RULES (Constraints and Business Logic)
// ================================================================

CREATE (vr_id_hash:_Schema:ValidationRule {
  name: "id_hash_uniqueness",
  applies_to: "SubjectConcept|Human|Event|Place|Period|Organization|Institution",
  rule_type: "uniqueness_constraint",
  cypher_check: "CREATE CONSTRAINT FOR (n:SubjectConcept) REQUIRE n.id_hash IS UNIQUE",
  rationale: "Every first-class entity must have unique identifier",
  severity: "CRITICAL"
})

CREATE (vr_claim_cipher:_Schema:ValidationRule {
  name: "claim_cipher_required",
  applies_to: "Claim",
  rule_type: "property_existence",
  cypher_check: "CREATE CONSTRAINT FOR (c:Claim) REQUIRE c.cipher IS NOT NULL",
  rationale: "Claims must be machine-parseable",
  severity: "CRITICAL"
})

CREATE (vr_year_uniqueness:_Schema:ValidationRule {
  name: "year_uniqueness",
  applies_to: "Year",
  rule_type: "uniqueness_constraint",
  cypher_check: "CREATE CONSTRAINT FOR (y:Year) REQUIRE y.year IS UNIQUE",
  rationale: "Each year exists once in temporal spine",
  severity: "CRITICAL"
})

CREATE (vr_no_year_zero:_Schema:ValidationRule {
  name: "no_year_zero",
  applies_to: "Year",
  rule_type: "business_logic",
  cypher_check: "MATCH (y:Year {year: 0}) RETURN count(y) = 0",
  rationale: "Historical convention: no year 0 exists",
  severity: "CRITICAL"
})

CREATE (vr_followed_by_chain:_Schema:ValidationRule {
  name: "year_chain_integrity",
  applies_to: "Year",
  rule_type: "graph_structure",
  cypher_check: "MATCH (y:Year) WHERE NOT (y)-[:FOLLOWED_BY]->() AND y.year <> 2025 RETURN count(y) = 0",
  rationale: "Every year except 2025 should have FOLLOWED_BY successor",
  severity: "HIGH"
})

CREATE (vr_tier_scoring:_Schema:ValidationRule {
  name: "subject_tier_scoring",
  applies_to: "SubjectConcept",
  rule_type: "business_logic",
  cypher_check: "MATCH (sc:SubjectConcept) WHERE sc.lcsh_id IS NOT NULL RETURN sc.confidence_tier_1 >= 0.95",
  rationale: "LCSH validation requires 0.95+ confidence",
  severity: "MEDIUM"
})

CREATE (vr_facet_count:_Schema:ValidationRule {
  name: "facet_registry_count",
  applies_to: "FacetReference",
  rule_type: "cardinality",
  cypher_check: "MATCH (f:FacetReference) RETURN count(f) = 17",
  rationale: "Chrystallum has exactly 17 discipline facets",
  severity: "MEDIUM"
});

// ================================================================
// SECTION 7: WIKIDATA PROPERTY MAPPINGS (Layer 2.5)
// ================================================================

CREATE (wp_p31:_Schema:WikidataProperty {
  property: "P31",
  label: "instance of",
  semantic: "classification",
  transitive: false,
  tier: 2.5,
  usage: "Classify individual entities by type",
  example: "Battle of Cannae (Q13377) P31 battle (Q178561)",
  agent_usage: "Entity classification, semantic queries"
})

CREATE (wp_p279:_Schema:WikidataProperty {
  property: "P279",
  label: "subclass of",
  semantic: "taxonomy",
  transitive: true,
  tier: 2.5,
  usage: "Build type hierarchies with transitive closure",
  example: "battle (Q178561) P279 conflict (Q180684) P279 event",
  agent_usage: "Query expansion, contradiction detection, semantic inference"
})

CREATE (wp_p361:_Schema:WikidataProperty {
  property: "P361",
  label: "part of",
  semantic: "mereology",
  transitive: true,
  tier: 2.5,
  usage: "Mereological containment (component-whole)",
  example: "Battle of Cannae P361 Second Punic War P361 Punic Wars",
  agent_usage: "Hierarchical entity nesting, period containment"
})

CREATE (wp_p101:_Schema:WikidataProperty {
  property: "P101",
  label: "field of work",
  semantic: "expertise",
  transitive: false,
  tier: 2.5,
  usage: "Map person to discipline specialization",
  example: "Polybius (Q7345) P101 military history (Q188507)",
  agent_usage: "Expert discovery, claim sourcing, historian routing"
})

CREATE (wp_p2578:_Schema:WikidataProperty {
  property: "P2578",
  label: "studies",
  semantic: "domain_definition",
  transitive: false,
  tier: 2.5,
  usage: "Define what a discipline studies",
  example: "military history P2578 warfare",
  agent_usage: "Discipline grounding, facet validation"
})

CREATE (wp_p921:_Schema:WikidataProperty {
  property: "P921",
  label: "main subject",
  semantic: "aboutness",
  transitive: false,
  tier: 2.5,
  usage: "Map work/source to primary topic",
  example: "Histories (Polybius) P921 Second Punic War",
  agent_usage: "Source discovery, evidence grounding"
})

CREATE (wp_p1269:_Schema:WikidataProperty {
  property: "P1269",
  label: "facet of",
  semantic: "facet_hierarchy",
  transitive: false,
  tier: 2.5,
  usage: "Map aspect to broader concept",
  example: "microeconomics P1269 economics",
  agent_usage: "Facet relationships, domain inheritance"
});

// ================================================================
// STATISTICS AND CARDINALITY (For Agent Planning)
// ================================================================

CREATE (stats:_Schema:GraphStatistics {
  last_updated: datetime(),
  total_labels: 14,
  total_relationship_types: 12,
  total_facets: 17,
  total_authority_tiers: 6,
  year_nodes: 4025,
  year_range_start: -2000,
  year_range_end: 2025,
  wikidata_properties_layer_2_5: 7,
  validation_rules: 7
});

// ================================================================
// USAGE EXAMPLES FOR AGENTS
// ================================================================

CREATE (examples:_Schema:AgentQueryExamples {
  created: datetime(),
  
  example_1_what_labels: "MATCH (n:_Schema:NodeLabel) RETURN n.name, n.definition, n.tier ORDER BY n.tier",
  
  example_2_what_relationships: "MATCH (r:_Schema:RelationshipType) RETURN r.name, r.semantic, r.source_label, r.target_label",
  
  example_3_what_facets: "MATCH (f:_Schema:FacetReference) RETURN f.key, f.label, f.definition ORDER BY f.key",
  
  example_4_what_layers: "MATCH (t:_Schema:AuthorityTier) RETURN t.tier, t.layer_name, t.purpose ORDER BY t.tier",
  
  example_5_valid_relationships_for_label: "MATCH (nl:_Schema:NodeLabel {name: 'SubjectConcept'})<-[:SOURCE_LABEL]-(r:_Schema:RelationshipType)-[:TARGET_LABEL]->(target) RETURN r.name, target.name",
  
  example_6_properties_for_label: "MATCH (nl:_Schema:NodeLabel {name: 'Claim'})-[:HAS_REQUIRED_PROPERTY]->(p:_Schema:Property) RETURN p.name, p.type, p.purpose",
  
  example_7_wikidata_properties: "MATCH (wp:_Schema:WikidataProperty) WHERE wp.transitive = true RETURN wp.property, wp.label, wp.usage",
  
  example_8_validation_rules: "MATCH (vr:_Schema:ValidationRule) WHERE vr.severity = 'CRITICAL' RETURN vr.name, vr.rationale"
});

// ================================================================
// INDEXES FOR FAST META-GRAPH QUERIES
// ================================================================

CREATE INDEX meta_node_label_name IF NOT EXISTS FOR (n:_Schema:NodeLabel) ON (n.name);
CREATE INDEX meta_relationship_type_name IF NOT EXISTS FOR (r:_Schema:RelationshipType) ON (r.name);
CREATE INDEX meta_facet_key IF NOT EXISTS FOR (f:FacetReference) ON (f.key);
CREATE INDEX meta_authority_tier IF NOT EXISTS FOR (t:_Schema:AuthorityTier) ON (t.tier);
CREATE INDEX meta_wikidata_property IF NOT EXISTS FOR (wp:_Schema:WikidataProperty) ON (wp.property);

// ================================================================
// COMPLETION MESSAGE
// ================================================================

RETURN "✅ Meta-schema graph created successfully!" AS status,
       "Agents can now introspect schema via _Schema label queries" AS capability,
       "Use MATCH (n:_Schema) RETURN n to see all meta-nodes" AS test_query;
