# Revised Graph Model

This document defines the smallest useful graph contract for the clean start.
It is a practical property-graph model, not a complete ontology.

## 1. Core node types

### Entity

Represents a real-world or analytical thing.

Required properties:

```yaml
id: chr:entity:...
kind: Person | Event | Place | Group | Object | Work | Period | Other
label: ...
status: provisional | resolved | deprecated
```

Optional properties include descriptions, aliases, date values, and local
classification. Date values should also be represented through qualified
assertions when they are uncertain, disputed, or source-specific.

An Entity description is locally adopted display text. If it originates with
an authority record, preserve the source wording and revision on the linked
AuthorityRecord and SourceObservation.

### Subject

Represents a body of knowledge or inquiry about one or more entities.

Required properties:

```yaml
id: chr:subject:...
label: ...
status: candidate | provisional | validated | deprecated | merged
```

### AuthorityRecord

Represents an external record or identifier.

```yaml
id: chr:authority:wikidata:Q160387
label: Wikidata record: Battle of Actium (Q160387)
description: 31 BCE decisive confrontation of the Final War of the Roman Republic
system: Wikidata
identifier: Q160387
retrievedAt: ...
```

An AuthorityRecord identifies the external record. It does not automatically
assert that all data in the record is accepted locally.
Its `description`, when present, preserves the authority's display wording;
it is not a replacement for a locally adopted Entity description.

### SourceObservation

Represents a preserved statement or extracted fact from an external source.

```yaml
id: chr:observation:...
label: Wikidata observation: Marcus Vipsanius Agrippa participated in Battle of Actium
sourceSystem: Wikidata
sourceEntityId: Q160387
predicateExternalId: P710
objectExternalId: Q48174
externalStatementId: Q160387$32bdfa2f-...
sourceRevision: ...
retrievedAt: ...
contentHash: ...
rawPayloadUri: ...
status: observed | superseded
```

Source facts (`sourceSystem` through `rawPayloadUri`) are immutable once the
observation exists. Only display text and `observed`/`superseded` status may
change.

Two observation kinds currently exist, each with its own deterministic ID:

| Kind | Observes | ID form |
|---|---|---|
| Statement | one external statement at one revision | `chr:observation:wikidata:<QID>:<PID>:<statement prefix>:r<revision>` |
| Identity record | an entity record as fetched for identity discovery | `chr:observation:wikidata:<QID>:r<revision>:<hash>` |

The identity-record ID includes a digest of the preserved payload hash because
the same revision fetched with different properties is different observed
content. Claims are supported by statement observations; identity-record
observations support AuthorityRecord adoption.

Raw payloads may be stored outside Neo4j, with a URI or content hash recorded
on the observation.

The label explains the observation to a reader. The external entity IDs,
predicate ID, statement ID, revision, and content hash remain on the
observation because they identify the exact external statement that was
observed. They are provenance metadata, not preferred display captions.

### Assertion

Represents a local relationship or claim.

```yaml
id: chr:assertion:...
label: Marcus Vipsanius Agrippa participated in Battle of Actium
predicate: participatedIn
status: proposed | accepted | rejected | contested | superseded
assertedBy: ...
```

A new Assertion is always created `proposed`. Its status changes to
`accepted` or `rejected` only through a Proposal decision. Its predicate and
endpoints are fixed at creation; a different predicate or endpoint is a
different Assertion.

The assertion points to its subject and object and may point to one or more
source observations.

`id` is the stable machine identifier and must not be used as a user-facing
caption. Every committed assertion should also have a human-readable `label`.
The deterministic commit path generates the initial label from the subject
label, predicate display phrase, and object label. It may be revised for
grammar, localization, or an approved terminology change without changing the
assertion ID or predicate.

### Proposal

Represents a requested graph change that has not yet become an accepted
assertion.

```yaml
id: chr:proposal:...
label: Proposal to accept: Marcus Vipsanius Agrippa participated in Battle of Actium
operation: create | update | link | reject
status: submitted | validating | accepted | rejected | deferred
```

Proposals may be created by agents, scripts, or users. They are not durable
knowledge until accepted.

A new Proposal is always created `submitted` and proposes exactly one
Assertion. Its lifecycle is:

```text
submitted  -> validating | rejected | deferred
validating -> accepted | rejected | deferred
deferred   -> validating | rejected
accepted, rejected: terminal
```

Acceptance requires passing through `validating`. Repeating the current status
is an idempotent no-op that preserves the original `decidedAt`, `decidedBy`,
and `decisionBasis`. Accepting sets the Assertion to `accepted` (with
`acceptedAt`) and requires it to be `proposed`. Rejecting sets a `proposed`
Assertion to `rejected` but leaves an Assertion that another Proposal already
accepted untouched.

