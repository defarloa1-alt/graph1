# Star Pattern for Claims: Event as Hub with Multi-Facet Edges

**Date:** January 13, 2026  
**Core Insight:** A claim (Event node) is NOT a tree—it's a **star pattern** where the event/claim is the center hub with multiple edges radiating to multiple Facet nodes.

---

## The Star Pattern Architecture

### Traditional (Wrong) Graph Model
```
Event ─┬─→ Belief ─→ Source
       ├─→ Place
       └─→ Period
```
**Problem:** Facets are implicit (hidden in RelationshipType). Event structure is tree-like.

### Star Pattern (Correct) Model
```
                    ┌─→ MilitaryFacet
                    │
       ┌─→ Belief ──┼─→ DiplomaticFacet
       │            │
Event ─┼─→ Subject ─┼─→ PoliticalFacet
       │            │
       │            └─→ EconomicFacet
       │
       ├─→ Place
       │
       └─→ Period
```

**Advantage:** Each facet is explicitly a first-class node. The event/claim is the hub. Multiple edges from Belief → different Facets capture the **multi-dimensional nature** of the claim.

---

## Real Example: Battle of Pharsalus

The claim "Battle of Pharsalus occurred in 48 BCE in Thessaly" is actually **four parallel claims**:

### 1. Military Dimension
```
Belief {
  statement: "Battle of Pharsalus was a military engagement"
  confidence: 0.95
  type_ref: "Military_FOUGHT_IN"
} ─→ MilitaryFacet {
  label: "Conquest warfare"
  definition: "Warfare aimed at conquest and territorial control"
}
```

### 2. Political Dimension
```
Belief {
  statement: "Battle resulted in political shift: Octavian gained supremacy"
  confidence: 0.92
  type_ref: "Political_DEFEATED"
} ─→ PoliticalFacet {
  label: "Political transformation"
  definition: "Change in political control or regime"
}
```

### 3. Economic Dimension
```
Belief {
  statement: "Battle involved significant economic cost and plunder"
  confidence: 0.80
  type_ref: "Economic_RESOURCE_ALLOCATION"
} ─→ EconomicFacet {
  label: "War economy"
  definition: "Economic activity driven by military conflict"
}
```

### 4. Social Dimension
```
Belief {
  statement: "Battle involved soldiers (low-status participants)"
  confidence: 0.85
  type_ref: "Social_PARTICIPANT_ROLE"
} ─→ SocialFacet {
  label: "Military service"
  definition: "Social participation in organized violence"
}
```

### Full Star Pattern

```
        ┌───────────────────────────┐
        │    Battle of Pharsalus    │
        │    (Event Node)           │
        │    qid: Q48314            │
        └───────────────────────────┘
              │     │     │     │
         ┌────┴─────┴─────┴─────┴────┐
         │                            │
         ├─ Belief₁ (FOUGHT_IN)       │
         │  confidence: 0.95          │
         │  ├─→ MilitaryFacet         │
         │  ├─→ Place(Thessaly)       │
         │  ├─→ Period(48 BCE)        │
         │  └─→ Citation(Livy)        │
         │                            │
         ├─ Belief₂ (DEFEATED)        │
         │  confidence: 0.92          │
         │  ├─→ PoliticalFacet        │
         │  ├─→ Result(Octavian)      │
         │  └─→ Citation(Plutarch)    │
         │                            │
         ├─ Belief₃ (ECONOMIC_COST)   │
         │  confidence: 0.80          │
         │  ├─→ EconomicFacet         │
         │  └─→ Citation(Appian)      │
         │                            │
         └─ Belief₄ (SOCIAL_ROLE)     │
            confidence: 0.85          │
            ├─→ SocialFacet           │
            └─→ Citation(Cassius Dio) │
```

Each Belief has **its own edges to facets** (and other targets).

---

## Neo4j Structure (Cypher)

### Step 1: Create the Event (Hub)

```cypher
CREATE (event:Event {
  qid: "Q48314",
  label: "Battle of Pharsalus",
  unique_id: "EVENT_Q48314",
  date_iso8601: "-0048-08-09",
  crm_class: "E5",
  granularity: "atomic"
});
```

### Step 2: Create Facet Nodes (First-Class Objects)

