# Relationship-First Schema Design for Discovery

**Purpose:** Enable users to discover complex relationships and explore them logically  
**Principle:** Relationships are the primary value, not nodes

---

## Discovery Pattern: The Sword Example

### User Journey: "Tell me about swords"

**Step 1: Types and Variants**
- What kinds of swords existed?
- Query: `MATCH (sword_type:Concept {type_qid: "Q629"})-[:VARIANT_OF]->(variant)`

**Step 2: Temporal Context**
- When did different types exist?
- Query: `MATCH (sword_type)-[:PREVALENT_DURING]->(period:Period)`

**Step 3: Functional Use Cases**
- Did different types have different use cases?
- Query: `MATCH (sword_type)-[:DESIGNED_FOR]->(use_case:Concept)`

**Step 4: Production and Economics**
- Where and how were they made?
- Query: `MATCH (sword_type)-[:MANUFACTURED_IN]->(place:Place)`
- Query: `MATCH (sword_type)-[:PRODUCED_BY]->(industry:Organization)`
- Query: `MATCH (sword_type)-[:COST]->(currency_amount:Concept)`

**Step 5: Evolution and Replacement**
- When were they no longer the prevalent choice?
- Query: `MATCH (sword_type)-[:OBSOLETE_AFTER]->(event:Event)`
- Why replaced?
- Query: `MATCH (sword_type)-[:DISPLACED_BY]->(replacement:Concept)`
- Query: `MATCH (sword_type)-[:OBSOLETE_DUE_TO]->(reason:Event|Concept)`

**Step 6: Comparative Analysis**
- Which was superior/inferior?
- Query: `MATCH (sword1)-[:SUPERIOR_TO]->(sword2)`
- Query: `MATCH (sword_type)-[:EFFECTIVE_AGAINST]->(target:Concept)`

---

## Required Relationship Categories

### 1. Typological Relationships (What kinds exist?)

```cypher
// Variants and subtypes
(specific_sword_type)-[:VARIANT_OF]->(general_sword_type)
(gladius)-[:VARIANT_OF]->(sword)

// Alternatives/equivalents
(sword_type1)-[:ALTERNATIVE_TO]->(sword_type2)
```

**Existing:** None - need to add

---

### 2. Temporal Relationships (When did they exist/change?)

```cypher
// Period of prevalence
(sword_type)-[:PREVALENT_DURING {start: -300, end: 300}]->(period:Period)
(sword_type)-[:INTRODUCED_IN]->(period:Period)
(sword_type)-[:CEASED_USE_IN]->(period:Period)

// Event-based timing
(sword_type)-[:INTRODUCED_BY]->(event:Event)
(sword_type)-[:OBSOLETE_AFTER]->(event:Event)
```

**Existing:**
- `DURING` (for events in periods) ✅
- `WITHIN_TIMESPAN` (for entities) ✅
- Need: PREVALENT_DURING, INTRODUCED_IN, OBSOLETE_AFTER

---

### 3. Functional Relationships (What were they used for?)

```cypher
// Purpose and use cases
(sword_type)-[:DESIGNED_FOR]->(purpose:Concept)
(sword_type)-[:USED_FOR]->(use_case:Concept)
(sword_type)-[:EFFECTIVE_AGAINST]->(target:Concept)  // e.g., "effective against mail armor"
(sword_type)-[:INEFFECTIVE_AGAINST]->(target:Concept)

// Tactical/strategic
(sword_type)-[:OPTIMAL_IN]->(context:Concept)  // e.g., "optimal in close combat"
```

**Existing:**
- `USE` / `USED_BY` (generic use) ✅
- Need: DESIGNED_FOR, EFFECTIVE_AGAINST, OPTIMAL_IN

---

### 4. Production Relationships (How/where made?)

```cypher
// Manufacturing
(sword_type)-[:MANUFACTURED_IN]->(place:Place)
(sword_type)-[:MANUFACTURED_BY]->(organization:Organization)
(sword_type)-[:MADE_USING_TECHNIQUE]->(technique:Concept)
(sword_type)-[:REQUIRES_SKILL]->(skill:Concept)

// Materials and components
(sword_type)-[:TYPICALLY_MADE_OF]->(material:Material)
(sword_type)-[:REQUIRES_MATERIAL]->(material:Material)
```

