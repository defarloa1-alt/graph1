

### 1. Agent Self-Assessment Tool

A LangChain tool for agents to assess scope size:

"""

Tool for agents to assess if their domain scope is too large.

"""

def assess_agent_scope(agent_id: str) -> dict:

    """

    Agent assesses if its scope is too large and needs decomposition.

    Metrics:

    - Number of nodes in subgraph

    - Breadth of LCC coverage

    - Number of shell nodes vs expanded

    - Agent activity/confusion signals

    Returns:

        dict with assessment and recommendation

    """

    query = """

    MATCH (agent:Agent {agent_id: $agent_id})

    MATCH (agent)-[:CREATED_ENTITY|CREATED_SHELL]->(node)

    WHERE node.backbone_fast = agent.backbone_fast

       OR node.backbone_lcc STARTS WITH split(agent.backbone_lcc, '-')[0]

    WITH agent, 

         count(DISTINCT node) as node_count,

         collect(DISTINCT node.backbone_lcc) as lcc_codes,

         count(DISTINCT CASE WHEN node.status = 'shell' THEN node END) as shell_count,

         count(DISTINCT CASE WHEN node.status = 'expanded' THEN node END) as expanded_count

    RETURN agent.agent_id as agent_id,

           agent.backbone_lcc as agent_lcc,

           node_count,

           size(lcc_codes) as lcc_span,

           shell_count,

           expanded_count,

           shell_count * 1.0 / (expanded_count + 1) as shell_ratio

    """

    with driver.session() as session:

        result = session.run(query, agent_id=agent_id)

        record = result.single()

        if not record:

            return {"assessment": "no_data", "recommendation": "continue"}

        # Thresholds for decomposition

        MAX_NODES = 1000  # Adjust based on domain

        MAX_LCC_SPAN = 5  # Too many LCC codes = too broad

        SHELL_RATIO_THRESHOLD = 0.7  # Too many shells = underdeveloped

        assessment = {

            "node_count": record["node_count"],

            "lcc_span": record["lcc_span"],

            "shell_ratio": record["shell_ratio"],

            "should_decompose": False,

            "reason": None

        }

        if record["node_count"] > MAX_NODES:

            assessment["should_decompose"] = True

            assessment["reason"] = f"Node count ({record['node_count']}) exceeds threshold ({MAX_NODES})"

        elif record["lcc_span"] > MAX_LCC_SPAN:

            assessment["should_decompose"] = True

            assessment["reason"] = f"LCC span ({record['lcc_span']}) exceeds threshold ({MAX_LCC_SPAN})"

        elif record["shell_ratio"] > SHELL_RATIO_THRESHOLD:

            assessment["should_decompose"] = True

            assessment["reason"] = f"Shell ratio ({record['shell_ratio']:.2f}) indicates underdevelopment"

        return assessment

# LangChain tool

assess_scope_tool = Tool(

    name="assess_agent_scope",

    func=assess_agent_scope,

    description="Assesses if agent's domain scope is too large and needs decomposition. Returns should_decompose=True if scope is too large."

)

### 2. Agent Decomposition Tool

Tool for agents to decompose their domain and spawn new agents:

"""

Tool for agents to decompose their domain and create child agents.

"""

