# Quick Start: Neo4j Temporal Backbone Import

## 🚀 30-Second Start

### Option 1: Test With Sample Data (Kingdom to Sulla)
```bash
# Test mode - see what will be created
cd temporal
python scripts/import_year_nodes_to_neo4j.py --start -753 --end -82 --test

# Import to Neo4j
python scripts/import_year_nodes_to_neo4j.py \
  --start -753 --end -82 \
  --import \
  --password Chrystallum
```

### Option 2: Full Temporal Backbone (5026 years)
```bash
cd temporal
python scripts/import_year_nodes_to_neo4j.py \
  --full-range \
  --import \
  --password your_password
```

---

## 📋 Step-by-Step Guide

### Step 1: Install Dependencies
```bash
pip install neo4j
```

### Step 2: Start Neo4j
Make sure Neo4j is running:
- Desktop: Start database from Neo4j Desktop
- Command line: `neo4j start`

### Step 3: Import Historical Periods
```bash
# Copy CSV to Neo4j import directory
cp Temporal/time_periods.csv ~/.Neo4j/import/

# Run in Neo4j Browser or:
cypher-shell -u neo4j -p your_password < temporal/cypher/import_periods_to_neo4j.cypher
```

### Step 4: Import Year Nodes

**Small test (672 years):**
```bash
cd temporal
python scripts/import_year_nodes_to_neo4j.py \
  --start -753 --end -82 \
  --import \
  --uri bolt://localhost:7687 \
  --user neo4j \
  --password your_password
```

**Or full range (5026 years):**
```bash
cd temporal
python scripts/import_year_nodes_to_neo4j.py \
  --full-range \
  --import \
  --password your_password
```

### Step 5: Verify Import
Open Neo4j Browser and run:
```cypher
// Count nodes
MATCH (p:Period) RETURN count(p) as periods;
MATCH (y:Year) RETURN count(y) as years;

// Visualize sample
MATCH (y:Year {year_value: -753})-[r*1..10]->(n)
RETURN y, r, n
LIMIT 50;
```

---

## 🎯 What Gets Created

### Periods (14 nodes)
- Ancient History (-3000 to 650)
- Roman Kingdom (-753 to -509)
- Roman Republic (-509 to -27)
- Middle Ages (500 to 1500)
- And 10 more...

### Years (depends on range)
- Small test: 672 year nodes (-753 to -82)
- Full range: 5,026 year nodes (-3000 to 2025)

### Relationships
- `FOLLOWED_BY` / `PRECEDED_BY` (sequential chain)
- `WITHIN_TIMESPAN` (year to period - primary period only)
- `OVERLAPS` (periods that overlap)

---

## 📊 Example Queries

### Find years in Roman Republic
```cypher
MATCH (y:Year)-[:WITHIN_TIMESPAN]->(p:Period {label: 'Roman Republic'})
RETURN y.year_value, y.label
ORDER BY y.year_value
LIMIT 10;
```

### Navigate time sequentially
```cypher
// Get 10 years after -753
MATCH (y:Year {year_value: -753})-[:FOLLOWED_BY*1..10]->(next)
RETURN next.year_value, next.label;
```

### Find overlapping periods
```cypher
// What periods include year 500?
MATCH (y:Year {year_value: 500})-[:WITHIN_TIMESPAN]->(p:Period)
RETURN p.label, p.region;
```

---

## 🔧 Common Issues

### "Couldn't load external resource"
**Fix:** Copy CSV to Neo4j import directory:
```bash
# Find import directory
neo4j-admin server console

# Copy CSV
cp Temporal/time_periods.csv <import-dir>/
```

### "neo4j driver not installed"
**Fix:**
```bash
pip install neo4j
```

### "Authentication failed"
**Fix:** Use correct password:
```bash
cd temporal
python scripts/import_year_nodes_to_neo4j.py --password YOUR_ACTUAL_PASSWORD
```

---

## 📚 Next Steps

1. **Link your entities to years:**
   ```cypher
   MATCH (entity:Entity), (year:Year)
   WHERE entity.start_date CONTAINS toString(year.year_value)
   MERGE (entity)-[:POINT_IN_TIME]->(year);
   ```

2. **Classify entities by period:**
   ```cypher
   MATCH (entity)-[:POINT_IN_TIME]->(y:Year)-[:DURING]->(p:Period)
   SET entity.historical_period = p.label,
       entity.historical_period_qid = p.qid;
   ```

3. **Explore advanced queries:**
   - See `temporal/cypher/example_queries.cypher` for 50+ example queries
   - See `temporal/docs/Neo4j_Import_Guide.md` for full documentation

---

## 📖 Full Documentation

- **Import Guide:** `temporal/docs/Neo4j_Import_Guide.md`
- **Example Queries:** `temporal/cypher/example_queries.cypher`
- **Architecture:** `temporal/docs/Temporal_Comprehensive_Documentation.md`
- **Classifier:** `temporal/scripts/temporal_period_classifier.py`

---

## 💡 Tips

1. **Start small:** Test with Kingdom to Sulla range first (-753 to -82)
2. **Create indexes:** Run before large imports for better performance
   ```cypher
   CREATE INDEX year_value IF NOT EXISTS FOR (y:Year) ON (y.year_value);
   CREATE INDEX period_qid IF NOT EXISTS FOR (p:Period) ON (p.qid);
   ```
3. **Incremental import:** Import by era if full range is too large
4. **Monitor progress:** Script shows progress during import

---

*Need help? See `temporal/docs/Neo4j_Import_Guide.md` for troubleshooting*

