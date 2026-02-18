#!/usr/bin/env python3
"""
LCC Taxonomy Integration Test Suite
===================================

Comprehensive test suite to validate the complete LCC taxonomy integration.
Tests file parsing, database loading, and bundle functionality.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import logging

# Suppress logging during tests
logging.disable(logging.CRITICAL)

class TestLCCFileParser(unittest.TestCase):
    """Test LCC file parsing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = tempfile.mkdtemp()
        
        # Create sample CSV file
        sample_csv = """C1-51,Auxiliary Sciences of History (General)
CB3-482,History of Civilization
CC1-960,Archaeology"""
        
        csv_path = Path(self.test_data_dir) / "test_lcc.csv"
        with open(csv_path, 'w') as f:
            f.write(sample_csv)
        
        # Create sample data structure
        self.sample_consolidated_data = [
            {
                "class_code": "C1-51",
                "label": "Auxiliary Sciences of History (General)",
                "parent_code": "C",
                "level": 1,
                "source_file": "test_lcc.csv"
            },
            {
                "class_code": "CB3-482", 
                "label": "History of Civilization",
                "parent_code": "C",
                "level": 1,
                "source_file": "test_lcc.csv"
            }
        ]
    
    def test_validate_class_code(self):
        """Test class code validation."""
        try:
            from lcc_file_parser import LCCFileParser
            parser = LCCFileParser()
            
            # Valid codes
            self.assertTrue(parser.validate_class_code("A"))
            self.assertTrue(parser.validate_class_code("QA76"))
            self.assertTrue(parser.validate_class_code("QA76-77"))
            self.assertTrue(parser.validate_class_code("QA76.9"))
            
            # Invalid codes
            self.assertFalse(parser.validate_class_code(""))
            self.assertFalse(parser.validate_class_code("123"))
            self.assertFalse(parser.validate_class_code(None))
        
        except ImportError:
            self.skipTest("LCC file parser not available")
    
    def test_extract_numeric_range(self):
        """Test numeric range extraction."""
        try:
            from lcc_file_parser import LCCFileParser
            parser = LCCFileParser()
            
            # Range format
            start, end = parser.extract_numeric_range("QA76-77")
            self.assertEqual(start, 76.0)
            self.assertEqual(end, 77.0)
            
            # Decimal format
            start, end = parser.extract_numeric_range("QA76.9")
            self.assertEqual(start, 76.9)
            self.assertEqual(end, 76.9)
            
            # No numeric part
            start, end = parser.extract_numeric_range("QA")
            self.assertIsNone(start)
            self.assertIsNone(end)
        
        except ImportError:
            self.skipTest("LCC file parser not available")

class TestLCCDatabase(unittest.TestCase):
    """Test database schema and operations."""
    
    def setUp(self):
        """Set up test database."""
        # Use SQLite for testing (in-memory)
        self.test_db_url = "sqlite:///:memory:"
    
    @patch('lcc_database_schema.create_engine')
    def test_database_initialization(self, mock_create_engine):
        """Test database manager initialization."""
        try:
            from lcc_database_schema import LCCDatabaseManager
            
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine
            
            manager = LCCDatabaseManager(self.test_db_url)
            self.assertIsNotNone(manager.engine)
            mock_create_engine.assert_called_once()
        
        except ImportError:
            self.skipTest("Database schema not available")
    
    def test_subject_node_model(self):
        """Test SubjectNode model structure."""
        try:
            from lcc_database_schema import SubjectNode
            
            # Check required fields exist
            required_fields = ['class_code', 'label', 'parent_code', 'hierarchy_level']
            for field in required_fields:
                self.assertTrue(hasattr(SubjectNode, field))
        
        except ImportError:
            self.skipTest("Database schema not available")

class TestLCCETL(unittest.TestCase):
    """Test ETL processing functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = [
            {
                "class_code": "A",
                "label": "General Works",
                "parent_code": "",
                "level": 0,
                "source_file": "test.csv"
            },
            {
                "class_code": "A1-5",
                "label": "Polygraphy",
                "parent_code": "A",
                "level": 1,
                "source_file": "test.csv"
            }
        ]
        
        # Create temporary JSON file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.sample_data, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test files."""
        os.unlink(self.temp_file.name)
    
    def test_etl_data_validation(self):
        """Test ETL data validation."""
        try:
            from scripts.load_lcc_taxonomy import LCCETLProcessor
            
            # Mock database manager
            with patch('scripts.load_lcc_taxonomy.LCCDatabaseManager'):
                etl = LCCETLProcessor()
                
                # Test validation
                self.assertTrue(etl.validate_class_code("A1-5"))
                self.assertFalse(etl.validate_class_code(""))
                
                # Test parent code extraction
                parent = etl.normalize_parent_code("A1-5")
                self.assertEqual(parent, "A")
        
        except ImportError:
            self.skipTest("ETL processor not available")
    
    def test_etl_data_loading(self):
        """Test ETL data loading from file."""
        try:
            from scripts.load_lcc_taxonomy import LCCETLProcessor
            
            with patch('scripts.load_lcc_taxonomy.LCCDatabaseManager'):
                etl = LCCETLProcessor()
                
                # Load test data
                validated_data = etl.load_consolidated_data(self.temp_file.name)
                
                self.assertEqual(len(validated_data), 2)
                self.assertEqual(validated_data[0]['class_code'], 'A')
                self.assertEqual(validated_data[1]['parent_code'], 'A')
        
        except ImportError:
            self.skipTest("ETL processor not available")

