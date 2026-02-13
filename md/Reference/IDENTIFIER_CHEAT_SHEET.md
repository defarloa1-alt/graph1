# Identifier Atomicity Cheat Sheet

**Quick Reference: Can LLM Process This?**

Version: 1.0  
Date: 2025-12-10  
Related: [IDENTIFIER_ATOMICITY_AUDIT.md](IDENTIFIER_ATOMICITY_AUDIT.md), [Temporal_Data_Extraction_Guide.md](../temporal/docs/Temporal_Data_Extraction_Guide.md)

---

## The Golden Rule

**Two-Stage Processing:**
1. **LLM extracts** natural language labels and text
2. **Tools resolve** to atomic identifiers (QIDs, FAST IDs, etc.)
3. **Never** pass atomic identifiers to LLMs for interpretation

---

## Quick Lookup Table

| Data Type | Example | LLM Can Process? | How to Handle | Tokenization Risk |
|-----------|---------|------------------|---------------|-------------------|
| **Period name** | "Roman Republic" | ✅ YES | Extract with LLM | ✅ None (designed for it) |
| **Date text** | "49 BCE" | ✅ YES | Extract with LLM, convert with tool | ✅ None (designed for it) |
| **Place name** | "Rome" | ✅ YES | Extract with LLM | ✅ None (designed for it) |
| **Subject heading** | "Political science" | ✅ YES | Extract with LLM | ✅ None (designed for it) |
| | | | | |
| **Wikidata QID** | **"Q17193"** | **❌ NO** | **Tool lookup only** | 🔴 **HIGH** |
| **FAST ID** | **"1145002"** | **❌ NO** | **Tool lookup only** | 🔴 **HIGH** |
| **LCC code (range)** | **"DG241-269"** | **❌ NO** | **Tool lookup only** | 🔴 **HIGH** |
| **LCC code (simple)** | **"T"** | **❌ NO** | **Tool lookup only** | 🟡 **MEDIUM** |
| **MARC code** | **"sh85115058"** | **❌ NO** | **Tool lookup only** | 🔴 **HIGH** |
| **Pleiades ID** | **"423025"** | **❌ NO** | **Tool lookup only** | 🔴 **HIGH** |
| **GeoNames ID** | **"2643743"** | **❌ NO** | **Tool lookup only** | 🟡 **MEDIUM** |
| **ISO 8601 date** | **"-0753-01-01"** | **❌ NO** | **Tool-formatted only** | 🔴 **HIGH** |
| **Date without delimiters** | **"20250312"** | **❌ NEVER** | **Use YYYY-MM-DD instead** | 🔴 **CRITICAL** |
| | | | | |
| **Coordinates** | `41.9028, 12.4964` | ⚠️ **NUMERIC** | Store as numbers, not strings | 🟡 **MEDIUM** |
| **Year value** | `-753` | ⚠️ **NUMERIC** | Use as integer for calculations | ✅ None (numeric) |

---

## Common Patterns

### ✅ CORRECT Pattern: Natural Language → Tool Resolution

```python
# Step 1: LLM extracts natural language
text = "During the Roman Republic, Rome was the capital"
extracted = llm.extract({
    "period": "Roman Republic",    # ✅ Natural language
    "place": "Rome"                 # ✅ Natural language
})

# Step 2: Tools resolve to atomic identifiers
resolved = {
    "period": {
        "label": "Roman Republic",              # ✅ Human-readable
        "qid": wikidata_tool.lookup("Roman Republic"),  # "Q17193" (atomic)
        "fast_id": fast_tool.lookup("Roman Republic")    # "1411640" (atomic)
    },
    "place": {
        "label": "Rome",                        # ✅ Human-readable
        "qid": wikidata_tool.lookup("Rome"),    # "Q220" (atomic)
        "pleiades_id": pleiades_tool.lookup("Rome")  # "423025" (atomic)
    }
}

# Step 3: Store both formats
graph.create_node({
    "label": "Roman Republic",      # ✅ Natural (for display)
    "qid": "Q17193",                # ❌ Atomic (for lookups)
    "fast_id": "1411640"            # ❌ Atomic (for backbone)
})
```

### ❌ WRONG Pattern: Passing Identifiers to LLM

```python
# ❌ DON'T DO THIS:
qid = "Q17193"
llm.ask(f"What period is {qid}?")  # Gets tokenized to [Q, 17, 19, 3]

# ❌ DON'T DO THIS:
fast_id = "1145002"
llm.ask(f"What subject is FAST ID {fast_id}?")  # Gets tokenized

# ❌ DON'T DO THIS:
iso_date = "-0753-01-01"
llm.ask(f"What year is {iso_date}?")  # Gets tokenized
```

### ✅ CORRECT Pattern: Using Identifiers in Queries

```cypher
// ✅ CORRECT: Use atomic identifiers directly in Cypher
MATCH (p:Period {qid: 'Q17193'})
RETURN p.label, p.fast_id, p.start_date;

// Atomic identifiers are used as lookup keys, not passed through LLM
```

---

## Storage Format Examples

### Period Entity

```json
{
  "label": "Roman Republic",           // ✅ Natural (LLM extracts)
  "qid": "Q17193",                     // ❌ Atomic (tool resolves)
  "fast_id": "1411640",                // ❌ Atomic (tool resolves)
  "lcc_code": "DG241-269",             // ❌ Atomic (tool resolves)
  "lcsh_heading": "Rome--History--Republic",  // ✅ Natural (LLM extracts)
  "marc_code": "sh85115058",           // ❌ Atomic (tool resolves)
  "start_date_text": "509 BCE",        // ✅ Natural (LLM extracts)
  "start_date_iso": "-0509-01-01",    // ❌ Atomic (tool formats)
  "start_year": -509,                  // ✅ Numeric (calculations)
  "end_date_text": "27 BCE",           // ✅ Natural (LLM extracts)
  "end_date_iso": "-0027-12-31",      // ❌ Atomic (tool formats)
  "end_year": -27                      // ✅ Numeric (calculations)
}
```

