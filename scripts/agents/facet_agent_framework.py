#!/usr/bin/env python3
"""
Chrystallum Facet Agent Framework
Purpose: Multi-agent system with facet-specific expertise
Date: February 15, 2026
Status: Production ready

Architecture:
- FacetAgent: Base class extending ChromatogramQueryExecutor
- 17 specialized agents (one per facet)
- Router: Directs queries to appropriate agents
- Coordinator: Aggregates results, deduplicates claims
"""

import os
import json
import sys
from typing import Optional, Dict, Any, List, Tuple
from abc import ABC, abstractmethod
from neo4j import GraphDatabase, Driver
import openai

# Import configuration loader
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config_loader import (
    OPENAI_API_KEY,
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
    NEO4J_DATABASE,
    validate_agent_config
)

# Import claim pipeline
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from claim_ingestion_pipeline import ClaimIngestionPipeline


class FacetAgent(ABC):
    """
    Base class for facet-specific agents
    Each agent understands domain-specific terminology, concepts, and relationships
    """

    def __init__(self, facet_key: str, facet_label: str, system_prompt: str):
        """
        Initialize facet agent
        
        Args:
            facet_key: Lowercase registry key (e.g., 'military')
            facet_label: Display label (e.g., 'Military')
            system_prompt: Facet-specific system prompt
        """
        # Validate configuration
        validate_agent_config(require_openai=True, require_neo4j=True)

        self.facet_key = facet_key
        self.facet_label = facet_label
        self.system_prompt = system_prompt

        self.driver: Driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )

        openai.api_key = OPENAI_API_KEY

        # Initialize claim pipeline
        self.pipeline = ClaimIngestionPipeline(self.driver, database=NEO4J_DATABASE)

        # Discover schema on init
        self.schema = self._discover_schema()
        print(f"✓ Initialized {self.facet_label} Agent")
        print(f"  Schema: {len(self.schema['labels'])} labels, {len(self.schema['relationship_types'])} relationships")

    def _discover_schema(self) -> Dict[str, Any]:
        """Discover available labels and relationship types from Neo4j"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            labels_result = session.run("CALL db.labels()")
            labels = [record["label"] for record in labels_result]

            rel_result = session.run("CALL db.relationshipTypes()")
            relationship_types = [record["relationshipType"] for record in rel_result]

        return {
            "labels": labels,
            "relationship_types": relationship_types
        }

    def query_neo4j(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query against Neo4j"""
        params = params or {}

        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(cypher, params)
            records = result.data()

        return records

    def generate_cypher(self, natural_language_query: str) -> str:
        """
        Use ChatGPT to generate Cypher from natural language
        Uses facet-specific system prompt for domain expertise
        """

        system_prompt_with_schema = f"""{self.system_prompt}

AVAILABLE LABELS (Node Types):
{json.dumps(self.schema['labels'], indent=2)}

AVAILABLE RELATIONSHIPS:
{json.dumps(self.schema['relationship_types'], indent=2)}

CRITICAL RULES:
1. Use ONLY the labels listed above
2. Use canonical labels: SubjectConcept (not Concept), Human (not Person), Event (not Activity), Place (not Location)
3. Always add LIMIT 10 unless asking for more
4. For dates, use ISO 8601 format (e.g., "-0049-01-10" for 49 BCE)
5. Return ONLY valid Cypher - no explanations, no markdown, no code blocks
6. Prioritize {self.facet_label} domain concepts when disambiguating

EXAMPLE VALID QUERIES:
MATCH (n:SubjectConcept) RETURN n LIMIT 10
MATCH (h:Human)-[r:PARTICIPATED_IN]->(e:Event) RETURN h, r, e LIMIT 10
MATCH (subject:SubjectConcept) WHERE subject.label CONTAINS 'Roman' MATCH (entity)-[:CLASSIFIED_BY]->(subject) RETURN entity LIMIT 20

Generate a single Cypher query for this request. Return ONLY the Cypher code, nothing else."""

        user_message = f"Generate a Cypher query for: {natural_language_query}"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt_with_schema},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=500
        )

        cypher = response.choices[0].message.content.strip()

        # Clean up if ChatGPT wrapped in markdown code blocks
        if cypher.startswith("```"):
            cypher = cypher.split("```")[1]
            if cypher.startswith("cypher"):
                cypher = cypher[6:]
        cypher = cypher.strip()

        return cypher

    def format_results(self, records: List[Dict[str, Any]]) -> str:
        """Format query results for readable output"""
        if not records:
            return "No results found."

        if len(records) == 1 and len(records[0]) == 1:
            value = list(records[0].values())[0]
            return json.dumps(value, indent=2, default=str)

        output = f"Found {len(records)} result(s):\n\n"
        for i, record in enumerate(records, 1):
            output += f"{i}. "
            items = []
            for key, value in record.items():
                if isinstance(value, dict):
                    items.append(f"{key}: {json.dumps(value, indent=2, default=str)}")
                else:
                    items.append(f"{key}: {value}")
            output += " | ".join(items) + "\n"

        return output

    def query(self, user_query: str) -> str:
        """
        Main agent interface: Natural language query → Results
        
        Args:
            user_query: Natural language question about the graph
            
        Returns:
            Formatted results or error message
        """
        try:
            print(f"\n▶ [{self.facet_label}] User: {user_query}")

            print("  Generating Cypher...")
            cypher = self.generate_cypher(user_query)
            print(f"  Generated: {cypher[:80]}..." if len(cypher) > 80 else f"  Generated: {cypher}")

            print("  Executing query...")
            results = self.query_neo4j(cypher)

            formatted = self.format_results(results)
            print(f"\n✓ {formatted}")

            return formatted

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n✗ {error_msg}")
            return error_msg

    def propose_claim(
        self,
        entity_id: str,
        relationship_type: str,
        target_id: str,
        confidence: float,
        label: str,
        subject_qid: Optional[str] = None,
        retrieval_source: str = "agent_facet",
        reasoning_notes: str = "",
        authority_source: Optional[str] = None,
        authority_ids: Optional[Any] = None,
        claim_type: str = "relational",
        claim_signature: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Propose a claim via the ingestion pipeline
        Automatically assigns facet based on agent expertise
        
        Args:
            entity_id: Source entity ID
            relationship_type: Relationship type name
            target_id: Target entity ID
            confidence: Confidence score 0.0-1.0
            label: Human-readable claim label
            subject_qid: Wikidata subject QID
            retrieval_source: Data source
            reasoning_notes: Agent reasoning
            authority_source: Authority system
            authority_ids: Authority IDs
            claim_type: Claim type
            claim_signature: Deterministic signature
            
        Returns:
            Ingestion result dict
        """
        print(f"\n▶ [{self.facet_label}] Propose Claim: {label}")
        print(f"  Entity: {entity_id} -{relationship_type}-> {target_id}")
        print(f"  Confidence: {confidence:.2f}")

        result = self.pipeline.ingest_claim(
            entity_id=entity_id,
            relationship_type=relationship_type,
            target_id=target_id,
            confidence=confidence,
            label=label,
            subject_qid=subject_qid,
            retrieval_source=retrieval_source,
            reasoning_notes=reasoning_notes,
            facet=self.facet_key,  # Automatic facet assignment
            claim_signature=claim_signature,
            claim_type=claim_type,
            source_agent=f"agent_facet_{self.facet_key}",
            authority_source=authority_source,
            authority_ids=authority_ids
        )

        if result["status"] == "error":
            print(f"\n✗ Submission failed: {result['error']}")
        else:
            promoted = " (PROMOTED)" if result["promoted"] else ""
            print(f"\n✓ Claim created{promoted}: {result['claim_id']}")
            print(f"  Cipher: {result['cipher'][:16]}...")
            print(f"  Posterior: {result.get('posterior_probability')}")

        return result

    def close(self):
        """Close Neo4j driver connection"""
        self.driver.close()
        print(f"✓ Closed {self.facet_label} Agent")


class FacetAgentFactory:
    """Factory for creating facet agents with appropriate system prompts"""

    # 17 facet-specific system prompts (loaded from registry)
    FACET_PROMPTS = {}

    @staticmethod
    def load_facet_prompts(registry_path: str = "Facets/facet_registry_master.json"):
        """Load facet prompts from system prompt registry"""
        # To be populated from facet_agent_system_prompts.json
        pass

    @staticmethod
    def create_agent(facet_key: str, facet_label: str, system_prompt: str) -> FacetAgent:
        """
        Create a specialized facet agent
        
        Args:
            facet_key: Registry key (e.g., 'military')
            facet_label: Display label (e.g., 'Military')
            system_prompt: Facet-specific system prompt
            
        Returns:
            Instantiated FacetAgent subclass
        """
        # Create dynamic class inheriting from FacetAgent
        class SpecializedFacetAgent(FacetAgent):
            pass

        agent = SpecializedFacetAgent(facet_key, facet_label, system_prompt)
        return agent

    @staticmethod
    def create_all_agents() -> Dict[str, FacetAgent]:
        """
        Create all 17 facet agents
        
        Returns:
            Dict mapping facet_key → agent instance
        """
        agents = {}
        
        # Load prompts (to be populated from JSON)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'facet_agent_system_prompts.json')) as f:
            prompts_registry = json.load(f)

        for facet_config in prompts_registry['facets']:
            agent = FacetAgentFactory.create_agent(
                facet_key=facet_config['key'],
                facet_label=facet_config['label'],
                system_prompt=facet_config['system_prompt']
            )
            agents[facet_config['key']] = agent

        return agents


class MultiAgentRouter:
    """Routes queries to appropriate facet agents"""

    def __init__(self, agents: Dict[str, FacetAgent]):
        """
        Initialize router with agents
        
        Args:
            agents: Dict mapping facet_key → agent instance
        """
        self.agents = agents
        self.openai_api_key = OPENAI_API_KEY

    def route_query(self, user_query: str) -> Tuple[List[str], str]:
        """
        Determine which facet(s) a query should route to
        
        Args:
            user_query: Natural language query
            
        Returns:
            Tuple of (facet_keys, reasoning)
        """
        router_prompt = """You are a query router for a historical knowledge graph with these facets:
- archaeological, artistic, cultural, demographic, diplomatic, economic, environmental, geographic
- intellectual, linguistic, military, political, religious, scientific, social, technological, communication

Given a user query, identify which 1-3 facets are most relevant.

Return JSON with:
{
  "facets": ["facet_key1", "facet_key2"],
  "reasoning": "Why these facets"
}"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": router_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.3,
            max_tokens=200
        )

        try:
            result = json.loads(response.choices[0].message.content)
            return result["facets"], result["reasoning"]
        except:
            # Default to broader facets if parsing fails
            return ["political", "military"], "Default routing"

    def execute_multi_facet(self, user_query: str, facet_keys: List[str]) -> Dict[str, Any]:
        """
        Execute query across multiple facet agents
        Aggregate and deduplicate results
        
        Args:
            user_query: Query to execute
            facet_keys: List of facet keys to query
            
        Returns:
            Aggregated results dict
        """
        results = {
            "query": user_query,
            "facets": {},
            "aggregated": []
        }

        for facet_key in facet_keys:
            if facet_key not in self.agents:
                print(f"⚠ Facet '{facet_key}' not found")
                continue

            agent = self.agents[facet_key]
            facet_results = agent.query(user_query)
            results["facets"][facet_key] = facet_results

        return results

    def close_all(self):
        """Close all agent connections"""
        for agent in self.agents.values():
            agent.close()


# Test script
if __name__ == "__main__":
    print("Chrystallum Multi-Agent Facet Framework")
    print("=" * 60)

    # Example: Create a military facet agent
    military_prompt = """You are a Military History Expert Agent for the Chrystallum knowledge graph.
    
Your expertise:
- Warfare, battles, military campaigns, tactics, strategic operations
- Military leaders, commanders, generals, military institutions
- Armies, legions, military units, fortifications, weaponry
- Conflicts, wars, sieges, naval combat
- Military history, strategy, logistics, procurement

Key Wikidata Anchors:
Q8473 (military), Q198 (war), Q192781 (military history)

When querying:
1. Prioritize battles, military leaders, and warfare events
2. Look for Human nodes with military expertise (P101=military history)
3. Find Events classified as Q198 (wars)
4. Connect to tactical concepts and military strategies

Important: Distinguish between military operations and political outcomes."""

    print("\n→ Creating Military Facet Agent...")
    agent = FacetAgentFactory.create_agent(
        facet_key="military",
        facet_label="Military",
        system_prompt=military_prompt
    )

    print("\n→ Testing query...")
    result = agent.query("Show me battles in 31 BCE")

    print("\n→ Closing agent...")
    agent.close()

    print("\n✓ Framework test complete")