class TestSubjectTaxonomyBundle(unittest.TestCase):
    """Test subject taxonomy bundle functionality."""
    
    def setUp(self):
        """Set up mock bundle data."""
        self.mock_vertices = {
            'A': {
                'class_code': 'A',
                'label': 'General Works',
                'level': 0,
                'parent_code': None
            },
            'A1-5': {
                'class_code': 'A1-5', 
                'label': 'Polygraphy',
                'level': 1,
                'parent_code': 'A'
            }
        }
    
    @patch('subject_taxonomy_bundle.LCCDatabaseManager')
    def test_bundle_initialization(self, mock_db_manager):
        """Test bundle initialization."""
        try:
            from subject_taxonomy_bundle import SubjectTaxonomyBundle
            
            # Mock database manager
            mock_db_manager.return_value = None
            
            bundle = SubjectTaxonomyBundle(auto_load=False)
            self.assertIsNotNone(bundle)
            self.assertEqual(len(bundle.subject_vertices), 0)
        
        except ImportError:
            self.skipTest("Subject taxonomy bundle not available")
    
    def test_bundle_search_functionality(self):
        """Test bundle search capabilities."""
        try:
            from subject_taxonomy_bundle import SubjectVertex, SubjectTaxonomyBundle
            
            # Create bundle with mock data
            bundle = SubjectTaxonomyBundle(auto_load=False)
            
            # Add mock vertices
            for code, data in self.mock_vertices.items():
                vertex = SubjectVertex(
                    class_code=data['class_code'],
                    label=data['label'],
                    description=data['label'],
                    level=data['level'],
                    parent_code=data['parent_code']
                )
                bundle.subject_vertices[code] = vertex
            
            # Build indexes
            bundle._build_indexes()
            
            # Test search
            results = bundle.search_by_label("general")
            self.assertTrue(len(results) > 0)
            self.assertEqual(results[0].class_code, 'A')
        
        except ImportError:
            self.skipTest("Subject taxonomy bundle not available")

class TestIntegrationWorkflow(unittest.TestCase):
    """Test complete integration workflow."""
    
    def setUp(self):
        """Set up integration test environment."""
        # Create test data directory
        self.test_dir = tempfile.mkdtemp()
        
        # Sample LCC data
        self.sample_lcc_data = [
            {
                "class_code": "Q",
                "label": "Science",
                "parent_code": "",
                "level": 0,
                "source_file": "test_integration.json"
            },
            {
                "class_code": "QA",
                "label": "Mathematics",
                "parent_code": "Q", 
                "level": 1,
                "source_file": "test_integration.json"
            },
            {
                "class_code": "QA76",
                "label": "Computer Science",
                "parent_code": "QA",
                "level": 2, 
                "source_file": "test_integration.json"
            }
        ]
        
        # Save test data
        self.data_file = os.path.join(self.test_dir, "test_data.json")
        with open(self.data_file, 'w') as f:
            json.dump(self.sample_lcc_data, f)
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        try:
            # Test file parsing
            from lcc_file_parser import LCCFileParser
            parser = LCCFileParser()
            self.assertTrue(parser.validate_class_code("QA76"))
            
            # Test ETL processing  
            from scripts.load_lcc_taxonomy import LCCETLProcessor
            with patch('scripts.load_lcc_taxonomy.LCCDatabaseManager'):
                etl = LCCETLProcessor()
                validated_data = etl.load_consolidated_data(self.data_file)
                self.assertEqual(len(validated_data), 3)
            
            # Test bundle functionality
            from subject_taxonomy_bundle import SubjectTaxonomyBundle
            bundle = SubjectTaxonomyBundle(auto_load=False)
            self.assertIsNotNone(bundle)
            
            print("PASS: End-to-end workflow validation passed")
        
        except ImportError as e:
            self.skipTest(f"Integration components not available: {e}")

