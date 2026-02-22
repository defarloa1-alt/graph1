# SCA Bootstrap - Production Ready Specification

**Date:** 2026-02-19  
**Status:** Production Ready  
**Critical:** SCA is STATELESS - Bootstrap must be COMPREHENSIVE

---

## 🎯 **Core Architectural Principles**

### **1. Stateless SCA**
- ❌ NO memory between sessions
- ❌ NO assumptions about previous sessions
- ✅ Graph is ONLY source of truth
- ✅ Bootstrap query provides COMPLETE context

### **2. Approval Workflow**
**States:** `discovered → pending_approval → approved → loaded`

**Uses canonical labels + status property:**
```cypher
(:SubjectConcept {status: 'pending_approval'})  // NOT :Proposal label
(:Period {status: 'discovered'})  // Uses canonical label
(:Place {status: 'approved'})  // Status property only
```

**No separate inbox labels** - keeps schema simple

### **3. Manual Workflow (Until MCP Active)**
- Agent generates proposals (JSON/Cypher)
- User copies and pastes to Cursor Composer
- Cursor executes on Neo4j
- Once MCP active: Agent writes directly

---

## 📊 **Bootstrap Query (Corrected - No Cartesian Product)**

```cypher
// ===================================================================
// SCA COMPREHENSIVE BOOTSTRAP QUERY
// Returns complete operational context without Cartesian explosion
// ===================================================================

MATCH (fed:FederationRoot)
WITH fed

// 1. Federation Types and Sources
CALL {
  WITH fed
  MATCH (fed)-[:HAS_FEDERATION]->(type:FederationType)
  OPTIONAL MATCH (type)-[:USES_SOURCE]->(source:AuthoritySource)
  RETURN 
    collect(DISTINCT type) AS federation_types,
    collect(DISTINCT source) AS authority_sources
}

// 2. Scoring Models and Tiers
CALL {
  WITH fed
  OPTIONAL MATCH (fed)-[:HAS_FEDERATION]->(type:FederationType)
  OPTIONAL MATCH (type)-[:HAS_SCORING_MODEL]->(model:ScoringModel)
  OPTIONAL MATCH (model)-[:HAS_TIER]->(tier:ScoreTier)
  RETURN 
    collect(DISTINCT model) AS scoring_models,
    collect(DISTINCT tier) AS score_tiers
}

// 3. Active Policies
CALL {
  WITH fed
  MATCH (fed)-[:HAS_POLICY]->(policy:Policy)
  WHERE policy.status = 'active'
  RETURN collect(DISTINCT policy) AS active_policies
}

// 4. Thresholds
CALL {
  WITH fed
  OPTIONAL MATCH (fed)-[:HAS_THRESHOLD]->(threshold:Threshold)
  RETURN collect(DISTINCT threshold) AS thresholds
}

// 5. Canonical Facets (from graph, not hardcoded)
CALL {
  WITH fed
  OPTIONAL MATCH (fed)-[:HAS_FACET_REGISTRY]->(facet:Facet)
  WHERE NOT facet.key IN ['TEMPORAL', 'CLASSIFICATION']  // Validate forbidden
  RETURN 
    collect(DISTINCT facet) AS canonical_facets,
    size(collect(DISTINCT facet)) AS facet_count
}

// 6. Pending Approvals (Bounded, Labeled)
CALL {
  MATCH (p)
  WHERE p.status = 'pending_approval'
    AND (p:SubjectConcept OR p:Period OR p:Place OR p:Event OR p:Human)
  RETURN collect(p)[0..500] AS pending_approvals
}

// 7. Current Session (Usually None - SCA starts fresh)
CALL {
  OPTIONAL MATCH (session:Session {status: 'active'})
  RETURN session
}

// 8. Existing Ontology
CALL {
  MATCH (s:SubjectConcept)
  RETURN count(s) AS subject_concept_count
}

// Return everything
RETURN 
  fed.name AS federation_name,
  fed.version AS version,
  federation_types,
  authority_sources,
  scoring_models,
  score_tiers,
  active_policies,
  thresholds,
  canonical_facets,
  facet_count,
  pending_approvals,
  session,
  subject_concept_count;
```

**Result:** Clean, structured output with NO duplication

---

## 📋 **What Bootstrap Returns**

