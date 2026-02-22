#!/usr/bin/env python3
"""
Extract ALL classification identifiers from Wikidata QID.

This is the primary backbone integration tool for Chrystallum.
Fetches Dewey (agent routing), LCSH (subject ID), LCC (hierarchy), FAST (property).

Usage:
    from wikidata_fast_lookup import get_all_classification_ids
    
    data = get_all_classification_ids("Q17167")
    print(data['lcsh_id'])        # Primary backbone identifier
    print(data['dewey_decimal'])  # Agent assignment
    print(data['fast_id'])        # Supplementary property
"""
import requests
import sys
import json
from typing import Dict, Optional

def get_all_classification_ids(qid: str) -> Optional[Dict[str, Optional[str]]]:
    """
    Fetches ALL classification identifiers for a given Wikidata QID in one query.
    
    This is the primary function for Chrystallum backbone integration.
    Returns Dewey (primary for agent routing), LCSH (primary for subject identification),
    LCC (hierarchical classification), and FAST (supplementary property).
    
    Args:
        qid: Wikidata QID (e.g., "Q17167")
        
    Returns:
        Dictionary with classification identifiers:
        {
            'qid': str,
            'label': str or None,          # Human-readable label
            'dewey_decimal': str or None,  # P1036 - Agent assignment
            'lcsh_id': str or None,        # P244 - Subject unique_id (PRIMARY BACKBONE)
            'lcc_code': str or None,       # P1149 - Hierarchical classification
            'fast_id': str or None,        # P2163 - Supplementary property
        }
        Returns None if query fails.
    """
    sparql_query = f"""
    SELECT ?itemLabel ?dewey ?lcsh ?lcc ?fast WHERE {{
      BIND(wd:{qid} AS ?item)
      
      OPTIONAL {{ ?item wdt:P1036 ?dewey . }}  # Dewey Decimal
      OPTIONAL {{ ?item wdt:P244 ?lcsh . }}    # LCSH ID
      OPTIONAL {{ ?item wdt:P1149 ?lcc . }}    # LCC
      OPTIONAL {{ ?item wdt:P2163 ?fast . }}   # FAST ID
      
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 1
    """
    
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "ChrystallumBot/1.0 (federated-graph-framework; research project)"
    }
    
    try:
        response = requests.get(
            "https://query.wikidata.org/sparql",
            params={"query": sparql_query},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            bindings = data.get("results", {}).get("bindings", [])
            
            if bindings:
                binding = bindings[0]
                
                # Extract LCSH ID from URI
                lcsh_uri = binding.get('lcsh', {}).get('value', '')
                lcsh_id = lcsh_uri.split('/')[-1] if lcsh_uri else None
                
                return {
                    'qid': qid,
                    'label': binding.get('itemLabel', {}).get('value'),
                    'dewey_decimal': binding.get('dewey', {}).get('value'),
                    'lcsh_id': lcsh_id,
                    'lcc_code': binding.get('lcc', {}).get('value'),
                    'fast_id': binding.get('fast', {}).get('value')
                }
            else:
                print(f"⚠️  No classification data found for {qid}", file=sys.stderr)
                return {
                    'qid': qid,
                    'label': None,
                    'dewey_decimal': None,
                    'lcsh_id': None,
                    'lcc_code': None,
                    'fast_id': None
                }
        else:
            print(f"❌ Error fetching Wikidata for {qid}: {response.status_code} {response.reason}", file=sys.stderr)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error for {qid}: {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    # Test with some QIDs
    test_cases = [
        ("Q1048", "Julius Caesar"),
        ("Q48314", "Battle of Pharsalus"),
        ("Q17167", "Roman Republic"),
        ("Q220", "Rome"),
        ("Q11772", "Ancient Greece"),
        ("Q7209", "Han Dynasty")
    ]
    
    print("=" * 80)
    print("TESTING WIKIDATA CLASSIFICATION EXTRACTION (ALL IDs)")
    print("=" * 80)
    print()
    
    for qid, name in test_cases:
        print(f"Testing: {name} ({qid})")
        
        # Use new unified function
        data = get_all_classification_ids(qid)
        
        if data:
            print(f"  Label:          {data['label']}")
            print(f"  LCSH ID (P244): {data['lcsh_id'] or 'NOT FOUND'} <- PRIMARY BACKBONE")
            print(f"  Dewey (P1036):  {data['dewey_decimal'] or 'NOT FOUND'} <- AGENT ROUTING")
            print(f"  LCC (P1149):    {data['lcc_code'] or 'NOT FOUND'} <- HIERARCHY")
            print(f"  FAST (P2163):   {data['fast_id'] or 'NOT FOUND'} <- PROPERTY")
        else:
            print(f"  ERROR: Failed to fetch data")
        
        print()
