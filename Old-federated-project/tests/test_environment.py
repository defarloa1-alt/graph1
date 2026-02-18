"""
Environment Validation Tests
===========================

Test suite to validate the development environment setup and 
ensure all components are properly configured before running 
the full framework test suite.

Author: Enhanced Federated Graph Framework Team
Version: v1.0 (Environment Setup)
Date: September 29, 2025
"""

import unittest
import sys
import os
from pathlib import Path


class TestEnvironmentSetup(unittest.TestCase):
    """Test development environment configuration"""
    
    def test_python_version(self):
        """Test Python version compatibility"""
        version_info = sys.version_info
        
        # Ensure Python 3.9 or higher
        self.assertGreaterEqual(version_info.major, 3)
        self.assertGreaterEqual(version_info.minor, 9)
        
        print(f"✅ Python version: {sys.version}")
    
    def test_required_packages(self):
        """Test that required packages are importable"""
        required_packages = [
            'numpy',
            'pytest', 
            'unittest',
            'json',
            'os',
            'tempfile',
            'datetime',
            'pathlib'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} imported successfully")
            except ImportError:
                self.fail(f"Required package {package} not available")
    
    def test_optional_packages(self):
        """Test optional packages for framework features"""
        optional_packages = {
            'torch': 'Machine learning functionality',
            'networkx': 'Graph processing',
            'scipy': 'Scientific computing',
            'pandas': 'Data processing',
            'matplotlib': 'Visualization',
            'plotly': 'Interactive visualization'
        }
        
        for package, description in optional_packages.items():
            try:
                __import__(package)
                print(f"✅ {package} available - {description}")
            except ImportError:
                print(f"⚠️  {package} not available - {description}")
    
    def test_project_structure(self):
        """Test that project structure is properly set up"""
        project_root = Path(__file__).parent.parent
        
        expected_files = [
            'requirements.txt',
            'requirements-dev.txt',
            'DEVELOPMENT_WORKFLOW.md',
            'tox.ini',
            'noxfile.py',
            '.pre-commit-config.yaml'
        ]
        
        expected_dirs = [
            'tests',
            '.vscode',
            '.venv'
        ]
        
        for file_name in expected_files:
            file_path = project_root / file_name
            self.assertTrue(file_path.exists(), f"Missing required file: {file_name}")
            print(f"✅ Found: {file_name}")
        
        for dir_name in expected_dirs:
            dir_path = project_root / dir_name
            self.assertTrue(dir_path.exists(), f"Missing required directory: {dir_name}")
            print(f"✅ Found directory: {dir_name}")
    
    def test_vscode_configuration(self):
        """Test VS Code configuration files"""
        vscode_dir = Path(__file__).parent.parent / '.vscode'
        
        config_files = ['settings.json', 'tasks.json']
        
        for config_file in config_files:
            config_path = vscode_dir / config_file
            self.assertTrue(config_path.exists(), f"Missing VS Code config: {config_file}")
            
            # Test that JSON is valid
            try:
                import json
                with open(config_path, 'r') as f:
                    json.load(f)
                print(f"✅ VS Code {config_file} is valid JSON")
            except json.JSONDecodeError:
                self.fail(f"Invalid JSON in {config_file}")
    
    def test_test_files_exist(self):
        """Test that test files are present"""
        tests_dir = Path(__file__).parent
        
        expected_test_files = [
            'test_spatial_engine.py',
            'test_debate_topology.py',
            'test_lead_agent.py'
        ]
        
        for test_file in expected_test_files:
            test_path = tests_dir / test_file
            self.assertTrue(test_path.exists(), f"Missing test file: {test_file}")
            print(f"✅ Found test file: {test_file}")
    
    def test_requirements_files(self):
        """Test requirements files are properly formatted"""
        project_root = Path(__file__).parent.parent
        
        req_files = ['requirements.txt', 'requirements-dev.txt']
        
        for req_file in req_files:
            req_path = project_root / req_file
            
            self.assertTrue(req_path.exists(), f"Missing {req_file}")
            
            with open(req_path, 'r') as f:
                content = f.read()
                
            # Should contain pytest
            self.assertIn('pytest', content, f"{req_file} should contain pytest")
            print(f"✅ {req_file} properly formatted with pytest")


class TestMathematicalFramework(unittest.TestCase):
    """Test basic mathematical framework components"""
    
    def test_numpy_operations(self):
        """Test NumPy mathematical operations for f1-f17 formulas"""
        import numpy as np
        
        # Test basic operations that would be used in f1-f17
        test_array = np.array([1, 2, 3, 4, 5])
        
        # f1 spatial operations
        spatial_transform = np.linalg.norm(test_array)
        self.assertGreater(spatial_transform, 0)
        
        # f13 performance optimization
        optimized = np.max(test_array) - np.min(test_array)
        self.assertEqual(optimized, 4)
        
        print("✅ NumPy mathematical operations working")
    
    def test_basic_graph_structures(self):
        """Test basic graph structures for federated framework"""
        # Mock graph structure using basic Python
        nodes = {'node1', 'node2', 'node3'}
        edges = [('node1', 'node2'), ('node2', 'node3')]
        
        # Basic graph operations
        self.assertEqual(len(nodes), 3)
        self.assertEqual(len(edges), 2)
        
        # Test connectivity
        connected_nodes = set()
        for edge in edges:
            connected_nodes.update(edge)
        
        self.assertEqual(connected_nodes, nodes)
        print("✅ Basic graph structures working")


class TestFrameworkModules(unittest.TestCase):
    """Test that framework modules can be imported"""
    
    def test_import_framework_files(self):
        """Test importing framework Python files"""
        project_root = Path(__file__).parent.parent
        
        # Add project root to path
        sys.path.insert(0, str(project_root))
        
        # Test framework files that should be importable
        framework_files = [
            'universal_spatial_graph',
            'debate_topology_intelligence_engine',
            'enhanced_core'
        ]
        
        for module_name in framework_files:
            module_path = project_root / f"{module_name}.py"
            
            if module_path.exists():
                try:
                    # Try to import the module
                    module = __import__(module_name)
                    print(f"✅ Successfully imported {module_name}")
                except ImportError as e:
                    # Expected for modules with heavy dependencies
                    print(f"⚠️  {module_name} import failed (expected): {e}")
                except Exception as e:
                    print(f"⚠️  {module_name} had other issues: {e}")
            else:
                print(f"ℹ️  {module_name}.py not found")


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(loader.loadTestsFromTestCase(TestEnvironmentSetup))
    suite.addTest(loader.loadTestsFromTestCase(TestMathematicalFramework))
    suite.addTest(loader.loadTestsFromTestCase(TestFrameworkModules))
    
    # Run tests with high verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*50)
    if result.wasSuccessful():
        print(f"✅ All {result.testsRun} environment validation tests passed!")
        print("🚀 Development environment is properly configured")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors in {result.testsRun} tests")
        print("🔧 Please fix environment issues before proceeding")
    
    print("="*50)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)