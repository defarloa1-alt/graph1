# Identifier Atomicity Audit - ALL System IDs

**Date:** December 10, 2025  
**Purpose:** Verify ALL identifier types are treated as atomic strings  
**Concern:** Similar to QID tokenization issue, FAST/LCC/MARC/Pleiades IDs may be tokenized

---

## Executive Summary

**Critical Finding:** ⚠️ **FAST, LCC, MARC, and Pleiades IDs are NOT explicitly documented as atomic!**

**Risk:** If these identifiers are passed to LLMs, they may be tokenized and produce bad data lookups.

---

## Identifier Types in Project

### 1. **Wikidata QID** ✅ DOCUMENTED AS ATOMIC

**Format:** `Q` + digits (e.g., `Q17167`, `Q3281534`)

**Status:** ✅ **FULLY DOCUMENTED**
- Documented in: `temporal/docs/Temporal_Data_Extraction_Guide.md`
- Rule: "❌ NEVER pass QID to LLM for interpretation"
- Storage: Atomic string, tool-resolved only
- Tokenization risk: HIGH (fragments to `[Q, 328, 15, 34]`)

**Evidence:**
- Line 179: "❌ NEVER pass QID to LLM for interpretation"
- Line 166: "✅ GOOD - Treat as atomic string"
- Line 193: "❌ Atomic string (tool resolved, no LLM processing)"

---

### 2. **FAST ID** ⚠️ NOT DOCUMENTED AS ATOMIC

**Format:** 7-digit numeric ID (e.g., `1145002`, `831351`, `1069263`)

**Status:** ⚠️ **NOT EXPLICITLY DOCUMENTED**
- Found in: `canonical_relationship_types.csv` (all 236 relationships have FAST IDs)
- Found in: `Roman Republic/test_roman_kingdom_to_sulla.cypher` (backbone_fast properties)
- **NO extraction guide** for FAST IDs
- **NO warning** about LLM processing
- **NO atomicity rule**

**Tokenization Risk:** 🔴 **HIGH**

**Example of fragmentation:**
```python
# ❌ DANGER - FAST ID could fragment:
fast_id = "1145002"  # Technology
tokens = tokenize(fast_id)  # [114, 500, 2] or [1145, 002] or [11, 45, 00, 2]
llm.ask(f"What is FAST ID {fast_id}?")  # ❌ LLM cannot recognize - fragments prevent lookup

# ✅ CORRECT - Treat as atomic:
fast_id = "1145002"  # Atomic string
result = fast_api.lookup(fast_id)  # Tool lookup
```

**Current Usage:**
- Stored in: All 236 rows of `canonical_relationship_types.csv`
- Format: Plain 7-digit numbers (no prefix)
- Used in: Backbone alignment per Baseline Core 3.1

**Issues:**
1. No documentation warning against LLM processing
2. No storage format specification
3. No validation that it's treated atomically
4. Numeric format makes it easy to accidentally pass to LLM

---

### 3. **LCC Code** ⚠️ NOT DOCUMENTED AS ATOMIC

**Format:** Letter + optional numbers (e.g., `T`, `JA`, `DG241-269`, `QC851-859`)

**Status:** ⚠️ **NOT EXPLICITLY DOCUMENTED**
- Found in: `canonical_relationship_types.csv` (lcc_code column)
- Found in: `Roman Republic/test_roman_kingdom_to_sulla.cypher` (backbone_lcc properties)
- **NO extraction guide** for LCC codes
- **NO warning** about LLM processing
- **NO atomicity rule**

**Tokenization Risk:** 🟡 **MEDIUM-HIGH**

**Example of fragmentation:**
```python
# ❌ DANGER - LCC code could fragment:
lcc_code = "DG241-269"  # Roman history
tokens = tokenize(lcc_code)  # [DG, 241, -, 269] or [D, G, 24, 1, -, 26, 9]
llm.ask(f"What subject is LCC {lcc_code}?")  # ❌ May not recognize classification

# Simpler codes:
lcc_code = "T"  # Technology
tokens = tokenize(lcc_code)  # [T]  # Single token, but still shouldn't pass to LLM

# ✅ CORRECT - Treat as atomic:
lcc_code = "DG241-269"  # Atomic string
result = lcc_api.lookup(lcc_code)  # Tool lookup
```

