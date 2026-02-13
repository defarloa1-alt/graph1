# Schema Gap Analysis: Missing Valuable Standards

## Current Schema Coverage

We have canon/standards for:
- ✅ **Entities** - Entity types with Wikidata QIDs
- ✅ **Relationships** - Relationship types with Wikidata properties
- ✅ **Time** - ISO 8601 with historical dates (negative years)
- ✅ **Place** - Pleiades IDs, geographic coordinates
- ✅ **Subject Classification** - FAST, LCC, LCSH, MARC
- ✅ **Action Structure** - Goal, Trigger, Action, Result, Narrative vocabularies

## Potentially Missing Schemas

### 1. **Authority Control Standards** ⚠️ HIGH PRIORITY

#### VIAF (Virtual International Authority File)

**What it is:**
- International authority file linking name authority records from libraries worldwide
- Resolves variant names, different language forms, pseudonyms
- Standard IDs for persons, organizations, works

**Why We Need It:**
- ✅ **Person disambiguation**: "Julius Caesar" vs. "Gaius Julius Caesar" vs. other Caesars
- ✅ **Name variants**: Multiple language forms, historical spellings
- ✅ **Cross-library linking**: Connects our entities to worldwide library authority records

**Current Gap:**
```cypher
// Currently:
(person:Human {label: 'Julius Caesar', qid: 'Q1048'})

// Should also have:
(person:Human {
  viaf_id: '78287861',
  viaf_link: 'http://viaf.org/viaf/78287861'
})
```

**Integration:**
- Add `viaf_id` and `viaf_link` to Person entities
- Use VIAF for automatic name variant resolution
- Validate against VIAF during entity extraction

**Value:** ⭐⭐⭐ **HIGH** - Critical for person disambiguation and name authority

---

#### ISNI (International Standard Name Identifier)

**What it is:**
- ISO 27729 standard for identifying public identities
- Links person names across different domains (research, publishing, media)
- 16-digit numeric identifier

**Why We Need It:**
- ✅ **Cross-domain identity**: Same person in historical, academic, literary contexts
- ✅ **Work attribution**: Links authors to works across systems
- ✅ **Persistent identifiers**: Stable IDs independent of name changes

**Current Gap:**
- No ISNI properties on Person entities

**Integration:**
- Add `isni` property to Person entities
- Use for work-author relationships

**Value:** ⭐⭐ **MEDIUM** - Useful for author/work attribution, less critical than VIAF

---

#### ORCID (for Modern/Academic Persons)

**What it is:**
- Researcher identifiers for modern academics and scholars
- Less relevant for ancient history but useful for:
  - Modern historians who write about historical subjects
  - Scholars who publish on historical topics

**Why We Need It:**
- ⚠️ **Limited relevance** for ancient/medieval history
- ✅ Could be useful for modern scholars writing about historical topics
- ✅ Links to academic publications

**Current Gap:**
- Not applicable to most historical entities

**Integration:**
- Only add to modern Person entities (historians, researchers)
- Not needed for historical persons

**Value:** ⭐ **LOW** - Minimal relevance for historical focus

---

### 2. **Cultural Heritage & Archival Standards** ⚠️ HIGH PRIORITY

#### CIDOC-CRM (Conceptual Reference Model)

**What it is:**
- ISO 21127 standard for cultural heritage information
- Event-centric model (events are primary, entities participate)
- Used by museums, archives, cultural institutions worldwide

**Why We Need It:**
- ✅ **Museum integration**: Link knowledge graph to museum collections
- ✅ **Event modeling**: Aligns with our action structure approach
- ✅ **Cultural heritage data**: Standard for archaeological, museum data

**Current Gap:**
- Our event/action structure exists but not aligned with CIDOC-CRM classes
- No mapping to CIDOC-CRM properties/classes

**Integration Options:**
1. **Mapping layer**: Map our schema to CIDOC-CRM classes
2. **CIDOC-CRM properties**: Add CIDOC-CRM class IDs to entities
3. **Event alignment**: Ensure our event structure aligns with CIDOC-CRM event model

**Example Mapping:**
```cypher
// Our structure:
(event:Event {label: 'Crossing of Rubicon'})

// CIDOC-CRM alignment:
(event:Event {
  cidoc_crm_class: 'E5_Event',
  cidoc_crm_properties: {
    'P4_has_time-span': {...},
    'P7_took_place_at': {...},
    'P11_had_participant': {...}
  }
})
```

