MERGE (w:MethodologyText {id: 'DH_FISCHER_HF'})
SET w.title = "Historians' Fallacies: Toward a Logic of Historical Thought",
    w.author = "David Hackett Fischer";

UNWIND [
  {id: 'INQUIRY', label: 'Inquiry'},
  {id: 'EXPLANATION', label: 'Explanation'},
  {id: 'ARGUMENT', label: 'Argument'}
] AS d
MERGE (dom:MethodologicalDomain {id: d.id})
SET dom.label = d.label;

MATCH (w:MethodologyText {id: 'DH_FISCHER_HF'})
MATCH (dom:MethodologicalDomain)
MERGE (w)-[:HAS_DOMAIN]->(dom);

UNWIND [
  {id: 'QUESTION_FRAMING', domain: 'INQUIRY', label: 'Frame research questions'},
  {id: 'FACT_VERIFICATION', domain: 'INQUIRY', label: 'Check factual correctness'},
  {id: 'FACT_SIGNIFICANCE', domain: 'INQUIRY', label: 'Assess factual significance'},
  {id: 'GENERALIZATION', domain: 'EXPLANATION', label: 'Form general statements'},
  {id: 'NARRATION', domain: 'EXPLANATION', label: 'Compose historical narratives'},
  {id: 'CAUSATION', domain: 'EXPLANATION', label: 'Explain causes'},
  {id: 'MOTIVATION', domain: 'EXPLANATION', label: 'Explain motives'},
  {id: 'COMPOSITION', domain: 'EXPLANATION', label: 'Handle wholes vs parts'},
  {id: 'ANALOGY', domain: 'EXPLANATION', label: 'Use historical analogies'},
  {id: 'SEMANTICS', domain: 'ARGUMENT', label: 'Define and use terms'},
  {id: 'DISTRACTION', domain: 'ARGUMENT', label: 'Stay on relevant reasons'}
] AS row
MERGE (tt:TaskType {id: row.id})
SET tt.label = row.label
WITH tt, row
MATCH (dom:MethodologicalDomain {id: row.domain})
MERGE (dom)-[:HAS_TASKTYPE]->(tt);

MERGE (ff:FallacyFamily {id: 'F_FSIGNIF'})
SET ff.label = 'Fallacies of Factual Significance'
WITH ff
MATCH (dom:MethodologicalDomain {id: 'INQUIRY'})
MERGE (dom)-[:HAS_FAMILY]->(ff);

UNWIND [
  {id: 'HOLIST_FALLACY', label: 'Holist fallacy', family: 'F_FSIGNIF', guards: ['FACT_SIGNIFICANCE', 'COMPOSITION'],
   diagnostic_pattern: "Treating 'the whole of history' or 'the spirit of an age' as an attainable object of exhaustive representation; claiming to present 'the whole truth' or 'the past in its entirety'."},
  {id: 'ESSENCE_FALLACY', label: 'Fallacy of essences', family: 'F_FSIGNIF', guards: ['FACT_SIGNIFICANCE', 'SEMANTICS', 'COMPOSITION'],
   diagnostic_pattern: "Explaining significance by appeal to a supposed inner 'essence' of a person, age, or culture, rather than patterns of observable behavior."},
  {id: 'QUANTITATIVE_FALLACY', label: 'Quantitative fallacy', family: 'F_FSIGNIF', guards: ['FACT_SIGNIFICANCE', 'GENERALIZATION'],
   diagnostic_pattern: "Treating what can be measured or counted as inherently more significant than qualitative evidence."},
  {id: 'OVERGENERALIZATION', label: 'Overgeneralization', family: 'F_FSIGNIF', guards: ['GENERALIZATION', 'NARRATION'],
   diagnostic_pattern: "Extending a pattern from limited evidence to 'all' or 'everyone' without sufficient scope."},
  {id: 'MONOCAUSAL_EXPLANATION', label: 'Monocausal explanation', family: 'F_FSIGNIF', guards: ['CAUSATION', 'MOTIVATION'],
   diagnostic_pattern: "Explaining a complex outcome by a single cause; reducing motives to one factor."},
  {id: 'AESTHETIC_FALLACY', label: 'Aesthetic fallacy', family: 'F_FSIGNIF', guards: ['NARRATION', 'SEMANTICS'],
   diagnostic_pattern: "Prioritizing rhetorical flourish or narrative elegance over evidential strength."}
] AS f
MATCH (ff:FallacyFamily {id: f.family})
MERGE (fa:Fallacy {id: f.id})
SET fa.label = f.label,
    fa.diagnostic_pattern = f.diagnostic_pattern
MERGE (ff)-[:HAS_FALLACY]->(fa)
WITH fa, f
UNWIND f.guards AS t
MATCH (tt:TaskType {id: t})
MERGE (fa)-[:GUARDS_TASKTYPE]->(tt);

MATCH (fw:Framework {id: 'FISCHER_LOGIC'})
MATCH (w:MethodologyText {id: 'DH_FISCHER_HF'})
MERGE (fw)-[:CONTAINS]->(w);

MATCH (fw:Framework {id: 'FISCHER_LOGIC'})
MATCH (fa:Fallacy)
MERGE (fw)-[:CONTAINS]->(fa);

MATCH (fw:Framework {id: 'FISCHER_LOGIC'})
MATCH (tt:TaskType)
MERGE (fw)-[:CONTAINS]->(tt);
