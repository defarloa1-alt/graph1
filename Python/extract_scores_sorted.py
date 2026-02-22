import json
import re

input_file = "subjects_sample_50_llm_responses.json"
output_file = "subjects_scores_sorted_by_lcshid.json"

results = []


import json as _json
def extract_json_block(content):
    match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
    if match:
        try:
            return _json.loads(match.group(1))
        except Exception:
            pass
    # Try to find a JSON block without markdown
    match = re.search(r'(\{[\s\S]*?\})', content)
    if match:
        try:
            return _json.loads(match.group(1))
        except Exception:
            pass
    return None

def extract_score(content):
    block = extract_json_block(content)
    if block and "final_score" in block:
        return block["final_score"]
    # Fallback to regex
    score_match = re.search(r'"final_score"\s*:\s*([\d\.]+)', content)
    if score_match:
        return float(score_match.group(1))
    score_match = re.search(r'final_score\s*[:=]\s*([\d\.]+)', content)
    if score_match:
        return float(score_match.group(1))
    return None

def extract_assessment(content):
    block = extract_json_block(content)
    if block and "assessment" in block:
        return block["assessment"]
    # Fallback to regex
    assess_match = re.search(r'assessment(?: string)?\s*:?\s*`?([HML\+\-]+)`?', content, re.IGNORECASE)
    if not assess_match:
        assess_match = re.search(r'\*\*Assessment(?: String)?\*\*: ?`?([HML\+\-]+)`?', content, re.IGNORECASE)
    if not assess_match:
        assess_match = re.search(r'assessment\s*:?\s*\"([HML\+\-]+)\"', content, re.IGNORECASE)
    if assess_match:
        return assess_match.group(1)
    return None

with open(input_file, encoding="utf-8") as f:
    data = json.load(f)
    for entry in data:
        subject_label = None
        match = re.search(r"subject '([^']+)'", entry.get("llm_prompt", ""))
        if match:
            subject_label = match.group(1)
        else:
            subject_label = entry.get("subject_id", "")
        subject_id = entry.get("subject_id", "")
        # Extract numeric part of LCSH ID for sorting
        lcsh_num_match = re.search(r'sh(\d+)', subject_id)
        lcsh_num = int(lcsh_num_match.group(1)) if lcsh_num_match else -1
        content = entry.get("llm_response", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
        score = extract_score(content)
        assessment = extract_assessment(content)
        results.append({
            "subject_label": subject_label,
            "score": score,
            "assessment": assessment,
            "subject_id": subject_id,
            "lcsh_num": lcsh_num
        })


# Sort by LCSH numeric ID descending
results_sorted = sorted(results, key=lambda x: x["lcsh_num"], reverse=True)


with open(output_file, "w", encoding="utf-8") as out:
    json.dump(results_sorted, out, ensure_ascii=False, indent=2)

print(f"Extracted and sorted {len(results_sorted)} subjects by LCSH ID to {output_file}")
