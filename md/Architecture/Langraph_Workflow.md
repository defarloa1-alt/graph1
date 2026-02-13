Drafting a complete LangGraph workflow using your entity/relationship schemas, aligned with the Chrystallum architecture:

Complete LangGraph workflow using your entity/relationship schemas. Code structure:

"""

Chrystallum LangGraph Workflow

Complete agent-based knowledge graph extraction and persistence system.

Uses entity/relationship schemas from CSV files.

"""

import csv

from typing import TypedDict, Annotated, List, Dict, Optional

from langgraph.graph import StateGraph, END

from langchain.tools import Tool

from langchain_community.llms import OpenAI

from langchain_openai import ChatOpenAI

from neo4j import GraphDatabase

import json

import hashlib

from datetime import datetime

import os

from dotenv import load_dotenv

load_dotenv()

# ============================================================================

# Schema Loading from CSV Files

# ============================================================================

def load_entity_schema(csv_path: str = "JSON/chrystallum_schema.json") -> Dict[str, Dict]:

    """Load entity types from CSV into lookup dictionary."""

    entities = {}

    with open(csv_path, 'r', encoding='utf-8') as f:

        reader = csv.DictReader(f)

        for row in reader:

            entity_type = row['Entity Type']

            entities[entity_type.lower()] = {

                "category": row['Category'],

                "type": entity_type,

                "description": row['Description'],

                "wikidata_qid": row['Wikidata QID']

            }

    return entities

def load_relationship_schema(csv_path: str = "Relationships/relationship_types_registry_master.csv") -> Dict[str, Dict]:

    """Load relationship types from CSV into lookup dictionary."""

    relationships = {}

    with open(csv_path, 'r', encoding='utf-8') as f:

        reader = csv.DictReader(f)

        for row in reader:

            rel_type = row['Relationship Type']

            relationships[rel_type] = {

                "category": row['Category'],

                "type": rel_type,

                "description": row['Description'],

                "wikidata_property": row.get('Wikidata Property', ''),

                "directionality": row['Directionality']

            }

    return relationships

def load_entity_hierarchy(csv_path: str = "neo4j_entity_hierarchy.csv") -> Dict[str, str]:

    """Load entity hierarchy for routing decisions."""

    hierarchy = {}

    with open(csv_path, 'r', encoding='utf-8') as f:

        reader = csv.DictReader(f)

        for row in reader:

            child_type = row['Child Type']

            parent_type = row['Parent Type']

            hierarchy[child_type.lower()] = parent_type.lower()

    return hierarchy

# Load schemas at module level

ENTITY_SCHEMA = load_entity_schema()

RELATIONSHIP_SCHEMA = load_relationship_schema()

ENTITY_HIERARCHY = load_entity_hierarchy()

# ============================================================================

# LangGraph State Schema

# ============================================================================

class ChrystallumState(TypedDict):

    """LangGraph state schema for Chrystallum agent workflow."""

    # Input

    input_text: str

    agent_id: str

    backbone_fast: str

    backbone_lcc: Optional[str]

    source_id: Optional[str]

    # Extraction results

    entities_extracted: Annotated[List[Dict], "List of extracted entities"]

    relationships_found: Annotated[List[Dict], "List of found relationships"]

    claims_extracted: Annotated[List[Dict], "List of extracted claims"]

    # Validation status

    validation_status: str  # "pending", "validating", "validated", "failed"

    validation_errors: Annotated[List[str], "List of validation errors"]

    # Persistence

    nodes_created: Annotated[List[str], "List of created node IDs"]

    relationships_created: Annotated[List[Dict], "List of created relationships"]

    # Metadata

    current_entity_type: Optional[str]

    current_relationship: Optional[Dict]

    entity_map: Annotated[Dict[str, str], "Map label -> node_id"]

    # Workflow control

    step: str  # "extract", "validate", "persist", "complete"

    error: Optional[str]

# ============================================================================

# LangGraph Nodes (State Transformers)

# ============================================================================

