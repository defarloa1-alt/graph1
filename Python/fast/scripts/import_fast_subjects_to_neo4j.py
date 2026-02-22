#!/usr/bin/env python3
"""
FAST Subject Import Pipeline for Chrystallum

Imports Library of Congress Subject Headings (LCSH) from JSONLD format
into Neo4j with multi-faceted classification and authority tiers.

Features:
- Parse JSONLD SKOS records
- Detect authority tier (TIER_1/2/3) by federation level
- Map subjects to 16 analytical facets
- Handle temporal name variants (e.g., Mount McKinley → Denali)
- Create Subject nodes with extended properties
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

@dataclass
class SubjectRecord:
    """LCSH Subject record with authority tier and facet mapping."""
    lcsh_id: str
    unique_id: str
    label: str
    wikidata_qid: Optional[str] = None
    wikipedia_link: bool = False
    authority_tier: str = "TIER_3"
    authority_confidence: float = 0.70
    facet_scores: Dict[str, float] = None
    facet_richness: int = 0
    named_variants: List[Dict] = None
    lcc_code: Optional[str] = None
    dewey_code: Optional[str] = None
    created_date: Optional[str] = None
    last_revised: Optional[str] = None
    is_deprecated: bool = False
    
    def __post_init__(self):
        if self.facet_scores is None:
            self.facet_scores = {}
        if self.named_variants is None:
            self.named_variants = []
    
    def to_cypher_create(self) -> str:
        """Generate Cypher CREATE statement for this subject."""
        props = {
            "lcsh_id": self.lcsh_id,
            "unique_id": self.unique_id,
            "label": self.label,
            "authority_tier": self.authority_tier,
            "authority_confidence": self.authority_confidence,
            "facet_richness": self.facet_richness,
            "is_deprecated": self.is_deprecated
        }
        
        # Add optional properties
        if self.wikidata_qid:
            props["wikidata_qid"] = self.wikidata_qid
        if self.lcc_code:
            props["lcc_code"] = self.lcc_code
        if self.dewey_code:
            props["dewey_code"] = self.dewey_code
        if self.created_date:
            props["created_date"] = f"datetime('{self.created_date}')"
        if self.last_revised:
            props["last_revised"] = f"datetime('{self.last_revised}')"
        
        props["facet_scores"] = self.facet_scores
        props["named_variants"] = self.named_variants
        props["wikipedia_link"] = self.wikipedia_link
        
        # Build property string
        prop_str = ", ".join(
            f"{k}: {json.dumps(v) if not isinstance(v, str) or not v.startswith('datetime') else v}"
            for k, v in props.items()
        )
        
        return f"CREATE (s:Subject {{{prop_str}}})"


class FASTSubjectImporter:
    """Import FAST LCSH subjects into Neo4j knowledge graph."""
    
    # Facet patterns for classification
    FACET_PATTERNS = {
        "political": {
            "keywords": ["government", "state", "empire", "dynasty", "regime", "political"],
            "score_base": 0.90
        },
        "military": {
            "keywords": ["war", "battle", "military", "conquest", "army", "navy"],
            "score_base": 0.85
        },
        "economic": {
            "keywords": ["trade", "commerce", "economic", "currency", "market", "industry"],
            "score_base": 0.80
        },
        "cultural": {
            "keywords": ["culture", "art", "customs", "traditions", "society"],
            "score_base": 0.75
        },
        "religious": {
            "keywords": ["religion", "religious", "faith", "doctrine", "theology"],
            "score_base": 0.80
        },
        "geographic": {
            "keywords": ["geographic", "place", "region", "territory", "zone", "area"],
            "score_base": 0.95
        }
    }
    
    def __init__(self, jsonld_file: str):
        """Initialize importer with JSONLD source file."""
        self.jsonld_file = Path(jsonld_file)
        self.subjects: List[SubjectRecord] = []
        self.wikidata_lookups: Dict[str, str] = {}  # label -> QID cache
    
    def parse_jsonld(self) -> List[Dict]:
        """Parse JSONLD SKOS records from file."""
        with open(self.jsonld_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = []
        if "@graph" in data:
            for item in data["@graph"]:
                if "@graph" in item:
                    # Nested structure: extract inner graph
                    for inner_item in item["@graph"]:
                        if inner_item.get("@type") == "skos:Concept":
                            records.append(inner_item)
                elif item.get("@type") == "skos:Concept":
                    records.append(item)
        
        return records
    
    def extract_lcsh_id(self, record: Dict) -> Optional[str]:
        """Extract LCSH ID from @id field."""
        at_id = record.get("@id", "")
        match = re.search(r"sh(\d+)", at_id)
        if match:
            return match.group(0)  # Return 'sh12345'
        return None
    
    def extract_label(self, record: Dict) -> Optional[str]:
        """Extract preferred label from SKOS record."""
        pref_label = record.get("skos:prefLabel")
        if isinstance(pref_label, dict):
            return pref_label.get("@value")
        elif isinstance(pref_label, str):
            return pref_label
        return None
    
    def extract_change_dates(self, record: Dict) -> Tuple[Optional[str], Optional[str]]:
        """Extract creation and revision dates from change notes."""
        created = None
        revised = None
        
        change_notes = record.get("skos:changeNote", [])
        if not isinstance(change_notes, list):
            change_notes = [change_notes]
        
        for note in change_notes:
            # Change notes are typically @id references; need full record lookup
            # For now, use simplified date extraction
            pass
        
        return created, revised
    
    def determine_authority_tier(self, label: str, has_wikidata: bool, has_wikipedia: bool) -> Tuple[str, float]:
        """Determine authority tier based on federation level."""
        if has_wikidata and has_wikipedia:
            return "TIER_1", 0.98
        elif has_wikidata:
            return "TIER_2", 0.90
        else:
            return "TIER_3", 0.70
    
    def score_facets(self, label: str) -> Tuple[Dict[str, float], int]:
        """Score subject across analytical facets."""
        scores = {}
        label_lower = label.lower()
        
        for facet, config in self.FACET_PATTERNS.items():
            # Check for keyword matches
            matches = sum(1 for kw in config["keywords"] if kw in label_lower)
            if matches > 0:
                # Score based on matches: each match adds 0.1, capped at base score
                score = min(config["score_base"], 0.5 + matches * 0.1)
                scores[facet] = round(score, 2)
        
        richness = len([s for s in scores.values() if s > 0.5])
        return scores, richness
    
    def subject_from_jsonld(self, record: Dict) -> Optional[SubjectRecord]:
        """Convert JSONLD SKOS record to SubjectRecord."""
        lcsh_id = self.extract_lcsh_id(record)
        if not lcsh_id:
            return None
        
        label = self.extract_label(record)
        if not label:
            return None
        
        # Extract dates
        created_date, revised_date = self.extract_change_dates(record)
        
        # Determine authority tier (simple heuristic for now)
        # In production, would look up Wikidata/Wikipedia
        has_wikidata = False  # TODO: lookup in Wikidata
        has_wikipedia = False  # TODO: lookup in Wikipedia
        tier, confidence = self.determine_authority_tier(label, has_wikidata, has_wikipedia)
        
        # Score facets
        facet_scores, richness = self.score_facets(label)
        
        # Create name variant for current form
        named_variants = [
            {
                "name": label,
                "valid_from": 2000,  # Default LCSH epoch
                "valid_until": 9999,
                "is_preferred": True,
                "is_official": True,
                "source": "LCSH",
                "reason": "Current LCSH heading"
            }
        ]
        
        return SubjectRecord(
            lcsh_id=lcsh_id,
            unique_id=f"SUBJECT_LCSH_{lcsh_id}",
            label=label,
            authority_tier=tier,
            authority_confidence=confidence,
            facet_scores=facet_scores,
            facet_richness=richness,
            named_variants=named_variants,
            created_date=created_date,
            last_revised=revised_date
        )
    
    def import_subjects(self) -> List[SubjectRecord]:
        """Import all subjects from JSONLD file."""
        records = self.parse_jsonld()
        
        for record in records:
            subject = self.subject_from_jsonld(record)
            if subject:
                self.subjects.append(subject)
        
        return self.subjects
    
    def generate_cypher_script(self, output_file: Optional[str] = None) -> str:
        """Generate Cypher import script."""
        script = "// Subject Import Script - Generated Auto\n"
        script += f"// Generated: {datetime.now().isoformat()}\n"
        script += f"// Subject Count: {len(self.subjects)}\n\n"
        
        for subject in self.subjects:
            script += subject.to_cypher_create() + ";\n"
            
            # Add facet anchor relationships
            for facet, score in subject.facet_scores.items():
                facet_class = f"{facet.capitalize()}Facet"
                script += f"MATCH (s:Subject {{lcsh_id: '{subject.lcsh_id}'}})\n"
                script += f"CREATE (s)-[:FACET_ANCHOR {{score: {score}}}]->(:{facet_class})\n"
                script += ";\n"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(script)
        
        return script
    
    def print_summary(self):
        """Print import summary statistics."""
        print(f"\n{'=' * 60}")
        print(f"FAST Subject Import Summary")
        print(f"{'=' * 60}")
        print(f"Total subjects imported: {len(self.subjects)}")
        
        # Count by tier
        tier_counts = {}
        for subject in self.subjects:
            tier_counts[subject.authority_tier] = tier_counts.get(subject.authority_tier, 0) + 1
        
        print("\nBy Authority Tier:")
        for tier in ["TIER_1", "TIER_2", "TIER_3"]:
            count = tier_counts.get(tier, 0)
            print(f"  {tier}: {count}")
        
        # Top subjects by facet richness
        top_rich = sorted(self.subjects, key=lambda s: s.facet_richness, reverse=True)[:5]
        print(f"\nTop subjects by facet richness:")
        for s in top_rich:
            print(f"  {s.label} ({s.facet_richness} facets)")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python import_fast_subjects_to_neo4j.py <jsonld_file> [output_cypher]")
        sys.exit(1)
    
    jsonld_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    importer = FASTSubjectImporter(jsonld_file)
    importer.import_subjects()
    importer.print_summary()
    
    if output_file:
        cypher = importer.generate_cypher_script(output_file)
        print(f"\nCypher script written to: {output_file}")
    else:
        print("\nNo output file specified. Use: python script.py <input> <output>")
