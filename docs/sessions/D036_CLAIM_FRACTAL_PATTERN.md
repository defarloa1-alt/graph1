# D-036 — Claim as Fractal Pattern with Emergent Structure
## Formal Mathematical Grounding and SysML Expression

**Decision ID:** D-036
**Date:** 2026-02-25
**Category:** Architecture — Claim Data Model / Theoretical Foundation
**Status:** Approved — model update required, implementation deferred to post-prototype
**Depends on:** D-033 (claim lifecycle), D-035 (subcluster structure), D-019 (subclaim propagation)
**Origin:** Multi-agent design thread, 2026-02-25

---

## Part 1 — Core Decision (Original)

Claims are fractal patterns. Every claim is simultaneously a node
(addressable, citable, disputable) and a subgraph (an argument with
internal structure). The same structural properties repeat at every
scale from atomic subclaim to MultiDimensionalClaim.

Three frameworks describe the same phenomenon at different levels:

```
Fractal theory    — describes the STRUCTURE (self-similar, scale-invariant)
Game of Life      — describes the DYNAMICS (local rules, emergent patterns)
Claim architecture — is the IMPLEMENTATION
```

---

## Part 2 — Formal Mathematical Grounding

The following formalism (derived from a governed Bayesian claim-update
framework) provides precise grounding for the architecture.

### Notation Mapping

```
FORMAL          CHRYSTALLUM
───────────────────────────────────────────────────────────
G = (V, E)      Neo4j graph (full knowledge graph)
c ∈ V           Claim node
U_c ⊆ V         Node set defining the subcluster
H_c = G[U_c]    Subcluster (induced subgraph on U_c)
Γ               Governance rules (D10/D11 + Fischer checks)
H̃_c            Proposed new version of subcluster
E = H̃_c \ H_c  Evidence delta — what is new in the proposal
H ⊨ Γ          Subcluster satisfies all governance rules
U_Γ(H_c, H̃_c) Governed update function (four cipher states)
P_t(c)          Claim credence (confidence score) at time t
P_t(E|c)        Likelihood: probability of seeing E if c is true
P_t(E)          Marginal: probability of seeing E regardless of c
```

### The Governed Bayesian Update

```
IF E is admissible (H̃_c ⊨ Γ):
  P_t+1(c) = P_t(E|c) · P_t(c) / P_t(E)

IF E is not admissible (H̃_c ⊭ Γ):
  P_t+1(c) = P_t(c)          [no change]
  H_c' = H_c                  [no change]
```

### Mapping to Four Cipher States

```
State 1: cipher match, same source
  → E is empty (same evidence already present)
  → no-op. P_t+1(c) = P_t(c)

State 2: cipher match, different source
  → E = new source provenance node + edge
  → E is admissible (provenance satisfies Γ)
  → Bayesian update applies
  → P_t+1(c) = P_t(E|c) · P_t(c) / P_t(E)
  → NOTE: P_t(E) varies with source independence (see below)

State 3: no cipher match, nodes exist
  → E = new claim node + relationships
  → governance check runs
  → if H̃_c ⊨ Γ: new claim enters lifecycle, credence initialised
  → if H̃_c ⊭ Γ: rejected, no change

State 4: no cipher match, nodes missing
  → SCA creates missing nodes (mid/leaf level only)
  → then follows State 3 path
```

### H_c as Traversal Pattern (Not Stored Induced Subgraph)

H_c is operationally defined by a traversal pattern, not stored as
a literal induced subgraph. In Neo4j, U_c is defined by:

```cypher
MATCH (c:Claim)-[:ABOUT|ASSERTS|SOURCED_FROM|FLAGGED_BY|
                   SUBCLAIM_OF*1..3]-(related)
WHERE c.cipher = $cipher
RETURN c, related
```

The traversal pattern is a :TraversalPattern node in the SYS_
metanode schema. The SCA holds the reference to this pattern —
it does not store the subcluster itself.

### Γ as Executable Cypher

H ⊨ Γ does not mean "passes a human review step."
It means "all governance Cypher queries return zero rows."

Each governance rule is a :GovernanceRule node with:
  - cypher_check: the validation query
  - severity: block | warn
  - remediation: suggested fix

Example governance rules as Cypher:

```cypher
-- Rule: every Claim must have at least one source
MATCH (c:Claim)
WHERE NOT (c)-[:SOURCED_FROM]->(:Source)
RETURN c.cipher AS violation, 'missing_source' AS reason

-- Rule: every Source must have independence_score
MATCH (s:Source)
WHERE s.independence_score IS NULL
RETURN s.id AS violation, 'missing_independence_score' AS reason

-- Rule: no Claim may have confidence > 0.9 with fractal_dimension > 5
--       without at least 3 independent sources
MATCH (c:Claim)
WHERE c.confidence > 0.9
  AND c.fractal_dimension > 5
  AND size([(c)-[:SOURCED_FROM]->(s:Source) WHERE s.independence_score > 0.7 | s]) < 3
RETURN c.cipher AS violation, 'insufficient_independent_sources' AS reason
```

SFA runs all governance queries before GPS writes.
H ⊨ Γ iff all return zero rows.

---

## Part 3 — Source Independence and the Marginal P_t(E)

### The Problem with Flat State 2

Current architecture treats all State 2 events equally:
  same cipher, different source → confidence bumps by fixed amount

This is incorrect. Two studies from the same lab should produce
a smaller confidence bump than two studies from independent labs.

The Bayesian formalism explains why:

```
P_t+1(c) = P_t(E|c) · P_t(c) / P_t(E)

Dependent source:
  P_t(E) is high — you'd expect to see similar evidence from
  the same research group regardless of whether c is true
  → smaller update

Independent source:
  P_t(E) is lower — seeing the same conclusion from an
  independent source is more surprising if c were false
  → larger update
```

### Source Independence as a Property

```
Source node — new properties:
  independence_score: Real [0..1]
    1.0 = fully independent (different institution, era, methodology)
    0.0 = fully dependent (same author, same dataset)
  
  viaf_id: String         ← resolves via Phase 3 VIAF integration
  lcnaf_id: String        ← resolves via Phase 3 LCNAF integration
  institution_id: String  ← for independence computation
  publication_date: Date  ← temporal independence factor
```

### Independence Score Computation

```
independence_score = f(
  author_overlap,       ← VIAF/LCNAF identity resolution
  institution_overlap,  ← same lab, department, funder
  dataset_overlap,      ← same underlying data
  temporal_distance,    ← years between publications
  methodology_distance  ← qualitative vs quantitative, etc.
)
```

This is why Phase 3 Library Authority Integration has sharper
justification than previously stated. VIAF and LCNAF are not just
for display — they are the infrastructure for computing source
independence, which determines the magnitude of Bayesian updates.

### Updated State 2 Formula

```
confidence_bump = P_t(E|c) · P_t(c) / P_t(E)

where P_t(E) = f(source.independence_score)
  high independence → lower P_t(E) → larger bump
  low independence  → higher P_t(E) → smaller bump

SYS_Threshold: independence_weight_factor — controls the scaling
```

---

## Part 4 — Likelihood Model P_t(E|c)

### The Problem with Uniform Confidence Propagation

Current D-019 spec says causal subclaims carry more weight than
factual subclaims. The Bayesian formalism names what this weight is:
it is the likelihood P_t(E|c).

```
C3: Fugitive Slave Act was part of Compromise of 1850
  P_t(E|c) is LOW — this evidence would exist regardless of whether
  the parent claim (political identity formation) is true.
  It is support structure, not discriminating evidence.

C4: refusal caused meaning formation (causal claim)
  P_t(E|c) is HIGH — this evidence would only tend to appear
  if the causal claim is actually true. It is discriminating.
```

### Likelihood by Subclaim Type

```
subclaim_type: factual
  likelihood_weight: low (0.2–0.4)
  rationale: factual subclaims are necessary but not sufficient
             they would be present in many claim contexts

subclaim_type: causal
  likelihood_weight: high (0.6–0.9)
  rationale: causal subclaims are discriminating — they are
             more likely under the claim than under its negation

subclaim_type: contextual
  likelihood_weight: medium (0.3–0.6)
  rationale: context constrains the claim but does not confirm it
```

These weights are the formal grounding for D-019 DMN table.

---

## Part 5 — SysML Expression of the Formalism

### What Can Be Expressed in the Model

The formalism is precise enough to express directly in SysML as
typed constraints and value properties. Not as commentary —
as formal model elements.

**Claim block — value properties and constraints:**

```
Block: Claim
  value properties:
    credence:          Real [0.0..1.0]   ← P_t(c)
    likelihood:        Real [0.0..1.0]   ← P_t(E|c)
    marginal:          Real [0.0..1.0]   ← P_t(E)
    fractal_dimension: Real
    boundary_status:   BoundaryStatus    ← {interior, boundary, frontier}
    life_pattern:      LifePattern       ← {still_life, glider, oscillator, frontier}
    corroboration_count: Integer
    dispute_count:     Integer
    subclaim_depth:    Integer

  constraints:
    {credence_update_accepted}
      context: evidence delta E is admissible (H̃_c ⊨ Γ)
      body: credence_new = (likelihood * credence_old) / marginal

    {credence_update_rejected}
      context: evidence delta E is not admissible (H̃_c ⊭ Γ)
      body: credence_new = credence_old

    {life_pattern_derivation}
      still_life:  credence > promotion_threshold
                   AND corroboration_count >= 2
                   AND dispute_count = 0
      glider:      subject_concept_count > 1
      oscillator:  dispute_count > oscillation_limit
      frontier:    corroboration_count = 0

    {fractal_dimension_computation}
      fractal_dimension = subclaim_depth * subclaim_branching_factor
```

