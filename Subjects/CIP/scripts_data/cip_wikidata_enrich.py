import csv
import requests
import time
import re
from pathlib import Path

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"

SCRIPT_DIR = Path(__file__).resolve().parent
CIP_DIR = SCRIPT_DIR.parent


def resolve_file(candidates):
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("Missing required file. Tried: " + ", ".join(str(p) for p in candidates))

# ---------------------------------------------------------
# Load CIP labels and IDs
# ---------------------------------------------------------
cip_rows = []
cip_source_path = resolve_file([
    SCRIPT_DIR / "2-11-26-cip_source.csv",
    SCRIPT_DIR / "cip_source.csv",
    CIP_DIR / "2-11-26-cip_source.csv",
    CIP_DIR / "cip_source.csv",
])
with cip_source_path.open(encoding="utf-8") as cipfile:
    reader = csv.DictReader(cipfile)
    for row in reader:
        cip_rows.append(row)

# ---------------------------------------------------------
# Load property IDs
# ---------------------------------------------------------
property_ids = []
property_labels = []
property_map_path = resolve_file([
    CIP_DIR / "2-11-26-property_id,property_label,first_seen_in.csv",
    CIP_DIR / "property_id,property_label,first_seen_in.csv",
    SCRIPT_DIR / "2-11-26-property_id,property_label,first_seen_in.csv",
    SCRIPT_DIR / "property_id,property_label,first_seen_in.csv",
])
with property_map_path.open(encoding="utf-8") as propfile:
    reader = csv.DictReader(propfile)
    for row in reader:
        property_ids.append(row["property_id"])
        property_labels.append(row["property_label"])

# ---------------------------------------------------------
# Prepare output
# ---------------------------------------------------------
output_fields = ["qid", "qid_label", "cip_id", "cip_label"]

output_prefix = "2-11-26-" if cip_source_path.name.startswith("2-11-26-") else ""
output_path = CIP_DIR / f"{output_prefix}cip_wikidata_enriched.csv"
with output_path.open("w", encoding="utf-8", newline="") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=output_fields)
    writer.writeheader()

    for idx, cip in enumerate(cip_rows, 1):
        # 🔧 Adjust these two lines to match your actual CIP headers
        # If your CSV uses cip_6_digit / cip_title, use those:
        # cip_id = cip["cip_6_digit"]
        # cip_label = cip["cip_title"]
        cip_id = cip.get("cip_id", cip.get("cip_6_digit", "")).strip()
        cip_label = cip.get("cip_label", cip.get("cip_title", "")).strip().strip('"')

        print(f"[{idx}/{len(cip_rows)}] Processing: {cip_id} | {cip_label}")

        # ---------------------------------------------------------
        # STRICT NORMALIZATION RULE:
        # Use ONLY the text before any comma or slash
        # ---------------------------------------------------------
        label_main = cip_label.split(',')[0].split('/')[0].strip()
        label_clean = re.sub(r'[.,()]', '', label_main).strip()

        print(f"  Normalized search label: '{label_clean}'")

        # Only ONE deterministic search term
        search_terms = [label_clean] if label_clean else [cip_label]

        qid = None
        qid_label = None

        # ---------------------------------------------------------
        # Wikidata API search
        # ---------------------------------------------------------
        headers = {"User-Agent": "cip-matcher/1.0 (your_email@example.com)"}

        for term in search_terms:
            print(f"  Trying search term: '{term}' (API)")
            params = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "type": "item",
                "search": term
            }
            try:
                r = requests.get(WIKIDATA_API_URL, params=params, headers=headers)
                r.raise_for_status()
                data = r.json()
                search_results = data.get("search", [])
                if search_results:
                    qid = search_results[0]["id"]
                    qid_label = search_results[0]["label"]
                    print(f"    QID: {qid} | Label: {qid_label}")
                    break
            except Exception as e:
                print(f"[WARN] Failed to get QID for '{cip_label}' (term '{term}'): {e}")

        # ---------------------------------------------------------
        # If no QID found, write empty row
        # ---------------------------------------------------------

        if not qid:
            print(f"    No match found for: {cip_label}")
            row = {
                "qid": "",
                "qid_label": "",
                "cip_id": cip_id,
                "cip_label": cip_label
            }
            writer.writerow(row)
            continue


        # Write output row (QID and label only)
        row = {
            "qid": qid,
            "qid_label": qid_label,
            "cip_id": cip_id,
            "cip_label": cip_label
        }
        writer.writerow(row)

        time.sleep(0.5)  # Be polite to Wikidata