### Place Entity

```json
{
  "label": "Rome",                     // ✅ Natural (LLM extracts)
  "qid": "Q220",                       // ❌ Atomic (tool resolves)
  "pleiades_id": "423025",             // ❌ Atomic (tool resolves)
  "pleiades_link": "https://pleiades.stoa.org/places/423025",
  "geonames_id": "3169070",            // ❌ Atomic (tool resolves)
  "latitude": 41.9028,                 // ✅ Numeric (not string!)
  "longitude": 12.4964,                // ✅ Numeric (not string!)
  "description": "Capital of the Roman Empire"  // ✅ Natural (LLM extracts)
}
```

### Relationship Type (Backbone Alignment)

```json
{
  "relationship_type": "GOVERNED",     // ✅ Natural (LLM understands)
  "category": "Political",             // ✅ Natural (LLM understands)
  "fast_id": "1069263",                // ❌ Atomic (tool only)
  "lcc_code": "JA",                    // ❌ Atomic (tool only)
  "lcsh_heading": "Political science", // ✅ Natural (LLM extracts)
  "description": "Entity exercised governmental authority over another"  // ✅ Natural
}
```

---

## Why This Matters: Tokenization Examples

### Example 1: QID Fragmentation

```python
# Input to LLM:
text = "What period is Q3281534?"

# What LLM sees (tokenized):
tokens = ["What", "period", "is", "Q", "328", "15", "34", "?"]

# Result: LLM cannot recognize "Q3281534" as identifier
# Lookup fails, entity resolution breaks
```

### Example 2: FAST ID Fragmentation

```python
# Input to LLM:
text = "FAST ID 1145002 is Technology"

# What LLM sees:
tokens = ["FAST", "ID", "114", "500", "2", "is", "Technology"]

# Result: "1145002" fragmented, backbone alignment fails
```

### Example 3: LCC Code Fragmentation

```python
# Input to LLM:
text = "LCC code DG241-269 covers Roman history"

# What LLM sees:
tokens = ["LCC", "code", "DG", "241", "-", "269", "covers", "Roman", "history"]

# Result: "DG241-269" broken into pieces, classification lookup fails
```

### Example 4: Date Without Delimiters

```python
# ❌ BAD - Gets severely fragmented:
date = "20250312"
tokens = ["202", "503", "12"]  # 45% accuracy drop!

# ✅ GOOD - Delimiters help:
date = "2025-03-12"
tokens = ["2025", "-", "03", "-", "12"]  # Better, but still use tool parsing
```

---

## Validation

Use the validation tool to check for identifiers in prompts:

```python
from relations.scripts.validate_identifier_atomicity import IdentifierValidator

validator = IdentifierValidator()

# Check a prompt before sending to LLM:
prompt = "Tell me about Q17193"
result = validator.check_prompt(prompt)

if not result['is_safe']:
    print(result['summary'])
    for issue in result['issues']:
        print(f"  {issue}")
```

---

## Quick Decision Tree

```
Is this data being processed?
│
├─ Natural language text? (period name, date text, place name)
│  └─ ✅ LLM can extract it
│
├─ System identifier? (QID, FAST ID, LCC, MARC, Pleiades, GeoNames)
│  └─ ❌ Tool resolves it, NEVER pass to LLM
│
├─ ISO 8601 date?
│  └─ ❌ Tool formats it, NEVER pass to LLM
│
├─ Numeric value? (year, coordinate)
│  └─ ✅ Store as number, use in calculations
│
└─ Unsure?
   └─ Default to ❌ Tool handling (safer to over-protect)
```

---

## Emergency Checklist

Before sending ANY text to an LLM, verify:

- [ ] No QIDs (Q followed by digits)
- [ ] No FAST IDs (7-digit numbers)
- [ ] No LCC codes (letters + numbers with ranges)
- [ ] No MARC codes (sh + 8 digits)
- [ ] No Pleiades IDs (6-digit numbers)
- [ ] No GeoNames IDs (5-8 digit numbers in geographic context)
- [ ] No ISO dates (YYYY-MM-DD format, especially with negative years)
- [ ] No dates without delimiters (YYYYMMDD)

If any detected → Remove from prompt and use tool lookup instead!

---

## Resources

- **Full Documentation:** [Temporal_Data_Extraction_Guide.md](../temporal/docs/Temporal_Data_Extraction_Guide.md)
- **Detailed Audit:** [IDENTIFIER_ATOMICITY_AUDIT.md](IDENTIFIER_ATOMICITY_AUDIT.md)
- **Validation Tool:** [validate_identifier_atomicity.py](scripts/validate_identifier_atomicity.py)
- **Cypher Examples:** [temporal/cypher/](../temporal/cypher/)

---

## Summary

| ✅ LLM Can Process | ❌ LLM Cannot Process (Atomic) |
|-------------------|--------------------------------|
| Period names | Wikidata QIDs |
| Place names | FAST IDs |
| Date text (BCE/CE) | LCC codes |
| Subject headings (LCSH) | MARC codes |
| Descriptions | Pleiades IDs |
| Natural language | GeoNames IDs |
| | ISO 8601 dates |

**Remember:** When in doubt, use tools! It's always safer to over-protect identifiers than risk tokenization.

---

*Last Updated: 2025-12-10*  
*Related: IDENTIFIER_ATOMICITY_AUDIT.md, Temporal_Data_Extraction_Guide.md*


