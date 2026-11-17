---
status: governing
authority: what a thing means and how it is stored (labels, subtype properties, relationships, statuses, identity)
depends_on: []
details_in: [22-CLAIM-QUALIFIERS.md, 23-NARRATIVE-AND-NOTES.md, 27-GAZETTEER.md, 28-SUBJECT-BUCKETS.md]
superseded_by: null
last_reviewed: 2026-10-17
---

# Revised Graph Model

This document defines the smallest useful graph contract for the clean start.
It is a practical property-graph model, not a complete ontology.

## 1. Domain entity hierarchy

### Entity

Represents a real-world or analytical thing.

Required properties:

```yaml
id: chr:entity:...
label: ...
status: proposed | provisional | resolved | deprecated
```

`proposed` marks an entity an agent surfaced (the harvest, the reader), shown
at once and labelled, until the curator accepts or rejects it.

Optional properties include descriptions, aliases, date values, and local
classification. Date values should also be represented through qualified
assertions when they are uncertain, disputed, or source-specific.

An Entity description is locally adopted display text. If it originates with
an authority record, preserve the source wording and revision on the linked
AuthorityRecord and SourceObservation.

Neo4j subtype labels make the finite ontology explicit:

```text
(:Entity:Person)
(:Entity:Place)
(:Entity:Event)
(:Entity:Group)
(:Entity:Work)
(:Entity:Object)
(:Entity:Period)
(:Entity:Office)
(:Entity:Concept)
(:Entity:Polity)
(:Entity:Type)
(:Entity:Question)
(:Entity:Position)
(:Entity:Other)
```

`Person`, `Place`, `Event`, `Group`, `Work`, `Object`, `Period`, `Office`,
`Concept`, `Polity`, `Type`, `Question`, `Position`, and `Other` are domain
subtypes, not values of a generic `kind` property. `Office` holds positions
and posts; `Concept` holds analytical ideas and frames; `Polity` holds states;
`Type` holds unit types, organizational patterns, roles, and powers; a
`Question` is a historical question scholars answer differently, and a
`Position` one answer to it, shared by the Works that hold it (D-153, 44).

Subtype properties should remain small and type-specific:

| Subtype | Initial properties |
|---|---|
| Person | `gender`, `birthName`, `nameVariants` |
| Place | `placeType`, `latitude`, `longitude`, `coordinatePrecision`, `modernCountry` |
| Event | `eventType` |
| Group | `groupType` |
| Work | `workType`, `language` |
| Object | `objectType`, `material` |
| Period | `periodType` |
| Office | `officeType` |
| Concept | `conceptType` |
| Polity | `polityType` |
| Type | `typeCategory` |
| Other | `otherType` |

Dates, membership, creators, ownership, locations, and other source-sensitive
facts remain Assertions rather than unconstrained scalar fields.

`Year` is deliberately not an Entity subtype. It is a temporal coordinate and
the graph's ordered temporal backbone; see
[03-TEMPORAL-YEAR-BACKBONE.md](03-TEMPORAL-YEAR-BACKBONE.md).

### Subject

Represents a body of knowledge or inquiry about one or more entities.

A Subject is created intentionally: for an inquiry, a research scope, a body
of literature, or a user's drill-down. It is never an automatic shadow of an
Entity. **Since 2026-10-14 Subjects are also buckets** ([28](28-SUBJECT-BUCKETS.md)):
every entity sits in at least one, mostly computed from its claims, and
Subjects form a hierarchy (`NARROWER_THAN`, several parents allowed) anchored to
library headings.

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

### External-system roles

External systems are selected by workflow, not treated as interchangeable
identity providers:

| System | Role | Durable key and storage |
|---|---|---|
| Wikidata | identity discovery and source statements | `AuthorityRecord(system, identifier)`; statement and identity-record `SourceObservation`s |
| Pleiades | ancient-place gazetteer and location crosswalk | `Location(system, identifier)`; selected Place links may also carry a Pleiades `AuthorityRecord` |
| GeoNames | modern gazetteer and administrative tree | `Location(system, identifier)` |
| PeriodO | published period definitions, not local identity | `SourceObservation(sourceSystem, sourceEntityId)` with the PeriodO definition ID and ARK locator; the publication is a `Work` |
| LCSH, FAST, LCNAF, VIAF, GND | bibliographic or name authority control | `AuthorityRecord(system, identifier)` when a local entity or subject is linked |

