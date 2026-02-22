# FAST Subject Import Documentation

## Overview

The **FAST Subject Import Pipeline** imports Library of Congress Subject Headings (LCSH) from JSONLD SKOS format into a Chrystallum Neo4j knowledge graph with:

- **Authority tier classification** (TIER_1/2/3 based on federation level)
- **Multi-faceted analysis** (subjects scored across 16 analytical dimensions)
- **Temporal name handling** (supports historical name variants like Mount McKinley → Denali)
- **Cypher generation** (produces ready-to-import Neo4j statements)

## Files

### Scripts

- `scripts/import_fast_subjects_to_neo4j.py` – Main import pipeline
  - Parses JSONLD SKOS records from FAST exports
  - Classifies subjects by authority tier
  - Scores subjects across 16 facets
  - Generates Cypher import statements

### Input Files

- `key/subjects_sample_50.jsonld` – Sample of 50 LCSH subjects in JSONLD/SKOS format
- `key/FASTTopical_parsed.csv` – Full FAST topical subjects export (325 MB)

### Output Files

- `output/subjects_import_sample.cypher` – Generated Cypher for sample subjects
- `output/subjects_full.cypher` – Generated Cypher for full FAST export (future)

## Usage

### Basic Import (Sample)

```bash
cd c:\Projects\Graph1
python Python/fast/scripts/import_fast_subjects_to_neo4j.py \
  "Python/fast/key/subjects_sample_50.jsonld" \
  "Python/fast/output/subjects_import_sample.cypher"
```

**Output:**
```
============================================================
FAST Subject Import Summary
============================================================
Total subjects imported: 50

By Authority Tier:
  TIER_1: 0
  TIER_2: 0
  TIER_3: 50

Top subjects by facet richness:
  Antipatterns (Software engineering) (1 facets)
  ...
```

### Full FAST Import (Future)

```bash
# Parse full CSV
python Python/fast/scripts/import_fast_subjects_to_neo4j.py \
  "Python/fast/key/FASTTopical_parsed.csv" \
  "Python/fast/output/subjects_full.cypher"
```

## Authority Tier Classification

Subjects are classified into three tiers based on federation level:

| Tier | LCSH | Wikidata | Wikipedia | Confidence | Use Case |
|------|------|----------|-----------|-----------|----------|
| **TIER_1** | ✅ | ✅ | ✅ | 98% | Central subjects (e.g., "Roman Republic") |
| **TIER_2** | ✅ | ✅ | ❌ | 90% | Domain-specific (e.g., "Pithecia" genus) |
| **TIER_3** | ✅ | ❌ | ❌ | 70% | Narrow/rare subjects (e.g., local watersheds) |

**Determination:**
- Current implementation: All subjects start as TIER_3 (LCSH only)
- Enhancement in progress: Add Wikidata/Wikipedia lookups for tier upgrade

## Facet Scoring

Subjects are auto-scored across 6 primary facets:

| Facet | Keywords | Base Score | Example |
|-------|----------|-----------|---------|
| Political | government, state, empire, dynasty, regime | 0.90 | "Rome--History--Republic" |
| Military | war, battle, military, conquest, army | 0.85 | "Military units" |
| Economic | trade, commerce, economic, market | 0.80 | "Trade routes" |
| Cultural | culture, art, customs, traditions | 0.75 | "Cultural heritage" |
| Religious | religion, faith, doctrine, theology | 0.80 | "Religious movements" |
| Geographic | geographic, place, region, territory | 0.95 | "Denali, Mount" |

**Facet richness:** Count of facets with score > 0.50 (ranges 0-16 with full taxonomy)

## Data Model

### Subject Node (Neo4j)

```cypher
(:Subject {
  lcsh_id: "sh85036288",                    // Primary key from LCSH
  unique_id: "SUBJECT_LCSH_sh85036288",     // UUID for graph
  label: "Denali, Mount",                   // Current LCSH heading
  authority_tier: "TIER_1",                 // Confidence tier
  authority_confidence: 0.98,               // Numeric confidence
  
  // Facet scoring
  facet_scores: {
    geographic: 0.98,
    environmental: 0.75,
    scientific: 0.65
  },
  facet_richness: 3,                        // Number of strong facets
  
  // Federation
  wikidata_qid: "Q131407",                  // Wikidata link
  wikipedia_link: true,                     // Has Wikipedia article
  
  // Temporal variants
  named_variants: [
    {
      name: "Mount McKinley",
      valid_from: 1896,
      valid_until: 2015,
      is_official: true
    },
    {
      name: "Denali, Mount",
      valid_from: 2015,
      valid_until: 9999,
      is_official: true
    }
  ],
  
  // Classification
  lcc_code: "QG101.4.D",
  dewey_code: "557.98",
  created_date: datetime("1896-01-01"),
  last_revised: datetime("2015-09-01"),
  is_deprecated: false
})
```

### Subject-to-Facet Relationship

