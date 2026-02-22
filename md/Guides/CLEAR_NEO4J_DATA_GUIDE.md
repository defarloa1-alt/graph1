# Clear Neo4j Data - Quick Guide

**Date:** December 11, 2025  
**Purpose:** Guide to clearing Neo4j data for fresh imports

---

## ðŸ—‘ï¸ Available Clear Scripts

### 1. Clear Temporal Backbone Data

**Batch File:** `scripts/backbone/temporal/clear_temporal_data.bat`

**What it does:**
- Deletes all Period nodes
- Deletes all Year nodes
- Deletes all temporal relationships
- Cleans up temporal backbone data

**Usage:**
```batch
cd scripts\backbone\temporal
clear_temporal_data.bat
```

**Or with password:**
```batch
clear_temporal_data.bat YourPassword
```

**What gets deleted:**
- All `:Period` nodes
- All `:Year` nodes
- All `PART_OF` relationships
- All `FOLLOWED_BY` relationships
- All period-related relationships

---

### 2. Complete Reimport (Clear + Reimport)

**Batch File:** `scripts/backbone/temporal/reimport_all.bat`

**What it does:**
1. Clears all temporal data
2. Reimports periods
3. Reimports year nodes
4. Recreates all mappings

**Usage:**
```batch
cd scripts\backbone\temporal
reimport_all.bat
```

**Warning:** âš ï¸ This is a complete wipe and reimport!

---

## ðŸŒ Geographic Data

**Note:** There's currently no dedicated clear script for geographic data, but you can:

### Option 1: Clear via Cypher (Neo4j Browser)

```cypher
// Clear all Place nodes and relationships
MATCH (p:Place)
DETACH DELETE p;

// Clear Period-Place links
MATCH (period:Period)-[r:LOCATED_IN]->(place:Place)
DELETE r;
```

### Option 2: Clear All Geographic Data

```cypher
// Clear everything geographic
MATCH (p:Place)
DETACH DELETE p;

// Verify
MATCH (p:Place) RETURN count(p);
// Should return: 0
```

---

## ðŸ”¥ Clear Everything (Nuclear Option)

**To clear ALL backbone data:**

### Step 1: Clear Temporal
```batch
cd scripts\backbone\temporal
clear_temporal_data.bat
```

### Step 2: Clear Geographic (via Cypher)
```cypher
// In Neo4j Browser
MATCH (p:Place) DETACH DELETE p;
```

### Step 3: Clear Relationships
```cypher
// Clear all Period-Place links
MATCH (period:Period)-[r:LOCATED_IN]->()
DELETE r;
```

---

## ðŸ“‹ Quick Reference

| What to Clear | Batch File | Location |
|---------------|------------|----------|
| **Temporal (Periods + Years)** | `clear_temporal_data.bat` | `scripts/backbone/temporal/` |
| **Temporal + Reimport** | `reimport_all.bat` | `scripts/backbone/temporal/` |
| **Geographic (Places)** | Manual Cypher | Neo4j Browser |
| **Period-Place Links** | Manual Cypher | Neo4j Browser |

---

## âš ï¸ Warnings

1. **Backup First:** If you have important data, export it first
2. **Irreversible:** Deletions cannot be undone
3. **Relationships:** Clearing nodes also clears their relationships
4. **Indexes:** Indexes remain but will be empty

---

## âœ… Verification

After clearing, verify in Neo4j Browser:

```cypher
// Check temporal
MATCH (p:Period) RETURN count(p);  // Should be 0
MATCH (y:Year) RETURN count(y);    // Should be 0

// Check geographic
MATCH (p:Place) RETURN count(p);   // Should be 0

// Check relationships
MATCH (period:Period)-[r:LOCATED_IN]->(place:Place)
RETURN count(r);  // Should be 0
```

---

## ðŸš€ After Clearing

Once cleared, you can:

1. **Reimport Temporal:**
   ```batch
   cd scripts\backbone\temporal
   RUN_FULL_IMPORT.bat
   ```

2. **Reimport Geographic:**
   ```batch
   cd scripts\backbone\geographic
   RUN_FULL_GEO_IMPORT.bat
   ```

---

**Last Updated:** December 11, 2025

