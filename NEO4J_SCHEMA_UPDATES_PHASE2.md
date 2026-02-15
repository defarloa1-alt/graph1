# Neo4j Schema Updates for Two-Track Temporal Validation
**Execute these Cypher scripts BEFORE running Phase 2**

---

## STEP 1: Create Bridge Metadata Indexes
**Run in Neo4j Browser**

```cypher
// Create index for fast bridge entity lookups
CREATE INDEX entity_is_bridge FOR (e:Entity) ON (e.is_bridge);
CREATE INDEX entity_track FOR (e:Entity) ON (e.track);
CREATE INDEX entity_bridge_type FOR (e:Entity) ON (e.bridge_type);

// Create indexes for temporal bridge queries
CREATE INDEX relationship_is_bridge FOR (r:IS_BRIDGE_RELATIONSHIP) ON (r.temporal_gap);
CREATE INDEX relationship_bridge_priority FOR (r:IS_BRIDGE_RELATIONSHIP) ON (r.priority);

// Create indexes for fast validation queries
CREATE INDEX entity_date FOR (e:Entity) ON (e.date);
CREATE INDEX entity_date_birth FOR (e:Entity) ON (e.date_of_birth);
CREATE INDEX entity_date_death FOR (e:Entity) ON (e.date_of_death);

CALL db.awaitIndexes();
```

---

## STEP 2: Update Entity Node Schema
**Add properties for two-track validation**

```cypher
// Update all existing entities to include track property
// (Default to "direct_historical" for backward compatibility)
MATCH (e:Entity)
WHERE e.track IS NULL
SET e.track = "direct_historical",
    e.validation_timestamp = datetime(),
    e.requires_review = false;

// Add bridge metadata properties (null for non-bridge entities)
MATCH (e:Entity)
SET e.is_bridge = false,
    e.bridge_type = NULL,
    e.bridge_confidence = NULL,
    e.temporal_gap = NULL,
    e.evidence_markers = [],
    e.bridge_priority = NULL;

// Confirm schema update
MATCH (e:Entity) RETURN COUNT(e) AS total_entities;
```

---

## STEP 3: Create Temporal Bridge Relationship Type
**New relationship node type for bridges**

```cypher
// Create bridge relationship nodes
// These connect modern discoveries to ancient facts
// DO THIS ONCE to establish pattern

CREATE (bridge_pattern:RelationshipPattern {
  name: "TEMPORAL_BRIDGE_RELATIONSHIP",
  description: "Relationship connecting modern entity to ancient entity through evidential chain",
  is_bridge_pattern: true,
  created: datetime()
});

// Create bridge type vocabulary
CREATE (arch_bridge:BridgeType {
  type: "archaeological_discovery",
  base_confidence: 0.92,
  created: datetime()
});

CREATE (hist_bridge:BridgeType {
  type: "historiographic_reinterpretation",
  base_confidence: 0.85,
  created: datetime()
});

CREATE (prec_bridge:BridgeType {
  type: "political_precedent",
  base_confidence: 0.90,
  created: datetime()
});

CREATE (cult_bridge:BridgeType {
  type: "cultural_representation",
  base_confidence: 0.70,
  created: datetime()
});

CREATE (sci_bridge:BridgeType {
  type: "scientific_validation",
  base_confidence: 0.92,
  created: datetime()
});

RETURN arch_bridge, hist_bridge, prec_bridge, cult_bridge, sci_bridge;
```

---

## STEP 4: Create Example Bridge Entities (Test Data)
**Load sample bridge to verify schema**

```cypher
// Create a modern entity (bridge source)
CREATE (excavation:Entity {
  entity_id: "evt_2024_perugia_excavation_test_001",
  label: "2024 Perugia Excavation",
  type: "Event",
  date: 2024,
  description: "Archaeologists discovered lead sling bullets confirming Siege of Perusia location",
  qid: "LOCAL_perugia_2024",
  track: "bridging_discovery",
  is_bridge: true,
  bridge_type: "archaeological_discovery",
  bridge_confidence: 0.94,
  bridge_priority: "HIGH",
  evidence_markers: ["excavated", "discovered", "archaeologists", "confirmed"],
  created_timestamp: datetime(),
  source: "Wikipedia_backlink_discovery"
})
RETURN excavation;

// Create matching ancient entity
CREATE (ancient_siege:Entity {
  entity_id: "evt_siege_perusia_q12345",
  label: "Siege of Perusia",
  type: "Event",
  date: -41,
  description: "Siege during Second Civil War of Roman Republic",
  qid: "Q12345",
  track: "direct_historical",
  is_bridge: false,
  created_timestamp: datetime(),
  source: "Wikidata"
})
RETURN ancient_siege;

// Create bridge relationship between them
CREATE (excavation)-[bridge:DISCOVERED_EVIDENCE_FOR {
  temporal_gap: 2065,
  confidence: 0.94,
  priority: "HIGH",
  is_bridge: true,
  bridge_type: "archaeological_discovery",
  evidence_text: "Lead sling bullets found at site",
  created: datetime()
}]->(ancient_siege)
RETURN bridge;
```

