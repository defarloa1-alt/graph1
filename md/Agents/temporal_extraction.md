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
Tokens: [Q, 328, 15, 34]  âŒ FRAGMENTED
Result: LLM cannot recognize as identifier â†’ lookup fails

Input:  "20250312" (ISO date without delimiters)
Tokens: [202, 503, 12]  âŒ FRAGMENTED  
Result: LLM cannot parse date â†’ 45% accuracy drop
```

**Key Finding:** Tool-augmented reasoning achieves **95.31% accuracy** vs 34.5% for pure LLM.

---

## Part 1: Natural Language Terms (CAN TOKENIZE)

### âœ… Period Names

**Examples:**
- "The Great Depression"
- "Roman Republic"
- "Middle Ages"
- "Victorian Era"
- "The Cold War"
- "The Renaissance"

**Tokenization:**
```python
"The Great Depression" â†’ [The, Great, Depression]  âœ… OK
"Roman Republic" â†’ [Roman, Republic]  âœ… OK
```

**LLM Processing:**
- âœ… Can extract from text
- âœ… Understands semantic meaning
- âœ… Can identify in multiple languages
- âœ… Can handle fuzzy boundaries
- âœ… Recognizes even when dates not specified

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

### âœ… Human-Readable Dates

**Examples:**
- "October 29, 1929"
- "March 2025"
- "49 BCE"
- "1st century BCE"
- "Late 1800s"
- "Early Renaissance"

**Tokenization:**
```python
"October 29, 1929" â†’ [October, 29, ,, 1929]  âœ… OK
"49 BCE" â†’ [49, BCE]  âœ… OK
"late 1800s" â†’ [late, 1800s]  âœ… OK
```

**LLM Processing:**
- âœ… Can extract from natural language
- âœ… Understands various date formats
- âœ… Can handle imprecise dates ("late 1800s")
- âœ… Can recognize BCE/CE notation
- âœ… Can extract relative dates ("50 years later")

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

### âœ… Era/Period References with Fuzzy Boundaries

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

### âŒ Wikidata QIDs

**Format:** Q followed by digits (e.g., Q3281534, Q17167, Q8698)

**Problem with Tokenization:**
```python
# âŒ BAD - Gets fragmented:
qid = "Q3281534"  # Modern Period
tokens = tokenize(qid)  # [Q, 328, 15, 34]
llm.ask(f"What period is {qid}?")  # LLM cannot recognize - fragments prevent understanding
```

**Correct Handling:**
```python
# âœ… GOOD - Treat as atomic string:
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
1. âŒ NEVER pass QID to LLM for interpretation
2. âœ… ALWAYS use as lookup key in tools/APIs
3. âœ… Store as string in database
4. âœ… Use tool-augmented resolution
5. âœ… Treat QIDs as opaque identifiers (like database primary keys)

**Why This Matters:**
From research: QIDs suffer same tokenization fragmentation as dates, causing lookup failures and entity resolution errors.

**Storage Format:**
```json
{
  "period": {
    "label": "Modern Period",        // âœ… Human-readable (LLM can extract)
    "qid": "Q3281534",              // âŒ Atomic string (tool resolved, no LLM processing)
    "source": "wikidata",
    "validation": "verified_2025_01_09"
  }
}
```

---

### âŒ ISO 8601 Dates (System Format)

**Format:** YYYY-MM-DD, -YYYY-MM-DD (for BCE)

**Problem with Tokenization:**
```python
# âŒ BAD - Without delimiters:
date = "20250312"
tokens = tokenize(date)  # [202, 503, 12]
llm.ask(f"Parse this date: {date}")  # 45% accuracy

# âš ï¸ BETTER - With delimiters:
date = "2025-03-12"
tokens = tokenize(date)  # [2025, -, 03, -, 12]
# Less fragmentation, but still use tool for parsing
```

**Correct Handling:**
```python
# âœ… GOOD - Tool-augmented parsing:
date_text = "October 29, 1929"  # LLM extracts this (natural language)
iso_date = parse_date_tool(date_text)  # Tool converts to ISO

# Result: "1929-10-29" (atomic string for storage/queries)
```

