#!/usr/bin/env python3
"""
EXAMPLE: Agent Training for Roman Republic
===========================================

Demonstrates the complete training pipeline:
1. QID Q17167 (Roman Republic)
2. Fetch Wikidata properties + backlinks
3. Generate subject_concept_id
4. Parse Wikipedia TOC for "Government", "Military", "Economy", etc.
5. Auto-discover sub-concepts grounded in Wikipedia structure

Then shows agent initialization with trained ontology.
"""

import json
from datetime import datetime


# Simulated Wikidata response for Q17167
WIKIDATA_Q17167 = {
    "Q17167": {
        "labels": {
            "en": {"value": "Roman Republic"}
        },
        "descriptions": {
            "en": {"value": "period of ancient Roman civilization before the empire"}
        },
        "claims": {
            "P580": "-509-01-01T00:00:00Z",      # start time
            "P582": "-27-01-01T00:00:00Z",       # end time
            "P131": "Q38",                        # located in (Italy)
            "P625": "41.9028, 12.4964",          # geographic center
            "P910": "Q7032956",                   # main category
            "P17": "Q38",                         # country (Italy)
            "P30": "Q46",                         # continent (Europe)
            "P1566": "3169070",                   # GeoNames ID
        }
    }
}

# Simulated Wikipedia TOC for "Roman Republic"
WIKIPEDIA_SECTIONS_ROMAN_REPUBLIC = [
    {"level": 2, "line": "Early history and development"},
    {"level": 2, "line": "Government"},
    {"level": 3, "line": "Magistrates"},
    {"level": 3, "line": "Senate"},
    {"level": 3, "line": "Assemblies"},
    {"level": 2, "line": "Military"},
    {"level": 3, "line": "Legions"},
    {"level": 3, "line": "Naval warfare"},
    {"level": 2, "line": "Economy"},
    {"level": 3, "line": "Agriculture and land"},
    {"level": 3, "line": "Trade and commerce"},
    {"level": 3, "line": "Coinage"},
    {"level": 2, "line": "Society and culture"},
    {"level": 3, "line": "Class structure"},
    {"level": 3, "line": "Religion"},
    {"level": 3, "line": "Art and literature"},
    {"level": 2, "line": "Wars and conflicts"},
    {"level": 3, "line": "Punic Wars"},
    {"level": 3, "line": "Macedonian Wars"},
    {"level": 3, "line": "Civil Wars"},
]

# Simulated Wikidata backlinks (entities related to Q17167)
WIKIDATA_BACKLINKS_Q17167 = [
    {"qid": "Q186214", "label": "First Punic War", "property": "P276", "relation": "location"},
    {"qid": "Q3105", "label": "Punic Wars", "property": "P131", "relation": "part_of"},
    {"qid": "Q1048", "label": "Julius Caesar", "property": "P17", "relation": "associated_with"},
    {"qid": "Q1048", "label": "Julius Caesar", "property": "P19", "relation": "born_in"},
    {"qid": "Q12098", "label": "Roman Empire", "property": "P155", "relation": "follows"},
    {"qid": "Q83", "label": "Ancient Rome", "property": "P155", "relation": "follows"},
]


def simulate_training_phase_1():
    """PHASE 1: Fetch Wikidata properties"""
    print("\n" + "="*80)
    print("PHASE 1: Fetch Wikidata Properties")
    print("="*80)
    
    entity = WIKIDATA_Q17167["Q17167"]
    
    print(f"\nQID: Q17167")
    print(f"Label: {entity['labels']['en']['value']}")
    print(f"Description: {entity['descriptions']['en']['value']}")
    print(f"\nKey Properties:")
    
    for prop_id, value in entity["claims"].items():
        prop_name = {
            "P580": "start time",
            "P582": "end time",
            "P131": "located in",
            "P625": "geographic center",
            "P910": "main category",
            "P17": "country",
            "P30": "continent",
            "P1566": "GeoNames ID",
        }.get(prop_id, prop_id)
        
        print(f"  {prop_id} ({prop_name}): {value}")
    
    return entity["claims"]


def simulate_training_phase_2():
    """PHASE 2: Fetch Wikidata backlinks"""
    print("\n" + "="*80)
    print("PHASE 2: Fetch Wikidata Backlinks (Related Entities)")
    print("="*80)
    
    print(f"\nEntities related to Q17167 (Roman Republic):\n")
    
    for i, link in enumerate(WIKIDATA_BACKLINKS_Q17167, 1):
        print(f"{i}. {link['label']} ({link['qid']})")
        print(f"   Relation: {link['property']} ({link['relation']})")
    
    return WIKIDATA_BACKLINKS_Q17167


