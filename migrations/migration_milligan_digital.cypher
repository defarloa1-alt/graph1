MERGE (w:MethodologyText {id: 'MILLIGAN_TRANSFORMATION'})
SET w.title = 'The Transformation of Historical Research in the Digital Age',
    w.author = 'Ian Milligan';

UNWIND [
  {id: 'SEARCH_BIAS_AWARENESS', label: 'Search bias awareness', constraint: 'Acknowledge that search interfaces and algorithms shape what evidence surfaces; avoid treating search results as representative.'},
  {id: 'SCALE_REFLEXIVITY', label: 'Scale reflexivity', constraint: 'Reflect on how scale (corpus size, sampling) affects claims; large-N and small-N have different epistemic affordances.'},
  {id: 'INFRASTRUCTURE_LITERACY', label: 'Infrastructure literacy', constraint: 'Understand how digital infrastructure (APIs, formats, platforms) shapes data availability and interpretation.'},
  {id: 'OCR_AND_METADATA_SKEPTICISM', label: 'OCR and metadata skepticism', constraint: 'Treat OCR output and metadata as fallible; verify critical passages and provenance.'},
  {id: 'PLATFORM_DEPENDENCE_TRANSPARENCY', label: 'Platform dependence transparency', constraint: 'Disclose platform and tool dependencies; changes in APIs or algorithms can invalidate prior findings.'},
  {id: 'ALGORITHMIC_MODESTY', label: 'Algorithmic modesty', constraint: 'Avoid overclaiming from algorithmic outputs; distinguish pattern detection from causal explanation.'}
] AS row
MERGE (dp:DigitalPrinciple {id: row.id})
SET dp.label = row.label,
    dp.constraint = row.constraint;

MATCH (w:MethodologyText {id: 'MILLIGAN_TRANSFORMATION'})
MATCH (dp:DigitalPrinciple)
MERGE (w)-[:HAS_PRINCIPLE]->(dp);

MATCH (fw:Framework {id: 'MILLIGAN_DIGITAL'})
MATCH (w:MethodologyText {id: 'MILLIGAN_TRANSFORMATION'})
MERGE (fw)-[:CONTAINS]->(w);

MATCH (fw:Framework {id: 'MILLIGAN_DIGITAL'})
MATCH (dp:DigitalPrinciple)
MERGE (fw)-[:CONTAINS]->(dp);

UNWIND [
  {principle: 'SEARCH_BIAS_AWARENESS', task_types: ['FACT_SIGNIFICANCE', 'FACT_VERIFICATION', 'QUESTION_FRAMING']},
  {principle: 'SCALE_REFLEXIVITY', task_types: ['GENERALIZATION', 'FACT_SIGNIFICANCE', 'NARRATION']},
  {principle: 'INFRASTRUCTURE_LITERACY', task_types: ['FACT_VERIFICATION', 'QUESTION_FRAMING']},
  {principle: 'OCR_AND_METADATA_SKEPTICISM', task_types: ['FACT_VERIFICATION', 'FACT_SIGNIFICANCE']},
  {principle: 'PLATFORM_DEPENDENCE_TRANSPARENCY', task_types: ['FACT_VERIFICATION', 'GENERALIZATION']},
  {principle: 'ALGORITHMIC_MODESTY', task_types: ['CAUSATION', 'GENERALIZATION', 'NARRATION']}
] AS row
MATCH (dp:DigitalPrinciple {id: row.principle})
UNWIND row.task_types AS tt_id
MATCH (tt:TaskType {id: tt_id})
MERGE (dp)-[:IMPOSES_CONSTRAINT_ON]->(tt);

MATCH (dp:DigitalPrinciple {id: 'SEARCH_BIAS_AWARENESS'})
MATCH (fa:Fallacy {id: 'QUANTITATIVE_FALLACY'})
MERGE (dp)-[:INTENSIFIES_RISK_OF]->(fa);
