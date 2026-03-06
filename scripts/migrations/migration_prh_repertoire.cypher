MERGE (rf:RepertoireFamily {id: 'RF_ASSEMBLY_DEMONSTRATION'})
SET rf.label = 'Assembly and demonstration';

MERGE (rf2:RepertoireFamily {id: 'RF_CONFLICT'})
SET rf2.label = 'Conflict and disruption';

UNWIND [
  {id: 'RP_CONTENTIOUS_ASSEMBLY', label: 'Contentious assembly', family: 'RF_ASSEMBLY_DEMONSTRATION'},
  {id: 'RP_URBAN_RIOT', label: 'Urban riot', family: 'RF_CONFLICT'},
  {id: 'RP_MUSHROOM_STRIKE', label: 'Mushroom strike', family: 'RF_CONFLICT'},
  {id: 'RP_GENERAL_STRIKE', label: 'General strike', family: 'RF_CONFLICT'},
  {id: 'RP_PROCESSION_DEMONSTRATION', label: 'Procession or demonstration', family: 'RF_ASSEMBLY_DEMONSTRATION'},
  {id: 'RP_OCCUPATION', label: 'Occupation', family: 'RF_CONFLICT'}
] AS row
MATCH (rf:RepertoireFamily {id: row.family})
MERGE (rp:RepertoirePattern {id: row.id})
SET rp.label = row.label
MERGE (rf)-[:HAS_PATTERN]->(rp);

UNWIND [
  {id: 'M_ESCALATION', label: 'Escalation'},
  {id: 'M_DIFFUSION', label: 'Diffusion'},
  {id: 'M_BROKERAGE', label: 'Brokerage'},
  {id: 'M_POLICING_RESPONSE', label: 'Policing response'},
  {id: 'M_FRAME_ALIGNMENT', label: 'Frame alignment'}
] AS row
MERGE (m:Mechanism {id: row.id})
SET m.label = row.label;

UNWIND [
  {pattern: 'RP_CONTENTIOUS_ASSEMBLY', mechanisms: ['M_FRAME_ALIGNMENT', 'M_BROKERAGE']},
  {pattern: 'RP_URBAN_RIOT', mechanisms: ['M_ESCALATION', 'M_POLICING_RESPONSE']},
  {pattern: 'RP_MUSHROOM_STRIKE', mechanisms: ['M_DIFFUSION', 'M_ESCALATION']},
  {pattern: 'RP_GENERAL_STRIKE', mechanisms: ['M_DIFFUSION', 'M_BROKERAGE', 'M_FRAME_ALIGNMENT']},
  {pattern: 'RP_PROCESSION_DEMONSTRATION', mechanisms: ['M_FRAME_ALIGNMENT']},
  {pattern: 'RP_OCCUPATION', mechanisms: ['M_ESCALATION', 'M_POLICING_RESPONSE']}
] AS row
MATCH (rp:RepertoirePattern {id: row.pattern})
UNWIND row.mechanisms AS m_id
MATCH (m:Mechanism {id: m_id})
MERGE (rp)-[:USES_MECHANISM]->(m);

MATCH (fw:Framework {id: 'PRH_REPERTOIRE'})
MATCH (rp:RepertoirePattern)
MERGE (fw)-[:CONTAINS]->(rp);

MATCH (fw:Framework {id: 'PRH_REPERTOIRE'})
MATCH (m:Mechanism)
MERGE (fw)-[:CONTAINS]->(m);