**Current Usage:**
- Stored in: All 236 rows of `canonical_relationship_types.csv`
- Format: Varied (single letter to complex ranges)
- Used in: Backbone alignment per Baseline Core 3.1

**Issues:**
1. Complex format (letters + numbers + hyphens) prone to fragmentation
2. No documentation on atomic handling
3. Could be confused as natural language by LLM
4. Range notation (e.g., `DG241-269`) particularly fragile

---

### 4. **LCSH Heading** ✅ SAFE (Natural Language)

**Format:** Human-readable subject heading (e.g., "Technology", "Political science", "Geography")

**Status:** ✅ **SAFE**
- Natural language text - **CAN be tokenized** by LLM
- Similar to period names and labels
- Stored for human readability

**Tokenization Risk:** ✅ **NONE** (designed to be tokenized)

**Example:**
```python
# ✅ SAFE - Natural language:
lcsh = "Political science"
tokens = tokenize(lcsh)  # [Political, science]  ✅ OK
llm.ask(f"Classify: {lcsh}")  # ✅ LLM can process natural language
```

**Current Usage:**
- Stored in: All 236 rows of `canonical_relationship_types.csv`
- Format: Human-readable English text
- Purpose: Human understanding and search

**Note:** LCSH headings are natural language labels, NOT system identifiers.

---

### 5. **MARC Code** ⚠️ NOT DOCUMENTED AS ATOMIC

**Format:** `sh` + 8 digits (e.g., `sh85115058`)

**Status:** ⚠️ **NOT EXPLICITLY DOCUMENTED**
- Found in: `Roman Republic/test_roman_kingdom_to_sulla.cypher` (backbone_marc properties)
- Found in: Some backbone alignment examples
- **NO extraction guide** for MARC codes
- **NO warning** about LLM processing
- **NO atomicity rule**

**Tokenization Risk:** 🔴 **HIGH**

**Example of fragmentation:**
```python
# ❌ DANGER - MARC code could fragment:
marc_code = "sh85115058"  # Subject heading identifier
tokens = tokenize(marc_code)  # [sh, 851, 150, 58] or [sh, 8511, 5058] 
llm.ask(f"What is MARC {marc_code}?")  # ❌ Fragmentation prevents lookup

# ✅ CORRECT - Treat as atomic:
marc_code = "sh85115058"  # Atomic string
result = marc_api.lookup(marc_code)  # Tool lookup
```

**Current Usage:**
- Stored in: Some nodes in Cypher files
- Format: "sh" prefix + 8 digits
- Used in: Backbone alignment for bibliography

**Issues:**
1. Alphanumeric format prone to tokenization
2. No documentation on atomic handling
3. Similar tokenization risk to QIDs
4. Could be confused with natural language prefix "sh"

---

### 6. **Pleiades ID** ⚠️ NOT DOCUMENTED AS ATOMIC

**Format:** 6-digit numeric (e.g., `423025`)

**Status:** ⚠️ **NOT EXPLICITLY DOCUMENTED**
- Found in: `Roman Republic/test_roman_kingdom_to_sulla.cypher` (pleiades_id property)
- Used for: Ancient geographic locations
- **NO extraction guide** for Pleiades IDs
- **NO warning** about LLM processing
- **NO atomicity rule**

**Tokenization Risk:** 🔴 **HIGH**

**Example of fragmentation:**
```python
# ❌ DANGER - Pleiades ID could fragment:
pleiades_id = "423025"  # Rome location
tokens = tokenize(pleiades_id)  # [423, 025] or [42, 30, 25] or [4230, 25]
llm.ask(f"What location is Pleiades {pleiades_id}?")  # ❌ Fragmentation prevents lookup

# ✅ CORRECT - Treat as atomic:
pleiades_id = "423025"  # Atomic string
result = pleiades_api.lookup(pleiades_id)  # Tool lookup
pleiades_link = f"https://pleiades.stoa.org/places/{pleiades_id}"  # URL construction
```

**Current Usage:**
- Stored in: Geographic place nodes
- Format: 6-digit numeric string
- Used in: Ancient geography references
- Often paired with: pleiades_link URL

**Issues:**
1. Pure numeric format highly prone to tokenization
2. No documentation on atomic handling
3. Critical for ancient geography lookups
4. Would fail silently if fragmented

