# Complete Examples for Obsidian

Copy these examples into Obsidian notes to build your knowledge graph documentation.

---

## Example 1: Battle of Pharsalus - Complete Walkthrough

### Claim Input

```
Source: Livy, Ab Urbe Condita, Book III
Claim: "The Battle of Pharsalus occurred in Thessaly during 48 BCE, where 
Pompey the Great was defeated by Caesar's forces."
Confidence: HIGH (primary historical source, widely accepted)
```

### LLM Extraction

**Entities extracted:**
- Event: Battle of Pharsalus (Q48314)
- Participant: Pompey the Great (Q101968)
- Participant: Julius Caesar (Q1048)
- Place: Thessaly (Q1359)
- Period: 48 BCE (-48)
- Citation: Livy, Ab Urbe Condita III.10 (Q191339)

**Relationships extracted:**
- Battle FOUGHT_IN Thessaly
- Battle DURING 48 BCE
- Pompey FOUGHT_IN Battle
- Caesar DEFEATED Pompey

**Confidence extracted:**
- Location confidence: 0.85 (primary source, archaeological support)
- Dates confidence: 0.95 (multiple sources agree)
- Participants: 0.95 (well-documented)

### Neo4j Creation

**Cypher statements:**

```cypher
// Create RelationshipType nodes from canonical types
MERGE (reltype_foughtin:RelationshipType {
  id: "Military_FOUGHT_IN",
  category: "Military",
  label: "Fought in",
  description: "Entity fought in battle",
  crm_property: "CRM_TOOK_PLACE_AT",
  lcsh_id: "sh85075661",
  specificity_level: 2
});

MERGE (reltype_defeated:RelationshipType {
  id: "Military_DEFEATED",
  category: "Military",
  label: "Defeated",
  description: "Defeated opponent in battle",
  crm_property: "CRM_AFFECTED",
  lcsh_id: "sh85075661",
  specificity_level: 3
});

// Create entity nodes
CREATE (battle:Event {
  qid: "Q48314",
  label: "Battle of Pharsalus",
  crm_class: "E5",
  unique_id: "EVENT_Q48314"
});

CREATE (place:Place {
  qid: "Q1359",
  label: "Thessaly",
  crm_class: "E53",
  unique_id: "PLACE_Q1359"
});

CREATE (period:Period {
  qid: "Q11761",
  label: "48 BCE",
  start_year: -48,
  end_year: -48,
  crm_class: "E2",
  unique_id: "PERIOD_48BCE"
});

CREATE (pompey:Person {
  qid: "Q101968",
  label: "Pompey the Great",
  crm_class: "E21",
  unique_id: "PERSON_Q101968"
});

CREATE (caesar:Person {
  qid: "Q1048",
  label: "Julius Caesar",
  crm_class: "E21",
  unique_id: "PERSON_Q1048"
});

// Create citation node
CREATE (citation:Citation {
  id: "livy_ab_urbe_condita_3_10",
  label: "Livy, Ab Urbe Condita, Book III, Chapter 10",
  qid: "Q191339",
  source_type: "primary_historical",
  reliability: "high",
  unique_id: "CITATION_livy_3_10"
});

// Create Belief nodes (reified relationships)
CREATE (belief_location:Belief {
  id: "belief_pharsalus_location",
  type_ref: "Military_FOUGHT_IN",
  statement: "Battle of Pharsalus fought in Thessaly",
  subject_qid: "Q48314",
  object_qid: "Q1359",
  confidence: 0.85,
  certainty: "probable",
  belief_level: "probable",
  status: "current",
  created_at: "2026-01-14T05:19:00Z"
});

CREATE (belief_date:Belief {
  id: "belief_pharsalus_date",
  type_ref: "Temporal_DURING",
  statement: "Battle of Pharsalus occurred in 48 BCE",
  subject_qid: "Q48314",
  object_qid: "-48",
  confidence: 0.95,
  certainty: "probable",
  belief_level: "probable",
  status: "current",
  created_at: "2026-01-14T05:19:00Z"
});

CREATE (belief_defeat:Belief {
  id: "belief_pompey_defeated",
  type_ref: "Military_DEFEATED",
  statement: "Pompey defeated by Caesar",
  subject_qid: "Q1048",
  object_qid: "Q101968",
  confidence: 0.92,
  certainty: "probable",
  belief_level: "probable",
  status: "current",
  created_at: "2026-01-14T05:19:00Z"
});

// Create Note node (caveat)
CREATE (note:Note {
  id: "note_pharsalus_location_alternative",
  text: "Some modern scholars argue Pharsalus may have occurred in Egypt, not Thessaly, though this is minority view",
  type: "caveat",
  source: "Modern historical scholarship debate",
  created_at: "2026-01-14T05:19:00Z"
});

// Create Subject node (LCSH classification)
CREATE (subject:Subject {
  lcsh_id: "sh85109289",
  lcsh_heading: "Punic Wars",
  label: "Punic Wars",
  qid: "Q40231",
  unique_id: "SUBJECT_sh85109289"
});

// Create Facet nodes
CREATE (milFacet:MilitaryFacet {
  unique_id: "MILITARY_FACET_conquest",
  label: "Conquest warfare",
  definition: "Warfare aimed at conquest and territorial control"
});

CREATE (polFacet:PoliticalFacet {
  unique_id: "POLITICAL_FACET_civil_war",
  label: "Civil conflict",
  definition: "Internal political conflicts within polity"
});

// Create CRM relationships (direct, formal)
CREATE (battle)-[:CRM_TOOK_PLACE_AT]->(place);
CREATE (battle)-[:CRM_HAS_TIMESPAN]->(period);
CREATE (pompey)-[:CRM_PARTICIPATED_IN]->(battle);
CREATE (caesar)-[:CRM_PARTICIPATED_IN]->(battle);

// Create Belief-based relationships (evidence-aware)
CREATE (battle)-[:CRM_BELIEF_OBJECT]->(belief_location);
CREATE (belief_location)-[:CRM_BELIEF_OBJECT]->(place);
CREATE (belief_location)-[:HAS_TYPE]->(reltype_foughtin);
CREATE (belief_location)-[:CRM_HAS_SOURCE]->(citation);
CREATE (belief_location)-[:MINF_HAS_NOTE]->(note);

CREATE (battle)-[:CRM_BELIEF_OBJECT]->(belief_date);
CREATE (belief_date)-[:CRM_BELIEF_OBJECT]->(period);

CREATE (caesar)-[:CRM_BELIEF_OBJECT]->(belief_defeat);
CREATE (belief_defeat)-[:CRM_BELIEF_OBJECT]->(pompey);
CREATE (belief_defeat)-[:HAS_TYPE]->(reltype_defeated);
CREATE (belief_defeat)-[:CRM_HAS_SOURCE]->(citation);

// Link to classification
CREATE (battle)-[:HAS_SUBJECT]->(subject);
CREATE (subject)-[:HAS_MILITARY_FACET]->(milFacet);
CREATE (subject)-[:HAS_POLITICAL_FACET]->(polFacet);
```

