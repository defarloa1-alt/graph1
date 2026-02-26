// =============================================================================
// STEP 1 of 2: Remove legacy SubjectConcepts (run this FIRST in Neo4j Browser)
// =============================================================================
// After this, run: output/neo4j/load_subject_concepts_qid_canonical.cypher
//
// RUN EACH BLOCK SEPARATELY (select one block, then click Run or Ctrl+Enter)

// -----------------------------------------------------------------------------
// DIAGNOSTIC: Run this first — always returns a row
// -----------------------------------------------------------------------------
UNWIND [1] AS _
OPTIONAL MATCH (sc:SubjectConcept)
WITH count(sc) AS total,
     [x IN collect(sc.subject_id) WHERE x IS NOT NULL][0..10] AS sample_subject_ids
RETURN total, sample_subject_ids,
       CASE WHEN total = 0 THEN "No SubjectConcepts - proceed to Step 2"
            WHEN size([x IN sample_subject_ids WHERE x STARTS WITH "subj_rr_" OR x = "subj_roman_republic_q17167"]) > 0
                 THEN "Legacy subj_rr_* found - run 1a and 1b below"
            ELSE "Already QID-canonical - proceed to Step 2" END AS action;

// NOTE: If edges_deleted=0 and nodes_deleted=0, graph has no legacy subj_rr_* nodes.
// Proceed to Step 2 (load canonical) — MERGE will create/update SubjectConcepts.

// -----------------------------------------------------------------------------
// 1a. Delete MEMBER_OF edges pointing at legacy SubjectConcepts
// -----------------------------------------------------------------------------
OPTIONAL MATCH (e:Entity)-[r:MEMBER_OF]->(sc:SubjectConcept)
WHERE sc.subject_id STARTS WITH 'subj_rr_' OR sc.subject_id = 'subj_roman_republic_q17167'
WITH [x IN collect(r) WHERE x IS NOT NULL] AS rels
WITH rels, size(rels) AS edges_deleted
FOREACH (x IN rels | DELETE x)
RETURN edges_deleted;

// -----------------------------------------------------------------------------
// 1b. Delete legacy SubjectConcept nodes (and any remaining relationships)
// -----------------------------------------------------------------------------
OPTIONAL MATCH (sc:SubjectConcept)
WHERE sc.subject_id STARTS WITH 'subj_rr_' OR sc.subject_id = 'subj_roman_republic_q17167'
WITH [n IN collect(sc) WHERE n IS NOT NULL] AS nodes
WITH nodes, size(nodes) AS nodes_deleted
FOREACH (n IN nodes | DETACH DELETE n)
RETURN nodes_deleted;
