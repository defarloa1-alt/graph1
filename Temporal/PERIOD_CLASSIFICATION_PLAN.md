# Period Classification and Cleanup Plan

**Date:** January 16, 2026  
**Status:** Planning Phase - NOT YET EXECUTED

---

## Classification Strategy

Based on historiographic analysis, classify the 130+ period entries into:

### Tier 1: **Historical Periods** (Keep as Period nodes)
- Extended spans (decades+)
- Widely used in historiography
- Coherent political/social/cultural pattern
- **Action:** Keep as `:Period` nodes

### Tier 2: **Events/Phases** (Convert to Event nodes)
- Short duration (< 5-10 years typically)
- Tightly bound to specific wars, crises, persons
- Better modeled as events
- **Action:** Convert `:Period` → `:Event`

### Tier 3: **Institutional Spans** (Convert to specialized nodes)
- Life of institutions, archives, offices, courts
- Administrative/bureaucratic intervals
- Not historiographic periods
- **Action:** Convert `:Period` → `:InstitutionalSpan` or delete

### Tier 4: **Problematic Entries** (Remove or reclassify)
- Disciplines masquerading as periods (e.g., "Classics")
- Suspicious date ranges
- Conceptually muddled
- **Action:** Remove or reclassify

---

## Tier 1: Keep as Historical Periods (✅ ~80-90 periods)

### Ancient Near East & Mediterranean (15 periods)
- Mesopotamia: Early Dynastic III / IIIa / IIIb
- Elam: Proto-Elamite period (Q1196237)
- Mesopotamia: Isin-Larsa period (Q13577667)
- Mesopotamia: Ur III period (Q109384761)
- Crete: Minoan civilization (Q134178)
- Peloponnese: Helladic period (Q937774)
- Ancient Egypt: Second Intermediate Period (Q206715)
- Amarna: Amarna Period (Q455151)
- Latium: Roman Kingdom (Q201038)
- Ancient Greece: Classical Greece (Q843745)
- Classical Athens: Fifth-century Athens (Q2000977)
- Ancient Greece: Macedonian Period (Q12880607)
- Land of Israel: Second Temple period (Q2911414)
- Southern Levant: Roman Palestine (Q15843470)
- Southern Levant: Holy Land during Byzantine rule (Q11802354)

### China & East Asia (12 periods)
- China: Ancient China (Q630276)
- China: Spring and Autumn period (Q185047)
- China: Three Kingdoms (Q185043)
- China: Sixteen Kingdoms (Q683551)
- China: Five Dynasties and Ten Kingdoms Period (Q242115)
- China: Warlord Era (Q1201263)
- Korea: Samhan (Q1376093)
- Korea: Three Kingdoms of Korea (Q165292)
- Korea: North South States Period (Q702639)
- Ryūkyū: Sanzan period (Q55525)

### South Asia / India (2 periods)
- Indian subcontinent: Iron Age India (Q1056845)
- South Asia: Medieval India (Q12057021)

### European Medieval & Early Modern (20 periods)
- continental Europe: Migration Period (Q131192)
- Europe: Early Middle Ages (Q202763)
- Europe: High Middle Ages (Q212685)
- Europe: Late Middle Ages (Q212976)
- Northern Europe: Viking Age (Q213649)
- Iberian Peninsula: Early Middle Ages in the Iberian Peninsula (Q63226529)
- Low Countries: Burgundian Netherlands (Q157109)
- Greece / Central Greece / Peloponnese: Frankokratia (Q1197995)
- Netherlands: Dutch Golden Age (Q661566)
- Italy: Proto-Renaissance (Q979160)
- Italy: High Renaissance (Q1474884)
- Italy: Unification of Italy (Q51122)
- Europe: Scientific Revolution (Q214078)
- Europe: Baroque (Q37853)
- London: Tudor London (Q7851298)
- London: Stuart London (Q7626770)

