import csv
import os
import re
import sys
import requests
import time

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "cip-property-enrich/1.0 (your_email@example.com)"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Resolve input/output filenames so dated and undated files both work.
property_candidates = ["property_id,property_label,first_seen_in.csv"]
property_candidates.extend(
    sorted(
        name for name in os.listdir(SCRIPT_DIR)
        if name.endswith("property_id,property_label,first_seen_in.csv") and name not in property_candidates
    )
)
property_input = next((name for name in property_candidates if os.path.exists(os.path.join(SCRIPT_DIR, name))), None)
if property_input is None:
    raise FileNotFoundError("Could not find property_id,property_label,first_seen_in.csv (dated or undated)")

subjects_candidates = ["subjects_broader_narrower.csv"]
subjects_candidates.extend(
    sorted(
        name for name in os.listdir(SCRIPT_DIR)
        if name.endswith("subjects_broader_narrower.csv") and name not in subjects_candidates
    )
)
subjects_input = next((name for name in subjects_candidates if os.path.exists(os.path.join(SCRIPT_DIR, name))), None)
if subjects_input is None:
    raise FileNotFoundError("Could not find subjects_broader_narrower.csv (dated or undated)")

prefix_match = re.match(r"^(\d{1,2}-\d{1,2}-\d{2}-)", subjects_input)
output_prefix = prefix_match.group(1) if prefix_match else ""
output_file = f"{output_prefix}subjects_properties_enriched.csv"

# Read property list
property_input_path = os.path.join(SCRIPT_DIR, property_input)
subjects_input_path = os.path.join(SCRIPT_DIR, subjects_input)
output_path = os.path.join(SCRIPT_DIR, output_file)

with open(property_input_path, encoding="utf-8") as f:
    prop_reader = csv.DictReader(f)
    properties = [row["property_id"] for row in prop_reader]

# Read subjects
with open(subjects_input_path, encoding="utf-8") as f:
    subj_reader = csv.DictReader(f)
    fieldnames = list(subj_reader.fieldnames)
    for pid in properties:
        if f"{pid}_qids" not in fieldnames:
            fieldnames.append(f"{pid}_qids")
        if f"{pid}_labels" not in fieldnames:
            fieldnames.append(f"{pid}_labels")
    rows = list(subj_reader)

# Helper to fetch property values for a QID
def fetch_properties_with_labels(qid, pids):
        results = {}
        for pid in pids:
                query = f'''
                PREFIX wd: <http://www.wikidata.org/entity/>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?val ?valLabel WHERE {{
                    wd:{qid} wdt:{pid} ?val .
                    OPTIONAL {{ ?val rdfs:label ?valLabel FILTER (lang(?valLabel) = "en") }}
                }}
                '''
                headers = {"User-Agent": USER_AGENT}
                r = requests.get(WIKIDATA_SPARQL_URL, params={"format": "json", "query": query}, headers=headers)
                r.raise_for_status()
                bindings = r.json()["results"]["bindings"]
                if bindings:
                        results[pid] = bindings[0]
                else:
                        results[pid] = {}
        return results

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for idx, row in enumerate(rows, 1):
        qid = row.get("qid", "")
        if not qid:
            writer.writerow(row)
            continue
        try:
            bindings = fetch_properties_with_labels(qid, properties)
        except Exception as e:
            print(f"[{idx}] WARN: property fetch failed for {qid}: {e}")
            time.sleep(1)
            writer.writerow(row)
            continue
        print(f"[{idx}] Subject QID: {qid} | Label: {row.get('qid_label', '')}")
        for pid in properties:
            prop_row = bindings.get(pid, {})
            if "val" in prop_row:
                val = prop_row["val"]["value"]
                target_qid = val.split("/")[-1]
                label = prop_row.get("valLabel", {}).get("value", "")
                row[f"{pid}_qids"] = target_qid
                row[f"{pid}_labels"] = label
                print(f"    {pid}: {target_qid} - {label}")
            else:
                row[f"{pid}_qids"] = ""
                row[f"{pid}_labels"] = ""

        # Print any other values found for the columns
        for col in fieldnames:
            if row.get(col) and col not in [f"{pid}_qids" for pid in properties] + [f"{pid}_labels" for pid in properties]:
                print(f"    {col}: {row[col]}")
        writer.writerow(row)
        time.sleep(0.5)  # Be polite to Wikidata

print(f"Done. Output written to {output_file}")
