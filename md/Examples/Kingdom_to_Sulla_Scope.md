# Test Case Scope: Roman Kingdom to Sulla's Dictatorship

## Timeline Coverage

- **Start**: 753 BCE (`'-0753-01-01'`) - Foundation of Roman Kingdom
- **End**: 82 BCE (`'-0082-01-01'`) - Sulla named dictator

## Date Format Standards (ISO 8601 + Canonical Time Backbone)

All dates in this scope conform to:
1. **ISO 8601 Format:**
   - BCE dates: `'-0753-01-01'` (negative year with leading zeros, -YYYY-MM-DD)
   - CE dates: `'1600-01-01'` (positive year, YYYY-MM-DD)

2. **Canonical Time Backbone Properties:**
   - `start_date`: ISO 8601 formatted date string
   - `end_date`: ISO 8601 formatted date string
   - `date_precision`: Precision level (`'day'`, `'month'`, `'year'`, `'century'`)
   - `temporal_period_classification`: Historical period name (from `Temporal/time_periods.csv`)
   - `temporal_period_qid`: Wikidata QID of the historical period
   - `temporal_period_start`: Start year of the period (integer)
   - `temporal_period_end`: End year of the period (integer)

3. **Historical Period Classification:**
   - **Roman Kingdom** (753-509 BCE): QID `Q17167`, Start: `-753`, End: `-509`
   - **Roman Republic** (509-27 BCE): QID `Q17193`, Start: `-509`, End: `-27`
   - **Ancient History** (-3000 to 650): QID `Q41493`
   - Source: `Temporal/time_periods.csv`

## Key Periods Covered

### 1. Roman Kingdom (753-509 BCE)
- **ISO 8601 Range:** `'-0753-01-01'` to `'-0509-12-31'`
- **Temporal Period:** Roman Kingdom (QID: `Q17167`)
- Basic background
- Foundation and structure
- Overthrow and transition to Republic

### 2. Early Republic (509 BCE onwards)
- **ISO 8601 Start:** `'-0509-01-01'`
- **Temporal Period:** Roman Republic (QID: `Q17193`)
- Establishment of consulship
- Foundation of republican institutions

### 3. Lead-up to Sulla's Dictatorship

#### Social War (91-88 BCE)
- **ISO 8601 Range:** `'-0091-01-01'` to `'-0088-12-31'`
- **Temporal Period:** Roman Republic (QID: `Q17193`)
- Conflict between Rome and Italian allies
- Sulla's military service
- Result: Citizenship granted to Italian allies

#### First Mithridatic War (89-85 BCE)
- **ISO 8601 Range:** `'-0089-01-01'` to `'-0085-12-31'`
- **Temporal Period:** Roman Republic (QID: `Q17193`)
- War against Mithridates VI of Pontus
- Command dispute between Sulla and Marius
- Sulla's successful campaign

#### First March on Rome (88 BCE)
- **ISO 8601 Date:** `'-0088-01-01'` (approximate, date precision: year)
- **Temporal Period:** Roman Republic (QID: `Q17193`)
- Sulla's unprecedented action
- Regaining command from Marius
- Breaking of republican taboo

#### Sullan Civil War (83-82 BCE)
- **ISO 8601 Range:** `'-0083-01-01'` to `'-0082-12-31'`
- **Temporal Period:** Roman Republic (QID: `Q17193`)
- Conflict between Sulla and Marians
- Sulla's return from Greece
- Battle for control of Rome

#### Sulla's Second March on Rome (82 BCE)
- **ISO 8601 Date:** `'-0082-01-01'` (approximate, date precision: year)
- **Temporal Period:** Roman Republic (QID: `Q17193`)
- Final victory over Marians
- Control of the city

#### Sulla Named Dictator (82 BCE)
- **ISO 8601 Date:** `'-0082-01-01'` (approximate, date precision: year)
- **Temporal Period:** Roman Republic (QID: `Q17193`)
- **End Point** - Senate appointment
- Unlimited authority granted
- Beginning of constitutional reforms

## Key Entities

### Political Organizations
- Roman Kingdom
- Roman Republic

### People
- **Lucius Junius Brutus** - First consul (`'-0509-01-01'`, date precision: year)
- **Lucius Cornelius Sulla Felix** - Dictator (`'-0082-01-01'`, date precision: year)
- **Gaius Marius** - Sulla's rival

### Positions
- King of Rome
- Consul
- Dictator

### Major Events
- Overthrow of Monarchy (`'-0509-01-01'`, date precision: year)
- Social War (`'-0091-01-01'` to `'-0088-12-31'`)
- First Mithridatic War (`'-0089-01-01'` to `'-0085-12-31'`)
- Sulla's First March on Rome (`'-0088-01-01'`, date precision: year)
- Sullan Civil War (`'-0083-01-01'` to `'-0082-12-31'`)
- Sulla's Second March on Rome (`'-0082-01-01'`, date precision: year)
- Sulla Named Dictator (`'-0082-01-01'`, date precision: year)

## Property Extensions Included

### For Places
- Geographic coordinates
- Pleiades ID and link
- Google Earth link

### For People
- Image URLs (where available)
- Online text availability
- Temporal data (birth/death dates)

### For All Entities
- **Backbone alignment** (FAST, LCC, LCSH, MARC)
- **ISO 8601 dates** (start_date, end_date)
- **Date precision** (day, month, year, century)
- **Temporal backbone alignment:**
  - `temporal_period_classification` (e.g., 'Roman Kingdom', 'Roman Republic')
  - `temporal_period_qid` (Wikidata QID from Temporal/time_periods.csv)
  - `temporal_period_start` (start year as integer)
  - `temporal_period_end` (end year as integer)

## Relationship Structure

All relationships include:
- Action structure (goal, trigger, action, result)
- Narrative summaries
- Temporal information
- Confidence scores

## Test Case Identifier

All nodes and relationships use:
```
test_case: 'kingdom_to_sulla'
```

## Query Examples

See bottom of `test_kingdom_to_sulla.cypher` for example queries:
- Timeline from Kingdom to Sulla
- Sulla's career progression
- Chronological event listing
- Action structure queries

