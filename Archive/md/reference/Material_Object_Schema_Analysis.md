# Material and Object Schema Analysis - Ancient Rome Focus

**Date:** December 12, 2025  
**Context:** Adding Objects and Materials to schema with focus on Ancient Rome

---

## Current Relationship Coverage

### ✅ Existing Relationships We Can Use

1. **MATERIAL_USED** (P186) - "Made from"
   - Can use for: `(toga)-[:MATERIAL_USED]->(wool)`
   - Can also use for: `(toga)-[:MATERIAL_USED]->(purple_dye)` (treating dye as material component)

2. **PRODUCES_GOOD** / **PRODUCED_BY** (P1056) - "Entity produces good or service"
   - Can use for: `(tyre)-[:PRODUCES_GOOD]->(tyrian_purple)`
   - Direction: `(location)-[:PRODUCES_GOOD]->(material)`

3. **LOCATED_IN** - "Entity is located in place"
   - Can use for: `(tyrian_purple)-[:LOCATED_IN]->(tyre)` (production location)

4. **CREATOR** / **CREATED_BY** (P170) - "Created by"
   - Could use for: `(toga)-[:CREATED_BY]->(artisan)` (if we have creator info)

5. **EXPORTED_TO** / **IMPORTED_FROM** - Trade relationships
   - Can use for: `(tyrian_purple)-[:EXPORTED_TO]->(rome)`

### ❌ Missing Relationships Needed

1. **DYED_WITH** / **DYED_BY** - Object dyed with dye/pigment
   - Needed for: `(toga)-[:DYED_WITH]->(tyrian_purple)`
   - Wikidata property: P462 (color) or P186 (material) - but these don't quite fit
   - Suggestion: Create new relationship

2. **DERIVED_FROM** / **DERIVES_FROM** - Material extracted from source organism
   - Needed for: `(tyrian_purple)-[:DERIVED_FROM]->(murex_snail)`
   - Note: EXTRACTED_FROM exists but only for Attribution category
   - Wikidata property: P1535 (used by) or P1071 (location of origin) might work
   - Suggestion: Create new relationship

3. **WORN_BY** / **WEARS** - Person wears clothing
   - Needed for: `(senator)-[:WEARS]->(toga)`
   - Wikidata property: P1324 (form of expression) doesn't fit
   - Suggestion: Create new relationship

4. **PRODUCED_IN** - Material produced in location (more specific than LOCATED_IN)
   - Can work around with: PRODUCES_GOOD or LOCATED_IN
   - But a dedicated relationship would be clearer

---

## Proposed Material Schema (Ancient Rome Focus)

### Materials CSV Structure

```csv
Category,Entity Type,Description,Wikidata QID
Material,Metallic Element,Pure metal element,Q11344
Material,Precious Metal,Rare valuable metal,Q10895043
Material,Base Metal,Common industrial metal,Q11426
Material,Gold,Precious metal element,Q897
Material,Silver,Precious metal element,Q1090
Material,Iron,Metal element,Q677
Material,Copper,Metal element,Q753
Material,Tin,Metal element,Q1096
Material,Lead,Metal element,Q708
Material,Alloy,Metal mixture,Q124458
Material,Bronze,Alloy of copper and tin,Q34095
Material,Steel,Iron-carbon alloy,Q11427
Material,Brass,Alloy of copper and zinc,Q34098
Material,Textile Material,Woven fabric material,Q28823
Material,Wool,Animal fiber from sheep,Q170303
Material,Linen,Plant fiber from flax,Q175315
Material,Leather,Tanned animal hide,Q161556
Material,Stone,Natural rock material,Q1201835
Material,Marble,Metamorphic rock,Q40861
Material,Clay,Earthen material,Q1143459
Material,Ceramic Material,Fired clay material,Q1088477
Material,Glass,Amorphous solid material,Q40847
Material,Purple Dye,Coloring substance,Q1067557
Material,Tyrian Purple,Ancient purple dye from murex snails,Q1067557
Material,Mineral,Natural crystalline substance,Q7946
```

### Objects (Artifacts) CSV Structure

