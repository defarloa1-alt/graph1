# Concepts — from 2-26-26-Compare_federated_vs_centralized_knowledge_graphs.md
_Extracted: 2026-02-27_

---

## OVERVIEW

This file is largely the same Perplexity session as `2-26-26-perplex-mc--agents.md`. The vast majority of content was already captured in the previous backlog. There is **one significant unique block**: Perplexity's direct review of `federation_node_schema.py` as a cellular automaton experiment after the code was uploaded. That review contains actionable critique not available elsewhere.

---

## THE UNIQUE CONTENT — Perplexity's Schema Review

Perplexity read the schema code and gave a structured assessment. Key points extracted below.

---

### 1. What the Schema Gets Right (as CA)

**Local rules, global pattern — correctly implemented:**
- Adjacency is entirely local: two nodes are neighbours if they share alignment fields.
- Survival is based on local state (dimensions present), not any global ontology.
- This matches the spirit of "simple local rules → emergent global structure."

**Dimension-based survival floor — correctly analogous:**
- `SURVIVAL_FLOOR_DIMS = {POLITICAL, GEOGRAPHIC}` + `SURVIVAL_MIN_TOTAL = 4` is a sound analogue of "needs enough neighbours not to die."
- Gives a principled, explainable, tweakable filter. Much better than ad-hoc thresholds.
- Assessment: "As a schema/contract, this is already strong and definitely worth keeping."

**Three concrete values delivered even without full CA:**
1. Unified alignment contract — all federation surveys return comparable nodes with the same alignment fields; generic adjacency and survival checks work without per-federation logic.
2. Dimension-aware filtering — `survives` is compact and explainable; easy to adjust `SURVIVAL_MIN_TOTAL` per experiment.
3. Local adjacency as primitive — `adjacency()` is exactly the primitive needed for cluster detection and AI-periodization; gives agents a clear "why are these two nodes related?" surface.

---

### 2. What Is Missing — The Critical Gap

**The schema has state and neighbourhood but no update dynamics.**

Conway's Game of Life requires:
- A grid/graph of cells ✓ (done — `FederationNode` graph)
- A discrete time step ✗ (not implemented)
- An **update rule** that changes each cell's state based on its neighbours ✗ (not implemented)

Currently the schema is:
- State: alignment fields, dimensions, `status` ✓
- Neighbourhood: `adjacency()` ✓
- Update dynamics: **nothing** ✗

The `status` field exists (`RAW → ALIGNED → ALIVE → DEAD → MERGED → SPAWN`) but nothing transitions it. It's a label with no engine behind it.

---

### 3. The Minimal Update Rule Needed

Perplexity proposed a concrete minimal function:

```python
def update_status(nodes: list[FederationNode]) -> None:
    """
    One generation tick. Compute adjacency counts, set node.status.
    Call repeatedly until stable (no status changes).
    """
    # For each node:
    #   Count distinct adjacency dimensions with other nodes
    #   Count total neighbour count across all dimensions
    #   Apply transition rules (see below)
```

**Transition rules suggested:**

```
RAW → ALIGNED:   node has ≥ 2 distinct adjacency dimensions
                 with ≥ 3 total neighbours
                 (crosses into the active game)

ALIGNED → ALIVE: node is in a densely connected component
                 (enough neighbours across multiple dimensions)
                 = candidate SubjectConcept

RAW/ALIGNED → DEAD: node isolated in all dimensions
                    after k generations with no new neighbours
                    (thin, floating evidence — cull it)

ALIVE → MERGED:  group of nodes mutually adjacent in ≥ 3 dimensions
                 collapse into single richer node

→ SPAWN:         canonical node created to represent dense cluster
                 where no single node dominated
                 (the gap concept — this is the birth rule)
```

**Implementation note:** Run `update_status()` in a loop until no `status` changes. Stable state = the emergent SubjectConcept landscape.

---

### 4. Specific Architectural Suggestions

