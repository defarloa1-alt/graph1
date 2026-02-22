# Federation Sources: Local vs API

**Date:** 2026-02-19  
**Purpose:** Clarify which federation sources are local vs external API  
**Key Insight:** Wikidata is THE federation hub, not "a" federation source

---

## 🔍 **Federation Sources: Local vs API**

Excellent question! Let me clarify what's **yours** vs **external**:

---

## 📁 **LOCAL (Extracted to CSV/Files)**

### **1. Pleiades (Ancient Geography)**
**Source:** Local files
```
Geographic/pleiades_places.csv (41,993 rows)
Geographic/pleiades_names.csv (42,000+ rows)
Geographic/pleiades_coordinates.csv
```

**How obtained:**
- Downloaded from pleiades.stoa.org
- Extracted to CSV
- **Stored locally** in your repo
- Version-controlled
- **No API calls needed** ✅

**Federation type:** PRIMARY (you own this data)

---

### **2. PeriodO (Temporal Periods)**
**Source:** Local files
```
Temporal/periodo-dataset.csv (30,000+ periods)
Temporal/periodo_filtered_end_before_minus2000.csv (1,077 periods)
```

**How obtained:**
- Downloaded from PeriodO project
- Filtered and processed
- **Stored locally** in CSV
- **No API calls needed** ✅

**Federation type:** PRIMARY (you own this data)

---

### **3. LCSH (Library of Congress Subject Headings)**
**Source:** Local files
```
LCSH/skos_subjects/ (SKOS/RDF format)
Subjects/CIP/cip_code,cip_title,lcc_classes,lcsh_term.csv (crosswalk)
```

**How obtained:**
- Downloaded from Library of Congress
- Converted to SKOS format
- **Stored locally**
- **No API calls needed** ✅

**Federation type:** PRIMARY (canonical authority, local copy)

---

### **4. FAST (Faceted Subject Headings)**
**Source:** Local file (large)
```
Python/fast/key/FASTTopical_parsed.csv (~1.9M records)
```

**How obtained:**
- Downloaded from OCLC FAST
- Parsed from MARC XML
- **Stored locally** (gitignored due to size)
- **No API calls needed** ✅

**Federation type:** PRIMARY (canonical authority, local copy)

---

### **5. LCC (Library of Congress Classification)**
**Source:** Local file
```
Subjects/lcc_flat.csv
Subjects/LCC/ (JSON files)
```

**How obtained:**
- Extracted from Library of Congress
- Flattened to CSV
- **Stored locally**
- **No API calls needed** ✅

**Federation type:** PRIMARY (canonical authority, local copy)

---

## 🌐 **EXTERNAL (API Calls)**

### **6. Wikidata (QID - THE FEDERATION HUB)**
**Source:** **Live API** ⚠️
```
API: https://www.wikidata.org/w/api.php
SPARQL: https://query.wikidata.org/sparql
```

**How obtained:**
- **API calls** to Wikidata Query Service
- SPARQL queries for properties (P31, P279, etc.)
- **NOT stored locally** (live queries)
- Rate-limited, requires internet

