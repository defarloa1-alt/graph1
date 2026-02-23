# Wikidata Property Type → Chrystallum Facet Mapping

**Source:** Q107649491 backlinks (500 unique property types)  
**Date:** 2026-02-22  
**Purpose:** Map Wikidata property classifications to Chrystallum's 18 facets

---

## Core Mappings

### ⚔️ **MILITARY Facet**
```
Q22964288 - Wikidata property for items about military
Q51089849 - Wikidata property related to weapons and military equipment
```

### 🏛️ **POLITICAL Facet**
```
Q22984475 - Wikidata property related to politics
Q22997934 - Wikidata property related to government and state
Q93433126 - Wikidata property for authority control for politicians
Q56457408 - Wikidata property for items about positions
```

### 🕌 **RELIGIOUS Facet**
```
Q22983697 - Wikidata property related to religions and beliefs
Q64263681 - Wikidata property related to Catholicism and the Catholic Church
Q64264420 - Wikidata property related to Christianity
Q64289010 - Wikidata property related to Buddhism
Q64348848 - Wikidata property related to Judaism and the Jewish people
Q64349017 - Wikidata property related to the Eastern Orthodox Church
Q73688627 - Wikidata property related to Islam
Q64295974 - Wikidata property related to Greek mythology
```

### 📍 **GEOGRAPHIC Facet**
```
Q18615777 - Wikidata property to indicate a location
Q18635217 - Wikidata property for specifying the location of an event
Q19829908 - Wikidata property for authority control for places
Q19829914 - Wikidata property related to places
Q52511956 - Wikidata property related to geography
```

### 📚 **INTELLECTUAL Facet**
```
Q18618644 - Wikidata property related to creative works
Q19833377 - Wikidata property for authority control for works
Q29546443 - Wikidata property for items about books
Q29548341 - Wikidata property for items about scholarly articles
Q29561722 - Wikidata property related to literature
Q54835335 - Wikidata property related to philosophy
Q55192982 - Wikidata property related to historiography
```

### 🎨 **ARTISTIC Facet**
```
Q27918607 - Wikidata property related to art
Q44847669 - Wikidata property to identify artworks
Q45312863 - Wikidata property related to sculpture
Q56216473 - Wikidata property for authority control for architects
Q43831109 - Wikidata property related to architecture
```

### 🏺 **ARCHAEOLOGICAL Facet**
```
Q46246642 - Wikidata property related to archaeology
Q107156662 - Wikidata property related to numismatics
Q51122237 - Wikidata property related to burials, graves, and memorials
```

### 💰 **ECONOMIC Facet**
```
Q21451178 - Wikidata property related to economics
Q51326087 - Wikidata property related to banking
Q106035765 - Wikidata property to identify businesses
```

### 👥 **DEMOGRAPHIC Facet**
```
Q22984494 - Wikidata property related to demography
Q18608871 - Wikidata property for items about people
Q52514469 - Wikidata property related to personal life
```

### 🌾 **CULTURAL Facet**
```
Q18618628 - Wikidata property for authority control for cultural heritage
Q23038310 - Wikidata property related to food and eating
Q41804262 - Wikidata property related to gastronomy
Q105999586 - Wikidata property related to ethnic groups or indigenous people
```

### 🔬 **SCIENTIFIC Facet**
```
Q21294996 - Wikidata property related to chemistry
Q21451142 - Wikidata property for items about astronomical objects
Q22981316 - Wikidata property related to physics
Q42752243 - Wikidata property related to anatomy
Q51077473 - Wikidata property related to time and duration
Q52425722 - Wikidata property related to natural science
Q61058429 - Wikidata property related to science
```

### 🗣️ **LINGUISTIC Facet**
```
Q18616084 - Wikidata property to indicate a language
Q20824104 - Wikidata property for items about languages
Q29887391 - Wikidata property related to linguistics
Q51092639 - Wikidata property related to phonetics
Q54076056 - Wikidata property for lexicographical data
```

### 🏛️ **BIOGRAPHIC Facet**
```
Q18608756 - Wikidata property for birth or death
Q18636233 - Wikidata property for a person-related event
Q19595382 - Wikidata property for authority control for people
Q56249073 - Wikidata property related to genealogy
Q97584729 - Wikidata property related to biographical dictionaries
```

---

## 📅 **Historical Period Filter (CRITICAL)**

**These 4 QIDs define which properties are relevant for historical research:**

```
Q56248884 - Ancient World (3000 BCE - 500 CE)
Q56248867 - Middle Ages (500 - 1500 CE)
Q56248906 - Early Modern (1500 - 1800 CE)
Q106827312 - Renaissance (14th-17th century)
```

**Use Case:**
When federating Wikidata properties, prioritize properties that are:
1. Instance of one of these 4 historical period types
2. OR: Instance of authority control types
3. OR: Related to core facets (MILITARY, POLITICAL, RELIGIOUS, etc.)

---

## 🎯 **Federation Scoring Formula**

```python
def calculate_property_federation_score(property_qid, property_types):
    """
    Calculate federation score based on property type classifications
    
    Args:
        property_qid: The property (e.g., P31, P279)
        property_types: List of QIDs this property is instance of
        
    Returns:
        Score 0-5
    """
    score = 0
    
    # Historical period relevance (+2)
    historical_types = {'Q56248884', 'Q56248867', 'Q56248906', 'Q106827312'}
    if any(pt in historical_types for pt in property_types):
        score += 2
    
    # Authority control (+2)
    if 'Q18614948' in property_types or any('authority control' in str(pt) for pt in property_types):
        score += 2
    
    # Core facet relevance (+1)
    core_facets = {
        'Q22964288', 'Q22984475', 'Q22983697',  # Military, Political, Religious
        'Q24575337', 'Q18615777', 'Q19829914'   # Events, Location, Places
    }
    if any(pt in core_facets for pt in property_types):
        score += 1
    
    return min(score, 5)  # Cap at 5
```

---

## 📋 **Next Steps**

1. ✅ Use `Q107649491_property_types_CLEAN.csv` for schema alignment
2. ⏳ Create property type lookup table in Neo4j
3. ⏳ Implement federation scoring based on property types
4. ⏳ Filter Wikidata properties by historical relevance
5. ⏳ Map to 18 Chrystallum facets systematically

---

**Files Ready:**
- `CSV/backlinks/Q107649491_property_types_CLEAN.csv` (500 unique)
- `CSV/backlinks/Q107649491_property_types_20260222_135228.csv` (1500 with dups)