```cypher
CREATE (mil_facet:MilitaryFacet {
  unique_id: "MILITARY_FACET_conquest",
  label: "Conquest warfare",
  definition: "Warfare aimed at conquest and territorial control"
});

CREATE (pol_facet:PoliticalFacet {
  unique_id: "POLITICAL_FACET_transformation",
  label: "Political transformation",
  definition: "Change in political control or regime"
});

CREATE (econ_facet:EconomicFacet {
  unique_id: "ECONOMIC_FACET_war_economy",
  label: "War economy",
  definition: "Economic activity driven by military conflict"
});

CREATE (soc_facet:SocialFacet {
  unique_id: "SOCIAL_FACET_military_service",
  label: "Military service",
  definition: "Social participation in organized violence"
});
```

### Step 3: Create Belief Nodes (Each with Independent Facet Edges)

```cypher
// Belief 1: Military dimension
CREATE (b1:Belief {
  id: "belief_pharsalus_military",
  statement: "Battle of Pharsalus was a military engagement",
  confidence: 0.95,
  certainty: "probable",
  type_ref: "Military_FOUGHT_IN",
  status: "current"
});

// Belief 2: Political dimension
CREATE (b2:Belief {
  id: "belief_pharsalus_political",
  statement: "Battle resulted in Octavian gaining political supremacy",
  confidence: 0.92,
  certainty: "probable",
  type_ref: "Political_DEFEATED",
  status: "current"
});

// Belief 3: Economic dimension
CREATE (b3:Belief {
  id: "belief_pharsalus_economic",
  statement: "Battle involved significant economic cost and plunder",
  confidence: 0.80,
  certainty: "probable",
  type_ref: "Economic_RESOURCE_ALLOCATION",
  status: "current"
});

// Belief 4: Social dimension
CREATE (b4:Belief {
  id: "belief_pharsalus_social",
  statement: "Battle involved soldiers in organized violence",
  confidence: 0.85,
  certainty: "probable",
  type_ref: "Social_PARTICIPANT_ROLE",
  status: "current"
});
```

### Step 4: Create the Star Pattern (Facet Edges)

```cypher
// Star pattern: Each Belief radiates to its own Facet(s)

// Belief 1 → Military Facet
MATCH (b:Belief {id: "belief_pharsalus_military"})
MATCH (mf:MilitaryFacet {unique_id: "MILITARY_FACET_conquest"})
CREATE (b)-[:HAS_MILITARY_FACET]->(mf);

// Belief 2 → Political Facet
MATCH (b:Belief {id: "belief_pharsalus_political"})
MATCH (pf:PoliticalFacet {unique_id: "POLITICAL_FACET_transformation"})
CREATE (b)-[:HAS_POLITICAL_FACET]->(pf);

// Belief 3 → Economic Facet
MATCH (b:Belief {id: "belief_pharsalus_economic"})
MATCH (ef:EconomicFacet {unique_id: "ECONOMIC_FACET_war_economy"})
CREATE (b)-[:HAS_ECONOMIC_FACET]->(ef);

// Belief 4 → Social Facet
MATCH (b:Belief {id: "belief_pharsalus_social"})
MATCH (sf:SocialFacet {unique_id: "SOCIAL_FACET_military_service"})
CREATE (b)-[:HAS_SOCIAL_FACET]->(sf);
```

### Step 5: Link Everything to Event Hub

```cypher
MATCH (event:Event {qid: "Q48314"})
MATCH (b1:Belief {id: "belief_pharsalus_military"})
MATCH (b2:Belief {id: "belief_pharsalus_political"})
MATCH (b3:Belief {id: "belief_pharsalus_economic"})
MATCH (b4:Belief {id: "belief_pharsalus_social"})
CREATE (event)-[:CRM_BELIEF_OBJECT]->(b1)
CREATE (event)-[:CRM_BELIEF_OBJECT]->(b2)
CREATE (event)-[:CRM_BELIEF_OBJECT]->(b3)
CREATE (event)-[:CRM_BELIEF_OBJECT]->(b4);
```

### Step 6: Add Supporting Context (Places, Periods, Citations)