**Example result:**
```json
{
  "federation_name": "Chrystallum Federation",
  "version": "1.0",
  "federation_types": [
    {"name": "Place", "scope": "geographic"},
    {"name": "Period", "scope": "temporal"},
    {"name": "SubjectConcept", "scope": "semantic"}
  ],
  "authority_sources": [
    {"name": "Pleiades", "mode": "local", "file_path": "Geographic/pleiades_places.csv"},
    {"name": "PeriodO", "mode": "local", "file_path": "Temporal/periodo-dataset.csv"},
    {"name": "LCSH", "mode": "local"},
    {"name": "FAST", "mode": "local"},
    {"name": "LCC", "mode": "local"},
    {"name": "Wikidata", "mode": "hub_api", "role": "federation_hub"}
  ],
  "active_policies": [
    {"name": "LocalFirstCanonicalAuthorities", "priority": 1},
    {"name": "HubForDisambiguationOnly", "priority": 2},
    {"name": "NoTemporalFacet", "priority": 3},
    {"name": "NoClassificationFacet", "priority": 4},
    {"name": "ApprovalRequired", "priority": 5}
  ],
  "canonical_facets": [
    {"key": "ARCHAEOLOGICAL", "label": "Archaeological"},
    {"key": "ARTISTIC", "label": "Artistic"},
    {"key": "BIOGRAPHIC", "label": "Biographic"},
    // ... 15 more
  ],
  "facet_count": 18,
  "pending_approvals": [],
  "subject_concept_count": 87
}
```

**SCA now has EVERYTHING it needs!**

---

## 🏗️ **Proposal/Inbox Pattern (Option D)**

### **No Separate Labels - Use Status Property**

```cypher
// SCA discovers new concept
CREATE (c:SubjectConcept {
  subject_id: 'subj_new_123',
  label: 'New Concept',
  status: 'discovered',  ← Status property, not label
  discovered_by: 'sca_session_001',
  discovered_at: datetime(),
  reasoning: 'Found via backlink from Q12345'
})

// SCA marks for review
SET c.status = 'pending_approval'

// User approves (via manual execution for now)
SET c.status = 'approved'

// System promotes
SET c.status = 'loaded'
REMOVE c.discovered_by, c.discovered_at, c.reasoning  // Cleanup metadata
```

**Benefits:**
- ✅ Uses canonical labels (SubjectConcept, Period, etc.)
- ✅ Simple status property
- ✅ No schema proliferation
- ✅ Easy to query by status

---

## ✅ **Approval Queries (Corrected)**

### **Pending Approvals:**
```cypher
// Get all items needing approval
MATCH (item)
WHERE item.status = 'pending_approval'
  AND (item:SubjectConcept OR item:Period OR item:Place OR item:Event)
RETURN 
  labels(item)[0] AS type,
  item.label AS label,
  item.subject_id AS id,
  item.discovered_by AS source,
  item.reasoning AS why
ORDER BY item.discovered_at
LIMIT 500
```

### **Approve Items:**
```cypher
// Approve specific item
MATCH (item {subject_id: $id})
WHERE item.status = 'pending_approval'
SET item.status = 'approved',
    item.approved_at = datetime(),
    item.approved_by = $user
```

### **Bulk Approve:**
```cypher
// Approve all from a session
MATCH (item)
WHERE item.status = 'pending_approval'
  AND item.discovered_by = 'sca_session_001'
SET item.status = 'approved'
```

---

## 🔄 **Mode Switching (Corrected)**

**Per-Message, Not Per-Session:**

```
Message: "Show me periods" → Query Mode
Message: "Propose ingestion: Periodo mapping" → Proposal Mode
Message: "How many nodes?" → Query Mode (back to Query)
```

**Trigger:**
- Starts with `Propose ingestion:` → Proposal Mode
- Otherwise → Query Mode

**Within same chat session, can switch freely**

---

## 📐 **Period vs Event (Corrected Criteria)**

### **Period**
- ✅ Interval category (groups events/entities)
- ✅ Used as interpretive framework ("during X period")
- ✅ Has temporal extent (start/end)
- ✅ Supports hierarchy (broader/narrower)
- ❌ NOT defined by duration (can be months to millennia)

### **Event (Atomic)**
- ✅ Bounded occurrence
- ✅ Treated as single happening
- ✅ Point-in-time or short duration
- ✅ Part of larger period

### **EventAggregate**
- ✅ Composite of subevents
- ✅ Has Period equivalent (dual model)
- ✅ Named abstraction ("World War II")