**Rules for ISO Dates:**
1. âŒ NEVER use continuous numbers: "20250312"
2. âœ… ALWAYS use delimiters: "2025-03-12"
3. âœ… Let tools parse, not LLM
4. âœ… Store as atomic string
5. âœ… Use ISO 8601 as canonical format

**BCE Dates Handling:**
```python
# âœ… GOOD:
year_bce = -753  # Numeric value for calculations
iso_date = "-0753-01-01"  # Atomic string (ISO 8601 format)

# Storage format:
{
  "date_text": "753 BCE",          // âœ… Human-readable (LLM extracted)
  "date_iso8601": "-0753-01-01",   // âŒ Atomic string (tool formatted)
  "year": -753,              // Numeric for queries
  "precision": "year",
  "calendar": "proleptic_gregorian"
}
```

---

### âŒ Year Node Identifiers

**Format:** YEAR_{year}

**Problem:**
```python
# When year is part of identifier, keep atomic:
year_node_id = "YEAR_-753"  # Atomic string identifier
# NOT: ["YEAR", "_", "-", "753"]
```

**Correct Handling:**
```python
# âœ… Year value for calculation (numeric):
year = -753  # Integer, can use in math

# âœ… Year as node ID (atomic string):
year_id = "YEAR_-753"  # String identifier, don't let LLM parse

# âœ… Year in ISO format (atomic string):
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
      "term": "Roman Republic",       # âœ… Natural language
      "date_hint": "509-27 BCE",      # âœ… Natural language
      "term_consistency": "high"
    }
  ],
  "event_dates": [
    {
      "event": "crossed the Rubicon",
      "date": "49 BCE",                # âœ… Natural language
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
      "date_text": "49 BCE",                  // âœ… Human (LLM extracted)
      "date_iso8601": "-0049-01-01",          // âŒ Atomic (tool formatted)
      "year": -49,                      // Numeric for queries
      
      "period_text": "Roman Republic",       // âœ… Human (LLM extracted)
      "period_qid": "Q17167",                 // âŒ Atomic (tool resolved)
      
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

1. **Period names â†’ QIDs:**
   - You extract: "Roman Republic"
   - Tool converts: "Q17167" â† ATOMIC STRING, don't let LLM process this

2. **Date text â†’ ISO 8601:**
   - You extract: "October 29, 1929"
   - Tool converts: "1929-10-29" â† ATOMIC STRING

3. **Year references â†’ Numeric:**
   - You extract: "49 BCE"
   - Tool converts: -49 â† NUMERIC VALUE

### What You Should NOT Do

âŒ Don't try to parse QIDs:
   Bad: "What period is Q3281534?"
   Why: QID gets tokenized to [Q, 328, 15, 34] - LLM cannot recognize
   
âŒ Don't try to parse ISO dates:
   Bad: "Parse date: -0753-01-01"
   Why: Tokenization breaks date structure
   
âŒ Don't generate QIDs:
   Bad: "The QID for this is probably Q12345"
   Why: QIDs are assigned by Wikidata, not generated

âŒ Don't skip fuzzy periods:
   Bad: Ignoring "The Great Depression" because end date is debated
   Why: Term consistency is more valuable than date precision

### What You SHOULD Do

âœ… Extract natural language:
   Good: "Period mentioned: 'The Great Depression'"
   
âœ… Extract date text as written:
   Good: "Date mentioned: 'October 1929'"
   
âœ… Note uncertainty:
   Good: "Approximate date: 'late 1920s' (precision: decade)"
   
âœ… Capture fuzzy periods with term consistency:
   Good: "Period 'The Great Depression' widely used; dates approximately 1929-1939/1941"
   
âœ… Link to boundary events:
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
   # âŒ WRONG:
   prompt = f"What time period is {qid}?"
   
   # âœ… CORRECT:
   period_data = wikidata_lookup(qid)  # Tool handles atomic string
   ```

2. **Letting LLM parse ISO dates:**
   ```python
   # âŒ WRONG:
   prompt = f"Convert {iso_date} to year"
   
   # âœ… CORRECT:
   year = datetime.fromisoformat(iso_date).year  # Tool parses
   ```

