# SCA Bootstrap - Comprehensive Specification

**Date:** 2026-02-19  
**Critical:** SCA is STATELESS - Graph is the only persistent memory  
**Requirement:** Bootstrap must be COMPREHENSIVE

---

## 🎯 **Core Principle: Stateless SCA**

**SCA has NO memory between sessions:**
- ❌ Doesn't remember previous discoveries
- ❌ Doesn't remember what was approved
- ❌ Doesn't remember configuration
- ✅ **Graph is the ONLY source of truth**

**Implication:**
- **Bootstrap query must return EVERYTHING**
- No assumptions about prior sessions
- Complete operational context from graph
- All rules, policies, thresholds discoverable

---

## 📊 **Bootstrap Query (Single Query for Complete Context)**

```cypher
// ===================================================================
// SCA BOOTSTRAP QUERY - Returns Complete Operational Context
// ===================================================================

// 1. Federation Configuration
MATCH (fed:FederationRoot)
MATCH (fed)-[:HAS_FEDERATION]->(type:FederationType)
MATCH (type)-[:USES_SOURCE]->(source:AuthoritySource)

// 2. Scoring Models and Tiers
MATCH (type)-[:HAS_SCORING_MODEL]->(model:ScoringModel)
MATCH (model)-[:HAS_TIER]->(tier:ScoreTier)

// 3. Active Policies (Governance Rules)
MATCH (fed)-[:HAS_POLICY]->(policy:Policy)
WHERE policy.status = 'active'

// 4. Thresholds (Split Triggers, Monitoring)
MATCH (fed)-[:HAS_THRESHOLD]->(threshold:Threshold)

// 5. Canonical Facets (18 facets - NO temporal, NO classification)
MATCH (fed)-[:HAS_FACET_REGISTRY]->(facet:Facet)

// 6. Pending Approvals (What Needs Review)
OPTIONAL MATCH (pending_item)
WHERE pending_item.status = 'pending_approval'

// 7. Current Session Context (If Resuming - though SCA starts fresh)
OPTIONAL MATCH (session:Session)
WHERE session.status = 'active'

// 8. Existing Ontology (What's Already Built)
OPTIONAL MATCH (ontology:SubjectConcept)

RETURN 
  fed,
  collect(DISTINCT type) AS federation_types,
  collect(DISTINCT source) AS authority_sources,
  collect(DISTINCT model) AS scoring_models,
  collect(DISTINCT tier) AS score_tiers,
  collect(DISTINCT policy) AS active_policies,
  collect(DISTINCT threshold) AS thresholds,
  collect(DISTINCT facet) AS canonical_facets,
  collect(DISTINCT pending_item) AS pending_approvals,
  session,
  count(ontology) AS existing_concepts
```

**This ONE query gives SCA everything it needs to start!**

---

## 🏗️ **Required Graph Nodes for Bootstrap**

### **1. FederationRoot (Singleton)**
```cypher
(:FederationRoot {
  name: 'Chrystallum Federation',
  version: '1.0',
  created: datetime(),
  last_updated: datetime()
})
```

### **2. FederationType (3 types)**
```cypher
(:FederationType {
  name: 'Place',
  scope: 'geographic',
  node_label: 'Place',
  count: 41993
})

(:FederationType {
  name: 'Period',
  scope: 'temporal',
  node_label: 'Period',
  count: 1077
})

(:FederationType {
  name: 'SubjectConcept',
  scope: 'semantic',
  node_label: 'SubjectConcept',
  count: 87
})
```

### **3. AuthoritySource (6 sources)**
```cypher
// Local authorities
(:AuthoritySource {
  name: 'Pleiades',
  mode: 'local',
  file_path: 'Geographic/pleiades_places.csv',
  type: 'geographic',
  coverage: 41993
})

(:AuthoritySource {
  name: 'PeriodO',
  mode: 'local',
  file_path: 'Temporal/periodo-dataset.csv',
  type: 'temporal',
  coverage: 8959
})

(:AuthoritySource {
  name: 'LCSH',
  mode: 'local',
  file_path: 'LCSH/skos_subjects/',
  type: 'conceptual'
})

(:AuthoritySource {
  name: 'FAST',
  mode: 'local',
  file_path: 'Python/fast/key/FASTTopical_parsed.csv',
  type: 'topical'
})

(:AuthoritySource {
  name: 'LCC',
  mode: 'local',
  file_path: 'Subjects/lcc_flat.csv',
  type: 'classification'
})

// Hub (not local)
(:AuthoritySource {
  name: 'Wikidata',
  mode: 'hub_api',
  api_endpoint: 'https://query.wikidata.org/sparql',
  type: 'federation_hub',
  role: 'Global knowledge graph - discovery and disambiguation only'
})
```

