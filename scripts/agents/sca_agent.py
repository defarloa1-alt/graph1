#!/usr/bin/env python3
"""
Subject Concept Agent (SCA) - Python Implementation with Perplexity

Stateless agent that:
- Bootstraps from Neo4j Chrystallum system subgraph
- Uses Perplexity API for reasoning and classification
- Queries Wikidata for hierarchy and backlinks
- Creates proposals for human approval
- Writes approved items to Neo4j
"""

import os
import json
import hashlib
import requests
from datetime import datetime
from typing import Dict, List, Optional
from neo4j import GraphDatabase


class SCAAgent:
    """Subject Concept Agent - Stateless orchestrator"""
    
    def __init__(self, 
                 neo4j_uri: str,
                 neo4j_user: str,
                 neo4j_password: str,
                 perplexity_api_key: Optional[str] = None):
        """
        Initialize SCA Agent
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            perplexity_api_key: Perplexity API key (optional)
        """
        # Neo4j connection
        self.driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )
        
        # Perplexity API
        self.perplexity_api_key = perplexity_api_key or os.getenv('PERPLEXITY_API_KEY')
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        
        # State (loaded from Neo4j on bootstrap)
        self.federations = []
        self.facets = []
        self.entity_types = []
        self.active_agents = []
        self.subject_concepts = []
        
        # Bootstrap
        self.bootstrap()
    
    def bootstrap(self):
        """
        Bootstrap from Neo4j Chrystallum system subgraph
        
        Loads complete operational context:
        - Federations
        - Facets
        - Entity types
        - Active agents
        - Existing SubjectConcepts
        """
        print("=" * 80)
        print("SCA BOOTSTRAP - Loading from Chrystallum")
        print("=" * 80)
        print()
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (sys:Chrystallum)
                
                // Get Federations (SYS_FederationRegistry -> SYS_FederationSource)
                OPTIONAL MATCH (sys)-[:HAS_FEDERATION]->(fed_root:SYS_FederationRegistry)
                OPTIONAL MATCH (fed_root)-[:CONTAINS]->(fed:SYS_FederationSource)
                
                // Get Facets
                OPTIONAL MATCH (sys)-[:HAS_FACET_ROOT]->(facet_root)
                OPTIONAL MATCH (facet_root)-[:HAS_FACET]->(facet:Facet)
                
                // Get Entity Types
                OPTIONAL MATCH (sys)-[:HAS_ENTITY_ROOT]->(entity_root)
                OPTIONAL MATCH (entity_root)-[:HAS_ENTITY_TYPE]->(et:EntityType)
                
                // Get Agents
                OPTIONAL MATCH (sys)-[:HAS_SUBJECT_CONCEPT_ROOT]->(sc_root)
                OPTIONAL MATCH (sc_root)-[:HAS_AGENT_REGISTRY]->(agent_reg)
                OPTIONAL MATCH (agent_reg)-[:HAS_AGENT]->(agent:Agent)
                
                // Get SubjectConcepts
                OPTIONAL MATCH (sc_root)-[:HAS_SUBJECT_REGISTRY]->(sc_reg)
                OPTIONAL MATCH (sc_reg)-[:CONTAINS]->(sc:SubjectConcept)
                
                RETURN 
                  collect(DISTINCT fed) AS federations,
                  collect(DISTINCT facet) AS facets,
                  collect(DISTINCT et) AS entity_types,
                  collect(DISTINCT agent) AS agents,
                  collect(DISTINCT sc) AS subject_concepts
            """)
            
            data = result.single()
            
            # Store in memory
            self.federations = [dict(f) for f in data['federations'] if f is not None]
            self.facets = [dict(f) for f in data['facets']]
            self.entity_types = [dict(et) for et in data['entity_types']]
            self.active_agents = [dict(a) for a in data['agents']]
            self.subject_concepts = [dict(sc) for sc in data['subject_concepts']]
        
        print(f"Loaded from Chrystallum:")
        print(f"  Federations: {len(self.federations)}")
        print(f"  Facets: {len(self.facets)}")
        print(f"  Entity Types: {len(self.entity_types)}")
        print(f"  Active Agents: {len(self.active_agents)}")
        print(f"  SubjectConcepts: {len(self.subject_concepts)}")
        print()
        
        # Validate
        self._validate_bootstrap()
    
    def _validate_bootstrap(self):
        """Validate bootstrap loaded correct configuration"""
        
        # Check facet count
        assert len(self.facets) == 18, f"Should have 18 facets, got {len(self.facets)}"
        
        # Check no forbidden facets
        facet_keys = [f['key'] for f in self.facets]
        forbidden = ['TEMPORAL', 'CLASSIFICATION', 'PATRONAGE', 'GENEALOGICAL']
        for f in forbidden:
            assert f not in facet_keys, f"Forbidden facet {f} found!"
        
        # Check facets are uppercase
        for key in facet_keys:
            assert key == key.upper(), f"Facet {key} must be uppercase"
        
        print("Bootstrap validation: PASSED")
        print()
    
    def query_perplexity(self, prompt: str, model: str = "llama-3.1-sonar-large-128k-online") -> Dict:
        """
        Query Perplexity API for reasoning/classification
        
        Args:
            prompt: Question/task for Perplexity
            model: Perplexity model (online models have web access)
        
        Returns:
            Response dict with content and sources
        """
        if not self.perplexity_api_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a historical research assistant analyzing periods and temporal concepts. Provide scholarly analysis with citations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = requests.post(self.perplexity_url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'content': data['choices'][0]['message']['content'],
            'model': model,
            'usage': data.get('usage', {})
        }
    
    def query_wikidata_sparql(self, sparql_query: str) -> List[Dict]:
        """
        Query Wikidata SPARQL endpoint
        
        Args:
            sparql_query: SPARQL query string
        
        Returns:
            List of result bindings
        """
        endpoint = "https://query.wikidata.org/sparql"
        
        headers = {
            'User-Agent': 'Chrystallum/1.0 (research project)',
            'Accept': 'application/sparql-results+json'
        }
        
        response = requests.get(
            endpoint,
            params={'query': sparql_query, 'format': 'json'},
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        return data['results']['bindings']
    
    def discover_period_backlinks(self, seed_qid: str) -> List[Dict]:
        """
        Discover periods via Wikidata backlinks
        
        Args:
            seed_qid: Seed QID (e.g., 'Q11756' for prehistory)
        
        Returns:
            List of candidate period QIDs with metadata
        """
        print(f"Discovering backlinks from {seed_qid}...")
        
        # SPARQL: Find all items that link TO this QID
        sparql = f"""
        SELECT DISTINCT ?item ?itemLabel ?instanceOf ?instanceOfLabel
        WHERE {{
          ?item ?prop wd:{seed_qid} .
          OPTIONAL {{ ?item wdt:P31 ?instanceOf }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 500
        """
        
        results = self.query_wikidata_sparql(sparql)
        
        candidates = []
        for binding in results:
            item_qid = binding['item']['value'].split('/')[-1]
            candidates.append({
                'qid': item_qid,
                'label': binding.get('itemLabel', {}).get('value', ''),
                'instance_of': binding.get('instanceOfLabel', {}).get('value', ''),
                'instance_of_qid': binding.get('instanceOf', {}).get('value', '').split('/')[-1] if binding.get('instanceOf') else None
            })
        
        print(f"  Found {len(candidates)} candidates")
        return candidates
    
    def classify_period_candidate(self, candidate: Dict) -> Dict:
        """
        Use Perplexity to classify a period candidate
        
        Args:
            candidate: Candidate dict with qid, label, etc.
        
        Returns:
            Classification result
        """
        prompt = f"""
        Analyze this historical concept: {candidate['label']} (Wikidata {candidate['qid']})
        
        Questions:
        1. Is this a Period (extended time span used as grouping category) or an Event (specific occurrence)?
        2. If Period, what type? (political, cultural, geological, technological, military, social, religious, etc.)
        3. What are the approximate start and end dates?
        4. Confidence in this classification (0-1)?
        
        Provide brief, structured answer.
        """
        
        result = self.query_perplexity(prompt)
        
        # Parse Perplexity response (simplified - would need robust parsing)
        content = result['content']
        
        return {
            'qid': candidate['qid'],
            'label': candidate['label'],
            'classification': content,
            'classified_by': 'perplexity',
            'model': result['model']
        }
    
    def create_period_proposal(self, 
                               qid: str,
                               label: str,
                               period_type: str,
                               start_year: int,
                               end_year: int,
                               periodo_id: Optional[str] = None,
                               confidence: float = 0.8) -> Dict:
        """
        Create a Period node proposal
        
        Args:
            qid: Wikidata QID
            label: Period label
            period_type: Type (political, cultural, etc.)
            start_year, end_year: Temporal bounds
            periodo_id: PeriodO ID if matched
            confidence: Confidence score
        
        Returns:
            Proposal dict
        """
        period_id = f"period_{qid.lower()}"
        
        proposal = {
            'entity_type': 'Period',
            'entity_id': period_id,
            'properties': {
                'period_id': period_id,
                'label': label,
                'qid': qid,
                'periodo_id': periodo_id,
                'start_year': start_year,
                'end_year': end_year,
                'period_type': period_type,
                'status': 'pending_approval',
                'proposed_by': 'sca_python',
                'proposed_at': datetime.utcnow().isoformat(),
                'confidence': confidence
            },
            'relationships': [
                {'type': 'STARTS_IN_YEAR', 'target': f'Year:{start_year}'},
                {'type': 'ENDS_IN_YEAR', 'target': f'Year:{end_year}'}
            ]
        }
        
        return proposal
    
    def check_pending_approvals(self) -> List[Dict]:
        """
        Query Neo4j for items awaiting approval
        
        Returns:
            List of pending items
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (item)
                WHERE item.status = 'pending_approval'
                  AND (item:SubjectConcept OR item:Period OR item:Place OR item:Event)
                RETURN item
                LIMIT 500
            """)
            
            return [dict(record['item']) for record in result]
    
    def load_proposal_to_neo4j(self, proposal: Dict):
        """
        Load an approved proposal to Neo4j
        
        Args:
            proposal: Proposal dict from create_period_proposal or similar
        """
        with self.driver.session() as session:
            # Create node
            entity_type = proposal['entity_type']
            properties = proposal['properties']
            
            # Build Cypher
            props_str = ', '.join([f"{k}: ${k}" for k in properties.keys()])
            
            query = f"""
            CREATE (n:{entity_type} {{{props_str}}})
            RETURN n
            """
            
            result = session.run(query, **properties)
            created = result.single()['n']
            
            print(f"Created {entity_type}: {properties.get('label', properties.get('entity_id'))}")
            
            # Create relationships if specified
            for rel in proposal.get('relationships', []):
                # Parse target (e.g., "Year:1453")
                target_label, target_value = rel['target'].split(':')
                
                rel_query = f"""
                MATCH (source:{entity_type} {{entity_id: $entity_id}})
                MATCH (target:{target_label} {{year: $target_value}})
                CREATE (source)-[:{rel['type']}]->(target)
                """
                
                try:
                    session.run(rel_query, 
                               entity_id=properties['entity_id'],
                               target_value=int(target_value))
                except:
                    pass  # Target might not exist yet
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()


# Example usage
if __name__ == "__main__":
    # Initialize
    agent = SCAAgent(
        neo4j_uri="neo4j+s://f7b612a3.databases.neo4j.io",
        neo4j_user="neo4j",
        neo4j_password="K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"
    )
    
    print("SCA Agent initialized and bootstrapped from Chrystallum!")
    print()
    print("Agent can now:")
    print("  - Query Wikidata for backlinks")
    print("  - Use Perplexity for classification")
    print("  - Create proposals")
    print("  - Load approved items to Neo4j")
    print()
    
    # Check pending approvals
    pending = agent.check_pending_approvals()
    print(f"Pending approvals: {len(pending)}")
    
    agent.close()

