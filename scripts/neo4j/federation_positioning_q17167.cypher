// SCA Federation Positioning - Q17167 (stubbed write)
// Run in Neo4j Browser. If "Driver is not connected": reconnect, then run ONE block at a time.
// Copy-paste each block between the --- markers, run it, then the next.

// --- BLOCK 1: SYS_Policy ---
MERGE (p:SYS_Policy {name: 'FederationPositioningHopsSemantics'})
SET p.definition   = '{"0": "self", "1": "direct parent", "2": "grandparent", "n": "nth ancestor"}',
    p.rule         = 'shortest path from domain root to anchor through traversed properties',
    p.last_updated = toString(datetime()),
    p.updated_by   = 'sca_federation_positioning'
RETURN p.name;

// --- BLOCK 2: POSITIONED_AS edges (run each MATCH/MERGE separately if needed) ---
// Q1307214 form of government
MATCH (sc:SubjectConcept {qid: 'Q17167'}), (target:Entity {qid: 'Q1307214'})
MERGE (sc)-[r:POSITIONED_AS {federation: 'wikidata', property: 'P31', hops: 1}]->(target)
SET r.rel_type = 'INSTANCE_OF_CLASS', r.anchor_type = 'FormOfGovernment', r.confidence = 'HIGH',
    r.policy_ref = 'FederationPositioningHopsSemantics', r.positioned_at = toString(datetime())
RETURN target.qid;

// Q11514315 historical period
MATCH (sc:SubjectConcept {qid: 'Q17167'}), (target:Entity {qid: 'Q11514315'})
MERGE (sc)-[r:POSITIONED_AS {federation: 'wikidata', property: 'P31', hops: 1}]->(target)
SET r.rel_type = 'INSTANCE_OF_CLASS', r.anchor_type = 'HistoricalPeriod', r.confidence = 'HIGH',
    r.policy_ref = 'FederationPositioningHopsSemantics', r.positioned_at = toString(datetime())
RETURN target.qid;

// Q3024240 historical country
MATCH (sc:SubjectConcept {qid: 'Q17167'}), (target:Entity {qid: 'Q3024240'})
MERGE (sc)-[r:POSITIONED_AS {federation: 'wikidata', property: 'P31', hops: 1}]->(target)
SET r.rel_type = 'INSTANCE_OF_CLASS', r.anchor_type = 'HistoricalCountry', r.confidence = 'HIGH',
    r.policy_ref = 'FederationPositioningHopsSemantics', r.positioned_at = toString(datetime())
RETURN target.qid;

// Q48349 empire
MATCH (sc:SubjectConcept {qid: 'Q17167'}), (target:Entity {qid: 'Q48349'})
MERGE (sc)-[r:POSITIONED_AS {federation: 'wikidata', property: 'P31', hops: 1}]->(target)
SET r.rel_type = 'INSTANCE_OF_CLASS', r.anchor_type = 'FormOfGovernment', r.confidence = 'MEDIUM',
    r.policy_ref = 'FederationPositioningHopsSemantics', r.positioned_at = toString(datetime())
RETURN target.qid;

// Q666680 aristocratic republic
MATCH (sc:SubjectConcept {qid: 'Q17167'}), (target:Entity {qid: 'Q666680'})
MERGE (sc)-[r:POSITIONED_AS {federation: 'wikidata', property: 'P122', hops: 1}]->(target)
SET r.rel_type = 'TYPE_ANCHOR', r.anchor_type = 'FormOfGovernmentType', r.confidence = 'HIGH',
    r.policy_ref = 'FederationPositioningHopsSemantics', r.positioned_at = toString(datetime())
RETURN target.qid;

// Q1747689 Ancient Rome
MATCH (sc:SubjectConcept {qid: 'Q17167'}), (target:Entity {qid: 'Q1747689'})
MERGE (sc)-[r:POSITIONED_AS {federation: 'wikidata', property: 'P361', hops: 1}]->(target)
SET r.rel_type = 'COMPOSITIONAL_PARENT', r.anchor_type = 'CivilisationContext', r.confidence = 'HIGH',
    r.policy_ref = 'FederationPositioningHopsSemantics', r.positioned_at = toString(datetime())
RETURN target.qid;
