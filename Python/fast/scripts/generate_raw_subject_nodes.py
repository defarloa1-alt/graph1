import json
import sys

# Usage: python generate_raw_subject_nodes.py input.jsonld output.cypher

def escape_cypher_string(value):
    if isinstance(value, str):
        return value.replace('"', '\\"')
    return value

def format_property_value(value):
    if isinstance(value, list):
        # Join list values as a string for Cypher property, use double quotes
        return '[' + ', '.join(f'"{escape_cypher_string(str(v))}"' for v in value) + ']'
    elif isinstance(value, dict):
        # Store dict as JSON string, use double quotes
        return f'"{escape_cypher_string(json.dumps(value, ensure_ascii=False))}"'
    else:
        return f'"{escape_cypher_string(str(value))}"'

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_raw_subject_nodes.py input.jsonld output.cypher")
        sys.exit(1)
    infile, outfile = sys.argv[1], sys.argv[2]
    with open(infile, encoding='utf-8') as f:
        data = json.load(f)
    # Find the @graph array (outer)
    outer_graph = data.get('@graph', data if isinstance(data, list) else [])
    if not outer_graph:
        print('No @graph found in input.')
        sys.exit(1)
    # Collect all skos:Concept nodes from nested @graph arrays
    concept_nodes = []
    for item in outer_graph:
        if isinstance(item, dict) and '@graph' in item:
            for subnode in item['@graph']:
                if not isinstance(subnode, dict):
                    continue
                node_type = subnode.get('@type')
                if isinstance(node_type, list):
                    if 'skos:Concept' in node_type:
                        concept_nodes.append(subnode)
                elif node_type == 'skos:Concept':
                    concept_nodes.append(subnode)
    if not concept_nodes:
        print('No skos:Concept nodes found in input.')
        sys.exit(1)
    with open(outfile, 'w', encoding='utf-8') as out:
        count = 0
        total = len(concept_nodes)
        for node in concept_nodes:
            node_id = node.get('@id')
            if not node_id:
                continue
            # Flatten SKOS properties
            props = {}
            for k, v in node.items():
                if k in ('@id', '@type'):
                    continue
                # For language maps or value dicts, extract value
                if isinstance(v, dict) and '@value' in v:
                    props[k.replace('skos:', '')] = v['@value']
                elif isinstance(v, list):
                    # If list of dicts with @value, extract values
                    values = []
                    for item2 in v:
                        if isinstance(item2, dict) and '@value' in item2:
                            values.append(item2['@value'])
                        elif isinstance(item2, dict) and '@id' in item2:
                            values.append(item2['@id'])
                        else:
                            values.append(str(item2))
                    props[k.replace('skos:', '')] = values
                elif isinstance(v, dict) and '@id' in v:
                    props[k.replace('skos:', '')] = v['@id']
                else:
                    props[k.replace('skos:', '')] = v
            props['ingestion_status'] = 'raw_imported'
            cypher_props = ', '.join(f"{k}: {format_property_value(v)}" for k, v in props.items())
            out.write(f'MERGE (s:Subject {{id: "{escape_cypher_string(node_id)}"}})\n')
            out.write(f'SET s += {{{cypher_props}}}\n\n')
            count += 1
            if count % 1000 == 0:
                print(f"Processed {count} of {total} nodes...")
        print(f"Done. Processed {count} nodes in total.")

if __name__ == '__main__':
    main()
