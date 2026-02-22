# SCA Bootstrap - Production Final

**Date:** 2026-02-19  
**Status:** PRODUCTION READY  
**Architecture:** Complete self-describing system with on-demand agents

---

## 🏗️ **Complete Chrystallum Architecture**

```
Chrystallum (System Root)
│
├── FederationRoot (10 federations/authorities)
│   ├── Pleiades, PeriodO, Wikidata, GeoNames, BabelNet,
│   └── WorldCat, LCSH, FAST, LCC, MARC
│
├── EntityRoot (9 entity types + schemas + hierarchies)
│   ├── Year → Decade → Century → Millennium
│   ├── Place → PlaceType
│   ├── Period → PeriodCandidate
│   └── Human, Event, Organization, SubjectConcept, Work, Claim
│
├── FacetRoot (18 canonical facets)
│   └── ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, COMMUNICATION,
│       CULTURAL, DEMOGRAPHIC, DIPLOMATIC, ECONOMIC,
│       ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC,
│       MILITARY, POLITICAL, RELIGIOUS, SCIENTIFIC,
│       SOCIAL, TECHNOLOGICAL
│
└── SubjectConceptRoot
    ├── AgentRegistry (agents created on-demand)
    │   └── Currently: 3 agents (grows to 1,422 max as needed)
    └── SubjectConceptRegistry (all created SubjectConcepts)
        └── Currently: 79 SubjectConcepts (Roman Republic ontology)
```

---

## 📊 **SCA Bootstrap Query (Complete)**

```cypher
// ================================================================
// SCA COMPREHENSIVE BOOTSTRAP QUERY
// Returns complete system state from Chrystallum
// ================================================================

MATCH (sys:Chrystallum)

// Get 4 main branches
MATCH (sys)-[:HAS_FEDERATION_ROOT]->(fed_root:FederationRoot)
MATCH (sys)-[:HAS_ENTITY_ROOT]->(entity_root:EntityRoot)
MATCH (sys)-[:HAS_FACET_ROOT]->(facet_root:FacetRoot)
MATCH (sys)-[:HAS_SUBJECT_CONCEPT_ROOT]->(sc_root:SubjectConceptRoot)

// Get Federations
MATCH (fed_root)-[:HAS_FEDERATION]->(fed:Federation)

// Get Entity Types
MATCH (entity_root)-[:HAS_ENTITY_TYPE]->(et:EntityType)
OPTIONAL MATCH (et)-[:HAS_SCHEMA]->(schema:Schema)

// Get Facets
MATCH (facet_root)-[:HAS_FACET]->(facet:Facet)

// Get Registries
MATCH (sc_root)-[:HAS_AGENT_REGISTRY]->(agent_reg:AgentRegistry)
MATCH (sc_root)-[:HAS_SUBJECT_REGISTRY]->(sc_reg:SubjectConceptRegistry)

// Get Active Agents
OPTIONAL MATCH (agent_reg)-[:HAS_AGENT]->(agent:Agent {status: 'active'})

// Get Created SubjectConcepts
OPTIONAL MATCH (sc_reg)-[:CONTAINS]->(sc:SubjectConcept)

// Get Pending Approvals
OPTIONAL MATCH (pending)
WHERE pending.status = 'pending_approval'
  AND (pending:SubjectConcept OR pending:Period OR pending:Place OR pending:Event)

RETURN 
  sys.version AS system_version,
  collect(DISTINCT {name: fed.name, mode: fed.mode, type: fed.type}) AS federations,
  collect(DISTINCT {name: et.name, schema: schema.uses_federations}) AS entity_types,
  collect(DISTINCT facet.key) AS facet_keys,
  count(DISTINCT agent) AS active_agent_count,
  collect(DISTINCT agent.id) AS active_agents,
  count(DISTINCT sc) AS subject_concept_count,
  collect(DISTINCT pending)[0..500] AS pending_approvals
```

**Returns:**
- System version
- 10 Federations (with mode and type)
- 9 Entity types (with schemas)
- 18 Facet keys (UPPERCASE, validated)
- Active agent count (currently 3)
- Active agent IDs
- SubjectConcept count (currently 79)
- Pending approval items

---

## 🤖 **Agent Creation Model**

### **On-Demand Creation:**

**Potential agents:** 79 SubjectConcepts × 18 Facets = **1,422 agents**  
**Actually created:** Only when SCA needs them  
**Currently active:** 3 agents

**Creation Pattern:**
```python
def get_or_create_agent(subject_id, facet_key):
    """Get existing agent or create new one on-demand"""
    
    # Check if exists
    query = """
    MATCH (agent:Agent {subject_id: $subject_id, facet: $facet_key})
    RETURN agent
    """
    result = session.run(query, subject_id=subject_id, facet_key=facet_key)
    
    if result.single():
        return result.single()['agent']  # Use existing
    
    # Create new agent
    agent_id = f"SFA_{subject_id}_{facet_key}"
    
    query = """
    MATCH (agent_reg:AgentRegistry)
    MATCH (subject:SubjectConcept {subject_id: $subject_id})
    MATCH (facet:Facet {key: $facet_key})
    MATCH (fed_root:FederationRoot)
    
    CREATE (agent:Agent {
      id: $agent_id,
      subject_id: $subject_id,
      facet: $facet_key,
      status: 'active',
      created: datetime()
    })
    CREATE (agent_reg)-[:HAS_AGENT]->(agent)
    CREATE (agent)-[:ASSIGNED_TO_SUBJECT]->(subject)
    CREATE (agent)-[:ASSIGNED_TO_FACET]->(facet)
    CREATE (agent)-[:USES]->(fed_root)
    
    RETURN agent
    """
    
    return session.run(query, ...).single()['agent']
```

