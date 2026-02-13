
import xml.etree.ElementTree as ET
import csv

INPUT_FILE = '../../../FAST/FASTTopical.marcxml'
OUTPUT_FILE = '../key/FASTTopical_parsed.csv'
ns = {'mx': 'http://www.loc.gov/MARC21/slim'}

# Human-readable column mapping
COLUMN_LABELS = {
    'leader': 'Leader',
    'control_001': 'FAST ID',
    'control_003': 'Institution Code',
    'control_005': 'Record Update',
    'control_008': 'Fixed Data',
    '016|7| |a': 'FAST ID (016$a)',
    '024|7| |a': 'FAST URI',
    '043| | |a': 'Geographic Code',
    '046| | |s': 'Start Date',
    '046| | |t': 'End Date',
    '148| | |a': 'Chronological Label',
    '150| | |a': 'Topical Label',
    '448| | |a': 'Related Chronological',
    '751| |0|a': 'Geographic Name',
    '751| |0|0': 'LCSH ID',
    # Add more as needed
}

def extract_flat_row(record):
    row = {}
    # Leader
    leader = record.find('mx:leader', ns)
    row['leader'] = leader.text if leader is not None else ''
    # Controlfields
    for cf in record.findall('mx:controlfield', ns):
        row[f"control_{cf.attrib.get('tag')}"] = cf.text
    # Datafields
    for df in record.findall('mx:datafield', ns):
        tag = df.attrib.get('tag')
        ind1 = df.attrib.get('ind1')
        ind2 = df.attrib.get('ind2')
        for sf in df.findall('mx:subfield', ns):
            code = sf.attrib.get('code')
            value = sf.text
            key = f"{tag}|{ind1}|{ind2}|{code}"
            # If multiple subfields with same key, join with ;
            if key in row:
                row[key] += f";{value}"
            else:
                row[key] = value

    # --- Enhanced LCSH ID extraction ---
    import re
    lcsh_candidates = []
    lcsh_pattern = r'(?:\(DLC\))?sh ?\d+'
    # 1. 751| |0|0 (original)
    if row.get('751| |0|0'):
        lcsh_candidates.append(row['751| |0|0'])
    # 2. 016|7| |a or 016|7| |z with $2 DLC or similar
    for k in row:
        if k.startswith('016|7| |a') or k.startswith('016|7| |z'):
            # Check for $2 DLC in the same field
            base = k[:-1]  # remove trailing 'a' or 'z'
            code2 = row.get(base + '2', '')
            if code2 and 'DLC' in code2:
                if re.search(lcsh_pattern, row[k], re.IGNORECASE):
                    lcsh_candidates.append(row[k])
        # 3. Any $0 subfield with (DLC)sh or sh pattern
        if k.endswith('|0') and re.search(lcsh_pattern, row[k], re.IGNORECASE):
            lcsh_candidates.append(row[k])
    # 4. Any value in any subfield matching (DLC)sh or sh pattern
    for v in row.values():
        if isinstance(v, str) and re.search(lcsh_pattern, v, re.IGNORECASE):
            lcsh_candidates.append(v)
    # Remove duplicates, keep first
    row['LCSH_ID'] = next((x for x in lcsh_candidates if x), '')

    # --- Enhanced geo extraction ---
    row['has_geo'] = bool(row.get('043| | |a') or row.get('751| |0|a'))

    # Enhanced date extraction
    # If 046 $s and $t are missing, try to extract from 148| | |a and 150| | |a
    if not row.get('046| | |s') and not row.get('046| | |t'):
        # Try 148| | |a
        chrono_label = row.get('148| | |a', '')
        # Try 150| | |a if 148 is empty
        if not chrono_label:
            chrono_label = row.get('150| | |a', '')
        # Look for date range patterns (e.g., 1002-1024)
        import re
        match = re.search(r'(\d{3,4})-(\d{3,4})', chrono_label)
        if match:
            row['046| | |s'] = match.group(1)
            row['046| | |t'] = match.group(2)
        else:
            # Try single year
            match = re.search(r'(\d{3,4})', chrono_label)
            if match:
                row['046| | |s'] = match.group(1)
                row['046| | |t'] = ''
    return row

print(f"Parsing {INPUT_FILE} ...")
tree = ET.parse(INPUT_FILE)
root = tree.getroot()

rows = []
for record in root.findall('mx:record', ns):
    rows.append(extract_flat_row(record))

# Collect all possible columns
all_keys = set()
for row in rows:
    all_keys.update(row.keys())

# Use human-readable labels if available
fieldnames = []
for k in ['leader', 'control_001', 'control_003', 'control_005', 'control_008', '016|7| |a', '024|7| |a', '043| | |a', '046| | |s', '046| | |t', '148| | |a', '150| | |a', '448| | |a', '751| |0|a', '751| |0|0', 'LCSH_ID']:
    if k in all_keys or k == 'LCSH_ID':
        fieldnames.append(COLUMN_LABELS.get(k, k))
# Add any other columns not mapped
for k in sorted(all_keys):
    if k not in COLUMN_LABELS and k not in fieldnames:
        fieldnames.append(k)

with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as out:
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        # Map keys to human-readable labels for output
        output_row = {}
        for k, v in row.items():
            label = COLUMN_LABELS.get(k, k)
            output_row[label] = v
        writer.writerow(output_row)
print(f"Done. Output: {OUTPUT_FILE}")
