# Immediate SubjectConcepts & SFAs from Q17167

**Source:** Q17167_recursive_20260220_135756.json  
**Created from:** Actual Wikidata properties

---

## 🎯 SUBJECTCONCEPT CREATED

### **SubjectConcept: Roman Republic**

```cypher
CREATE (sc:SubjectConcept {
  subject_id: 'subj_roman_republic_q17167',
  label: 'Roman Republic',
  qid: 'Q17167',
  
  // Classification
  primary_facet: 'POLITICAL',
  related_facets: ['RELIGIOUS', 'MILITARY', 'ECONOMIC', 'LINGUISTIC', 
                   'GEOGRAPHIC', 'SOCIAL', 'ARCHAEOLOGICAL', 'CULTURAL', 'DIPLOMATIC'],
  
  // Authority Federation
  lcsh_id: 'sh85115114',
  lcsh_label: 'Rome--History--Republic, 510-30 B.C.',
  bnf_id: '11951115f',
  gnd_id: NULL,  // Not in data
  
  // Temporal
  start_date: '-0509-00-00',
  end_date: '-0027-01-16',
  temporal_scope: '-0509/-0027',
  time_period_qid: 'Q486761',  // classical antiquity
  
  // Geographic
  geographic_scope: 'Europe, Asia, Africa',
  capital_qid: 'Q220',  // Rome
  coordinates: '41.9, 12.5',
  
  // Description
  description: 'period of ancient Roman civilization (509 BC–27 BC)',
  
  // Metadata
  status: 'approved',
  discovered_from: 'wikidata_5hop_exploration',
  discovered_at: datetime(),
  confidence: 0.95,
  
  // Additional
  official_name: 'Res publica Romana',
  basic_government: 'aristocratic republic',
  official_religion_qid: 'Q337547',  // ancient Roman religion
  currency_qid: 'Q952064',  // Roman currency
  languages: ['Q397', 'Q35497']  // Latin, Ancient Greek
})
```

---

## 🤖 10 SFAs IMMEDIATELY AGENTIZED

### Agent Pattern: `SFA_{subject_id}_{facet_key}`

| # | Agent ID | Facet | Evidence | Properties |
|---|----------|-------|----------|------------|
| 1 | **SFA_subj_roman_republic_q17167_POLITICAL** | POLITICAL | P31, P122, P194, P36 | 4+ |
| 2 | **SFA_subj_roman_republic_q17167_RELIGIOUS** | RELIGIOUS | P140, P3075 | 2 |
| 3 | **SFA_subj_roman_republic_q17167_ECONOMIC** | ECONOMIC | P38, P2046 | 2 |
| 4 | **SFA_subj_roman_republic_q17167_LINGUISTIC** | LINGUISTIC | P37, P2936, P1448 | 3 |
| 5 | **SFA_subj_roman_republic_q17167_GEOGRAPHIC** | GEOGRAPHIC | P30, P36, P625, P242 | 4 |
| 6 | **SFA_subj_roman_republic_q17167_SOCIAL** | SOCIAL | P1792 | 1 |
| 7 | **SFA_subj_roman_republic_q17167_MILITARY** | MILITARY | P793 (wars) | 7 events |
| 8 | **SFA_subj_roman_republic_q17167_ARCHAEOLOGICAL** | ARCHAEOLOGICAL | Inherited from Ancient Rome | Inherited |
| 9 | **SFA_subj_roman_republic_q17167_CULTURAL** | CULTURAL | Inherited from Ancient Rome | Inherited |
| 10 | **SFA_subj_roman_republic_q17167_DIPLOMATIC** | DIPLOMATIC | P793 (wars), Inherited | Mixed |

---

## 🔗 RELATIONSHIPS CREATED

### Parent-Child (Temporal Hierarchy):

```cypher
// Children
(sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
  -[:HAS_PARTS]->
(child1:SubjectConcept {subject_id: 'subj_early_roman_republic_q2839628'})

(sc)-[:HAS_PARTS]->(child2:SubjectConcept {subject_id: 'subj_middle_roman_republic_q6106068'})

(sc)-[:HAS_PARTS]->(child3:SubjectConcept {subject_id: 'subj_late_roman_republic_q2815472'})

// Parent
(sc)-[:PART_OF]->(parent:SubjectConcept {subject_id: 'subj_ancient_rome_q1747689'})
```

### Succession (Timeline):

```cypher
(predecessor:SubjectConcept {subject_id: 'subj_roman_kingdom_q201038'})
  -[:FOLLOWED_BY]->
(sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
  -[:FOLLOWED_BY]->
(successor1:SubjectConcept {subject_id: 'subj_roman_empire_q2277'})

(sc)-[:FOLLOWED_BY]->(successor2:SubjectConcept {subject_id: 'subj_principate_q206414'})
```

