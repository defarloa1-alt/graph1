# Temporal Data Extraction: Atomic vs Tokenizable Handling

## Purpose

This document specifies how AI agents should handle temporal data during extraction, distinguishing between:
- **Natural language terms** (LLM can tokenize)
- **System identifiers** (must remain atomic strings)

---

## The Tokenization Problem

From research: **Date tokenization fragmentation increases errors by up to 10%**

### Example of Fragmentation

```
Input:  "Q3281534" (Wikidata QID for Modern Period)
Tokens: [Q, 328, 15, 34]  ❌ FRAGMENTED
Result: LLM cannot recognize as identifier → lookup fails

Input:  "20250312" (ISO date without delimiters)
Tokens: [202, 503, 12]  ❌ FRAGMENTED  
Result: LLM cannot parse date → 45% accuracy drop
```

**Key Finding:** Tool-augmented reasoning achieves **95.31% accuracy** vs 34.5% for pure LLM.

---

## Part 1: Natural Language Terms (CAN TOKENIZE)

### ✅ Period Names

**Examples:**
- "The Great Depression"
- "Roman Republic"
- "Middle Ages"
- "Victorian Era"
- "The Cold War"
- "The Renaissance"

**Tokenization:**
```python
"The Great Depression" → [The, Great, Depression]  ✅ OK
"Roman Republic" → [Roman, Republic]  ✅ OK
```

**LLM Processing:**
- ✅ Can extract from text
- ✅ Understands semantic meaning
- ✅ Can identify in multiple languages
- ✅ Can handle fuzzy boundaries
- ✅ Recognizes even when dates not specified

**Extraction Pattern:**
```json
{
  "text": "During the Great Depression, unemployment rose to 25%",
  "extracted_period": "The Great Depression",
  "term_consistency": "very_high",
  "scholarly_consensus": "high",
  "confidence": 0.95,
  "extraction_method": "natural_language_understanding",
  "note": "Term widely used even though exact dates debated (1929-1939 vs 1929-1941)"
}
```

**Important:** Capture period terms even if dates are fuzzy! High term consistency = valuable data.

---

### ✅ Human-Readable Dates

**Examples:**
- "October 29, 1929"
- "March 2025"
- "49 BCE"
- "1st century BCE"
- "Late 1800s"
- "Early Renaissance"

**Tokenization:**
```python
"October 29, 1929" → [October, 29, ,, 1929]  ✅ OK
"49 BCE" → [49, BCE]  ✅ OK
"late 1800s" → [late, 1800s]  ✅ OK
```

**LLM Processing:**
- ✅ Can extract from natural language
- ✅ Understands various date formats
- ✅ Can handle imprecise dates ("late 1800s")
- ✅ Can recognize BCE/CE notation
- ✅ Can extract relative dates ("50 years later")

**Extraction Pattern:**
```json
{
  "text": "On October 29, 1929, the stock market crashed",
  "extracted_date": "October 29, 1929",
  "precision": "day",
  "confidence": 0.98,
  "extraction_method": "natural_language_date_recognition"
}
```

**Next Step:** Convert to ISO 8601 using date parsing tool (see Part 2)

---

### ✅ Era/Period References with Fuzzy Boundaries

**Examples:**
- "during the Renaissance"
- "in Classical times"
- "throughout the Medieval period"
- "the Roaring Twenties"
- "the Space Race era"

**Critical Rule:** **If literature is consistent on a temporal term, capture it even if dates are fuzzy!**

**Extraction Pattern for Fuzzy Periods:**
```json
{
  "period_term": "The Great Depression",
  "term_consistency": "very_high",
  "scholarly_usage": "widespread",
  "date_precision": "fuzzy",
  "approximate_dates": {
    "start": "1929",
    "end": "1939-1941 (debated)",
    "start_event": "Wall Street Crash, October 1929",
    "end_event_options": [
      "Economic recovery (1939)",
      "US entry into WWII (1941)"
    ]
  },
  "boundary_clarity": {
    "start": "high_consensus",
    "end": "moderate_debate"
  },
  "extraction_reasoning": "Term universally recognized; start date clear; end date contested"
}
```

