#!/usr/bin/env python3
"""
Chrystallum Query Executor Agent - Test Implementation
Purpose: Execute live Neo4j queries and submit claims
Date: February 14, 2026
Status: Initial test

Usage:
  python query_executor_agent_test.py                    # Run basic query tests
  python query_executor_agent_test.py test              # Run predefined test queries
  python query_executor_agent_test.py claims            # Run claim submission tests
  python query_executor_agent_test.py interactive       # Run interactive REPL mode
  python query_executor_agent_test.py "<natural query>" # Execute single query

Environment Variables (Required):
  NEO4J_PASSWORD      - Password for Neo4j authentication
  OPENAI_API_KEY      - OpenAI API key for ChatGPT access
  NEO4J_URI           - Neo4j connection string (default: bolt://localhost:7687)
  NEO4J_USERNAME      - Neo4j username (default: neo4j)
  NEO4J_DATABASE      - Neo4j database name (default: neo4j)
"""

import os
import json
import sys
from typing import Optional, Dict, Any, List
from neo4j import GraphDatabase, Driver, Session
from openai import OpenAI

# Import claim pipeline
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from claim_ingestion_pipeline import ClaimIngestionPipeline

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ChromatogramQueryExecutor:
    """Query executor agent for Chrystallum knowledge graph"""

    def __init__(self):
        """Initialize Neo4j driver, OpenAI client, and claim pipeline"""
        if not NEO4J_PASSWORD:
            raise ValueError("NEO4J_PASSWORD environment variable not set")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.driver: Driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Initialize claim pipeline
        self.pipeline = ClaimIngestionPipeline(self.driver, database=NEO4J_DATABASE)
        
        # Discover schema on init
        self.schema = self._discover_schema()
        print(f"✓ Connected to Neo4j at {NEO4J_URI}")
        print(f"✓ Schema discovered: {len(self.schema['labels'])} labels, {len(self.schema['relationship_types'])} relationship types")
        print(f"✓ Claim pipeline initialized")

    def _discover_schema(self) -> Dict[str, Any]:
        """Discover available labels and relationship types from Neo4j"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Get labels
            labels_result = session.run("CALL db.labels()")
            labels = [record["label"] for record in labels_result]
            
            # Get relationship types
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
        """Use ChatGPT to generate Cypher from natural language"""
        
        system_prompt = f"""You are a Cypher query generator for a historical knowledge graph (Chrystallum).

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

EXAMPLE VALID QUERIES:
MATCH (n:SubjectConcept) RETURN n LIMIT 10
MATCH (h:Human)-[r:PARTICIPATED_IN]->(e:Event) RETURN h, r, e LIMIT 10
MATCH (subject:SubjectConcept) WHERE subject.label CONTAINS 'Roman' MATCH (entity)-[:CLASSIFIED_BY]->(subject) RETURN entity LIMIT 20

