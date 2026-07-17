// Script 19b — Fix Discipline→HAS_FACET routing
// Root cause: Q5 (human) anchor in Biographic facet registry caused 108 disciplines
// to be tagged Biographic. Q5 removed from registry. This script cleans the graph.
//
// Strategy:
// 1. Delete all Discipline→HAS_FACET→Biographic edges (Biographic is di_trainable=false/method;
//    having disciplines tagged to it provides no value for training pipeline)
// 2. Delete all Discipline→HAS_FACET→Cultural edges (Cultural is di_trainable=false/epistemic_dimension)
// 3. Delete all Discipline→HAS_FACET→Geographic edges (Geographic is di_trainable=false/covered)
// 4. Any discipline left with no HAS_FACET edges after cleanup: leave as-is (float)
//    They will be re-tagged on next classify.py run with fixed anchors.

// Step 1: Remove spurious Biographic edges from Discipline nodes
MATCH (d:Discipline)-[r:HAS_FACET]->(f:Facet {key: 'BIOGRAPHIC'})
DELETE r;

// Step 2: Remove spurious Cultural edges from Discipline nodes
MATCH (d:Discipline)-[r:HAS_FACET]->(f:Facet {key: 'CULTURAL'})
DELETE r;

// Step 3: Remove Geographic edges (covered by geo_bootstrap)
MATCH (d:Discipline)-[r:HAS_FACET]->(f:Facet {key: 'GEOGRAPHIC'})
DELETE r;

// Verify: disciplines with no remaining HAS_FACET edges
MATCH (d:Discipline) WHERE NOT (d)-[:HAS_FACET]->()
RETURN count(d) AS disciplines_without_facet_tag;
