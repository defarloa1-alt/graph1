#cip_splitter
import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def resolve_file(candidates):
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("Missing required file. Tried: " + ", ".join(str(p) for p in candidates))


INPUT = resolve_file([
    SCRIPT_DIR / "2-11-26-cip_with_subject_type.csv",
    SCRIPT_DIR / "cip_with_subject_type.csv",
])
output_prefix = "2-11-26-" if INPUT.name.startswith("2-11-26-") else ""

SUBJECTS = SCRIPT_DIR / f"{output_prefix}subjects.csv"
CONCEPTS = SCRIPT_DIR / f"{output_prefix}concepts.csv"
REJECTED = SCRIPT_DIR / f"{output_prefix}rejected.csv"

def main():
    with INPUT.open(newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        fields = reader.fieldnames

        # Writers
        w_sub = csv.DictWriter(SUBJECTS.open("w", newline="", encoding="utf-8"), fields)
        w_con = csv.DictWriter(CONCEPTS.open("w", newline="", encoding="utf-8"), fields)
        w_rej = csv.DictWriter(REJECTED.open("w", newline="", encoding="utf-8"), fields)

        # Headers
        w_sub.writeheader()
        w_con.writeheader()
        w_rej.writeheader()

        for row in reader:
            node_type = row["node_type"]
            subject_type = row["subject_type"]

            # 1. SUBJECTS (disciplines only)
            if subject_type == "discipline":
                w_sub.writerow(row)
                continue

            # 2. REJECTED (noise)
            if node_type in (
                "journal",
                "book",
                "organization",
                "event",
                "exclude_profession",
            ):
                w_rej.writerow(row)
                continue

            # 3. CONCEPTS (everything else)
            w_con.writerow(row)

if __name__ == "__main__":
    main()
