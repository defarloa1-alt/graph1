"""
Project-Level Debate Context Schema
===================================

Database schema for grouping debates under projects/programs.
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Numeric, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class DebateProject(Base):
    """Project/Program container for grouping related debates."""
    __tablename__ = 'debate_projects'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(50), unique=True, nullable=True)  # Human-friendly ID (e.g., "DV-001")
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sponsor = Column(String(255), nullable=True)  # Organization or person sponsoring the project
    status = Column(String(20), nullable=False, default='planned')
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    debates = relationship("Debate", back_populates="project")
    scenarios = relationship("Scenario", back_populates="project")
    subject_links = relationship("ProjectSubjectLink", back_populates="project")
    metrics = relationship("ProjectMetrics", back_populates="project", uselist=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('planned','active','on_hold','complete')", name='valid_status'),
    )
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'external_id': self.external_id,
            'name': self.name,
            'description': self.description,
            'sponsor': self.sponsor,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ProjectSubjectLink(Base):
    """Links projects to LCC subject codes for classification."""
    __tablename__ = 'project_subject_links'
    
    project_id = Column(UUID(as_uuid=True), ForeignKey('debate_projects.id'), primary_key=True)
    class_code = Column(String(50), primary_key=True)  # LCC code
    label = Column(String(500), nullable=True)  # Subject label for convenience
    relevance_score = Column(Numeric(3, 2), nullable=True)  # 0.0 - 1.0 relevance
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("DebateProject", back_populates="subject_links")
    
    def to_dict(self):
        return {
            'class_code': self.class_code,
            'label': self.label,
            'relevance_score': float(self.relevance_score) if self.relevance_score else None,
            'created_at': self.created_at.isoformat()
        }

class ProjectMetrics(Base):
    """Aggregated metrics for each project."""
    __tablename__ = 'project_metrics'
    
    project_id = Column(UUID(as_uuid=True), ForeignKey('debate_projects.id'), primary_key=True)
    debate_count = Column(Integer, default=0)
    scenario_count = Column(Integer, default=0)
    open_debates = Column(Integer, default=0)
    closed_debates = Column(Integer, default=0)
    average_consensus = Column(Numeric(4, 3), nullable=True)  # 0.000 - 1.000
    mismatch_events = Column(Integer, default=0)
    total_participants = Column(Integer, default=0)
    last_refresh = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("DebateProject", back_populates="metrics")
    
    def to_dict(self):
        return {
            'debate_count': self.debate_count,
            'scenario_count': self.scenario_count,
            'open_debates': self.open_debates,
            'closed_debates': self.closed_debates,
            'average_consensus': float(self.average_consensus) if self.average_consensus else None,
            'mismatch_events': self.mismatch_events,
            'total_participants': self.total_participants,
            'last_refresh': self.last_refresh.isoformat()
        }

# Updates to existing models (pseudocode - actual implementation would modify existing files)
"""
class Debate(Base):
    # ... existing fields ...
    project_id = Column(UUID(as_uuid=True), ForeignKey('debate_projects.id'), nullable=True)
    project = relationship("DebateProject", back_populates="debates")

class Scenario(Base):
    # ... existing fields ...
    project_id = Column(UUID(as_uuid=True), ForeignKey('debate_projects.id'), nullable=True)
    project = relationship("DebateProject", back_populates="scenarios")
"""

# Database migration script
CREATE_TABLES_SQL = """
-- Create debate_projects table
CREATE TABLE debate_projects (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id     VARCHAR(50) UNIQUE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    sponsor         VARCHAR(255),
    status          VARCHAR(20) NOT NULL DEFAULT 'planned' CHECK (status IN ('planned','active','on_hold','complete')),
    start_date      TIMESTAMP,
    end_date        TIMESTAMP,
    created_at      TIMESTAMP DEFAULT now(),
    updated_at      TIMESTAMP DEFAULT now()
);

-- Create project_subject_links table
CREATE TABLE project_subject_links (
    project_id      UUID NOT NULL REFERENCES debate_projects(id) ON DELETE CASCADE,
    class_code      VARCHAR(50) NOT NULL,
    label           VARCHAR(500),
    relevance_score NUMERIC(3, 2) CHECK (relevance_score >= 0 AND relevance_score <= 1),
    created_at      TIMESTAMP DEFAULT now(),
    PRIMARY KEY (project_id, class_code)
);

-- Create project_metrics table
CREATE TABLE project_metrics (
    project_id         UUID PRIMARY KEY REFERENCES debate_projects(id) ON DELETE CASCADE,
    debate_count       INTEGER DEFAULT 0,
    scenario_count     INTEGER DEFAULT 0,
    open_debates       INTEGER DEFAULT 0,
    closed_debates     INTEGER DEFAULT 0,
    average_consensus  NUMERIC(4, 3) CHECK (average_consensus >= 0 AND average_consensus <= 1),
    mismatch_events    INTEGER DEFAULT 0,
    total_participants INTEGER DEFAULT 0,
    last_refresh       TIMESTAMP DEFAULT now()
);

-- Add project_id to existing tables (if they exist)
-- ALTER TABLE debates ADD COLUMN project_id UUID REFERENCES debate_projects(id);
-- ALTER TABLE scenarios ADD COLUMN project_id UUID REFERENCES debate_projects(id);

-- Create indexes for performance
CREATE INDEX idx_project_status ON debate_projects(status);
CREATE INDEX idx_project_sponsor ON debate_projects(sponsor);
CREATE INDEX idx_project_subjects_code ON project_subject_links(class_code);
CREATE INDEX idx_project_metrics_refresh ON project_metrics(last_refresh);
"""

if __name__ == '__main__':
    print("Project-Level Debate Context Schema")
    print("===================================")
    print()
    print("Key entities:")
    print("- DebateProject: Container for grouping debates/scenarios")
    print("- ProjectSubjectLink: LCC subject classification for projects")
    print("- ProjectMetrics: Aggregated statistics per project")
    print()
    print("Ready for API implementation and database migration.")