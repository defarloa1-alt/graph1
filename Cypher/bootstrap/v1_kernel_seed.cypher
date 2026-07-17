// V1 Kernel Seed Data - Cypher Script
// =====================================
// Purpose: Seed minimal graph demonstrating all 25 v1 kernel relationships
// Domain: Roman Republic + Historical Figures (Using existing sample data)
// Generated: 2026-02-16
// Version: 1.0
//
// This script creates:
// - 12 entities (Roman Republic, Julius Caesar, Augustus, Gaul, etc.)
// - 25 relationships (one of each v1 kernel type)
// - Demonstrates federation-ready structure

// ============================================================================
// PHASE 1: Indexes & Constraints
// ============================================================================

// Entity indexes
CREATE INDEX entity_qid_idx IF NOT EXISTS FOR (e:Entity) ON (e.qid);
CREATE INDEX entity_name_idx IF NOT EXISTS FOR (e:Entity) ON (e.name);
CREATE INDEX entity_type_idx IF NOT EXISTS FOR (e:Entity) ON (e.entity_type);

// Relationship indexes
CREATE INDEX same_as_idx IF NOT EXISTS FOR ()-[r:SAME_AS]->() ON r.confidence;
CREATE INDEX cited_by_idx IF NOT EXISTS FOR ()-[r:CITES]->() ON r.confidence;
CREATE INDEX temporal_order_idx IF NOT EXISTS FOR ()-[r:HAPPENED_BEFORE]->() ON r.confidence;

// Uniqueness constraints
CREATE CONSTRAINT entity_qid_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.qid IS UNIQUE;

// Cardinality constraints
CREATE CONSTRAINT name_relationship IF NOT EXISTS FOR ()-[r:NAME]->() REQUIRE r.is_literal = true;

// ============================================================================
// PHASE 2: Create Entities
// ============================================================================

// Roman Republic (polity)
MERGE (rome:Entity {
  qid: "Q87",
  name: "Roman Republic",
  label: "The Roman Republic",
  entity_type: "polity",
  founded: "509 BCE",
  dissolved: "27 BCE",
  temporal_scope: "-509/-27"
});

// Augustus (Octavian) - Roman Emperor
MERGE (augustus:Entity {
  qid: "Q1048",
  name: "Augustus",
  label: "Augustus (Gaius Julius Caesar Octavianus)",
  entity_type: "person",
  role: "Emperor",
  birth_year: "-63",
  death_year: "14 CE",
  temporal_scope: "-63/14"
});

// Julius Caesar - Roman General & Statesman
MERGE (caesar:Entity {
  qid: "Q1048_variant",
  name: "Julius Caesar",
  label: "Gaius Julius Caesar",
  entity_type: "person",
  role: "Military Commander",
  birth_year: "-100",
  death_year: "-44",
  temporal_scope: "-100/-44"
});

// Gaul - Geographic region
MERGE (gaul:Entity {
  qid: "Q779",
  name: "Gaul",
  label: "Gaul (ancient region)",
  entity_type: "place",
  region_type: "province",
  temporal_scope: "-500/500"
});

// Conquest of Gaul (military campaign)
MERGE (conquest:Entity {
  qid: "Q184359",
  name: "Conquest of Gaul",
  label: "Caesar's Conquest of Gaul",
  entity_type: "event",
  event_type: "military campaign",
  start_date: "-58",
  end_date: "-50",
  temporal_scope: "-58/-50"
});

// writings by Caesar
MERGE (commentaries:Entity {
  qid: "Q174037",
  name: "Commentarii de Bello Gallico",
  label: "Commentaries on the Gallic Wars",
  entity_type: "work",
  author: "Julius Caesar",
  language: "Latin",
  date_written: "-50"
});

// Ancient Rome (state/civilization)
MERGE (ancientRome:Entity {
  qid: "Q127376",
  name: "Ancient Rome",
  label: "Ancient Rome",
  entity_type: "civilization",
  temporal_scope: "-753/476"
});

// Britain entity (neighboring territory)
MERGE (britain:Entity {
  qid: "Q23666",
  name: "Britain",
  label: "Ancient Britain",
  entity_type: "place",
  region_type: "island",
  temporal_scope: "-4000/present"
});

// Pompey (Roman General)
MERGE (pompey:Entity {
  qid: "Q49054",
  name: "Pompey",
  label: "Pompey the Great",
  entity_type: "person",
  role: "Military Commander",
  birth_year: "-106",
  death_year: "-48",
  temporal_scope: "-106/-48"
});

// Cleopatra (Egyptian Queen)
MERGE (cleopatra:Entity {
  qid: "Q635",
  name: "Cleopatra",
  label: "Cleopatra VII",
  entity_type: "person",
  role: "Pharaoh",
  birth_year: "-69",
  death_year: "-30",
  temporal_scope: "-69/-30"
});

