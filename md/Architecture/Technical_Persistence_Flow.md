Here’s how an agent persists LLM-extracted knowledge like "Columbus discovered America" to Neo4j:

## Technical Persistence Flow

### 1. LLM Extraction (Structured Output)

The agent calls the LLM to extract structured knowledge:

Agent extracts knowledge from text/document using LLM.


def extract_knowledge_with_llm(text: str, agent_id: str) -> dict:

    `"""`

    `LLM extracts structured knowledge from text.`

    `"""`

    `prompt = f"""`

    `Extract knowledge from the following text. Return structured JSON.`

    `Text: {text}`

    `Extract:`

    `1. Entities (Person, Place, Event, SubjectConcept)`

    `2. Claims (facts/statements)`

    `3. Relationships between entities`

    `Return JSON format:`

    `{{`

      `"entities": [`

        `{{`

          `"label": "Christopher Columbus",`

          `"type": "Person",`

          `"qid": "Q1312",`

          `"confidence": 0.95`

        `}}`

      `],`

      `"claims": [`

        `{{`

          `"claim": "Columbus discovered America",`

          `"entities": ["Christopher Columbus", "America"],`

          `"confidence": 0.85,`

          `"source_sentence": "Columbus discovered America in 1492"`

        `}}`

      `],`

      `"relationships": [`

        `{{`

          `"source": "Christopher Columbus",`

          `"target": "America",`

          `"predicate": "DISCOVERED",`

          `"confidence": 0.85`

        `}}`

      `]`

    `}}`

    `"""`

    `# Call LLM (OpenAI, Anthropic, etc.)`

    `response = llm.generate(prompt)`

    `# Parse structured JSON response`

    `import json`

    `knowledge = json.loads(response)`

    `return knowledge`

Persistence to Neo4j (Concrete Implementation)

The agent persists the extracted knowledge:

"""

Persist LLM-extracted knowledge to Neo4j.

"""

