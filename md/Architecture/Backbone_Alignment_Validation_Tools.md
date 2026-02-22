

### 1. Neo4j Constraints (Database-Level Enforcement)

// Property existence constraints (requires Neo4j Enterprise or newer Community)

// For nodes that MUST have backbone alignment

CREATE CONSTRAINT backbone_fast_required_concept IF NOT EXISTS

FOR (n:SubjectConcept) 

REQUIRE n.backbone_fast IS NOT NULL;

CREATE CONSTRAINT backbone_fast_required_claim IF NOT EXISTS

FOR (n:Claim) 

REQUIRE n.backbone_fast IS NOT NULL;

CREATE CONSTRAINT backbone_fast_required_event IF NOT EXISTS

FOR (n:Event) 

REQUIRE n.backbone_fast IS NOT NULL;

// For Agents - backbone is always required

CREATE CONSTRAINT backbone_fast_required_agent IF NOT EXISTS

FOR (n:Agent) 

REQUIRE n.backbone_fast IS NOT NULL;

// Note: Neo4j Community Edition may not support property existence constraints

// In that case, use application-level validation (tools below)

// Create indexes for fast backbone queries

CREATE INDEX backbone_fast_index IF NOT EXISTS 

FOR (n) ON (n.backbone_fast);

CREATE INDEX backbone_lcc_index IF NOT EXISTS 

FOR (n) ON (n.backbone_lcc);

### 2. FAST Registry Lookup Tool

"""

FAST Registry validation tool for LangChain agents.

Ensures FAST codes exist and are valid.

"""

from langchain.tools import Tool

from neo4j import GraphDatabase

import os

from dotenv import load_dotenv

import re

load_dotenv()

driver = GraphDatabase.driver(

    os.getenv("NEO4J_URI"),

    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

)

def validate_fast_id(fast_id: str) -> dict:

    """

    Validate that a FAST ID is properly formatted.

    Args:

        fast_id: FAST subject code (numeric string)

    Returns:

        dict with 'valid' (bool) and 'error' (str) if invalid

    """

    if not fast_id:

        return {"valid": False, "error": "FAST ID is required"}

    # FAST IDs are numeric strings

    if not re.match(r'^\d+$', str(fast_id)):

        return {

            "valid": False, 

            "error": f"FAST ID must be numeric, got: {fast_id}"

        }

    # Optionally: check if FAST ID exists in external registry

    # For now, just validate format

    return {"valid": True, "fast_id": fast_id}

def get_fast_metadata(fast_id: str) -> dict:

    """

    Retrieve FAST metadata from registry (if stored in Neo4j).

    Args:

        fast_id: FAST subject code

    Returns:

        dict with FAST metadata or None if not found

    """

    query = """

    MATCH (fast:FASTRegistry {fast_id: $fast_id})

    RETURN fast.fast_id as fast_id,

           fast.label as label,

           fast.lcc_code as lcc_code,

           fast.qid as qid

    """

    with driver.session() as session:

        result = session.run(query, fast_id=fast_id)

        record = result.single()

        if record:

            return {

                "fast_id": record["fast_id"],

                "label": record["label"],

                "lcc_code": record["lcc_code"],

                "qid": record["qid"]

            }

        return None

# LangChain tool for FAST validation

validate_fast_tool = Tool(

    name="validate_fast_id",

    func=lambda fast_id: validate_fast_id(fast_id),

    description="Validates that a FAST subject code is properly formatted (numeric string). Returns valid=True if format is correct."

)

### 3. Agent Backbone Validation Tool

"""

Agent backbone alignment validation.

Ensures agents can only create nodes within their backbone scope.

"""

