# Neo4j Reference Data Schema (Phase 2)

**Purpose:** Define node structures for reference data that GPT queries (roles, relationships, authorities)  
**Date:** February 15, 2026  
**Version:** Phase 2 Planning  
**Audience:** Neo4j architects, backend developers  

---

## Overview

**Problem:** GPT can't hold 100k+ reference entries (20 file limit). Solution: Store in Neo4j, query on demand.

**Architecture:**
```
GPT Agent → Query Neo4j → Get reference data → Continue claim processing
   ↓
   MATCH (role:Role {name: "commander"}) RETURN role.aliases, role.p_value, role.confidence_baseline
   ↓
Returns: {aliases: ["general", "leader"], p_value: "P641", baseline: 0.98}
```

**Reference Data Types:**
1. Roles (70+ canonical)
2. Relationship Types (312 types)
3. Facet Configurations (17 facets with per-relationship baselines)
4. Authority Vocabularies (LCSH, FAST, LCC)

---

## 1. Role Nodes

**Source:** `role_qualifier_reference.json`

### Node Structure

```cypher
CREATE (role:Role {
  // Identity
  name: "commander",                    // Canonical name
  role_id: "role_military_commander",   // Unique ID
  
  // Metadata
  description: "Military leader commanding troops",
  category: "Military",                 // 10 categories
  aliases: ["general", "military commander", "colonel"],
  
  // Wikidata Integration
  p_value: "P641",                      // Wikidata property
  cidoc_crm_type: "E39_Actor",          // CIDOC-CRM class
  
  // Scoring
  confidence_baseline: 0.98,            // Default confidence when used
  
  // Context
  context_facets: ["military", "political", "social"],
  examples: ["Julius Caesar", "Alexander the Great"],
  
  // Metadata
  created_date: date(),
  source: "Phase_1_registry"
})
```

### Query Examples

**Lookup by name (for validation):**
```cypher
MATCH (role:Role {name: $role_name})
WHERE role.name =~ "(?i).*leader.*"  // Fuzzy match
RETURN role.name, role.confidence_baseline, role.aliases
```

**All military roles:**
```cypher
MATCH (role:Role)
WHERE role.category = "Military"
RETURN role.name, role.confidence_baseline, role.context_facets
```

**Role with best fit for context:**
```cypher
MATCH (role:Role)
WHERE "military" IN role.context_facets
  AND role.confidence_baseline > 0.90
RETURN role.name, role.confidence_baseline
ORDER BY role.confidence_baseline DESC
LIMIT 5
```

### Load Script (Cypher)

```cypher
// Load from JSON (assumes file uploaded to Neo4j import)
LOAD CSV WITH HEADERS FROM "file:///role_qualifier_reference.json" AS row
CREATE (role:Role {
  name: row.role_name,
  role_id: "role_" + toLower(replace(row.role_name, " ", "_")),
  description: row.description,
  category: row.category,
  aliases: split(row.aliases, ","),
  p_value: row.p_value,
  cidoc_crm_type: row.cidoc_crm_type,
  confidence_baseline: toFloat(row.confidence_baseline),
  context_facets: split(row.context_facets, ","),
  examples: split(row.examples, ",")
})

// Create indexes for fast lookup
CREATE INDEX role_name FOR (r:Role) ON (r.name);
CREATE INDEX role_category FOR (r:Role) ON (r.category);
```

---

## 2. Relationship Type Nodes

**Source:** `relationship_types_registry_master.csv` + `relationship_facet_baselines.json`

### Node Structure

```cypher
CREATE (reltype:RelationshipType {
  // Identity
  name: "PARTICIPATED_IN",              // Canonical name
  rel_id: "rel_participated_in",        // Unique ID
  
  // Metadata
  description: "Entity participated in event or conflict",
  category: "Participation",            // 25+ categories
  aliases: ["participated", "took_part_in"],
  
  // Wikidata Integration
  p_value: "P710",                      // Wikidata property
  direction: "bidirectional",           // PARTICIPATED_IN / HAD_PARTICIPANT
  inverse_name: "HAD_PARTICIPANT",      // For reverse queries
  
  // Scoring
  base_confidence: 0.85,                // Default if no facet specified
  
  // Facet Baselines (expanded at query time)
  facet_baseline_military: 0.90,
  facet_baseline_political: 0.75,
  facet_baseline_social: 0.70,
  
  // Constraints
  requires_role: true,                  // Must have role qualifier
  required_role_category: "Military",   // What roles apply
  
  // Metadata
  created_date: date(),
  source: "Phase_1_registry"
})
```

