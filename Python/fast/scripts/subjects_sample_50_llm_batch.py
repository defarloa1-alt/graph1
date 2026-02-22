import os
import json
import requests
import time

API_URL = "https://api.perplexity.ai/chat/completions"
API_KEY = os.getenv("PERPLEXITY_API_KEY")
INPUT_FILE = "../output/subjects_sample_50_llm_prompts.json"
OUTPUT_FILE = "../output/subjects_sample_50_llm_responses.json"
MODEL = "sonar-pro"

if not API_KEY:
    print("PERPLEXITY_API_KEY not set in environment.")
    exit(1)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def call_perplexity(prompt):
    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 600
    }
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        prompts = json.load(f)

    results = []
    # Only process the first subject for testing
    for item in prompts[:100]:
        subject_id = item.get("subject_id", "")
        # Build a concise prompt for scoring only
        subject_label = ""
        subject_record = None
        try:
            subject_record = json.loads(item["llm_prompt"].split('Subject record:')[1].strip())
            subject_label = subject_record["@graph"][0]["skos:prefLabel"]["@value"]
        except Exception:
            subject_label = item.get("subject_id", "")
        concise_prompt = (
            f"For the subject '{subject_label}':\n"
            "1. Score the relevance of each Facet Class (PoliticalFacet, CulturalFacet, TechnologicalFacet, ReligiousFacet, EconomicFacet, MilitaryFacet, EnvironmentalFacet, DemographicFacet, IntellectualFacet, ScientificFacet, ArtisticFacet, SocialFacet, LinguisticFacet, ArchaeologicalFacet, DiplomaticFacet) with a confidence score (0-1).\n"
            "2. For each facet, assign H if score > 0.75, L if < 0.5, and M for the rest.\n"
            "3. Concatenate these codes in facet order into a string called 'assessment'.\n"
            "4. Search for the subject in Wikidata and Wikipedia. If found in Wikidata, add a '+' to the assessment string, if not add '-'. Do the same for Wikipedia. Append these two symbols to the assessment string (e.g., 'MLHLLLMLMMLH++').\n"
            "5. Calculate a final score: H = 1 point, M = 0.5 points, L = 0 points, Wikidata hit = +2, Wikipedia hit = +2. Return the score as 'final_score'.\n"
            "6. Return a JSON object with: 'facet_scores', 'assessment', 'wikidata_hit', 'wikipedia_hit', and 'final_score'."
        )
        print(f"Processing subject: {subject_id}")
        result = call_perplexity(concise_prompt)
        results.append({
            "subject_id": subject_id,
            "llm_prompt": concise_prompt,
            "llm_response": result
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(results, out, ensure_ascii=False, indent=2)
    print(f"Saved {len(results)} responses to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