### Queries on this data

**Query 1: Simple - Where did the battle occur?**

```cypher
MATCH (e:Event {qid: "Q48314"})-[:CRM_TOOK_PLACE_AT]->(p:Place)
RETURN e.label, p.label
// Result: Battle of Pharsalus | Thessaly
```

**Query 2: With Confidence - How confident are we?**

```cypher
MATCH (e:Event {qid: "Q48314"})-[:CRM_BELIEF_OBJECT]->(b:Belief)-[:CRM_BELIEF_OBJECT]->(p:Place)
WHERE b.confidence >= 0.8
RETURN e.label, p.label, b.confidence, b.certainty
// Result: Battle of Pharsalus | Thessaly | 0.85 | probable
```

**Query 3: With Evidence - What's the source?**

```cypher
MATCH (e:Event {qid: "Q48314"})-[:CRM_BELIEF_OBJECT]->(b:Belief)-[:CRM_HAS_SOURCE]->(c:Citation)
RETURN e.label, b.statement, c.label, b.confidence
// Result: Battle of Pharsalus | Battle fought in Thessaly | Livy, Ab Urbe Condita III.10 | 0.85
```

**Query 4: With Caveats - Any disputes?**

```cypher
MATCH (e:Event {qid: "Q48314"})-[:CRM_BELIEF_OBJECT]->(b:Belief)-[:MINF_HAS_NOTE]->(n:Note {type: "caveat"})
RETURN e.label, b.statement, n.text
// Result: Battle of Pharsalus | Battle fought in Thessaly | Some modern scholars argue...
```