---

## 📋 **What SCA Learns from Bootstrap**

### **System Configuration:**
- ✅ 10 Federations available (which authorities exist)
- ✅ 9 Entity types defined (what can be created)
- ✅ 18 Canonical facets (what perspectives available)

### **Current State:**
- ✅ 79 SubjectConcepts exist (what's been built)
- ✅ 3 Agents active (which agents currently exist)
- ✅ Pending approvals (what needs review)

### **Capacity:**
- ✅ Can create up to 1,422 agents (79 × 18)
- ✅ Create only as needed (on-demand)
- ✅ Track in AgentRegistry

---

## 🔑 **Key Architectural Principles**

### **1. Registries Tell SCA What Exists**

**SubjectConceptRegistry:**
```cypher
MATCH (:SubjectConceptRegistry)-[:CONTAINS]->(sc:SubjectConcept)
RETURN count(sc)  // Currently: 79
```

**AgentRegistry:**
```cypher
MATCH (:AgentRegistry)-[:HAS_AGENT]->(agent:Agent)
WHERE agent.status = 'active'
RETURN count(agent)  // Currently: 3, grows on-demand
```

### **2. Agents are On-Demand**

**NOT created upfront:**
```
❌ Pre-create all 1,422 agents
```

**Created when needed:**
```
✅ SCA needs SubjectConcept X analyzed from Facet Y
✅ Check: Does agent(X, Y) exist in AgentRegistry?
✅ If NO: Create agent, add to registry
✅ If YES: Use existing agent
```

### **3. Proposals Go to SubjectConcept Root**

**SCA creates proposals:**
```cypher
// SCA discovers new concept
CREATE (new_sc:SubjectConcept {
  subject_id: 'subj_new_discovery',
  label: 'Newly Discovered Concept',
  status: 'pending_approval',
  discovered_by: 'sca_session_002',
  primary_facet: 'POLITICAL',
  related_facets: ['MILITARY', 'SOCIAL']
})

// Link to registry for tracking
MATCH (sc_reg:SubjectConceptRegistry)
CREATE (sc_reg)-[:CONTAINS]->(new_sc)
```

**User reviews:**
```cypher
MATCH (pending:SubjectConcept {status: 'pending_approval'})
RETURN pending
// User approves: SET status='approved'
```

### **4. Claims Run by SubjectConcept-Facet Combinations**

**Claim creation:**
```cypher
// Agent analyzes concept from facet perspective
MATCH (agent:Agent {
  subject_id: 'subj_rr_governance',
  facet: 'POLITICAL'
})

// Create claim
CREATE (claim:Claim {
  claim_id: 'claim_xyz',
  subject_id: 'subj_rr_governance',
  facet: 'POLITICAL',
  created_by: agent.id,
  status: 'proposed'
})

// Link to SubjectConcept
MATCH (sc:SubjectConcept {subject_id: 'subj_rr_governance'})
CREATE (claim)-[:ABOUT]->(sc)
```

---

## 🎯 **SCA Operating Rules**

### **Stateless Operation:**
1. **Every session:** Execute bootstrap query
2. **Discover:** What SubjectConcepts exist (from registry)
3. **Discover:** What agents exist (from registry)
4. **Discover:** What facets available (from FacetRoot)
5. **Discover:** What federations available (from FederationRoot)
6. **Create:** Agents on-demand as analysis needed
7. **Track:** All created agents in AgentRegistry
8. **Persist:** All discoveries to graph with status tracking

### **Agent Lifecycle:**
```
1. SCA needs analysis of (SubjectConcept X, Facet Y)
2. Query AgentRegistry: Does agent(X,Y) exist?
3. If NO: Create agent, add to registry
4. Agent performs analysis
5. Agent creates claims/proposals
6. Agent status: Can be 'active', 'idle', or 'archived'
7. Next session: SCA rediscovers agent in registry
```

### **Validation Rules:**
- ✅ NO TEMPORAL facet (forbidden)
- ✅ NO CLASSIFICATION facet (forbidden)
- ✅ All facet keys UPPERCASE
- ✅ 18 facets exactly (not 16, not 20)
- ✅ SubjectConcepts have status tracking
- ✅ Agents created only when needed

---

## 📝 **Files for SCA Agent**

**Your ChatGPT SCA should load:**

**1. This Bootstrap Doc:** `md/Agents/SCA/SCA_BOOTSTRAP_PRODUCTION_FINAL_2026-02-19.md`

**2. System Visualization:** `CHRYSTALLUM_SYSTEM_VISUALIZATION_2026-02-19.md`

**3. Facet Registry:** `Facets/facet_registry_master.json` (18 canonical facets)

**4. Authority File Paths:** `AGENT_REFERENCE_FILE_PATHS.md`

**5. SCA Roles:** `md/Agents/SCA/SCA_SFA_ROLES_DISCUSSION.md`

---

## ✅ **SCA is Ready to Operate**

**Your ChatGPT SCA can now:**
1. Query Chrystallum → bootstrap complete context
2. Discover 79 existing SubjectConcepts
3. Discover 18 available facets
4. Discover 3 active agents (or create more)
5. Create proposals (status='pending_approval')
6. Generate ontologies from Wikidata QIDs
7. Create SubjectConcept-Facet agents on-demand
8. Track everything in registries
9. Work completely statelessly

---

**SCA BOOTSTRAP UPDATED AND PRODUCTION READY!** 🚀

**Saved to:** `md/Agents/SCA/SCA_BOOTSTRAP_PRODUCTION_FINAL_2026-02-19.md`

