---
status: descriptive
authority: none; describes the graph as built (where it and 02 disagree, 02 governs)
depends_on: [02-GRAPH-MODEL.md]
superseded_by: null
last_reviewed: 2026-10-17
---

# 30 — Logical Model (UML)

**Date:** 2026-10-16.
**Status:** descriptive. It records the graph as built and as designed; it
changes no rule. Where this document and [02](02-GRAPH-MODEL.md) disagree, 02
governs and this document is out of date.
**Sources:** the live local database (`neo4j://127.0.0.1:7687`, database
`neo4j`, profiled read-only on 2026-10-16); [02](02-GRAPH-MODEL.md),
[22](22-CLAIM-QUALIFIERS.md), [23](23-NARRATIVE-AND-NOTES.md),
[27](27-GAZETTEER.md), [28](28-SUBJECT-BUCKETS.md); the operations file
[13](13-PHASE-3-DIRECT-OPERATIONS.cypher); the predicate registry
`proposals/predicates.v11.json`.

## 0. Reading this model

- **Class = Neo4j label.** Nine labels, one per node, no multi-label nodes.
- **Association = relationship type**, drawn in its one stored direction.
- **Multiplicity** is written at each end, UML style: the number at the
  *target* end says how many targets one source node has; the number at the
  *source* end says how many sources one target node has. The multiplicity is
  the rule the design states; §4 sets it beside what the live graph shows.
- **Dashed** associations are designed but not yet in the graph.
- `Entity` is one label whose `kind` property acts as a UML discriminator
  (§3). Kinds are data, in the predicate registry, not labels.
- `Assertion` is a **reified association**: a claim between Entities that
  carries its own identity, status, qualifiers, and evidence. The predicate
  registry (§5) types it.

## 1. Overview diagram

```mermaid
classDiagram
    direction LR

    class Entity {
        id : String [1] unique
        kind : EntityKind [1]
        label : String [1]
        status : EntityStatus [1]
    }
    class Subject {
        id : String [1] unique
        label : String [1]
        status : SubjectStatus [1]
    }
    class Assertion {
        id : String [1] unique
        predicate : String [1]
        label : String [1]
        status : AssertionStatus [1]
        category : ClaimCategory [1]
        mode : ClaimMode [0..1]
    }
    class Proposal {
        id : String [1] unique
        operation : ProposalOperation [1]
        label : String [1]
        status : ProposalStatus [1]
    }
    class SourceObservation {
        id : String [1] unique
        sourceSystem : String [1]
        observationKind : ObservationKind [0..1]
        status : ObservationStatus [1]
    }
    class AuthorityRecord {
        id : String [1] unique
        system : String [1]
        identifier : String [1]
        label : String [1]
    }
    class Annotation {
        id : String [1] unique
        kind : AnnotationKind [1]
        note : String [1]
        visibility : Visibility [1]
        status : AnnotationStatus [1]
    }
    class Year {
        year : Integer [1] unique
        label : String [1]
    }
    class Location {
        id : String [1] unique
        system : LocationSystem [1]
        identifier : String [1]
        kind : String [1]
        location : Point [0..1]
    }

    %% Claims
    Assertion "0..*" --> "1" Entity : ASSERTION_SUBJECT
    Assertion "0..*" --> "0..1" Entity : ASSERTION_OBJECT
    Assertion "0..*" --> "0..1" Entity : ASSERTION_CONTEXT
    Assertion "0..*" ..> "0..1" Entity : ASSERTION_ROLE (designed)
    Assertion "0..*" --> "0..1" Entity : ATTRIBUTED_TO (Work)
    Assertion "0..*" --> "0..*" Year : IN_YEAR
    Assertion "0..*" --> "0..*" Assertion : SUPERSEDED_BY
    Assertion "0..*" --> "0..*" Assertion : PROMOTED_FROM

    %% Evidence and review
    Assertion "0..*" --> "0..*" SourceObservation : SUPPORTED_BY
    Proposal "1..*" --> "1" Assertion : PROPOSES
    Proposal "0..*" --> "0..1" SourceObservation : PROPOSES_EVIDENCE
    SourceObservation "0..*" --> "0..1" Entity : IN_WORK (Work)

    %% Identity and subjects
    Entity "1..*" --> "0..*" AuthorityRecord : HAS_AUTHORITY_RECORD
    Subject "1..*" --> "0..*" AuthorityRecord : HAS_AUTHORITY_RECORD
    Subject "0..*" --> "1..*" Entity : HAS_SUBJECT_FOCUS
    Subject "0..*" ..> "0..*" Subject : BROADER (designed)

    %% Commentary
    Annotation "0..*" --> "0..1" SourceObservation : ANNOTATES
    Annotation "0..*" --> "1..*" Entity : CONCERNS

    %% Backbones
    Entity "0..*" --> "0..*" Year : IN_YEAR
    Year "0..1" --> "0..1" Year : FOLLOWED_BY
    Entity "0..*" --> "0..*" Location : AT_LOCATION (Place)
    Location "0..*" --> "0..*" Location : WITHIN
    Location "0..*" --> "0..*" Location : MODERN_LOCATION
```