An external identifier is a key to a preserved external record, not proof that
the record's claims are accepted locally. A system that supplies evidence but
does not identify a local entity belongs on `SourceObservation`; a system that
identifies a local entity belongs on `AuthorityRecord`; a gazetteer location
belongs on `Location`.

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
qualifierPropertyIds: [...]
sourceRevision: ...
retrievedAt: ...
contentHash: ...
rawPayloadUri: ...
status: observed | superseded
```

Source facts (`sourceSystem` through `rawPayloadUri`) are immutable once the
observation exists. Only display text and `observed`/`superseded` status may
change.

Passage observations (`observationKind: passage`) preserve a located span of
a specific edition: locator, passage text without editorial notes, notes kept
separately, edition citation, rights, and hashes. Their ID is
`chr:observation:<system>:<work>:<locator>:<source revision prefix>`.

`SUPPORTED_BY` and `PROPOSES_EVIDENCE` carry a `quotation` when the evidence
is a passage: the verbatim span offered in support.

Transcription observations (`observationKind: transcription`) are short
quotations the curator captured while reading, by hand or from Kindle and
Readwise/Reader highlights, with the edition and locator (page or Kindle
location), who captured them, and when. They are linked `IN_WORK` to their
Work, are private by default, and serve as evidence like passages
([23](23-NARRATIVE-AND-NOTES.md) §7).

Two Wikidata observation kinds currently exist, each with its own deterministic ID:

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
category: factual | interpretive | imaginative
mode: asserted | attributed
assertedBy: ...
```

A new Assertion is always created `proposed`. Its status changes to
`accepted` or `rejected` only through a Proposal decision. Its predicate and
endpoints are fixed at creation; a different predicate or endpoint is a
different Assertion. So are its qualifiers (time, role, context, quantity)
and its mode: `asserted` is Chrystallum's own claim, `attributed` a source's
depiction, linked `ATTRIBUTED_TO` its Work ([22](22-CLAIM-QUALIFIERS.md)).
`contested` is reserved for evidence stance (backlog E8) and not yet used.