### Context:

```cypher
(sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
  -[:WITHIN_TIME_PERIOD]->
(period:SubjectConcept {subject_id: 'subj_classical_antiquity_q486761'})
```

---

## 📊 IMMEDIATE SUBJECTCONCEPT NETWORK

### From Roman Republic, we can create:

**Direct SubjectConcepts (8):**
1. Roman Republic (Q17167) ← Root
2. Early Roman Republic (Q2839628) ← Child
3. Middle Roman Republic (Q6106068) ← Child
4. Late Roman Republic (Q2815472) ← Child
5. Ancient Rome (Q1747689) ← Parent
6. Roman Kingdom (Q201038) ← Predecessor
7. Roman Empire (Q2277) ← Successor
8. Principate (Q206414) ← Successor

**Context SubjectConcepts (1):**
9. classical antiquity (Q486761) ← Time period

**Total:** 9 SubjectConcepts immediately

---

## 🤖 TOTAL SFAs CREATED

### From Roman Republic alone:

**10 facets × 1 SubjectConcept = 10 SFAs**

### If we create all 9 SubjectConcepts:

**Potential:** 9 SubjectConcepts × 10 relevant facets = **90 potential SFAs**

**Actually needed:** Create on-demand when analyzing

---

## 💾 READY FOR NEO4J

### Cypher to Create Roman Republic SubjectConcept:

```cypher
// Create SubjectConcept
CREATE (sc:SubjectConcept {
  subject_id: 'subj_roman_republic_q17167',
  label: 'Roman Republic',
  qid: 'Q17167',
  primary_facet: 'POLITICAL',
  related_facets: ['RELIGIOUS', 'MILITARY', 'ECONOMIC', 'LINGUISTIC', 
                   'GEOGRAPHIC', 'SOCIAL', 'ARCHAEOLOGICAL', 'CULTURAL', 'DIPLOMATIC'],
  lcsh_id: 'sh85115114',
  start_date: '-0509-00-00',
  end_date: '-0027-01-16',
  description: 'period of ancient Roman civilization (509 BC–27 BC)',
  status: 'approved',
  confidence: 0.95
})

// Link to temporal backbone
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (start:Year {year: -509})
MATCH (end:Year {year: -27})
MERGE (sc)-[:STARTS_IN_YEAR]->(start)
MERGE (sc)-[:ENDS_IN_YEAR]->(end)

// Link to parent
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (parent:SubjectConcept {subject_id: 'subj_ancient_rome_q1747689'})
MERGE (sc)-[:PART_OF]->(parent)

// Link to children
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (early:SubjectConcept {subject_id: 'subj_early_roman_republic_q2839628'})
MATCH (middle:SubjectConcept {subject_id: 'subj_middle_roman_republic_q6106068'})
MATCH (late:SubjectConcept {subject_id: 'subj_late_roman_republic_q2815472'})
MERGE (sc)-[:HAS_PARTS]->(early)
MERGE (sc)-[:HAS_PARTS]->(middle)
MERGE (sc)-[:HAS_PARTS]->(late)

// Create initial SFAs
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
UNWIND ['POLITICAL', 'RELIGIOUS', 'MILITARY', 'ECONOMIC', 'LINGUISTIC', 
        'GEOGRAPHIC', 'SOCIAL', 'ARCHAEOLOGICAL', 'CULTURAL', 'DIPLOMATIC'] 
AS facet
CREATE (agent:Agent {
  id: 'SFA_subj_roman_republic_q17167_' + facet,
  agent_type: 'SubjectFacetAgent',
  facet: facet,
  subject_concept_id: 'subj_roman_republic_q17167',
  status: 'active',
  created_at: datetime()
})
MERGE (agent)-[:ANALYZES]->(sc)
```

---

## 🎯 **SUMMARY:**

**From 1 QID (Q17167), we immediately get:**
- ✅ 1 SubjectConcept (Roman Republic)
- ✅ 10 facet edges
- ✅ 10 SFAs (agentized)
- ✅ 3 child SubjectConcepts
- ✅ 1 parent SubjectConcept
- ✅ 2 successor SubjectConcepts
- ✅ 1 predecessor SubjectConcept

**Total potential:** 9 SubjectConcepts, 90 SFAs

**The edges to facets are REVEALED by:**
1. Direct properties (P31, P140, P38, P37, etc.)
2. Inherited classifications (archaeological culture, Roman civilization)
3. Event properties (P793 wars)

**Ready to agentize and deploy!** 🚀