**Existing:**
- `MATERIAL_USED` (instance level) ✅
- `PRODUCES_GOOD` / `PRODUCED_BY` (production) ✅
- `CREATED_BY` / `CREATOR` (authorship) ✅
- Need: MANUFACTURED_IN, MADE_USING_TECHNIQUE, TYPICALLY_MADE_OF

---

### 5. Economic Relationships (Cost, trade, availability)

```cypher
// Cost and value
(sword_type)-[:COST]->(price:Concept)  // e.g., "expensive", "costly"
(sword_type)-[:VALUED_AT]->(currency_amount:Concept)

// Trade
(sword_type)-[:TRADED_FROM]->(place:Place)
(sword_type)-[:IMPORTED_FROM]->(place:Place)
(sword_type)-[:EXPORTED_TO]->(place:Place)

// Availability
(sword_type)-[:AVAILABLE_TO]->(social_class:Concept)  // e.g., "available to nobles"
(sword_type)-[:RESTRICTED_TO]->(group:Concept)
```

**Existing:**
- `EXPORTED_TO` / `IMPORTED_FROM` ✅
- Need: COST, VALUED_AT, AVAILABLE_TO

---

### 6. Evolution and Replacement (How did they change/why replaced?)

```cypher
// Evolution
(sword_type1)-[:EVOLVED_FROM]->(sword_type2)
(sword_type1)-[:EVOLVED_INTO]->(sword_type3)

// Replacement and obsolescence
(old_sword_type)-[:DISPLACED_BY]->(new_sword_type)
(old_sword_type)-[:REPLACED_BY]->(new_sword_type)
(old_sword_type)-[:SUPERSEDED_BY]->(new_sword_type)
(old_sword_type)-[:OBSOLETE_DUE_TO]->(reason:Event|Concept)  // e.g., "obsolete due to improved armor"
(old_sword_type)-[:PHASED_OUT_BECAUSE]->(reason:Concept)
```

**Existing:**
- `EVOLVED_FROM` / `EVOLVED_INTO` (Cultural category) ✅
- Need: DISPLACED_BY, REPLACED_BY, OBSOLETE_DUE_TO, PHASED_OUT_BECAUSE

---

### 7. Comparative Relationships (Which was better/worse?)

```cypher
// Superiority
(sword_type1)-[:SUPERIOR_TO]->(sword_type2)
(sword_type1)-[:INFERIOR_TO]->(sword_type2)

// Advantages/disadvantages
(sword_type)-[:ADVANTAGE]->(advantage:Concept)  // e.g., "lighter", "longer reach"
(sword_type)-[:DISADVANTAGE]->(disadvantage:Concept)

// Competition
(sword_type1)-[:COMPETED_WITH]->(sword_type2)
```

**Existing:**
- `COMPETED_WITH` (Political category - but could be adapted) ✅
- Need: SUPERIOR_TO, ADVANTAGE, DISADVANTAGE

---

## Complete Discovery Query: Sword Evolution

```cypher
// Full exploration query
MATCH (gladius:Concept {qid: "Q629"})
OPTIONAL MATCH (gladius)-[:VARIANT_OF]->(parent)
OPTIONAL MATCH (gladius)-[:PREVALENT_DURING]->(period:Period)
OPTIONAL MATCH (gladius)-[:DESIGNED_FOR]->(purpose:Concept)
OPTIONAL MATCH (gladius)-[:TYPICALLY_MADE_OF]->(material:Material)
OPTIONAL MATCH (gladius)-[:MANUFACTURED_IN]->(place:Place)
OPTIONAL MATCH (gladius)-[:EFFECTIVE_AGAINST]->(target:Concept)
OPTIONAL MATCH (gladius)-[r:DISPLACED_BY|REPLACED_BY|OBSOLETE_DUE_TO]->(replacement)
OPTIONAL MATCH (gladius)-[:SUPERIOR_TO]->(inferior)
OPTIONAL MATCH (gladius)<-[:SUPERIOR_TO]-(superior)
RETURN gladius,
       parent,
       period,
       purpose,
       material,
       place,
       target,
       replacement,
       type(r) as obsolescence_reason,
       inferior,
       superior
```

---

## Recommended Relationship Additions

### Typological Category

