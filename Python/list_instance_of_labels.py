import csv
from collections import Counter

INPUT_PATH = 'c:/projects/graph1/Subjects/sample_token_qid_enriched.csv'

instance_counter = Counter()

with open(INPUT_PATH, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        labels = row['instanceOf_label']
        if labels:
            for label in labels.split(','):
                label = label.strip()
                if label:
                    instance_counter[label] += 1

print("Most common 'instance of' labels:")
for label, count in instance_counter.most_common(50):
    print(f"{label}: {count}")
