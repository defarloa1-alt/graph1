# Agent Reference: Authority File Paths

**Date:** 2026-02-19  
**Purpose:** File path reference for SCA and SFA agents  
**Audience:** Automated agents, developers

---

## 🗂️ **Authority Reference Files**

### **1. LCC (Library of Congress Classification)**

**Primary:**
```
Subjects/lcc_flat.csv
```
- **Purpose:** LCC classification codes and labels
- **Columns:** lcc_code, lcc_label, description
- **Usage:** Agent routing, primary classification backbone
- **Example:** DG (Roman History), DF (Greek History)

**Secondary:**
```
Subjects/CIP/cip_code,cip_title,lcc_classes,lcsh_term.csv
```
- **Purpose:** CIP → LCC → LCSH crosswalk
- **Usage:** Academic discipline alignment

---

### **2. LCSH (Library of Congress Subject Headings)**

**Primary:**
```
LCSH/skos_subjects/
```
- **Purpose:** LCSH subject headings (SKOS format)
- **Note:** This is a directory with multiple files
- **Format:** RDF/SKOS
- **Usage:** Subject concept authority, library catalog compatibility

**Crosswalk:**
```
Subjects/CIP/cip_code,cip_title,lcc_classes,lcsh_term.csv
```
- **Purpose:** Links CIP codes to LCSH terms
- **Columns:** cip_code, cip_title, lcc_classes, lcsh_term

---

### **3. FAST (Faceted Application of Subject Terminology)**

**Primary (Topical):**
```
Python/fast/key/FASTTopical_parsed.csv
```
- **Purpose:** FAST topical subject headings
- **Columns:** fast_id, label, broader, narrower, related
- **Usage:** Faceted subject tagging, multi-dimensional discovery

**Note:** FASTTopical_parsed.csv is gitignored (large file)
- **Size:** ~1.9M records
- **Generate:** Use FAST import scripts if needed
- **Alternative:** Query via FAST API or Wikidata

---

### **4. PeriodO (Temporal Period Authority)**

**Current Canonical:**
```
Temporal/periodo-dataset.csv
```
- **Purpose:** PeriodO period definitions (all periods)
- **Columns:** periodo_id, label, start_year, end_year, spatial_coverage, authority_uri
- **Rows:** ~30,000+ periods
- **Usage:** Temporal period authority, period classification

**Filtered (Ancient Focus):**
```
Temporal/periodo_filtered_end_before_minus2000.csv
Temporal/periodo_filtered_end_before_minus2000_with_geography.csv
```
- **Purpose:** Periods ending before -2000 (ancient/prehistoric focus)
- **Rows:** ~1,077 periods
- **Usage:** Ancient history subset
- **Current in Neo4j:** This filtered set (1,077 Period nodes)

**Wikidata Crosswalk:**
```
Temporal/periodo_wikidata_crosswalk.csv
```
- **Purpose:** Maps PeriodO IDs to Wikidata QIDs
- **Columns:** periodo_id, wikidata_qid, label
- **Rows:** 96 mappings
- **Usage:** Link PeriodO periods to Wikidata

**Recent Analysis:**
```
Temporal/periodoCurrent.csv
```
- **Purpose:** Current/active periods snapshot

---

### **5. Pleiades (Ancient Geography Authority)**

**Core Place Data:**
```
Geographic/pleiades_places.csv
```
- **Purpose:** Pleiades ancient place gazetteer
- **Columns:** pleiades_id, label, description, place_type, bbox, lat, long, min_date, max_date, uri, wikidata_qid
- **Rows:** ~41,993 places
- **Usage:** Primary ancient geography source
- **Current in Neo4j:** All 41,993 loaded

**Place Names (Multilingual):**
```
Geographic/pleiades_names.csv
```
- **Purpose:** Alternate names in multiple languages
- **Columns:** pleiades_id, name_id, name_attested, language, name_type, romanized
- **Rows:** ~42,000+ names in 101 languages
- **Note:** Not loaded to Neo4j (canonical model uses QIDs)

**Coordinates:**
```
Geographic/pleiades_coordinates.csv
```
- **Purpose:** Geographic coordinates for places
- **Columns:** pleiades_id, location_id, lat, long, precision, title, location_type
- **Rows:** ~8 (minimal - most coords are in pleiades_places.csv)

**Enhanced:**
```
Geographic/pleiades_plus.csv
```
- **Purpose:** Pleiades + GeoNames enrichment
- **Source:** https://github.com/ryanfb/pleiades-plus

---

### **6. Federation Crosswalks**

