---
status: descriptive
authority: 02-GRAPH-MODEL.md
depends_on: [02-GRAPH-MODEL.md, 03-TEMPORAL-YEAR-BACKBONE.md, 27-GAZETTEER.md, 30-LOGICAL-MODEL.md]
superseded_by: null
last_reviewed: 2026-11-03
---

# 36 — Graph Data Dictionary

This is the compact data dictionary for the current clean-start graph. It
describes node labels, properties, and stored relationships. The property
counts are the descriptive snapshot recorded in
[30-LOGICAL-MODEL.md](30-LOGICAL-MODEL.md), not a claim that the live database
has not changed.

## 1. Conventions

- **Required** means the write contract requires the property.
- **Optional** means the property may be absent.
- `Entity` is a shared label. Every domain entity has exactly one approved
  subtype label; the subtype is not stored as `Entity.kind`.
- `kind` remains valid for `Annotation`, `Location`, and in-memory/API
  compatibility vocabularies.
- IDs are stable machine identifiers; `label` is the reader-facing caption.
- A relationship listed as **designed** is part of the model but is not yet
  present in the stored graph.

## 2. Node types

### 2.1 Domain entities

All domain entities carry:

| Property | Type | Requirement | Meaning |
|---|---|---|---|
| `id` | String | Required, unique | `chr:entity:...` |
| `label` | String | Required | Local reader-facing name |
| `shortLabel` | String | Optional | Compact display caption |
| `status` | Enum | Required | `proposed`, `provisional`, `resolved`, `deprecated` |
| `description` | String | Optional | Locally adopted description |
| `sourceNote` | String | Optional | Local provenance note |
| `decidedAt`, `decidedBy`, `decisionBasis` | String | Optional | Curator decision metadata |
| `when`, `where`, `partOf` | String | Derived | Fact-layer display summaries (D-144): one answer with who says it. Display text only, never a date or a claim; rebuilt by `export.fact_layer` |

Approved labels are:

| Node label | Type-specific properties | Meaning |
|---|---|---|
| `Entity:Person` | `gender`, `birthName`, `nameVariants` | Individual person |
| `Entity:Place` | `placeType`, `latitude`, `longitude`, `coordinatePrecision`, `modernCountry` | Historical or geographic place |
| `Entity:Event` | `eventType` | Event, including depicted events and phases |
| `Entity:Group` | `groupType` | Fleet, army, faction, or other collective |
| `Entity:Work` | `workType`, `language`, `form`, `standing` (`primary`, `secondary`, `tertiary`; with `standingSetAt`, `standingSetBy`, `standingBasis`, `standingPrevious`, `standingConfirmedAt`, `standingConfirmedBy`) | Source, text, creative work, or dataset. `standing` (D-148, 42): ancient source, modern study, or reference work; a Work without one counts as reference |
| `Entity:Object` | `objectType`, `material` | Material or physical object |
| `Entity:Period` | `periodType` | Historical interval or framework |
| `Entity:Office` | `officeType` | Position or institutional post |
| `Entity:Concept` | `conceptType` | Analytical idea or frame |
| `Entity:Polity` | `polityType` | State or political entity |
| `Entity:Type` | `typeCategory` | Role, unit type, organizational pattern, power, or status (registry v15 `typeCategories`; set with `set_type_category`, D-141) |
| `Entity:Other` | `otherType` | Domain entity not otherwise classified |

Type-specific properties are intentionally small. Dates, membership,
authorship, ownership, locations, and other source-sensitive facts belong in
Assertions.

Special Event units:

- Depicted event: `chr:entity:depicted:<work>:<slug>`, an event narrated by one
  Work and attributed to that Work.
- Phase: `chr:entity:phase:<event>:<key>`, a Chrystallum-defined event unit.

### 2.2 Subject

Represents an intentional inquiry or knowledge bucket.

| Property | Type | Requirement | Meaning |
|---|---|---|---|
| `id` | String | Required, unique | `chr:subject:...` |
| `label` | String | Required | Subject or bucket name |
| `shortLabel` | String | Optional | Compact display name |
| `status` | Enum | Required | `candidate`, `provisional`, `validated`, `deprecated`, `merged` |

### 2.3 Assertion

Represents a local, reified claim. Its predicate and endpoints are fixed at
creation; a changed claim is a new Assertion.