**`update_status` should live outside the dataclass.** The dataclass should remain a pure data contract. The update logic is pipeline behaviour, not schema behaviour. Suggested module: `apply_rules.py` in the pipeline.

**Generations should be discrete passes over the full node list.** Not per-node updates. All nodes are evaluated against the current state simultaneously, then all statuses are updated. This preserves the CA semantics — no node sees the effects of another node's update in the same tick.

**Track generation number.** Add `generation: int = 0` to `FederationNode` (or just track it externally in `apply_rules.py`). Log status transitions per generation. The trajectory from RAW to ALIVE is itself a finding — how many generations does it take for a concept to stabilise?

---

### 5. Assessment of the CA Framing Overall

Perplexity's bottom line (verbatim reconstructed):

> As a schema/contract, this is already strong and definitely worth keeping; the alignment-field-first design and dimension derivation are useful independent of the Game-of-Life metaphor. As a cellular automaton, it's half-built: you have state and neighborhood, but not the update dynamics yet. If you add a simple generation update step based on adjacency counts and `survives`, you'll get a real experiment in emergent federation structure, which is likely to be interesting enough to be worth trying.

The framing is validated as useful. The gap is the update engine. That's `apply_rules.py`.

---

## BACKLOG ITEMS FROM THIS FILE

Only one new item not already in the previous backlog:

---

### NEW ITEM: `apply_rules.py` — Generation Update Engine

**What it is:** The missing piece that makes the schema a real cellular automaton rather than a static scoring system. A single function `update_status(nodes)` that runs one generation tick — evaluates all nodes against current adjacency counts and transitions statuses — run in a loop until stable.

**Why it matters:** Without this, `status` is just a label. The SPAWN/birth rule — the key academic contribution — never fires. The entire Game of Life framing is metaphor without this function.

**Concrete items:**
- Write `apply_rules.py` in `scripts/backbone/subject/`
- Implement `update_status(nodes: list[FederationNode]) -> list[StatusChange]`
- Returns list of `(node_id, old_status, new_status)` tuples for logging
- Run in loop: `while update_status(nodes): generation += 1`
- Termination: stable when no status changes in a generation
- Log trajectory: for each node, record `[(generation, status)]` — the path from RAW to ALIVE (or DEAD)
- Output: `output/candidates/roman_republic_candidates.json` with final statuses + trajectories

**Transition rules to implement:**
```python
RAW → ALIGNED:    len(neighbours) >= 3 and distinct_adj_dims >= 2
ALIGNED → ALIVE:  survives and neighbours_by_dim count >= threshold
ALIVE → MERGED:   mutual_adjacency_dims(group) >= 3
→ SPAWN:          gap node implied by ALIVE cluster structure
RAW/ALIGNED → DEAD: 0 neighbours after k=3 generations
```

**Note:** The threshold values are experimental. Run on Roman Republic data and see what the natural clusters look like before locking in numbers. The whole point is to let the data determine what survives.

---

### REFINEMENT TO EXISTING ITEM 1 (Bayesian credence)

The review confirms: schema-level state tracking is correct as a precondition. The credence layer sits on top of `ALIVE` nodes only — nodes that are dead or raw don't accumulate credence. This ordering (CA stabilisation first, Bayesian credence second) should be made explicit in the pipeline sequence.

Pipeline order:
```
Phase 0a: Survey all federations → RAW nodes
Phase 0b: Align → ALIGNED nodes  
Phase 0c: apply_rules.py generations → ALIVE/DEAD/SPAWN
Phase 1:  Synthesis on ALIVE nodes only
Phase 2:  Bayesian credence layer on confirmed SubjectConcepts
```

---

## SUMMARY

The file adds one critical conceptual finding not in the previous backlog: **the schema is half a cellular automaton**. State and neighbourhood are built. The update engine is not. `apply_rules.py` is the missing piece and should be the next thing written after the six federation surveys are running.

Everything else in this file was already captured.
