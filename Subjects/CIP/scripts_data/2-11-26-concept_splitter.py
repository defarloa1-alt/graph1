#concept_splitter
import csv
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent


def resolve_file(candidates):
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("Missing required file. Tried: " + ", ".join(str(p) for p in candidates))


INPUT = resolve_file([
    SCRIPT_DIR / "2-11-26-concepts.csv",
    SCRIPT_DIR / "concepts.csv",
])
output_prefix = "2-11-26-" if INPUT.name.startswith("2-11-26-") else ""
OUTPUT = SCRIPT_DIR / f"{output_prefix}concepts_with_hierarchy.csv"

def parent_of(cip_id: str):
    # 6-digit → 4-digit
    if cip_id.endswith("00"):
        return None
    return cip_id[:4] + "00"

# Load all rows
rows = []
with INPUT.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)
if not rows:
    raise ValueError(f"{INPUT.name} is empty")

# Index by CIP ID
by_cip = {r["cip_id"]: r for r in rows}

# Create synthetic parent rows if missing
def ensure_parent_exists(cip_id):
    parent = parent_of(cip_id)
    if parent and parent not in by_cip:
        # Create synthetic parent
        synthetic = {
            "cip_id": parent,
            "cip_label": "",  # will fill later
            "cip_header": parent[:2],
            "cip_category": parent[3:5],
            "cip_subclass": "00",
            "cip_level": "4-digit",
            "node_type": "concept_other",
            "subject_type": "",
        }
        # Copy all other fields as empty
        for k in rows[0].keys():
            synthetic.setdefault(k, "")
        by_cip[parent] = synthetic
    return parent

# Build broader/narrower
children = defaultdict(list)
for r in rows:
    parent = ensure_parent_exists(r["cip_id"])
    if parent:
        children[parent].append(r["cip_id"])

# Add hierarchy fields
for r in rows:
    cid = r["cip_id"]
    parent = parent_of(cid)

    r["broader_cip_id"] = parent or ""
    r["broader_label"] = by_cip[parent]["cip_label"] if parent else ""

    kids = children.get(cid, [])
    r["narrower_cip_ids"] = ";".join(kids)
    r["narrower_labels"] = ";".join(by_cip[k]["cip_label"] for k in kids)

# Write output
with OUTPUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("Wrote", OUTPUT)