**Federation type:** **EXTERNAL HUB** (not "your" federation - it's THE federation everyone connects to)

**Critical distinction:**
- Wikidata is not **A** federation source
- Wikidata is **THE** federation hub
- Everyone federates TO Wikidata
- You use QIDs to link YOUR data to THE hub

---

### **7. GeoNames (Geographic Names)**
**Source:** Hybrid (API + Local crosswalk)
```
Local crosswalk: CSV/geographic/geonames_wikidata_mapping_v1.csv
Live lookup: Via Wikidata SPARQL (P1566 property)
```

**How obtained:**
- Crosswalk: Pre-built via API, stored as CSV
- Live: SPARQL query to Wikidata for P1566
- **Mostly local** (crosswalk), API for new lookups

**Federation type:** SECONDARY (via Wikidata bridge)

---

### **8. TGN (Getty Thesaurus of Geographic Names)**
**Source:** Local crosswalk only
```
CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv (45 mappings)
Temporal/Data/tgn_wikidata_mapping.csv
```

**How obtained:**
- Pre-built crosswalk
- **Stored locally**
- Limited coverage (45 places)

**Federation type:** TERTIARY (minimal, via crosswalk)

---

## 🎯 **Key Architectural Insight**

### **Wikidata is Special - NOT a "Federation Source"**

**Wrong thinking:**
```
Your federations: Pleiades, PeriodO, LCSH, FAST, LCC, Wikidata
(treating Wikidata as equal to others)
```

**Correct thinking:**
```
Your canonical authorities: Pleiades, PeriodO, LCSH, FAST, LCC
   ↓ (all link TO)
Wikidata (THE federation hub - everyone's shared reference point)
```

**Analogy:**
- Your authorities = **Your databases**
- Wikidata = **The internet**
- QID = **URL to shared knowledge**

---

## 📐 **Corrected Federation Model**

### **For Place:**
```python
federation_score = 
  pleiades_id (local) +      # 20 pts - YOUR authority
  temporal (local) +          # 20 pts - YOUR data
  coordinates (local) +       # 10 pts - YOUR data
  qid (link to hub) +        # 50 pts - LINK to shared knowledge
```

**QID doesn't mean "Wikidata is your federation"**  
**QID means "You're LINKED to the global federation hub"**

### **For SubjectConcept:**
```python
authority_federation_score =
  lcsh_id (local) +          # 30 pts - YOUR authority
  fast_id (local) +          # 30 pts - YOUR authority
  lcc_class (local) +        # 20 pts - YOUR authority
  qid (link to hub) +        # 20 pts - LINK to shared knowledge
```

**Pattern:** YOUR authorities + LINK to global hub

---

## ✅ **Your Federation Architecture**

```
LOCAL CANONICAL AUTHORITIES (Your Data):
├── Pleiades (41,993 places) - Geographic authority
├── PeriodO (1,077 periods) - Temporal authority
├── LCSH (subject headings) - Conceptual authority
├── FAST (faceted subjects) - Topical authority
└── LCC (classification) - Structural authority

   ↓ All link via QID to...

GLOBAL FEDERATION HUB (Shared Knowledge):
└── Wikidata (QID) - The shared reference point
    ↓ Everyone else also links here
    
OTHER SYSTEMS ALSO LINKING TO WIKIDATA:
├── Library of Congress → QID
├── Getty (TGN) → QID  
├── VIAF → QID
├── GeoNames → QID (P1566)
└── Thousands of other databases → QID
```

---

## 🎯 **Federation Scoring Clarified**

**Score measures:**
1. **Completeness of YOUR canonical authorities** (Pleiades, PeriodO, LCSH, FAST, LCC)
2. **PLUS connection to global hub** (QID)

**NOT:**
- How many external APIs you call
- How much Wikidata data you duplicate

**BUT:**
- How complete YOUR authorities are
- How well YOU link to THE hub

---

## 📝 **Summary**

**Your federations (local):**
- ✅ Pleiades (CSV)
- ✅ PeriodO (CSV)
- ✅ LCSH (SKOS files)
- ✅ FAST (CSV)
- ✅ LCC (CSV)

**Your link to THE hub:**
- ✅ Wikidata QID (connects you to global knowledge graph)

**Pattern:**
- **Federation = YOUR canonical authorities**
- **QID = Your link to EVERYONE ELSE's authorities**

---

## 🔧 **Practical Implications**

### **When to Query API:**
- **Wikidata:** Only when discovering new entities (backlinks, hierarchy traversal)
- **GeoNames:** Only for new place lookups (most are in crosswalk)

### **When to Use Local:**
- **Pleiades:** Always (all data is local)
- **PeriodO:** Always (all data is local)
- **LCSH/FAST/LCC:** Always (all data is local)

### **Offline Capability:**
- ✅ Can score places/periods/concepts WITHOUT internet
- ✅ Local authorities are complete
- ⚠️ Need internet ONLY for:
  - New Wikidata entity discovery
  - New GeoNames lookups
  - Backlink harvesting

---

**This is the correct federation architecture!** ✅

---

**Saved to:** `md/Architecture/FEDERATION_SOURCES_LOCAL_VS_API_2026-02-19.md`

