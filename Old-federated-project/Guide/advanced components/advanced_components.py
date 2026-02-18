"""
Advanced Components: Pattern Recognition, Clustering, and Recommendation Engine
Implements components 7, 8, 9, 11 from the mathematical specification
"""

from core_base import *
from typing import Protocol, runtime_checkable
from collections import defaultdict
import re
import json


@runtime_checkable
class PatternMatcher(Protocol):
    """Protocol for pattern matching implementations"""
    def match(self, graph: TemporalGraph, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find patterns in the graph matching the query"""
        ...


class TemporalPatternEngine:
    """Implements Pattern(V, E, time, spatial, social, query) → Annotations"""
    
    def __init__(self):
        self.pattern_matchers: Dict[str, PatternMatcher] = {}
        self.cached_patterns: Dict[str, List[Dict[str, Any]]] = {}
    
    def register_pattern_matcher(self, pattern_type: str, matcher: PatternMatcher):
        """Register a pattern matcher for specific pattern types"""
        self.pattern_matchers[pattern_type] = matcher
    
    def find_patterns(self, graph: TemporalGraph, 
                     time_window: Optional[Tuple[float, float]] = None,
                     spatial_bounds: Optional[Dict[str, Any]] = None,
                     social_context: Optional[List[str]] = None,
                     query: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find patterns across temporal, spatial, and social dimensions
        """
        patterns = defaultdict(list)
        
        # Filter graph elements by time window
        filtered_nodes = self._filter_by_time(list(graph.nodes.values()), time_window)
        filtered_edges = self._filter_by_time(list(graph.edges.values()), time_window)
        
        # Apply each registered pattern matcher
        for pattern_type, matcher in self.pattern_matchers.items():
            try:
                # Create context for this pattern search
                pattern_query = {
                    'nodes': filtered_nodes,
                    'edges': filtered_edges,
                    'spatial_bounds': spatial_bounds,
                    'social_context': social_context,
                    'user_query': query or {}
                }
                
                matches = matcher.match(graph, pattern_query)
                patterns[pattern_type].extend(matches)
            except Exception as e:
                print(f"Error in pattern matcher {pattern_type}: {e}")
        
        return dict(patterns)
    
    def _filter_by_time(self, elements: List[Union[GraphNode, GraphEdge]], 
                       time_window: Optional[Tuple[float, float]]) -> List[Union[GraphNode, GraphEdge]]:
        """Filter elements by time window"""
        if not time_window:
            return elements
        
        start_time, end_time = time_window
        return [e for e in elements if start_time <= e.timestamp <= end_time]


class GraphClustering:
    """Implements C = Cluster(V, E, features) → {c_1, ..., c_m}"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
        self.feature_extractors: Dict[str, Callable] = {}
    
    def register_feature_extractor(self, name: str, extractor: Callable):
        """Register a feature extraction function"""
        self.feature_extractors[name] = extractor
    
    def cluster_nodes(self, nodes: List[GraphNode], 
                     feature_names: List[str] = None) -> List[List[GraphNode]]:
        """Cluster nodes based on specified features"""
        if not nodes:
            return []
        
        # Extract features for all nodes
        features = self._extract_features(nodes, feature_names or list(self.feature_extractors.keys()))
        
        # Simple clustering algorithm (can be replaced with more sophisticated methods)
        clusters = []
        assigned = set()
        
        for i, node in enumerate(nodes):
            if node.id in assigned:
                continue
            
            # Start new cluster with this node
            cluster = [node]
            assigned.add(node.id)
            
            # Find similar nodes
            for j, other_node in enumerate(nodes[i+1:], i+1):
                if other_node.id in assigned:
                    continue
                
                similarity = self._calculate_similarity(features[i], features[j])
                if similarity >= self.similarity_threshold:
                    cluster.append(other_node)
                    assigned.add(other_node.id)
            
            clusters.append(cluster)
        
        return clusters
    
    def _extract_features(self, nodes: List[GraphNode], feature_names: List[str]) -> List[Dict[str, Any]]:
        """Extract features from nodes"""
        features = []
        
        for node in nodes:
            node_features = {}
            for feature_name in feature_names:
                if feature_name in self.feature_extractors:
                    try:
                        node_features[feature_name] = self.feature_extractors[feature_name](node)
                    except Exception as e:
                        print(f"Error extracting feature {feature_name}: {e}")
                        node_features[feature_name] = None
            features.append(node_features)
        
        return features
    
    def _calculate_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> float:
        """Calculate similarity between two feature vectors"""
        if not features1 or not features2:
            return 0.0
        
        common_features = set(features1.keys()) & set(features2.keys())
        if not common_features:
            return 0.0
        
        similarities = []
        for feature in common_features:
            val1, val2 = features1[feature], features2[feature]
            
            if val1 is None or val2 is None:
                similarities.append(0.0)
            elif isinstance(val1, str) and isinstance(val2, str):
                # String similarity (Jaccard)
                similarities.append(self._jaccard_similarity(val1, val2))
            elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numeric similarity (inverse of normalized difference)
                max_val = max(abs(val1), abs(val2), 1)  # Avoid division by zero
                similarities.append(1.0 - abs(val1 - val2) / max_val)
            else:
                # Exact match for other types
                similarities.append(1.0 if val1 == val2 else 0.0)
        
        return sum(similarities) / len(similarities)
    
    def _jaccard_similarity(self, str1: str, str2: str) -> float:
        """Calculate Jaccard similarity between two strings"""
        words1 = set(re.findall(r'\w+', str1.lower()))
        words2 = set(re.findall(r'\w+', str2.lower()))
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)


class IngestionEngine:
    """Implements Ingest(v) → {QID(v), PropertySet(v), GeodataEdges, AuthorityIDs}"""
    
    def __init__(self):
        self.enrichment_providers: Dict[str, Callable] = {}
        self.property_extractors: Dict[str, Callable] = {}
        self.geodata_resolvers: Dict[str, Callable] = {}
    
    def register_enrichment_provider(self, provider_name: str, provider_func: Callable):
        """Register an external enrichment provider"""
        self.enrichment_providers[provider_name] = provider_func
    
    def register_property_extractor(self, property_name: str, extractor_func: Callable):
        """Register a property extraction function"""
        self.property_extractors[property_name] = extractor_func
    
    def register_geodata_resolver(self, resolver_name: str, resolver_func: Callable):
        """Register a geodata resolution function"""
        self.geodata_resolvers[resolver_name] = resolver_func
    
    def enrich_node(self, node: GraphNode) -> Dict[str, Any]:
        """
        Enrich a node with external data
        Returns: {QID(v), PropertySet(v), GeodataEdges, AuthorityIDs}
        """
        enrichment_result = {
            'qid': None,
            'properties': {},
            'geodata_edges': [],
            'authority_ids': {}
        }
        
        # Extract QID using enrichment providers
        for provider_name, provider_func in self.enrichment_providers.items():
            try:
                qid = provider_func(node)
                if qid:
                    enrichment_result['qid'] = qid
                    enrichment_result['authority_ids'][provider_name] = qid
                    break  # Use first successful QID
            except Exception as e:
                print(f"Error in enrichment provider {provider_name}: {e}")
        
        # Extract additional properties
        for property_name, extractor_func in self.property_extractors.items():
            try:
                property_value = extractor_func(node)
                if property_value is not None:
                    enrichment_result['properties'][property_name] = property_value
            except Exception as e:
                print(f"Error extracting property {property_name}: {e}")
        
        # Resolve geodata if applicable
        for resolver_name, resolver_func in self.geodata_resolvers.items():
            try:
                geodata = resolver_func(node)
                if geodata:
                    # Create geodata edges
                    for geo_item in geodata:
                        edge = GraphEdge(
                            id=f"geo_{node.id}_{len(enrichment_result['geodata_edges'])}",
                            source_id=node.id,
                            target_id=geo_item['target_id'],
                            edge_type=EdgeType.FEDERATION,
                            label=f"geodata_{resolver_name}",
                            properties=geo_item.get('properties', {})
                        )
                        enrichment_result['geodata_edges'].append(edge)
            except Exception as e:
                print(f"Error in geodata resolver {resolver_name}: {e}")
        
        return enrichment_result


class RecommendationEngine:
    """Implements S(u, G, C) → Suggestions"""
    
    def __init__(self):
        self.recommendation_strategies: Dict[str, Callable] = {}
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
    
    def register_strategy(self, strategy_name: str, strategy_func: Callable):
        """Register a recommendation strategy"""
        self.recommendation_strategies[strategy_name] = strategy_func
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]):
        """Update user profile for personalized recommendations"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        self.user_profiles[user_id].update(profile_data)
    
    def generate_suggestions(self, 
                           user_id: str,
                           graph: TemporalGraph,
                           clusters: List[List[GraphNode]] = None,
                           context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Generate personalized suggestions for a user
        S(u, G, C) → Suggestions
        """
        suggestions = []
        
        user_profile = self.user_profiles.get(user_id, {})
        
        for strategy_name, strategy_func in self.recommendation_strategies.items():
            try:
                strategy_suggestions = strategy_func(
                    user_profile=user_profile,
                    graph=graph,
                    clusters=clusters or [],
                    context=context or {}
                )
                
                # Add strategy metadata to suggestions
                for suggestion in strategy_suggestions:
                    suggestion['strategy'] = strategy_name
                    suggestion['confidence'] = suggestion.get('confidence', 0.5)
                
                suggestions.extend(strategy_suggestions)
                
            except Exception as e:
                print(f"Error in recommendation strategy {strategy_name}: {e}")
        
        # Sort by confidence score
        suggestions.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return suggestions


# Example implementations of the advanced components
class SemanticPatternMatcher:
    """Example pattern matcher for semantic relationships"""
    
    def match(self, graph: TemporalGraph, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find semantic patterns in the graph"""
        patterns = []
        nodes = query.get('nodes', [])
        edges = query.get('edges', [])
        
        # Find semantic chains (A -> B -> C relationships)
        for node in nodes:
            outgoing_edges = [e for e in edges if e.source_id == node.id and e.edge_type == EdgeType.SEMANTIC]
            
            for edge1 in outgoing_edges:
                # Look for continuation of semantic chain
                continuation_edges = [e for e in edges if e.source_id == edge1.target_id and e.edge_type == EdgeType.SEMANTIC]
                
                if continuation_edges:
                    patterns.append({
                        'pattern_type': 'semantic_chain',
                        'start_node': node.id,
                        'intermediate_node': edge1.target_id,
                        'end_nodes': [e.target_id for e in continuation_edges],
                        'chain_length': 2,
                        'confidence': 0.8
                    })
        
        return patterns


def create_advanced_demo():
    """Demonstrate advanced components"""
    print("=== Advanced Components Demo ===\n")
    
    # Create sample graph
    graph = TemporalGraph("advanced_demo")
    
    # Add nodes with varied properties
    nodes_data = [
        ("concept1", NodeType.CONCEPT, "Machine Learning", {"domain": "AI", "complexity": "high"}),
        ("concept2", NodeType.CONCEPT, "Deep Learning", {"domain": "AI", "complexity": "very_high"}),
        ("concept3", NodeType.CONCEPT, "Data Mining", {"domain": "Data Science", "complexity": "medium"}),
        ("artifact1", NodeType.ARTIFACT, "ML Model", {"type": "model", "status": "production"}),
        ("artifact2", NodeType.ARTIFACT, "Training Dataset", {"type": "data", "status": "validated"}),
    ]
    
    for node_data in nodes_data:
        node = GraphNode(*node_data)
        graph.add_node(node)
    
    # Add semantic relationships
    edges_data = [
        ("edge1", "concept2", "concept1", EdgeType.SEMANTIC, "specializes"),
        ("edge2", "artifact1", "concept1", EdgeType.SEMANTIC, "implements"),
        ("edge3", "artifact1", "artifact2", EdgeType.CAUSAL, "trained_on"),
    ]
    
    for edge_data in edges_data:
        edge = GraphEdge(*edge_data)
        graph.add_edge(edge)
    
    # Demo pattern recognition
    pattern_engine = TemporalPatternEngine()
    semantic_matcher = SemanticPatternMatcher()
    pattern_engine.register_pattern_matcher("semantic", semantic_matcher)
    
    patterns = pattern_engine.find_patterns(graph)
    print("Found patterns:", json.dumps(patterns, indent=2, default=str))
    
    # Demo clustering
    clustering = GraphClustering()
    clustering.register_feature_extractor("domain", lambda node: node.properties.get("domain"))
    clustering.register_feature_extractor("complexity", lambda node: node.properties.get("complexity"))
    
    clusters = clustering.cluster_nodes(list(graph.nodes.values()))
    print(f"\nFound {len(clusters)} clusters:")
    for i, cluster in enumerate(clusters):
        print(f"  Cluster {i}: {[node.label for node in cluster]}")
    
    # Demo recommendations
    rec_engine = RecommendationEngine()
    
    def similarity_strategy(user_profile, graph, clusters, context):
        """Simple similarity-based recommendations"""
        user_interests = user_profile.get('interests', [])
        suggestions = []
        
        for node in graph.nodes.values():
            node_domain = node.properties.get('domain', '')
            if any(interest.lower() in node_domain.lower() for interest in user_interests):
                suggestions.append({
                    'type': 'explore_node',
                    'target': node.id,
                    'reason': f"Matches interest in {node_domain}",
                    'confidence': 0.7
                })
        
        return suggestions
    
    rec_engine.register_strategy("similarity", similarity_strategy)
    rec_engine.update_user_profile("user1", {"interests": ["AI", "Machine Learning"]})
    
    suggestions = rec_engine.generate_suggestions("user1", graph, clusters)
    print(f"\nRecommendations for user1:")
    for suggestion in suggestions:
        print(f"  {suggestion['type']}: {suggestion['target']} - {suggestion['reason']}")


if __name__ == "__main__":
    create_advanced_demo()