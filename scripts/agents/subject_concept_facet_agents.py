#!/usr/bin/env python3
"""
Subject Concept Facet Agents - 18 Specialized Agents for Subject Analysis

Each facet agent analyzes SubjectConcepts from its specialized perspective:
- ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, COMMUNICATION
- CULTURAL, DEMOGRAPHIC, DIPLOMATIC, ECONOMIC
- ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC
- MILITARY, POLITICAL, RELIGIOUS, SCIENTIFIC
- SOCIAL, TECHNOLOGICAL

Architecture:
- On-demand agent creation (not all 1,422 upfront)
- Stateless operation (bootstrap from Chrystallum)
- Perplexity API for reasoning
- Wikidata SPARQL for enrichment
- Neo4j for persistence
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from neo4j import GraphDatabase
import requests


# ============================================================================
# CANONICAL FACETS (from bootstrap_packet/facets.json)
# ============================================================================

CANONICAL_FACETS = [
    "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION",
    "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC",
    "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC",
    "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC",
    "SOCIAL", "TECHNOLOGICAL"
]

FORBIDDEN_FACETS = ["TEMPORAL", "CLASSIFICATION", "PATRONAGE", "GENEALOGICAL"]


# ============================================================================
# BASE SUBJECT CONCEPT FACET AGENT
# ============================================================================

class SubjectConceptFacetAgent:
    """Base class for facet-specific subject concept agents"""
    
    def __init__(self,
                 facet_key: str,
                 facet_label: str,
                 neo4j_driver,
                 perplexity_api_key: Optional[str] = None):
        """
        Initialize a facet-specific agent
        
        Args:
            facet_key: Facet key (UPPERCASE, e.g., "MILITARY")
            facet_label: Facet label (e.g., "Military")
            neo4j_driver: Neo4j driver instance
            perplexity_api_key: Perplexity API key
        """
        # Validate facet
        if facet_key not in CANONICAL_FACETS:
            raise ValueError(f"Invalid facet: {facet_key}. Must be one of {CANONICAL_FACETS}")
        if facet_key in FORBIDDEN_FACETS:
            raise ValueError(f"Forbidden facet: {facet_key}")
        
        self.facet_key = facet_key
        self.facet_label = facet_label
        self.driver = neo4j_driver
        
        # Perplexity API
        self.perplexity_api_key = perplexity_api_key or os.getenv('PERPLEXITY_API_KEY')
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        
        # Agent ID
        self.agent_id = f"SFA_{facet_key}"
        
        # System context (loaded on demand)
        self.federations = []
        self.entity_types = []
    
    def bootstrap_context(self):
        """Load system context from Chrystallum"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (sys:Chrystallum)
                OPTIONAL MATCH (sys)-[:HAS_FEDERATION_ROOT]->(fed_root)-[:HAS_FEDERATION]->(fed)
                OPTIONAL MATCH (sys)-[:HAS_ENTITY_ROOT]->(entity_root)-[:HAS_ENTITY_TYPE]->(et)
                RETURN 
                  collect(DISTINCT fed) AS federations,
                  collect(DISTINCT et) AS entity_types
            """)
            
            data = result.single()
            self.federations = [dict(f) for f in data['federations']]
            self.entity_types = [dict(et) for et in data['entity_types']]
    
    def analyze_subject_concept(self, subject_concept_id: str) -> Dict:
        """
        Analyze a SubjectConcept from this facet's perspective
        
        Args:
            subject_concept_id: Subject concept ID
        
        Returns:
            Analysis dict with facet-specific insights
        """
        # Get subject concept from Neo4j
        with self.driver.session() as session:
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: $subject_id})
                RETURN sc
            """, subject_id=subject_concept_id)
            
            record = result.single()
            if not record:
                raise ValueError(f"SubjectConcept {subject_concept_id} not found")
            
            sc = dict(record['sc'])
        
        # Prepare facet-specific analysis prompt
        prompt = self._build_analysis_prompt(sc)
        
        # Query Perplexity
        analysis = self._query_perplexity(prompt)
        
        return {
            'subject_concept_id': subject_concept_id,
            'facet': self.facet_key,
            'agent_id': self.agent_id,
            'analysis': analysis,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _build_analysis_prompt(self, subject_concept: Dict) -> str:
        """Build facet-specific analysis prompt (override in subclasses)"""
        label = subject_concept.get('label', 'Unknown')
        qid = subject_concept.get('qid', 'Unknown')
        
        return f"""
        Analyze this subject concept from a {self.facet_label} perspective:
        
        Subject: {label} (Wikidata {qid})
        
        Questions:
        1. What are the key {self.facet_label.lower()} aspects of this subject?
        2. What related {self.facet_label.lower()} topics should be explored?
        3. What entities (people, events, places) are relevant from a {self.facet_label.lower()} viewpoint?
        4. What time periods are significant for {self.facet_label.lower()} analysis?
        5. Confidence in this facet being relevant (0-1)?
        
        Provide structured, scholarly analysis with sources.
        """
    
    def _query_perplexity(self, prompt: str, model: str = "llama-3.1-sonar-large-128k-online") -> Dict:
        """Query Perplexity API"""
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
                    "content": f"You are a specialized {self.facet_label} historian analyzing historical subjects. Provide scholarly analysis with citations."
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
    
    def discover_related_entities(self, subject_concept_id: str, entity_type: str = "Human") -> List[Dict]:
        """
        Discover entities related to this subject concept from facet perspective
        
        Args:
            subject_concept_id: Subject concept ID
            entity_type: Entity type to discover (Human, Event, etc.)
        
        Returns:
            List of candidate entities
        """
        # Query Wikidata for entities
        sparql = self._build_wikidata_discovery_query(subject_concept_id, entity_type)
        results = self._query_wikidata_sparql(sparql)
        
        candidates = []
        for binding in results:
            item_qid = binding['item']['value'].split('/')[-1]
            candidates.append({
                'qid': item_qid,
                'label': binding.get('itemLabel', {}).get('value', ''),
                'description': binding.get('description', {}).get('value', ''),
                'facet': self.facet_key,
                'entity_type': entity_type
            })
        
        return candidates
    
    def _build_wikidata_discovery_query(self, subject_concept_id: str, entity_type: str) -> str:
        """Build Wikidata SPARQL query (override in subclasses for facet-specific queries)"""
        # Generic query - subclasses should override with facet-specific properties
        return f"""
        SELECT DISTINCT ?item ?itemLabel ?description
        WHERE {{
          ?item wdt:P31 wd:Q5 .  # instance of human
          ?item rdfs:label ?itemLabel .
          OPTIONAL {{ ?item schema:description ?description }}
          FILTER(LANG(?itemLabel) = "en")
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 100
        """
    
    def _query_wikidata_sparql(self, sparql_query: str) -> List[Dict]:
        """Query Wikidata SPARQL endpoint"""
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
    
    def create_entity_proposal(self,
                              entity_type: str,
                              qid: str,
                              label: str,
                              properties: Dict,
                              confidence: float = 0.8) -> Dict:
        """
        Create entity proposal for this subject concept
        
        Args:
            entity_type: Entity type (Human, Event, etc.)
            qid: Wikidata QID
            label: Entity label
            properties: Additional properties
            confidence: Confidence score
        
        Returns:
            Proposal dict
        """
        entity_id = f"{entity_type.lower()}_{qid.lower()}"
        
        proposal = {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'properties': {
                'entity_id': entity_id,
                'label': label,
                'qid': qid,
                **properties,
                'discovered_by_facet': self.facet_key,
                'discovered_by_agent': self.agent_id,
                'status': 'pending_approval',
                'proposed_at': datetime.utcnow().isoformat(),
                'confidence': confidence
            }
        }
        
        return proposal


# ============================================================================
# SPECIALIZED FACET AGENTS (Examples)
# ============================================================================

class MilitaryFacetAgent(SubjectConceptFacetAgent):
    """Military facet agent - analyzes warfare, battles, strategy"""
    
    def _build_analysis_prompt(self, subject_concept: Dict) -> str:
        label = subject_concept.get('label', 'Unknown')
        qid = subject_concept.get('qid', 'Unknown')
        
        return f"""
        Analyze this subject from a MILITARY perspective:
        
        Subject: {label} (Wikidata {qid})
        
        Questions:
        1. What military conflicts, battles, or campaigns are associated?
        2. What military leaders, commanders, or generals are relevant?
        3. What military technologies, tactics, or strategies were employed?
        4. What military institutions or organizations existed?
        5. What was the military significance of this subject in its historical context?
        6. Confidence that this subject has significant military aspects (0-1)?
        
        Provide detailed military analysis with scholarly sources.
        """
    
    def _build_wikidata_discovery_query(self, subject_concept_id: str, entity_type: str) -> str:
        # Military-specific Wikidata properties
        if entity_type == "Human":
            return """
            SELECT DISTINCT ?item ?itemLabel ?description
            WHERE {
              {?item wdt:P106 wd:Q4991371 .}  # occupation: military commander
              UNION
              {?item wdt:P106 wd:Q189290 .}   # occupation: military officer
              UNION
              {?item wdt:P31 wd:Q5 ; wdt:P241 ?military_unit .}  # served in military
              OPTIONAL { ?item schema:description ?description }
              SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }
            LIMIT 100
            """
        elif entity_type == "Event":
            return """
            SELECT DISTINCT ?item ?itemLabel ?description
            WHERE {
              {?item wdt:P31 wd:Q178561 .}  # instance of: battle
              UNION
              {?item wdt:P31 wd:Q198 .}     # instance of: war
              UNION
              {?item wdt:P31 wd:Q2001676 .} # instance of: military operation
              OPTIONAL { ?item schema:description ?description }
              SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }
            LIMIT 100
            """
        else:
            return super()._build_wikidata_discovery_query(subject_concept_id, entity_type)


class PoliticalFacetAgent(SubjectConceptFacetAgent):
    """Political facet agent - analyzes governance, rulers, states"""
    
    def _build_analysis_prompt(self, subject_concept: Dict) -> str:
        label = subject_concept.get('label', 'Unknown')
        qid = subject_concept.get('qid', 'Unknown')
        
        return f"""
        Analyze this subject from a POLITICAL perspective:
        
        Subject: {label} (Wikidata {qid})
        
        Questions:
        1. What political entities (states, empires, polities) are involved?
        2. What political leaders, rulers, or statesmen are relevant?
        3. What forms of government or political systems existed?
        4. What political events (elections, coups, reforms) occurred?
        5. What was the political significance of this subject?
        6. Confidence that this subject has significant political aspects (0-1)?
        
        Provide detailed political analysis with scholarly sources.
        """
    
    def _build_wikidata_discovery_query(self, subject_concept_id: str, entity_type: str) -> str:
        if entity_type == "Human":
            return """
            SELECT DISTINCT ?item ?itemLabel ?description
            WHERE {
              {?item wdt:P106 wd:Q82955 .}    # occupation: politician
              UNION
              {?item wdt:P106 wd:Q14212 .}    # occupation: head of state
              UNION
              {?item wdt:P39 ?position . ?position wdt:P279* wd:Q4164871 .}  # political office
              OPTIONAL { ?item schema:description ?description }
              SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }
            LIMIT 100
            """
        else:
            return super()._build_wikidata_discovery_query(subject_concept_id, entity_type)


class EconomicFacetAgent(SubjectConceptFacetAgent):
    """Economic facet agent - analyzes trade, currency, economic systems"""
    
    def _build_analysis_prompt(self, subject_concept: Dict) -> str:
        label = subject_concept.get('label', 'Unknown')
        qid = subject_concept.get('qid', 'Unknown')
        
        return f"""
        Analyze this subject from an ECONOMIC perspective:
        
        Subject: {label} (Wikidata {qid})
        
        Questions:
        1. What economic systems, trade networks, or markets existed?
        2. What currencies, commodities, or trade goods were important?
        3. What economic policies, reforms, or crises occurred?
        4. What economic institutions or merchant organizations were active?
        5. What was the economic impact of this subject?
        6. Confidence that this subject has significant economic aspects (0-1)?
        
        Provide detailed economic analysis with scholarly sources.
        """


# ============================================================================
# FACET AGENT FACTORY
# ============================================================================

class SubjectConceptAgentFactory:
    """Factory for creating facet-specific subject concept agents"""
    
    # Mapping of facet keys to specialized agent classes
    SPECIALIZED_AGENTS = {
        'MILITARY': MilitaryFacetAgent,
        'POLITICAL': PoliticalFacetAgent,
        'ECONOMIC': EconomicFacetAgent,
        # Add more specialized agents as needed
    }
    
    @classmethod
    def create_agent(cls,
                    facet_key: str,
                    neo4j_driver,
                    perplexity_api_key: Optional[str] = None) -> SubjectConceptFacetAgent:
        """
        Create a facet-specific agent
        
        Args:
            facet_key: Facet key (UPPERCASE)
            neo4j_driver: Neo4j driver instance
            perplexity_api_key: Perplexity API key
        
        Returns:
            Facet agent instance
        """
        if facet_key not in CANONICAL_FACETS:
            raise ValueError(f"Invalid facet: {facet_key}")
        
        # Get specialized agent class or use base class
        agent_class = cls.SPECIALIZED_AGENTS.get(facet_key, SubjectConceptFacetAgent)
        
        # Convert facet key to label
        facet_label = facet_key.capitalize()
        
        return agent_class(
            facet_key=facet_key,
            facet_label=facet_label,
            neo4j_driver=neo4j_driver,
            perplexity_api_key=perplexity_api_key
        )
    
    @classmethod
    def create_all_agents(cls,
                         neo4j_driver,
                         perplexity_api_key: Optional[str] = None) -> Dict[str, SubjectConceptFacetAgent]:
        """
        Create all 18 facet agents
        
        Args:
            neo4j_driver: Neo4j driver instance
            perplexity_api_key: Perplexity API key
        
        Returns:
            Dict mapping facet keys to agent instances
        """
        agents = {}
        for facet_key in CANONICAL_FACETS:
            agents[facet_key] = cls.create_agent(
                facet_key=facet_key,
                neo4j_driver=neo4j_driver,
                perplexity_api_key=perplexity_api_key
            )
        
        return agents


# ============================================================================
# MULTI-FACET SUBJECT ANALYZER
# ============================================================================

class MultiFacetSubjectAnalyzer:
    """Analyze a subject concept across multiple facets"""
    
    def __init__(self, neo4j_driver, perplexity_api_key: Optional[str] = None):
        self.driver = neo4j_driver
        self.perplexity_api_key = perplexity_api_key
    
    def analyze_subject_all_facets(self, subject_concept_id: str) -> Dict:
        """
        Analyze a subject concept across all 18 facets
        
        Args:
            subject_concept_id: Subject concept ID
        
        Returns:
            Combined analysis from all facets
        """
        agents = SubjectConceptAgentFactory.create_all_agents(
            neo4j_driver=self.driver,
            perplexity_api_key=self.perplexity_api_key
        )
        
        analyses = {}
        for facet_key, agent in agents.items():
            print(f"Analyzing from {facet_key} perspective...")
            try:
                analysis = agent.analyze_subject_concept(subject_concept_id)
                analyses[facet_key] = analysis
            except Exception as e:
                print(f"  Error: {e}")
                analyses[facet_key] = {'error': str(e)}
        
        return {
            'subject_concept_id': subject_concept_id,
            'facet_analyses': analyses,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def analyze_subject_selected_facets(self,
                                       subject_concept_id: str,
                                       facet_keys: List[str]) -> Dict:
        """
        Analyze a subject concept from selected facets
        
        Args:
            subject_concept_id: Subject concept ID
            facet_keys: List of facet keys to analyze
        
        Returns:
            Combined analysis from selected facets
        """
        analyses = {}
        for facet_key in facet_keys:
            agent = SubjectConceptAgentFactory.create_agent(
                facet_key=facet_key,
                neo4j_driver=self.driver,
                perplexity_api_key=self.perplexity_api_key
            )
            
            print(f"Analyzing from {facet_key} perspective...")
            try:
                analysis = agent.analyze_subject_concept(subject_concept_id)
                analyses[facet_key] = analysis
            except Exception as e:
                print(f"  Error: {e}")
                analyses[facet_key] = {'error': str(e)}
        
        return {
            'subject_concept_id': subject_concept_id,
            'facet_analyses': analyses,
            'timestamp': datetime.utcnow().isoformat()
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, PERPLEXITY_API_KEY
    
    # Initialize Neo4j driver
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )
    
    print("=" * 80)
    print("SUBJECT CONCEPT FACET AGENTS - Example Usage")
    print("=" * 80)
    print()
    
    # Create a single facet agent
    print("Creating MILITARY facet agent...")
    military_agent = SubjectConceptAgentFactory.create_agent(
        facet_key="MILITARY",
        neo4j_driver=driver,
        perplexity_api_key=PERPLEXITY_API_KEY
    )
    print(f"  Agent ID: {military_agent.agent_id}")
    print()
    
    # Create all 18 facet agents
    print("Creating all 18 facet agents...")
    all_agents = SubjectConceptAgentFactory.create_all_agents(
        neo4j_driver=driver,
        perplexity_api_key=PERPLEXITY_API_KEY
    )
    print(f"  Created {len(all_agents)} agents:")
    for facet_key in CANONICAL_FACETS:
        print(f"    - {facet_key}: {all_agents[facet_key].agent_id}")
    print()
    
    # Multi-facet analyzer
    print("Creating multi-facet analyzer...")
    analyzer = MultiFacetSubjectAnalyzer(
        neo4j_driver=driver,
        perplexity_api_key=PERPLEXITY_API_KEY
    )
    print("  Analyzer ready for cross-facet analysis")
    print()
    
    driver.close()
    print("✓ Demo complete")
