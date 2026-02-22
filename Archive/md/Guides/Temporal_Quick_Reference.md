# Quick Reference Guide

**Last Updated:** December 11, 2025

---

## 🚀 Common Commands

### Validate Taxonomy
```bash
python temporal/scripts/query_wikidata_periods.py --query validate
```

### Generate Import CSVs
```bash
# Test range (Roman Kingdom to Sulla)
python temporal/scripts/generate_csv_for_import.py --start -753 --end -82

# Full range (3000 BCE to 2025 CE)
python temporal/scripts/generate_csv_for_import.py --full-range
```

### Discover New Periods
```bash
# Find Q11514315 periods from Wikidata
python temporal/scripts/query_dbpedia_periods.py

# Get all curated periods (377)
python temporal/scripts/curate_q11514315_taxonomy.py

# Get core periods only (92)
python temporal/scripts/select_core_periods.py
```

---

## 📊 Current Numbers

| Metric | Count |
|--------|-------|
| **Taxonomy periods** | 13 |
| **Valid Q11514315** | 11 |
| **Invalid (need fix)** | 2 |
| **Year mappings** | 672 |
| **Hierarchy relationships** | 7 |
| **Available Q11514315** | 92 core / 377 total |

---

## 📁 Key Files

### Taxonomy
- `Temporal/time_periods.csv` - Your 13 periods
- `selected_core_periods.csv` - 92 major periods available
- `curated_q11514315_taxonomy.csv` - 377 total periods

### Generated (for Neo4j)
- `year_nodes.csv` - Year backbone
- `period_mappings.csv` - Year → Period links
- `sequential_relationships.csv` - Year → Year chain
- `period_hierarchy.csv` - Period → Period hierarchy

---

## ✅ Validation Status

**11/13 Valid** (84.6%)

**Invalid:**
- Q745799: Islamic Golden Age (type: "golden age")
- Q5308718: Early Modern Period (type: "era")

**Action:** Replace with Q11514315 equivalents

---

## 🔧 Quick Fixes

### Fix Invalid Periods
1. Open `Temporal/time_periods.csv`
2. Find Q11514315 replacements in `selected_core_periods.csv`
3. Replace Q745799 and Q5308718
4. Validate: `python query_wikidata_periods.py --query validate`

### Expand Taxonomy
1. Review `selected_core_periods.csv` (92 periods)
2. Pick 20-30 relevant periods
3. Add to `Temporal/time_periods.csv`
4. Regenerate: `python generate_csv_for_import.py --full-range`

---

## 📐 Graph Structure

```
Year (-753)
  -[:WITHIN_TIMESPAN]->
Period (Roman Kingdom, Q201038)
  -[:SUB_PERIOD_OF]->
Period (Ancient History, Q41493)
  -[:INSTANCE_OF]->  (optional)
Class (Q11514315, "historical period")
```

---

## 🎯 Next Steps

1. **Fix 2 invalid periods** → 100% Q11514315 compliance
2. **Expand to ~35 periods** → Better coverage
3. **Generate full range** → -3000 to 2025 (5026 years)
4. **Import to Neo4j** → Use Cypher scripts

---

**For details, see:** `COMPREHENSIVE_SUMMARY.md`

