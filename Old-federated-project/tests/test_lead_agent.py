"""
Unit Tests for ProductDevelopmentLeadAgent
==========================================

Comprehensive test suite for the Product Development Lead Agent including:
- f16 CollectData functionality and P16 triggers
- f17 ModelUpdate functionality and threshold triggers
- f7 Consensus proposal generation and confidence gates
- Training cycle orchestration and evaluation
- Mathematical integration hooks
- Configuration and metrics validation

Author: Enhanced Federated Graph Framework Team
Version: v1.0 (Production Ready)
Date: September 28, 2025
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

# Import the agent classes
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))

from product_development_lead_agent import (
    ProductDevelopmentLeadAgent, 
    AgentConfig, 
    AgentMetrics,
    create_lead_agent
)


class TestAgentConfig(unittest.TestCase):
    """Test AgentConfig dataclass functionality"""
    
    def test_default_config_creation(self):
        """Test default configuration values"""
        config = AgentConfig()
        
        self.assertEqual(config.agent_id, "lead")
        self.assertEqual(config.domain, "product_development")
        self.assertEqual(config.accuracy_threshold_f16, 0.85)
        self.assertEqual(config.accuracy_threshold_f17, 0.87)
        self.assertEqual(config.consensus_gate_threshold, 0.80)
        self.assertTrue(config.data_collection_enabled)
        self.assertTrue(config.model_update_enabled)
    
    def test_custom_config_creation(self):
        """Test configuration with custom values"""
        config = AgentConfig(
            agent_id="test_agent",
            domain="test_domain",
            accuracy_threshold_f16=0.90,
            accuracy_threshold_f17=0.92,
            consensus_gate_threshold=0.85
        )
        
        self.assertEqual(config.agent_id, "test_agent")
        self.assertEqual(config.domain, "test_domain")
        self.assertEqual(config.accuracy_threshold_f16, 0.90)
        self.assertEqual(config.accuracy_threshold_f17, 0.92)
        self.assertEqual(config.consensus_gate_threshold, 0.85)


class TestAgentMetrics(unittest.TestCase):
    """Test AgentMetrics dataclass functionality"""
    
    def test_default_metrics_creation(self):
        """Test default metrics values"""
        metrics = AgentMetrics()
        
        self.assertEqual(metrics.expert_accuracy, 0.0)
        self.assertEqual(metrics.consensus_quality, 0.0)
        self.assertEqual(metrics.decision_latency, 0.0)
        self.assertEqual(metrics.training_cycles_completed, 0)
        self.assertEqual(metrics.data_collection_volume_gb, 0.0)
        self.assertIsInstance(metrics.last_updated, datetime)
    
    def test_metrics_updates(self):
        """Test metrics can be updated"""
        metrics = AgentMetrics()
        
        metrics.expert_accuracy = 0.85
        metrics.consensus_quality = 0.78
        metrics.training_cycles_completed = 5
        
        self.assertEqual(metrics.expert_accuracy, 0.85)
        self.assertEqual(metrics.consensus_quality, 0.78)
        self.assertEqual(metrics.training_cycles_completed, 5)


class TestProductDevelopmentLeadAgent(unittest.TestCase):
    """Test ProductDevelopmentLeadAgent core functionality"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test configuration
        self.test_config = AgentConfig(
            agent_id="test_lead",
            domain="product_development",
            data_directory=os.path.join(self.temp_dir, "data"),
            checkpoint_directory=os.path.join(self.temp_dir, "checkpoints"),
            accuracy_threshold_f16=0.85,
            accuracy_threshold_f17=0.87,
            consensus_gate_threshold=0.80
        )
        
        # Create agent instance
        self.agent = ProductDevelopmentLeadAgent("test_lead", self.test_config)
    
    def tearDown(self):
        """Clean up test environment after each test"""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.agent_id, "test_lead")
        self.assertEqual(self.agent.config.domain, "product_development")
        self.assertIsInstance(self.agent.metrics, AgentMetrics)
        self.assertIsInstance(self.agent.policy_parameters, dict)
        self.assertEqual(len(self.agent.training_data), 0)
        self.assertEqual(len(self.agent.consensus_proposals), 0)
        self.assertFalse(self.agent.registered_with_engine)
        self.assertEqual(self.agent.traversal_position, 0)
    
    def test_policy_parameters_initialization(self):
        """Test policy parameters are properly initialized"""
        params = self.agent.policy_parameters
        
        expected_keys = [
            "accuracy_weight", "consensus_weight", "latency_weight",
            "learning_rate", "confidence_threshold", "decision_timeout",
            "max_iterations", "convergence_threshold"
        ]
        
        for key in expected_keys:
            self.assertIn(key, params)
        
        # Test weight parameters sum to 1.0
        weights = params["accuracy_weight"] + params["consensus_weight"] + params["latency_weight"]
        self.assertAlmostEqual(weights, 1.0, places=1)
    
    def test_directory_setup(self):
        """Test that required directories are created"""
        expected_dirs = [
            self.test_config.data_directory,
            self.test_config.checkpoint_directory,
            os.path.join(self.test_config.checkpoint_directory, "models"),
            os.path.join(self.test_config.checkpoint_directory, "metrics")
        ]
        
        for directory in expected_dirs:
            self.assertTrue(os.path.exists(directory), f"Directory {directory} should exist")


