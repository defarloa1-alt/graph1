# Knowledge Graph Architecture — Complete Documentation

## What This Is

Complete documentation for your **6-layer knowledge graph architecture** that integrates:
- **200+ canonical relationship types** (your CSV)
- **CIDOC-CRM** (formal ontology)
- **Wikidata** (linked data authority)
- **LCSH/FAST** (subject classification + 15 facets)
- **Neo4j** (graph database)
- **MINF** (inference model with evidence tracking)

This creates an **evidence-aware, uncertainty-quantified, semantically rich** knowledge graph for historical data.

---

## Files You Now Have

### Core Documentation (5 files)

1. **QUICK-START.md** ← **START HERE**
   - 30 minutes to working graph
   - 3 Cypher blocks to copy-paste
   - Get running immediately

2. **CONCEPTUAL_MODEL.md**
   - 10 Mermaid diagrams
   - Visual architecture
   - Copy into Obsidian

3. **EXAMPLES-complete.md**
   - 5 complete worked examples
   - Full Cypher code
   - Copy-paste template

4. **CHEATSHEET.md**
   - Quick reference (print this!)
   - All 6 layers explained
   - Decision matrix

5. **VISUAL_INDEX.md**
   - Navigation guide
   - Reading order suggestions
   - Topic index

### Supporting Files (Already Have)

- **NODE_TYPE_SCHEMAS-1.md** [file:362] — Entity schemas
- **canonical_relationship_types.csv** [file:367] — Your 200+ types

---

## The 6-Layer Model (Simple Version)

```
Layer 1: CSV of 200+ relationship types (your vocabulary)
    ↓
Layer 2: CIDOC-CRM (formal structure: E5=Event, E21=Person, E53=Place)
    ↓
Layer 3: Wikidata (authority: QIDs + properties)
    ↓
Layer 4: LCSH/FAST + 15 Facets (subject classification)
    ↓
Layer 5: Neo4j (actual graph nodes and relationships)
    ↓
Layer 6: MINF (reasoning: evidence, confidence, belief revision)

Result: Evidence-aware knowledge graph with tracked confidence
```

---

## Key Innovation: Belief Nodes

**Traditional approach (simple edge):**
```
Battle -[:FOUGHT_IN]-> Thessaly
```
*Problem: Can't attach evidence, confidence, or caveats*

**Your approach (reified with MINF):**
```
Battle -[:CRM_BELIEF_OBJECT]-> Belief {
  statement: "Battle fought in Thessaly"
  confidence: 0.85
  sources: [Citation: "Livy 3.10"]
  caveats: [Note: "Some scholars dispute"]
} -[:CRM_BELIEF_OBJECT]-> Thessaly
```
*Solution: Belief node holds evidence, confidence, and uncertainty*

---

## Quick Start (30 Minutes)

### 1. Understand (10 min)
Open **CONCEPTUAL_MODEL.md**, look at Diagram 1

### 2. See Example (10 min)
Open **EXAMPLES-complete.md**, read Example 1

### 3. Run Code (10 min)
Copy 3 Cypher blocks from **QUICK-START.md**, paste into Neo4j

**Done!** You have a working 6-layer graph.

---

## The Three Types of Relationships

### 1. CRM Relationships (Formal Structure)
```cypher
:Event -[:CRM_TOOK_PLACE_AT]-> :Place
:Person -[:CRM_PARTICIPATED_IN]-> :Event
```
Direct edges for formal ontology.

### 2. Belief/MINF Relationships (Evidence Structure)
```cypher
:Event -[:CRM_BELIEF_OBJECT]-> :Belief -[:CRM_HAS_SOURCE]-> :Citation
:Belief -[:MINF_HAS_NOTE]-> :Note
```
Reified relationships with evidence and confidence.

### 3. Classification Relationships
```cypher
:Event -[:HAS_SUBJECT]-> :Subject
:Subject -[:HAS_MILITARY_FACET]-> :MilitaryFacet
```
Subject classification for agent routing.

---

## The 6 Query Sophistication Levels

| Level | What You Get | Use Case |
|-------|--------------|----------|
| 1. Simple edge | Basic facts | Casual browsing |
| 2. + Confidence | High-confidence only | Quick research |
| 3. + Evidence | Facts + sources | Verification |
| 4. + Caveats | Facts + warnings | Understanding disputes |
| 5. By type | All instances of relationship type | Comprehensive analysis |
| 6. Belief revision | How thinking evolved | Historical understanding |

See **EXAMPLES-complete.md** for actual queries.

---

## How to Use These Files

### First Day (30 minutes)
1. Read **QUICK-START.md**
2. Look at **Diagram 1** in CONCEPTUAL_MODEL.md
3. Run the 3 Cypher blocks

### First Week (3 hours)
1. **Print CHEATSHEET.md** (keep at desk)
2. Study all 10 diagrams in **CONCEPTUAL_MODEL.md**
3. Work through **Example 1** in EXAMPLES-complete.md
4. Build your own entity using template (Example 5)

### Ongoing Reference
- **CHEATSHEET.md** — Quick lookup (printed)
- **VISUAL_INDEX.md** — Find what you need
- **EXAMPLES-complete.md** — Copy code patterns
- **Diagram 5** — Before writing new queries

---

## File Organization for Obsidian

