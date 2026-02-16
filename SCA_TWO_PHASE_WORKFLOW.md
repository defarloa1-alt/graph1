# SCA Two-Phase Workflow - Quick Summary

**Date:** February 15, 2026  
**Context:** Clarification on SCA un-faceted exploration vs facet-by-facet analysis

---

## The Key Insight

The **SubjectConceptAgent (SCA)** operates in **TWO DISTINCT PHASES**:

1. **Phase 1: Un-Faceted Exploration** - Just hunting nodes and edges (NO facet lens)
2. **APPROVAL POINT** - Human reviews proposed ontology
3. **Phase 2: Facet-by-Facet Analysis** - Sequential facet roles (military → political → cultural → etc.)

---

## Phase 1: Un-Faceted Exploration

**What SCA Does:**
- Starts with anchor QID (e.g., Q17167 "Roman Republic")
- **NO facet lens at this point** - pure structural discovery
- Follows P31/P279/P361 hierarchies + backlinks
- Creates shell nodes for ALL discovered concepts
- Goes well beyond initial domain (breadth over depth)

**What SCA Outputs:**
```json
{
  "discovered_nodes": ["Q17167", "Q191172", "Q172645", "Q189108", "Q191989", ...],
  "discovered_edges": [
    {"from": "Q17167", "to": "Q191172", "via": "P31"},
    {"from": "Q172645", "to": "Q189108", "via": "backlink"},
    {"from": "Q189108", "to": "Q191989", "via": "backlink"}
  ],
  "shell_nodes": 15,
  "strength_score": 0.88
}
```

**Key Point:** At this stage, NO FACETS are assigned. These are just discovered entities and relationships.

---

## Approval Point

**Human reviews proposed ontology:**
- ✅ Are discovered nodes relevant?
- ✅ Is breadth exploration appropriate?
- ✅ Are cross-domain connections valid (purple → mollusk)?
- ✅ Is strength score acceptable?

**Decision:**
- ✅ **APPROVE** → Proceed to Phase 2
- ❌ **REJECT** → Adjust parameters and re-run Phase 1
- 📝 **MODIFY** → Edit nodes/edges, then approve

---

## Phase 2: Facet-by-Facet Analysis

**What SCA Does:**
- **Adopts facet roles sequentially** (one at a time)
- Reads the SAME discovered claims from different facet perspectives
- Generates facet-specific insights for each node

**Sequential Workflow:**
```python
approved_ontology = {...}  # From Phase 1

# Step 1: Military perspective
sca.adopt_facet_role('military')
military_claims = sca.analyze_from_facet_perspective(approved_ontology, 'military')

# Step 2: Political perspective
sca.adopt_facet_role('political')
political_claims = sca.analyze_from_facet_perspective(approved_ontology, 'political')

# Step 3: Cultural perspective
sca.adopt_facet_role('cultural')
cultural_claims = sca.analyze_from_facet_perspective(approved_ontology, 'cultural')

# Step 4: Economic perspective
sca.adopt_facet_role('economic')
economic_claims = sca.analyze_from_facet_perspective(approved_ontology, 'economic')

# Step 5: Scientific perspective
sca.adopt_facet_role('scientific')
scientific_claims = sca.analyze_from_facet_perspective(approved_ontology, 'scientific')

# Result: 5x claims from same ontology!
```

**Example: Q189108 (Tyrian purple) analyzed from 5 facets:**

| Facet | Claim | Confidence |
|-------|-------|------------|
| Military | "Tyrian purple used for military commander insignia" | 0.85 |
| Political | "Tyrian purple indicated senatorial rank" | 0.92 |
| Economic | "Tyrian purple high-value trade commodity" | 0.88 |
| Scientific | "Tyrian purple extracted from murex snail" | 0.95 |
| Cultural | "Tyrian purple symbolized prestige" | 0.90 |

**Key Point:** Same node (Tyrian purple), analyzed from 5 different facet perspectives = 5 different claims!

---

## Purple to Mollusk Example

**Phase 1: Un-Faceted Discovery**
```
Q17167 (Roman Republic) [anchor]
  ↓ P31 traversal
Q191172 (Roman senator) [shell node]
  ↓ backlink
Q172645 (toga) [shell node]
  ↓ P31 traversal
Q189108 (Tyrian purple) [shell node]
  ↓ backlink
Q191989 (murex) [shell node] ⭐

NO FACETS ASSIGNED YET
```

**Approval Point**
```
Human reviews:
- 15 nodes discovered
- Purple → mollusk path validated
- Strength score: 0.88

Decision: ✅ APPROVED
```

**Phase 2: Facet-by-Facet Analysis**
```
Q191989 (murex) analyzed from:
- Military facet: "Dye for military insignia"
- Political facet: "Source of senatorial purple"
- Economic facet: "High-value trade commodity"
- Scientific facet: "Murex brandaris biology"
- Cultural facet: "Symbol of prestige"

RESULT: 5 claims about murex from different perspectives
```

---

## Why This Matters

### Phase 1 Benefits (Un-Faceted)
- **Unbiased discovery:** No facet bias limits exploration
- **Breadth coverage:** Discovers all related concepts
- **Cross-domain bridges:** Finds unexpected connections (purple → mollusk)
- **Efficient structure:** Creates shell nodes (low cost)

### Approval Point Benefits
- **Quality control:** Human validates discovery quality
- **Scope adjustment:** Can modify before expensive facet analysis
- **Resource planning:** Decide which facets to apply

### Phase 2 Benefits (Facet-by-Facet)
- **Claim richness:** 5x more claims from same data
- **Multi-perspective:** Same entity analyzed from different angles
- **No interference:** Each facet gets clean read
- **Comprehensive:** Ensures all facet-relevant insights extracted

---

## Implementation Notes

### Current Status
- ✅ Phase 1 implemented (Initialize + Ontology Proposal)
- ⏸️ Approval Point (manual workflow)
- ⏸️ Phase 2 design (Training Mode needs facet-switching logic)
- ⚠️ **DECISION POINT: Real vs Simulated SFAs**
  * Current: Simulated agents (hard-coded responses)
  * Option A: Spawn real FacetAgents (~2 hours effort)
  * Option B: Keep simulated for smoke test only
  * See: [REAL_VS_SIMULATED_SFA_ANALYSIS.md](REAL_VS_SIMULATED_SFA_ANALYSIS.md)

### Next Steps
1. **DECIDE:** Real vs simulated agent spawning
2. Add approval workflow to Gradio UI
3. Implement facet-switching in Training Mode (if using real agents)
4. Test sequential facet analysis
5. Validate claim richness (5x multiplier)

---

## See Also

- [SCA_SEED_AGENT_PATTERN.md](SCA_SEED_AGENT_PATTERN.md) - Complete SCA pattern documentation
- [STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md](STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md) - Phase 1 implementation
- [STEP_5_COMPLETE.md](STEP_5_COMPLETE.md) - Training Mode (Phase 2 framework)
- [STEP_6_DESIGN_WIKIPEDIA_TRAINING.md](STEP_6_DESIGN_WIKIPEDIA_TRAINING.md) - Wikipedia training integration

---

**Status:** ✅ Documentation updated to reflect two-phase workflow with approval point.