**Value:** ⭐⭐⭐ **HIGH** - Critical for museum/archival integration

---

#### EAC-CPF (Encoded Archival Context - Corporate Bodies, Persons, Families)

**What it is:**
- XML standard for describing archival creators (persons, organizations, families)
- Used in archives worldwide for authority records
- Provides biographical/historical information about entities

**Why We Need It:**
- ✅ **Archival integration**: Link to archival authority records
- ✅ **Biographical data**: Rich biographical/historical context
- ✅ **Authority records**: Standard format for entity descriptions

**Current Gap:**
- No EAC-CPF alignment or properties

**Integration:**
- Add `eac_cpf_id` to Person/Organization entities
- Import biographical data from EAC-CPF records
- Use for entity enrichment

**Value:** ⭐⭐ **MEDIUM** - Useful for archival integration, less critical than CIDOC-CRM

---

#### EAD (Encoded Archival Description)

**What it is:**
- XML standard for describing archival collections
- Used for finding aids, collection descriptions
- Less directly relevant for entity-level data

**Why We Might Need It:**
- ⚠️ Collection-level, not entity-level standard
- ✅ Could link entities to archival collections that document them
- ✅ Source attribution for historical claims

**Current Gap:**
- No EAD collection links

**Integration:**
- Add `ead_collection_id` to sources/relationships
- Link entities to archival collections that document them

**Value:** ⭐ **LOW** - Useful but not critical for core schema

---

### 3. **Language & Script Standards** ⚠️ MEDIUM PRIORITY

#### ISO 639 (Language Codes)

**What it is:**
- ISO standard for language identification
- ISO 639-1 (2-letter), ISO 639-2 (3-letter), ISO 639-3 (comprehensive)

**Why We Need It:**
- ✅ **Multilingual labels**: Entity labels in multiple languages
- ✅ **Source language**: Identify language of historical sources
- ✅ **Ancient languages**: Latin, Greek, Ancient Egyptian, etc.
- ✅ **Work language**: Language of written works

**Current Gap:**
```cypher
// Currently:
(work:Book {label: 'Commentarii de Bello Gallico'})

// Should also have:
(work:Book {
  label: 'Commentarii de Bello Gallico',
  language: 'la',  // ISO 639-1: Latin
  language_iso639_2: 'lat',  // ISO 639-2
  language_iso639_3: 'lat'   // ISO 639-3
})
```

**Integration:**
- Add `language` (ISO 639-1), `language_iso639_2`, `language_iso639_3` properties
- Add to Works, Documents, Manuscripts
- Add to relationships (source language for narratives)

**Value:** ⭐⭐ **MEDIUM** - Important for multilingual historical sources

---

#### Unicode Script Property

**What it is:**
- Unicode standard for identifying writing systems
- Script codes: Latn (Latin), Grek (Greek), Copt (Coptic), etc.

**Why We Need It:**
- ✅ **Ancient scripts**: Identify script of inscriptions, manuscripts
- ✅ **Digital representation**: Ensure proper character encoding
- ✅ **Source material**: Script of original historical sources

**Integration:**
- Add `script` property (Unicode script code)
- Most relevant for Works, Inscriptions, Manuscripts

**Value:** ⭐ **LOW-MEDIUM** - Useful but specialized use case

---

### 4. **Provenance & Source Standards** ⚠️ MEDIUM PRIORITY

#### Citation Styles (APA, Chicago, MLA, etc.)

**What it is:**
- Standard citation formats for academic sources
- Used for scholarly attribution

**Why We Need It:**
- ✅ **Source attribution**: Standard formats for citations
- ✅ **Academic compatibility**: Works with citation management tools
- ✅ **Bibliographic data**: Structured citation information

**Current Gap:**
- We have `sources` array but not standardized citation formats

**Integration:**
```cypher
// Current:
sources: [{source: 'Suetonius - Life of Caesar'}]

// Enhanced:
sources: [{
  source: 'Suetonius - Life of Caesar',
  citation_apa: 'Suetonius. (c. 121 CE). Life of Caesar.',
  citation_chicago: 'Suetonius. Life of Caesar. c. 121 CE.',
  citation_mla: 'Suetonius. Life of Caesar. c. 121 CE.',
  citation_harvard: 'Suetonius (c. 121 CE) Life of Caesar'
}]
```