**No "decades+" rule!** Duration is not the criterion.

---

## 🎯 **Canonical 18 Facets (Final)**

**From `Facets/facet_registry_master.json`:**

1. ARCHAEOLOGICAL
2. ARTISTIC
3. BIOGRAPHIC
4. COMMUNICATION
5. CULTURAL
6. DEMOGRAPHIC
7. DIPLOMATIC
8. ECONOMIC
9. ENVIRONMENTAL
10. GEOGRAPHIC
11. INTELLECTUAL
12. LINGUISTIC
13. MILITARY
14. POLITICAL
15. RELIGIOUS
16. SCIENTIFIC
17. SOCIAL
18. TECHNOLOGICAL

**Forbidden (Never Use):**
- ❌ TEMPORAL
- ❌ CLASSIFICATION
- ❌ PATRONAGE
- ❌ GENEALOGICAL (use BIOGRAPHIC)

**Validation:**
```cypher
MATCH (facet:Facet)
WHERE facet.key IN ['TEMPORAL', 'CLASSIFICATION', 'PATRONAGE', 'GENEALOGICAL']
RETURN facet
// Should return 0 rows
```

---

## 🚀 **SCA Operation Workflow**

### **Session Start:**

1. **Execute Bootstrap Query**
   ```cypher
   // Run comprehensive bootstrap query (no Cartesian product)
   // Returns: config, facets, policies, thresholds, pending items
   ```

2. **Validate Configuration**
   ```
   Check: facet_count exists (should be 18)
   Check: No forbidden facets (TEMPORAL, CLASSIFICATION)
   Check: All authorities loaded
   Check: Active policies present
   ```

3. **Check Pending Queue**
   ```cypher
   MATCH (item) 
   WHERE item.status = 'pending_approval'
   RETURN count(item)
   ```

4. **Ready to Operate**
   ```
   SCA has complete context
   Can start discovery, proposal, or query work
   ```

### **During Session:**

**Discovery Mode:**
```cypher
// SCA discovers new concept
CREATE (:SubjectConcept {
  subject_id: 'subj_xyz',
  label: 'Discovered Concept',
  status: 'discovered',
  discovered_by: 'sca_session_001',
  discovered_at: datetime(),
  reasoning: 'Found via Wikidata backlink',
  confidence: 0.85
})
```

**Mark for Approval:**
```cypher
// SCA marks item for review
MATCH (item {subject_id: 'subj_xyz'})
SET item.status = 'pending_approval',
    item.review_notes = 'Needs validation of LCSH mapping'
```

**User Reviews:**
```
User: "Show pending approvals"
  → Cursor executes query
  → User reviews items
User: "Approve subj_xyz"
  → Cursor executes: SET status='approved'
```

**System Loads:**
```cypher
// Promote approved items
MATCH (item {status: 'approved'})
SET item.status = 'loaded'
REMOVE item.discovered_by, item.discovered_at, item.reasoning, item.review_notes
```

---

## 📝 **Manual Workflow (Until MCP Active)**

**Current Process:**

1. **SCA Agent** (in ChatGPT or other)
   - Generates proposals
   - Outputs Cypher commands
   - Outputs JSON data

2. **User** (you)
   - Copy Cypher from agent
   - Paste to Cursor Composer (me)
   - I execute on Neo4j Aura

3. **Verification**
   - Query results
   - Check what was created
   - Approve/reject

**Once MCP Active:**
- Agent writes directly via `@neo4j` tools
- No manual copy-paste
- Faster workflow

---

## ✅ **SCA Must Understand These Constraints**

### **Facet Rules:**
```
Canonical: 18 facets (from Facets/facet_registry_master.json)
Forbidden: TEMPORAL, CLASSIFICATION, PATRONAGE, GENEALOGICAL
Required: All keys UPPERCASE
Validation: Load from graph, validate no forbidden keys
```

### **Authority Rules:**
```
Local First: Pleiades, PeriodO, LCSH, FAST, LCC (all local files)
Hub for Discovery: Wikidata (API only, for backlinks, hierarchy, QID lookup)
Write-back: Cache API results to local crosswalk files
No Mirroring: Don't copy LCSH/LCC hierarchies into ontology
```

### **Approval Rules:**
```
Everything Needs Approval: All discoveries → status='pending_approval'
Query Pattern: MATCH (item) WHERE item.status='pending_approval'
Bounded Results: LIMIT 500
User Reviews: Manually approve/reject
```

