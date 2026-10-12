# Response: Review of the GraphRevised Direction

**Responds to:** [Review of the Chrystallum GraphRevised Direction](Review%20of%20the%20Chrystallum%20GraphRevised%20Direction.md)
**Date:** 2026-10-12

The review read the public branch at `c19aceb` (2026-10-11). Since then,
registry v3 (the command split), reason codes, supersession, retraction, and
the delegation policy are done, and the qualifier design is drafted in
[22-CLAIM-QUALIFIERS.md](../22-CLAIM-QUALIFIERS.md). The review's central
concern, that subject–predicate–object identity is too narrow, is the
problem 22 addresses.

## Agreed and already done or designed

| Review point | Status |
|---|---|
| Finish registry v3 and the command split (priority 1) | Done: `heldAuthorityOver` and `commanded` (predicates-v3) |
| Supersession links and reason codes (priority 4) | Done, plus `retract` for accepted claims found wrong |
| Qualifier canonicalization and assertion identity (priority 2) | Designed: 22 §3, qualifiers in the ID as a canonical digest |
| E12 attribution before micro-events (priority 3, "Narrative versus fact") | Designed: claim mode in 22 §4 |
| Qualified time authoritative, `IN_YEAR` a rebuildable projection (priority 6) | Recorded in [04 §9](../04-IMPLEMENTATION-PLAN.md) and 22 §6 |
| Roman Army as a later stress test, not bulk-loaded | Agreed in [Response - Roman Republican Army Structure](Response%20-%20Roman%20Republican%20Army%20Structure.md) |
| Read API before the React/Cytoscape explorer | Already the sequence in [20-EXPLORER-UI.md](../20-EXPLORER-UI.md) |

## Proposition model or claim-expression model

The review asks for an explicit choice and recommends a hybrid: a canonical
proposition plus source-specific attributions. 22 is that hybrid, built from
one label:

- **Attributed claims** are the claim expressions: one per source ("according
  to Plutarch", "according to Dio"), never merged.
- **Asserted claims** are the propositions: Chrystallum's own, with evidence
  from any source accumulating on one node.
- **`PROMOTED_FROM`** links a proposition to the attributions it rests on.
  Promotion creates the asserted claim; it never mutates an attributed one.

A separate `Proposition` label is not needed while asserted claims play that
role. The open piece is the review's "deny": a source that contradicts a
proposition is evidence with stance `contradicts` on the asserted claim (E8),
not a negated claim.

## Accepted with changes

- **Evidence stance (E8).** Adopt `supports`, `contradicts`, `qualifies`,
  `mentions` as the controlled vocabulary on the evidence link. **Leave out
  `is_silent_on` for now:** silence is an inference about what a source would
  be expected to say, not something a passage shows, so it fails the
  verbatim-quotation rule. If needed, it belongs later as a curator- or
  method-made claim with its own basis.
- **Confidence and assessment.** Agreed: no single numeric confidence. Most of
  the proposed `EvidenceAssessment` already exists on the decision: who
  (`decidedBy`), when (`decidedAt`), conclusion (status and `decisionReason`),
  rationale (`decisionBasis`), and method version (prompt, registry, and
  schema versions on the Proposal). Stance belongs on the evidence link. A
  separate assessment node waits until one piece of evidence needs several
  assessments.
- **Work and edition.** 22 adds Work entities and `IN_WORK`. A separate
  edition node waits for a concrete trigger: two editions or translations of
  one work being read, or a claim that depends on the original language
  rather than the translation (a Greek or Latin title rendered loosely in
  English is the likely first case).
- **Bridges.** The review's "Bridge" (modern scholarship, archaeology, or
  science connected to an ancient claim) differs from the navigation docs'
  semantic bridge (a conceptual path across domains, such as senator to
  mollusk). Both are wanted. Cross-temporal evidence fits E10 (sources),
  E13 (computed claims), and E8 (stance); it needs no new operation beyond
  trace and expand.

## Corrections made

- **`Year` as an Assertion object.** [02 §3](../02-GRAPH-MODEL.md) showed
  `ASSERTION_OBJECT → Year`, which the canonical endpoint list does not
  allow. 02 now points to the time qualifier in 22 instead; a date is a
  qualifier, not an object.
- **Proposal as audit history.** 02 now states the boundary: Proposals and
  their decisions are durable editorial history in Neo4j and hidden in
  ordinary exploration; queues, locks, retries, jobs, and checkpoints stay
  outside it.
- **Subjects are intentional.** 02 now states that a Subject is created for
  an inquiry or a body of work, never as a shadow of every Entity.
- **Handoff push status.** [19](../19-SESSION-HANDOFF.md) now says the branch
  is public and which commits are local.

## Proposed, awaiting the curator

- **Root README notice.** The public root README still describes the legacy
  17-agent architecture as "Production Ready". Add a short notice at the top
  pointing to `GraphRevised/README.md`.
- **Conformance check.** Every accepted claim has at least one evidence link.
  This is a check on the live graph, not a unit test (tests must not depend on
  live contents), so it belongs in a read-only `review check` command. All 10
  accepted claims pass it today.
- **Versions in run traces.** Run logs record the prompt and model; add the
  predicate-registry and draft-schema versions. Read API responses will carry
  them when that API exists.
- **CI for the offline tests** on push, with the live tests opt-in.
- **ADRs: not adopted as a new directory.** Decisions already live in the
  numbered docs and the `docs/Response - …` files. A short decision index in
  the README would give the same lookup without a parallel set of records.
