"""
FAST Database Schema Extension
=============================

Extends the LCC taxonomy schema to include FAST (Faceted Application of Subject Terminology)
overlay data and crosswalk mappings between LCC and FAST vocabularies.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    Index, ForeignKey, Enum, JSON
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from lcc_database_schema import Base

class FASTFacetType(enum.Enum):
    """FAST facet types enumeration."""
    TOPICAL = "topical"
    GEOGRAPHIC = "geographic"
    FORM_GENRE = "form_genre"
    PERSONAL_NAME = "personal_name"
    CORPORATE_NAME = "corporate_name"
    EVENT = "event"
    CHRONOLOGICAL = "chronological"
    TITLE_WORK = "title_work"

class FASTSubject(Base):
    """
    FAST (Faceted Application of Subject Terminology) subjects.
    Represents FAST headings with facet classification.
    """
    __tablename__ = 'fast_subjects'
    
    id = Column(Integer, primary_key=True)
    fast_id = Column(String(20), nullable=False, unique=True, index=True)  # e.g., "fst01234567"
    heading = Column(Text, nullable=False)
    facet_type = Column(Enum(FASTFacetType), nullable=False, index=True)
    
    # FAST-specific fields
    authority_source = Column(String(50), default='fast')
    scope_note = Column(Text)
    variant_forms = Column(JSON, default=list)  # Alternative forms/labels
    related_terms = Column(JSON, default=list)  # Related FAST IDs
    
    # Source and quality indicators
    source_heading = Column(Text)  # Original LCSH if applicable
    confidence_score = Column(Integer, default=100)  # 0-100 quality indicator
    
    # JSON field for additional FAST metadata
    extra = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_fast_subjects_facet_heading', 'facet_type', 'heading'),
        Index('idx_fast_subjects_heading_search', 'heading'),
    )

class FASTEdge(Base):
    """
    Relationships between FAST subjects (hierarchical and associative).
    """
    __tablename__ = 'fast_edges'
    
    id = Column(Integer, primary_key=True)
    source_fast_id = Column(String(20), ForeignKey('fast_subjects.fast_id'), 
                           nullable=False, index=True)
    target_fast_id = Column(String(20), ForeignKey('fast_subjects.fast_id'), 
                           nullable=False, index=True)
    
    # Relationship types
    relationship_type = Column(String(50), nullable=False, index=True)  # 'broader', 'narrower', 'related'
    strength = Column(Integer, default=1)  # Relationship strength (1-100)
    
    # Metadata
    source = Column(String(100), default='fast')
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Unique constraint to prevent duplicate edges
    __table_args__ = (
        Index('idx_fast_edges_source_target', 'source_fast_id', 'target_fast_id'),
    )

class LCCFASTCrosswalk(Base):
    """
    Crosswalk mappings between LCC class codes and FAST IDs.
    Enables bridging between the two classification systems.
    """
    __tablename__ = 'lcc_fast_crosswalk'
    
    id = Column(Integer, primary_key=True)
    lcc_class_code = Column(String(50), ForeignKey('subject_nodes.class_code'), 
                           nullable=False, index=True)
    fast_id = Column(String(20), ForeignKey('fast_subjects.fast_id'), 
                    nullable=False, index=True)
    
    # Mapping metadata
    mapping_type = Column(String(50), nullable=False, index=True)  # 'direct', 'approximate', 'manual'
    confidence_level = Column(Integer, default=50)  # 0-100 confidence in mapping
    mapping_source = Column(String(100))  # How the mapping was created
    
    # Facet-specific mapping info
    facet_relevance = Column(JSON, default=dict)  # Which facets are most relevant
    scope_notes = Column(Text)  # Human-readable mapping notes
    
    # Quality and maintenance
    verified = Column(Boolean, default=False)
    verified_by = Column(String(100))
    verified_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    lcc_node = relationship("SubjectNode", backref="fast_mappings")
    fast_subject = relationship("FASTSubject", backref="lcc_mappings")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_crosswalk_lcc_fast', 'lcc_class_code', 'fast_id'),
        Index('idx_crosswalk_mapping_type', 'mapping_type', 'confidence_level'),
    )

class SubjectCoUsage(Base):
    """
    Co-usage relationships between LCC subjects based on document analysis.
    Used for thematic clustering in GraphVisualizer.
    """
    __tablename__ = 'subject_co_usage'
    
    id = Column(Integer, primary_key=True)
    source_lcc_code = Column(String(50), ForeignKey('subject_nodes.class_code'), 
                            nullable=False, index=True)
    target_lcc_code = Column(String(50), ForeignKey('subject_nodes.class_code'), 
                            nullable=False, index=True)
    
    # Co-usage statistics
    co_occurrence_count = Column(Integer, default=1)
    documents_count = Column(Integer, default=1)  # Number of documents containing both
    weight = Column(Integer, default=1)  # Calculated weight for visualization
    
    # Source information
    analysis_source = Column(String(100))  # e.g., 'cmmi_artifacts', 'scenarios'
    analysis_method = Column(String(50))   # e.g., 'text_analysis', 'manual'
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Clustering metadata
    cluster_id = Column(String(50), index=True)  # For grouping related subjects
    cluster_strength = Column(Integer, default=50)  # 0-100 strength within cluster
    
    # JSON field for additional analysis metadata
    extra = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    source_node = relationship("SubjectNode", foreign_keys=[source_lcc_code], backref="co_usage_sources")
    target_node = relationship("SubjectNode", foreign_keys=[target_lcc_code], backref="co_usage_targets")
    
    # Indexes for performance and unique constraints
    __table_args__ = (
        Index('idx_co_usage_source_target', 'source_lcc_code', 'target_lcc_code'),
        Index('idx_co_usage_cluster', 'cluster_id', 'cluster_strength'),
        Index('idx_co_usage_weight', 'weight', 'co_occurrence_count'),
    )