---

### 7. **GeoNames ID** ⚠️ PARTIALLY DOCUMENTED AS ATOMIC

**Format:** Numeric ID (variable length)

**Status:** ⚠️ **PARTIALLY DOCUMENTED**
- Found in: `temporal/Geo/scripts/generate_place_entities.py`
- Comment says: "# Atomic string"
- **Limited documentation** in extraction guides
- **Implicit atomicity** in code comments

**Tokenization Risk:** 🟡 **MEDIUM**

**Example:**
```python
# From generate_place_entities.py (Line 94-95):
'qid': qid,  # Atomic string
'geonames_id': row.get('GeoNames_ID', '').strip() if row.get('GeoNames_ID') else None,

# Later (Line 125):
if place.get('geonames_id'):
    props['geonames_id'] = place['geonames_id']  # Atomic string
```

**Current Usage:**
- Stored in: Geographic place entities
- Format: Numeric string
- Purpose: GeoNames database lookups

**Issues:**
1. Only documented in code comments
2. Not in main extraction guide
3. Numeric format prone to tokenization
4. Needs explicit extraction rules

---

### 8. **ISO 8601 Dates** ✅ DOCUMENTED AS ATOMIC

**Format:** `YYYY-MM-DD` or `-YYYY-MM-DD` (e.g., `2025-03-12`, `-0753-01-01`)

**Status:** ✅ **DOCUMENTED**
- Documented in: `temporal/docs/Temporal_Data_Extraction_Guide.md`
- Rule: "✅ Let tools parse, not LLM"
- Storage: Atomic string
- Tokenization risk: HIGH without delimiters

**Evidence:**
- Line 232: "✅ Store as atomic string"
- Line 244: "❌ Atomic string (tool formatted)"
- Line 478: "❌ ATOMIC STRING"

---

### 9. **Coordinates (Latitude/Longitude)** ✅ DOCUMENTED AS ATOMIC

**Format:** Numeric floats (e.g., `41.9028`, `12.4964`)

**Status:** ✅ **DOCUMENTED**
- Documented in: Code comments and geo scripts
- Rule: "Atomic numerics - never pass to LLM as strings"
- Storage: Numeric (not string)

**Evidence from generate_place_entities.py:**
```python
# Lines 96-97:
'latitude': coords[0] if coords else None,  # Atomic float or None
'longitude': coords[1] if coords else None,  # Atomic float or None

# Lines 121-122:
props['latitude'] = place['latitude']  # Atomic float
props['longitude'] = place['longitude']  # Atomic float
```

---

## Risk Assessment Matrix

| Identifier Type | Tokenization Risk | Documented | In Extraction Guide | Action Required |
|-----------------|-------------------|------------|---------------------|-----------------|
| **Wikidata QID** | 🔴 HIGH | ✅ YES | ✅ YES | ✅ None (already documented) |
| **FAST ID** | 🔴 HIGH | ❌ NO | ❌ NO | 🔴 **URGENT: Add to guide** |
| **LCC Code** | 🟡 MED-HIGH | ❌ NO | ❌ NO | 🔴 **URGENT: Add to guide** |
| **LCSH Heading** | ✅ NONE | N/A | N/A | ✅ Safe (natural language) |
| **MARC Code** | 🔴 HIGH | ❌ NO | ❌ NO | 🔴 **URGENT: Add to guide** |
| **Pleiades ID** | 🔴 HIGH | ❌ NO | ❌ NO | 🔴 **URGENT: Add to guide** |
| **GeoNames ID** | 🟡 MEDIUM | ⚠️ CODE ONLY | ❌ NO | 🟡 **HIGH: Document properly** |
| **ISO 8601 Date** | 🔴 HIGH | ✅ YES | ✅ YES | ✅ None (already documented) |
| **Coordinates** | 🟡 MEDIUM | ✅ CODE | ⚠️ PARTIAL | 🟡 **MED: Add to main guide** |

---

## Critical Gap Analysis

### What's Missing:

1. ❌ **FAST IDs** not in extraction guide
2. ❌ **LCC codes** not in extraction guide
3. ❌ **MARC codes** not in extraction guide
4. ❌ **Pleiades IDs** not in extraction guide
5. ⚠️ **GeoNames IDs** only in code comments
6. ⚠️ **Coordinates** not in main extraction guide