`partOf` also relates a Work to a containing Work, such as a biography to a
collection (D-136). The two Works remain distinct identities; containment is
an evidence-bearing assertion subject to the normal proposal and review
process, not an automatic consequence of naming or identity.

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
operation: create | addEvidence
status: submitted | validating | accepted | rejected | deferred
```

`create` proposes a new Assertion; `addEvidence` offers new evidence for an
existing one. (`update`, `link`, and `reject` were listed here before Phase 5
and were never used: changes to a claim are new claims, supersession, or
retraction, below.)

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
and `decisionBasis`.

Every Proposal carries its evidence as pending (`PROPOSES_EVIDENCE`), which is
attached to the Assertion as `SUPPORTED_BY` only when the Proposal is
accepted. Evidence and claim are decided separately:

- **accept**: the evidence is attached; a `proposed` Assertion becomes
  `accepted` (with `acceptedAt`).
- **reject** (default): the Proposal's evidence is rejected and the claim
  stays open for better evidence.
- **reject the claim** (`rejectClaim`): the Assertion, which must still be
  `proposed`, becomes `rejected`. An accepted claim cannot be rejected through
  a Proposal.
- **reopen**: an explicit, recorded curator act returns a `rejected`
  Assertion to `proposed` (`reopenedAt`, `reopenedBy`, `reopenBasis`), so new
  evidence can be proposed for it.
- **supersede**: an explicit, recorded curator act replaces a `proposed` or
  `accepted` Assertion with one or more more precise Assertions. It becomes
  `superseded` and links to each replacement by `SUPERSEDED_BY`, recording
  `supersededFrom`, `supersededAt`, `supersededBy`, `supersedeBasis`, and
  `supersedeReason`. Its open Proposals must be decided first. A superseded
  Assertion takes no new evidence and leaves inquiry scope.
- **retract**: an explicit, recorded curator act rejects an `accepted`
  Assertion found to be wrong (`retractedAt`, `retractedBy`, `retractBasis`,
  `retractReason`). Its evidence links remain as audit history, and it can be
  reopened. Its open Proposals must be decided first.

Every Assertion records its claim `category` (`factual` or
`interpretive`) from its predicate; interpretive claims are attributed only.
A claim attributed to a Work of a creative form (poem, play, novel, …) is
`imaginative`, derived from the Work's `form`, never chosen; fiction never
supports an asserted claim ([25](25-LIVES-AND-PLAYGROUND.md) §6 item 3).

Every rejection, supersession, and retraction carries a reason code (`decisionReason` on
the Proposal, `supersedeReason` on the Assertion):

| Code | Meaning |
|---|---|
| `false` | the claim is wrong |
| `unsupported` | the evidence does not show the claim |
| `malformed` | the claim breaks the predicate's definition or kinds |
| `underspecified` | true in substance but too coarse; precise claims replace it |
| `superseded-by-model` | a model or registry change replaced it |

An `addEvidence` Proposal offers new evidence for an existing Assertion.
Accepting it for a still-`proposed` Assertion also accepts the claim: a claim
whose first evidence was rejected can be carried by stronger evidence.

A stored Proposal also records its provenance: `createdBy`, `rationale`,
`draftSchemaVersion`, `predicateRegistryVersion`, `promptVersion`, and
`modelId`. These are fixed at creation.

Proposals and their decisions are durable editorial history and stay in
Neo4j. Agent workflow state does not: queues, locks, retries, model jobs, and
checkpoints live outside the graph (the identity queue and run traces are
files).

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
(:Proposal)-[:PROPOSES_EVIDENCE]->(:SourceObservation)
(:Assertion)-[:SUPERSEDED_BY]->(:Assertion)
(:Assertion)-[:ASSERTION_CONTEXT]->(:Entity)   Event by default; per predicate (registry contextKinds)
(:Assertion)-[:ASSERTION_ROLE]->(:Entity)      Office by default; per predicate (registry roleKinds)
(:Assertion)-[:ATTRIBUTED_TO]->(:Entity:Work)
(:Assertion)-[:PROMOTED_FROM]->(:Assertion)
(:Assertion)-[:IN_YEAR]->(:Year)
(:SourceObservation)-[:IN_WORK]->(:Entity:Work)
(:Annotation)-[:ANNOTATES {quotation}]->(:SourceObservation)
(:Annotation)-[:CONCERNS]->(:Entity)          built; designed (32 §2.1): also Assertion, Subject, Proposal, Annotation
(:Entity)-[:IN_YEAR]->(:Year)
(:Subject)-[:NARROWER_THAN]->(:Subject)
(:Location)-[:WITHIN]->(:Location)
(:Location)-[:MODERN_LOCATION]->(:Location)
(:Entity:Place)-[:AT_LOCATION]->(:Location)
```

**Location** (the ninth core label, loaded 2026-10-15) is the gazetteer:
a geographic backbone preloaded from Pleiades and GeoNames, off the canvas
like Year ([27](27-GAZETTEER.md), 505,546 Locations; the last four
relationships above).

**Annotation** (the eighth core label, unique `id`, migration 003) is
commentary, never a claim: a passage of note flagged by the reader or the
curator, or a curator's note, with `kind`, `noteType`, `note`, `author`,
`visibility` (private, team, public), and `status` (flagged, endorsed,
dismissed). Its `label` says what it is and where, never what it says
("Anecdote · Weigall 17.11", "Mention of “Empire” (Period) · Hale 2.34");
the `note` carries the content (capture.core.annotation_label, migration 006). It may be deleted freely; it is never a hop in path tracing.

