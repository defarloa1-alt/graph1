# Neo4j Temporal Backbone Import Guide

## Overview

This guide explains how to import the temporal backbone (year nodes and historical periods) into your Neo4j graph database.

---

## Prerequisites

### 1. Neo4j Database
- Neo4j 4.0 or higher installed and running
- Access credentials (username/password)
- APOC plugin installed (recommended for batch operations)

### 2. Python Dependencies
```bash
pip install neo4j
```

### 3. Files Required
- `Temporal/time_periods.csv` - Period definitions
- `temporal/cypher/import_periods_to_neo4j.cypher` - Cypher script for periods
- `temporal/scripts/import_year_nodes_to_neo4j.py` - Python script for year nodes
- `temporal/scripts/temporal_period_classifier.py` - Period classifier

---

## Import Methods

### Method 1: Manual Cypher Import (Periods Only)

**Step 1: Copy CSV to Neo4j Import Directory**

Find your Neo4j import directory:
```bash
# Default locations:
# Windows: C:\Users\<YourUser>\.Neo4jDesktop\relate-data\dbmss\<dbms-id>\import
# Mac: ~/Library/Application Support/Neo4j Desktop/Application/relate-data/dbmss/<dbms-id>/import
# Linux: ~/.config/Neo4j Desktop/Application/relate-data/dbmss/<dbms-id>/import
```

Copy the CSV:
```bash
cp Temporal/time_periods.csv <neo4j-import-directory>/time_periods.csv
```

**Step 2: Run Cypher Script in Neo4j Browser**

Open Neo4j Browser and run:
```cypher
// Load historical periods
LOAD CSV WITH HEADERS FROM 'file:///time_periods.csv' AS row
MERGE (period:Concept:Period {
  qid: row.QID,
  unique_id: row.QID + '_CONCEPT_' + toUpper(replace(row.Period, ' ', '_'))
})
SET period.label = row.Period,
    period.type = 'Time Period',
    period.type_qid = 'Q186081',
    period.start_year = toInteger(row.Start_Year),
    period.end_year = toInteger(row.End_Year),
    period.region = row.Region,
    period.notes = row.Notes,
    period.temporal_backbone = true
RETURN period.label, period.qid, period.start_year, period.end_year;
```

Or run the complete script:
```bash
cat temporal/cypher/import_periods_to_neo4j.cypher | cypher-shell -u neo4j -p <password>
```

---

### Method 2: Python Script (Full Temporal Backbone)

This method creates:
1. Historical period nodes
2. Year nodes (one per year)
3. Sequential relationships (FOLLOWED_BY, PRECEDED_BY)
4. Period mappings (DURING, PART_OF)

#### Quick Start Examples

**Example 1: Test Mode (Kingdom to Sulla period)**
```bash
cd temporal
python scripts/import_year_nodes_to_neo4j.py \
  --start -753 \
  --end -82 \
  --test
```

**Example 2: Generate Cypher File**
```bash
cd temporal
python scripts/import_year_nodes_to_neo4j.py \
  --start -753 \
  --end -82 \
  --output temporal_backbone_753_82_bce.cypher
```

**Example 3: Import to Local Neo4j**
```bash
cd temporal
python scripts/import_year_nodes_to_neo4j.py \
  --start -753 \
  --end -82 \
  --import \
  --uri bolt://localhost:7687 \
  --user neo4j \
  --password your_password
```

**Example 4: Full Range Import (5026 years)**
```bash
cd temporal
python scripts/import_year_nodes_to_neo4j.py \
  --full-range \
  --import \
  --uri bolt://localhost:7687 \
  --user neo4j \
  --password your_password
```

**Example 5: Incremental Import (by century)**
```bash
cd temporal
# Century 1: 1st century BCE
python scripts/import_year_nodes_to_neo4j.py --start -100 --end -1 --import --password your_password

# Century 2: 1st century CE
python scripts/import_year_nodes_to_neo4j.py --start 1 --end 100 --import --password your_password
```

#### Command Line Options

```
--start YEAR          Start year (negative for BCE, e.g., -753)
--end YEAR            End year (negative for BCE, e.g., -82)
--full-range          Generate full range from -3000 to 2025
--test                Test mode: show samples without importing
--import              Import directly to Neo4j
--uri URI             Neo4j connection URI (default: bolt://localhost:7687)
--user USER           Neo4j username (default: neo4j)
--password PASSWORD   Neo4j password (default: neo4j)
--output FILE         Save Cypher to file instead of importing
```

---

## Import Process Details

### What Gets Created