class TestF16CollectData(unittest.TestCase):
    """Test f16 CollectData functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = AgentConfig(
            agent_id="test_f16",
            domain="product_development",
            data_directory=os.path.join(self.temp_dir, "data")
        )
        self.agent = ProductDevelopmentLeadAgent("test_f16", self.test_config)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_collect_data_p16_trigger_success(self):
        """Test f16 CollectData with P16 trigger condition met"""
        # Set accuracy below f16 threshold to trigger P16
        self.agent.metrics.expert_accuracy = 0.80  # Below 0.85 threshold
        
        result = self.agent.collect_data("product_development", {"urgency": "high"})
        
        self.assertTrue(result["success"])
        self.assertTrue(result["p16_triggered"])
        self.assertGreater(result["data_points_collected"], 0)
        self.assertGreaterEqual(result["data_size_gb"], 0)
        self.assertEqual(result["agent_id"], "test_f16")
    
    def test_collect_data_p16_not_triggered(self):
        """Test f16 CollectData when P16 trigger condition not met"""
        # Set accuracy above f16 threshold
        self.agent.metrics.expert_accuracy = 0.90  # Above 0.85 threshold
        
        result = self.agent.collect_data("product_development")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "p16_not_triggered")
        self.assertEqual(result["current_accuracy"], 0.90)
        self.assertEqual(result["threshold"], 0.85)
    
    def test_collect_data_domain_mismatch(self):
        """Test f16 CollectData with domain mismatch"""
        # Set accuracy to trigger P16
        self.agent.metrics.expert_accuracy = 0.80
        
        result = self.agent.collect_data("different_domain")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "domain_mismatch")
        self.assertEqual(result["expected_domain"], "product_development")
        self.assertEqual(result["requested_domain"], "different_domain")
    
    def test_collect_data_general_domain_accepted(self):
        """Test f16 CollectData accepts 'general' domain"""
        # Set accuracy to trigger P16
        self.agent.metrics.expert_accuracy = 0.80
        
        result = self.agent.collect_data("general")
        
        self.assertTrue(result["success"])
        self.assertTrue(result["p16_triggered"])
    
    def test_collect_data_disabled(self):
        """Test f16 CollectData when data collection disabled"""
        # Disable data collection
        self.agent.config.data_collection_enabled = False
        self.agent.metrics.expert_accuracy = 0.80
        
        result = self.agent.collect_data("product_development")
        
        # Should still work since P16 check is bypassed when disabled
        self.assertTrue(result["success"])
    
    def test_collect_data_with_real_artifacts(self):
        """Test f16 CollectData with real JSON artifacts"""
        # Create test artifacts
        roadmaps_dir = Path(self.test_config.data_directory) / "roadmaps"
        roadmaps_dir.mkdir(parents=True, exist_ok=True)
        
        test_artifact = {
            "title": "Test Roadmap",
            "content": "Test roadmap content",
            "quality_score": 0.85,
            "complexity": "medium",
            "stakeholders": 4,
            "decision_points": 2
        }
        
        with open(roadmaps_dir / "test_roadmap.json", "w") as f:
            json.dump(test_artifact, f)
        
        # Trigger data collection
        self.agent.metrics.expert_accuracy = 0.80
        result = self.agent.collect_data("product_development")
        
        self.assertTrue(result["success"])
        self.assertGreater(result["data_points_collected"], 0)
        
        # Verify training data was updated
        self.assertGreater(len(self.agent.training_data), 0)
        
        # Find the real artifact in training data
        real_artifact = None
        for data_point in self.agent.training_data:
            if data_point["type"] == "roadmaps" and "test_roadmap.json" in data_point["source"]:
                real_artifact = data_point
                break
        
        self.assertIsNotNone(real_artifact)
        self.assertEqual(real_artifact["data"]["title"], "Test Roadmap")
    
    def test_f16_hook_registration_and_execution(self):
        """Test f16 hook registration and execution"""
        hook_called = False
        hook_args = None
        
        def test_f16_hook(domain, data, context):
            nonlocal hook_called, hook_args
            hook_called = True
            hook_args = (domain, data, context)
            return {"hook_executed": True}
        
        # Register hook
        self.agent.register_f16_hook(test_f16_hook)
        
        # Trigger data collection
        self.agent.metrics.expert_accuracy = 0.80
        result = self.agent.collect_data("product_development", {"test": "context"})
        
        # Verify hook was called
        self.assertTrue(hook_called)
        self.assertIsNotNone(hook_args)
        self.assertEqual(hook_args[0], "product_development")
        self.assertIsInstance(hook_args[1], list)  # Filtered data
        self.assertEqual(hook_args[2], {"test": "context"})
        
        # Verify hook result is included
        self.assertIn("hook_result", result)
        self.assertEqual(result["hook_result"]["hook_executed"], True)


class TestTrainingCycle(unittest.TestCase):
    """Test training cycle functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = AgentConfig(
            agent_id="test_training",
            data_directory=os.path.join(self.temp_dir, "data")
        )
        self.agent = ProductDevelopmentLeadAgent("test_training", self.test_config)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_training_cycle_success(self):
        """Test successful training cycle"""
        # Add training data
        self.agent.training_data = [{"data": f"sample_{i}"} for i in range(20)]
        
        old_accuracy = self.agent.metrics.expert_accuracy
        result = self.agent.train_cycle()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["cycle_number"], 1)
        self.assertIn("train_result", result)
        self.assertIn("eval_result", result)
        self.assertIn("accuracy_improvement", result)
        self.assertEqual(self.agent.metrics.training_cycles_completed, 1)
        
        # Accuracy should have improved
        self.assertGreater(self.agent.metrics.expert_accuracy, old_accuracy)
    
    def test_training_cycle_insufficient_data(self):
        """Test training cycle with insufficient data"""
        # No training data
        self.agent.training_data = []
        
        result = self.agent.train_cycle()
        
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "insufficient_training_data")
        self.assertEqual(result["data_points"], 0)
        self.assertEqual(result["minimum_required"], 10)
    
    def test_training_cycle_disabled(self):
        """Test training cycle when training is disabled"""
        self.agent.config.training_enabled = False
        self.agent.training_data = [{"data": f"sample_{i}"} for i in range(20)]
        
        result = self.agent.train_cycle()
        
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "training_disabled")
    
    def test_training_cycle_max_cycles_reached(self):
        """Test training cycle when max cycles reached"""
        self.agent.training_data = [{"data": f"sample_{i}"} for i in range(20)]
        self.agent.metrics.training_cycles_completed = 10  # At max
        self.agent.config.max_training_cycles = 10
        
        result = self.agent.train_cycle()
        
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "max_cycles_reached")
    
    def test_training_cycle_triggers_f17(self):
        """Test training cycle triggering f17 ModelUpdate"""
        # Set up conditions for f17 trigger
        self.agent.training_data = [{"data": f"sample_{i}"} for i in range(20)]
        self.agent.metrics.expert_accuracy = 0.86  # Will be improved above f17 threshold
        
        with patch.object(self.agent, '_execute_evaluate_performance') as mock_eval:
            mock_eval.return_value = {
                "accuracy": 0.88,  # Above f17 threshold of 0.87
                "consensus_quality": 0.82,
                "decision_latency": 2.5,
                "evaluation_method": "cross_validation",
                "validation_samples": 4,
                "performance_trend": "improving"
            }
            
            result = self.agent.train_cycle()
            
            self.assertTrue(result["success"])
            self.assertTrue(result["f17_triggered"])
            self.assertIn("model_update_result", result)