Built kinds: `passage-of-note` (a passage worth reading for an entity, and
why) and `entity-mention` (the words in a passage that first name an entity,
such as a depicted event); since 2026-10-18 `note` (a curator's note from the
vault, `ANNOTATES` its transcription) and `image-note` (on an image), written
by `capture/notes.py`. An **image** is a SourceObservation of kind `image`
(the hash and path of the curator's file, what it depicts, who made it, its
rights; operation `upsert_image_observation`): never evidence for a claim,
the file never in Neo4j. **Designed, not built**
([32](32-RESEARCH-WORKSPACE.md) §2): `kind: note`, the curator's research
notes (observation, question, hypothesis, interpretation, excerpt, outline,
argument), and `kind: path`, a saved path (32 §3 item 2: Annotations until a
query needs more); `CONCERNS` widened to an Assertion, a Subject, a Proposal,
or another Annotation, so a note on a claim comments on it without becoming
one. The visibility words are open (32 §3 item 1: `team` or `shared`).

### Our own units and the sources' units

#### Historical phases and topical sections (D-134)

A historical phase is a durable, curator-defined analytical sub-event, not
an automatically inferred fact. It may be revised, disputed, incomplete, or
overlap another phase; its existence, event membership, and ordering need
separate provenance and review. A phase of a battle must be a portion of that
battle: lead-up, aftermath, and later reception do not become battle parts
merely because they belong in its history. A Subject answers what material is
about; `IN_SUBJECT` is topical relevance, not `partOf`. Subjects may cover
events before or after their focus, including meaning and memory.

The existing phase `Event` and evidence-bearing `partOf` representation is
unchanged. No new `Phase` label or `HAS_PARTITION` relationship is authorized
by this decision. The accepted Meaning and memory phase-to-battle claim is a
legacy claim requiring an explicit curator review; do not silently remove,
relabel, or change it or infer a decision for individual placements. D-134
qualifies D-091's interpretation, not its record of the earlier decision.

Two kinds of Event are not historical identities from an authority but units
of a reading:

- **Depicted events** ([23](23-NARRATIVE-AND-NOTES.md) §2):
  `chr:entity:depicted:<work>:<slug>`, one source's narrative unit, labelled
  with its voice ("Antony's flight (Plutarch)"), proposed by the reader, its
  claims attributed to that Work. The same action in two sources is two
  depicted events until the curator links them by `depictsSameAs`.
- **Phases** ([29](29-EVENT-CENTRED-INQUIRY.md) §10 item 2):
  `chr:entity:phase:<event>:<key>`, our own sub-events of an event, labelled as
  ours ("The lines engage (Chrystallum)"): each `partOf` the event, asserted,
  evidenced by the passages that depict its events; each depicted event
  `partOf` one phase at most. A depicted event from a creative Work is never
  placed. **The phases' order is the curator's decision, kept as data**: the
  ordered spine in `curation/phases.json`, never claims between the phases
  ([33](33-DECISIONS.md) D-091). A claim needs a passage that shows it, and
  the sources order only some of the steps; where a source orders two events
  against the spine, that is a review item (a weak placement or link, or
  phases that overlap), not a second order.

### Not graph data

Kept as files, never as nodes ([31](31-ONE-COMMAND.md) §3.11): programs,
inquiries (their reading configuration in `inquiries/`), plans, runs
(`runs/`), orientation dossiers (`dossiers/`), evidence packets, and
Chrystallum's accounts (`accounts/`, [29](29-EVENT-CENTRED-INQUIRY.md) §4b),
as well as queues, briefs, finds, and source plans. They name graph ids; the
graph does not name them.

The qualifier relationships, `PROMOTED_FROM`, and `IN_WORK` are specified in
[22-CLAIM-QUALIFIERS.md](22-CLAIM-QUALIFIERS.md). A unary Assertion (such as
`occurred`) has no `ASSERTION_OBJECT`. An Assertion's `IN_YEAR` links are
derived from its time qualifier.

The inverse wording may be generated for display, but the database should use
one canonical direction.

## 3. Temporal relationships

Use an explicit relationship when a simple, unqualified year link is enough:

```text
(:Entity)-[:IN_YEAR]->(:Year)
```