// Egypt (territory)
MERGE (egypt:Entity {
  qid: "Q11768",
  name: "Egypt",
  label: "Ptolemaic Egypt",
  entity_type: "place",
  region_type: "kingdom",
  temporal_scope: "-305/-30"
});

// Alexandria (city)
MERGE (alexandria:Entity {
  qid: "Q87",
  name: "Alexandria",
  label: "Alexandria",
  entity_type: "place",
  place_type: "city",
  founded: "-331"
});

// ============================================================================
// PHASE 3: Create V1 Kernel Relationships
// ============================================================================

// 1. SAME_AS - Entity deduplication
MATCH (rome:Entity {qid: "Q87"}), (ancientRome:Entity {qid: "Q127376"})
CREATE (ancientRome)-[:SAME_AS {confidence: 0.90, rationale: "Ancient Rome as political entity", version: "1.0"}]->(rome);

// 2. TYPE_OF - Classification hierarchy
MATCH (conquest:Entity {qid: "Q184359"}), (rome:Entity {qid: "Q87"})
CREATE (conquest)-[:TYPE_OF {confidence: 0.95, category: "military_campaign", version: "1.0"}]->(rome);

// 3. INSTANCE_OF - Type assertion
MATCH (caesar:Entity), (rome:Entity {qid: "Q87"})
CREATE (caesar)-[:INSTANCE_OF {confidence: 0.98, category: "leader", version: "1.0"}]->(rome);

// 4. NAME - Entity naming (literal)
MATCH (caesar:Entity {qid: "Q1048_variant"})
CREATE (caesar)-[:NAME {literal: "Gaius Julius Caesar", lang: "la", is_literal: true, confidence: 1.0, version: "1.0"}]->(:NameNode {value: "Julius Caesar"});

// 5. ALIAS_OF - Alternative identifiers
MATCH (augustus:Entity {qid: "Q1048"}), (caesar:Entity {qid: "Q1048_variant"})
CREATE (caesar)-[:ALIAS_OF {confidence: 0.85, note: "Early name variant", version: "1.0"}]->(augustus);

// 6. LOCATED_IN - Spatial hierarchy
MATCH (alexandria:Entity {name: "Alexandria"}), (egypt:Entity {qid: "Q11768"})
CREATE (alexandria)-[:LOCATED_IN {confidence: 0.99, region_type: "city_in_country", version: "1.0"}]->(egypt);

// 7. PART_OF - Composition
MATCH (gaul:Entity {qid: "Q779"}), (rome:Entity {qid: "Q87"})
CREATE (gaul)-[:PART_OF {confidence: 0.88, period_start: "-27", period_end: "476", version: "1.0"}]->(rome);

// 8. BORDERS - Spatial adjacency
MATCH (gaul:Entity {qid: "Q779"}), (britain:Entity {qid: "Q23666"})
CREATE (gaul)-[:BORDERS {confidence: 0.92, separated_by: "sea", version: "1.0"}]->(britain);

// 9. CAPITAL_OF - Administrative center
MATCH (alexandria:Entity {name: "Alexandria"}), (egypt:Entity {qid: "Q11768"})
CREATE (alexandria)-[:CAPITAL_OF {confidence: 0.95, period_start: "-305", period_end: "-30", version: "1.0"}]->(egypt);

// 10. CONTAINED_BY - Spatial containment
MATCH (alexandria:Entity {name: "Alexandria"}), (egypt:Entity {qid: "Q11768"})
CREATE (alexandria)-[:CONTAINED_BY {confidence: 0.99, region_id: "egypt_region", version: "1.0"}]->(egypt);

// 11. OCCURRED_AT - Event location
MATCH (conquest:Entity {qid: "Q184359"}), (gaul:Entity {qid: "Q779"})
CREATE (conquest)-[:OCCURRED_AT {confidence: 0.93, location_role: "primary", version: "1.0"}]->(gaul);

// 12. OCCURS_DURING - Event temporal scope
MATCH (conquest:Entity {qid: "Q184359"})
CREATE (conquest)-[:OCCURS_DURING {confidence: 0.98, period_id: "late_republic", period_start: "-58", period_end: "-50", version: "1.0"}]->(:TimePeriod {name: "Late Roman Republic", epoch_start: "-58", epoch_end: "-50"});

// 13. HAPPENED_BEFORE - Temporal ordering
MATCH (conquest:Entity {qid: "Q184359"}), (pompey:Entity {qid: "Q49054"})
CREATE (conquest)-[:HAPPENED_BEFORE {confidence: 0.95, evidence: "documented", version: "1.0"}]->(pompey);