```cypher
(subject:Subject)-[:FACET_ANCHOR {score: float}]->(facet:Facet)
```

Example: `Denali, Mount` → 0.98 score to `GeographicFacet`

## Cypher Import Process

### 1. Generate Cypher Script

```python
importer = FASTSubjectImporter("subjects_sample_50.jsonld")
importer.import_subjects()
cypher = importer.generate_cypher_script("output.cypher")
```

### 2. Load Into Neo4j

```cypher
// Option A: Copy-paste from output file (small imports)
// Option B: Use Neo4j CLI
neo4j-admin database import full --nodes=/path/to/subjects_import_sample.cypher

// Option C: From Python driver
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
with driver.session() as session:
    with open("output.cypher") as f:
        for line in f:
            if line.strip() and not line.startswith("//"):
                session.run(line)
```

### 3. Verify Import

```cypher
// Count imported subjects
MATCH (s:Subject)
RETURN count(s) AS subject_count;

// Find subjects by tier
MATCH (s:Subject)
WHERE s.authority_tier = "TIER_1"
RETURN s.label, s.authority_confidence;

// Find subjects with facet anchors
MATCH (s:Subject)-[r:FACET_ANCHOR]->(f:Facet)
RETURN s.label, f.label, r.score
LIMIT 50;
```

## Enhancements & TODO

### Priority 1: Federation Enhancement
- [ ] Add Wikidata QID lookup for subjects
- [ ] Add Wikipedia availability check
- [ ] Auto-upgrade TIER_3 subjects to TIER_1/TIER_2 based on lookups
- [ ] Batch lookup via Wikidata SPARQL API

### Priority 2: Facet Enrichment
- [ ] Expand facet keywords from 6 to 16 full facets
- [ ] Weight facet scoring by scholarly authority
- [ ] Add facet anchors for all 16 dimensions (not just 6)
- [ ] Link to facet_registry_master.json for canonical mappings

### Priority 3: Import Optimization
- [ ] Handle full CSV parse (325 MB file)
- [ ] Batch Neo4j writes (current: 1 statement per subject)
- [ ] Add transaction rollback on errors
- [ ] Support incremental imports (detect duplicates)

### Priority 4: Historical Name Binding
- [ ] Extract temporal variants from LCSH change notes
- [ ] Parse valid_from/valid_until from change dates
- [ ] Support official name transitions (Mount McKinley → Denali)

## Testing

### Test 1: Parse Sample JSONLD

```bash
python Python/fast/scripts/import_fast_subjects_to_neo4j.py \
  "Python/fast/key/subjects_sample_50.jsonld"
```

✅ Expected: 50 subjects parsed, summary printed

### Test 2: Generate Cypher

```bash
python Python/fast/scripts/import_fast_subjects_to_neo4j.py \
  "Python/fast/key/subjects_sample_50.jsonld" \
  "Python/fast/output/test_output.cypher"
```

✅ Expected: Cypher file created with 50 CREATE statements + facet anchors

### Test 3: Verify Cypher Syntax

```bash
# Check for cypher syntax errors
grep -E "^CREATE|^MATCH" "Python/fast/output/test_output.cypher" | wc -l
```

✅ Expected: 50+ lines (mix of CREATE and MATCH statements)

## Performance Notes

- **Sample (50 subjects):** ~500ms parse + generate
- **Full dataset (expected):** ~10-15s for parsing, 30-60s for Cypher generation
- **Neo4j import:** Depends on batch size; ~1 subject/ms with tuned writes

## Integration with Chrystallum

### How Subjects Fit Into the Architecture

1. **Section 4: Subject Layer** – Subjects are primary semantic anchors
2. **Appendix C: Entity Taxonomies** – Authority tier framework applies to all subjects
3. **Section 3.2-3.3: Facet System** – Subject → Facet mappings drive multi-dimensional analysis
4. **Section 5.5: Agent Assignment** – Facet scores route subjects to specialist agents

### Query Examples

**Find all subjects rich in Political facet:**
```cypher
MATCH (s:Subject)
WHERE s.facet_scores.political >= 0.80
RETURN s.label, s.facet_scores.political
ORDER BY s.facet_scores.political DESC;
```

**Route subjects to agents by facet specialization:**
```cypher
MATCH (s:Subject)-[:FACET_ANCHOR {score: score}]->(f:Facet)
MATCH (agent:Agent)-[:OWNS_CATEGORY]->(cat:FacetCategory)
WHERE f.facet_class_base = cat.key
RETURN s.label, agent.label, score
ORDER BY score DESC;
```

**Subject timeline (temporal name variants):**
```cypher
MATCH (s:Subject {lcsh_id: "sh85036288"})
UNWIND s.named_variants AS variant
RETURN variant.name, variant.valid_from, variant.valid_until
ORDER BY variant.valid_from;
```

---

**Last Updated:** February 12, 2026  
**Status:** Sample import working; full FAST export in progress