**Query 5: All military events in this period**

```cypher
MATCH (e:Event)-[:CRM_HAS_TIMESPAN]->(:Period {start_year: -48})
MATCH (e)-[:HAS_SUBJECT]->(:Subject)-[:HAS_MILITARY_FACET]->(mf:MilitaryFacet)
RETURN e.label, e.qid, mf.label
// Result: Battle of Pharsalus | Q48314 | Conquest warfare
```

**Query 6: Compare old vs new belief about location**

```cypher
MATCH (old:Belief {status: "superseded"})-[:MINF_REPLACED_BY]->(new:Belief {status: "current"})
WHERE old.statement CONTAINS "Pharsalus"
RETURN old.statement, new.statement, old.confidence, new.confidence
// Result: (If we had old belief) Pharsalus in Egypt | Pharsalus in Thessaly | 0.3 | 0.85
```

---

## Example 2: Roman Republic - Multiple Relationships

### Scenario

The Roman Republic involved multiple concurrent relationships:
- **Political**: Republican government form
- **Military**: Conquest and warfare
- **Economic**: Trade and taxation
- **Social**: Patron-client relationships

### Multi-faceted Graph

```cypher
// Entity: Roman Republic
CREATE (rome_rep:Period {
  qid: "Q17167",
  label: "Roman Republic",
  start_year: -510,
  end_year: -27,
  crm_class: "E2",
  unique_id: "PERIOD_Q17167"
});

// Multiple relationships with same entity

// POLITICAL relationship
CREATE (belief_gov:Belief {
  id: "belief_rome_republic_government",
  statement: "Rome governed as a republic",
  confidence: 0.98,
  type_ref: "Political_GOVERNED_AS"
});

// MILITARY relationship
CREATE (belief_military:Belief {
  id: "belief_rome_expansion_conquest",
  statement: "Rome expanded through military conquest",
  confidence: 0.95,
  type_ref: "Military_CONQUERED"
});

// ECONOMIC relationship
CREATE (belief_trade:Belief {
  id: "belief_rome_trade_network",
  statement: "Rome dominated Mediterranean trade",
  confidence: 0.90,
  type_ref: "Economic_CONTROLLED_TRADE"
});

// SOCIAL relationship
CREATE (belief_social:Belief {
  id: "belief_rome_patron_client",
  statement: "Roman society organized by patron-client ties",
  confidence: 0.85,
  type_ref: "Social_PATRON_CLIENT"
});

// Create facets
CREATE (pol_facet:PoliticalFacet {unique_id: "POLITICAL_FACET_republican", label: "Republican government"});
CREATE (mil_facet:MilitaryFacet {unique_id: "MILITARY_FACET_conquest", label: "Conquest warfare"});
CREATE (econ_facet:EconomicFacet {unique_id: "ECONOMIC_FACET_trade", label: "Trade control"});
CREATE (soc_facet:SocialFacet {unique_id: "SOCIAL_FACET_patronage", label: "Patron-client networks"});

// Create subject
CREATE (subj:Subject {lcsh_id: "sh85115055", label: "Rome--History--Republic"});

// Link everything
CREATE (rome_rep)-[:HAS_SUBJECT]->(subj);
CREATE (subj)-[:HAS_POLITICAL_FACET]->(pol_facet);
CREATE (subj)-[:HAS_MILITARY_FACET]->(mil_facet);
CREATE (subj)-[:HAS_ECONOMIC_FACET]->(econ_facet);
CREATE (subj)-[:HAS_SOCIAL_FACET]->(soc_facet);

CREATE (rome_rep)-[:CRM_BELIEF_OBJECT]->(belief_gov);
CREATE (rome_rep)-[:CRM_BELIEF_OBJECT]->(belief_military);
CREATE (rome_rep)-[:CRM_BELIEF_OBJECT]->(belief_trade);
CREATE (rome_rep)-[:CRM_BELIEF_OBJECT]->(belief_social);
```

