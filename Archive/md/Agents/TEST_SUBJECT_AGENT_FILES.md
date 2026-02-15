# Test Subject Agent - Training Files

**Purpose:** Files to train a Roman Republic expert agent for testing Chrystallum extraction  
**Agent Type:** Test Subject (not system documentation)  
**Date:** December 12, 2025

---

## ðŸŽ¯ What This Agent Tests

This agent will help validate:
1. **QID extraction accuracy** - Are Wikidata IDs captured correctly?
2. **Relationship mapping** - Are canonical types used?
3. **CIDOC-CRM alignment** - Are museum standards applied?
4. **Temporal structuring** - Are dates in ISO 8601?
5. **Geographic structuring** - Are places properly linked?
6. **Action structure** - Is Goal/Trigger/Action/Result captured?

---

## ðŸ“‹ Required Training Files

### 1. Core Instructions
âœ… **TEST_SUBJECT_AGENT_PROMPT.md** - The agent's role and response format
âœ… **md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md** - Required properties and edges for each node type

### 2. Reference Data (CRITICAL)
âœ… **Relationships/relationship_types_registry_master.csv** - ONLY these 236 relationship types allowed
âœ… **Temporal/time_periods.csv** - Period definitions with QIDs
âœ… **CSV/action_structure_vocabularies.csv** - Goal/Trigger/Action/Result codes

### 3. Standards & Schemas
âœ… **arch/Cidoc/CIDOC-CRM_vs_Chrystallum_Comparison.md** - CIDOC-CRM alignment guide
âœ… **arch/Cidoc/CIDOC-CRM_Explanation.md** - E-class and P-property explanations
âœ… **Docs/Property_Extensions_Implementation_Guide.md** - How to structure properties

### 4. Example Extractions
âœ… **Docs/examples/Caesar_Rubicon_Example.md** - Complete worked example
âœ… **Docs/examples/India_Cotton_Trade_Extraction.md** - Extraction pattern examples

### 5. Extraction Guides
âœ… **temporal/docs/Temporal_Data_Extraction_Guide.md** - How to extract temporal data
âœ… **temporal/docs/Geographic_Data_Extraction_Guide.md** - How to extract geographic data (if exists)

### 6. Roman Republic Context (Optional - create these)
âš ï¸ **Create: Roman_Republic_Entities.csv** - Key people, places, events with QIDs
âš ï¸ **Create: Roman_Republic_Timeline.csv** - Key dates and events
âš ï¸ **Create: Roman_Republic_Relationships.csv** - Common relationship patterns

---

## ðŸ“ Files to CREATE for Better Testing

### Roman_Republic_Entities.csv

```csv
type,name,wikidata_qid,type_qid,cidoc_class,birth_death,notes
Person,Julius Caesar,Q1048,Q5,E21_Person,-0100 to -0044,Consul and dictator
Person,Pompey,Q297162,Q5,E21_Person,-0106 to -0048,Military commander
Person,Crassus,Q83646,Q5,E21_Person,-0115 to -0053,Wealthy politician
Person,Cicero,Q1541,Q5,E21_Person,-0106 to -0043,Orator and consul
Person,Brutus,Q193616,Q5,E21_Person,-0085 to -0042,Senator and assassin
Person,Mark Antony,Q51673,Q5,E21_Person,-0083 to -0030,General and triumvir
Person,Sulla,Q46654,Q5,E21_Person,-0138 to -0078,Dictator
Place,Rome,Q220,Q515,E53_Place,41.9028|12.4964,Capital city
Place,Rubicon River,Q14378,Q4022,E53_Place,44.0667|12.25,Northern Italy border
Place,Gaul,Q38060,Q1620908,E53_Place,,,Caesar's conquest region
Place,Italy,Q38,Q6256,E53_Place,42.8333|12.8333,Italian peninsula
Event,Crossing the Rubicon,Q161954,Q1190554,E5_Event,-0049-01-10,Start of civil war
Event,Battle of Pharsalus,Q48314,Q178561,E5_Event,-0048-08-09,Caesar defeats Pompey
Event,Assassination of Caesar,Q106398,Q3882219,E5_Event,-0044-03-15,Ides of March
Event,First Triumvirate,Q232550,Q2150801,E7_Activity,-0060,Political alliance
Event,Battle of Carrhae,Q153893,Q178561,E5_Event,-0053,Crassus defeated
Position,Consul,Q20056508,Q4164871,E55_Type,,Chief magistrate
Position,Dictator,Q3769,Q4164871,E55_Type,,Emergency leader
Position,Tribune,Q3363504,Q4164871,E55_Type,,People's representative
Position,Senator,Q3270791,Q4164871,E55_Type,,Senate member
```

### Roman_Republic_Timeline.csv