3. **Using dates without delimiters:**
   ```python
   # âŒ WRONG:
   date = "20250312"  # Gets fragmented badly: [202, 503, 12]
   
   # âœ… CORRECT:
   date = "2025-03-12"  # Delimiters help reduce fragmentation
   date = parse_date_tool(date_text)  # Even better: tool parsing
   ```

4. **Rejecting fuzzy periods:**
   ```python
   # âŒ WRONG:
   if not has_exact_dates(period):
       skip_extraction()  # Don't do this!
   
   # âœ… CORRECT:
   if has_high_term_consistency(period):
       extract_period(period, note_uncertainty=True)
   ```

---

## Part 8: Backbone Alignment & Geographic Identifiers (MUST BE ATOMIC)

**Critical:** These identifiers are used for backbone alignment and geographic lookups. They MUST NEVER be passed to LLMs.

### âŒ FAST IDs (Faceted Application of Subject Terminology)

**Format:** 7-digit numeric (e.g., `1145002`, `831351`, `1069263`)

**Problem with Tokenization:**
```python
# âŒ BAD - Gets fragmented:
fast_id = "1145002"  # Technology classification
tokens = tokenize(fast_id)  # [114, 500, 2] or [1145, 002]
llm.ask(f"What is FAST ID {fast_id}?")  # âŒ LLM cannot recognize - fragments prevent lookup

# Example fragmentation impact:
"1145002" â†’ [114, 500, 2]     # Lookup fails
"831351"  â†’ [831, 351]         # Lookup fails  
"1069263" â†’ [106, 92, 63]      # Lookup fails
```

**Correct Handling:**
```python
# âœ… GOOD - Treat as atomic string:
fast_id = "1145002"  # Atomic string, NOT tokenized
subject_data = fast_api.lookup(fast_id)  # Tool lookup

# Storage format:
{
  "relationship_type": "USE",
  "fast_id": "1145002",              # âŒ Atomic (tool lookup only)
  "lcsh_heading": "Technology",      # âœ… Human-readable (LLM can extract)
  "lcc_code": "T"                    # âŒ Atomic (tool lookup only)
}
```

**Critical Rules:**
1. âŒ NEVER pass FAST ID to LLM for interpretation
2. âœ… ALWAYS store as string (not integer)
3. âœ… ALWAYS use as lookup key in FAST API/database
4. âœ… Treat as opaque identifier (like database primary key)
5. âœ… Extract LCSH heading with LLM, resolve to FAST ID with tool

**Why This Matters:**
- FAST IDs are used in ALL 236 canonical relationship types
- Backbone alignment depends on correct FAST ID lookups
- Tokenization causes silent failures - bad data instead of errors
- Used for subject classification and knowledge organization

---

### âŒ LCC Codes (Library of Congress Classification)

**Format:** Letter(s) + optional numbers and ranges (e.g., `T`, `JA`, `DG241-269`, `QC851-859`)

**Problem with Tokenization:**
```python
# âŒ BAD - Complex codes fragment:
lcc_code = "DG241-269"  # Roman history classification
tokens = tokenize(lcc_code)  # [DG, 241, -, 269] or [D, G, 24, 1, -, 26, 9]
llm.ask(f"What subject is LCC {lcc_code}?")  # âŒ Classification lookup fails

# Example fragmentation:
"DG241-269"  â†’ [DG, 241, -, 269]   # Range broken
"QC851-859"  â†’ [QC, 851, -, 859]   # Range broken
"T"          â†’ [T]                  # Simple but still atomic
"JA"         â†’ [JA]                 # Should not pass to LLM
```

**Correct Handling:**
```python
# âœ… GOOD - Treat as atomic string:
lcc_code = "DG241-269"  # Atomic string
classification = lcc_api.lookup(lcc_code)  # Tool lookup

# Storage format:
{
  "lcc_code": "DG241-269",              # âŒ Atomic (tool lookup only)
  "lcsh_heading": "Roman history",      # âœ… Human-readable (LLM can extract)
  "fast_id": "1069263"                  # âŒ Atomic (tool lookup only)
}
```

**Critical Rules:**
1. âŒ NEVER pass LCC code to LLM for interpretation
2. âœ… ALWAYS store as string
3. âœ… ALWAYS preserve exact format including hyphens and ranges
4. âœ… Use as lookup key in LCC classification system
5. âœ… Extract subject heading with LLM, resolve to LCC code with tool

