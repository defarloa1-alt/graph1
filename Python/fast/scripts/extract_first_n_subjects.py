import json
import sys

# Usage: python extract_first_n_subjects.py input.jsonld output.jsonld N

def main():
    if len(sys.argv) != 4:
        print("Usage: python extract_first_n_subjects.py input.jsonld output.jsonld N")
        sys.exit(1)
    infile, outfile, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
    with open(infile, encoding='utf-8') as f:
        data = json.load(f)
    outer_graph = data.get('@graph', data if isinstance(data, list) else [])
    sample = outer_graph[:n]
    out_data = {'@context': data.get('@context', None), '@graph': sample}
    print(f"Writing output to: {outfile}")
    with open(outfile, 'w', encoding='utf-8') as out:
        json.dump(out_data, out, ensure_ascii=False, indent=2)
    print(f"Extracted first {n} records to {outfile}")

if __name__ == '__main__':
    main()
