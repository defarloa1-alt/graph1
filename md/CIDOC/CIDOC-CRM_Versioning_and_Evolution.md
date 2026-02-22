# CIDOC-CRM Versioning and Evolution

## Is CIDOC-CRM Static or Evolving?

**Answer: CIDOC-CRM is an evolving standard, but with careful versioning and backward compatibility.**

---

## Version History

### ISO Standard Versions

| Version | Year | ISO Standard | Status |
|---------|------|--------------|--------|
| **7.1** | 2015 | ISO 21127:2014 | Current when ISO published |
| **8.0** | 2023 | ISO 21127:2023 | **Current ISO standard** |
| **7.1** | Ongoing | Pre-ISO | Community version (continues) |

### Current Status

- ✅ **ISO 21127:2023** = Official international standard (CIDOC-CRM version 8.0)
- ✅ **Community versions** continue (7.1.2, 8.x, etc.)
- ✅ **Active development** and maintenance

---

## How CIDOC-CRM Evolves

### 1. **Regular Updates**

**Development Model:**
- **CIDOC Documentation Working Group** maintains the standard
- **Regular releases** with new versions
- **Community input** and scholarly review
- **ISO standardization** for major versions

**Release Cycle:**
- Community versions: More frequent (as needed)
- ISO versions: Every ~5-10 years (major revisions)

### 2. **Extension Mechanism**

**CIDOC-CRM Extensions:**
- ✅ **Official extensions**: CRMgeo, CRMinf, CRMsci, CRMarchaeo
- ✅ **Community extensions**: Domain-specific additions
- ✅ **Compatible additions**: Can extend without breaking core

**Examples:**
- **CRMgeo**: Geographic extensions
- **CRMinf**: Inference and reasoning
- **CRMsci**: Scientific observation
- **CRMarchaeo**: Archaeological extensions

### 3. **Backward Compatibility**

**CIDOC-CRM Philosophy:**
- ✅ **Backward compatible** across versions
- ✅ **Additive changes** (new classes/properties)
- ✅ **Deprecation** rather than removal
- ✅ **Migration guides** between versions

**Example Changes:**
- Version 7.1 → 8.0: Added new classes, refined properties
- Old data remains valid
- New features available but not required

---

## What Changed Between Versions

### Version 7.1 → 8.0 (Major Update, ISO 21127:2023)

**Key Changes:**
1. **New Classes**: Additional entity classes for better modeling
2. **Property Refinements**: More precise property definitions
3. **Documentation**: Improved documentation and examples
4. **Clarifications**: Better definition of existing concepts

**Impact:**
- ✅ Existing 7.1 data still valid
- ✅ Can adopt 8.0 features incrementally
- ✅ Migration path available

### Community Development

**Ongoing Development:**
- Bug fixes
- Clarifications
- New extensions
- Best practices

**Examples:**
- CRMgeo extension (geographic data)
- CRMinf extension (inference)
- Domain-specific extensions

---

## Implications for Chrystallum

### ✅ Safe to Build On

**Why CIDOC-CRM is Reliable:**

1. **Stable Core**
   - Core classes (E5_Event, E21_Person, E53_Place) are stable
   - Fundamental concepts don't change
   - Event-centric model is established

2. **Backward Compatibility**
   - Data remains valid across versions
   - Migration is possible but not required
   - No breaking changes

3. **Extension-Friendly**
   - Designed for extensions
   - Our additions (FAST, action structure) are compatible
   - Official extensions show the pattern

4. **ISO Standardization**
   - ISO 21127:2023 is official international standard
   - Not going away
   - Long-term stability

---

## How to Handle CIDOC-CRM Evolution

### Strategy 1: Pin to ISO Version (Recommended for Stability)

**Approach:**
- Use **ISO 21127:2023** (CIDOC-CRM 8.0)
- Don't update until next ISO version
- Stable for production use

**Pros:**
- ✅ Maximum stability
- ✅ International standard
- ✅ Long-term support

**Cons:**
- ⚠️ Miss community improvements
- ⚠️ Less frequent updates

---

### Strategy 2: Track Community Versions (Recommended for Innovation)

**Approach:**
- Follow **CIDOC-CRM community versions**
- Adopt improvements as they emerge
- Migrate when stable

**Pros:**
- ✅ Latest features
- ✅ Bug fixes
- ✅ Best practices

**Cons:**
- ⚠️ More maintenance
- ⚠️ Need migration planning

---

### Strategy 3: Hybrid (Recommended for Chrystallum)

**Approach:**
- **Core**: Use ISO 21127:2023 stable classes/properties
- **Extensions**: Monitor CIDOC-CRM extensions
- **Chrystallum**: Add our unique features as extensions