---

## Part 2: System Identifiers (MUST BE ATOMIC)

### ❌ Wikidata QIDs

**Format:** Q followed by digits (e.g., Q3281534, Q17167, Q8698)

**Problem with Tokenization:**
```python
# ❌ BAD - Gets fragmented:
qid = "Q3281534"  # Modern Period
tokens = tokenize(qid)  # [Q, 328, 15, 34]
llm.ask(f"What period is {qid}?")  # LLM cannot recognize - fragments prevent understanding
```

**Correct Handling:**
```python
# ✅ GOOD - Treat as atomic string:
qid = "Q3281534"  # Atomic string, NOT tokenized by LLM
period_data = wikidata_api.get_entity(qid)  # Tool lookup

# Output:
{
  "qid": "Q3281534",
  "label": "modern period",
  "start_time": "+1800-00-00T00:00:00Z",
  "end_time": "+2100-00-00T00:00:00Z"
}
```

**Critical Rules:**
1. ❌ NEVER pass QID to LLM for interpretation
2. ✅ ALWAYS use as lookup key in tools/APIs
3. ✅ Store as string in database
4. ✅ Use tool-augmented resolution
5. ✅ Treat QIDs as opaque identifiers (like database primary keys)

**Why This Matters:**
From research: QIDs suffer same tokenization fragmentation as dates, causing lookup failures and entity resolution errors.

**Storage Format:**
```json
{
  "period": {
    "label": "Modern Period",        // ✅ Human-readable (LLM can extract)
    "qid": "Q3281534",              // ❌ Atomic string (tool resolved, no LLM processing)
    "source": "wikidata",
    "validation": "verified_2025_01_09"
  }
}
```

---

### ❌ ISO 8601 Dates (System Format)

**Format:** YYYY-MM-DD, -YYYY-MM-DD (for BCE)

**Problem with Tokenization:**
```python
# ❌ BAD - Without delimiters:
date = "20250312"
tokens = tokenize(date)  # [202, 503, 12]
llm.ask(f"Parse this date: {date}")  # 45% accuracy

# ⚠️ BETTER - With delimiters:
date = "2025-03-12"
tokens = tokenize(date)  # [2025, -, 03, -, 12]
# Less fragmentation, but still use tool for parsing
```

**Correct Handling:**
```python
# ✅ GOOD - Tool-augmented parsing:
date_text = "October 29, 1929"  # LLM extracts this (natural language)
iso_date = parse_date_tool(date_text)  # Tool converts to ISO

# Result: "1929-10-29" (atomic string for storage/queries)
```

**Rules for ISO Dates:**
1. ❌ NEVER use continuous numbers: "20250312"
2. ✅ ALWAYS use delimiters: "2025-03-12"
3. ✅ Let tools parse, not LLM
4. ✅ Store as atomic string
5. ✅ Use ISO 8601 as canonical format

**BCE Dates Handling:**
```python
# ✅ GOOD:
year_bce = -753  # Numeric value for calculations
iso_date = "-0753-01-01"  # Atomic string (ISO 8601 format)

# Storage format:
{
  "date_text": "753 BCE",          // ✅ Human-readable (LLM extracted)
  "date_iso8601": "-0753-01-01",   // ❌ Atomic string (tool formatted)
  "year_value": -753,              // Numeric for queries
  "precision": "year",
  "calendar": "proleptic_gregorian"
}
```

---

### ❌ Year Node Identifiers

**Format:** YEAR_{year_value}

**Problem:**
```python
# When year is part of identifier, keep atomic:
year_node_id = "YEAR_-753"  # Atomic string identifier
# NOT: ["YEAR", "_", "-", "753"]
```

