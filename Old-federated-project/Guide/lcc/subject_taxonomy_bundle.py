"""
Subject Taxonomy Bundle with LCC Integration
===========================================

Enhanced SubjectTaxonomyBundle that loads LCC taxonomy data from PostgreSQL
on startup and provides graph-based subject classification capabilities.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
import networkx as nx
from datetime import datetime

# Database imports
try:
    from lcc_database_schema import LCCDatabaseManager, SubjectNode, SubjectEdge
except ImportError:
    print("⚠️ LCC database schema not available. Run ETL process first.")
    LCCDatabaseManager = None

logger = logging.getLogger(__name__)

@dataclass
class SubjectVertex:
    """Represents a subject classification vertex in the taxonomy."""
    class_code: str
    label: str
    description: str
    level: int
    parent_code: Optional[str] = None
    children_codes: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass  
class SubjectEdgeData:
    """Represents an edge between subject vertices."""
    source: str
    target: str
    relationship: str
    weight: float = 1.0
    metadata: Optional[Dict[str, Any]] = None

class SubjectTaxonomyBundle:
    """
    Enhanced subject taxonomy bundle with LCC database integration.
    
    Provides multi-level star graph structure for subject classification
    with hierarchical navigation and semantic search capabilities.
    """
    
    def __init__(self, database_url: Optional[str] = None, auto_load: bool = True):
        """
        Initialize the subject taxonomy bundle.
        
        Args:
            database_url: PostgreSQL connection string for LCC data
            auto_load: Whether to automatically load taxonomy on initialization
        """
        self.database_url = database_url
        self.db_manager = None
        
        # Core taxonomy data structures
        self.subject_vertices: Dict[str, SubjectVertex] = {}
        self.subject_edges: List[SubjectEdgeData] = []
        self.taxonomy_graph: Optional[nx.DiGraph] = None
        
        # Indexes for fast lookup
        self.vertices_by_level: Dict[int, List[str]] = {}
        self.vertices_by_parent: Dict[str, List[str]] = {}
        self.label_search_index: Dict[str, List[str]] = {}
        
        # Metadata
        self.load_timestamp: Optional[datetime] = None
        self.version: Optional[str] = None
        self.statistics: Dict[str, Any] = {}
        
        # Initialize database connection if available
        if LCCDatabaseManager and database_url:
            self.db_manager = LCCDatabaseManager(database_url)
        
        # Auto-load taxonomy data
        if auto_load:
            self.load_taxonomy()
    
    def load_taxonomy(self) -> bool:
        """
        Load subject taxonomy from database.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.db_manager:
            logger.warning("Database manager not available. Cannot load taxonomy.")
            return False
        
        try:
            logger.info("🔄 Loading LCC taxonomy from database...")
            start_time = datetime.now()
            
            # Load vertices (subject nodes)
            self._load_vertices()
            
            # Load edges (relationships)
            self._load_edges()
            
            # Build graph structure
            self._build_graph()
            
            # Create search indexes
            self._build_indexes()
            
            # Update metadata
            self.load_timestamp = datetime.now()
            self.statistics = self._calculate_statistics()
            
            duration = (self.load_timestamp - start_time).total_seconds()
            logger.info(f"✅ Taxonomy loaded successfully in {duration:.2f} seconds")
            logger.info(f"📊 Loaded {len(self.subject_vertices)} vertices, {len(self.subject_edges)} edges")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load taxonomy: {e}")
            return False
    
    def _load_vertices(self):
        """Load subject vertices from database."""
        with self.db_manager.get_session() as session:
            nodes = session.query(SubjectNode).all()
            
            for node in nodes:
                vertex = SubjectVertex(
                    class_code=node.class_code,
                    label=node.label,
                    description=node.description or node.label,
                    level=node.hierarchy_level,
                    parent_code=node.parent_code,
                    metadata={
                        'range_start': float(node.range_start) if node.range_start else None,
                        'range_end': float(node.range_end) if node.range_end else None,
                        'source_file': node.source_file,
                        'extra': node.extra or {}
                    }
                )
                
                self.subject_vertices[node.class_code] = vertex
    
    def _load_edges(self):
        """Load subject edges from database."""
        with self.db_manager.get_session() as session:
            edges = session.query(SubjectEdge).all()
            
            for edge in edges:
                edge_data = SubjectEdgeData(
                    source=edge.parent_code,
                    target=edge.child_code,
                    relationship=edge.relationship,
                    weight=float(edge.weight) if edge.weight else 1.0,
                    metadata={
                        'source': edge.source,
                        'extra': edge.extra or {}
                    }
                )
                
                self.subject_edges.append(edge_data)
    
    def _build_graph(self):
        """Build NetworkX graph from vertices and edges."""
        self.taxonomy_graph = nx.DiGraph()
        
        # Add vertices
        for code, vertex in self.subject_vertices.items():
            self.taxonomy_graph.add_node(code, **vertex.__dict__)
        
        # Add edges
        for edge in self.subject_edges:
            if edge.source in self.subject_vertices and edge.target in self.subject_vertices:
                self.taxonomy_graph.add_edge(
                    edge.source, 
                    edge.target,
                    relationship=edge.relationship,
                    weight=edge.weight,
                    **edge.metadata
                )
    
    def _build_indexes(self):
        """Build search and lookup indexes."""
        # Index by hierarchy level
        self.vertices_by_level.clear()
        for code, vertex in self.subject_vertices.items():
            level = vertex.level
            if level not in self.vertices_by_level:
                self.vertices_by_level[level] = []
            self.vertices_by_level[level].append(code)
        
        # Index by parent
        self.vertices_by_parent.clear()
        for code, vertex in self.subject_vertices.items():
            if vertex.parent_code:
                if vertex.parent_code not in self.vertices_by_parent:
                    self.vertices_by_parent[vertex.parent_code] = []
                self.vertices_by_parent[vertex.parent_code].append(code)
        
        # Build search index (simple keyword-based)
        self.label_search_index.clear()
        for code, vertex in self.subject_vertices.items():
            # Extract keywords from label
            keywords = vertex.label.lower().split()
            for keyword in keywords:
                if len(keyword) > 2:  # Skip short words
                    if keyword not in self.label_search_index:
                        self.label_search_index[keyword] = []
                    self.label_search_index[keyword].append(code)
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate taxonomy statistics."""
        stats = {
            'total_vertices': len(self.subject_vertices),
            'total_edges': len(self.subject_edges),
            'levels': len(self.vertices_by_level),
            'vertices_by_level': {
                str(level): len(codes) 
                for level, codes in self.vertices_by_level.items()
            },
            'max_level': max(self.vertices_by_level.keys()) if self.vertices_by_level else 0,
            'root_vertices': len(self.vertices_by_level.get(0, [])),
            'search_keywords': len(self.label_search_index)
        }
        
        if self.taxonomy_graph:
            stats.update({
                'graph_density': nx.density(self.taxonomy_graph),
                'is_connected': nx.is_weakly_connected(self.taxonomy_graph),
                'number_of_components': nx.number_weakly_connected_components(self.taxonomy_graph)
            })
        
        return stats
    
    def get_vertex(self, class_code: str) -> Optional[SubjectVertex]:
        """Get subject vertex by class code."""
        return self.subject_vertices.get(class_code)
    
    def get_children(self, class_code: str) -> List[SubjectVertex]:
        """Get direct children of a subject vertex."""
        child_codes = self.vertices_by_parent.get(class_code, [])
        return [self.subject_vertices[code] for code in child_codes]
    
    def get_parents(self, class_code: str) -> List[SubjectVertex]:
        """Get parent chain from root to given vertex."""
        parents = []
        current = self.subject_vertices.get(class_code)
        
        while current and current.parent_code:
            parent = self.subject_vertices.get(current.parent_code)
            if parent:
                parents.insert(0, parent)
                current = parent
            else:
                break
        
        return parents
    
    def get_descendants(self, class_code: str, max_depth: Optional[int] = None) -> List[SubjectVertex]:
        """Get all descendants of a vertex up to max_depth."""
        if not self.taxonomy_graph or class_code not in self.taxonomy_graph:
            return []
        
        descendants = []
        
        if max_depth is None:
            # Get all descendants
            desc_codes = nx.descendants(self.taxonomy_graph, class_code)
        else:
            # Get descendants up to max_depth
            desc_codes = set()
            for depth in range(1, max_depth + 1):
                nodes_at_depth = set()
                for node in nx.single_source_shortest_path_length(
                    self.taxonomy_graph, class_code, cutoff=depth
                ).keys():
                    if nx.shortest_path_length(self.taxonomy_graph, class_code, node) == depth:
                        nodes_at_depth.add(node)
                desc_codes.update(nodes_at_depth)
        
        return [self.subject_vertices[code] for code in desc_codes if code in self.subject_vertices]
    
    def search_by_label(self, query: str, limit: int = 20) -> List[SubjectVertex]:
        """Search vertices by label keywords."""
        query_words = query.lower().split()
        matching_codes = set()
        
        for word in query_words:
            # Exact keyword match
            if word in self.label_search_index:
                matching_codes.update(self.label_search_index[word])
            
            # Partial keyword match
            for keyword, codes in self.label_search_index.items():
                if word in keyword or keyword in word:
                    matching_codes.update(codes)
        
        # Score by number of matching keywords
        scored_matches = []
        for code in matching_codes:
            vertex = self.subject_vertices[code]
            score = sum(1 for word in query_words if word in vertex.label.lower())
            scored_matches.append((score, vertex))
        
        # Sort by score and return top results
        scored_matches.sort(key=lambda x: x[0], reverse=True)
        return [vertex for score, vertex in scored_matches[:limit]]
    
    def get_top_level_classes(self) -> List[SubjectVertex]:
        """Get all top-level classification vertices."""
        top_level_codes = self.vertices_by_level.get(0, [])
        return [self.subject_vertices[code] for code in top_level_codes]
    
    def get_level_vertices(self, level: int) -> List[SubjectVertex]:
        """Get all vertices at a specific hierarchy level."""
        level_codes = self.vertices_by_level.get(level, [])
        return [self.subject_vertices[code] for code in level_codes]
    
    def classify_text(self, text: str, top_k: int = 5) -> List[Tuple[SubjectVertex, float]]:
        """
        Classify text against subject taxonomy.
        
        Args:
            text: Text to classify
            top_k: Number of top classifications to return
            
        Returns:
            List of (vertex, confidence_score) tuples
        """
        # Simple keyword-based classification
        text_words = set(text.lower().split())
        
        classifications = []
        for code, vertex in self.subject_vertices.items():
            # Calculate similarity based on label overlap
            label_words = set(vertex.label.lower().split())
            overlap = len(text_words.intersection(label_words))
            
            if overlap > 0:
                # Normalize by label length (prefer more specific matches)
                confidence = overlap / len(label_words) if label_words else 0
                classifications.append((vertex, confidence))
        
        # Sort by confidence and return top-k
        classifications.sort(key=lambda x: x[1], reverse=True)
        return classifications[:top_k]
    
    def export_to_json(self) -> Dict[str, Any]:
        """Export taxonomy bundle to JSON format."""
        return {
            'metadata': {
                'version': self.version,
                'load_timestamp': self.load_timestamp.isoformat() if self.load_timestamp else None,
                'statistics': self.statistics
            },
            'vertices': {
                code: {
                    'class_code': vertex.class_code,
                    'label': vertex.label,
                    'description': vertex.description,
                    'level': vertex.level,
                    'parent_code': vertex.parent_code,
                    'metadata': vertex.metadata
                }
                for code, vertex in self.subject_vertices.items()
            },
            'edges': [
                {
                    'source': edge.source,
                    'target': edge.target,
                    'relationship': edge.relationship,
                    'weight': edge.weight,
                    'metadata': edge.metadata
                }
                for edge in self.subject_edges
            ]
        }
    
    def refresh(self) -> bool:
        """Refresh taxonomy data from database."""
        logger.info("🔄 Refreshing subject taxonomy...")
        
        # Clear existing data
        self.subject_vertices.clear()
        self.subject_edges.clear()
        self.vertices_by_level.clear()
        self.vertices_by_parent.clear()
        self.label_search_index.clear()
        
        # Reload from database
        return self.load_taxonomy()

# Factory function for easy instantiation
def create_subject_taxonomy_bundle(database_url: Optional[str] = None) -> SubjectTaxonomyBundle:
    """
    Factory function to create a subject taxonomy bundle.
    
    Args:
        database_url: PostgreSQL connection string
        
    Returns:
        Initialized SubjectTaxonomyBundle
    """
    return SubjectTaxonomyBundle(database_url=database_url)

# Integration with existing framework
class SubjectTaxonomyEngine:
    """
    Engine that integrates SubjectTaxonomyBundle with the federated graph framework.
    """
    
    def __init__(self, bundle: SubjectTaxonomyBundle):
        self.bundle = bundle
        
    def get_subject_context(self, class_codes: List[str]) -> Dict[str, Any]:
        """Get comprehensive subject context for given class codes."""
        context = {
            'primary_subjects': [],
            'related_subjects': [],
            'hierarchy_paths': [],
            'classification_confidence': {}
        }
        
        for code in class_codes:
            vertex = self.bundle.get_vertex(code)
            if vertex:
                context['primary_subjects'].append({
                    'code': code,
                    'label': vertex.label,
                    'level': vertex.level
                })
                
                # Get hierarchy path
                parents = self.bundle.get_parents(code)
                if parents:
                    path = [{'code': p.class_code, 'label': p.label} for p in parents]
                    path.append({'code': vertex.class_code, 'label': vertex.label})
                    context['hierarchy_paths'].append(path)
                
                # Get related subjects (children)
                children = self.bundle.get_children(code)
                for child in children[:5]:  # Limit to top 5
                    context['related_subjects'].append({
                        'code': child.class_code,
                        'label': child.label,
                        'relationship': 'narrower'
                    })
        
        return context

def main():
    """
    Demonstration of SubjectTaxonomyBundle functionality.
    """
    print("📚 Subject Taxonomy Bundle Demo")
    print("=" * 50)
    
    try:
        # Create bundle (will try to load from database)
        bundle = create_subject_taxonomy_bundle()
        
        if not bundle.subject_vertices:
            print("⚠️ No taxonomy data loaded. Run ETL process first:")
            print("   python scripts/load_lcc_taxonomy.py")
            return
        
        # Show statistics
        print(f"📊 Taxonomy Statistics:")
        for key, value in bundle.statistics.items():
            print(f"  {key}: {value}")
        
        # Demonstrate search functionality
        print(f"\n🔍 Search Demo:")
        search_results = bundle.search_by_label("history", limit=5)
        for i, vertex in enumerate(search_results, 1):
            print(f"  {i}. {vertex.class_code}: {vertex.label}")
        
        # Demonstrate hierarchy navigation
        if search_results:
            example_vertex = search_results[0]
            print(f"\n🌳 Hierarchy Demo for {example_vertex.class_code}:")
            
            parents = bundle.get_parents(example_vertex.class_code)
            print(f"  Parents: {[p.class_code for p in parents]}")
            
            children = bundle.get_children(example_vertex.class_code)
            print(f"  Children: {[c.class_code for c in children[:5]]}")
        
        print(f"\n✅ Subject taxonomy bundle is operational!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure database is accessible and ETL has been run")

if __name__ == "__main__":
    main()