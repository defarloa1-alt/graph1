# Agent Handoff — 2026-03-07

**Purpose:** Orient a new Claude Code session to the Chrystallum codebase and the Domain Initiator pipeline built today. Read this first.

---

## How to Read the Graph (MCP tools)

The Chrystal MCP server gives you read-only access to the live Neo4j graph. Use these to understand structure before writing code:

| MCP Tool | What it does | Example use |
|----------|-------------|-------------|
| `run_cypher_readonly` | Execute any MATCH query (500 char limit, 500 row cap) | `MATCH (n:SubjectConcept) RETURN n.label, n.lcsh_id` |
| `list_policies` | All SYS_Policy nodes with decision table links | Understand governance rules |
| `list_thresholds` | All SYS_Threshold nodes with values and units | Know the numeric limits |
| `get_domain_structure` | Domain overview | Top-level orientation |
| `get_federation_sources` | All SYS_FederationSource nodes | See what's connected |
| `get_policy` | Single policy by name | e.g. `BacklinkRouting` |
| `get_threshold` | Single threshold by name | e.g. `level2_child_overload` |
| `get_subject_concepts` | All SubjectConcept nodes | See what subjects exist |

**Always check the graph before assuming structure.** The graph is the source of truth.

### Key Cypher patterns

```cypher
-- Node counts by label
MATCH (n) RETURN labels(n)[0] AS label, count(*) AS cnt ORDER BY cnt DESC

-- Decision tables (the spec IS the graph)
MATCH (d:SYS_DecisionTable) RETURN d.table_id, d.label

-- Federation sources with status
MATCH (f:SYS_FederationSource) RETURN f.source_id, f.label, f.phase, f.survey_status

-- Relationship types
MATCH (r:SYS_RelationshipType) RETURN r.rel_type, r.domain LIMIT 30
```

---

## Graph Shape (as of 2026-03-07)

| Label | Count | Notes |
|-------|-------|-------|
| Place | 44,193 | Geo backbone (Pleiades + enriched) |
| PlaceName | 38,321 | Place name variants |
| Pleiades_Place | 32,572 | Raw Pleiades import |
| Entity | 14,637 | DPRR persons + others |
| LCC_Class | 4,490 | Library of Congress Classification |
| Year | 4,030 | Temporal backbone |
| Discipline | 1,363 | Academic disciplines |
| Periodo_Period | 1,118 | PeriodO temporal |
| Cognomen/Nomen/Gens | 2,502 | Roman naming (prosopography) |
| SYS_PropertyMapping | 500 | Wikidata PID → facet maps |
| Position | 171 | Roman offices (was "Office") |
| SubjectConcept | 22 | Domain subjects (1 seed + 21 DI-written) |
| SYS_DecisionTable | 21 | D1-D21 (the spec IS these rows) |
| SYS_Policy | 20 | Governance rules |
| Facet | 18 | The 18 canonical facets |
| SYS_FederationSource | 17 | External data sources |
| SYS_FacetRouter | 38 | Facet routing patterns |

### 18 Facets

Archaeological, Artistic, Biographic, Communication, Cultural, Demographic, Diplomatic, Economic, Environmental, Geographic, Intellectual, Linguistic, Military, Political, Religious, Scientific, Social, Technological.

### 17 Federation Sources

| source_id | Phase | Status |
|-----------|-------|--------|
| wikidata | A | operational |
| dprr | A | survey complete (7,335 nodes) |
| pleiades | A | operational |
| trismegistos | A | operational |
| periodo | A | operational |
| lcsh_fast_lcc | A | operational |
| viaf | A | operational |
| lgpn | B | partial |
| getty_aat | B | partial |
| edh | C | planned |
| ocd | C | planned |
| open_alex | D | corpus source (NEW) |
| open_library | D | corpus source (NEW) |
| open_syllabus | D | corpus source (NEW) |
| perseus_digital_library | D | corpus source (NEW) |
| chrr | D | planned |
| crro | D | planned |

### 21 Decision Tables (D1-D21)

All in graph as `SYS_DecisionTable` nodes with `SYS_DecisionRow` children. Key ones for DI:
- **D8**: SFA facet assignment
- **D12**: SubjectConcept split trigger (child_overload=12, crosslink_ratio=0.3)
- **D13**: SFA drift alert
- **D15-D18**: Federation scoring
- **D19**: DPRR relationship normalization

---

## Domain Initiator Pipeline (Built 2026-03-07)

This is the main deliverable of the session. Three-step pipeline:

```
harvest.py  →  {seed}_di_harvest.json   (full Wikidata universe + disciplines + corpus endpoints)
     ↓
classify.py →  {seed}_di_classify.json  (per-facet deltas for SCA routing)
     ↓
               SCA router → 18 SFAs     (NOT YET BUILT)
```

