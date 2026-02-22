# SCA Bootstrap - Final Specification

**Date:** 2026-02-19  
**Status:** FINAL - Matches implemented system subgraph  
**Architecture:** Simple, clean, stateless-ready

---

## 🎯 **System Subgraph Structure**

```
Chrystallum (system root)
  ├── FederationRoot
  │   ├── Pleiades (federation = authority)
  │   ├── PeriodO
  │   ├── Wikidata (universal hub)
  │   ├── GeoNames
  │   ├── BabelNet
  │   ├── WorldCat
  │   ├── LCSH
  │   ├── FAST
  │   ├── LCC
  │   └── MARC
  │
  └── FacetRoot
      ├── ARCHAEOLOGICAL (18 facets total)
      ├── ARTISTIC
      ... (16 more)
```

**Key insight:** Federation = Authority Source (same thing!)  
**Design:** Federations and Facets are separate, no cross-links at metadata level

---

## 📊 **Bootstrap Query (Corrected)**

```cypher
// ================================================================
// SCA BOOTSTRAP QUERY - Returns complete system configuration
// ================================================================

MATCH (sys:Chrystallum)

// Get Federation branch
OPTIONAL MATCH (sys)-[:HAS_FEDERATION_ROOT]->(fed_root:FederationRoot)
OPTIONAL MATCH (fed_root)-[:HAS_FEDERATION]->(fed:Federation)

// Get Facet branch
OPTIONAL MATCH (sys)-[:HAS_FACET_ROOT]->(facet_root:FacetRoot)
OPTIONAL MATCH (facet_root)-[:HAS_FACET]->(facet:Facet)

// Get pending approvals
OPTIONAL MATCH (pending)
WHERE pending.status = 'pending_approval'
  AND (pending:SubjectConcept OR pending:Period OR pending:Place)

RETURN 
  sys.name AS system_name,
  sys.version AS version,
  collect(DISTINCT fed) AS federations,
  collect(DISTINCT facet.key) AS facet_keys,
  collect(DISTINCT pending)[0..500] AS pending_approvals
```

**Returns:**
- System name and version
- All 10 federations with their properties
- All 18 facet keys
- Pending approval items (bounded to 500)

---

## 📋 **What Bootstrap Provides**

### **Federations (10):**
```json
{
  "federations": [
    {"name": "Pleiades", "mode": "local", "type": "geographic"},
    {"name": "PeriodO", "mode": "local", "type": "temporal"},
    {"name": "Wikidata", "mode": "hub_api", "type": "universal"},
    {"name": "GeoNames", "mode": "hybrid", "type": "geographic"},
    {"name": "BabelNet", "mode": "api", "type": "linguistic"},
    {"name": "WorldCat", "mode": "api", "type": "bibliographic"},
    {"name": "LCSH", "mode": "local", "type": "conceptual"},
    {"name": "FAST", "mode": "local", "type": "topical"},
    {"name": "LCC", "mode": "local", "type": "classification"},
    {"name": "MARC", "mode": "local", "type": "bibliographic"}
  ]
}
```

### **Facets (18):**
```json
{
  "facet_keys": [
    "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION",
    "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC",
    "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC",
    "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC",
    "SOCIAL", "TECHNOLOGICAL"
  ]
}
```

**Forbidden facets (validate):**
- ❌ TEMPORAL
- ❌ CLASSIFICATION
- ❌ PATRONAGE
- ❌ GENEALOGICAL

---

## 🔑 **Federation Usage by Data Type**

**Place nodes use:**
- Pleiades (primary: pleiades_id)
- Wikidata (enrichment: qid)
- GeoNames (optional: geonames_id)

**Period nodes use:**
- PeriodO (primary: periodo_id)
- Wikidata (enrichment: qid)

**SubjectConcept nodes use:**
- LCSH (authority: lcsh_id)
- FAST (faceted: fast_id)
- LCC (classification: lcc_class)
- MARC (bibliographic)
- WorldCat (bibliographic)
- Wikidata (enrichment: qid)