```
Knowledge Graph/
├─ README.md (this file)
├─ QUICK-START.md ← START HERE
├─ VISUAL_INDEX.md (navigation)
├─ CHEATSHEET.md (print this)
├─ CONCEPTUAL_MODEL.md (10 diagrams)
├─ EXAMPLES-complete.md (5 examples)
│
├─ Reference/
│  ├─ NODE_TYPE_SCHEMAS-1.md
│  └─ canonical_relationship_types.csv
│
└─ My Entities/
   ├─ Battle of Pharsalus.md
   ├─ Roman Republic.md
   └─ [Your entities here]
```

---

## The 15 Facets (Semantic Dimensions)

Your entities can be classified via 15 facet dimensions:

1. **PoliticalFacet** — Government, regimes, dynasties
2. **MilitaryFacet** — Warfare, conquest, battles
3. **EconomicFacet** — Trade, finance, taxation
4. **SocialFacet** — Class structure, social movements
5. **CulturalFacet** — Arts, identity, practices
6. **ReligiousFacet** — Beliefs, institutions, movements
7. **TechnologicalFacet** — Tools, techniques, innovations
8. **ScientificFacet** — Scientific paradigms, discoveries
9. **ArtisticFacet** — Art movements, styles
10. **IntellectualFacet** — Philosophy, schools of thought
11. **LinguisticFacet** — Languages, scripts, communication
12. **DiplomaticFacet** — Treaties, alliances, international systems
13. **EnvironmentalFacet** — Climate, ecology
14. **DemographicFacet** — Population, migration
15. **ArchaeologicalFacet** — Material culture, periods

Facets enable **agent routing** — military historians query MilitaryFacet, political scientists query PoliticalFacet, etc.

---

## MINF Properties (I1-I8)

| Code | Property | Purpose | Example |
|------|----------|---------|---------|
| I1 | INFERRED_FROM | Link to evidence | Belief ← Citation |
| I2 | BELIEF_LEVEL | Subjective assessment | "probable" |
| I3 | HAS_NOTE | Caveat/explanation | Note about dispute |
| I4 | HAS_UNCERTAINTY | Quantified confidence | 0.85 |
| I7 | HAS_OBJECT | Old belief (revision) | Superseded belief |
| I8 | HAS_RESULT | New belief (revision) | Current belief |

See **Diagram 8** in CONCEPTUAL_MODEL.md for details.

---

## Success Criteria

You'll know this is working when you can:

✓ Explain the 6 layers without looking  
✓ Map relationship types to CIDOC-CRM properties  
✓ Create Belief nodes with confidence + evidence  
✓ Write queries at all 6 sophistication levels  
✓ Route entities to agents via facets  
✓ Track belief revisions (old → new)  

---

## Common Questions

**Q: Do I need all 6 layers?**  
A: Start simple (Layer 5 only). Add evidence (Layer 6) when you need confidence tracking.

**Q: Can I use this for non-historical data?**  
A: Yes! The architecture works for any domain needing evidence tracking.

**Q: What if I don't have Wikidata QIDs?**  
A: Create your own identifiers. Wikidata is recommended but not required.

**Q: Do I need to use CIDOC-CRM?**  
A: It's best practice for cultural heritage, but you can simplify. Keep E5, E21, E53 at minimum.

**Q: How do I track sources?**  
A: Create Citation nodes, link via `[:CRM_HAS_SOURCE]`.

**Q: How do I handle uncertainty?**  
A: Use `confidence` property (0.0-1.0) and `[:MINF_HAS_NOTE]` for caveats.

---

## What Makes This Different

Traditional knowledge graphs:
- Simple edges (`A -[:RELATED]-> B`)
- No confidence tracking
- No evidence linking
- No belief revision

Your 6-layer graph:
- ✓ Reified relationships (Belief nodes)
- ✓ Confidence quantified (0.0-1.0)
- ✓ Evidence linked (Citation nodes)
- ✓ Caveats recorded (Note nodes)
- ✓ Belief changes tracked (MINF_REPLACED_BY)
- ✓ Agent routing (15 semantic facets)
- ✓ Formal ontology (CIDOC-CRM + MINF)

This is **epistemically aware** knowledge representation.

---

## Next Steps

1. **Read QUICK-START.md** (5 min)
2. **Run the 3 Cypher blocks** (10 min)
3. **Print CHEATSHEET.md** (keep at desk)
4. **Build your first entity** using template in EXAMPLES-complete.md (30 min)

---

## File Reference Table

| File | Lines | Purpose | Read Time |
|------|-------|---------|-----------|
| QUICK-START.md | ~180 | Get running fast | 5 min |
| CONCEPTUAL_MODEL.md | ~600 | Visual architecture | 30 min |
| EXAMPLES-complete.md | ~600 | Working code | 60 min |
| CHEATSHEET.md | ~400 | Quick reference | 10 min |
| VISUAL_INDEX.md | ~300 | Navigation | 5 min |
| README.md | ~300 | This overview | 10 min |

**Total**: ~2400 lines, ~2 hours reading, lifetime of reference

---

## Key Insight

> "Every claim in your knowledge graph should be able to answer:  
> **What do we believe? How confident are we? What's the evidence? What are the caveats?**"

That's what this architecture delivers.

---

**Version**: 1.0  
**Created**: January 14, 2026  
**Status**: Ready to use  

**Next**: Open QUICK-START.md and get running in 30 minutes.
