# Dev Instructions: Comprehensive Wikidata Import

**Date:** February 22, 2026  
**Priority:** CRITICAL  
**Purpose:** Fix disconnected graph by importing ALL relationship data from checkpoint

---

## Current Problem

**Database State:**
- Nodes: 2,600 entities
- Edges: 784 relationships (0.30 per entity)
- **Graph is disconnected and unusable**

**Root Cause:**
- `scripts/neo4j/import_relationships.py` has hardcoded whitelist of 19 properties
- Checkpoint contains 3,777 properties
- **Missing: 3,758 properties (99.5% of available data)**

**Impact:**
- Can't see graph structure
- Can't discover multi-hop paths (senator → mollusk)
- Can't validate if SubjectConcept/Facet model works
- Graph looks "junky"

---

## Requirement

**Import ALL entity-to-entity relationships from checkpoint data.**

**No filtering. No whitelist. No guessing at what's important.**

Use **mechanical algorithm** based on Wikidata's own data model to classify claims into three buckets:
1. Attributes (node properties)
2. Simple edges (entity-to-entity)
3. Node candidates (complex, reify to FacetClaim)

---

## The Algorithm (Mechanical Classification)

```python
CIPHER_ELIGIBLE_QUALIFIERS = {"P580", "P582", "P585", "P276", "P1545"}

def classify_wikidata_claim(claim: dict) -> dict:
    """
    Three-bucket classification based on datavalue.type and qualifiers.
    
    Returns:
        {
            "bucket": "attribute" | "edge" | "node_candidate",
            "datatype": str,
            "has_qualifiers": bool
        }
    """
    mainsnak = claim.get('mainsnak', {})
    datavalue = mainsnak.get('datavalue', {})
    datatype = datavalue.get('type', '')
    
    # Bucket 1: Attribute (NOT entity reference)
    if datatype != 'wikibase-entityid':
        return {
            "bucket": "attribute",
            "datatype": datatype,
            "has_qualifiers": False
        }
    
    # It's entity-to-entity. Check qualifiers.
    qualifiers = set(claim.get('qualifiers', {}).keys())
    cipher_qualifiers = qualifiers & CIPHER_ELIGIBLE_QUALIFIERS
    
    # Bucket 3: Node candidate (has cipher-eligible qualifiers)
    if cipher_qualifiers:
        return {
            "bucket": "node_candidate",
            "datatype": datatype,
            "has_qualifiers": True,
            "cipher_qualifiers": list(cipher_qualifiers)
        }
    
    # Bucket 2: Simple edge (entity reference, no complex qualifiers)
    return {
        "bucket": "edge",
        "datatype": datatype,
        "has_qualifiers": False
    }
```

---

## Implementation Steps

### **Step 1: Analyze Checkpoint (15 minutes)**

Create analysis script to classify all claims in checkpoint:

```python
#!/usr/bin/env python3
"""Analyze checkpoint claims - classify into 3 buckets"""

import json
from collections import Counter

CIPHER_ELIGIBLE_QUALIFIERS = {"P580", "P582", "P585", "P276", "P1545"}

# Load checkpoint
with open('output/checkpoints/QQ17167_checkpoint_20260221_061318.json', encoding='utf-8') as f:
    data = json.load(f)

buckets = Counter()
property_classification = {}

for qid, entity in data['entities'].items():
    claims = entity.get('claims', {})
    
    for prop_id, prop_claims in claims.items():
        for claim in prop_claims:
            # Classify
            mainsnak = claim.get('mainsnak', {})
            datatype = mainsnak.get('datavalue', {}).get('type', '')
            
            if datatype != 'wikibase-entityid':
                bucket = 'attribute'
            else:
                qualifiers = set(claim.get('qualifiers', {}).keys())
                if qualifiers & CIPHER_ELIGIBLE_QUALIFIERS:
                    bucket = 'node_candidate'
                else:
                    bucket = 'edge'
            
            buckets[bucket] += 1
            
            if prop_id not in property_classification:
                property_classification[prop_id] = {
                    'attribute': 0,
                    'edge': 0,
                    'node_candidate': 0
                }
            property_classification[prop_id][bucket] += 1

# Report
print("CLAIM CLASSIFICATION ANALYSIS")
print("="*80)
print(f"\nTotal claims analyzed: {sum(buckets.values())}")
print(f"\nBucket distribution:")
print(f"  Attributes: {buckets['attribute']:,} ({buckets['attribute']/sum(buckets.values())*100:.1f}%)")
print(f"  Simple edges: {buckets['edge']:,} ({buckets['edge']/sum(buckets.values())*100:.1f}%)")
print(f"  Node candidates: {buckets['node_candidate']:,} ({buckets['node_candidate']/sum(buckets.values())*100:.1f}%)")

print(f"\nTop 20 edge properties:")
edge_props = {pid: counts['edge'] for pid, counts in property_classification.items() if counts['edge'] > 0}
for pid, count in sorted(edge_props.items(), key=lambda x: x[1], reverse=True)[:20]:
    print(f"  {pid}: {count:,}")

print(f"\nTop 20 node candidate properties:")
node_props = {pid: counts['node_candidate'] for pid, counts in property_classification.items() if counts['node_candidate'] > 0}
for pid, count in sorted(node_props.items(), key=lambda x: x[1], reverse=True)[:20]:
    print(f"  {pid}: {count:,}")

# Save
with open('output/claim_classification_analysis.json', 'w') as f:
    json.dump({
        'buckets': dict(buckets),
        'property_classification': property_classification
    }, f, indent=2)

print(f"\nSaved: output/claim_classification_analysis.json")
```

**Run:** `python analyze_checkpoint_claims.py`

