import csv
import re
from collections import defaultdict

# Step 1: Extract unique place tokens from periodo-dataset.csv
INPUT_PATH = '../Temporal/periodo-dataset.csv'
TOKENS_OUT = '../Subjects/periodo_unique_tokens.txt'

# Use a set to collect unique tokens
unique_tokens = set()

def clean_token(token):
    token = token.strip()
    token = re.sub(r'^[^\w]+|[^\w]+$', '', token)  # Remove leading/trailing punctuation
    return token if token else None

with open(INPUT_PATH, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        spatial = row.get('spatial_coverage', '')
        # Split on | and ,
        for part in re.split(r'[|,]', spatial):
            cleaned = clean_token(part)
            if cleaned:
                unique_tokens.add(cleaned)

# Write unique tokens to file for review or batch lookup
with open(TOKENS_OUT, 'w', encoding='utf-8') as out:
    for token in sorted(unique_tokens):
        out.write(token + '\n')

print(f"Extracted {len(unique_tokens)} unique place tokens. Written to {TOKENS_OUT}")