def persist_knowledge(knowledge: dict, agent_id: str, source_id: str = None):

    `"""`

    `Persist extracted knowledge to Neo4j graph.`

    `Args:`

        `knowledge: Structured knowledge from LLM`

        `agent_id: Creating agent`

        `source_id: Source document/node ID (for provenance)`

    """

    with driver.session() as session:

        # Step 1: Create/update entities

        entity_map = {}  # Map label -> node_id for relationship creation

        for entity in knowledge.get("entities", []):

            # Check if entity already exists

            existing = session.run("""

                MATCH (e)

                WHERE e.id = $qid OR e.label = $label

                RETURN e.id as id, e.label as label

                LIMIT 1

            """, qid=entity.get("qid"), label=entity["label"]).single()

            if existing:

                entity_id = existing["id"]

            else:

                # Create new entity node

                entity_id = entity.get("qid") or generate_chrystallum_id(

                    entity["label"], 

                    {"type": entity["type"]},

                    agent_id

                )

                # Get agent's backbone for this entity type

                agent_backbone = get_agent_backbone_scope(agent_id)

                session.run("""

                    CREATE (entity:Person {

                      id: $id,

                      label: $label,

                      type: $type,

                      qid: $qid,

                      backbone_fast: $backbone_fast,

                      backbone_lcc: $backbone_lcc,

                      created_by_agent: $agent_id,

                      created_at: datetime(),

                      confidence: $confidence,

                      status: "expanded"

                    })

                """,

                    id=entity_id,

                    label=entity["label"],

                    type=entity["type"],

                    qid=entity.get("qid"),

                    backbone_fast=agent_backbone["backbone_fast"],

                    backbone_lcc=agent_backbone["backbone_lcc"],

                    agent_id=agent_id,

                    confidence=entity.get("confidence", 0.8)

                )

            entity_map[entity["label"]] = entity_id

        # Step 2: Create Claim nodes

        for claim_data in knowledge.get("claims", []):

            # Generate claim ID

            claim_id = generate_chrystallum_id(

                claim_data["claim"],

                {"entities": claim_data["entities"]},

                agent_id

            )

            # Compute content hash

            content_hash = compute_content_hash(claim_id, {

                "claim": claim_data["claim"],

                "entities": claim_data["entities"]

            })

            # Create Claim node

            session.run("""

                CREATE (claim:Claim {

                  id: $id,

                  label: $claim,

                  claim_text: $claim,

                  content_hash: $content_hash,

                  confidence: $confidence,

                  source_sentence: $source_sentence,

                  backbone_fast: $backbone_fast,

                  backbone_lcc: $backbone_lcc,

                  created_by_agent: $agent_id,

                  created_at: datetime(),

                  version: 1

                })

            """,

                id=claim_id,

                claim=claim_data["claim"],

                content_hash=content_hash,

                confidence=claim_data.get("confidence", 0.8),

                source_sentence=claim_data.get("source_sentence"),

                backbone_fast=agent_backbone["backbone_fast"],

                backbone_lcc=agent_backbone["backbone_lcc"],

                agent_id=agent_id

            )

            # Link claim to entities

            for entity_label in claim_data["entities"]:

                if entity_label in entity_map:

                    session.run("""

                        MATCH (claim:Claim {id: $claim_id})

                        MATCH (entity {id: $entity_id})

                        CREATE (claim)-[:ABOUT]->(entity)

                    """,

                        claim_id=claim_id,

                        entity_id=entity_map[entity_label]

                    )

            # Link claim to source (provenance)

            if source_id:

                session.run("""

                    MATCH (claim:Claim {id: $claim_id})

                    MATCH (source:Source {id: $source_id})

                    CREATE (source)-[:EVIDENCE_FOR {

                      confidence: $confidence,

                      timestamp: datetime()

                    }]->(claim)

                """,

                    claim_id=claim_id,

                    source_id=source_id,

                    confidence=claim_data.get("confidence", 0.8)

                )

        # Step 3: Create relationships

        for rel_data in knowledge.get("relationships", []):

            source_id = entity_map.get(rel_data["source"])

            target_id = entity_map.get(rel_data["target"])

            if source_id and target_id:

                # Get relationship type from Property Registry

                rel_type = rel_data["predicate"]  # e.g., "DISCOVERED"

                session.run("""

                    MATCH (source {id: $source_id})

                    MATCH (target {id: $target_id})

                    CREATE (source)-[rel:DISCOVERED {

                      property_id: "REL_DISCOVERED",

                      confidence: $confidence,

                      created_by_agent: $agent_id,

                      timestamp: datetime()

                    }]->(target)

                """,

                    source_id=source_id,

                    target_id=target_id,

                    confidence=rel_data.get("confidence", 0.8),

                    agent_id=agent_id

                )

### 3. Complete Example: "Columbus discovered America"

Here's the exact Neo4j persistence:

// Step 1: Create Person node (Columbus)

CREATE (columbus:Person {

  id: "Q1312",

  label: "Christopher Columbus",

  type: "Person",

  qid: "Q1312",

  backbone_fast: "0854703",  // From agent's backbone

  backbone_lcc: "E111",      // History - Discovery

  created_by_agent: "agent_history",

  created_at: datetime(),

  confidence: 0.95,

  status: "expanded"

})

// Step 2: Create Place node (America)

CREATE (america:Place {

  id: "Q828",  // Americas

  label: "America",

  type: "Place",

  qid: "Q828",

  backbone_fast: "0854703",

  backbone_lcc: "E111",

  created_by_agent: "agent_history",

  created_at: datetime(),

  confidence: 0.95,

  status: "expanded"

})

// Step 3: Create Claim node

CREATE (claim:Claim {

  id: "C_abc123def456",

  label: "Columbus discovered America",

  claim_text: "Columbus discovered America",

  content_hash: "9f17a967891d...",

  confidence: 0.85,

  source_sentence: "Columbus discovered America in 1492",

  backbone_fast: "0854703",

  backbone_lcc: "E111",

  created_by_agent: "agent_history",

  created_at: datetime(),

  version: 1

})

// Step 4: Link claim to entities

CREATE (claim)-[:ABOUT]->(columbus)

CREATE (claim)-[:ABOUT]->(america)

// Step 5: Create relationship

CREATE (columbus)-[rel:DISCOVERED {

  property_id: "REL_DISCOVERED",

  confidence: 0.85,

  created_by_agent: "agent_history",

  timestamp: datetime()

}]->(america)

// Step 6: Link relationship to claim (optional)

CREATE (rel)-[:SUPPORTS]->(claim)

// Step 7: Provenance - link to source document

MATCH (source:Source {id: "source_doc_123"})

CREATE (source)-[:EVIDENCE_FOR {

  confidence: 0.85,

  timestamp: datetime()

}]->(claim)

### 4. Complete Flow in LangChain Agent

"""

Complete agent workflow: Learn → Extract → Persist

"""

def agent_learn_from_text(text: str, agent_id: str, source_id: str):

    """

    Agent learns from text and persists to Neo4j.

    """

    # Step 1: LLM extracts knowledge

    knowledge = extract_knowledge_with_llm(text, agent_id)

    # Step 2: Persist to Neo4j

    persist_knowledge(knowledge, agent_id, source_id)

    # Step 3: Return what was learned

    return {

        "entities_created": len(knowledge.get("entities", [])),

        "claims_created": len(knowledge.get("claims", [])),

        "relationships_created": len(knowledge.get("relationships", []))

    }

# LangChain agent tool

learn_from_text_tool = Tool(

    name="learn_from_text",

    func=agent_learn_from_text,

    description="Extracts knowledge from text using LLM and persists to Neo4j graph. Returns count of entities, claims, and relationships created."

)

# Agent uses it

agent_executor.run(

    "Learn from this text: 'Columbus discovered America in 1492.'"

)

## Summary: Technical Persistence

1. LLM extracts → Structured JSON (entities, claims, relationships)

2. Agent processes → Validates backbone, checks for duplicates

3. Neo4j CREATE → Nodes (Person, Place, Claim) with properties

4. Relationships → Edges (DISCOVERED, ABOUT, EVIDENCE_FOR)

5. Provenance → Links to source, agent, timestamp

The knowledge "Columbus discovered America" becomes:

- Nodes: Person (Columbus), Place (America), Claim ("Columbus discovered America")

- Relationships: (Columbus)-[:DISCOVERED]->(America), (Claim)-[:ABOUT]->(Columbus)

- Metadata: confidence, backbone, agent, timestamp, source

All persisted in Neo4j as graph structure.