---

## STEP 5: Verify Schema & Query Test Data
**Confirm everything working**

```cypher
// Query 1: Count by track
MATCH (e:Entity)
RETURN 
  e.track,
  COUNT(e) AS count
ORDER BY count DESC;

// Expected output:
// direct_historical: 2318 (existing)
// bridging_discovery: 1 (test data)

// Query 2: Show all bridge entities
MATCH (e:Entity {is_bridge: true})
RETURN 
  e.label,
  e.bridge_type,
  e.bridge_confidence,
  e.temporal_gap,
  e.bridge_priority
LIMIT 10;

// Query 3: Show bridge relationships
MATCH (source:Entity {is_bridge: true})
  -[bridge:DISCOVERED_EVIDENCE_FOR|REINTERPRETED|DREW_INSPIRATION_FROM]-
  (target:Entity)
RETURN 
  source.label,
  TYPE(bridge) AS relationship_type,
  target.label,
  bridge.temporal_gap,
  bridge.confidence;

// Query 4: Bridge statistics
MATCH (e:Entity {is_bridge: true})
RETURN
  COUNT(e) AS total_bridges,
  COUNT(DISTINCT e.bridge_type) AS bridge_types,
  AVG(e.bridge_confidence) AS avg_confidence,
  MIN(e.temporal_gap) AS min_gap,
  MAX(e.temporal_gap) AS max_gap;
```

---

## STEP 6: Create GPT Query Endpoints
**These are the Cypher queries GPT will call**

```cypher
// ENDPOINT 1: Search entities by track
MATCH (e:Entity {track: $track})
WHERE e.date >= $date_min AND e.date <= $date_max
RETURN 
  e.entity_id,
  e.label,
  e.type,
  e.date,
  e.confidence
LIMIT 20;

// Usage: GPT calls this to find entities by historical period or modern date

// ─────────────────────────────────────────────────────

// ENDPOINT 2: Find bridge relationships for an entity
MATCH (e:Entity {entity_id: $entity_id})
  -[bridge]-
  (connected:Entity)
WHERE bridge.is_bridge = true
RETURN
  e.label AS source_entity,
  TYPE(bridge) AS relationship_type,
  connected.label AS target_entity,
  bridge.temporal_gap AS gap_years,
  bridge.bridge_type AS bridge_type,
  bridge.confidence AS confidence,
  bridge.evidence_text AS evidence;

// Usage: GPT asks "Show bridges for Julius Caesar"
// Returns all modern discoveries/reinterpretations connected to him

// ─────────────────────────────────────────────────────

// ENDPOINT 3: Find modern perspective on ancient claim
MATCH (ancient:Entity)
  <-[bridge:REINTERPRETED|VALIDATED_CLAIM_ABOUT|CHALLENGED_NARRATIVE_OF]-
  (modern:Entity)
WHERE bridge.is_bridge = true
  AND ancient.qid = $ancient_qid
RETURN
  ancient.label AS ancient_topic,
  modern.label AS modern_source,
  TYPE(bridge) AS interpretation_type,
  bridge.evidence_text AS modern_view,
  bridge.confidence AS confidence;

// Usage: GPT asks "How do modern historians interpret Roman citizenship?"
// Returns scholarly reinterpretations

// ─────────────────────────────────────────────────────

// ENDPOINT 4: Find all bridges by type
MATCH (source:Entity {is_bridge: true})
  -[bridge]-
  (target:Entity)
WHERE source.bridge_type = $bridge_type
RETURN
  source.label AS modern_entity,
  TYPE(bridge) AS relationship,
  target.label AS ancient_entity,
  bridge.temporal_gap,
  bridge.confidence,
  source.bridge_priority AS priority
ORDER BY source.bridge_confidence DESC;

// Usage: GPT asks "Show archaeological bridges"
// Returns all excavations validating ancient claims

// ─────────────────────────────────────────────────────

// ENDPOINT 5: Statistics dashboard
MATCH (e:Entity)
RETURN
  COUNT(CASE WHEN e.track = "direct_historical" THEN 1 END) AS historical_entities,
  COUNT(CASE WHEN e.is_bridge = true THEN 1 END) AS bridge_entities,
  COUNT(DISTINCT e.bridge_type) AS bridge_types,
  AVG(CASE WHEN e.is_bridge = true THEN e.bridge_confidence ELSE NULL END) AS avg_bridge_confidence;

// Usage: System queries for dashboard metrics
```

---

## STEP 7: Grant Neo4j Access to GPT
**If using MCP server or REST API**

```cypher
// Create read-only user for GPT queries
CREATE USER gpt_query_user SET PASSWORD 'generate_strong_password_here' CHANGE REQUIRED false;

// Grant read permissions on entities and relationships
GRANT READ ON GRAPH neo4j TO gpt_query_user;

// Grant procedure execution (for aggregations)
GRANT EXECUTE PROCEDURE ON DBMS TO gpt_query_user;

// Example queries this user can run:
RETURN apoc.version();  // Check system info
```

