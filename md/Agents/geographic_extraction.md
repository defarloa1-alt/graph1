# Geographic Data Extraction: Atomic vs Tokenizable Handling

## Purpose

This document specifies how AI agents should handle geographic data during extraction, addressing:
- **Cultural/temporal naming variations** (Gaul vs France)
- **Atomic identifiers vs natural language** (coordinates, QIDs vs place names)
- **Stability hierarchy** (continents vs political boundaries)

---

## The Core Challenge: Geographic Anachronism

**Problem:** Geographic names and boundaries are **temporal and cultural constructs**:
- What Romans called "Gaul" became "France"
- What Britons called Gaul may differ from Roman usage
- Modern "Istanbul" was "Constantinople" was "Byzantium"
- Colonial America's boundaries differ completely from modern USA

**Solution:** Multi-name place entity model with temporal and cultural context.

---

## Part 1: Natural Language Terms (CAN TOKENIZE)

### ✅ Place Names

**Examples:**
- "Rome", "Gaul", "Constantinople", "The Roman Empire"
- "Colonial America", "The British Isles"
- "Mesopotamia", "The Levant", "Asia Minor"

**Tokenization:**
```python
"Constantinople" → [Const, ant, in, ople]  ✅ OK
"Roman Empire" → [Roman, Empire]  ✅ OK
"The Levant" → [The, Lev, ant]  ✅ OK
```

**LLM Processing:**
- ✅ Can extract from text
- ✅ Understands historical context
- ✅ Can identify in multiple languages
- ✅ Can link to modern equivalents
- ✅ Recognizes cultural variations

---

## Part 3: System Identifiers (MUST BE ATOMIC)

### ❌ Geographic Coordinates

**Format:** Latitude/Longitude (e.g., "41.9028° N, 12.4964° E")

**Problem with Tokenization:**
```python
# ❌ BAD - LLM parsing coordinates:
coords = "41.9028, 12.4964"
tokens = tokenize(coords)  # [41, ., 90, 28, ,, 12, ., 49, 64]
llm.ask(f"What city is at {coords}?")  # Tokenization breaks precision
```

**Correct Handling:**
```python
# ✅ GOOD - Tool-based geocoding:
coords = (41.9028, 12.4964)  # Tuple of floats (atomic numeric values)
location = geocoding_tool.reverse_geocode(coords)  # Tool handles lookup
```

**Storage Format:**
```json
{
  "location": {
    "label": "Rome",                          // ✅ Natural language
    "coordinates": {
      "latitude": 41.9028,                    // ❌ Atomic numeric
      "longitude": 12.4964,                   // ❌ Atomic numeric
      "format": "decimal_degrees",
      "precision": "city_level"
    },
    "qid": "Q220"                             // ❌ Atomic string
  }
}
```

---

### ❌ Wikidata QIDs for Places

**Same as temporal QIDs** - must be atomic strings.

```python
# ❌ BAD:
place_qid = "Q220"  # Rome
llm.ask(f"What place is {place_qid}?")  # Tokenizes to [Q, 220], LLM confused

# ✅ GOOD:
place_qid = "Q220"  # Atomic string
place_data = wikidata_api.get_entity(place_qid)  # Tool lookup
```

---

## Summary

### Natural Language (LLM CAN Tokenize)
- ✅ Place names: "Rome", "Gaul", "Constantinople"
- ✅ Geographic features: "Alps", "Mediterranean Sea", "Tiber River"
- ✅ Political regions: "Roman Republic", "Ottoman Empire"

### System Identifiers (MUST Be Atomic)
- ❌ Coordinates: (41.9028, 12.4964) - atomic numerics
- ❌ Wikidata QIDs: "Q220", "Q38" - atomic strings
- ❌ GeoNames IDs: "3169070" - atomic strings

### Critical Principles
1. ✅ **Multi-name entities** - Same place, multiple names across time/culture
2. ✅ **Temporal validity** - Names and boundaries change over time
3. ✅ **Cultural perspective** - Different cultures use different names
4. ✅ **Stability hierarchy** - Continents stable, political boundaries unstable
5. ❌ **Never let LLM process coordinates or QIDs** - Tool resolution only

---

*For complete documentation, see the full Geographic_Data_Extraction_Guide.md*


