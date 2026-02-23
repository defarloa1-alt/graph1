#!/usr/bin/env python3
"""
Extract pages that link to Q107649491 (type of Wikidata property)

Scrapes the "What Links Here" special page to get all Wikidata property types
that are classified under Q107649491.

Each entry represents a property type classification (e.g., 
"Wikidata property for authority control", "Wikidata property related to sport", etc.)

Output: CSV file with QID and label for each property type
"""

import csv
import re
import time
from pathlib import Path
from datetime import datetime
from collections import Counter
import requests
from bs4 import BeautifulSoup

# Configuration
TARGET_QID = "Q107649491"
OUTPUT_DIR = Path("CSV/backlinks")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIKIDATA_BASE = "https://www.wikidata.org"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Chrystallum/1.0 (backlinks extraction)"

# Rate limiting
REQUEST_DELAY = 1.0  # seconds between requests


def scrape_whatlinkshere_page(target_qid: str, limit: int = 500, offset: int = 0) -> tuple:
    """
    Scrape a single page of "What Links Here" results
    
    Returns: (list of backlinks, has_more_pages)
    """
    url = f"{WIKIDATA_BASE}/w/index.php"
    params = {
        "title": "Special:WhatLinksHere/" + target_qid,
        "limit": limit,
        "offset": offset
    }
    
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    backlinks = []
    
    # Find all list items in the whatlinkshere results
    results_list = soup.find('ul', id='mw-whatlinkshere-list')
    
    if results_list:
        for li in results_list.find_all('li', recursive=False):
            # Extract link to the entity
            link = li.find('a', href=re.compile(r'/wiki/Q\d+'))
            if link:
                href = link.get('href', '')
                qid_match = re.search(r'Q\d+', href)
                if qid_match:
                    qid = qid_match.group(0)
                    label = link.get_text(strip=True)
                    
                    backlinks.append({
                        'qid': qid,
                        'label': label
                    })
    
    # Check if there's a "next 500" link
    has_more = soup.find('a', string=re.compile(r'next \d+'))
    
    return backlinks, bool(has_more)


def enrich_with_descriptions(backlinks: list) -> list:
    """
    Enrich backlinks with descriptions from Wikidata API
    
    Args:
        backlinks: List of dicts with 'qid' and 'label'
    
    Returns:
        Enhanced list with descriptions added
    """
    if not backlinks:
        return []
    
    print("\nEnriching with descriptions...")
    
    # Batch request (max 50 at a time)
    qids = [bl['qid'] for bl in backlinks]
    enriched_data = {}
    
    for i in range(0, len(qids), 50):
        batch = qids[i:i+50]
        qid_str = "|".join(batch)
        
        params = {
            "action": "wbgetentities",
            "ids": qid_str,
            "format": "json",
            "props": "descriptions",
            "languages": "en"
        }
        
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(WIKIDATA_API, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            entities = data.get("entities", {})
            
            for qid, entity_data in entities.items():
                description = entity_data.get("descriptions", {}).get("en", {}).get("value", "")
                enriched_data[qid] = description
        
        if i % 100 == 0 and i > 0:
            print(f"  Processed {i}/{len(qids)} entities...")
        
        time.sleep(REQUEST_DELAY)  # Rate limiting
    
    # Add descriptions to backlinks
    for bl in backlinks:
        bl['description'] = enriched_data.get(bl['qid'], "")
    
    print(f"  Enriched {len(backlinks)} entities")
    
    return backlinks


def get_all_backlinks(target_qid: str, max_results: int = 10000) -> list:
    """
    Get all entities that link to the target QID by scraping What Links Here pages
    
    Returns list of dicts with: qid, label
    """
    all_backlinks = []
    offset = 0
    page_limit = 500
    page_num = 1
    
    print(f"Scraping 'What Links Here' for {target_qid}...")
    
    while len(all_backlinks) < max_results:
        print(f"  Page {page_num} (offset {offset})...", end=" ", flush=True)
        
        backlinks, has_more = scrape_whatlinkshere_page(target_qid, page_limit, offset)
        
        if not backlinks:
            print("No more results")
            break
        
        all_backlinks.extend(backlinks)
        print(f"Found {len(backlinks)} items (total: {len(all_backlinks)})")
        
        if not has_more:
            print("  Reached end of results")
            break
        
        offset += page_limit
        page_num += 1
        time.sleep(REQUEST_DELAY)  # Rate limiting
    
    return all_backlinks


def main():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = OUTPUT_DIR / f"{TARGET_QID}_property_types_{timestamp}.csv"
    
    print("="*80)
    print(f"EXTRACTING WIKIDATA PROPERTY TYPE CLASSIFICATIONS")
    print("="*80)
    print()
    print(f"Target: {TARGET_QID} (type of Wikidata property)")
    print(f"Source: https://www.wikidata.org/wiki/Special:WhatLinksHere/{TARGET_QID}")
    print(f"Output: {output_file}")
    print()
    
    # Step 1: Scrape all backlinks
    print("[1/3] Scraping What Links Here pages...")
    backlinks = get_all_backlinks(TARGET_QID, max_results=10000)
    print(f"\n  Total property types found: {len(backlinks):,}")
    print()
    
    if not backlinks:
        print("No backlinks found. Exiting.")
        return
    
    # Step 2: Enrich with descriptions
    print("[2/3] Enriching with descriptions from Wikidata API...")
    backlinks = enrich_with_descriptions(backlinks)
    print()
    
    # Step 3: Write CSV
    print("[3/3] Writing to CSV...")
    
    fieldnames = ['qid', 'label', 'description']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for bl in backlinks:
            writer.writerow({
                'qid': bl['qid'],
                'label': bl['label'],
                'description': bl.get('description', '')
            })
    
    print(f"  Written {len(backlinks):,} rows")
    print()
    
    # Statistics
    print("="*80)
    print("STATISTICS")
    print("="*80)
    print()
    
    print(f"Total property types: {len(backlinks):,}")
    print()
    
    # Pattern analysis (what kinds of property types)
    pattern_counts = Counter()
    for bl in backlinks:
        label = bl['label'].lower()
        
        if 'authority control' in label:
            pattern_counts['Authority Control'] += 1
        elif 'related to' in label:
            # Extract what it's related to
            match = re.search(r'related to (.+?)(?:\s*\(|$)', label)
            if match:
                topic = match.group(1).strip()
                pattern_counts[f'Related to: {topic}'] += 1
            else:
                pattern_counts['Related to (other)'] += 1
        elif 'to identify' in label or 'identifier' in label:
            pattern_counts['Identifier'] += 1
        elif 'for items about' in label:
            pattern_counts['Items about (topic)'] += 1
        else:
            pattern_counts['Other'] += 1
    
    print("Property type patterns (top 20):")
    for pattern, count in pattern_counts.most_common(20):
        print(f"  {pattern[:60]:60} {count:>6,}")
    print()
    
    # Sample
    print("Sample property types (first 15):")
    for i, bl in enumerate(backlinks[:15], 1):
        label = bl['label'][:70]
        qid = bl['qid']
        print(f"  {i:2}. {label:70} ({qid})")
    print()
    
    print("="*80)
    print(f"Export complete: {output_file}")
    print("="*80)
    print()
    print("Next steps:")
    print(f"  1. Review CSV to see all Wikidata property type classifications")
    print(f"  2. Map property types to Chrystallum entity types")
    print(f"  3. Use for schema alignment and federation scoring")


if __name__ == "__main__":
    main()