Use an Assertion when the date is uncertain, disputed, source-specific, or
requires a qualifier. A date is a **time qualifier** on the Assertion, not an
`ASSERTION_OBJECT`: a Year is never an assertion object. The qualifier
properties, the unary `occurred` predicate for dating an event, and the
derived `IN_YEAR` links from the Assertion are specified in
[22-CLAIM-QUALIFIERS.md](22-CLAIM-QUALIFIERS.md) §6.

The accepted dated Assertion is authoritative; `IN_YEAR` links are a
rebuildable navigation projection derived from it. The direct, unsourced
Phase 2 link *Battle of Actium → 31 BCE* predates this rule and is to be
replaced by a sourced claim.

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
classification_correspondence   (reserved: LCC is not used for now, 25 §8)
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
Annotation.id is unique                         (migration 003)
Location.id is unique                           (27, with a point index on Location.location)
Location.(system, identifier) is unique
```

These eleven are the live constraints (30 §7). Additional constraints should be added only after a real query or write
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
would change an Entity's subtype label, an Assertion's predicate or endpoints, a
Proposal's target, or an AuthorityRecord's local ID. A null optional display
value never erases an existing value. Operations link only to existing `Year`
nodes and never extend the backbone.

### 6.1 Direct lookup ("vertex jump")

A read or a write starts by finding its node directly, by a key the database
indexes, and only then walks a bounded number of relationships from it. In
Neo4j walking from a node already found is cheap; finding the starting node
by scanning property values is what is slow. The keys a lookup may use are
the unique ones:

```text
Entity.id, Subject.id, Assertion.id, Proposal.id, SourceObservation.id,
Annotation.id, Location.id, Year.year
AuthorityRecord.(system, identifier)      an external code: LCNAF n50051933, LCCN 2021007113, Wikidata Q1048
```

- **External codes are found through their AuthorityRecord, never kept
  inside a local id.** `(LCNAF, n50051933)` leads to its record and the record
  to the Entity that holds it: two index seeks. A local id stays the same when
  an authority merges, splits, or withdraws a code (01 invariant 1).
- **A claim's id is content-addressed** (22 §3): subject, predicate, object,
  and a digest of mode, attribution, context, role, time, and quantity, never
  who proposed it or when. Two proposers finding the same claim reach the same
  id, and a claim's family (every version of one fact) shares the id up to the
  digest.
- **Never a key from mutable properties** (a label, a description), and no
  composite key that would decide identity silently: a new one needs a
  versioned canonicalization rule, as the claim digest has.

**Cluster addresses are computed, not stored (D-138).** Because a claim id
begins with its subject and predicate, a cluster is found by its prefix with
one index range seek and no traversal (checked 2026-11-12: `STARTS WITH` on
`Assertion.id` plans as `NodeUniqueIndexSeekByRange`):

```text
chr:assertion:<subject>:<predicate>:              one entity's claims of one predicate
chr:assertion:depicted:<work>:<event>:            everything one depicted event stands for
<subject> × the predicates of one lens            an entity through a lens (one seek per predicate)
hash(entity id, lens, scope, claim ids read)      the cache key of a lens reading
```

This is what the legacy faceted cipher wanted (an entity seen from one facet),
without hub nodes or stored scores. The key is the local id, never the QID:
QIDs merge and redirect, and many entities (depicted events, phases) have none;
a QID start is two seeks through its AuthorityRecord. A claim id does not begin
with its object, so "who took part in this event" starts at the event and walks
its incoming links; when a node passes about 10,000 claims, an
object-and-predicate index on Assertion is added for that walk.

Dropped from the legacy design of the same name (`docs/architecture/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md`,
February 2026, reference only), on purpose: ids built from the QID with a type
prefix, and a cascade of BabelNet and synthetic ids for things without one
(they change when Wikidata does, and needed keys rewritten afterwards);
`FacetedEntity` hub nodes per entity, facet, and subject (facets are lenses,
never nodes: 33 D-039); stored aggregate confidence on them (rule: attestation
is computed, never stored, D-033).

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