The model has four layers, which the overview's comments group:

| Layer | Classes | Role |
|---|---|---|
| Knowledge | Entity, Subject, Assertion | what Chrystallum holds: things, inquiries and buckets, claims |
| Provenance and review | SourceObservation, AuthorityRecord, Proposal | what sources said, which external records identify things, how a claim entered |
| Commentary | Annotation | notes and passages of note; never a claim, never a hop in path tracing |
| Backbones | Year, Location | preloaded time and place scaffolds, off the canvas |

## 2. Classes and properties

Each table lists every property the live graph holds on that label, plus the
properties the operations write that no node yet carries (marked *designed*).
**Mult.** is the property's multiplicity: `[1]` required, `[0..1]` optional.
**Live** is how many nodes carry it on 2026-10-16.

### 2.1 Entity (688)

A real-world or analytical thing. Unique: `id`.

| Property | Type | Mult. | Live | Notes |
|---|---|---|---|---|
| id | String | [1] | 688 | `chr:entity:…`; unique |
| kind | EntityKind | [1] | 688 | discriminator (§3); fixed once set |
| label | String | [1] | 688 | reader-facing caption |
| shortLabel | String | [0..1] | 659 | compact caption |
| status | EntityStatus | [1] | 688 | |
| description | String | [0..1] | 209 | locally adopted display text |
| form | WorkForm | [0..1] | 10 | Works only; a creative form makes claims attributed to the Work imaginative |
| sourceNote | String | [0..1] | 2 | |
| decidedAt, decidedBy, decisionBasis | String | [0..1] | 0 | *designed*: the curator's decision on a proposed Entity |

### 2.2 Subject (1)

A body of knowledge or inquiry; since [28](28-SUBJECT-BUCKETS.md), also a
bucket. Created intentionally, never a shadow of an Entity. Unique: `id`.

| Property | Type | Mult. | Live | Notes |
|---|---|---|---|---|
| id | String | [1] | 1 | `chr:subject:…` |
| label | String | [1] | 1 | |
| shortLabel | String | [0..1] | 1 | |
| status | SubjectStatus | [1] | 1 | |

### 2.3 Assertion (1,718)

A local claim. Predicate and endpoints are fixed at creation; a different
predicate or endpoint is a different Assertion. Unique: `id`.

