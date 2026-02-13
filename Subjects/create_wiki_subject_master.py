import csv
import re

# File paths
hist_file = r"c:\Projects\Graph1\Subjects\Historical_Periods.txt"
query_file = r"c:\Projects\Graph1\Subjects\query.csv"
master_file = r"c:\Projects\Graph1\Subjects\historical_periods_master.csv"

def load_qids_from_txt(filepath):
    qids = set()
    qid_pattern = re.compile(r"\(Q\d+\)")
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            matches = qid_pattern.findall(line)
            for match in matches:
                qids.add(match[1:-1])  # Remove parentheses
    return qids

def load_qids_from_csv(filepath):
    qids = set()
    with open(filepath, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].startswith("http://www.wikidata.org/entity/Q"):
                qid = row[0].split("/")[-1]
                qids.add(qid)
    return qids

def main():
    qids_txt = load_qids_from_txt(hist_file)
    qids_csv = load_qids_from_csv(query_file)

    all_qids = sorted(qids_txt | qids_csv)
    only_txt = sorted(qids_txt - qids_csv)
    only_csv = sorted(qids_csv - qids_txt)
    both = sorted(qids_txt & qids_csv)

    print(f"Total in TXT: {len(qids_txt)}")
    print(f"Total in CSV: {len(qids_csv)}")
    print(f"Overlap: {len(both)}")
    print(f"Only in TXT: {len(only_txt)}")
    print(f"Only in CSV: {len(only_csv)}")
    print(f"Master list: {len(all_qids)}")

    # Write master list as CSV
    with open(master_file, "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["QID"])
        for qid in all_qids:
            writer.writerow([qid])
    print(f"Master list written to {master_file}")

if __name__ == "__main__":
    main()