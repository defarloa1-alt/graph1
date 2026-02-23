// Neo4j Import - SCA Entities with Ciphers
// Generated: 2026-02-21T07:14:40.289402
// Total entities: 300

// ============ INDEXES ============

// Tier 1: Entity cipher indexes
CREATE INDEX entity_cipher_idx IF NOT EXISTS FOR (n:Entity) ON (n.entity_cipher);
CREATE INDEX entity_qid_idx IF NOT EXISTS FOR (n:Entity) ON (n.qid);
CREATE INDEX entity_type_idx IF NOT EXISTS FOR (n:Entity) ON (n.entity_type, n.entity_cipher);

// Tier 2: Faceted cipher indexes
CREATE INDEX faceted_cipher_idx IF NOT EXISTS FOR (n:FacetedEntity) ON (n.faceted_cipher);
CREATE INDEX faceted_entity_facet_idx IF NOT EXISTS FOR (n:FacetedEntity) ON (n.entity_cipher, n.facet_id);

// ============ ENTITIES ============