### **4. ScoringModel and ScoreTier**
```cypher
(:ScoringModel {
  name: 'PlaceFederationScoring',
  version: '1.0',
  formula: 'pleiades(20) + qid(50) + temporal(20) + coords(10)'
})
  -[:HAS_TIER]->
(:ScoreTier {
  score_min: 80,
  score_max: 100,
  label: 'FS3_WELL_FEDERATED',
  description: 'Vertex jump enabled'
})
// ... other tiers
```

### **5. Policy (Governance Rules)**
```cypher
(:Policy {
  name: 'LocalFirstCanonicalAuthorities',
  description: 'Always check local authorities before hub API',
  status: 'active',
  priority: 1
})

(:Policy {
  name: 'HubForDisambiguationOnly',
  description: 'Use Wikidata for discovery/disambiguation, not as primary source',
  status: 'active',
  priority: 2
})

(:Policy {
  name: 'NoTemporalFacet',
  description: 'Temporal is NOT a facet - use Year backbone, Period, Event entities',
  status: 'active',
  priority: 3
})

(:Policy {
  name: 'NoClassificationFacet',
  description: 'Classification via LCC properties, not facet',
  status: 'active',
  priority: 4
})

(:Policy {
  name: 'ApprovalRequired',
  description: 'All discoveries require human approval before promotion',
  status: 'active',
  priority: 5
})
```

### **6. Threshold (Split Triggers)**
```cypher
(:Threshold {
  name: 'crosslink_ratio_split',
  value: 0.30,
  description: 'Split SFA when cross-links exceed 30% of total edges'
})

(:Threshold {
  name: 'level2_child_overload',
  value: 12,
  description: 'Split when L2 node has >12 children'
})

(:Threshold {
  name: 'facet_drift_alert',
  value: 0.20,
  description: 'Alert when 20%+ concepts have LCSH mismatched to facet'
})
```

### **7. Facet Registry (18 Canonical)**
```cypher
(:Facet {key: 'ARCHAEOLOGICAL', label: 'Archaeological'})
(:Facet {key: 'ARTISTIC', label: 'Artistic'})
(:Facet {key: 'BIOGRAPHIC', label: 'Biographic'})  ← Use this, not "genealogical"
(:Facet {key: 'COMMUNICATION', label: 'Communication'})
(:Facet {key: 'CULTURAL', label: 'Cultural'})
(:Facet {key: 'DEMOGRAPHIC', label: 'Demographic'})
(:Facet {key: 'DIPLOMATIC', label: 'Diplomatic'})
(:Facet {key: 'ECONOMIC', label: 'Economic'})
(:Facet {key: 'ENVIRONMENTAL', label: 'Environmental'})
(:Facet {key: 'GEOGRAPHIC', label: 'Geographic'})
(:Facet {key: 'INTELLECTUAL', label: 'Intellectual'})
(:Facet {key: 'LINGUISTIC', label: 'Linguistic'})
(:Facet {key: 'MILITARY', label: 'Military'})
(:Facet {key: 'POLITICAL', label: 'Political'})
(:Facet {key: 'RELIGIOUS', label: 'Religious'})
(:Facet {key: 'SCIENTIFIC', label: 'Scientific'})
(:Facet {key: 'SOCIAL', label: 'Social'})
(:Facet {key: 'TECHNOLOGICAL', label: 'Technological'})

// Total: 18 facets
// NOT included: temporal, classification, patronage, genealogical
```

---

## 📋 **Approval Workflow States**

**Lifecycle:** `discovered → pending_approval → approved → loaded`

### **State: discovered**
- SCA creates shell node or proposal
- Marked as `status='discovered'`
- Not yet reviewed

### **State: pending_approval**
- Item needs human review
- Query: `MATCH (item {status='pending_approval'}) RETURN item`
- User reviews and approves/rejects

### **State: approved**
- Human approved
- Ready to be promoted/loaded
- Can be loaded to canonical graph

### **State: loaded**
- Fully integrated into canonical graph
- No longer in approval queue
- Production data

**Example:**
```cypher
// SCA discovers new concept
CREATE (c:SubjectConcept {
  subject_id: 'subj_new_concept',
  label: 'New Concept',
  status: 'discovered',  ← Initial state
  discovered_by: 'sca_session_20260219',
  discovered_at: datetime()
})

// User marks for review
SET c.status = 'pending_approval'

// User approves
SET c.status = 'approved'

// System loads to production
SET c.status = 'loaded'
```

---

## 🔄 **Session Model**

### **SCA Starts Fresh Each Time**
- No memory of previous session
- Reads complete context from graph
- Can be edited/guided during session
- All discoveries written to graph with states

### **Bootstrap Sequence:**

**1. SCA Initializes**
```
Load bootstrap query (get complete context)
```