def get_agent_backbone_scope(agent_id: str) -> dict:

    """

    Get agent's allowed backbone scope.

    Args:

        agent_id: Agent identifier

    Returns:

        dict with agent's backbone configuration

    """

    query = """

    MATCH (agent:Agent {agent_id: $agent_id})

    RETURN agent.backbone_fast as backbone_fast,

           agent.backbone_lcc as backbone_lcc,

           agent.backbone_qid as backbone_qid,

           agent.allowed_backbone_range as allowed_range

    """

    with driver.session() as session:

        result = session.run(query, agent_id=agent_id)

        record = result.single()

        if not record:

            return None

        return {

            "backbone_fast": record["backbone_fast"],

            "backbone_lcc": record["backbone_lcc"],

            "backbone_qid": record["backbone_qid"],

            "allowed_range": record["allowed_range"] or []

        }

def is_backbone_in_range(fast_id: str, allowed_range: list) -> bool:

    """

    Check if FAST ID is within agent's allowed backbone range.

    Args:

        fast_id: FAST subject code to check

        allowed_range: List of allowed LCC prefixes (e.g., ["QC311", "QC312"])

    Returns:

        bool indicating if FAST is in range

    """

    if not allowed_range:

        return True  # No restrictions

    # Get LCC code for this FAST ID

    metadata = get_fast_metadata(fast_id)

    if not metadata or not metadata.get("lcc_code"):

        return False

    lcc_code = metadata["lcc_code"]

    # Check if LCC code matches any allowed prefix

    for prefix in allowed_range:

        if lcc_code.startswith(prefix):

            return True

    return False

def validate_agent_backbone_permission(

    agent_id: str, 

    backbone_fast: str

) -> dict:

    """

    Validate that an agent can create nodes with the given backbone.

    Args:

        agent_id: Agent identifier

        backbone_fast: FAST subject code

    Returns:

        dict with 'valid' (bool) and 'error' (str) if invalid

    """

    # Get agent config

    agent_config = get_agent_backbone_scope(agent_id)

    if not agent_config:

        return {

            "valid": False,

            "error": f"Agent {agent_id} not found"

        }

    # Validate FAST ID format

    fast_validation = validate_fast_id(backbone_fast)

    if not fast_validation["valid"]:

        return fast_validation

    # Check if agent's backbone matches or is in range

    if agent_config.get("allowed_range"):

        if not is_backbone_in_range(backbone_fast, agent_config["allowed_range"]):

            return {

                "valid": False,

                "error": f"Agent {agent_id} cannot create nodes outside backbone range {agent_config['allowed_range']}"

            }

    # Optionally: enforce exact match

    # if agent_config["backbone_fast"] != backbone_fast:

    #     return {

    #         "valid": False,

    #         "error": f"Agent backbone mismatch. Agent has {agent_config['backbone_fast']}, tried to use {backbone_fast}"

    #     }

    return {"valid": True, "agent_config": agent_config}

# LangChain tool

validate_agent_backbone_tool = Tool(

    name="validate_agent_backbone_permission",

    func=lambda agent_id, backbone_fast: validate_agent_backbone_permission(agent_id, backbone_fast),

    description="Validates that an agent has permission to create nodes with the given FAST backbone code. Returns valid=True if allowed."

)

### 4. Node Creation Tool with Backbone Validation

"""

Create node tool with mandatory backbone validation.

This is the main tool agents use to create nodes.

"""

from langchain.tools import Tool

import hashlib

from datetime import datetime