**Why This Matters:**
- LCC codes classify all subject domains
- Range notation (e.g., `DG241-269`) is particularly fragile
- Used for library classification and knowledge organization
- Critical for backbone alignment to Library of Congress system

---

### âŒ MARC Codes (Machine-Readable Cataloging)

**Format:** `sh` + 8 digits (e.g., `sh85115058`)

**Problem with Tokenization:**
```python
# âŒ BAD - Alphanumeric fragmentation:
marc_code = "sh85115058"  # Subject heading identifier
tokens = tokenize(marc_code)  # [sh, 851, 150, 58] or [sh, 8511, 5058]
llm.ask(f"What is MARC {marc_code}?")  # âŒ Bibliographic lookup fails

# Example fragmentation:
"sh85115058" â†’ [sh, 851, 150, 58]  # Prefix separated, numbers fragmented
"sh85140989" â†’ [sh, 851, 409, 89]  # Similar fragmentation pattern
```

**Correct Handling:**
```python
# âœ… GOOD - Treat as atomic string:
marc_code = "sh85115058"  # Atomic string
bibliographic_data = marc_api.lookup(marc_code)  # Tool lookup

# Storage format:
{
  "marc_code": "sh85115058",            # âŒ Atomic (tool lookup only)
  "subject_heading": "Political science",  # âœ… Human-readable (LLM can extract)
  "fast_id": "1069263"                  # âŒ Atomic (tool lookup only)
}
```

**Critical Rules:**
1. âŒ NEVER pass MARC code to LLM
2. âœ… ALWAYS store as atomic string
3. âœ… Use for bibliographic system lookups only
4. âœ… Treat "sh" prefix as part of atomic identifier
5. âœ… Extract subject with LLM, resolve to MARC code with tool

**Why This Matters:**
- MARC codes link to bibliographic systems
- Used for library catalog integration
- Tokenization breaks bibliographic lookups
- Critical for citation and reference management

---

### âŒ Pleiades IDs (Ancient Geography)

**Format:** 6-digit numeric (e.g., `423025` for Rome)

**Problem with Tokenization:**
```python
# âŒ BAD - Numeric fragmentation:
pleiades_id = "423025"  # Rome location
tokens = tokenize(pleiades_id)  # [423, 025] or [42, 30, 25] or [4230, 25]
llm.ask(f"What location is Pleiades {pleiades_id}?")  # âŒ Ancient geography lookup fails

# Example fragmentation:
"423025" â†’ [423, 025]    # Leading zero lost, lookup fails
"579885" â†’ [579, 885]    # Ancient Athens - fragmented
"197" â†’ [197]            # Shorter IDs also atomic
```

**Correct Handling:**
```python
# âœ… GOOD - Treat as atomic string:
pleiades_id = "423025"  # Atomic string (preserves leading zeros)
ancient_place = pleiades_api.lookup(pleiades_id)  # Tool lookup
pleiades_url = f"https://pleiades.stoa.org/places/{pleiades_id}"  # URL construction

# Storage format:
{
  "label": "Roma",                      # âœ… Human-readable (LLM can extract)
  "pleiades_id": "423025",              # âŒ Atomic (tool lookup only)
  "pleiades_link": "https://pleiades.stoa.org/places/423025",
  "coordinates": [41.8919, 12.5113],    # âœ… Numeric (not string)
  "qid": "Q220"                         # âŒ Atomic (tool lookup only)
}
```

**Critical Rules:**
1. âŒ NEVER pass Pleiades ID to LLM
2. âœ… ALWAYS store as string (not integer) to preserve leading zeros
3. âœ… Use for Pleiades API lookups
4. âœ… Construct URLs: `https://pleiades.stoa.org/places/{id}`
5. âœ… Extract place name with LLM, resolve to Pleiades ID with tool

**Why This Matters:**
- Pleiades is the authoritative gazetteer for ancient places
- Used for all ancient geography (Greece, Rome, Near East, etc.)
- Leading zeros in IDs must be preserved
- Critical for ancient historical entity linkage

---

### âŒ GeoNames IDs (Modern Geography)

**Format:** Numeric ID, variable length (e.g., `2643743` for London, `6455259` for Paris)

