# Property Domain Utility Analysis

**Key Insight:** Chrystallum is a domain-agnostic epistemological engine. Properties labeled "non-useful for history" are actually **useful for other domains**.

---

## 🎯 Domain-Specific Property Distribution

### **Domain 1: Ancient/Medieval History (Current)**

**High-Value Properties (50+):**
```
P19   - place of birth → BIOGRAPHIC/GEOGRAPHIC
P20   - place of death → BIOGRAPHIC/GEOGRAPHIC
P39   - position held → POLITICAL
P241  - military branch → MILITARY
P410  - military rank → MILITARY
P509  - cause of death → BIOGRAPHIC
P569  - date of birth → BIOGRAPHIC
P570  - date of death → BIOGRAPHIC
P580  - start time → TEMPORAL
P582  - end time → TEMPORAL
P607  - conflict → MILITARY
P112  - founded by → POLITICAL/ECONOMIC
P571  - inception → TEMPORAL
P576  - dissolved/abolished → TEMPORAL
```

**Domain Pack:** History  
**Temporal Scope:** -3000 to 1800 CE  
**Entity Focus:** Human, Event, Place, Period, Dynasty, Institution

---

### **Domain 2: Technology/Computing (Future)**

**High-Value Properties:**
```
P348  - software version → TECHNOLOGICAL
P408  - software engine → TECHNOLOGICAL
P487  - Unicode character → LINGUISTIC/TECHNOLOGICAL
P600  - Wine AppDB ID → TECHNOLOGICAL
P404  - game mode → TECHNOLOGICAL
```

**Domain Pack:** Technology History  
**Temporal Scope:** 1945 - present  
**Entity Focus:** Software, Hardware, Algorithm, Protocol, Standard

**Use Case:** Track evolution of computing systems, software genealogy, tech standards

---

### **Domain 3: Modern Sports Analytics (Future)**

**High-Value Properties:**
```
P536  - ATP player ID → SOCIAL
P597  - WTA player ID → SOCIAL
P599  - ITF player ID → SOCIAL
P555  - doubles record → SOCIAL
P564  - singles record → SOCIAL
P741  - playing hand → BIOGRAPHIC
```

**Domain Pack:** Sports Analytics  
**Temporal Scope:** 1800 - present  
**Entity Focus:** Athlete, Team, Competition, Match, Record

**Use Case:** Sports history, player analytics, career statistics

---

### **Domain 4: Biological/Environmental Science (Future)**

**High-Value Properties:**
```
P181  - taxon range map → SCIENTIFIC/ENVIRONMENTAL
P183  - endemic to → SCIENTIFIC/ENVIRONMENTAL
P225  - taxon name → SCIENTIFIC
P405  - taxon author → SCIENTIFIC/INTELLECTUAL
P566  - basionym → SCIENTIFIC
P784  - mushroom cap shape → SCIENTIFIC
P787  - spore print color → SCIENTIFIC
P830  - Encyclopedia of Life → SCIENTIFIC
```

**Domain Pack:** Natural History  
**Temporal Scope:** Geological time  
**Entity Focus:** Species, Habitat, Ecosystem, Specimen

**Use Case:** Biodiversity research, ecological history, taxonomy

---

### **Domain 5: Medical/Pharmaceutical (Future)**

**High-Value Properties:**
```
P231  - CAS Registry → SCIENTIFIC
P267  - ATC code → SCIENTIFIC
P486  - MeSH descriptor → SCIENTIFIC
P493  - ICD-9 → SCIENTIFIC
P494  - ICD-10 → SCIENTIFIC
P509  - cause of death → BIOGRAPHIC/SCIENTIFIC
P563  - ICD-O oncology → SCIENTIFIC
P592  - ChEMBL ID → SCIENTIFIC
P769  - drug interaction → SCIENTIFIC
```

**Domain Pack:** Medical Research  
**Temporal Scope:** 1600 - present  
**Entity Focus:** Disease, Drug, Treatment, Patient, Clinical Trial

**Use Case:** Medical history, pharmacology evolution, disease tracking

---

### **Domain 6: Cultural/Media Studies (Future)**

**High-Value Properties:**
```
P180  - depicts → ARTISTIC/CULTURAL
P57   - director → ARTISTIC
P58   - screenwriter → ARTISTIC/INTELLECTUAL
P86   - composer → ARTISTIC
P161  - cast member → ARTISTIC/BIOGRAPHIC
P480  - FilmAffinity → ARTISTIC
```

