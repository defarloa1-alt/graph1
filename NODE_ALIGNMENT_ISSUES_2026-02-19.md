# Node Alignment Issues - Architecture vs Neo4j

**Date:** 2026-02-19  
**Issue:** Neo4j contains 65 labels, many non-canonical  
**Impact:** Confuses agents, breaks queries, inconsistent with architecture

---

## 🔴 **Major Issues Found**

### **1. Duplicate Facet Labels (18 extras!)**

**Found in Neo4j:**
```
ArchaeologicalFacet (1 node)
ArtisticFacet (1 node)
BiographicFacet (1 node)
CommunicationFacet (1 node)
CulturalFacet (1 node)
DemographicFacet (1 node)
DiplomaticFacet (1 node)
EconomicFacet (1 node)
EnvironmentalFacet (1 node)
GeographicFacet (1 node)
IntellectualFacet (1 node)
LinguisticFacet (1 node)
MilitaryFacet (1 node)
PoliticalFacet (1 node)
ReligiousFacet (1 node)
ScientificFacet (1 node)
SocialFacet (1 node)
TechnologicalFacet (1 node)
```

**Problem:** These are individual class labels (18 separate labels)

**Should be:** One `Facet` label with `key` property
```cypher
(:Facet {key: 'ARCHAEOLOGICAL'})  // NOT :ArchaeologicalFacet
```

**Action:** Delete these 18 nodes, use canonical Facet nodes we just created

---

### **2. Federation Structure Duplicates**

**Found:**
```
Federation (10 nodes)
AuthoritySystem (9 nodes)
Category (2 nodes)
Chrystallum (1 node)
Facets (1 node)
Root (1 node)
CanonicalFacet (18 nodes)
```

**Problem:** These look like earlier federation experiments

**Should be:**
```
FederationRoot (1 node)
FederationType (3 nodes)
AuthoritySource (6 nodes)
Facet (18 nodes)
Policy (5 nodes)
Threshold (3 nodes)
```

**Action:** Cleanup old federation nodes, keep only canonical metadata we just created

---

### **3. CIDOC-CRM Label (E4_Period)**

**Found:**
```
E4_Period (1,077 nodes)
```

**Problem:** These are the same nodes as `:Period` (double-labeled)

**Should be:** Just `:Period` label

**Verification:**
```cypher
MATCH (p:Period:E4_Period)
RETURN count(p)
// If 1,077 → they're the same nodes with both labels
```

**Action:** Remove E4_Period label from Period nodes (or keep if needed for CIDOC-CRM compliance)

---

### **4. Deprecated Nodes (Good - All 0)**

**Found (correctly empty):**
```
Position (0 nodes)  ✓ Correctly deprecated
Activity (0 nodes)  ✓ Correctly deprecated
RetrievalContext (0 nodes)  ✓ Not using
```

**These are correct - deprecated and removed**

---

### **5. Empty Canonical Nodes (Expected)**

**Found (empty, waiting for data):**
```
Human (0 nodes)  ← Waiting for entity loading
Event (0 nodes)  ← Waiting for entity loading
Organization (0 nodes)  ← Waiting for entity loading
Claim (0 nodes)  ← Waiting for claims
Work (0 nodes)  ← Waiting for source loading
Dynasty, Gens, Praenomen, Cognomen (0 nodes)  ← Roman-specific
Material, Object, ConditionState (0 nodes)  ← Archaeological
```

**These are fine - empty but ready for data**

---

## ✅ **Canonical Architecture (What SHOULD Exist)**

### **First-Class Entity Nodes:**
```
SubjectConcept, Human, Event, Place, Period,
Organization, Dynasty, Institution, Claim, Work,
Year, Gens, Praenomen, Cognomen, LegalRestriction,
Material, Object, ConditionState
```

### **Federation Metadata Nodes:**
```
FederationRoot, FederationType, AuthoritySource,
Policy, Threshold, Facet
```

### **Supporting Nodes:**
```
PlaceType, PlaceTypeTokenMap, GeoSemanticType,
PeriodCandidate, GeoCoverageCandidate,
Decade, Century, Millennium (if hierarchy loaded)
```

**Total canonical labels:** ~35

**Current in Neo4j:** 65 labels (30 extra!)

---

## 🔧 **Cleanup Required**

### **Delete These Non-Canonical Nodes:**

```cypher
// 1. Delete individual facet class nodes
MATCH (n)
WHERE n:ArchaeologicalFacet OR n:ArtisticFacet OR n:BiographicFacet
   OR n:CommunicationFacet OR n:CulturalFacet OR n:DemographicFacet
   OR n:DiplomaticFacet OR n:EconomicFacet OR n:EnvironmentalFacet
   OR n:GeographicFacet OR n:IntellectualFacet OR n:LinguisticFacet
   OR n:MilitaryFacet OR n:PoliticalFacet OR n:ReligiousFacet
   OR n:ScientificFacet OR n:SocialFacet OR n:TechnologicalFacet
DETACH DELETE n

// 2. Delete old federation structure
MATCH (n)
WHERE n:AuthoritySystem OR n:Category OR n:Chrystallum 
   OR n:Facets OR n:Root OR n:CanonicalFacet
DETACH DELETE n

// 3. Optionally: Remove E4_Period label (keep Period)
MATCH (p:E4_Period)
REMOVE p:E4_Period
```

### **Keep These (Canonical):**
```
FederationRoot, FederationType, AuthoritySource, Policy, Threshold, Facet
Year, Period, PeriodCandidate, GeoCoverageCandidate
Place, PlaceType, PlaceTypeTokenMap, GeoSemanticType
SubjectConcept
(All with 0 nodes are fine - waiting for data)
```

---

## 📊 **After Cleanup, Should Have:**

**~35 canonical labels:**
- 18 first-class entity types
- 6 federation metadata types
- 11 supporting types

**Instead of 65**

---

## 🎯 **Recommendation**

**Run cleanup Cypher to:**
1. Delete 18 individual FacetClass nodes
2. Delete old Federation structure nodes  
3. Remove E4_Period label (optional)
4. Verify only canonical nodes remain

**Want me to generate the cleanup script?**

