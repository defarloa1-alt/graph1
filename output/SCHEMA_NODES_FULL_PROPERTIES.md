# Schema Nodes — Full Properties (for Architect Ruling)

**Query:** `MATCH (n:Schema) RETURN n`  
**Count:** 9 nodes

---

## Schema 1
```json
{
  "uses_federations": [],
  "required_props": ["year", "label", "entity_id"]
}
```

---

## Schema 2
```json
{
  "uses_federations": ["Pleiades", "Wikidata", "GeoNames"],
  "optional_props": ["qid", "lat", "long", "bbox"],
  "required_props": ["place_id", "pleiades_id"]
}
```

---

## Schema 3
```json
{
  "uses_federations": ["PeriodO", "Wikidata"],
  "optional_props": ["qid", "periodo_id"],
  "required_props": ["period_id", "start_year", "end_year"]
}
```

---

## Schema 4
```json
{
  "uses_federations": ["Wikidata", "VIAF"]
}
```

---

## Schema 5
```json
{
  "uses_federations": ["Wikidata"]
}
```

---

## Schema 6
```json
{
  "uses_federations": ["Wikidata"]
}
```

---

## Schema 7
```json
{
  "uses_federations": ["LCSH", "FAST", "LCC", "Wikidata"]
}
```

---

## Schema 8
```json
{
  "uses_federations": ["WorldCat", "Wikidata"]
}
```

---

## Schema 9
```json
{
  "uses_federations": []
}
```

---

**Note:** Schema nodes have no `name` or `entity_type` property to identify which entity type each defines. Inference from `required_props` and `uses_federations`:
- 1: Year (year, label, entity_id)
- 2: Place (place_id, pleiades_id; Pleiades, Wikidata, GeoNames)
- 3: Period (period_id, start_year, end_year; PeriodO, Wikidata)
- 4: Person (Wikidata, VIAF)
- 5, 6: Work or other (Wikidata only)
- 7: SubjectConcept (LCSH, FAST, LCC, Wikidata)
- 8: Bibliography (WorldCat, Wikidata)
- 9: Unknown (empty federations)