### Relationships (Reltype → Facet)

```cypher
CREATE (reltype:RelationshipType)
  -[:HAS_FACET_BASELINE {confidence: 0.90}]->
(facet:Facet {name: "military"})
```

### Query Examples

**Get relationship type by name:**
```cypher
MATCH (rt:RelationshipType {name: "PARTICIPATED_IN"})
RETURN rt.base_confidence, rt.p_value, rt.inverse_name
```

**Get per-facet baseline:**
```cypher
MATCH (rt:RelationshipType {name: "PARTICIPATED_IN"})
  -[baseline:HAS_FACET_BASELINE]->
(facet:Facet {name: $facet})
RETURN baseline.confidence
```

**All facet baselines for relationship:**
```cypher
MATCH (rt:RelationshipType {name: "SPOUSE_OF"})
  -[baseline:HAS_FACET_BASELINE]->
(facet:Facet)
RETURN facet.name, baseline.confidence
ORDER BY baseline.confidence DESC
```

**Relationships requiring specific role:**
```cypher
MATCH (rt:RelationshipType {required_role_category: "Military"})
RETURN rt.name, rt.description
```

### Load Script (Cypher)

```cypher
// Create RelationshipType nodes from CSV
LOAD CSV WITH HEADERS FROM "file:///relationship_types_registry_master.csv" AS row
CREATE (rt:RelationshipType {
  name: row.relationship_type,
  rel_id: "rel_" + toLower(replace(row.relationship_type, " ", "_")),
  description: row.description,
  category: row.category,
  p_value: row.p_value,
  direction: row.direction,
  inverse_name: row.inverse_name,
  base_confidence: toFloat(row.base_confidence),
  requires_role: row.requires_role = "true",
  required_role_category: row.required_role_category
})

// Link to facet baselines (from relationship_facet_baselines.json)
LOAD CSV WITH HEADERS FROM "file:///relationship_facet_baselines.json" AS row
MATCH (rt:RelationshipType {name: row.relationship_type})
MATCH (facet:Facet {name: row.facet})
CREATE (rt)-[:HAS_FACET_BASELINE {confidence: toFloat(row.confidence)}]->(facet)

// Create indexes
CREATE INDEX reltype_name FOR (r:RelationshipType) ON (r.name);
CREATE INDEX reltype_category FOR (r:RelationshipType) ON (r.category);
```

---

## 3. Facet Nodes

**Source:** SCHEMA_REFERENCE.md (17 facets)

### Node Structure

```cypher
CREATE (facet:Facet {
  name: "military",
  facet_id: "facet_military",
  description: "Military conflicts, participation, commands",
  color: "#8B0000",                     // For visualization
  
  // Expected properties for this facet
  typical_properties: [
    "role:commander",
    "outcome:victory|defeat|stalemate",
    "campaign:name",
    "deployment:location"
  ],
  
  // Temporal characteristics
  temporal_specificity: "high",         // Must specify year/season
  
  // Common relationships in this facet
  common_relationships: [
    "PARTICIPATED_IN",
    "COMMANDED",
    "DEFEATED",
    "ALLIED_WITH"
  ],
  
  created_date: date()
})
```

### Load Script (Cypher)

```cypher
CREATE (f1:Facet {name: "military", description: "Military conflicts, participation, commands"})
CREATE (f2:Facet {name: "political", description: "Political offices, authority, alliances"})
CREATE (f3:Facet {name: "genealogical", description: "Family relationships, lineage"})
CREATE (f4:Facet {name: "social", description: "Social class, group membership"})
// ... repeat for all 17 facets

CREATE INDEX facet_name FOR (f:Facet) ON (f.name);
```