### Islamic & Ottoman (10 periods)
- Southern Levant: early Islamic period in Palestine (Q12407080)
- Southern Levant: Mamluk Palestine (Q12407079)
- Najd/Hejaz: Jahiliyyah (Q726805)
- Medina: Muhammad in Medina (Q4086877)
- North Africa / Central Asia: Administrative policies of Ali (Q4725297)
- Ottoman Empire: Sultanate of Women (Q1543663)
- Turkey / Ottoman Empire: Tanzimat (Q330961)
- Ottoman Empire: First Constitutional Era (Q3545916)
- Southern Levant: Ottoman Palestine (Q2909425)
- Jerusalem during the Ottoman period (Q6262238)
- Syria: Ottoman Syria (Q3076765)

### Americas (4 periods)
- Americas: pre-Columbian era (Q202390)
- Peru: Sican culture (Q175801)
- North America: Woodland period (Q2299963)
- Southern United States: Antebellum South (Q7201622)

### Modern Global (5 periods)
- United States: American Century (Q3073537)
- Asia / Africa / Latin America / Europe: Cold War (Q8683)
- Europe: European Civil War (Q531510)

### Brussels Micro-Periods (8 periods - local history)
- Gallo-Roman Brussels (Q126949584)
- Merovingian Brussels (Q126951002)
- Carolingian Brussels (Q126951135)
- Lotharingian Brussels (Q126951168)
- Burgundian Brussels (Q126949104)
- Habsburg Brussels (Q126949076)
- French Brussels (Q126949230)
- Dutch Brussels (Q126949309)

### Canonical Era Layer (7 macro-periods)
- Ancient History (Q41493)
- Classical Antiquity (Q486761)
- Post-Classical / Medieval (Q12554)
- Early Modern (Q5308718)
- Long 19th Century (Q1368990)
- Short 20th Century (Q3769095)
- Contemporary (Q6958377)

---

## Tier 2: Convert to Event Nodes (❌→📅 ~10-15 entries)

### Short Military/Political Crises
```cypher
// Convert to Event
MATCH (p:Period {qid: 'Q129167'})  // barracks emperor
SET p:Event
REMOVE p:Period
SET p.event_type = 'political_crisis',
    p.granularity = 'composite'
```

**List:**
- Q129167: barracks emperor → Event (Crisis of 3rd Century phase)
- Q329838: Crisis of the Third Century → Event (or keep as short period)
- Q3800893: Barbarian invasion of the 3rd century → Event
- Q15140974: Barbarian invasions of the 4th century → Event
- Q193547: Reign of Terror → Event (1 year)
- Q474757: Thermidorian Reaction → Event (short phase)
- Q111699632: Black Week → Event (1 week!)
- Q190882: Phoney War → Event (campaign phase)
- Q4090708: Boldino autumn → Event (literary episode)

---

## Tier 3: Convert to InstitutionalSpan or Delete (❌→🏛️ ~5-10 entries)

### Institutional/Administrative
```cypher
// Create new label
MATCH (p:Period {qid: 'Q23019825'})  // Rehnquist Court
SET p:InstitutionalSpan
REMOVE p:Period
SET p.institution_type = 'court',
    p.institution_name = 'US Supreme Court'
```

**List:**
- Q23019825: Rehnquist Court → InstitutionalSpan
- Q111601268: Mayoralty of Dimitris Avramopoulos → InstitutionalSpan or DELETE
- Q28028316: Alfred Nobel Family Archives → DELETE (archival collection)
- Q4916863: Birmingham pen trade → InstitutionalSpan (economic phase)
- Q107124778: Paris-East law faculty → DELETE (institutional)
- Q113206337: Agronomía → DELETE (unclear)

---

## Tier 4: Remove or Reclassify (❌ ~5 entries)

### Problematic Entries
```cypher
// Delete problematic period
MATCH (p:Period {qid: 'Q12793702'})  // Europe: Classics (discipline, not period)
DETACH DELETE p
```

**List:**
- Q12793702: Europe: Classics → DELETE (discipline, not period)
- Q131433113: Qutux Llyung Topa (500-1907) → REVIEW (1400 years suspicious)
- Q133871248: Medieval Abkhazia (800-1800) → REVIEW (1000 years too broad)
- Q127237209: Indonesia span (1330-1863) → REVIEW (500+ years vague)