Generate a single Cypher query for this request. Return ONLY the Cypher code, nothing else."""

        user_message = f"Generate a Cypher query for: {natural_language_query}"
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        cypher = (response.choices[0].message.content or "").strip()
        
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
            # Single value result
            value = list(records[0].values())[0]
            return json.dumps(value, indent=2, default=str)
        
        # Multiple results or multiple columns
        output = f"Found {len(records)} result(s):\n\n"
        for i, record in enumerate(records, 1):
            output += f"{i}. "
            items = []
            for key, value in record.items():
                if isinstance(value, dict):
                    # Node or relationship object
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
            print(f"\n▶ User: {user_query}")
            
            # Generate Cypher
            print("  Generating Cypher...")
            cypher = self.generate_cypher(user_query)
            print(f"  Generated: {cypher[:80]}..." if len(cypher) > 80 else f"  Generated: {cypher}")
            
            # Execute query
            print("  Executing query...")
            results = self.query_neo4j(cypher)
            
            # Format results
            formatted = self.format_results(results)
            print(f"\n✓ {formatted}")
            
            return formatted
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n✗ {error_msg}")
            return error_msg

    def interactive_session(self):
        """Run an interactive query session"""
        print("\n" + "="*60)
        print("Chrystallum Query Executor Agent - Interactive Mode")
        print("="*60)
        print(f"Connected to: {NEO4J_URI}/{NEO4J_DATABASE}")
        print(f"Schema: {len(self.schema['labels'])} labels, {len(self.schema['relationship_types'])} relationships")
        print("\nType queries in natural language. Type 'exit' to quit.\n")
        
        while True:
            try:
                query = input("Query> ").strip()
                if query.lower() == "exit":
                    print("Goodbye!")
                    break
                if not query:
                    continue
                
                self.query(query)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

    def submit_claim(
        self,
        entity_id: str,
        relationship_type: str,
        target_id: str,
        confidence: float,
        label: str,
        subject_qid: Optional[str] = None,
        retrieval_source: str = "agent_extraction",
        reasoning_notes: str = "",
        facet: Optional[str] = None,
        authority_source: Optional[str] = None,
        authority_ids: Optional[Any] = None,
        claim_type: str = "relational",
        claim_signature: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Submit a claim via the ingestion pipeline
        
        Args:
            entity_id: Source entity ID
            relationship_type: Relationship type name
            target_id: Target entity ID
            confidence: Confidence score 0.0-1.0
            label: Human-readable claim label
            subject_qid: Wikidata subject QID
            retrieval_source: Data source
            reasoning_notes: Agent reasoning
            facet: Domain facet
            authority_source: Authority system (e.g., wikidata, lcsh, freebase)
            authority_ids: Authority IDs (e.g., QID, LCSH ID, string identifier)
            claim_type: Claim type (e.g., 'relational', 'temporal', 'motivational')
            claim_signature: Deterministic signature (QID + full statement signature)
            
        Returns:
            Ingestion result dict
        """
        print(f"\n▶ Submit Claim: {label}")
        print(f"  Entity: {entity_id} -{relationship_type}-> {target_id}")
        print(f"  Confidence: {confidence:.2f}")

        facet = facet.strip().lower() if facet else ""
        if not facet:
            raise ValueError("facet is required (lowercase registry key)")
        
        result = self.pipeline.ingest_claim(
            entity_id=entity_id,
            relationship_type=relationship_type,
            target_id=target_id,
            confidence=confidence,
            label=label,
            subject_qid=subject_qid,
            retrieval_source=retrieval_source,
            reasoning_notes=reasoning_notes,
            facet=facet,
            claim_signature=claim_signature,
            claim_type=claim_type,
            source_agent="agent_query_executor",
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
            print(f"  Critical fallacy: {result.get('critical_fallacy')}")
            if result.get("fallacies_detected"):
                print(f"  Fallacies: {', '.join(result['fallacies_detected'])}")
        
        return result

    def close(self):
        """Close Neo4j driver connection"""
        self.driver.close()


def test_basic_queries():
    """Run predefined test queries"""
    executor = ChromatogramQueryExecutor()
    
    test_queries = [
        "Show me all SubjectConcept nodes",
        "What Humans are in the graph?",
        "Show me Events from 49 BCE",
        "Find all Places",
    ]
    
    print("\n" + "="*60)
    print("Running Test Queries")
    print("="*60)
    
    for query in test_queries:
        executor.query(query)
        print()
    
    executor.close()


def test_claim_submission():
    """Test claim submission workflow"""
    executor = ChromatogramQueryExecutor()
    
    print("\n" + "="*60)
    print("Testing Claim Submission Workflow")
    print("="*60)
    
    # Example: Low confidence claim (proposed)
    print("\n[Test 1] Low confidence claim (proposed)")
    result = executor.submit_claim(
        entity_id="evt_battle_of_actium_q193304",
        relationship_type="OCCURRED_DURING",
        target_id="prd_roman_republic_q17167",
        confidence=0.75,
        label="Battle of Actium occurred during Roman Republic",
        subject_qid="Q17167",
        authority_source="wikidata",
        authority_ids={"Q17167": "P31", "Q193304": "P580"},
        reasoning_notes="Agent observed historical sources confirming event timing",
        facet="military",
        claim_signature={
            "qid": "Q17167",
            "pvalues": ["P31", "P361"],
            "values": {"P31": "Q3024240", "P361": "Q17167"}
        }
    )
    
    # Example: High confidence descriptive claim (should promote)
    print("\n[Test 2] High confidence DESCRIPTIVE claim (geographic facet)")
    print("  Claim type: 'locational' (descriptive)")
    result2 = executor.submit_claim(
        entity_id="evt_battle_of_actium_q193304",
        relationship_type="LOCATED_IN",
        target_id="plc_actium_q41747",
        confidence=0.95,
        label="Battle of Actium took place at Actium",
        subject_qid="Q17167",
        authority_source="wikidata",
        authority_ids={"Q41747": "P276"},
        reasoning_notes="Direct historical source confirmation with high reliability",
        facet="geographic",
        claim_type="locational",
        claim_signature={
            "qid": "Q17167",
            "pvalues": ["P276", "P361"],
            "values": {"P276": "Q41747", "P361": "Q17167"}
        }
    )
    print(f"  Result: {result2['status']}, Promoted: {result2['promoted']}")
    if result2.get('fallacies_detected'):
        print(f"  Fallacy Flag: {result2.get('fallacy_flag_intensity')} (detected: {result2['fallacies_detected']})")
    
    # Example: High confidence INTERPRETIVE claim (should promote, but flag fallacies)
    print("\n[Test 3] High confidence INTERPRETIVE claim (political facet)")
    print("  Claim type: 'motivational' (interpretive)")
    print("  Note: Promotes on metrics, but fallacies flagged 'high' for review")
    result3 = executor.submit_claim(
        entity_id="fig_julius_caesar_q1",
        relationship_type="MOTIVATED_BY",
        target_id="evt_gallic_wars_q123",
        confidence=0.92,
        label="Julius Caesar wanted to conquer Gaul for political power",
        subject_qid="Q1",
        authority_source="wikidata",
        authority_ids={"Q1": "P31"},
        reasoning_notes="Caesar's motivations were to gain military prestige and wealth for political ambitions",
        facet="political",
        claim_type="motivational",
        claim_signature={
            "qid": "Q1",
            "pvalues": ["P31", "P361"],
            "values": {"P31": "Q214650", "P361": "Q1"}
        }
    )
    print(f"  Result: {result3['status']}, Promoted: {result3['promoted']}")
    if result3.get('fallacies_detected'):
        print(f"  Fallacy Flag: {result3.get('fallacy_flag_intensity')} (detected: {result3['fallacies_detected']})")
    if result3.get('fallacies_detected'):
        print(f"  Fallacies: {result3['fallacies_detected']}")
        print(f"  Critical: {result3['critical_fallacy']} → Blocks promotion if true")
    
    executor.close()



def test_interactive():
    """Run interactive mode for manual testing"""
    executor = ChromatogramQueryExecutor()
    try:
        executor.interactive_session()
    finally:
        executor.close()


if __name__ == "__main__":
    print("Chrystallum Query Executor Agent")
    print("="*60)
    
    # Check for required environment variables
    if not NEO4J_PASSWORD:
        print("ERROR: NEO4J_PASSWORD not set")
        print("Usage:")
        print("  export NEO4J_PASSWORD=your_password")
        print("  export OPENAI_API_KEY=your_api_key")
        print("  python query_executor_agent_test.py")
        sys.exit(1)
    
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set")
        print("Usage:")
        print("  export OPENAI_API_KEY=your_api_key")
        sys.exit(1)
    
    # Run tests or interactive mode
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            test_interactive()
        elif sys.argv[1] == "claims":
            test_claim_submission()
        elif sys.argv[1] == "test":
            test_basic_queries()
        else:
            # Single query mode
            executor = ChromatogramQueryExecutor()
            try:
                result = executor.query(" ".join(sys.argv[1:]))
            finally:
                executor.close()
    else:
        # Default: run basic tests
        test_basic_queries()
