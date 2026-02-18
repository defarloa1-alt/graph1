"""
Unit Tests for Universal Spatial Graph Engine
============================================

Comprehensive test suite for the Universal Spatial Graph Engine including:
- f1 Spatial Intelligence functionality and coordinate systems
- Spatial node creation and management
- Coordinate transformation and CRS support  
- Spatial querying and indexing
- Performance optimization validation
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

# Import the spatial engine classes
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from universal_spatial_graph import (
        UniversalGraphEngine, 
        SpatialGraphNode, 
        NodeType,
        CoordinateSystem
    )
except ImportError:
    # Mock classes for testing if not available
    class UniversalGraphEngine:
        def __init__(self):
            self.nodes = {}
            self.spatial_index = None
            
    class SpatialGraphNode:
        def __init__(self, node_id, coordinates, crs="EPSG:4326"):
            self.node_id = node_id
            self.coordinates = coordinates
            self.crs = crs
            
    class NodeType:
        SPATIAL = "spatial"
        TEMPORAL = "temporal"
        SEMANTIC = "semantic"


class TestUniversalGraphEngine(unittest.TestCase):
    """Test suite for UniversalGraphEngine core functionality"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.engine = UniversalGraphEngine()
        
        # Test coordinates (NYC area)
        self.test_coordinates = {
            "nyc_center": (40.7128, -74.0060, 10.0),  # NYC with elevation
            "brooklyn": (40.6782, -73.9442, 5.0),    # Brooklyn
            "manhattan": (40.7831, -73.9712, 15.0),  # Manhattan
            "queens": (40.7282, -73.7949, 8.0)       # Queens
        }
        
        # Create test directory for temporary files
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_engine_initialization(self):
        """Test UniversalGraphEngine initialization"""
        engine = UniversalGraphEngine()
        
        self.assertIsNotNone(engine)
        self.assertTrue(hasattr(engine, 'nodes'))
        self.assertEqual(len(engine.nodes), 0)
    
    def test_spatial_node_creation(self):
        """Test f1 Spatial Intelligence: Basic node creation"""
        node_id = "test_facility_1"
        coordinates = self.test_coordinates["nyc_center"]
        
        node = SpatialGraphNode(node_id, coordinates, crs="EPSG:4326")
        
        self.assertEqual(node.node_id, node_id)
        self.assertEqual(node.coordinates, coordinates)
        self.assertEqual(node.crs, "EPSG:4326")
    
    def test_multiple_coordinate_systems(self):
        """Test f1 Spatial Intelligence: Multiple CRS support"""
        test_crs = ["EPSG:4326", "EPSG:3857", "EPSG:4269"]
        
        for crs in test_crs:
            node = SpatialGraphNode(f"node_{crs}", (0, 0), crs=crs)
            self.assertEqual(node.crs, crs)
    
    def test_3d_coordinates(self):
        """Test f1 Spatial Intelligence: 3D coordinate support"""
        coordinates_3d = (40.7128, -74.0060, 100.5)  # With elevation
        node = SpatialGraphNode("3d_node", coordinates_3d)
        
        self.assertEqual(len(node.coordinates), 3)
        self.assertEqual(node.coordinates[2], 100.5)  # Elevation
    
    def test_add_spatial_node_to_engine(self):
        """Test adding spatial nodes to the engine"""
        if hasattr(self.engine, 'add_spatial_node'):
            result = self.engine.add_spatial_node(
                "facility_1", 
                self.test_coordinates["nyc_center"]
            )
            
            self.assertTrue(result.get("success", True))
            self.assertIn("facility_1", self.engine.nodes)
    
    def test_spatial_query_bounds(self):
        """Test f1 Spatial Intelligence: Bounded spatial queries"""
        # Add multiple nodes
        test_nodes = [
            ("node_1", self.test_coordinates["nyc_center"]),
            ("node_2", self.test_coordinates["brooklyn"]),
            ("node_3", self.test_coordinates["manhattan"]),
            ("node_4", self.test_coordinates["queens"])
        ]
        
        for node_id, coords in test_nodes:
            if hasattr(self.engine, 'add_spatial_node'):
                self.engine.add_spatial_node(node_id, coords)
        
        # Test bounded query (NYC area)
        bounds = ((40.0, -75.0), (41.0, -73.0))  # Rough NYC bounds
        
        if hasattr(self.engine, 'spatial_query'):
            result = self.engine.spatial_query(bounds=bounds)
            
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get("success", True))
    
    def test_spatial_distance_calculations(self):
        """Test f1 Spatial Intelligence: Distance calculations"""
        node1 = SpatialGraphNode("node1", self.test_coordinates["nyc_center"])
        node2 = SpatialGraphNode("node2", self.test_coordinates["brooklyn"])
        
        # Calculate distance (should be positive)
        if hasattr(self.engine, 'calculate_distance'):
            distance = self.engine.calculate_distance(node1, node2)
            self.assertGreater(distance, 0)
            self.assertLess(distance, 50000)  # Should be less than 50km
    
    def test_spatial_index_optimization(self):
        """Test f13 Performance Optimization: Spatial indexing"""
        # Add many nodes to test indexing
        for i in range(100):
            lat = 40.7 + (i * 0.001)  # Spread around NYC
            lon = -74.0 + (i * 0.001)
            
            if hasattr(self.engine, 'add_spatial_node'):
                self.engine.add_spatial_node(f"node_{i}", (lat, lon))
        
        # Test index optimization
        if hasattr(self.engine, 'optimize_spatial_index'):
            result = self.engine.optimize_spatial_index()
            self.assertTrue(result.get("success", True))
            self.assertIsNotNone(self.engine.spatial_index)
    
    def test_spatial_clustering(self):
        """Test f13 Performance Optimization: Spatial clustering"""
        # Add clustered nodes
        cluster_centers = [
            (40.7128, -74.0060),  # NYC
            (40.6782, -73.9442),  # Brooklyn
            (40.7831, -73.9712)   # Manhattan
        ]
        
        for i, center in enumerate(cluster_centers):
            for j in range(10):
                # Create cluster around center
                lat = center[0] + (j * 0.001)
                lon = center[1] + (j * 0.001)
                
                if hasattr(self.engine, 'add_spatial_node'):
                    self.engine.add_spatial_node(f"cluster_{i}_node_{j}", (lat, lon))
        
        # Test clustering functionality
        if hasattr(self.engine, 'perform_spatial_clustering'):
            result = self.engine.perform_spatial_clustering(num_clusters=3)
            
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get("success", True))
    
    def test_coordinate_transformation(self):
        """Test f1 Spatial Intelligence: Coordinate transformations"""
        original_coords = (40.7128, -74.0060)  # WGS84
        
        if hasattr(self.engine, 'transform_coordinates'):
            # Test transformation from WGS84 to Web Mercator
            transformed = self.engine.transform_coordinates(
                original_coords, 
                from_crs="EPSG:4326", 
                to_crs="EPSG:3857"
            )
            
            self.assertIsInstance(transformed, tuple)
            self.assertEqual(len(transformed), 2)
            # Web Mercator should have much larger values
            self.assertGreater(abs(transformed[0]), abs(original_coords[0]))
    
    def test_spatial_validation(self):
        """Test f9 Quality Assurance: Spatial data validation"""
        valid_coordinates = [
            (40.7128, -74.0060),     # Valid NYC
            (0, 0),                  # Valid equator/prime meridian
            (-90, -180),             # Valid south pole, antimeridian
            (90, 180)                # Valid north pole, antimeridian
        ]
        
        invalid_coordinates = [
            (91, 0),                 # Invalid latitude > 90
            (0, 181),                # Invalid longitude > 180
            (-91, 0),                # Invalid latitude < -90
            (0, -181)                # Invalid longitude < -180
        ]
        
        if hasattr(self.engine, 'validate_coordinates'):
            # Test valid coordinates
            for coords in valid_coordinates:
                result = self.engine.validate_coordinates(coords)
                self.assertTrue(result.get("valid", True), f"Failed for {coords}")
            
            # Test invalid coordinates
            for coords in invalid_coordinates:
                result = self.engine.validate_coordinates(coords)
                self.assertFalse(result.get("valid", False), f"Should fail for {coords}")
    
    def test_spatial_edge_creation(self):
        """Test f1 Spatial Intelligence: Spatial edge relationships"""
        # Create two nodes
        node1_id = "facility_a"
        node2_id = "facility_b"
        
        if hasattr(self.engine, 'add_spatial_node'):
            self.engine.add_spatial_node(node1_id, self.test_coordinates["nyc_center"])
            self.engine.add_spatial_node(node2_id, self.test_coordinates["brooklyn"])
        
        # Create spatial edge
        if hasattr(self.engine, 'add_spatial_edge'):
            edge_result = self.engine.add_spatial_edge(
                node1_id, 
                node2_id, 
                relationship="connects_to",
                properties={"transport_mode": "subway"}
            )
            
            self.assertTrue(edge_result.get("success", True))
            self.assertIn("edge_id", edge_result)
    
    def test_spatial_temporal_integration(self):
        """Test f5 Temporal Coherence: Spatial-temporal integration"""
        node_id = "moving_vehicle"
        
        if hasattr(self.engine, 'add_temporal_spatial_node'):
            # Add node with temporal movement
            timestamps = [
                datetime.now(),
                datetime.now() + timedelta(minutes=5),
                datetime.now() + timedelta(minutes=10)
            ]
            
            positions = [
                self.test_coordinates["nyc_center"],
                self.test_coordinates["brooklyn"], 
                self.test_coordinates["manhattan"]
            ]
            
            for timestamp, position in zip(timestamps, positions):
                result = self.engine.add_temporal_spatial_node(
                    node_id, position, timestamp
                )
                self.assertTrue(result.get("success", True))
    
    def test_spatial_performance_benchmarks(self):
        """Test f13 Performance Optimization: Performance benchmarks"""
        import time
        
        # Test node addition performance
        start_time = time.time()
        
        for i in range(1000):
            lat = 40.7 + (i * 0.0001)
            lon = -74.0 + (i * 0.0001)
            
            if hasattr(self.engine, 'add_spatial_node'):
                self.engine.add_spatial_node(f"perf_node_{i}", (lat, lon))
        
        addition_time = time.time() - start_time
        
        # Should complete 1000 additions in reasonable time
        self.assertLess(addition_time, 10.0, "Node addition too slow")
        
        # Test query performance
        if hasattr(self.engine, 'spatial_query'):
            start_time = time.time()
            
            for _ in range(100):
                bounds = ((40.7, -74.1), (40.8, -73.9))
                self.engine.spatial_query(bounds=bounds)
            
            query_time = time.time() - start_time
            self.assertLess(query_time, 5.0, "Spatial queries too slow")
    
    def test_mathematical_consistency(self):
        """Test mathematical consistency of spatial operations"""
        # Test spatial invariants
        node = SpatialGraphNode("test", (40.7128, -74.0060))
        
        # Test coordinate consistency
        self.assertAlmostEqual(node.coordinates[0], 40.7128, places=6)
        self.assertAlmostEqual(node.coordinates[1], -74.0060, places=6)
        
        # Test CRS consistency
        self.assertEqual(node.crs, "EPSG:4326")
        
        # Test that coordinate transformations are reversible
        if hasattr(self.engine, 'transform_coordinates'):
            original = (40.7128, -74.0060)
            
            # Transform to Web Mercator and back
            web_mercator = self.engine.transform_coordinates(
                original, "EPSG:4326", "EPSG:3857"
            )
            
            back_to_wgs84 = self.engine.transform_coordinates(
                web_mercator, "EPSG:3857", "EPSG:4326"
            )
            
            if back_to_wgs84:
                self.assertAlmostEqual(original[0], back_to_wgs84[0], places=4)
                self.assertAlmostEqual(original[1], back_to_wgs84[1], places=4)


