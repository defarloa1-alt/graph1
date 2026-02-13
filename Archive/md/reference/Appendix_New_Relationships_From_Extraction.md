# Appendix: New Relationships from LLM Extraction Experiment

## Source
Relationships identified as missing during the Osci Wikipedia page extraction experiment. These relationships are needed to model historical facts extracted from text.

---

## New Relationship Types to Add to `neo4j_relationships_bidirectional.csv`

### Linguistic Relationships

```csv
Linguistic,SPOKE_LANGUAGE,People/group spoke a language,P1412,forward
Linguistic,LANGUAGE_OF,Language was spoken by people/group,P1412,inverse
```

**Example Usage:**
- `Osci → SPOKE_LANGUAGE → Oscan language`
- `Samnites → SPOKE_LANGUAGE → Oscan language`

**Wikidata Property:** P1412 (language spoken)

---

### Cultural Assimilation Relationships

```csv
Cultural,ASSIMILATED_TO,Group/people assimilated into another culture,,forward
Cultural,ASSIMILATED,Culture that absorbed another group,,inverse
```

**Example Usage:**
- `Osci → ASSIMILATED_TO → Roman culture`

**Wikidata Property:** (may need custom, or use P460 - "said to be the same as")

---

### Diplomatic Relationships

```csv
Diplomatic,APPEALED_TO,Entity appealed/requested help from another,,forward
Diplomatic,RECEIVED_APPEAL_FROM,Entity received appeal/request for help,,inverse
Diplomatic,ACCEPTED_OFFER,Accepted diplomatic offer/proposal,,forward
Diplomatic,OFFER_ACCEPTED_BY,Diplomatic offer was accepted by entity,,inverse
Diplomatic,REJECTED_OFFER,Rejected diplomatic offer/proposal,,forward
Diplomatic,OFFER_REJECTED_BY,Diplomatic offer was rejected by entity,,inverse
Diplomatic,OFFERED_SELF_TO,Offered themselves as subjects/allies to another entity,,forward
Diplomatic,RECEIVED_OFFER_FROM,Received offer of subjection/alliance from entity,,inverse
Diplomatic,SENT_ENVOYS_TO,Sent diplomatic envoys/representatives,,forward
Diplomatic,RECEIVED_ENVOYS_FROM,Received diplomatic envoys/representatives from entity,,inverse
```

**Example Usage:**
- `Sidicini → APPEALED_TO → Campania`
- `Campanians → OFFERED_SELF_TO → Rome`
- `Rome → ACCEPTED_OFFER → Campanians`
- `Aurunci → SENT_ENVOYS_TO → Romans`
- `Rome → REJECTED_OFFER → Sidicini` (implied)

**Wikidata Properties:** 
- P1412 (may not have direct equivalents for all)
- Consider P1037 (director/manager), P488 (chairperson) for diplomatic roles

---

### Political/Sovereignty Relationships

```csv
Political,SUBJUGATED,Conquered/subdued and incorporated into empire,,forward
Political,SUBJUGATED_BY,Was conquered/subdued and incorporated,,inverse
Political,LOST_SOVEREIGNTY,Lost political independence/sovereignty,,forward
Political,GAINED_SOVEREIGNTY_OVER,Gained political sovereignty over entity,,inverse
```

**Example Usage:**
- `Romans → SUBJUGATED → Osci`
- `Osci → LOST_SOVEREIGNTY → (during Second Samnite War)`

**Wikidata Properties:**
- P361 (part of) - for incorporation
- P576 (dissolved/abolished) - for sovereignty loss

**Note:** SUBJUGATED is more specific than CONQUERED (implies incorporation/absorption)

---

### Military Detail Relationships

```csv
Military,SALLIED_FROM,Made military sortie/sally from besieged place,,forward
Military,GARRISONED,Left military garrison in place,,forward
Military,GARRISONED_BY,Place was garrisoned by military force,,inverse
Military,LEVELLED,Completely destroyed/razed to ground,,forward
Military,LEVELLED_BY,Place was completely destroyed/razed,,inverse
```

**Example Usage:**
- `Aurunci → SALLIED_FROM → Satricum`
- `Romans → GARRISONED → Cales`
- `Romans → LEVELLED → Satricum`

**Wikidata Properties:**
- P576 (dissolved/abolished) - for destruction
- P159 (headquarters) - for garrison (though not exact match)

**Note:** LEVELLED is more extreme than SACKED (complete destruction vs. pillaging)

---

### Economic Relationships

```csv
Economic,SOLD_INTO_SLAVERY,Sold people into slavery,,forward
Economic,SOLD_INTO_SLAVERY_BY,People were sold into slavery by entity,,inverse
Economic,DISTRIBUTED_LAND_TO,Distributed confiscated/conquered land,,forward
Economic,LAND_DISTRIBUTED_BY,Land was distributed by entity,,inverse
```

**Example Usage:**
- `Romans → SOLD_INTO_SLAVERY → 4,000 fighting men`
- `Romans → DISTRIBUTED_LAND_TO → 2,500 colonists`

**Wikidata Properties:**
- P2795 (directions for usage) - not ideal
- May need custom properties

---

### Geographic Relationships

```csv
Geographic,RENAMED,Renamed place or entity,,forward
Geographic,RENAMED_TO,Place was renamed to new name,,inverse
```

**Example Usage:**
- `Aurunci → RENAMED → Suessa → Aurunca`

