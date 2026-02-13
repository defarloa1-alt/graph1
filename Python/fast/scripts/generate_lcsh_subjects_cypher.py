import json
import sys
from pathlib import Path

def safe_get(d, *keys):
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return None
    return d

def cypher_escape(s):
    if s is None:
        return ''
    return str(s).replace('"', '\"').replace("'", "\\'")

def process_concept(concept):
    node_id = concept.get('@id')
    props = []
    # All properties except relationships
    for k, v in concept.items():
        if k.startswith('@') or k in ['skos:broader', 'skos:narrower', 'skos:inScheme', 'skos:changeNote', 'skos:altLabel', 'skos:prefLabel', 'skos:notation', 'skos:editorialNote']:
            continue
        props.append(f"{k.replace(':','_')}: '{cypher_escape(v)}'")
    # Main label
    pref_label = safe_get(concept, 'skos:prefLabel', '@value')
    if pref_label:
        props.append(f"prefLabel: '{cypher_escape(pref_label)}'")
    # Notation
    notation = safe_get(concept, 'skos:notation', '@value')
    if notation:
        props.append(f"notation: '{cypher_escape(notation)}'")
    # Editorial note
    editorial_note = concept.get('skos:editorialNote')
    if editorial_note:
        props.append(f"editorialNote: '{cypher_escape(editorial_note)}'")
    # Alt labels
    alt_labels = concept.get('skos:altLabel')
    if alt_labels:
        if isinstance(alt_labels, list):
            for i, alt in enumerate(alt_labels):
                if isinstance(alt, dict):
                    val = alt.get('@value')
                else:
                    val = alt
                props.append(f"altLabel_{i}: '{cypher_escape(val)}'")
        elif isinstance(alt_labels, dict):
            props.append(f"altLabel: '{cypher_escape(alt_labels.get('@value'))}'")
        else:
            props.append(f"altLabel: '{cypher_escape(alt_labels)}'")
    # Ingestion status
    props.append("ingestion_status: 'raw_imported'")
    # Build Cypher
    cypher = [f"MERGE (s:Subject {{id: '{cypher_escape(node_id)}'}})"]
    if props:
        cypher.append(f"SET s += {{{', '.join(props)}}}")
    # Relationships
    if 'skos:broader' in concept:
        broader = concept['skos:broader']
        if isinstance(broader, dict):
            broader = [broader]
        for b in broader:
            b_id = b.get('@id') if isinstance(b, dict) else b
            cypher.append(f"MERGE (b:Subject {{id: '{cypher_escape(b_id)}'}})")
            cypher.append(f"MERGE (s)-[:BROADER]->(b)")
    if 'skos:narrower' in concept:
        narrower = concept['skos:narrower']
        if isinstance(narrower, dict):
            narrower = [narrower]
        for n in narrower:
            n_id = n.get('@id') if isinstance(n, dict) else n
            cypher.append(f"MERGE (n:Subject {{id: '{cypher_escape(n_id)}'}})")
            cypher.append(f"MERGE (s)-[:NARROWER]->(n)")
    if 'skos:inScheme' in concept:
        scheme = concept['skos:inScheme']
        s_id = scheme.get('@id') if isinstance(scheme, dict) else scheme
        cypher.append(f"MERGE (sch:Scheme {{id: '{cypher_escape(s_id)}'}})")
        cypher.append(f"MERGE (s)-[:IN_SCHEME]->(sch)")
    if 'skos:changeNote' in concept:
        notes = concept['skos:changeNote']
        if isinstance(notes, dict):
            notes = [notes]
        for note in notes:
            n_id = note.get('@id') if isinstance(note, dict) else note
            cypher.append(f"MERGE (cn:ChangeNote {{id: '{cypher_escape(n_id)}'}})")
            cypher.append(f"MERGE (s)-[:CHANGE_NOTE]->(cn)")
    return '\n'.join(cypher)

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_lcsh_subjects_cypher.py <input.jsonld> <output.cypher>")
        sys.exit(1)
    infile = Path(sys.argv[1])
    outfile = Path(sys.argv[2])
    with infile.open('r', encoding='utf-8') as f:
        data = json.load(f)
    graph = data.get('@graph', [])
    concepts = []
    for entry in graph:
        # If entry has its own @graph, process all skos:Concepts inside
        if isinstance(entry, dict) and '@graph' in entry:
            for subentry in entry['@graph']:
                if subentry.get('@type') == 'skos:Concept':
                    concepts.append(subentry)
        elif entry.get('@type') == 'skos:Concept':
            concepts.append(entry)
    with outfile.open('w', encoding='utf-8') as out:
        for obj in concepts:
            cypher = process_concept(obj)
            out.write(cypher + '\n\n')

if __name__ == '__main__':
    main()
