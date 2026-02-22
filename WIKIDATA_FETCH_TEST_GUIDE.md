# Wikidata Full Fetch - Test Guide

**Purpose:** Fetch **ALL** data from a Wikidata QID including properties, labels, values, and external identifiers.

---

## 🎯 What This Does

Given a QID (e.g., `Q17167` for Roman Republic), this fetches:

✅ **Labels** - All languages (English, French, German, etc.)  
✅ **Descriptions** - All languages  
✅ **Aliases** - All alternate names in all languages  
✅ **Properties** - ALL Wikidata properties with their values  
✅ **External Identifiers** - VIAF, LCNAF, GND, FAST, etc.  
✅ **Sitelinks** - Wikipedia articles in all languages  
✅ **Qualifiers** - Additional context for statements  
✅ **References** - Citations for statements

---

## 🚀 Quick Test (Command Line)

### Step 1: Test the Fetcher

```bash
# Test with Roman Republic (Q17167)
python test_wikidata_fetch.py

# Test with another QID
python test_wikidata_fetch.py Q1048

# Test with Julius Caesar
python test_wikidata_fetch.py Q1048
```

**Expected Output:**
```
================================================================================
FETCHING COMPLETE DATA FOR: Q17167
================================================================================

Fetching from: https://www.wikidata.org/wiki/Special:EntityData/Q17167.json
Extracting labels...
  Found 142 labels
Extracting descriptions...
  Found 128 descriptions
Extracting aliases...
  Found 87 aliases across 34 languages
Extracting claims/properties...
  Found 45 properties
  Found 8 external identifier types
Extracting sitelinks...
  Found 156 sitelinks

================================================================================
FETCH SUMMARY FOR: Q17167
================================================================================

📊 STATISTICS:
  Labels:              142 languages
  Descriptions:        128 languages
  Aliases:             87 total
  Properties:          45 unique
  Total Statements:    156
  External IDs:        8 types
  Sitelinks:           156 (Wikipedia articles)

🏷️  MAIN LABEL (English):
  Roman Republic

📝 DESCRIPTION (English):
  period in ancient Roman civilization (509 BC–27 BC)

🔗 EXTERNAL IDENTIFIERS:
  P214: 240572050
  P227: 4076778-2
  P1566: 11880931
  P2163: 1204885

🌐 WIKIPEDIA ARTICLES (first 5):
  enwiki: Roman Republic
  frwiki: République romaine
  dewiki: Römische Republik
  eswiki: República romana
  itwiki: Repubblica romana

💾 Saved to: output/wikidata/Q17167_20260220_123456.json
```

---

## 🎨 Gradio UI Test

### Step 2: Launch the Web Interface

```bash
# Install Gradio if needed
pip install gradio

# Launch UI
python scripts/ui/test_wikidata_fetch_ui.py
```

**Opens at:** http://localhost:7860

### Using the UI:

1. **Enter a QID** in the text box (e.g., `Q17167`)
2. **Click "Fetch Complete Data"**
3. **View the summary** (labels, descriptions, external IDs)
4. **Check the JSON output** (complete raw data)
5. **Get the file path** where JSON was saved

---

## 📋 Example QIDs to Test

| QID | Entity | Type |
|-----|--------|------|
| **Q17167** | Roman Republic | Historical period |
| **Q1048** | Julius Caesar | Person |
| **Q1747689** | Ancient Rome | Civilization |
| **Q11768** | Ancient Greece | Civilization |
| **Q842606** | Second Punic War | Event |
| **Q5916** | Hannibal | Person |
| **Q220** | Rome | City |
| **Q1524** | Athens | City |

---

## 📦 Output Structure

The fetched data is structured as:

```json
{
  "qid": "Q17167",
  "fetch_timestamp": "2026-02-20T12:34:56.789Z",
  
  "labels": {
    "en": "Roman Republic",
    "fr": "République romaine",
    "de": "Römische Republik",
    ...
  },
  
  "descriptions": {
    "en": "period in ancient Roman civilization (509 BC–27 BC)",
    ...
  },
  
  "aliases": {
    "en": ["Roman state", "res publica Romana", ...],
    ...
  },
  
  "claims": {
    "P31": [  // instance of
      {
        "type": "wikibase-item",
        "value": "Q15304597",
        "rank": "normal",
        "qualifiers": {},
        "references": []
      }
    ],
    "P214": [  // VIAF ID
      {
        "type": "external-id",
        "value": "240572050",
        ...
      }
    ],
    ...
  },
  
  "external_identifiers": {
    "P214": ["240572050"],  // VIAF
    "P227": ["4076778-2"],  // GND
    "P2163": ["1204885"],   // FAST
    ...
  },
  
  "sitelinks": {
    "enwiki": {
      "title": "Roman Republic",
      "url": "https://en.wikipedia.org/wiki/Roman_Republic"
    },
    ...
  },
  
  "statistics": {
    "total_labels": 142,
    "total_descriptions": 128,
    "total_aliases": 87,
    "total_properties": 45,
    "total_external_ids": 8,
    "total_sitelinks": 156,
    "total_statements": 156
  }
}
```