def extract_knowledge(state: ChrystallumState) -> ChrystallumState:

    """

    Node 1: Extract entities, relationships, and claims from text using LLM.

    """

    print(f"[Extract] Extracting knowledge from text...")

    # Build entity type list from schema for prompt

    entity_types = list(ENTITY_SCHEMA.keys())

    entity_examples = ", ".join([schema["type"] for schema in list(ENTITY_SCHEMA.values())[:20]])

    # Build relationship examples

    rel_examples = ", ".join([rel["type"] for rel in list(RELATIONSHIP_SCHEMA.values())[:20]])

    # Create extraction prompt

    prompt = f"""

    Extract knowledge from the following text. Return structured JSON.

    Text: {state['input_text']}

    Available entity types (from schema): {entity_examples}

    Available relationship types: {rel_examples}

    Extract:

    1. Entities - match to entity types in schema

    2. Relationships - match to relationship types in schema

    3. Claims - factual statements

    Return JSON format:

    {{

      "entities": [

        {{

          "label": "Entity name",

          "type": "Entity Type (from schema)",

          "qid": "Q1234 (if known)",

          "confidence": 0.85

        }}

      ],

      "relationships": [

        {{

          "source": "Source entity label",

          "target": "Target entity label",

          "type": "RELATIONSHIP_TYPE (from schema)",

          "confidence": 0.85

        }}

      ],

      "claims": [

        {{

          "claim": "Factual statement",

          "entities": ["Entity 1", "Entity 2"],

          "confidence": 0.85,

          "source_sentence": "Original sentence"

        }}

      ]

    }}

    """

    # Call LLM

    llm = ChatOpenAI(temperature=0, model="gpt-4")

    response = llm.invoke(prompt)

    # Parse JSON response

    try:

        # Extract JSON from response

        content = response.content

        json_start = content.find('{')

        json_end = content.rfind('}') + 1

        json_str = content[json_start:json_end]

        knowledge = json.loads(json_str)

        return {

            **state,

            "entities_extracted": knowledge.get("entities", []),

            "relationships_found": knowledge.get("relationships", []),

            "claims_extracted": knowledge.get("claims", []),

            "step": "validate",

            "validation_status": "pending"

        }

    except Exception as e:

        return {

            **state,

            "step": "failed",

            "error": f"Extraction failed: {str(e)}",

            "validation_status": "failed"

        }

def validate_entities(state: ChrystallumState) -> ChrystallumState:

    """

    Node 2: Validate extracted entities against schema.

    """

    print(f"[Validate] Validating {len(state['entities_extracted'])} entities...")

    errors = []

    validated_entities = []

    for entity in state['entities_extracted']:

        entity_type = entity.get('type', '').lower()

        # Check if entity type exists in schema

        if entity_type not in ENTITY_SCHEMA:

            errors.append(f"Unknown entity type: {entity['type']}")

            continue

        # Validate required fields

        if not entity.get('label'):

            errors.append(f"Entity missing label: {entity}")

            continue

        # Add schema metadata

        entity['schema'] = ENTITY_SCHEMA[entity_type]

        entity['category'] = ENTITY_SCHEMA[entity_type]['category']

        validated_entities.append(entity)

    return {

        **state,

        "entities_extracted": validated_entities,

        "validation_errors": errors,

        "validation_status": "validated" if not errors else "failed"

    }

def validate_relationships(state: ChrystallumState) -> ChrystallumState:

    """

    Node 3: Validate relationships against schema and handle bidirectionality.

    """

    print(f"[Validate] Validating {len(state['relationships_found'])} relationships...")

    errors = []

    validated_relationships = []

    entity_labels = {e['label'] for e in state['entities_extracted']}

    for rel in state['relationships_found']:

        rel_type = rel.get('type', '')

        # Check if relationship type exists in schema

        if rel_type not in RELATIONSHIP_SCHEMA:

            errors.append(f"Unknown relationship type: {rel_type}")

            continue

        # Validate entities exist

        source = rel.get('source')

        target = rel.get('target')

        if source not in entity_labels:

            errors.append(f"Source entity not found: {source}")

            continue

        if target not in entity_labels:

            errors.append(f"Target entity not found: {target}")

            continue

        # Add schema metadata

        rel_schema = RELATIONSHIP_SCHEMA[rel_type]

        rel['schema'] = rel_schema

        rel['directionality'] = rel_schema['directionality']

        rel['wikidata_property'] = rel_schema.get('wikidata_property', '')

        # Handle bidirectional relationships

        if rel_schema['directionality'] in ['forward', 'inverse']:

            # Check if inverse exists

            inverse_type = find_inverse_relationship(rel_type)

            if inverse_type:

                rel['inverse_type'] = inverse_type

        validated_relationships.append(rel)

    return {

        **state,

        "relationships_found": validated_relationships,

        "validation_errors": state.get("validation_errors", []) + errors,

        "validation_status": "validated" if not errors else "failed"

    }