**2. SCA Discovers Context**
```
Federation types: Place, Period, SubjectConcept
Authority sources: Pleiades (local), PeriodO (local), LCSH (local), FAST (local), LCC (local), Wikidata (hub)
Scoring models: Place (4 components), Period (3 components), SubjectConcept (4 components)
Active policies: LocalFirst, HubForDisambiguation, NoTemporal, NoClassification, ApprovalRequired
Canonical facets: 18 facets (list)
Pending approvals: [items awaiting review]
Existing ontology: 87 SubjectConcept nodes for Roman Republic
```

**3. SCA Operates**
```
Create discoveries → status='discovered'
Mark for review → status='pending_approval'
Write all to graph
```

**4. User Reviews**
```
Query pending: MATCH (item {status='pending_approval'})
Approve: SET status='approved'
Reject: DELETE or SET status='rejected'
```

**5. System Loads**
```
Approved items → status='loaded'
Integrated into production
```

---

## 🚫 **Critical Constraints (Enforce These)**

### **1. No Temporal Facet**
```
Rule: TEMPORAL is NOT a facet
Enforcement: Reject any facet assignment with "temporal" or "TEMPORAL"
Temporal semantics ONLY via: Year backbone, Period entities, Event entities
No SFA_TEMPORAL
```

### **2. No Classification Facet**
```
Rule: CLASSIFICATION is NOT a facet
Enforcement: Reject any facet assignment with "classification" or "CLASSIFICATION"
Classification via: LCC properties, entity types, SKOS hierarchies
```

### **3. No Patronage Facet**
```
Rule: PATRONAGE is NOT a facet
Merge into: SOCIAL or POLITICAL
```

### **4. Genealogical → Biographic**
```
Rule: Use "BIOGRAPHIC" not "genealogical"
BIOGRAPHIC is canonical
genealogical is non-canonical alias
```

### **5. Facets Must Be UPPERCASE**
```
Rule: All facet keys MUST be UPPERCASE
Correct: "POLITICAL", "MILITARY", "SOCIAL"
Wrong: "political", "military", "social"
```

---

## 📐 **Period Validation Heuristic**

**Task:** Determine what makes a valid Period

**Approach:** Analyze PeriodO + Wikidata backlinks

### **Valid Period Criteria:**

**Must Have:**
1. ✅ Temporal extent (start_year, end_year)
2. ✅ Interval semantics (not point-in-time)
3. ✅ Used as grouping category (not single event)
4. ✅ Can tether to Year backbone

**Should Have:**
5. ✅ Period type (political, cultural, geological, etc.)
6. ✅ Wikidata QID (if widely recognized)
7. ✅ Hierarchical placement (broader/narrower periods)
8. ✅ Spatial coverage (where applicable)

**Fuzziness Support:**
- earliest_start_year, latest_start_year
- earliest_end_year, latest_end_year

### **Period vs Event Decision:**

**Period:**
- Extended duration (decades+)
- Grouping category
- Hierarchical structure
- **Default when ambiguous**

**EventAggregate:**
- Composite of subevents
- Can link to Period
- Dual modeling allowed

**Example: World War II**
```cypher
(:Period {qid: 'Q362', start_year: 1939, end_year: 1945})
  -[:DENOTES]->
(:EventAggregate {qid: 'Q362'})
  -[:HAS_SUBEVENT]->
(:Event {label: 'D-Day', date: '1944-06-06'})
```

---

## 🔍 **Wikidata Backlink Harvesting**

**Method for Period Discovery:**

```
Step 1: Start with seed QIDs
  - Q11756 (prehistory)
  - Q12554 (Middle Ages)
  - Q17167 (Roman Republic)
  - etc.

Step 2: Query Wikidata backlinks
  SPARQL: Find all items that link TO seed QID
  Result: 500+ candidate periods

Step 3: Classify each candidate
  - Period (has interval, widely used)
  - Event (point-in-time, specific occurrence)
  - Polity (state, dynasty, empire)
  - Movement (cultural, technological)
  - Noise (modern orgs, disambiguation pages)

Step 4: Propose mapping to Periodo
  - Match by label, temporal overlap
  - Infer period_type from Wikidata P31
  - Propose new Period nodes
  - Status: 'pending_approval'
```

---

## ✅ **What SCA Must Do Each Session**

### **On Session Start:**

1. **Execute Bootstrap Query**
   - Get complete federation config
   - Load canonical 18 facets
   - Load active policies
   - Load thresholds
   - Check pending approvals

2. **Verify Configuration**
   - 18 facets loaded (not 16, not 20)
   - No temporal facet
   - No classification facet
   - All facets UPPERCASE

3. **Load Operational Context**
   - What federations exist
   - What authorities to use (local first!)
   - What scoring rules apply
   - What requires approval

4. **Check Pending Queue**
   - Query: `MATCH (item {status='pending_approval'})`
   - Present to user for review
   - Process approvals/rejections