| Property | Type | Mult. | Live | Notes |
|---|---|---|---|---|
| id | String | [1] | 1718 | machine identifier, never a caption |
| predicate | String | [1] | 1718 | a registry predicate (§5) |
| label | String | [1] | 1718 | generated from subject, predicate phrase, object |
| shortLabel | String | [0..1] | 1718 | |
| status | AssertionStatus | [1] | 1718 | created `proposed` |
| category | ClaimCategory | [1] | 1718 | from the predicate; `imaginative` when attributed to a creative Work |
| mode | ClaimMode | [0..1] | 1424 | part of identity; 294 older claims have none |
| assertedBy | String | [1] | 1718 | |
| acceptedAt | String | [0..1] | 68 | |
| contextBasis | String | [0..1] | 69 | why the context Event was attached |
| **Time qualifier** ([22](22-CLAIM-QUALIFIERS.md) §6) | | | | |
| timeSourceExpression | String | [0..1] | 241 | the source's own wording |
| timeEdtf | String | [0..1] | 110 | normalized EDTF value |
| timePrecision | TimePrecision | [0..1] | 110 | |
| timeCalendar | String | [0..1] | 110 | |
| timeMode | TimeMode | [0..1] | 95 | |
| timeApproximate, timeUncertain | Boolean | [0..1] | 110 | |
| timeNormalizationBasis | String | [0..1] | 110 | |
| startEarliestJdn, startLatestJdn | Integer | [0..1] | 105 | Julian Day window of the start |
| endEarliestJdn, endLatestJdn | Integer | [0..1] | 109 | Julian Day window of the end |
| timeRelativeOffset | String | [0..1] | 0 | *designed*: offset within a context Event (registry v10) |
| **Quantity qualifier** (registry v9) | | | | |
| quantityMinimum, quantityMaximum, quantityTypical | Number | [0..1] | 0 | *designed*: `partOf`, `electedBy` |
| quantitySourceExpression | String | [0..1] | 0 | *designed* |
| **Lifecycle acts** | | | | |
| supersededFrom, supersededAt, supersededBy, supersedeBasis, supersedeReason | String | [0..1] | 8 | supersession; reason is a ReasonCode |
| reopenedAt, reopenedBy, reopenBasis | String | [0..1] | 0 | *designed*: reopen |
| retractedAt, retractedBy, retractBasis, retractReason | String | [0..1] | 0 | *designed*: retraction |

### 2.4 Proposal (1,929)

A requested graph change; durable editorial history. Proposes exactly one
Assertion. Provenance fields are fixed at creation. Unique: `id`.

| Property | Type | Mult. | Live | Notes |
|---|---|---|---|---|
| id | String | [1] | 1929 | |
| operation | ProposalOperation | [1] | 1929 | |
| label | String | [1] | 1929 | the requested action in plain language |
| shortLabel | String | [0..1] | 1929 | |
| status | ProposalStatus | [1] | 1929 | created `submitted` |
| createdBy | String | [1] | 1928 | |
| rationale | String | [1] | 1928 | |
| draftSchemaVersion | String | [1] | 1928 | |
| predicateRegistryVersion | String | [1] | 1928 | |
| promptVersion | String | [0..1] | 1493 | agent-made Proposals |
| modelId | String | [0..1] | 1480 | agent-made Proposals |
| inquiryId | String | [0..1] | 1470 | the inquiry that produced it |
| relevance | String | [0..1] | 1483 | why the evidence bears on the inquiry |
| ambiguities | List<String> | [0..1] | 1917 | |
| decidedAt, decidedBy, decisionBasis | String | [0..1] | 155 | set once on a decision |
| decisionReason | ReasonCode | [0..1] | 22 | rejections |
| rejectedClaim | Boolean | [0..1] | 23 | the decision also rejected the claim |

### 2.5 SourceObservation (805)

A preserved statement or located passage from an external source. Source
facts are immutable; only display text and status change. Unique: `id`.

