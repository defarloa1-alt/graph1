# Entity Property Extensions

## Overview

Additional properties to enhance entity richness and linking to external resources.

---

## 1. Place Extensions

### Geographic Data

**Properties to add:**
- `geo_coordinates`: Geographic coordinates (lat/long)
- `pleiades_id`: Pleiades gazetteer ID
- `pleiades_link`: URL to Pleiades entry
- `google_earth_link`: KML/KMZ link or coordinates for Google Earth
- `geo_json`: GeoJSON geometry data (optional, for complex shapes)

**Format:**
```json
{
  "geo_coordinates": {
    "latitude": 41.9028,
    "longitude": 12.4964,
    "altitude": null,
    "precision": "city"
  },
  "pleiades_id": "423025",
  "pleiades_link": "https://pleiades.stoa.org/places/423025",
  "google_earth_link": "https://earth.google.com/web/@41.9028,12.4964,0a,0y,0h,0t,0r/data=..."
}
```

---

## 2. Temporal Extensions

### Start and End Dates

**Properties to add:**
- `start_date`: Start date/time (already have, but ensure format)
- `end_date`: End date/time (NEW)
- `date_precision`: Level of precision (year, month, day, approximate)
- `date_range`: Time period range
- `temporal_uncertainty`: If dates are uncertain

**Format:**
```json
{
  "start_date": "-509-01-01",  // ISO 8601 with negative years for BC
  "end_date": "-27-01-01",     // End of Republic, start of Empire
  "date_precision": "year",
  "temporal_uncertainty": false
}
```

---

## 3. Backbone Alignment Extensions

### FAST, LCC, MARC Data

**Properties to add:**
- `backbone_fast`: FAST (Faceted Application of Subject Terminology) ID
- `backbone_lcc`: Library of Congress Classification code
- `backbone_lcsh`: Library of Congress Subject Headings
- `backbone_marc`: MARC authority record ID
- `backbone_alignment`: Combined backbone alignment data

**Format:**
```json
{
  "backbone_fast": "fst01411640",  // FAST ID
  "backbone_lcc": "DG241-269",     // LCC classification
  "backbone_lcsh": ["Rome--History--Republic, 510-30 B.C."],
  "backbone_marc": "sh85115058",   // MARC authority ID
  "backbone_alignment": {
    "fast_id": "fst01411640",
    "lcc_code": "DG241-269",
    "lcsh_terms": ["Rome--History--Republic, 510-30 B.C."],
    "marc_id": "sh85115058"
  }
}
```

---

## 4. Person Extensions

### Image and Media

**Properties to add:**
- `image_url`: URL to portrait/image
- `image_source`: Source/attribution for image
- `image_license`: License information
- `wikimedia_image`: Wikimedia Commons file name

**Format:**
```json
{
  "image_url": "https://upload.wikimedia.org/wikipedia/commons/...",
  "image_source": "Wikimedia Commons",
  "image_license": "Public Domain",
  "wikimedia_image": "File:Brutus.jpg"
}
```

### Related Works

**Properties to add:**
- `related_fiction`: List of fictional works featuring this person
- `related_art`: List of artworks depicting this person
- `related_nonfiction`: List of non-fiction works about this person
- `related_works`: Combined list with metadata

**Format:**
```json
{
  "related_fiction": [
    {
      "title": "Julius Caesar",
      "author": "William Shakespeare",
      "work_type": "Play",
      "wikidata_qid": "Q104832"
    }
  ],
  "related_art": [
    {
      "title": "Brutus",
      "artist": "Michelangelo",
      "work_type": "Sculpture",
      "wikidata_qid": "Q..."
    }
  ],
  "related_nonfiction": [
    {
      "title": "The Life of Brutus",
      "author": "Plutarch",
      "work_type": "Biography",
      "wikidata_qid": "Q..."
    }
  ],
  "online_text_available": true,
  "online_text_sources": ["Project Gutenberg", "Internet Archive"]
}
```

### Online Text Availability

**Properties to add:**
- `online_text_available`: Boolean - whether online text exists
- `online_text_sources`: List of sources (Project Gutenberg, Internet Archive, etc.)
- `online_text_urls`: Direct URLs to online texts
- `text_language`: Language of available texts

**Format:**
```json
{
  "online_text_available": true,
  "online_text_sources": [
    {
      "source": "Project Gutenberg",
      "url": "https://www.gutenberg.org/...",
      "format": "HTML",
      "language": "en"
    },
    {
      "source": "Internet Archive",
      "url": "https://archive.org/...",
      "format": "PDF",
      "language": "en"
    }
  ]
}
```

---

## 5. Updated Entity Structure

### Complete Entity Definition (Extended)

An entity $v$ is now a tuple:

$$v = (id, unique\_id, label, type, qid, P, metadata, extensions)$$

Where $extensions$ includes:

**For Places:**
$$extensions_{place} = \{geo\_coordinates, pleiades\_id, pleiades\_link, google\_earth\_link, geo\_json\}$$

**For Temporal Entities:**
$$extensions_{temporal} = \{start\_date, end\_date, date\_precision, temporal\_uncertainty\}$$

