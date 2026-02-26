// Fix BROADER_THAN cycles: delete edges where Q17167 (root) is the narrower node
// Root must never have incoming BROADER_THAN — run this to remove the 4 bad edges

MATCH (root:SubjectConcept {qid: 'Q17167'})<-[r:BROADER_THAN]-(broader:SubjectConcept)
DELETE r
RETURN count(r) AS deleted