| Property | Type | Mult. | Live | Notes |
|---|---|---|---|---|
| id | String | [1] | 805 | deterministic per kind |
| label | String | [1] | 805 | |
| shortLabel | String | [0..1] | 805 | |
| status | ObservationStatus | [1] | 805 | |
| sourceSystem | String | [1] | 805 | Wikidata, Perseus, Gutenberg, PeriodO, … |
| sourceRevision | String or Integer | [1] | 805 | mixed types in the live graph (§6) |
| retrievedAt | String | [1] | 805 | |
| contentHash | String | [1] | 805 | |
| rawPayloadUri | String | [1] | 805 | payload kept outside Neo4j |
| sourceUri | String | [0..1] | 348 | |
| observationKind | ObservationKind | [0..1] | 347 | absent on Wikidata statement observations |
| **Statement observations** (Wikidata) | | | | |
| sourceEntityId | String | [0..1] | 471 | the statement's item |
| predicateExternalId | String | [0..1] | 458 | |
| predicateExternalLabel | String | [0..1] | 1 | |
| objectExternalId | String | [0..1] | 415 | |
| externalStatementId | String | [0..1] | 458 | |
| qualifierPropertyIds | List<String> | [0..1] | 457 | |
| statementQualifiers | String | [0..1] | 456 | serialized qualifiers |
| statementTimeEdtf, statementTimeDisplay, statementTimeCalendar, statementTimeMode | String | [0..1] | 81 | the statement's time, normalized |
| statementTimeRenormalizedAt, …From, …Basis | String | [0..1] | 8 | |
| **Passage and transcription observations** | | | | |
| workTitle | String | [0..1] | 347 | |
| author | String | [0..1] | 346 | |
| translator | String | [0..1] | 159 | |
| editionCitation | String | [0..1] | 347 | |
| language | String | [0..1] | 347 | |
| rights | String | [0..1] | 347 | |
| locator | String | [0..1] | 347 | |
| locatorType | String | [0..1] | 0 | *designed*: page or Kindle location |
| passageText | String | [0..1] | 347 | without editorial notes |
| editorialNotes | List<String> | [0..1] | 347 | kept apart from the text |
| passageHash | String | [0..1] | 347 | |
| capturedBy, capturedAt, visibility | String | [0..1] | 0 | *designed*: transcriptions ([23](23-NARRATIVE-AND-NOTES.md) §7) |

### 2.6 AuthorityRecord (287)

An external record or identifier. It identifies the record; it does not
accept the record's data locally. Unique: `id`; unique: `(system, identifier)`.

| Property | Type | Mult. | Live | Notes |
|---|---|---|---|---|
| id | String | [1] | 287 | `chr:authority:<system>:<identifier>` |
| system | AuthoritySystem | [1] | 287 | |
| identifier | String | [1] | 287 | |
| label | String | [1] | 287 | read from the record |
| shortLabel | String | [0..1] | 287 | |
| description | String | [0..1] | 188 | the authority's wording, not a local description |
| retrievedAt | String | [1] | 287 | |
| sourceRevision | Integer | [0..1] | 284 | |
| sourceUri | String | [0..1] | 286 | |
| contentHash | String | [1] | 287 | |
| rawPayloadUri | String | [1] | 287 | |
| license | String | [0..1] | 1 | |
| formerId | String | [0..1] | 10 | before a system rename (migration 007) |
| mergedIds | List<String> | [0..1] | 1 | records merged into this one |

### 2.7 Annotation (920)

Commentary, never a claim. Freely deletable. Unique: `id` (migration 003).

| Property | Type | Mult. | Live | Notes |
|---|---|---|---|---|
| id | String | [1] | 920 | |
| kind | AnnotationKind | [1] | 920 | |
| noteType | NoteType | [1] | 920 | |
| label | String | [1] | 920 | what it is and where, never what it says |
| note | String | [1] | 920 | the content |
| author | String | [1] | 920 | |
| visibility | Visibility | [1] | 920 | |
| status | AnnotationStatus | [1] | 920 | |
| createdAt | String | [1] | 920 | |
| decidedAt, decidedBy | String | [0..1] | 117 | endorsement or dismissal |

### 2.8 Year (4,025)

The temporal backbone, −2000 to 2025, no year zero. Unique: `year`.

| Property | Type | Mult. | Live | Notes |
|---|---|---|---|---|
| year | Integer | [1] | 4025 | canonical; unique |
| label | String | [1] | 4025 | "31 BCE" |
| iso8601_start, iso8601_end | String | [1] | 4025 | |
| temporal_backbone | Boolean | [1] | 4025 | |
| year_value | Integer | [1] | 4025 | legacy; equals `year`; new writes must not use it |
| created | DateTime | [1] | 4025 | legacy operational metadata |

### 2.9 Location (505,546)

The gazetteer: Pleiades (42,399) and GeoNames (463,147), loaded 2026-10-14/15.
Unique: `id`; unique: `(system, identifier)`; point index on `location`.