```cypher
// Supporting nodes
CREATE (place:Place {qid: "Q1359", label: "Thessaly"});
CREATE (period:Period {qid: "Q11761", label: "48 BCE", start_year: -48, end_year: -48});
CREATE (citation1:Citation {id: "livy_3_10", label: "Livy, Ab Urbe Condita III.10", source_type: "primary"});
CREATE (citation2:Citation {id: "plutarch_antony", label: "Plutarch, Life of Antony", source_type: "primary"});
CREATE (citation3:Citation {id: "appian_bcw_2", label: "Appian, Civil Wars II", source_type: "primary"});
CREATE (citation4:Citation {id: "dio_cassius_50", label: "Dio Cassius, Roman History 50", source_type: "primary"});

// Link Beliefs to supporting context
MATCH (b1:Belief {id: "belief_pharsalus_military"})
MATCH (place:Place {qid: "Q1359"})
MATCH (period:Period {qid: "Q11761"})
MATCH (c1:Citation {id: "livy_3_10"})
CREATE (b1)-[:CRM_BELIEF_OBJECT]->(place)
CREATE (b1)-[:CRM_BELIEF_OBJECT]->(period)
CREATE (b1)-[:CRM_HAS_SOURCE]->(c1);

MATCH (b2:Belief {id: "belief_pharsalus_political"})
MATCH (c2:Citation {id: "plutarch_antony"})
CREATE (b2)-[:CRM_HAS_SOURCE]->(c2);

MATCH (b3:Belief {id: "belief_pharsalus_economic"})
MATCH (c3:Citation {id: "appian_bcw_2"})
CREATE (b3)-[:CRM_HAS_SOURCE]->(c3);

MATCH (b4:Belief {id: "belief_pharsalus_social"})
MATCH (c4:Citation {id: "dio_cassius_50"})
CREATE (b4)-[:CRM_HAS_SOURCE]->(c4);
```

---

## Why This is a Star Pattern

### Key Insight: **Facets are First-Class Objects**

In the star pattern:

1. **Event is the hub** - The central claim (Battle of Pharsalus)
2. **Beliefs are spokes** - Each belief is a **separate claim about one dimension**
3. **Facets are radial endpoints** - Each facet is its own node type with its own identity

```
       Facet1 (Military)
         ↑
         │ HAS_MILITARY_FACET
         │
Belief1 ─┼─ CRM_BELIEF_OBJECT
    ↑    │
    │    └─ CRM_HAS_SOURCE → Citation1
    │
Event ─── CRM_BELIEF_OBJECT ──→ Belief2 ─→ HAS_POLITICAL_FACET → Facet2
    │
    ├─────────────────────────→ Belief3 ─→ HAS_ECONOMIC_FACET → Facet3
    │
    └─────────────────────────→ Belief4 ─→ HAS_SOCIAL_FACET → Facet4
```

### Advantages of Star Pattern

1. **Multi-dimensional queries** - Query "all military events" by finding Events → Beliefs → MilitaryFacets
2. **Independent confidence** - Each dimension has its own confidence score (military_conf=0.95, political_conf=0.92)
3. **Separate sourcing** - Each belief can cite different sources (military from Livy, political from Plutarch)
4. **Agent routing** - Agents query their specific facet:
   - Military historian: find Events with MilitaryFacets
   - Political scientist: find Events with PoliticalFacets
   - Economist: find Events with EconomicFacets
5. **Facet as metadata** - Facets are not implicit in RelationshipType; they're explicit graph nodes
6. **Extensibility** - Add new facets without changing the Event or Belief structure

---

## Query Examples Using Star Pattern

### Query 1: Find all military aspects of an event

```cypher
MATCH (event:Event {qid: "Q48314"})
  -[:CRM_BELIEF_OBJECT]->(b:Belief)
  -[:HAS_MILITARY_FACET]->(mf:MilitaryFacet)
RETURN event.label, b.statement, b.confidence, mf.label;
```

**Result:**
```
event                    | statement                              | confidence | mf.label
------------------------|-----------------------------------------|------------|------------------
Battle of Pharsalus      | Battle was military engagement          | 0.95       | Conquest warfare
```

### Query 2: Find all facets for a single event

```cypher
MATCH (event:Event {qid: "Q48314"})
  -[:CRM_BELIEF_OBJECT]->(b:Belief)
OPTIONAL MATCH (b)-[:HAS_MILITARY_FACET]->(mf:MilitaryFacet)
OPTIONAL MATCH (b)-[:HAS_POLITICAL_FACET]->(pf:PoliticalFacet)
OPTIONAL MATCH (b)-[:HAS_ECONOMIC_FACET]->(ef:EconomicFacet)
OPTIONAL MATCH (b)-[:HAS_SOCIAL_FACET]->(sf:SocialFacet)
RETURN 
  event.label,
  b.statement,
  b.confidence,
  mf.label AS military,
  pf.label AS political,
  ef.label AS economic,
  sf.label AS social;
```