### **During Session:**

5. **Create Discoveries**
   - Shell nodes → `status='discovered'`
   - Ontology proposals → `status='proposed'`
   - Authority mappings → `status='discovered'`

6. **Mark for Approval**
   - Move to `status='pending_approval'`
   - Write reasoning/provenance
   - Queue for user review

7. **Process Approvals**
   - User approves → `status='approved'`
   - User rejects → `status='rejected'` or DELETE
   - Approved items → Can be promoted to `status='loaded'`

### **On Session End:**

8. **Persist All State**
   - All discoveries written to graph
   - All approval states recorded
   - All provenance captured
   - Ready for next session bootstrap

---

## 📊 **Approval Workflow**

### **What Requires Approval:**

**Everything with `status='pending_approval'`:**
- New shell nodes
- Ontology proposals
- Authority mappings
- Period type inferences
- Cross-links
- Period classifications (Period vs Event)

### **Approval Query:**
```cypher
MATCH (item {status: 'pending_approval'})
RETURN 
  item,
  labels(item) AS type,
  item.label AS label,
  item.discovered_by AS source,
  item.discovered_at AS when,
  item.reasoning AS why
ORDER BY item.discovered_at
```

### **Approval Actions:**
```cypher
// Approve
MATCH (item {status: 'pending_approval'})
WHERE item.subject_id = $id
SET item.status = 'approved',
    item.approved_by = $user,
    item.approved_at = datetime()

// Reject
MATCH (item {status: 'pending_approval'})
WHERE item.subject_id = $id
SET item.status = 'rejected',
    item.rejected_reason = $reason
// Or DELETE if not worth keeping

// Bulk approve
MATCH (item {status: 'pending_approval'})
WHERE item.discovered_by = 'sca_session_20260219'
SET item.status = 'approved'
```

---

## 🎯 **SCA Operating Constraints**

### **Mode Discipline**
- **Default:** Query Mode
- **Proposal Mode:** Only when message starts with `Propose ingestion ...`
- **No mixing:** Each session is one mode

### **Facet Constraints**
- **18 canonical facets** (from graph)
- **NO temporal** (rejected)
- **NO classification** (rejected)
- **NO patronage** (merge into SOCIAL)
- **Use BIOGRAPHIC** (not genealogical)
- **All facets UPPERCASE**

### **Authority Constraints**
- **Local first:** Check Pleiades, PeriodO, LCSH, FAST, LCC before API
- **Hub for discovery:** Wikidata for backlinks, hierarchy, disambiguation
- **Write-back:** Cache API results to local files
- **Don't mirror:** Don't copy LCSH/LCC hierarchies into ontology

### **Approval Constraints**
- **Everything needs approval:** status='pending_approval'
- **User reviews:** Query pending approvals
- **No auto-promotion:** Approved items must be explicitly loaded

---

## 📝 **Year Backbone Contract**

**Fixed Range:**
- Year nodes: -2000 to 2025 (fixed, not auto-extending)
- Decade nodes: Rollup of years
- Century nodes: Rollup of decades

**Tethering Rule:**
```
ANY entity with temporal aspect MUST tether to Year backbone
```

**Relationships:**
- `STARTS_IN_YEAR → Year`
- `ENDS_IN_YEAR → Year`

**Fuzziness:**
- `earliest_start_year` (fuzzy lower bound)
- `latest_start_year` (fuzzy upper bound)
- `earliest_end_year` (fuzzy lower bound)
- `latest_end_year` (fuzzy upper bound)

---

## 🚀 **Next Task for SCA**

**Command:**
```
Propose ingestion: Periodo→Wikidata period mapping via backlinks harvesting
```

**What SCA will do:**
1. Load PeriodO dataset (8,959 periods)
2. Query Wikidata backlinks from seed QIDs
3. Classify: Period vs Event vs Polity vs Noise
4. Infer period_type for each (political, geological, etc.)
5. Propose mappings to Wikidata QIDs
6. Create Period nodes with `status='pending_approval'`
7. User reviews and approves

**Output:**
- JSON proposal
- Markdown reasoning report
- Deduplication log
- All with `status='pending_approval'`

---

## ✅ **Bootstrap is Now Comprehensive**

**SCA can:**
- Start fresh each session
- Bootstrap from graph completely
- No external memory needed
- All state in graph
- All discoveries tracked
- All approvals queryable

**Graph provides:**
- Federation configuration
- Authority sources
- Scoring models
- Policies and rules
- Thresholds
- Canonical facets
- Pending approvals
- Current ontology state

---

**Ready to update your SCA agent with this comprehensive bootstrap specification!**

**Saved to:** `md/Agents/SCA/SCA_BOOTSTRAP_COMPREHENSIVE_2026-02-19.md`

