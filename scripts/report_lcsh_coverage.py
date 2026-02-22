import csv
import os

SCRIPT_DIR = os.path.dirname(__file__)
TSV_PATH = os.path.join(SCRIPT_DIR, '..', 'Subjects', 'query_lcsh_enriched.tsv')

total = 0
missing = 0
with open(TSV_PATH, encoding='utf-8') as tsvfile:
    reader = csv.DictReader(tsvfile, delimiter='\t')
    for row in reader:
        total += 1
        lcnaf = row.get('lcnaf', '').strip()
        if not lcnaf:
            missing += 1

if total > 0:
    percent_missing = (missing / total) * 100
else:
    percent_missing = 0

print(f"Rows with no LCSH (lcnaf): {missing} / {total} ({percent_missing:.2f}%)")
