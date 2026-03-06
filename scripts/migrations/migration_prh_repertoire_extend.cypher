MERGE (rf3:RepertoireFamily {id: 'RF_SUBSISTENCE'})
SET rf3.label = 'Subsistence and consumption';

MERGE (rf4:RepertoireFamily {id: 'RF_INSURRECTION'})
SET rf4.label = 'Insurrection and barricade';

UNWIND [
  {id: 'RP_FOOD_RIOT', label: 'Food riot', family: 'RF_SUBSISTENCE'},
  {id: 'RP_BARRICADE', label: 'Barricade (static insurrection)', family: 'RF_INSURRECTION'},
  {id: 'RP_MOBILE_INSURRECTION', label: 'Mobile insurrection', family: 'RF_INSURRECTION'},
  {id: 'RP_POLITICAL_ASSASSINATION', label: 'Political assassination', family: 'RF_CONFLICT'},
  {id: 'RP_FISCAL_REVOLT', label: 'Fiscal revolt', family: 'RF_CONFLICT'},
  {id: 'RP_FACTORY_OCCUPATION', label: 'Factory occupation (strike)', family: 'RF_CONFLICT'}
] AS row
MATCH (rf:RepertoireFamily {id: row.family})
MERGE (rp:RepertoirePattern {id: row.id})
SET rp.label = row.label
MERGE (rf)-[:HAS_PATTERN]->(rp);

UNWIND [
  {id: 'M_PARONYMY', label: 'Paronymic repetition'},
  {id: 'M_NATIONAL_ACTIVATION', label: 'National activation'}
] AS row
MERGE (m:Mechanism {id: row.id})
SET m.label = row.label;

UNWIND [
  {pattern: 'RP_FOOD_RIOT', mechanisms: ['M_DIFFUSION', 'M_ESCALATION']},
  {pattern: 'RP_BARRICADE', mechanisms: ['M_FRAME_ALIGNMENT', 'M_ESCALATION', 'M_POLICING_RESPONSE']},
  {pattern: 'RP_MOBILE_INSURRECTION', mechanisms: ['M_DIFFUSION', 'M_ESCALATION']},
  {pattern: 'RP_POLITICAL_ASSASSINATION', mechanisms: ['M_FRAME_ALIGNMENT', 'M_ESCALATION']},
  {pattern: 'RP_FISCAL_REVOLT', mechanisms: ['M_FRAME_ALIGNMENT', 'M_BROKERAGE']},
  {pattern: 'RP_FACTORY_OCCUPATION', mechanisms: ['M_ESCALATION', 'M_POLICING_RESPONSE', 'M_DIFFUSION']}
] AS row
MATCH (rp:RepertoirePattern {id: row.pattern})
UNWIND row.mechanisms AS m_id
MATCH (m:Mechanism {id: m_id})
MERGE (rp)-[:USES_MECHANISM]->(m);

MATCH (fw:Framework {id: 'PRH_REPERTOIRE'})
MATCH (rp:RepertoirePattern)
WHERE rp.id IN ['RP_FOOD_RIOT', 'RP_BARRICADE', 'RP_MOBILE_INSURRECTION', 'RP_POLITICAL_ASSASSINATION', 'RP_FISCAL_REVOLT', 'RP_FACTORY_OCCUPATION']
MERGE (fw)-[:CONTAINS]->(rp);

MATCH (fw:Framework {id: 'PRH_REPERTOIRE'})
MATCH (m:Mechanism)
WHERE m.id IN ['M_PARONYMY', 'M_NATIONAL_ACTIVATION']
MERGE (fw)-[:CONTAINS]->(m);