```csv
Category,Entity Type,Description,Wikidata QID
Artifact,Weapon,Implement for combat,Q728
Artifact,Sword,Edged weapon,Q629
Artifact,Spear,Thrusting weapon,Q126005
Artifact,Clothing,Body covering garment,Q11460
Artifact,Toga,Roman draped garment,Q185598
Artifact,Tunic,Simple garment worn under toga,Q636968
Artifact,Coin,Metal currency,Q41207
Artifact,Pottery,Ceramic container,Q134661
Artifact,Vessel,Container or ship,Q207571
Artifact,Tool,Device used for work,Q39546
```

### Hierarchy Structure

```csv
# Material hierarchy
Metallic Element,Q11344,Precious Metal,Q10895043,SUBCLASS_OF
Metallic Element,Q11344,Base Metal,Q11426,SUBCLASS_OF
Precious Metal,Q10895043,Gold,Q897,SUBCLASS_OF
Precious Metal,Q10895043,Silver,Q1090,SUBCLASS_OF
Base Metal,Q11426,Iron,Q677,SUBCLASS_OF
Base Metal,Q11426,Copper,Q753,SUBCLASS_OF
Base Metal,Q11426,Tin,Q1096,SUBCLASS_OF
Base Metal,Q11426,Lead,Q708,SUBCLASS_OF
Alloy,Q124458,Bronze,Q34095,SUBCLASS_OF
Alloy,Q124458,Steel,Q11427,SUBCLASS_OF
Alloy,Q124458,Brass,Q34098,SUBCLASS_OF
Textile Material,Q28823,Wool,Q170303,SUBCLASS_OF
Textile Material,Q28823,Linen,Q175315,SUBCLASS_OF
Purple Dye,Q1067557,Tyrian Purple,Q1067557,SUBCLASS_OF

# Object hierarchy
Artifact,Q35127,Weapon,Q728,SUBCLASS_OF
Weapon,Q728,Sword,Q629,SUBCLASS_OF
Weapon,Q728,Spear,Q126005,SUBCLASS_OF
Artifact,Q35127,Clothing,Q11460,SUBCLASS_OF
Clothing,Q11460,Toga,Q185598,SUBCLASS_OF
Clothing,Q11460,Tunic,Q636968,SUBCLASS_OF
Artifact,Q35127,Tool,Q39546,SUBCLASS_OF
Artifact,Q35127,Coin,Q41207,SUBCLASS_OF
```

---

## Purple Toga Example - Complete Graph Structure

### Question: "Where did the purple come from and how was it made?"

### Graph Pattern

```cypher
// 1. THE TOGA (object instance)
CREATE (toga_instance:Artifact {
  qid: "Q12345",  // Specific toga instance ID
  type_qid: "Q185598",  // Toga type
  cidoc_class: "E22_Man-Made_Object",
  label: "Toga Praetexta of Senator Marcus",
  unique_id: "TOGA_PRAETEXTA_001"
})

// 2. TOGA TYPE (concept)
CREATE (toga_type:Concept {
  qid: "Q185598",
  label: "Toga",
  unique_id: "CONCEPT_TOGA"
})

// Type relationship
CREATE (toga_instance)-[:INSTANCE_OF]->(toga_type)

// 3. MATERIAL: Wool
CREATE (wool:Material {
  qid: "Q170303",
  type_qid: "Q170303",
  label: "Wool",
  unique_id: "MATERIAL_WOOL"
})

CREATE (toga_instance)-[:MATERIAL_USED]->(wool)

// 4. DYE: Tyrian Purple
CREATE (tyrian_purple:Material {
  qid: "Q1067557",
  type_qid: "Q1067557",
  label: "Tyrian Purple",
  unique_id: "MATERIAL_TYRIAN_PURPLE"
})

// OPTION A: Use MATERIAL_USED (if we treat dye as material component)
CREATE (toga_instance)-[:MATERIAL_USED]->(tyrian_purple)

// OPTION B: Use new DYED_WITH relationship (preferred - more semantic)
// CREATE (toga_instance)-[:DYED_WITH]->(tyrian_purple)

// 5. SOURCE: Murex Snail
CREATE (murex_snail:Concept {
  qid: "Q202825",  // Or specific species QID
  label: "Murex Snail",
  unique_id: "CONCEPT_MUREX_SNAIL"
})

// OPTION A: Use new DERIVED_FROM relationship (preferred)
// CREATE (tyrian_purple)-[:DERIVED_FROM]->(murex_snail)

// OPTION B: Work around with RELATED_TO (less precise)
CREATE (tyrian_purple)-[:RELATED_TO]->(murex_snail)

// 6. PRODUCTION LOCATION: Tyre
CREATE (tyre:Place {
  qid: "Q182033",
  label: "Tyre",
  unique_id: "PLACE_TYRE"
})

// OPTION A: Use PRODUCES_GOOD
CREATE (tyre)-[:PRODUCES_GOOD]->(tyrian_purple)

// OPTION B: Use LOCATED_IN
CREATE (tyrian_purple)-[:LOCATED_IN]->(tyre)

// 7. WEARER: Senator
CREATE (senator:Person {
  qid: "Q123456",
  label: "Marcus Tullius Cicero",
  unique_id: "PERSON_CICERO"
})

// OPTION A: Use new WEARS relationship (preferred)
// CREATE (senator)-[:WEARS]->(toga_instance)

// OPTION B: Work around with RELATED_TO (less precise)
CREATE (senator)-[:RELATED_TO]->(toga_instance)

// 8. BACKBONE: FAST tether (REQUIRED)
CREATE (fast_subject:Subject {
  fast_id: "1145002",  // Technology subject
  label: "Ancient Roman Clothing",
  unique_id: "SUBJECT_FAST_1145002"
})

CREATE (toga_instance)-[:SUBJECT_OF]->(fast_subject)
```

