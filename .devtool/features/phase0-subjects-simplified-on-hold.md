---
id: "phase0-subjects-simplified-on-hold-2026-02-26"
status: "on-hold"
priority: "low"
assignee: null
dueDate: null
created: "2026-02-26T00:00:00.000Z"
modified: "2026-02-26T00:00:00.000Z"
completedAt: null
labels: ["dev", "phase-0"]
order: "f1"
---
# On Hold: subjects_simplified.csv rebuild

LCSH live mode makes this less urgent. Still useful for offline matching. Build: `cd Subjects && python -c "import gzip,shutil;..."` then `python simplify_skos_to_csv.py`
