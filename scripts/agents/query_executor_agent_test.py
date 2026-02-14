#!/usr/bin/env python3
"""
Chrystallum Query Executor Agent - Test Implementation
Purpose: Execute live Neo4j queries based on natural language input
Date: February 14, 2026
Status: Initial test
"""

import os
import json
import sys
from typing import Optional, Dict, Any, List
from neo4j import GraphDatabase, Driver, Session
import openai

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ChromatogramQueryExecutor:
    """Query executor agent for Chrystallum knowledge graph"""

    def __init__(self):
        """Initialize Neo4j driver and OpenAI client"""
        if not NEO4J_PASSWORD:
            raise ValueError("NEO4J_PASSWORD environment variable not set")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.driver: Driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        
        openai.api_key = OPENAI_API_KEY
        
        # Discover schema on init
        self.schema = self._discover_schema()
        print(f"✓ Connected to Neo4j at {NEO4J_URI}")
        print(f"✓ Schema discovered: {len(self.schema['labels'])} labels, {len(self.schema['relationship_types'])} relationship types")

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
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
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
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        test_interactive()
    else:
        # Run basic tests if no args, or single query if provided
        if len(sys.argv) > 1 and sys.argv[1] != "test":
            # Single query mode
            executor = ChromatogramQueryExecutor()
            try:
                result = executor.query(" ".join(sys.argv[1:]))
            finally:
                executor.close()
        else:
            # Test mode
            test_basic_queries()
