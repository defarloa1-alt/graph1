import json
import csv

# File paths
import os
BASE = os.path.dirname(os.path.abspath(__file__))
E_F_PATH = os.path.join(BASE, 'lcc_E-F_hierarchy.json')
DS_DX_PATH = os.path.join(BASE, 'lcc_DS-DX_hierarchy.json')
CSV_PATH = os.path.join(BASE, 'lcc_flat.csv')

# Load JSON data
def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def main():
    # Find all JSON files in Subjects/LCC directory
    lcc_dir = os.path.join(BASE, 'LCC')
    json_files = [f for f in os.listdir(lcc_dir) if f.endswith('.json') and not f.startswith('lcc_R_medicine')]
    rows = []
    for jf in json_files:
        path = os.path.join(lcc_dir, jf)
        try:
            data = load_json(path)
            if isinstance(data, list):
                rows.extend(data)
            else:
                rows.append(data)
        except Exception as e:
            print(f"Error loading {jf}: {e}")
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'code', 'prefix', 'start', 'end', 'label'])
        for r in rows:
            w.writerow([
                r.get('id', ''),
                r.get('code', ''),
                r.get('prefix', ''),
                r.get('start', ''),
                r.get('end', ''),
                r.get('label', '')
            ])

if __name__ == '__main__':
    main()