**Implementation:**
```cypher
// Stable CIDOC-CRM core (ISO 21127:2023)
(event: E5_Event) -[:P4_has_time-span]-> (timeSpan: E52_Time-Span)

// CIDOC-CRM extensions (when stable)
// Use CRMgeo for geographic data if needed

// Chrystallum extensions (our additions)
(event: E5_Event {
  cidoc_crm_version: '8.0',  // Track version
  iso_standard: 'ISO 21127:2023',
  
  // Stable core
  cidoc_crm_class: 'E5_Event',
  
  // Chrystallum extensions
  backbone_fast: 'fst01411640',
  action_type: 'MIL_ACT'
})
```

---

## Version Tracking in Chrystallum

### Recommended Approach

**Add Version Metadata:**

```cypher
// Entity with version tracking
(event: E5_Event {
  // CIDOC-CRM version info
  cidoc_crm_version: '8.0',
  iso_standard: 'ISO 21127:2023',
  cidoc_crm_class: 'E5_Event',
  
  // Chrystallum version info
  chrystallum_schema_version: '3.2',
  
  // Data
  label: 'Crossing of Rubicon',
  start_date: '-0049-01-10'
})
```

**Benefits:**
- ✅ Know which CIDOC-CRM version used
- ✅ Can migrate when needed
- ✅ Maintain compatibility

---

## Migration Strategy

### When CIDOC-CRM Updates

**Scenario: CIDOC-CRM 8.0 → 9.0 (Future)**

**Steps:**

1. **Review Changes**
   - What's new?
   - What's deprecated?
   - Migration guide?

2. **Test Migration**
   - Test on sample data
   - Verify compatibility
   - Check Chrystallum extensions

3. **Plan Migration**
   - Decide if/when to migrate
   - Update version metadata
   - Migrate data if needed

4. **Maintain Compatibility**
   - Keep supporting old version
   - Gradual migration
   - No breaking changes to Chrystallum

---

## Extensions vs. Core

### Core (Stable, Rarely Changes)

**CIDOC-CRM Core Classes:**
- E5_Event
- E21_Person
- E53_Place
- E52_Time-Span
- P4_has_time-span
- P7_took_place_at
- P11_had_participant

**These are stable** - fundamental concepts

---

### Extensions (More Dynamic)

**CIDOC-CRM Extensions:**
- CRMgeo (geographic)
- CRMinf (inference)
- CRMsci (scientific)
- CRMarchaeo (archaeological)

**These evolve** - domain-specific additions

---

### Chrystallum Extensions (Our Control)

**Our Extensions:**
- FAST/LCC/LCSH/MARC properties
- Action structure vocabularies
- Systematic ISO 8601 dates
- Wikidata alignment

**We control these** - not dependent on CIDOC-CRM changes

---

## Best Practices

### ✅ Do

1. **Use ISO Standard**
   - ISO 21127:2023 (CIDOC-CRM 8.0)
   - Stable, official standard

2. **Version Your Data**
   - Track CIDOC-CRM version used
   - Track Chrystallum schema version

3. **Design for Extensions**
   - Keep core and extensions separate
   - Make Chrystallum features independent

4. **Monitor Updates**
   - Watch for new CIDOC-CRM versions
   - Evaluate benefits vs. migration cost

### ❌ Don't

1. **Don't Assume Static**
   - CIDOC-CRM does evolve
   - Plan for version updates

2. **Don't Mix Versions**
   - Use consistent CIDOC-CRM version
   - Don't mix 7.1 and 8.0 in same dataset

3. **Don't Break Compatibility**
   - Keep Chrystallum extensions compatible
   - Don't break existing queries

---

## Summary

### Is CIDOC-CRM Static or Current?

**Answer: Both - it's a stable core with evolving extensions**

**Core (Stable):**
- ✅ ISO 21127:2023 standard
- ✅ Core classes/properties don't change
- ✅ Backward compatible

**Extensions (Evolving):**
- ✅ Community extensions develop
- ✅ Domain-specific additions
- ✅ Best practices improve

**For Chrystallum:**
- ✅ **Safe to build on** - core is stable
- ✅ **Version tracking** - know what we're using
- ✅ **Extension strategy** - our features are independent
- ✅ **Migration planning** - can update when needed

**Recommendation:**
- Use **ISO 21127:2023 (CIDOC-CRM 8.0)** as foundation
- Track version in metadata
- Design Chrystallum extensions to be version-independent
- Monitor CIDOC-CRM updates but don't need to follow every change

**Bottom Line:** CIDOC-CRM is **stable enough to build on** but **evolving enough to stay relevant**. Perfect foundation for Chrystallum!