**Correct Handling:**
```python
# ✅ Year value for calculation (numeric):
year_value = -753  # Integer, can use in math

# ✅ Year as node ID (atomic string):
year_id = "YEAR_-753"  # String identifier, don't let LLM parse

# ✅ Year in ISO format (atomic string):
iso_date = "-0753-01-01"  # Atomic string for storage/queries
```

---

## Part 3: Fuzzy Period Handling

### Principle: Term Consistency > Date Precision

**Rule:** If a temporal term appears consistently in scholarly literature, **CAPTURE IT** even if:
- Exact start/end dates are debated
- Different sources give slightly different ranges  
- Boundaries are marked by different events

**Why:** The period concept itself has scholarly value, independent of precise dates.

### Example: The Great Depression

```json
{
  "period": {
    "term": "The Great Depression",
    "term_consistency": "very_high",
    "scholarly_consensus": "high",
    
    "dates": {
      "canonical": {
        "start": "1929",
        "end": "1939",
        "source": "Most common definition"
      },
      "alternate_definitions": [
        {
          "start": "1929",
          "end": "1941",
          "source": "US historiography (includes pre-WWII period)",
          "usage": "common"
        },
        {
          "start": "1929",
          "end": "1945",
          "source": "Some economists (full recovery)",
          "usage": "less_common"
        }
      ],
      "precision": "year",
      "boundary_clarity": {
        "start": "high_consensus",
        "end": "moderate_debate"
      }
    },
    
    "boundary_events": {
      "start": "Wall Street Crash, October 24-29, 1929",
      "end_options": [
        "Economic recovery indicators (1939)",
        "US entry into WWII (December 1941)",
        "End of WWII and full employment (1945)"
      ]
    },
    
    "geographic_scope": "Global (originated in US, affected worldwide)",
    "qid": "Q8698",
    
    "notes": "Universally recognized term; dates debated by 2-12 years depending on criteria"
  }
}
```

### Fuzzy Period Confidence Scoring

| Aspect | High Confidence (0.8+) | Medium (0.6-0.8) | Low (<0.6) |
|--------|----------------------|------------------|------------|
| **Term consistency** | 10+ sources use term | 3-9 sources | 1-2 sources |
| **Date precision** | Within 5 years | 5-20 years | >20 years |
| **Boundary clarity** | Marked by specific event | Gradual transition | Unclear |
| **Scholarly consensus** | 80%+ agreement | 50-80% agreement | <50% agreement |

---

## Part 4: Extraction Workflow

### Step 1: LLM Extracts Natural Language

```python
text = """During the Roman Republic (509-27 BCE), Julius Caesar 
crossed the Rubicon in 49 BCE, marking the beginning of civil war."""

# LLM extraction (natural language - CAN tokenize):
extracted = llm.extract_temporal_references(text)

# Result:
{
  "period_mentions": [
    {
      "term": "Roman Republic",       # ✅ Natural language
      "date_hint": "509-27 BCE",      # ✅ Natural language
      "term_consistency": "high"
    }
  ],
  "event_dates": [
    {
      "event": "crossed the Rubicon",
      "date": "49 BCE",                # ✅ Natural language
      "precision": "year"
    }
  ]
}
```

### Step 2: Tools Resolve to System Identifiers

```python
# Tool-augmented resolution (atomic strings):
resolved = {
  "period": {
    "label": "Roman Republic",                    # From LLM
    "qid": resolve_to_qid("Roman Republic"),      # Tool: "Q17167" (atomic)
    "dates": {
      "start_text": "509 BCE",                    # Human-readable
      "start_iso": "-0509-01-01",                 # Atomic string
      "start_year": -509,                         # Numeric
      "end_text": "27 BCE",                       # Human-readable  
      "end_iso": "-0027-12-31",                   # Atomic string
      "end_year": -27                             # Numeric
    }
  },
  "event": {
    "date_text": "49 BCE",                        # From LLM
    "date_iso": "-0049-01-01",                    # Tool conversion (atomic)
    "year": -49                                   # Numeric
  }
}
```