| Property | Type | Mult. | Live | Notes |
|---|---|---|---|---|
| id | String | [1] | 505546 | |
| system | LocationSystem | [1] | 505546 | |
| identifier | String | [1] | 505546 | |
| dataset | String | [1] | 505546 | the dump, its date and hash |
| kind | String | [1] | 505546 | Pleiades place type or GeoNames feature code |
| label | String | [1] | 505546 | |
| location | Point | [0..1] | 497961 | absent for unlocated Pleiades places |
| names | List<String> | [0..1] | 27282 | Pleiades |
| nameAttestations | List<String> | [0..1] | 27282 | Pleiades |
| placeTypes | List<String> | [0..1] | 42398 | Pleiades |
| population | Integer | [0..1] | 146417 | GeoNames |

## 3. Entity kinds (generalization)

`Entity.kind` partitions Entities, `{complete, disjoint}`. Kinds are not Neo4j
labels: they are a property and a list in the predicate registry
(`entityKinds`). Some associations are restricted to one kind.

```mermaid
classDiagram
    direction TB
    class Entity {
        kind : EntityKind [1]
    }
    Entity <|-- Person
    Entity <|-- Event
    Entity <|-- Place
    Entity <|-- Group
    Entity <|-- Work
    Entity <|-- Office
    Entity <|-- Period
    Entity <|-- Polity
    Entity <|-- Concept
    Entity <|-- Type
    Entity <|-- Object
    Entity <|-- Other
    class Work {
        form : WorkForm [0..1]
    }
    Place "0..*" --> "0..*" Location : AT_LOCATION
    SourceObservation "0..*" --> "0..1" Work : IN_WORK
    Assertion "0..*" --> "0..1" Work : ATTRIBUTED_TO
```

| Kind | Live (proposed / provisional / resolved) | Holds |
|---|---|---|
| Event | 470 / 0 / 1 | battles, wars, narrative steps |
| Person | 81 / 16 / 0 | |
| Work | 43 / 6 / 0 | sources and depictions; carries `form` |
| Place | 23 / 1 / 0 | the only kind linked to Location |
| Group | 8 / 11 / 0 | fleets, armies, factions |
| Office | 19 / 0 / 0 | positions and posts; the default role kind |
| Period | 3 / 0 / 0 | |
| Polity | 3 / 0 / 0 | states |
| Concept | 0 / 3 / 0 | analytical ideas and frames |
| Type | 0 | unit types, organizational patterns, roles, powers |
| Object, Other | 0 | |

Kind restrictions that hold in the stored graph:

- `ATTRIBUTED_TO` and `IN_WORK` target a Work.
- `AT_LOCATION` starts at a Place.
- `ASSERTION_CONTEXT` targets the predicate's `contextKinds` (Event by default).
- `ASSERTION_ROLE` targets the predicate's `roleKinds` (Office by default).
- `ASSERTION_SUBJECT` and `ASSERTION_OBJECT` follow the predicate's
  `subjectKinds` and `objectKinds` (§5).

## 4. Associations

**Mult. (src → tgt)** reads: how many sources per target node → how many
targets per source node. **Observed** gives the live count and the largest
fan-out seen (out = per source node, in = per target node).

