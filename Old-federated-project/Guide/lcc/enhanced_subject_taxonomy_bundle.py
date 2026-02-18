"""
Enhanced Subject Taxonomy Bundle with FAST Integration
=====================================================

Extended SubjectTaxonomyBundle that provides enriched subject classification
with both LCC hierarchy and FAST faceted overlays for comprehensive
subject analysis and navigation.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
import networkx as nx
from datetime import datetime
import json

# Database imports
try:
    from enhanced_taxonomy_manager import EnhancedTaxonomyManager
    from lcc_database_schema import SubjectNode, SubjectEdge
    from fast_database_schema import FASTSubject, FASTFacetType, LCCFASTCrosswalk
    DATABASE_AVAILABLE = True
except ImportError:
    print("⚠️ Enhanced database schema not available.")
    DATABASE_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class FASTFacetData:
    """Represents FAST facet data for enrichment."""
    fast_id: str
    heading: str
    facet_type: str
    confidence_level: int
    mapping_type: str
    scope_note: Optional[str] = None
    variant_forms: List[str] = field(default_factory=list)

@dataclass
class EnrichedSubjectVertex:
    """Enhanced subject vertex with FAST facet enrichments."""
    # Core LCC data
    class_code: str
    label: str
    description: str
    level: int
    parent_code: Optional[str] = None
    children_codes: List[str] = field(default_factory=list)
    
    # FAST enrichments organized by facet
    fast_facets: Dict[str, List[FASTFacetData]] = field(default_factory=dict)
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    enrichment_timestamp: Optional[str] = None
    
    def get_primary_topics(self) -> List[FASTFacetData]:
        """Get primary topical FAST subjects."""
        return self.fast_facets.get('topical', [])
    
    def get_geographic_contexts(self) -> List[FASTFacetData]:
        """Get geographic FAST subjects."""
        return self.fast_facets.get('geographic', [])
    
    def get_form_genres(self) -> List[FASTFacetData]:
        """Get form/genre FAST subjects."""
        return self.fast_facets.get('form_genre', [])
    
    def has_fast_enrichments(self) -> bool:
        """Check if vertex has any FAST enrichments."""
        return any(self.fast_facets.values())
    
    def get_enrichment_summary(self) -> Dict[str, int]:
        """Get summary of FAST enrichments by facet."""
        return {facet: len(subjects) for facet, subjects in self.fast_facets.items() if subjects}

class EnhancedSubjectTaxonomyBundle:
    """
    Enhanced subject taxonomy bundle with FAST faceted enrichments.
    
    Provides comprehensive subject classification combining:
    - LCC hierarchical structure
    - FAST faceted vocabulary overlays
    - Advanced search and navigation
    - Graph-based analysis capabilities
    """
    
    def __init__(self, database_manager: Optional[EnhancedTaxonomyManager] = None, 
                 auto_load: bool = True):
        """
        Initialize enhanced taxonomy bundle.
        
        Args:
            database_manager: Enhanced database manager instance
            auto_load: Whether to automatically load taxonomy data on initialization
        """
        self.db_manager = database_manager or EnhancedTaxonomyManager()
        
        # Core data structures
        self.subject_vertices: Dict[str, EnrichedSubjectVertex] = {}
        self.subject_edges: Dict[str, Dict[str, Any]] = {}
        self.taxonomy_graph = nx.DiGraph()
        
        # Search and navigation indexes
        self.label_search_index: Dict[str, Set[str]] = {}
        self.fast_search_index: Dict[str, Set[str]] = {}
        self.facet_indexes: Dict[str, Dict[str, Set[str]]] = {}
        
        # Statistics and metadata
        self.load_timestamp: Optional[datetime] = None
        self.enrichment_stats: Dict[str, Any] = {}
        self.version = "2.0-enhanced"
        
        if auto_load and DATABASE_AVAILABLE:
            self.load_enhanced_taxonomy()
    
    def load_enhanced_taxonomy(self) -> Dict[str, Any]:
        """
        Load complete taxonomy with LCC hierarchy and FAST enrichments.
        
        Returns:
            Loading statistics and results
        """
        logger.info("Loading enhanced taxonomy with FAST enrichments...")
        start_time = datetime.now()
        
        try:
            # Step 1: Load LCC nodes
            lcc_stats = self._load_lcc_nodes()
            
            # Step 2: Load FAST enrichments
            fast_stats = self._load_fast_enrichments()
            
            # Step 3: Build graph structure
            graph_stats = self._build_taxonomy_graph()
            
            # Step 4: Build search indexes
            self._build_enhanced_indexes()
            
            # Calculate final statistics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.load_timestamp = end_time
            self.enrichment_stats = {
                'lcc_nodes': lcc_stats,
                'fast_enrichments': fast_stats,
                'graph_structure': graph_stats,
                'total_vertices': len(self.subject_vertices),
                'enriched_vertices': sum(1 for v in self.subject_vertices.values() if v.has_fast_enrichments()),
                'load_duration_seconds': duration,
                'load_timestamp': end_time.isoformat()
            }
            
            logger.info(f"Enhanced taxonomy loaded: {len(self.subject_vertices)} vertices, "
                       f"{self.enrichment_stats['enriched_vertices']} enriched in {duration:.2f}s")
            
            return self.enrichment_stats
            
        except Exception as e:
            logger.error(f"Failed to load enhanced taxonomy: {str(e)}")
            raise
    
    def _load_lcc_nodes(self) -> Dict[str, Any]:
        """Load LCC nodes from database."""
        logger.info("Loading LCC nodes...")
        
        with self.db_manager.get_session() as session:
            lcc_nodes = session.query(SubjectNode).all()
        
        lcc_count = 0
        for node in lcc_nodes:
            vertex = EnrichedSubjectVertex(
                class_code=node.class_code,
                label=node.label,
                description=node.description or node.label,
                level=node.hierarchy_level,
                parent_code=node.parent_code,
                metadata={
                    'source_file': node.source_file,
                    'range_start': float(node.range_start) if node.range_start else None,
                    'range_end': float(node.range_end) if node.range_end else None,
                    'extra': node.extra or {}
                }
            )
            
            self.subject_vertices[node.class_code] = vertex
            lcc_count += 1
        
        # Build parent-child relationships
        for vertex in self.subject_vertices.values():
            if vertex.parent_code and vertex.parent_code in self.subject_vertices:
                parent = self.subject_vertices[vertex.parent_code]
                parent.children_codes.append(vertex.class_code)
        
        return {'nodes_loaded': lcc_count}
    
    def _load_fast_enrichments(self) -> Dict[str, Any]:
        """Load FAST enrichments from crosswalk mappings."""
        logger.info("Loading FAST enrichments...")
        
        enrichment_count = 0
        facet_counts = {}
        
        with self.db_manager.get_session() as session:
            # Get all crosswalk mappings with FAST data
            mappings = session.query(LCCFASTCrosswalk, FASTSubject).join(
                FASTSubject, LCCFASTCrosswalk.fast_id == FASTSubject.fast_id
            ).all()
        
        for mapping, fast_subject in mappings:
            lcc_code = mapping.lcc_class_code
            
            if lcc_code not in self.subject_vertices:
                continue  # Skip if LCC node not loaded
            
            # Create FAST facet data
            facet_data = FASTFacetData(
                fast_id=fast_subject.fast_id,
                heading=fast_subject.heading,
                facet_type=fast_subject.facet_type.value,
                confidence_level=mapping.confidence_level,
                mapping_type=mapping.mapping_type,
                scope_note=fast_subject.scope_note,
                variant_forms=fast_subject.variant_forms or []
            )
            
            # Add to vertex
            vertex = self.subject_vertices[lcc_code]
            facet_type = fast_subject.facet_type.value
            
            if facet_type not in vertex.fast_facets:
                vertex.fast_facets[facet_type] = []
            
            vertex.fast_facets[facet_type].append(facet_data)
            vertex.enrichment_timestamp = datetime.now().isoformat()
            
            enrichment_count += 1
            facet_counts[facet_type] = facet_counts.get(facet_type, 0) + 1
        
        return {
            'enrichments_loaded': enrichment_count,
            'facet_distribution': facet_counts
        }
    
    def _build_taxonomy_graph(self) -> Dict[str, Any]:
        """Build NetworkX graph from taxonomy data."""
        logger.info("Building taxonomy graph...")
        
        # Add nodes
        for vertex in self.subject_vertices.values():
            self.taxonomy_graph.add_node(
                vertex.class_code,
                label=vertex.label,
                level=vertex.level,
                fast_enriched=vertex.has_fast_enrichments(),
                facet_count=len(vertex.get_enrichment_summary())
            )
        
        # Add hierarchical edges
        edge_count = 0
        for vertex in self.subject_vertices.values():
            if vertex.parent_code and vertex.parent_code in self.subject_vertices:
                self.taxonomy_graph.add_edge(
                    vertex.parent_code,
                    vertex.class_code,
                    relationship='parent-child',
                    weight=1.0
                )
                edge_count += 1
        
        return {
            'nodes': self.taxonomy_graph.number_of_nodes(),
            'edges': self.taxonomy_graph.number_of_edges(),
            'hierarchical_edges': edge_count
        }
    
    def _build_enhanced_indexes(self):
        """Build search indexes for both LCC and FAST data."""
        logger.info("Building enhanced search indexes...")
        
        # Clear existing indexes
        self.label_search_index.clear()
        self.fast_search_index.clear()
        self.facet_indexes.clear()
        
        for vertex in self.subject_vertices.values():
            # Index LCC labels
            label_words = vertex.label.lower().split()
            for word in label_words:
                if word not in self.label_search_index:
                    self.label_search_index[word] = set()
                self.label_search_index[word].add(vertex.class_code)
            
            # Index FAST headings and build facet indexes
            for facet_type, facet_subjects in vertex.fast_facets.items():
                if facet_type not in self.facet_indexes:
                    self.facet_indexes[facet_type] = {}
                
                for fast_data in facet_subjects:
                    # Index FAST headings
                    heading_words = fast_data.heading.lower().split()
                    for word in heading_words:
                        if word not in self.fast_search_index:
                            self.fast_search_index[word] = set()
                        self.fast_search_index[word].add(vertex.class_code)
                        
                        # Build facet-specific indexes
                        if word not in self.facet_indexes[facet_type]:
                            self.facet_indexes[facet_type][word] = set()
                        self.facet_indexes[facet_type][word].add(vertex.class_code)
    
    def search_enhanced(self, query: str, facet_filter: Optional[str] = None,
                       confidence_threshold: int = 0) -> List[EnrichedSubjectVertex]:
        """
        Enhanced search across both LCC and FAST data.
        
        Args:
            query: Search query
            facet_filter: Optional FAST facet type to filter by
            confidence_threshold: Minimum confidence level for FAST mappings
            
        Returns:
            List of matching enriched vertices
        """
        query_words = query.lower().split()
        matching_codes = set()
        
        # Search LCC labels
        for word in query_words:
            if word in self.label_search_index:
                matching_codes.update(self.label_search_index[word])
        
        # Search FAST headings
        if facet_filter and facet_filter in self.facet_indexes:
            # Search specific facet
            for word in query_words:
                if word in self.facet_indexes[facet_filter]:
                    matching_codes.update(self.facet_indexes[facet_filter][word])
        else:
            # Search all FAST data
            for word in query_words:
                if word in self.fast_search_index:
                    matching_codes.update(self.fast_search_index[word])
        
        # Filter by confidence threshold and return vertices
        results = []
        for code in matching_codes:
            vertex = self.subject_vertices[code]
            
            # Check confidence threshold
            if confidence_threshold > 0:
                max_confidence = 0
                for facet_subjects in vertex.fast_facets.values():
                    for fast_data in facet_subjects:
                        max_confidence = max(max_confidence, fast_data.confidence_level)
                
                if max_confidence < confidence_threshold:
                    continue
            
            results.append(vertex)
        
        # Sort by relevance (enriched vertices first, then by level)
        results.sort(key=lambda v: (not v.has_fast_enrichments(), v.level, v.class_code))
        
        return results
    
    def get_enriched_vertex(self, class_code: str) -> Optional[EnrichedSubjectVertex]:
        """Get enriched vertex by LCC class code."""
        return self.subject_vertices.get(class_code)
    
    def get_facet_suggestions(self, class_code: str, facet_type: str, limit: int = 5) -> List[FASTFacetData]:
        """
        Get FAST facet suggestions for a given LCC code.
        
        Args:
            class_code: LCC class code
            facet_type: FAST facet type
            limit: Maximum number of suggestions
            
        Returns:
            List of FAST facet data sorted by confidence
        """
        vertex = self.subject_vertices.get(class_code)
        if not vertex or facet_type not in vertex.fast_facets:
            return []
        
        # Sort by confidence level
        facet_data = vertex.fast_facets[facet_type]
        facet_data.sort(key=lambda f: f.confidence_level, reverse=True)
        
        return facet_data[:limit]
    
    def get_related_by_fast(self, class_code: str, facet_type: Optional[str] = None,
                           min_confidence: int = 70) -> List[Tuple[str, str, int]]:
        """
        Find LCC codes related through shared FAST subjects.
        
        Args:
            class_code: Source LCC class code
            facet_type: Optional facet type to filter by
            min_confidence: Minimum confidence level
            
        Returns:
            List of (related_code, shared_fast_id, confidence) tuples
        """
        source_vertex = self.subject_vertices.get(class_code)
        if not source_vertex:
            return []
        
        # Collect FAST IDs from source vertex
        source_fast_ids = set()
        for ft, facet_subjects in source_vertex.fast_facets.items():
            if facet_type is None or ft == facet_type:
                for fast_data in facet_subjects:
                    if fast_data.confidence_level >= min_confidence:
                        source_fast_ids.add(fast_data.fast_id)
        
        # Find other vertices sharing these FAST IDs
        related = []
        for other_code, other_vertex in self.subject_vertices.items():
            if other_code == class_code:
                continue
            
            for ft, facet_subjects in other_vertex.fast_facets.items():
                if facet_type is None or ft == facet_type:
                    for fast_data in facet_subjects:
                        if (fast_data.fast_id in source_fast_ids and 
                            fast_data.confidence_level >= min_confidence):
                            related.append((other_code, fast_data.fast_id, fast_data.confidence_level))
        
        # Sort by confidence
        related.sort(key=lambda x: x[2], reverse=True)
        return related
    
    def get_enrichment_statistics(self) -> Dict[str, Any]:
        """Get comprehensive enrichment statistics."""
        stats = {
            'total_vertices': len(self.subject_vertices),
            'enriched_vertices': 0,
            'facet_coverage': {},
            'confidence_distribution': {},
            'mapping_type_distribution': {},
            'top_enriched_classes': []
        }
        
        confidence_buckets = [0, 50, 70, 80, 90, 95]
        confidence_counts = {f"{confidence_buckets[i]}-{confidence_buckets[i+1]-1}": 0 
                           for i in range(len(confidence_buckets)-1)}
        confidence_counts["95-100"] = 0
        
        mapping_types = {}
        
        enriched_classes = []
        
        for vertex in self.subject_vertices.values():
            if vertex.has_fast_enrichments():
                stats['enriched_vertices'] += 1
                
                enrichment_count = sum(len(subjects) for subjects in vertex.fast_facets.values())
                enriched_classes.append((vertex.class_code, vertex.label, enrichment_count))
                
                # Count facet coverage
                for facet_type, subjects in vertex.fast_facets.items():
                    stats['facet_coverage'][facet_type] = stats['facet_coverage'].get(facet_type, 0) + len(subjects)
                    
                    # Analyze confidence and mapping types
                    for fast_data in subjects:
                        # Confidence distribution
                        confidence = fast_data.confidence_level
                        for i in range(len(confidence_buckets)-1):
                            if confidence_buckets[i] <= confidence < confidence_buckets[i+1]:
                                bucket_key = f"{confidence_buckets[i]}-{confidence_buckets[i+1]-1}"
                                confidence_counts[bucket_key] += 1
                                break
                        else:
                            if confidence >= 95:
                                confidence_counts["95-100"] += 1
                        
                        # Mapping type distribution
                        mapping_types[fast_data.mapping_type] = mapping_types.get(fast_data.mapping_type, 0) + 1
        
        stats['confidence_distribution'] = confidence_counts
        stats['mapping_type_distribution'] = mapping_types
        
        # Top enriched classes
        enriched_classes.sort(key=lambda x: x[2], reverse=True)
        stats['top_enriched_classes'] = enriched_classes[:10]
        
        return stats
    
    def export_enriched_data(self, file_path: str, include_fast_details: bool = True):
        """
        Export enriched taxonomy data to JSON file.
        
        Args:
            file_path: Path to save the JSON file
            include_fast_details: Whether to include detailed FAST data
        """
        export_data = {
            'metadata': {
                'version': self.version,
                'load_timestamp': self.load_timestamp.isoformat() if self.load_timestamp else None,
                'total_vertices': len(self.subject_vertices),
                'enrichment_stats': self.enrichment_stats
            },
            'vertices': []
        }
        
        for vertex in self.subject_vertices.values():
            vertex_data = {
                'class_code': vertex.class_code,
                'label': vertex.label,
                'description': vertex.description,
                'level': vertex.level,
                'parent_code': vertex.parent_code,
                'children_codes': vertex.children_codes,
                'has_fast_enrichments': vertex.has_fast_enrichments()
            }
            
            if include_fast_details and vertex.has_fast_enrichments():
                vertex_data['fast_facets'] = {}
                for facet_type, subjects in vertex.fast_facets.items():
                    vertex_data['fast_facets'][facet_type] = [
                        {
                            'fast_id': s.fast_id,
                            'heading': s.heading,
                            'confidence_level': s.confidence_level,
                            'mapping_type': s.mapping_type,
                            'scope_note': s.scope_note
                        } for s in subjects
                    ]
            
            export_data['vertices'].append(vertex_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported enriched taxonomy data to {file_path}")

def main():
    """Main function for testing enhanced taxonomy bundle."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Enhanced Subject Taxonomy Bundle')
    parser.add_argument('--search', help='Test search functionality')
    parser.add_argument('--export', help='Export enriched data to file')
    parser.add_argument('--stats', action='store_true', help='Show enrichment statistics')
    
    args = parser.parse_args()
    
    # Initialize enhanced bundle
    print("Initializing Enhanced Subject Taxonomy Bundle...")
    bundle = EnhancedSubjectTaxonomyBundle()
    
    if args.stats:
        # Show statistics
        stats = bundle.get_enrichment_statistics()
        print("\nEnrichment Statistics:")
        print("=" * 50)
        print(f"Total Vertices: {stats['total_vertices']}")
        print(f"Enriched Vertices: {stats['enriched_vertices']}")
        print(f"Enrichment Rate: {stats['enriched_vertices']/stats['total_vertices']*100:.1f}%")
        
        print(f"\nFacet Coverage:")
        for facet, count in stats['facet_coverage'].items():
            print(f"  {facet}: {count}")
        
        print(f"\nTop Enriched Classes:")
        for code, label, count in stats['top_enriched_classes'][:5]:
            print(f"  {code}: {label} ({count} enrichments)")
    
    if args.search:
        # Test search
        results = bundle.search_enhanced(args.search)
        print(f"\nSearch Results for '{args.search}':")
        print("=" * 50)
        for i, vertex in enumerate(results[:10], 1):
            enrichment_info = f" [+{sum(len(s) for s in vertex.fast_facets.values())} FAST]" if vertex.has_fast_enrichments() else ""
            print(f"{i}. {vertex.class_code}: {vertex.label}{enrichment_info}")
    
    if args.export:
        # Export data
        bundle.export_enriched_data(args.export)
        print(f"Exported enriched data to {args.export}")

if __name__ == "__main__":
    main()