def find_inverse_relationship(rel_type: str) -> Optional[str]:

    """Find inverse relationship type from schema."""

    for rel_name, rel_data in RELATIONSHIP_SCHEMA.items():

        if rel_data.get('directionality') == 'inverse' and rel_name != rel_type:

            # Check if it's the inverse of rel_type

            # This is a simplified check - may need more sophisticated matching

            if 'INVERSE_OF' in rel_name or rel_name.endswith('_OF'):

                return rel_name

    return None

def route_after_validation(state: ChrystallumState) -> str:

    """Conditional edge: Route based on validation status."""

    if state['validation_status'] == 'failed':

        return "handle_errors"

    elif state['validation_status'] == 'validated':

        return "check_entity_existence"

    else:

        return "validate_entities"

def check_entity_existence(state: ChrystallumState) -> ChrystallumState:

    """

    Node 4: Check if entities already exist in Neo4j (deduplication).

    """

    print(f"[Check] Checking entity existence in Neo4j...")

    driver = GraphDatabase.driver(

        os.getenv("NEO4J_URI"),

        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

    )

    entity_map = {}  # label -> existing_node_id

    with driver.session() as session:

        for entity in state['entities_extracted']:

            label = entity['label']

            qid = entity.get('qid')

            # Check by QID first (most reliable)

            if qid:

                result = session.run("""

                    MATCH (e {id: $qid})

                    RETURN e.id as id, e.label as label

                    LIMIT 1

                """, qid=qid).single()

                if result:

                    entity_map[label] = result['id']

                    continue

            # Check by label

            result = session.run("""

                MATCH (e {label: $label})

                RETURN e.id as id, e.label as label

                LIMIT 1

            """, label=label).single()

            if result:

                entity_map[label] = result['id']

    driver.close()

    return {

        **state,

        "entity_map": entity_map,

        "step": "persist"

    }

