// Wikidata Hierarchy Relationships Schema for Chrystallum
// File: Cypher/wikidata_hierarchy_relationships.cypher
// Purpose: Create constraints and indexes for P31/P279/P361/P101/P2578/P921/P1269 relationships

// ============================================================================
// CONSTRAINTS: Ensure data integrity
// ============================================================================

// Relationship source tracking
CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:INSTANCE_OF]-() 
    REQUIRE r.source IS NOT NULL;
CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:SUBCLASS_OF]-() 
    REQUIRE r.source IS NOT NULL;
CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:PART_OF]-() 
    REQUIRE r.source IS NOT NULL;
CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:FIELD_OF_WORK]-() 
    REQUIRE r.source IS NOT NULL;
CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:STUDIES]-() 
    REQUIRE r.source IS NOT NULL;
CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:MAIN_SUBJECT]-() 
    REQUIRE r.source IS NOT NULL;
CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:FACET_OF]-() 
    REQUIRE r.source IS NOT NULL;

// ============================================================================
// INDEXES: Optimize query performance for hierarchy traversal
// ============================================================================

// P31 (instance-of) traversal
CREATE INDEX instance_of_outgoing IF NOT EXISTS 
    FOR ()-[r:INSTANCE_OF]->() 
    ON (r.source);

CREATE INDEX instance_of_incoming IF NOT EXISTS 
    FOR ()-[r:INSTANCE_OF]->(n:SubjectConcept) 
    ON (n.qid);

// P279 (subclass-of) traversal - TRANSITIVE
CREATE INDEX subclass_of_outgoing IF NOT EXISTS 
    FOR ()-[r:SUBCLASS_OF]->() 
    ON (r.source);

CREATE INDEX subclass_of_incoming IF NOT EXISTS 
    FOR ()-[r:SUBCLASS_OF]->(n:SubjectConcept) 
    ON (n.qid);

// P361 (part-of) traversal - TRANSITIVE
CREATE INDEX part_of_outgoing IF NOT EXISTS 
    FOR ()-[r:PART_OF]->() 
    ON (r.source);

CREATE INDEX part_of_incoming IF NOT EXISTS 
    FOR ()-[r:PART_OF]->(n) 
    ON (n.qid);

// P101 (field-of-work) queries
CREATE INDEX field_of_work_outgoing IF NOT EXISTS 
    FOR (n:Person)-[r:FIELD_OF_WORK]->() 
    ON (n.qid);

CREATE INDEX field_of_work_incoming IF NOT EXISTS 
    FOR ()-[r:FIELD_OF_WORK]->(d:SubjectConcept) 
    ON (d.qid);

// P2578 (studies) queries
CREATE INDEX studies_outgoing IF NOT EXISTS 
    FOR (d:SubjectConcept)-[r:STUDIES]->() 
    ON (d.qid);

CREATE INDEX studies_incoming IF NOT EXISTS 
    FOR ()-[r:STUDIES]->(n) 
    ON (n.qid);

// P921 (main-subject) queries
CREATE INDEX main_subject_outgoing IF NOT EXISTS 
    FOR (w:Work)-[r:MAIN_SUBJECT]->() 
    ON (w.qid);

CREATE INDEX main_subject_incoming IF NOT EXISTS 
    FOR ()-[r:MAIN_SUBJECT]->(t) 
    ON (t.qid);

// P1269 (facet-of) queries
CREATE INDEX facet_of_outgoing IF NOT EXISTS 
    FOR ()-[r:FACET_OF]->() 
    ON (r.source);

CREATE INDEX facet_of_incoming IF NOT EXISTS 
    FOR ()-[r:FACET_OF]->(c:SubjectConcept) 
    ON (c.qid);

// ============================================================================
// EXAMPLE DATA: Bootstrap hierarchy relationships for Roman Republic
// ============================================================================

// === Events Hierarchy (P31 + P279) ===

// Event nodes
MERGE (cannae:Event {
    qid: "Q13377",
    label: "Battle of Cannae",
    node_type: "Event"
});

MERGE (trebia:Event {
    qid: "Q133819",
    label: "Battle of Trebia",
    node_type: "Event"
});

MERGE (zama:Event {
    qid: "Q187456",
    label: "Battle of Zama",
    node_type: "Event"
});

// Class nodes
MERGE (battle:SubjectConcept {
    qid: "Q178561",
    label: "battle",
    node_type: "SubjectConcept",
    type: "class"
});

MERGE (military_conflict:SubjectConcept {
    qid: "Q180684",
    label: "military conflict",
    node_type: "SubjectConcept",
    type: "class"
});

MERGE (event_class:SubjectConcept {
    qid: "Q1656682",
    label: "event",
    node_type: "SubjectConcept",
    type: "class"
});

// P31 relationships (instance-of)
MERGE (cannae)-[r1:INSTANCE_OF {source: "wikidata", property: "P31", confidence: 0.99}]->(battle);
MERGE (trebia)-[r2:INSTANCE_OF {source: "wikidata", property: "P31", confidence: 0.99}]->(battle);
MERGE (zama)-[r3:INSTANCE_OF {source: "wikidata", property: "P31", confidence: 0.99}]->(battle);

// P279 relationships (subclass-of) - TRANSITIVE
MERGE (battle)-[r4:SUBCLASS_OF {source: "wikidata", property: "P279", confidence: 0.99}]->(military_conflict);
MERGE (military_conflict)-[r5:SUBCLASS_OF {source: "wikidata", property: "P279", confidence: 0.99}]->(event_class);

// === Periods Hierarchy (P361) ===

// Period nodes
MERGE (republic:Period {
    qid: "Q17167",
    label: "Roman Republic",
    node_type: "Period"
});

