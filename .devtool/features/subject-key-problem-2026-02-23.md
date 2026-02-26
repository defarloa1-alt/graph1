---
id: "subject-key-problem-2026-02-23"
status: "in-progress"
priority: "high"
assignee: null
dueDate: null
created: "2026-02-23T23:28:33.142Z"
modified: "2026-02-24T13:21:41.731Z"
completedAt: null
labels: ["Core Subject"]
order: "a1"
---
# subject key problem

## **Remaining Work to Fully Retire subj_rr\_**

1. Update load_roman_republic\_[ontology.py](http://ontology.py) to use QID-based identity (or mark it legacy-only).


1) Update find_subject_concept\_[anchors.py](http://anchors.py) so CURATED_ANCHORS is keyed by QID.


1. Update validate_anchors and reresolve_anchors to work with QID-canonical anchors.


1) Update docs, Cypher examples, and agents that still reference subj_rr\_\* or subj_roman_republic_q17167.