**ClaimLifecycleService block — governance as typed operation:**

```
Block: ClaimLifecycleService
  operations:
    governanceCheck(H_proposed: ClaimSubgraph): Boolean
      precondition:  H_proposed is well-formed claim subgraph
      postcondition: returns true iff H_proposed ⊨ Γ
      body: executes all :GovernanceRule Cypher checks
            returns true iff all return zero rows

    computeCredenceUpdate(
      c: Claim,
      delta: EvidenceDelta,
      source: Source
    ): Real
      body: if delta.admissible
              return (c.likelihood * c.credence) / c.marginal
            else
              return c.credence
```

**Source block — independence as typed property:**

```
Block: Source
  value properties:
    independence_score: Real [0.0..1.0]
    viaf_id:   String
    lcnaf_id:  String

  constraints:
    {independence_affects_marginal}
      marginal = f(independence_score)
      high independence_score → lower marginal → larger credence update
      low independence_score  → higher marginal → smaller credence update
```

**EvidenceDelta block — four cipher states as state machine:**

```
Block: EvidenceDelta
  value properties:
    cipher_match:    Boolean
    source_new:      Boolean
    nodes_exist:     Boolean

  state machine: CipherStateMachine
    state_1: cipher_match=true,  source_new=false → no-op
    state_2: cipher_match=true,  source_new=true  → governance → credence update
    state_3: cipher_match=false, nodes_exist=true  → governance → new claim
    state_4: cipher_match=false, nodes_exist=false → SCA creates → state_3
```

**SCAEngine block — subcluster as formal composite:**

```
Block: SCAEngine
  value properties:
    subcluster:       ClaimSubgraph    ← H_c = G[U_c]
    traversal_pattern: TraversalPattern ← defines U_c
    evidence_delta:   EvidenceDelta    ← E = H̃_c \ H_c

  operations:
    computeDelta(H_proposed: ClaimSubgraph): EvidenceDelta
      body: return H_proposed minus subcluster
            (set difference on nodes and edges)

    evaluateGovernance(delta: EvidenceDelta): Boolean
      body: delegate to ClaimLifecycleService.governanceCheck()

    monitorConvergence(): ConvergenceStatus
      body: measure State2_rate / (State2_rate + State3_rate)
            return {forming, stabilising, converged}

    detectOscillation(): Boolean
      body: return dispute_count > oscillation_limit
```

### The XMI Artifact

A SysML XMI expressing the above is produced as:
  sysml/claim_bayesian_formal.xmi

This is a separate XMI from the proposed_multiagent model.
It focuses on the formal properties of the Claim and its
update mechanics, not the multi-agent coordination pattern.

The two XMI files together constitute the full model:
  proposed_multiagent_broadcast_optin.xmi — coordination structure
  claim_bayesian_formal.xmi               — claim update semantics

---

## Part 6 — Metanode Schema Validation

The document we reviewed confirms our SYS_ metanode architecture
maps correctly to the formally recommended structure:

```
Their recommendation       Our implementation
──────────────────────────────────────────────
:NodeType                  SYS_ node type definitions
:RelType                   Relationship type catalog
:Property                  Property definitions on SYS_ nodes
:GovernanceRule            SYS_Policy nodes
:Constraint                SYS_Threshold nodes
:TraversalPattern          Vertex jumping pattern definitions
:QueryTemplate             MCP tool query templates
:SchemaVersion             DECISIONS.md + commit hash versioning
```

Critical warning from the document, confirmed by our D-034 gap:
  "If the meta layer drifts from the actual database,
   agents regress into guessing."

SYS_FederationSource stub nodes with null pid/scoping_weight/
property_name are exactly this failure mode. D-035 must include
populating those stubs before Phase 3 begins.

---

## Part 7 — Consequences and New SYS_Threshold Nodes

### New Properties Required

