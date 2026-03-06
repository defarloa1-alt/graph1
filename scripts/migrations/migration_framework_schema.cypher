MERGE (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MERGE (f1:Framework {id: 'FISCHER_LOGIC'})
SET f1.label = 'Fischer Logic of Historical Thought',
    f1.description = 'Methodology overlay from Historians Fallacies (D.H. Fischer). Fallacies guard TaskTypes; agents consult before claim extraction and narrative synthesis.',
    f1.source = 'historians_fallacies_toward_a_logic_of_historical_thought.pdf'
MERGE (c)-[:HAS_FRAMEWORK]->(f1);

MERGE (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MERGE (f2:Framework {id: 'MILLIGAN_DIGITAL'})
SET f2.label = 'Milligan Digital Hermeneutics',
    f2.description = 'Methodology overlay from Transformation of Historical Research in the Digital Age. Digital principles impose constraints on search, OCR, platform dependence.',
    f2.source = 'Milligan, Cambridge Elements'
MERGE (c)-[:HAS_FRAMEWORK]->(f2);

MERGE (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MERGE (f3:Framework {id: 'PRH_REPERTOIRE'})
SET f3.label = 'PRH Patterns and Repertoires',
    f3.description = 'Methodology overlay from Patterns and Repertoires (Roehner & Syme). RepertoirePattern and Mechanism nodes for event classification.',
    f3.source = 'prh.pdf'
MERGE (c)-[:HAS_FRAMEWORK]->(f3);
