#!/usr/bin/env python3
"""
Subject Concept Agents - Comprehensive Test Script

Tests and demonstrates:
1. Agent creation (single and all 18 facets)
2. Subject concept analysis
3. Multi-facet analysis
4. Entity discovery
5. Workflow execution
6. Proposal generation
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from neo4j import GraphDatabase

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import configuration
try:
    from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, PERPLEXITY_API_KEY
except ImportError:
    print("ERROR: config.py not found. Please create it with your credentials.")
    print("See config.py.example for template.")
    sys.exit(1)

# Import agent modules
from scripts.agents.subject_concept_facet_agents import (
    SubjectConceptAgentFactory,
    MultiFacetSubjectAnalyzer,
    CANONICAL_FACETS
)

from scripts.agents.subject_concept_workflow import (
    SubjectConceptDiscoveryWorkflow,
    SubjectConceptEnrichmentWorkflow
)


# ============================================================================
# TEST UTILITIES
# ============================================================================

class TestRunner:
    """Test runner with progress tracking"""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.start_time = None
    
    def start(self, test_name: str):
        """Start a test"""
        self.start_time = datetime.now()
        print("\n" + "=" * 80)
        print(f"TEST: {test_name}")
        print("=" * 80)
    
    def end(self, success: bool):
        """End a test"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            print("\n✅ PASSED")
        else:
            self.failed_tests += 1
            print("\n❌ FAILED")
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"Time: {elapsed:.2f}s")
    
    def summary(self):
        """Print summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_neo4j_connection(driver):
    """Test Neo4j connection"""
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            assert result.single()['test'] == 1
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_chrystallum_structure(driver):
    """Test Chrystallum system structure exists"""
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (sys:Chrystallum)
                OPTIONAL MATCH (sys)-[:HAS_SUBJECT_CONCEPT_ROOT]->(sc_root)
                OPTIONAL MATCH (sys)-[:HAS_FACET_ROOT]->(facet_root)
                RETURN sys, sc_root, facet_root
            """)
            
            record = result.single()
            if not record or not record['sys']:
                print("Chrystallum root node not found")
                print("Run: Cypher/bootstrap_subject_concept_agents.cypher")
                return False
            
            print(f"✓ Chrystallum root exists")
            print(f"✓ SubjectConceptRoot: {record['sc_root'] is not None}")
            print(f"✓ FacetRoot: {record['facet_root'] is not None}")
            
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_facets_exist(driver):
    """Test all 18 canonical facets exist"""
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (facet:Facet)
                RETURN collect(facet.key) AS facet_keys
            """)
            
            record = result.single()
            facet_keys = record['facet_keys'] if record else []
            
            print(f"Found {len(facet_keys)} facets in Neo4j:")
            for key in sorted(facet_keys):
                print(f"  - {key}")
            
            missing = set(CANONICAL_FACETS) - set(facet_keys)
            if missing:
                print(f"\nMissing facets: {missing}")
                print("Run: Cypher/bootstrap_subject_concept_agents.cypher")
                return False
            
            return len(facet_keys) == 18
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_subject_concepts_exist(driver):
    """Test SubjectConcepts exist"""
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (sc:SubjectConcept)
                RETURN count(sc) AS total,
                       collect(sc.subject_id)[0..5] AS sample_ids,
                       collect(sc.label)[0..5] AS sample_labels
            """)
            
            record = result.single()
            total = record['total'] if record else 0
            
            print(f"Found {total} SubjectConcepts")
            
            if total > 0:
                print("\nSample SubjectConcepts:")
                for i, (sid, label) in enumerate(zip(record['sample_ids'], record['sample_labels'])):
                    print(f"  {i+1}. {label} ({sid})")
            else:
                print("No SubjectConcepts found")
                print("Run: Cypher/bootstrap_subject_concept_agents.cypher")
            
            return total > 0
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_create_single_agent(driver):
    """Test creating a single facet agent"""
    try:
        print("Creating MILITARY facet agent...")
        
        agent = SubjectConceptAgentFactory.create_agent(
            facet_key="MILITARY",
            neo4j_driver=driver,
            perplexity_api_key=PERPLEXITY_API_KEY
        )
        
        print(f"✓ Agent created: {agent.agent_id}")
        print(f"✓ Facet: {agent.facet_key}")
        print(f"✓ Label: {agent.facet_label}")
        
        # Bootstrap context
        print("\nBootstrapping context...")
        agent.bootstrap_context()
        
        print(f"✓ Federations loaded: {len(agent.federations)}")
        print(f"✓ Entity types loaded: {len(agent.entity_types)}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_create_all_agents(driver):
    """Test creating all 18 facet agents"""
    try:
        print("Creating all 18 facet agents...")
        
        agents = SubjectConceptAgentFactory.create_all_agents(
            neo4j_driver=driver,
            perplexity_api_key=PERPLEXITY_API_KEY
        )
        
        print(f"\n✓ Created {len(agents)} agents:")
        for facet_key in sorted(agents.keys()):
            agent = agents[facet_key]
            print(f"  - {facet_key:20s} → {agent.agent_id}")
        
        return len(agents) == 18
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_analyze_subject_concept(driver):
    """Test analyzing a SubjectConcept (requires Perplexity API)"""
    
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY == "your_perplexity_key_here":
        print("SKIPPED: PERPLEXITY_API_KEY not configured")
        return True  # Don't fail if API key not set
    
    try:
        # Get a sample SubjectConcept
        with driver.session() as session:
            result = session.run("""
                MATCH (sc:SubjectConcept)
                WHERE sc.status = 'approved'
                RETURN sc.subject_id AS id, sc.label AS label
                LIMIT 1
            """)
            
            record = result.single()
            if not record:
                print("No approved SubjectConcepts found")
                return False
            
            subject_id = record['id']
            label = record['label']
        
        print(f"Analyzing: {label} ({subject_id})")
        
        # Create agent
        agent = SubjectConceptAgentFactory.create_agent(
            facet_key="MILITARY",
            neo4j_driver=driver,
            perplexity_api_key=PERPLEXITY_API_KEY
        )
        
        # Analyze
        print("\nQuerying Perplexity (this may take 10-20 seconds)...")
        analysis = agent.analyze_subject_concept(subject_id)
        
        print(f"\n✓ Analysis complete")
        print(f"  Facet: {analysis['facet']}")
        print(f"  Agent: {analysis['agent_id']}")
        print(f"\nAnalysis Preview (first 500 chars):")
        print(analysis['analysis']['content'][:500])
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_multi_facet_analyzer(driver):
    """Test multi-facet subject analyzer"""
    
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY == "your_perplexity_key_here":
        print("SKIPPED: PERPLEXITY_API_KEY not configured")
        return True
    
    try:
        # Get a sample SubjectConcept
        with driver.session() as session:
            result = session.run("""
                MATCH (sc:SubjectConcept)
                WHERE sc.status = 'approved'
                  AND size(sc.related_facets) > 0
                RETURN sc.subject_id AS id, 
                       sc.label AS label,
                       sc.primary_facet AS primary,
                       sc.related_facets AS related
                LIMIT 1
            """)
            
            record = result.single()
            if not record:
                print("No multi-facet SubjectConcepts found")
                return False
            
            subject_id = record['id']
            label = record['label']
            primary = record['primary']
            related = record['related']
        
        print(f"Analyzing: {label} ({subject_id})")
        print(f"Primary: {primary}")
        print(f"Related: {related}")
        
        # Select facets to analyze (primary + related, max 3)
        facets = [primary] + related[:2]
        
        print(f"\nAnalyzing from {len(facets)} facets: {facets}")
        
        analyzer = MultiFacetSubjectAnalyzer(
            neo4j_driver=driver,
            perplexity_api_key=PERPLEXITY_API_KEY
        )
        
        print("\nQuerying Perplexity (this may take 30-60 seconds)...")
        analysis = analyzer.analyze_subject_selected_facets(
            subject_concept_id=subject_id,
            facet_keys=facets
        )
        
        print(f"\n✓ Multi-facet analysis complete")
        for facet_key, result in analysis['facet_analyses'].items():
            if 'error' in result:
                print(f"  {facet_key}: ERROR - {result['error']}")
            else:
                print(f"  {facet_key}: {len(result['analysis']['content'])} chars")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_discovery_workflow(driver):
    """Test discovery workflow (without actually running Perplexity)"""
    try:
        print("Initializing discovery workflow...")
        
        discovery = SubjectConceptDiscoveryWorkflow(
            neo4j_driver=driver,
            perplexity_api_key=PERPLEXITY_API_KEY,
            output_dir="output/subject_proposals"
        )
        
        print(f"✓ Workflow initialized")
        print(f"  Output directory: {discovery.output_dir}")
        print(f"  Wikidata endpoint: {discovery.wikidata_endpoint}")
        
        # Test Wikidata query (without running full workflow)
        print("\nTesting Wikidata backlinks query...")
        candidates = discovery._query_wikidata_backlinks('Q17167', limit=5)
        
        print(f"✓ Found {len(candidates)} candidates from Q17167 (Roman Republic)")
        for i, c in enumerate(candidates[:3]):
            print(f"  {i+1}. {c['label']} ({c['qid']})")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_enrichment_workflow(driver):
    """Test enrichment workflow"""
    try:
        print("Initializing enrichment workflow...")
        
        enrichment = SubjectConceptEnrichmentWorkflow(
            neo4j_driver=driver
        )
        
        print(f"✓ Workflow initialized")
        print(f"  FAST index: {len(enrichment.fast_index)} entries")
        print(f"  LCC index: {len(enrichment.lcc_index)} entries")
        
        # Show sample FAST entries
        if enrichment.fast_index:
            print("\nSample FAST entries:")
            for i, (label, data) in enumerate(list(enrichment.fast_index.items())[:3]):
                print(f"  {i+1}. {label} → {data['fast_id']}")
        
        # Show sample LCC entries
        if enrichment.lcc_index:
            print("\nSample LCC entries:")
            for i, (label, data) in enumerate(list(enrichment.lcc_index.items())[:3]):
                print(f"  {i+1}. {label} → {data['code']}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    """Run all tests"""
    
    print("=" * 80)
    print("SUBJECT CONCEPT AGENTS - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Neo4j: {NEO4J_URI}")
    print(f"Perplexity API: {'Configured' if PERPLEXITY_API_KEY and PERPLEXITY_API_KEY != 'your_perplexity_key_here' else 'Not configured'}")
    print("=" * 80)
    
    # Initialize driver
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )
    
    # Initialize test runner
    runner = TestRunner()
    
    # Test 1: Neo4j Connection
    runner.start("Neo4j Connection")
    success = test_neo4j_connection(driver)
    runner.end(success)
    
    if not success:
        print("\nERROR: Cannot connect to Neo4j. Check your credentials.")
        driver.close()
        return
    
    # Test 2: Chrystallum Structure
    runner.start("Chrystallum System Structure")
    success = test_chrystallum_structure(driver)
    runner.end(success)
    
    # Test 3: Facets
    runner.start("18 Canonical Facets")
    success = test_facets_exist(driver)
    runner.end(success)
    
    # Test 4: SubjectConcepts
    runner.start("SubjectConcepts Exist")
    success = test_subject_concepts_exist(driver)
    runner.end(success)
    
    # Test 5: Create Single Agent
    runner.start("Create Single Facet Agent")
    success = test_create_single_agent(driver)
    runner.end(success)
    
    # Test 6: Create All Agents
    runner.start("Create All 18 Facet Agents")
    success = test_create_all_agents(driver)
    runner.end(success)
    
    # Test 7: Analyze SubjectConcept (requires Perplexity)
    runner.start("Analyze SubjectConcept (Perplexity)")
    success = test_analyze_subject_concept(driver)
    runner.end(success)
    
    # Test 8: Multi-Facet Analyzer (requires Perplexity)
    runner.start("Multi-Facet Analysis (Perplexity)")
    success = test_multi_facet_analyzer(driver)
    runner.end(success)
    
    # Test 9: Discovery Workflow
    runner.start("Discovery Workflow (Wikidata)")
    success = test_discovery_workflow(driver)
    runner.end(success)
    
    # Test 10: Enrichment Workflow
    runner.start("Enrichment Workflow (FAST/LCC)")
    success = test_enrichment_workflow(driver)
    runner.end(success)
    
    # Close driver
    driver.close()
    
    # Print summary
    runner.summary()
    
    # Exit code
    sys.exit(0 if runner.failed_tests == 0 else 1)


if __name__ == "__main__":
    main()
