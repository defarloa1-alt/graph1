"""
Decompose a given anchor (facet or category) into logical subcomponents using Perplexity LLM.
Input: CSV with columns: fc, rf, f, a, rc, inRel, rt, mwd, wd, mcc, cc, mcp, cp

Usage:
- Place your anchor and related rows in a CSV file (e.g., anchor_decompose.csv)
- Run: python decompose_anchor_llm.py --input anchor_decompose.csv --anchor_label "Demographic"
- The script will send the anchor and its context to Perplexity and print the decomposition.
"""
import os
import csv
import argparse
import requests

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

PROMPT_TEMPLATE = """
Given the following anchor and its immediate subcomponents (from a knowledge graph), decompose the anchor one level down logically. List the most meaningful subfacets or subcategories that should exist under this anchor, based on the context and definitions provided. Use the background rows as context, but focus on the anchor provided.

Anchor:
{anchor}

Context rows:
{rows}

Return a list of subcomponents with a short label and a one-sentence definition for each.
"""

def read_csv_rows(input_file):
    with open(input_file, encoding='utf-8') as f:
        reader = csv.DictReader(f, fieldnames=[
            'fc','rf','f','a','rc','inRel','rt','mwd','wd','mcc','cc','mcp','cp'])
        return list(reader)

def build_prompt(anchor, rows):
    context = '\n'.join([str(row) for row in rows])
    return PROMPT_TEMPLATE.format(anchor=anchor, rows=context)

def call_perplexity(prompt):
    if not PERPLEXITY_API_KEY:
        raise RuntimeError("PERPLEXITY_API_KEY environment variable not set.")
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3-sonar-large-32k-online",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
        "temperature": 0.3
    }
    response = requests.post(PERPLEXITY_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def main():
    parser = argparse.ArgumentParser(description='Decompose anchor using Perplexity LLM')
    parser.add_argument('--input', required=True, help='CSV file with anchor and context rows')
    parser.add_argument('--anchor_qids', nargs='+', required=True, help='List of anchor QIDs to decompose (e.g. Q37732 Q177626 ...)')
    args = parser.parse_args()

    rows = read_csv_rows(args.input)
    for anchor_qid in args.anchor_qids:
        # Find the anchor row by QID
        anchor_row = next((row for row in rows if anchor_qid in str(row)), None)
        if not anchor_row:
            print(f"Anchor QID '{anchor_qid}' not found in input.")
            continue
        prompt = build_prompt(anchor_row, rows)
        print(f"\n=== Anchor QID: {anchor_qid} ===\n")
        print("--- Prompt to Perplexity ---\n")
        print(prompt)
        print("\n--- LLM Output ---\n")
        result = call_perplexity(prompt)
        print(result)

if __name__ == "__main__":
    main()