**Pleiades ↔ GeoNames ↔ Wikidata ↔ TGN:**
```
CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv
```
- **Purpose:** Four-way federation mapping
- **Columns:** pleiades_id, geonames_id, wikidata_qid, tgn_id, has_wikidata_match, is_fully_triangulated
- **Rows:** 4,555
- **Usage:** Wikidata QID enrichment, federation scoring
- **Used by:** enrich_places_with_wikidata.py

**Pleiades ↔ GeoNames:**
```
CSV/geographic/pleiades_geonames_crosswalk_v1.csv
```
- **Purpose:** Pleiades to GeoNames mapping
- **Usage:** Geographic name standardization

**GeoNames ↔ Wikidata:**
```
CSV/geographic/geonames_wikidata_mapping_v1.csv
```
- **Purpose:** GeoNames to Wikidata via SPARQL (P1566)
- **Rows:** 3,344
- **Usage:** Wikidata QID resolution from GeoNames

---

### **7. Place Type Taxonomy**

**Hierarchy:**
```
CSV/geographic/place_type_hierarchy_v1.csv
```
- **Purpose:** PlaceType taxonomy with semantic classification
- **Columns:** place_type, parent_type, geo_semantic_type, confidence
- **Rows:** 14 types
- **Current in Neo4j:** Loaded (14 PlaceType nodes)

**Token Mapping:**
```
CSV/geographic/pleiades_place_type_token_mapping_v1.csv
```
- **Purpose:** Maps Pleiades type strings to canonical types
- **Rows:** 212 token mappings
- **Current in Neo4j:** Loaded (212 PlaceTypeTokenMap nodes)

---

### **8. Wikidata Enrichment**