### Step 1: harvest.py

**Location:** `scripts/agents/domain_initiator/harvest.py`

**What it does:**
1. Fetches **backlinks** (X → seed) via 9 properties: P31/P279/P361/P1344/P793/P17/P131/P276/P706
2. Fetches **forward links** (seed → X) from all entity-valued claims on seed
3. Deduplicates — entities in both directions tagged as "both"
4. Extracts: instance_of, subclass_of, geo_properties, external_ids, subject backbone (FAST/Dewey/LCNAF)
5. **Discipline traversal** (NEW): Seed → P361/P31/P279/P2348 → hop2 P361 → P2579 (studied in) → academic disciplines → P527 sub-disciplines → authority IDs
6. **Corpus endpoint discovery** (NEW): Probes OpenAlex, Internet Archive, Open Library live; builds query keys for WorldCat, Perseus, JSTOR, Google Books, HathiTrust, Open Syllabus, Wikidata P921, LoC, FAST, VIAF, GND (14 endpoints total)

**Run:** `python scripts/agents/domain_initiator/harvest.py --seed Q17167`
**Output:** `output/di_harvest/Q17167_di_harvest.json`

**Q17167 stats:**
- 109 candidates (29 forward + 75 backlink + 5 both)
- 39 backbone links (18 LCNAF + 14 Dewey + 7 FAST)
- 4 disciplines + 10 sub-disciplines
- Corpus: OpenAlex 7,309 works | Internet Archive 309 texts | Open Library 121 books

### Step 2: classify.py

**Location:** `scripts/agents/domain_initiator/classify.py`

**What it does:** Three-tier facet routing:
1. **Tier 1** (weight 8x): instance_of/subclass_of QIDs + self-QID matched against facet registry anchors + TYPE_EXTENSIONS
2. **Tier 2** (weight 1x): PIDs vs SYS_PropertyMapping from graph (static fallback). Deduplicated by PID per facet.
3. **Tier 3** (weight 2x): External ID PIDs → federation source routing

**Run:** `python scripts/agents/domain_initiator/classify.py --harvest output/di_harvest/Q17167_di_harvest.json`
**Output:** `output/di_classify/Q17167_di_classify.json`

**Q17167 stats:** 15 facets activated, 96 routed, 11 temporal, 2 unrouted. Military 19p, Economic 27p, Political 10p, Geographic 29p+62s, Linguistic 2p, Religious 1p.

### Step 3: SCA Router (NOT BUILT)

The SCA reads `facet_deltas[]` from classify output and dispatches each facet bundle to its SFA. Each SFA receives:

1. **Facet delta** — candidates (QID + label + role + score + evidence signals), federation sources activated
2. **Discipline traversal** — academic disciplines with authority IDs
3. **Corpus endpoints** — 14 sources with query keys and live counts
4. **Domain context** — seed LCSH tether, sub-subjects from backbone

**SFA training flow** (architectural decision, not yet implemented):
- SFA traverses seed → discipline → corpus endpoints
- Filters corpus by facet keywords (e.g., Military SFA searches "Roman army legion warfare" in OpenAlex)
- Trains on top-cited works + primary sources from Internet Archive
- **Then** evaluates its candidates with disciplinary grounding

---

## Discipline Traversal Architecture

The key insight: certain Wikidata properties lead from a domain seed to academic disciplines, which map to a scholarly corpus.

```
Q17167 (Roman Republic)
  → P361 → Q1747689 (Ancient Rome) → P2579 → Q435608 (ancient history)
  → P2348 → Q486761 (classical antiquity) → P2579 → Q495527 (classical philology) [LCSH: sh85026710]
  → P2348 → Q486761 → P2579 → Q112939719 (Classical Greek & Roman history)
      → P527 → Q830852 (history of ancient Rome)
      → P527 → Q7798 (History of ancient Greece)
  → P361 → Q1747689 → P361 → Q120754777 (Roman civilization) → P2579 → Q136980874 (Roman studies)
      → P279 children → Q2345364 (Roman historiography), Q136980940 (ancient Roman studies)
```

The authority IDs (LCSH/Dewey) on discipline QIDs become query keys into corpus sources. The LCSH on classical philology (sh85026710) and the Dewey codes (480, 091) are directly queryable in WorldCat, Google Books, HathiTrust.

---

## Key Files

| File | Purpose |
|------|---------|
| `scripts/agents/domain_initiator/harvest.py` | Bidirectional harvest + discipline traversal + corpus discovery |
| `scripts/agents/domain_initiator/classify.py` | Three-tier facet classifier |
| `scripts/agents/domain_initiator/README.md` | Pipeline docs with stats and corpus endpoint table |
| `output/di_harvest/Q17167_di_harvest.json` | Full harvest output (109 candidates + disciplines + 14 endpoints) |
| `output/di_classify/Q17167_di_classify.json` | Classification output (15 facets, 96 routed) |
| `Facets/facet_registry_master.json` | 18 canonical facets with anchor QIDs (used by classifier Tier 1) |
| `docs/DOMAIN_INITIATOR.md` | Architecture doc |
| `docs/SCA_SFA_CONTRACT.md` | SCA / SFA division of labor |
| `Key Files/chrystallum_di_constitution.jsx` | DI constitution (self-describing) |