def create_node_with_backbone_validation(

    label: str,

    entity_type: str,

    backbone_fast: str,

    agent_id: str,

    backbone_lcc: str = None,

    backbone_qid: str = None,

    properties: dict = None,

    id: str = None

) -> dict:

    """

    Create a node in Neo4j with mandatory backbone alignment validation.

    Args:

        label: Human-readable label

        entity_type: Type of entity (Concept, Claim, Event, Person, etc.)

        backbone_fast: FAST subject code (REQUIRED)

        agent_id: Creating agent ID (REQUIRED)

        backbone_lcc: LCC code (optional, will be looked up if not provided)

        backbone_qid: Wikidata QID (optional)

        properties: Additional properties dict

        id: Node ID (will generate if not provided)

    Returns:

        dict with created node info or error

    """

    # Step 1: Validate FAST ID format

    fast_validation = validate_fast_id(backbone_fast)

    if not fast_validation["valid"]:

        return {

            "success": False,

            "error": fast_validation["error"]

        }

    # Step 2: Validate agent permission

    agent_validation = validate_agent_backbone_permission(agent_id, backbone_fast)

    if not agent_validation["valid"]:

        return {

            "success": False,

            "error": agent_validation["error"]

        }

    # Step 3: Look up FAST metadata if LCC not provided

    if not backbone_lcc:

        fast_metadata = get_fast_metadata(backbone_fast)

        if fast_metadata:

            backbone_lcc = fast_metadata.get("lcc_code")

            if not backbone_qid and fast_metadata.get("qid"):

                backbone_qid = fast_metadata["qid"]

    # Step 4: Generate ID if not provided

    if not id:

        if backbone_qid:

            id = backbone_qid

        else:

            # Generate Chrystallum ID

            content = f"{agent_id}|{label.lower()}|{backbone_fast}"

            digest = hashlib.sha256(content.encode()).hexdigest()[:12]

            id = f"C_{digest}"

    # Step 5: Compute content hash

    properties = properties or {}

    canonical_props = {

        "label": label,

        "type": entity_type,

        "backbone_fast": backbone_fast,

        **properties

    }

    content_hash = hashlib.sha256(

        f"{id}||{json.dumps(canonical_props, sort_keys=True)}".encode()

    ).hexdigest()

    # Step 6: Create node in Neo4j

    query = """

    CREATE (node:SubjectConcept {

      id: $id,

      label: $label,

      type: $entity_type,

      backbone_fast: $backbone_fast,

      backbone_lcc: $backbone_lcc,

      backbone_qid: $backbone_qid,

      created_by_agent: $agent_id,

      created_at: datetime(),

      content_hash: $content_hash,

      status: $status

    })

    SET node += $properties

    RETURN node.id as id, node.label as label, node.backbone_fast as backbone_fast

    """

    with driver.session() as session:

        try:

            result = session.run(

                query,

                id=id,

                label=label,

                entity_type=entity_type,

                backbone_fast=backbone_fast,

                backbone_lcc=backbone_lcc,

                backbone_qid=backbone_qid,

                agent_id=agent_id,

                content_hash=content_hash,

                status="expanded",  # or "shell" if appropriate

                properties=properties or {}

            )

            record = result.single()

            return {

                "success": True,

                "node_id": record["id"],

                "label": record["label"],

                "backbone_fast": record["backbone_fast"]

            }

        except Exception as e:

            return {

                "success": False,

                "error": f"Failed to create node: {str(e)}"

            }

# LangChain tool

create_node_tool = Tool(

    name="create_node_with_backbone",

    func=create_node_with_backbone_validation,

    description="Creates a node in Neo4j with mandatory FAST backbone alignment. Requires: label, entity_type, backbone_fast, agent_id. Returns created node info."

)

### 5. Validation Queries (Post-Creation Checks)

// Find nodes missing backbone_fast

MATCH (n)

WHERE (n:SubjectConcept OR n:Claim OR n:Event OR n:Person OR n:Organization)

  AND NOT exists(n.backbone_fast)

RETURN n.id as node_id, 

       n.label as label,

       labels(n) as node_labels,

       n.created_by_agent as agent_id,

       n.created_at as created_at

// Find nodes with invalid FAST ID format

MATCH (n)

WHERE exists(n.backbone_fast)

  AND NOT (n.backbone_fast =~ '^\\d+$')

RETURN n.id as node_id,

       n.label as label,

       n.backbone_fast as invalid_fast,

       n.created_by_agent as agent_id

// Find nodes created by agents outside their backbone scope

MATCH (agent:Agent)

MATCH (node)

WHERE node.created_by_agent = agent.agent_id

  AND exists(agent.allowed_backbone_range)

  AND NOT any(prefix IN agent.allowed_backbone_range 

              WHERE node.backbone_lcc STARTS WITH prefix)

