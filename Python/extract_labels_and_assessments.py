import json
import re

input_file = "subjects_sample_50_llm_responses.json"
output_file = "subjects_labels_and_assessments.json"

results = []

with open(input_file, encoding="utf-8") as f:
    data = json.load(f)
    for entry in data:
        subject_label = None
        # Try to extract label from the llm_prompt string
        match = re.search(r"subject '([^']+)'", entry.get("llm_prompt", ""))
        if match:
            subject_label = match.group(1)
        else:
            subject_label = entry.get("subject_id", "")
        assessment = None
        # Try to extract assessment string from the llm_response content
        content = entry.get("llm_response", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
        assess_match = re.search(r"assessment(?: string)?:?\s*`?([HML]+)`?", content, re.IGNORECASE)
        if not assess_match:
            assess_match = re.search(r"\*\*Assessment(?: String)?\*\*: ?`?([HML]+)`?", content, re.IGNORECASE)
        if not assess_match:
            assess_match = re.search(r"assessment\s*:?\s*\"([HML]+)\"", content, re.IGNORECASE)
        if assess_match:
            assessment = assess_match.group(1)
        results.append({
            "subject_label": subject_label,
            "assessment": assessment
        })

with open(output_file, "w", encoding="utf-8") as out:
    json.dump(results, out, ensure_ascii=False, indent=2)

print(f"Extracted {len(results)} subject labels and assessments to {output_file}")
