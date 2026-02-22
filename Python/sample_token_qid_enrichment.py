import requests
import csv
import time


# Read full token list from file
TOKENS_PATH = '../Subjects/periodo_unique_tokens.txt'
with open(TOKENS_PATH, encoding='utf-8') as f:
    TOKENS = [line.strip() for line in f if line.strip()]

SEARCH_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Graph1-Period-Enrichment/1.0 (contact: defarloa1@gmail.com)"

# Step 1: Search API for QID
results = []
for token in TOKENS:
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "type": "item",
        "limit": 10,
        "search": token
    }
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(SEARCH_API, params=params, headers=headers)
    r.raise_for_status()
    data = r.json()
    candidates = data.get("search", [])
    best = None
    confidence = 0.0
    all_qids = []
    all_labels = []
    all_descriptions = []
    all_aliases = []
    for c in candidates:
        all_qids.append(c.get("id", ""))
        all_labels.append(c.get("label", ""))
        all_descriptions.append(c.get("description", ""))
        if "aliases" in c:
            all_aliases.extend(c["aliases"])
    for idx_c, c in enumerate(candidates):
        # Prefer exact label match (case-insensitive)
        if c["label"].lower() == token.lower():
            best = c
            confidence = 1.0
            break
        # Prefer alias match (case-insensitive)
        if "aliases" in c and any(token.lower() == alias.lower() for alias in c["aliases"]):
            best = c
            confidence = 0.95
            break
    if not best and candidates:
        best = candidates[0]  # fallback: top result
        confidence = 0.8
    if best:
        print(f"Token: {token} | QID: {best['id']} | Label: {best['label']} | Description: {best.get('description','')} | Confidence: {confidence}")
        results.append({
            "token": token,
            "qid": best["id"],
            "label": best["label"],
            "description": best.get("description", ""),
            "aliases": ";".join(sorted(set(all_aliases))),
            "all_qids": ";".join(sorted(set(all_qids))),
            "all_labels": ";".join(sorted(set(all_labels))),
            "all_descriptions": ";".join(sorted(set(all_descriptions))),
            "confidence": confidence,
            "rank": best.get('match', '')
        })
    else:
        print(f"Token: {token} | QID: [not found]")
        results.append({
            "token": token,
            "qid": "",
            "label": "",
            "description": "",
            "aliases": "",
            "all_qids": "",
            "all_labels": "",
            "all_descriptions": "",
            "confidence": 0.0,
            "rank": ""
        })
    time.sleep(1.0)

# Step 2: Enrich QIDs with SPARQL
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
ENRICHED = []

for row in results:
    qid = row["qid"]
    if not qid:
        ENRICHED.append({**row, "instanceOf_qid": "", "instanceOf_label": "", "subclassOf_qid": "", "subclassOf_label": "", "partOf_qid": "", "partOf_label": ""})
        continue
    query = f'''
    SELECT ?item ?itemLabel ?instanceOf ?instanceOfLabel ?subclassOf ?subclassOfLabel ?partOf ?partOfLabel WHERE {{
      VALUES ?item {{ wd:{qid} }}
      OPTIONAL {{ ?item wdt:P31 ?instanceOf . }}
      OPTIONAL {{ ?item wdt:P279 ?subclassOf . }}
      OPTIONAL {{ ?item wdt:P361 ?partOf . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    '''
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": USER_AGENT
    }
    r = requests.get(SPARQL_ENDPOINT, params={"query": query}, headers=headers)
    r.raise_for_status()
    data = r.json()
    print(f"SPARQL response for QID {qid}:")
    import json
    print(json.dumps(data, indent=2))
    # Collect all values (comma-separated)
    instanceOf_qids = []
    instanceOf_labels = []
    subclassOf_qids = []
    subclassOf_labels = []
    partOf_qids = []
    partOf_labels = []
    for b in data["results"]["bindings"]:
        if "instanceOf" in b:
            instanceOf_qids.append(b["instanceOf"]["value"].split("/")[-1])
        if "instanceOfLabel" in b:
            instanceOf_labels.append(b["instanceOfLabel"]["value"])
        if "subclassOf" in b:
            subclassOf_qids.append(b["subclassOf"]["value"].split("/")[-1])
        if "subclassOfLabel" in b:
            subclassOf_labels.append(b["subclassOfLabel"]["value"])
        if "partOf" in b:
            partOf_qids.append(b["partOf"]["value"].split("/")[-1])
        if "partOfLabel" in b:
            partOf_labels.append(b["partOfLabel"]["value"])
    ENRICHED.append({
        **row,
        "instanceOf_qid": ",".join(sorted(set(instanceOf_qids))),
        "instanceOf_label": ",".join(sorted(set(instanceOf_labels))),
        "subclassOf_qid": ",".join(sorted(set(subclassOf_qids))),
        "subclassOf_label": ",".join(sorted(set(subclassOf_labels))),
        "partOf_qid": ",".join(sorted(set(partOf_qids))),
        "partOf_label": ",".join(sorted(set(partOf_labels)))
    })
    time.sleep(1.0)

# Step 3: Output CSV
with open("../Subjects/sample_token_qid_enriched.csv", "w", encoding="utf-8", newline="") as out:
    writer = csv.DictWriter(out, fieldnames=[
        "token", "qid", "label", "description", "aliases", "all_qids", "all_labels", "all_descriptions", "confidence", "rank",
        "instanceOf_qid", "instanceOf_label",
        "subclassOf_qid", "subclassOf_label",
        "partOf_qid", "partOf_label"
    ])
    writer.writeheader()
    for row in ENRICHED:
        writer.writerow(row)

print("Sample reconciliation and enrichment complete. See ../Subjects/sample_token_qid_enriched.csv")
