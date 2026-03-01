# Federation Positioning — Run One at a Time

If you get "Driver is not connected": **reconnect** to your Neo4j instance, then run each query below **separately** in Neo4j Browser. Wait for each to complete before running the next.

---

**Step 1 — SYS_Policy**
```cypher
MERGE (p:SYS_Policy {name: 'FederationPositioningHopsSemantics'})
SET p.definition   = '{"0": "self", "1": "direct parent", "2": "grandparent", "n": "nth ancestor"}',
    p.rule         = 'shortest path from domain root to anchor through traversed properties',
    p.last_updated = toString(datetime()),
    p.updated_by   = 'sca_federation_positioning'
RETURN p.name;
```

---

**Step 2 — Q1307214**
```cypher
MATCH (sc:SubjectConcept {qid: 'Q17167'}), (target:Entity {qid: 'Q1307214'})
MERGE (sc)-[r:POSITIONED_AS {federation: 'wikidata', property: 'P31', hops: 1}]->(target)
SET r.rel_type = 'INSTANCE_OF_CLASS', r.anchor_type = 'FormOfGovernment', r.confidence = 'HIGH',
    r.policy_ref = 'FederationPositioningHopsSemantics', r.positioned_at = toString(datetime())
RETURN target.qid;
```

---

**Step 3 — Q11514315**
```cypher
MATCH (sc:SubjectConcept {qid: 'Q17167'}), (target:Entity {qid: 'Q11514315'})
MERGE (sc)-[r:POSITIONED_AS {federation: 'wikidata', property: 'P31', hops: 1}]->(target)
SET r.rel_type = 'INSTANCE_OF_CLASS', r.anchor_type = 'HistoricalPeriod', r.confidence = 'HIGH',
    r.policy_ref = 'FederationPositioningHopsSemantics', r.positioned_at = toString(datetime())
RETURN target.qid;
```

---

**Step 4 — Q3024240**
```cypher
MATCH (sc:SubjectConcept {qid: 'Q17167'}), (target:Entity {qid: 'Q3024240'})
MERGE (sc)-[r:POSITIONED_AS {federation: 'wikidata', property: 'P31', hops: 1}]->(target)
SET r.rel_type = 'INSTANCE_OF_CLASS', r.anchor_type = 'HistoricalCountry', r.confidence = 'HIGH',
    r.policy_ref = 'FederationPositioningHopsSemantics', r.positioned_at = toString(datetime())
RETURN target.qid;
```

---

**Step 5 — Q48349**
```cypher
MATCH (sc:SubjectConcept {qid: 'Q17167'}), (target:Entity {qid: 'Q48349'})
MERGE (sc)-[r:POSITIONED_AS {federation: 'wikidata', property: 'P31', hops: 1}]->(target)
SET r.rel_type = 'INSTANCE_OF_CLASS', r.anchor_type = 'FormOfGovernment', r.confidence = 'MEDIUM',
    r.policy_ref = 'FederationPositioningHopsSemantics', r.positioned_at = toString(datetime())
RETURN target.qid;
```

---

**Step 6 — Q666680**
```cypher
MATCH (sc:SubjectConcept {qid: 'Q17167'}), (target:Entity {qid: 'Q666680'})
MERGE (sc)-[r:POSITIONED_AS {federation: 'wikidata', property: 'P122', hops: 1}]->(target)
SET r.rel_type = 'TYPE_ANCHOR', r.anchor_type = 'FormOfGovernmentType', r.confidence = 'HIGH',
    r.policy_ref = 'FederationPositioningHopsSemantics', r.positioned_at = toString(datetime())
RETURN target.qid;
```

---

**Step 7 — Q1747689**
```cypher
MATCH (sc:SubjectConcept {qid: 'Q17167'}), (target:Entity {qid: 'Q1747689'})
MERGE (sc)-[r:POSITIONED_AS {federation: 'wikidata', property: 'P361', hops: 1}]->(target)
SET r.rel_type = 'COMPOSITIONAL_PARENT', r.anchor_type = 'CivilisationContext', r.confidence = 'HIGH',
    r.policy_ref = 'FederationPositioningHopsSemantics', r.positioned_at = toString(datetime())
RETURN target.qid;
```

---

**Note:** If any step returns 0 rows, that Entity may not exist in your graph. Skip it and continue. After all steps, run verification 4a and 4e from the runbook.