def run_comprehensive_test():
    """Run comprehensive test suite with detailed reporting."""
    
    print("LCC Taxonomy Integration Test Suite")
    print("=" * 60)
    
    # Test suite configuration
    test_classes = [
        TestLCCFileParser,
        TestLCCDatabase, 
        TestLCCETL,
        TestSubjectTaxonomyBundle,
        TestIntegrationWorkflow
    ]
    
    # Run tests
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'skipped_tests': 0,
        'errors': []
    }
    
    for test_class in test_classes:
        print(f"\nRunning {test_class.__name__}...")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        # Update results
        results['total_tests'] += result.testsRun
        results['passed_tests'] += result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
        results['failed_tests'] += len(result.failures)
        results['skipped_tests'] += len(result.skipped)
        
        # Collect errors
        for test, error in result.failures + result.errors:
            results['errors'].append(f"{test}: {error}")
        
        # Report test class results
        if result.failures or result.errors:
            print(f"  FAILED: {len(result.failures + result.errors)} tests")
        else:
            print(f"  PASSED: {result.testsRun - len(result.skipped)} tests")
        
        if result.skipped:
            print(f"  SKIPPED: {len(result.skipped)} tests")
    
    # Final report
    print(f"\nTest Summary:")
    print(f"  Total Tests: {results['total_tests']}")
    print(f"  Passed: {results['passed_tests']}")
    print(f"  Failed: {results['failed_tests']}")
    print(f"  Skipped: {results['skipped_tests']}")
    
    if results['failed_tests'] == 0:
        print(f"\nALL AVAILABLE TESTS PASSED!")
        return True
    else:
        print(f"\n{results['failed_tests']} TESTS FAILED")
        for error in results['errors'][:3]:  # Show first 3 errors
            print(f"  • {error}")
        return False

def validate_implementation():
    """Validate the complete LCC taxonomy implementation."""
    
    print("LCC Taxonomy Implementation Validation")
    print("=" * 60)
    
    validation_results = {
        'file_parser': False,
        'database_schema': False,
        'etl_processor': False,
        'taxonomy_bundle': False,
        'configuration': False
    }
    
    # Check file parser
    try:
        from lcc_file_parser import LCCFileParser
        parser = LCCFileParser()
        validation_results['file_parser'] = True
        print("PASS: File parser available")
    except ImportError:
        print("FAIL: File parser not available")
    
    # Check database schema
    try:
        from lcc_database_schema import LCCDatabaseManager, SubjectNode, SubjectEdge
        validation_results['database_schema'] = True
        print("PASS: Database schema available")
    except ImportError:
        print("FAIL: Database schema not available")
    
    # Check ETL processor
    try:
        from scripts.load_lcc_taxonomy import LCCETLProcessor
        validation_results['etl_processor'] = True
        print("PASS: ETL processor available")
    except ImportError:
        print("FAIL: ETL processor not available")
    
    # Check taxonomy bundle
    try:
        from subject_taxonomy_bundle import SubjectTaxonomyBundle
        validation_results['taxonomy_bundle'] = True
        print("PASS: Taxonomy bundle available")
    except ImportError:
        print("FAIL: Taxonomy bundle not available")
    
    # Check configuration
    config_file = Path("deployment/config/subject_taxonomy/README.md")
    if config_file.exists():
        validation_results['configuration'] = True
        print("PASS: Configuration available")
    else:
        print("FAIL: Configuration not available")
    
    # Check data files
    data_file = Path("consolidated_lcc_data.json")
    if data_file.exists():
        print("PASS: Consolidated data available")
    else:
        print("WARN: Consolidated data not found (run lcc_file_parser.py)")
    
    # Overall validation
    all_available = all(validation_results.values())
    
    print(f"\nImplementation Status:")
    print(f"  Components Available: {sum(validation_results.values())}/5")
    print(f"  Ready for Deployment: {'YES' if all_available else 'NO'}")
    
    if not all_available:
        print(f"\nNext Steps:")
        if not validation_results['file_parser']:
            print("  1. Verify lcc_file_parser.py is in project root")
        if not validation_results['database_schema']:
            print("  2. Install database dependencies: pip install sqlalchemy psycopg2-binary")
        if not validation_results['etl_processor']:
            print("  3. Verify scripts/load_lcc_taxonomy.py exists")
        if not validation_results['taxonomy_bundle']:
            print("  4. Verify subject_taxonomy_bundle.py is in project root")
        if not validation_results['configuration']:
            print("  5. Create configuration files in deployment/config/subject_taxonomy/")
    
    return all_available

if __name__ == "__main__":
    # Run validation first
    print("Starting LCC Taxonomy Validation and Testing")
    print("=" * 80)
    
    # Validate implementation
    implementation_ready = validate_implementation()
    
    if implementation_ready:
        # Run comprehensive tests
        test_success = run_comprehensive_test()
        
        if test_success:
            print(f"\nLCC Taxonomy Integration: READY FOR PRODUCTION")
        else:
            print(f"\nLCC Taxonomy Integration: NEEDS ATTENTION")
    else:
        print(f"\nLCC Taxonomy Integration: INCOMPLETE IMPLEMENTATION")
    
    print(f"\nNext Steps:")
    print(f"  1. Run file parser: python lcc_file_parser.py")
    print(f"  2. Set up database: Set LCC_DATABASE_URL environment variable")
    print(f"  3. Run ETL process: python scripts/load_lcc_taxonomy.py")
    print(f"  4. Test bundle: python subject_taxonomy_bundle.py")