| Property | Type | Requirement | Meaning |
|---|---|---|---|
| `id` | String | Required, unique | Content-addressed claim ID |
| `predicate` | String | Required | Predicate registry key |
| `label` | String | Required | Generated readable claim |
| `shortLabel` | String | Optional | Compact claim |
| `status` | Enum | Required | `proposed`, `accepted`, `rejected`, `contested`, `superseded` |
| `category` | Enum | Required | `factual`, `interpretive`, `imaginative` |
| `mode` | Enum | Optional | `asserted` or `attributed` |
| `basis`, `basisSetAt`, `basisSetBy` | Enum | Optional | D-148 (42 §3): what an attributed claim of a modern or reference Work is doing: `reports` (retells an ancient source; carries `RESTS_ON`), `reconstructs` (the author's own argument), `unknown` (not traced; not counted) |
| `assertedBy` | String | Required | Drafting agent or person |
| `acceptedAt` | String | Optional | Acceptance time |
| `contextBasis` | String | Optional | Why a context Event was attached |
| `timeSourceExpression`, `timeEdtf`, `timePrecision`, `timeCalendar`, `timeMode` | String/Enum | Optional | Source and normalized time |
| `timeApproximate`, `timeUncertain` | Boolean | Optional | Temporal uncertainty flags |
| `timeNormalizationBasis` | String | Optional | Normalization explanation |
| `startEarliestJdn`, `startLatestJdn`, `endEarliestJdn`, `endLatestJdn` | Integer | Optional | Julian Day uncertainty windows |
| `quantityMinimum`, `quantityMaximum`, `quantityTypical` | Number | Optional/design | Quantity qualifiers |
| `quantitySourceExpression` | String | Optional/design | Source wording for quantity |
| `quantityPrecision` | Enum | Optional | Draft v7, registry v16 (43 §5): `exact`, `approximate`, `round` (set by code when every figure is a multiple of 10 and the draft gives none), `rhetorical` (a reading, reviewed as reasoning); never part of the claim's identity |
| `supersededFrom`, `supersededAt`, `supersededBy`, `supersedeBasis`, `supersedeReason` | String | Optional | Supersession audit |
| `reopenedAt`, `reopenedBy`, `reopenBasis` | String | Optional/design | Reopening audit |
| `retractedAt`, `retractedBy`, `retractBasis`, `retractReason` | String | Optional/design | Retraction audit |

### 2.4 Proposal

Represents a governed requested graph change and its editorial history.

| Property | Type | Requirement | Meaning |
|---|---|---|---|
| `id` | String | Required, unique | Proposal ID |
| `operation` | Enum | Required | `create` or `addEvidence` |
| `label` | String | Required | Requested action in plain language |
| `shortLabel` | String | Optional | Compact action |
| `status` | Enum | Required | `submitted`, `validating`, `accepted`, `rejected`, `deferred` |
| `createdBy` | String | Required | Creator |
| `rationale` | String | Required | Why the change is proposed |
| `draftSchemaVersion` | String | Required | Draft schema version |
| `predicateRegistryVersion` | String | Required | Predicate registry version |
| `promptVersion`, `modelId`, `inquiryId` | String | Optional | Agent provenance |
| `relevance` | String | Optional | Relevance to the inquiry |
| `ambiguities` | List<String> | Optional | Open ambiguities |
| `decidedAt`, `decidedBy`, `decisionBasis`, `decisionReason` | String | Optional | Curator decision |
| `rejectedClaim` | Boolean | Optional | Whether rejection also rejected the claim |

### 2.5 SourceObservation

Preserves a source statement, passage, record, transcription, or image
metadata. Source facts are immutable except for display text and status.

| Property group | Properties |
|---|---|
| Identity and lifecycle | `id` (required, unique), `label` (required), `shortLabel`, `status` (required) |
| Source provenance | `sourceSystem` (required), `observationKind`, `sourceRevision`, `retrievedAt` (required), `contentHash` (required), `rawPayloadUri`, `sourceUri` |
| Access and capture | `visibility`, `capturedBy`, `capturedAt` |
| Wikidata statements | `sourceEntityId`, `predicateExternalId`, `predicateExternalLabel`, `objectExternalId`, `externalStatementId`, `qualifierPropertyIds`, `statementQualifiers`, `statementTimeEdtf`, `statementTimeDisplay`, `statementTimeCalendar`, `statementTimeMode`, `statementStatedIn` (the QIDs its references are "stated in", D-154), `statementReferences` (the references as JSON: stated in, page, URL, name used), and renormalization metadata |
| Passages and transcriptions | `workTitle`, `author`, `translator`, `editionCitation`, `language`, `rights`, `locator`, `locatorType`, `passageText`, `editorialNotes`, `passageHash` |
| Images | `depicts`, `madeBy`, `madeOn`, `collection`, `accession` |

`observationKind` values are `passage`, `record`, `transcription`, and
`image`; Wikidata statement observations currently leave it unset. Images
are provenance records, not claim evidence.

### 2.6 AuthorityRecord

Represents an external identifier record, not accepted local truth.

| Property | Type | Requirement | Meaning |
|---|---|---|---|
| `id` | String | Required, unique | `chr:authority:<system>:<identifier>` |
| `system` | String/Enum | Required | Wikidata, Pleiades, GeoNames, LCSH, FAST, VIAF, GND, etc. |
| `identifier` | String | Required | External key; unique with `system` |
| `label` | String | Required | External record caption |
| `shortLabel` | String | Optional | Compact caption |
| `description` | String | Optional | Preserved authority wording |
| `retrievedAt` | String | Required | Retrieval time |
| `sourceRevision` | Integer | Optional | External revision |
| `sourceUri` | String | Optional | External record URI |
| `contentHash` | String | Required | Preserved-content hash |
| `rawPayloadUri` | String | Required | Raw payload location |
| `license` | String | Optional | Source license |
| `formerId` | String | Optional | Previous identifier |
| `mergedIds` | List<String> | Optional | Merged identifiers |

### 2.7 Annotation

Commentary, never a claim.

| Property | Type | Requirement | Meaning |
|---|---|---|---|
| `id` | String | Required, unique | Annotation ID |
| `kind` | Enum | Required | `passage-of-note`, `entity-mention`, `note`, `image-note`; `path` designed |
| `noteType` | Enum | Optional | Interpretation, motive, detail, observation, question, etc. |
| `label` | String | Required | What/where the annotation is |
| `note` | String | Optional | Commentary content |
| `author` | String | Required | Creator |
| `visibility` | Enum | Required | `private`, `team`, `public` |
| `status` | Enum | Required | `flagged`, `endorsed`, `dismissed` |
| `createdAt` | String | Required | Creation time |
| `decidedAt`, `decidedBy` | String | Optional | Endorsement or dismissal |
| `title`, `body`, `modifiedAt`, `origin`, `filePath` | String | Optional/design | Vault note metadata |
| `quotationStatus` | Enum | Optional/design | Rights/reuse decision |
| `generatedBy` | String; `pathIds` | Optional/design | Saved-path metadata |

### 2.8 Year

The ordered temporal infrastructure, not an Entity or a Period.

| Property | Type | Requirement | Meaning |
|---|---|---|---|
| `year` | Integer | Required, unique | Canonical year; negative is BCE; zero absent |
| `label` | String | Required | For example, `31 BCE` |
| `iso8601_start`, `iso8601_end` | String | Required/legacy | Legacy ISO metadata |
| `temporal_backbone` | Boolean | Required | Marks backbone nodes |
| `year_value` | Integer | Required/legacy | Equal to `year`; do not use in new writes |
| `created` | DateTime | Required/legacy | Creation metadata |

### 2.9 Location

The off-canvas Pleiades and GeoNames geographic backbone.

| Property | Type | Requirement | Meaning |
|---|---|---|---|
| `id` | String | Required, unique | `chr:location:<system>:<identifier>` |
| `system` | Enum | Required | `Pleiades` or `GeoNames` |
| `identifier` | String | Required, unique with system | External key |
| `dataset` | String | Required | Dump/date/hash provenance |
| `kind` | String | Required | Pleiades place type or GeoNames feature code |
| `label` | String | Required | Display name |
| `location` | Point | Optional | Coordinates; point-indexed |
| `names` | List<String> | Optional | Pleiades ancient names |
| `nameAttestations` | List<String> | Optional | Pleiades name attestations |
| `placeTypes` | List<String> | Optional | Pleiades types |
| `population` | Integer | Optional | GeoNames population |

## 3. Stored relationships

Relationship properties are listed after the arrow.

| Type | From → To | Properties | Meaning |
|---|---|---|---|
| `ASSERTION_SUBJECT` | Assertion → Entity | — | Claim subject; exactly one in the current graph |
| `ASSERTION_OBJECT` | Assertion → Entity | — | Optional claim object; absent for unary predicates |
| `ASSERTION_CONTEXT` | Assertion → Entity/Event | — | Predicate context, normally an Event |
| `ASSERTION_ROLE` | Assertion → Entity/Office | — | Predicate role, normally an Office; designed |
| `ATTRIBUTED_TO` | Assertion → Entity/Work | — | Source Work voice for attributed claims |
| `RESTS_ON` | Assertion → Assertion, SourceObservation, or Work | `status`, `createdAt`, `createdBy`, `decisionBasis`, `citation`, `quotation` | D-148: a modern or reference claim's link to the ancient claim or passage it retells. From a citation's own words (a Wikipedia footnote, `harvest.wikipedia_footnotes`), a code-made extraction accepted by rule (D-145, D-150); from an agent's reading, proposed and reviewed as reasoning. Attestation counts the ancient line only when the target is text we hold (a passage or claim); a link to a Work alone is shown, not counted |
| `IN_YEAR` | Assertion → Year | `as` | Derived temporal projection |
| `IN_YEAR` | Entity → Year | `as` | Legacy/initial direct entity-year link |
| *predicate* (`OCCURRED_AT`, `PART_OF`, `PARTICIPATED_IN`, …) | Entity → Entity | `derived: "fact-layer"`, `predicate`, `status`, `mode`, `category`, `attestation`, `sentence`, `when`, `role`, `accordingTo`, `assertions` | Derived fact layer (D-144): one edge per live fact, named after its predicate; rebuilt from the Assertions by `export.fact_layer`, never edited |
| `OCCURRED`, `BORN`, `DIED` | Entity → Year | `derived: "fact-layer"`, `predicate`, `as`, `status`, `accordingTo`, `assertions` | Derived fact layer: a dated unary fact's Year links, lifted to the entity |
| `SUPERSEDED_BY` | Assertion → Assertion | — | Replacement claim(s) |
| `PROMOTED_FROM` | Assertion → Assertion | — | Claim promotion lineage |
| `SUPPORTED_BY` | Assertion → SourceObservation | `quotation`, `qualifierQuotations`, `addedByProposal` | Accepted claim evidence |
| `PROPOSES` | Proposal → Assertion | — | Claim governed by the proposal |
| `PROPOSES_EVIDENCE` | Proposal → SourceObservation | `quotation`, `qualifierQuotations`, `migratedBy` | Pending proposal evidence |
| `IN_WORK` | SourceObservation → Entity/Work | — | Observation belongs to a Work |
| `HAS_AUTHORITY_RECORD` | Entity/Subject → AuthorityRecord | `role`, `relation`, `status`, optional statement rank/reference counts | External identity or crosswalk |
| `HAS_SUBJECT_FOCUS` | Subject → Entity | — | Entities covered by a Subject |
| `HAS_SUBJECT_HEADING` | Work → AuthorityRecord (LCSH, LCNAF) | `status`, `heading` (as the record words it), `observationId`, `createdBy`, `createdAt`, `decisionBasis` | A subject heading the book's LC catalog record assigns (D-155) |
| `BROADER_HEADING` | AuthorityRecord → AuthorityRecord | `status`, `createdBy`, `createdAt`, `sourceIdentifier` | A heading's broader heading, as its LCSH record states (skos broader, or narrower read in reverse; D-155) |
| `RELATED_HEADING` | AuthorityRecord → AuthorityRecord | same | A heading's related heading (skos related; D-155) |
| `NARROWER_THAN` | Subject → Subject | — | Subject hierarchy, narrower to broader |
| `ANNOTATES` | Annotation → SourceObservation | `quotation` | Commentary on a passage, transcription, or image |
| `CONCERNS` | Annotation → Entity | — | Annotation target; wider targets designed |
| `FOLLOWED_BY` | Year → Year | — | Ordered temporal chain |
| `AT_LOCATION` | Entity/Place → Location | `status`, `basis` | Place-to-gazetteer crosswalk |
| `WITHIN` | Location → Location | `tree`, `relation`, optional `periods` | Ancient or modern containment |
| `MODERN_LOCATION` | Location → Location | `how`, optional `viaId`, `viaLabel`, `distanceKm` | Ancient-to-modern bridge |

## 4. Invariants and constraints

- Unique constraints exist for `Year.year`, `Entity.id`, `Subject.id`,
  `AuthorityRecord.id`, `(AuthorityRecord.system, identifier)`,
  `SourceObservation.id`, `Assertion.id`, `Proposal.id`, `Location.id`, and
  `(Location.system, identifier)`.
- Every Entity has exactly one approved subtype label and no stored Entity
  `kind` property.
- `Year` is not `Entity:Period`; the backbone has no year zero.
- `SUPPORTED_BY` and `PROPOSES_EVIDENCE` must not target image observations.
- `ATTRIBUTED_TO` and `IN_WORK` target `Work`; `AT_LOCATION` starts at `Place`.
- Claims enter through Proposals; direct promotion/rejection actions preserve
  their audit metadata.

The read-only integrity check is:

```powershell
python -m GraphRevised.validate_ontology
```