### Step 3: Store Both Formats

```json
{
  "entity": {
    "label": "Julius Caesar",
    "event": "Crossed Rubicon",
    
    "temporal_data": {
      "date_text": "49 BCE",                  // ✅ Human (LLM extracted)
      "date_iso8601": "-0049-01-01",          // ❌ Atomic (tool formatted)
      "year_value": -49,                      // Numeric for queries
      
      "period_text": "Roman Republic",       // ✅ Human (LLM extracted)
      "period_qid": "Q17167",                 // ❌ Atomic (tool resolved)
      
      "extraction_confidence": 0.95,
      "date_precision": "year"
    }
  }
}
```

---

## Part 5: Prompt Instructions for Agent

### For LLM Extraction Phase

```
## TEMPORAL DATA EXTRACTION INSTRUCTIONS

### Phase 1: Natural Language Extraction (You Can Tokenize These)

Extract temporal references in their natural language form:

1. **Period names:**
   - Extract: "The Great Depression", "Roman Republic", "Middle Ages"
   - Confidence: High for well-known periods
   - Include: Any date hints in text ("1929-1941")
   - **CAPTURE EVEN IF DATES ARE FUZZY** - term consistency matters!

2. **Date expressions:**
   - Extract: "October 29, 1929", "49 BCE", "early 1800s"
   - Preserve: Original text format
   - Note: Precision level (day, month, year, decade, century)

3. **Temporal context:**
   - Extract: "during", "throughout", "by the end of"
   - Identify: Start/end indicators
   - Capture: Duration hints
   - Note: Boundary events when mentioned

4. **Fuzzy period handling:**
   - Extract: "The Space Race" even if exact dates unclear
   - Note: Scholarly usage consistency
   - Capture: Boundary events ("began with Sputnik 1957")
   - Flag: When sources disagree on dates

### Phase 2: What Tools Will Do (DO NOT Try These Yourself)

AFTER extraction, tools will convert to system formats:

1. **Period names → QIDs:**
   - You extract: "Roman Republic"
   - Tool converts: "Q17167" ← ATOMIC STRING, don't let LLM process this

2. **Date text → ISO 8601:**
   - You extract: "October 29, 1929"
   - Tool converts: "1929-10-29" ← ATOMIC STRING

3. **Year references → Numeric:**
   - You extract: "49 BCE"
   - Tool converts: -49 ← NUMERIC VALUE

### What You Should NOT Do

❌ Don't try to parse QIDs:
   Bad: "What period is Q3281534?"
   Why: QID gets tokenized to [Q, 328, 15, 34] - LLM cannot recognize
   
❌ Don't try to parse ISO dates:
   Bad: "Parse date: -0753-01-01"
   Why: Tokenization breaks date structure
   
❌ Don't generate QIDs:
   Bad: "The QID for this is probably Q12345"
   Why: QIDs are assigned by Wikidata, not generated

❌ Don't skip fuzzy periods:
   Bad: Ignoring "The Great Depression" because end date is debated
   Why: Term consistency is more valuable than date precision

### What You SHOULD Do

✅ Extract natural language:
   Good: "Period mentioned: 'The Great Depression'"
   
✅ Extract date text as written:
   Good: "Date mentioned: 'October 1929'"
   
✅ Note uncertainty:
   Good: "Approximate date: 'late 1920s' (precision: decade)"
   
✅ Capture fuzzy periods with term consistency:
   Good: "Period 'The Great Depression' widely used; dates approximately 1929-1939/1941"
   
✅ Link to boundary events:
   Good: "Period began with 'stock market crash'; ended with 'economic recovery' or 'WWII entry'"
```

---

## Part 6: Testing & Validation

### Test Case 1: Clear Period Reference

**Input:**
```
"During the Roman Republic (509-27 BCE), the Senate controlled Rome."
```