### SCA / SubjectConcept scripts (pre-existing, detached from harvest)

| File | Purpose |
|------|---------|
| `scripts/sca/build_subject_schema.py` | LLM-based SubjectConcept proposal (does NOT consume harvest) |
| `scripts/sca/write_subject_concepts.py` | Writes SubjectConcepts to Neo4j from JSON |
| `scripts/sca/write_facet_router.py` | Writes SYS_FacetRouter nodes |
| `scripts/sca/write_di_governance.py` | Writes policies, thresholds, curation decisions |
| `scripts/sca/verify_and_patch_lcsh.py` | LCSH validation (18/22 LLM-guessed sh-IDs were wrong) |
| `scripts/sca/resolve_lcsh_gaps.py` | Gap resolution for missing LCSH |

---

## What Was Done This Session (2026-03-07)

1. **Built classify.py** — the missing DI step 2. Three-tier facet routing with TYPE_EXTENSIONS, SYS_PropertyMapping from graph, deduplication. ~450 lines.

2. **Expanded harvest.py** — Added forward links (seed → X) alongside existing backlinks (X → seed). Q17167 went from 32 to 109 candidates.

3. **Added discipline traversal** — Multi-hop P361/P31/P279/P2348 → P2579 → P527/P279 chain reaching academic disciplines with authority IDs.

4. **Added corpus endpoint discovery** — 14 sources (3 probed live, 10 ready with query keys, 1 needing IDs). OpenAlex, Internet Archive, Open Library, WorldCat, Perseus, JSTOR, Google Books, HathiTrust, Open Syllabus, Wikidata P921, LoC, FAST, VIAF, GND.

5. **Fixed classifier issues:**
   - Tier weight imbalance (battles mis-assigned as geographic primary) → Tier 1 weight raised to 8x
   - Tier 2 PID deduplication (P17 ×3 countries → counts once per facet)
   - Self-QID matching (Q337547 ancient Roman religion directly matched)
   - Expanded TYPE_EXTENSIONS for geographic, political, religious, linguistic, temporal entities

---

## What's Next

### Immediate

1. **Wire classify output to SCA router** — The SCA reads facet_deltas and dispatches to SFAs. Not yet built.
2. **SFA training pipeline** — Each SFA uses corpus endpoints to train on discipline literature before evaluating candidates. Architecture designed, not implemented.
3. **Reconcile build_subject_schema.py** — Currently detached from harvest; either wire it to consume harvest or supersede with harvest-driven proposals.

### Known Issues

- **2 unrouted entities** in classifier: Q346629 (Roman Republic "different from" duplicate), Q6173448 (Wikipedia vital articles)
- **22 SubjectConcepts** in graph have null `concept_qid` — written by LLM process, not yet wired to Wikidata QIDs
- **18/22 LCSH IDs** from LLM were wrong (see `output/subject_schema/lcsh_validation.txt`) — only 4 verified correct
- **FAST endpoint** shows `no_fast` — discipline QIDs don't have FAST IDs; needs backbone FAST IDs from candidates instead
- **Facet nodes** in graph have null properties (no `facet_id`, no `anchor_qids`) — data lives in `facet_registry_master.json` instead

### Architectural Decisions

- **SFAs train before evaluating** — First order of business is discipline → corpus → training, not candidate evaluation
- **Cipher address space** — QID + PID + value_QID = deterministic key. Harvest creates the full addressing scheme; classifier partitions by facet; each SFA gets O(1) access to its vertices.
- **Forward + backward = complete universe** — Re-running periodically detects diffs (new QIDs, new federation anchors)
- **Never pass PID or QID without its label** — Foundational rule for all DI output

---

## Memory Files

Auto-memory persists across sessions at `C:\Users\defar\.claude\projects\c--Projects-Graph1\memory\`:

| File | Content |
|------|---------|
| `MEMORY.md` | Master index (~216 lines, truncated at 200) |
| `domain_initiator.md` | DI pipeline architecture, stats, scripts |
| `sca_architecture.md` | SCA design notes |

---

## Neo4j Connection

```python
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
```

Reads from `.env` → Aura cloud. All scripts use MERGE (idempotent).

## Foundational Rule

**Decision tables ARE the spec.** Agents read SYS_DecisionTable rows from the graph. There is no separate implementation. Code = I/O shell; reasoning = LLM; data = graph.
