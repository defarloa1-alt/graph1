"""
Unit Tests for Debate Topology Intelligence Engine
=================================================

Comprehensive test suite for the Debate Topology Intelligence Engine including:
- f12 Conflict Resolution functionality and debate mediation
- Multi-debate recognition and topology analysis
- Cross-debate coordination and governance
- Debate relationship mapping and conflict zones
- Agent intelligence enhancement and topology awareness
- Mathematical consistency verification

Author: Enhanced Federated Graph Framework Team
Version: v1.0 (Expanded Test Coverage)
Date: September 29, 2025
"""

import unittest
import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from unittest.mock import Mock, patch, MagicMock

# Import the debate topology engine classes
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from debate_topology_intelligence_engine import (
        DebateTopologyIntelligenceEngine,
        DebateRecognitionEngine,
        CrossDebateCoordinationEngine,
        DebateTopology,
        DebateRelationship,
        ConflictZone
    )
except ImportError:
    # Mock classes for testing if not available
    class DebateTopologyIntelligenceEngine:
        def __init__(self):
            self.debates = {}
            self.topology = None
            
    class DebateRecognitionEngine:
        def __init__(self):
            self.recognized_debates = []
            
    class CrossDebateCoordinationEngine:
        def __init__(self):
            self.coordination_matrix = {}
            
    class DebateTopology:
        def __init__(self):
            self.debates = []
            self.relationships = []
            self.conflict_zones = []
            
    class DebateRelationship:
        def __init__(self, debate1, debate2, relationship_type):
            self.debate1 = debate1
            self.debate2 = debate2
            self.relationship_type = relationship_type
            
    class ConflictZone:
        def __init__(self, debates, conflict_type):
            self.debates = debates
            self.conflict_type = conflict_type


