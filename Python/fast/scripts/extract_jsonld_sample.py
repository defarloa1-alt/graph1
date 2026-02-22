import json
import sys
from pathlib import Path

def extract_graph_objects(input_path, output_path, max_records=10):
    """
    Extracts the first N objects from the @graph array in a large JSON-LD file and writes a valid JSON-LD sample.
    """
    with open(input_path, 'r', encoding='utf-8') as infile:
        # Find the start of the @graph array
        for line in infile:
            if '"@graph"' in line:
                break
        # Now, build the @graph array
        graph_objs = []
        obj_lines = []
        in_obj = False
        brace_count = 0
        for line in infile:
            if line.strip().startswith('{'):
                in_obj = True
                brace_count = 0
                obj_lines = [line]
            elif in_obj:
                obj_lines.append(line)
            if in_obj:
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    # End of object
                    try:
                        obj = json.loads(''.join(obj_lines).rstrip(',\n'))
                        graph_objs.append(obj)
                    except Exception:
                        pass
                    in_obj = False
                    obj_lines = []
                    if len(graph_objs) >= max_records:
                        break
        # Write output
        sample = {
            "@context": "http://id.loc.gov/authorities/subjects/context.json",
            "@graph": graph_objs
        }
        with open(output_path, 'w', encoding='utf-8') as out:
            json.dump(sample, out, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_jsonld_sample.py <input.jsonld> <output.jsonld> [max_records]")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    max_records = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    extract_graph_objects(input_path, output_path, max_records)
