#!/usr/bin/env python3
"""
AGENT TRAINING & INITIALIZATION PIPELINE
==========================================

Agent Training Process:
1. Receive Q-identifier (Wikidata QID)
2. Fetch all Wikidata properties + backlinks
3. Generate canonical subject_concept_id
4. Parse Wikipedia for ontology discovery
5. Extract sub-concept patterns from index/TOC
6. Build domain ontology for agent initialization

This creates self-bootstrapped ontologies grounded in authoritative sources.
"""

import requests
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib


class AgentTrainingPipeline:
    """Train agents to understand domain-specific sub-concepts"""
    
    WIKIDATA_API = "https://www.wikidata.org/w/api.php"
    WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
    
    def __init__(self, qid: str, language: str = "en"):
        """
        Initialize training for a SubjectConcept by QID.
        
        Args:
            qid: Wikidata Q-identifier (e.g., "Q17167" for Roman Republic)
            language: Wikipedia language code (default: "en")
        """
        self.qid = qid
        self.language = language
        
        # Will populate during training
        self.wikidata_properties = {}
        self.wikidata_backlinks = {}
        self.subject_concept_id = None
        self.wikipedia_title = None
        self.wikipedia_sections = []
        self.domain_ontology = {}
    
    # ========================================================================
    # PHASE 1: Fetch Wikidata Properties
    # ========================================================================
    
    def fetch_wikidata_properties(self) -> Dict:
        """
        Fetch all properties for QID from Wikidata.
        
        Returns: {property_id: value, ...}
        
        Example: Q17167 (Roman Republic)
          - P580 (start time): -509-01-01T00:00:00Z
          - P582 (end time): -27-01-01T00:00:00Z
          - P131 (located in): Q38 (Italy)
          - P625 (coordinate location): [12.4964, 41.9028]
          - P910 (topic's main category): Category:Ancient Rome
          - etc.
        """
        print(f"\n[PHASE 1] Fetching Wikidata properties for {self.qid}...")
        
        params = {
            "action": "wbgetentities",
            "ids": self.qid,
            "format": "json",
            "props": "labels|descriptions|claims"
        }
        
        try:
            response = requests.get(self.WIKIDATA_API, params=params)
            data = response.json()
            
            entity = data.get("entities", {}).get(self.qid, {})
            
            if not entity:
                print(f"  ✗ QID not found: {self.qid}")
                return {}
            
            # Extract properties
            properties = {}
            for prop_id, claims in entity.get("claims", {}).items():
                # For each property, get the main value
                if claims:
                    # Simplify: take first claim's value
                    claim = claims[0]
                    value = self._extract_claim_value(claim)
                    properties[prop_id] = value
            
            self.wikidata_properties = properties
            
            print(f"  ✓ Fetched {len(properties)} properties")
            print(f"    Label: {entity.get('labels', {}).get(self.language, {}).get('value', 'N/A')}")
            print(f"    Description: {entity.get('descriptions', {}).get(self.language, {}).get('value', 'N/A')}")
            
            return properties
        
        except Exception as e:
            print(f"  ✗ Error fetching Wikidata: {e}")
            return {}
    
    def _extract_claim_value(self, claim: Dict) -> str:
        """Extract human-readable value from Wikidata claim"""
        try:
            mainsnak = claim.get("mainsnak", {})
            datavalue = mainsnak.get("datavalue", {})
            
            # Handle different data types
            dtype = mainsnak.get("datatype", "")
            
            if dtype == "wikibase-item":
                # Reference to another QID
                return datavalue.get("value", {}).get("id", "")
            
            elif dtype == "time":
                # Temporal value
                return datavalue.get("value", {}).get("time", "")
            
            elif dtype == "string":
                return datavalue.get("value", "")
            
            elif dtype == "globe-coordinate":
                # Geographic coordinate
                coord = datavalue.get("value", {})
                return f"({coord.get('latitude', 0)}, {coord.get('longitude', 0)})"
            
            else:
                return str(datavalue.get("value", ""))
        
        except Exception:
            return ""
    
    # ========================================================================
    # PHASE 2: Fetch Wikidata Backlinks
    # ========================================================================
    
    def fetch_wikidata_backlinks(self) -> Dict:
        """
        Fetch entities that have relationships TO this QID (backlinks).
        
        This shows what other entities are connected to our subject.
        
        Example: For Q17167 (Roman Republic), backlinks might include:
          - Q186214 (First Punic War) has P580=Q17167 (occurs_in)
          - Q3105 (Punic Wars) has P131=Q17167 (part_of)
          - Q17167 has reverse links from battles, emperors, concepts
        
        This helps identify related sub-concepts.
        """
        print(f"\n[PHASE 2] Fetching Wikidata backlinks for {self.qid}...")
        
        params = {
            "action": "wbgetclaims",
            "entity": self.qid,
            "format": "json"
        }
        
        try:
            response = requests.get(self.WIKIDATA_API, params=params)
            data = response.json()
            
            # Invert: find all entities with properties pointing to self.qid
            # This requires a secondary query - simplified version:
            # Search for entities where property P131 (part_of) or P17 (country) etc. = self.qid
            
            backlinks = self._search_related_entities(self.qid)
            self.wikidata_backlinks = backlinks
            
            print(f"  ✓ Found {len(backlinks)} related entities")
            
            return backlinks
        
        except Exception as e:
            print(f"  ✗ Error fetching backlinks: {e}")
            return {}
    
    def _search_related_entities(self, qid: str, max_results: int = 50) -> Dict:
        """
        Search for entities related to qid.
        Uses SPARQL or simple search as fallback.
        """
        # Simplified: search Wikipedia for mentions
        related = {}
        
        try:
            # Search for entities with P131 (part of) = qid
            params = {
                "action": "query",
                "list": "search",
                "srsearch": f"haswbstatement:P131={qid}",
                "format": "json",
                "srnamespace": "0",
                "srlimit": max_results
            }
            
            response = requests.get(self.WIKIDATA_API, params=params)
            # Simplified - in production would parse Wikidata SPARQL
            
        except Exception:
            pass
        
        return related
    
    # ========================================================================
    # PHASE 3: Generate Canonical subject_concept_id
    # ========================================================================
    
    def generate_subject_concept_id(self) -> str:
        """
        Generate canonical subject_concept_id from Wikidata properties.
        
        Composite: SHA256(QID + expanded_properties)
        
        This ensures idempotent IDs that change if properties change.
        """
        print(f"\n[PHASE 3] Generating canonical subject_concept_id...")
        
        # Build canonical composite from key properties
        composite_parts = [self.qid]
        
        # Add key temporal properties (P580, P582 = start/end time)
        if "P580" in self.wikidata_properties:
            composite_parts.append(f"start:{self.wikidata_properties['P580']}")
        if "P582" in self.wikidata_properties:
            composite_parts.append(f"end:{self.wikidata_properties['P582']}")
        
        # Add location (P131, P17 = located in, country)
        if "P131" in self.wikidata_properties:
            composite_parts.append(f"location:{self.wikidata_properties['P131']}")
        
        # Build canonical string
        canonical = "|".join(composite_parts)
        
        # Hash it
        hash_obj = hashlib.sha256(canonical.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()[:12]
        
        self.subject_concept_id = f"subj_{hash_hex}"
        
        print(f"  ✓ Generated: {self.subject_concept_id}")
        print(f"    Composite: {canonical}")
        
        return self.subject_concept_id
    
    # ========================================================================
    # PHASE 4: Fetch Wikipedia & Parse Index
    # ========================================================================
    
    def fetch_wikipedia_article(self) -> Dict:
        """
        Fetch Wikipedia article for entity.
        
        Returns full text + parsed sections.
        """
        print(f"\n[PHASE 4] Fetching Wikipedia article...")
        
        # Get Wikipedia title from Wikidata
        title = self._get_wikipedia_title_from_wikidata()
        
        if not title:
            print(f"  ✗ No Wikipedia article found")
            return {}
        
        self.wikipedia_title = title
        
        # Fetch article
        params = {
            "action": "query",
            "titles": title,
            "prop": "extracts|sections",
            "explaintext": True,
            "format": "json"
        }
        
        try:
            response = requests.get(self.WIKIPEDIA_API, params=params)
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            page = list(pages.values())[0] if pages else {}
            
            text = page.get("extract", "")
            sections = page.get("sections", [])
            
            print(f"  ✓ Fetched Wikipedia article: {title}")
            print(f"    Length: {len(text)} characters")
            print(f"    Sections: {len(sections)}")
            
            # Parse sections into ontology hints
            self.wikipedia_sections = self._parse_sections(sections)
            
            return {
                "title": title,
                "text": text,
                "sections": sections
            }
        
        except Exception as e:
            print(f"  ✗ Error fetching Wikipedia: {e}")
            return {}
    
    def _get_wikipedia_title_from_wikidata(self) -> str:
        """Get Wikipedia article title from Wikidata sitelinks"""
        try:
            params = {
                "action": "wbgetentities",
                "ids": self.qid,
                "format": "json",
                "props": "sitelinks"
            }
            
            response = requests.get(self.WIKIDATA_API, params=params)
            data = response.json()
            
            entity = data.get("entities", {}).get(self.qid, {})
            sitelinks = entity.get("sitelinks", {})
            
            # Get English Wikipedia title
            enwiki = sitelinks.get(f"{self.language}wiki", {})
            return enwiki.get("title", "")
        
        except Exception:
            return ""
    
    def _parse_sections(self, sections: List[Dict]) -> List[Dict]:
        """
        Parse Wikipedia sections into ontology hints.
        
        Wikipedia TOC reveals natural sub-topics.
        
        Example for Roman Republic:
          1. Government and Politics
          2. Military (with subsections: Navy, Legions, etc.)
          3. Economy
          4. Society and Culture
          5. Wars and Conflicts
          
        Each section becomes a candidate for domain ontology concept.
        """
        parsed = []
        
        for section in sections:
            title = section.get("line", "")
            level = int(section.get("level", 2))
            
            # Skip lead section (level 0)
            if level == 0 or not title:
                continue
            
            # Only top-level sections (level 2) for high-level ontology
            if level == 2:
                parsed.append({
                    "title": title,
                    "level": level,
                    "suggested_facet": self._infer_facet_from_section(title)
                })
        
        return parsed
    
    def _infer_facet_from_section(self, section_title: str) -> str:
        """
        Infer likely facet from Wikipedia section title.
        
        Mapping section names to our 17 facets.
        """
        section_lower = section_title.lower()
        
        facet_mapping = {
            "military|war|army|navy|battle|combat|soldier": "Military",
            "government|politics|political|senate|congress|parliament|policy": "Political",
            "economic|economy|trade|commerce|business|finance|money|banking": "Economic",
            "social|society|culture|class|citizen|population|demography": "Social",
            "diplomacy|international|relations|treaty|ambassador|foreign": "Diplomatic",
            "religion|religious|church|faith|belief|priest|temple": "Religious",
            "legal|law|justice|court|crime|punishment": "Legal",
            "literature|literary|writing|author|poet|drama|play": "Literary",
            "art|artistic|sculpture|painting|architecture|monument": "Artistic",
            "science|scientific|technology|engineering|invention": "Technological",
            "philosophy|philosophical|thought|ethics|metaphysics": "Philosophical",
            "geography|geographic|region|territory|boundary|map": "Geographic",
            "people|person|biography|biography|individual|figure": "Biographical",
        }
        
        for keywords, facet in facet_mapping.items():
            if any(kw in section_lower for kw in keywords.split("|")):
                return facet
        
        return "Other"
    
    # ========================================================================
    # PHASE 5: Build Domain Ontology
    # ========================================================================
    
    def build_domain_ontology(self) -> Dict:
        """
        Build domain-specific ontology from Wikipedia sections.
        
        Output: Ontology JSON ready for agent initialization.
        """
        print(f"\n[PHASE 5] Building domain ontology...")
        
        ontology = {
            "qid": self.qid,
            "subject_concept_id": self.subject_concept_id,
            "wikipedia_title": self.wikipedia_title,
            "generated_date": datetime.now().isoformat(),
            "source": "Wikipedia TOC + Wikidata properties",
            
            # Facet grouping: organize sections by inferred facet
            "facets": {},
            
            # Flat list of all concepts
            "typical_sub_concepts": []
        }
        
        # Group sections by facet
        facet_groups = {}
        for section in self.wikipedia_sections:
            facet = section["suggested_facet"]
            if facet not in facet_groups:
                facet_groups[facet] = []
            facet_groups[facet].append(section["title"])
        
        # For each facet, create canonical concept entries
        concept_id = 1
        for facet, sections in facet_groups.items():
            ontology["facets"][facet] = {"concepts": len(sections)}
            
            for section_title in sections:
                concept = {
                    "id": concept_id,
                    "label": f"{self.wikipedia_title}--{section_title}",
                    "section_title": section_title,
                    "facet": facet,
                    "description": f"Wikipedia section: {section_title}",
                    "evidence_patterns": self._extract_keywords_from_section(section_title),
                    "confidence_baseline": 0.82,  # High confidence from Wikipedia structure
                    "authority_hints": [],  # Would be filled in by authority mapper
                    "typical_claims_count": [2, 5],
                    "wikipedia_source": True
                }
                
                ontology["typical_sub_concepts"].append(concept)
                concept_id += 1
        
        self.domain_ontology = ontology
        
        print(f"  ✓ Built domain ontology")
        print(f"    Facets represented: {list(facet_groups.keys())}")
        print(f"    Sub-concepts identified: {len(ontology['typical_sub_concepts'])}")
        
        return ontology
    
    def _extract_keywords_from_section(self, section_title: str) -> List[str]:
        """
        Extract keywords from section title for pattern matching.
        
        Used by agents to identify relevant claims.
        """
        # Simple: split title into meaningful tokens, lowercase
        keywords = []
        
        # Remove common words
        stopwords = {"and", "or", "the", "a", "of", "in", "to", "for", "by"}
        
        words = section_title.lower().split()
        for word in words:
            # Clean punctuation
            word = re.sub(r"[^\w]", "", word)
            
            if word and word not in stopwords and len(word) > 2:
                keywords.append(word)
        
        # Add some variations (singular/plural)
        expanded = keywords[:]
        for kw in keywords:
            if kw.endswith("s"):
                expanded.append(kw[:-1])  # Singular
            else:
                expanded.append(kw + "s")  # Plural
        
        return expanded
    
    # ========================================================================
    # MAIN EXECUTION
    # ========================================================================
    
    def train(self) -> Dict:
        """
        Execute full training pipeline.
        
        Returns: Complete domain ontology ready for agent initialization.
        """
        print(f"\n{'='*80}")
        print(f"AGENT TRAINING PIPELINE: {self.qid}")
        print(f"{'='*80}")
        
        # Phase 1: Wikidata properties
        self.fetch_wikidata_properties()
        
        # Phase 2: Backlinks
        self.fetch_wikidata_backlinks()
        
        # Phase 3: Generate subject_concept_id
        self.generate_subject_concept_id()
        
        # Phase 4: Wikipedia article + sections
        self.fetch_wikipedia_article()
        
        # Phase 5: Build ontology
        self.build_domain_ontology()
        
        print(f"\n{'='*80}")
        print(f"TRAINING COMPLETE")
        print(f"{'='*80}")
        print(f"Subject Concept ID: {self.subject_concept_id}")
        print(f"Wikipedia Title: {self.wikipedia_title}")
        print(f"Domain Ontology Sub-Concepts: {len(self.domain_ontology['typical_sub_concepts'])}")
        
        return self.domain_ontology
    
    def save_ontology(self, filepath: str) -> str:
        """Save domain ontology to JSON file"""
        with open(filepath, "w") as f:
            json.dump(self.domain_ontology, f, indent=2)
        
        print(f"\n✓ Saved ontology: {filepath}")
        return filepath


if __name__ == "__main__":
    import sys
    
    # Example: Train agent for Roman Republic
    qid = sys.argv[1] if len(sys.argv) > 1 else "Q17167"  # Roman Republic
    
    pipeline = AgentTrainingPipeline(qid=qid)
    ontology = pipeline.train()
    
    # Save for agent use
    pipeline.save_ontology(f"ontologies/{qid}_ontology.json")
    
    # Display results
    print(f"\nOntology Preview:")
    print(json.dumps(ontology, indent=2)[:1000])