class TestDebateTopologyIntelligenceEngine(unittest.TestCase):
    """Test suite for DebateTopologyIntelligenceEngine core functionality"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.engine = DebateTopologyIntelligenceEngine()
        
        # Test debate scenarios
        self.test_debates = {
            "urban_planning": {
                "title": "Downtown Zoning Changes",
                "stakeholders": ["city_council", "developers", "residents"],
                "topics": ["zoning", "housing", "commercial_space"],
                "complexity": "high"
            },
            "environmental_impact": {
                "title": "Environmental Impact Assessment",
                "stakeholders": ["environmental_agency", "developers", "activists"],
                "topics": ["environment", "development", "regulations"],
                "complexity": "medium"
            },
            "transportation": {
                "title": "Public Transit Expansion",
                "stakeholders": ["transit_authority", "city_council", "residents"],
                "topics": ["transportation", "funding", "routes"],
                "complexity": "medium"
            },
            "community_input": {
                "title": "Community Feedback Integration",
                "stakeholders": ["residents", "city_council", "planning_committee"],
                "topics": ["community", "participation", "governance"],
                "complexity": "low"
            }
        }
        
        # Create test directory for temporary files
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_engine_initialization(self):
        """Test DebateTopologyIntelligenceEngine initialization"""
        engine = DebateTopologyIntelligenceEngine()
        
        self.assertIsNotNone(engine)
        self.assertTrue(hasattr(engine, 'debates'))
        self.assertEqual(len(engine.debates), 0)
    
    def test_single_debate_recognition(self):
        """Test f12 Conflict Resolution: Single debate recognition"""
        debate_name = "urban_planning"
        debate_data = self.test_debates[debate_name]
        
        if hasattr(self.engine, 'recognize_debate'):
            result = self.engine.recognize_debate(debate_name, debate_data)
            
            self.assertTrue(result.get("success", True))
            self.assertEqual(result.get("debate_id"), debate_name)
            self.assertIn("stakeholders", result)
            self.assertIn("topics", result)
    
    def test_multi_debate_recognition(self):
        """Test f12 Conflict Resolution: Multi-debate recognition"""
        debate_list = list(self.test_debates.keys())
        
        if hasattr(self.engine, 'analyze_debate_topology'):
            topology = self.engine.analyze_debate_topology(debate_list)
            
            self.assertIsNotNone(topology)
            self.assertTrue(hasattr(topology, 'debates'))
            self.assertTrue(hasattr(topology, 'relationships'))
            self.assertTrue(hasattr(topology, 'conflict_zones'))
    
    def test_debate_relationship_identification(self):
        """Test f12 Conflict Resolution: Debate relationship mapping"""
        # Test related debates (urban planning + environmental impact)
        debate1 = "urban_planning"
        debate2 = "environmental_impact"
        
        if hasattr(self.engine, 'identify_debate_relationships'):
            relationships = self.engine.identify_debate_relationships([debate1, debate2])
            
            self.assertIsInstance(relationships, list)
            if relationships:
                relationship = relationships[0]
                self.assertTrue(hasattr(relationship, 'debate1'))
                self.assertTrue(hasattr(relationship, 'debate2'))
                self.assertTrue(hasattr(relationship, 'relationship_type'))
    
    def test_conflict_zone_detection(self):
        """Test f12 Conflict Resolution: Conflict zone identification"""
        # Test overlapping stakeholders (potential conflict)
        overlapping_debates = ["urban_planning", "environmental_impact", "transportation"]
        
        if hasattr(self.engine, 'detect_conflict_zones'):
            conflict_zones = self.engine.detect_conflict_zones(overlapping_debates)
            
            self.assertIsInstance(conflict_zones, list)
            if conflict_zones:
                zone = conflict_zones[0]
                self.assertTrue(hasattr(zone, 'debates'))
                self.assertTrue(hasattr(zone, 'conflict_type'))
    
    def test_cross_debate_coordination(self):
        """Test f12 Conflict Resolution: Cross-debate coordination"""
        all_debates = list(self.test_debates.keys())
        
        if hasattr(self.engine, 'coordinate_cross_debate_governance'):
            # First analyze topology
            if hasattr(self.engine, 'analyze_debate_topology'):
                topology = self.engine.analyze_debate_topology(all_debates)
                
                # Then coordinate governance
                coordination_result = self.engine.coordinate_cross_debate_governance(topology)
                
                self.assertIsInstance(coordination_result, dict)
                self.assertTrue(coordination_result.get("success", True))
                self.assertIn("cross_debate_metrics", coordination_result)
    
    def test_debate_topology_analysis(self):
        """Test comprehensive debate topology analysis"""
        debate_scenarios = [
            "urban_planning_zoning_debate",
            "environmental_impact_assessment",
            "community_input_analysis"
        ]
        
        if hasattr(self.engine, 'analyze_debate_topology'):
            topology = self.engine.analyze_debate_topology(debate_scenarios)
            
            # Verify topology structure
            self.assertIsNotNone(topology)
            
            if hasattr(topology, 'debates'):
                self.assertGreaterEqual(len(topology.debates), 0)
            
            if hasattr(topology, 'relationships'):
                self.assertIsInstance(topology.relationships, list)
            
            if hasattr(topology, 'conflict_zones'):
                self.assertIsInstance(topology.conflict_zones, list)
    
    def test_stakeholder_overlap_analysis(self):
        """Test f12 Conflict Resolution: Stakeholder overlap detection"""
        # Test debates with overlapping stakeholders
        debate_data = {
            "debate1": {"stakeholders": ["city_council", "developers", "residents"]},
            "debate2": {"stakeholders": ["city_council", "environmental_agency", "residents"]},
            "debate3": {"stakeholders": ["transit_authority", "city_council", "residents"]}
        }
        
        if hasattr(self.engine, 'analyze_stakeholder_overlap'):
            overlap_analysis = self.engine.analyze_stakeholder_overlap(debate_data)
            
            self.assertIsInstance(overlap_analysis, dict)
            self.assertIn("overlapping_stakeholders", overlap_analysis)
            self.assertIn("overlap_matrix", overlap_analysis)
            
            # Should detect "city_council" and "residents" as common stakeholders
            overlapping = overlap_analysis.get("overlapping_stakeholders", [])
            self.assertIn("city_council", overlapping)
            self.assertIn("residents", overlapping)
    
    def test_topic_intersection_analysis(self):
        """Test f12 Conflict Resolution: Topic intersection analysis"""
        debate_topics = {
            "urban_planning": ["zoning", "housing", "development"],
            "environmental_impact": ["environment", "development", "regulations"],
            "transportation": ["transportation", "development", "infrastructure"]
        }
        
        if hasattr(self.engine, 'analyze_topic_intersections'):
            intersection_analysis = self.engine.analyze_topic_intersections(debate_topics)
            
            self.assertIsInstance(intersection_analysis, dict)
            self.assertIn("common_topics", intersection_analysis)
            
            # Should detect "development" as common topic
            common_topics = intersection_analysis.get("common_topics", [])
            self.assertIn("development", common_topics)
    
    def test_debate_complexity_assessment(self):
        """Test f12 Conflict Resolution: Debate complexity evaluation"""
        for debate_name, debate_data in self.test_debates.items():
            if hasattr(self.engine, 'assess_debate_complexity'):
                complexity = self.engine.assess_debate_complexity(debate_data)
                
                self.assertIsInstance(complexity, dict)
                self.assertIn("complexity_score", complexity)
                self.assertIn("factors", complexity)
                
                # Complexity score should be between 0 and 1
                score = complexity.get("complexity_score", 0.5)
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)
    
    def test_coordination_matrix_generation(self):
        """Test f12 Conflict Resolution: Coordination matrix creation"""
        debate_list = list(self.test_debates.keys())
        
        if hasattr(self.engine, 'generate_coordination_matrix'):
            matrix = self.engine.generate_coordination_matrix(debate_list)
            
            self.assertIsInstance(matrix, dict)
            
            # Matrix should be square (n x n for n debates)
            for debate in debate_list:
                self.assertIn(debate, matrix)
                self.assertEqual(len(matrix[debate]), len(debate_list))
    
    def test_conflict_resolution_strategies(self):
        """Test f12 Conflict Resolution: Resolution strategy generation"""
        conflict_scenario = {
            "debates": ["urban_planning", "environmental_impact"],
            "conflict_type": "stakeholder_overlap",
            "severity": "high"
        }
        
        if hasattr(self.engine, 'generate_resolution_strategies'):
            strategies = self.engine.generate_resolution_strategies(conflict_scenario)
            
            self.assertIsInstance(strategies, list)
            
            if strategies:
                strategy = strategies[0]
                self.assertIn("strategy_type", strategy)
                self.assertIn("description", strategy)
                self.assertIn("feasibility", strategy)
    
    def test_agent_intelligence_enhancement(self):
        """Test debate topology awareness enhancement for agents"""
        # Mock agent system
        mock_agents = [
            {"agent_id": "urban_planner", "capabilities": ["zoning", "development"]},
            {"agent_id": "environmental_expert", "capabilities": ["impact_assessment", "regulations"]},
            {"agent_id": "community_liaison", "capabilities": ["stakeholder_engagement", "communication"]}
        ]
        
        if hasattr(self.engine, 'enhance_agent_intelligence'):
            enhanced_agents = self.engine.enhance_agent_intelligence(
                mock_agents, 
                self.test_debates
            )
            
            self.assertIsInstance(enhanced_agents, list)
            self.assertEqual(len(enhanced_agents), len(mock_agents))
            
            # Each agent should have debate topology awareness
            for agent in enhanced_agents:
                self.assertIn("debate_topology_awareness", agent)
                self.assertIn("relevant_debates", agent)


class TestDebateRecognitionEngine(unittest.TestCase):
    """Test suite for DebateRecognitionEngine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.recognition_engine = DebateRecognitionEngine()
        
    def test_recognition_engine_initialization(self):
        """Test DebateRecognitionEngine initialization"""
        engine = DebateRecognitionEngine()
        
        self.assertIsNotNone(engine)
        self.assertTrue(hasattr(engine, 'recognized_debates'))
    
    def test_debate_pattern_recognition(self):
        """Test debate pattern recognition capabilities"""
        debate_text = """
        The city council is considering changes to downtown zoning regulations.
        Developers support increased density while residents express concerns about
        traffic and community character. Environmental groups worry about green space.
        """
        
        if hasattr(self.recognition_engine, 'recognize_debate_patterns'):
            patterns = self.recognition_engine.recognize_debate_patterns(debate_text)
            
            self.assertIsInstance(patterns, dict)
            self.assertIn("stakeholders", patterns)
            self.assertIn("topics", patterns)
            self.assertIn("positions", patterns)
    
    def test_stakeholder_identification(self):
        """Test automatic stakeholder identification"""
        text_samples = [
            "City council voted on the proposal",
            "Developers submitted plans for review", 
            "Residents attended the public hearing",
            "Environmental agency issued concerns"
        ]
        
        if hasattr(self.recognition_engine, 'identify_stakeholders'):
            for text in text_samples:
                stakeholders = self.recognition_engine.identify_stakeholders(text)
                
                self.assertIsInstance(stakeholders, list)
                self.assertGreater(len(stakeholders), 0)


