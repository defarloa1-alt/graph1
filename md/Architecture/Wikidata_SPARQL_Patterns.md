# Wikidata SPARQL Patterns for Implementation

## Overview

This document extracts useful patterns from SPARQL query research for querying Wikidata to support our LLM agent-based knowledge graph implementation.

## Key Concepts

### 1. Occupation vs Role Distinction

**Occupations (P106)** - Global, person-centric attributes:
- Long-term professions (engineer, lawyer, carpenter)
- Model as `(:Person)-[:HAS_OCCUPATION]->(:Occupation)` edges
- Use Wikidata's occupation class hierarchy (Q28640)

**Roles** - Context-dependent functions:
- How a person participates in a relationship or event
- Model as edge properties or Role nodes attached to relationships
- Examples: chair, reviewer, plaintiff, lead engineer

### 2. Properties That Map Well to Roles

These Wikidata properties are best treated as roles (context-dependent):

- **P39 – position held**: Offices and posts (mayor, CEO, senator)
- **P463 – member of**: Membership in organizations, committees, boards
- **P710 – participant**: Participation in events, meetings, competitions
- **P453 – character role**: Role/character an actor plays in a work
- **P2868 – subject has role**: Generic role qualifier (carries role Q-ids)
- **P3831 – object has role**: Complement of P2868

**Properties better as occupations or attributes:**
- **P106 – occupation**: Long-term professions (global descriptors)
- **P21 – sex or gender**, **P569/P570 – birth/death**: Intrinsic properties
- **P108 – employer**, **P1416 – affiliation**: Point to organizations

## SPARQL Query Patterns

### Pattern 1: Get Occupation Q-ids (Fast, No Labels)

```sparql
PREFIX wd:  <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT DISTINCT ?occupation
WHERE {
  ?occupation wdt:P31/wdt:P279* wd:Q28640 .
}
ORDER BY ?occupation
LIMIT 1000
```

**Why**: Avoids timeouts by querying the occupation class hierarchy directly instead of scanning all people.

### Pattern 2: Resolve Q-ids to Labels in Batches

```sparql
PREFIX wd:  <http://www.wikidata.org/entity/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?occupation ?label
WHERE {
  VALUES ?occupation {
    wd:Q1001321 wd:Q49757 wd:Q36180  # Batch of Q-ids
  }
  ?occupation rdfs:label ?label .
  FILTER(LANG(?label) = "en")
}
```

**Why**: Two-step approach prevents timeouts and gives better control over batch size.

### Pattern 3: Query Role-like Properties

For properties that represent roles (P39, P463, P710, etc.):

```sparql
PREFIX wd:  <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?person ?role ?roleLabel
WHERE {
  ?person wdt:P39 ?role .  # position held
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
  }
}
LIMIT 100
```

## Python Implementation Patterns

### Two-Step Query Pattern

```python
import requests

ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {"User-Agent": "Chrystallum-Graph/1.0 (your.email@example.com)"}

# Step 1: Get Q-ids
q_ids_query = """
PREFIX wd:  <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT DISTINCT ?occupation
WHERE {
  ?occupation wdt:P31/wdt:P279* wd:Q28640 .
}
ORDER BY ?occupation
LIMIT 1000
"""

resp = requests.get(
    ENDPOINT,
    params={"query": q_ids_query, "format": "json"},
    headers=HEADERS,
)
resp.raise_for_status()
data = resp.json()

occupation_ids = [
    b["occupation"]["value"].rsplit("/", 1)[-1]  # Extract 'Q1234'
    for b in data["results"]["bindings"]
]

# Step 2: Resolve labels in batches
def get_labels_for_qids(qids, lang="en", batch_size=100):
    labels = {}
    for i in range(0, len(qids), batch_size):
        batch = qids[i:i+batch_size]
        values_clause = " ".join(f"wd:{qid}" for qid in batch)

        query = f"""
        PREFIX wd:  <http://www.wikidata.org/entity/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?occupation ?label
        WHERE {{
          VALUES ?occupation {{ {values_clause} }}
          ?occupation rdfs:label ?label .
          FILTER(LANG(?label) = "{lang}")
        }}
        """

        resp = requests.get(
            ENDPOINT,
            params={"query": query, "format": "json"},
            headers=HEADERS,
        )
        resp.raise_for_status()
        data = resp.json()

        for b in data["results"]["bindings"]:
            qid = b["occupation"]["value"].rsplit("/", 1)[-1]
            label = b["label"]["value"]
            labels[qid] = label

    return labels

occupation_labels = get_labels_for_qids(occupation_ids)
```

## Agent Output Schema

Based on the research, here's a recommended JSON schema for LLM agent output:

```json
{
  "entities": [
    {
      "local_id": "person_1",
      "qid": "Q42",
      "type": "Person",
      "labels": { "en": "Douglas Adams" },
      "properties": {
        "P569": "1952-03-11",
        "P19": "Q84",
        "P106": ["Q36180", "Q482980"]
      }
    }
  ],
  "relations": [
    {
      "subject_qid": "Q42",
      "rel_type_pid": "P39",
      "object_qid": "Q12345",
      "qualifiers": {
        "P580": "1979-01-01",
        "P582": "1985-12-31",
        "P2868": "QXYZ"
      },
      "fast_code": "1234",
      "start_year": 1979,
      "end_year": 1985,
      "role_qid": "Q_ROLE"
    }
  ],
  "narrative": [
    {
      "text": "Douglas Adams (Q42) worked for Example Org (Q12345) as a script editor.",
      "supports": ["relation:0"]
    }
  ]
}
```

## Neo4j Patterns

### Pattern 1: Relationship Instance as Edge with Structural Attachments

```cypher
// Ensure structural nodes
MERGE (f:Fast {code: "1234"})
MERGE (rt:RelType {pid: "P39"})
  ON CREATE SET rt.name = "position held"
MERGE (y1:Year {value: 1937})
MERGE (y2:Year {value: 1940})

// Ensure domain nodes
MERGE (p:Person {qid: "Q1"})
MERGE (o:Org {qid: "Q2"})

// Main relationship
MERGE (p)-[r:REL_INSTANCE {pid: "P39"}]->(o)
  ON CREATE SET r.source = "agent_1234"

MERGE (r)-[:HAS_FAST]->(f)
MERGE (r)-[:HAS_TYPE]->(rt)
MERGE (r)-[:STARTED_IN]->(y1)
MERGE (r)-[:ENDED_IN]->(y2)
```

### Pattern 2: Full Relation-Instance Node (for richer qualifiers)

```cypher
MERGE (p:Person {qid: "Q1"})
MERGE (o:Org {qid: "Q2"})
MERGE (f:Fast {code: "1234"})
MERGE (rt:RelType {pid: "P39"})
MERGE (y1:Year {value: 1937})
MERGE (y2:Year {value: 1940})

// Optional role Q-id from P2868
MERGE (role:Role {qid: "Q_ROLE"})
  ON CREATE SET role.label = "Mayor"

CREATE (rel:RelationInstance {id: apoc.create.uuid(), pid: "P39"})
MERGE (rel)-[:HAS_TYPE]->(rt)
MERGE (rel)-[:ABOUT_FAST]->(f)
MERGE (rel)-[:STARTED_IN]->(y1)
MERGE (rel)-[:ENDED_IN]->(y2)
MERGE (rel)-[:HAS_ROLE]->(role)

MERGE (p)-[:PARTICIPATES_AS_SUBJECT]->(rel)
MERGE (rel)-[:PARTICIPATES_AS_OBJECT]->(o)
```

## Implementation Recommendations

### For FAST Code Agents

1. **Pre-load canonical P-ids and role Q-ids** for each FAST domain:
   - P31, P279, P131, P361 for places
   - P39, P463, P102 for people in politics
   - P106 for occupations

2. **Agent output should always include**:
   - `subject_qid`, `object_qid`
   - `rel_type_pid` (or internal ID)
   - `fast_code`
   - `start_year`, `end_year` (or `period_id`)
   - `role_qid` (when applicable, from P2868/P3831)

3. **Graph ingestion layer**:
   - Upsert entities by `qid` or `local_id`
   - Create edges from relations, mapping P-ids to edge labels
   - Attach qualifiers as edge properties or separate nodes
   - Connect to Agent node for provenance

### For Relationship Types

- Use **P2868/P3831** values as role qualifiers on edges
- Store roles as `Role` nodes with Q-ids
- Attach roles to relation instances, not as flat node properties

## Key Takeaways

1. **Two-step query pattern** prevents timeouts when querying Wikidata
2. **Occupation vs Role distinction** is critical for proper modeling
3. **Structural nodes** (Fast, RelType, Year, Period) should be first-class nodes
4. **Agent output schema** should always include Q-ids and P-ids for traceability
5. **Roles belong on edges**, not as node properties
6. **Batch processing** is essential for large-scale Wikidata queries

## References

- Wikidata Query Service: https://query.wikidata.org
- Property P106 (occupation): https://www.wikidata.org/wiki/Property:P106
- Property P39 (position held): https://www.wikidata.org/wiki/Property:P39
- Property P2868 (subject has role): https://www.wikidata.org/wiki/Property:P2868
- Occupation class (Q28640): https://www.wikidata.org/wiki/Q28640


