#!/usr/bin/env python3
"""
Subject Concept Agent Workflows - Complete Pipelines

Orchestrates multi-step workflows for:
1. Subject discovery (Wikidata → Period/Event candidates)
2. Subject classification (Perplexity facet analysis)
3. Subject enrichment (Authority federation)
4. Subject validation (Confidence scoring)
5. Subject approval (Human-in-loop review)
"""

import os
import json
import csv
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from neo4j import GraphDatabase
import requests


# ============================================================================
# SUBJECT CONCEPT DISCOVERY WORKFLOW
# ============================================================================

class SubjectConceptDiscoveryWorkflow:
    """
    Workflow: Discover new SubjectConcepts via Wikidata backlinks
    
    Steps:
    1. Query Wikidata for backlinks from seed QIDs
    2. Classify candidates (Period vs Event vs Concept)
    3. Filter by relevance and confidence
    4. Create proposals for human approval
    """
    
    def __init__(self,
                 neo4j_driver,
                 perplexity_api_key: Optional[str] = None,
                 output_dir: str = "output/subject_proposals"):
        self.driver = neo4j_driver
        self.perplexity_api_key = perplexity_api_key or os.getenv('PERPLEXITY_API_KEY')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Wikidata SPARQL endpoint
        self.wikidata_endpoint = "https://query.wikidata.org/sparql"
        
        # Perplexity API
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
    
    def discover_from_seed(self, 
                          seed_qids: List[str],
                          limit_per_seed: int = 100) -> List[Dict]:
        """
        Discover SubjectConcept candidates from seed QIDs
        
        Args:
            seed_qids: List of seed Wikidata QIDs
            limit_per_seed: Max candidates per seed
        
        Returns:
            List of candidate dicts
        """
        all_candidates = []
        
        for seed_qid in seed_qids:
            print(f"\n[DISCOVERY] Querying backlinks from {seed_qid}...")
            
            candidates = self._query_wikidata_backlinks(seed_qid, limit_per_seed)
            print(f"  Found {len(candidates)} candidates")
            
            all_candidates.extend(candidates)
        
        print(f"\n[DISCOVERY] Total candidates: {len(all_candidates)}")
        
        # Deduplicate by QID
        unique_candidates = {}
        for c in all_candidates:
            qid = c['qid']
            if qid not in unique_candidates:
                unique_candidates[qid] = c
        
        print(f"[DISCOVERY] Unique candidates: {len(unique_candidates)}")
        
        return list(unique_candidates.values())
    
    def _query_wikidata_backlinks(self, seed_qid: str, limit: int) -> List[Dict]:
        """Query Wikidata for items linking to seed QID"""
        
        sparql = f"""
        SELECT DISTINCT ?item ?itemLabel ?itemDescription 
               ?instanceOf ?instanceOfLabel
        WHERE {{
          ?item ?prop wd:{seed_qid} .
          OPTIONAL {{ ?item wdt:P31 ?instanceOf }}
          OPTIONAL {{ ?item schema:description ?itemDescription . 
                      FILTER(LANG(?itemDescription) = "en") }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT {limit}
        """
        
        headers = {
            'User-Agent': 'Chrystallum/1.0 (research project)',
            'Accept': 'application/sparql-results+json'
        }
        
        response = requests.get(
            self.wikidata_endpoint,
            params={'query': sparql, 'format': 'json'},
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        
        candidates = []
        for binding in data['results']['bindings']:
            item_qid = binding['item']['value'].split('/')[-1]
            candidates.append({
                'qid': item_qid,
                'label': binding.get('itemLabel', {}).get('value', ''),
                'description': binding.get('itemDescription', {}).get('value', ''),
                'instance_of': binding.get('instanceOfLabel', {}).get('value', ''),
                'instance_of_qid': binding.get('instanceOf', {}).get('value', '').split('/')[-1] if binding.get('instanceOf') else None,
                'seed_qid': seed_qid
            })
        
        return candidates
    
    def classify_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """
        Classify candidates using Perplexity
        
        Args:
            candidates: List of candidate dicts
        
        Returns:
            List of classified candidates with facets
        """
        classified = []
        
        for i, candidate in enumerate(candidates):
            print(f"\n[CLASSIFY] {i+1}/{len(candidates)}: {candidate['label']} ({candidate['qid']})")
            
            try:
                classification = self._classify_with_perplexity(candidate)
                classified.append({
                    **candidate,
                    **classification
                })
                print(f"  Type: {classification.get('subject_type')}")
                print(f"  Primary Facet: {classification.get('primary_facet')}")
                print(f"  Confidence: {classification.get('confidence')}")
            except Exception as e:
                print(f"  Error: {e}")
                classified.append({
                    **candidate,
                    'classification_error': str(e)
                })
        
        return classified
    
    def _classify_with_perplexity(self, candidate: Dict) -> Dict:
        """Classify a single Wikidata ENTITY candidate using Perplexity.

        IMPORTANT: This is ONLY for entity classification (Period|Event|SubjectConcept).
        Do NOT use for property-to-facet mapping. For unknown property labels, use:
        - CSV lookup: CSV/property_mappings/property_facet_mapping_HYBRID.csv
        - LLM resolver: llm_resolve_unknown_properties.resolve_property_with_llm()
        That returns {pid, facet, confidence} — never SubjectConcept proposals.
        """
        
        prompt = f"""
        Analyze this historical concept for classification:
        
        Title: {candidate['label']}
        Wikidata QID: {candidate['qid']}
        Description: {candidate.get('description', 'N/A')}
        Instance Of: {candidate.get('instance_of', 'N/A')}
        
        Questions:
        1. Is this a Period (extended time span), Event (specific occurrence), or SubjectConcept (thematic category)?
        2. What is the primary facet? Choose ONE from:
           ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, COMMUNICATION, CULTURAL, DEMOGRAPHIC,
           DIPLOMATIC, ECONOMIC, ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC,
           MILITARY, POLITICAL, RELIGIOUS, SCIENTIFIC, SOCIAL, TECHNOLOGICAL
        3. What are 0-3 related facets (secondary relevance)?
        4. Confidence score (0-1) that this should be a SubjectConcept?
        5. Brief justification (2-3 sentences)
        
        Respond in JSON format:
        {{
          "subject_type": "Period|Event|SubjectConcept",
          "primary_facet": "FACET_NAME",
          "related_facets": ["FACET1", "FACET2"],
          "confidence": 0.85,
          "justification": "..."
        }}
        """
        
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a scholarly historical classifier. Respond ONLY with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1  # Low temperature for consistent classification
        }
        
        response = requests.post(self.perplexity_url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        content = data['choices'][0]['message']['content']
        
        # Parse JSON from response
        # Strip markdown code blocks if present
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        classification = json.loads(content)
        
        return classification
    
    def create_proposals(self, classified_candidates: List[Dict]) -> Dict:
        """
        Create SubjectConcept proposals from classified candidates
        
        Args:
            classified_candidates: List of classified candidate dicts
        
        Returns:
            Proposals dict with metadata
        """
        proposals = {
            'proposal_type': 'SubjectConcept',
            'created_at': datetime.utcnow().isoformat(),
            'total_candidates': len(classified_candidates),
            'proposals': []
        }
        
        for candidate in classified_candidates:
            # Filter: Only SubjectConcepts with confidence >= 0.7
            if candidate.get('subject_type') == 'SubjectConcept' and candidate.get('confidence', 0) >= 0.7:
                subject_id = f"subj_{candidate['label'].lower().replace(' ', '_')}_{candidate['qid'].lower()}"
                
                proposal = {
                    'entity_type': 'SubjectConcept',
                    'subject_id': subject_id,
                    'properties': {
                        'subject_id': subject_id,
                        'label': candidate['label'],
                        'qid': candidate['qid'],
                        'primary_facet': candidate['primary_facet'],
                        'related_facets': candidate.get('related_facets', []),
                        'description': candidate.get('description', ''),
                        'status': 'pending_approval',
                        'proposed_by': 'discovery_workflow',
                        'proposed_at': datetime.utcnow().isoformat(),
                        'confidence': candidate['confidence'],
                        'justification': candidate.get('justification', ''),
                        'seed_qid': candidate['seed_qid']
                    }
                }
                
                proposals['proposals'].append(proposal)
        
        proposals['proposal_count'] = len(proposals['proposals'])
        
        return proposals
    
    def save_proposals(self, proposals: Dict, filename: Optional[str] = None) -> str:
        """Save proposals to JSON file"""
        
        if not filename:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"subject_proposals_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(proposals, f, indent=2, ensure_ascii=False)
        
        print(f"\n[SAVE] Proposals saved to: {filepath}")
        print(f"  Total proposals: {proposals['proposal_count']}")
        
        return str(filepath)
    
    def run_full_workflow(self,
                         seed_qids: List[str],
                         limit_per_seed: int = 100,
                         save: bool = True) -> Dict:
        """
        Run complete discovery workflow
        
        Args:
            seed_qids: List of seed Wikidata QIDs
            limit_per_seed: Max candidates per seed
            save: Save proposals to file
        
        Returns:
            Proposals dict
        """
        print("=" * 80)
        print("SUBJECT CONCEPT DISCOVERY WORKFLOW")
        print("=" * 80)
        
        # Step 1: Discover candidates
        candidates = self.discover_from_seed(seed_qids, limit_per_seed)
        
        # Step 2: Classify candidates
        classified = self.classify_candidates(candidates)
        
        # Step 3: Create proposals
        proposals = self.create_proposals(classified)
        
        # Step 4: Save proposals
        if save:
            self.save_proposals(proposals)
        
        print("\n" + "=" * 80)
        print("WORKFLOW COMPLETE")
        print("=" * 80)
        print(f"Total candidates discovered: {len(candidates)}")
        print(f"Classified candidates: {len(classified)}")
        print(f"Proposals created: {proposals['proposal_count']}")
        
        return proposals


# ============================================================================
# SUBJECT CONCEPT ENRICHMENT WORKFLOW
# ============================================================================

class SubjectConceptEnrichmentWorkflow:
    """
    Workflow: Enrich existing SubjectConcepts with authority federation
    
    Steps:
    1. Query Neo4j for SubjectConcepts missing authorities
    2. Query Wikidata for additional metadata
    3. Match to LCSH/FAST/LCC authorities (local files)
    4. Update SubjectConcept properties
    5. Create authority relationship links
    """
    
    def __init__(self,
                 neo4j_driver,
                 lcsh_data_path: Optional[str] = None,
                 fast_data_path: Optional[str] = None,
                 lcc_data_path: Optional[str] = None):
        self.driver = neo4j_driver
        
        # Authority data paths
        self.lcsh_path = Path(lcsh_data_path) if lcsh_data_path else Path("LCSH/skos_subjects")
        self.fast_path = Path(fast_data_path) if fast_data_path else Path("Python/fast/key/FASTTopical_parsed.csv")
        self.lcc_path = Path(lcc_data_path) if lcc_data_path else Path("Subjects/lcc_flat.csv")
        
        # Load authority indexes
        self.fast_index = self._load_fast_index()
        self.lcc_index = self._load_lcc_index()
    
    def _load_fast_index(self) -> Dict:
        """Load FAST authority index"""
        index = {}
        
        if not self.fast_path.exists():
            print(f"[WARN] FAST data not found at {self.fast_path}")
            return index
        
        with open(self.fast_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                fast_id = row.get('fast_id', '').strip()
                label = row.get('preferred_label', '').strip().lower()
                
                if fast_id and label:
                    index[label] = {
                        'fast_id': fast_id,
                        'preferred_label': row.get('preferred_label', ''),
                        'alt_labels': row.get('alt_labels', '').split('|') if row.get('alt_labels') else []
                    }
        
        print(f"[LOAD] FAST index: {len(index)} entries")
        return index
    
    def _load_lcc_index(self) -> Dict:
        """Load LCC classification index"""
        index = {}
        
        if not self.lcc_path.exists():
            print(f"[WARN] LCC data not found at {self.lcc_path}")
            return index
        
        with open(self.lcc_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row.get('code', '').strip()
                label = row.get('label', '').strip().lower()
                
                if code and label:
                    index[label] = {
                        'code': code,
                        'label': row.get('label', '')
                    }
        
        print(f"[LOAD] LCC index: {len(index)} entries")
        return index
    
    def enrich_subject_concept(self, subject_id: str) -> Dict:
        """
        Enrich a single SubjectConcept
        
        Args:
            subject_id: SubjectConcept ID
        
        Returns:
            Enrichment result dict
        """
        # Get SubjectConcept from Neo4j
        with self.driver.session() as session:
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: $subject_id})
                RETURN sc
            """, subject_id=subject_id)
            
            record = result.single()
            if not record:
                raise ValueError(f"SubjectConcept {subject_id} not found")
            
            sc = dict(record['sc'])
        
        enrichment = {
            'subject_id': subject_id,
            'label': sc.get('label'),
            'enrichments': []
        }
        
        # Match to FAST
        if not sc.get('fast_id'):
            fast_match = self._match_fast(sc)
            if fast_match:
                enrichment['enrichments'].append({
                    'type': 'FAST',
                    'fast_id': fast_match['fast_id'],
                    'preferred_label': fast_match['preferred_label']
                })
        
        # Match to LCC
        if not sc.get('lcc_class'):
            lcc_match = self._match_lcc(sc)
            if lcc_match:
                enrichment['enrichments'].append({
                    'type': 'LCC',
                    'code': lcc_match['code'],
                    'label': lcc_match['label']
                })
        
        return enrichment
    
    def _match_fast(self, subject_concept: Dict) -> Optional[Dict]:
        """Match SubjectConcept to FAST authority"""
        label = subject_concept.get('label', '').lower()
        
        # Exact match
        if label in self.fast_index:
            return self.fast_index[label]
        
        # Fuzzy match (simplified - could use better fuzzy matching)
        for fast_label, fast_data in self.fast_index.items():
            if label in fast_label or fast_label in label:
                return fast_data
        
        return None
    
    def _match_lcc(self, subject_concept: Dict) -> Optional[Dict]:
        """Match SubjectConcept to LCC classification"""
        label = subject_concept.get('label', '').lower()
        
        # Exact match
        if label in self.lcc_index:
            return self.lcc_index[label]
        
        # Fuzzy match
        for lcc_label, lcc_data in self.lcc_index.items():
            if label in lcc_label or lcc_label in label:
                return lcc_data
        
        return None


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, PERPLEXITY_API_KEY
    
    # Initialize Neo4j driver
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )
    
    print("=" * 80)
    print("SUBJECT CONCEPT WORKFLOWS - Example Usage")
    print("=" * 80)
    print()
    
    # Discovery Workflow
    print("DISCOVERY WORKFLOW")
    print("-" * 80)
    
    discovery = SubjectConceptDiscoveryWorkflow(
        neo4j_driver=driver,
        perplexity_api_key=PERPLEXITY_API_KEY
    )
    
    # Example: Discover subjects related to Roman Republic
    seed_qids = [
        'Q17167',   # Roman Republic
        'Q1747689', # Ancient Rome
        'Q11768'    # Ancient Greece
    ]
    
    # Uncomment to run discovery
    # proposals = discovery.run_full_workflow(seed_qids, limit_per_seed=50)
    
    print("Discovery workflow ready")
    print(f"  Seed QIDs: {seed_qids}")
    print(f"  Output: output/subject_proposals/")
    print()
    
    # Enrichment Workflow
    print("ENRICHMENT WORKFLOW")
    print("-" * 80)
    
    enrichment = SubjectConceptEnrichmentWorkflow(
        neo4j_driver=driver
    )
    
    print("Enrichment workflow ready")
    print(f"  FAST index: {len(enrichment.fast_index)} entries")
    print(f"  LCC index: {len(enrichment.lcc_index)} entries")
    print()
    
    driver.close()
    print("✓ Workflows initialized")