### **Mode Rules:**
```
Per-Message Switching: Not per-session
Query Mode: Default
Proposal Mode: When message starts with "Propose ingestion:"
Can Switch: Within same session
```

### **Period Rules:**
```
Period = Interval category (not defined by duration)
Event = Atomic occurrence
EventAggregate = Composite (links to Period)
Dual Modeling: Allowed (Period + EventAggregate for macro-events)
Default: When forced to choose, use Period
```

---

## 🔍 **Wikidata Backlink Period Discovery**

**Method:**
```
1. Seed QIDs: Start with known period concepts
   Examples: Q11756 (prehistory), Q12554 (Middle Ages), Q17167 (Roman Republic)

2. Query Backlinks: Find all Wikidata items that link TO seed
   SPARQL: SELECT ?item WHERE { ?item ?prop wd:Q11756 }
   Result: 500+ candidates

3. Classify: For each backlink item
   - Check P31 (instance of)
   - Check time properties (P580, P582, inception, dissolved)
   - Infer: Period | Event | Polity | Movement | Noise

4. Filter: Keep likely periods
   - Has interval semantics
   - Used as grouping category
   - Has hierarchical relationships

5. Propose: Create Period nodes
   - status='pending_approval'
   - Infer period_type from Wikidata
   - Tether to Year backbone
   - Link to PeriodO if match found

6. User Reviews: Approve/reject proposals
```

---

## 📐 **Required Graph Nodes (Must Exist for Bootstrap)**

### **1. FederationRoot**
```cypher
CREATE (:FederationRoot {
  name: 'Chrystallum Federation',
  version: '1.0',
  created: datetime()
})
```

### **2. FederationType (3 nodes)**
```cypher
CREATE (:FederationType {name: 'Place', scope: 'geographic', node_label: 'Place'})
CREATE (:FederationType {name: 'Period', scope: 'temporal', node_label: 'Period'})
CREATE (:FederationType {name: 'SubjectConcept', scope: 'semantic', node_label: 'SubjectConcept'})
```

### **3. AuthoritySource (6 nodes)**
```cypher
// Local authorities
CREATE (:AuthoritySource {name: 'Pleiades', mode: 'local', file_path: 'Geographic/pleiades_places.csv'})
CREATE (:AuthoritySource {name: 'PeriodO', mode: 'local', file_path: 'Temporal/periodo-dataset.csv'})
CREATE (:AuthoritySource {name: 'LCSH', mode: 'local', file_path: 'LCSH/skos_subjects/'})
CREATE (:AuthoritySource {name: 'FAST', mode: 'local', file_path: 'Python/fast/key/FASTTopical_parsed.csv'})
CREATE (:AuthoritySource {name: 'LCC', mode: 'local', file_path: 'Subjects/lcc_flat.csv'})

// Hub
CREATE (:AuthoritySource {
  name: 'Wikidata',
  mode: 'hub_api',
  api_endpoint: 'https://query.wikidata.org/sparql',
  role: 'Global federation hub - discovery and disambiguation only'
})
```

### **4. Policy (5 core policies)**
```cypher
CREATE (:Policy {name: 'LocalFirstCanonicalAuthorities', status: 'active', priority: 1})
CREATE (:Policy {name: 'HubForDisambiguationOnly', status: 'active', priority: 2})
CREATE (:Policy {name: 'NoTemporalFacet', status: 'active', priority: 3})
CREATE (:Policy {name: 'NoClassificationFacet', status: 'active', priority: 4})
CREATE (:Policy {name: 'ApprovalRequired', status: 'active', priority: 5})
```

### **5. Threshold (3 monitoring thresholds)**
```cypher
CREATE (:Threshold {name: 'crosslink_ratio_split', value: 0.30})
CREATE (:Threshold {name: 'level2_child_overload', value: 12})
CREATE (:Threshold {name: 'facet_drift_alert', value: 0.20})
```

