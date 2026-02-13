# Output Format: Process and Facet Determination

## What You'll See When Running the Script

### Step 1: Parsing
```
📊 Step 1: Parsing periods from Cypher file...
   Found 1005 periods
```

### Step 2: Analysis (Detailed for Each Period)

For each period, you'll see:

```
   [1/1005] Processing: Prehistoric Brussels
      QID: entity/Q126951505>
      Dates: ? to 56
      Location: entity/Q111901161>
      → Determining primary facet (Perplexity API)...✓
      Facet Determination (perplexity-api):
         Primary Facet: ArchaeologicalFacet
         Confidence: 0.85
         Is Period: True
         Is Event: False
      Validation: ✅ PASSED - Will be included in output

   [2/1005] Processing: Habsburg Netherlands
      QID: entity/Q1031430>
      Dates: 1482 to 1797
      Location: entity/Q476033>
      → Determining primary facet (Perplexity API)...✓
      Facet Determination (perplexity-api):
         Primary Facet: PoliticalFacet
         Confidence: 0.90
         Is Period: True
         Is Event: False
      Validation: ✅ PASSED - Will be included in output

   [3/1005] Processing: World War II
      QID: entity/Q362>
      Dates: 1939 to 1945
      → Determining primary facet (Perplexity API)...✓
      Facet Determination (perplexity-api):
         Primary Facet: MilitaryFacet
         Confidence: 0.95
         Is Period: False
         Is Event: True
      Validation: ❌ EVENT (will skip)

   [4/1005] Processing: Modern animation in the United States
      QID: entity/Q1038653>
      → Determining primary facet (Rule-based)...✓
      Facet Determination (rule-based):
         Primary Facet: CulturalFacet
         Confidence: 0.60
         Is Period: True
         Is Event: False
      Validation: ❌ MISSING DATES
```

### Step 3: Cypher Generation

```
📝 Step 3: Generating enriched Cypher file...

   Processing 1005 analyzed periods for Cypher generation...
      ⚠️  FILTERED: Missing dates (start_year, end_year) - Modern animation in the United States
      ⚠️  FILTERED: Event detected - World War II
      ✅ INCLUDED [1]: Prehistoric Brussels
         Primary Facet: ArchaeologicalFacet
         Dates: ? to 56
         Location: entity/Q111901161>
      ✅ INCLUDED [2]: Habsburg Netherlands
         Primary Facet: PoliticalFacet
         Dates: 1482 to 1797
         Location: entity/Q476033>
```

### Final Summary

```
================================================================================
Summary
================================================================================
Total analyzed: 1005
✅ Valid periods (with dates + location, end >= 2000 BCE): 750
❌ Events (filtered out): 50
❌ Missing start/end dates: 80
❌ Missing location: 95
❌ End date before 2000 BCE: 30

✅ Enriched file ready: Subjects/periods_import_enriched.cypher
================================================================================
```

## What Each Section Shows

### Processing Section
- Period number and total
- Period label
- QID (last 20 chars)
- Date range (if available)
- Location QID (if available)

### Facet Determination Section
- Method used (Perplexity API or Rule-based)
- Primary facet assigned
- Confidence score (0.0 to 1.0)
- Whether it's a period or event
- Validation status

### Generation Section
- Which periods are filtered and why
- Which periods are included
- For included periods: primary facet, dates, location

## Example: Complete Output for One Period

```
   [23/1005] Processing: Habsburg Netherlands
      QID: entity/Q1031430>
      Dates: 1482 to 1797
      Location: entity/Q476033>
      → Determining primary facet (Perplexity API)...✓
      Facet Determination (perplexity-api):
         Primary Facet: PoliticalFacet
         Confidence: 0.90
         Is Period: True
         Is Event: False
      Validation: ✅ PASSED - Will be included in output

   Processing 1005 analyzed periods for Cypher generation...
      ✅ INCLUDED [15]: Habsburg Netherlands
         Primary Facet: PoliticalFacet
         Dates: 1482 to 1797
         Location: entity/Q476033>
```

This shows:
1. ✅ Period was analyzed
2. ✅ Primary facet determined: PoliticalFacet
3. ✅ All validations passed
4. ✅ Included in final Cypher file