**For All Entities:**
$$extensions_{backbone} = \{backbone\_fast, backbone\_lcc, backbone\_lcsh, backbone\_marc\}$$

**For People:**
$$extensions_{person} = \{image\_url, related\_fiction, related\_art, related\_nonfiction, online\_text\_available, online\_text\_sources\}$$

---

## 6. Neo4j Property Structure

### Place Node (Extended)

```cypher
CREATE (place:Place {
  id: 'Q220',
  unique_id: 'Q220_CITY_ROME',
  label: 'Rome',
  type: 'City',
  qid: 'Q220',
  
  // Geographic extensions
  geo_coordinates: {latitude: 41.9028, longitude: 12.4964},
  pleiades_id: '423025',
  pleiades_link: 'https://pleiades.stoa.org/places/423025',
  google_earth_link: 'https://earth.google.com/web/@41.9028,12.4964...',
  
  // Backbone alignment
  backbone_fast: 'fst01411640',
  backbone_lcc: 'DG241-269',
  backbone_lcsh: ['Rome--History'],
  backbone_marc: 'sh85115058'
})
```

### Person Node (Extended)

```cypher
CREATE (person:Human {
  id: 'Q156138',
  unique_id: 'Q156138_HUM_BRUTUS',
  label: 'Lucius Junius Brutus',
  type: 'Human',
  qid: 'Q156138',
  
  // Temporal
  start_date: '-509-01-01',
  end_date: null,
  
  // Image
  image_url: 'https://upload.wikimedia.org/wikipedia/commons/...',
  image_source: 'Wikimedia Commons',
  
  // Related works
  related_fiction: [{title: 'Julius Caesar', author: 'Shakespeare', qid: 'Q104832'}],
  related_art: [{title: 'Brutus', artist: 'Michelangelo', qid: 'Q...'}],
  related_nonfiction: [{title: 'Life of Brutus', author: 'Plutarch', qid: 'Q...'}],
  
  // Online text
  online_text_available: true,
  online_text_sources: [
    {source: 'Project Gutenberg', url: '...', format: 'HTML'}
  ],
  
  // Backbone alignment
  backbone_fast: 'fst...',
  backbone_lcc: '...',
  backbone_lcsh: ['Brutus, Lucius Junius']
})
```

### Event/Organization Node (Extended)

```cypher
CREATE (event:Event {
  id: 'C_OVERTHROW_MONARCHY_509',
  unique_id: 'EVENT_OVERTHROW_MONARCHY_509BC',
  label: 'Overthrow of Roman Monarchy',
  type: 'Revolution',
  
  // Temporal (with end date)
  start_time: '509 BC',
  start_date: '-509-01-01',
  end_date: '-509-12-31',  // NEW: end date
  date_precision: 'year',
  
  // Backbone alignment
  backbone_fast: '...',
  backbone_lcc: '...',
  backbone_lcsh: ['Rome--History--Republic, 510-30 B.C.']
})
```

---

## 7. Property Schema Summary

### Required vs Optional

**Core Properties** (Required):
- `id`, `unique_id`, `label`, `type`, `qid` (if available)

**Extended Properties** (Optional):
- Geographic: Only for Place entities
- Temporal: Only for entities with temporal aspects
- Image/Works: Only for Person entities
- Backbone: Available for all entities (highly recommended)

---

## 8. Implementation Notes

### Pleiades Integration

- Pleiades IDs format: numeric (e.g., "423025")
- Pleiades links: `https://pleiades.stoa.org/places/{id}`
- Can query Pleiades API for coordinates

### Google Earth Links

- Can generate KML/KMZ from coordinates
- Or use Google Earth Web URL format
- Format: `https://earth.google.com/web/@lat,lon,altitude`

### FAST/LCC/MARC

- FAST: Faceted Application of Subject Terminology
- LCC: Library of Congress Classification
- LCSH: Library of Congress Subject Headings  
- MARC: Machine-Readable Cataloging authority records

### Related Works

- Can link to Work entities via relationships
- Or store as embedded lists with metadata
- Recommended: Store as relationships to Work nodes

---

## 9. Example: Complete Extended Entity

```json
{
  "id": "Q156138",
  "unique_id": "Q156138_HUM_BRUTUS",
  "label": "Lucius Junius Brutus",
  "type": "Human",
  "qid": "Q156138",
  
  "properties": {
    "birth_date": null,
    "death_date": "-509-01-01",
    "title": "Consul"
  },
  
  "metadata": {
    "test_case": "monarchy_to_republic",
    "confidence": 0.95
  },
  
  "extensions": {
    "temporal": {
      "start_date": null,
      "end_date": "-509-01-01",
      "date_precision": "year"
    },
    "backbone": {
      "backbone_fast": "fst...",
      "backbone_lcc": "...",
      "backbone_lcsh": ["Brutus, Lucius Junius"],
      "backbone_marc": "..."
    },
    "image": {
      "image_url": "https://...",
      "image_source": "Wikimedia Commons",
      "wikimedia_image": "File:Brutus.jpg"
    },
    "related_works": {
      "related_fiction": [...],
      "related_art": [...],
      "related_nonfiction": [...]
    },
    "online_text": {
      "online_text_available": true,
      "online_text_sources": [...]
    }
  }
}
```