**Places with QID (Extract):**
```
CSV/geographic/places_with_wikidata_qid_2026-02-19.csv
```
- **Purpose:** Export of places that have Wikidata QIDs
- **Rows:** 2,458 places
- **Created:** 2026-02-19 (today's session)
- **Usage:** Federation quality analysis

---

### **9. Facet Registry**

**Canonical Facets:**
```
Facets/facet_registry_master.json
Facets/facet_registry_master.csv
```
- **Purpose:** 18 canonical facets with anchors
- **Facets:** Military, Political, Economic, Religious, Social, Cultural, Artistic, Intellectual, Linguistic, Geographic, Environmental, Technological, Demographic, Diplomatic, Scientific, Archaeological, Biographic, Communication
- **Usage:** Facet classification, agent spawning

---

### **10. Relationship Types**

**Canonical Relationships:**
```
Relationships/relationship_types_registry_master.csv
```
- **Purpose:** 311 canonical relationship types
- **Columns:** relationship_type, wikidata_property, cidoc_crm_property, definition
- **Usage:** Relationship validation, semantic alignment

**Wikidata P-values:**
```
CSV/project_p_values_canonical.csv
```
- **Purpose:** Wikidata property mappings
- **Usage:** Property alignment, federation

---

## 🤖 **Agent Quick Reference**

### **For SCA Agent:**

**Bootstrap Authority Files (Load These First):**
```python
AUTHORITY_FILES = {
    'lcc': 'Subjects/lcc_flat.csv',
    'lcsh_crosswalk': 'Subjects/CIP/cip_code,cip_title,lcc_classes,lcsh_term.csv',
    'fast': 'Python/fast/key/FASTTopical_parsed.csv',  # If available
    'periodo': 'Temporal/periodo-dataset.csv',
    'periodo_filtered': 'Temporal/periodo_filtered_end_before_minus2000_with_geography.csv',
    'pleiades_places': 'Geographic/pleiades_places.csv',
    'pleiades_names': 'Geographic/pleiades_names.csv',
    'facets': 'Facets/facet_registry_master.json',
    'relationships': 'Relationships/relationship_types_registry_master.csv'
}
```

**Federation Crosswalks (For Enrichment):**
```python
FEDERATION_FILES = {
    'pleiades_wikidata': 'CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv',
    'periodo_wikidata': 'Temporal/periodo_wikidata_crosswalk.csv',
    'geonames_wikidata': 'CSV/geographic/geonames_wikidata_mapping_v1.csv'
}
```

---

## 📍 **Absolute Paths (For Agent Config)**

```python
# Base directory
BASE_DIR = "C:\\Projects\\Graph1"

# Authority files (absolute paths)
PATHS = {
    # LCC
    'lcc_flat': f"{BASE_DIR}\\Subjects\\lcc_flat.csv",
    
    # LCSH  
    'lcsh_skos_dir': f"{BASE_DIR}\\LCSH\\skos_subjects",
    'cip_lcsh_crosswalk': f"{BASE_DIR}\\Subjects\\CIP\\cip_code,cip_title,lcc_classes,lcsh_term.csv",
    
    # FAST
    'fast_topical': f"{BASE_DIR}\\Python\\fast\\key\\FASTTopical_parsed.csv",
    
    # PeriodO
    'periodo_full': f"{BASE_DIR}\\Temporal\\periodo-dataset.csv",
    'periodo_ancient': f"{BASE_DIR}\\Temporal\\periodo_filtered_end_before_minus2000_with_geography.csv",
    'periodo_wikidata': f"{BASE_DIR}\\Temporal\\periodo_wikidata_crosswalk.csv",
    
    # Pleiades
    'pleiades_places': f"{BASE_DIR}\\Geographic\\pleiades_places.csv",
    'pleiades_names': f"{BASE_DIR}\\Geographic\\pleiades_names.csv",
    'pleiades_coords': f"{BASE_DIR}\\Geographic\\pleiades_coordinates.csv",
    
    # Federation
    'pleiades_wikidata_crosswalk': f"{BASE_DIR}\\CSV\\geographic\\pleiades_geonames_wikidata_tgn_crosswalk_v1.csv",
    'geonames_wikidata': f"{BASE_DIR}\\CSV\\geographic\\geonames_wikidata_mapping_v1.csv",
    
    # Facets & Relationships
    'facets_json': f"{BASE_DIR}\\Facets\\facet_registry_master.json",
    'facets_csv': f"{BASE_DIR}\\Facets\\facet_registry_master.csv",
    'relationships': f"{BASE_DIR}\\Relationships\\relationship_types_registry_master.csv",
    'p_values': f"{BASE_DIR}\\CSV\\project_p_values_canonical.csv"
}
```

---

## 🎯 **Usage Instructions for Agent**

### **Step 1: Load Authority References**

```python
import csv
import json
from pathlib import Path

BASE_DIR = Path("C:/Projects/Graph1")

# Load LCC codes
lcc_lookup = {}
with open(BASE_DIR / "Subjects/lcc_flat.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        lcc_lookup[row['lcc_code']] = row['lcc_label']

# Load Facets
with open(BASE_DIR / "Facets/facet_registry_master.json") as f:
    facets = json.load(f)['facets']

# Load PeriodO periods
periodo_lookup = {}
with open(BASE_DIR / "Temporal/periodo-dataset.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        periodo_lookup[row['periodo_id']] = {
            'label': row['label'],
            'start': row['start_year'],
            'end': row['end_year']
        }

# Load Pleiades places
pleiades_lookup = {}
with open(BASE_DIR / "Geographic/pleiades_places.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pleiades_lookup[row['pleiades_id']] = {
            'label': row['label'],
            'lat': row['lat'],
            'long': row['long'],
            'qid': row.get('wikidata_qid')
        }

# Load Wikidata crosswalk
pleiades_to_qid = {}
with open(BASE_DIR / "CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['pleiades_id'] and row['wikidata_qid']:
            pleiades_to_qid[row['pleiades_id']] = row['wikidata_qid']
```

### **Step 2: Query Neo4j with Authority Context**

```python
from neo4j import GraphDatabase

# Connect to Aura
driver = GraphDatabase.driver(
    "neo4j+s://f7b612a3.databases.neo4j.io",
    auth=("neo4j", "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM")
)

# Fetch place with authority enrichment
with driver.session() as session:
    result = session.run("""
        MATCH (p:Place {pleiades_id: $pleiades_id})
        RETURN p
    """, pleiades_id="295353")
    
    place = result.single()['p']
    
    # Enrich with crosswalk data
    if place['pleiades_id'] in pleiades_to_qid:
        wikidata_qid = pleiades_to_qid[place['pleiades_id']]
        print(f"Wikidata QID: {wikidata_qid}")
```

### **Step 3: Federation Scoring**

```python
from scripts.federation.federation_scorer import FederationScorer

scorer = FederationScorer()

# Score a place
place_data = {
    'pleiades_id': place['pleiades_id'],
    'qid': place.get('qid'),
    'min_date': place.get('min_date'),
    'max_date': place.get('max_date'),
    'lat': place.get('lat'),
    'long': place.get('long')
}

score_result = scorer.score_place_simple(place_data)

print(f"Federation Score: {score_result['federation_score']}")
print(f"State: {score_result['federation_state']}")
print(f"Vertex Jump: {score_result['vertex_jump_enabled']}")
```

---

## 📋 **File Path Quick Reference Table**

| Authority | Primary File | Location | Format | Size |
|-----------|--------------|----------|--------|------|
| **LCC** | lcc_flat.csv | Subjects/ | CSV | Small |
| **LCSH** | skos_subjects/ | LCSH/ | RDF/SKOS | Large |
| **FAST** | FASTTopical_parsed.csv | Python/fast/key/ | CSV | Large (gitignored) |
| **PeriodO** | periodo-dataset.csv | Temporal/ | CSV | Large (30K rows) |
| **PeriodO (filtered)** | periodo_filtered_*.csv | Temporal/ | CSV | Medium (1K rows) |
| **Pleiades** | pleiades_places.csv | Geographic/ | CSV | Large (42K rows) |
| **Pleiades Names** | pleiades_names.csv | Geographic/ | CSV | Large (42K rows) |
| **Federation** | pleiades_geonames_wikidata_tgn_crosswalk_v1.csv | CSV/geographic/ | CSV | Medium (4.5K rows) |
| **Facets** | facet_registry_master.json | Facets/ | JSON | Small |
| **Relationships** | relationship_types_registry_master.csv | Relationships/ | CSV | Medium (311 types) |

---

## 🔗 **Neo4j Connection (Aura)**

**For Agent Configuration:**

```python
NEO4J_CONFIG = {
    'uri': 'neo4j+s://f7b612a3.databases.neo4j.io',
    'username': 'neo4j',
    'password': 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM',
    'database': 'neo4j'
}
```

**What's Already in Neo4j:**
- Year: 4,025 nodes
- Period: 1,077 nodes (from periodo_filtered)
- Place: 41,993 nodes (from pleiades_places)
- PlaceType: 14 nodes
- Federation properties: Scores, states, cipher keys

---

## 📝 **Agent Implementation Template**

```python
#!/usr/bin/env python3
"""
SCA Agent - Authority File Reference Template
"""
from pathlib import Path
import csv
import json
from neo4j import GraphDatabase

# Base directory
BASE_DIR = Path("C:/Projects/Graph1")

class SCAAgent:
    """Subject Concept Agent with authority file access"""
    
    def __init__(self):
        # Load authority references
        self.lcc = self._load_lcc()
        self.facets = self._load_facets()
        self.periodo = self._load_periodo()
        self.pleiades = self._load_pleiades()
        self.crosswalk = self._load_crosswalk()
        
        # Connect to Neo4j
        self.driver = GraphDatabase.driver(
            "neo4j+s://f7b612a3.databases.neo4j.io",
            auth=("neo4j", "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM")
        )
    
    def _load_lcc(self):
        """Load LCC classification codes"""
        lcc = {}
        with open(BASE_DIR / "Subjects/lcc_flat.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lcc[row['lcc_code']] = row
        return lcc
    
    def _load_facets(self):
        """Load facet registry"""
        with open(BASE_DIR / "Facets/facet_registry_master.json") as f:
            return json.load(f)
    
    def _load_periodo(self):
        """Load PeriodO periods"""
        periodo = {}
        with open(BASE_DIR / "Temporal/periodo-dataset.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                periodo[row['periodo_id']] = row
        return periodo
    
    def _load_pleiades(self):
        """Load Pleiades places"""
        pleiades = {}
        with open(BASE_DIR / "Geographic/pleiades_places.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pleiades[row['pleiades_id']] = row
        return pleiades
    
    def _load_crosswalk(self):
        """Load Pleiades-Wikidata crosswalk"""
        crosswalk = {}
        with open(BASE_DIR / "CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['pleiades_id']:
                    crosswalk[row['pleiades_id']] = {
                        'wikidata_qid': row['wikidata_qid'],
                        'geonames_id': row['geonames_id'],
                        'tgn_id': row['tgn_id']
                    }
        return crosswalk
    
    def discover_hierarchy(self, qid: str):
        """Discover hierarchy from Wikidata"""
        # Implementation here
        pass
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()


# Usage
if __name__ == "__main__":
    agent = SCAAgent()
    print(f"Loaded {len(agent.lcc)} LCC codes")
    print(f"Loaded {len(agent.facets['facets'])} facets")
    print(f"Loaded {len(agent.periodo)} periods")
    print(f"Loaded {len(agent.pleiades)} places")
    print(f"Loaded {len(agent.crosswalk)} crosswalk mappings")
    agent.close()
```

---

## ✅ **Ready for Agent Implementation**

**All authority files are:**
- ✅ Located and documented
- ✅ Absolute paths provided
- ✅ Loading code template provided
- ✅ Neo4j connection configured for Aura

**Agent can now:**
- Load all authority references
- Query Neo4j with enriched context
- Calculate federation scores
- Resolve QIDs via crosswalks
- Navigate temporal/geographic backbones

---

**Want me to create the full SCA agent implementation using these paths?**
