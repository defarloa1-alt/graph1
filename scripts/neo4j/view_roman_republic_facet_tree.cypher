// Neo4j Browser: Roman Republic facet hierarchy (SubjectDomain, NOT Period)
// Period Q17167 also labels as "Roman Republic" but has 41k+ temporal edges.
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MATCH (sd)-[:HAS_SUBJECT_CONCEPT]->(u:FacetUmbrella)
OPTIONAL MATCH (u)<-[:PART_OF]-(sc:SubjectConcept {source: 'di_proposal'})
RETURN sd, u, sc
