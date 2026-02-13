import json

input_file = "subjects_scores_sorted.json"
output_file = "subjects_nulls.json"

with open(input_file, encoding="utf-8") as f:
    data = json.load(f)
    nulls = [entry for entry in data if entry["assessment"] is None]

with open(output_file, "w", encoding="utf-8") as out:
    json.dump(nulls, out, ensure_ascii=False, indent=2)

print(f"Extracted {len(nulls)} subjects with null assessments to {output_file}")