**Expected LLM Extraction:**
```json
{
  "period_name": "Roman Republic",
  "date_range_text": "509-27 BCE",
  "term_consistency": "very_high",
  "confidence": 0.95
}
```

**Expected Tool Resolution:**
```json
{
  "period_qid": "Q17167",
  "start_iso": "-0509-01-01",
  "end_iso": "-0027-12-31",
  "start_year": -509,
  "end_year": -27
}
```

### Test Case 2: Fuzzy Period Boundary

**Input:**
```
"The Great Depression lasted throughout the 1930s, devastating the economy."
```

**Expected LLM Extraction:**
```json
{
  "period_name": "The Great Depression",
  "date_range_text": "throughout the 1930s",
  "precision": "decade",
  "boundary_clarity": "fuzzy",
  "term_consistency": "very_high",
  "confidence": 0.85,
  "note": "Dates imprecise but term widely recognized"
}
```

**Expected Tool Resolution:**
```json
{
  "period_qid": "Q8698",
  "start_iso": "1929-01-01",
  "end_iso": "1939-12-31",
  "date_range": [1929, 1939],
  "alternate_end_dates": [1941, 1945],
  "uncertainty_note": "End date debated: 1939 (recovery) vs 1941 (WWII) vs 1945 (full employment)"
}
```

### Test Case 3: Period Without Explicit Dates

**Input:**
```
"The Space Race accelerated technological development."
```

**Expected LLM Extraction:**
```json
{
  "period_name": "The Space Race",
  "date_range_text": null,
  "term_consistency": "high",
  "dates_explicit": false,
  "confidence": 0.75,
  "note": "Well-known period but dates not stated in text"
}
```

**Expected Tool Resolution:**
```json
{
  "period_qid": "Q8683",
  "start_iso": "1957-10-04",
  "end_iso": "1975-07-17",
  "start_event": "Sputnik 1 launch",
  "end_event": "Apollo-Soyuz Test Project",
  "note": "Tool provides dates from knowledge base"
}
```

---

## Part 7: Error Prevention

### Common Mistakes to Avoid

1. **Asking LLM to interpret QIDs:**
   ```python
   # ❌ WRONG:
   prompt = f"What time period is {qid}?"
   
   # ✅ CORRECT:
   period_data = wikidata_lookup(qid)  # Tool handles atomic string
   ```

2. **Letting LLM parse ISO dates:**
   ```python
   # ❌ WRONG:
   prompt = f"Convert {iso_date} to year"
   
   # ✅ CORRECT:
   year = datetime.fromisoformat(iso_date).year  # Tool parses
   ```

3. **Using dates without delimiters:**
   ```python
   # ❌ WRONG:
   date = "20250312"  # Gets fragmented badly: [202, 503, 12]
   
   # ✅ CORRECT:
   date = "2025-03-12"  # Delimiters help reduce fragmentation
   date = parse_date_tool(date_text)  # Even better: tool parsing
   ```

4. **Rejecting fuzzy periods:**
   ```python
   # ❌ WRONG:
   if not has_exact_dates(period):
       skip_extraction()  # Don't do this!
   
   # ✅ CORRECT:
   if has_high_term_consistency(period):
       extract_period(period, note_uncertainty=True)
   ```

---

## Part 8: Backbone Alignment & Geographic Identifiers (MUST BE ATOMIC)

**Critical:** These identifiers are used for backbone alignment and geographic lookups. They MUST NEVER be passed to LLMs.

### ❌ FAST IDs (Faceted Application of Subject Terminology)

**Format:** 7-digit numeric (e.g., `1145002`, `831351`, `1069263`)

**Problem with Tokenization:**
```python
# ❌ BAD - Gets fragmented:
fast_id = "1145002"  # Technology classification
tokens = tokenize(fast_id)  # [114, 500, 2] or [1145, 002]
llm.ask(f"What is FAST ID {fast_id}?")  # ❌ LLM cannot recognize - fragments prevent lookup

# Example fragmentation impact:
"1145002" → [114, 500, 2]     # Lookup fails
"831351"  → [831, 351]         # Lookup fails  
"1069263" → [106, 92, 63]      # Lookup fails
```