```csv
date_iso8601,date_natural,event,event_qid,period,period_qid,significance
-0753-04-21,April 21 753 BCE,Founding of Rome,Q1858518,Roman Kingdom,Q202686,Traditional founding date
-0509,509 BCE,Establishment of Republic,Q17167,Roman Republic,Q17167,Overthrow of monarchy
-0264 to -0241,264-241 BCE,First Punic War,Q33456,Roman Republic,Q17167,Rome vs Carthage
-0218 to -0201,218-201 BCE,Second Punic War,Q33413,Roman Republic,Q17167,Hannibal's invasion
-0149 to -0146,149-146 BCE,Third Punic War,Q33260,Roman Republic,Q17167,Destruction of Carthage
-0133,133 BCE,Gracchi reforms begin,Q577277,Late Republic,Q1747689,Political crisis starts
-0091 to -0088,91-88 BCE,Social War,Q152088,Late Republic,Q1747689,Italian allies revolt
-0082 to -0080,82-80 BCE,Sulla's dictatorship,Q46654,Late Republic,Q1747689,Proscriptions
-0073 to -0071,73-71 BCE,Spartacus revolt,Q1419,Late Republic,Q1747689,Slave rebellion
-0063,63 BCE,Catiline conspiracy,Q506290,Late Republic,Q1747689,Attempted coup
-0060,60 BCE,First Triumvirate,Q232550,Late Republic,Q1747689,Caesar-Pompey-Crassus
-0058 to -0050,58-50 BCE,Gallic Wars,Q179826,Late Republic,Q1747689,Caesar conquers Gaul
-0053,53 BCE,Battle of Carrhae,Q153893,Late Republic,Q1747689,Crassus killed
-0049-01-10,Jan 10 49 BCE,Crossing Rubicon,Q161954,Late Republic,Q1747689,Civil war begins
-0048-08-09,Aug 9 48 BCE,Battle of Pharsalus,Q48314,Late Republic,Q1747689,Caesar defeats Pompey
-0044-03-15,Mar 15 44 BCE,Assassination of Caesar,Q106398,Late Republic,Q1747689,Ides of March
-0043,43 BCE,Second Triumvirate,Q1056978,Late Republic,Q1747689,Octavian-Antony-Lepidus
-0031-09-02,Sep 2 31 BCE,Battle of Actium,Q170807,Late Republic,Q1747689,Octavian defeats Antony
-0027,27 BCE,End of Republic,Q17167,Principate begins,Q22651,Octavian becomes Augustus
```

### Roman_Republic_Relationships.csv

```csv
subject,subject_qid,relationship,object,object_qid,date,notes
Julius Caesar,Q1048,HELD_POSITION,Consul,Q20056508,-0059,First consulship
Julius Caesar,Q1048,COMMANDED,Gallic Wars,Q179826,-0058 to -0050,Military campaign
Julius Caesar,Q1048,ALLIED_WITH,Pompey,Q297162,-0060,First Triumvirate
Julius Caesar,Q1048,ALLIED_WITH,Crassus,Q83646,-0060,First Triumvirate
Julius Caesar,Q1048,OPPOSED_BY,Pompey,Q297162,-0049,Civil war
Julius Caesar,Q1048,DEFEATED,Pompey,Q297162,-0048,Battle of Pharsalus
Julius Caesar,Q1048,ASSASSINATED_BY,Brutus,Q193616,-0044-03-15,Ides of March
Julius Caesar,Q1048,CROSSED,Rubicon River,Q14378,-0049-01-10,Start of civil war
Pompey,Q297162,HELD_POSITION,Consul,Q20056508,-0070,First consulship
Pompey,Q297162,MARRIED_TO,Julia,Q237047,-0059,Caesar's daughter
Brutus,Q193616,ALLIED_WITH,Cassius,Q159623,-0044,Assassination plot
Cicero,Q1541,OPPOSED,Mark Antony,Q51673,-0044,Philippics speeches
Crassus,Q83646,DIED_IN,Battle of Carrhae,Q153893,-0053,Killed in battle
Sulla,Q46654,HELD_POSITION,Dictator,Q3769,-0082,Constitutional reforms
Rome,Q220,CAPITAL_OF,Roman Republic,Q17167,-0509 to -0027,Seat of government
Rubicon River,Q14378,BORDERS,Italy,Q38,-0049,Northern boundary
Gaul,Q38060,CONQUERED_BY,Julius Caesar,Q1048,-0058 to -0050,Roman province
```

---

## ðŸ§ª Testing Workflow

### 1. Create the Agent
1. Upload `TEST_SUBJECT_AGENT_PROMPT.md` as instructions
2. Upload required training files (8-10 files)
3. Upload custom Roman Republic CSVs (if created)
4. Name: "Roman Republic Historian (Test Subject)"

### 2. Query the Agent
Ask structured questions:
- "Tell me about Caesar crossing the Rubicon"
- "Who were Caesar's allies?"
- "Describe the Battle of Pharsalus"
- "What positions did Pompey hold?"

### 3. Extract Structured Data
The agent's responses should include:
- **QIDs** for all entities
- **Canonical relationship types** only
- **ISO 8601 dates**
- **CIDOC classes**
- **Action structures**

