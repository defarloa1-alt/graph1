// SCA Domain Structure Schema — WikidataType lookup nodes and subject domain skeleton
// Persists findings from SCA traversal so new Claude sessions can ground themselves.
// Run after core schema; idempotent (CREATE IF NOT EXISTS).

// ── WikidataType: ontology lookup nodes (P31/P279 types from traversal) ──
// Replicates Wikidata's type hierarchy for SCA lookup; backlink profiles cached.
CREATE CONSTRAINT wikidata_type_qid IF NOT EXISTS
FOR (w:WikidataType) REQUIRE w.qid IS UNIQUE;

// ── SubjectDomain: skeleton structure per subject (e.g. Roman Republic) ──
// One per SubjectConcept; holds traversal summary and training QID set.
CREATE CONSTRAINT subject_domain_qid IF NOT EXISTS
FOR (d:SubjectDomain) REQUIRE d.seed_qid IS UNIQUE;

// ── Relationships ──
// (SubjectConcept)-[:HAS_DOMAIN_STRUCTURE]->(SubjectDomain)
// (SubjectDomain)-[:USES_TYPE]->(WikidataType)  // types discovered in traversal
// (WikidataType)-[:INSTANCE_OF]->(WikidataType) // P31 hierarchy
// (WikidataType)-[:SUBCLASS_OF]->(WikidataType) // P279 hierarchy
// (WikidataType)-[:HAS_BACKLINK_PROFILE]->(BacklinkProfile) // optional, for rich cache
