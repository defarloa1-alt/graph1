import csv
import requests
import time

TOKENS_PATH = '../Subjects/periodo_unique_tokens.txt'
OUTPUT_PATH = '../Subjects/periodo_tokens_wikidata_enriched.csv'
SPARQL_ENDPOINT = 'https://query.wikidata.org/sparql'

# SPARQL template to get all QIDs and their P31, P361, P279
SPARQL_TEMPLATE = '''
SELECT ?item ?itemLabel ?instanceOf ?instanceOfLabel ?partOf ?partOfLabel ?subclassOf ?subclassOfLabel WHERE {
    VALUES ?name { "%s" }
    {
        ?item rdfs:label ?name FILTER (lang(?name) = "en")
    }
    UNION
    {
        ?item skos:altLabel ?name FILTER (lang(?name) = "en")
    }
    OPTIONAL { ?item wdt:P31 ?instanceOf . }
    OPTIONAL { ?item wdt:P361 ?partOf . }
    OPTIONAL { ?item wdt:P279 ?subclassOf . }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
'''

# Read tokens
with open(TOKENS_PATH, encoding='utf-8') as f:
    tokens = [line.strip() for line in f if line.strip()]

results = []

# Use a compliant User-Agent and conservative throttling
USER_AGENT = 'Graph1-Period-Enrichment/1.0 (contact: defarloa1@gmail.com)'

for idx, token in enumerate(tokens):
    query = SPARQL_TEMPLATE % token.replace('"', '\"')
    headers = {
        'Accept': 'application/sparql-results+json',
        'User-Agent': USER_AGENT
    }
    try:
        response = requests.get(SPARQL_ENDPOINT, params={'query': query}, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        found_labels = set()
        for row in data['results']['bindings']:
            item_label = row.get('itemLabel', {}).get('value', '')
            found_labels.add(item_label)
            results.append({
                'token': token,
                'wikidata_qid': row.get('item', {}).get('value', '').split('/')[-1],
                'item_label': item_label,
                'instance_of_qid': row.get('instanceOf', {}).get('value', '').split('/')[-1] if 'instanceOf' in row else '',
                'instance_of_label': row.get('instanceOfLabel', {}).get('value', ''),
                'part_of_qid': row.get('partOf', {}).get('value', '').split('/')[-1] if 'partOf' in row else '',
                'part_of_label': row.get('partOfLabel', {}).get('value', ''),
                'subclass_of_qid': row.get('subclassOf', {}).get('value', '').split('/')[-1] if 'subclassOf' in row else '',
                'subclass_of_label': row.get('subclassOfLabel', {}).get('value', ''),
            })
        if found_labels:
            print(f"Token: {token} | Wikidata label(s): {', '.join(sorted(found_labels))}")
        else:
            print(f"Token: {token} | Wikidata label(s): [none found]")
    except Exception as e:
        print(f"Error for token '{token}': {e}")
    # Conservative throttling: 2 seconds between requests
    time.sleep(2.0)
    if (idx+1) % 20 == 0:
        print(f"Processed {idx+1}/{len(tokens)} tokens...")

# Write results
with open(OUTPUT_PATH, 'w', encoding='utf-8', newline='') as out:
    writer = csv.DictWriter(out, fieldnames=[
        'token','wikidata_qid','item_label','instance_of_qid','instance_of_label',
        'part_of_qid','part_of_label','subclass_of_qid','subclass_of_label'])
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print(f"Wikidata enrichment complete. Results written to {OUTPUT_PATH}")