### 4. Validate Against Framework
Check if extraction system captures:
- âœ… All QIDs correctly
- âœ… Relationship types from canonical list
- âœ… Dates converted to ISO 8601
- âœ… CIDOC classes assigned
- âœ… Geographic coordinates
- âœ… Goal/Trigger/Action/Result patterns

### 5. Measure Accuracy
Score the extraction:
- **QID Accuracy:** % of QIDs captured correctly
- **Relationship Accuracy:** % using canonical types
- **Date Format:** % converted to ISO 8601
- **CIDOC Compliance:** % with correct E-classes
- **Completeness:** % of fields populated

---

## ðŸ“Š Success Metrics

### Target Accuracy (After Extraction)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **QID Capture** | 95%+ | Correct Wikidata IDs extracted |
| **Relationship Mapping** | 90%+ | Canonical types used |
| **Date Conversion** | 95%+ | ISO 8601 format |
| **CIDOC Alignment** | 85%+ | Correct E-classes |
| **Coordinate Extraction** | 90%+ | Lat/lon captured |
| **Action Structure** | 80%+ | All 4 components present |

---

## ðŸ”„ Iterative Improvement

### If QID accuracy is low:
- Add more examples to agent prompt
- Create Roman_Republic_Entities.csv with all QIDs
- Emphasize QID requirement in prompt

### If relationships are wrong:
- Upload canonical_relationship_types.csv
- Add more relationship examples
- Create Roman_Republic_Relationships.csv

### If CIDOC alignment is weak:
- Upload CIDOC-CRM documentation
- Add more E-class examples
- Emphasize CIDOC structure in prompt

### If dates are incorrect:
- Add more date examples in ISO 8601
- Upload Temporal_Data_Extraction_Guide.md
- Create Roman_Republic_Timeline.csv

---

## ðŸ’¡ Testing Strategy

### Phase 1: Simple Entities (Week 1)
Test extraction of:
- Single person (Caesar)
- Single place (Rome)
- Single event (Crossing Rubicon)

### Phase 2: Relationships (Week 2)
Test extraction of:
- Allied relationships (First Triumvirate)
- Opposition relationships (Caesar vs Pompey)
- Military relationships (Caesar commanded legions)

### Phase 3: Complex Events (Week 3)
Test extraction of:
- Multi-party events (Assassination)
- Long-duration events (Gallic Wars)
- Cascading events (Rubicon â†’ Civil War â†’ Dictatorship)

### Phase 4: Full Narratives (Week 4)
Test extraction of:
- Complete stories with multiple entities
- Temporal sequences
- Geographic movements
- Action structures

---

## ðŸŽ¯ Example Test Query

**Query:** "Tell me about Caesar crossing the Rubicon"

**Expected Agent Response Structure:**
```json
{
  "event": {
    "name": "Crossing of the Rubicon",
    "qid": "Q161954",
    "cidoc_class": "E5_Event"
  },
  "date": {
    "iso8601": "-0049-01-10",
    "natural": "January 10, 49 BCE"
  },
  "participants": [
    {
      "name": "Julius Caesar",
      "qid": "Q1048",
      "role": "leader"
    }
  ],
  "location": {
    "name": "Rubicon River",
    "qid": "Q14378"
  },
  "relationships": [
    {
      "type": "CROSSED",
      "from_qid": "Q1048",
      "to_qid": "Q14378"
    }
  ],
  "action_structure": {
    "goal_type": "POL",
    "trigger_type": "OPPORT",
    "action_type": "MIL_ACT",
    "result_type": "POL_TRANS"
  }
}
```

**What to Validate:**
- âœ… Event QID (Q161954) captured
- âœ… Date in ISO 8601 (-0049-01-10)
- âœ… Caesar QID (Q1048) captured
- âœ… Location QID (Q14378) captured
- âœ… Relationship type (CROSSED) is canonical
- âœ… Action structure has all 4 components

---

## ðŸ“š Minimum Files for Testing

**Start with these 6 files:**
1. TEST_SUBJECT_AGENT_PROMPT.md
2. md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md â† **NEW: Critical for proper node structure**
3. Relationships/relationship_types_registry_master.csv
4. Temporal/time_periods.csv
5. Roman_Republic_Entities.csv (create from template above)
6. arch/Cidoc/CIDOC-CRM_vs_Chrystallum_Comparison.md

**Add these 5 for complete testing:**
7. Roman_Republic_Timeline.csv (create from template above)
8. Roman_Republic_Relationships.csv (create from template above)
9. CSV/action_structure_vocabularies.csv
10. Docs/examples/Caesar_Rubicon_Example.md
11. temporal/docs/Temporal_Data_Extraction_Guide.md

---

**Purpose:** Test structured extraction capabilities  
**Domain:** Roman Republic (753 BCE - 27 BCE)  
**Success:** High accuracy on QIDs, relationships, dates, CIDOC classes  
**Next Step:** Query agent, extract responses, validate against framework