**Value:** ⭐⭐ **MEDIUM** - Useful for academic integration, not critical for core functionality

---

#### PROV (Provenance Data Model)

**What it is:**
- W3C standard for representing provenance (origin/history of data)
- Entities, Activities, Agents model

**Why We Might Need It:**
- ✅ **Data lineage**: Track where knowledge graph data came from
- ✅ **Transformation history**: How data was processed
- ✅ **Agent attribution**: Who/what extracted/validated data

**Current Gap:**
- We have basic source attribution but not structured PROV model

**Integration:**
- Add PROV properties to track data provenance
- `prov_wasGeneratedBy`, `prov_wasDerivedFrom`, `prov_wasAttributedTo`

**Value:** ⭐ **LOW-MEDIUM** - Advanced use case, might be overkill

---

### 5. **Temporal Granularity Standards** ✅ PARTIALLY COVERED

#### Calendar Systems

**What it is:**
- Different calendar systems: Julian, Gregorian, Roman, Egyptian, etc.
- Date conversion between calendars

**Why We Need It:**
- ✅ **Historical accuracy**: Original sources use different calendars
- ✅ **Date conversion**: Convert between calendar systems
- ✅ **Precision**: Some events only known in specific calendar

**Current Gap:**
- We use ISO 8601 (Gregorian) exclusively
- No calendar system metadata

**Integration:**
```cypher
// Current:
start_date: '-0049-01-10'  // Assumes Gregorian

// Enhanced:
start_date: '-0049-01-10',
date_calendar: 'julian',  // or 'gregorian', 'roman', 'egyptian'
original_date: 'Ides of January, AUC 705',  // Original source format
date_converted: true
```

**Value:** ⭐⭐ **MEDIUM** - Important for historical accuracy

---

#### Time Precision Standards

**What it is:**
- XSD dateTime precision levels
- ISO 8601 allows varying precision (year, month, day, time)

**Current Coverage:**
- ✅ We have `date_precision` property
- ⚠️ Could be more standardized

**Value:** ⭐ **LOW** - Already partially covered

---

### 6. **Cultural & Religious Standards** ⚠️ LOW-MEDIUM PRIORITY

#### Religious Calendar Standards

**What it is:**
- Liturgical calendars, religious eras, feast days
- Relevant for religious events, festivals, observances

**Integration:**
- Add `religious_calendar_date` for events tied to religious calendars
- Most relevant for religious events

**Value:** ⭐ **LOW** - Specialized use case

---

#### Cultural Period Classifications

**What it is:**
- Art history periods (Renaissance, Baroque, etc.)
- Archaeological periods (Bronze Age, Iron Age, etc.)
- We have `Temporal/time_periods.csv` - good start!

**Current Coverage:**
- ✅ We have historical period taxonomy
- ⚠️ Could align with art history, archaeological period standards

**Value:** ⭐⭐ **MEDIUM** - Useful for cultural/archaeological integration

---

### 7. **Work & Intellectual Property Standards** ⚠️ MEDIUM PRIORITY

#### DOI (Digital Object Identifier)

**What it is:**
- Persistent identifier for digital publications
- Used for modern scholarly works

**Why We Need It:**
- ✅ **Modern sources**: Link to modern historical scholarship
- ✅ **Persistent links**: Stable URLs for academic publications
- ✅ **Bibliographic integration**: Works with academic databases

**Integration:**
- Add `doi` property to Work entities (modern scholarly works)
- Not relevant for ancient works

**Value:** ⭐⭐ **MEDIUM** - Important for modern source attribution

---

#### ISBN/ISSN

**What it is:**
- ISBN (books), ISSN (journals/serials)
- Standard identifiers for publications

**Why We Need It:**
- ✅ **Bibliographic data**: Standard book/journal identification
- ✅ **Library integration**: Links to library catalogs
- ✅ **Work identification**: Unique identifiers for publications

**Integration:**
- Add `isbn` (for books), `issn` (for journals) to Work entities

**Value:** ⭐⭐ **MEDIUM** - Useful for bibliographic integration

---

### 8. **Geographic Standards (Additional)** ✅ PARTIALLY COVERED

#### GeoNames

**What it is:**
- Geographic database with place names worldwide
- Includes historical places, variant names

**Why We Might Need It:**
- ✅ **Place name variants**: Multiple names for same place
- ✅ **Hierarchical structure**: Country → Region → City
- ⚠️ **Pleiades is better** for ancient/classical geography

