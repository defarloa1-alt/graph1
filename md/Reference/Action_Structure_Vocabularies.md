# Action Structure Standard Vocabularies

## Overview

Standard vocabularies for the action structure components:
- **Goal Type**: Categories of objectives
- **Trigger Type**: Categories of causes/triggers
- **Action Type**: Categories of actions
- **Result Type**: Categories of outcomes

These ensure consistency across the knowledge graph and enable standardized querying.

---

## Goal Types

| Code | Type | Description | Examples |
|------|------|-------------|----------|
| POL | Political | Political objectives - governance, power, institutions | Overthrow monarchy, Establish republic, Gain territory |
| PERS | Personal | Personal objectives - desires, ambitions, status | Satisfy desire, Assert power, Gain revenge |
| MIL | Military | Military objectives - victory, defense, conquest | Defeat enemy, Defend territory, Conquer region |
| ECON | Economic | Economic objectives - wealth, resources, trade | Acquire wealth, Control trade routes |
| CONST | Constitutional | Constitutional objectives - laws, institutions | Create institution, Reform laws, Establish precedent |
| MORAL | Moral | Moral objectives - justice, ethics | Seek justice, Right wrong, Protect innocent |
| CULT | Cultural | Cultural objectives - identity, traditions | Preserve culture, Spread religion |
| RELIG | Religious | Religious objectives - faith, conversion | Convert population, Establish religion |
| DIPL | Diplomatic | Diplomatic objectives - alliances, peace | Form alliance, Negotiate peace |
| SURV | Survival | Survival objectives - life, safety | Preserve life, Avoid death |

---

## Trigger Types

| Code | Type | Description | Examples |
|------|------|-------------|----------|
| CIRCUM | Circumstantial | External circumstances or opportunities | Opportunity presented, Right time/place |
| MORAL_TRIGGER | Moral | Moral outrage or ethical imperative | Moral outrage, Injustice observed |
| EMOT | Emotional | Emotional response or state | Anger, Fear, Grief, Love |
| POL_TRIGGER | Political | Political events or situations | Threat to power, Loss of control |
| PERS_TRIGGER | Personal | Personal experiences or events | Personal loss, Betrayal, Insult |
| EXT_THREAT | External Threat | External danger or aggression | Enemy attack, Invasion |
| INT_PRESS | Internal Pressure | Internal political or social pressure | Popular uprising, Internal conflict |
| LEGAL | Legal | Legal requirements or violations | Legal obligation, Law broken |
| AMB | Ambition | Personal ambition or desire | Desire for power, Ambition |
| OPPORT | Opportunity | Available opportunity to act | Window of opportunity, Favorable moment |

---

## Action Types

| Code | Type | Description | Examples |
|------|------|-------------|----------|
| REVOL | Political Revolution | Political overthrow or regime change | Overthrow government, Rebel, Seize power |
| MIL_ACT | Military Action | Military operations or warfare | Battle, Siege, Campaign, Defense |
| CRIME | Criminal Act | Illegal or criminal behavior | Murder, Theft, Rape, Assault |
| DIPL_ACT | Diplomatic Action | Diplomatic activities | Negotiation, Alliance formation, Treaty |
| CONST_INNOV | Constitutional Innovation | Creating new institutions | Establish office, Create institution |
| ECON_ACT | Economic Action | Economic activities | Trade, Taxation, Confiscation |
| LEGAL_ACT | Legal Action | Legal proceedings | Trial, Execution, Proscription |
| SOC_ACT | Social Action | Social movements | Protest, Cultural change, Reform |
| RELIG_ACT | Religious Action | Religious activities | Conversion, Ceremony, Doctrine |
| PERS_ACT | Personal Action | Personal behaviors | Marriage, Suicide, Flight |
| ADMIN | Administrative | Administrative actions | Appointment, Organization, Management |
| CAUSAL | Causal Chain | Events causing other events | Cascade, Chain reaction |
| TYRANNY | Tyrannical Governance | Abusive or oppressive rule | Suppression, Violent rule |
| DEFENSIVE | Defensive Action | Defensive measures | Defense, Resistance, Counter-attack |
| OFFENSIVE | Offensive Action | Aggressive measures | Attack, Invasion, Conquest |

---

## Result Types

| Code | Type | Description | Examples |
|------|------|-------------|----------|
| POL_TRANS | Political Transformation | Fundamental political change | Regime change, System transformation |
| INST_CREATE | Institutional Creation | New institutions created | New office, Institution founded |
| CONQUEST | Conquest | Military conquest | Territory gained, Enemy defeated |
| DEFEAT | Defeat | Military or political defeat | Loss, Retreat, Surrender |
| ALLIANCE | Alliance | Formation of alliances | Alliance formed, Partnership created |
| TRAGIC | Tragic | Tragic outcomes | Death, Suicide, Loss, Suffering |
| SUCCESS | Success | Successful achievement | Goal achieved, Victory |
| FAILURE | Failure | Failed attempt | Goal not achieved, Defeat |
| STABILITY | Stability | Stability maintained | Peace established, Order restored |
| INSTABILITY | Instability | Destabilization | Chaos, Disorder, Unrest |
| LEGAL_OUTCOME | Legal Outcome | Legal consequences | Conviction, Legal precedent |
| CULT_CHANGE | Cultural Change | Cultural transformations | Culture changed, Tradition altered |
| PERS_OUTCOME | Personal Outcome | Personal consequences | Status changed, Personal loss |
| ECON_OUTCOME | Economic Outcome | Economic consequences | Wealth gained, Trade established |
| SOC_CHANGE | Social Change | Social transformations | Social reform, Society changed |
| RELIG_OUTCOME | Religious Outcome | Religious consequences | Conversion, Religion established |
| MORAL_VICT | Moral Victory | Moral success | Justice served, Right upheld |
| MORAL_FAIL | Moral Failure | Moral failure | Injustice, Wrong committed |
| NEUTRAL | Neutral Outcome | Ambiguous result | Status quo, Mixed outcome |

---

## Usage Examples

### In Cypher Relationships

```cypher
(brutus)-[:PARTICIPATED_IN {
  goal: 'Overthrow tyrannical monarchy',
  goal_type: 'POL',  // Political
  trigger: 'Rape of Lucretia and public outrage',
  trigger_type: 'MORAL_TRIGGER',  // Moral outrage
  action_type: 'REVOL',  // Political Revolution
  result: 'Monarchy overthrown, Republic established',
  result_type: 'POL_TRANS'  // Political Transformation
}]->(rebellion)
```

### Querying by Type

```cypher
// Find all actions with political goals
MATCH (a)-[r]->(b)
WHERE r.goal_type = 'POL'
RETURN a, r, b

// Find actions triggered by moral outrage
MATCH (a)-[r]->(b)
WHERE r.trigger_type = 'MORAL_TRIGGER'
RETURN a, r, b

// Find actions with tragic results
MATCH (a)-[r]->(b)
WHERE r.result_type = 'TRAGIC'
RETURN a, r, b
```

---

## Extensibility

These vocabularies can be extended as needed. When adding new types:

1. Follow the existing code format (3-5 letter codes)
2. Add to the CSV file
3. Update this documentation
4. Consider backward compatibility

---

## Implementation Notes

- **Validation**: These codes should be validated during LLM extraction
- **Schema**: Store in Neo4j as reference nodes or CSV for validation
- **Queries**: Use codes for filtering and analysis
- **Display**: Map codes to descriptions for UI display

