"""
Domain Version Manager

Version management for Domain nodes (not SubjectConcept nodes).

A Domain represents a top-level subgraph (e.g., ROMAN_REPUBLIC, MILITARY_THEORY).
SubjectConcepts and other nodes are CONTAINED within domains.

This is the correct versioning architecture per user requirement.
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


class DomainVersionManager:
    """Manages versions and dependencies for Domain subgraphs."""
    
    def __init__(self, driver):
        self.driver = driver
    
    def initialize_version(
        self,
        domain_id: str,
        version: str = "1.0.0",
        description: Optional[str] = None
    ) -> Dict:
        """
        Initialize version tracking for a Domain.
        
        Args:
            domain_id: Domain identifier (e.g., 'roman_republic')
            version: Semantic version (major.minor.patch)
            description: Version description
        
        Returns:
            Version metadata
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Domain {domain_id: $domain_id})
                SET d.version = $version,
                    d.version_created = datetime(),
                    d.schema_version = 'domain_v1',
                    d.versioned = true
                RETURN d
            """, domain_id=domain_id, version=version)
            
            record = result.single()
            if not record:
                raise ValueError(f"Domain not found: {domain_id}")
            
            # Create version node
            session.run("""
                MATCH (d:Domain {domain_id: $domain_id})
                CREATE (v:Version {
                    domain_id: $domain_id,
                    version: $version,
                    created_at: datetime(),
                    description: $description,
                    changes: []
                })
                CREATE (d)-[:HAS_VERSION]->(v)
            """, 
            domain_id=domain_id,
            version=version,
            description=description or f"Initial version of {domain_id}"
            )
            
            return {
                'domain_id': domain_id,
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
        Declare that one Domain depends on another.
        
        Args:
            dependent_id: Domain that has the dependency
            dependency_id: Domain being depended on
            version_spec: Version specification (e.g., "1.0.0", "^1.0", "*")
            pinned: If true, exact version required
        
        Returns:
            Dependency metadata
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (dependent:Domain {domain_id: $dependent_id})
                MATCH (dependency:Domain {domain_id: $dependency_id})
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
                raise ValueError(f"Domains not found")
            
            return {
                'dependent': dependent_id,
                'dependency': dependency_id,
                'version_spec': version_spec,
                'pinned': pinned
            }
    
    def bump_version(
        self,
        domain_id: str,
        bump_type: str = "patch",
        changes: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Increment version (major, minor, or patch).
        
        Args:
            domain_id: Domain to version
            bump_type: "major", "minor", or "patch"
            changes: List of changes in this version
            description: Version description
        
        Returns:
            New version metadata
        """
        with self.driver.session() as session:
            # Get current version
            result = session.run("""
                MATCH (d:Domain {domain_id: $domain_id})
                RETURN d.version as current_version
            """, domain_id=domain_id)
            
            record = result.single()
            if not record or not record['current_version']:
                raise ValueError(f"Domain not versioned: {domain_id}")
            
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
            
            # Update Domain version
            session.run("""
                MATCH (d:Domain {domain_id: $domain_id})
                SET d.version = $new_version,
                    d.version_updated = datetime()
            """, domain_id=domain_id, new_version=new_version)
            
            # Create new version node
            session.run("""
                MATCH (d:Domain {domain_id: $domain_id})
                CREATE (v:Version {
                    domain_id: $domain_id,
                    version: $new_version,
                    created_at: datetime(),
                    description: $description,
                    changes: $changes,
                    bump_type: $bump_type
                })
                CREATE (d)-[:HAS_VERSION]->(v)
            """,
            domain_id=domain_id,
            new_version=new_version,
            description=description or f"{bump_type.title()} update",
            changes=changes or [],
            bump_type=bump_type
            )
            
            return {
                'domain_id': domain_id,
                'old_version': current,
                'new_version': new_version,
                'bump_type': bump_type,
                'changes': changes or []
            }
    
    def get_dependencies(self, domain_id: str) -> List[Dict]:
        """Get all dependencies for a Domain."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Domain {domain_id: $domain_id})
                      -[dep:DEPENDS_ON]->
                      (dependency:Domain)
                RETURN 
                    dependency.domain_id as dependency,
                    dependency.label as dep_label,
                    dependency.version as dep_version,
                    dep.version_spec as version_spec,
                    dep.pinned as pinned
            """, domain_id=domain_id)
            
            return [dict(record) for record in result]
    
    def get_dependents(self, domain_id: str) -> List[Dict]:
        """Get all Domains that depend on this one."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (dependent:Domain)
                      -[dep:DEPENDS_ON]->
                      (d:Domain {domain_id: $domain_id})
                RETURN 
                    dependent.domain_id as dependent,
                    dependent.label as dep_label,
                    dependent.version as dep_version,
                    dep.version_spec as version_spec
            """, domain_id=domain_id)
            
            return [dict(record) for record in result]
    
    def get_version_history(self, domain_id: str) -> List[Dict]:
        """Get version history for a Domain."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Domain {domain_id: $domain_id})
                      -[:HAS_VERSION]->
                      (v:Version)
                RETURN 
                    v.version as version,
                    v.created_at as created_at,
                    v.description as description,
                    v.changes as changes,
                    v.bump_type as bump_type
                ORDER BY v.created_at DESC
            """, domain_id=domain_id)
            
            return [dict(record) for record in result]
    
    def check_compatibility(
        self,
        domain_id: str,
        new_version: str
    ) -> Dict:
        """Check if updating to new version would break dependents."""
        dependents = self.get_dependents(domain_id)
        
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


def create_domain_version_manager(driver=None):
    """Create DomainVersionManager instance."""
    if not driver:
        driver = GraphDatabase.driver(
            os.getenv('NEO4J_URI'),
            auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
        )
    return DomainVersionManager(driver)


if __name__ == "__main__":
    # Demo usage
    manager = create_domain_version_manager()
    
    # Domains are already created by restructure script
    print("DomainVersionManager ready")
    print("Use version CLI or API to manage domain versions")
