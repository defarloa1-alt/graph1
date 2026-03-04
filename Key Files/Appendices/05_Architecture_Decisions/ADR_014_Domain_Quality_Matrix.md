# ADR 014: Domain Quality Matrix Pattern

**Status:** Accepted
**Date:** March 4, 2026
**Decision:** Introduce a systematic ontological-walk + backlink-probe pattern for evaluating domain quality before SCA expansion.

---

## Context

When the SCA receives a new domain QID (e.g., Q17167 = Roman Republic), it needs to understand the quality landscape of the ontological neighbourhood before committing resources to backlink harvesting, facet assignment, and entity ingestion.

Currently, the system follows a linear path: seed → P31 anchors → federation positioning → backlink harvest. This works but gives no upfront visibility into which branches of the ontology are rich (authority-covered, backlink-dense) versus sparse.

## Decision

### 1. Ontological Walk Structure

Given a domain QID, the matrix builder:

| Step | Property | Direction | Purpose |
|------|----------|-----------|---------|
| Anchor | P31 (instance of) | up | Find class anchors (e.g., historical period, form of government, historical country) |
| Chain | P279 (subclass of) | up | Walk class hierarchy |
| Chain | P527 (has parts) | down | Walk compositional children |
| Chain | P361 (part of) | up | Walk compositional parents |

For each `P31` target, the system recursively follows P279/P527/P361 up to `max_depth` (default 3).

### 2. Backlink Quality Probe

At each visited node, probe inbound links across signal properties:

- P31 (instance of) — entities typed as this concept
- P279 (subclass of) — children in class hierarchy
- P361 (part of) — components claiming membership
- P527 (has part) — containers
- P710 (participant) — events referencing this
- P17 (country) — geo-political links
- P131 (located in) — spatial links
- P921 (main subject) — scholarly works

Wikimedia administrative noise (categories, templates, disambiguation pages) is filtered via P31 denylist.

### 3. Quality Scoring (Per Node)

| Dimension | Weight | Calculation |
|-----------|--------|-------------|
| authority_coverage | 0.25 | Fraction of 5 authority IDs present (LCSH, LCC, Dewey, FAST, GND) |
| backlink_density | 0.30 | Normalised backlink count (capped at 100) |
| type_diversity | 0.20 | Unique entity types / 10 (capped at 1.0) |
| property_spread | 0.25 | Fraction of 8 signal properties with ≥1 backlink |

Composite = weighted sum → 0.0–1.0

### 4. Output as Matrix

The result is a flat matrix (CSV + JSON) with one row per visited node:

```
QID | Label | Depth | Via | Anchor | LCSH | LCC | Dewey | FAST | GND | Backlinks | Composite
```

This matrix enables:
- **Prioritisation:** High-composite nodes get harvested first
- **Gap analysis:** Nodes with authority IDs but no backlinks indicate untapped sources
- **Budget allocation:** Sparse branches can be deprioritised or skipped
- **Facet routing:** Entity-type distribution hints at which facet agents should be activated

### 5. Neo4j Persistence (Optional)

When `--write` is used, each row becomes a `DomainQualityProbe` node linked to the `SubjectConcept` via `HAS_QUALITY_PROBE`. This allows the SCA to query the matrix during planning.

## Consequences

- SCA gains upfront visibility into domain quality before committing to full harvesting
- Federation positioning (Layer 1) can use the matrix to prioritise anchor resolution
- Facet agents can check composite scores before activating on sparse branches
- The matrix pattern is domain-agnostic — works for any QID, not just Q17167