class TestF17ModelUpdate(unittest.TestCase):
    """Test f17 ModelUpdate functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = AgentConfig(agent_id="test_f17")
        self.agent = ProductDevelopmentLeadAgent("test_f17", self.test_config)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_model_update_success(self):
        """Test successful f17 ModelUpdate with required metric fields"""
        # Set accuracy above f17 threshold with required fields
        metrics = {
            "accuracy": 0.90,  # Above 0.87 threshold
            "accuracy_delta": 0.03,  # Required for f17 contract
            "confidence_score": 0.85,  # Required for f17 contract
            "consensus_quality": 0.85,
            "decision_latency": 2.0,
            "evaluation_method": "cross_validation"
        }
        
        old_params = self.agent.policy_parameters.copy()
        result = self.agent.model_update(metrics)
        
        self.assertTrue(result["success"])
        self.assertGreater(result["parameters_updated"], 0)
        self.assertIn("old_params_backup", result)
        self.assertIn("new_params", result)
        self.assertIn("validation_result", result)
        
        # Verify parameters were actually updated
        self.assertNotEqual(self.agent.policy_parameters, old_params)
    
    def test_model_update_below_threshold(self):
        """Test f17 ModelUpdate with accuracy below threshold"""
        metrics = {
            "accuracy": 0.80,  # Below 0.87 threshold
            "accuracy_delta": -0.02,  # Required for f17 contract
            "confidence_score": 0.75,  # Required for f17 contract
            "consensus_quality": 0.75,
            "decision_latency": 3.0,
            "evaluation_method": "cross_validation"
        }
        
        result = self.agent.model_update(metrics)
        
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "accuracy_below_f17_threshold")
        self.assertEqual(result["current_accuracy"], 0.80)
        self.assertEqual(result["threshold"], 0.87)
    
    def test_model_update_disabled(self):
        """Test f17 ModelUpdate when disabled"""
        self.agent.config.model_update_enabled = False
        
        metrics = {
            "accuracy": 0.90,
            "accuracy_delta": 0.03,  # Required for f17 contract
            "confidence_score": 0.85  # Required for f17 contract
        }
        result = self.agent.model_update(metrics)
        
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "model_update_disabled")
    
    def test_model_update_missing_required_fields(self):
        """Test f17 ModelUpdate with missing required metric fields"""
        # Test missing accuracy_delta
        metrics_missing_delta = {
            "accuracy": 0.90,
            "confidence_score": 0.85,
            "consensus_quality": 0.85
        }
        
        result = self.agent.model_update(metrics_missing_delta)
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "missing_required_metrics")
        self.assertIn("accuracy_delta", result["missing_fields"])
        
        # Test missing confidence_score
        metrics_missing_confidence = {
            "accuracy": 0.90,
            "accuracy_delta": 0.03,
            "consensus_quality": 0.85
        }
        
        result = self.agent.model_update(metrics_missing_confidence)
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "missing_required_metrics")
        self.assertIn("confidence_score", result["missing_fields"])
    
    def test_model_update_parameter_validation_failure(self):
        """Test f17 ModelUpdate with invalid parameters"""
        metrics = {
            "accuracy": 0.90,
            "accuracy_delta": 0.03,  # Required for f17 contract
            "confidence_score": 0.85  # Required for f17 contract
        }
        
        # Mock validation to fail
        with patch.object(self.agent, '_validate_policy_parameters') as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "errors": ["Test validation error"]
            }
            
            result = self.agent.model_update(metrics)
            
            self.assertFalse(result["success"])
            self.assertEqual(result["reason"], "parameter_validation_failed")
    
    def test_f17_hook_registration_and_execution(self):
        """Test f17 hook registration and execution"""
        hook_called = False
        hook_args = None
        
        def test_f17_hook(params, metrics):
            nonlocal hook_called, hook_args
            hook_called = True
            hook_args = (params, metrics)
            return {"f17_hook_executed": True}
        
        # Register hook
        self.agent.register_f17_hook(test_f17_hook)
        
        # Trigger model update
        metrics = {"accuracy": 0.90}
        result = self.agent.model_update(metrics)
        
        # Verify hook was called
        self.assertTrue(hook_called)
        self.assertIsNotNone(hook_args)
        
        # Verify hook result is included
        self.assertIn("hook_result", result)
        self.assertEqual(result["hook_result"]["f17_hook_executed"], True)


class TestF7ConsensusProposal(unittest.TestCase):
    """Test f7 Consensus proposal functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.agent = ProductDevelopmentLeadAgent("test_f7")
        
        # Create mock graph
        self.mock_graph = Mock()
        self.mock_graph.nodes.return_value = ["v1", "v2", "v3", "lead"]
        self.mock_graph.edges.return_value = [("v1", "v2"), ("v2", "v3"), ("v3", "lead")]
    
    def test_propose_consensus_success(self):
        """Test successful f7 consensus proposal"""
        # Mock high confidence for success
        with patch.object(self.agent, '_apply_confidence_gates') as mock_gates:
            mock_gates.return_value = {
                "confidence_score": 0.85,  # Above 0.80 threshold
                "gate_passed": True,
                "individual_scores": {"data_quality": 0.85, "stakeholder_engagement": 0.82},
                "gate_threshold": 0.80
            }
            
            result = self.agent.propose_consensus(self.mock_graph)
            
            self.assertTrue(result["success"])
            self.assertTrue(result["consensus_threshold_met"])
            self.assertIn("consensus_proposal", result)
            self.assertIn("confidence_result", result)
            self.assertEqual(len(self.agent.consensus_proposals), 1)
    
    def test_propose_consensus_threshold_not_met(self):
        """Test f7 consensus proposal with threshold not met"""
        # Mock low confidence for failure
        with patch.object(self.agent, '_apply_confidence_gates') as mock_gates:
            mock_gates.return_value = {
                "confidence_score": 0.75,  # Below 0.80 threshold
                "gate_passed": False,
                "individual_scores": {"data_quality": 0.75, "stakeholder_engagement": 0.72},
                "gate_threshold": 0.80
            }
            
            result = self.agent.propose_consensus(self.mock_graph)
            
            self.assertFalse(result["success"])
            self.assertEqual(result["reason"], "consensus_threshold_not_met")
            self.assertEqual(result["confidence_score"], 0.75)
            self.assertEqual(result["threshold"], 0.80)
    
    def test_f7_hook_registration_and_execution(self):
        """Test f7 hook registration and execution"""
        hook_called = False
        hook_args = None
        
        def test_f7_hook(proposal, graph):
            nonlocal hook_called, hook_args
            hook_called = True
            hook_args = (proposal, graph)
            return {"f7_hook_executed": True}
        
        # Register hook
        self.agent.register_f7_hook(test_f7_hook)
        
        # Mock successful consensus
        with patch.object(self.agent, '_apply_confidence_gates') as mock_gates:
            mock_gates.return_value = {
                "confidence_score": 0.85,
                "gate_passed": True,
                "individual_scores": {},
                "gate_threshold": 0.80
            }
            
            result = self.agent.propose_consensus(self.mock_graph)
            
            # Verify hook was called
            self.assertTrue(hook_called)
            self.assertIsNotNone(hook_args)
            
            # Verify hook result is included
            self.assertIn("hook_result", result)
            self.assertEqual(result["hook_result"]["f7_hook_executed"], True)


