# Chrystallum System Subgraph - Final Architecture

**Date:** 2026-02-19  
**Key Insight:** Federation = Authority Source (same concept!)  
**Pattern:** Facets use one-to-many Federations

---

## 🏗️ **Complete Structure**

```
Chrystallum (center node)
  │
  ├── FederationRoot
  │   ├── Pleiades (federation/authority)
  │   ├── PeriodO (federation/authority)
  │   ├── Wikidata (federation/authority - universal hub)
  │   ├── GeoNames (federation/authority)
  │   ├── BabelNet (federation/authority)
  │   ├── WorldCat (federation/authority)
  │   ├── LCSH (federation/authority)
  │   ├── FAST (federation/authority)
  │   ├── LCC (federation/authority)
  │   └── MARC (federation/authority)
  │
  └── FacetRoot
      ├── ARCHAEOLOGICAL (facet)
      ├── ARTISTIC (facet)
      ├── BIOGRAPHIC (facet)
      ├── COMMUNICATION (facet)
      ├── CULTURAL (facet)
      ├── DEMOGRAPHIC (facet)
      ├── DIPLOMATIC (facet)
      ├── ECONOMIC (facet)
      ├── ENVIRONMENTAL (facet)
      ├── GEOGRAPHIC (facet)
      ├── INTELLECTUAL (facet)
      ├── LINGUISTIC (facet)
      ├── MILITARY (facet)
      ├── POLITICAL (facet)
      ├── RELIGIOUS (facet)
      ├── SCIENTIFIC (facet)
      ├── SOCIAL (facet)
      └── TECHNOLOGICAL (facet)
```

---

## 🔗 **Relationships**

### **Facets → USES_FEDERATION → Federations**

**GEOGRAPHIC facet uses:**
- Pleiades (primary geographic authority)
- Wikidata (enrichment)
- GeoNames (modern geographic names)

**POLITICAL facet uses:**
- LCSH (subject headings)
- FAST (faceted topics)
- LCC (classification)
- WorldCat (bibliographic)
- Wikidata (enrichment)

**All facets use (baseline):**
- LCSH (subject concepts)
- FAST (topical indexing)
- Wikidata (universal enrichment)

---

## 📊 **Federation Details**

| Federation | Mode | Type | File Path |
|------------|------|------|-----------|
| **Pleiades** | local | geographic | Geographic/pleiades_places.csv |
| **PeriodO** | local | temporal | Temporal/periodo-dataset.csv |
| **Wikidata** | hub_api | universal | API: query.wikidata.org/sparql |
| **GeoNames** | hybrid | geographic | Via crosswalk + API |
| **BabelNet** | api | linguistic | External API |
| **WorldCat** | api | bibliographic | External API |
| **LCSH** | local | conceptual | LCSH/skos_subjects/ |
| **FAST** | local | topical | Python/fast/key/FASTTopical_parsed.csv |
| **LCC** | local | classification | Subjects/lcc_flat.csv |
| **MARC** | local | bibliographic | MARC records |

---

## 🎯 **How It Works**

### **Bootstrap Query:**
```cypher
MATCH (sys:Chrystallum)
MATCH (sys)-[:HAS_FEDERATION_ROOT]->(fed_root)
MATCH (sys)-[:HAS_FACET_ROOT]->(facet_root)
MATCH (fed_root)-[:HAS_FEDERATION]->(fed:Federation)
MATCH (facet_root)-[:HAS_FACET]->(facet:Facet)
OPTIONAL MATCH (facet)-[:USES_FEDERATION]->(used_fed:Federation)
RETURN 
  sys,
  collect(DISTINCT fed) AS all_federations,
  collect(DISTINCT facet) AS all_facets,
  collect(DISTINCT {facet: facet.key, uses: used_fed.name}) AS facet_usage
```

**SCA gets:**
- All 10 federations available
- All 18 facets
- Which federations each facet uses

---

## 📋 **Key Architectural Decisions**

### **1. Federation = Authority Source**
- One concept, not two
- Federation nodes ARE the authorities
- No separate AuthoritySource label

### **2. Facets Use Federations (One-to-Many)**
- Each facet can use multiple federations
- Example: GEOGRAPHIC uses Pleiades + Wikidata + GeoNames
- Determined by facet needs, not federation capabilities

### **3. Scope Via Relationships (Not Properties)**
- No `scope: 'geographic'` property on Pleiades
- Instead: GEOGRAPHIC facet -[:USES_FEDERATION]-> Pleiades
- Discoverable from graph queries

### **4. Wikidata is Universal**
- Used by ALL facets (enrichment hub)
- Mode: 'hub_api' (not local)
- Special role: Cross-federation linking

---

## 🔍 **Discovery Queries**

### **Which federations does a facet use?**
```cypher
MATCH (:Facet {key: 'GEOGRAPHIC'})-[:USES_FEDERATION]->(fed:Federation)
RETURN fed.name
// Returns: Pleiades, Wikidata, GeoNames
```

### **Which facets use a federation?**
```cypher
MATCH (facet:Facet)-[:USES_FEDERATION]->(:Federation {name: 'Wikidata'})
RETURN facet.key
// Returns: ALL 18 facets (Wikidata is universal)
```

### **What federations are available?**
```cypher
MATCH (:FederationRoot)-[:HAS_FEDERATION]->(fed:Federation)
RETURN fed.name, fed.mode, fed.type
ORDER BY fed.name
```

---

## ✅ **This is the Canonical Architecture**

**Clean, hierarchical, self-describing:**
- Chrystallum (system root)
- 2 branches (Federations, Facets)
- 10 federations (authorities)
- 18 facets
- Clear relationships (facets use federations)

**SCA can bootstrap from this!**

---

**Visualize in Neo4j Browser:**
```cypher
MATCH path = (sys:Chrystallum)-[*..3]->(n)
RETURN path
```

**Saved to:** `SYSTEM_SUBGRAPH_ARCHITECTURE_2026-02-19.md`

