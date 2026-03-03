// Phase 0.3: Person schema constraints and indexes (ADR-007)
// Run: python scripts/neo4j/run_cypher_file.py scripts/neo4j/person_schema_constraints.cypher

// Uniqueness constraint for Person entity_id
CREATE CONSTRAINT person_entity_id_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.entity_id IS UNIQUE;

// Indexes for Person lookups
CREATE INDEX person_dprr_id IF NOT EXISTS
FOR (p:Person) ON (p.dprr_id);

CREATE INDEX person_qid IF NOT EXISTS
FOR (p:Person) ON (p.qid);

CREATE INDEX person_viaf_id IF NOT EXISTS
FOR (p:Person) ON (p.viaf_id);

// Note: :Gens, :Praenomen, :Nomen, :Cognomen, :Tribe constraints/indexes
// will be added in Phase 3 when those nodes are created.