class TestAgentStatus(unittest.TestCase):
    """Test agent status and metrics functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.agent = ProductDevelopmentLeadAgent("test_status")
    
    def test_get_agent_status(self):
        """Test comprehensive agent status retrieval"""
        # Update some metrics
        self.agent.metrics.expert_accuracy = 0.85
        self.agent.metrics.consensus_quality = 0.78
        self.agent.metrics.training_cycles_completed = 3
        self.agent.training_data = [{"data": "sample"}] * 15
        self.agent.consensus_proposals = [{"proposal": "test"}] * 2
        
        status = self.agent.get_agent_status()
        
        # Verify structure
        expected_keys = [
            "agent_id", "domain", "traversal_position", "registered_with_engine",
            "metrics", "configuration", "data_state"
        ]
        
        for key in expected_keys:
            self.assertIn(key, status)
        
        # Verify metrics formatting
        self.assertEqual(status["metrics"]["expert_accuracy"], "85.0%")
        self.assertEqual(status["metrics"]["consensus_quality"], "78.0%")
        self.assertEqual(status["metrics"]["training_cycles_completed"], 3)
        
        # Verify configuration
        self.assertEqual(status["configuration"]["f16_threshold"], 0.85)
        self.assertEqual(status["configuration"]["f17_threshold"], 0.87)
        
        # Verify data state
        self.assertEqual(status["data_state"]["training_data_points"], 15)
        self.assertEqual(status["data_state"]["consensus_proposals"], 2)


class TestFactoryFunction(unittest.TestCase):
    """Test create_lead_agent factory function"""
    
    def test_create_lead_agent_default(self):
        """Test factory function with default parameters"""
        agent = create_lead_agent()
        
        self.assertEqual(agent.agent_id, "lead")
        self.assertEqual(agent.config.domain, "product_development")
        self.assertIsInstance(agent, ProductDevelopmentLeadAgent)
    
    def test_create_lead_agent_custom_id(self):
        """Test factory function with custom agent ID"""
        agent = create_lead_agent("custom_agent")
        
        self.assertEqual(agent.agent_id, "custom_agent")
        self.assertEqual(agent.config.agent_id, "custom_agent")
    
    def test_create_lead_agent_custom_config(self):
        """Test factory function with custom configuration"""
        config = {
            "domain": "test_domain",
            "accuracy_threshold_f16": 0.90,
            "consensus_gate_threshold": 0.85
        }
        
        agent = create_lead_agent("test_agent", config)
        
        self.assertEqual(agent.config.domain, "test_domain")
        self.assertEqual(agent.config.accuracy_threshold_f16, 0.90)
        self.assertEqual(agent.config.consensus_gate_threshold, 0.85)


class TestParameterValidation(unittest.TestCase):
    """Test policy parameter validation"""
    
    def setUp(self):
        """Set up test environment"""
        self.agent = ProductDevelopmentLeadAgent("test_validation")
    
    def test_validate_policy_parameters_success(self):
        """Test successful parameter validation"""
        valid_params = {
            "accuracy_weight": 0.4,
            "consensus_weight": 0.3,
            "latency_weight": 0.3,
            "learning_rate": 0.005,
            "confidence_threshold": 0.75
        }
        
        result = self.agent._validate_policy_parameters(valid_params)
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)
    
    def test_validate_policy_parameters_weight_sum_error(self):
        """Test parameter validation with incorrect weight sum"""
        invalid_params = {
            "accuracy_weight": 0.5,
            "consensus_weight": 0.4,
            "latency_weight": 0.2  # Sum = 1.1, not 1.0
        }
        
        result = self.agent._validate_policy_parameters(invalid_params)
        
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)
        self.assertTrue(any("sum to" in error for error in result["errors"]))
    
    def test_validate_policy_parameters_range_error(self):
        """Test parameter validation with out-of-range values"""
        invalid_params = {
            "learning_rate": 0.5,  # Above max 0.1
            "confidence_threshold": 0.4,  # Below min 0.5
            "decision_timeout": 15.0  # Above max 10.0
        }
        
        result = self.agent._validate_policy_parameters(invalid_params)
        
        self.assertFalse(result["valid"])
        self.assertGreaterEqual(len(result["errors"]), 3)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete agent workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = AgentConfig(
            agent_id="integration_test",
            data_directory=os.path.join(self.temp_dir, "data")
        )
        self.agent = ProductDevelopmentLeadAgent("integration_test", self.test_config)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_agent_workflow(self):
        """Test complete agent workflow: collect data -> train -> update -> consensus"""
        
        # Step 1: f16 CollectData
        self.agent.metrics.expert_accuracy = 0.80  # Trigger P16
        collect_result = self.agent.collect_data("product_development")
        
        self.assertTrue(collect_result["success"])
        self.assertGreater(len(self.agent.training_data), 0)
        
        # Step 2: Training cycle (includes f17 if triggered)
        train_result = self.agent.train_cycle()
        
        self.assertTrue(train_result["success"])
        self.assertEqual(self.agent.metrics.training_cycles_completed, 1)
        
        # Step 3: f7 Consensus proposal
        mock_graph = Mock()
        mock_graph.nodes.return_value = ["v1", "v2", "lead"]
        mock_graph.edges.return_value = [("v1", "v2"), ("v2", "lead")]
        
        # Mock successful consensus
        with patch.object(self.agent, '_apply_confidence_gates') as mock_gates:
            mock_gates.return_value = {
                "confidence_score": 0.85,
                "gate_passed": True,
                "individual_scores": {},
                "gate_threshold": 0.80
            }
            
            consensus_result = self.agent.propose_consensus(mock_graph)
            
            self.assertTrue(consensus_result["success"])
            self.assertGreater(len(self.agent.consensus_proposals), 0)
        
        # Verify final state
        status = self.agent.get_agent_status()
        self.assertGreater(float(status["metrics"]["expert_accuracy"].rstrip("%")), 80.0)
        self.assertEqual(status["data_state"]["training_data_points"], len(self.agent.training_data))
    
    def test_mathematical_hooks_integration(self):
        """Test integration of all mathematical hooks (f16, f17, f7)"""
        
        hooks_called = {"f16": False, "f17": False, "f7": False}
        
        def f16_hook(domain, data, context):
            hooks_called["f16"] = True
            return {"f16_executed": True}
        
        def f17_hook(params, metrics):
            hooks_called["f17"] = True
            return {"f17_executed": True}
        
        def f7_hook(proposal, graph):
            hooks_called["f7"] = True
            return {"f7_executed": True}
        
        # Register all hooks
        self.agent.register_f16_hook(f16_hook)
        self.agent.register_f17_hook(f17_hook)
        self.agent.register_f7_hook(f7_hook)
        
        # Trigger f16
        self.agent.metrics.expert_accuracy = 0.80
        collect_result = self.agent.collect_data("product_development")
        
        # Trigger f17 through training with high resulting accuracy
        with patch.object(self.agent, '_execute_evaluate_performance') as mock_eval:
            mock_eval.return_value = {
                "accuracy": 0.90,  # Above f17 threshold
                "consensus_quality": 0.85,
                "decision_latency": 2.0,
                "evaluation_method": "test",
                "validation_samples": 10,
                "performance_trend": "improving"
            }
            
            train_result = self.agent.train_cycle()
        
        # Trigger f7
        mock_graph = Mock()
        mock_graph.nodes.return_value = ["v1", "lead"]
        mock_graph.edges.return_value = [("v1", "lead")]
        
        with patch.object(self.agent, '_apply_confidence_gates') as mock_gates:
            mock_gates.return_value = {
                "confidence_score": 0.85,
                "gate_passed": True,
                "individual_scores": {},
                "gate_threshold": 0.80
            }
            
            consensus_result = self.agent.propose_consensus(mock_graph)
        
        # Verify all hooks were called
        self.assertTrue(hooks_called["f16"], "f16 hook should have been called")
        self.assertTrue(hooks_called["f17"], "f17 hook should have been called") 
        self.assertTrue(hooks_called["f7"], "f7 hook should have been called")


if __name__ == "__main__":
    # Configure test runner
    unittest.main(
        verbosity=2,
        buffer=True,
        failfast=False
    )