**Domain Pack:** Media Studies  
**Temporal Scope:** 1800 - present  
**Entity Focus:** Film, Music, Performance, Artist, Production

**Use Case:** Film history, music evolution, cultural production

---

## 🎯 Universal Core Properties (All Domains)

**These properties are useful REGARDLESS of domain:**

### Structural/Ontological (Always Useful)
```
P31   - instance of → Classification backbone
P279  - subclass of → Taxonomy backbone
P361  - part of → Hierarchical structure
P527  - has part → Hierarchical structure
```

### Temporal (Always Useful)
```
P580  - start time → Temporal bounds
P582  - end time → Temporal bounds
P585  - point in time → Temporal documentation
P571  - inception → Entity lifecycle
P576  - dissolved → Entity lifecycle
```

### Spatial (Always Useful)
```
P625  - coordinates → Geographic location
P17   - country → Political geography
P131  - administrative entity → Spatial hierarchy
P276  - location → Spatial context
```

### Provenance (Always Useful)
```
P248  - stated in → Source citation
P813  - retrieved → Data provenance
P854  - reference URL → Source tracking
```

---

## 📊 Domain Adaptability Matrix

| Property | History | Tech | Sports | Bio | Medical | Media |
|----------|---------|------|--------|-----|---------|-------|
| P19 (birth place) | ✅ High | ❌ Low | ⚠️ Med | ❌ Low | ❌ Low | ⚠️ Med |
| P569 (birth date) | ✅ High | ❌ Low | ⚠️ Med | ❌ Low | ❌ Low | ⚠️ Med |
| P241 (military) | ✅ High | ❌ Low | ❌ Low | ❌ Low | ❌ Low | ⚠️ Med |
| P348 (software) | ❌ Low | ✅ High | ❌ Low | ⚠️ Med | ⚠️ Med | ⚠️ Med |
| P536 (ATP ID) | ❌ Low | ❌ Low | ✅ High | ❌ Low | ❌ Low | ⚠️ Med |
| P784 (mushroom) | ❌ Low | ❌ Low | ❌ Low | ✅ High | ⚠️ Med | ❌ Low |
| P31 (instance) | ✅ High | ✅ High | ✅ High | ✅ High | ✅ High | ✅ High |
| P580 (start) | ✅ High | ✅ High | ✅ High | ⚠️ Med | ✅ High | ✅ High |

---

## 💡 The Key Insight

Instead of "non-useful," these are **domain-specific** properties:

- **History Domain:** Use properties like P241, P410, P607 (military), P39 (positions)
- **Tech Domain:** Use properties like P348, P408, P487 (software/encoding)
- **Sports Domain:** Use properties like P536, P597, P741 (player stats)
- **Bio Domain:** Use properties like P784, P787, P788 (species characteristics)

**All properties have utility - just in different domain contexts!**

---

## 🎯 Recommendations for Chrystallum

### For Current Implementation (History Domain)
1. **Filter by domain relevance** - Not "exclude," but "deprioritize"
2. **Create domain profiles**:
   ```json
   {
     "ancient_history": {
       "priority_properties": ["P19", "P20", "P39", "P241", "P569", "P570"],
       "exclude_properties": ["P348", "P404", "P536", "P784"]
     },
     "tech_history": {
       "priority_properties": ["P348", "P408", "P487", "P571", "P576"],
       "exclude_properties": ["P241", "P410", "P784"]
     }
   }
   ```

### For Future Domain Adaptation
3. **Keep all 500 property mappings** - Don't delete "non-historical" ones
4. **Add domain_relevance scores per domain**
5. **Swap domain profiles** when switching use cases

---

## 📋 Updated Property Tiers (History Domain)

**Tier 1 (Priority):** 50 properties - Core historical (birth, death, positions, military, temporal)  
**Tier 2 (Include):** 200 properties - Supporting historical (cultural, geographic, intellectual)  
**Tier 3 (Optional):** 230 properties - Specialized (scientific IDs, modern databases)  
**Tier 4 (Other Domain):** 20 properties - Tech/sports/modern (useful elsewhere)

**All tiers preserved** - just different scoring per domain!

---

**This is much better aligned with your universal architecture!** 🎯
