# Phase 1: Detailed Discussion Points

**Status:** Planned Discussion  
**Date:** February 14, 2026  

---

## DISCUSSION 1: QID Requirement for Granular Claims

**Your Question:** "If we get a really granular claim, how to handle?"

**Scenario:** Entity exists but is so specific (e.g., "Marcus Junius Brutus during Senate meeting of 44 BCE") that a dedicated Wikidata QID doesn't exist.

### Current Constraint Proposal
```cypher
CREATE CONSTRAINT human_has_qid IF NOT EXISTS
FOR (h:Human) REQUIRE h.qid IS NOT NULL;
```

### Problem This Creates
- ❌ Blocks ingestion of valid historical claims for entities without Wikidata equivalents
- ❌ Assumes all historical figures have QIDs (not true for minor figures)
- ❌ Prevents local/LCSH-only entities from being claimed

### Options to Discuss

**Option A: "Hard QID Requirement"** (Conservative)
```
IF QID IS NULL → REJECT CLAIM
Rationale: QID = federated identity marker; claims without it are local-only
Consequence: 15-25% of valid historical claims blocked
```

**Option B: "QID Optional with Authority Trace"** (Permissive)
```
IF QID IS NULL BUT authority_source IS NOT NULL → ACCEPT CLAIM
Example: Marcus Brutus variant actor in 49 BCE Senate = no QID, but LCSH sh85018999 exists
Consequence: Allows LCSH/FAST-only claims; loses Wikidata traceability
```

**Option C: "Provisional QID Placeholder"** (Hybrid)
```
IF QID IS NULL → auto-generate local QID: "local_entity_{entity_hash}"
LINK to: Wikidata via authority_ids if match exists later
Example: local_entity_a8f9e2 = Future "Marcus Brutus variant" if verified
Consequence: Allows granular claims; enables post-hoc Wikidata linking
```

### YOUR CALL NEEDED:
- Which option for genealogical claims (low-granularity, many have QIDs)?
- Which option for military participation (higher-granularity, fewer QIDs)?
- Should rule differ by facet?

---

## DISCUSSION 2: Facet Mappings (Item 3: "We Need to Discuss")

**Current State:** Facets in registry only as string (e.g., "demographic|social")

**Why Discuss?**
- Single relationship can apply to multiple facets
- Example: SPOUSE_OF could be `social` (personal bond) + `political` (alliance) + `demographic` (genealogy)
- Claims promoted separately per facet, but relationship is same

### Problem Scenario
```
Claim 1: "Julius Caesar married Cornelia" 
  Facet: social → confidence 0.92, posterior 0.91 → PROMOTED
  Facet: political → confidence 0.88, posterior 0.85 → NOT PROMOTED (posterior < 0.90)
  Facet: demographic → confidence 0.95, posterior 0.87 → NOT PROMOTED (posterior < 0.90)
```

Result: **Same relationship promoted in one facet, blocked in others**

### Options to Discuss

**Option A: "Facet-Independent Relationship"** (Simplest)
```
SPOUSE_OF has ONE confidence baseline (0.88)
Claim evaluated once; applies to ALL appropriate facets
Pro: Clean, no per-facet calculation
Con: Loses nuance (military participation ≠ diplomatic participation)
```

**Option B: "Facet-Specific Baselines"** (Granular)
```
SPOUSE_OF → social: baseline 0.88
SPOUSE_OF → political: baseline 0.85  
SPOUSE_OF → demographic: baseline 0.92
Claim evaluated 3 times with different baselines per facet
Pro: Fine-grained confidence per context
Con: Complex; relationship now axis-dependent
```

**Option C: "Facet Context in Claim Metadata"** (Current Approach)
```
Claim stores: relationship_type + facet + confidence
Single confidence evaluation for chosen facet only
Pro: Preserves user intent ("this is a political marriage claim")
Con: User must pre-select facet; loses multi-facet claim efficiency
```

### YOUR CALL NEEDED:
- Should one relationship → one confidence baseline or per-facet?
- If per-facet: does relationship get created multiple times or store array?
- Should genealogical relationships be facet-independent (always demographic)?

---

## DISCUSSION 3: Role/Faction Storage on Relationships (Item 4: "Discuss")