**Correct Handling:**
```python
# ✅ GOOD - Treat as atomic string:
fast_id = "1145002"  # Atomic string, NOT tokenized
subject_data = fast_api.lookup(fast_id)  # Tool lookup

# Storage format:
{
  "relationship_type": "USE",
  "fast_id": "1145002",              # ❌ Atomic (tool lookup only)
  "lcsh_heading": "Technology",      # ✅ Human-readable (LLM can extract)
  "lcc_code": "T"                    # ❌ Atomic (tool lookup only)
}
```

**Critical Rules:**
1. ❌ NEVER pass FAST ID to LLM for interpretation
2. ✅ ALWAYS store as string (not integer)
3. ✅ ALWAYS use as lookup key in FAST API/database
4. ✅ Treat as opaque identifier (like database primary key)
5. ✅ Extract LCSH heading with LLM, resolve to FAST ID with tool

**Why This Matters:**
- FAST IDs are used in ALL 236 canonical relationship types
- Backbone alignment depends on correct FAST ID lookups
- Tokenization causes silent failures - bad data instead of errors
- Used for subject classification and knowledge organization

---

### ❌ LCC Codes (Library of Congress Classification)

**Format:** Letter(s) + optional numbers and ranges (e.g., `T`, `JA`, `DG241-269`, `QC851-859`)

**Problem with Tokenization:**
```python
# ❌ BAD - Complex codes fragment:
lcc_code = "DG241-269"  # Roman history classification
tokens = tokenize(lcc_code)  # [DG, 241, -, 269] or [D, G, 24, 1, -, 26, 9]
llm.ask(f"What subject is LCC {lcc_code}?")  # ❌ Classification lookup fails

# Example fragmentation:
"DG241-269"  → [DG, 241, -, 269]   # Range broken
"QC851-859"  → [QC, 851, -, 859]   # Range broken
"T"          → [T]                  # Simple but still atomic
"JA"         → [JA]                 # Should not pass to LLM
```

**Correct Handling:**
```python
# ✅ GOOD - Treat as atomic string:
lcc_code = "DG241-269"  # Atomic string
classification = lcc_api.lookup(lcc_code)  # Tool lookup

# Storage format:
{
  "lcc_code": "DG241-269",              # ❌ Atomic (tool lookup only)
  "lcsh_heading": "Roman history",      # ✅ Human-readable (LLM can extract)
  "fast_id": "1069263"                  # ❌ Atomic (tool lookup only)
}
```

**Critical Rules:**
1. ❌ NEVER pass LCC code to LLM for interpretation
2. ✅ ALWAYS store as string
3. ✅ ALWAYS preserve exact format including hyphens and ranges
4. ✅ Use as lookup key in LCC classification system
5. ✅ Extract subject heading with LLM, resolve to LCC code with tool

**Why This Matters:**
- LCC codes classify all subject domains
- Range notation (e.g., `DG241-269`) is particularly fragile
- Used for library classification and knowledge organization
- Critical for backbone alignment to Library of Congress system

---

### ❌ MARC Codes (Machine-Readable Cataloging)

**Format:** `sh` + 8 digits (e.g., `sh85115058`)

**Problem with Tokenization:**
```python
# ❌ BAD - Alphanumeric fragmentation:
marc_code = "sh85115058"  # Subject heading identifier
tokens = tokenize(marc_code)  # [sh, 851, 150, 58] or [sh, 8511, 5058]
llm.ask(f"What is MARC {marc_code}?")  # ❌ Bibliographic lookup fails

# Example fragmentation:
"sh85115058" → [sh, 851, 150, 58]  # Prefix separated, numbers fragmented
"sh85140989" → [sh, 851, 409, 89]  # Similar fragmentation pattern
```

