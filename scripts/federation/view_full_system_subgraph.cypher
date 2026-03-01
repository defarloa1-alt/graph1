// ============================================================================
// VIEW FULL CHRYSTALLUM SYSTEM SUBGRAPH
// ============================================================================
// Returns the complete schema subgraph for Neo4j Browser visualization.
// Use in Neo4j Browser: paste and run. Shows facets, federations, subjects,
// biblio, self-description — everything under the Chrystallum root.
//
// All branches use OPTIONAL MATCH so the query works even if some branches
// haven't been bootstrapped yet.
// ============================================================================

MATCH (c:Chrystallum)
OPTIONAL MATCH (c)-[:HAS_FACET_CLUSTER]->(fc:Facets:Category)-[:IS_COMPOSED_OF]->(facet:CanonicalFacet)
OPTIONAL MATCH (c)-[:HAS_FEDERATION_CLUSTER]->(fed_cat:Federation:Category)-[:IS_COMPOSED_OF]->(auth:Federation:AuthoritySystem)
OPTIONAL MATCH (c)-[:HAS_FEDERATION]->(fr:SYS_FederationRegistry)-[:CONTAINS]->(src:SYS_FederationSource)
OPTIONAL MATCH (c)-[:HAS_SUBJECT_CONCEPT_ROOT]->(scr:SubjectConceptRoot)
OPTIONAL MATCH (scr)-[:HAS_SUBJECT_REGISTRY]->(reg:SubjectConceptRegistry)
OPTIONAL MATCH (scr)-[:HAS_AGENT_REGISTRY]->(agent_reg:AgentRegistry)-[:HAS_AGENT]->(agent:Agent)
OPTIONAL MATCH (c)-[:HAS_BIBLIOGRAPHY]->(br:BibliographyRegistry)-[:CONTAINS]->(bs:BibliographySource)
OPTIONAL MATCH (c)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
OPTIONAL MATCH (c)-[:HAS_FACET_ROOT]->(facet_root:FacetRoot)-[:HAS_FACET]->(f:Facet)
RETURN c, fc, facet, fed_cat, auth, fr, src, scr, reg, agent_reg, agent, br, bs, sd, facet_root, f;

// ============================================================================
// ALTERNATIVE: Table summary (run separately if you prefer counts)
// ============================================================================
/*
MATCH (c:Chrystallum)
OPTIONAL MATCH (c)-[:HAS_FACET_CLUSTER]->(fc)-[:IS_COMPOSED_OF]->(facet)
OPTIONAL MATCH (c)-[:HAS_FEDERATION_CLUSTER]->(fed_cat)-[:IS_COMPOSED_OF]->(auth)
OPTIONAL MATCH (c)-[:HAS_FEDERATION]->(fr)-[:CONTAINS]->(src)
OPTIONAL MATCH (c)-[:HAS_SUBJECT_CONCEPT_ROOT]->(scr)
OPTIONAL MATCH (scr)-[:HAS_AGENT_REGISTRY]->(agent_reg)-[:HAS_AGENT]->(agent)
OPTIONAL MATCH (c)-[:HAS_BIBLIOGRAPHY]->(br)
OPTIONAL MATCH (c)-[:HAS_SELF_DESCRIPTION]->(sd)
RETURN
  c.id AS root,
  count(DISTINCT facet) AS facets,
  count(DISTINCT auth) AS authority_systems,
  count(DISTINCT src) AS federation_sources,
  count(DISTINCT agent) AS agents,
  count(DISTINCT sd) AS has_self_description,
  count(DISTINCT br) AS has_bibliography;
*/
