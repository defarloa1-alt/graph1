import csv
import os
import re
import requests
import time

WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Helper to fetch broader (P279) and narrower (P361) relationships for a QID
def fetch_broader_narrower(qid):
    query = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?broader ?broaderLabel ?narrower ?narrowerLabel WHERE {{
      OPTIONAL {{ wd:{qid} wdt:P279 ?broader .
                 ?broader rdfs:label ?broaderLabel FILTER (lang(?broaderLabel) = 'en') }}
      OPTIONAL {{ ?narrower wdt:P279 wd:{qid} .
                 ?narrower rdfs:label ?narrowerLabel FILTER (lang(?narrowerLabel) = 'en') }}
    }}
    """
    headers = {"User-Agent": "cip-broader-narrower/1.0 (your_email@example.com)"}
    r = requests.get(WIKIDATA_SPARQL_URL, params={"format": "json", "query": query}, headers=headers)
    r.raise_for_status()
    results = r.json()["results"]["bindings"]
    broader = [(row["broader"]["value"].split("/")[-1], row["broaderLabel"]["value"]) for row in results if "broader" in row]
    narrower = [(row["narrower"]["value"].split("/")[-1], row["narrowerLabel"]["value"]) for row in results if "narrower" in row]
    return broader, narrower

# Resolve input/output filenames so dated and undated files both work.
subject_candidates = ["subjects.csv"]
subject_candidates.extend(
    sorted(
        name for name in os.listdir(SCRIPT_DIR)
        if name.endswith("subjects.csv") and name not in subject_candidates
    )
)
subjects_input = next((name for name in subject_candidates if os.path.exists(os.path.join(SCRIPT_DIR, name))), None)
if subjects_input is None:
    raise FileNotFoundError("Could not find subjects.csv (dated or undated)")

prefix_match = re.match(r"^(\d{1,2}-\d{1,2}-\d{2}-)", subjects_input)
output_prefix = prefix_match.group(1) if prefix_match else ""
subjects_output = f"{output_prefix}subjects_broader_narrower.csv"

# Read subjects.csv
subjects_input_path = os.path.join(SCRIPT_DIR, subjects_input)
subjects_output_path = os.path.join(SCRIPT_DIR, subjects_output)
with open(subjects_input_path, encoding="utf-8") as f_in, open(subjects_output_path, "w", encoding="utf-8", newline="") as f_out:
    rows = list(csv.DictReader(f_in))
    if not rows:
        raise ValueError("subjects.csv is empty")
    fieldnames = list(rows[0].keys())

    # Build QID index for fast lookup
    qid_index = {row["qid"]: row for row in rows if row["qid"]}

    # Prepare to add new columns
    if "broader_than" not in fieldnames or "narrower_than" not in fieldnames:
        fieldnames = list(fieldnames) + ["broader_than", "broader_than_label", "narrower_than", "narrower_than_label"]

    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()

    # Track new rows to add
    new_rows = []
    seen_new_qids = set()

    for row in rows:
        qid = row["qid"]
        if not qid:
            continue
        broader, narrower = fetch_broader_narrower(qid)
        # Only take the first broader/narrower for simplicity (can be extended)
        if broader:
            row["broader_than"] = broader[0][0]
            row["broader_than_label"] = broader[0][1]
            # Add new row if not present
            if broader[0][0] not in qid_index and broader[0][0] not in seen_new_qids:
                new_rows.append({"qid": broader[0][0], "qid_label": broader[0][1]})
                seen_new_qids.add(broader[0][0])
        else:
            row["broader_than"] = ""
            row["broader_than_label"] = ""
        if narrower:
            row["narrower_than"] = narrower[0][0]
            row["narrower_than_label"] = narrower[0][1]
            if narrower[0][0] not in qid_index and narrower[0][0] not in seen_new_qids:
                new_rows.append({"qid": narrower[0][0], "qid_label": narrower[0][1]})
                seen_new_qids.add(narrower[0][0])
        else:
            row["narrower_than"] = ""
            row["narrower_than_label"] = ""
        writer.writerow(row)
        time.sleep(0.5)  # Be polite to Wikidata

    # Add new rows for missing QIDs (minimal info)
    for new_row in new_rows:
        # Fill all columns with empty except qid/qid_label
        full_row = {k: "" for k in fieldnames}
        full_row["qid"] = new_row["qid"]
        full_row["qid_label"] = new_row["qid_label"]
        writer.writerow(full_row)

print(f"Done. Output written to {subjects_output}")
