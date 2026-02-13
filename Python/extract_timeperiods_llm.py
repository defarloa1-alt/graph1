"""
Script to extract subject, dates, and geo location from a Markdown file using Perplexity LLM API (or similar LLM API).
- Input: timeperiods.md
- Output: JSONL or CSV with fields: subject, date(s), geo_location
- Requires: requests, API key for Perplexity (or OpenAI, etc.)
"""
import os
import requests
import json



# Get Perplexity API key from PPLX_API_KEY environment variable
PPLX_API_KEY = os.getenv('PPLX_API_KEY')
if not PPLX_API_KEY:
    raise EnvironmentError("PPLX_API_KEY environment variable not set.")


INPUT_FILE = '../timeperiods.md'
OUTPUT_FILE = 'timeperiods_extracted.jsonl'
BATCH_SIZE = 3000  # characters per batch
RECORDS_PER_BATCH = 20

SAMPLE_JSON = '{"lcsh_id": "sh85026371", "label": "Bronze Age", "narrower_than": [{"id": "sh85026372", "label": "Early Bronze Age"}], "broader_than": [{"id": "sh85026200", "label": "Ancient history"}], "category_id": "cat123", "category_label": "Historical Periods", "dates": "c. 3300–1200 BC", "geo_location": "Eurasia"}'

PROMPT_TEMPLATE = (
    f"We are building a subject index for constructing timelines of history from political, social, economic, technical, and cultural perspectives. "
    "A proper subject must be able to be tied to a geographical area and a start and end date. Do not include events. "
    "Our knowledge graph will create an agent for most of these subjects, and they will learn the subject area. "
    f"Extract up to {RECORDS_PER_BATCH} subject records from the following Markdown. For each subject, return a JSON object with the following fields: "
    "lcsh_id (if present), label (subject name), narrower_than (array of objects with id and label), broader_than (array of objects with id and label), "
    "category_id (if present), category_label (if present), dates (required), geo_location (required). "
    "If a field is missing, use null. Output one JSON object per line. Only include subject records, not events.\n"
    "Example output:\n"
    f"{SAMPLE_JSON}\n\n"
    "Markdown:\n"
)



print(f"Reading input file: {INPUT_FILE}")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    md_text = f.read()
print(f"Loaded {len(md_text)} characters from input file.")

url = 'https://api.perplexity.ai/chat/completions'
headers = {
    'Authorization': f'Bearer {PPLX_API_KEY}',
    'Content-Type': 'application/json',
}

num_batches = (len(md_text) + BATCH_SIZE - 1) // BATCH_SIZE
print(f"Processing in {num_batches} batches of {BATCH_SIZE} characters each.")

with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
    for i in range(num_batches):
        start = i * BATCH_SIZE
        end = min((i + 1) * BATCH_SIZE, len(md_text))
        chunk = md_text[start:end]
        prompt = PROMPT_TEMPLATE + chunk
        print(f"\nBatch {i+1}/{num_batches}: Sending request to Perplexity API...")
        data = {
            'model': 'sonar-pro',
            'messages': [
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 2048,
            'temperature': 0.2,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            llm_text = result['choices'][0]['message']['content']
            out.write(llm_text.strip() + '\n')
            print(f"Batch {i+1} complete. Results appended to {OUTPUT_FILE}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
