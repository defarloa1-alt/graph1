"""
Enhanced Database Manager with FAST Support
==========================================

Extends the LCC database manager to handle FAST overlay data,
crosswalk mappings, and co-usage relationships.
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from sqlalchemy import create_engine, func, and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from lcc_database_schema import Base, SubjectNode, SubjectEdge, SubjectTaxonomyMetadata
from fast_database_schema import (
    FASTSubject, FASTEdge, LCCFASTCrosswalk, SubjectCoUsage, FASTFacetType
)

class EnhancedTaxonomyManager:
    """
    Enhanced database manager supporting both LCC and FAST taxonomies.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database connection with FAST support.
        
        Args:
            database_url: Database connection string. If None, uses environment variable or SQLite.
        """
        if database_url is None:
            # Check for environment variable first, fallback to SQLite for development
            database_url = os.getenv('LCC_DATABASE_URL')
            if not database_url:
                # Use SQLite for development/testing
                db_path = Path("taxonomy.db")
                database_url = f"sqlite:///{db_path.absolute()}"
                print(f"Using SQLite database: {database_url}")
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables including FAST extensions."""
        Base.metadata.create_all(bind=self.engine)
        print("✅ Enhanced taxonomy tables created successfully")
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    # ============================
    # LCC Operations (inherited)
    # ============================
    
    def get_lcc_node(self, class_code: str) -> Optional[SubjectNode]:
        """Retrieve an LCC subject node by class code."""
        with self.get_session() as session:
            return session.query(SubjectNode).filter(SubjectNode.class_code == class_code).first()
    
    def search_lcc_nodes(self, query: str, limit: int = 20) -> List[SubjectNode]:
        """Search LCC nodes by label or class code."""
        with self.get_session() as session:
            return session.query(SubjectNode).filter(
                SubjectNode.label.ilike(f'%{query}%') | 
                SubjectNode.class_code.ilike(f'%{query}%')
            ).limit(limit).all()
    
    # ============================
    # FAST Operations
    # ============================
    
    def create_fast_subject(self, fast_id: str, heading: str, facet_type: FASTFacetType, 
                           **kwargs) -> FASTSubject:
        """Create a new FAST subject."""
        with self.get_session() as session:
            fast_subject = FASTSubject(
                fast_id=fast_id,
                heading=heading,
                facet_type=facet_type,
                **kwargs
            )
            session.add(fast_subject)
            session.commit()
            session.refresh(fast_subject)
            return fast_subject
    
    def get_fast_subject(self, fast_id: str) -> Optional[FASTSubject]:
        """Retrieve a FAST subject by ID."""
        with self.get_session() as session:
            return session.query(FASTSubject).filter(FASTSubject.fast_id == fast_id).first()
    
    def search_fast_subjects(self, query: str, facet_type: Optional[FASTFacetType] = None, 
                           limit: int = 20) -> List[FASTSubject]:
        """Search FAST subjects by heading."""
        with self.get_session() as session:
            q = session.query(FASTSubject).filter(
                FASTSubject.heading.ilike(f'%{query}%')
            )
            if facet_type:
                q = q.filter(FASTSubject.facet_type == facet_type)
            return q.limit(limit).all()
    
    def get_fast_by_facet(self, facet_type: FASTFacetType, limit: int = 100) -> List[FASTSubject]:
        """Get FAST subjects by facet type."""
        with self.get_session() as session:
            return session.query(FASTSubject).filter(
                FASTSubject.facet_type == facet_type
            ).limit(limit).all()
    
    # ============================
    # Crosswalk Operations
    # ============================
    
    def create_crosswalk_mapping(self, lcc_code: str, fast_id: str, mapping_type: str,
                                confidence_level: int = 50, **kwargs) -> LCCFASTCrosswalk:
        """Create a crosswalk mapping between LCC and FAST."""
        with self.get_session() as session:
            try:
                mapping = LCCFASTCrosswalk(
                    lcc_class_code=lcc_code,
                    fast_id=fast_id,
                    mapping_type=mapping_type,
                    confidence_level=confidence_level,
                    **kwargs
                )
                session.add(mapping)
                session.commit()
                session.refresh(mapping)
                return mapping
            except IntegrityError:
                session.rollback()
                # Return existing mapping if duplicate
                return session.query(LCCFASTCrosswalk).filter(
                    and_(
                        LCCFASTCrosswalk.lcc_class_code == lcc_code,
                        LCCFASTCrosswalk.fast_id == fast_id
                    )
                ).first()
    
    def get_fast_for_lcc(self, lcc_code: str) -> List[Tuple[FASTSubject, LCCFASTCrosswalk]]:
        """Get all FAST subjects mapped to an LCC code."""
        with self.get_session() as session:
            return session.query(FASTSubject, LCCFASTCrosswalk).join(
                LCCFASTCrosswalk, FASTSubject.fast_id == LCCFASTCrosswalk.fast_id
            ).filter(LCCFASTCrosswalk.lcc_class_code == lcc_code).all()
    
    def get_lcc_for_fast(self, fast_id: str) -> List[Tuple[SubjectNode, LCCFASTCrosswalk]]:
        """Get all LCC codes mapped to a FAST subject."""
        with self.get_session() as session:
            return session.query(SubjectNode, LCCFASTCrosswalk).join(
                LCCFASTCrosswalk, SubjectNode.class_code == LCCFASTCrosswalk.lcc_class_code
            ).filter(LCCFASTCrosswalk.fast_id == fast_id).all()
    
    def get_enriched_lcc_node(self, lcc_code: str) -> Optional[Dict[str, Any]]:
        """Get LCC node with FAST enrichments."""
        lcc_node = self.get_lcc_node(lcc_code)
        if not lcc_node:
            return None
        
        # Get FAST mappings
        fast_mappings = self.get_fast_for_lcc(lcc_code)
        
        # Build enriched response
        enriched = {
            'lcc': {
                'class_code': lcc_node.class_code,
                'label': lcc_node.label,
                'description': lcc_node.description,
                'hierarchy_level': lcc_node.hierarchy_level,
                'parent_code': lcc_node.parent_code
            },
            'fast_facets': {
                'topical': [],
                'geographic': [],
                'form_genre': [],
                'personal_name': [],
                'corporate_name': [],
                'event': [],
                'chronological': [],
                'title_work': []
            },
            'mapping_metadata': []
        }
        
        # Organize FAST subjects by facet
        for fast_subject, mapping in fast_mappings:
            facet_key = fast_subject.facet_type.value
            if facet_key in enriched['fast_facets']:
                enriched['fast_facets'][facet_key].append({
                    'fast_id': fast_subject.fast_id,
                    'heading': fast_subject.heading,
                    'confidence': mapping.confidence_level,
                    'mapping_type': mapping.mapping_type
                })
                
                enriched['mapping_metadata'].append({
                    'fast_id': fast_subject.fast_id,
                    'mapping_type': mapping.mapping_type,
                    'confidence_level': mapping.confidence_level,
                    'verified': mapping.verified
                })
        
        return enriched
    
    # ============================
    # Co-usage Operations
    # ============================
    
    def create_co_usage(self, source_lcc: str, target_lcc: str, weight: int = 1,
                       analysis_source: str = 'unknown', **kwargs) -> SubjectCoUsage:
        """Create or update a co-usage relationship."""
        with self.get_session() as session:
            # Check if relationship already exists
            existing = session.query(SubjectCoUsage).filter(
                and_(
                    SubjectCoUsage.source_lcc_code == source_lcc,
                    SubjectCoUsage.target_lcc_code == target_lcc
                )
            ).first()
            
            if existing:
                # Update existing relationship
                existing.co_occurrence_count += 1
                existing.weight += weight
                existing.analysis_source = analysis_source
                session.commit()
                return existing
            else:
                # Create new relationship
                co_usage = SubjectCoUsage(
                    source_lcc_code=source_lcc,
                    target_lcc_code=target_lcc,
                    weight=weight,
                    analysis_source=analysis_source,
                    **kwargs
                )
                session.add(co_usage)
                session.commit()
                session.refresh(co_usage)
                return co_usage
    
    def get_co_usage_for_lcc(self, lcc_code: str, min_weight: int = 1) -> List[SubjectCoUsage]:
        """Get co-usage relationships for an LCC code."""
        with self.get_session() as session:
            return session.query(SubjectCoUsage).filter(
                and_(
                    or_(
                        SubjectCoUsage.source_lcc_code == lcc_code,
                        SubjectCoUsage.target_lcc_code == lcc_code
                    ),
                    SubjectCoUsage.weight >= min_weight
                )
            ).all()
    
    def get_clustering_data(self, cluster_id: Optional[str] = None) -> List[SubjectCoUsage]:
        """Get co-usage data for clustering visualization."""
        with self.get_session() as session:
            q = session.query(SubjectCoUsage)
            if cluster_id:
                q = q.filter(SubjectCoUsage.cluster_id == cluster_id)
            return q.order_by(SubjectCoUsage.weight.desc()).all()
    
    # ============================
    # Statistics and Analytics
    # ============================
    
    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Get comprehensive taxonomy statistics including FAST data."""
        with self.get_session() as session:
            stats = {
                'lcc': {
                    'total_nodes': session.query(SubjectNode).count(),
                    'total_edges': session.query(SubjectEdge).count()
                },
                'fast': {
                    'total_subjects': session.query(FASTSubject).count(),
                    'facet_counts': {},
                    'total_edges': session.query(FASTEdge).count()
                },
                'crosswalk': {
                    'total_mappings': session.query(LCCFASTCrosswalk).count(),
                    'verified_mappings': session.query(LCCFASTCrosswalk).filter(
                        LCCFASTCrosswalk.verified == True
                    ).count(),
                    'mapping_types': {}
                },
                'co_usage': {
                    'total_relationships': session.query(SubjectCoUsage).count(),
                    'sources': {}
                }
            }
            
            # FAST facet counts
            facet_counts = session.query(
                FASTSubject.facet_type, 
                func.count(FASTSubject.id)
            ).group_by(FASTSubject.facet_type).all()
            
            stats['fast']['facet_counts'] = {
                facet.value: count for facet, count in facet_counts
            }
            
            # Crosswalk mapping types
            mapping_types = session.query(
                LCCFASTCrosswalk.mapping_type,
                func.count(LCCFASTCrosswalk.id)
            ).group_by(LCCFASTCrosswalk.mapping_type).all()
            
            stats['crosswalk']['mapping_types'] = {
                mapping_type: count for mapping_type, count in mapping_types
            }
            
            # Co-usage sources
            usage_sources = session.query(
                SubjectCoUsage.analysis_source,
                func.count(SubjectCoUsage.id)
            ).group_by(SubjectCoUsage.analysis_source).all()
            
            stats['co_usage']['sources'] = {
                source: count for source, count in usage_sources
            }
            
            return stats
    
    def health_check(self) -> Dict[str, Any]:
        """Check database health and connectivity."""
        try:
            with self.get_session() as session:
                # Test basic connectivity
                session.execute("SELECT 1")
                
                # Get table row counts
                health = {
                    'status': 'healthy',
                    'tables': {
                        'subject_nodes': session.query(SubjectNode).count(),
                        'subject_edges': session.query(SubjectEdge).count(),
                        'fast_subjects': session.query(FASTSubject).count(),
                        'fast_edges': session.query(FASTEdge).count(),
                        'lcc_fast_crosswalk': session.query(LCCFASTCrosswalk).count(),
                        'subject_co_usage': session.query(SubjectCoUsage).count()
                    },
                    'database_url': self.engine.url.render_as_string(hide_password=True)
                }
                
                return health
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'database_url': self.engine.url.render_as_string(hide_password=True)
            }