| Relationship | From → To | Mult. (src → tgt) | Properties | Live | Observed max out / in |
|---|---|---|---|---|---|
| ASSERTION_SUBJECT | Assertion → Entity | 0..* → 1 | | 1718 | 1 / 217 |
| ASSERTION_OBJECT | Assertion → Entity | 0..* → 0..1 | | 1530 | 1 / 233 |
| ASSERTION_CONTEXT | Assertion → Entity | 0..* → 0..1 | | 69 | 1 / 69 |
| ASSERTION_ROLE | Assertion → Entity | 0..* → 0..1 | | 0 | *designed* |
| ATTRIBUTED_TO | Assertion → Entity (Work) | 0..* → 0..1 | | 1339 | 1 / 352 |
| IN_YEAR | Assertion → Year | 0..* → 0..* | as [0..1] | 424 | 103 / 13 |
| SUPERSEDED_BY | Assertion → Assertion | 0..* → 0..* | | 8 | 1 / 1 |
| PROMOTED_FROM | Assertion → Assertion | 0..* → 0..* | | 6 | 2 / 1 |
| SUPPORTED_BY | Assertion → SourceObservation | 0..* → 0..* | quotation, qualifierQuotations, addedByProposal [0..1] | 125 | 7 / 10 |
| PROPOSES | Proposal → Assertion | 1..* → 1 | | 1929 | 1 / 10 |
| PROPOSES_EVIDENCE | Proposal → SourceObservation | 0..* → 0..1 | quotation, qualifierQuotations, migratedBy [0..1] | 1926 | 1 / 38 |
| IN_WORK | SourceObservation → Entity (Work) | 0..* → 0..1 | | 347 | 1 / 97 |
| HAS_AUTHORITY_RECORD | Entity → AuthorityRecord | 1..* → 0..* | role, relation, status [1]; statementRank, statementReferences [0..1] | 286 | 13 / 1 |
| HAS_AUTHORITY_RECORD | Subject → AuthorityRecord | 1..* → 0..* | (as above) | 2 | 2 / 1 |
| HAS_SUBJECT_FOCUS | Subject → Entity | 0..* → 1..* | | 1 | 1 / 1 |
| BROADER | Subject → Subject | 0..* → 0..* | | 0 | *designed*; several parents allowed |
| ANNOTATES | Annotation → SourceObservation | 0..* → 0..1 | quotation [1] | 909 | 1 / 12 |
| CONCERNS | Annotation → Entity | 0..* → 1..* | | 1364 | 5 / 244 |
| IN_YEAR | Entity → Year | 0..* → 0..* | as [0..1] | 1 | 1 / 1 |
| FOLLOWED_BY | Year → Year | 0..1 → 0..1 | created [0..1] (legacy) | 4024 | 1 / 1 |
| AT_LOCATION | Entity (Place) → Location | 0..* → 0..* | status, basis [1] | 12 | 2 / 1 |
| WITHIN | Location → Location | 0..* → 0..* | tree, relation [1]; periods [0..1] | 466494 | 7 / 9039 |
| MODERN_LOCATION | Location → Location | 0..* → 0..* | how [1]; viaId, viaLabel, distanceKm [0..1] | 34673 | 5 / 327 |

Multiplicity notes:

- **ASSERTION_SUBJECT [1]**: every Assertion has exactly one subject
  (confirmed live). Doc 02 also allows a Subject as an assertion subject and a
  Subject or AuthorityRecord as an object; no live Assertion uses that.
- **ASSERTION_OBJECT [0..1]**: unary predicates (`occurred`, `born`, `died`)
  have none; every other predicate has one. No unary claim carries an object.
- **ATTRIBUTED_TO [0..1]**: required when `mode = attributed` (all 1,339
  attributed claims have one), absent when `asserted`.
- **PROPOSES 1..* → 1**: every Proposal proposes exactly one Assertion, and
  every Assertion has at least one Proposal (its `create`, then any
  `addEvidence`).
- **PROPOSES_EVIDENCE [0..1]**: one evidence item per Proposal by design;
  three `create` Proposals have none.
- **SUPPORTED_BY** is written only when a Proposal is accepted, from that
  Proposal's pending evidence.
- **IN_YEAR from Assertion** is a projection derived from the time qualifier
  and rebuildable; `as` says which part of the span the Year is (`start`,
  `end`, `during`, `earliest`, `latest`). The one **IN_YEAR from Entity** is
  the Phase 2 *Battle of Actium → 31 BCE* link, due to be replaced by a
  sourced claim.
- **HAS_AUTHORITY_RECORD**: an AuthorityRecord is normally held by one node;
  one LCSH record is shared by an Entity and a Subject, as
  [28](28-SUBJECT-BUCKETS.md) §4 intends. No AuthorityRecord is orphaned.
- **SUPERSEDED_BY 0..***: a superseded Assertion may be replaced by several
  more precise ones; live cases have one.
- **ANNOTATES [0..1]**: a passage-of-note annotates its passage; 11
  entity-mention Annotations have none.
- **CONCERNS 1..***: every Annotation concerns at least one Entity.

## 5. Assertion types: the predicate registry

The registry (`predicates-v11`) is the typing layer over `Assertion`: each
predicate fixes the kinds at both ends, the claim category, the allowed
modes, and the qualifier multiplicities. Qualifier multiplicity: **none** =
[0], **opt** = [0..1], **req** = [1], **withRole** = [1] when a role is given.
Modes: A = asserted, T = attributed.

