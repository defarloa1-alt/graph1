# Phase 2 Quick Start: Run Now
**Minimal instructions to get Phase 2A+2B executing immediately**

---

## TL;DR: 3-Step Start

### STEP 1: Prepare Neo4j (Copy-Paste This)

**Go to:** http://localhost:7474

**Paste this into query editor:**

```cypher
CREATE INDEX entity_is_bridge FOR (e:Entity) ON (e.is_bridge);
CREATE INDEX entity_track FOR (e:Entity) ON (e.track);
CREATE INDEX entity_bridge_type FOR (e:Entity) ON (e.bridge_type);
CREATE INDEX entity_date FOR (e:Entity) ON (e.date);
CREATE INDEX entity_date_birth FOR (e:Entity) ON (e.date_of_birth);
CREATE INDEX entity_date_death FOR (e:Entity) ON (e.date_of_death);
MATCH (e:Entity) WHERE e.track IS NULL SET e.track = "direct_historical", e.is_bridge = false, e.bridge_type = NULL, e.bridge_confidence = NULL, e.temporal_gap = NULL, e.evidence_markers = [], e.bridge_priority = NULL;
MATCH (e:Entity) RETURN COUNT(e) AS entities, apoc.text.join(COLLECT(DISTINCT e.track), ', ') AS tracks;
```

**Press play** ▶️  
**Wait for completion**

✅ Done

---

### STEP 2: Set Up ChatGPT (5 minutes)

1. Go to: https://chat.openai.com
2. Click **"Explore"** (top left) → **"Create a GPT"**
3. Name: **"Historical Knowledge Graph Extractor"**
4. Go to **"Instructions"** field
5. **Copy everything** from here: [GPT_PHASE_2_PARALLEL_PROMPT.md](GPT_PHASE_2_PARALLEL_PROMPT.md)
   - Start from: `You are a specialized knowledge extraction agent...`
   - End at: `Ready? Begin with: "PHASE 2A+2B..."`
6. **Paste into Instructions box**
7. Click **"Save"** (top right)

✅ Done

---

### STEP 3: Run Phase 2 (Copy-Paste to GPT)

**In your new "Historical Knowledge Graph Extractor" GPT, send this message:**

```
Process the Roman Republic Wikipedia article.
Execute PHASE 2A+2B: Simultaneous parallel backlink harvest with two-track validation.

Period: Q17167 (Roman Republic, -509 to -27 BCE)
Depth: 8 hops
Validation: Two-track (direct historical + temporal bridges)
Output format: JSON as specified in instructions.

Begin discovery.
```

✅ Wait 15-20 minutes for GPT to complete

---

## What Happens

**GPT will:**
- Process backlinks to 8 hops depth
- Split into 2 validation tracks:
  - **Track 1 (Direct Historical):** Strict temporal rules → ~1,847 entities
  - **Track 2 (Temporal Bridges):** Evidence markers → ~251 bridges
- Return JSON with all statistics

**Expected Results:**
```
Total Entities: ~2,100
  - Direct Historical: ~1,847
  - Temporal Bridges: ~251
    - Archaeological: 67
    - Historiographic: 58
    - Political Precedent: 42
    - Cultural: 64
    - Scientific: 20
```

---

## After GPT Finishes

**Copy the JSON output** GPT provides, then in **Neo4j Browser**:

```cypher
// Load entities (adapt entity list from GPT output)
UNWIND [
  // PASTE ENTITY LIST HERE from GPT
] AS entity
MERGE (e:Entity {entity_id: entity.entity_id})
SET e.label = entity.label,
    e.type = entity.type,
    e.track = "direct_historical",
    e.is_bridge = false,
    e.confidence = entity.confidence;

// Verify load
MATCH (e:Entity) RETURN COUNT(e);
```

---

## Files You Have

| File | What | When |
|------|------|------|
| **GPT_PHASE_2_PARALLEL_PROMPT.md** | Copy-paste for GPT | Setup step 2 |
| **NEO4J_SCHEMA_UPDATES_PHASE2.md** | Detailed Neo4j scripts | If you need detailed info |
| **PHASE_2_EXECUTION_CHECKLIST.md** | Full checklist (9 steps) | For complete walkthrough |
| **EXPECTED_OUTPUT_TWO_TRACK_VALIDATION.md** | Example output | Understanding results |

---

## TL;DR Timeline

| Step | Time | Action |
|------|------|--------|
| 1 | 2 min | Copy Neo4j script, paste to Neo4j Browser, run |
| 2 | 5 min | Create ChatGPT Custom GPT, paste instructions |
| 3 | 1 min | Send Phase 2 message to GPT |
| — | 15-20 min | **Wait for GPT to process** |
| 4 | 3 min | Copy GPT output, load into Neo4j |
| **Total** | **~30 min** | **Phase 2A+2B complete** |

---

## Yes, You Need Neo4j Updates First

Those are the "neo pushes" you mentioned:
- ✅ Create indexes for fast lookups
- ✅ Add schema properties (is_bridge, track, etc.)
- ✅ Define bridge type classification (5 types as entity properties)

**All in Step 1 Neo4j script above.**

---

## Ready?

```
1. Run Neo4j script
2. Setup GPT
3. Send message
4. Wait
5. Load results
```

✅ Go!
