#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wikidata Claim Integration Pipeline

Integrates Wikidata extraction (e.g., Q17167 Roman Republic) into validated Claim structure:
1. Load Q17167 claim proposals from JSON
2. Validate using validation_models.py (Pydantic)
3. Compute AssertionCiphers (facet-agnostic for deduplication)
4. Group by AssertionCipher for cross-facet consensus
5. Generate Cypher statements for Neo4j import

Part of Priority 10: Enrichment Pipeline Integration
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

# Set UTF-8 output encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add models directory to path
sys.path.insert(0, str(Path(__file__).parent / "models"))

from validation_models import (
    Claim,
    RelationshipAssertion,
    FacetPerspective,
    initialize_registry,
    LifecycleStatus
)


class WikidataClaimIntegrator:
    """Integrates Wikidata extractions into validated claim structure."""
    
    # Wikidata predicate → canonical relationship type mappings (Priority 10 expansion)
    PREDICATE_MAPPINGS = {
        "P710": ["PARTICIPATED_IN", "HAD_PARTICIPANT"],  # Participant (65 instances)
        "P921": ["SUBJECT_OF", "ABOUT"],                 # Main subject (23 instances)
        "P101": ["FIELD_OF_STUDY", "STUDIED_BY"],       # Field of work (5 instances)
        # Keep existing mappings working
        "P17": ["CONTROLLED", "CONTROLLED_BY"],         # Country (54 instances)
        "P276": ["LOCATED_IN"],                          # Location (8 instances)
        "P61": ["DISCOVERED_BY"],                        # Discoverer (3 instances)
        "P138": ["NAMED_AFTER"],                         # Named after (2 instances)
        "P580": ["START_TIME"],                          # Start point (2 instances)
        "P582": ["END_TIME"],                            # End point (2 instances)
        "P170": ["CREATED_BY"],                          # Creator (1 instance)
        "P195": ["COLLECTION"],                          # Collection (1 instance)
    }
    
    def __init__(
        self,
        facet_registry_path: Path,
        relationship_registry_path: Path,
        default_facet: str = "historical",
        default_agent: str = "wikidata_harvester_001"
    ):
        """
        Initialize integrator.
        
        Args:
            facet_registry_path: Path to facet_registry_master.json
            facet_registry_path: Path to facet_registry_master.json
            relationship_registry_path: Path to relationship_types_registry_master.csv
            default_facet: Default facet for claims without explicit assignment
            default_agent: Default agent ID for claim creation
        """
        # Initialize registry for validation
        initialize_registry(facet_registry_path, relationship_registry_path)
        
        self.default_facet = default_facet
        self.default_agent = default_agent
        
        # Stats tracking
        self.stats = {
            "relationship_claims_processed": 0,
            "relationship_claims_validated": 0,
            "relationship_claims_failed": 0,
            "attribute_claims_processed": 0,
            "unique_assertion_ciphers": 0,
            "claims_with_multiple_perspectives": 0,
            "v1_kernel_mappings": 0,
            "unmapped_predicates": 0
        }
        
    def load_wikidata_extraction(self, filepath: Path) -> Dict[str, Any]:
        """Load Wikidata extraction JSON (e.g., Q17167_claim_subgraph_proposal.json)."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def map_confidence_to_facet(self, predicate: str, subject_p31: List[str]) -> str:
        """
        Map Wikidata predicate + subject type to most relevant facet.
        
        Simple heuristic for now:
        - P17 (country), P30 (continent), P36 (capital) → geographic
        - P710 (participant), P607 (conflict) → military
        - P38 (currency), P2936 (language used) → cultural/economic
        - Default → historical
        """
        # Military predicates
        if predicate in ["P710", "P607", "P47"]:  # participant, conflict, shares border
            return "military"
        
        # Geographic predicates
        if predicate in ["P17", "P30", "P36", "P131", "P706"]:  # country, continent, capital, located in, location
            return "geographic"
        
        # Economic/Cultural
        if predicate in ["P38", "P2936", "P140"]:  # currency, language, religion
            return "cultural"
        
        # Political
        if predicate in ["P194", "P1906", "P1001"]:  # legislative body, office, jurisdiction
            return "political"
        
        # Default to historical for Roman Republic context
        return "historical"
    
    def create_claim_from_relationship_proposal(
        self,
        proposal: Dict[str, Any],
        source_qid: str
    ) -> Optional[Claim]:
        """
        Create validated Claim from Wikidata relationship proposal.
        
        Args:
            proposal: Relationship claim proposal dict
            source_qid: Source QID (e.g., Q17167)
        
        Returns:
            Validated Claim object or None if validation fails
        """
        try:
            # Extract fields
            claim_id = proposal["claim_id"]
            subject_qid = proposal["subject_qid"]
            subject_label = proposal["subject_label"]
            predicate_pid = proposal["predicate_pid"]
            predicate_label = proposal["predicate_label"]
            object_qid = proposal["object_qid"]
            object_label = proposal["object_label"]
            confidence = proposal.get("confidence", 0.5)
            canonical_types = proposal.get("canonical_relationship_types", [])
            source_p31 = proposal.get("source_p31", [])
            
            # Build claim content (natural language assertion)
            content = f"{subject_label} {predicate_label} {object_label}"
            
            # Map to facet (heuristic)
            facet = self.map_confidence_to_facet(predicate_pid, source_p31)
            
            # Create relationship assertions
            relationships = []
            if canonical_types:
                # Use first canonical type (we have bidirectional pairs like CONTROLLED/CONTROLLED_BY)
                rel_type = canonical_types[0]
                relationships.append(
                    RelationshipAssertion(
                        rel_type=rel_type,
                        subject_id=subject_qid,
                        object_id=object_qid,
                        confidence=confidence,
                        source_id=f"wikidata:{predicate_pid}"
                    )
                )
                self.stats["v1_kernel_mappings"] += 1
            elif predicate_pid in self.PREDICATE_MAPPINGS:
                # Fallback: Use predicate mapping if available (Priority 10 expansion)
                canonical_types = self.PREDICATE_MAPPINGS[predicate_pid]
                rel_type = canonical_types[0]
                relationships.append(
                    RelationshipAssertion(
                        rel_type=rel_type,
                        subject_id=subject_qid,
                        object_id=object_qid,
                        confidence=confidence,
                        source_id=f"wikidata:{predicate_pid}"
                    )
                )
                self.stats["v1_kernel_mappings"] += 1
                print(f"  [MAPPED] {claim_id}: Applied fallback mapping {predicate_pid} → {rel_type}")
            else:
                # No canonical mapping - track but skip
                self.stats["unmapped_predicates"] += 1
                print(f"  [SKIP] {claim_id}: No canonical mapping for {predicate_pid}")
                return None
            
            # Create Claim with AssertionCipher (facet-agnostic)
            claim = Claim.create_with_cipher(
                claim_id=claim_id,
                content=content,
                source_id=f"wikidata:{source_qid}:{predicate_pid}",
                created_by=self.default_agent,
                confidence=confidence,
                relationships=relationships,
                facets=[],  # Empty for AssertionCipher computation
                cipher_type="assertion"  # Facet-agnostic for deduplication
            )
            
            self.stats["relationship_claims_validated"] += 1
            return claim
            
        except Exception as e:
            print(f"  [FAIL] Failed to create claim from {proposal.get('claim_id', 'unknown')}: {e}")
            self.stats["relationship_claims_failed"] += 1
            return None
    
    def process_extraction(
        self,
        extraction_path: Path,
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Process complete Wikidata extraction.
        
        Args:
            extraction_path: Path to Q17167_claim_subgraph_proposal.json
            output_dir: Directory for output files
        
        Returns:
            Processing results with stats and grouped claims
        """
        print("="*70)
        print("WIKIDATA CLAIM INTEGRATION PIPELINE")
        print("Priority 10: Enrichment Pipeline Integration")
        print("="*70)
        print()
        
        # Load extraction
        print(f"Loading extraction: {extraction_path.name}")
        extraction = self.load_wikidata_extraction(extraction_path)
        
        seed = extraction["seed"]
        print(f"Seed entity: {seed['qid']} - {seed['label']}")
        print(f"Description: {seed['description']}")
        print()
        
        summary = extraction["summary"]
        print(f"Extraction summary:")
        print(f"  Nodes: {summary['node_count']}")
        print(f"  Relationship claims: {summary['relationship_claim_count']}")
        print(f"  Attribute claims: {summary['attribute_claim_count']}")
        print()
        
        # Process relationship claims
        print("Processing relationship claims...")
        relationship_proposals = extraction.get("relationship_claim_proposals", [])
        
        claims: List[Claim] = []
        for proposal in relationship_proposals:
            self.stats["relationship_claims_processed"] += 1
            claim = self.create_claim_from_relationship_proposal(proposal, seed["qid"])
            if claim:
                claims.append(claim)
        
        print(f"  Processed: {self.stats['relationship_claims_processed']}")
        print(f"  Validated: {self.stats['relationship_claims_validated']}")
        print(f"  Failed: {self.stats['relationship_claims_failed']}")
        print(f"  V1 kernel mappings: {self.stats['v1_kernel_mappings']}")
        print(f"  Unmapped predicates: {self.stats['unmapped_predicates']}")
        print()
        
        # Group by AssertionCipher for deduplication
        print("Grouping by AssertionCipher (cross-facet deduplication)...")
        cipher_groups: Dict[str, List[Claim]] = defaultdict(list)
        for claim in claims:
            cipher_groups[claim.cipher].append(claim)
        
        self.stats["unique_assertion_ciphers"] = len(cipher_groups)
        self.stats["claims_with_multiple_perspectives"] = sum(
            1 for claims in cipher_groups.values() if len(claims) > 1
        )
        
        print(f"  Unique AssertionCiphers: {self.stats['unique_assertion_ciphers']}")
        print(f"  Claims with multiple perspectives: {self.stats['claims_with_multiple_perspectives']}")
        print()
        
        # Export results
        print("Exporting results...")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Export validated claims as JSON
        claims_output = output_dir / f"{seed['qid']}_validated_claims.json"
        self.export_claims_json(claims, claims_output)
        print(f"  [OK] Validated claims: {claims_output.name}")
        
        # 2. Export cipher groups for consensus tracking
        consensus_output = output_dir / f"{seed['qid']}_cipher_groups.json"
        self.export_cipher_groups(cipher_groups, consensus_output)
        print(f"  [OK] Cipher groups: {consensus_output.name}")
        
        # 3. Export Cypher statements for Neo4j
        cypher_output = output_dir / f"{seed['qid']}_neo4j_import.cypher"
        self.export_cypher_statements(claims, cipher_groups, cypher_output, seed)
        print(f"  [OK] Neo4j Cypher: {cypher_output.name}")
        
        # 4. Export processing stats
        stats_output = output_dir / f"{seed['qid']}_integration_stats.json"
        self.export_stats(stats_output, seed, extraction)
        print(f"  [OK] Stats: {stats_output.name}")
        
        print()
        print("="*70)
        print("INTEGRATION COMPLETE")
        print("="*70)
        
        return {
            "stats": self.stats,
            "claims": claims,
            "cipher_groups": cipher_groups
        }
    
    def export_claims_json(self, claims: List[Claim], output_path: Path):
        """Export validated claims as JSON."""
        claims_data = [
            {
                "claim_id": c.claim_id,
                "cipher": c.cipher,
                "content": c.content,
                "source_id": c.source_id,
                "confidence": c.confidence,
                "created_by": c.created_by,
                "relationships": [
                    {
                        "rel_type": r.rel_type,
                        "subject_id": r.subject_id,
                        "object_id": r.object_id,
                        "confidence": r.confidence,
                        "source_id": r.source_id
                    }
                    for r in c.relationships
                ],
                "created_at": c.created_at.isoformat()
            }
            for c in claims
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(claims_data, f, indent=2, ensure_ascii=False)
    
    def export_cipher_groups(self, cipher_groups: Dict[str, List[Claim]], output_path: Path):
        """Export cipher groups for consensus tracking."""
        groups_data = []
        for cipher, claims in cipher_groups.items():
            groups_data.append({
                "assertion_cipher": cipher,
                "claim_count": len(claims),
                "claims": [c.claim_id for c in claims],
                "content": claims[0].content,  # Same for all (facet-agnostic)
                "avg_confidence": sum(c.confidence for c in claims) / len(claims)
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(groups_data, f, indent=2, ensure_ascii=False)
    
    def export_cypher_statements(
        self,
        claims: List[Claim],
        cipher_groups: Dict[str, List[Claim]],
        output_path: Path,
        seed: Dict[str, str]
    ):
        """Generate Cypher statements for Neo4j import."""
        statements = []
        
        # Header
        statements.append(f"// Neo4j Import for {seed['qid']} - {seed['label']}")
        statements.append(f"// Generated: {datetime.utcnow().isoformat()}Z")
        statements.append(f"// Claims: {len(claims)}")
        statements.append(f"// Unique assertions: {len(cipher_groups)}")
        statements.append("")
        
        # Create seed entity
        statements.append("// Create seed entity")
        statements.append(f"MERGE (seed:Entity:HistoricalPeriod {{qid: '{seed['qid']}'}})")
        statements.append(f"  SET seed.label = '{seed['label']}'")
        statements.append(f"  SET seed.description = '{seed['description']}'")
        statements.append("")
        
        # Create claims (one per unique cipher)
        statements.append("// Create claims (by AssertionCipher)")
        for cipher, claim_list in cipher_groups.items():
            # Use first claim as representative
            claim = claim_list[0]
            content_escaped = claim.content.replace("'", "\\'")
            
            statements.append(f"MERGE (c:Claim {{cipher: '{cipher}'}})")
            statements.append(f"  SET c.content = '{content_escaped}'")
            statements.append(f"  SET c.source_id = '{claim.source_id}'")
            statements.append(f"  SET c.created_by = '{claim.created_by}'")
            statements.append(f"  SET c.created_at = '{claim.created_at.isoformat()}Z'")
            
            # Create relationships
            for rel in claim.relationships:
                statements.append(f"MERGE (subj:Entity {{qid: '{rel.subject_id}'}})")
                statements.append(f"MERGE (obj:Entity {{qid: '{rel.object_id}'}})")
                statements.append(f"MERGE (subj)-[r:{rel.rel_type}]->(obj)")
                statements.append(f"  SET r.confidence = {rel.confidence}")
                if rel.source_id:
                    statements.append(f"  SET r.source_id = '{rel.source_id}'")
                statements.append(f"MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)")
            
            statements.append("")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(statements))
    
    def export_stats(self, output_path: Path, seed: Dict[str, str], extraction: Dict[str, Any]):
        """Export processing statistics."""
        stats_data = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "seed": seed,
            "extraction_summary": extraction["summary"],
            "integration_stats": self.stats
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, indent=2, ensure_ascii=False)


def main():
    """Run integration pipeline on Q17167 Roman Republic extraction."""
    # Paths
    root = Path(__file__).parent.parent
    facet_registry = root / "Facets" / "facet_registry_master.json"
    relationship_registry = root / "Relationships" / "relationship_types_registry_master.csv"
    extraction_file = root / "JSON" / "wikidata" / "proposals" / "Q17167_claim_subgraph_proposal.json"
    output_dir = root / "JSON" / "wikidata" / "integrated"
    
    # Validate paths
    if not facet_registry.exists():
        print(f"Error: Facet registry not found: {facet_registry}")
        return 1
    if not relationship_registry.exists():
        print(f"Error: Relationship registry not found: {relationship_registry}")
        return 1
    if not extraction_file.exists():
        print(f"Error: Extraction file not found: {extraction_file}")
        return 1
    
    # Create integrator
    integrator = WikidataClaimIntegrator(
        facet_registry_path=facet_registry,
        relationship_registry_path=relationship_registry,
        default_facet="historical",
        default_agent="wikidata_harvester_001"
    )
    
    # Process extraction
    results = integrator.process_extraction(
        extraction_path=extraction_file,
        output_dir=output_dir
    )
    
    # Print summary
    print()
    print("Integration Summary:")
    print(f"  Validated claims: {results['stats']['relationship_claims_validated']}")
    print(f"  Unique assertions: {results['stats']['unique_assertion_ciphers']}")
    print(f"  V1 kernel mappings: {results['stats']['v1_kernel_mappings']}")
    print(f"  Output directory: {output_dir}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
