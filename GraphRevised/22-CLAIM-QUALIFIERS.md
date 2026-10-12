# Claim Qualifiers and Claim Mode

**Status:** agreed with the curator, 2026-10-12 (decisions in §12). Implementation in progress (§11).
**Covers:** the qualifier work in [19 §5a](19-SESSION-HANDOFF.md) (event
context, role), Phase 7 temporal qualification
([04 §9](04-IMPLEMENTATION-PLAN.md)), and the claim mode of E12, as one
mechanism.

## 1. Why one design

Three planned additions all refine what a claim says:

- **context:** in which event ("at Actium");
- **role:** as what the person acted (*legatus*, consul);
- **time:** when, at whatever precision the source gives.

A fourth, **mode**, says whose claim it is: Chrystallum's own (asserted) or a
source's depiction ("according to Plutarch"). Mode matters as soon as a second
source is read: Plutarch, Dio, Velleius, and the Augustan poets will differ on
roles, dates, and who did what. The design assumes several sources from the
start, so competing accounts coexist as separate claims instead of
overwriting each other.

## 2. What a qualified claim looks like

The Assertion stays the reified relationship (the intermediate node). The
qualifiers hang off it. The example is illustrative; whether Dio gives
Agrippa a role or a date is for the reader to find:

```text
(:Assertion {
   predicate: commanded,
   mode: attributed,
   timeEdtf: "-0030-09-02", timePrecision: day, timeCalendar: julian,
   timeSourceExpression: "...", timeNormalizationBasis: source,
   startEarliestJdn: ..., startLatestJdn: ..., endEarliestJdn: ..., endLatestJdn: ...
})
  ─ ASSERTION_SUBJECT → Agrippa
  ─ ASSERTION_OBJECT  → left wing of Octavian's fleet
  ─ ASSERTION_CONTEXT → Battle of Actium                (Event)
  ─ ASSERTION_ROLE    → legatus                          (Entity, kind Other)
  ─ ATTRIBUTED_TO     → Cassius Dio, Roman History       (Entity, kind Work)
  ─ SUPPORTED_BY      → passage observation(s), with quotations
  ─ IN_YEAR           → Year -31                         (derived, for navigation)
```

All four qualifiers are optional in general; the predicate registry says
which each predicate allows or requires (§7).

## 3. Identity

**Qualifiers are part of the claim's identity and fixed at creation**, like
the predicate and endpoints today. A claim with a different role, time,
context, or attribution is a different claim with its own evidence.

- Unqualified asserted claims keep the current ID form,
  `chr:assertion:<subject>:<predicate>:<object>`, so the 19 existing claims
  keep their IDs.
- A qualified claim appends a digest of its canonical qualifiers:
  `chr:assertion:<subject>:<predicate>:<object>:q<10 hex>`. The digest covers
  mode, attributedTo, context, role, and the normalized time (EDTF value and
  calendar), serialized canonically. Labels carry the readable form.
- Agreement accumulates evidence: two passages that support the same
  qualified claim are two pieces of evidence on one Assertion.
- A coarser claim and a finer one ("31 BCE" and "2 September 31 BCE") are
  different claims. They are compatible, not contradictory; the coarser one
  may be superseded with reason `underspecified`, or kept.
- Conflicting claims (different days, different roles) coexist. Marking them
  `contested` is E8 and outside this design, which must only not block it.

## 4. Claim mode

| Mode | Means | Accepting it means |
|---|---|---|
| `asserted` | Chrystallum claims it happened | the evidence establishes it |
| `attributed` | a source depicts it | the claim accurately captures what that source says |

- An attributed claim links `ATTRIBUTED_TO` one Work entity. Its evidence must
  be passages from that Work (checked mechanically, §8).
- Each source keeps its own narrative. "According to Plutarch" and "according
  to Dio" are separate claims even when they say the same thing.
- **Promotion never mutates a claim.** Because mode is part of identity, an
  attributed claim stays true forever (Plutarch does say it). Promotion
  creates the corresponding asserted claim through a curator-authored
  Proposal whose basis names the corroboration (independent witnesses,
  scholarly consensus), and links it `PROMOTED_FROM` the attributed claims.
  Promotion is a curator decision ([21](21-REVIEW-DELEGATION.md)).
- Wikidata statements are aggregator evidence, not a narrative: they support
  asserted claims only, as now.

