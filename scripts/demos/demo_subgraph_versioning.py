"""
Demo: SubjectConcept Versioning System

Demonstrates version tracking and dependency management for knowledge subgraphs.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv
from neo4j import GraphDatabase
from scripts.system.subgraph_version_manager import SubgraphVersionManager

load_dotenv()


def demo():
    """Run versioning demo."""
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    manager = SubgraphVersionManager(driver)
    
    print("\n" + "="*70)
    print("  SUBGRAPH VERSIONING DEMO")
    print("  Chrystallum as 'GitHub for Knowledge Graphs'")
    print("="*70)
    
    try:
        # ============================================
        # 1. Initialize MILITARY_THEORY version
        # ============================================
        
        print("\n[1] Initializing MILITARY_THEORY v1.0.0...\n")
        
        result = manager.initialize_version(
            'military_theory',
            version='1.0.0',
            description='Boyd OODA principles with SPO structure'
        )
        
        print(f"    [OK] {result['subject_id']} initialized at v{result['version']}")
        
        # ============================================
        # 2. Create roman_republic SubjectConcept (if needed)
        # ============================================
        
        print("\n[2] Ensuring roman_republic SubjectConcept exists...\n")
        
        with driver.session() as session:
            session.run("""
                MERGE (sc:SubjectConcept {subject_id: 'roman_republic'})
                SET sc.label = 'Roman Republic',
                    sc.scope = 'historical',
                    sc.period = '509-27 BCE'
            """)
        
        print("    [OK] roman_republic SubjectConcept ready")
        
        # Initialize its version
        result = manager.initialize_version(
            'roman_republic',
            version='0.1.0',
            description='Roman Republic historical graph (early stage)'
        )
        
        print(f"    [OK] {result['subject_id']} initialized at v{result['version']}")
        
        # ============================================
        # 3. Declare Dependency
        # ============================================
        
        print("\n[3] Declaring dependency: roman_republic depends on military_theory...\n")
        
        result = manager.add_dependency(
            dependent_id='roman_republic',
            dependency_id='military_theory',
            version_spec='^1.0.0',  # Compatible with 1.x
            pinned=False
        )
        
        print(f"    [OK] {result['dependent']} depends on {result['dependency']}")
        print(f"    Version spec: {result['version_spec']}")
        print(f"    Pinned: {result['pinned']}")
        
        # ============================================
        # 4. Show Dependencies
        # ============================================
        
        print("\n[4] Dependencies for roman_republic:\n")
        
        deps = manager.get_dependencies('roman_republic')
        for dep in deps:
            print(f"    - {dep['dependency']} ({dep['dep_label']})")
            print(f"      Version: {dep['dep_version']}")
            print(f"      Spec: {dep['version_spec']}")
            print()
        
        # ============================================
        # 5. Simulate Version Update (Minor)
        # ============================================
        
        print("[5] Simulating update: Adding Clausewitz to MILITARY_THEORY...\n")
        
        # Check compatibility first
        compat = manager.check_compatibility('military_theory', '1.1.0')
        print(f"    Compatibility check for v1.1.0:")
        print(f"      Dependents: {compat['dependents_count']}")
        print(f"      Breaking changes: {compat['breaking_changes']}")
        
        if compat['breaking_changes'] == 0:
            print(f"      [OK] Safe to update (minor bump)\n")
            
            # Bump version
            result = manager.bump_version(
                'military_theory',
                bump_type='minor',
                changes=[
                    'Added Clausewitz friction principle',
                    'Added Clausewitz trinity concept',
                    'Enhanced SPO structure'
                ],
                description='Added Clausewitz principles'
            )
            
            print(f"    [OK] Updated: {result['old_version']} -> {result['new_version']}")
            print(f"    Bump type: {result['bump_type']}")
            print(f"    Changes:")
            for change in result['changes']:
                print(f"      - {change}")
        
        # ============================================
        # 6. Simulate Breaking Change (Major)
        # ============================================
        
        print("\n\n[6] Simulating BREAKING update (major bump)...\n")
        
        compat = manager.check_compatibility('military_theory', '2.0.0')
        print(f"    Compatibility check for v2.0.0:")
        print(f"      Dependents: {compat['dependents_count']}")
        print(f"      Breaking changes: {compat['breaking_changes']}")
        
        if compat['breaking_changes'] > 0:
            print(f"      [!] BREAKING: Would affect {compat['breaking_changes']} dependent(s)")
            for issue in compat['issues']:
                if issue.get('breaking'):
                    print(f"      - {issue['dependent']}: {issue['issue']}")
            print(f"\n      User would need to:")
            print(f"        1. Review changes")
            print(f"        2. Update roman_republic code if needed")
            print(f"        3. Update version spec to ^2.0.0")
        
        # ============================================
        # 7. Version History
        # ============================================
        
        print("\n\n[7] Version history for MILITARY_THEORY:\n")
        
        history = manager.get_version_history('military_theory')
        for v in history:
            print(f"    v{v['version']} - {v['description']}")
            print(f"      Created: {v['created_at']}")
            if v.get('changes'):
                print(f"      Changes:")
                for change in v['changes']:
                    print(f"        - {change}")
            print()
        
        # ============================================
        # 8. Dependency Graph
        # ============================================
        
        print("[8] Query to visualize dependency graph:\n")
        print("    MATCH (sc1:SubjectConcept)")
        print("          -[d:DEPENDS_ON]->")
        print("          (sc2:SubjectConcept)")
        print("    RETURN sc1, d, sc2")
        
        print("\n" + "="*70)
        print("  VERSIONING SYSTEM OPERATIONAL")
        print("  Chrystallum now tracks subgraph versions and dependencies!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.close()


if __name__ == "__main__":
    demo()