### Query: Multi-perspective view

```cypher
// Get all perspectives on Roman Republic
MATCH (p:Period {qid: "Q17167"})-[:HAS_SUBJECT]->(s:Subject)
MATCH (s)-[:HAS_MILITARY_FACET]->(mf:MilitaryFacet)
MATCH (s)-[:HAS_POLITICAL_FACET]->(pf:PoliticalFacet)
MATCH (s)-[:HAS_ECONOMIC_FACET]->(ef:EconomicFacet)
MATCH (s)-[:HAS_SOCIAL_FACET]->(sf:SocialFacet)
RETURN 
  p.label as period,
  pf.label as political_aspect,
  mf.label as military_aspect,
  ef.label as economic_aspect,
  sf.label as social_aspect
```

---

## Example 3: Belief Revision - Caesar's Birthplace

### Original Claim (Ancient)

```
Source: Various ancient texts
Claim: "Caesar born in Rome"
Status: Historical consensus, high confidence
```

### Modern Revision

```
Source: Modern epigraphic evidence
Claim: "Caesar born in Rome, specifically in Subura district"
Status: More specific, higher precision
Revision: Refinement rather than contradiction
```

### Graph Implementation

```cypher
// Old belief (still recorded for history)
CREATE (old_belief:Belief {
  id: "belief_caesar_birthplace_old",
  statement: "Julius Caesar born in Rome",
  confidence: 0.95,
  certainty: "probable",
  status: "superseded",
  source: "Ancient texts - Suetonius",
  created_at: "1900-01-01"
});

// New belief (current understanding)
CREATE (new_belief:Belief {
  id: "belief_caesar_birthplace_new",
  statement: "Julius Caesar born in Rome, Subura district",
  confidence: 0.98,
  certainty: "probable",
  status: "current",
  source: "Epigraphic evidence, modern scholarship",
  created_at: "2000-01-01"
});

// Link: old belief was replaced by new belief
CREATE (old_belief)-[:MINF_REPLACED_BY]->(new_belief);

// Add context notes
CREATE (note1:Note {
  text: "Ancient sources did not specify district",
  type: "caveat"
});

CREATE (note2:Note {
  text: "Epigraphic evidence from Subura narrowed location",
  type: "refinement"
});

CREATE (old_belief)-[:MINF_HAS_NOTE]->(note1);
CREATE (new_belief)-[:MINF_HAS_NOTE]->(note2);
```

### Query: Show belief evolution

```cypher
MATCH (old:Belief {status: "superseded"})-[:MINF_REPLACED_BY]->(new:Belief {status: "current"})
WHERE old.statement CONTAINS "Caesar"
MATCH (old)-[:MINF_HAS_NOTE]->(old_note)
MATCH (new)-[:MINF_HAS_NOTE]->(new_note)
RETURN 
  old.statement as original_belief,
  old.confidence as old_confidence,
  new.statement as current_belief,
  new.confidence as new_confidence,
  old_note.text as why_superseded,
  new_note.text as why_updated
```