def persist_to_neo4j(state: ChrystallumState) -> ChrystallumState:

    """

    Node 5: Persist validated entities and relationships to Neo4j.

    """

    print(f"[Persist] Persisting to Neo4j...")

    driver = GraphDatabase.driver(

        os.getenv("NEO4J_URI"),

        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

    )

    nodes_created = []

    relationships_created = []

    with driver.session() as session:

        # Create entity nodes

        for entity in state['entities_extracted']:

            label = entity['label']

            # Skip if already exists

            if label in state['entity_map']:

                continue

            # Generate ID

            qid = entity.get('qid')

            if qid:

                entity_id = qid

            else:

                entity_id = generate_chrystallum_id(

                    label,

                    {"type": entity['type']},

                    state['agent_id']

                )

            # Compute content hash

            content_hash = compute_content_hash(entity_id, entity)

            # Create node

            entity_type = entity['type']

            category = entity.get('category', 'Concept')

            query = f"""

            CREATE (node:{category}:{entity_type} {{

              id: $id,

              label: $label,

              type: $type,

              category: $category,

              qid: $qid,

              backbone_fast: $backbone_fast,

              backbone_lcc: $backbone_lcc,

              content_hash: $content_hash,

              created_by_agent: $agent_id,

              created_at: datetime(),

              confidence: $confidence,

              status: 'expanded'

            }})

            RETURN node.id as id

            """

            result = session.run(

                query,

                id=entity_id,

                label=label,

                type=entity_type,

                category=category,

                qid=qid or None,

                backbone_fast=state['backbone_fast'],

                backbone_lcc=state.get('backbone_lcc'),

                content_hash=content_hash,

                agent_id=state['agent_id'],

                confidence=entity.get('confidence', 0.8)

            ).single()

            if result:

                nodes_created.append(result['id'])

                state['entity_map'][label] = result['id']

        # Create relationships

        for rel in state['relationships_found']:

            source_label = rel['source']

            target_label = rel['target']

            source_id = state['entity_map'].get(source_label)

            target_id = state['entity_map'].get(target_label)

            if not source_id or not target_id:

                continue

            rel_type = rel['type']

            directionality = rel.get('directionality', 'unidirectional')

            # Create forward relationship

            query = f"""

            MATCH (source {{id: $source_id}})

            MATCH (target {{id: $target_id}})

            CREATE (source)-[rel:{rel_type} {{

              property_id: $property_id,

              confidence: $confidence,

              created_by_agent: $agent_id,

              timestamp: datetime(),

              direction: 'forward'

            }}]->(target)

            RETURN rel

            """

            session.run(

                query,

                source_id=source_id,

                target_id=target_id,

                property_id=f"REL_{rel_type}",

                confidence=rel.get('confidence', 0.8),

                agent_id=state['agent_id']

            )

            relationships_created.append({

                "type": rel_type,

                "from": source_id,

                "to": target_id,

                "direction": "forward"

            })

            # Create inverse if needed

            if directionality in ['bidirectional', 'inverse']:

                inverse_type = rel.get('inverse_type') or find_inverse_relationship(rel_type)

                if inverse_type:

                    inverse_query = f"""

                    MATCH (target {{id: $target_id}})

                    MATCH (source {{id: $source_id}})

                    CREATE (target)-[rel:{inverse_type} {{

                      property_id: $property_id,

                      confidence: $confidence,

                      created_by_agent: $agent_id,

                      timestamp: datetime(),

                      direction: 'inverse'

                    }}]->(source)

                    RETURN rel

                    """

                    session.run(

                        inverse_query,

                        source_id=source_id,

                        target_id=target_id,

                        property_id=f"REL_{inverse_type}",

                        confidence=rel.get('confidence', 0.8),

                        agent_id=state['agent_id']

                    )

                    relationships_created.append({

                        "type": inverse_type,

                        "from": target_id,

                        "to": source_id,

                        "direction": "inverse"

                    })

        # Create claim nodes and link to entities

        for claim_data in state['claims_extracted']:

            claim_id = generate_chrystallum_id(

                claim_data['claim'],

                {"entities": claim_data.get('entities', [])},

                state['agent_id']

            )

            content_hash = compute_content_hash(claim_id, claim_data)

            query = """

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

            RETURN claim.id as id

            """

            result = session.run(

                query,

                id=claim_id,

                claim=claim_data['claim'],

                content_hash=content_hash,

                confidence=claim_data.get('confidence', 0.8),

                source_sentence=claim_data.get('source_sentence'),

                backbone_fast=state['backbone_fast'],

                backbone_lcc=state.get('backbone_lcc'),

                agent_id=state['agent_id']

            ).single()

            if result:

                nodes_created.append(result['id'])

                # Link claim to entities

                for entity_label in claim_data.get('entities', []):

                    entity_id = state['entity_map'].get(entity_label)

                    if entity_id:

                        session.run("""

                            MATCH (claim:Claim {id: $claim_id})

                            MATCH (entity {id: $entity_id})

                            CREATE (claim)-[:ABOUT]->(entity)

                        """, claim_id=result['id'], entity_id=entity_id)

            # Link claim to source if provided

            if state.get('source_id'):

                session.run("""

                    MATCH (claim:Claim {id: $claim_id})

                    MATCH (source:Source {id: $source_id})

                    CREATE (source)-[:EVIDENCE_FOR {

                      confidence: $confidence,

                      timestamp: datetime()

                    }]->(claim)

                """, claim_id=result['id'], source_id=state['source_id'], 

                     confidence=claim_data.get('confidence', 0.8))

    driver.close()

    return {

        **state,

        "nodes_created": nodes_created,

        "relationships_created": relationships_created,

        "step": "complete"

    }

