---
id: "phase0-survey-worldcat-2026-02-26"
status: "todo"
priority: "medium"
assignee: null
dueDate: null
created: "2026-02-26T00:00:00.000Z"
modified: "2026-02-26T00:00:00.000Z"
completedAt: null
labels: ["dev", "phase-0"]
order: "c5"
---
# Phase 0a: Write survey_worldcat.py

LC SRU `http://lx2.loc.gov:210/LCDB`. Query `bath.subjectHeading = "Rome History Republic"`. Extract 650 LCSH, 050 LCC, 245 title. `new_node()` with `concept_ref`=650 $0 URI, `text_ref`=WorldCat work URI. Output: `output/nodes/worldcat_roman_republic.json`
