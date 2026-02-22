#!/usr/bin/env python3
"""
Explore Wikidata Time Period Structure
Shows what classes, properties, and data are available for time periods
"""

import requests
import json
import sys
import io
from collections import defaultdict

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def query_wikidata(sparql):
    """Execute SPARQL query against Wikidata."""
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "ChrystallumBot/1.0 (research project)"
    }
    
    response = requests.get(
        "https://query.wikidata.org/sparql",
        params={"query": sparql},
        headers=headers,
        timeout=60
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[ERROR] HTTP {response.status_code}: {response.reason}")
        return None

def explore_time_period_classes():
    """Find all classes used for time periods."""
    print("="*80)
    print("EXPLORING TIME PERIOD CLASSES")
    print("="*80)
    print()
    
    sparql = """
    SELECT ?class ?classLabel (COUNT(?item) as ?count) WHERE {
      VALUES ?class {
        wd:Q11514315  # historical period
        wd:Q186081    # time interval
        wd:Q573302    # era
        wd:Q2164983   # historical era
        wd:Q49848     # epoch
        wd:Q3186692   # time period
        wd:Q36507     # calendar era
      }
      ?item wdt:P31 ?class .
      
      # Must have some temporal property
      { ?item wdt:P580 [] } UNION { ?item wdt:P582 [] } UNION { ?item wdt:P571 [] }
      
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    GROUP BY ?class ?classLabel
    ORDER BY DESC(?count)
    """
    
    result = query_wikidata(sparql)
    if result:
        bindings = result.get("results", {}).get("bindings", [])
        print(f"Found {len(bindings)} time period classes:\n")
        for b in bindings:
            qid = b['class']['value'].split('/')[-1]
            label = b['classLabel']['value']
            count = b['count']['value']
            print(f"  {qid:15s} {label:30s} {count:>8s} items")
        print()

def explore_sample_periods():
    """Get sample time periods with full property set."""
    print("="*80)
    print("SAMPLE TIME PERIODS (with all available properties)")
    print("="*80)
    print()
    
    sparql = """
    SELECT DISTINCT ?item ?itemLabel ?desc 
           ?start ?end ?inception ?dissolved
           ?lcsh ?dewey ?lcc ?fast
           ?partOf ?partOfLabel
           ?country ?countryLabel
           ?location ?locationLabel
    WHERE {
      VALUES ?item {
        wd:Q17167   # Roman Republic
        wd:Q2277    # Roman Empire
        wd:Q11772   # Ancient Greece
        wd:Q361     # World War I
        wd:Q362     # World War II
      }
      
      OPTIONAL { ?item wdt:P580 ?start . }
      OPTIONAL { ?item wdt:P582 ?end . }
      OPTIONAL { ?item wdt:P571 ?inception . }
      OPTIONAL { ?item wdt:P576 ?dissolved . }
      
      OPTIONAL { ?item wdt:P244 ?lcsh . }
      OPTIONAL { ?item wdt:P1036 ?dewey . }
      OPTIONAL { ?item wdt:P1149 ?lcc . }
      OPTIONAL { ?item wdt:P2163 ?fast . }
      
      OPTIONAL { ?item wdt:P361 ?partOf . }
      OPTIONAL { ?item wdt:P17 ?country . }
      OPTIONAL { ?item wdt:P276 ?location . }
      
      OPTIONAL { ?item schema:description ?desc . FILTER(LANG(?desc) = "en") }
      
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    """
    
    result = query_wikidata(sparql)
    if result:
        bindings = result.get("results", {}).get("bindings", [])
        
        # Group by item
        by_item = defaultdict(lambda: {
            'qid': '', 'label': '', 'desc': '',
            'start': None, 'end': None, 'inception': None, 'dissolved': None,
            'lcsh': None, 'dewey': None, 'lcc': None, 'fast': None,
            'partOf': None, 'country': None, 'location': None
        })
        
        for b in bindings:
            qid = b['item']['value'].split('/')[-1]
            item = by_item[qid]
            
            if not item['qid']:
                item['qid'] = qid
                item['label'] = b.get('itemLabel', {}).get('value', '')
                item['desc'] = b.get('desc', {}).get('value', '')
            
            if 'start' in b:
                item['start'] = b['start']['value']
            if 'end' in b:
                item['end'] = b['end']['value']
            if 'inception' in b:
                item['inception'] = b['inception']['value']
            if 'dissolved' in b:
                item['dissolved'] = b['dissolved']['value']
            
            if 'lcsh' in b:
                lcsh_uri = b['lcsh']['value']
                item['lcsh'] = lcsh_uri.split('/')[-1]
            if 'dewey' in b:
                item['dewey'] = b['dewey']['value']
            if 'lcc' in b:
                item['lcc'] = b['lcc']['value']
            if 'fast' in b:
                item['fast'] = b['fast']['value']
            
            if 'partOfLabel' in b:
                item['partOf'] = b['partOfLabel']['value']
            if 'countryLabel' in b:
                item['country'] = b['countryLabel']['value']
            if 'locationLabel' in b:
                item['location'] = b['locationLabel']['value']
        
        for qid, item in by_item.items():
            print(f"[{item['qid']}] {item['label']}")
            if item['desc']:
                print(f"  Description: {item['desc'][:80]}...")
            print(f"  Start:     {item['start'] or item['inception'] or 'N/A'}")
            print(f"  End:       {item['end'] or item['dissolved'] or 'N/A'}")
            print(f"  LCSH:      {item['lcsh'] or 'N/A'}")
            print(f"  Dewey:     {item['dewey'] or 'N/A'}")
            print(f"  LCC:       {item['lcc'] or 'N/A'}")
            print(f"  FAST:      {item['fast'] or 'N/A'}")
            print(f"  Part of:   {item['partOf'] or 'N/A'}")
            print(f"  Country:   {item['country'] or 'N/A'}")
            print(f"  Location:  {item['location'] or 'N/A'}")
            print()

def count_periods_with_classifications():
    """Count how many time periods have each classification."""
    print("="*80)
    print("CLASSIFICATION COVERAGE")
    print("="*80)
    print()
    
    sparql = """
    SELECT 
      (COUNT(DISTINCT ?item) as ?total)
      (COUNT(DISTINCT ?lcsh) as ?with_lcsh)
      (COUNT(DISTINCT ?dewey) as ?with_dewey)
      (COUNT(DISTINCT ?lcc) as ?with_lcc)
      (COUNT(DISTINCT ?fast) as ?with_fast)
    WHERE {
      ?item wdt:P31/wdt:P279* wd:Q11514315 .  # instance of historical period
      
      # Must have temporal bounds
      { ?item wdt:P580 [] } UNION { ?item wdt:P582 [] }
      
      OPTIONAL { ?item wdt:P244 ?lcsh . }
      OPTIONAL { ?item wdt:P1036 ?dewey . }
      OPTIONAL { ?item wdt:P1149 ?lcc . }
      OPTIONAL { ?item wdt:P2163 ?fast . }
    }
    """
    
    print("Querying... (this may take 30-60 seconds)")
    result = query_wikidata(sparql)
    if result:
        b = result.get("results", {}).get("bindings", [{}])[0]
        total = int(b.get('total', {}).get('value', 0))
        lcsh = int(b.get('with_lcsh', {}).get('value', 0))
        dewey = int(b.get('with_dewey', {}).get('value', 0))
        lcc = int(b.get('with_lcc', {}).get('value', 0))
        fast = int(b.get('with_fast', {}).get('value', 0))
        
        print(f"Total historical periods: {total:,}")
        print(f"  With LCSH (P244):       {lcsh:>6,} ({lcsh/total*100:.1f}%)")
        print(f"  With Dewey (P1036):     {dewey:>6,} ({dewey/total*100:.1f}%)")
        print(f"  With LCC (P1149):       {lcc:>6,} ({lcc/total*100:.1f}%)")
        print(f"  With FAST (P2163):      {fast:>6,} ({fast/total*100:.1f}%)")
        print()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("WIKIDATA TIME PERIOD EXPLORATION")
    print("="*80)
    print()
    
    explore_time_period_classes()
    explore_sample_periods()
    count_periods_with_classifications()
    
    print("="*80)
    print("[COMPLETE] Exploration finished")
    print("="*80)


