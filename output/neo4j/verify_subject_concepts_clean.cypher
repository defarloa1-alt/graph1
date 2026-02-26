// Verify SubjectConcept state - run in Neo4j Browser
// "Clean" = QID-canonical (subject_id = qid like Q17167, Q105427)
// "Legacy" = subj_rr_* or subj_roman_republic_q17167

UNWIND [1] AS _
OPTIONAL MATCH (sc:SubjectConcept)
WITH count(sc) AS total,
     [x IN collect(sc.qid) WHERE x IS NOT NULL][0..5] AS sample_qids,
     [x IN collect(sc.subject_id) WHERE x IS NOT NULL][0..5] AS sample_subject_ids
RETURN total,
       sample_qids,
       sample_subject_ids,
       CASE WHEN total = 0 THEN "No SubjectConcepts - run Step 2 (load canonical)"
            WHEN size([x IN sample_subject_ids WHERE x STARTS WITH 'subj_rr_' OR x = 'subj_roman_republic_q17167']) > 0
                 THEN "Legacy subj_rr_* found - run migrate script"
            ELSE "Clean (QID-canonical) - Step 1 not needed" END AS status;