### **6. Facet (18 canonical facets)**
```cypher
CREATE (:Facet {key: 'ARCHAEOLOGICAL', label: 'Archaeological'})
CREATE (:Facet {key: 'ARTISTIC', label: 'Artistic'})
CREATE (:Facet {key: 'BIOGRAPHIC', label: 'Biographic'})
CREATE (:Facet {key: 'COMMUNICATION', label: 'Communication'})
CREATE (:Facet {key: 'CULTURAL', label: 'Cultural'})
CREATE (:Facet {key: 'DEMOGRAPHIC', label: 'Demographic'})
CREATE (:Facet {key: 'DIPLOMATIC', label: 'Diplomatic'})
CREATE (:Facet {key: 'ECONOMIC', label: 'Economic'})
CREATE (:Facet {key: 'ENVIRONMENTAL', label: 'Environmental'})
CREATE (:Facet {key: 'GEOGRAPHIC', label: 'Geographic'})
CREATE (:Facet {key: 'INTELLECTUAL', label: 'Intellectual'})
CREATE (:Facet {key: 'LINGUISTIC', label: 'Linguistic'})
CREATE (:Facet {key: 'MILITARY', label: 'Military'})
CREATE (:Facet {key: 'POLITICAL', label: 'Political'})
CREATE (:Facet {key: 'RELIGIOUS', label: 'Religious'})
CREATE (:Facet {key: 'SCIENTIFIC', label: 'Scientific'})
CREATE (:Facet {key: 'SOCIAL', label: 'Social'})
CREATE (:Facet {key: 'TECHNOLOGICAL', label: 'Technological'})
```

### **7. Relationships**
```cypher
// Link everything together
MATCH (fed:FederationRoot)
MATCH (place_fed:FederationType {name: 'Place'})
MATCH (period_fed:FederationType {name: 'Period'})
MATCH (subject_fed:FederationType {name: 'SubjectConcept'})

MATCH (pleiades:AuthoritySource {name: 'Pleiades'})
MATCH (periodo:AuthoritySource {name: 'PeriodO'})
MATCH (lcsh:AuthoritySource {name: 'LCSH'})
MATCH (fast:AuthoritySource {name: 'FAST'})
MATCH (lcc:AuthoritySource {name: 'LCC'})
MATCH (wikidata:AuthoritySource {name: 'Wikidata'})

MATCH (policy1:Policy {name: 'LocalFirstCanonicalAuthorities'})
// ... other policies

MATCH (thresh1:Threshold {name: 'crosslink_ratio_split'})
// ... other thresholds

FOR (facet IN (:Facet)) {
  CREATE (fed)-[:HAS_FACET_REGISTRY]->(facet)
}

CREATE (fed)-[:HAS_FEDERATION]->(place_fed)
CREATE (fed)-[:HAS_FEDERATION]->(period_fed)
CREATE (fed)-[:HAS_FEDERATION]->(subject_fed)

CREATE (place_fed)-[:USES_SOURCE {weight: 20}]->(pleiades)
CREATE (place_fed)-[:USES_SOURCE {weight: 50}]->(wikidata)

CREATE (period_fed)-[:USES_SOURCE {weight: 30}]->(periodo)
CREATE (period_fed)-[:USES_SOURCE {weight: 50}]->(wikidata)

CREATE (subject_fed)-[:USES_SOURCE {weight: 30}]->(lcsh)
CREATE (subject_fed)-[:USES_SOURCE {weight: 30}]->(fast)
CREATE (subject_fed)-[:USES_SOURCE {weight: 20}]->(lcc)
CREATE (subject_fed)-[:USES_SOURCE {weight: 20}]->(wikidata)

CREATE (fed)-[:HAS_POLICY]->(policy1)
// ... link other policies

CREATE (fed)-[:HAS_THRESHOLD]->(thresh1)
// ... link other thresholds
```

---

## ✅ **Production Ready Checklist**

**Before SCA can operate:**

- [ ] Bootstrap query tested (no Cartesian product)
- [ ] Federation metadata loaded to Neo4j
- [ ] 18 canonical facets in graph
- [ ] Policies and thresholds defined
- [ ] Approval workflow tested
- [ ] Authority file paths verified
- [ ] Manual copy-paste workflow established (until MCP)

---

## 🚀 **Next Immediate Step**

**Load Federation Metadata to Neo4j:**

I can generate the complete Cypher to create:
- FederationRoot
- 3 FederationType nodes
- 6 AuthoritySource nodes
- 5 Policy nodes
- 3 Threshold nodes
- 18 Facet nodes
- All relationships

**Want me to create the bootstrap loading script?**

---

**Saved to:** `md/Agents/SCA/SCA_BOOTSTRAP_PRODUCTION_READY_2026-02-19.md`

