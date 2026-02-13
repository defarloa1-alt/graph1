import json
import csv

import pandas as pd

# Path to the CSV file you have
csv_input_path = 'c:/projects/graph1/Subjects/sample_token_qid_enriched.csv'
# Output CSV path (can be changed as needed)
csv_output_path = 'c:/projects/graph1/Subjects/sample_token_qid_enriched_copy.csv'

# Read the CSV file
df = pd.read_csv(csv_input_path, encoding='utf-8')

# Save a copy or process as needed
df.to_csv(csv_output_path, index=False, encoding='utf-8')

print(f"Copied {csv_input_path} to {csv_output_path}")