### Impact:

**If these IDs are passed to LLMs:**
- FAST ID lookups fail → backbone alignment breaks
- LCC lookups fail → classification system breaks
- MARC lookups fail → bibliographic links break
- Pleiades lookups fail → ancient geography breaks
- GeoNames lookups fail → modern geography breaks

### Likelihood:

**HIGH** - Because:
1. IDs are stored in database properties
2. Agents may extract them from documents
3. No explicit warnings in documentation
4. Numeric formats invite LLM processing
5. No validation checks exist

---

## Recommended Immediate Actions

### 1. Update `Temporal_Data_Extraction_Guide.md` ✅ CRITICAL

Add section for all backbone/geographic identifiers:

```markdown
### ❌ FAST IDs (Faceted Application of Subject Terminology)

**Format:** 7-digit numeric (e.g., `1145002`, `831351`)

**Critical Rules:**
1. ❌ NEVER pass FAST ID to LLM for interpretation
2. ✅ ALWAYS use as lookup key in FAST API/database
3. ✅ Store as string (not integer)
4. ✅ Treat as opaque identifier

**Tokenization Risk:**
```python
# ❌ BAD - Gets fragmented:
fast_id = "1145002"
tokens = tokenize(fast_id)  # [114, 500, 2] - fragments prevent lookup

# ✅ GOOD - Treat as atomic:
fast_id = "1145002"  # Atomic string
result = fast_lookup_tool(fast_id)
```

### ❌ LCC Codes (Library of Congress Classification)

**Format:** Letter(s) + optional numbers and ranges (e.g., `T`, `DG241-269`)

**Critical Rules:**
1. ❌ NEVER pass LCC code to LLM for interpretation
2. ✅ ALWAYS use as lookup key in LCC system
3. ✅ Store as string
4. ✅ Preserve exact format including hyphens

**Tokenization Risk:**
```python
# ❌ BAD - Complex codes fragment:
lcc = "DG241-269"
tokens = tokenize(lcc)  # [DG, 241, -, 269] - breaks lookup

# ✅ GOOD - Treat as atomic:
lcc = "DG241-269"  # Atomic string
result = lcc_lookup_tool(lcc)
```

### ❌ MARC Codes

**Format:** `sh` + 8 digits (e.g., `sh85115058`)

**Critical Rules:**
1. ❌ NEVER pass MARC code to LLM
2. ✅ Store as atomic string
3. ✅ Use for bibliographic lookups only

### ❌ Pleiades IDs (Ancient Geography)

**Format:** 6-digit numeric (e.g., `423025`)

**Critical Rules:**
1. ❌ NEVER pass Pleiades ID to LLM
2. ✅ Store as string (not integer)
3. ✅ Use for Pleiades API lookups
4. ✅ Construct URLs: `https://pleiades.stoa.org/places/{id}`

### ❌ GeoNames IDs (Modern Geography)

**Format:** Numeric ID (variable length)

**Critical Rules:**
1. ❌ NEVER pass GeoNames ID to LLM
2. ✅ Store as string
3. ✅ Use for GeoNames API lookups
```

### 2. Create Validation Tool ✅ HIGH PRIORITY

```python
# relations/scripts/validate_identifier_atomicity.py

def check_identifier_in_llm_prompt(prompt: str) -> dict:
    """
    Scan prompt for system identifiers that shouldn't be there.
    
    Returns warnings if identifiers detected.
    """
    issues = []
    
    # Check for FAST IDs (7 digits)
    if re.search(r'\b\d{7}\b', prompt):
        issues.append({
            'type': 'FAST_ID',
            'severity': 'HIGH',
            'message': 'Possible FAST ID in LLM prompt'
        })
    
    # Check for LCC codes
    if re.search(r'\b[A-Z]{1,3}\d+-\d+\b', prompt):
        issues.append({
            'type': 'LCC_CODE',
            'severity': 'HIGH',
            'message': 'Possible LCC code in LLM prompt'
        })
    
    # Check for MARC codes
    if re.search(r'\bsh\d{8}\b', prompt):
        issues.append({
            'type': 'MARC_CODE',
            'severity': 'HIGH',
            'message': 'Possible MARC code in LLM prompt'
        })
    
    # Check for Pleiades IDs (6 digits)
    if re.search(r'\b\d{6}\b', prompt):
        issues.append({
            'type': 'PLEIADES_ID',
            'severity': 'MEDIUM',
            'message': 'Possible Pleiades ID in LLM prompt'
        })
    
    # Check for QIDs (already documented but double-check)
    if re.search(r'\bQ\d+\b', prompt):
        issues.append({
            'type': 'WIKIDATA_QID',
            'severity': 'CRITICAL',
            'message': 'QID detected in LLM prompt - NEVER pass QIDs to LLM!'
        })
    
    return {
        'safe': len(issues) == 0,
        'issues': issues
    }