**Result:**

| original_belief | old_confidence | current_belief | new_confidence | why_superseded | why_updated |
|---|---|---|---|---|---|
| Julius Caesar born in Rome | 0.95 | Julius Caesar born in Rome, Subura district | 0.98 | Ancient sources did not specify district | Epigraphic evidence from Subura narrowed location |

---

## Example 4: Agent Routing via Facets

### Military Historian Agent

```cypher
// Military historian looking for battles
MATCH (facet:MilitaryFacet)
MATCH (subj:Subject)-[:HAS_MILITARY_FACET]->(facet)
MATCH (entity)-[:HAS_SUBJECT]->(subj)
MATCH (entity)-[:CRM_BELIEF_OBJECT]->(b:Belief)
WHERE b.confidence >= 0.8  // Only high-confidence beliefs
RETURN 
  entity.label,
  entity.qid,
  b.statement,
  b.confidence,
  facet.label as military_aspect
LIMIT 20
```

### Political Scientist Agent

```cypher
// Political scientist looking for governance
MATCH (facet:PoliticalFacet)
MATCH (subj:Subject)-[:HAS_POLITICAL_FACET]->(facet)
MATCH (entity)-[:HAS_SUBJECT]->(subj)
MATCH (entity)-[:CRM_BELIEF_OBJECT]->(b:Belief)
WHERE b.confidence >= 0.75  // Slightly lower bar
RETURN 
  entity.label,
  b.statement,
  b.confidence,
  facet.label as political_aspect
ORDER BY b.confidence DESC
```

### Uncertain Claims Agent

```cypher
// Agent looking for disputed or uncertain claims
MATCH (b:Belief)-[:MINF_HAS_NOTE]->(n:Note {type: "caveat"})
WHERE b.confidence < 0.8
MATCH (e)-[:CRM_BELIEF_OBJECT]->(b)
RETURN 
  e.label,
  b.statement,
  b.confidence,
  n.text as caveat
ORDER BY b.confidence ASC
LIMIT 10
```

---

## Example 5: LCSH/FAST Integration Example

### AIDS Disease - Multiple Subdivisions

```
LCSH Heading: AIDS (Disease)
LCSH ID: sh85002541
FAST ID: fst00794380
QID: Q12199

Subdivisions:
- $x: Epidemiology (→ ScientificFacet)
- $x: Prevention (→ MilitaryFacet - metaphorically)
- $x: Transmission (→ ScientificFacet)
- $y: 20th century (→ Period node)
- $z: United States (→ Place node)
- $v: Statistics (→ form/genre)
```

### Graph Implementation

```cypher
// Subject node (LCSH backbone)
CREATE (subj:Subject {
  lcsh_id: "sh85002541",
  qid: "Q12199",
  label: "AIDS (Disease)",
  lcsh_heading: "AIDS (Disease)",
  scope_note: "Use for works on the infectious disease AIDS (Acquired Immunodeficiency Syndrome)"
});

// Facet nodes (from subdivisions)
CREATE (sci_facet:ScientificFacet {
  unique_id: "SCIENTIFIC_FACET_epidemiology",
  label: "Epidemiology",
  definition: "Study of disease distribution and determinants"
});

CREATE (soc_facet:SocialFacet {
  unique_id: "SOCIAL_FACET_public_health",
  label: "Public Health",
  definition: "Public health responses and initiatives"
});

// Temporal and geographic scope
CREATE (period:Period {
  label: "20th century",
  start_year: 1900,
  end_year: 2000
});

CREATE (place:Place {
  qid: "Q30",
  label: "United States",
  crm_class: "E53"
});

// Link everything
CREATE (subj)-[:HAS_SCIENTIFIC_FACET]->(sci_facet);
CREATE (subj)-[:HAS_SOCIAL_FACET]->(soc_facet);
CREATE (subj)-[:HAS_TEMPORAL_CONTEXT]->(period);
CREATE (subj)-[:HAS_GEOGRAPHIC_CONTEXT]->(place);

// Create broader/narrower hierarchy
CREATE (broader:Subject {lcsh_id: "sh85008859", label: "Communicable diseases"});
CREATE (narrower:Subject {lcsh_id: "sh85002542", label: "AIDS--Transmission"});

CREATE (subj)-[:BROADER_THAN]->(broader);
CREATE (subj)-[:NARROWER_THAN]->(narrower);
```

