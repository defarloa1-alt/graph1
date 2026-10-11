// Run only against the local clean-start neo4j database.
// This schema preserves the existing Year backbone and adds no data nodes.

CREATE CONSTRAINT year_year_unique IF NOT EXISTS
FOR (node:Year)
REQUIRE node.year IS UNIQUE;

CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (node:Entity)
REQUIRE node.id IS UNIQUE;

CREATE CONSTRAINT subject_id_unique IF NOT EXISTS
FOR (node:Subject)
REQUIRE node.id IS UNIQUE;

CREATE CONSTRAINT authority_record_id_unique IF NOT EXISTS
FOR (node:AuthorityRecord)
REQUIRE node.id IS UNIQUE;

CREATE CONSTRAINT authority_record_system_identifier_unique IF NOT EXISTS
FOR (node:AuthorityRecord)
REQUIRE (node.system, node.identifier) IS UNIQUE;

CREATE CONSTRAINT source_observation_id_unique IF NOT EXISTS
FOR (node:SourceObservation)
REQUIRE node.id IS UNIQUE;

CREATE CONSTRAINT assertion_id_unique IF NOT EXISTS
FOR (node:Assertion)
REQUIRE node.id IS UNIQUE;

CREATE CONSTRAINT proposal_id_unique IF NOT EXISTS
FOR (node:Proposal)
REQUIRE node.id IS UNIQUE;
