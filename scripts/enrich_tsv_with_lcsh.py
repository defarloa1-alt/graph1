import csv
import json
import os
import glob
from rapidfuzz import process, fuzz

# Paths
SCRIPT_DIR = os.path.dirname(__file__)
TSV_PATH = os.path.join(SCRIPT_DIR, '..', 'Subjects', 'query.tsv')
LCSH_CHUNKS_DIR = os.path.join(SCRIPT_DIR, '..', 'LCSH', 'skos subject', 'chunks')
OUTPUT_TSV_PATH = os.path.join(SCRIPT_DIR, '..', 'Subjects', 'query_lcsh_enriched.tsv')

def normalize_label(label):
    return ''.join(e for e in label.lower() if e.isalnum() or e.isspace()).strip()

# 1. Aggregate all LCSH labels and their values from all chunks
lcsh_label_to_value = dict()
chunk_files = sorted(glob.glob(os.path.join(LCSH_CHUNKS_DIR, 'subjects_chunk_*.jsonld')))
for chunk_path in chunk_files:
    with open(chunk_path, encoding='utf-8') as f:
        data = json.load(f)
        for entry in data['@graph']:
            if '@graph' in entry:
                for concept in entry['@graph']:
                    # prefLabel
                    if 'skos:prefLabel' in concept:
                        pl = concept['skos:prefLabel']
                        if isinstance(pl, dict) and pl.get('@language') == 'en':
                            label = pl['@value'].strip()
                            lcsh_label_to_value[label] = label
                    # altLabel
                    if 'skos:altLabel' in concept:
                        alt = concept['skos:altLabel']
                        if isinstance(alt, list):
                            for a in alt:
                                if a.get('@language') == 'en':
                                    label = a['@value'].strip()
                                    lcsh_label_to_value[label] = label
                        elif isinstance(alt, dict) and alt.get('@language') == 'en':
                            label = alt['@value'].strip()
                            lcsh_label_to_value[label] = label

# Normalized lookup for fuzzy matching
lcsh_labels_norm = {normalize_label(l): l for l in lcsh_label_to_value}

# 2. Read TSV and enrich

with open(TSV_PATH, encoding='utf-8') as tsvfile:
    reader = csv.DictReader(tsvfile, delimiter='\t')
    rows = list(reader)
    fieldnames = reader.fieldnames if reader.fieldnames else []
    if 'lcnaf' not in fieldnames:
        fieldnames = fieldnames + ['lcnaf']


updated_count = 0
for row in rows:
    # Ensure 'lcnaf' key exists for every row
    if 'lcnaf' not in row:
        row['lcnaf'] = ''
    label = row.get('?itemLabel', '')
    if not label:
        continue
    label_clean = label.split('@')[0].strip()
    lcnaf = row.get('lcnaf', '')
    if lcnaf:
        continue  # Don't overwrite existing
    # 1. Exact match
    if label_clean in lcsh_label_to_value:
        row['lcnaf'] = lcsh_label_to_value[label_clean]
        updated_count += 1
        continue
    # 2. Fuzzy/normalized match
    norm = normalize_label(label_clean)
    match, score, _ = process.extractOne(norm, lcsh_labels_norm.keys(), scorer=fuzz.ratio)
    if score >= 90:
        row['lcnaf'] = lcsh_labels_norm[match]
        updated_count += 1

# 3. Write enriched TSV
with open(OUTPUT_TSV_PATH, 'w', encoding='utf-8', newline='') as out:
    writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    writer.writerows(rows)

print(f"Enrichment complete. {updated_count} lcnaf values added. Output: {OUTPUT_TSV_PATH}")
