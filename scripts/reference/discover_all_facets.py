#!/usr/bin/env python3
"""
Setup script: Discover all 17 facet reference categories from Wikipedia + Wikidata

This script:
1. Defines all 17 discipline QIDs
2. Discovers categories for each
3. Displays results
4. (Optional) Loads to Neo4j

Run with:
    python discover_all_facets.py
    
Or with console output only (no Neo4j):
    python discover_all_facets.py --no-load
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from facet_qid_discovery import FacetQIDDiscovery, DiscoveredFacet
from facet_reference_subgraph import FacetReferenceLoader


# All 17 discipline QIDs
DISCIPLINE_QIDS = {
    "Economic": "Q8134",           # https://en.wikipedia.org/wiki/Economics
    "Military": "Q1300",           # https://en.wikipedia.org/wiki/War
    "Political": "Q7163",          # https://en.wikipedia.org/wiki/Politics
    "Social": "Q34749",            # https://en.wikipedia.org/wiki/Social_science
    "Religious": "Q9592",          # https://en.wikipedia.org/wiki/Religion
    "Artistic": "Q735",            # https://en.wikipedia.org/wiki/Art
    "Technological": "Q11016",     # https://en.wikipedia.org/wiki/Technology
    "Geographic": "Q1365",         # https://en.wikipedia.org/wiki/Geography
    "Diplomatic": "Q2397041",      # https://en.wikipedia.org/wiki/Diplomacy
    "Legal": "Q7748",              # https://en.wikipedia.org/wiki/Law
    "Literary": "Q8242",           # https://en.wikipedia.org/wiki/Literature
    "Biographical": "Q1071",       # https://en.wikipedia.org/wiki/Biography
    "Chronological": "Q11348",     # https://en.wikipedia.org/wiki/Chronology
    "Philosophical": "Q5891",      # https://en.wikipedia.org/wiki/Philosophy
    "Communicational": "Q11033",   # https://en.wikipedia.org/wiki/Communication
    "Agricultural": "Q11019",      # https://en.wikipedia.org/wiki/Agriculture
    "Epidemiological": "Q3274934", # https://en.wikipedia.org/wiki/Epidemiology
}


def print_header(text: str, char: str = "="):
    """Print formatted header"""
    width = 70
    print(f"\n{char * width}")
    print(f"{text.center(width)}")
    print(f"{char * width}\n")


def print_facet_summary(facet: DiscoveredFacet, index: int, total: int):
    """Print summary of discovered facet"""
    print(f"[{index:2d}/{total}] {facet.facet_name.upper()}")
    print(f"      QID: {facet.facet_qid}")
    print(f"      Categories discovered: {len(facet.concept_categories)}")
    print(f"      Method: {facet.extraction_method}")
    print(f"      Confidence: {facet.confidence_score:.2%}")
    print(f"      URL: {facet.wikipedia_url}")
    
    # Print top categories
    for idx, category in enumerate(facet.concept_categories[:3], 1):
        print(f"      {idx}. {category.label} ({len(category.key_topics)} keywords, {category.confidence:.2%})")
    
    if len(facet.concept_categories) > 3:
        print(f"      ... and {len(facet.concept_categories) - 3} more categories")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Discover facet reference categories from Wikipedia + Wikidata"
    )
    parser.add_argument(
        "--no-load",
        action="store_true",
        help="Show results only, don't load to Neo4j"
    )
    parser.add_argument(
        "--facet",
        type=str,
        help="Discover only specific facet (e.g., 'Economic')"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="discovered_facets.json",
        help="Save results to JSON file"
    )
    
    args = parser.parse_args()
    
    print_header("FACET REFERENCE DISCOVERY FROM WIKIPEDIA + WIKIDATA")
    
    # Initialize discovery system
    discovery = FacetQIDDiscovery()
    discovered_facets = {}
    
    # Determine which facets to discover
    facets_to_discover = DISCIPLINE_QIDS
    if args.facet:
        if args.facet in DISCIPLINE_QIDS:
            facets_to_discover = {args.facet: DISCIPLINE_QIDS[args.facet]}
        else:
            print(f"ERROR: Facet '{args.facet}' not found")
            print(f"Available facets: {', '.join(DISCIPLINE_QIDS.keys())}")
            sys.exit(1)
    
    total = len(facets_to_discover)
    
    print(f"Discovering {total} facet reference categories...\n")
    
    # Discover categories for each facet
    for idx, (facet_name, qid) in enumerate(facets_to_discover.items(), 1):
        try:
            print(f"[{idx:2d}/{total}] Discovering {facet_name} ({qid})...")
            
            facet = discovery.discover_facet_canonical_categories(qid)
            discovered_facets[facet_name] = facet
            
            print_facet_summary(facet, idx, total)
            
        except Exception as e:
            print(f"      ✗ ERROR: {e}\n")
            continue
    
    # Summary
    print_header("DISCOVERY SUMMARY", "=")
    
    total_facets = len(discovered_facets)
    total_categories = sum(len(f.concept_categories) for f in discovered_facets.values())
    avg_confidence = (
        sum(f.confidence_score for f in discovered_facets.values()) / total_facets
        if total_facets > 0 else 0
    )
    
    print(f"Total facets discovered: {total_facets}/{total}")
    print(f"Total concept categories: {total_categories}")
    print(f"Average confidence: {avg_confidence:.2%}")
    print()
    
    # Breakdown by extraction method
    methods = {}
    for facet in discovered_facets.values():
        method = facet.extraction_method
        if method not in methods:
            methods[method] = 0
        methods[method] += 1
    
    print("Discovery methods used:")
    for method, count in sorted(methods.items()):
        print(f"  - {method}: {count} facets")
    print()
    
    # Save to JSON
    results = {
        "timestamp": str(discovery.session.get_query(f"RETURN datetime() as dt")),
        "total_facets": total_facets,
        "total_categories": total_categories,
        "average_confidence": avg_confidence,
        "facets": {}
    }
    
    for facet_name, facet in discovered_facets.items():
        results["facets"][facet_name] = {
            "qid": facet.facet_qid,
            "wikipedia_url": facet.wikipedia_url,
            "extraction_method": facet.extraction_method,
            "confidence": facet.confidence_score,
            "categories": [
                {
                    "id": cat.id,
                    "label": cat.label,
                    "description": cat.description[:100] + "..." if len(cat.description) > 100 else cat.description,
                    "key_topics": cat.key_topics[:5],
                    "wikipedia_section": cat.wikipedia_section,
                    "confidence": cat.confidence
                }
                for cat in facet.concept_categories
            ]
        }
    
    # Save results
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✓ Results saved to: {output_path}")
    print()
    
    # Load to Neo4j (optional)
    if not args.no_load:
        print_header("LOADING TO NEO4J")
        
        try:
            # Note: This will need actual Neo4j credentials
            # For now, just show what would happen
            print("To load to Neo4j, run:")
            print()
            print("  from facet_reference_subgraph import FacetReferenceLoader")
            print("  loader = FacetReferenceLoader(uri, user, password)")
            print("  loader.create_facet_schema()")
            print()
            
            for facet_name, facet in discovered_facets.items():
                print(f"  loader.load_discovered_facet(facet_{facet_name.lower()})")
            
            print()
            print("Note: FacetReferenceLoader.load_discovered_facet() needs to be implemented")
            print("      in facet_reference_subgraph.py")
            
        except Exception as e:
            print(f"✗ Neo4j loading failed: {e}")
    
    print_header("DISCOVERY COMPLETE", "=")
    print(f"Discovered {total_facets} facets with {total_categories} total concept categories")
    print("Run next: Load to Neo4j or review saved results")
    print()


if __name__ == "__main__":
    main()
