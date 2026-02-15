# Phase 2 Parallel Execution: Complete Checklist
**Run Phase 2A + 2B simultaneously with Neo4j ready**

---

## BEFORE YOU START

**Prerequisites:**
- [ ] Neo4j running (http://localhost:7474)
- [ ] ChatGPT browser open
- [ ] Both terminals ready

---

## STEP 1: Prepare Neo4j (5 minutes)

**In Neo4j Browser (http://localhost:7474):**

1. | your Neo4j password in**Paste this** entire script into Neo4j Browser query editor:

```cypher
// ===== CREATE INDEXES =====
CREATE INDEX entity_is_bridge FOR (e:Entity) ON (e.is_bridge);
CREATE INDEX entity_track FOR (e:Entity) ON (e.track);
CREATE INDEX entity_bridge_type FOR (e:Entity) ON (e.bridge_type);
CREATE INDEX entity_date FOR (e:Entity) ON (e.date);
CREATE INDEX entity_date_birth FOR (e:Entity) ON (e.date_of_birth);
CREATE INDEX entity_date_death FOR (e:Entity) ON (e.date_of_death);

// ===== UPDATE EXISTING ENTITIES =====
MATCH (e:Entity)
WHERE e.track IS NULL
SET e.track = "direct_historical",
    e.validation_timestamp = datetime(),
    e.is_bridge = false,
    e.bridge_type = NULL,
    e.bridge_confidence = NULL,
    e.temporal_gap = NULL,
    e.evidence_markers = [],
    e.bridge_priority = NULL;

// ===== CREATE BRIDGE TYPE VOCABULARY =====
CREATE (arch:BridgeType {type: "archaeological_discovery", base_confidence: 0.92});
CREATE (hist:BridgeType {type: "historiographic_reinterpretation", base_confidence: 0.85});
CREATE (prec:BridgeType {type: "political_precedent", base_confidence: 0.90});
CREATE (cult:BridgeType {type: "cultural_representation", base_confidence: 0.70});
CREATE (sci:BridgeType {type: "scientific_validation", base_confidence: 0.92});

// ===== VERIFY SETUP =====
MATCH (e:Entity)
RETURN COUNT(e) AS total_entities, 
       apoc.text.join(COLLECT(DISTINCT e.track), ', ') AS tracks;
```

**Press play** ▶️

**Expected output:**
```
total_entities: 2318
tracks: "direct_historical"
```

- [ ] Neo4j schema updated successfully

---

## STEP 2: Copy GPT Prompt (2 minutes)

**Go to:** [GPT_PHASE_2_PARALLEL_PROMPT.md](GPT_PHASE_2_PARALLEL_PROMPT.md)

**Copy everything inside the triple backticks** (from `You are a specialized...` to `...Ready? Begin...`)

- [ ] Prompt copied to clipboard

---

## STEP 3: Set Up ChatGPT Custom GPT (3 minutes)

**In ChatGPT:**

1. Go to **https://chat.openai.com**
2. Click **"Explore"** → **"Create a GPT"**
3. Name it: **"Historical Knowledge Graph Extractor"**
4. In **"Instructions"** field: **Paste the prompt** you copied
5. Click **"Save"**

**In the new GPT chat:**

- [ ] GPT created and saved

---

## STEP 4: Start Phase 2A+2B (2 minutes)

**In ChatGPT (your new Historical Knowledge Graph Extractor GPT), paste:**

```
Process the Roman Republic Wikipedia article.
Execute PHASE 2A+2B: Simultaneous parallel backlink harvest with two-track validation.

Period: Q17167 (Roman Republic, -509 to -27 BCE)
Depth: 8 hops
Validation: Two-track (direct historical + temporal bridges)
Output format: JSON as specified

Begin discovery.
```

- [ ] Phase 2A+2B execution started

**Expected runtime:** 10-20 minutes

---

## STEP 5: Monitor Execution

**While GPT is processing, you'll see:**

```
PHASE 2A+2B: Beginning parallel backlink harvest...

Processing TRACK 1 (Direct Historical)...
  ✓ Filtering entities by temporal boundaries (-509 to -27 BCE)
  ✓ Applying lifespan overlap validation
  ✓ Calculating contemporaneity scores
  → Progress: [████░░░░░░░░░░░░░░] 20%

Processing TRACK 2 (Temporal Bridges) SIMULTANEOUSLY...
  ✓ Detecting evidence markers
  ✓ Identifying bridge types
  → Progress: [████░░░░░░░░░░░░░░] 20%

Merging results...
```

**Expected progress indicators:**
- Track 1: "2,318 entities → filtering → ~1,847 direct accepted (47.9%)"
- Track 2: "1,200+ candidate bridges → filtering → ~251 accepted (20.9%)"

- [ ] Execution completed (GPT has final JSON output)

---

## STEP 6: GPT Output Verification

**GPT will output structured JSON like:**

```json
{
  "phase": "2_parallel_backlink_harvest",
  "timestamp": "2026-02-15T14:30:00Z",
  "track_1_direct_historical": {
    "total_discovered": 3847,
    "total_accepted": 1847,
    "acceptance_rate": "47.9%",
    "entities": [...]
  },
  "track_2_bridges": {
    "total_candidate_bridges": 1200,
    "total_accepted_bridges": 251,
    "acceptance_rate": "20.9%",
    "bridge_types": {
      "archaeological": 67,
      "historiographic": 58,
      "political_precedent": 42,
      "cultural": 64,
      "scientific": 20
    },
    "entities": [...]
  },
  "merged_output": {
    "total_entities": 2098,
    "direct_historical": 1847,
    "temporal_bridges": 251,
    "bridge_percentage": "11.9%"
  }
}
```

- [ ] Verify output includes both tracks
- [ ] Verify ~251 bridges discovered
- [ ] Verify bridge types (archaeological, historiographic, etc.)

---

## STEP 7: Load Results into Neo4j (5 minutes)

**Copy GPT output**, then in **Neo4j Browser**, run:

```cypher
// ===== LOAD DIRECT HISTORICAL ENTITIES =====
UNWIND [
  {entity_id: "hum_julius_caesar_q1048", label: "Julius Caesar", type: "Human", date_of_birth: -100, date_of_death: -44, qid: "Q1048", confidence: 0.95},
  // ... paste all direct historical entities from GPT output here
] AS entity
MERGE (e:Entity {entity_id: entity.entity_id})
SET e.label = entity.label,
    e.type = entity.type,
    e.date_of_birth = entity.date_of_birth,
    e.date_of_death = entity.date_of_death,
    e.qid = entity.qid,
    e.track = "direct_historical",
    e.is_bridge = false,
    e.confidence = entity.confidence,
    e.created_phase = "2a";

// ===== LOAD BRIDGE ENTITIES =====
UNWIND [
  {entity_id: "evt_2024_perugia_excavation", label: "2024 Perugia Excavation", type: "Event", date: 2024, bridge_type: "archaeological_discovery", confidence: 0.94, temporal_gap: 2065},
  // ... paste all bridge entities from GPT output here
] AS bridge
MERGE (e:Entity {entity_id: bridge.entity_id})
SET e.label = bridge.label,
    e.type = bridge.type,
    e.date = bridge.date,
    e.track = "bridging_discovery",
    e.is_bridge = true,
    e.bridge_type = bridge.bridge_type,
    e.bridge_confidence = bridge.confidence,
    e.temporal_gap = bridge.temporal_gap,
    e.created_phase = "2b";

// ===== VERIFY LOAD =====
MATCH (e:Entity)
RETURN 
  COUNT(CASE WHEN e.track = "direct_historical" THEN 1 END) AS direct_count,
  COUNT(CASE WHEN e.is_bridge = true THEN 1 END) AS bridge_count;
```

**Expected output:**
```
direct_count: 1847 (approximate)
bridge_count: 251 (approximate)
```

- [ ] Results loaded into Neo4j

---

## STEP 8: Create Bridge Relationships in Neo4j (3 minutes)

**For each bridge entity, connect to ancient target:**

```cypher
// Example: Connect 2024 Perugia excavation to ancient Siege
MATCH (modern:Entity {entity_id: "evt_2024_perugia_excavation"})
MATCH (ancient:Entity {label: "Siege of Perusia"})
CREATE (modern)-[r:DISCOVERED_EVIDENCE_FOR {
  temporal_gap: 2065,
  confidence: 0.94,
  is_bridge: true,
  bridge_type: "archaeological_discovery",
  evidence_text: "Archaeological confirmation of siege location",
  created: datetime()
}]->(ancient)
RETURN r;
```

*Repeat for all bridges* (or write script to automate)

- [ ] Bridge relationships created

---

## STEP 9: Verify Complete Result

**In Neo4j Browser, run:**

```cypher
// Entity count by track
MATCH (e:Entity)
RETURN 
  e.track AS track,
  COUNT(e) AS count
ORDER BY count DESC;

// Bridge statistics
MATCH (bridge:Entity {is_bridge: true})
RETURN
  COUNT(*) AS total_bridges,
  COUNT(DISTINCT bridge.bridge_type) AS bridge_types,
  COLLECT(DISTINCT bridge.bridge_type) AS types_found,
  AVG(bridge.bridge_confidence) AS avg_confidence;

// Sample bridges
MATCH (bridge:Entity {is_bridge: true})
RETURN bridge.label, bridge.bridge_type, bridge.bridge_confidence
LIMIT 10;
```

**Expected output:**
```
Track breakdown:
  direct_historical: 1847
  bridging_discovery: 251

Bridge statistics:
  total_bridges: 251
  bridge_types: 5
  types_found: ["archaeological_discovery", "historiographic_reinterpretation", "political_precedent", "cultural_representation", "scientific_validation"]
  avg_confidence: 0.83

Sample bridges shown with confidence scores
```

- [ ] All results verified

---

## FINAL CHECKLIST

✅ **Phase 2 Complete When:**

- [ ] Neo4j schema updated (indexes + bridge types)
- [ ] GPT prompt set up in Custom GPT
- [ ] Phase 2A+2B executed (dual-track validation)
- [ ] ~2,100 total entities discovered (1,847 direct + 251 bridges)
- [ ] Entities loaded into Neo4j with metadata
- [ ] Bridge relationships created
- [ ] Statistics verified in Neo4j

**Total Time:** ~40 minutes

---

## Next Steps: Phase 3

When Phase 2 is complete:

```
PHASE 3: Wikipedia Text Entity Resolution
Input: 2,100 entities from Phase 2
Action: Match to Wikipedia with authority links (LCSH, FAST, LCC, Wikidata)
Output: Authority-enriched entity records ready for Phase 4
```

**Start Phase 3 when:**
- [ ] All 2,100 entities in Neo4j
- [ ] Bridge relationships created
- [ ] Ready to proceed to relationship extraction

---

## Files Reference

| File | Purpose | Use When |
|------|---------|----------|
| [GPT_PHASE_2_PARALLEL_PROMPT.md](GPT_PHASE_2_PARALLEL_PROMPT.md) | Complete GPT instructions | Pasting into Custom GPT |
| [NEO4J_SCHEMA_UPDATES_PHASE2.md](NEO4J_SCHEMA_UPDATES_PHASE2.md) | Neo4j setup scripts | Running in Neo4j Browser |
| [EXPECTED_OUTPUT_TWO_TRACK_VALIDATION.md](EXPECTED_OUTPUT_TWO_TRACK_VALIDATION.md) | Example output | Understanding results |
| [temporal_bridge_discovery.py](scripts/processing/temporal_bridge_discovery.py) | Validator code | Reference/integration |

---

**Ready to run Phase 2?** ✅

Start with: **Step 1 (Neo4j) → Step 2 (Copy Prompt) → Step 3 (Setup GPT) → Step 4 (Execute)**