### Query Patterns

```cypher
// Find purple dye sources
MATCH (purple:Material {type_qid: "Q1067557"})
MATCH (purple)-[:DERIVED_FROM]->(source)
RETURN purple.label, source.label

// Find how togas are made
MATCH (toga:Artifact {type_qid: "Q185598"})
MATCH (toga)-[:MATERIAL_USED]->(material)
RETURN toga.label, material.label

// Find who wore purple togas
MATCH (person:Person)-[:WEARS]->(toga:Artifact)
MATCH (toga)-[:DYED_WITH]->(purple:Material {type_qid: "Q1067557"})
RETURN person.label, toga.label

// Trace purple production chain
MATCH (toga:Artifact)-[:MATERIAL_USED]->(purple:Material {type_qid: "Q1067557"})
MATCH (purple)-[:DERIVED_FROM]->(snail:Concept)
MATCH (purple)-[:PRODUCED_IN]->(location:Place)
RETURN toga.label, purple.label, snail.label, location.label
```

---

## Recommended Relationship Additions

Add these to `relations/canonical_relationship_types.csv`:

```csv
Application,DYED_WITH,Object dyed with dye or pigment,,forward,,1,T,Technology,1145002,active,Dyeing/tinting relationship,new,1.0
Application,DYED_BY,Dye used to dye object,,inverse,,1,T,Technology,1145002,active,Inverse of DYED_WITH,new,1.0
Application,DERIVED_FROM,Material extracted or derived from source organism,,forward,,1,T,Technology,1145002,active,Material extraction from biological source,new,1.0
Application,DERIVES_MATERIAL,Source organism used to derive material,,inverse,,1,T,Technology,1145002,active,Inverse of DERIVED_FROM,new,1.0
Application,PRODUCED_IN,Material produced or manufactured in location,,forward,,1,T,Technology,1145002,active,Production location for materials,new,1.0
Application,PRODUCES_MATERIAL,Location produces this material,,inverse,,1,T,Technology,1145002,active,Inverse of PRODUCED_IN,new,1.0
Social,WEARS,Person wears clothing or garment,,forward,,1,HM,Social structure,1123372,active,Wearing clothing,new,1.0
Social,WORN_BY,Garment is worn by person,,inverse,,1,HM,Social structure,1123372,active,Inverse of WEARS,new,1.0
```

---

## Action Items

1. ✅ Add materials to `Reference/neo4j_entities_deduplicated.csv`
2. ✅ Add objects to `Reference/neo4j_entities_deduplicated.csv`
3. ✅ Add hierarchy relationships to `relations/neo4j_entity_hierarchy.csv`
4. ⚠️ Consider adding new relationships for dyeing, derivation, and wearing
5. ✅ Regenerate schema using `consolidate_schema.py`
6. ✅ Update `arch/NODE_TYPE_SCHEMAS.md` with Object and Material schemas

---

## Notes

- Focus on Ancient Rome: Only include materials/objects relevant to the domain
- Avoid overly broad categories: No generic "Material" or "Object" types
- Use existing relationships where possible, but add new ones for clarity
- Maintain backbone compliance: All entities need FAST tether