**Current Problem:** Can't distinguish `commander` vs `soldier` in `PARTICIPATED_IN`

### Option A: "Edge Properties with Constraints"** (Neo4j Native)
```cypher
MATCH (h:Human)-[r:PARTICIPATED_IN]->(e:Event)
WHERE r.role = 'commander' AND r.faction = 'Roman'
```

**Pros:**
- Native Neo4j; efficient queries
- Indexable on specific properties
- Aligns with Wikidata qualifiers

**Cons:**
- Each role becomes a separate edge property
- No type validation in Neo4j (can store "comander", "commandor", typos)
- Scalability: 20 different roles = 20 property fields

### Option B: "Reified Role Node"** (Entity-Relation-Role)
```cypher
(h:Human)-[:PARTICIPATED_IN]->(ref:ParticipationRole)-[:ROLE_IN]->(e:Event)
ref.type = "commander"
ref.faction = "Roman"
```

**Pros:**
- Role becomes first-class entity (queryable, constrainable)
- Can add timestamps to role ("started as soldier, became commander")
- Links to `MilitaryRank` entity if needed

**Cons:**
- Adds 2x relationships per participation
- Queries become nested (less direct)
- Over-engineered for simple role labels?

### Option C: "JSON Stringified Qualifiers"** (Flexible)
```cypher
(h:Human)-[r:PARTICIPATED_IN {
  qualifiers: '{"role":"commander","faction":"Roman","rank":"general","outcome":"decisive_victory"}'
}]->(e:Event)
```

**Pros:**
- Arbitrary role complexity supported
- Compacts multiple qualifiers into one field
- Wikidata-aligned (qualifiers are list of objects)

**Cons:**
- Not queryable without parsing
- Requires index on stringified values
- CRMinf reasoning needs JSON deserialization

### YOUR CALL NEEDED:
- How many distinct roles do we anticipate? (10? 50? 100+?)
- Do roles need historical tracking ("was promoted from X to Y")?
- Should roles link to authority entities (e.g., Wikidata P410 Military Rank)?

---

## DISCUSSION 4: Missing Relationships with Wiki/CIDOC/CRMinf Alignment

**My Proposal:** Add 5 new relationships:

```
PARTICIPATED_IN (P710)
DIED_AT (P1120)
MEMBER_OF_GENS (P53)
NEGOTIATED_TREATY (P3342)
WITNESSED_EVENT (P1441)
```

**Question for You:** Before adding, should we:

1. **Map each to CRMinf classes?**
   - PARTICIPATED_IN → E7_Activity + I2_Belief
   - DIED_AT → E6_Destruction + E69_Death
   - etc.

2. **Add CRMinf belief node tracking per relationship?**
   - Currently: `claim.minf_belief_id` on node
   - Proposed: `relationship.minf_belief_id` on edge (who asserted this participation?)

3. **Add CIDOC-CRM type equivalency?**
   - MEMBER_OF_GENS → P107_has_member (Family link)
   - PARTICIPATED_IN → P73_has_object (Activity participation)
   - etc.

### YOUR CALL NEEDED:
- Should each relationship have its own CRMinf belief tracking?
- Do we track "who claimed this participation" separately from "who participated"?
- Is P-value → CRMinf mapping mandatory or optional in registry?

---

## DECISION MATRIX

| Issue | Option A | Option B | Option C | PREFERRED? |
|-------|----------|----------|----------|------------|
| **QID Requirement** | Hard QID | QID Optional | Provisional QID | ? |
| **Facet Mapping** | Facet-Independent | Facet-Specific | Metadata Context | ? |
| **Role Storage** | Edge Properties | Reified Role Node | JSON Qualifiers | ? |
| **Missing Rels** | Add all + CIDOC | Add all + CRMinf | Add all + both | ? |

---

## NEXT STEPS (After Your Answers)

1. **Update PHASE_1_GENEALOGY_PARTICIPATION.md** with your decisions
2. **Create concrete CSV entries** aligned with your choices
3. **Write Neo4j schema** implementing chosen options
4. **Update claim pipeline** with role handling logic
5. **Test with Caesar-Brutus cluster** to validate

---

**READY FOR DISCUSSION**

Please address each section and we'll lock in Phase 1 implementation details.
