#!/usr/bin/env python3
"""Quick sample of delta entities per anchor to assess quality."""
import json
from pathlib import Path

path = Path(__file__).resolve().parents[2] / "output/analysis/harvest_deltas.json"
with open(path) as f:
    data = json.load(f)

for anchor in data["deltas_by_anchor"]:
    seed = anchor["seed_qid"]
    label = anchor["seed_label"]
    entities = anchor["delta_entities"]
    n = len(entities)
    if n <= 15:
        sample = entities
    else:
        sample = entities[:5] + entities[n // 2 - 2 : n // 2 + 3] + entities[-5:]
    print(f"\n=== {seed} {label} (n={n}) ===")
    for e in sample:
        lbl = (e["label"] or "")[:55]
        print(f"  {e['qid']} | {lbl} | hits={e['backlink_hits']}")
