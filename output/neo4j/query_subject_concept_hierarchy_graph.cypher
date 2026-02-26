// BROADER_THAN hierarchy as graph (Neo4j Browser)
// Returns path for graph visualization, not table

MATCH path = (root:SubjectConcept {qid: 'Q17167'})-[:BROADER_THAN*]->(narrower:SubjectConcept)
RETURN path
LIMIT 200
