# Response: Roman Republican Army Structure

**Responds to:** [Roman Republican Army Structure for a Neo4j Knowledge Graph](Roman%20Republican%20Army%20Structure%20for%20a%20Neo4j%20Knowledge%20Graph.md)
**Date:** 2026-10-12
**Status:** Agreed with the curator

## Decision

Adopt the document's reified-command pattern, which the core model already
has, and use it to redefine the planned `capacity` qualifier as a **role**:
a link from a command Assertion to the office or post the person acted in.
Do not adopt its label set. The author worked without knowledge of the
GraphRevised schema, and most of its proposed labels map onto the seven core
labels.

## The intermediate node is the Assertion

The document replaces a timeless `Person -[:COMMANDED]-> Unit` edge with a
`CommandAssignment` node carrying the force, role, authority, campaign,
dates, and source. In GraphRevised that node is the Assertion, the reified
relationship:

| Document | GraphRevised |
|---|---|
| `CommandAssignment` | Assertion with predicate `commanded` or `heldAuthorityOver` |
| `SUBJECT_OF` / `ASSIGNED_TO` | `ASSERTION_SUBJECT` / `ASSERTION_OBJECT` |
| `DURING → Campaign` | `ASSERTION_CONTEXT → Event` (planned) |
| `IN_ROLE → Office` | `ASSERTION_ROLE → Entity` (the role qualifier, replacing `capacity`) |
| `SUPPORTED_BY_SOURCE` | `SUPPORTED_BY`, with a verbatim quotation |
| `validFrom` / `validTo` | Phase 7 date spans on the Assertion |
| distinction between formal authority and operational control | `heldAuthorityOver` versus `commanded` (predicates-v3) |

## Role, not capacity

The earlier `capacity` list (*imperium*, triumvir, *legatus*, *praefectus
classis*) mixed three kinds of thing. The document's command table separates
them:

| Kind | Examples | Treatment |
|---|---|---|
| Role: the position a person acted in | consul, triumvir, *legatus*, *praefectus classis* | role qualifier |
| Legal basis: the source of authority | *imperium*, delegation from a magistrate | not a role; deferred |
| Battle-line position | right wing, reserve | carried by the force entities |

Rules:

1. The role is an optional link from a `commanded` or `heldAuthorityOver`
   Assertion to an Entity for the office or post, the same Entity that
   `heldPosition` claims point to. Command claims and career claims then meet
   at one node, which creates paths for exploration.
2. The role Entity's label keeps the source's term; glosses are aliases
   ([07 §7](../07-DOMAIN-ADAPTATION.md)).
3. The role is part of the claim's identity and fixed at creation, like
   Phase 7 dates. A claim with no role is a coarser claim that a role-qualified
   claim may later supersede (reason `underspecified`).
4. The quotation must show the role. The reader may not supply an office from
   outside knowledge. Plutarch's "Caesar posted Agrippa on the left" names no
   role, so a claim from it has none.
5. Roles can be contested. In 31 BCE Octavian was consul, and whether he still
   held triumviral powers is debated, so "as consul" and "as triumvir" are
   separate, separately evidenced claims.
6. Open: whether a role-qualified claim needs a date span (Phase 7 lists
   "command in a capacity" among the predicates that do).

## Adopted as principles

- Separate a unit type from a historical unit; separate nominal from observed
  strength.
- Do not back-project later organization (the Imperial first cohort, a
  single "Marian reform" event).
- Model change and evidence rather than one timeless hierarchy.

## Not adopted

- Its roughly twenty labels (`UnitType`, `OrganizationModel`,
  `CommandAssignment`, `Claim`, `Source`, and others). Unit types, models,
  and offices fit as Entity kinds with claims between them. Adding labels
  requires a query the core cannot express (README clean-start rules).
- The period-by-period army ontology as core model. It is candidate content
  for a Roman domain pack.

## Backlog

- **Force hierarchy:** a predicate between Groups for the document's
  `SUBUNIT_OF` ("a wing is part of a fleet"), currently a known gap carried
  only by labels.