#### 1. Period Nodes
```cypher
(:Concept:Period {
  qid: 'Q17193',
  unique_id: 'Q17193_CONCEPT_ROMAN_REPUBLIC',
  label: 'Roman Republic',
  type: 'Time Period',
  type_qid: 'Q186081',
  start_year: -509,
  end_year: -27,
  region: 'Italy',
  notes: 'Roman republican period',
  iso8601_start: '-0509-01-01',
  iso8601_end: '-0027-12-31',
  temporal_backbone: true
})
```

#### 2. Year Nodes
```cypher
(:Concept:Year {
  id: 'year_-753',
  unique_id: 'YEAR_-753',
  label: '753 BCE',
  type: 'Time Period',
  type_qid: 'Q186081',
  year_value: -753,
  iso8601_start: '-0753-01-01',
  iso8601_end: '-0753-12-31',
  temporal_backbone: true
})
```

#### 3. Sequential Relationships
```cypher
// Forward
(:Year {year_value: -753})-[:FOLLOWED_BY {
  temporal_sequence: 'chronological',
  temporal_backbone: true
}]->(:Year {year_value: -752})

// Backward
(:Year {year_value: -752})-[:PRECEDED_BY {
  temporal_sequence: 'chronological',
  temporal_backbone: true
}]->(:Year {year_value: -753})
```

#### 4. Period Mappings
```cypher
// Primary period
(:Year {year_value: -753})-[:DURING {
  relationship_type: 'temporal_classification',
  classification_type: 'primary_geographic',
  region: 'Italy',
  classification_source: 'Temporal/time_periods.csv',
  temporal_backbone: true
}]->(:Period {qid: 'Q17167'})  // Roman Kingdom

// Coincident period
(:Year {year_value: -753})-[:PART_OF {
  relationship_type: 'temporal_classification',
  classification_type: 'coincident_geographic',
  region: 'Global',
  classification_source: 'Temporal/time_periods.csv',
  temporal_backbone: true
}]->(:Period {qid: 'Q41493'})  // Ancient History
```

---

## Verification Queries

### After Import, Run These Queries

#### 1. Count Nodes
```cypher
// Count periods
MATCH (p:Period)
RETURN count(p) as total_periods;

// Count years
MATCH (y:Year)
RETURN count(y) as total_years;
```

#### 2. Verify Sequential Chain
```cypher
// Check sequential relationships exist
MATCH (y1:Year {year_value: -753})-[:FOLLOWED_BY*10]->(y2:Year)
RETURN y1.label, y2.label, y2.year_value;
```

#### 3. Verify Period Mappings
```cypher
// Years in Roman Republic
MATCH (y:Year)-[:DURING]->(p:Period {qid: 'Q17193'})
RETURN count(y) as years_in_roman_republic;

// Expected: 482 years (-509 to -27)
```

#### 4. Find Overlapping Periods
```cypher
MATCH (p1:Period)-[r:OVERLAPS_WITH]-(p2:Period)
RETURN p1.label, p2.label, 
       r.overlap_start, r.overlap_end,
       (r.overlap_end - r.overlap_start) as overlap_years;
```

#### 5. Test Year Classification
```cypher
// What periods does year -100 belong to?
MATCH (y:Year {year_value: -100})-[r:WITHIN_TIMESPAN]->(p:Period)
RETURN y.label, type(r) as relationship, p.label, p.region, r.classification_type;
```

---

## Performance Considerations

### Small Range (< 1000 years)
- Import directly using Python script
- Takes ~1-5 minutes
- Example: Kingdom to Sulla (-753 to -82) = 672 years

### Medium Range (1000-2000 years)
- Use batch import with `--import`
- Takes ~5-15 minutes
- Example: Ancient History complete (-3000 to 650) = 3651 years

### Full Range (5026 years)
- Use `--full-range` option
- Takes ~15-30 minutes
- Creates 5026 year nodes + 10,052 sequential relationships + ~15,000+ period mappings

### Optimization Tips

1. **Create indexes FIRST:**
```cypher
CREATE INDEX year_value IF NOT EXISTS FOR (y:Year) ON (y.year_value);
CREATE INDEX period_qid IF NOT EXISTS FOR (p:Period) ON (p.qid);
```

2. **Use MERGE instead of CREATE** (script does this automatically)

3. **Batch size:** Default is 100 statements per transaction (configurable in code)

4. **Monitor memory:** Large imports may require increasing Neo4j heap size

---

## Troubleshooting

### Error: "Couldn't load the external resource"
**Cause:** CSV file not in Neo4j import directory  
**Solution:** Copy CSV to correct import directory or use `file:///` protocol

