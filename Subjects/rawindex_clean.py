import csv
import re

input_file = "Subjects/rawindex.txt"
output_file = "Subjects/rawindex_clean.csv"

rows = []
with open(input_file, encoding="utf-8") as f:
    for line in f:
        # Skip header, separator, and empty lines
        if line.strip().startswith("|") and not line.strip().startswith("|-"):
            # Remove web refs and trailing pipes
            line = re.sub(r"\[web:[^\]]*\]", "", line)
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            # Only keep rows with at least 3 columns (Term, QID, Label)
            if len(parts) >= 3:
                rows.append(parts[:5])  # Only keep first 5 columns

# Write to CSV
with open(output_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Term", "QID", "Label", "P31_instance_of", "P279_subclass_of"])
    for row in rows:
        writer.writerow(row)

print(f"Done. Output written to {output_file}")
