import json
import csv

# Input and output file paths
INPUT_FILE = 'subjects.skosrdf.jsonld'
OUTPUT_FILE = 'subjects_simplified.csv'

# Load JSON-LD data
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find the list of concepts (usually under '@graph' or as a list)
concepts = data.get('@graph', data if isinstance(data, list) else [])

# Prepare CSV output
with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['id', 'prefLabel', 'altLabel', 'broader', 'narrower']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for concept in concepts:
        # Only process SKOS concepts
        types = concept.get('@type') or concept.get('type')
        if not types:
            continue
        if isinstance(types, list):
            is_concept = any('Concept' in t for t in types)
        else:
            is_concept = 'Concept' in types
        if not is_concept:
            continue

        row = {
            'id': concept.get('@id', ''),
            'prefLabel': '',
            'altLabel': '',
            'broader': '',
            'narrower': ''
        }
        # Handle labels (may be dict or list)
        for label_type in ['prefLabel', 'altLabel']:
            val = concept.get(f'skos:{label_type}') or concept.get(label_type)
            if isinstance(val, list):
                row[label_type] = '|'.join(v['@value'] if isinstance(v, dict) and '@value' in v else str(v) for v in val)
            elif isinstance(val, dict):
                row[label_type] = val.get('@value', '')
            elif val:
                row[label_type] = str(val)
        # Handle broader/narrower (may be list or string)
        for rel in ['broader', 'narrower']:
            val = concept.get(f'skos:{rel}') or concept.get(rel)
            if isinstance(val, list):
                row[rel] = '|'.join(v.get('@id', str(v)) for v in val)
            elif isinstance(val, dict):
                row[rel] = val.get('@id', '')
            elif val:
                row[rel] = str(val)
        writer.writerow(row)

print(f"Simplified CSV written to {OUTPUT_FILE}")
