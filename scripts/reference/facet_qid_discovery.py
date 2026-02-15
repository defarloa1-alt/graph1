"""
Facet Canonical Category Discovery from Wikipedia + Wikidata

Instead of manually defining canonical categories per facet, this system:
1. Takes a discipline QID (e.g., Q8134 = Economics)
2. Fetches Wikipedia article → Extracts major concepts
3. Fetches Wikidata properties → Gets formal relationships and properties
4. Merges into canonical concept categories
5. Creates FacetReference automatically

Example:
    Economics (Q8134)
    ├─ Wikipedia: "Supply and demand" section → ConceptCategory
    ├─ Wikipedia: "Production" section → ConceptCategory
    ├─ Wikipedia: "Macroeconomics" section → ConceptCategory
    ├─ Wikipedia: "Microeconomics" section → ConceptCategory
    ├─ Wikipedia: "Finance and Trade" section → ConceptCategory
    └─ Wikidata Q8134 properties → Validates relationships
"""

import requests
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConceptCategory:
    """Represents a major concept category within a discipline"""
    id: str
    label: str
    description: str
    key_topics: List[str]
    wikipedia_section: Optional[str] = None
    wikidata_properties: Optional[Dict] = None
    confidence: float = 0.0  # Confidence score from Wikipedia/Wikidata alignment


@dataclass
class DiscoveredFacet:
    """Represents a discipline facet discovered from Wikipedia + Wikidata"""
    facet_name: str
    facet_qid: str
    wikipedia_url: str
    wikidata_properties: Dict
    concept_categories: List[ConceptCategory]
    extraction_method: str  # "wikipedia_sections", "wikidata_properties", "hybrid"
    confidence_score: float


