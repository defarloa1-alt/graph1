# Graph Visualization Guide

**Purpose:** Cypher queries to visualize the backbone in Neo4j Browser

---

## 🎯 Quick Start

**Best query to start with:**

```cypher
// Full Chain Visualization
MATCH path = (y:Year)
  -[:WITHIN_TIMESPAN]->(p:Period)
  -[:LOCATED_IN]->(pl:Place)
RETURN path
LIMIT 20;
```

**Paste this into Neo4j Browser** and click the play button. You'll see:
- Year nodes (blue)
- Period nodes (green)
- Place nodes (orange)
- WITHIN_TIMESPAN relationships (Year → Period)
- LOCATED_IN relationships (Period → Place)

---

## 📊 Visualization Queries

### 1. Full Chain (Recommended)
```cypher
MATCH path = (y:Year)
  -[:WITHIN_TIMESPAN]->(p:Period)
  -[:LOCATED_IN]->(pl:Place)
RETURN path
LIMIT 20;
```
**Shows:** Complete Year → Period → Place chain

### 2. Timeline View
```cypher
MATCH path = (y:Year)
  -[:WITHIN_TIMESPAN]->(p:Period)
  -[:LOCATED_IN]->(pl:Place)
WHERE y.year_value IN [-753, -509, -27, 476, 1000, 1500, 1800]
RETURN path;
```
**Shows:** Backbone for specific historical years

### 3. Roman Periods
```cypher
MATCH path = (y:Year)
  -[:WITHIN_TIMESPAN]->(p:Period)
  -[:LOCATED_IN]->(pl:Place)
WHERE p.qid IN ['Q202686', 'Q17167', 'Q2277']
RETURN path
LIMIT 50;
```
**Shows:** Roman Kingdom → Republic → Empire with places

### 4. Feature-Place Hierarchy
```cypher
MATCH path = (f:Place)
  -[r:LOCATED_IN]->(pl:Place)
WHERE r.feature_to_place = true
RETURN path;
```
**Shows:** Rivers, mountains, islands → their containing places

### 5. Period-Place Network
```cypher
MATCH path = (p:Period)
  -[:LOCATED_IN]->(pl:Place)
RETURN path;
```
**Shows:** All period-place relationships (geographic coverage)

### 6. Year Sequence
```cypher
MATCH 
  seq = (y1:Year)-[:FOLLOWED_BY]->(y2:Year),
  period1 = (y1)-[:WITHIN_TIMESPAN]->(p1:Period),
  period2 = (y2)-[:WITHIN_TIMESPAN]->(p2:Period)
WHERE y1.year_value IN [-753, -509, -27, 476]
RETURN seq, period1, period2;
```
**Shows:** Sequential years with their periods

---

## 🎨 Neo4j Browser Tips

1. **Click nodes** to see properties
2. **Hover over relationships** to see relationship types
3. **Drag nodes** to rearrange the graph
4. **Use the slider** to adjust node size
5. **Click node labels** to expand/collapse

---

## 🔍 If No Results

If you get no results, check:

1. **Place nodes exist:**
   ```cypher
   MATCH (pl:Place) RETURN count(pl);
   ```

2. **Period-Place links exist:**
   ```cypher
   MATCH (p:Period)-[:LOCATED_IN]->(pl:Place) RETURN count(*);
   ```

3. **Year-Period links exist:**
   ```cypher
   MATCH (y:Year)-[:WITHIN_TIMESPAN]->(p:Period) RETURN count(*);
   ```

---

**Files:**
- `QUICK_GRAPH_VISUALIZATION.cypher` - Quick start queries
- `VISUALIZE_BACKBONE_GRAPH.cypher` - Comprehensive visualization queries


