# Backlinks Extraction Guide - Q107649491

## What This Does

Extracts all **Wikidata property type classifications** that link to Q107649491 ("type of Wikidata property").

Examples of property types extracted:
- Wikidata property for authority control (Q18614948)
- Wikidata property related to Ancient World (Q56248884) ← **Relevant for Chrystallum!**
- Wikidata property related to politics (Q22984475)
- Wikidata property to identify events (Q24575337)
- And ~500+ more...

## Quick Start

### Step 1: Install Dependencies

```powershell
pip install requests beautifulsoup4 lxml
```

Or use the requirements file:
```powershell
pip install -r scripts/requirements_backlinks.txt
```

### Step 2: Run the Script

```powershell
python extract_q107649491_backlinks.py
```

### Step 3: Check Output

```
CSV/backlinks/Q107649491_property_types_YYYYMMDD_HHMMSS.csv
```

---

## Output Format

**CSV Columns:**
- `qid` - Wikidata QID of the property type
- `label` - Human-readable name
- `description` - Wikidata description

**Example Rows:**
```csv
qid,label,description
Q56248884,"Wikidata property related to the Ancient World","type of Wikidata property"
Q22984475,"Wikidata property related to politics","type of Wikidata property"
Q18614948,"Wikidata property for authority control","type of Wikidata property"
```

---

## What You'll Get

### Statistics Output:
- Total property types found
- Pattern breakdown:
  - Authority Control properties
  - "Related to" properties (by topic)
  - Identifier properties
  - "Items about" properties
- Sample of first 15 property types

### Expected Results:
- **~500-1000 property types** total
- Covers all Wikidata property classification categories
- Organized by domain (sports, geography, authority control, etc.)

---

## Use Cases for Chrystallum

### 1. **Schema Alignment**
Map Wikidata property types to Chrystallum entity types:
```
Q56248884 (Ancient World) → SUBJECTCONCEPT, HISTORICAL_PERIOD
Q24575337 (events) → EVENT
Q18615777 (location) → PLACE
```

### 2. **Federation Scoring**
Identify which property types are relevant for federation:
```
- Authority control properties → High federation value
- "Related to Ancient World" → Core domain match
- Identifier properties → Cross-reference potential
```

### 3. **Agent Routing**
Map property types to facets:
```
Q22984475 (politics) → POLITICAL facet
Q22964288 (military) → MILITARY facet
Q22983697 (religion) → RELIGIOUS facet
```

---

## Customization

### Change Target QID
Edit line 24 in the script:
```python
TARGET_QID = "Q107649491"  # Change to any QID
```

### Change Output Location
Edit line 25:
```python
OUTPUT_DIR = Path("CSV/backlinks")  # Change path
```

### Change Rate Limiting
Edit line 33:
```python
REQUEST_DELAY = 1.0  # Increase to 2.0 for slower scraping
```

### Change Max Results
Edit line 191 in main():
```python
backlinks = get_all_backlinks(TARGET_QID, max_results=10000)  # Increase limit
```

---

## Performance

- **Page scraping:** ~1 second per 500 items
- **API enrichment:** ~1 second per 50 items
- **Total time for 500 items:** ~3-5 minutes
- **Total time for 1000 items:** ~10-15 minutes

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'bs4'"
```powershell
pip install beautifulsoup4
```

### "No backlinks found"
- Check internet connection
- Verify TARGET_QID is correct
- Check if Wikidata is accessible

### "Rate limit exceeded"
Increase REQUEST_DELAY:
```python
REQUEST_DELAY = 2.0  # Slower but safer
```

---

## Next Steps After Extraction

1. **Review CSV** - Understand property type taxonomy
2. **Map to Chrystallum** - Align property types with entity types
3. **Create Lookup Table** - QID → Chrystallum entity type mapping
4. **Use in Federation** - Enhance federation scoring based on property types

---

**Status:** ✅ Ready to run
**Dependencies:** requests, beautifulsoup4, lxml
**Output:** CSV with QID, label, description
