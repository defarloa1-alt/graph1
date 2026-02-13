
import xml.etree.ElementTree as ET
import json

INPUT_FILE = '../../../FAST/FASTChronological.marcxml'
OUTPUT_FILE = '../output/FASTChronological_parsed.jsonl'
ns = {'mx': 'http://www.loc.gov/MARC21/slim'}

def extract_all_fields(record):
    obj = {}
    # Leader
    leader = record.find('mx:leader', ns)
    obj['leader'] = leader.text if leader is not None else None
    # Controlfields
    obj['controlfields'] = []
    for cf in record.findall('mx:controlfield', ns):
        obj['controlfields'].append({
            'tag': cf.attrib.get('tag'),
            'value': cf.text
        })
    # Datafields
    obj['datafields'] = []
    for df in record.findall('mx:datafield', ns):
        df_obj = {
            'tag': df.attrib.get('tag'),
            'ind1': df.attrib.get('ind1'),
            'ind2': df.attrib.get('ind2'),
            'subfields': []
        }
        for sf in df.findall('mx:subfield', ns):
            df_obj['subfields'].append({
                'code': sf.attrib.get('code'),
                'value': sf.text
            })
        obj['datafields'].append(df_obj)
    return obj

print(f"Parsing {INPUT_FILE} ...")
tree = ET.parse(INPUT_FILE)
root = tree.getroot()

with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
    for record in root.findall('mx:record', ns):
        obj = extract_all_fields(record)
        out.write(json.dumps(obj, ensure_ascii=False) + '\n')
print(f"Done. Output: {OUTPUT_FILE}")