```csv
Typological,VARIANT_OF,Is variant or subtype of,,forward,,1,GN,Culture,885059,active,Subtype relationship for objects/materials,new,1.0
Typological,HAS_VARIANT,Has variant or subtype,,inverse,,1,GN,Culture,885059,active,Inverse of VARIANT_OF,new,1.0
Typological,ALTERNATIVE_TO,Alternative/equivalent to another type,,symmetric,,1,GN,Culture,885059,active,Equivalent alternatives,new,1.0
```

### Temporal Evolution Category

```csv
Evolution,PREVALENT_DURING,Type was prevalent during period,,forward,,1,QB,Time,1151043,active,Period of common use with temporal bounds,new,1.0
Evolution,INTRODUCED_IN,Type was introduced in period,,forward,,1,QB,Time,1151043,active,Introduction period,new,1.0
Evolution,CEASED_USE_IN,Type ceased to be used in period,,forward,,1,QB,Time,1151043,active,Cessation period,new,1.0
Evolution,INTRODUCED_BY,Type was introduced by event,,forward,,1,QB,Time,1151043,active,Introduction event,new,1.0
Evolution,OBSOLETE_AFTER,Type became obsolete after event,,forward,,1,QB,Time,1151043,active,Obsolescence event,new,1.0
Evolution,DISPLACED_BY,Type was displaced by another type,,forward,,1,GN,Culture,885059,active,Displacement relationship,new,1.0
Evolution,REPLACED_BY,Type was replaced by another type,,forward,,1,GN,Culture,885059,active,Replacement relationship,new,1.0
Evolution,SUPERSEDED_BY,Type was superseded by another type,,forward,,1,GN,Culture,885059,active,Supersession relationship,new,1.0
Evolution,OBSOLETE_DUE_TO,Type became obsolete due to reason,,forward,,1,GN,Culture,885059,active,Reason for obsolescence,new,1.0
Evolution,PHASED_OUT_BECAUSE,Type was phased out because of reason,,forward,,1,GN,Culture,885059,active,Reason for phasing out,new,1.0
```

### Functional Category

```csv
Functional,DESIGNED_FOR,Purpose for which type was designed,,forward,,1,T,Technology,1145002,active,Design purpose,new,1.0
Functional,EFFECTIVE_AGAINST,Type is effective against target,,forward,,1,T,Technology,1145002,active,Effectiveness relationship,new,1.0
Functional,INEFFECTIVE_AGAINST,Type is ineffective against target,,forward,,1,T,Technology,1145002,active,Ineffectiveness relationship,new,1.0
Functional,OPTIMAL_IN,Type is optimal in context/situation,,forward,,1,T,Technology,1145002,active,Optimal context,new,1.0
```

### Production Category

```csv
Production,MANUFACTURED_IN,Type manufactured in location,,forward,,1,T,Technology,1145002,active,Manufacturing location,new,1.0
Production,MANUFACTURED_BY,Type manufactured by organization,,forward,,1,T,Technology,1145002,active,Manufacturing organization,new,1.0
Production,MADE_USING_TECHNIQUE,Type made using technique,,forward,,1,T,Technology,1145002,active,Manufacturing technique,new,1.0
Production,REQUIRES_SKILL,Type requires skill to make,,forward,,1,T,Technology,1145002,active,Required skill,new,1.0
Production,TYPICALLY_MADE_OF,Material type is typically made from,,forward,,1,T,Technology,1145002,active,Typical material composition,new,1.0
Production,REQUIRES_MATERIAL,Type requires material for production,,forward,,1,T,Technology,1145002,active,Required material,new,1.0
```

### Economic Category

```csv
Economic,COST,Type has cost/value characteristic,,forward,,1,HB,Economics,902116,active,Cost descriptor,new,1.0
Economic,VALUED_AT,Type valued at amount,,forward,,1,HB,Economics,902116,active,Monetary value,new,1.0
Economic,AVAILABLE_TO,Type available to social group,,forward,,1,HB,Economics,902116,active,Social availability,new,1.0
Economic,RESTRICTED_TO,Type restricted to group,,forward,,1,HB,Economics,902116,active,Social restriction,new,1.0
```

### Comparative Category