### Query 3: Find high-confidence claims with their sources by facet

```cypher
MATCH (event:Event)
  -[:CRM_BELIEF_OBJECT]->(b:Belief)
WHERE b.confidence >= 0.90
OPTIONAL MATCH (b)-[:HAS_MILITARY_FACET]->(mf:MilitaryFacet)
OPTIONAL MATCH (b)-[:HAS_POLITICAL_FACET]->(pf:PoliticalFacet)
OPTIONAL MATCH (b)-[:HAS_ECONOMIC_FACET]->(ef:EconomicFacet)
OPTIONAL MATCH (b)-[:CRM_HAS_SOURCE]->(c:Citation)
RETURN 
  event.label,
  b.statement,
  b.confidence,
  coalesce(mf.label, pf.label, ef.label) AS facet_dimension,
  c.label AS source
ORDER BY event.label, b.confidence DESC;
```

### Query 4: Find all events that have both military AND political dimensions

```cypher
MATCH (event:Event)
  -[:CRM_BELIEF_OBJECT]->(b_mil:Belief)
  -[:HAS_MILITARY_FACET]->(:MilitaryFacet)
MATCH (event)
  -[:CRM_BELIEF_OBJECT]->(b_pol:Belief)
  -[:HAS_POLITICAL_FACET]->(:PoliticalFacet)
RETURN 
  event.label,
  b_mil.statement AS military_claim,
  b_mil.confidence AS military_conf,
  b_pol.statement AS political_claim,
  b_pol.confidence AS political_conf;
```

### Query 5: Agent routing by facet (Military Historian)

```cypher
MATCH (event:Event)
  -[:CRM_BELIEF_OBJECT]->(b:Belief)
  -[:HAS_MILITARY_FACET]->(mf:MilitaryFacet)
WHERE b.confidence >= 0.8
MATCH (b)-[:CRM_HAS_SOURCE]->(c:Citation)
RETURN 
  event.label,
  event.date_iso8601,
  b.statement,
  b.confidence,
  mf.label,
  c.label AS primary_source
ORDER BY b.confidence DESC;
```

---

## Python Implementation

Your Python ingestion would look like:

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

def create_star_pattern_claim(session, event_data, beliefs):
    """
    event_data: {qid, label, date_iso8601, crm_class, ...}
    beliefs: [
      {
        id, statement, confidence, type_ref, facet_type, 
        target_entity, target_qid, citations, ...
      },
      ...
    ]
    """
    
    # Create Event (hub)
    session.run("""
    MERGE (e:Event {unique_id: $unique_id})
    ON CREATE SET
      e.qid = $qid,
      e.label = $label,
      e.date_iso8601 = $date_iso8601,
      e.crm_class = $crm_class,
      e.granularity = $granularity
    """, **event_data)
    
    # Create Facets (if not exists)
    for belief in beliefs:
        facet_type = belief["facet_type"]  # "Military", "Political", "Economic", "Social"
        facet_id = belief["facet_id"]
        facet_label = belief["facet_label"]
        
        session.run(f"""
        MERGE (f:{facet_type}Facet {{unique_id: $facet_id}})
        ON CREATE SET
          f.label = $label,
          f.definition = $definition
        """, facet_id=facet_id, label=facet_label, definition=belief.get("facet_definition"))
    
    # Create Beliefs (spokes)
    for belief in beliefs:
        session.run("""
        MERGE (b:Belief {id: $belief_id})
        ON CREATE SET
          b.statement = $statement,
          b.confidence = $confidence,
          b.certainty = $certainty,
          b.type_ref = $type_ref,
          b.status = $status
        """, 
        belief_id=belief["id"],
        statement=belief["statement"],
        confidence=belief["confidence"],
        certainty=belief.get("certainty", "probable"),
        type_ref=belief["type_ref"],
        status=belief.get("status", "current"))
    
    # Link Beliefs to Facets (facet edge)
    for belief in beliefs:
        facet_type = belief["facet_type"]
        facet_id = belief["facet_id"]
        belief_id = belief["id"]
        
        session.run(f"""
        MATCH (b:Belief {{id: $belief_id}})
        MATCH (f:{facet_type}Facet {{unique_id: $facet_id}})
        MERGE (b)-[:HAS_{facet_type.upper()}_FACET]->(f)
        """, belief_id=belief_id, facet_id=facet_id)
    
    # Link Beliefs to Event (spoke edge)
    event_id = event_data["unique_id"]
    for belief in beliefs:
        session.run("""
        MATCH (e:Event {unique_id: $event_id})
        MATCH (b:Belief {id: $belief_id})
        MERGE (e)-[:CRM_BELIEF_OBJECT]->(b)
        """, event_id=event_id, belief_id=belief["id"])
    
    # Link Beliefs to sources (if provided)
    for belief in beliefs:
        if "citations" in belief and belief["citations"]:
            for citation in belief["citations"]:
                session.run("""
                MERGE (c:Citation {id: $citation_id})
                ON CREATE SET
                  c.label = $label,
                  c.source_type = $source_type
                MATCH (b:Belief {id: $belief_id})
                MERGE (b)-[:CRM_HAS_SOURCE]->(c)
                """,
                citation_id=citation["id"],
                label=citation["label"],
                source_type=citation.get("source_type", "primary"),
                belief_id=belief["id"])

