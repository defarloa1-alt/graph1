// ============================================================================
// OI-008-06: Label-gap remediation — Concept → Person (Population A only)
// ============================================================================
// PURPOSE: Promote :Entity nodes with entity_type=CONCEPT that have family
//          edges and real Wikidata QIDs (Q\d+) to :Person. These were
//          subject-concept stubs; person harvest wrote correct family edges
//          but targets were never promoted.
// POPULATION A: 66 nodes — QID format Q\d+, concept_qXXX. Safe to promote.
// POPULATION B: 80 nodes — MD5 hash in qid, con_qHASH. Do NOT promote.
//               See OI-008-07.
// RUN BEFORE: Next person harvest (otherwise traversal keeps writing to
//             concept_qXXX nodes, compounding the gap).
// IDEMPOTENT: Safe to re-run (SET is idempotent).
// ============================================================================

// Part 1: Promote only Population A — real Wikidata QIDs (Q\d+)
MATCH (n:Entity)
WHERE n.entity_type = 'CONCEPT'
  AND n.qid =~ '^Q[0-9]+$'
  AND (
    ()-[:FATHER_OF|MOTHER_OF|SIBLING_OF|SPOUSE_OF]->(n)
    OR (n)-[:FATHER_OF|MOTHER_OF|SIBLING_OF|SPOUSE_OF]->()
  )
SET n:Person,
    n.entity_type = 'PERSON',
    n.entity_id = 'person_' + toLower(n.qid);

// ============================================================================
// VERIFICATION (run separately)
// ============================================================================
// -- Population A candidates (pre-run, expect 66)
// MATCH (n:Entity)
// WHERE n.entity_type = 'CONCEPT'
//   AND n.qid =~ '^Q[0-9]+$'
//   AND (()-[:FATHER_OF|MOTHER_OF|SIBLING_OF|SPOUSE_OF]->(n)
//     OR (n)-[:FATHER_OF|MOTHER_OF|SIBLING_OF|SPOUSE_OF]->())
// RETURN n.label, n.qid, n.entity_id ORDER BY n.label
//
// -- Sample: Caesar (Q1048)
// MATCH (n:Person {qid: 'Q1048'}) RETURN n.label, n.entity_id, n.entity_type, labels(n)
