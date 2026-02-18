#!/usr/bin/env python3
"""
Regression tests for formal ScenarioGenerator to prevent fallback issues.

These tests exercise the real constraint-space extraction and assert that
formal scenario generation stays out of fallback mode, catching future
regressions early.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import torch
import logging
from typing import Dict, List, Callable, Any

# Import from the local module
from mathematical_formalism_v2 import SystemState, ScenarioGenerator

class TestScenarioGeneratorRegression:
    """Regression tests to ensure formal scenario generation remains stable"""
    
    def setup_method(self):
        """Set up test environment"""
        self.generator = ScenarioGenerator()
        self.logger = logging.getLogger(__name__)
        
    def create_test_state(self, graph_size: int = 8, agent_count: int = 6) -> SystemState:
        """Create a test SystemState with realistic parameters"""
        return SystemState(
            graph_topology=torch.randn(graph_size, graph_size),
            agent_states=torch.randn(agent_count, 4),
            spatial_coordinates=torch.randn(agent_count, 3),
            temporal_sequence=torch.randn(10, 2),
            epistemic_beliefs=torch.randn(agent_count, 3)
        )
    
    def test_basic_constraint_satisfaction_no_fallback(self):
        """Test that basic constraints generate scenarios without fallback"""
        state = self.create_test_state()
        
        constraints = {
            'graph_size': lambda s: s.graph_topology.shape[0] <= 15,
            'agent_count': lambda s: s.agent_states.shape[0] <= 10,
            'spatial_bounds': lambda s: torch.all(torch.abs(s.spatial_coordinates) <= 20.0)
        }
        
        # Should generate scenarios without raising exceptions
        scenarios = self.generator.generate_scenarios(
            graph_state=state,
            domain_constraints=constraints,
            completeness_threshold=0.6,
            minimality_threshold=0.1
        )
        
        # Assert formal generation succeeded
        assert len(scenarios) > 0, "Formal scenario generation failed - no scenarios produced"
        assert isinstance(scenarios, list), "Scenarios should be returned as list"
        
        # Verify scenario structure
        for scenario in scenarios:
            assert 'id' in scenario, "Scenario missing required 'id' field"
            assert 'constraint_satisfaction' in scenario, "Scenario missing constraint satisfaction"
            assert 'graph_perturbation' in scenario, "Scenario missing graph perturbation"
            assert 'expected_outcomes' in scenario, "Scenario missing expected outcomes"
    
    def test_diverse_constraint_types(self):
        """Test scenario generation with diverse constraint types"""
        state = self.create_test_state(graph_size=10, agent_count=8)
        
        # Mix of numerical, boolean, and tensor-based constraints
        constraints = {
            'max_graph_nodes': lambda s: s.graph_topology.shape[0] <= 12,
            'min_agents': lambda s: s.agent_states.shape[0] >= 5,
            'spatial_coherence': lambda s: torch.std(s.spatial_coordinates) < 5.0,
            'temporal_continuity': lambda s: s.temporal_sequence.shape[0] >= 8,
            'epistemic_consistency': lambda s: torch.all(torch.abs(s.epistemic_beliefs) <= 10.0),
            'agent_spatial_alignment': lambda s: s.agent_states.shape[0] == s.spatial_coordinates.shape[0]
        }
        
        scenarios = self.generator.generate_scenarios(
            graph_state=state,
            domain_constraints=constraints,
            completeness_threshold=0.5,
            minimality_threshold=0.15
        )
        
        assert len(scenarios) > 0, "Failed to generate scenarios with diverse constraints"
        
        # Verify constraint satisfaction tensors have proper dimensionality
        for scenario in scenarios:
            constraint_vec = scenario['constraint_satisfaction']
            assert len(constraint_vec.shape) >= 1, "Constraint satisfaction should be vector-like"
            assert constraint_vec.shape[0] == len(constraints), f"Expected {len(constraints)} constraints, got {constraint_vec.shape[0]}"
    
    def test_empty_constraints_edge_case(self):
        """Test behavior with empty constraint set"""
        state = self.create_test_state()
        
        # Empty constraints should still produce valid scenarios
        scenarios = self.generator.generate_scenarios(
            graph_state=state,
            domain_constraints={},
            completeness_threshold=0.3,
            minimality_threshold=0.1
        )
        
        assert len(scenarios) > 0, "Should generate scenarios even with empty constraints"
        
        for scenario in scenarios:
            # With empty constraints, constraint satisfaction should be minimal
            constraint_vec = scenario['constraint_satisfaction']
            assert constraint_vec.numel() >= 1, "Should have at least minimal constraint representation"
    
    def test_threshold_boundary_conditions(self):
        """Test behavior at threshold boundaries"""
        state = self.create_test_state()
        
        constraints = {
            'graph_size': lambda s: s.graph_topology.shape[0] <= 20,
            'agent_bounds': lambda s: s.agent_states.shape[0] <= 15
        }
        
        # Test with very low thresholds (should always pass)
        scenarios_low = self.generator.generate_scenarios(
            graph_state=state,
            domain_constraints=constraints,
            completeness_threshold=0.1,
            minimality_threshold=0.05
        )
        assert len(scenarios_low) > 0, "Low thresholds should generate scenarios"
        
        # Test with reasonable thresholds
        scenarios_mid = self.generator.generate_scenarios(
            graph_state=state,
            domain_constraints=constraints,
            completeness_threshold=0.6,
            minimality_threshold=0.1
        )
        assert len(scenarios_mid) > 0, "Mid-range thresholds should generate scenarios"
        
        # Test with higher thresholds (may be more selective but shouldn't crash)
        scenarios_high = self.generator.generate_scenarios(
            graph_state=state,
            domain_constraints=constraints,
            completeness_threshold=0.8,
            minimality_threshold=0.2
        )
        # High thresholds might produce fewer scenarios but shouldn't fail completely
        assert isinstance(scenarios_high, list), "High thresholds should return valid list"
    
    def test_constraint_failure_scenarios(self):
        """Test constraints that are designed to be difficult to satisfy"""
        state = self.create_test_state(graph_size=5, agent_count=3)
        
        # Constraints that are very restrictive but not impossible
        strict_constraints = {
            'tiny_graph': lambda s: s.graph_topology.shape[0] <= 6,
            'few_agents': lambda s: s.agent_states.shape[0] <= 4,
            'small_spatial': lambda s: torch.all(torch.abs(s.spatial_coordinates) <= 1.0),
            'short_temporal': lambda s: s.temporal_sequence.shape[0] >= 8
        }
        
        # Should still generate some scenarios, even if coverage is lower
        scenarios = self.generator.generate_scenarios(
            graph_state=state,
            domain_constraints=strict_constraints,
            completeness_threshold=0.3,  # Lower threshold for strict constraints
            minimality_threshold=0.1
        )
        
        assert len(scenarios) > 0, "Should generate scenarios even with strict constraints"
    
    def test_scenario_independence_property(self):
        """Test that generated scenarios satisfy independence requirements"""
        state = self.create_test_state()
        
        constraints = {
            'balanced_graph': lambda s: 4 <= s.graph_topology.shape[0] <= 12,
            'sufficient_agents': lambda s: 3 <= s.agent_states.shape[0] <= 10
        }
        
        scenarios = self.generator.generate_scenarios(
            graph_state=state,
            domain_constraints=constraints,
            completeness_threshold=0.5,
            minimality_threshold=0.2  # Higher minimality requirement
        )
        
        assert len(scenarios) > 0, "Should generate scenarios with independence requirements"
        
        # If we have multiple scenarios, they should be reasonably independent
        if len(scenarios) > 1:
            for i in range(len(scenarios)):
                for j in range(i+1, len(scenarios)):
                    vec_i = scenarios[i]['constraint_satisfaction']
                    vec_j = scenarios[j]['constraint_satisfaction']
                    
                    # Compute similarity
                    if vec_i.numel() > 0 and vec_j.numel() > 0:
                        similarity = torch.cosine_similarity(vec_i, vec_j, dim=0)
                        independence = 1.0 - similarity.item()
                        
                        # Should have some independence (not identical)
                        assert independence > 0.0, f"Scenarios {i} and {j} are too similar (independence: {independence})"
    
    def test_coverage_computation_accuracy(self):
        """Test that coverage computation is working correctly"""
        state = self.create_test_state()
        
        # Use constraints we know should be satisfiable
        simple_constraints = {
            'reasonable_size': lambda s: s.graph_topology.shape[0] >= 1,
            'has_agents': lambda s: s.agent_states.shape[0] >= 1
        }
        
        scenarios = self.generator.generate_scenarios(
            graph_state=state,
            domain_constraints=simple_constraints,
            completeness_threshold=0.4,
            minimality_threshold=0.1
        )
        
        assert len(scenarios) > 0, "Simple constraints should generate scenarios"
        
        # Test internal coverage computation by accessing the method
        constraint_space = self.generator._extract_constraint_space(simple_constraints)
        coverage = self.generator._compute_scenario_coverage(scenarios, constraint_space)
        
        assert 0.0 <= coverage <= 1.0, f"Coverage should be between 0 and 1, got {coverage}"
        assert coverage >= 0.4, f"Coverage {coverage} should meet threshold 0.4"
    
    def test_constraint_space_extraction_robustness(self):
        """Test that constraint space extraction handles various edge cases"""
        state = self.create_test_state()
        
        # Test constraints that might fail on some samples
        robust_constraints = {
            'size_check': lambda s: s.graph_topology.shape[0] > 0,
            'dimension_check': lambda s: len(s.agent_states.shape) == 2,
            'positive_temporal': lambda s: s.temporal_sequence.shape[0] > 0,
            'valid_spatial': lambda s: torch.all(torch.isfinite(s.spatial_coordinates))
        }
        
        # Extract constraint space directly to test robustness
        constraint_space = self.generator._extract_constraint_space(robust_constraints)
        
        assert constraint_space.shape[0] == len(robust_constraints), "Should have one row per constraint"
        assert constraint_space.shape[1] > 0, "Should have sample points"
        assert torch.all(torch.isfinite(constraint_space)), "Constraint space should contain finite values"
        
        # Verify scenarios can be generated
        scenarios = self.generator.generate_scenarios(
            graph_state=state,
            domain_constraints=robust_constraints,
            completeness_threshold=0.5,
            minimality_threshold=0.1
        )
        
        assert len(scenarios) > 0, "Robust constraints should generate scenarios"


class TestScenarioGeneratorIntegration:
    """Integration tests with live engine components"""
    
    def test_live_engine_integration_no_fallback(self):
        """Test that live engine integration uses formal generation without fallback"""
        from src.live_engine_integration import LiveEngineIntegrator
        import logging
        
        # Capture logging to verify no fallback warnings
        log_capture = []
        
        class TestLogHandler(logging.Handler):
            def emit(self, record):
                log_capture.append(record.getMessage())
        
        # Set up integrator with test config
        test_config = {
            'graph_size': 10,
            'agent_count': 8,
            'spatial_dims': 3,
            'debug_mode': True
        }
        integrator = LiveEngineIntegrator(config=test_config, enable_persistence=False)
        
        # Add test log handler
        test_handler = TestLogHandler()
        integrator.logger.addHandler(test_handler)
        integrator.logger.setLevel(logging.INFO)
        
        try:
            # Generate scenario through live engine
            scenario_data = integrator.generate_scenario(
                scenario_type='test_regression',
                constraints={
                    'basic_graph': lambda s: s.graph_topology.shape[0] <= 20,
                    'basic_agents': lambda s: s.agent_states.shape[0] <= 15
                }
            )
            
            # Verify formal generation was used (data is nested under 'generated_scenario')
            assert 'generated_scenario' in scenario_data, "Should contain generated_scenario field"
            generated = scenario_data['generated_scenario']
            
            assert generated['generation_method'] == 'constraint_satisfaction', "Should use formal generation method"
            assert generated['generated_at'] == 'formal_generation', "Should be marked as formal generation"
            assert 'scenarios' in generated, "Should contain scenario list"
            assert len(generated['scenarios']) > 0, "Should have generated scenarios"
            
            # Check logs for fallback warnings
            fallback_warnings = [msg for msg in log_capture if 'fallback' in msg.lower()]
            assert len(fallback_warnings) == 0, f"Should not have fallback warnings, but found: {fallback_warnings}"
            
            # Check for success indicators
            success_logs = [msg for msg in log_capture if '✅ Formal scenario generation successful' in msg]
            assert len(success_logs) > 0, "Should have success logs from formal generation"
            
        finally:
            # Clean up log handler
            integrator.logger.removeHandler(test_handler)


if __name__ == "__main__":
    # Run basic regression tests
    test_runner = TestScenarioGeneratorRegression()
    test_runner.setup_method()
    
    print("🧪 Running scenario generation regression tests...")
    
    try:
        test_runner.test_basic_constraint_satisfaction_no_fallback()
        print("✅ Basic constraint satisfaction test passed")
        
        test_runner.test_diverse_constraint_types()
        print("✅ Diverse constraint types test passed")
        
        test_runner.test_empty_constraints_edge_case()
        print("✅ Empty constraints edge case test passed")
        
        test_runner.test_threshold_boundary_conditions()
        print("✅ Threshold boundary conditions test passed")
        
        test_runner.test_constraint_failure_scenarios()
        print("✅ Constraint failure scenarios test passed")
        
        test_runner.test_scenario_independence_property()
        print("✅ Scenario independence property test passed")
        
        test_runner.test_coverage_computation_accuracy()
        print("✅ Coverage computation accuracy test passed")
        
        test_runner.test_constraint_space_extraction_robustness()
        print("✅ Constraint space extraction robustness test passed")
        
        # Integration test
        integration_test = TestScenarioGeneratorIntegration()
        integration_test.test_live_engine_integration_no_fallback()
        print("✅ Live engine integration no-fallback test passed")
        
        print("\n🎯 All regression tests passed! Formal ScenarioGenerator is stable.")
        
    except Exception as e:
        print(f"❌ Regression test failed: {e}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")