```
Claim node:
  credence               (rename from confidence — more precise)
  likelihood             P_t(E|c)
  marginal               P_t(E)
  fractal_dimension      derived
  boundary_status        derived: interior | boundary | frontier
  life_pattern           derived: still_life | glider | oscillator | frontier
  corroboration_count    maintained by SCA
  dispute_count          maintained by SCA

Source node:
  independence_score     Real [0..1]
  institution_id         for independence computation
  publication_date       for temporal independence

EvidenceDelta (new node type):
  cipher_match           Boolean
  source_new             Boolean
  nodes_exist            Boolean
  admissible             Boolean (H̃_c ⊨ Γ result)
```

### New SYS_Threshold Nodes

```
subcluster_convergence_ratio    State2 rate for convergence detection
claim_oscillation_limit         dispute count before contested_permanent
fractal_dimension_base          baseline for promotion threshold calc
independence_weight_factor      scaling for marginal computation
likelihood_causal_weight        P_t(E|c) for causal subclaims
likelihood_factual_weight       P_t(E|c) for factual subclaims
likelihood_contextual_weight    P_t(E|c) for contextual subclaims
```

### D10 Promotion Threshold Adjustment

```
BEFORE: promote if credence >= claim_promotion_confidence (flat 0.9)

AFTER:  promote if credence >= f(base_threshold, fractal_dimension,
                                  independent_source_count)
  higher fractal_dimension → higher threshold
  fewer independent sources → higher threshold
  more independent sources  → threshold relaxed toward base
```

---

## Part 8 — Implementation Sequencing (Post-Prototype)

```
1. Rename confidence → credence on Claim nodes
   (semantic precision — matches formal literature)

2. Add EvidenceDelta as explicit node type
   (makes the four cipher states queryable)

3. Add independence_score to Source nodes
   (unblocked after Phase 3 VIAF/LCNAF integration)

4. Add likelihood, marginal to Claim nodes
   (computed values — need likelihood model initialisation)

5. Implement governanceCheck() as Cypher query set
   (converts D10/D11 DMN tables to executable governance)

6. Implement computeCredenceUpdate() with independence weighting
   (replaces flat confidence bump in State 2)

7. Add fractal_dimension, boundary_status as derived properties
   (computed by SCA on subcluster assembly)

8. Implement monitorConvergence(), detectOscillation()
   (SCA operations, require threshold values)

9. Cytoscape rendering by boundary_status and life_pattern
   (visual differentiation — requires all above)
```

---

## Commit Instructions

Files:
  docs/D036_CLAIM_FRACTAL_PATTERN.md — this document
  sysml/claim_bayesian_formal.xmi    — SysML expression of formalism

Update:
  DECISIONS.md — D-036 entry
  KANBAN.md    — D-036 implementation items (post-prototype backlog)
  sysml/BLOCK_CATALOG_RECONCILED.md:
    Claim block: credence, likelihood, marginal, fractal_dimension,
                 boundary_status, life_pattern, corroboration_count,
                 dispute_count
    Source block: independence_score, institution_id, publication_date
    New block: EvidenceDelta
    SCAEngine: monitorConvergence(), detectOscillation(),
               computeDelta(), evaluateGovernance()
    ClaimLifecycleService: governanceCheck(), computeCredenceUpdate()

Suggested commit message:
  D-036: Bayesian formalism, fractal theory, Game of Life — claim model
  - Formal grounding: governed Bayesian update, P_t(E|c), P_t(E)
  - Source independence as marginal factor — Phase 3 justified precisely
  - Gamma as executable Cypher — not prose, not DMN alone
  - Four cipher states mapped to Bayesian update steps
  - SUBCLAIM_OF, EvidenceDelta, boundary_status, life_pattern
  - SysML expression: claim_bayesian_formal.xmi
  - New SYS_Threshold nodes: independence_weight, likelihood weights,
    convergence_ratio, oscillation_limit, fractal_dimension_base

---

## Part 9 — Framework Applicability and Fischer Flag Lifecycle

### Fischer and Bayes Are Constitution Layer Plugins, Not Hard Architecture

Fischer and Bayes are analytical perspectives — frameworks the SFA
constitution loads and applies where relevant. They are not mandatory
passes. For some domains, some sources, some claim types they may not
be the right frameworks at all.

```
Constitution Layer 3M is not:
  "run Fischer check, then run Bayes update"

Constitution Layer 3M is:
  a registry of analytical frameworks
  each with applicability conditions, domain scope, claim type scope
  SFA selects applicable frameworks per claim per source per context
```

Fischer applies to historical claims where the author is making causal
or interpretive arguments about the past. It does not apply to a
purely documentary claim — "the Fugitive Slave Act was passed on
September 18, 1850." No fallacy check needed on a date and a fact.

