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

import argparse
import csv
import json
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict

# Set UTF-8 output encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent / "models"))

from scripts.agents.domain_initiator.proposal_backbone import FACET_BOOTSTRAP_PARENT

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
        self._rel_type_labels = self._load_relationship_labels(relationship_registry_path)
        self._seed: Dict[str, str] = {}
        
        # Stats tracking
        self.stats = {
            "relationship_claims_processed": 0,
            "relationship_claims_validated": 0,
            "relationship_claims_failed": 0,
            "attribute_claims_processed": 0,
            "unique_assertion_ciphers": 0,
            "claims_with_multiple_perspectives": 0,
            "v1_kernel_mappings": 0,
            "unmapped_predicates": 0,
            "skipped_bare_labels": 0,
            "validation_errors": 0,
        }
        self._quiet = False
        self._unmapped_by_pid: Counter[str] = Counter()

    @staticmethod
    def _load_relationship_labels(registry_path: Path) -> Dict[str, str]:
        labels: Dict[str, str] = {}
        if not registry_path.exists():
            return labels
        with registry_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                rel_type = (row.get("relationship_type") or "").strip()
                if not rel_type:
                    continue
                labels[rel_type] = (
                    (row.get("wikidata_label") or "").strip()
                    or (row.get("description") or "").strip()
                    or rel_type
                )
        return labels

    @staticmethod
    def _labeled_endpoint(qid: str, label: str) -> Dict[str, str]:
        return {"qid": qid, "label": label}

    def _backbone_block(self, facet: str) -> Dict[str, Any]:
        seed = self._seed or {}
        parent = FACET_BOOTSTRAP_PARENT.get(facet, {})
        block: Dict[str, Any] = {
            "seed": {
                "qid": seed.get("qid", ""),
                "label": seed.get("label", ""),
            },
            "facet_hint": facet,
            "subject_concept_routing": "deferred",
            "routing_note": (
                "Federation bootstrap claims anchor to the seed period. "
                "Facet→bootstrap parent is a review hint only until DI SubjectConcepts "
                "are approved and routing edges (ABOUT / MEMBER_OF) are written."
            ),
        }
        if parent.get("subject_id"):
            block["bootstrap_parent_hint"] = {
                "subject_id": parent.get("subject_id"),
                "label": parent.get("label"),
            }
        return block
        
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

    def _pick_rel_type(
        self,
        *,
        predicate_pid: str,
        canonical_types: List[str],
        proposal: Dict[str, Any],
    ) -> Optional[str]:
        types = list(canonical_types)
        if not types:
            if predicate_pid in self.PREDICATE_MAPPINGS:
                types = list(self.PREDICATE_MAPPINGS[predicate_pid])
            else:
                return None

        if len(types) == 1:
            return types[0]

        source_mode = (proposal.get("source_mode") or "").lower()
        inverse_pairs = {
            frozenset({"HAD_PARTICIPANT", "PARTICIPATED_IN"}),
            frozenset({"CAUSED", "CAUSED_BY"}),
            frozenset({"CONTROLLED", "CONTROLLED_BY"}),
            frozenset({"LOCATED_IN", "LOCATION_OF"}),
            frozenset({"PART_OF", "HAS_PART"}),
            frozenset({"APPOINTED", "APPOINTED_BY"}),
            frozenset({"POSITION_HELD", "OFFICE_HELD_BY"}),
        }
        if frozenset(types) in inverse_pairs:
            if source_mode.startswith("expanded_event") or source_mode.startswith("expanded_battle"):
                for preferred in ("HAD_PARTICIPANT", "CAUSED", "HAS_PART", "LOCATION_OF", "OFFICE_HELD_BY"):
                    if preferred in types:
                        return preferred
            if source_mode == "second_hop_person":
                for preferred in ("PARTICIPATED_IN", "CAUSED_BY", "PART_OF", "LOCATED_IN", "POSITION_HELD"):
                    if preferred in types:
                        return preferred
        return types[0]

    @staticmethod
    def _format_relationship_content(
        rel_type: str,
        subject_label: str,
        object_label: str,
    ) -> str:
        """Natural-language assertion for the directed relationship edge."""
        templates = {
            "HAD_PARTICIPANT": "{subject} had participant {object}",
            "PARTICIPATED_IN": "{subject} participated in {object}",
            "BATTLED_IN": "{subject} fought in {object}",
            "BATTLE_PARTICIPANT": "{subject} fought in {object}",
            "FOUGHT_IN": "{subject} fought in {object}",
            "CAUSED": "{subject} was caused by {object}",
            "CAUSED_BY": "{subject} caused {object}",
            "POSITION_HELD": "{subject} held position {object}",
            "APPOINTED": "{subject} held office {object}",
            "OFFICE_HELD_BY": "{object} was held by {subject}",
            "LOCATED_IN": "{subject} is located in {object}",
            "BIRTHPLACE_OF": "{object} is birthplace of {subject}",
            "PLACE_OF_BIRTH": "{subject} was born in {object}",
            "PART_OF": "{subject} is part of {object}",
            "HAS_PART": "{subject} has part {object}",
            "INSTANCE_OF": "{subject} is instance of {object}",
            "CONTROLLED": "{subject} was under country {object}",
            "CONTROLLED_BY": "{object} controlled {subject}",
            "SPOUSE_OF": "{subject} is spouse of {object}",
            "FATHER_OF": "{subject} is parent of {object}",
            "PARENT_OF": "{subject} is parent of {object}",
            "CHILD_OF": "{subject} is child of {object}",
            "CITIZEN_OF": "{subject} is citizen of {object}",
        }
        template = templates.get(rel_type)
        if template:
            return template.format(subject=subject_label, object=object_label)
        return f"{subject_label} —[{rel_type}]→ {object_label}"
    
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
            if (
                subject_qid == object_qid
                or not subject_label
                or not object_label
                or subject_label.strip().upper() == subject_qid.strip().upper()
                or object_label.strip().upper() == object_qid.strip().upper()
            ):
                self.stats["skipped_bare_labels"] += 1
                return None
            confidence = proposal.get("confidence", 0.5)
            canonical_types = proposal.get("canonical_relationship_types", [])

            rel_type = self._pick_rel_type(
                predicate_pid=predicate_pid,
                canonical_types=canonical_types,
                proposal=proposal,
            )
            if not rel_type:
                self.stats["unmapped_predicates"] += 1
                self._unmapped_by_pid[predicate_pid] += 1
                if not self._quiet:
                    print(f"  [SKIP] {claim_id}: No canonical mapping for {predicate_pid}")
                return None

            content = self._format_relationship_content(rel_type, subject_label, object_label)
            relationships = [
                RelationshipAssertion(
                    rel_type=rel_type,
                    subject_id=subject_qid,
                    object_id=object_qid,
                    confidence=confidence,
                    source_id=f"wikidata:{predicate_pid}",
                )
            ]
            self.stats["v1_kernel_mappings"] += 1

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
            if not self._quiet:
                print(f"  [FAIL] Failed to create claim from {proposal.get('claim_id', 'unknown')}: {e}")
            self.stats["validation_errors"] += 1
            self.stats["relationship_claims_failed"] += 1
            return None
    
    def process_extraction(
        self,
        extraction_path: Path,
        output_dir: Path,
        *,
        output_suffix: str = "",
        quiet: bool = True,
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
        print("="*70)
        print()
        
        self._quiet = quiet
        suffix = f"_{output_suffix}" if output_suffix else ""
        
        # Load extraction
        print(f"Loading extraction: {extraction_path.name}")
        extraction = self.load_wikidata_extraction(extraction_path)
        
        seed = extraction["seed"]
        self._seed = seed
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
        proposal_by_id: Dict[str, Dict[str, Any]] = {}
        for proposal in relationship_proposals:
            self.stats["relationship_claims_processed"] += 1
            claim = self.create_claim_from_relationship_proposal(proposal, seed["qid"])
            if claim:
                claims.append(claim)
                proposal_by_id[claim.claim_id] = proposal
        
        print(f"  Processed: {self.stats['relationship_claims_processed']}")
        print(f"  Validated: {self.stats['relationship_claims_validated']}")
        print(f"  Failed: {self.stats['relationship_claims_failed']}")
        print(f"  Skipped (bare labels): {self.stats['skipped_bare_labels']}")
        print(f"  Validation errors: {self.stats['validation_errors']}")
        print(f"  Unmapped predicates: {self.stats['unmapped_predicates']}")
        if self._unmapped_by_pid:
            print("  Top unmapped PIDs:")
            for pid, count in self._unmapped_by_pid.most_common(10):
                print(f"    {pid}: {count}")
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
        claims_output = output_dir / f"{seed['qid']}_validated_claims{suffix}.json"
        self.export_claims_json(claims, claims_output, proposal_by_id=proposal_by_id)
        print(f"  [OK] Validated claims: {claims_output.name}")
        
        consensus_output = output_dir / f"{seed['qid']}_cipher_groups{suffix}.json"
        self.export_cipher_groups(cipher_groups, consensus_output)
        print(f"  [OK] Cipher groups: {consensus_output.name}")
        
        cypher_output = output_dir / f"{seed['qid']}_neo4j_import{suffix}.cypher"
        self.export_cypher_statements(claims, cipher_groups, cypher_output, seed)
        print(f"  [OK] Neo4j Cypher: {cypher_output.name}")
        
        stats_output = output_dir / f"{seed['qid']}_integration_stats{suffix}.json"
        self.export_stats(stats_output, seed, extraction, extraction_path=str(extraction_path))
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
    
    def export_claims_json(
        self,
        claims: List[Claim],
        output_path: Path,
        *,
        proposal_by_id: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """Export validated claims as JSON."""
        claims_data = []
        for c in claims:
            proposal = (proposal_by_id or {}).get(c.claim_id) or {}
            subject_qid = proposal.get("subject_qid") or (
                c.relationships[0].subject_id if c.relationships else ""
            )
            object_qid = proposal.get("object_qid") or (
                c.relationships[0].object_id if c.relationships else ""
            )
            subject_label = proposal.get("subject_label") or ""
            object_label = proposal.get("object_label") or ""
            predicate_pid = proposal.get("predicate_pid") or ""
            predicate_label = proposal.get("predicate_label") or predicate_pid
            facet = self.map_confidence_to_facet(
                predicate_pid,
                proposal.get("source_p31") or [],
            )

            rel_rows = []
            for r in c.relationships:
                rel_label = self._rel_type_labels.get(r.rel_type, r.rel_type)
                prop_label = predicate_label
                if r.source_id and r.source_id.startswith("wikidata:"):
                    prop_label = predicate_label or r.source_id.replace("wikidata:", "")
                rel_rows.append(
                    {
                        "rel_type": r.rel_type,
                        "rel_type_label": rel_label,
                        "subject": self._labeled_endpoint(r.subject_id, subject_label),
                        "object": self._labeled_endpoint(r.object_id, object_label),
                        "confidence": r.confidence,
                        "source": {
                            "system": "wikidata",
                            "property": {
                                "pid": predicate_pid,
                                "label": prop_label,
                            },
                        },
                    }
                )

            row: Dict[str, Any] = {
                "claim_id": c.claim_id,
                "cipher": c.cipher,
                "claim_type": "RELATIONSHIP",
                "content": c.content,
                "confidence": c.confidence,
                "status": "proposed",
                "created_by": c.created_by,
                "created_at": c.created_at.isoformat(),
                "endpoints": {
                    "subject": self._labeled_endpoint(subject_qid, subject_label),
                    "object": self._labeled_endpoint(object_qid, object_label),
                },
                "predicate": {
                    "pid": predicate_pid,
                    "label": predicate_label,
                },
                "relationships": rel_rows,
                "provenance": {
                    "source_id": c.source_id,
                    "wikidata_statement_id": proposal.get("statement_id"),
                    "source_mode": proposal.get("source_mode"),
                    "federation_source": c.created_by,
                },
                "backbone": self._backbone_block(facet),
            }
            claims_data.append(row)
        
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
    
    def export_stats(
        self,
        output_path: Path,
        seed: Dict[str, str],
        extraction: Dict[str, Any],
        *,
        extraction_path: str = "",
    ):
        """Export processing statistics."""
        stats_data = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "seed": seed,
            "extraction_path": extraction_path,
            "extraction_summary": extraction["summary"],
            "integration_stats": self.stats,
            "unmapped_by_pid": dict(self._unmapped_by_pid.most_common(30)),
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        help="Claim subgraph proposal JSON (default: JSON/wikidata/proposals/Q17167_claim_subgraph_proposal.json)",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory (default: JSON/wikidata/integrated)",
    )
    parser.add_argument(
        "--output-suffix",
        default="",
        help="Suffix for output files, e.g. v2 -> Q17167_validated_claims_v2.json",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-claim skip/map messages",
    )
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    facet_registry = root / "Facets" / "facet_registry_master.json"
    relationship_registry = root / "Relationships" / "relationship_types_registry_master.csv"
    extraction_file = Path(args.input) if args.input else (
        root / "JSON" / "wikidata" / "proposals" / "Q17167_claim_subgraph_proposal.json"
    )
    output_dir = Path(args.output_dir) if args.output_dir else (root / "JSON" / "wikidata" / "integrated")
    
    if not facet_registry.exists():
        print(f"Error: Facet registry not found: {facet_registry}")
        return 1
    if not relationship_registry.exists():
        print(f"Error: Relationship registry not found: {relationship_registry}")
        return 1
    if not extraction_file.exists():
        print(f"Error: Extraction file not found: {extraction_file}")
        return 1
    
    integrator = WikidataClaimIntegrator(
        facet_registry_path=facet_registry,
        relationship_registry_path=relationship_registry,
        default_facet="historical",
        default_agent="wikidata_harvester_001",
    )
    
    results = integrator.process_extraction(
        extraction_path=extraction_file,
        output_dir=output_dir,
        output_suffix=args.output_suffix,
        quiet=not args.verbose,
    )
    
    print()
    print("Integration Summary:")
    print(f"  Validated claims: {results['stats']['relationship_claims_validated']}")
    print(f"  Unique assertions: {results['stats']['unique_assertion_ciphers']}")
    print(f"  Output directory: {output_dir}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
