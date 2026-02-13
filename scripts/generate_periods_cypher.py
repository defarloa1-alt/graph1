import csv
import os

def cypher_escape(s):
    if s is None:
        return ''
    return s.replace('"', '\"').replace("'", "\'")

SCRIPT_DIR = os.path.dirname(__file__)
TSV_PATH = os.path.join(SCRIPT_DIR, '..', 'Subjects', 'query_lcsh_enriched.tsv')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, '..', 'Subjects', 'periods_import.cypher')

with open(TSV_PATH, encoding='utf-8') as tsvfile, open(OUTPUT_PATH, 'w', encoding='utf-8') as out:
    reader = csv.DictReader(tsvfile, delimiter='\t')
    for row in reader:
        # Skip header, comment, or empty lines
        qid = row.get('?item', '').strip()
        if not qid or qid.startswith('#') or qid.startswith('##') or qid.lower().startswith('master merge') or 'QID' in qid:
            continue
        label = row.get('?itemLabel', '').split('@')[0].strip()
        start = row.get('?startDate', '').strip()
        end = row.get('?endDate', '').strip()
        location = row.get('?location', '').strip()
        location_label = row.get('?locationLabel', '').split('@')[0].strip()
        lcnaf = row.get('lcnaf', '').strip()
        part_of = row.get('?partOf', '').strip()
        follows = row.get('?follows', '').strip()
        followed_by = row.get('?followedBy', '').strip()
        facet = row.get('?instanceOfLabel', '').split('@')[0].strip()

        # Parse years from start/end
        def extract_year(date):
            if not date or date.lower() == 'null':
                return None
            for part in date.split('-'):
                if part.lstrip('-').isdigit():
                    return int(part)
            return None
        start_year = extract_year(start)
        end_year = extract_year(end)

        # Create/MERGE Period node
        # Output all Cypher for a single period as one block
        cypher_block = []
        cypher_block.append(f"MERGE (p:Period {{qid: '{cypher_escape(qid)}'}})")
        if start_year:
            cypher_block.append(f"MERGE (start:Year {{value: {start_year}}})")
            cypher_block.append(f"MERGE (p)-[:STARTS_IN]->(start)")
        if end_year:
            cypher_block.append(f"MERGE (end:Year {{value: {end_year}}})")
            cypher_block.append(f"MERGE (p)-[:ENDS_IN]->(end)")
        if facet:
            cypher_block.append(f"MERGE (f:Facet {{label: '{cypher_escape(facet)}'}})")
            cypher_block.append(f"MERGE (p)-[:HAS_FACET]->(f)")
        if location:
            cypher_block.append(f"MERGE (geo:Place {{qid: '{cypher_escape(location)}'}})")
            cypher_block.append(f"MERGE (p)-[:LOCATED_IN]->(geo)")
        elif location_label:
            cypher_block.append(f"MERGE (geo:Place {{label: '{cypher_escape(location_label)}'}})")
            cypher_block.append(f"MERGE (p)-[:LOCATED_IN]->(geo)")
        if part_of:
            cypher_block.append(f"MERGE (parent:Period {{qid: '{cypher_escape(part_of)}'}})")
            cypher_block.append(f"MERGE (p)-[:PART_OF]->(parent)")
        if follows:
            cypher_block.append(f"MERGE (prev:Period {{qid: '{cypher_escape(follows)}'}})")
            cypher_block.append(f"MERGE (p)-[:PRECEDED_BY]->(prev)")
        if followed_by:
            cypher_block.append(f"MERGE (next:Period {{qid: '{cypher_escape(followed_by)}'}})")
            cypher_block.append(f"MERGE (p)-[:FOLLOWED_BY]->(next)")
        # SET properties at the end, while p is still in scope
        set_props = [f"p.label = '{cypher_escape(label)}'"]
        if start_year:
            set_props.append(f"p.start_year = {start_year}")
        if end_year:
            set_props.append(f"p.end_year = {end_year}")
        if lcnaf:
            set_props.append(f"p.lcnaf = '{cypher_escape(lcnaf)}'")
        if set_props:
            cypher_block.append(f"SET {', '.join(set_props)}")
        out.write("\n".join(cypher_block) + "\n\n")
print(f"Cypher import script written to {OUTPUT_PATH}")