### Error: "neo4j driver not installed"
**Cause:** Python neo4j package not installed  
**Solution:** `pip install neo4j`

### Error: "Authentication failed"
**Cause:** Incorrect Neo4j credentials  
**Solution:** Verify username/password with `cypher-shell` or Neo4j Browser

### Slow Import
**Cause:** Too many nodes/relationships without indexes  
**Solution:** Create indexes before importing:
```cypher
CREATE INDEX year_value IF NOT EXISTS FOR (y:Year) ON (y.year_value);
CREATE INDEX period_qid IF NOT EXISTS FOR (p:Period) ON (p.qid);
```

### Duplicate Nodes
**Cause:** Running import script multiple times  
**Solution:** Script uses MERGE, so duplicates shouldn't occur. If they do, delete and re-import:
```cypher
// Delete temporal backbone
MATCH (n {temporal_backbone: true})
DETACH DELETE n;
```

---

## Incremental Import Strategy

For large databases, import in phases:

### Phase 1: Periods Only
```bash
# Run Cypher script
cypher-shell -u neo4j -p password < temporal/cypher/import_periods_to_neo4j.cypher
```

### Phase 2: Test Cases
```bash
cd temporal
# Kingdom to Sulla (672 years)
python scripts/import_year_nodes_to_neo4j.py --start -753 --end -82 --import --password your_password
```

### Phase 3: Expand by Era
```bash
cd temporal
# Ancient History (-3000 to 650)
python scripts/import_year_nodes_to_neo4j.py --start -3000 --end 650 --import --password your_password

# Middle Ages (500 to 1500)
python scripts/import_year_nodes_to_neo4j.py --start 500 --end 1500 --import --password your_password

# Early Modern (1500 to 1800)
python scripts/import_year_nodes_to_neo4j.py --start 1500 --end 1800 --import --password your_password

# Modern (1800 to 2025)
python scripts/import_year_nodes_to_neo4j.py --start 1800 --end 2025 --import --password your_password
```

---

## Query Examples After Import

### Find Events in Period
```cypher
// Link your events to years
MATCH (event:Event)
WHERE event.start_date CONTAINS '-509'
MATCH (year:Year {year_value: -509})
MERGE (event)-[:POINT_IN_TIME]->(year);

// Find events in Roman Republic
MATCH (event:Event)-[:POINT_IN_TIME]->(year:Year)-[:DURING]->(period:Period {qid: 'Q17193'})
RETURN event.label, year.year_value, period.label;
```

### Temporal Range Queries
```cypher
// Find all entities between two years
MATCH path = (start:Year {year_value: -100})-[:FOLLOWED_BY*]->(end:Year {year_value: -50})
WITH nodes(path) as year_nodes
MATCH (entity)-[:POINT_IN_TIME]->(year:Year)
WHERE year IN year_nodes
RETURN entity.label, year.year_value
ORDER BY year.year_value;
```

### Cross-Regional Comparison
```cypher
// What was happening in different regions in year 1400?
MATCH (year:Year {year_value: 1400})-[:WITHIN_TIMESPAN]->(period:Period)
RETURN period.label, period.region
ORDER BY period.region;
```

---

## Next Steps

After importing the temporal backbone:

1. **Link existing entities to years:**
   ```cypher
   MATCH (entity:Entity)
   WHERE entity.start_date IS NOT NULL
   WITH entity, toInteger(substring(entity.start_date, 0, 4)) as year_num
   MATCH (year:Year {year_value: year_num})
   MERGE (entity)-[:POINT_IN_TIME]->(year);
   ```

2. **Classify entities by period:**
   ```cypher
   MATCH (entity)-[:POINT_IN_TIME]->(year:Year)-[:DURING]->(period:Period)
   SET entity.historical_period = period.label,
       entity.historical_period_qid = period.qid;
   ```

3. **Create period-based queries in your application:**
   - See `temporal/docs/Temporal_Comprehensive_Documentation.md` for query patterns
   - Add to `chrystallum_query_tools.py` for programmatic access

---

## References

- **Comprehensive Docs:** `temporal/docs/Temporal_Comprehensive_Documentation.md`
- **Extraction Guides:** `temporal/docs/Temporal_Data_Extraction_Guide.md` and `Geographic_Data_Extraction_Guide.md`
- **Classifier:** `temporal/scripts/temporal_period_classifier.py`
- **Critical Review:** `temporal/docs/Critical_Review.md`
- **Example Queries:** `temporal/cypher/example_queries.cypher`

---

*Last Updated: 2025-01-09*