---

## 4. Authority Vocabulary Nodes (LCSH, FAST, LCC)

**Source:** LCSH/, FAST/, Subjects/LCC/ folders

### Node Structure

#### LCSH (Library of Congress Subject Headings)

```cypher
CREATE (lcsh:AuthorityTerm:LCSH {
  // Identity
  lcsh_id: "sh85001870",                // Official LCSH ID
  preferred_label: "Rome--History",
  
  // Relationships to concepts
  broader_terms: ["sh85001865"],        // BT (broader term)
  narrower_terms: ["sh85001871"],       // NT (narrower term)
  related_terms: ["sh85040853"],        // RT (related term)
  
  // Mappings to other systems
  wikidata_qid: "Q7184",                // Q7184 = Rome
  fast_id: "fst01205435",               // FAST equivalent
  
  // Metadata
  created_date: date(),
  notes: "Use for historical Rome topics"
})
```

#### FAST (Faceted Application of Subject Terminology)

```cypher
CREATE (fast:AuthorityTerm:FAST {
  fast_id: "fst01205435",
  preferred_label: "Rome",
  
  // FAST hierarchy
  broader_terms: ["fst01431059"],       // Geographic area
  narrower_terms: ["fst01205436"],      // Roman history
  
  // Cross-system mappings
  lcsh_id: "sh85001870",
  wikidata_qid: "Q7184",
  
  // FAST-specific
  type: "Geographic",                   // Type of FAST term
  created_date: date()
})
```

#### LCC (Library of Congress Classification)

```cypher
CREATE (lcc:ClassificationTerm:LCC {
  lcc_code: "DG70",                     // LCC code for Roman history
  label: "Rome",
  
  // Classification hierarchy
  parent_code: "DG",                    // D = History, DG = History (Ancient Rome)
  child_codes: ["DG71", "DG72"],        // Narrower classifications
  
  // Cross-system mappings
  lcsh_id: "sh85001870",
  fast_id: "fst01205435",
  wikidata_qid: "Q7184",
  
  created_date: date()
})

// Create relationships between classification systems
(:LCC {code: "DG70"})
  -[:EQUIVALENT_TO]->
(:LCSH {id: "sh85001870"})
  -[:EQUIVALENT_TO]->
(:FAST {id: "fst01205435"})
```

### Query Examples

**Find subject by term (any authority system):**
```cypher
MATCH (term:AuthorityTerm)
WHERE term.preferred_label =~ "(?i).*Rome.*"
RETURN term.lcsh_id, term.fast_id, term.wikidata_qid, labels(term)
```

**Cross-system lookup (LCSH ID → Wikidata QID):**
```cypher
MATCH (lcsh:LCSH {lcsh_id: "sh85001870"})
OPTIONAL MATCH (lcsh)-[:EQUIVALENT_TO]->(fast:FAST)
OPTIONAL MATCH (fast)-[:EQUIVALENT_TO]->(lcc:LCC)
RETURN lcsh.preferred_label, fast.preferred_label, lcc.label, 
       lcsh.wikidata_qid, fast.wikidata_qid
```

**Broader concepts (for facet context):**
```cypher
MATCH (term:AuthorityTerm {preferred_label: "Rome--History"})
OPTIONAL MATCH (term)-[:BROADER_TERM]->(broader:AuthorityTerm)
RETURN term.preferred_label, broader.preferred_label
```

### Load Script (Cypher)