| Predicate | Subject kinds → Object kinds | Cat. | Modes | Context | Role | Time | Live |
|---|---|---|---|---|---|---|---|
| participatedIn | Person, Group, Polity → Event | F | A T | none | opt | opt | 718 |
| partOf | Event, Group, Type → Event, Group, Type (paired) | F | A T | none | none | opt (+ quantity opt) | 165 |
| occurred | Event, Period, Polity → (unary) | F | A T | opt | none | req | 137 |
| happenedBefore | Event → Event | F | A T | none | none | none | 126 |
| describedBy | any kind → Work | F | A T | none | none | none | 95 |
| triggeredBy | Event → Event | F | A T | none | none | none | 88 |
| siblingOf | Person → Person | F | A T | none | none | none | 60 |
| childOf | Person → Person | F | A T | none | none | none | 58 |
| occurredAt | Event → Place | F | A T | none | none | none | 57 |
| commanded | Person → Group | F | A T | opt | opt | withRole | 52 |
| born | Person → (unary) | F | A T | none | none | req | 32 |
| heldPosition | Person → Office | F | A T | none | none | req | 30 |
| spouseOf | Person → Person | F | A T | none | none | req | 22 |
| died | Person → (unary) | F | A T | none | none | req | 19 |
| heldAuthorityOver | Person → Group | F | A T | opt | opt | req | 10 |
| bornAt | Person → Place | F | A T | none | none | none | 10 |
| diedAt | Person → Place | F | A T | none | none | none | 9 |
| opposed | Person, Group, Polity → Person, Group, Polity | F | A T | opt | none | req | 9 |
| ledTo | Event → Concept, Event, Group, Period, Place, Polity | I | T | none | none | none | 5 |
| exemplifies | Event, Group, Person, Polity, Work → Concept | I | T | none | none | none | 4 |
| distinctFrom | any kind → any kind | F | A T | none | none | none | 4 |
| resultedIn | Event → Event | F | A T | none | none | none | 3 |
| alliedWith | Person, Group, Polity → Person, Group, Polity | F | A T | none | none | req | 3 |
| authorOf | Person → Work | F | A T | none | none | opt | 2 |
| depictsSameAs | Event → Event | I | A | none | none | none | 0 |
| subperiodOf | Period → Period | F | A T | none | none | none | 0 |
| followedBy | Period → Period | F | A T | none | none | none | 0 |
| instanceOf | Group → Type | F | A T | none | none | opt | 0 |
| precedes | Office → Office | F | A T | none | none | req | 0 |
| electedBy | Office → Group | F | A T | none | none | req (+ quantity opt) | 0 |
| exercisedPower | Office → Type | F | A T | none | none | req | 0 |
| heldPower | Person → Type | F | A T | opt | opt | req | 0 |
| servedUnder | Person → Person | F | A T | opt | opt | req | 0 |
| memberOf | Person → Group | F | A T | none | opt | req | 0 |

The qualifiers map onto the model: **context** is `ASSERTION_CONTEXT`,
**role** is `ASSERTION_ROLE`, **time** is the `time*` and `*Jdn` properties
with their derived `IN_YEAR` links, **quantity** is the `quantity*`
properties. Category: F = factual, I = interpretive; any claim attributed to
a Work of a creative form becomes `imaginative`, derived, never chosen.

## 6. Enumerations