**Integration:**
- Could add `geonames_id` alongside `pleiades_id`
- Pleiades is more specialized for our use case

**Value:** ⭐ **LOW** - Pleiades is sufficient for ancient history

---

#### Getty Thesaurus of Geographic Names (TGN)

**What it is:**
- Art/cultural heritage geographic database
- Used by museums, art institutions

**Why We Might Need It:**
- ✅ **Museum integration**: Links to museum collection databases
- ✅ **Art historical places**: Places relevant to art/culture
- ⚠️ **Overlap with Pleiades**: Pleiades is more comprehensive for ancient history

**Integration:**
- Add `tgn_id` for places with art historical significance
- Complement to Pleiades

**Value:** ⭐ **LOW-MEDIUM** - Useful for museum integration

---

## Priority Recommendations

### 🔴 HIGH PRIORITY (Implement Soon)

1. **VIAF (Authority Control)**
   - Critical for person disambiguation
   - Name variant resolution
   - Cross-library linking
   - **Action**: Add `viaf_id`, `viaf_link` to Person entities

2. **CIDOC-CRM Alignment**
   - Critical for museum/archival integration
   - Event-centric model alignment
   - Cultural heritage data standard
   - **Action**: Create mapping layer, add CIDOC-CRM class properties

3. **ISO 639 Language Codes**
   - Important for multilingual sources
   - Ancient language identification
   - **Action**: Add `language` properties to Works, relationships

---

### 🟡 MEDIUM PRIORITY (Consider for Future)

4. **Calendar Systems**
   - Historical accuracy (Julian, Roman calendars)
   - Date conversion metadata
   - **Action**: Add `date_calendar`, `original_date` properties

5. **ISNI**
   - Cross-domain identity for persons
   - Work attribution
   - **Action**: Add `isni` to Person entities

6. **EAC-CPF**
   - Archival authority records
   - Biographical data
   - **Action**: Add `eac_cpf_id`, import biographical data

7. **DOI, ISBN, ISSN**
   - Modern source attribution
   - Bibliographic integration
   - **Action**: Add to Work entities

---

### 🟢 LOW PRIORITY (Nice to Have)

8. **ORCID** - Only for modern scholars
9. **EAD** - Collection-level, less relevant
10. **PROV** - Advanced provenance tracking
11. **Getty TGN** - Overlap with Pleiades
12. **Citation Styles** - Can be generated from structured data

---

## Implementation Strategy

### Phase 1: Authority Control (Immediate)

```cypher
// Add to Person entities:
(person:Human {
  viaf_id: '78287861',
  viaf_link: 'http://viaf.org/viaf/78287861',
  isni: '0000 0001 2103 499X'  // Optional
})
```

### Phase 2: CIDOC-CRM Mapping (Short-term)

```cypher
// Add CIDOC-CRM alignment:
(event:Event {
  cidoc_crm_class: 'E5_Event',
  cidoc_crm_aligned: true
})
```

### Phase 3: Language & Calendar (Medium-term)

```cypher
// Add language codes:
(work:Book {
  language: 'la',  // ISO 639-1
  language_iso639_2: 'lat'
})

// Add calendar system:
(event:Event {
  start_date: '-0049-01-10',
  date_calendar: 'julian',
  original_date: 'Ides of January, AUC 705'
})
```

---

## Summary

### Currently Missing High-Value Schemas:

1. ✅ **VIAF** - Authority control for persons (HIGH)
2. ✅ **CIDOC-CRM** - Cultural heritage/museum integration (HIGH)
3. ✅ **ISO 639** - Language codes for multilingual sources (HIGH)
4. ⚠️ **Calendar Systems** - Historical calendar metadata (MEDIUM)
5. ⚠️ **ISNI** - Cross-domain identity (MEDIUM)
6. ⚠️ **DOI/ISBN/ISSN** - Bibliographic identifiers (MEDIUM)

### Well-Covered Areas:

- ✅ Entities (Wikidata QIDs)
- ✅ Relationships (Wikidata properties)
- ✅ Temporal (ISO 8601)
- ✅ Geographic (Pleiades)
- ✅ Subject Classification (FAST/LCC/LCSH/MARC)

**Recommendation:** Prioritize VIAF and CIDOC-CRM alignment for maximum impact.