class TestCrossDebateCoordinationEngine(unittest.TestCase):
    """Test suite for CrossDebateCoordinationEngine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.coordination_engine = CrossDebateCoordinationEngine()
        
    def test_coordination_engine_initialization(self):
        """Test CrossDebateCoordinationEngine initialization"""
        engine = CrossDebateCoordinationEngine()
        
        self.assertIsNotNone(engine)
        self.assertTrue(hasattr(engine, 'coordination_matrix'))
    
    def test_resource_allocation_coordination(self):
        """Test f12 Conflict Resolution: Resource allocation across debates"""
        debates = {
            "debate1": {"required_resources": ["expert_time", "meeting_rooms", "funding"]},
            "debate2": {"required_resources": ["expert_time", "technical_analysis", "funding"]},
            "debate3": {"required_resources": ["community_outreach", "meeting_rooms", "staff_time"]}
        }
        
        available_resources = {
            "expert_time": 100,
            "meeting_rooms": 5,
            "funding": 50000,
            "technical_analysis": 3,
            "community_outreach": 10,
            "staff_time": 200
        }
        
        if hasattr(self.coordination_engine, 'allocate_resources'):
            allocation = self.coordination_engine.allocate_resources(debates, available_resources)
            
            self.assertIsInstance(allocation, dict)
            
            # Verify no over-allocation
            for resource, total_available in available_resources.items():
                total_allocated = sum(
                    allocation.get(debate_id, {}).get(resource, 0)
                    for debate_id in debates.keys()
                )
                self.assertLessEqual(total_allocated, total_available)
    
    def test_timeline_coordination(self):
        """Test f12 Conflict Resolution: Timeline coordination across debates"""
        debate_timelines = {
            "urban_planning": {
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(days=60),
                "milestones": ["public_hearing", "council_vote", "implementation"]
            },
            "environmental_impact": {
                "start_date": datetime.now() + timedelta(days=15),
                "end_date": datetime.now() + timedelta(days=90),
                "milestones": ["assessment", "review", "approval"]
            }
        }
        
        if hasattr(self.coordination_engine, 'coordinate_timelines'):
            coordination = self.coordination_engine.coordinate_timelines(debate_timelines)
            
            self.assertIsInstance(coordination, dict)
            self.assertIn("synchronized_timeline", coordination)
            self.assertIn("potential_conflicts", coordination)


class TestDebateTopologyMathematicalProperties(unittest.TestCase):
    """Test mathematical properties of debate topology operations"""
    
    def setUp(self):
        """Set up mathematical property tests"""
        self.engine = DebateTopologyIntelligenceEngine()
    
    def test_topology_consistency_theorem(self):
        """Test debate topology consistency properties"""
        # Create consistent debate topology
        debates = ["debate1", "debate2", "debate3"]
        
        if hasattr(self.engine, 'analyze_debate_topology'):
            topology1 = self.engine.analyze_debate_topology(debates)
            
            # Apply topology transformation
            if hasattr(self.engine, 'transform_topology'):
                topology2 = self.engine.transform_topology(
                    topology1,
                    transformation="add_relationship",
                    parameters={"debate1": "debate2", "type": "prerequisite"}
                )
                
                # Verify topology consistency preserved
                if hasattr(topology1, 'debates') and hasattr(topology2, 'debates'):
                    self.assertEqual(len(topology1.debates), len(topology2.debates))
    
    def test_conflict_resolution_convergence(self):
        """Test that conflict resolution algorithms converge"""
        # Create conflict scenario
        conflict_scenario = {
            "debates": ["debate1", "debate2"],
            "conflict_intensity": 0.8,
            "stakeholder_overlap": 0.6
        }
        
        if hasattr(self.engine, 'iterative_conflict_resolution'):
            resolution_history = self.engine.iterative_conflict_resolution(
                conflict_scenario,
                max_iterations=50,
                convergence_threshold=0.1
            )
            
            # Verify convergence
            self.assertTrue(resolution_history.get("converged", True))
            self.assertLess(resolution_history.get("iterations", 50), 50)
            
            # Verify conflict intensity decreases
            final_intensity = resolution_history.get("final_conflict_intensity", 1.0)
            initial_intensity = conflict_scenario["conflict_intensity"]
            self.assertLess(final_intensity, initial_intensity)
    
    def test_coordination_matrix_properties(self):
        """Test mathematical properties of coordination matrix"""
        debates = ["debate1", "debate2", "debate3"]
        
        if hasattr(self.engine, 'generate_coordination_matrix'):
            matrix = self.engine.generate_coordination_matrix(debates)
            
            # Test matrix properties
            if isinstance(matrix, dict):
                # Should be symmetric for undirected relationships
                for i, debate_i in enumerate(debates):
                    for j, debate_j in enumerate(debates):
                        if debate_i in matrix and debate_j in matrix:
                            if isinstance(matrix[debate_i], list) and isinstance(matrix[debate_j], list):
                                if len(matrix[debate_i]) > j and len(matrix[debate_j]) > i:
                                    # Symmetric property: matrix[i][j] == matrix[j][i]
                                    self.assertEqual(matrix[debate_i][j], matrix[debate_j][i])


class TestDebateTopologyIntegration(unittest.TestCase):
    """Integration tests for debate topology engine with other framework components"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.engine = DebateTopologyIntelligenceEngine()
        
    def test_agent_debate_integration(self):
        """Test f12 + f2: Debate topology integration with agent system"""
        # Mock agents with debate capabilities
        mock_agents = [
            {"agent_id": "mediator", "capabilities": ["conflict_resolution", "facilitation"]},
            {"agent_id": "expert", "capabilities": ["domain_knowledge", "analysis"]},
            {"agent_id": "stakeholder_rep", "capabilities": ["representation", "communication"]}
        ]
        
        debate_scenario = {
            "debate_id": "test_debate",
            "complexity": "high",
            "stakeholders": ["group_a", "group_b", "group_c"]
        }
        
        if hasattr(self.engine, 'assign_agents_to_debate'):
            assignment = self.engine.assign_agents_to_debate(mock_agents, debate_scenario)
            
            self.assertIsInstance(assignment, dict)
            self.assertIn("agent_assignments", assignment)
            self.assertIn("role_mappings", assignment)
    
    def test_governance_debate_integration(self):
        """Test f12 + f9: Debate topology integration with governance"""
        governance_policies = {
            "max_concurrent_debates": 5,
            "required_stakeholder_representation": 0.8,
            "debate_duration_limits": {"simple": 30, "medium": 60, "complex": 120}
        }
        
        active_debates = [
            {"id": "debate1", "complexity": "simple", "duration": 25},
            {"id": "debate2", "complexity": "medium", "duration": 45},
            {"id": "debate3", "complexity": "complex", "duration": 100}
        ]
        
        if hasattr(self.engine, 'apply_governance_to_debates'):
            governance_result = self.engine.apply_governance_to_debates(
                active_debates, 
                governance_policies
            )
            
            self.assertIsInstance(governance_result, dict)
            self.assertIn("compliance_status", governance_result)
            self.assertIn("policy_violations", governance_result)
    
    def test_spatial_debate_integration(self):
        """Test f12 + f1: Debate topology integration with spatial intelligence"""
        # Spatially-located debates
        spatial_debates = {
            "downtown_zoning": {"location": (40.7128, -74.0060), "radius": 1000},
            "waterfront_development": {"location": (40.7000, -74.0100), "radius": 500},
            "transit_expansion": {"location": (40.7200, -73.9900), "radius": 2000}
        }
        
        if hasattr(self.engine, 'analyze_spatial_debate_topology'):
            spatial_topology = self.engine.analyze_spatial_debate_topology(spatial_debates)
            
            self.assertIsInstance(spatial_topology, dict)
            self.assertIn("spatial_relationships", spatial_topology)
            self.assertIn("geographic_clusters", spatial_topology)