// 14. CONTEMPORARY_WITH - Temporal overlap
MATCH (caesar:Entity {qid: "Q1048_variant"}), (pompey:Entity {qid: "Q49054"})
CREATE (caesar)-[:CONTEMPORARY_WITH {confidence: 0.99, overlap_start: "-60", overlap_end: "-48", version: "1.0"}]->(pompey);

// 15. CITES - Citation/reference
MATCH (commentaries:Entity {qid: "Q174037"}), (gaul:Entity {qid: "Q779"})
CREATE (commentaries)-[:CITES {confidence: 0.97, citation_type: "describes", version: "1.0"}]->(gaul);

// 16. DERIVES_FROM - Lineage/derivation
MATCH (augustus:Entity), (caesar:Entity {qid: "Q1048_variant"})
CREATE (augustus)-[:DERIVES_FROM {confidence: 0.92, derivation_type: "adopted_heir", version: "1.0"}]->(caesar);

// 17. EXTRACTED_FROM - Source claim
MATCH (commentaries:Entity {qid: "Q174037"}), (conquest:Entity {qid: "Q184359"})
CREATE (conquest)-[:EXTRACTED_FROM {confidence: 0.90, source_type: "primary_document", passage_id: "commentaries_001", version: "1.0"}]->(commentaries);

// 18. AUTHOR - Authorship relationship
MATCH (commentaries:Entity {qid: "Q174037"}), (caesar:Entity {qid: "Q1048_variant"})
CREATE (caesar)-[:AUTHOR {confidence: 1.0, role: "primary_author", version: "1.0"}]->(commentaries);

// 19. ATTRIBUTED_TO - Claim attribution
MATCH (commentaries:Entity {qid: "Q174037"}), (caesar:Entity {qid: "Q1048_variant"})
CREATE (commentaries)-[:ATTRIBUTED_TO {confidence: 0.99, attribution_type: "authorship", version: "1.0"}]->(caesar);

// 20. DESCRIBES - Reference/description
MATCH (commentaries:Entity {qid: "Q174037"}), (conquest:Entity {qid: "Q184359"})
CREATE (commentaries)-[:DESCRIBES {confidence: 0.96, description_role: "primary_subject", version: "1.0"}]->(conquest);

// 21. SUBJECT_OF - Entity as subject of description
MATCH (caesar:Entity {qid: "Q1048_variant"}), (commentaries:Entity {qid: "Q174037"})
CREATE (caesar)-[:SUBJECT_OF {confidence: 0.92, role: "documented_subject", version: "1.0"}]->(commentaries);

// 22. OBJECT_OF - Entity as object of action
MATCH (gaul:Entity {qid: "Q779"}), (conquest:Entity {qid: "Q184359"})
CREATE (gaul)-[:OBJECT_OF {confidence: 0.95, role: "target_of_conquest", version: "1.0"}]->(conquest);

// 23. CAUSED - Causality
MATCH (conquest:Entity {qid: "Q184359"}), (pompey:Entity {qid: "Q49054"})
CREATE (conquest)-[:CAUSED {confidence: 0.88, causal_role: "trigger", version: "1.0"}]->(pompey);

// 24. CONTRADICTS - Contradiction
MATCH (pompey:Entity {qid: "Q49054"}), (caesar:Entity {qid: "Q1048_variant"})
CREATE (pompey)-[:CONTRADICTS {confidence: 0.75, dispute_type: "political", resolved: false, version: "1.0"}]->(caesar);

// 25. SUPPORTS - Support/corroboration
MATCH (commentaries:Entity {qid: "Q174037"}), (conquest:Entity {qid: "Q184359"})
CREATE (commentaries)-[:SUPPORTS {confidence: 0.94, support_type: "primary_evidence", version: "1.0"}]->(conquest);

// ============================================================================
// PHASE 4: Validation & Statistics
// ============================================================================

// Show created entities
MATCH (e:Entity)
RETURN e.qid, e.name, e.entity_type
ORDER BY e.entity_type, e.name;

// Show all v1 kernel relationships
MATCH ()-[r:SAME_AS | ALIAS_OF | NAME | TYPE_OF | INSTANCE_OF | LOCATED_IN | 
           PART_OF | BORDERS | CAPITAL_OF | CONTAINED_BY | OCCURRED_AT | 
           OCCURS_DURING | HAPPENED_BEFORE | CONTEMPORARY_WITH | CITES | 
           DERIVES_FROM | EXTRACTED_FROM | AUTHOR | ATTRIBUTED_TO | DESCRIBES | 
           SUBJECT_OF | OBJECT_OF | CAUSED | CONTRADICTS | SUPPORTS]->()
RETURN type(r) AS relationship_type, count(r) AS count
ORDER BY relationship_type;

// Show graph statistics
MATCH (e:Entity)
WITH count(e) AS entity_count
MATCH ()-[r]->()
RETURN entity_count, count(r) AS relationship_count;
