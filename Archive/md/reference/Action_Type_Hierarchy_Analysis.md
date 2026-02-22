# Action Type Hierarchy Analysis

## Question

Do action types need a hierarchy like entity types have?

---

## Current State

**Entity Types**: Have explicit hierarchy (`neo4j_entity_hierarchy.csv`)
- Parent → Child relationships (e.g., Event → Battle → War)
- Used for "most specific" classification rule
- Enables querying at different levels of abstraction

**Action Types**: Flat list with 15 action types
- No explicit hierarchy
- Used as properties on relationships (`action_type` property)
- Some clearly have parent-child relationships (e.g., MIL_ACT → DEFENSIVE/OFFENSIVE)

---

## Potential Hierarchical Relationships

### 1. **Military Actions** (Clear hierarchy)
```
MIL_ACT (Military Action)
  ├─ DEFENSIVE (Defensive Action)
  └─ OFFENSIVE (Offensive Action)
```
**Rationale**: DEFENSIVE and OFFENSIVE are subtypes of military actions

### 2. **Governance Actions** (Possible hierarchy)
```
ADMIN (Administrative)
  └─ TYRANNY (Tyrannical Governance)

CONST_INNOV (Constitutional Innovation)
  └─ ADMIN (Administrative)
```
**Rationale**: Tyranny is a form of administrative/governance action

### 3. **Criminal Actions** (Possible hierarchy)
```
CRIME (Criminal Act)
  └─ (Could have subtypes: Murder, Theft, etc.)
```
**Note**: Currently no subtypes defined

---

## Benefits of Hierarchy

### ✅ 1. **Query Flexibility**
```cypher
// Query all military actions (including subtypes)
MATCH ()-[r]->()
WHERE r.action_type IN ['MIL_ACT', 'DEFENSIVE', 'OFFENSIVE']
RETURN r

// With hierarchy, could query:
MATCH ()-[r]->()
WHERE r.action_type IN descendants('MIL_ACT')
RETURN r
```

### ✅ 2. **Classification Guidance**
- LLM could use hierarchy for "most specific" rule
- If an action is both MIL_ACT and DEFENSIVE, use DEFENSIVE (more specific)

### ✅ 3. **Validation**
- Can validate that DEFENSIVE must be a subtype of MIL_ACT
- Prevents inconsistent classifications

### ✅ 4. **Consistency with Entity Types**
- Matches the pattern used for entity type hierarchy
- Familiar structure for developers/LLMs

---

## Drawbacks of Hierarchy

### ❌ 1. **Action Types Are Properties, Not Entities**
- Entity types are **nodes** in the graph (can have relationships)
- Action types are **properties** on relationships (less structured)

### ❌ 2. **Multiple Categories**
- An action might belong to multiple categories (e.g., TYRANNY could be ADMIN or POL_ACT)
- Hierarchy assumes single parent (unless we use multiple inheritance)

### ❌ 3. **Less Clear Parent-Child**
- Unlike entity types (Battle IS-A Event), action types are more categorical
- DEFENSIVE is a type of military action, but is it really a "subtype" or just a "category"?

### ❌ 4. **Current Usage**
- Action types are stored as simple string codes on relationships
- No current mechanism to query "descendants" of action types

---

## Recommendation: **Optional Hierarchy with Categorization**

### Approach 1: **Flat with Categories** (Simpler - Recommended)

Keep action types flat, but group them by **domain/category**:

```csv
Category,Action_Type,Code
Military,Military Action,MIL_ACT
Military,Defensive Action,DEFENSIVE
Military,Offensive Action,OFFENSIVE
Governance,Administrative,ADMIN
Governance,Tyrannical Governance,TYRANNY
Governance,Constitutional Innovation,CONST_INNOV
...
```

**Benefits**:
- Simple to implement
- Easy to query by category
- No complex hierarchy logic needed
- Matches current flat structure

**Usage**:
```cypher
// Query all military category actions
MATCH ()-[r]->()
WHERE r.action_type_category = 'Military'
RETURN r
```

