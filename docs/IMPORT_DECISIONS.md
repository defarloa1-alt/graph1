# Import Design Decisions

**Purpose:** Document architectural choices for federation and external data imports so they are not relitigated later.

---

## DPRR Assertion Reification (2026-02-25)

### The Choice

**Option A — Edge with provenance properties:**
```
(Caesar)-[:FATHER_OF {
  source: "dprr",
  dprr_assertion_uri: "http://romanrepublic.ac.uk/rdf/entity/RelationshipAssertion/1234",
  secondary_source: "Zmeskal_Adfinitas",
  confidence: 0.85,
  scoping_status: "temporal_scoped"
}]->(Octavian)
```

**Option B — Claim node reification:**
```
(:Claim { type: "FATHER_OF", dprr_assertion_uri: "...", secondary_source: "Zmeskal" })
  -[:ABOUT]->(Caesar)
  -[:ABOUT]->(Octavian)
```

### Decision: Option A for DPRR

DPRR is a secondary source layer — it does not itself contain contested claims between sources. Every assertion in DPRR comes from one secondary source (Broughton, Zmeskal, Rüpke) with one confidence level. The complexity of Option B is not justified by the data structure. Edge provenance properties carry everything needed.

### Upgrade Path

When the SFA layer generates claims that **contest** DPRR assertions — e.g. "Livy suggests a different paternity than Zmeskal records" — those contested claims use Option B reification. The DPRR layer stays as Option A. The two coexist: DPRR edges carry provenance on the edge; contested SFA claims attach via Claim nodes.

### Implementation

- DPRR PostAssertions → `POSITION_HELD` edges with `dprr_assertion_uri`, `secondary_source`, `year`
- DPRR RelationshipAssertions → familial edges (`FATHER_OF`, `MOTHER_OF`, `SIBLING_OF`, `SPOUSE_OF`, etc.) with same provenance pattern
- DPRR StatusAssertions → status edges with provenance
- Bibliography nodes (`DPRR`, `Broughton_MRR`, `Zmeskal_Adfinitas`) exist in graph; provenance properties reference them

---

*Last updated: 2026-02-25*
