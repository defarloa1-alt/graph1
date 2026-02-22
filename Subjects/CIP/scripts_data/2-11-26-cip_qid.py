# cip to qid
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
# Load CIP source
# ---------------------------------------------------------
cip_rows = []
cip_source_path = resolve_file([
    SCRIPT_DIR / "2-11-26-cip_source.csv",
    SCRIPT_DIR / "cip_source.csv",
    CIP_DIR / "2-11-26-cip_source.csv",
    CIP_DIR / "cip_source.csv",
])
with cip_source_path.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cip_rows.append(row)

# ---------------------------------------------------------

# Load property registry
registry_pids = []
property_map_path = resolve_file([
    CIP_DIR / "2-11-26-property_id,property_label,first_seen_in.csv",
    CIP_DIR / "property_id,property_label,first_seen_in.csv",
    SCRIPT_DIR / "2-11-26-property_id,property_label,first_seen_in.csv",
    SCRIPT_DIR / "property_id,property_label,first_seen_in.csv",
])
with property_map_path.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        registry_pids.append(row["property_id"])
registry_pids = list(dict.fromkeys(registry_pids))  # dedupe

# Load discipline registry (QID to label)
discipline_labels = {}
discipline_registry_path = resolve_file([
    SCRIPT_DIR / "2-11-26-disciplines_registry.csv",
    SCRIPT_DIR / "disciplines_registry.csv",
    CIP_DIR / "2-11-26-disciplines_registry.csv",
    CIP_DIR / "disciplines_registry.csv",
])
with discipline_registry_path.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        qid = row["discipline"].replace("http://www.wikidata.org/entity/", "").strip()
        label = row["disciplineLabel"].strip()
        discipline_labels[qid] = label


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def normalize_label(label: str) -> str:
    """Normalize CIP label for Wikidata search."""
    core = label.split(",")[0].split("/")[0]
    core = re.sub(r"\(.*?\)", "", core)
    core = re.sub(r"[.,]", "", core)
    return core.strip()


def wikidata_search(term: str):
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "type": "item",
        "search": term
    }
    headers = {"User-Agent": "cip-matcher/1.0 (defarloa1@gmail.com)"}  # TODO: Replace with your email or project info
    # Optionally add authentication if you have Wikidata credentials
    # Example: auth = ("username", "password")
    r = requests.get(WIKIDATA_API_URL, params=params, headers=headers)
    r.raise_for_status()
    return r.json().get("search", [])


def fetch_properties(qid: str, pids):
    prefix = """
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    """
    select = " ".join([f"?{pid}" for pid in pids])
    optional = "\n".join([f"OPTIONAL {{ wd:{qid} wdt:{pid} ?{pid} . }}" for pid in pids])

    query = f"""
    {prefix}
    SELECT {select} WHERE {{
      {optional}
    }} LIMIT 1
    """

    headers = {"User-Agent": "cip-matcher/1.0 (your_email@example.com)"}  # TODO: Replace with your email or project info
    # Optionally add authentication if you have Wikidata credentials
    # Example: auth = ("username", "password")
    r = requests.get(WIKIDATA_SPARQL_URL, params={"format": "json", "query": query}, headers=headers)
    r.raise_for_status()
    return r.json().get("results", {}).get("bindings", [])


# ---------------------------------------------------------
# Subject validation (the FIXED version)
# ---------------------------------------------------------

VALID_P31 = {
    "Q11862829",  # academic discipline / field of study
    "Q2465832",   # branch of science
    "Q336",       # applied science
    "Q8068",      # engineering discipline
    "Q34749",     # social science
    "Q80071",     # humanities discipline
    "Q28640",     # profession
    "Q12737077",  # occupation
    "Q8148",      # industry
    "Q3606845",   # agricultural science
    "Q7991",      # natural science
    "Q188",       # life science
    "Q2374149",   # environmental science
    "Q420",       # biological science
    "Q11023"      # technical field
}

DISCIPLINE_SUFFIXES = (
    "science", "sciences", "studies", "engineering", "technology",
    "management", "economics", "education", "agriculture",
    "horticulture", "forestry", "ecology", "biology",
    "chemistry", "physics"
)