---

## 🔍 What External Identifiers Are Fetched?

The fetcher automatically extracts these external identifier properties:

| Property | External Authority | Example |
|----------|-------------------|---------|
| **P214** | VIAF ID | 240572050 |
| **P227** | GND (Germany) | 4076778-2 |
| **P244** | LCNAF (Library of Congress) | n80126865 |
| **P268** | BnF ID (France) | 119326743 |
| **P1566** | GeoNames ID | 11880931 |
| **P2163** | FAST ID | 1204885 |
| **P691** | NKCR ID (Czech) | xx0243831 |
| **P950** | BNE ID (Spain) | XX1790345 |
| **P1015** | NORAF ID (Norway) | 90633986 |

*...and many more!*

---

## 📂 Files Created

After testing, you'll have:

```
Graph1/
├── scripts/agents/
│   └── wikidata_full_fetch.py          (Main fetcher class)
├── scripts/ui/
│   └── test_wikidata_fetch_ui.py       (Gradio UI)
├── test_wikidata_fetch.py              (Quick CLI test)
├── output/wikidata/
│   └── Q17167_20260220_123456.json     (Saved JSON data)
└── WIKIDATA_FETCH_TEST_GUIDE.md        (This file)
```

---

## ✅ Verify It's Working

### Expected Behavior:

1. **Command line test** completes without errors
2. **JSON file** is created in `output/wikidata/`
3. **Statistics** show:
   - 100+ labels (for popular entities)
   - 50+ descriptions
   - 20+ properties
   - Multiple external IDs
   - Many Wikipedia sitelinks

### If It Fails:

**Error: "Connection refused"**
- Check internet connection
- Wikidata might be temporarily down

**Error: "QID not found"**
- Verify QID is correct (starts with Q)
- Try a different QID

**Error: "Module not found"**
- Install: `pip install requests`

---

## 🔧 Code Overview

### `WikidataFullFetcher` Class

```python
from scripts.agents.wikidata_full_fetch import WikidataFullFetcher

fetcher = WikidataFullFetcher()

# Fetch complete data
data = fetcher.fetch_entity_full('Q17167')

# Print summary
fetcher.print_summary(data)

# Save to JSON
filepath = fetcher.save_to_json(data)

# Get property labels
prop_labels = fetcher.get_property_labels(['P31', 'P279', 'P361'])
```

### Key Methods:

- `fetch_entity_full(qid)` - Fetch all data for a QID
- `print_summary(data)` - Print formatted summary
- `save_to_json(data, filename)` - Save to JSON file
- `get_property_labels(prop_ids)` - Get English labels for property IDs

---

## 🎯 Next Steps

Once this test works, we'll:

1. ✅ **DONE** - Fetch complete QID data
2. **TODO** - Clear SubjectConcepts in Aura
3. **TODO** - Build domain from QID properties
4. **TODO** - Create SubjectConcepts from property values
5. **TODO** - Link to facets and agents
6. **TODO** - Full workflow in Gradio UI

---

## 📊 Performance Notes

**Fetch Time:**
- Simple entity (< 10 properties): ~1 second
- Medium entity (10-50 properties): ~2-3 seconds
- Complex entity (> 100 properties): ~5-10 seconds

**Data Size:**
- Small: ~50 KB JSON
- Medium: ~200 KB JSON
- Large: ~1 MB+ JSON (rare)

**Rate Limits:**
- Wikidata allows reasonable use
- For bulk operations, add delays between requests

---

## 🆘 Support

**Test not working?**
1. Check internet connection
2. Verify Wikidata is accessible: https://www.wikidata.org
3. Try different QID
4. Check error message details

**Questions?**
- See code comments in `wikidata_full_fetch.py`
- Check example output in `output/wikidata/`

---

**Status:** ✅ Ready to Test  
**Date:** February 20, 2026  
**Version:** 1.0