```cypher
// Load LCSH terms from LCSH folder
LOAD CSV WITH HEADERS FROM "file:///LCSH/lcsh_terms.csv" AS row
CREATE (lcsh:AuthorityTerm:LCSH {
  lcsh_id: row.lcsh_id,
  preferred_label: row.preferred_label,
  broader_terms: split(row.broader_terms, ";"),
  narrower_terms: split(row.narrower_terms, ";"),
  wikidata_qid: row.wikidata_qid,
  fast_id: row.fast_id
})

// Load FAST terms from FAST folder
LOAD CSV WITH HEADERS FROM "file:///FAST/fast_terms.csv" AS row
CREATE (fast:AuthorityTerm:FAST {
  fast_id: row.fast_id,
  preferred_label: row.preferred_label,
  type: row.type,
  lcsh_id: row.lcsh_id,
  wikidata_qid: row.wikidata_qid
})

// Create equivalence relationships
MATCH (lcsh:LCSH), (fast:FAST)
WHERE lcsh.fast_id = fast.fast_id
CREATE (lcsh)-[:EQUIVALENT_TO]->(fast)

// Create indexes for authority lookups
CREATE INDEX lcsh_id FOR (l:LCSH) ON (l.lcsh_id);
CREATE INDEX fast_id FOR (f:FAST) ON (f.fast_id);
CREATE INDEX lcc_code FOR (l:LCC) ON (l.lcc_code);
CREATE INDEX authority_label FOR (a:AuthorityTerm) ON (a.preferred_label);
```

---

## 5. Summary: Query Patterns for GPT

**All queries GPT might need:**

### Role Validation
```cypher
// Validate "commander" → get p_value and aliases
MATCH (role:Role {name: $role_name})
RETURN {
  canonical_name: role.name,
  p_value: role.p_value,
  confidence: role.confidence_baseline,
  aliases: role.aliases,
  valid: true
}
```

### Facet Baseline Lookup
```cypher
// What confidence for SPOUSE_OF in political facet?
MATCH (rt:RelationshipType {name: "SPOUSE_OF"})
  -[b:HAS_FACET_BASELINE]->
(f:Facet {name: $facet})
RETURN b.confidence AS facet_baseline
```

### Authority Cross-Reference
```cypher
// Convert "Roman history" → all authority IDs
MATCH (term:AuthorityTerm {preferred_label: $label})
RETURN {
  lcsh_id: term.lcsh_id,
  fast_id: term.fast_id,
  wikidata_qid: term.wikidata_qid,
  lcc_code: term.lcc_code
}
```

### Relationship Requirements
```cypher
// Can I use relationship X with role Y?
MATCH (rt:RelationshipType {name: $rel_type})
MATCH (role:Role {category: rt.required_role_category})
RETURN rt.name, collect(role.name) AS allowed_roles
```

---

## 6. Implementation Roadmap (Phase 2)

**Week 1:** Load reference data
- [ ] Create Role nodes (70+)
- [ ] Create RelationshipType nodes (312)
- [ ] Create Facet nodes (17)
- [ ] Create indexes

**Week 2:** Authority vocabularies
- [ ] Load LCSH samples (1,000+)
- [ ] Load FAST samples (1,000+)
- [ ] Create equivalence relationships
- [ ] Build hierarchy

**Week 3:** Query API for GPT
- [ ] Expose query endpoints (REST/MCP)
- [ ] Implement query caching
- [ ] Add response formatting for GPT

**Week 4:** Integration testing
- [ ] Test GPT queries against Neo4j
- [ ] Validate round-trip (GPT → Neo4j → GPT)
- [ ] Performance tuning if needed

---

## 7. Performance Considerations

**Indexes needed:**
- Role.name (for lookup)
- RelationshipType.name (for lookup)
- Facet.name (for lookup)
- AuthorityTerm.preferred_label (for search)
- All authority IDs (lcsh_id, fast_id, wikidata_qid)

**Cache strategy:**
- Role queries: Cache ~5 minutes (static registry)
- Facet baselines: Cache ~1 hour
- Authority searches: Cache ~24 hours (external source changes rarely)

**Expected response times:**
- Role lookup: <10ms
- Per-facet baseline: <20ms
- Authority cross-reference: <50ms
- Relationship validation: <20ms

---

## Next Steps

1. Verify Neo4j can handle 100k+ reference nodes efficiently
2. Load sample data; test query performance
3. Design REST/MCP API for GPT access
4. Implement query response formatter (JSON for GPT consumption)

This moves reference data architecture from **file-based** (GPT) to **query-based** (Neo4j), enabling unlimited growth without hitting GPT's 20-file limit.