```

### 3. Update Cypher Files ✅ MEDIUM PRIORITY

Add comments to all Cypher files using these IDs:

```cypher
// ⚠️ ATOMIC IDENTIFIERS - NEVER PASS TO LLM:
//   - qid: Wikidata QID (e.g., "Q17167")
//   - backbone_fast: FAST ID (e.g., "1145002")
//   - backbone_lcc: LCC code (e.g., "DG241-269")
//   - backbone_marc: MARC code (e.g., "sh85115058")
//   - pleiades_id: Pleiades ID (e.g., "423025")
//   - geonames_id: GeoNames ID (numeric string)
//
// These are TOOL-RESOLVED ONLY. Extract natural language labels with LLM,
// then resolve to these IDs using tools/APIs.

CREATE (entity:Concept {
  label: "Roman Republic",           // ✅ Natural language (LLM can extract)
  qid: "Q17193",                     // ❌ Atomic (tool-resolved)
  backbone_fast: "fst01411640",      // ❌ Atomic (tool-resolved)
  backbone_lcc: "DG241-269",         // ❌ Atomic (tool-resolved)
  backbone_marc: "sh85115058"        // ❌ Atomic (tool-resolved)
})
```

### 4. Create Cheat Sheet ✅ LOW PRIORITY

Create `relations/IDENTIFIER_CHEAT_SHEET.md`:

**Quick Reference: Can LLM Process This?**

| Data Type | Example | LLM Can Process? | How to Handle |
|-----------|---------|------------------|---------------|
| Period name | "Roman Republic" | ✅ YES | Extract with LLM |
| Date text | "49 BCE" | ✅ YES | Extract with LLM, convert with tool |
| **Wikidata QID** | **"Q17193"** | **❌ NO** | **Tool lookup only** |
| **FAST ID** | **"1145002"** | **❌ NO** | **Tool lookup only** |
| **LCC code** | **"DG241-269"** | **❌ NO** | **Tool lookup only** |
| **MARC code** | **"sh85115058"** | **❌ NO** | **Tool lookup only** |
| **Pleiades ID** | **"423025"** | **❌ NO** | **Tool lookup only** |
| **GeoNames ID** | **"2643743"** | **❌ NO** | **Tool lookup only** |
| LCSH heading | "Political science" | ✅ YES | Natural language |
| Coordinates | `41.9028, 12.4964` | ⚠️ NUMBERS | Store as numeric, never stringify |
| ISO date | "-0753-01-01" | ❌ NO | Tool-formatted only |

---

## Current State Assessment

### What's Protected: ✅
1. Wikidata QIDs - Fully documented
2. ISO 8601 dates - Fully documented
3. Coordinates - Code-documented

### What's Vulnerable: ⚠️
1. FAST IDs - No documentation
2. LCC codes - No documentation
3. MARC codes - No documentation
4. Pleiades IDs - No documentation
5. GeoNames IDs - Minimal documentation

---

## Next Steps

1. **URGENT:** Update `Temporal_Data_Extraction_Guide.md` with all identifier types
2. **HIGH:** Create validation tool for identifier detection in prompts
3. **MEDIUM:** Add warning comments to all Cypher files
4. **LOW:** Create quick-reference cheat sheet

---

**Status:** ⚠️ CRITICAL GAPS IDENTIFIED  
**Risk Level:** 🔴 HIGH - Multiple identifier types at risk of tokenization  
**Recommendation:** Update extraction guide immediately before any LLM agent work

---

**Your concern is 100% valid. This needs immediate attention.**