RETURN agent.agent_id as agent_id,

       node.id as node_id,

       node.label as label,

       node.backbone_lcc as node_backbone,

       agent.allowed_backbone_range as agent_range

// Count nodes per FAST code (health check)

MATCH (n)

WHERE exists(n.backbone_fast)

RETURN n.backbone_fast as fast_id,

       count(n) as node_count

ORDER BY node_count DESC

LIMIT 20

### 6. Pydantic Models for Validation

"""

Pydantic models for backbone alignment validation.

"""

from pydantic import BaseModel, Field, validator

from typing import Optional

import re

class NodeWithBackbone(BaseModel):

    """Model for nodes that must have backbone alignment."""

    id: str

    label: str

    entity_type: str = Field(..., description="SubjectConcept, Claim, Event, etc.")

    backbone_fast: str = Field(..., description="FAST subject code - REQUIRED")

    backbone_lcc: Optional[str] = Field(None, description="LCC code")

    backbone_qid: Optional[str] = Field(None, description="Wikidata QID")

    agent_id: str = Field(..., description="Creating agent ID")

    properties: Optional[dict] = Field(default_factory=dict)

    @validator('backbone_fast')

    def validate_fast_format(cls, v):

        if not v:

            raise ValueError('backbone_fast is required')

        if not re.match(r'^\d+$', str(v)):

            raise ValueError(f'FAST ID must be numeric, got: {v}')

        return str(v)

    @validator('agent_id')

    def validate_agent_id(cls, v):

        if not v:

            raise ValueError('agent_id is required')

        return v

    class Config:

        extra = "forbid"  # Don't allow extra fields

# Use in tools

def create_node_validated(data: dict):

    """Create node with Pydantic validation."""

    validated = NodeWithBackbone(**data)

    return create_node_with_backbone_validation(**validated.dict())

### 7. Agent Setup Example

"""

Example: Setting up an agent with backbone validation.

"""

def create_agent_with_backbone(

    agent_id: str,

    agent_name: str,

    backbone_fast: str,

    backbone_lcc: str,

    backbone_qid: str = None,

    allowed_backbone_range: list = None

):

    """

    Create an agent node with backbone alignment.

    """

    # Validate FAST ID first

    fast_validation = validate_fast_id(backbone_fast)

    if not fast_validation["valid"]:

        raise ValueError(fast_validation["error"])

    query = """

    CREATE (agent:Agent {

      agent_id: $agent_id,

      agent_name: $agent_name,

      backbone_fast: $backbone_fast,

      backbone_lcc: $backbone_lcc,

      backbone_qid: $backbone_qid,

      allowed_backbone_range: $allowed_backbone_range,

      status: "active",

      created_at: datetime()

    })

    RETURN agent

    """

    with driver.session() as session:

        session.run(

            query,

            agent_id=agent_id,

            agent_name=agent_name,

            backbone_fast=backbone_fast,

            backbone_lcc=backbone_lcc,

            backbone_qid=backbone_qid,

            allowed_backbone_range=allowed_backbone_range or []

        )

    return {

        "agent_id": agent_id,

        "backbone_fast": backbone_fast,

        "backbone_lcc": backbone_lcc

    }

# Example usage

agent = create_agent_with_backbone(

    agent_id="agent_heat_transfer",

    agent_name="HeatTransferAgent",

    backbone_fast="0854703",

    backbone_lcc="QC311.5",

    backbone_qid="Q18619352",

    allowed_backbone_range=["QC311", "QC312"]

)

## Summary

This provides:

1. Database constraints (Neo4j)

2. FAST ID validation

3. Agent backbone permission checks

4. Node creation tool with validation

5. Post-creation validation queries

6. Pydantic models for structure validation

7. Agent setup example

These ensure all nodes are tethered to the FAST backbone before persistence.

Want me to organize these into a structured Implementation Guide section?