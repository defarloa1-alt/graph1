#index_scan
#!/usr/bin/env python3
"""
Script to search for Wikidata QIDs and entity information for Roman history index terms.
Uses web scraping to query Wikidata and extract QID, label, and entity type.
"""

import csv
import json
import time
import urllib.request
import urllib.parse
from typing import Optional, Dict, List

def search_wikidata(term: str) -> Optional[Dict[str, str]]:
    """
    Search Wikidata for a term and return QID, label, and type.
    
    Args:
        term: The search term
        
    Returns:
        Dictionary with 'qid', 'label', and 'type' keys, or None if not found
    """
    try:
        # Wikidata search API
        search_url = "https://www.wikidata.org/w/api.php"
        params = {
            'action': 'wbsearchentities',
            'format': 'json',
            'language': 'en',
            'type': 'item',
            'search': term,
            'limit': 1
        }
        
        url = f"{search_url}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        if 'search' in data and len(data['search']) > 0:
            result = data['search'][0]
            qid = result.get('id', '')
            label = result.get('label', '')
            description = result.get('description', '')
            
            # Get more detailed type information
            entity_type = get_entity_type(qid) if qid else description
            
            return {
                'qid': qid,
                'label': label,
                'type': entity_type or description
            }
        
        return None
        
    except Exception as e:
        print(f"Error searching for '{term}': {e}")
        return None


def get_entity_type(qid: str) -> Optional[str]:
    """
    Get the instance-of (P31) property for a Wikidata entity to determine its type.
    
    Args:
        qid: Wikidata QID
        
    Returns:
        Type description string or None
    """
    try:
        entity_url = "https://www.wikidata.org/w/api.php"
        params = {
            'action': 'wbgetentities',
            'format': 'json',
            'ids': qid,
            'props': 'claims',
            'languages': 'en'
        }
        
        url = f"{entity_url}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        if 'entities' in data and qid in data['entities']:
            entity = data['entities'][qid]
            if 'claims' in entity and 'P31' in entity['claims']:
                # P31 is "instance of" property
                instance_claims = entity['claims']['P31']
                if instance_claims:
                    # Get the first instance-of value
                    instance_qid = instance_claims[0]['mainsnak']['datavalue']['value']['id']
                    # Get label for this instance type
                    return get_label(instance_qid)
        
        return None
        
    except Exception as e:
        print(f"Error getting type for {qid}: {e}")
        return None


def get_label(qid: str) -> Optional[str]:
    """
    Get the English label for a Wikidata entity.
    
    Args:
        qid: Wikidata QID
        
    Returns:
        Label string or None
    """
    try:
        entity_url = "https://www.wikidata.org/w/api.php"
        params = {
            'action': 'wbgetentities',
            'format': 'json',
            'ids': qid,
            'props': 'labels',
            'languages': 'en'
        }
        
        url = f"{entity_url}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        if 'entities' in data and qid in data['entities']:
            entity = data['entities'][qid]
            if 'labels' in entity and 'en' in entity['labels']:
                return entity['labels']['en']['value']
        
        return None
        
    except Exception as e:
        return None


def process_terms(terms: List[str], output_file: str, delay: float = 1.0):
    """
    Process a list of terms and write results to CSV.
    
    Args:
        terms: List of search terms
        output_file: Path to output CSV file
        delay: Delay between requests in seconds (to be polite to Wikidata)
    """
    results = []
    
    for i, term in enumerate(terms, 1):
        print(f"Processing {i}/{len(terms)}: {term}")
        
        result = search_wikidata(term)
        
        if result:
            results.append({
                'term': term,
                'qid': result['qid'],
                'label': result['label'],
                'type': result['type']
            })
            print(f"  ✓ Found: {result['qid']} - {result['label']} ({result['type']})")
        else:
            results.append({
                'term': term,
                'qid': '',
                'label': '',
                'type': 'not found'
            })
            print(f"  ✗ Not found")
        
        # Be polite to Wikidata's servers
        time.sleep(delay)
    
    # Write results to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['term', 'qid', 'label', 'type'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✓ Results written to {output_file}")
    print(f"  Found: {sum(1 for r in results if r['qid'])}/{len(results)} terms")


def main():
    """Main function to process all index terms."""
    
    # List of all terms from the Roman history index
    terms = [
        "accensus",
        "Acco Senones execution",
        "Achaean League",
        "Battle of Actium",
        "Acts of the Apostles",
        "Acts of the Pagan Martyrs",
        "Adherbal Numidia",
        "Adramyttium",
        "Aedui tribe",
        "Aelius Aristides",
        "Aequi people",
        "Gnaeus Julius Agricola",
        "Marcus Vipsanius Agrippa",
        "ala Gallorum Indiana",
        "ala I Pannioniorum",
        "ala Sebastinorum",
        "Alamanni",
        "Alans nomads",
        "Aulus Postumius Albinus",
        "Battle of Alesia",
        "Alexander the Great",
        "Alexandria Egypt",
        "Allobroges",
        "Amastris Paphlagonia",
        "amber trade",
        "amicitia Roman",
        "Amisus Pontus",
        "Antioch Syria",
        "Antiochus III the Great",
        "Antiochus IV Epiphanes",
        "Antonine Wall",
        "Herennius Antoninus",
        "Antoninus Pius",
        "Apache people",
        "Apamea Syria",
        "Appian historian",
        "Appian Way",
        "Appius Claudius Pulcher",
        "Apuleius Golden Ass",
        "Aquae Sextiae",
        "Roman aqueduct",
        "Ara Pacis Augustae",
        "Arbeia Roman fort",
        "Arch of Titus",
        "Claudius Archibios",
        "Arevaci Celtiberian",
        "Ariobarzanes I of Cappadocia",
        "Ariovistus Germanic king",
        "Armenia ancient kingdom",
        "Arminius Germanic chieftain",
        "Arrian historian",
        "Arverni tribe",
        "Ascalon ancient city",
        "Athens Greece",
        "Quintus Atilius Primus",
        "Atrebates tribe",
        "Titus Pomponius Atticus",
        "Atuatuca Tungrorum",
        "Augusta Vindelicum Augsburg",
        "Augustodunum Autun",
        "Augustus Roman Emperor",
        "aurochs extinct cattle",
        "Auzia Mauretania",
        "Babylon ancient city",
        "Baetica Roman province",
        "Balkans region",
        "Bastarnae people",
        "Batanaea region",
        "Batavian revolt",
        "Bede Venerable",
        "Belgae tribes",
        "Bellovaci tribe",
        "beneficiarius Roman military",
        "Berenice Egypt",
        "Bibracte Gaul",
        "Marcus Calpurnius Bibulus",
        "Bithynia ancient kingdom",
        "Bithynia et Pontus province",
        "Quintus Junius Blaesus",
        "Second Boer War",
        "Boii Celtic people",
        "Book of Deuteronomy"
    ]
    
    output_file = "/mnt/user-data/outputs/wikidata_search_results.csv"
    
    print("=" * 60)
    print("Wikidata Search Tool for Roman History Index")
    print("=" * 60)
    print(f"Processing {len(terms)} terms...")
    print()
    
    process_terms(terms, output_file, delay=1.0)
    
    print("\nDone!")


if __name__ == "__main__":
    main()