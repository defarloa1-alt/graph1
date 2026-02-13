
import csv
import json
import os
import glob

# Paths
SCRIPT_DIR = os.path.dirname(__file__)
TSV_PATH = os.path.join(SCRIPT_DIR, '..', 'Subjects', 'query.tsv')
LCSH_CHUNKS_DIR = os.path.join(SCRIPT_DIR, '..', 'LCSH', 'skos subject', 'chunks')

# 1. Extract unique subject labels from TSV
with open(TSV_PATH, encoding='utf-8') as tsvfile:
    reader = csv.DictReader(tsvfile, delimiter='\t')
    tsv_labels = set()
    for row in reader:
        label = row['?itemLabel']
        if label:
            label = label.split('@')[0].strip()
            tsv_labels.add(label)

# 2. Aggregate all LCSH labels from all chunks
lcsh_labels = set()
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
                            lcsh_labels.add(pl['@value'].strip())
                    # altLabel
                    if 'skos:altLabel' in concept:
                        alt = concept['skos:altLabel']
                        if isinstance(alt, list):
                            for a in alt:
                                if a.get('@language') == 'en':
                                    lcsh_labels.add(a['@value'].strip())
                        elif isinstance(alt, dict) and alt.get('@language') == 'en':
                            lcsh_labels.add(alt['@value'].strip())

# 3. TSV→LCSH analysis
matched = tsv_labels & lcsh_labels
unmatched = tsv_labels - lcsh_labels


print(f"Total TSV labels: {len(tsv_labels)}")
print(f"Total LCSH labels (all chunks): {len(lcsh_labels)}")
print(f"Matched TSV labels in LCSH: {len(matched)}")
print(f"Unmatched TSV labels: {len(unmatched)}")
print("\nSample matched labels:", list(matched)[:10])
print("\nSample unmatched TSV labels:", list(unmatched)[:10])

# 4. LCSH→TSV analysis
lcsh_not_in_tsv = lcsh_labels - tsv_labels
print(f"\nLCSH labels not in TSV: {len(lcsh_not_in_tsv)}")
print("Sample LCSH-only labels:", list(lcsh_not_in_tsv)[:10])

# 5. Show side-by-side samples for format comparison
print("\n--- Format Comparison Samples ---")
unmatched_list = list(unmatched)
lcsh_list = list(lcsh_labels)
print(f"{'TSV Unmatched Label':40} | {'LCSH Label':40}")
print('-'*85)

for i in range(10):
    tsv_label = unmatched_list[i] if i < len(unmatched_list) else ''
    lcsh_label = lcsh_list[i] if i < len(lcsh_list) else ''
    print(f"{tsv_label[:40]:40} | {lcsh_label[:40]:40}")

# --- Fuzzy/normalized matching using rapidfuzz ---
from rapidfuzz import process, fuzz
def normalize_label(label):
    return ''.join(e for e in label.lower() if e.isalnum() or e.isspace()).strip()

lcsh_labels_norm = {normalize_label(l): l for l in lcsh_labels}
fuzzy_matches = []
for tsv_label in unmatched_list:
    norm = normalize_label(tsv_label)
    match, score, _ = process.extractOne(norm, lcsh_labels_norm.keys(), scorer=fuzz.ratio)
    if score >= 90:
        fuzzy_matches.append((tsv_label, lcsh_labels_norm[match], score))

print("\n--- Fuzzy/Normalized Matches (score >= 90) ---")
print(f"{'TSV Label':40} | {'LCSH Label':40} | Score")
print('-'*95)
for tsv_label, lcsh_label, score in fuzzy_matches[:10]:
    print(f"{tsv_label[:40]:40} | {lcsh_label[:40]:40} | {score}")
