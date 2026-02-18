"""
LCC Taxonomy Database Schema
===========================

PostgreSQL schema for Library of Congress Classification taxonomy storage.
Implements multi-level star graph structure for hierarchical subject data.
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, 
    Numeric, JSON, DateTime, Boolean, Index, 
    UniqueConstraint, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os
from typing import Optional, List, Dict, Any

Base = declarative_base()

class SubjectNode(Base):
    """
    Core LCC subject classification nodes.
    Represents individual LCC class codes and their metadata.
    """
    __tablename__ = 'subject_nodes'
    
    id = Column(Integer, primary_key=True)
    class_code = Column(String(50), nullable=False, unique=True, index=True)
    label = Column(Text, nullable=False)
    parent_code = Column(String(50), index=True)  # References another class_code
    description = Column(Text)
    range_start = Column(Numeric(10, 3))
    range_end = Column(Numeric(10, 3))
    hierarchy_level = Column(Integer, default=0, index=True)
    source_file = Column(String(255))
    
    # JSON field for additional metadata
    extra = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_subject_nodes_parent_level', 'parent_code', 'hierarchy_level'),
        Index('idx_subject_nodes_code_pattern', 'class_code'),
    )
    
    def __repr__(self):
        return f"<SubjectNode(class_code='{self.class_code}', label='{self.label[:30]}...')>"

class SubjectEdge(Base):
    """
    Relationships between subject nodes.
    Supports hierarchical (broader/narrower) and lateral (related) relationships.
    """
    __tablename__ = 'subject_edges'
    
    id = Column(Integer, primary_key=True)
    parent_code = Column(String(50), nullable=False, index=True)
    child_code = Column(String(50), nullable=False, index=True)
    relationship = Column(String(20), default='broader', index=True)  # broader, narrower, related, see_also
    weight = Column(Numeric(3, 2), default=1.0)  # Relationship strength
    source = Column(String(50), default='lcc')  # Source of relationship
    
    # JSON field for relationship metadata
    extra = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('parent_code', 'child_code', 'relationship', name='uq_edge_relationship'),
        Index('idx_subject_edges_codes', 'parent_code', 'child_code'),
    )
    
    def __repr__(self):
        return f"<SubjectEdge(parent='{self.parent_code}', child='{self.child_code}', rel='{self.relationship}')>"

class SubjectTaxonomyMetadata(Base):
    """
    Metadata about the taxonomy import and versioning.
    """
    __tablename__ = 'subject_taxonomy_metadata'
    
    id = Column(Integer, primary_key=True)
    version = Column(String(20), nullable=False, unique=True)
    import_date = Column(DateTime(timezone=True), server_default=func.now())
    source_description = Column(Text)
    total_nodes = Column(Integer)
    total_edges = Column(Integer)
    import_status = Column(String(20), default='active')  # active, archived, failed
    
    # Import statistics and configuration
    import_config = Column(JSON, default=dict)
    
    def __repr__(self):
        return f"<SubjectTaxonomyMetadata(version='{self.version}', nodes={self.total_nodes})>"

class LCCDatabaseManager:
    """
    Database manager for LCC taxonomy operations.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            database_url: PostgreSQL connection string. If None, uses environment variable.
        """
        if database_url is None:
            # Default to environment variable or local development setup
            database_url = os.getenv(
                'LCC_DATABASE_URL', 
                'postgresql://postgres:password@localhost:5432/federated_graph'
            )
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)
        print("✅ LCC taxonomy tables created successfully")
    
    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        Base.metadata.drop_all(bind=self.engine)
        print("🗑️ LCC taxonomy tables dropped")
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def get_node_by_code(self, class_code: str) -> Optional[SubjectNode]:
        """Retrieve a subject node by class code."""
        with self.get_session() as session:
            return session.query(SubjectNode).filter(SubjectNode.class_code == class_code).first()
    
    def get_children(self, parent_code: str) -> List[SubjectNode]:
        """Get all direct children of a subject node."""
        with self.get_session() as session:
            return session.query(SubjectNode).filter(SubjectNode.parent_code == parent_code).all()
    
    def get_hierarchy_path(self, class_code: str) -> List[SubjectNode]:
        """Get the complete hierarchy path from root to the given node."""
        path = []
        current_code = class_code
        
        with self.get_session() as session:
            while current_code:
                node = session.query(SubjectNode).filter(SubjectNode.class_code == current_code).first()
                if node:
                    path.insert(0, node)
                    current_code = node.parent_code
                else:
                    break
        
        return path
    
    def search_nodes(self, query: str, limit: int = 20) -> List[SubjectNode]:
        """Search subject nodes by label or class code."""
        with self.get_session() as session:
            return session.query(SubjectNode).filter(
                SubjectNode.label.ilike(f'%{query}%') | 
                SubjectNode.class_code.ilike(f'%{query}%')
            ).limit(limit).all()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get taxonomy statistics."""
        with self.get_session() as session:
            stats = {
                'total_nodes': session.query(SubjectNode).count(),
                'total_edges': session.query(SubjectEdge).count(),
                'levels': {},
                'top_level_classes': []
            }
            
            # Count nodes by level
            level_counts = session.query(
                SubjectNode.hierarchy_level, 
                func.count(SubjectNode.id)
            ).group_by(SubjectNode.hierarchy_level).all()
            
            stats['levels'] = {str(level): count for level, count in level_counts}
            
            # Get top-level classes
            top_level = session.query(SubjectNode).filter(
                SubjectNode.parent_code.is_(None) | (SubjectNode.parent_code == '')
            ).limit(20).all()
            
            stats['top_level_classes'] = [
                {'code': node.class_code, 'label': node.label} 
                for node in top_level
            ]
            
            return stats

# Database schema initialization function
def init_lcc_database(database_url: Optional[str] = None, recreate: bool = False):
    """
    Initialize the LCC taxonomy database.
    
    Args:
        database_url: PostgreSQL connection string
        recreate: If True, drop and recreate all tables
    """
    manager = LCCDatabaseManager(database_url)
    
    if recreate:
        print("🔄 Recreating database tables...")
        manager.drop_tables()
    
    manager.create_tables()
    
    # Test connection
    stats = manager.get_statistics()
    print(f"📊 Database initialized. Current stats: {stats}")
    
    return manager

if __name__ == "__main__":
    # Example usage and testing
    print("🗄️ LCC Taxonomy Database Schema")
    print("=" * 50)
    
    # Initialize database (uses environment variables or defaults)
    try:
        manager = init_lcc_database(recreate=True)
        print("✅ Database schema created successfully")
        
        # Show current statistics
        stats = manager.get_statistics()
        print(f"📊 Current database statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("💡 Make sure PostgreSQL is running and connection details are correct")
        print("   Set LCC_DATABASE_URL environment variable if needed")