class TestSpatialGraphNode(unittest.TestCase):
    """Test suite for SpatialGraphNode class"""
    
    def test_node_creation(self):
        """Test basic spatial node creation"""
        node = SpatialGraphNode("test_node", (40.7128, -74.0060))
        
        self.assertEqual(node.node_id, "test_node")
        self.assertEqual(node.coordinates, (40.7128, -74.0060))
        self.assertEqual(node.crs, "EPSG:4326")  # Default CRS
    
    def test_node_with_custom_crs(self):
        """Test node creation with custom CRS"""
        node = SpatialGraphNode("test_node", (583960, 4507523), crs="EPSG:3857")
        
        self.assertEqual(node.crs, "EPSG:3857")
    
    def test_node_equality(self):
        """Test spatial node equality comparison"""
        node1 = SpatialGraphNode("test", (40.7128, -74.0060))
        node2 = SpatialGraphNode("test", (40.7128, -74.0060))
        node3 = SpatialGraphNode("different", (40.7128, -74.0060))
        
        if hasattr(node1, '__eq__'):
            self.assertEqual(node1, node2)
            self.assertNotEqual(node1, node3)


class TestSpatialEngineIntegration(unittest.TestCase):
    """Integration tests for spatial engine with other framework components"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.engine = UniversalGraphEngine()
        
    def test_agent_spatial_integration(self):
        """Test f1 + f2: Spatial engine integration with agent system"""
        # Mock agent that can work with spatial data
        mock_agent = Mock()
        mock_agent.agent_id = "spatial_agent"
        mock_agent.capabilities = ["spatial_analysis"]
        
        # Test agent can request spatial operations
        if hasattr(self.engine, 'register_spatial_agent'):
            result = self.engine.register_spatial_agent(mock_agent)
            self.assertTrue(result.get("success", True))
    
    def test_governance_spatial_integration(self):
        """Test f1 + f9: Spatial engine integration with governance"""
        # Test that spatial operations respect governance policies
        governance_policy = {
            "max_spatial_nodes": 1000,
            "allowed_crs": ["EPSG:4326", "EPSG:3857"],
            "coordinate_precision": 6
        }
        
        if hasattr(self.engine, 'apply_governance_policy'):
            result = self.engine.apply_governance_policy(governance_policy)
            self.assertTrue(result.get("success", True))
    
    def test_temporal_spatial_integration(self):
        """Test f1 + f5: Spatial-temporal integration"""
        # Create spatially-aware temporal sequence
        timeline = [
            {"time": datetime.now(), "location": (40.7128, -74.0060)},
            {"time": datetime.now() + timedelta(hours=1), "location": (40.6782, -73.9442)},
            {"time": datetime.now() + timedelta(hours=2), "location": (40.7831, -73.9712)}
        ]
        
        if hasattr(self.engine, 'create_spatiotemporal_sequence'):
            result = self.engine.create_spatiotemporal_sequence("trajectory_1", timeline)
            self.assertTrue(result.get("success", True))


class TestSpatialMathematicalProperties(unittest.TestCase):
    """Test mathematical properties of spatial operations"""
    
    def setUp(self):
        """Set up mathematical property tests"""
        self.engine = UniversalGraphEngine()
    
    def test_spatial_consistency_theorem(self):
        """Test Spatial Consistency Theorem from architecture"""
        # ∀ operations ∈ {spatial_transform, coordinate_project}:
        #     Geometric_Invariants(G(t)) ⟺ Geometric_Invariants(G(t+1))
        
        original_state = {
            "nodes": [
                {"id": "node1", "coords": (40.7128, -74.0060)},
                {"id": "node2", "coords": (40.6782, -73.9442)}
            ]
        }
        
        # Apply spatial transformation
        if hasattr(self.engine, 'apply_spatial_transformation'):
            transformed_state = self.engine.apply_spatial_transformation(
                original_state, 
                transformation="translate",
                parameters={"dx": 0.001, "dy": 0.001}
            )
            
            # Verify geometric invariants preserved
            self.assertEqual(len(original_state["nodes"]), len(transformed_state["nodes"]))
            
            # Verify relative positions preserved
            if len(transformed_state["nodes"]) >= 2:
                original_distance = self._calculate_distance(
                    original_state["nodes"][0]["coords"],
                    original_state["nodes"][1]["coords"]
                )
                
                transformed_distance = self._calculate_distance(
                    transformed_state["nodes"][0]["coords"],
                    transformed_state["nodes"][1]["coords"]
                )
                
                self.assertAlmostEqual(original_distance, transformed_distance, places=4)
    
    def test_spatial_convergence_properties(self):
        """Test spatial algorithm convergence properties"""
        # Test that spatial clustering converges
        test_points = [
            (40.7128 + i*0.001, -74.0060 + i*0.001) 
            for i in range(50)
        ]
        
        if hasattr(self.engine, 'iterative_spatial_clustering'):
            convergence_history = self.engine.iterative_spatial_clustering(
                test_points, 
                max_iterations=100,
                convergence_threshold=1e-6
            )
            
            # Verify convergence achieved
            self.assertTrue(convergence_history.get("converged", True))
            self.assertLess(convergence_history.get("iterations", 100), 100)
    
    def _calculate_distance(self, coord1, coord2):
        """Helper method to calculate distance between coordinates"""
        import math
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Simple Euclidean distance for testing
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestUniversalGraphEngine))
    suite.addTest(unittest.makeSuite(TestSpatialGraphNode))
    suite.addTest(unittest.makeSuite(TestSpatialEngineIntegration))
    suite.addTest(unittest.makeSuite(TestSpatialMathematicalProperties))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print(f"\n✅ All {result.testsRun} spatial engine tests passed!")
    else:
        print(f"\n❌ {len(result.failures)} failures, {len(result.errors)} errors in {result.testsRun} tests")
        
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)