---

### Approach 2: **Explicit Hierarchy** (More Complex)

Create `action_type_hierarchy.csv` similar to entity hierarchy:

```csv
Parent Type,Parent Code,Child Type,Child Code,Relationship
Military Action,MIL_ACT,Defensive Action,DEFENSIVE,SUBTYPE_OF
Military Action,MIL_ACT,Offensive Action,OFFENSIVE,SUBTYPE_OF
Administrative,ADMIN,Tyrannical Governance,TYRANNY,SUBTYPE_OF
```

**Benefits**:
- Enables "most specific" classification
- Query flexibility (find all military actions including subtypes)
- Consistency with entity type approach

**Drawbacks**:
- More complex to implement
- Need hierarchy query functions
- Some action types may not have clear hierarchy

---

## Hybrid Approach (Recommended)

**Use both categories AND optional hierarchy**:

1. **Categories** (required): Group action types by domain
   - Military, Governance, Legal, Economic, Social, Personal, Religious, Criminal

2. **Hierarchy** (optional): Only define hierarchy where clear parent-child exists
   - MIL_ACT → DEFENSIVE/OFFENSIVE (clear)
   - ADMIN → TYRANNY (optional/debatable)
   - Others remain flat

---

## Implementation Options

### Option A: Add Categories Only (Simplest)
- Add `category` column to vocabularies CSV
- No hierarchy file needed
- Query by category for grouping

### Option B: Add Optional Hierarchy (Most Flexible)
- Keep flat structure as default
- Add `action_type_hierarchy.csv` for explicit parent-child
- Support both flat queries and hierarchy queries

### Option C: No Hierarchy (Current State)
- Keep action types flat
- Use domain knowledge for grouping
- Simpler, but less structured

---

## Decision Matrix

| Need | Option A: Categories | Option B: Hierarchy | Option C: Flat |
|------|---------------------|---------------------|----------------|
| **Query by domain** | ✅ Easy | ✅ Easy | ❌ Manual |
| **Most specific rule** | ❌ No | ✅ Yes | ❌ No |
| **Validation** | ⚠️ Category only | ✅ Full validation | ❌ No |
| **Complexity** | ✅ Low | ⚠️ Medium | ✅ Low |
| **Consistency with entities** | ⚠️ Partial | ✅ Yes | ❌ No |
| **Future extensibility** | ⚠️ Limited | ✅ High | ❌ Limited |

---

## Recommendation

**Start with Option A (Categories)** because:
1. ✅ Simple to implement
2. ✅ Covers most use cases (grouping/querying)
3. ✅ Can add hierarchy later if needed
4. ✅ Action types are less structured than entity types

**Add hierarchy later (Option B) if**:
- You need "most specific" classification for actions
- You want to query "all military actions" including subtypes
- Multiple action types clearly form hierarchies

---

## Example Implementation (Categories Only)

Update `action_structure_vocabularies.csv`:

```csv
Category,Type,Code,Description,Examples,Action_Category
Action Type,Political Revolution,REVOL,Political overthrow...,Military
Action Type,Military Action,MIL_ACT,Military operations...,Military
Action Type,Defensive Action,DEFENSIVE,Defensive measures...,Military
Action Type,Offensive Action,OFFENSIVE,Aggressive measures...,Military
Action Type,Administrative,ADMIN,Administrative actions...,Governance
Action Type,Tyrannical Governance,TYRANNY,Abusive rule...,Governance
...
```

**Query Example**:
```cypher
// Find all military category actions
MATCH ()-[r]->()
WHERE r.action_type_category = 'Military'
RETURN r.action_type, count(*) as count
```

---

## Conclusion

**Action types don't strictly NEED hierarchy**, but **categories would be helpful** for:
- Grouping related actions
- Querying by domain
- LLM classification guidance

**Explicit hierarchy is optional** and only needed if you want:
- "Most specific" classification rule
- Query "all military actions" including subtypes
- Full validation of action type relationships

**Recommendation**: Add categories first, consider hierarchy later if use cases emerge.