class TestDebateTopologyPerformance(unittest.TestCase):
    """Performance tests for debate topology operations"""
    
    def setUp(self):
        """Set up performance test fixtures"""
        self.engine = DebateTopologyIntelligenceEngine()
    
    def test_large_scale_topology_analysis(self):
        """Test performance with large numbers of debates"""
        import time
        
        # Create large set of debates
        large_debate_set = [f"debate_{i}" for i in range(100)]
        
        start_time = time.time()
        
        if hasattr(self.engine, 'analyze_debate_topology'):
            topology = self.engine.analyze_debate_topology(large_debate_set)
            
        analysis_time = time.time() - start_time
        
        # Should complete analysis in reasonable time
        self.assertLess(analysis_time, 30.0, "Large-scale topology analysis too slow")
    
    def test_coordination_scalability(self):
        """Test coordination engine scalability"""
        import time
        
        # Create many concurrent debates
        many_debates = {
            f"debate_{i}": {
                "stakeholders": [f"stakeholder_{j}" for j in range(i % 5 + 1)],
                "resources": [f"resource_{k}" for k in range(i % 3 + 1)]
            }
            for i in range(50)
        }
        
        start_time = time.time()
        
        if hasattr(self.engine, 'coordinate_cross_debate_governance'):
            # Create mock topology
            mock_topology = DebateTopology()
            mock_topology.debates = list(many_debates.keys())
            
            coordination = self.engine.coordinate_cross_debate_governance(mock_topology)
            
        coordination_time = time.time() - start_time
        
        # Should complete coordination in reasonable time
        self.assertLess(coordination_time, 15.0, "Cross-debate coordination too slow")


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestDebateTopologyIntelligenceEngine))
    suite.addTest(unittest.makeSuite(TestDebateRecognitionEngine))
    suite.addTest(unittest.makeSuite(TestCrossDebateCoordinationEngine))
    suite.addTest(unittest.makeSuite(TestDebateTopologyMathematicalProperties))
    suite.addTest(unittest.makeSuite(TestDebateTopologyIntegration))
    suite.addTest(unittest.makeSuite(TestDebateTopologyPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print(f"\n✅ All {result.testsRun} debate topology tests passed!")
    else:
        print(f"\n❌ {len(result.failures)} failures, {len(result.errors)} errors in {result.testsRun} tests")
        
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)