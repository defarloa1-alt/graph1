"""
SubjectConcept Version Manager (DEPRECATED)

Use scripts.system.domain_version_manager.DomainVersionManager instead.
Domains (:Domain) are the versioned subgraph units; SubjectConcepts are
organizational topics within domains.
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


class SubgraphVersionManager:
    """Manages versions and dependencies for SubjectConcept subgraphs."""
    
    def __init__(self, driver):
        self.driver = driver
    
    def initialize_version(
        self,
        subject_id: str,
        version: str = "1.0.0",
        description: Optional[str] = None
    ) -> Dict:
        """
        Initialize version tracking for a SubjectConcept.
        
        Args:
            subject_id: SubjectConcept identifier
            version: Semantic version (major.minor.patch)
            description: Version description
        
        Returns:
            Version metadata
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: $subject_id})
                SET sc.version = $version,
                    sc.version_created = datetime(),
                    sc.schema_version = 'spo_v1',
                    sc.versioned = true
                RETURN sc
            """, subject_id=subject_id, version=version)
            
            record = result.single()
            if not record:
                raise ValueError(f"SubjectConcept not found: {subject_id}")
            
            # Create version node
            session.run("""
                MATCH (sc:SubjectConcept {subject_id: $subject_id})
                CREATE (v:Version {
                    subject_id: $subject_id,
                    version: $version,
                    created_at: datetime(),
                    description: $description,
                    changes: []
                })
                CREATE (sc)-[:HAS_VERSION]->(v)
            """, 
            subject_id=subject_id,
            version=version,
            description=description or f"Initial version of {subject_id}"
            )
            
            return {
                'subject_id': subject_id,
                'version': version,
                'status': 'initialized'
            }
    
    def add_dependency(
        self,
        dependent_id: str,
        dependency_id: str,
        version_spec: str = "*",
        pinned: bool = False
    ) -> Dict:
        """
        Declare that one SubjectConcept depends on another.
        
        Args:
            dependent_id: SubjectConcept that has the dependency
            dependency_id: SubjectConcept being depended on
            version_spec: Version specification (e.g., "1.0.0", "^1.0", "*")
            pinned: If true, exact version required
        
        Returns:
            Dependency metadata
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (dependent:SubjectConcept {subject_id: $dependent_id})
                MATCH (dependency:SubjectConcept {subject_id: $dependency_id})
                MERGE (dependent)-[d:DEPENDS_ON]->(dependency)
                SET d.version_spec = $version_spec,
                    d.pinned = $pinned,
                    d.declared_at = datetime()
                RETURN dependent, dependency, d
            """,
            dependent_id=dependent_id,
            dependency_id=dependency_id,
            version_spec=version_spec,
            pinned=pinned
            )
            
            record = result.single()
            if not record:
                raise ValueError(f"SubjectConcepts not found")
            
            return {
                'dependent': dependent_id,
                'dependency': dependency_id,
                'version_spec': version_spec,
                'pinned': pinned
            }
    
    def bump_version(
        self,
        subject_id: str,
        bump_type: str = "patch",
        changes: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Increment version (major, minor, or patch).
        
        Args:
            subject_id: SubjectConcept to version
            bump_type: "major", "minor", or "patch"
            changes: List of changes in this version
            description: Version description
        
        Returns:
            New version metadata
        """
        with self.driver.session() as session:
            # Get current version
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: $subject_id})
                RETURN sc.version as current_version
            """, subject_id=subject_id)
            
            record = result.single()
            if not record or not record['current_version']:
                raise ValueError(f"SubjectConcept not versioned: {subject_id}")
            
            # Parse and increment version
            current = record['current_version']
            major, minor, patch = map(int, current.split('.'))
            
            if bump_type == "major":
                major += 1
                minor = 0
                patch = 0
            elif bump_type == "minor":
                minor += 1
                patch = 0
            elif bump_type == "patch":
                patch += 1
            else:
                raise ValueError(f"Invalid bump_type: {bump_type}")
            
            new_version = f"{major}.{minor}.{patch}"
            
            # Update SubjectConcept version
            session.run("""
                MATCH (sc:SubjectConcept {subject_id: $subject_id})
                SET sc.version = $new_version,
                    sc.version_updated = datetime()
            """, subject_id=subject_id, new_version=new_version)
            
            # Create new version node
            session.run("""
                MATCH (sc:SubjectConcept {subject_id: $subject_id})
                CREATE (v:Version {
                    subject_id: $subject_id,
                    version: $new_version,
                    created_at: datetime(),
                    description: $description,
                    changes: $changes,
                    bump_type: $bump_type
                })
                CREATE (sc)-[:HAS_VERSION]->(v)
            """,
            subject_id=subject_id,
            new_version=new_version,
            description=description or f"{bump_type.title()} update",
            changes=changes or [],
            bump_type=bump_type
            )
            
            return {
                'subject_id': subject_id,
                'old_version': current,
                'new_version': new_version,
                'bump_type': bump_type,
                'changes': changes or []
            }
    
    def get_dependencies(self, subject_id: str) -> List[Dict]:
        """Get all dependencies for a SubjectConcept."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: $subject_id})
                      -[d:DEPENDS_ON]->
                      (dep:SubjectConcept)
                RETURN 
                    dep.subject_id as dependency,
                    dep.label as dep_label,
                    dep.version as dep_version,
                    d.version_spec as version_spec,
                    d.pinned as pinned
            """, subject_id=subject_id)
            
            return [dict(record) for record in result]
    
    def get_dependents(self, subject_id: str) -> List[Dict]:
        """Get all SubjectConcepts that depend on this one."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (dependent:SubjectConcept)
                      -[d:DEPENDS_ON]->
                      (sc:SubjectConcept {subject_id: $subject_id})
                RETURN 
                    dependent.subject_id as dependent,
                    dependent.label as dep_label,
                    dependent.version as dep_version,
                    d.version_spec as version_spec
            """, subject_id=subject_id)
            
            return [dict(record) for record in result]
    
    def get_version_history(self, subject_id: str) -> List[Dict]:
        """Get version history for a SubjectConcept."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: $subject_id})
                      -[:HAS_VERSION]->
                      (v:Version)
                RETURN 
                    v.version as version,
                    v.created_at as created_at,
                    v.description as description,
                    v.changes as changes,
                    v.bump_type as bump_type
                ORDER BY v.created_at DESC
            """, subject_id=subject_id)
            
            return [dict(record) for record in result]
    
    def check_compatibility(
        self,
        subject_id: str,
        new_version: str
    ) -> Dict:
        """
        Check if updating to new version would break dependents.
        
        Uses semantic versioning rules:
        - Major bump: breaking changes
        - Minor bump: new features, backwards compatible
        - Patch bump: bug fixes, backwards compatible
        """
        dependents = self.get_dependents(subject_id)
        
        major, minor, patch = map(int, new_version.split('.'))
        
        issues = []
        for dep in dependents:
            spec = dep['version_spec']
            
            # Check if spec allows new version
            if spec.startswith('^'):
                # Compatible with same major version
                spec_major = int(spec[1:].split('.')[0])
                if major != spec_major:
                    issues.append({
                        'dependent': dep['dependent'],
                        'issue': f"Major version bump {spec} -> {new_version}",
                        'breaking': True
                    })
            elif spec != '*':
                # Exact version required
                if spec != new_version:
                    issues.append({
                        'dependent': dep['dependent'],
                        'issue': f"Pinned to {spec}, new version {new_version}",
                        'breaking': False
                    })
        
        return {
            'new_version': new_version,
            'dependents_count': len(dependents),
            'breaking_changes': len([i for i in issues if i.get('breaking')]),
            'issues': issues
        }


def create_version_manager(driver=None):
    """Create SubgraphVersionManager instance."""
    if not driver:
        driver = GraphDatabase.driver(
            os.getenv('NEO4J_URI'),
            auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
        )
    return SubgraphVersionManager(driver)


if __name__ == "__main__":
    # Demo usage
    manager = create_version_manager()
    
    # Initialize MILITARY_THEORY version
    result = manager.initialize_version(
        'military_theory',
        version='1.0.0',
        description='Boyd principles with SPO structure'
    )
    print(f"Initialized: {result}")
    
    # Add dependency from roman_republic (if it exists)
    # This would be done when needed