Bayes applies when there is a prior belief to update and new evidence
to update it with. It does not apply when a claim is being established
for the first time with a single authoritative source — there is no
meaningful prior, no likelihood model yet populated.

### Framework Applicability as Precondition

```
Before applying Fischer check:
  evaluate: does_fischer_apply(claim_type, source_type, domain)
  applicable_to:     [historical_causal, historical_interpretive]
  not_applicable_to: [documentary, definitional, quantitative]
  trigger:           claim contains causal or interpretive assertion

Before applying Bayesian update:
  evaluate: is_prior_meaningful(claim, credence_history)
  applicable_to:     [any claim with credence history and prior]
  not_applicable_to: [first_occurrence with no prior established]
  trigger:           State 2 or State 3 event on existing claim

If framework does not apply:
  skip — do not produce null or trivial result
  log: framework_not_applicable, reason
```

### The Registry Pattern — SYS_BibliographyRegistry Layer 3M

```
SYS_BibliographyRegistry — methodological entries (Layer 3M):

  Fischer 1970:
    applicable_to:     [historical_causal, historical_interpretive]
    not_applicable_to: [documentary, definitional, quantitative]
    trigger:           claim contains causal assertion
    recompute_on:      State 2 or State 3 event on parent claim
    flag_lifecycle:    active | resolved | weakened | strengthened

  Bayesian update:
    applicable_to:     [any claim with credence history]
    not_applicable_to: [first_occurrence, no prior]
    trigger:           State 2 or State 3 event on existing claim

  [additional frameworks: domain expert owned, Layer 3 per facet]
```

### Fischer Flag Lifecycle — Not Terminal

A Fischer flag at claim creation is not a permanent judgment on the
source. It is a hypothesis about what is missing from the evidence
at the time of evaluation. As the subcluster grows, the flag is
recomputed.

```
FischerFlag node — additional properties:
  status:       active | resolved | weakened | strengthened
  resolved_by:  EvidenceDelta cipher that provided resolving evidence
  trigger:      recompute on each State 2 or State 3 event
                on the parent claim

Example lifecycle:
  Paragraph 1: False Cause flag raised on C4 (causal claim)
    status: active, severity: HIGH, credence reduced 0.81 → 0.71

  Paragraph 2 arrives — provides causal mechanism evidence:
    recompute Fischer False Cause flag
    if paragraph 2 establishes mechanism → status: resolved
    if paragraph 2 partially supports → status: weakened
    credence recalculated with updated likelihood
```

A False Cause flag that resolves as evidence accumulates is not a
failure. It is the system working correctly. The claim was
appropriately tentative at paragraph 1. By paragraph 3 it may be
appropriately confident.

Fischer flags are hypotheses about what is missing from the evidence.
They are resolved — not overruled — when the missing evidence arrives.

### Recomputation Trigger on Subcluster Growth

```
On each State 2 event (new source, same claim):
  1. recompute applicable Fischer flags:
     if new evidence provides causal mechanism:
       False Cause: active → resolved or weakened
     if new evidence introduces new group composition:
       Composition: active → strengthened
  2. update likelihood P_t(E|c) with updated Fischer assessment
  3. recompute credence via Bayes with updated likelihood
  4. recompute boundary_status and life_pattern

On each State 3 event (new claim with [:EXTENDS] relationship):
  same recomputation sequence
  EXTENDS relationship: new claim may provide evidence
  the previous claim's flags were waiting for
  the subcluster grows forward and the flags respond
```

### Consequences for D-019 and the Likelihood Model

D-019 subclaim confidence propagation must be updated:

```
BEFORE: likelihood_weight is fixed by subclaim_type at claim creation

AFTER:  likelihood_weight is recomputed when Fischer flags change
        active False Cause flag on C4 → lower likelihood_weight
        resolved False Cause flag on C4 → higher likelihood_weight
        the Bayesian update and the Fischer assessment are coupled
```

This coupling is correct — it means the system gets more confident
as evidence fills the gaps that Fischer identified, and it gets less
confident if new evidence introduces new gaps.

### New SYS_Threshold Node

```
fischer_recompute_window:
  number of State 2/3 events after which Fischer flags are
  force-reviewed even if not triggered by specific evidence
  prevents stale flags on long-running claims
```

### XMI Update Required

sysml/claim_bayesian_formal.xmi — additions needed:
  - FischerFlag block: status enum, resolved_by, trigger
  - Claim block: constraint for Fischer flag recomputation on growth
  - SCAEngine: recomputeFischerFlags() operation
  - SYS_BibliographyRegistry: applicability_conditions on Layer3M entries
  - Layer3MFramework block: applicable_to, not_applicable_to, trigger

See Part 10 — updated XMI artifact.
