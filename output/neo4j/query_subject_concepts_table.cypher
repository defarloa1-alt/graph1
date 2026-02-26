// SubjectConcepts as table (Neo4j Browser)
MATCH (sc:SubjectConcept)
RETURN sc.qid AS qid, sc.label AS label, sc.harvest_status AS harvest_status, sc.confidence AS confidence
ORDER BY sc.qid