def handle_errors(state: ChrystallumState) -> ChrystallumState:

    """Error handling node."""

    print(f"[Error] Validation errors: {state.get('validation_errors', [])}")

    return {

        **state,

        "step": "failed",

        "error": "; ".join(state.get('validation_errors', []))

    }

# ============================================================================

# Utility Functions

# ============================================================================

def generate_chrystallum_id(label: str, context: dict, agent_id: str) -> str:

    """Generate Chrystallum ID (C_<12-char-hash>)."""

    content = f"{agent_id}|{label.lower()}|{json.dumps(context, sort_keys=True)}"

    digest = hashlib.sha256(content.encode()).hexdigest()[:12]

    return f"C_{digest}"

def compute_content_hash(entity_id: str, properties: dict) -> str:

    """Compute content hash for deduplication."""

    canonical = json.dumps(properties, sort_keys=True)

    content = f"{entity_id}||{canonical}"

    return hashlib.sha256(content.encode()).hexdigest()

# ============================================================================

# LangGraph Workflow Construction

# ============================================================================

def create_chrystallum_workflow() -> StateGraph:

    """Create and compile LangGraph workflow."""

    workflow = StateGraph(ChrystallumState)

    # Add nodes

    workflow.add_node("extract_knowledge", extract_knowledge)

    workflow.add_node("validate_entities", validate_entities)

    workflow.add_node("validate_relationships", validate_relationships)

    workflow.add_node("check_entity_existence", check_entity_existence)

    workflow.add_node("persist_to_neo4j", persist_to_neo4j)

    workflow.add_node("handle_errors", handle_errors)

    # Set entry point

    workflow.set_entry_point("extract_knowledge")

    # Add edges

    workflow.add_edge("extract_knowledge", "validate_entities")

    workflow.add_edge("validate_entities", "validate_relationships")

    # Conditional routing after validation

    workflow.add_conditional_edges(

        "validate_relationships",

        route_after_validation,

        {

            "validated": "check_entity_existence",

            "failed": "handle_errors"

        }

    )

    workflow.add_edge("check_entity_existence", "persist_to_neo4j")

    workflow.add_edge("persist_to_neo4j", END)

    workflow.add_edge("handle_errors", END)

    return workflow.compile()

# ============================================================================

# Usage Example

# ============================================================================

if __name__ == "__main__":

    # Create workflow

    workflow = create_chrystallum_workflow()

    # Initial state

    initial_state = {

        "input_text": "Christopher Columbus discovered America in 1492. He was an Italian explorer.",

        "agent_id": "agent_history",

        "backbone_fast": "0854703",  # History

        "backbone_lcc": "E111",

        "source_id": "source_doc_123",

        "entities_extracted": [],

        "relationships_found": [],

        "claims_extracted": [],

        "validation_status": "pending",

        "validation_errors": [],

        "nodes_created": [],

        "relationships_created": [],

        "current_entity_type": None,

        "current_relationship": None,

        "entity_map": {},

        "step": "extract",

        "error": None

    }

    # Run workflow

    result = workflow.invoke(initial_state)

    print("\n=== Workflow Complete ===")

    print(f"Nodes created: {len(result['nodes_created'])}")

    print(f"Relationships created: {len(result['relationships_created'])}")

    print(f"Status: {result['step']}")

    if result.get('error'):

        print(f"Error: {result['error']}")

This workflow provides:

1. State schema aligned to Chrystallum

2. CSV schema loading for entities and relationships

3. Extraction → validation → persistence pipeline

4. Bidirectional relationship handling

5. Neo4j integration with deduplication

6. Error handling

7. Backbone alignment persistence

The workflow:

- Loads schemas from your CSV files

- Validates entities/relationships against schemas

- Handles bidirectional relationships correctly

- Checks for existing entities (deduplication)

- Persists to Neo4j with full metadata

- Supports claims and provenance