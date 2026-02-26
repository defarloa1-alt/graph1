#!/usr/bin/env python3
"""
Get property type classifications by querying property entities directly

Instead of scraping backlinks, query each property's P31 (instance of)
to find which property type classes it belongs to.

Example: P39 (position held) → P31: Q107649491, Q18616576, etc.
"""

import requests
import json
import time
from pathlib import Path

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Chrystallum/1.0"

def get_property_types(property_id: str) -> dict:
    """
    Get all P31 (instance of) values for a property
    
    Args:
        property_id: Property PID (e.g., "P39")
        
    Returns:
        Dict with property info and type classifications
    """
    params = {
        "action": "wbgetentities",
        "ids": property_id,
        "format": "json",
        "props": "labels|descriptions|claims",
        "languages": "en"
    }
    
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(WIKIDATA_API, headers=headers, params=params)
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code}")
    
    data = response.json()
    entity = data.get("entities", {}).get(property_id, {})
    
    # Get basic info
    label = entity.get("labels", {}).get("en", {}).get("value", property_id)
    description = entity.get("descriptions", {}).get("en", {}).get("value", "")
    
    # Get P31 (instance of) - property type classifications
    claims = entity.get("claims", {})
    p31_claims = claims.get("P31", [])
    
    type_qids = []
    for claim in p31_claims:
        try:
            qid = claim["mainsnak"]["datavalue"]["value"]["id"]
            type_qids.append(qid)
        except (KeyError, TypeError):
            pass
    
    return {
        "property_id": property_id,
        "label": label,
        "description": description,
        "type_qids": type_qids,
        "type_count": len(type_qids)
    }


def main():
    """Test with sample properties"""
    
    test_properties = [
        "P39",   # position held
        "P31",   # instance of
        "P279",  # subclass of
        "P625",  # coordinate location
        "P17",   # country
        "P580",  # start time
    ]
    
    print("="*80)
    print("TESTING: Get Property Type Classifications")
    print("="*80)
    print()
    
    for prop in test_properties:
        print(f"Querying {prop}...", end=" ")
        
        try:
            result = get_property_types(prop)
            
            print(f"OK - {result['label']}")
            print(f"  Description: {result['description']}")
            print(f"  Type classifications ({result['type_count']}):")
            
            for type_qid in result['type_qids']:
                print(f"    - {type_qid}")
                
                # Check if it's Q107649491
                if type_qid == "Q107649491":
                    print(f"      ** IS A 'type of Wikidata property'")
            
            print()
            
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"ERROR: {e}")
            print()
    
    print("="*80)
    print("KEY INSIGHT:")
    print("="*80)
    print()
    print("Properties that have P31=Q107649491 are meta-classifications!")
    print("Regular properties (like P39, P31) will have OTHER type QIDs.")
    print()
    print("To find property types, query properties that have P31=Q107649491")
    print("(which is exactly what the backlinks extraction already did!)")
    print()


if __name__ == "__main__":
    main()