**Expected Output:**
```
Attributes: ~15,000-25,000 (strings, dates, IDs)
Simple edges: ~3,000-8,000 (entity-to-entity, no qualifiers)
Node candidates: ~500-2,000 (complex claims with qualifiers)
```

---

### **Step 2: Import Simple Edges (1 hour)**

Use the analysis to import Bucket 2 (simple edges) first:

```python
#!/usr/bin/env python3
"""Import simple entity-to-entity edges from checkpoint"""

import json
from neo4j import GraphDatabase

CIPHER_ELIGIBLE_QUALIFIERS = {"P580", "P582", "P585", "P276", "P1545"}

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

# Load checkpoint
with open('output/checkpoints/QQ17167_checkpoint_20260221_061318.json', encoding='utf-8') as f:
    data = json.load(f)

entities = data['entities']
all_qids = set(entities.keys())

edge_count = 0
batch = []

for qid_from, entity in entities.items():
    claims = entity.get('claims', {})
    
    for prop_id, prop_claims in claims.items():
        for claim in prop_claims:
            mainsnak = claim.get('mainsnak', {})
            datavalue = mainsnak.get('datavalue', {})
            
            # Only wikibase-entityid (entity-to-entity)
            if datavalue.get('type') != 'wikibase-entityid':
                continue
            
            qid_to = datavalue.get('value', {}).get('id', '')
            
            # Only if target entity exists in our set
            if not qid_to or qid_to not in all_qids:
                continue
            
            # Only simple edges (no cipher-eligible qualifiers)
            qualifiers = set(claim.get('qualifiers', {}).keys())
            if qualifiers & CIPHER_ELIGIBLE_QUALIFIERS:
                continue  # Skip node candidates for now
            
            # Add to batch
            batch.append({
                'from_qid': qid_from,
                'to_qid': qid_to,
                'property_pid': prop_id
            })
            edge_count += 1
            
            # Process in batches of 1000
            if len(batch) >= 1000:
                with driver.session() as session:
                    session.run("""
                        UNWIND $edges as edge
                        MATCH (from:Entity {qid: edge.from_qid})
                        MATCH (to:Entity {qid: edge.to_qid})
                        CALL apoc.merge.relationship(
                          from,
                          'WIKIDATA_' + edge.property_pid,
                          {wikidata_pid: edge.property_pid},
                          {},
                          to,
                          {}
                        ) YIELD rel
                        RETURN count(rel)
                    """, edges=batch)
                print(f"Imported {edge_count:,} edges...")
                batch = []

# Final batch
if batch:
    with driver.session() as session:
        session.run("""
            UNWIND $edges as edge
            MATCH (from:Entity {qid: edge.from_qid})
            MATCH (to:Entity {qid: edge.to_qid})
            CALL apoc.merge.relationship(
              from,
              'WIKIDATA_' + edge.property_pid,
              {wikidata_pid: edge.property_pid},
              {},
              to,
              {}
            ) YIELD rel
            RETURN count(rel)
        """, edges=batch)

driver.close()

print(f"\nTotal simple edges imported: {edge_count:,}")
print(f"Expected: 3,000-8,000 edges")
print(f"Previous: 784 edges")
print(f"Improvement: {edge_count/784:.1f}x")
```

**Run:** `python import_simple_edges.py`

**Expected Result:**
- 3,000-8,000 new edges
- Relationship types: WIKIDATA_P31, WIKIDATA_P279, WIKIDATA_P361, etc.
- Graph becomes connected (can see structure!)

---

### **Step 3: Import Attributes (30 minutes)**

Import Bucket 1 (attributes) as node properties:

```python
# For each entity, update properties from non-entityid claims
# P569 (birth_date), P214 (viaf_id), P18 (image), etc.
# Store as properties on Entity node
```

**Defer to next session** (edges are priority)

---

### **Step 4: Defer Node Candidates**

Bucket 3 (node candidates with qualifiers) requires:
- FacetClaim node creation
- Compound cipher generation
- Facet assignment
- Pattern-centric architecture

**Defer until:** Simple edges validated, SFA deployment ready

---

## Success Criteria

**After Step 2:**
- [ ] 3,000-8,000 entity-to-entity edges imported
- [ ] Avg edges per entity: 1.5-3.0 (vs current 0.30)
- [ ] Can visualize graph structure
- [ ] Can test multi-hop traversal (senator → mollusk)
- [ ] Can validate if SubjectConcept/Facet model works

**Validation Query:**
```cypher
// Check connectivity
MATCH (e:Entity)
OPTIONAL MATCH (e)-[r]-()
WITH e, count(r) as degree
RETURN 
  min(degree) as min_degree,
  avg(degree) as avg_degree,
  max(degree) as max_degree,
  count(CASE WHEN degree = 0 THEN 1 END) as isolated_count
```

**Expected:**
- avg_degree: 1.5-3.0
- isolated_count: <500 (vs current ~2,000)

---

## Files to Create

1. `analyze_checkpoint_claims.py` - Classification analysis
2. `import_simple_edges.py` - Import Bucket 2 (simple edges)
3. `output/claim_classification_analysis.json` - Analysis results

---

## What NOT to Do

❌ Don't use hardcoded whitelist (19 properties)  
❌ Don't filter by registry (314 relationships)  
❌ Don't rename properties yet (keep WIKIDATA_P31, not INSTANCE_OF)  
❌ Don't implement FacetClaim nodes yet (defer)  
❌ Don't guess at intent

✅ DO: Mechanically classify and import ALL entity-to-entity claims

---

**Estimated Time:** 2 hours (analysis + import + validation)  
**Blocking:** Nothing (can start immediately)  
**Output:** Connected graph with 3,000-8,000 edges

**Ready for Dev execution.** 🎯
