#!/usr/bin/env python3
"""
LLM-Powered Property Facet Resolver

For properties marked UNKNOWN in the base mapping, use LLM to infer
facets based on property label and description.

Hybrid approach:
1. Base mapping (deterministic) - 248 properties
2. LLM inference (semantic) - 252 UNKNOWN properties
= 500 total with full coverage

Requires: OpenAI API key

Usage:
    python llm_resolve_unknown_properties.py --auto-proceed
"""

import csv
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# Configuration
INPUT_FILE = Path("CSV/property_mappings/property_facet_mapping_20260222_143544.csv")
OUTPUT_FILE = Path("CSV/property_mappings/property_facet_mapping_COMPLETE.csv")

# OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Chrystallum's 18 canonical facets
CANONICAL_FACETS = [
    "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION",
    "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC",
    "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC",
    "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC",
    "SOCIAL", "TECHNOLOGICAL"
]

SYSTEM_PROMPT = """You are a property classification expert for the Chrystallum historical knowledge graph.

Your task: Analyze Wikidata property descriptions and assign them to one or more of these 18 facets:

ARCHAEOLOGICAL - Archaeology, artifacts, excavations, material culture
ARTISTIC - Art, sculpture, painting, architecture, aesthetics
BIOGRAPHIC - Personal life events, genealogy, prosopography
COMMUNICATION - Language, writing systems, information exchange
CULTURAL - Cultural heritage, traditions, customs, ethnography
DEMOGRAPHIC - Population, census, vital statistics, migration
DIPLOMATIC - Treaties, alliances, international relations, embassies
ECONOMIC - Trade, commerce, finance, taxation, markets
ENVIRONMENTAL - Climate, geography, natural resources, ecology
GEOGRAPHIC - Places, locations, spatial relationships, maps
INTELLECTUAL - Literature, philosophy, scholarship, education, libraries
LINGUISTIC - Languages, dialects, etymology, translation
MILITARY - Warfare, battles, weapons, military organizations, tactics
POLITICAL - Government, laws, institutions, political events, offices
RELIGIOUS - Religions, beliefs, churches, clergy, rituals, theology
SCIENTIFIC - Natural sciences, mathematics, astronomy, medicine
SOCIAL - Social structures, classes, relationships, daily life
TECHNOLOGICAL - Engineering, tools, construction, innovation

Guidelines:
- Assign 1-3 facets (primary, secondary, tertiary)
- Consider historical research context
- Be specific but practical
- Focus on how the property would be used in historical analysis

Output format (JSON):
{
  "primary_facet": "FACET_NAME",
  "secondary_facets": ["FACET2", "FACET3"],
  "reasoning": "Brief explanation",
  "confidence": 0.7
}
"""