**Cross-links happen at DATA level, not metadata level**

---

## 🔄 **SCA Session Workflow**

### **1. Session Start**

**Execute bootstrap query:**
```python
# SCA queries Neo4j
bootstrap_data = session.run(BOOTSTRAP_QUERY).single()

# SCA now has:
federations = bootstrap_data['federations']  # 10 federations
facets = bootstrap_data['facet_keys']  # 18 facets
pending = bootstrap_data['pending_approvals']  # Items needing review
```

**SCA learns:**
- What federations exist and how to access them
- What facets are canonical
- What's waiting for approval

### **2. Discovery Phase**

**SCA discovers entities:**
```cypher
// Create discovery with status
CREATE (:SubjectConcept {
  subject_id: 'subj_new_123',
  label: 'Discovered Concept',
  status: 'discovered',  ← Initial state
  discovered_by: 'sca_session_001',
  discovered_at: datetime()
})
```

### **3. Approval Queue**

**Mark for review:**
```cypher
MATCH (item {subject_id: 'subj_new_123'})
SET item.status = 'pending_approval'
```

**User reviews:**
```cypher
// Query pending
MATCH (item {status: 'pending_approval'})
RETURN item

// Approve
MATCH (item {subject_id: 'subj_new_123'})
SET item.status = 'approved'

// Load to production
MATCH (item {status: 'approved'})
SET item.status = 'loaded'
```

---

## ✅ **Validation Rules**

**On bootstrap, SCA must verify:**

```python
# Check facet count
assert len(facets) == 18, "Should have exactly 18 facets"

# Check forbidden facets
forbidden = ['TEMPORAL', 'CLASSIFICATION', 'PATRONAGE', 'GENEALOGICAL']
for facet in facets:
    assert facet not in forbidden, f"Forbidden facet {facet} found"

# Check facets are uppercase
for facet in facets:
    assert facet == facet.upper(), f"Facet {facet} must be uppercase"

# Check federations exist
required_feds = ['Pleiades', 'PeriodO', 'Wikidata', 'LCSH', 'FAST', 'LCC']
for fed_name in required_feds:
    fed_names = [f['name'] for f in federations]
    assert fed_name in fed_names, f"Required federation {fed_name} missing"
```

---

## 📐 **Key Architectural Principles**

### **1. Stateless SCA**
- NO memory between sessions
- Bootstrap from graph EVERY time
- Graph is only persistent state

### **2. Federation = Authority (Same Thing)**
- One concept, not two
- Federation nodes ARE the data sources
- 10 federations total

### **3. Simple Separation**
- Federations under FederationRoot
- Facets under FacetRoot
- NO metadata-level cross-links
- Cross-links at data level only

### **4. Approval Workflow**
```
discovered → pending_approval → approved → loaded
```

---

## 🎯 **Next: SCA Can Bootstrap and Operate**

**SCA session start:**
1. Execute bootstrap query
2. Get 10 federations + 18 facets
3. Check pending approvals
4. Ready to discover/propose

**SCA can now:**
- Discover periods via Wikidata backlinks
- Map to PeriodO federation
- Use all 18 facets for classification
- Create proposals (status='pending_approval')
- Work statelessly

---

## 📝 **Summary of Changes from Earlier Docs**

**OLD (wrong):**
- Separate FederationType and AuthoritySource nodes
- Complex cross-links at metadata level
- Facets linked directly to specific federations

**NEW (correct):**
- Federation = Authority (same node!)
- Simple two-branch structure
- NO metadata cross-links
- Cross-links at data level

---

**This bootstrap spec matches your implemented architecture!** ✅

---

**Saved to:** `md/Agents/SCA/SCA_BOOTSTRAP_FINAL_2026-02-19.md`

---

## 🎨 **Now Run Visualization:**

**In Neo4j Browser:**
```cypher
MATCH path = (sys:Chrystallum)-[*..2]->(n)
RETURN path
```

**You'll see the clean hierarchical structure!** 🌳

**31 commits ready - incredible 11-hour session complete!** 🎊