**Work entities.** Mode requires Works as Entities (`kind: Work`): the work,
not a translation or edition (*Life of Antony*, not Perrin's Loeb). The
author is a Person linked by a new `authorOf` predicate (Person → Work, time
optional: composition date). A passage observation links to its Work with a
new `(:SourceObservation)-[:IN_WORK]->(:Entity {kind: Work})`; the edition
stays on the observation, as now.

## 5. Context and role

**Context** (`ASSERTION_CONTEXT → Entity {kind: Event}`): the event within
which the relationship holds. Most forces in the graph are already
event-specific ("Octavian's fleet at Actium"), so context matters most for
durable objects: a legion, a person's office, an alliance.

**Role** (`ASSERTION_ROLE → Entity`): the office or post the person acted in,
per [docs/Response - Roman Republican Army Structure.md](docs/Response%20-%20Roman%20Republican%20Army%20Structure.md).
Role entities use `kind: Other`, like the offices `heldPosition` already
points to, so command claims and career claims meet at one node. The label is
the source's term; glosses are aliases. Legal basis (*imperium*) is not a
role and is not modelled here.

## 6. Time

### Values

| Property | Holds |
|---|---|
| `timeEdtf` | the normalized value in EDTF (ISO 8601-2), astronomical year numbering: 31 BCE is `-0030` |
| `timePrecision` | day, month, season, year, decade, century, circa |
| `timeCalendar` | the calendar of the normalized value: `julian` (proleptic before 45 BCE) or `gregorian` |
| `timeSourceExpression` | the source's own wording, verbatim ("on the fifth day", "in the consulship of …") |
| `timeNormalizationBasis` | who made the normalized value: `source` (the source gives the date), `scholarship` (a cited modern conversion), or `curator` |
| `start/end Earliest/Latest Jdn` | four sortable bounds as Julian Day Numbers, derived from `timeEdtf` and `timeCalendar` |

- **Spans** have a start and an end, each with earliest and latest bounds
  ("married between 37 and 36 BCE": the start falls somewhere in two years).
  A point in time has start equal to end.
- **Julian Day Numbers** are calendar-neutral integers, so Julian,
  Gregorian, and converted dates sort and compare together, and day-level
  filtering is an indexed range query.
- **Year links are derived.** The Assertion links `IN_YEAR` to every backbone
  Year its bounds touch (Chrystallum numbering, through the single tested
  conversion function), so year queries and the timeline slider keep working.
  A span longer than a set limit (proposed: 200 years) is refused rather than
  linked.
- **No time is invented.** A source that gives no date yields no time
  qualifier. The reader records `timeSourceExpression` verbatim; it may fill
  `timeEdtf` only when the source itself states a calendar date or year.
  Conversions from consular or regnal years, or from the pre-Julian calendar,
  are separate acts with a cited basis; until then a pre-Julian date stays in
  `timeSourceExpression` only, because only Julian and Gregorian values can be
  computed. The Julian calendar is applied proleptically: the misapplied leap
  years of 45–8 BCE are not modelled. Editorial notes are never the source
  (Perrin's "Sept. 2, 31 B.C." is `scholarship` at best, citing Perrin, and
  never Plutarch).
- **Relative time** ("the fifth day", "the sixth hour") is anchored to the
  context event: `timeSourceExpression` verbatim plus an optional offset as an
  ISO 8601 duration from the anchor (`P4D`, `PT6H`), which orders the E12
  micro-events. Its detail belongs to the E12 pilot.

### Dating an entity

The Phase 2 link *Battle of Actium → 31 BCE* is direct and unsourced.
Proposal: a **unary** dated-existence predicate, `occurred` (Event, no
object), whose content is its required time qualifier; birth and death gain
optional time on `bornAt` and `diedAt`. `upsert_assertion` must then accept an
Assertion without an object. Once an `occurred` claim is accepted, the Event's
`IN_YEAR` links are derived from it and the unsourced Phase 2 link is
replaced.

## 7. Registry v4

Each predicate declares its qualifiers, replacing `temporalQualification`:

```json
"qualifiers": {"context": "optional", "role": "optional", "time": "required"},
"modes": ["asserted", "attributed"]
```

with `none | optional | required` per qualifier. Proposed values:

| Predicate | context | role | time |
|---|---|---|---|
| `participatedIn` | none | optional | none (the event carries it) |
| `commanded` | optional | optional | required when a role is given; otherwise none |
| `heldAuthorityOver` | optional | optional | required |
| `heldPosition` | none | none | required |
| `spouseOf`, `alliedWith` | none | none | required |
| `occurred` (new, unary) | none | none | required |
| `authorOf` (new) | none | none | optional |
| others | none | none | as now |

**Revised by the curator (2026-10-12): an expected qualifier is a note, not a
gate.** Not every passage dates what it says, and passages that only add
colour still belong in the graph. A draft missing a "required" qualifier is
stored like any other and noted (`undated: heldAuthorityOver expects a time`);
the review listing marks it UNDATED, and the frontier ledger (E16) treats it
as a gap a later source may fill. A dated version from another source is a
separate, finer claim (§3). Vague time phrases in the source's own words are
kept verbatim as time expressions and are never normalized. One exception:
a unary claim such as `occurred` has no content without its time, so it
still waits for one. This supersedes the earlier ruling that event-bound
claims get no exemption.

Wikidata qualifiers stop being a reason to defer: P580, P582, P585, P1319,
and P1326 map to time; P2868 and P3831 (subject or object has role) map to
role. Agrippa's three dated P26 spouse statements become storable.

## 8. Validation

Deterministic checks, added to the existing ones:

1. Each qualifier is allowed for the predicate, and required ones are present.
2. Context is an existing Event; role an existing Entity of kind Other;
   attributedTo an existing Work.
3. **Attributed:** every cited passage observation is `IN_WORK` the
   attributed Work.
4. **Qualifier evidence:** a role or time qualifier from passage evidence
   needs its own verbatim quotation (`qualifier_quotations`, tagged `role` or
   `time`) in a cited passage. `timeSourceExpression` must appear verbatim
   there. Whether the span really shows the role is the curator's judgement.
5. `timeEdtf` parses, its calendar is known, its bounds are consistent, and
   `timeNormalizationBasis` is `source` only when the source expression states
   the date.
6. Wikidata evidence: the statement's qualifiers must match the claim's
   time and role, so a statement cannot evidence a claim with different
   qualifiers.

## 9. Draft schema v4

`proposal-draft-v4` adds `mode`, `attributed_to`, `context_id`, `role_id`,
`time` (`edtf`, `calendar`, `source_expression`, `normalization_basis`,
`relative_offset`), and `qualifier_quotations`. The reader's output gains the
same fields; it may fill only what the target passage states.

## 10. Existing data

No churn while the model is in design ([19 §5a](19-SESSION-HANDOFF.md)):

- The 19 existing Assertions keep their IDs, have no qualifiers, and take
  `mode: asserted`.
- Their Proposals keep their stored schema and registry versions.
- The Phase 2 Actium `IN_YEAR` link stays until an `occurred` claim replaces
  it.

## 11. Implementation order

1. Year-numbering conversion and EDTF parsing to bounds (tested; consider the
   `edtf` library if it handles negative years and the Julian calendar).
2. Registry v4 and draft schema v4.
3. Work entities, `IN_WORK`, and `authorOf`, starting with Plutarch and *Life
   of Antony*.
4. Operations: qualified `upsert_assertion` (including unary), qualifier
   links, derived Year links, `promote` via a curator Proposal.
5. Validator checks §8; live and offline tests with synthetic fixtures.
6. Reader prompt v8 and inquiry guidance for mode, roles, and verbatim time.
7. Rerun on *Antony* 61–68 after source discovery adds a second source
   ([19 §6](19-SESSION-HANDOFF.md)).

### Progress (2026-10-12)

Steps 1, 2, 4, and 5 are implemented and tested (106 tests), with step 3
built and tested on synthetic Works:

- [proposals/temporal.py](proposals/temporal.py): year conversion, EDTF
  parsing to Julian Day Number bounds, display form, the 200-year link limit.
- [predicates.v4.json](proposals/predicates.v4.json) and
  `proposal-draft-v4` ([schema.py](proposals/schema.py)).
- Validator checks §8, except that Wikidata qualifier *values* are not yet
  compared with a claim's: a Wikidata statement offered for a time- or
  role-qualified claim is deferred, and statements carrying qualifiers are
  still deferred rather than flattened. Agrippa's dated marriages therefore
  stay deferred until the statement adapter records qualifier values.
- Operations `upsert_qualified_assertion` (including unary claims),
  `set_pending_qualifier_quotations`, `link_assertion_years`,
  `link_observation_work`, `link_promoted_from`; evidence acceptance copies
  qualifier quotations to `SUPPORTED_BY`.
- `review promote <attributed claim> ... --by --basis`: creates, links, and
  accepts the asserted claim in one transaction.

Step 3's identity act is done (curator approval, 2026-10-12;
[curation/works.json](curation/works.json)): Plutarch (Person,
Q41523) and *Life of Antony* (Work, Q12902608, local label "Plutarch, Life of
Antony"), the 16 preserved passages linked `IN_WORK`, and *Plutarch author of
Life of Antony* submitted from Wikidata P50 for the curator.

Step 6 is done: reader prompt `passage-reader-v8` drafts attributed claims
(to the inquiry's `source.workId`), takes role, time, and context only as the
passage states them with their own spans, uses the inquiry's
`narrativeEventId` as a context basis, and may draft unary claims; inquiry
v11 separates `commanded` from `heldAuthorityOver`. A one-section dry run
(65.2) produced four valid attributed `commanded` drafts with the narrative
event as context, no role, and no time, and stored nothing. Remaining:
step 7, the rerun.

## 12. Curator decisions (2026-10-12)

All five recommendations were accepted:

1. **The reader's default mode is `attributed`.** A single source's narrative
   is its depiction (E12); asserted claims come by promotion.
2. **Existing accepted claims stay `asserted`**, under the design-mode policy,
   although seven of them rest on Plutarch alone.
3. **A unary `occurred` predicate** dates an event's existence (§6).
4. **Context may rest on the inquiry's declared narrative**, recorded as
   `contextBasis: inquiry`, as well as on a quotation; most passages do not
   repeat the event's name (65.5 never says "Actium").
5. **`commanded` with a role expects a time; without a role it does not.**
   `heldAuthorityOver` always expects one. (Revised the same day: a missing
   expected time no longer defers a claim; see §7.)
