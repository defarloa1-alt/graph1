"""Fix ciphers to use concept QID (not seed QID)."""
import hashlib, json

with open("output/subject_schema/Q17167_subject_schema.json") as f:
    s = json.load(f)

fixed = 0
for sc in s["subject_concepts"]:
    qid = sc.get("wikidata_qid", "")
    sh = sc.get("lcsh_id", "")
    if not qid or qid == "NEEDS_LOOKUP" or not sh or sh == "NEEDS_LOOKUP":
        continue
    correct = hashlib.sha256(f"SUBJECT_CONCEPT|{qid}|{sh}".encode()).hexdigest()
    old = sc.get("concept_cipher", "")
    if old != correct:
        print(f"  FIX {sc['label']}: {old[:16]} -> {correct[:16]}")
        sc["concept_cipher"] = correct
        fixed += 1

with open("output/subject_schema/Q17167_subject_schema.json", "w", encoding="utf-8") as f:
    json.dump(s, f, indent=2, ensure_ascii=False)
print(f"Fixed {fixed} ciphers")