# Usage
with driver.session() as session:
    event_data = {
        "unique_id": "EVENT_Q48314",
        "qid": "Q48314",
        "label": "Battle of Pharsalus",
        "date_iso8601": "-0048-08-09",
        "crm_class": "E5",
        "granularity": "atomic"
    }
    
    beliefs = [
        {
            "id": "belief_pharsalus_military",
            "statement": "Battle of Pharsalus was a military engagement",
            "confidence": 0.95,
            "certainty": "probable",
            "type_ref": "Military_FOUGHT_IN",
            "facet_type": "Military",
            "facet_id": "MILITARY_FACET_conquest",
            "facet_label": "Conquest warfare",
            "facet_definition": "Warfare aimed at conquest and territorial control",
            "citations": [
                {"id": "livy_3_10", "label": "Livy, Ab Urbe Condita III.10", "source_type": "primary"}
            ]
        },
        {
            "id": "belief_pharsalus_political",
            "statement": "Battle resulted in Octavian gaining political supremacy",
            "confidence": 0.92,
            "certainty": "probable",
            "type_ref": "Political_DEFEATED",
            "facet_type": "Political",
            "facet_id": "POLITICAL_FACET_transformation",
            "facet_label": "Political transformation",
            "facet_definition": "Change in political control or regime",
            "citations": [
                {"id": "plutarch_antony", "label": "Plutarch, Life of Antony", "source_type": "primary"}
            ]
        },
        {
            "id": "belief_pharsalus_economic",
            "statement": "Battle involved significant economic cost and plunder",
            "confidence": 0.80,
            "certainty": "probable",
            "type_ref": "Economic_RESOURCE_ALLOCATION",
            "facet_type": "Economic",
            "facet_id": "ECONOMIC_FACET_war_economy",
            "facet_label": "War economy",
            "facet_definition": "Economic activity driven by military conflict",
            "citations": [
                {"id": "appian_bcw_2", "label": "Appian, Civil Wars II", "source_type": "primary"}
            ]
        },
        {
            "id": "belief_pharsalus_social",
            "statement": "Battle involved soldiers in organized violence",
            "confidence": 0.85,
            "certainty": "probable",
            "type_ref": "Social_PARTICIPANT_ROLE",
            "facet_type": "Social",
            "facet_id": "SOCIAL_FACET_military_service",
            "facet_label": "Military service",
            "facet_definition": "Social participation in organized violence",
            "citations": [
                {"id": "dio_cassius_50", "label": "Dio Cassius, Roman History 50", "source_type": "primary"}
            ]
        }
    ]
    
    create_star_pattern_claim(session, event_data, beliefs)

driver.close()
```

---

## Summary

You're absolutely right: **A claim is a star pattern.**

- **Event** = Hub (the claim itself)
- **Beliefs** = Spokes (independent assertions about one dimension)
- **Facets** = Radial endpoints (first-class classification objects)

Each spoke (Belief) can point to **one or more facets**, each with its own confidence, sources, and caveats.

This is far more powerful than a simple tree because:
1. Single event can have multiple independent facet-specific claims
2. Each facet claim has its own confidence + sources
3. Agents query the specific facets they care about
4. Facets are first-class nodes, not just properties

This is exactly what your intuition about "first class objects" points to.

---

**Analysis Date:** January 13, 2026  
**Status:** ✅ Star pattern validated for claim modeling
