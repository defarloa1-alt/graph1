#!/usr/bin/env python3
"""
INTEGRATION: Load Trained Ontologies into Neo4j
================================================

After agent training pipeline generates ontology JSON files,
this script loads them into Neo4j for use by Phase 2A+2B agents.

Workflow:
1. Agent training generates: ontologies/Q17167_ontology.json
2. This script loads it into Neo4j
3. Phase 2A+2B agents query these ontologies

Example Neo4j Structure:
  
  SubjectConcept(Roman Republic)
    ├─ subject_id: subj_37decd8454b1
    ├─ qid: Q17167
    └─ HAS_TRAINED_AGENT → FacetAgent(Economic)
                             ├─ facet: "Economic"
                             ├─ domain_ontology: <JSON array>
                             └─ trained_date: 2026-02-15
"""

import json
from typing import Dict, List, Optional
from neo4j import GraphDatabase
import hashlib


class TrainedOntologyLoader:
    """Load trained agent ontologies into Neo4j"""
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j connection string (e.g., "neo4j://localhost:7687")
            user: Neo4j username
            password: Neo4j password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
    
    # ========================================================================
    # Load Ontology into Neo4j
    # ========================================================================
    
    def load_ontology_to_neo4j(self, ontology_json: Dict, force_update: bool = False) -> bool:
        """
        Load trained ontology into Neo4j.
        
        Creates/updates:
        1. SubjectConcept node (if doesn't exist)
        2. FacetAgent nodes (one per facet in ontology)
        3. HAS_TRAINED_AGENT relationships
        4. FACET_SUB_CONCEPT relationships
        
        Args:
            ontology_json: Parsed ontology JSON from training pipeline
            force_update: Overwrite existing ontologies if True
            
        Returns: True if successful
        """
        try:
            qid = ontology_json["qid"]
            subject_concept_id = ontology_json["subject_concept_id"]
            
            print(f"\n[Neo4j] Loading ontology for {qid} ({subject_concept_id})...")
            
            # Step 1: Find or create MainSubjectConcept
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (root:SubjectConcept { subject_id: $subject_concept_id })
                    RETURN root.subject_id as id
                """, subject_concept_id=subject_concept_id)
                
                existing = result.single()
                if not existing:
                    print(f"  ✗ SubjectConcept not found: {subject_concept_id}")
                    print(f"  → Create it first via create_subject_concept_schema.py")
                    return False
                
                print(f"  ✓ Found SubjectConcept: {subject_concept_id}")
            
            # Step 2: Group sub-concepts by facet
            facets_dict = {}
            for concept in ontology_json["typical_sub_concepts"]:
                facet = concept["facet"]
                if facet not in facets_dict:
                    facets_dict[facet] = []
                facets_dict[facet].append(concept)
            
            print(f"  ✓ Organized sub-concepts by {len(facets_dict)} facets")
            
            # Step 3: Create FacetAgent for each facet
            for facet, concepts in facets_dict.items():
                self._create_facet_agent(
                    subject_concept_id=subject_concept_id,
                    facet=facet,
                    concepts=concepts,
                    ontology_meta=ontology_json
                )
            
            print(f"  ✓ Loaded {len(facets_dict)} FacetAgents")
            print(f"  ✓ Ontology loaded successfully")
            
            return True
        
        except Exception as e:
            print(f"  ✗ Error loading ontology: {e}")
            return False
    
    def _create_facet_agent(self, subject_concept_id: str, facet: str, 
                            concepts: List[Dict], ontology_meta: Dict) -> str:
        """
        Create FacetAgent node for specific facet.
        
        Structure:
          FacetAgent {
            facet_agent_id: "agent_<hash>"
            facet: "Economic"
            civilization_subject_id: "subj_37decd8454b1"
            domain_ontology: [sub-concepts]
            trained_date: 2026-02-15
            source: "Wikipedia-bootstrapped"
          }
        """
        try:
            # Generate unique agent ID
            agent_id_composite = f"{subject_concept_id}|{facet}"
            agent_id_hash = hashlib.sha256(agent_id_composite.encode()).hexdigest()[:12]
            facet_agent_id = f"agent_{agent_id_hash}"
            
            # Prepare domain ontology for this facet
            facet_ontology = {
                "facet": facet,
                "subject_concept_id": subject_concept_id,
                "wikipedia_title": ontology_meta.get("wikipedia_title", ""),
                "typical_sub_concepts": concepts
            }
            
            with self.driver.session() as session:
                # Create or update FacetAgent
                session.run("""
                    MATCH (root:SubjectConcept { subject_id: $subject_concept_id })
                    
                    MERGE (agent:FacetAgent {
                        facet_agent_id: $facet_agent_id,
                        facet: $facet
                    })
                    SET agent.civilization_subject_id = $subject_concept_id
                    SET agent.domain_ontology = $ontology
                    SET agent.sub_concept_count = $concept_count
                    SET agent.trained_date = datetime.now()
                    SET agent.source = "Wikipedia-bootstrapped"
                    SET agent.qid = $qid
                    
                    MERGE (root)-[:HAS_TRAINED_AGENT]->(agent)
                    
                    RETURN agent.facet_agent_id as id
                """,
                facet_agent_id=facet_agent_id,
                facet=facet,
                subject_concept_id=subject_concept_id,
                ontology=json.dumps(facet_ontology),
                concept_count=len(concepts),
                qid=ontology_meta.get("qid", "")
                )
                
                print(f"    ✓ Created FacetAgent: {facet} ({facet_agent_id})")
                print(f"      Sub-concepts: {len(concepts)}")
                
                return facet_agent_id
        
        except Exception as e:
            print(f"    ✗ Error creating FacetAgent for {facet}: {e}")
            return ""
    
    # ========================================================================
    # Query Trained Ontologies
    # ========================================================================
    
    def get_agent_ontology(self, subject_concept_id: str, facet: str) -> Optional[Dict]:
        """
        Retrieve trained ontology for agent (used by Phase 2A+2B).
        
        Returns: Domain ontology JSON ready for pattern matching
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (root:SubjectConcept { subject_id: $subject_concept_id })
                    -[:HAS_TRAINED_AGENT]-> 
                    (agent:FacetAgent { facet: $facet })
                    
                    RETURN 
                        agent.domain_ontology as ontology,
                        agent.trained_date as trained_date,
                        agent.sub_concept_count as count
                """,
                subject_concept_id=subject_concept_id,
                facet=facet
                )
                
                record = result.single()
                if record:
                    return json.loads(record["ontology"])
                else:
                    return None
        
        except Exception as e:
            print(f"Error retrieving ontology: {e}")
            return None
    
    def list_trained_agents(self, subject_concept_id: str) -> List[Dict]:
        """
        List all trained agents for a subject concept.
        
        Returns: [{ facet, sub_concept_count, trained_date }, ...]
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (root:SubjectConcept { subject_id: $subject_concept_id })
                    -[:HAS_TRAINED_AGENT]-> 
                    (agent:FacetAgent)
                    
                    RETURN 
                        agent.facet as facet,
                        agent.sub_concept_count as count,
                        agent.trained_date as trained_date
                    ORDER BY agent.facet
                """,
                subject_concept_id=subject_concept_id
                )
                
                agents = []
                for record in result:
                    agents.append({
                        "facet": record["facet"],
                        "sub_concept_count": record["count"],
                        "trained_date": record["trained_date"]
                    })
                
                return agents
        
        except Exception as e:
            print(f"Error listing agents: {e}")
            return []


# ============================================================================
# Example Usage
# ============================================================================

def example_load_and_use():
    """Example: Load ontology and use for agent initialization"""
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  EXAMPLE: Load Trained Ontology into Neo4j                   ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Read ontology JSON from training pipeline
    print("\nStep 1: Load ontology from training pipeline output")
    print("-" * 60)
    
    with open("ontologies/Q17167_ontology.json", "r") as f:
        ontology = json.load(f)
    
    print(f"✓ Loaded ontology for {ontology['qid']}")
    print(f"  Subject Concept ID: {ontology['subject_concept_id']}")
    print(f"  Facets: {list(ontology['facets'].keys())}")
    print(f"  Total sub-concepts: {len(ontology['typical_sub_concepts'])}")
    
    # Step 2: Connect to Neo4j
    print("\nStep 2: Connect to Neo4j")
    print("-" * 60)
    
    try:
        loader = TrainedOntologyLoader(
            uri="neo4j://localhost:7687",
            user="neo4j",
            password="Chrystallum"
        )
        print("✓ Connected to Neo4j")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return
    
    # Step 3: Load ontology
    print("\nStep 3: Load ontology into Neo4j")
    print("-" * 60)
    
    success = loader.load_ontology_to_neo4j(ontology)
    
    if success:
        # Step 4: Verify - query what we just loaded
        print("\nStep 4: Verify - Query loaded agents")
        print("-" * 60)
        
        agents = loader.list_trained_agents(ontology["subject_concept_id"])
        
        print(f"\nTrained Agents for {ontology['subject_concept_id']}:\n")
        
        for agent in agents:
            print(f"  • {agent['facet']}")
            print(f"    Sub-concepts: {agent['sub_concept_count']}")
            print(f"    Trained: {agent['trained_date']}")
        
        # Step 5: Show how agent would use it
        print("\nStep 5: Agent Usage Example")
        print("-" * 60)
        
        economic_ontology = loader.get_agent_ontology(
            subject_concept_id=ontology["subject_concept_id"],
            facet="Economic"
        )
        
        if economic_ontology:
            print(f"\nEconomicAgent for {ontology['wikipedia_title']}:")
            print(f"  Recognized Sub-Concepts:")
            
            for concept in economic_ontology["typical_sub_concepts"]:
                print(f"\n    • {concept['label']}")
                print(f"      Evidence Patterns: {concept['evidence_patterns']}")
                print(f"      Confidence: {concept['confidence_baseline']}")
                print(f"      Wikipedia Section: {concept['section_title']}")
    
    loader.close()
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  NEXT: Use trained ontology in Phase 2A+2B GPT prompt        ║
    ║                                                               ║
    ║  GPT prompt gets injected with:                             ║
    ║  - Trained agent facet + sub-concepts                       ║
    ║  - Evidence patterns for matching                           ║
    ║  - Confidence baselines from Wikipedia                      ║
    ║  - Instructions for proposing sub-concepts                 ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    # Dry-run example (without actual Neo4j connection)
    print("""
    This script loads trained ontologies into Neo4j.
    
    Usage:
    ------
    loader = TrainedOntologyLoader(uri, user, password)
    
    # Load ontology
    with open("ontologies/Q17167_ontology.json", "r") as f:
        ontology = json.load(f)
    loader.load_ontology_to_neo4j(ontology)
    
    # Query agent
    agent_ontology = loader.get_agent_ontology("subj_37decd8454b1", "Economic")
    
    # List all trained agents
    agents = loader.list_trained_agents("subj_37decd8454b1")
    
    Expected Neo4j Result:
    ─────────────────────
    
    SubjectConcept(Roman Republic)
      ├─ subject_id: "subj_37decd8454b1"
      └─ HAS_TRAINED_AGENT → FacetAgent(Economic)
                              ├─ facet: "Economic"
                              ├─ sub_concept_count: 3
                              ├─ trained_date: 2026-02-15T12:34:56.000Z
                              └─ domain_ontology: [
                                   {
                                     "label": "Roman Republic--Economy",
                                     "evidence_patterns": ["economy"],
                                     "confidence_baseline": 0.82,
                                     "section_title": "Economy"
                                   },
                                   ...
                                 ]
    
    Then Phase 2A+2B queries this for pattern-matching and proposal guidance.
    """)