---

## Implementation Plan

### Phase 1: Analysis & CSV Generation

**Create classification CSV:**
```csv
qid,current_label,classification,action,new_node_type,reason
Q129167,barracks emperor,EVENT,convert,Event,Short crisis period
Q12793702,Europe: Classics,PROBLEMATIC,delete,N/A,Discipline not period
Q23019825,Rehnquist Court,INSTITUTIONAL,convert,InstitutionalSpan,Court term
Q185047,Spring and Autumn period,KEEP,none,Period,Standard historiographic period
...
```

### Phase 2: Create New Node Types

```cypher
// Create InstitutionalSpan label if needed
CREATE CONSTRAINT institutional_span_qid IF NOT EXISTS
FOR (i:InstitutionalSpan) REQUIRE i.qid IS UNIQUE
```

### Phase 3: Execute Conversions

**Script 1: Convert to Events**
```python
# Python/convert_periods_to_events.py
# Reads: period_classification.csv
# Action: Convert specified periods to Event nodes
```

**Script 2: Convert to InstitutionalSpans**
```python
# Python/convert_periods_to_institutional.py
# Reads: period_classification.csv
# Action: Convert institutional periods
```

**Script 3: Delete Problematic**
```python
# Python/delete_problematic_periods.py
# Reads: period_classification.csv
# Action: Delete entries that don't belong
```

### Phase 4: Verification

```cypher
// Verify Period nodes are clean
MATCH (p:Period)
WHERE p.end_year - p.start_year < 2  // Flag very short "periods"
RETURN p.qid, p.label, p.start_year, p.end_year
```

---

## Classification Rules (Codified)

### Rule 1: Duration Threshold
```python
def is_period(start_year, end_year):
    duration = end_year - start_year
    if duration >= 20:  # 20+ years
        return True
    elif duration >= 2 and is_canonical_short_period():  # Exception for Reign of Terror, etc.
        return True
    else:
        return False  # Too short, make it an Event
```

### Rule 2: Name Pattern Matching
```python
# Auto-flag for Event conversion
event_keywords = ['week', 'war', 'battle', 'crisis', 'invasion', 'rebellion', 'uprising']

# Auto-flag for Institutional conversion
institutional_keywords = ['court', 'mayoralty', 'archives', 'faculty', 'office of']

# Auto-flag for deletion
delete_keywords = ['Q[digits with no label]', 'Unknown', 'archival collection']
```

### Rule 3: Historiographic Validation
- If used as a named period in scholarly literature → Keep
- If it's a bureaucratic/administrative label → Convert or delete
- If it's a discipline name (like "Classics") → Delete

---

## Expected Outcomes

### Before
- 130 Period nodes (mixed quality)
- Some are events, some are institutions, some are periods

### After
- **~80-90 Period nodes** (clean, historiographically valid)
- **~10-15 Event nodes** (converted from short periods)
- **~5-10 InstitutionalSpan nodes** (converted from office/institutional periods)
- **~5-10 deleted** (problematic entries)

---

## Next Steps

1. **Manual Review:** You review the classification above
2. **Create CSV:** I create `period_classification.csv` with all 130 entries classified
3. **Create Scripts:** I create conversion/deletion scripts
4. **Execute:** Run scripts to clean up the Period nodes
5. **Rebuild Years:** After cleanup, rebuild Year backbone and link to clean Periods

---

## Questions for You

1. **Keep Brussels micro-periods?** (8 very local periods - they're valid but hyper-local)
2. **Keep institutional periods like "Rehnquist Court"?** (valid for legal history but not general history)
3. **Minimum period duration?** (I suggest 20 years, with exceptions for canonical phases)
4. **Keep very long polity spans?** (e.g., Meliau Kingdom 1762-1960, 198 years)
5. **Keep "Cold War" style global frames?** (thematic rather than strictly temporal)

Let me know your preferences and I'll generate the classification CSV and conversion scripts!

