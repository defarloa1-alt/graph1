# SCA Bootstrap Packet

**Date:** 2026-02-19  
**Purpose:** Files for stateless SCA agent to bootstrap without Neo4j access  
**Use:** Provide these to your ChatGPT SCA agent

---

## 📁 **Files in This Packet**

### **1. facets.json**
- 18 canonical facets (UPPERCASE keys)
- Forbidden facets list
- Validation rules

### **2. federations.json**
- 10 federation/authority sources
- Mode (local vs hub_api)
- File paths and coverage

### **3. entity_types.json**
- 9 entity type definitions
- Required/optional properties
- Federation usage per type
- Child type hierarchies (backbones)

### **4. current_state.json**
- Current Neo4j state snapshot
- Node counts
- SubjectConcept registry state (79 concepts)
- Agent registry state (3 active)
- Deduplication baseline

---

## 🤖 **How SCA Uses These Files**

### **Bootstrap Sequence:**

1. **Load facets.json**
   - Get 18 canonical facets
   - Validate no forbidden facets (TEMPORAL, CLASSIFICATION)
   - Enforce UPPERCASE keys

2. **Load federations.json**
   - Get 10 available federations
   - Know which are local vs API
   - Local-first policy

3. **Load entity_types.json**
   - Know what entity types can be created
   - Understand schemas and required properties
   - Know which federations each type uses
   - Understand backbone hierarchies

4. **Load current_state.json**
   - Know what already exists (deduplication)
   - Know current SubjectConcept count (79)
   - Know current Agent count (3)
   - Baseline for proposals

---

## 📝 **JSON Proposal Schema**

**When SCA outputs proposals, use this schema:**

```json
{
  "proposal_type": "PeriodMapping",
  "version": "1.0",
  "created": "2026-02-19T23:00:00Z",
  "created_by": "sca_session_003",
  
  "source_data": {
    "periodo_file": "Temporal/periodo-dataset.csv",
    "wikidata_backlinks_from": ["Q11756", "Q12554", "Q17167"],
    "total_periodo_records": 8959,
    "total_wikidata_candidates": 500
  },
  
  "proposed_entities": [
    {
      "entity_type": "Period",
      "entity_id": "period_xyz",
      "properties": {
        "label": "Middle Ages",
        "qid": "Q12554",
        "periodo_id": "p0abc123",
        "start_year": 476,
        "end_year": 1453,
        "earliest_start": 400,
        "latest_end": 1500,
        "period_type": "cultural_political",
        "status": "pending_approval"
      },
      "relationships": [
        {"type": "STARTS_IN_YEAR", "target": "Year:-476"},
        {"type": "ENDS_IN_YEAR", "target": "Year:1453"}
      ],
      "reasoning": "Wikidata Q12554 matches PeriodO definition...",
      "confidence": 0.85
    }
  ],
  
  "deduplication": {
    "checked_against": "current_state.json",
    "duplicates_found": 0,
    "new_unique_proposals": 500
  },
  
  "statistics": {
    "total_proposed": 500,
    "with_qid": 450,
    "with_periodo": 500,
    "period_types": {
      "political": 150,
      "cultural": 100,
      "geological": 50,
      "technological": 25,
      "other": 175
    }
  }
}
```

---

## 🎯 **SCA Operational Mode**

**Until MCP active:**
- ✅ Read from bootstrap packet files
- ✅ Output to JSON proposals
- ✅ User reviews JSON
- ✅ User copies Cypher to Cursor Composer
- ✅ Cursor executes on Neo4j

**Once MCP active:**
- ✅ Read from Neo4j via bootstrap query
- ✅ Write directly via @neo4j tools
- ✅ No manual copy-paste

---

**Bootstrap packet ready for your SCA agent!**