**Problem with Tokenization:**
```python
# âŒ BAD - Numeric fragmentation:
geonames_id = "2643743"  # London
tokens = tokenize(geonames_id)  # [264, 37, 43] or [2643, 743]
llm.ask(f"What location is GeoNames {geonames_id}?")  # âŒ Modern geography lookup fails

# Example fragmentation:
"2643743" â†’ [264, 37, 43]   # London - fragmented
"6455259" â†’ [645, 52, 59]   # Paris - fragmented
"3169070" â†’ [316, 90, 70]   # Rome - fragmented
```

**Correct Handling:**
```python
# âœ… GOOD - Treat as atomic string:
geonames_id = "2643743"  # Atomic string
modern_place = geonames_api.lookup(geonames_id)  # Tool lookup

# Storage format (from generate_place_entities.py):
{
  "label": "London",                    # âœ… Human-readable (LLM can extract)
  "qid": "Q84",                         # âŒ Atomic (tool lookup only)
  "geonames_id": "2643743",             # âŒ Atomic (tool lookup only)
  "latitude": 51.5074,                  # âœ… Numeric (not string)
  "longitude": -0.1278                  # âœ… Numeric (not string)
}
```

**Critical Rules:**
1. âŒ NEVER pass GeoNames ID to LLM
2. âœ… ALWAYS store as string
3. âœ… Use for GeoNames API lookups
4. âœ… Extract place name with LLM, resolve to GeoNames ID with tool
5. âœ… Strip whitespace when reading from CSV (`.strip()`)

**Why This Matters:**
- GeoNames is the primary gazetteer for modern places
- Used for all modern geography (cities, countries, features)
- Variable length IDs require string storage
- Critical for modern geographic entity linkage

---

### âœ… LCSH Headings (Natural Language - CAN Tokenize)

**Format:** Human-readable subject heading (e.g., "Technology", "Political science", "Geography")

**Status:** âœ… **SAFE** - This is natural language, NOT an identifier

**Tokenization:** âœ… **OK** - Designed to be tokenized
```python
# âœ… SAFE - Natural language:
lcsh = "Political science"
tokens = tokenize(lcsh)  # [Political, science]  âœ… OK
llm.ask(f"Classify the topic: {lcsh}")  # âœ… LLM can process natural language
```

**Current Usage:**
- Stored in: All 236 rows of `canonical_relationship_types.csv`
- Format: Human-readable English text
- Purpose: Human understanding and search

**Important:** LCSH headings are natural language labels, NOT system identifiers. They pair with atomic identifiers:
- LCSH heading: "Technology" (âœ… LLM can extract)
- FAST ID: "1145002" (âŒ Tool resolves)
- LCC code: "T" (âŒ Tool resolves)

---

## Summary

### Natural Language (LLM CAN Tokenize)
- âœ… Period names: "The Great Depression", "Roman Republic"
- âœ… Date text: "October 29, 1929", "49 BCE"
- âœ… Temporal phrases: "during", "throughout", "by the end of"
- âœ… Fuzzy periods: "The Space Race" (even without exact dates)
- âœ… LCSH headings: "Technology", "Political science" (subject labels)

### System Identifiers (MUST Be Atomic)
- âŒ Wikidata QIDs: "Q3281534", "Q17167" (never let LLM process)
- âŒ ISO dates: "-0753-01-01", "1929-10-29" (tool parsing only)
- âŒ Year node IDs: "YEAR_-753" (atomic identifiers)
- âŒ FAST IDs: "1145002", "831351" (backbone alignment - tool only)
- âŒ LCC codes: "T", "DG241-269" (classification - tool only)
- âŒ MARC codes: "sh85115058" (bibliographic - tool only)
- âŒ Pleiades IDs: "423025" (ancient geography - tool only)
- âŒ GeoNames IDs: "2643743" (modern geography - tool only)

### Critical Principles
1. âœ… **Term consistency > Date precision** - Capture well-known periods even if fuzzy
2. âœ… **Two-stage processing** - LLM extracts labels, tools resolve identifiers
3. âœ… **Store both formats** - Human-readable + machine-readable
4. âŒ **Never let LLM process system identifiers** - Tokenization breaks them

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