def simulate_training_phase_3(properties):
    """PHASE 3: Generate canonical subject_concept_id"""
    print("\n" + "="*80)
    print("PHASE 3: Generate Canonical subject_concept_id")
    print("="*80)
    
    import hashlib
    
    qid = "Q17167"
    start_time = properties["P580"]
    end_time = properties["P582"]
    location = properties["P131"]
    
    # Build canonical composite
    canonical = f"{qid}|start:{start_time}|end:{end_time}|location:{location}"
    
    print(f"\nCanonical Composite:")
    print(f"  {canonical}")
    
    # Hash it
    hash_obj = hashlib.sha256(canonical.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()[:12]
    
    subject_concept_id = f"subj_{hash_hex}"
    
    print(f"\nSHA256 Hash (first 12 chars): {hash_hex}")
    print(f"Subject Concept ID: {subject_concept_id}")
    print(f"\n✓ Idempotent: Same properties always generate same ID")
    print(f"✓ Traceable: Different properties would generate different ID")
    
    return subject_concept_id


def simulate_training_phase_4():
    """PHASE 4: Parse Wikipedia TOC for sections"""
    print("\n" + "="*80)
    print("PHASE 4: Parse Wikipedia TOC (Sections & Subsections)")
    print("="*80)
    
    wikipedia_title = "Roman Republic"
    
    print(f"\nWikipedia Article: {wikipedia_title}")
    print(f"\nTable of Contents Structure:")
    
    # Group by level
    level_2_sections = [s for s in WIKIPEDIA_SECTIONS_ROMAN_REPUBLIC if s["level"] == 2]
    
    for section in level_2_sections:
        print(f"\n  {section['line']}")
        
        # Find subsections
        subsections = [s for s in WIKIPEDIA_SECTIONS_ROMAN_REPUBLIC 
                       if s["level"] == 3 and 
                       WIKIPEDIA_SECTIONS_ROMAN_REPUBLIC.index(s) > 
                       WIKIPEDIA_SECTIONS_ROMAN_REPUBLIC.index(section)]
        
        for subsection in subsections[:3]:  # Show first 3
            print(f"    - {subsection['line']}")
    
    return level_2_sections


def infer_facet_from_section(section_title):
    """Infer facet from Wikipedia section title"""
    section_lower = section_title.lower()
    
    facet_mapping = {
        "government|magistrate|senate|assembl": "Political",
        "military|legion|war|naval|conflict": "Military",
        "economy|trade|commerce|coinage|agriculture": "Economic",
        "society|culture|class|religion|literature": "Social",
    }
    
    for keywords, facet in facet_mapping.items():
        if any(kw in section_lower for kw in keywords.split("|")):
            return facet
    
    return "Other"


def extract_keywords(section_title):
    """Extract keywords for pattern matching"""
    import re
    
    stopwords = {"and", "or", "the", "a", "of", "in", "to", "for", "by"}
    
    words = section_title.lower().split()
    keywords = []
    
    for word in words:
        word = re.sub(r"[^\w]", "", word)
        if word and word not in stopwords and len(word) > 2:
            keywords.append(word)
            # Add plural/singular variants
            if word.endswith("s"):
                keywords.append(word[:-1])
            else:
                keywords.append(word + "s")
    
    return list(set(keywords))  # Deduplicate


def simulate_training_phase_5(subject_concept_id, sections):
    """PHASE 5: Build domain ontology from sections"""
    print("\n" + "="*80)
    print("PHASE 5: Build Domain Ontology")
    print("="*80)
    
    wikipedia_title = "Roman Republic"
    
    print(f"\nInferring facets and building sub-concepts:\n")
    
    ontology = {
        "qid": "Q17167",
        "subject_concept_id": subject_concept_id,
        "wikipedia_title": wikipedia_title,
        "generated_date": datetime.now().isoformat(),
        "source": "Wikipedia TOC + Wikidata properties",
        "facets": {},
        "typical_sub_concepts": []
    }
    
    concept_id = 1
    facet_groups = {}
    
    for section in sections:
        facet = infer_facet_from_section(section["line"])
        
        if facet not in facet_groups:
            facet_groups[facet] = []
            ontology["facets"][facet] = {"concepts": 0}
        
        facet_groups[facet].append(section["line"])
        
        # Create concept entry
        concept = {
            "id": concept_id,
            "label": f"{wikipedia_title}--{section['line']}",
            "section_title": section["line"],
            "facet": facet,
            "description": f"Wikipedia section: {section['line']}",
            "evidence_patterns": extract_keywords(section["line"]),
            "confidence_baseline": 0.82,
            "authority_hints": [],
            "typical_claims_count": [2, 5],
            "wikipedia_source": True
        }
        
        ontology["typical_sub_concepts"].append(concept)
        ontology["facets"][facet]["concepts"] += 1
        
        concept_id += 1
    
    print(f"Domain Facets Identified:")
    for facet, data in ontology["facets"].items():
        print(f"  {facet}: {data['concepts']} sub-concepts")
    
    print(f"\nSample Sub-Concepts:")
    for concept in ontology["typical_sub_concepts"][:5]:
        print(f"\n  {concept['id']}. {concept['label']}")
        print(f"     Facet: {concept['facet']}")
        print(f"     Evidence Patterns: {', '.join(concept['evidence_patterns'][:4])}")
        print(f"     Confidence: {concept['confidence_baseline']}")
    
    print(f"\n✓ Total sub-concepts discovered: {len(ontology['typical_sub_concepts'])}")
    
    return ontology


def agent_initialization_demo(ontology):
    """Demonstrate agent initialization with trained ontology"""
    print("\n" + "="*80)
    print("AGENT INITIALIZATION: EconomicAgent for Roman Republic")
    print("="*80)
    
    print(f"""
Agent Configuration:
  - Agent Type: EconomicAgent
  - Civilization: Roman Republic
  - Time Period: Period 2 (200 BCE - 100 BCE)
  - Facet: Economic
  - Training Status: ✓ Self-Trained via Wikipedia
  
Trained Domain Knowledge:
  - Subject Concept ID: {ontology['subject_concept_id']}
  - Wikipedia Title: {ontology['wikipedia_title']}
  - Recognized Economic Sub-Concepts: {ontology['facets'].get('Economic', {}).get('concepts', 0)}
  
Trained Sub-Concepts (Economic Facet):
""")
    
    economic_concepts = [c for c in ontology["typical_sub_concepts"] if c["facet"] == "Economic"]
    
    for concept in economic_concepts:
        print(f"""
  • {concept['label']}
    Evidence Patterns: {', '.join(concept['evidence_patterns'])}
    Confidence: {concept['confidence_baseline']}
    Wikipedia Grounding: {concept['section_title']}""")
    
    print(f"""
What This Enables:
  ✓ Agent understands Roman economic structure via Wikipedia
  ✓ Agent recognizes trade, agriculture, coinage as sub-concepts
  ✓ Agent can pattern-match findings against known categories
  ✓ Agent can propose sub-concepts with high confidence

Example: Finding Analysis
  Input Finding: "Evidence of large-scale grain trade and commercial networks"
  Pattern Matching:
    - Searched "Trade and commerce" concept
    - Matched patterns: ["trade", "commerce", "grain"]
    - Match score: 3/4 = 75% ✓
  
  Output Proposal:
    - Create sub-concept: "Roman Republic--Trade and Commerce"
    - Confidence: MIN(0.88 finding, 0.82 concept) = 0.82
    - Evidence: Found trade networks, commercial patterns
    - Wikipedia Section: Trade and commerce
""")


def save_ontology_demo(ontology):
    """Demonstrate saving ontology to JSON"""
    print("\n" + "="*80)
    print("ONTOLOGY OUTPUT")
    print("="*80)
    
    print(f"\nSaving to: ontologies/Q17167_ontology.json")
    
    # Show JSON structure
    json_preview = {
        "qid": ontology["qid"],
        "subject_concept_id": ontology["subject_concept_id"],
        "wikipedia_title": ontology["wikipedia_title"],
        "generated_date": ontology["generated_date"],
        "facets": ontology["facets"],
        "typical_sub_concepts_count": len(ontology["typical_sub_concepts"]),
        "sample_concepts": ontology["typical_sub_concepts"][:2]
    }
    
    print(json.dumps(json_preview, indent=2))
    
    print(f"\n✓ Full ontology saved with {len(ontology['typical_sub_concepts'])} sub-concepts")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                   AGENT TRAINING PIPELINE DEMO                                ║
║                 Self-Bootstrapped Ontology from Wikipedia                     ║
║                                                                               ║
║ Training: Q17167 (Roman Republic)                                            ║
║ Output: Domain ontology for facet-specific agents                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Execute training pipeline
    properties = simulate_training_phase_1()
    backlinks = simulate_training_phase_2()
    subject_concept_id = simulate_training_phase_3(properties)
    sections = simulate_training_phase_4()
    ontology = simulate_training_phase_5(subject_concept_id, sections)
    
    # Demonstrate usage
    agent_initialization_demo(ontology)
    
    # Show output
    save_ontology_demo(ontology)
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         NEXT STEPS                                            ║
├───────────────────────────────────────────────────────────────────────────────┤
║ 1. Execute agent_training_pipeline.py Q17167                                 ║
║    → Fetches real Wikidata properties                                        ║
║    → Parses real Wikipedia TOC                                               ║
║    → Generates ontologies/ JSON files                                        ║
║                                                                               ║
║ 2. Register trained ontologies in Neo4j                                      ║
║    → Create FacetAgent nodes                                                 ║
║    → Store domain_ontology property                                          ║
║    → Link to SubjectConcepts                                                 ║
║                                                                               ║
║ 3. Update Phase 2A+2B GPT prompts                                            ║
║    → Inject trained ontologies                                               ║
║    → Include pattern-matching rules                                          ║
║    → Show sub-concept proposal format                                        ║
║                                                                               ║
║ 4. Execute Phase 2A+2B with self-trained agents                             ║
║    → Agents recognize domain patterns                                        ║
║    → Propose sub-concepts grounded in Wikipedia                             ║
║    → Generate 40,000+ claims + sub-concept proposals                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