```csv
Comparative,SUPERIOR_TO,Type is superior to another type,,forward,,1,T,Technology,1145002,active,Superiority comparison,new,1.0
Comparative,INFERIOR_TO,Type is inferior to another type,,forward,,1,T,Technology,1145002,active,Inferiority comparison,new,1.0
Comparative,ADVANTAGE,Type has advantage,,forward,,1,T,Technology,1145002,active,Advantage descriptor,new,1.0
Comparative,DISADVANTAGE,Type has disadvantage,,forward,,1,T,Technology,1145002,active,Disadvantage descriptor,new,1.0
Comparative,COMPETED_WITH,Type competed with another type,,symmetric,,1,T,Technology,1145002,active,Competition between types,new,1.0
```

---

## Schema Design Principles

### 1. Relationship-First Thinking
- Ask: "What questions will users explore?" before "What properties do nodes need?"
- Design relationships that answer questions, not just store facts

### 2. Discovery Paths
- Every relationship should enable a logical next question
- Chain relationships: Type → Variants → Temporal → Use Cases → Production → Economics → Replacement

### 3. Temporal Precision
- Use temporal relationships with properties: `{start: -300, end: 300}`
- Link to Periods for broad context
- Link to Events for specific moments

### 4. Comparative Structures
- Always provide ways to compare alternatives
- SUPERIOR_TO, EFFECTIVE_AGAINST, OPTIMAL_IN all enable comparison

### 5. Causal Chains
- Connect obsolescence to reasons
- Connect replacement to events
- Enable "why" queries, not just "what" and "when"

---

## Example: Complete Sword Exploration

### Graph Structure

```cypher
// Sword types and variants
(gladius:Concept {qid: "Q629", label: "Gladius"})
(spatha:Concept {qid: "Q123", label: "Spatha"})
(gladius_hispaniensis:Concept {label: "Gladius Hispaniensis"})

// Variants
(gladius_hispaniensis)-[:VARIANT_OF]->(gladius)

// Temporal
(gladius)-[:PREVALENT_DURING {start: -300, end: 300}]->(republic_period:Period)
(gladius)-[:INTRODUCED_BY]->(punic_wars:Event)
(gladius)-[:OBSOLETE_AFTER]->(military_reform:Event)
(gladius)-[r:DISPLACED_BY {date: 300}]->(spatha)

// Functional
(gladius)-[:DESIGNED_FOR]->(close_combat:Concept)
(gladius)-[:EFFECTIVE_AGAINST]->(unarmored:Concept)
(gladius)-[:OPTIMAL_IN]->(formation_fighting:Concept)

// Production
(gladius)-[:MANUFACTURED_IN]->(noricum:Place)
(gladius)-[:TYPICALLY_MADE_OF]->(steel:Material)
(gladius)-[:MADE_USING_TECHNIQUE]->(pattern_welding:Concept)

// Economics
(gladius)-[:COST]->(expensive:Concept)
(gladius)-[:AVAILABLE_TO]->(legionaries:Concept)

// Replacement
(gladius)-[:OBSOLETE_DUE_TO]->(improved_cavalry:Concept)
(gladius)-[:PHASED_OUT_BECAUSE]->(need_longer_reach:Concept)

// Comparison
(gladius)-[:SUPERIOR_TO]->(greek_xiphos:Concept)
(spatha)-[:SUPERIOR_TO]->(gladius)
(gladius)-[:ADVANTAGE]->(versatility:Concept)
(gladius)-[:DISADVANTAGE]->(short_reach:Concept)
```

### User Queries Enable Discovery

1. **"What types of swords existed?"**
   ```cypher
   MATCH (sword:Concept {type_qid: "Q629"})-[:VARIANT_OF*]->(variant)
   RETURN variant
   ```

2. **"When was the gladius used?"**
   ```cypher
   MATCH (gladius)-[:PREVALENT_DURING]->(period)
   RETURN period, period.start_year, period.end_year
   ```

3. **"Why was the gladius replaced?"**
   ```cypher
   MATCH (gladius)-[:OBSOLETE_DUE_TO|PHASED_OUT_BECAUSE]->(reason)
   RETURN reason
   ```

4. **"What was better than the gladius?"**
   ```cypher
   MATCH (gladius)<-[:SUPERIOR_TO]-(superior)
   RETURN superior
   ```

---

## Next Steps

1. Add relationship categories above to canonical CSV
2. Create examples in documentation showing discovery paths
3. Update agent prompts to extract these relationships
4. Build query templates for common exploration patterns