Proposal labels must state the requested action in plain language. An accepted
Proposal is workflow/audit history that records how an Assertion entered the
graph; it is not a second historical claim and should be hidden from ordinary
navigation views unless review history is requested.

## 1.1 Display-label rule

Every first-class node that may appear in a visual graph projection must have
a reader-facing `label` property. IDs, authority identifiers, source statement
IDs, and hashes remain machine-readable/provenance properties and must not be
used as the default node caption.

Nodes whose labels are verbose statements or source descriptions may also have
`shortLabel`. A compact graph projection uses `shortLabel` as its caption,
while node details always show the complete `label`. `shortLabel` is
presentation metadata; it does not replace the full label, identifier, or
predicate.

## 2. Canonical relationship directions

Relationship direction must be consistent in the stored graph.

```text
(:Subject)-[:HAS_SUBJECT_FOCUS]->(:Entity)
(:Entity)-[:HAS_AUTHORITY_RECORD]->(:AuthorityRecord)
(:Assertion)-[:ASSERTION_SUBJECT]->(:Entity|:Subject)
(:Assertion)-[:ASSERTION_OBJECT]->(:Entity|:Subject|:AuthorityRecord)
(:Assertion)-[:SUPPORTED_BY]->(:SourceObservation)
(:Proposal)-[:PROPOSES]->(:Assertion)
(:Entity)-[:IN_YEAR]->(:Year)
```

The inverse wording may be generated for display, but the database should use
one canonical direction.

## 3. Temporal relationships

Use an explicit relationship when a simple, unqualified year link is enough:

```text
(:Entity)-[:IN_YEAR]->(:Year)
```

Use an Assertion when the date is uncertain, disputed, source-specific, or
requires a qualifier:

```text
(:Assertion {
  predicate: occurredOn,
  status: accepted,
  datePrecision: day
})-[:ASSERTION_SUBJECT]->(:Entity)
(:Assertion)-[:ASSERTION_OBJECT]->(:Year)
```

The initial implementation may use direct `IN_YEAR` links for the temporal
backbone and introduce qualified temporal assertions when the first use case
requires them. Do not create both representations for the same fact without
defining which one is authoritative.

An assertion about an event may derive temporal context through its assertion
object. For example, an assertion that a person participated in the Battle of
Actium is displayed with the context “Battle of Actium, 31 BCE” because the
event has `IN_YEAR → Year {-31}`. Do not duplicate that context as a direct
assertion-to-year relationship unless the assertion itself has a different,
uncertain, disputed, or independently sourced date.

## 4. Authority mappings

Authority links must carry a role:

```yaml
authorityLink:
  localNode: chr:entity:actium
  authority: Wikidata
  identifier: Q160387
  role: entity_identity
  relation: closeMatch
  status: accepted
```

Examples of roles:

```text
entity_identity
subject_access
faceted_subject_access
classification_correspondence
place_gazetteer
period_definition
object_type
```

Do not use `exactMatch` merely because two labels are equal. Scope, type, and
source evidence must support the mapping.

## 5. Minimal constraints

The first database schema should enforce only constraints that prevent obvious
corruption:

```text
Entity.id is unique
Subject.id is unique
AuthorityRecord.id is unique
AuthorityRecord.(system, identifier) is unique
SourceObservation.id is unique
Assertion.id is unique
Proposal.id is unique
Year.year is unique
```

Additional constraints should be added only after a real query or write
pattern demonstrates the need.

`Year.year` is canonical because the existing local temporal backbone has a
complete, unique integer value in that property. `year_value` is identical in
the starting data but remains legacy compatibility metadata; new writes must
not depend on it.

## 6. Idempotent writes

Every write operation must be safe to retry.

Use deterministic identifiers where possible:

```text
observationId =
  hash(source system + external statement ID + source revision)

proposalId =
  hash(operation + target + normalized payload)
```

Use `MERGE`, uniqueness constraints, source revision checks, and explicit
status transitions. A retry must not create duplicate nodes or duplicate
accepted assertions.

A retry must also not silently change what an existing node means. The direct
operations therefore refuse (return zero rows and write nothing) when a retry
would change an Entity's `kind`, an Assertion's predicate or endpoints, a
Proposal's target, or an AuthorityRecord's local ID. A null optional display
value never erases an existing value. Operations link only to existing `Year`
nodes and never extend the backbone.

## 7. Source and claim separation

Keep the following distinct:

```text
Raw source payload
  → SourceObservation
  → local Assertion
  → accepted or rejected Decision
```

This allows the graph to answer:

- what did the source say?
- what did Chrystallum infer from it?
- who accepted or rejected the resulting claim?
- what changed when the source changed?