**Wikidata Property:** P138 (named after) - not exact match, may need custom

---

## Complete CSV Block for Copy-Paste

```csv
Linguistic,SPOKE_LANGUAGE,People/group spoke a language,P1412,forward
Linguistic,LANGUAGE_OF,Language was spoken by people/group,P1412,inverse
Cultural,ASSIMILATED_TO,Group/people assimilated into another culture,,forward
Cultural,ASSIMILATED,Culture that absorbed another group,,inverse
Diplomatic,APPEALED_TO,Entity appealed/requested help from another,,forward
Diplomatic,RECEIVED_APPEAL_FROM,Entity received appeal/request for help,,inverse
Diplomatic,ACCEPTED_OFFER,Accepted diplomatic offer/proposal,,forward
Diplomatic,OFFER_ACCEPTED_BY,Diplomatic offer was accepted by entity,,inverse
Diplomatic,REJECTED_OFFER,Rejected diplomatic offer/proposal,,forward
Diplomatic,OFFER_REJECTED_BY,Diplomatic offer was rejected by entity,,inverse
Diplomatic,OFFERED_SELF_TO,Offered themselves as subjects/allies to another entity,,forward
Diplomatic,RECEIVED_OFFER_FROM,Received offer of subjection/alliance from entity,,inverse
Diplomatic,SENT_ENVOYS_TO,Sent diplomatic envoys/representatives,,forward
Diplomatic,RECEIVED_ENVOYS_FROM,Received diplomatic envoys/representatives from entity,,inverse
Political,SUBJUGATED,Conquered/subdued and incorporated into empire,,forward
Political,SUBJUGATED_BY,Was conquered/subdued and incorporated,,inverse
Political,LOST_SOVEREIGNTY,Lost political independence/sovereignty,,forward
Political,GAINED_SOVEREIGNTY_OVER,Gained political sovereignty over entity,,inverse
Military,SALLIED_FROM,Made military sortie/sally from besieged place,,forward
Military,GARRISONED,Left military garrison in place,,forward
Military,GARRISONED_BY,Place was garrisoned by military force,,inverse
Military,LEVELLED,Completely destroyed/razed to ground,,forward
Military,LEVELLED_BY,Place was completely destroyed/razed,,inverse
Economic,SOLD_INTO_SLAVERY,Sold people into slavery,,forward
Economic,SOLD_INTO_SLAVERY_BY,People were sold into slavery by entity,,inverse
Economic,DISTRIBUTED_LAND_TO,Distributed confiscated/conquered land,,forward
Economic,LAND_DISTRIBUTED_BY,Land was distributed by entity,,inverse
Geographic,RENAMED,Renamed place or entity,,forward
Geographic,RENAMED_TO,Place was renamed to new name,,inverse
```

---

## Summary Statistics

- **Total New Relationships:** 26 (13 forward + 13 inverse pairs)
- **Categories:**
  - Linguistic: 2 relationships
  - Cultural: 2 relationships
  - Diplomatic: 10 relationships (5 pairs)
  - Political: 4 relationships (2 pairs)
  - Military: 5 relationships
  - Economic: 4 relationships (2 pairs)
  - Geographic: 2 relationships (1 pair)

---

## Priority for Implementation

### **High Priority** (Critical for historical text extraction)
1. SPOKE_LANGUAGE / LANGUAGE_OF
2. ASSIMILATED_TO / ASSIMILATED
3. APPEALED_TO / RECEIVED_APPEAL_FROM
4. OFFERED_SELF_TO / RECEIVED_OFFER_FROM
5. ACCEPTED_OFFER / OFFER_ACCEPTED_BY
6. SUBJUGATED / SUBJUGATED_BY

### **Medium Priority** (Important for completeness)
1. SENT_ENVOYS_TO / RECEIVED_ENVOYS_FROM
2. REJECTED_OFFER / OFFER_REJECTED_BY
3. GARRISONED / GARRISONED_BY
4. LEVELLED / LEVELLED_BY
5. SOLD_INTO_SLAVERY / SOLD_INTO_SLAVERY_BY
6. DISTRIBUTED_LAND_TO / LAND_DISTRIBUTED_BY

### **Lower Priority** (Nice to have)
1. LOST_SOVEREIGNTY / GAINED_SOVEREIGNTY_OVER (may overlap with SUBJUGATED)
2. SALLIED_FROM (specific military detail)
3. RENAMED / RENAMED_TO (can use properties instead)

---

## Notes

1. **Wikidata Alignment:** Some relationships don't have direct Wikidata property matches. Consider:
   - Using existing properties where they fit
   - Creating custom properties for Chrystallum-specific needs
   - Documenting the mapping decision

2. **Relationship Hierarchy:** Consider adding parent relationships:
   - Diplomatic relationships could have parent "DIPLOMATIC_ACTION"
   - Military details could be children of FOUGHT_IN or MILITARY_ACTION

3. **Temporal Properties:** Many of these relationships need temporal context (e.g., "during Second Samnite War"). Ensure temporal properties are supported.

4. **Directionality:** All relationships shown are bidirectional pairs (forward/inverse). Some may be unidirectional or symmetric.

---

## Related Documents

- `Osci_Triples_Summary.md` - Simple triple extraction examples
- `LLM_Extraction_Experiment_Osci.md` - Detailed extraction examples
- `Osci_Page_Changes_Appendix.md` - Original gap analysis appendix

