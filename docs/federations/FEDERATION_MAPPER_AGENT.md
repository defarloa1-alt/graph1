# Federation Mapper Agent

**Purpose:** Hook into multiple federation sources and return IDs + Labels

---

## 🌐 FEDERATION SOURCES

### **1. Wikidata** (Primary Hub)
- **Input:** QID (Q17167)
- **Output:** 
  - QID: Q17167
  - Label: "Roman Republic"
  - All properties with labels
  - All values with labels

### **2. LCSH** (Library of Congress Subject Headings)
- **Source 1:** Wikidata P244 property
- **Source 2:** Local LCSH dataset
- **Output:**
  - LCSH ID: sh85115114
  - Label: "Rome--History--Republic, 510-30 B.C."
  - Authority file metadata

### **3. FAST** (Faceted Application of Subject Terminology)
- **Source 1:** Wikidata P2163 property
- **Source 2:** Local FAST dataset (Python/fast/key/FASTTopical_parsed.csv)
- **Output:**
  - FAST ID: fst01204885
  - Label: "Rome--History--Republic, 265-30 B.C."
  - Topical facets

### **4. LCC** (Library of Congress Classification)
- **Source 1:** Wikidata P1149 property
- **Source 2:** Local LCC dataset (Subjects/lcc_flat.csv)
- **Output:**
  - LCC Class: DG241-269
  - Label: "Rome--History--Republic"
  - Classification hierarchy

### **5. PeriodO** (Period Gazetteer)
- **Source:** Local PeriodO dataset (Temporal/periodo-dataset.csv - 8,959 periods)
- **Matching:**
  - By label similarity
  - By temporal overlap
  - By QID crosswalk
- **Output:**
  - PeriodO ID: p0xxxxx
  - Label: "Roman Republic"
  - Spatial coverage
  - Temporal extent

### **6. Pleiades** (Ancient Places)
- **Source:** Local Pleiades dataset (Geographic/pleiades_places.csv - 41,993 places)
- **Matching:**
  - By Wikidata P1584
  - By label similarity
  - By coordinate proximity
- **Output:**
  - Pleiades ID: 423025
  - Label: "Roma"
  - Coordinates
  - Temporal attestation

### **7. Getty TGN** (Thesaurus of Geographic Names)
- **Source:** Wikidata P1667 property
- **Output:**
  - TGN ID: 7000874
  - Label: "Roma"
  - Geographic hierarchy

### **8. Wikidata Labels** (Multilingual)
- **Source:** Wikidata labels
- **Output:**
  - 138 languages
  - All label variants
  - Aliases

---

## 🔧 FEDERATION MAPPER FUNCTIONALITY

### **Function 1: get_all_federations(qid)**

```python
def get_all_federations(qid: str) -> dict:
    """
    Hook into all federation sources for a QID
    
    Returns ALL federation IDs and labels
    """
    
    result = {
        'qid': qid,
        'federations': {}
    }
    
    # 1. Wikidata (primary)
    wikidata = fetch_wikidata(qid)
    result['federations']['wikidata'] = {
        'id': qid,
        'label': wikidata['labels']['en'],
        'description': wikidata['descriptions']['en']
    }
    
    # 2. LCSH (from Wikidata P244)
    if 'P244' in wikidata['claims']:
        lcsh_id = wikidata['claims']['P244'][0]['value']
        result['federations']['lcsh'] = {
            'id': lcsh_id,
            'label': get_lcsh_label(lcsh_id),  # Query LCSH
            'source': 'wikidata_p244'
        }
    else:
        # Try matching to local LCSH
        lcsh_match = match_to_lcsh(wikidata['labels']['en'])
        if lcsh_match:
            result['federations']['lcsh'] = lcsh_match
    
    # 3. FAST (from Wikidata P2163 or local match)
    if 'P2163' in wikidata['claims']:
        fast_id = wikidata['claims']['P2163'][0]['value']
        result['federations']['fast'] = {
            'id': fast_id,
            'label': get_fast_label(fast_id),  # Load from local CSV
            'source': 'wikidata_p2163'
        }
    else:
        fast_match = match_to_fast(wikidata['labels']['en'])
        if fast_match:
            result['federations']['fast'] = fast_match
    
    # 4. PeriodO (external matching for periods)
    if is_period(wikidata):
        periodo_match = match_to_periodo(
            label=wikidata['labels']['en'],
            start_date=extract_start_date(wikidata),
            end_date=extract_end_date(wikidata),
            qid=qid
        )
        if periodo_match:
            result['federations']['periodo'] = {
                'id': periodo_match['periodo_id'],
                'label': periodo_match['label'],
                'spatial_coverage': periodo_match['spatial'],
                'temporal_extent': periodo_match['temporal']
            }
    
    # 5. Pleiades (from Wikidata P1584 or local match for places)
    if is_place(wikidata):
        if 'P1584' in wikidata['claims']:
            pleiades_id = wikidata['claims']['P1584'][0]['value']
            result['federations']['pleiades'] = {
                'id': pleiades_id,
                'label': get_pleiades_label(pleiades_id),  # Load from CSV
                'source': 'wikidata_p1584'
            }
        else:
            pleiades_match = match_to_pleiades(
                label=wikidata['labels']['en'],
                coordinates=extract_coordinates(wikidata)
            )
            if pleiades_match:
                result['federations']['pleiades'] = pleiades_match
    
    # 6. Getty TGN (from Wikidata P1667)
    if 'P1667' in wikidata['claims']:
        tgn_id = wikidata['claims']['P1667'][0]['value']
        result['federations']['tgn'] = {
            'id': tgn_id,
            'label': wikidata['labels']['en'],  # Use Wikidata label
            'source': 'wikidata_p1667'
        }
    
    return result
```

---

## 📊 EXAMPLE OUTPUT

### **For Q17167 (Roman Republic):**

```json
{
  "qid": "Q17167",
  "federations": {
    "wikidata": {
      "id": "Q17167",
      "label": "Roman Republic",
      "description": "period of ancient Roman civilization (509 BC–27 BC)"
    },
    "lcsh": {
      "id": "sh85115114",
      "label": "Rome--History--Republic, 510-30 B.C.",
      "source": "wikidata_p244"
    },
    "fast": {
      "id": "fst01204885",
      "label": "Rome--History--Republic, 265-30 B.C.",
      "source": "local_match"
    },
    "lcc": {
      "id": "DG241-269",
      "label": "Rome--History--Republic",
      "source": "local_match"
    },
    "periodo": {
      "id": "p0qhb9w",
      "label": "Roman Republic",
      "spatial_coverage": "Mediterranean",
      "temporal_extent": "-0509/-0027"
    }
  }
}
```

### **For Q220 (Rome):**

```json
{
  "qid": "Q220",
  "federations": {
    "wikidata": {
      "id": "Q220",
      "label": "Rome"
    },
    "lcsh": {
      "id": "n79018704",
      "label": "Rome (Italy)"
    },
    "fast": {
      "id": "1204500",
      "label": "Rome (Italy)"
    },
    "pleiades": {
      "id": "423025",
      "label": "Roma",
      "coordinates": "41.891775, 12.486137"
    },
    "tgn": {
      "id": "7000874",
      "label": "Roma"
    }
  }
}
```

---

## 🎯 NEXT STEPS

**After SCA completes:**

1. Build Federation Mapper components
2. Load local federation datasets (PeriodO, Pleiades, FAST, LCC)
3. Process SCA output through mapper
4. Generate complete federation report
5. Create Neo4j import files

**Federation Mapper = The bridge between Wikidata and Chrystallum!** 🌉