MERGE (ancient_rome:Period {
    qid: "Q1747689",
    label: "Ancient Rome",
    node_type: "Period"
});

MERGE (antiquity:Period {
    qid: "Q486761",
    label: "Classical antiquity",
    node_type: "Period"
});

// P361 relationships (part-of)
MERGE (republic)-[r6:PART_OF {source: "wikidata", property: "P361", confidence: 0.99}]->(ancient_rome);
MERGE (ancient_rome)-[r7:PART_OF {source: "wikidata", property: "P361", confidence: 0.99}]->(antiquity);

// === Discipline + Studies Hierarchy ===

// Discipline nodes
MERGE (mil_hist:SubjectConcept {
    qid: "Q188507",
    label: "military history",
    node_type: "SubjectConcept",
    type: "discipline"
});

MERGE (econ:SubjectConcept {
    qid: "Q8134",
    label: "economics",
    node_type: "SubjectConcept",
    type: "discipline"
});

MERGE (pol_sci:SubjectConcept {
    qid: "Q36442",
    label: "political science",
    node_type: "SubjectConcept",
    type: "discipline"
});

// Objects of study
MERGE (warfare:SubjectConcept {
    qid: "Q198",
    label: "warfare",
    node_type: "SubjectConcept"
});

MERGE (economy:SubjectConcept {
    qid: "Q8142",
    label: "economy",
    node_type: "SubjectConcept"
});

MERGE (politics:SubjectConcept {
    qid: "Q7163",
    label: "politics",
    node_type: "SubjectConcept"
});

// P2578 relationships (studies)
MERGE (mil_hist)-[r8:STUDIES {source: "wikidata", property: "P2578", confidence: 0.99}]->(warfare);
MERGE (econ)-[r9:STUDIES {source: "wikidata", property: "P2578", confidence: 0.99}]->(economy);
MERGE (pol_sci)-[r10:STUDIES {source: "wikidata", property: "P2578", confidence: 0.99}]->(politics);

// === Experts (P101) ===

MERGE (polybius:Person {
    qid: "Q7345",
    label: "Polybius",
    node_type: "Person"
});

MERGE (cicero:Person {
    qid: "Q1541",
    label: "Cicero",
    node_type: "Person"
});

MERGE (livy:Person {
    qid: "Q6058",
    label: "Livy",
    node_type: "Person"
});

// P101 relationships (field of work)
MERGE (polybius)-[r11:FIELD_OF_WORK {source: "wikidata", property: "P101", confidence: 0.95}]->(mil_hist);
MERGE (cicero)-[r12:FIELD_OF_WORK {source: "wikidata", property: "P101", confidence: 0.95}]->(pol_sci);
MERGE (livy)-[r13:FIELD_OF_WORK {source: "wikidata", property: "P101", confidence: 0.95}]->(mil_hist);

// === Works (P921) ===

MERGE (histories:Work {
    qid: "Q1139494",
    label: "Histories (Polybius)",
    node_type: "Work",
    type: "book"
});

MERGE (de_republica:Work {
    qid: "Q1199689",
    label: "De re publica",
    node_type: "Work",
    type: "book"
});

MERGE (ab_urbe_condita:Work {
    qid: "Q868969",
    label: "Ab Urbe Condita",
    node_type: "Work",
    type: "book"
});

// P921 relationships (main subject)
MERGE (histories)-[r14:MAIN_SUBJECT {source: "wikidata", property: "P921", confidence: 0.99}]->(mil_hist);
MERGE (histories)-[r15:MAIN_SUBJECT {source: "wikidata", property: "P921", confidence: 0.95}]->(cannae);
MERGE (de_republica)-[r16:MAIN_SUBJECT {source: "wikidata", property: "P921", confidence: 0.99}]->(pol_sci);
MERGE (ab_urbe_condita)-[r17:MAIN_SUBJECT {source: "wikidata", property: "P921", confidence: 0.99}]->(mil_hist);

// === Facets (P1269) ===

MERGE (microecon:SubjectConcept {
    qid: "Q47664",
    label: "microeconomics",
    node_type: "SubjectConcept",
    type: "discipline"
});

MERGE (macroeconomics:SubjectConcept {
    qid: "Q8020715",
    label: "macroeconomics",
    node_type: "SubjectConcept",
    type: "discipline"
});

MERGE (roman_tactics:SubjectConcept {
    qid: "Q842606",
    label: "Roman military tactics",
    node_type: "SubjectConcept"
});

MERGE (naval_warfare:SubjectConcept {
    qid: "Q1357395",
    label: "naval warfare",
    node_type: "SubjectConcept"
});

// P1269 relationships (facet-of)
MERGE (microecon)-[r18:FACET_OF {source: "wikidata", property: "P1269", confidence: 0.99}]->(econ);
MERGE (macroeconomics)-[r19:FACET_OF {source: "wikidata", property: "P1269", confidence: 0.99}]->(econ);
MERGE (roman_tactics)-[r20:FACET_OF {source: "wikidata", property: "P1269", confidence: 0.95}]->(warfare);
MERGE (naval_warfare)-[r21:FACET_OF {source: "wikidata", property: "P1269", confidence: 0.99}]->(warfare);

// ============================================================================
// QUERIES: Verify relationships loaded
// ============================================================================

// Count relationships by type
RETURN {
    instance_of: COUNT(()-[:INSTANCE_OF]->()),
    subclass_of: COUNT(()-[:SUBCLASS_OF]->()),
    part_of: COUNT(()-[:PART_OF]->()),
    field_of_work: COUNT(()-[:FIELD_OF_WORK]->()),
    studies: COUNT(()-[:STUDIES]->()),
    main_subject: COUNT(()-[:MAIN_SUBJECT]->()),
    facet_of: COUNT(()-[:FACET_OF]->())
} as relationship_counts;