def decompose_domain(

    parent_agent_id: str,

    new_backbone_fast: str,

    new_backbone_lcc: str,

    new_agent_name: str,

    domain_ontology: dict = None

) -> dict:

    """

    Create a new subject agent by decomposing parent agent's domain.

    This implements the dual backbone pattern (§3.6):

    - Universal backbone (LCC/LCSH/FAST) - required

    - Domain-specific ontology - optional for decomposition

    Args:

        parent_agent_id: Agent that's decomposing

        new_backbone_fast: FAST code for new agent

        new_backbone_lcc: LCC code for new agent

        new_agent_name: Name for new agent

        domain_ontology: Domain-specific structure (time periods, dynasties, etc.)

    Returns:

        dict with new agent info

    """

    # Validate parent agent exists

    parent_query = """

    MATCH (parent:Agent {agent_id: $parent_agent_id})

    RETURN parent.backbone_lcc as parent_lcc,

           parent.backbone_fast as parent_fast

    """

    with driver.session() as session:

        parent_result = session.run(parent_query, parent_agent_id=parent_agent_id)

        parent_record = parent_result.single()

        if not parent_record:

            return {

                "success": False,

                "error": f"Parent agent {parent_agent_id} not found"

            }

        # Validate new backbone is within parent's scope

        if not new_backbone_lcc.startswith(parent_record["parent_lcc"].split('-')[0]):

            return {

                "success": False,

                "error": f"New LCC {new_backbone_lcc} is not within parent's scope {parent_record['parent_lcc']}"

            }

        # Generate new agent ID

        import hashlib

        agent_id_content = f"{parent_agent_id}|{new_backbone_fast}|{new_backbone_lcc}"

        new_agent_id = f"{parent_agent_id}_child_{hashlib.sha256(agent_id_content.encode()).hexdigest()[:8]}"

        # Validate new agent doesn't already exist

        existing_query = """

        MATCH (existing:Agent {agent_id: $new_agent_id})

        RETURN existing

        """

        existing = session.run(existing_query, new_agent_id=new_agent_id).single()

        if existing:

            return {

                "success": False,

                "error": f"Agent {new_agent_id} already exists"

            }

        # Create new agent

        create_query = """

        MATCH (parent:Agent {agent_id: $parent_agent_id})

        CREATE (child:Agent {

          agent_id: $new_agent_id,

          agent_name: $new_agent_name,

          backbone_fast: $new_backbone_fast,

          backbone_lcc: $new_backbone_lcc,

          parent_agent_id: $parent_agent_id,

          status: "active",

          created_at: datetime(),

          domain_ontology: $domain_ontology

        })

        CREATE (parent)-[:DECOMPOSED_INTO {

          timestamp: datetime(),

          reason: "scope_too_large"

        }]->(child)

        RETURN child.agent_id as agent_id,

               child.agent_name as agent_name,

               child.backbone_fast as backbone_fast

        """

        result = session.run(

            create_query,

            parent_agent_id=parent_agent_id,

            new_agent_id=new_agent_id,

            new_agent_name=new_agent_name,

            new_backbone_fast=new_backbone_fast,

            new_backbone_lcc=new_backbone_lcc,

            domain_ontology=domain_ontology

        )

        record = result.single()

        # Migrate nodes to child agent if needed

        # (Optional: reassign nodes to child agent's scope)

        return {

            "success": True,

            "new_agent_id": record["agent_id"],

            "agent_name": record["agent_name"],

            "backbone_fast": record["backbone_fast"],

            "parent_agent_id": parent_agent_id

        }

# LangChain tool

decompose_domain_tool = Tool(

    name="decompose_domain",

    func=decompose_domain,

    description="Decomposes agent's domain by creating a new subject agent. Use when scope is too large. Requires: parent_agent_id, new_backbone_fast, new_backbone_lcc, new_agent_name."

)

### 3. LangChain Agent with Decomposition Logic

Agent configuration that includes decomposition:

"""

LangChain agent setup with decomposition capabilities.

"""

from langchain.agents import AgentExecutor, create_structured_chat_agent

from langchain.llms import OpenAI

from langchain.tools import Tool

# Agent tools include decomposition tools

agent_tools = [

    assess_scope_tool,

    decompose_domain_tool,

    create_node_tool,

    validate_fast_tool,

    # ... other tools

]

# Agent prompt includes decomposition instructions

agent_prompt = """

You are {agent_name}, managing the domain {backbone_fast} (FAST: {fast_id}, LCC: {lcc_code}).

Your responsibilities:

1. Extract and learn knowledge within your domain

2. Create nodes and relationships aligned to your backbone

3. Assess if your scope is too large

4. Decompose domain when scope exceeds limits by creating child agents

When to decompose:

- Your subgraph has >1000 nodes, OR

- You cover >5 different LCC codes, OR

- >70% of your nodes are shells (underdeveloped)

When decomposing:

1. Use assess_agent_scope tool to evaluate

2. If should_decompose=True, identify a sub-domain

3. Use decompose_domain tool to create a child agent

4. Continue learning in your narrowed scope

Example decomposition:

- Parent: "American History" (LCC E-F)

- Child 1: "American Civil War" (LCC E456-E655)

- Child 2: "Colonial America" (LCC E186-E199)

Always maintain backbone alignment when decomposing.

"""

# Create agent

llm = OpenAI(temperature=0)

agent = create_structured_chat_agent(llm, agent_tools, agent_prompt)

agent_executor = AgentExecutor(agent=agent, tools=agent_tools)

### 4. Agent Learning Loop with Decomposition Check

Workflow that periodically checks for decomposition:

"""

Agent execution loop that includes decomposition assessment.

"""

def agent_learning_cycle(agent_id: str, task: str):

    """

    Agent learning cycle with decomposition checks.

    Args:

        agent_id: Agent to run

        task: Learning task (e.g., "extract entities from document X")

    """

    # Step 1: Assess current scope

    assessment = assess_agent_scope(agent_id)

    if assessment.get("should_decompose"):

        # Step 2: Decompose domain

        decomposition_prompt = f"""

        Your scope is too large. Assessment: {assessment['reason']}

        Analyze your domain and identify a sub-domain that should be handled by a child agent.

        Consider:

        - Natural boundaries (time periods, topics, themes)

        - LCC code subdivisions

        - Domain ontology structure

        Then use decompose_domain tool to create a child agent.

        """

        # Agent decides how to decompose

        result = agent_executor.run(decomposition_prompt)

        # Continue with narrowed scope or pause

        return {

            "action": "decomposed",

            "assessment": assessment,

            "decomposition_result": result

        }

    # Step 3: Normal learning

    result = agent_executor.run(task)

    return {

        "action": "learned",

        "assessment": assessment,

        "result": result

    }

### 5. Domain Ontology for Decomposition

Support for domain-specific ontology (dual backbone pattern §3.6):

"""

Domain ontology structure for decomposition.

"""

def get_domain_ontology(backbone_fast: str) -> dict:

    """

    Retrieve domain-specific ontology for decomposition.

    For example, "Roman History" domain ontology might have:

    - Time periods: Republic, Empire

    - Dynasties: Julio-Claudian, Flavian

    - Themes: Military, Politics, Culture

    """

    query = """

    MATCH (agent:Agent {backbone_fast: $backbone_fast})

    RETURN agent.domain_ontology as domain_ontology

    """

    with driver.session() as session:

        result = session.run(query, backbone_fast=backbone_fast)

        record = result.single()

        if record and record["domain_ontology"]:

            return record["domain_ontology"]

        # Default: use LCC subdivisions

        return {

            "type": "lcc_subdivision",

            "structure": "hierarchical"

        }

def suggest_decomposition_structure(parent_agent_id: str) -> list:

    """

    Suggest how to decompose a domain based on backbone and ontology.

    Returns:

        List of potential child agent configurations

    """

    # Get parent agent

    parent_query = """

    MATCH (parent:Agent {agent_id: $parent_agent_id})

    RETURN parent.backbone_lcc as parent_lcc,

           parent.backbone_fast as parent_fast,

           parent.domain_ontology as domain_ontology

    """

    with driver.session() as session:

        parent_result = session.run(parent_query, parent_agent_id=parent_agent_id)

        parent = parent_result.single()

        if not parent:

            return []

        suggestions = []

        # Example: If parent is "Roman History" (DG231-261)

        # Suggest subdivisions like:

        # - "Roman Republic" (DG231-241)

        # - "Roman Empire" (DG241-261)

        # This would use domain ontology or LCC subdivision logic

        # Implementation depends on your ontology structure

        return suggestions

### 6. Neo4j Schema for Agent Decomposition

Graph structure for agent relationships:

// Agent decomposition relationship

// Parent agent DECOMPOSED_INTO child agent

CREATE (parent:Agent {agent_id: "agent_roman_history"})

CREATE (child:Agent {agent_id: "agent_roman_republic"})

CREATE (parent)-[:DECOMPOSED_INTO {

  timestamp: datetime(),

  reason: "scope_too_large",

  assessment: {node_count: 1500, lcc_span: 8}

}]->(child)

// Query decomposition tree

MATCH path = (root:Agent)-[:DECOMPOSED_INTO*]->(child:Agent)

WHERE root.agent_id = "agent_roman_history"

RETURN path

// Find leaf agents (no children)

MATCH (agent:Agent)

WHERE NOT (agent)-[:DECOMPOSED_INTO]->()

RETURN agent.agent_id, agent.backbone_fast

## Summary

1. Self-assessment: Agents check scope size using metrics

2. Decomposition decision: When scope is too large, agent decides to decompose

3. Child agent creation: Agent spawns new LangChain agent for sub-domain

4. Dual backbone: New agents maintain universal backbone + domain ontology

5. Continuation: Parent agent continues in narrowed scope

This implements the dual backbone pattern (§3.6) where seed agents recursively decompose until reaching "trainable units."

Want me to expand any specific part or show the complete agent lifecycle?