def resolve_property_with_llm(property_id: str, label: str, description: str) -> dict:
    """
    Use LLM to infer facets for a property
    
    Args:
        property_id: P180, P186, etc.
        label: "depicts", "made from material"
        description: Full property description
        
    Returns:
        {primary_facet, secondary_facets, reasoning, confidence}
    """
    
    user_prompt = f"""Analyze this Wikidata property and assign to Chrystallum facets:

Property ID: {property_id}
Label: {label}
Description: {description}

What facet(s) should this property be assigned to for historical research?"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        
        # Try to parse JSON
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                # Fallback: try to parse as-is
                result = json.loads(content)
        
        return result
        
    except Exception as e:
        print(f"  LLM error: {e}")
        return {
            "primary_facet": "UNKNOWN",
            "secondary_facets": [],
            "reasoning": f"Error: {e}",
            "confidence": 0.0
        }


def main():
    print("="*80)
    print("LLM-POWERED PROPERTY FACET RESOLUTION")
    print("="*80)
    print()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set in environment")
        print("Set it with: $env:OPENAI_API_KEY = 'your-key'")
        return
    
    # Load base mapping
    print(f"Loading base mapping: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        properties = list(reader)
    
    print(f"  Total properties: {len(properties)}")
    
    # Find UNKNOWN properties
    unknown = [p for p in properties if p['primary_facet'] == 'UNKNOWN']
    known = [p for p in properties if p['primary_facet'] != 'UNKNOWN']
    
    print(f"  Already mapped: {len(known)}")
    print(f"  Need LLM resolution: {len(unknown)}")
    print()
    
    # Ask to proceed
    print(f"This will make {len(unknown)} LLM API calls.")
    print(f"Estimated cost: ~${len(unknown) * 0.0005:.2f} (using gpt-3.5-turbo)")
    print(f"Estimated time: ~{len(unknown) * 2} seconds (~{len(unknown) * 2 / 60:.1f} minutes)")
    print()
    
    # Auto-proceed if --auto-proceed flag
    if '--auto-proceed' in sys.argv:
        print("Auto-proceeding...")
    else:
        proceed = input("Proceed? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Cancelled.")
            return
    
    print()
    print("Processing UNKNOWN properties with LLM...")
    print()
    
    # Process UNKNOWN properties
    resolved = []
    
    for i, prop in enumerate(unknown, 1):
        prop_id = prop['property_id']
        label = prop['property_label']
        desc = prop['property_description']
        
        print(f"[{i}/{len(unknown)}] {prop_id} - {label[:40]:40}...", end=" ", flush=True)
        
        # Get LLM inference
        llm_result = resolve_property_with_llm(prop_id, label, desc)
        
        # Update property data
        prop['primary_facet'] = llm_result.get('primary_facet', 'UNKNOWN')
        prop['secondary_facets'] = ','.join(llm_result.get('secondary_facets', []))
        
        all_facets = [llm_result.get('primary_facet')] + llm_result.get('secondary_facets', [])
        prop['all_facets'] = ','.join([f for f in all_facets if f and f != 'UNKNOWN'])
        
        prop['confidence'] = llm_result.get('confidence', 0.5)
        prop['llm_reasoning'] = llm_result.get('reasoning', '')
        prop['resolved_by'] = 'llm'
        
        resolved.append(prop)
        
        print(f"-> {prop['primary_facet']} (conf: {prop['confidence']:.2f})")
    
    # Add resolved_by flag to known properties
    for prop in known:
        prop['resolved_by'] = 'base_mapping'
        prop['llm_reasoning'] = ''
    
    # Combine
    all_properties = known + resolved
    
    # Write complete mapping
    print()
    print(f"Writing complete mapping to: {OUTPUT_FILE}")
    
    fieldnames = list(properties[0].keys()) + ['llm_reasoning', 'resolved_by']
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_properties)
    
    print(f"  Written {len(all_properties)} properties")
    print()
    
    # Final statistics
    print("="*80)
    print("FINAL STATISTICS")
    print("="*80)
    print()
    
    facet_counts = {}
    for prop in all_properties:
        facet = prop['primary_facet']
        facet_counts[facet] = facet_counts.get(facet, 0) + 1
    
    print("Properties by facet:")
    for facet in sorted(facet_counts.keys()):
        count = facet_counts[facet]
        print(f"  {facet:20} {count:>4}")
    print()
    
    # Coverage
    unknown_final = [p for p in all_properties if p['primary_facet'] == 'UNKNOWN']
    coverage = ((500 - len(unknown_final)) / 500) * 100
    
    print(f"Coverage: {500 - len(unknown_final)}/500 ({coverage:.1f}%)")
    print(f"Remaining UNKNOWN: {len(unknown_final)}")
    print()
    
    # Method breakdown
    base = len([p for p in all_properties if p['resolved_by'] == 'base_mapping'])
    llm = len([p for p in all_properties if p['resolved_by'] == 'llm'])
    
    print(f"Resolved by base mapping: {base}")
    print(f"Resolved by LLM: {llm}")
    print()
    
    print("="*80)
    print("COMPLETE!")
    print("="*80)
    print()
    print("Output: CSV/property_mappings/property_facet_mapping_COMPLETE.csv")


if __name__ == "__main__":
    main()
