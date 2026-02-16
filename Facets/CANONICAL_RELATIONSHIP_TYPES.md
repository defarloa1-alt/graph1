# Canonical Relationship Types

**Owner:** BiographicSFA (Biographic Specialist Facet Agent)

**Purpose:** Standardized relationship taxonomy for all person-to-person connections in the knowledge graph.

**Last Updated:** February 16, 2026

---

## Overview

BiographicSFA defines **canonical relationship types** that all agents must use when creating relationship claims. This ensures:

1. **Consistency:** Same relationship expressed same way across all facets
2. **Query efficiency:** Standard types enable efficient graph traversal
3. **Semantic clarity:** Explicit directionality and relationship nature
4. **Cross-facet interoperability:** All facets reference same relationship vocabulary

---

## Family Relationships (Blood/Legal)

### Parent-Child (Directional)

**CHILD_OF** (person → parent)
- **Usage:** Subject is child of object
- **Example:** `Caesar -[CHILD_OF]-> C. Julius Caesar (father)`
- **Qualifiers:** 
  * `biological` (blood relation)
  * `adoptive` (legal adoption)
  * `step` (via parent's remarriage)
- **Inverse:** PARENT_OF

**PARENT_OF** (parent → person)
- **Usage:** Subject is parent of object
- **Example:** `Aurelia -[PARENT_OF]-> Caesar`
- **Qualifiers:** Same as CHILD_OF
- **Note:** Create BOTH claims for complete stemma (bidirectional edges)

### Sibling (Symmetric)

**SIBLING_OF** (person ↔ person)
- **Usage:** Subject and object share parent(s)
- **Example:** `Caesar -[SIBLING_OF]-> Julia (sister)`
- **Qualifiers:**
  * `full_sibling` (same father and mother)
  * `half_sibling` (one shared parent)
  * `adoptive_sibling` (via one parent's adoption)
- **Note:** Symmetric (if A sibling of B, then B sibling of A)

### Spouse (Symmetric)

**MARRIED** (person ↔ person)
- **Usage:** Marriage relationship
- **Example:** `Caesar -[MARRIED]-> Cornelia Cinna`
- **Temporal:** MUST include start time, optionally end time (divorce/death)
- **Qualifiers:**
  * `marriage_year` (start)
  * `divorce_year` (if divorced)
  * `ended_by_death` (if spouse died)
- **Note:** Symmetric, but create BOTH claims for query efficiency

**BETROTHED_TO** (person ↔ person)
- **Usage:** Engagement (politically significant in Roman Republic)
- **Example:** `Octavian -[BETROTHED_TO]-> Clodia Pulchra`
- **Temporal:** MUST include betrothal date
- **Note:** Often broken for political reasons

### Adoption (Directional)

**ADOPTED_BY** (person → adopter)
- **Usage:** Subject legally adopted by object
- **Example:** `Octavian -[ADOPTED_BY]-> Caesar`
- **Temporal:** MUST include adoption date
- **Note:** In Roman law, adoption creates full legal parent-child bond
- **Consequences:**
  * Name change (adopter's nomen + original nomen as cognomen)
  * Inheritance rights
  * Gens membership transfer

**ADOPTED** (adopter → person)
- **Usage:** Subject adopted object as child
- **Example:** `Caesar -[ADOPTED]-> Octavian`
- **Inverse:** ADOPTED_BY

### Extended Family

**GRANDPARENT_OF** / **GRANDCHILD_OF** (directional)
- **Usage:** Two-generation separation
- **Example:** `Julia -[GRANDCHILD_OF]-> C. Julius Caesar (grandfather)`
- **Note:** Can be inferred from CHILD_OF chains, but explicit claim useful

**COUSIN_OF** (symmetric)
- **Usage:** Shared grandparent
- **Qualifiers:**
  * `first_cousin` (shared grandparent)
  * `second_cousin` (shared great-grandparent)
- **Note:** Important for Roman alliances (cousin marriages)

---

## Clan/Gens Relationships

**MEMBER_OF_GENS** (person → gens)
- **Usage:** Membership in Roman clan (gens)
- **Example:** `Caesar -[MEMBER_OF_GENS]-> gens Julia`
- **Temporal:** From birth (or adoption)
- **Note:** Determines nomen (family name: e.g., Julius, Cornelius, Claudius)

**FOUNDER_OF_GENS** (legendary/historical person → gens)
- **Usage:** Legendary or historical founder
- **Example:** `Iulus -[FOUNDER_OF_GENS]-> gens Julia`
- **Note:** Often mythological (gens Julia claimed descent from Venus via Iulus/Ascanius)

**COGNOMEN_BRANCH** (person → sub-branch)
- **Usage:** Branch within gens designated by cognomen
- **Example:** `Scipio Africanus -[COGNOMEN_BRANCH]-> Cornelii Scipiones`
- **Note:** Major gentes had multiple branches (e.g., Cornelii Scipiones, Cornelii Lentuli, Cornelii Sullae)

---

## Social/Political Relationships

### Patron-Client System

**PATRON_OF** (patron → client)
- **Usage:** Patron-client relationship (critical in Roman society)
- **Example:** `Caesar -[PATRON_OF]-> Clodius Pulcher`
- **Temporal:** Can change over career
- **Note:** Patrons provide protection, clients provide political support

**CLIENT_OF** (client → patron)
- **Usage:** Inverse of PATRON_OF
- **Example:** `Clodius -[CLIENT_OF]-> Caesar`
- **Inverse:** PATRON_OF

### Political Alliances

**POLITICAL_ALLY_OF** (person ↔ person)
- **Usage:** Temporary or permanent political alliance
- **Example:** `Caesar -[POLITICAL_ALLY_OF]-> Crassus` (First Triumvirate)
- **Temporal:** MUST include start, optionally end
- **Qualifiers:**
  * `alliance_type` (triumvirate, marriage alliance, factional)
  * `alliance_sealed_by` (marriage, treaty, oath)
- **Note:** Often sealed by marriage between families

**POLITICAL_RIVAL_OF** (person ↔ person)
- **Usage:** Factional opposition
- **Example:** `Caesar -[POLITICAL_RIVAL_OF]-> Cato the Younger`
- **Temporal:** Duration of rivalry
- **Note:** Not same as ENEMY_OF (can be respectful rivals)

**ENEMY_OF** (person ↔ person)
- **Usage:** Declared enmity (inimicitia)
- **Example:** `Cicero -[ENEMY_OF]-> Marc Antony`
- **Note:** Formal enmity with legal/social consequences

### Mentor-Student

**MENTOR_OF** (mentor → student)
- **Usage:** Educational or political mentorship
- **Example:** `Cicero -[MENTOR_OF]-> Octavian` (rhetoric training)
- **Temporal:** Duration of mentorship
- **Note:** Important for oratorical training

**MENTORED_BY** (student → mentor)
- **Usage:** Inverse of MENTOR_OF
- **Example:** `Octavian -[MENTORED_BY]-> Cicero`
- **Inverse:** MENTOR_OF

**FRIEND_OF** (person ↔ person)
- **Usage:** Amicitia (friendship with political implications)
- **Example:** `Caesar -[FRIEND_OF]-> Oppius`
- **Note:** In Roman context, friendship often means political alliance

---

## Affinal Relationships (Through Marriage)

**FATHER_IN_LAW_OF** / **SON_IN_LAW_OF** (directional)
- **Usage:** Relationship via child's marriage
- **Example:** `Caesar -[FATHER_IN_LAW_OF]-> Pompey` (via Julia's marriage)
- **Temporal:** Duration of marriage
- **Note:** Critical for political alliances

**BROTHER_IN_LAW_OF** / **SISTER_IN_LAW_OF** (symmetric)
- **Usage:** Spouse's sibling or sibling's spouse
- **Example:** `Clodius -[BROTHER_IN_LAW_OF]-> Cicero` (via sister Clodia's connection)

---

## Implementation Notes

### Directionality Rules

1. **Always specify from subject to object perspective**
   - ✅ `Caesar CHILD_OF Father` (Caesar is child)
   - ❌ `Caesar PARENT_OF Father` (incorrect direction)

2. **Create bidirectional claims for symmetric relationships**
   ```cypher
   // Marriage (create both)
   (Caesar)-[:MARRIED]->(Cornelia)
   (Cornelia)-[:MARRIED]->(Caesar)
   ```

3. **Use inverse relationships for query convenience**
   ```cypher
   // Parent-child (create both)
   (Caesar)-[:CHILD_OF]->(Father)
   (Father)-[:PARENT_OF]->(Caesar)
   ```

### Temporal Scope Requirements

**MUST include temporal_scope:**
- MARRIED (marriage year)
- ADOPTED_BY (adoption date)
- POLITICAL_ALLY_OF (alliance period)
- MENTOR_OF (mentorship period)

**OPTIONAL temporal_scope:**
- SIBLING_OF (from birth, implicit)
- MEMBER_OF_GENS (from birth/adoption)

**SHOULD include end_temporal_scope:**
- MARRIED (if divorced or widowed)
- POLITICAL_ALLY_OF (when alliance ended)

### Claim Creation Pattern

```cypher
// Example: Marriage relationship
(C_bio_marriage:FacetClaim {
  cipher: "fclaim_bio_marriage_001...",
  facet: "biographic",  // BiographicSFA owns this
  subject_node_id: "Q1048",  // Caesar
  property_path_id: "MARRIED",  // Canonical type
  object_node_id: "Q230677",  // Cornelia
  temporal_scope: "-0084",  // Marriage year
  end_temporal_scope: "-0069",  // Her death
  source_document_id: "Q1385",  // Suetonius
  assertion: "Caesar married Cornelia Cinna 84 BCE, marriage ended by her death 69 BCE"
})

// Reverse direction (bidirectional)
(C_bio_marriage_rev:FacetClaim {
  cipher: "fclaim_bio_marriage_001_rev...",
  facet: "biographic",
  subject_node_id: "Q230677",  // Cornelia
  property_path_id: "MARRIED",
  object_node_id: "Q1048",  // Caesar
  temporal_scope: "-0084",
  end_temporal_scope: "-0069",
  source_document_id: "Q1385"
})
```

---

## Query Patterns

### Find all direct family members

```cypher
MATCH (person:Human {qid: "Q1048"})  // Caesar
MATCH (person)-[r:CHILD_OF|PARENT_OF|SIBLING_OF|MARRIED|ADOPTED_BY|ADOPTED]->(relative:Human)
RETURN person, type(r) as relationship_type, relative
```

### Find ancestors (multi-generational)

```cypher
MATCH (person:Human {qid: "Q1048"})
MATCH path = (person)-[:CHILD_OF*1..5]->(ancestor:Human)
RETURN path, length(path) as generations
ORDER BY generations DESC
```

### Find gens members (clan structure)

```cypher
MATCH (person:Human {qid: "Q1048"})
MATCH (person)-[:MEMBER_OF_GENS]->(gens:Gens)
MATCH (gens_member:Human)-[:MEMBER_OF_GENS]->(gens)
RETURN gens.label, collect(gens_member.label) as members
```

### Find political network (alliances + family)

```cypher
MATCH (person:Human {qid: "Q1048"})
MATCH (person)-[r:POLITICAL_ALLY_OF|MARRIED|FATHER_IN_LAW_OF|PATRON_OF]-(connection:Human)
WHERE r.temporal_scope >= "-0060" AND r.temporal_scope <= "-0050"  // 60s BCE
RETURN person, r, connection
```

### Find family tree (stemma) 3 generations

```cypher
MATCH (person:Human {qid: "Q1048"})
// Parents
OPTIONAL MATCH (person)-[:CHILD_OF]->(parent:Human)
// Grandparents
OPTIONAL MATCH (parent)-[:CHILD_OF]->(grandparent:Human)
// Children
OPTIONAL MATCH (child:Human)-[:CHILD_OF]->(person)
// Grandchildren
OPTIONAL MATCH (grandchild:Human)-[:CHILD_OF]->(child)
RETURN person, parent, grandparent, child, grandchild
```

---

## Validation Rules

### Family Relationships

1. **No circular parentage**
   ```cypher
   // Check: person is not their own ancestor
   MATCH (person:Human)-[:CHILD_OF*1..10]->(person)
   RETURN "❌ VIOLATION: Circular parentage" as error
   ```

2. **Consistent sibling relationships**
   ```cypher
   // Check: if A sibling of B via shared parent, then B sibling of A
   MATCH (person_a:Human)-[:CHILD_OF]->(parent:Human)<-[:CHILD_OF]-(person_b:Human)
   WHERE NOT (person_a)-[:SIBLING_OF]-(person_b)
   RETURN "⚠️ WARNING: Missing sibling relationship" as warning
   ```

3. **Adoption creates gens membership**
   ```cypher
   // Check: adopted person has MEMBER_OF_GENS claim for adopter's gens
   MATCH (adopted:Human)-[:ADOPTED_BY]->(adopter:Human)
   MATCH (adopter)-[:MEMBER_OF_GENS]->(gens:Gens)
   WHERE NOT (adopted)-[:MEMBER_OF_GENS]->(gens)
   RETURN "⚠️ WARNING: Adopted person missing gens membership" as warning
   ```

### Temporal Consistency

1. **Marriage after birth**
   ```cypher
   MATCH (person:Human)-[:MARRIED {temporal_scope: $marriage_year}]->()
   MATCH (person)-[:BORN {temporal_scope: $birth_date}]
   WHERE toInteger($marriage_year) < toInteger(substring($birth_date, 0, 4))
   RETURN "❌ VIOLATION: Marriage before birth" as error
   ```

2. **Parent older than child**
   ```cypher
   MATCH (child:Human)-[:CHILD_OF]->(parent:Human)
   MATCH (child {birth_year: $child_birth}), (parent {birth_year: $parent_birth})
   WHERE $parent_birth >= $child_birth
   RETURN "❌ VIOLATION: Parent not older than child" as error
   ```

---

## Cross-Facet Usage

### BiographicSFA: Creates all relationship claims
```python
# BiographicSFA owns relationship creation
bio_claim = create_facet_claim(
    facet="biographic",
    subject="Q1048",  # Caesar
    property="MARRIED",  # Canonical type
    object="Q230677",  # Cornelia
    temporal_scope="-0084"
)
```

### PoliticalSFA: References family relationships for alliance analysis
```python
# PoliticalSFA analyzes political implications
pol_claim = create_facet_claim(
    facet="political",
    subject="Q188646",  # gens Julia
    property="ALLIED_TO",
    object="Q????",  # gens Cornelia
    temporal_scope="-0084",
    context_claims=[bio_claim.cipher]  # References marriage
)
```

### SocialSFA: References status via family connections
```python
# SocialSFA analyzes social class implications
social_claim = create_facet_claim(
    facet="social",
    subject="Q1048",
    property="MEMBER_OF_CLASS",
    object="Q2912932",  # senatorial order
    temporal_scope="-0069",  # From quaestorship
    context_claims=[parent_claim.cipher]  # Family background matters
)
```

---

## References

### Academic Sources
- **Prosopography:**
  - Nicolet, Claude. *The World of the Citizen in Republican Rome* (1980)
  - Wiseman, T.P. *New Men in the Roman Senate* (1971)
  
- **Roman Naming & Adoption:**
  - Salway, Benet. "What's in a Name? A Survey of Roman Onomastic Practice" (1994)
  - Lindsay, Hugh. *Adoption in the Roman World* (2009)

- **Patron-Client Relations:**
  - Brunt, P.A. "Clientela" in *The Fall of the Roman Republic* (1988)

### Digital Resources
- [Digital Prosopography of the Roman Republic (DPRR)](https://romanrepublic.ac.uk)
- [Broughton's Magistrates of the Roman Republic (MRR)](http://magistrates.atlas-consulum.com/)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-16 | Initial taxonomy definition |

---

**Maintained by:** BiographicSFA

**Questions/Updates:** Contact SCA for cross-facet coordination
