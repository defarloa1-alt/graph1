"""
Comprehensive Advisor Validation Tests
=====================================

Tests to verify all 4 advisor feedback points:
1. collect_data() - validation errors and timeout handling
2. train_cycle() - comprehensive logging and error handling  
3. model_update() - metrics validation for required fields
4. propose_consensus() - hierarchical tie-breaking logic

Run: python advisor_validation_tests.py
"""

import sys
import os
import time
import logging
from unittest.mock import patch, MagicMock
from io import StringIO

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.product_development_lead_agent import ProductDevelopmentLeadAgent, AgentConfig

class AdvisorValidationTests:
    def __init__(self):
        self.config = AgentConfig()
        self.config.agent_id = "advisor_test_agent"
        self.config.domain = "validation"
        self.config.consensus_gate_threshold = 0.8
        self.agent = ProductDevelopmentLeadAgent(self.config)
        self.results = []
        
        # Capture logs
        self.log_stream = StringIO()
        handler = logging.StreamHandler(self.log_stream)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Setup logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
    def log_result(self, test_name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append((test_name, passed, details))
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
            
    def test_collect_data_validation(self):
        """Test 1: collect_data() validation errors"""
        print("\n🧪 Testing collect_data() validation...")
        
        # Test invalid domain
        result = self.agent.collect_data("", {"valid": "context"})
        domain_validation_passed = not result.get("success", True) and "invalid_domain" in result.get("reason", "")
        self.log_result("Invalid domain rejection", domain_validation_passed, 
                       f"Response: {result.get('reason', 'unknown')}")
            
        # Test invalid context
        result = self.agent.collect_data("valid_domain", "not_a_dict")
        context_validation_passed = not result.get("success", True) and "invalid_context" in result.get("reason", "")
        self.log_result("Invalid context rejection", context_validation_passed,
                       f"Response: {result.get('reason', 'unknown')}")
            
        # Test invalid timeout
        result = self.agent.collect_data("valid_domain", {"test": "data"}, timeout_seconds=0)
        timeout_validation_passed = not result.get("success", True) and "invalid_timeout" in result.get("reason", "")
        self.log_result("Invalid timeout rejection", timeout_validation_passed,
                       f"Response: {result.get('reason', 'unknown')}")
        
        # Test valid parameters
        result = self.agent.collect_data("valid_domain", {"test": "data"}, timeout_seconds=1)
        valid_execution = result.get("success", False)
        self.log_result("Valid parameters acceptance", valid_execution,
                       f"Execution succeeded: {valid_execution}")
                
    def test_train_cycle_logging(self):
        """Test 2: train_cycle() logging and error handling"""
        print("\n🧪 Testing train_cycle() logging and error handling...")
        
        # Clear log stream
        self.log_stream.seek(0)
        self.log_stream.truncate(0)
        
        # Run training cycle to capture logs
        try:
            self.agent.train_cycle()
            
            # Check logs
            log_content = self.log_stream.getvalue()
            
            # Verify iteration logging
            has_iteration_logs = "Training iteration" in log_content
            self.log_result("Training iteration logging", has_iteration_logs, 
                          f"Found iteration logs: {has_iteration_logs}")
            
            # Verify completion logging
            has_completion = "Training cycle completed" in log_content
            self.log_result("Training completion logging", has_completion,
                          f"Found completion logs: {has_completion}")
            
        except Exception as e:
            self.log_result("Train cycle execution", False, f"Unexpected error: {e}")
            
        # Test error injection
        print("\n   Testing error injection...")
        original_train = self.agent._execute_train_model
        
        def failing_train(*args, **kwargs):
            raise RuntimeError("Simulated training failure")
            
        with patch.object(self.agent, '_execute_train_model', side_effect=failing_train):
            self.log_stream.seek(0)
            self.log_stream.truncate(0)
            
            result = self.agent.train_cycle()
            
            # Check if error was properly handled
            log_content = self.log_stream.getvalue()
            error_logged = "TrainModel phase failed" in log_content or "ERROR" in log_content
            error_handled = not result.get("success", True) and "train_model_failed" in result.get("reason", "")
            
            self.log_result("Error injection recovery", error_logged and error_handled,
                          f"Error logged: {error_logged}, Error handled: {error_handled}")
                
    def test_model_update_validation(self):
        """Test 3: model_update() metrics validation"""
        print("\n🧪 Testing model_update() metrics validation...")
        
        # Test missing accuracy_delta
        invalid_metrics_1 = {
            "accuracy": 0.85,
            "confidence_score": 0.9,
            # Missing accuracy_delta
            "consensus_quality": 0.8
        }
        
        result = self.agent.model_update(invalid_metrics_1)
        accuracy_delta_validation = not result.get("success", True) and "missing_required_metrics" in result.get("reason", "")
        self.log_result("Missing accuracy_delta rejection", accuracy_delta_validation,
                       f"Response: {result.get('reason', 'unknown')}")
            
        # Test missing confidence_score
        invalid_metrics_2 = {
            "accuracy": 0.85,
            "accuracy_delta": 0.02,
            # Missing confidence_score
            "consensus_quality": 0.8
        }
        
        result = self.agent.model_update(invalid_metrics_2)
        confidence_score_validation = not result.get("success", True) and "missing_required_metrics" in result.get("reason", "")
        self.log_result("Missing confidence_score rejection", confidence_score_validation,
                       f"Response: {result.get('reason', 'unknown')}")
            
        # Test valid metrics
        valid_metrics = {
            "accuracy": 0.87,
            "accuracy_delta": 0.03,
            "confidence_score": 0.85,
            "consensus_quality": 0.8,
            "evaluation_method": "cross_validation"
        }
        
        result = self.agent.model_update(valid_metrics)
        execution_success = result.get("success", False)
        self.log_result("Valid metrics acceptance", execution_success,
                       f"Model update succeeded: {execution_success}")
            
    def test_propose_consensus_tie_breaking(self):
        """Test 4: propose_consensus() hierarchical tie-breaking"""
        print("\n🧪 Testing propose_consensus() tie-breaking logic...")
        
        # Create mock graph with identical threshold proposals
        mock_graph = MagicMock()
        
        # Mock proposals with identical consensus values to trigger tie-breaking
        identical_proposals = [
            {
                "proposal_id": "A",
                "consensus_value": 0.85,
                "confidence": 0.90,  # Highest confidence (40% weight)
                "stakeholder_priority": 0.7,
                "technical_feasibility": 0.8,
                "timestamp": time.time() - 100
            },
            {
                "proposal_id": "B", 
                "consensus_value": 0.85,
                "confidence": 0.85,  # Lower confidence
                "stakeholder_priority": 0.9,  # Higher stakeholder (30% weight)
                "technical_feasibility": 0.9,
                "timestamp": time.time() - 50
            },
            {
                "proposal_id": "C",
                "consensus_value": 0.85,
                "confidence": 0.80,  # Lowest confidence
                "stakeholder_priority": 0.6,
                "technical_feasibility": 0.95,  # Highest technical (20% weight)
                "timestamp": time.time()  # Most recent (10% weight)
            }
        ]
        
        # Patch the proposal generation to return our test data
        with patch.object(self.agent, '_generate_multiple_consensus_proposals', 
                         return_value=identical_proposals):
            
            try:
                result = self.agent.propose_consensus(mock_graph)
                
                selected_id = result.get("selected_proposal_id")
                
                # Proposal A should win due to highest confidence (40% weight)
                expected_winner = "A"
                tie_breaking_worked = selected_id == expected_winner
                
                self.log_result("Hierarchical tie-breaking", tie_breaking_worked,
                              f"Selected: {selected_id}, Expected: {expected_winner}")
                
                # Verify tie-breaking was actually used
                tie_breaking_used = result.get("tie_breaking_applied", False)
                self.log_result("Tie-breaking activation", tie_breaking_used,
                              f"Tie-breaking applied: {tie_breaking_used}")
                
                # Verify weight calculation
                if "tie_breaking_scores" in result:
                    scores = result["tie_breaking_scores"]
                    self.log_result("Weight calculation", True,
                                  f"Calculated scores: {scores}")
                else:
                    self.log_result("Weight calculation", False, "No tie-breaking scores returned")
                    
            except Exception as e:
                self.log_result("Tie-breaking execution", False, f"Error: {e}")
                
    def run_all_tests(self):
        """Run all advisor validation tests"""
        print("=" * 60)
        print("🚀 ADVISOR VALIDATION TEST SUITE")
        print("=" * 60)
        
        self.test_collect_data_validation()
        self.test_train_cycle_logging()
        self.test_model_update_validation()
        self.test_propose_consensus_tie_breaking()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result, _ in self.results if result)
        total = len(self.results)
        
        print(f"Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n✅ ALL TESTS PASSED - READY FOR MERGE TO MASTER")
        else:
            print(f"\n❌ {total-passed} TESTS FAILED - NEEDS ATTENTION")
            
        return passed == total

if __name__ == "__main__":
    tester = AdvisorValidationTests()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)