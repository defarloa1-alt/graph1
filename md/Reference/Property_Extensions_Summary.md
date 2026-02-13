# Property Extensions Summary

## Quick Reference: New Properties to Add

### For Places

```json
{
  "geo_coordinates": {"latitude": 41.9028, "longitude": 12.4964},
  "pleiades_id": "423025",
  "pleiades_link": "https://pleiades.stoa.org/places/423025",
  "google_earth_link": "https://earth.google.com/web/@41.9028,12.4964..."
}
```

### For Temporal Entities (Events, Organizations, etc.)

```json
{
  "start_date": "-509-01-01",
  "end_date": "-27-01-01",  // NEW: End date
  "date_precision": "year",
  "temporal_uncertainty": false
}
```

### For All Entities (Backbone Alignment)

```json
{
  "backbone_fast": "fst01411640",
  "backbone_lcc": "DG241-269",
  "backbone_lcsh": ["Rome--History--Republic, 510-30 B.C."],
  "backbone_marc": "sh85115058"
}
```

### For People

```json
{
  "image_url": "https://...",
  "image_source": "Wikimedia Commons",
  "related_fiction": [{title: "...", author: "...", qid: "..."}],
  "related_art": [{title: "...", artist: "...", qid: "..."}],
  "related_nonfiction": [{title: "...", author: "...", qid: "..."}],
  "online_text_available": true,
  "online_text_sources": [
    {source: "Project Gutenberg", url: "...", format: "HTML"}
  ]
}
```

---

## Implementation Checklist

- [ ] Update entity structure definition
- [ ] Add Pleiades integration (API lookup)
- [ ] Add Google Earth link generation
- [ ] Update temporal properties (start_date + end_date)
- [ ] Add FAST/LCC/MARC lookup/integration
- [ ] Add image property handling for people
- [ ] Add related works structure
- [ ] Add online text source tracking
- [ ] Update Cypher scripts to include extensions
- [ ] Update LLM extraction prompts to capture these properties