### Query: Scientific research on AIDS epidemiology

```cypher
MATCH (subj:Subject {lcsh_id: "sh85002541"})-[:HAS_SCIENTIFIC_FACET]->(sf:ScientificFacet)
MATCH (subj)-[:HAS_GEOGRAPHIC_CONTEXT]->(place)
MATCH (subj)-[:HAS_TEMPORAL_CONTEXT]->(period)
RETURN 
  subj.lcsh_heading,
  sf.label as research_focus,
  place.label as geographic_scope,
  period.label as time_period
```

---

## Copy-Paste Template: Your Own Entity

Use this template to create entries for any historical entity:

```cypher
// Step 1: Create main entity node
CREATE (entity:Event {  // or Person, Place, Period, etc.
  qid: "Q[ID]",
  label: "[Display Name]",
  crm_class: "[E2|E5|E21|E53|etc]",
  unique_id: "[TYPE]_[QID]"
});

// Step 2: Create relationship types involved
MERGE (reltype:RelationshipType {
  id: "[Category]_[RELATIONTYPE]",
  category: "[Category]",
  label: "[Human readable]"
});

// Step 3: Create Belief node for each relationship
CREATE (belief:Belief {
  id: "belief_[description]",
  type_ref: "[Category]_[RELATIONTYPE]",
  statement: "[The claim]",
  confidence: [0.0-1.0],
  certainty: "probable|certain|speculative",
  status: "current|superseded"
});

// Step 4: Create Citation node (evidence)
CREATE (citation:Citation {
  id: "[source_id]",
  label: "[Source title]",
  source_type: "primary|secondary|tertiary",
  reliability: "high|medium|low"
});

// Step 5: Create Note node (optional caveat)
CREATE (note:Note {
  id: "note_[description]",
  text: "[The caveat or explanation]",
  type: "caveat|note|alternative|revision"
});

// Step 6: Link everything
CREATE (entity)-[:CRM_BELIEF_OBJECT]->(belief);
CREATE (belief)-[:CRM_BELIEF_OBJECT]->(target_entity);
CREATE (belief)-[:HAS_TYPE]->(reltype);
CREATE (belief)-[:CRM_HAS_SOURCE]->(citation);
CREATE (belief)-[:MINF_HAS_NOTE]->(note);

// Step 7: Add subject classification
CREATE (subject:Subject {lcsh_id: "sh[ID]", label: "[Topic]"});
CREATE (entity)-[:HAS_SUBJECT]->(subject);

// Step 8: Add facets
CREATE (facet:FacetType {unique_id: "[FACET]_[description]", label: "[Label]"});
CREATE (subject)-[:HAS_[FACET]_FACET]->(facet);
```

---

## Usage Instructions

1. **Copy diagrams** into Obsidian notes
2. **Use template** for new entities
3. **Run examples** in your Neo4j browser
4. **Build queries** from patterns shown
5. **Link Obsidian notes** for navigation

Example Obsidian structure:
```
├─ Knowledge Graph/
│  ├─ Conceptual Model.md (all Mermaid diagrams)
│  ├─ Examples.md (this file)
│  ├─ Battle of Pharsalus.md (entity-specific)
│  ├─ Roman Republic.md
│  ├─ Query Patterns.md
│  └─ Implementation Guide.md
```