| Enumeration | Values | Live |
|---|---|---|
| EntityKind | Person, Event, Place, Group, Object, Work, Period, Office, Concept, Polity, Type, Other | 9 used |
| EntityStatus | proposed, provisional, resolved, deprecated | proposed 650, provisional 37, resolved 1 |
| SubjectStatus | candidate, provisional, validated, deprecated, merged | provisional 1 |
| AssertionStatus | proposed, accepted, rejected, contested, superseded | proposed 1641, accepted 68, superseded 8, rejected 1 |
| ClaimCategory | factual, interpretive, imaginative | 1690 / 9 / 19 |
| ClaimMode | asserted, attributed | 85 / 1339 (294 unset) |
| ProposalOperation | create, addEvidence (02 also lists update, link, reject) | 1718 / 211 |
| ProposalStatus | submitted, validating, accepted, rejected, deferred | submitted 1774, accepted 125, rejected 30 |
| ReasonCode | false, unsupported, malformed, underspecified, superseded-by-model | unsupported 14, superseded-by-model 8 |
| ObservationKind | passage, record, transcription (Wikidata statements: unset) | passage 334, record 13 (PeriodO) |
| ObservationStatus | observed, superseded | observed 805 |
| AnnotationKind | passage-of-note, entity-mention | 377 / 543 |
| NoteType | interpretation, motive, characterization, anecdote, detail, atmosphere, speech, omen | |
| AnnotationStatus | flagged, endorsed, dismissed | 803 / 117 / 0 |
| Visibility | private, team, public | 849 / 71 / 0 (Annotations) |
| TimePrecision | year, month, day (and coarser) | 94 / 2 / 14 |
| TimeMode | during, within | 86 / 9 |
| WorkForm | history, biography, chronicle, letters, speech, inscription, commentary, reference, dataset; creative: poem, play, novel, short story, film, television series, painting, sculpture, opera, song, video game | |
| AuthoritySystem | Wikidata, VIAF, GND, DPRR, Nomisma, FAST, LCNAF, LCSH, Trismegistos, GeoNames, Pleiades, TGN | Wikidata 193 … |
| AuthorityLink.role | entity_identity, crosswalk, subject_access (02 reserves faceted_subject_access, classification_correspondence, place_gazetteer, period_definition, object_type) | 193 / 93 / 2 |
| AuthorityLink.relation | closeMatch (exactMatch only with scope, type, and evidence) | closeMatch 288 |
| LocationSystem | Pleiades, GeoNames | 42399 / 463147 |
| WITHIN.tree / relation | modern: admin; ancient: part_of_physical, part_of_regional, part_of_admin, part_of_analytical, in_territory_of | |
| MODERN_LOCATION.how | nearest place, pleiades reference | 33164 / 1509 |
| IN_YEAR.as | start, end, during, earliest, latest | |

## 7. Constraints and indexes (live)

| Constraint | Label | Property |
|---|---|---|
| entity_id_unique | Entity | id |
| subject_id_unique | Subject | id |
| assertion_id_unique | Assertion | id |
| proposal_id_unique | Proposal | id |
| source_observation_id_unique | SourceObservation | id |
| authority_record_id_unique | AuthorityRecord | id |
| authority_record_system_identifier_unique | AuthorityRecord | (system, identifier) |
| annotation_id_unique | Annotation | id |
| year_year_unique | Year | year |
| location_id_unique | Location | id |
| location_system_identifier_unique | Location | (system, identifier) |

Each constraint carries its range index. One extra index: `location_point`
(point, `Location.location`).

Rules the database does not enforce, held by the guarded operations in
[13](13-PHASE-3-DIRECT-OPERATIONS.cypher): the multiplicities in §4, kind
restrictions in §3 and §5, status transitions, immutability of source facts,
of an Entity's `kind`, and of an Assertion's predicate and endpoints.

## 8. Observations from the profile

Points the curator may want to decide on; none is changed here.

1. **`Assertion.mode` is unset on 294 claims.** [22](22-CLAIM-QUALIFIERS.md)
   §10 says existing claims are `asserted`; the property was not back-filled.
   Since mode is part of identity, the model treats it as [0..1] for now.
2. **`SourceObservation.sourceRevision` has two types**: Integer (Wikidata
   revisions) and String (text edition hashes). The model shows it as one
   property with a union type.
3. **`Year.year_value` and `Year.created`** remain legacy; the open question
   in [00](00-NEO4J-SCHEMA-SNAPSHOT.md) still stands.
4. **31 SourceObservations are unused**: 30 Wikidata statement observations
   and one passage with no Proposal, support, or Annotation.
5. **Two Entities are isolated**: one Work and one Person with no
   relationship at all.
6. **Subject buckets are not built yet**: one Subject, no `BROADER`, and
   no stored-placement relationship. [28](28-SUBJECT-BUCKETS.md) §3.4 calls for
   one but does not name it.
