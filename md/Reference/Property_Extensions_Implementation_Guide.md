# Property Extensions Implementation Guide

## Summary of Additions

This document outlines the implementation of new property extensions for the Chrystallum Core Model.

---

## 1. Place Extensions

### Properties Added
- `geo_coordinates`: Object with `{latitude, longitude, altitude, precision}`
- `pleiades_id`: String (numeric ID from Pleiades gazetteer)
- `pleiades_link`: URL to Pleiades entry
- `google_earth_link`: URL or coordinates for Google Earth

### Example
```cypher
CREATE (place:Place {
  geo_coordinates: {latitude: 41.9028, longitude: 12.4964, precision: 'city'},
  pleiades_id: '423025',
  pleiades_link: 'https://pleiades.stoa.org/places/423025',
  google_earth_link: 'https://earth.google.com/web/@41.9028,12.4964...'
})
```

---

## 2. Temporal Extensions

### Properties Added
- `end_date`: End date/time (complement to existing `start_date`)
- `date_precision`: `year`, `month`, `day`, or `approximate`
- `temporal_uncertainty`: Boolean flag

### Example
```cypher
CREATE (event:Event {
  start_date: '-509-01-01',  // ISO 8601 with negative years for BC
  end_date: '-509-12-31',
  date_precision: 'year',
  temporal_uncertainty: false
})
```

---

## 3. Backbone Alignment Extensions

### Properties Added
- `backbone_fast`: FAST (Faceted Application of Subject Terminology) ID
- `backbone_lcc`: Library of Congress Classification code
- `backbone_lcsh`: Array of Library of Congress Subject Headings
- `backbone_marc`: MARC authority record ID

### Example
```cypher
CREATE (entity {
  backbone_fast: 'fst01411640',
  backbone_lcc: 'DG241-269',
  backbone_lcsh: ['Rome--History--Republic, 510-30 B.C.'],
  backbone_marc: 'sh85115058'
})
```

---

## 4. Person Extensions

### Image Properties
- `image_url`: URL to portrait/image
- `image_source`: Source/attribution
- `image_license`: License information
- `wikimedia_image`: Wikimedia Commons file name

### Related Works Properties
- `related_fiction`: Array of fictional works featuring this person
- `related_art`: Array of artworks depicting this person
- `related_nonfiction`: Array of non-fiction works about this person

Each work entry contains:
```json
{
  "title": "Julius Caesar",
  "author": "William Shakespeare",
  "work_type": "Play",
  "qid": "Q104832"
}
```

### Online Text Properties
- `online_text_available`: Boolean
- `online_text_sources`: Array of source objects with:
  - `source`: Name (e.g., "Project Gutenberg")
  - `url`: Direct URL
  - `format`: Format type (HTML, PDF, etc.)
  - `language`: Language code

### Example
```cypher
CREATE (person:Human {
  image_url: 'https://upload.wikimedia.org/...',
  image_source: 'Wikimedia Commons',
  wikimedia_image: 'File:Brutus.jpg',
  
  related_fiction: [
    {title: 'Julius Caesar', author: 'Shakespeare', work_type: 'Play', qid: 'Q104832'}
  ],
  related_art: [
    {title: 'Brutus', artist: 'Michelangelo', work_type: 'Sculpture', qid: 'Q...'}
  ],
  related_nonfiction: [
    {title: 'Life of Brutus', author: 'Plutarch', work_type: 'Biography', qid: 'Q...'}
  ],
  
  online_text_available: true,
  online_text_sources: [
    {source: 'Project Gutenberg', url: '...', format: 'HTML', language: 'en'}
  ]
})
```

---

## 5. Mathematical Formalization

The entity structure is now:

$$v = (id, unique\_id, label, type, qid, P, metadata, extensions)$$

Where `extensions` is conditionally applied based on entity type:
- **Place extensions**: Geographic data, Pleiades, Google Earth
- **Temporal extensions**: Start/end dates, precision
- **Backbone extensions**: FAST, LCC, MARC (all entities)
- **Person extensions**: Image, related works, online text

See `Docs/Mathematical_Data_Structure_Formalization.md` Section 14 for complete formal definition.

---

## 6. Implementation Tasks

### Immediate
- [ ] Update entity CSV schema to include new properties
- [ ] Update LLM extraction prompts to capture these properties
- [ ] Update Cypher template library for queries using new properties
- [ ] Add validation functions for new property formats

### Integration
- [ ] Create Pleiades API lookup function
- [ ] Create Google Earth link generator
- [ ] Integrate FAST/LCC/MARC lookup (Library of Congress APIs)
- [ ] Integrate Wikimedia Commons image lookup
- [ ] Integrate Project Gutenberg/Internet Archive text search

### Testing
- [ ] Test Place node creation with geographic data
- [ ] Test temporal entities with start/end dates
- [ ] Test Person nodes with image and related works
- [ ] Validate backbone alignment data format

---

## 7. Updated Files

1. **`Docs/Entity_Property_Extensions.md`**: Complete documentation of all extensions
2. **`Docs/Mathematical_Data_Structure_Formalization.md`**: Updated with Section 14 formalizing extensions
3. **`test_monarchy_to_republic_simplified.cypher`**: Updated examples with new properties
4. **`Docs/Property_Extensions_Summary.md`**: Quick reference summary

---

## 8. Next Steps

1. Review the extension documentation
2. Update entity schema CSVs if needed
3. Update LangGraph extraction prompts to include these properties
4. Create integration functions for external data sources (Pleiades, LOC, etc.)
5. Test with real data from Wikipedia/historical sources

