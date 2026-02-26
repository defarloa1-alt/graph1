# Narrative Paths: Design Notes

## Purpose

Curated paths are the SCA's answer to "what are the narratively coherent routes through this domain" without requiring the SFA to discover them at query time.

## Path Selection

The seven paths are well-chosen. Each crosses at least two facets — they're not just drilling down a single branch, they're the routes that reveal connections:

- **Land reform → Social orders → Civil wars** — The Gracchan crisis in three hops
- **Government → Factions → Civil wars** — Late Republic constitutional breakdown

These are the paths a good historian would naturally suggest to someone arriving cold.

## Weighting

The +0.05 per path cap at +0.15 is conservative and right. Narrative paths should not dominate the score so heavily that a confirmed, entity-rich node with no curated path gets buried under a thin node that happens to start a path. The current weighting keeps paths as a tiebreaker and mild boost rather than the primary signal.

## Gaps

**Religion** — absent from the seven paths. The Roman Republic's religious-political entanglement (auspices, priesthoods, legitimacy) is one of the most non-obvious and interesting traversal routes in the domain. A path like:

- Religion → Public ritual → Legitimacy → Constitutional crisis

would be valuable once the entity layer is rich enough to support it. Flag for when the graph has more substance behind the religious SubjectConcepts.

## Tests

The tests are the right tests. Loading and the narrative boost are the two things that can silently fail without being noticed.

## Calibration

Until entity counts are real (from cluster assignment), the base_score term runs on zeros and the narrative path boost does more work than it should relative to the full algorithm. Once cluster assignment has populated the graph, re-evaluate whether the current path weighting is calibrated correctly or needs adjustment.