---

## STEP 8: Create Cypher Query Template for Phase 2 Output
**This is what GPT will write to when Phase 2 completes**

```cypher
// Bulk-load Phase 2 direct historical entities
UNWIND $entities AS entity
CREATE (e:Entity {
  entity_id: entity.entity_id,
  label: entity.label,
  type: entity.type,
  date_of_birth: entity.date_of_birth,
  date_of_death: entity.date_of_death,
  date: entity.date,
  qid: entity.qid,
  lcsh_id: entity.lcsh_id,
  fast_id: entity.fast_id,
  description: entity.description,
  track: "direct_historical",
  is_bridge: false,
  confidence: entity.confidence,
  authority_source: entity.authority_source,
  created_timestamp: datetime(),
  phase: "2a_direct_historical"
});

// ─────────────────────────────────────────────────────

// Bulk-load Phase 2 bridge entities
UNWIND $bridge_entities AS bridge_entity
CREATE (e:Entity {
  entity_id: bridge_entity.entity_id,
  label: bridge_entity.label,
  type: bridge_entity.type,
  date: bridge_entity.date,
  qid: bridge_entity.qid,
  description: bridge_entity.description,
  track: "bridging_discovery",
  is_bridge: true,
  bridge_type: bridge_entity.bridge_type,
  bridge_confidence: bridge_entity.confidence,
  bridge_priority: bridge_entity.priority,
  temporal_gap: bridge_entity.temporal_gap,
  evidence_markers: bridge_entity.evidence_markers,
  created_timestamp: datetime(),
  phase: "2b_temporal_bridges"
});

// ─────────────────────────────────────────────────────

// Create bridge relationships
UNWIND $bridge_relationships AS rel
MATCH (source:Entity {entity_id: rel.source_id})
MATCH (target:Entity {entity_id: rel.target_id})
CREATE (source)-[r:DISCOVERED_EVIDENCE_FOR|REINTERPRETED|DREW_INSPIRATION_FROM|VALIDATED_CLAIM_ABOUT|DRAMATIZED {
  temporal_gap: rel.temporal_gap,
  confidence: rel.confidence,
  priority: rel.priority,
  is_bridge: true,
  bridge_type: rel.bridge_type,
  evidence_text: rel.evidence_text,
  created: datetime()
}]->(target);
```

---

## HOW TO EXECUTE THESE SCRIPTS

1. **Open Neo4j Browser** (http://localhost:7474)
2. **Copy each section** one at a time
3. **Paste into query editor** and press play
4. **Wait for completion** before next section

**Order:**
1. ✅ Step 1 (Indexes)
2. ✅ Step 2 (Entity schema)
3. ✅ Step 3 (Bridge types)
4. ✅ Step 4 (Test data)
5. ✅ Step 5 (Verification)
6. ✅ Step 6 (Query endpoints - reference only)
7. ✅ Step 7 (GPT user - if using MCP)
8. ✅ Step 8 (Load template - reference only)

**Typical execution time:** 2-5 minutes total

---

## VERIFICATION CHECKLIST

After running all steps, verify:

```cypher
// Check 1: Indexes created
CALL db.indexes() YIELD name;

// Check 2: Entity properties exist
MATCH (e:Entity) 
RETURN keys(e) 
LIMIT 1;

// Check 3: Bridge type nodes created
MATCH (bt:BridgeType)
RETURN COUNT(bt);
// Expected: 5 (archaeological, historiographic, political, cultural, scientific)

// Check 4: Test bridge entity exists
MATCH (e:Entity {entity_id: "evt_2024_perugia_excavation_test_001"})
RETURN e.label, e.is_bridge, e.bridge_type;
// Expected: "2024 Perugia Excavation", true, "archaeological_discovery"

// Check 5: Test bridge relationship exists
MATCH (e:Entity {is_bridge: true})
  -[r]-
  (ancient:Entity)
RETURN COUNT(r);
// Expected: >= 1
```

---

## AFTER PHASE 2 COMPLETES

GPT will output JSON with ~2,250 total entities. 

**To load them into Neo4j:**

```cypher
// Use Step 8 load templates
// Adapt the $entities and $bridge_entities parameters from GPT output

// Load direct historical (Phase 2A output)
UNWIND gpt_output.track_1_direct_historical.entities AS entity
CREATE (e:Entity { ... });

// Load bridges (Phase 2B output)
UNWIND gpt_output.track_2_bridges.entities AS bridge
CREATE (e:Entity { ... });

// Create bridge relationships
UNWIND gpt_output.track_2_bridges.relationships AS rel
CREATE (source)-[r:DISCOVERED_EVIDENCE_FOR]->(target);
```

---

## Ready to Run Phase 2?

✅ Execute all 8 steps above  
✅ Verify each step completes successfully  
✅ Then tell GPT: "Neo4j schema ready. Begin Phase 2A+2B parallel backlink harvest."

Neo4j will be prepared to accept both direct historical entities AND temporal bridge entities in parallel.