def is_valid_subject(qid: str, qlabel: str, cip_label: str) -> bool:
    """Return True if QID is a valid CIP subject."""
    try:
        props = fetch_properties(qid, ["P31", "P279", "P921"])
    except:
        return False

    if not props:
        return False

    row = props[0]

    # Rule 1: P31
    if "P31" in row:
        cls = row["P31"]["value"].split("/")[-1]
        if cls in VALID_P31:
            return True

    # Rule 2: P279
    if "P279" in row:
        cls = row["P279"]["value"].split("/")[-1]
        if cls in VALID_P31:
            return True

    # Rule 3: P921 (main subject)
    if "P921" in row:
        return True

    # Rule 4: label pattern
    l = qlabel.lower()
    if any(l.endswith(s) for s in DISCIPLINE_SUFFIXES):
        return True

    # Rule 5: CIP label pattern
    cl = cip_label.lower()
    if any(cl.endswith(s) for s in DISCIPLINE_SUFFIXES):
        return True

    return False


# ---------------------------------------------------------
# CIP level detection
# ---------------------------------------------------------
def cip_level(row):
    h = row["cip_header"]
    c = row["cip_category"]
    s = row["cip_subclass"]
    if c == "00" and s == "00":
        return "2-digit"
    if s == "00":
        return "4-digit"
    return "6-digit"


# ---------------------------------------------------------
# Prepare output
# ---------------------------------------------------------
base_fields = [
    "cip_id", "cip_label", "cip_header", "cip_category", "cip_subclass", "cip_level",
    "qid", "qid_label", "qid_description"
]

prop_fields = []
for pid in registry_pids:
    prop_fields.append(f"{pid}_qids")
    prop_fields.append(f"{pid}_labels")

fieldnames = base_fields + prop_fields

output_prefix = "2-11-26-" if cip_source_path.name.startswith("2-11-26-") else ""
output_path = SCRIPT_DIR / f"{output_prefix}cip_wikidata_rich.csv"
out = output_path.open("w", encoding="utf-8", newline="")
writer = csv.DictWriter(out, fieldnames=fieldnames)
writer.writeheader()


# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
for idx, row in enumerate(cip_rows, 1):
    cip_id = row["cip_id"]
    cip_label = row["cip_label"]

    print(f"[{idx}/{len(cip_rows)}] {cip_id} | {cip_label}")

    term = normalize_label(cip_label)
    if not term:
        continue

    # Search Wikidata
    try:
        results = wikidata_search(term)
    except Exception as e:
        print(f"  [WARN] search failed for '{term}': {e}")
        continue

    if not results:
        print("  no search results")
        continue


    qid = results[0]["id"]
    # Use discipline registry for label if available, else fallback to API label
    qlabel = discipline_labels.get(qid, results[0]["label"])
    # If label is a QID (no English label), set to empty string
    if qlabel == qid:
        qlabel = ""
    qdesc = results[0].get("description", "")

    # Print QID and QID label when successful
    print(f"  QID: {qid} | QID Label: {qlabel}")

    # Validate subject
    try:
        if not is_valid_subject(qid, qlabel, cip_label):
            print(f"  rejected {qid} ({qlabel}) as non-subject")
            continue
    except Exception as e:
        print(f"  [WARN] validation failed for {qid}: {e}")
        continue

    # Fetch registry properties
    try:
        bindings = fetch_properties(qid, registry_pids)
    except Exception as e:
        print(f"  [WARN] property fetch failed for {qid}: {e}")
        bindings = []

    prop_row = bindings[0] if bindings else {}

    # Build output row
    outrow = {
        "cip_id": cip_id,
        "cip_label": cip_label,
        "cip_header": row["cip_header"],
        "cip_category": row["cip_category"],
        "cip_subclass": row["cip_subclass"],
        "cip_level": cip_level(row),
        "qid": qid,
        "qid_label": qlabel,
        "qid_description": qdesc
    }

    # Fill property columns
    for pid in registry_pids:
        if pid in prop_row:
            val = prop_row[pid]["value"]
            target_qid = val.split("/")[-1]
            outrow[f"{pid}_qids"] = target_qid
            outrow[f"{pid}_labels"] = ""
        else:
            outrow[f"{pid}_qids"] = ""
            outrow[f"{pid}_labels"] = ""

    writer.writerow(outrow)
    time.sleep(0.5)  # be polite to Wikidata

out.close()