**Correct Handling:**
```python
# ✅ GOOD - Treat as atomic string:
marc_code = "sh85115058"  # Atomic string
bibliographic_data = marc_api.lookup(marc_code)  # Tool lookup

# Storage format:
{
  "marc_code": "sh85115058",            # ❌ Atomic (tool lookup only)
  "subject_heading": "Political science",  # ✅ Human-readable (LLM can extract)
  "fast_id": "1069263"                  # ❌ Atomic (tool lookup only)
}
```

**Critical Rules:**
1. ❌ NEVER pass MARC code to LLM
2. ✅ ALWAYS store as atomic string
3. ✅ Use for bibliographic system lookups only
4. ✅ Treat "sh" prefix as part of atomic identifier
5. ✅ Extract subject with LLM, resolve to MARC code with tool

**Why This Matters:**
- MARC codes link to bibliographic systems
- Used for library catalog integration
- Tokenization breaks bibliographic lookups
- Critical for citation and reference management

---

### ❌ Pleiades IDs (Ancient Geography)

**Format:** 6-digit numeric (e.g., `423025` for Rome)

**Problem with Tokenization:**
```python
# ❌ BAD - Numeric fragmentation:
pleiades_id = "423025"  # Rome location
tokens = tokenize(pleiades_id)  # [423, 025] or [42, 30, 25] or [4230, 25]
llm.ask(f"What location is Pleiades {pleiades_id}?")  # ❌ Ancient geography lookup fails

# Example fragmentation:
"423025" → [423, 025]    # Leading zero lost, lookup fails
"579885" → [579, 885]    # Ancient Athens - fragmented
"197" → [197]            # Shorter IDs also atomic
```

**Correct Handling:**
```python
# ✅ GOOD - Treat as atomic string:
pleiades_id = "423025"  # Atomic string (preserves leading zeros)
ancient_place = pleiades_api.lookup(pleiades_id)  # Tool lookup
pleiades_url = f"https://pleiades.stoa.org/places/{pleiades_id}"  # URL construction

# Storage format:
{
  "label": "Roma",                      # ✅ Human-readable (LLM can extract)
  "pleiades_id": "423025",              # ❌ Atomic (tool lookup only)
  "pleiades_link": "https://pleiades.stoa.org/places/423025",
  "coordinates": [41.8919, 12.5113],    # ✅ Numeric (not string)
  "qid": "Q220"                         # ❌ Atomic (tool lookup only)
}
```

**Critical Rules:**
1. ❌ NEVER pass Pleiades ID to LLM
2. ✅ ALWAYS store as string (not integer) to preserve leading zeros
3. ✅ Use for Pleiades API lookups
4. ✅ Construct URLs: `https://pleiades.stoa.org/places/{id}`
5. ✅ Extract place name with LLM, resolve to Pleiades ID with tool

**Why This Matters:**
- Pleiades is the authoritative gazetteer for ancient places
- Used for all ancient geography (Greece, Rome, Near East, etc.)
- Leading zeros in IDs must be preserved
- Critical for ancient historical entity linkage

---

### ❌ GeoNames IDs (Modern Geography)

**Format:** Numeric ID, variable length (e.g., `2643743` for London, `6455259` for Paris)

**Problem with Tokenization:**
```python
# ❌ BAD - Numeric fragmentation:
geonames_id = "2643743"  # London
tokens = tokenize(geonames_id)  # [264, 37, 43] or [2643, 743]
llm.ask(f"What location is GeoNames {geonames_id}?")  # ❌ Modern geography lookup fails

# Example fragmentation:
"2643743" → [264, 37, 43]   # London - fragmented
"6455259" → [645, 52, 59]   # Paris - fragmented
"3169070" → [316, 90, 70]   # Rome - fragmented
```