class FacetQIDDiscovery:
    """Discover canonical categories from Wikipedia + Wikidata for a discipline QID"""
    
    WIKIPEDIA_BASE = "https://en.wikipedia.org/w/api.php"
    WIKIDATA_BASE = "https://www.wikidata.org/w/api.php"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FacetQIDDiscovery/1.0 (+http://example.com)'
        })
    
    def get_wikidata_entity(self, qid: str) -> Dict:
        """Fetch Wikidata entity for a QID"""
        logger.info(f"Fetching Wikidata {qid}...")
        
        params = {
            'action': 'wbgetentities',
            'ids': qid,
            'format': 'json',
            'languages': 'en'
        }
        
        response = self.session.get(self.WIKIDATA_BASE, params=params)
        response.raise_for_status()
        
        data = response.json()
        if qid in data['entities']:
            return data['entities'][qid]
        return {}
    
    def get_wikipedia_title_from_qid(self, wikidata_entity: Dict) -> Optional[str]:
        """Extract Wikipedia article title from Wikidata entity"""
        if 'sitelinks' not in wikidata_entity:
            return None
        
        enwiki = wikidata_entity.get('sitelinks', {}).get('enwiki')
        if enwiki:
            return enwiki['title']
        return None
    
    def get_wikipedia_article(self, title: str) -> Dict:
        """Fetch Wikipedia article by title"""
        logger.info(f"Fetching Wikipedia article: {title}...")
        
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'extracts|sections',
            'explaintext': True,
            'format': 'json',
            'redirects': True
        }
        
        response = self.session.get(self.WIKIPEDIA_BASE, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def extract_sections_from_wikipedia(self, wiki_title: str) -> List[Dict]:
        """Extract major sections and their content from Wikipedia"""
        logger.info(f"Extracting sections from {wiki_title}...")
        
        params = {
            'action': 'query',
            'titles': wiki_title,
            'prop': 'sections',
            'format': 'json'
        }
        
        response = self.session.get(self.WIKIPEDIA_BASE, params=params)
        response.raise_for_status()
        
        data = response.json()
        pages = data.get('query', {}).get('pages', {})
        
        sections = []
        for page in pages.values():
            if 'sections' in page:
                sections = page['sections']
                break
        
        # Filter to major sections (level 2) that are meaningful
        major_sections = [
            s for s in sections 
            if s.get('level') == '2' and s.get('line') and 'edit' in s
        ]
        
        return major_sections
    
    def extract_section_content(self, wiki_title: str, section_title: str) -> str:
        """Extract content of a specific section"""
        params = {
            'action': 'query',
            'titles': wiki_title,
            'prop': 'extracts',
            'explaintext': True,
            'format': 'json'
        }
        
        response = self.session.get(self.WIKIPEDIA_BASE, params=params)
        response.raise_for_status()
        
        data = response.json()
        pages = data.get('query', {}).get('pages', {})
        
        for page in pages.values():
            extract = page.get('extract', '')
            if section_title in extract:
                # Simple extraction - find section and next section
                start = extract.find(section_title)
                next_section = extract.find('\n== ', start + 1)
                if next_section == -1:
                    return extract[start:]
                return extract[start:next_section]
        
        return ""
    
    def get_wikidata_properties(self, wikidata_entity: Dict) -> Dict:
        """Extract meaningful properties from Wikidata entity"""
        properties = {}
        
        # Extract claims (properties)
        if 'claims' in wikidata_entity:
            claims = wikidata_entity['claims']
            
            # P31 = instance of (what is it?)
            if 'P31' in claims:
                properties['instance_of'] = [
                    c.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id', '')
                    for c in claims['P31']
                ]
            
            # P279 = subclass of (what is it a type of?)
            if 'P279' in claims:
                properties['subclass_of'] = [
                    c.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id', '')
                    for c in claims['P279']
                ]
            
            # P361 = part of (what is it part of?)
            if 'P361' in claims:
                properties['part_of'] = [
                    c.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id', '')
                    for c in claims['P361']
                ]
            
            # P625 = coordinate location
            if 'P625' in claims:
                properties['has_coordinate_location'] = True
            
            # P580 = start time
            if 'P580' in claims:
                properties['has_start_time'] = True
        
        return properties
    
    def extract_keywords_from_text(self, text: str, section_title: str = "") -> Tuple[List[str], float]:
        """
        Extract meaningful keywords from text.
        Returns (keywords, confidence_score)
        """
        # Clean text
        text = re.sub(r'\[\d+\]', '', text)  # Remove citation markers
        text = re.sub(r'\n+', ' ', text)  # Join lines
        
        # Look for bold terms (concepts mentioned explicitly)
        bold_terms = re.findall(r"'''([^']+)'''", text)
        
        # Look for common phrase patterns in this section
        phrases = []
        
        # Simple keyword extraction - words that appear frequently
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        word_freq = Counter(words)
        
        # Get top meaningful phrases (excluding very common ones)
        common = {'The', 'This', 'That', 'These', 'Those', 'Which', 'From', 'Were'}
        meaningful_words = [w for w, count in word_freq.most_common(20) if w not in common and count > 1]
        
        # Combine bold terms and meaningful words
        keywords = []
        
        # Add bold terms (explicitly highlighted)
        keywords.extend([t.lower() for t in bold_terms if len(t) > 3])
        
        # Add meaningful phrases
        keywords.extend([w.lower() for w in meaningful_words])
        
        # Add section title components as keywords
        if section_title:
            title_words = section_title.lower().split()
            keywords.extend([w for w in title_words if len(w) > 3])
        
        # Remove duplicates and sort by frequency
        keywords = list(set(keywords))
        
        # Confidence based on how much content we extracted
        confidence = min(len(text) / 500, 1.0)  # Normalize to 0-1
        
        return keywords, confidence
    
    def discover_from_wikipedia_sections(
        self, 
        wiki_title: str, 
        max_sections: int = 5
    ) -> List[ConceptCategory]:
        """
        Discover concept categories from Wikipedia article structure.
        Uses major sections as concept boundaries.
        """
        logger.info(f"Discovering concepts from Wikipedia sections in {wiki_title}...")
        
        sections = self.extract_sections_from_wikipedia(wiki_title)
        
        # Filter out non-conceptual sections
        exclude_sections = {'See also', 'References', 'External links', 'Notes', 'Further reading', 'Footnotes', 'History'}
        sections = [s for s in sections if s.get('line') not in exclude_sections]
        
        # Limit to major conceptual sections
        sections = sections[:max_sections]
        
        concept_categories = []
        
        for idx, section in enumerate(sections):
            section_title = section.get('line', f'Concept {idx}')
            
            try:
                # Extract content for this section
                content = self.extract_section_content(wiki_title, section_title)
                
                if not content or len(content) < 50:
                    continue
                
                # Extract keywords from section
                keywords, confidence = self.extract_keywords_from_text(content, section_title)
                
                # Create concept category
                category = ConceptCategory(
                    id=f"concept_{idx:03d}",
                    label=section_title.strip('=').strip(),
                    description=content[:200] + "..." if len(content) > 200 else content,
                    key_topics=keywords[:10],  # Top 10 keywords
                    wikipedia_section=section_title,
                    confidence=confidence
                )
                
                concept_categories.append(category)
                logger.info(f"  + {category.label} ({len(keywords)} keywords, conf={confidence:.2f})")
            
            except Exception as e:
                logger.warning(f"  - Failed to extract section {section_title}: {e}")
                continue
        
        return concept_categories
    
    def discover_from_wikidata_properties(
        self, 
        wikidata_entity: Dict,
        wiki_categories: Optional[List[str]] = None
    ) -> List[ConceptCategory]:
        """
        Discover concept categories from Wikidata properties and relationships.
        """
        logger.info("Discovering concepts from Wikidata properties...")
        
        concept_categories = []
        props = self.get_wikidata_properties(wikidata_entity)
        
        # Create concept categories from properties
        category_idx = 0
        
        # Subclass of → what types exist?
        if 'subclass_of' in props:
            subclasses = props['subclass_of']
            if subclasses:
                category = ConceptCategory(
                    id=f"wikidata_subclass_{category_idx}",
                    label="Types and Branches",
                    description=f"Major subcategories: {subclasses}",
                    key_topics=subclasses[:5],
                    wikidata_properties=props,
                    confidence=0.8
                )
                concept_categories.append(category)
                category_idx += 1
        
        # Part of → broader context
        if 'part_of' in props:
            parts = props['part_of']
            if parts:
                category = ConceptCategory(
                    id=f"wikidata_partof_{category_idx}",
                    label="Broader Contexts",
                    description=f"Part of: {parts}",
                    key_topics=parts[:5],
                    wikidata_properties=props,
                    confidence=0.7
                )
                concept_categories.append(category)
        
        return concept_categories
    
    def discover_facet_canonical_categories(
        self, 
        facet_qid: str,
        use_wikipedia: bool = True,
        use_wikidata: bool = True
    ) -> DiscoveredFacet:
        """
        Main discovery function.
        Takes a discipline QID and returns discovered canonical categories.
        
        Args:
            facet_qid: Wikidata QID of the discipline (e.g., "Q8134" for Economics)
            use_wikipedia: Whether to extract from Wikipedia sections
            use_wikidata: Whether to extract from Wikidata properties
        
        Returns:
            DiscoveredFacet with concept_categories automatically discovered
        """
        logger.info(f"\n=== DISCOVERING FACET FROM QID {facet_qid} ===\n")
        
        # Step 1: Get Wikidata entity
        wikidata_entity = self.get_wikidata_entity(facet_qid)
        
        if not wikidata_entity:
            raise ValueError(f"QID {facet_qid} not found in Wikidata")
        
        facet_name = wikidata_entity.get('labels', {}).get('en', {}).get('value', facet_qid)
        logger.info(f"Facet name: {facet_name}")
        
        # Step 2: Get Wikipedia article title
        wiki_title = self.get_wikipedia_title_from_qid(wikidata_entity)
        wikipedia_url = f"https://en.wikipedia.org/wiki/{wiki_title}" if wiki_title else ""
        
        logger.info(f"Wikipedia: {wikipedia_url}")
        
        concept_categories = []
        extraction_method = "none"
        
        # Step 3: Extract from Wikipedia
        if use_wikipedia and wiki_title:
            try:
                wiki_concepts = self.discover_from_wikipedia_sections(wiki_title)
                concept_categories.extend(wiki_concepts)
                extraction_method = "wikipedia_sections"
                logger.info(f"✓ Extracted {len(wiki_concepts)} concepts from Wikipedia")
            except Exception as e:
                logger.warning(f"✗ Wikipedia extraction failed: {e}")
        
        # Step 4: Extract from Wikidata properties
        if use_wikidata:
            try:
                wikidata_concepts = self.discover_from_wikidata_properties(wikidata_entity)
                concept_categories.extend(wikidata_concepts)
                extraction_method = "hybrid" if extraction_method == "wikipedia_sections" else "wikidata_properties"
                logger.info(f"✓ Extracted {len(wikidata_concepts)} concepts from Wikidata")
            except Exception as e:
                logger.warning(f"✗ Wikidata extraction failed: {e}")
        
        # Step 5: Calculate overall confidence
        if concept_categories:
            avg_confidence = sum(c.confidence for c in concept_categories) / len(concept_categories)
        else:
            avg_confidence = 0.0
        
        discovered_facet = DiscoveredFacet(
            facet_name=facet_name,
            facet_qid=facet_qid,
            wikipedia_url=wikipedia_url,
            wikidata_properties=self.get_wikidata_properties(wikidata_entity),
            concept_categories=concept_categories,
            extraction_method=extraction_method,
            confidence_score=avg_confidence
        )
        
        logger.info(f"\n✓ DISCOVERY COMPLETE: {len(concept_categories)} concept categories")
        logger.info(f"  Average confidence: {avg_confidence:.2f}")
        logger.info(f"  Method: {extraction_method}\n")
        
        return discovered_facet


# Example usage and testing
if __name__ == "__main__":
    discovery = FacetQIDDiscovery()
    
    # Test with various discipline QIDs
    test_qids = [
        ("Q8134", "Economics"),
        ("Q1300", "War / Military"),
        ("Q7163", "Politics"),
    ]
    
    for qid, label in test_qids:
        try:
            print(f"\n{'='*60}")
            print(f"DISCOVERING: {label} ({qid})")
            print(f"{'='*60}\n")
            
            facet = discovery.discover_facet_canonical_categories(qid)
            
            # Print results
            print(f"\n{'RESULTS':^60}")
            print(f"{'='*60}\n")
            print(f"Facet: {facet.facet_name}")
            print(f"QID: {facet.facet_qid}")
            print(f"Wikipedia: {facet.wikipedia_url}")
            print(f"Method: {facet.extraction_method}")
            print(f"Confidence: {facet.confidence_score:.2f}")
            print(f"\nConcept Categories ({len(facet.concept_categories)}):\n")
            
            for idx, category in enumerate(facet.concept_categories, 1):
                print(f"{idx}. {category.label}")
                print(f"   Keywords: {', '.join(category.key_topics[:5])}")
                print(f"   Confidence: {category.confidence:.2f}")
                if category.wikipedia_section:
                    print(f"   Source: Wikipedia section")
                else:
                    print(f"   Source: Wikidata properties")
                print()
        
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
