import os
def extract_concepts(data):
    concepts = []
    if isinstance(data, list):
        for item in data:
            concepts.extend(extract_concepts(item))
    elif isinstance(data, dict):
        # If this is a skos:Concept, add it
        if data.get("@type") == "skos:Concept":
            concepts.append(data)
        # If there's an @graph key, recurse
        if "@graph" in data:
            concepts.extend(extract_concepts(data["@graph"]))
    return concepts
import json

input_dir = os.path.join("LCSH", "skos subject", "chunks")
output_file = os.path.join("LCSH", "skos subject", "concepts_only.jsonld")

concepts = []


for fname in os.listdir(input_dir):
    if not fname.endswith(".jsonld"):
        continue
    fpath = os.path.join(input_dir, fname)
    with open(fpath, encoding="utf-8") as f:
        data = json.load(f)
        concepts.extend(extract_concepts(data))

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(concepts, f, indent=2, ensure_ascii=False)

print(f"Done. Output written to {output_file}")