**Correct Handling:**
```python
# ✅ GOOD - Treat as atomic string:
geonames_id = "2643743"  # Atomic string
modern_place = geonames_api.lookup(geonames_id)  # Tool lookup

# Storage format (from generate_place_entities.py):
{
  "label": "London",                    # ✅ Human-readable (LLM can extract)
  "qid": "Q84",                         # ❌ Atomic (tool lookup only)
  "geonames_id": "2643743",             # ❌ Atomic (tool lookup only)
  "latitude": 51.5074,                  # ✅ Numeric (not string)
  "longitude": -0.1278                  # ✅ Numeric (not string)
}
```

**Critical Rules:**
1. ❌ NEVER pass GeoNames ID to LLM
2. ✅ ALWAYS store as string
3. ✅ Use for GeoNames API lookups
4. ✅ Extract place name with LLM, resolve to GeoNames ID with tool
5. ✅ Strip whitespace when reading from CSV (`.strip()`)

**Why This Matters:**
- GeoNames is the primary gazetteer for modern places
- Used for all modern geography (cities, countries, features)
- Variable length IDs require string storage
- Critical for modern geographic entity linkage

---

### ✅ LCSH Headings (Natural Language - CAN Tokenize)

**Format:** Human-readable subject heading (e.g., "Technology", "Political science", "Geography")

**Status:** ✅ **SAFE** - This is natural language, NOT an identifier

**Tokenization:** ✅ **OK** - Designed to be tokenized
```python
# ✅ SAFE - Natural language:
lcsh = "Political science"
tokens = tokenize(lcsh)  # [Political, science]  ✅ OK
llm.ask(f"Classify the topic: {lcsh}")  # ✅ LLM can process natural language
```

**Current Usage:**
- Stored in: All 236 rows of `canonical_relationship_types.csv`
- Format: Human-readable English text
- Purpose: Human understanding and search

**Important:** LCSH headings are natural language labels, NOT system identifiers. They pair with atomic identifiers:
- LCSH heading: "Technology" (✅ LLM can extract)
- FAST ID: "1145002" (❌ Tool resolves)
- LCC code: "T" (❌ Tool resolves)

---

## Summary

### Natural Language (LLM CAN Tokenize)
- ✅ Period names: "The Great Depression", "Roman Republic"
- ✅ Date text: "October 29, 1929", "49 BCE"
- ✅ Temporal phrases: "during", "throughout", "by the end of"
- ✅ Fuzzy periods: "The Space Race" (even without exact dates)
- ✅ LCSH headings: "Technology", "Political science" (subject labels)

### System Identifiers (MUST Be Atomic)
- ❌ Wikidata QIDs: "Q3281534", "Q17167" (never let LLM process)
- ❌ ISO dates: "-0753-01-01", "1929-10-29" (tool parsing only)
- ❌ Year node IDs: "YEAR_-753" (atomic identifiers)
- ❌ FAST IDs: "1145002", "831351" (backbone alignment - tool only)
- ❌ LCC codes: "T", "DG241-269" (classification - tool only)
- ❌ MARC codes: "sh85115058" (bibliographic - tool only)
- ❌ Pleiades IDs: "423025" (ancient geography - tool only)
- ❌ GeoNames IDs: "2643743" (modern geography - tool only)

### Critical Principles
1. ✅ **Term consistency > Date precision** - Capture well-known periods even if fuzzy
2. ✅ **Two-stage processing** - LLM extracts labels, tools resolve identifiers
3. ✅ **Store both formats** - Human-readable + machine-readable
4. ❌ **Never let LLM process system identifiers** - Tokenization breaks them

### Workflow
1. LLM extracts natural language terms
2. Tools resolve to atomic identifiers  
3. Store both formats with metadata
4. Capture uncertainty explicitly

---

*Version: 2.0*  
*Last Updated: 2025-12-10*  
*Related: Geographic_Data_Extraction_Guide.md, relations/IDENTIFIER_ATOMICITY_AUDIT.md*  
*Research: Tool-augmented reasoning: 95.31% accuracy vs 34.5% pure LLM*  
*Critical Update: Added backbone alignment & geographic identifier atomicity rules*

