#!/usr/bin/env python3
"""
SUBJECT CONCEPT SCHEMA LOADER
==============================

Creates SubjectConcept and SubjectConceptRegistry infrastructure in Neo4j.

Usage:
    python scripts/reference/create_subject_concept_schema.py --password <password>

Features:
    - Creates schema constraints and indexes
    - Bootstraps core SubjectConcepts (e.g., Roman Republic)
    - Creates SubjectConceptRegistry nodes
    - Provides API for agents to create new concepts with validation
    - Manages hierarchy (parent/child concepts)

"""

import sys
import argparse
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import hashlib

from neo4j import GraphDatabase, Session


class SubjectConceptLoader:
    """Loads and manages SubjectConcept schema in Neo4j"""
    
    def __init__(self, uri: str, username: str, password: str):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.session = None
    
    def close(self):
        """Close driver connection"""
        if self.session:
            self.session.close()
        self.driver.close()
    
    def _generate_canonical_subject_id(self, 
                                       wikidata_qid: str,
                                       label: str,
                                       facet: str,
                                       period_start: int = None,
                                       period_end: int = None) -> str:
        """
        Generate canonical subject_id using SHA256 hash of core properties.
        
        This ensures:
        - Same concept always gets same ID (deterministic)
        - If properties change, ID changes (reflects reality)
        - Independent of label formatting or display variations
        """
        # Build canonical tuple of properties
        canonical = f"{wikidata_qid}|{label}|{facet}|{period_start}|{period_end}"
        
        # Hash it
        hash_obj = hashlib.sha256(canonical.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()[:12]  # Use first 12 chars for readability
        
        return f"subj_{hash_hex}"
    
    def create_schema(self) -> bool:
        """Create constraints and indexes"""
        print("[1/4] Creating schema constraints and indexes...")
        
        constraints = [
            "CREATE CONSTRAINT subject_concept_id IF NOT EXISTS FOR (n:SubjectConcept) REQUIRE n.concept_id IS UNIQUE",
            "CREATE CONSTRAINT subject_concept_label_wikidata IF NOT EXISTS FOR (n:SubjectConcept) REQUIRE (n.label, n.wikidata_qid) IS UNIQUE",
            "CREATE CONSTRAINT registry_id IF NOT EXISTS FOR (n:SubjectConceptRegistry) REQUIRE n.registry_id IS UNIQUE",
            "CREATE CONSTRAINT lcc_class_code IF NOT EXISTS FOR (n:LCC_Class) REQUIRE n.code IS UNIQUE",
            "CREATE CONSTRAINT lcsh_subject_id IF NOT EXISTS FOR (n:LCSH_Subject) REQUIRE n.lcsh_id IS UNIQUE",
            "CREATE CONSTRAINT fast_subject_id IF NOT EXISTS FOR (n:FAST_Subject) REQUIRE n.fast_id IS UNIQUE",
            "CREATE CONSTRAINT claim_id IF NOT EXISTS FOR (n:Claim) REQUIRE n.claim_id IS UNIQUE",
        ]
        
        indexes = [
            "CREATE INDEX subject_concept_label IF NOT EXISTS FOR (n:SubjectConcept) ON (n.label)",
            "CREATE INDEX subject_concept_wikidata_qid IF NOT EXISTS FOR (n:SubjectConcept) ON (n.wikidata_qid)",
            "CREATE INDEX subject_concept_parent IF NOT EXISTS FOR (n:SubjectConcept) ON (n.parent_concept_id)",
            "CREATE INDEX subject_concept_source IF NOT EXISTS FOR (n:SubjectConcept) ON (n.source)",
            "CREATE INDEX subject_concept_is_agent_created IF NOT EXISTS FOR (n:SubjectConcept) ON (n.is_agent_created)",
            "CREATE INDEX subject_concept_validation_status IF NOT EXISTS FOR (n:SubjectConcept) ON (n.validation_status)",
            "CREATE INDEX claim_primary_facet IF NOT EXISTS FOR (n:Claim) ON (n.primary_facet)",
            "CREATE INDEX claim_confidence IF NOT EXISTS FOR (n:Claim) ON (n.confidence)",
            "CREATE INDEX claim_source_agent IF NOT EXISTS FOR (n:Claim) ON (n.source_agent)",
            "CREATE INDEX lcc_class_label IF NOT EXISTS FOR (n:LCC_Class) ON (n.label)",
            "CREATE INDEX lcsh_subject_heading IF NOT EXISTS FOR (n:LCSH_Subject) ON (n.heading)",
            "CREATE INDEX fast_subject_label IF NOT EXISTS FOR (n:FAST_Subject) ON (n.preferred_label)",
            "CREATE INDEX registry_parent_concept IF NOT EXISTS FOR (n:SubjectConceptRegistry) ON (n.parent_concept_id)",
            "CREATE INDEX registry_updated IF NOT EXISTS FOR (n:SubjectConceptRegistry) ON (n.last_updated)",
        ]
        
        try:
            with self.driver.session() as session:
                for constraint in constraints:
                    try:
                        session.run(constraint)
                    except Exception as e:
                        if "already exists" not in str(e):
                            print(f"  ⚠ Constraint creation warning: {e}")
                
                for index in indexes:
                    try:
                        session.run(index)
                    except Exception as e:
                        if "already exists" not in str(e):
                            print(f"  ⚠ Index creation warning: {e}")
            
            print("  ✓ Schema constraints and indexes created")
            return True
        except Exception as e:
            print(f"  ✗ Schema creation failed: {e}")
            return False
    
    def create_bootstrap_concepts(self) -> Dict[str, str]:
        """
        Create core SubjectConcepts for Phase 2A+2B.
        These are canonical concepts that entities will align with.
        
        Returns:
            Dictionary mapping concept labels to concept_ids
        """
        print("[2/4] Creating bootstrap SubjectConcepts...")
        
        bootstrap_concepts = [
            {
                "label": "Roman Republic",
                "wikidata_qid": "Q17167",
                "facet": "Political",
                "period_start": -509,
                "period_end": -27,
                "source": "Wikidata + LCC DG",
                "lcc_codes": ["DG232-DG248"],
                "lcsh_ids": ["sh85114436"],
                "fast_ids": [1352255],
                "description": "Political entity: Ancient Rome, 509 BCE to 27 BCE",
            },
            {
                "label": "Roman Empire",
                "wikidata_qid": "Q25419",
                "facet": "Political",
                "period_start": -27,
                "period_end": 476,
                "source": "Wikidata + LCC DG",
                "lcc_codes": ["DG248-DG320"],
                "lcsh_ids": ["sh85114441"],
                "fast_ids": [1353432],
                "description": "Political entity: Ancient Rome, 27 BCE to 476 CE",
            },
            {
                "label": "Punic Wars",
                "wikidata_qid": "Q3105",
                "facet": "Military",
                "period_start": -264,
                "period_end": -146,
                "parent_concept": "Roman Republic",
                "source": "Wikidata + LCC",
                "lcc_codes": ["DG249-DG260"],
                "description": "Military conflict: Rome vs Carthage",
            },
            {
                "label": "Caesar's Gallic Wars",
                "wikidata_qid": "Q181098",
                "facet": "Military",
                "period_start": -58,
                "period_end": -50,
                "parent_concept": "Roman Republic",
                "source": "Wikidata",
                "lcc_codes": ["DG261-DG268"],
                "description": "Military campaign: Julius Caesar in Gaul",
            },
            {
                "label": "Augustus",
                "wikidata_qid": "Q1405",
                "facet": "Biographical",
                "period_start": -63,
                "period_end": 14,
                "source": "Wikidata",
                "description": "Historical figure: First Roman Emperor",
            },
        ]
        
        concept_map = {}
        
        cypher = """
        MERGE (subj:SubjectConcept {
            subject_id: $subject_id
        })
        SET subj.concept_id = $concept_id,
            subj.label = $label,
            subj.facet = $facet,
            subj.wikidata_qid = $wikidata_qid,
            subj.period_start = $period_start,
            subj.period_end = $period_end,
            subj.source = $source,
            subj.description = $description,
            subj.lcc_codes = $lcc_codes,
            subj.lcsh_ids = $lcsh_ids,
            subj.fast_ids = $fast_ids,
            subj.is_canonical = true,
            subj.is_agent_created = false,
            subj.validation_status = 'approved',
            subj.creation_timestamp = $creation_timestamp,
            subj.facet_claims_count = 0,
            subj.child_concept_count = 0,
            subj.concept_depth = 0
        
        RETURN subj.concept_id AS concept_id
        """
        
        try:
            with self.driver.session() as session:
                for concept in bootstrap_concepts:
                    safe_label = concept['label'].lower().replace(' ', '_').replace("'", '')
                    
                    # Generate canonical subject_id (hash-based)
                    subject_id = self._generate_canonical_subject_id(
                        wikidata_qid=concept['wikidata_qid'],
                        label=concept['label'],
                        facet=concept['facet'],
                        period_start=concept.get('period_start'),
                        period_end=concept.get('period_end')
                    )
                    
                    # concept_id is human-readable for debugging
                    concept_id = f"subj_{safe_label}_{concept['wikidata_qid']}"
                    
                    result = session.run(
                        cypher,
                        subject_id=subject_id,
                        concept_id=concept_id,
                        label=concept["label"],
                        facet=concept["facet"],
                        wikidata_qid=concept["wikidata_qid"],
                        period_start=concept.get("period_start"),
                        period_end=concept.get("period_end"),
                        source=concept["source"],
                        description=concept.get("description", ""),
                        lcc_codes=concept.get("lcc_codes", []),
                        lcsh_ids=concept.get("lcsh_ids", []),
                        fast_ids=concept.get("fast_ids", []),
                        creation_timestamp=datetime.now().isoformat()
                    )
                    
                    returned_id = result.single()["concept_id"]
                    concept_map[concept["label"]] = returned_id
                    print(f"  ✓ Created: {concept['label']} (subject_id: {subject_id})")
                
                # Link parent-child relationships
                parent_child_pairs = [
                    ("Roman Republic", "Punic Wars"),
                    ("Roman Republic", "Caesar's Gallic Wars"),
                ]
                
                for parent_label, child_label in parent_child_pairs:
                    if parent_label in concept_map and child_label in concept_map:
                        session.run("""
                            MATCH (parent:SubjectConcept {concept_id: $parent_id})
                            MATCH (child:SubjectConcept {concept_id: $child_id})
                            MERGE (parent)-[:HAS_CHILD_CONCEPT]->(child)
                            SET child.parent_concept_id = parent.concept_id,
                                child.concept_depth = parent.concept_depth + 1,
                                parent.child_concept_count = parent.child_concept_count + 1
                        """,
                        parent_id=concept_map[parent_label],
                        child_id=concept_map[child_label]
                        )
                        print(f"  ✓ Linked: {parent_label} → {child_label}")
        
        except Exception as e:
            print(f"  ✗ Bootstrap concept creation failed: {e}")
            return {}
        
        print(f"  ✓ Created {len(concept_map)} bootstrap SubjectConcepts")
        return concept_map
    
    def create_registries(self, concept_map: Dict[str, str]) -> bool:
        """
        Create SubjectConceptRegistry nodes to govern concept creation.
        One registry per root concept.
        """
        print("[3/4] Creating SubjectConceptRegistries...")
        
        cypher = """
        // Create registry for root concept (Roman Republic)
        MERGE (registry:SubjectConceptRegistry {
            registry_id: $registry_id
        })
        SET registry.parent_concept_id = $parent_concept_id,
            registry.total_concepts = 0,
            registry.validation_threshold_confidence = 0.75,
            registry.auto_approval_confidence = 0.90,
            registry.last_updated = $last_updated,
            registry.curator = 'system_bootstrap',
            registry.concept_ids_ordered = []
        
        // Link registry to concepts
        WITH registry
        MATCH (subj:SubjectConcept)
        WHERE (subj.concept_id IN $concept_ids OR subj.parent_concept_id IN $root_concept_ids)
        CREATE (registry)-[:CONTAINS]->(subj)
        RETURN count(*) AS registry_links
        """
        
        try:
            with self.driver.session() as session:
                # Create registry for Roman Republic (root concept)
                root_concept_ids = [cid for label, cid in concept_map.items() 
                                   if label in ["Roman Republic", "Roman Empire"]]
                
                all_concept_ids = list(concept_map.values())
                
                result = session.run(
                    cypher,
                    registry_id="registry_roman_antiquity_001",
                    parent_concept_id="subj_roman_republic_q17167",
                    concept_ids=all_concept_ids,
                    root_concept_ids=root_concept_ids,
                    last_updated=datetime.now().isoformat()
                )
                
                links = result.single()["registry_links"]
                print(f"  ✓ Created registry with {links} concept links")
                return True
        
        except Exception as e:
            print(f"  ✗ Registry creation failed: {e}")
            return False
    
    def verify_setup(self) -> bool:
        """Verify schema and data were created"""
        print("[4/4] Verifying SubjectConcept setup...")
        
        cypher = """
        MATCH (subj:SubjectConcept)
        WITH count(subj) AS subj_count
        
        MATCH (reg:SubjectConceptRegistry)
        WITH subj_count, count(reg) AS reg_count
        
        MATCH (claim:Claim)
        WITH subj_count, reg_count, count(claim) AS claim_count
        
        RETURN subj_count, reg_count, claim_count
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(cypher).single()
                
                subj_count = result["subj_count"]
                reg_count = result["reg_count"]
                claim_count = result["claim_count"]
                
                print(f"\n{'='*80}")
                print("VERIFICATION")
                print(f"{'='*80}")
                print(f"SubjectConcept nodes:        {subj_count}")
                print(f"SubjectConceptRegistry nodes: {reg_count}")
                print(f"Claim nodes:                  {claim_count}")
                print(f"{'='*80}")
                
                if subj_count > 0 and reg_count > 0:
                    print("[OK] SubjectConcept schema created successfully!")
                    return True
                else:
                    print("[ERROR] Schema creation incomplete")
                    return False
        
        except Exception as e:
            print(f"  ✗ Verification failed: {e}")
            return False
    
    def load(self) -> bool:
        """Execute full schema load"""
        print("\n" + "="*80)
        print("SUBJECT CONCEPT SCHEMA LOADER")
        print("="*80 + "\n")
        
        # Step 1: Schema
        if not self.create_schema():
            return False
        
        # Step 2: Bootstrap concepts
        concept_map = self.create_bootstrap_concepts()
        if not concept_map:
            return False
        
        # Step 3: Registries
        if not self.create_registries(concept_map):
            return False
        
        # Step 4: Verify
        if not self.verify_setup():
            return False
        
        print("\n" + "="*80)
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Create SubjectConcept schema and bootstrap data in Neo4j"
    )
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--username", default="neo4j", help="Neo4j username")
    parser.add_argument("--password", required=True, help="Neo4j password")
    
    args = parser.parse_args()
    
    loader = SubjectConceptLoader(args.uri, args.username, args.password)
    
    try:
        success = loader.load()
        sys.exit(0 if success else 1)
    finally:
        loader.close()


if __name__ == "__main__":
    main()
