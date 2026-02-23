#!/usr/bin/env python3
"""
Perplexity-Powered Property Facet Resolver

Uses Perplexity API to assign facets to UNKNOWN properties
Based on existing Perplexity integration pattern.

Requires: PERPLEXITY_API_KEY environment variable
"""

import csv
import json
import os
import time
from pathlib import Path
from datetime import datetime
import requests

# Configuration
INPUT_FILE = Path("CSV/property_mappings/property_facet_mapping_20260222_143544.csv")
OUTPUT_FILE = Path("CSV/property_mappings/property_facet_mapping_COMPLETE.csv")

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# Chrystallum's 18 canonical facets
CANONICAL_FACETS = [
    "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION",
    "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC",
    "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC",
    "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC",
    "SOCIAL", "TECHNOLOGICAL"
]

SYSTEM_PROMPT = """You are a Wikidata property classification expert for Chrystallum, a historical knowledge graph system.

Analyze Wikidata properties and assign them to appropriate facets for historical research.

18 Chrystallum Facets:
- ARCHAEOLOGICAL: Archaeology, artifacts, excavations, material culture
- ARTISTIC: Art, sculpture, architecture, aesthetics
- BIOGRAPHIC: Personal life events, genealogy, careers
- COMMUNICATION: Language systems, writing, information exchange
- CULTURAL: Heritage, traditions, customs, ethnography
- DEMOGRAPHIC: Population, census, vital statistics
- DIPLOMATIC: Treaties, alliances, international relations
- ECONOMIC: Trade, commerce, finance, markets
- ENVIRONMENTAL: Climate, natural resources, ecology
- GEOGRAPHIC: Places, locations, spatial relationships
- INTELLECTUAL: Literature, philosophy, scholarship, libraries
- LINGUISTIC: Languages, dialects, etymology
- MILITARY: Warfare, battles, weapons, tactics
- POLITICAL: Government, laws, institutions, offices
- RELIGIOUS: Religions, churches, clergy, theology
- SCIENTIFIC: Natural sciences, mathematics, astronomy
- SOCIAL: Social structures, classes, relationships
- TECHNOLOGICAL: Engineering, tools, construction

Respond ONLY with valid JSON in this exact format:
{"primary_facet": "FACET_NAME", "secondary_facets": ["FACET2"], "reasoning": "why", "confidence": 0.8}

Use facet names EXACTLY as listed above (all caps)."""


def resolve_with_perplexity(property_id: str, label: str, description: str) -> dict:
    """Use Perplexity to infer facets"""
    
    if not PERPLEXITY_API_KEY:
        return {
            "primary_facet": "UNKNOWN",
            "secondary_facets": [],
            "reasoning": "No API key",
            "confidence": 0.0
        }
    
    user_prompt = f"""Property: {property_id}
Label: {label}
Description: {description}

Which Chrystallum facet(s) should this be assigned to for historical research?
Respond with JSON only."""
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.2
    }
    
    try:
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code != 200:
            return {
                "primary_facet": "UNKNOWN",
                "secondary_facets": [],
                "reasoning": f"API error {response.status_code}",
                "confidence": 0.0
            }
        
        result_json = response.json()
        content = result_json.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Parse JSON response
        try:
            # Try direct JSON parse
            result = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown
            import re
            json_match = re.search(r'\{[^{}]*"primary_facet"[^{}]*\}', content)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                # Fallback: manual parsing
                result = {
                    "primary_facet": "UNKNOWN",
                    "secondary_facets": [],
                    "reasoning": content[:100],
                    "confidence": 0.5
                }
        
        # Validate facet names
        primary = result.get("primary_facet", "UNKNOWN")
        if primary not in CANONICAL_FACETS:
            primary = "UNKNOWN"
        
        secondary = [f for f in result.get("secondary_facets", []) if f in CANONICAL_FACETS]
        
        return {
            "primary_facet": primary,
            "secondary_facets": secondary,
            "reasoning": result.get("reasoning", "")[:200],
            "confidence": result.get("confidence", 0.7)
        }
        
    except Exception as e:
        return {
            "primary_facet": "UNKNOWN",
            "secondary_facets": [],
            "reasoning": f"Error: {str(e)[:100]}",
            "confidence": 0.0
        }


def main():
    print("="*80)
    print("PERPLEXITY-POWERED PROPERTY FACET RESOLUTION")
    print("="*80)
    print()
    
    # Check API key
    if not PERPLEXITY_API_KEY:
        print("ERROR: PERPLEXITY_API_KEY not set")
        print("Set it with: $env:PERPLEXITY_API_KEY = 'pplx-your-key'")
        return
    
    print("API Key: Found")
    print()
    
    # Load base mapping
    print(f"Loading: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        properties = list(reader)
    
    unknown = [p for p in properties if p['primary_facet'] == 'UNKNOWN']
    known = [p for p in properties if p['primary_facet'] != 'UNKNOWN']
    
    print(f"  Total: {len(properties)}")
    print(f"  Mapped: {len(known)}")
    print(f"  Need resolution: {len(unknown)}")
    print()
    
    print(f"Processing {len(unknown)} UNKNOWN properties with Perplexity...")
    print(f"Estimated cost: ~${len(unknown) * 0.005:.2f}")
    print(f"Estimated time: ~{len(unknown) * 3 / 60:.1f} minutes")
    print()
    
    # Process
    resolved = []
    
    for i, prop in enumerate(unknown, 1):
        prop_id = prop['property_id']
        label = prop['property_label']
        desc = prop['property_description']
        
        print(f"[{i}/{len(unknown)}] {prop_id} {label[:35]:35}...", end=" ", flush=True)
        
        # Resolve with Perplexity
        result = resolve_with_perplexity(prop_id, label, desc)
        
        # Update
        prop['primary_facet'] = result['primary_facet']
        prop['secondary_facets'] = ','.join(result['secondary_facets'])
        
        all_facets = [result['primary_facet']] + result['secondary_facets']
        prop['all_facets'] = ','.join([f for f in all_facets if f != 'UNKNOWN'])
        
        prop['confidence'] = result['confidence']
        prop['llm_reasoning'] = result['reasoning']
        prop['resolved_by'] = 'perplexity'
        
        resolved.append(prop)
        
        print(f"{result['primary_facet']} ({result['confidence']:.2f})")
        
        time.sleep(3)  # Rate limiting
    
    # Combine
    for prop in known:
        prop['resolved_by'] = 'base_mapping'
        prop['llm_reasoning'] = ''
    
    all_props = known + resolved
    
    # Write
    print()
    print(f"Writing: {OUTPUT_FILE}")
    
    fieldnames = list(properties[0].keys()) + ['llm_reasoning', 'resolved_by']
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_props)
    
    print(f"  Written {len(all_props)} properties")
    print()
    
    # Stats
    facet_counts = {}
    for prop in all_props:
        facet = prop['primary_facet']
        facet_counts[facet] = facet_counts.get(facet, 0) + 1
    
    print("Final distribution:")
    for facet in sorted(facet_counts.keys()):
        print(f"  {facet:20} {facet_counts[facet]:>4}")
    
    unknown_final = len([p for p in all_props if p['primary_facet'] == 'UNKNOWN'])
    coverage = ((500 - unknown_final) / 500) * 100
    
    print()
    print(f"Coverage: {500-unknown_final}/500 ({coverage:.1f}%)")
    print()
    print("="*80)
    print("COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    main()
