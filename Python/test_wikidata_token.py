import requests

SPARQL_ENDPOINT = 'https://query.wikidata.org/sparql'
USER_AGENT = 'Graph1-Period-Enrichment/1.0 (contact: defarloa1@gmail.com)'

def test_token(token):
    query = '''
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
    ''' % token.replace('"', '\"')
    headers = {
        'Accept': 'application/sparql-results+json',
        'User-Agent': USER_AGENT
    }
    print(f"Testing token: {token}\nSPARQL Query:\n{query}")
    response = requests.get(SPARQL_ENDPOINT, params={'query': query}, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()
    print(f"Results for token '{token}':")
    for row in data['results']['bindings']:
        print({
            'wikidata_qid': row.get('item', {}).get('value', '').split('/')[-1],
            'item_label': row.get('itemLabel', {}).get('value', ''),
            'instance_of_qid': row.get('instanceOf', {}).get('value', '').split('/')[-1] if 'instanceOf' in row else '',
            'instance_of_label': row.get('instanceOfLabel', {}).get('value', ''),
            'part_of_qid': row.get('partOf', {}).get('value', '').split('/')[-1] if 'partOf' in row else '',
            'part_of_label': row.get('partOfLabel', {}).get('value', ''),
            'subclass_of_qid': row.get('subclassOf', {}).get('value', '').split('/')[-1] if 'subclassOf' in row else '',
            'subclass_of_label': row.get('subclassOfLabel', {}).get('value', ''),
        })
    if not data['results']['bindings']:
        print("No results found.")

if __name__ == "__main__":
    test_token("Afghanistan")
