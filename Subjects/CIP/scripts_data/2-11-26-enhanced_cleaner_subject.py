#enhanced cip cleaner
import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def resolve_file(candidates):
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("Missing required file. Tried: " + ", ".join(str(p) for p in candidates))


INPUT = resolve_file([
    SCRIPT_DIR / "2-11-26-cip_concept_subject_clean_patched.csv",
    SCRIPT_DIR / "cip_concept_subject_clean_patched.csv",
])
output_prefix = "2-11-26-" if INPUT.name.startswith("2-11-26-") else ""
OUTPUT = SCRIPT_DIR / f"{output_prefix}cip_with_subject_type.csv"

with INPUT.open(newline="", encoding="utf-8") as f_in, \
     OUTPUT.open("w", newline="", encoding="utf-8") as f_out:

    reader = csv.DictReader(f_in)
    fieldnames = reader.fieldnames + ["subject_type"]

    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        node_type = row["node_type"]

        # Only academic disciplines get a subject_type
        if node_type == "concept_subject":
            row["subject_type"] = "discipline"
        else:
            row["subject_type"] = ""

        writer.writerow(row)

print(f"Wrote {OUTPUT.name}")
