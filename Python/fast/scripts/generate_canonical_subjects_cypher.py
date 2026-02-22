import json
from pathlib import Path
from datetime import datetime
import re

def extract_year(date_str):
    if isinstance(date_str, str):
        try:
            return int(date_str[:4])
        except:
            return 2000
    return 2000

def cypher_escape(s):
    if s is None:
        return ''
    return str(s).replace('"', '\"').replace("'", "\\'")

def build_named_variants(concept, change_notes, alt_labels):
    variants = []
    changes_sorted = sorted(change_notes, key=lambda x: x.get('cs:createdDate', {}).get('@value', ''))
    current_label = concept.get('skos:prefLabel', {}).get('@value')
    for i, change in enumerate(changes_sorted):
        date = change.get('cs:createdDate', {}).get('@value', '2000-01-01')
        reason = change.get('cs:changeReason', '')
        valid_from = date
        valid_until = changes_sorted[i+1].get('cs:createdDate', {}).get('@value') if i+1 < len(changes_sorted) else '9999-12-31'
        if reason == 'new':
            variants.append({
                'name': current_label,
                'valid_from': extract_year(valid_from),
                'valid_until': extract_year(valid_until),
                'is_preferred': True,
                'is_official': True,
                'source': 'LCSH',
                'reason': 'Heading created'
            })
        elif reason == 'revised':
            for alt in alt_labels:
                if isinstance(alt, dict):
                    alt_val = alt.get('@value')
                else:
                    alt_val = alt
                if alt_val != current_label:
                    variants.append({
                        'name': alt_val,
                        'valid_from': extract_year(valid_from),
                        'valid_until': extract_year(valid_until),
                        'is_preferred': False,
                        'is_official': True,
                        'source': 'LCSH',
                        'reason': f'Previous form (revised {date})'
                    })
    if changes_sorted:
        last_change = changes_sorted[-1]
        variants.append({
            'name': current_label,
            'valid_from': extract_year(last_change.get('cs:createdDate', {}).get('@value', '2000-01-01')),
            'valid_until': 9999,
            'is_preferred': True,
            'is_official': True,
            'source': 'LCSH',
            'reason': 'Current form'
        })
    return variants

def process_concept(concept, all_nodes):
    node_id = concept.get('@id')
    lcsh_id = node_id.split('/')[-1] if node_id else None
    base_id_match = re.match(r'(sh\d{8})(-\d+)?', lcsh_id or '')
    base_id = base_id_match.group(1) if base_id_match else lcsh_id
    change_notes = [n for n in all_nodes if n.get('@type') == 'cs:ChangeSet' and n.get('cs:subjectOfChange', {}).get('@id') == node_id]
    alt_labels = concept.get('skos:altLabel', [])
    if isinstance(alt_labels, dict):
        alt_labels = [alt_labels]
    named_variants = build_named_variants(concept, change_notes, alt_labels)
    broader = concept.get('skos:broader')
    broader_id = None
    if isinstance(broader, dict):
        broader_id = broader.get('@id', '').split('/')[-1] if broader.get('@id') else None
    elif isinstance(broader, list) and broader:
        # Take the first broader if multiple
        first_broader = broader[0]
        if isinstance(first_broader, dict):
            broader_id = first_broader.get('@id', '').split('/')[-1] if first_broader.get('@id') else None
        else:
            broader_id = str(first_broader).split('/')[-1]
    notation = concept.get('skos:notation', {}).get('@value')
    pref_label = concept.get('skos:prefLabel', {}).get('@value')
    cypher = [f"CREATE (s:Subject {{\n  lcsh_id: '{cypher_escape(base_id)}',\n  unique_id: 'SUBJECT_LCSH_{cypher_escape(base_id)}',\n  lcsh_heading: '{cypher_escape(pref_label)}',\n  label: '{cypher_escape(pref_label)}',\n  named_variants: {json.dumps(named_variants)},\n  authority_tier: 'TIER_3',\n  wikidata_qid: null,\n  wikipedia_link: false,\n  created_date: datetime('{change_notes[0].get('cs:createdDate', {}).get('@value', '2000-01-01')}') if change_notes else null,\n  last_revised: datetime('{change_notes[-1].get('cs:createdDate', {}).get('@value', '2000-01-01')}') if change_notes else null,\n  is_deprecated: false,\n  gac_code: '{cypher_escape(notation)}',\n  broader_lcsh_id: '{cypher_escape(broader_id)}'\n}})"]
    return '\n'.join(cypher)

def main():
    infile = Path('../key/subjects_sample_50.jsonld')
    outfile = Path('../output/subjects_canonical.cypher')
    with infile.open('r', encoding='utf-8') as f:
        data = json.load(f)
    graph = data.get('@graph', [])
    all_nodes = []
    for entry in graph:
        if isinstance(entry, dict) and '@graph' in entry:
            all_nodes.extend(entry['@graph'])
        else:
            all_nodes.append(entry)
    concepts = [n for n in all_nodes if n.get('@type') == 'skos:Concept']
    with outfile.open('w', encoding='utf-8') as out:
        for obj in concepts:
            cypher = process_concept(obj, all_nodes)
            out.write(cypher + '\n\n')

if __name__ == '__main__':
    main()
