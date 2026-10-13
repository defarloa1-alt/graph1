# Phase 5: Bounded Proposal Workflow

## 1. Scope

Phase 5 adds the governed path by which a proposer — a script now, an LLM
agent next — can suggest a new Assertion without being able to write accepted
knowledge:

```text
SourceObservation
  → proposer (deterministic or agent)
  → ProposalDraft (typed; no Cypher, no status, no new entities)
  → deterministic validator
  → stored: proposed Assertion + submitted Proposal
  → curator review (re-validates)
  → validating → accepted | rejected
```

Steps 1–3 of the handoff are complete and tested. The LLM agent (step 4) is
not built yet; see section 8. (Since built: the passage reader, sections 10 onward.
Since 2026-10-13 a stored proposal is visible at once, labelled;
[25](25-LIVES-AND-PLAYGROUND.md) decision 2.)

## 2. Artifacts

| Path | Role |
|---|---|
| [proposals/schema.py](proposals/schema.py) | `ProposalDraft` (`proposal-draft-v1`), Pydantic, extra fields forbidden |
| [proposals/predicates.v1.json](proposals/predicates.v1.json) | Predicate registry `predicates-v1` |
| [proposals/registry.py](proposals/registry.py) | Registry loader and deterministic assertion/proposal IDs |
| [proposals/validator.py](proposals/validator.py) | Deterministic validator; reads only |
| [proposals/store.py](proposals/store.py) | Neo4j reader, `submit`, `accept`, `reject`, `list_proposals` |
| [proposals/review.py](proposals/review.py) | Curator CLI |
| [proposals/wikidata_proposer.py](proposals/wikidata_proposer.py) | Deterministic baseline proposer for Wikidata statements |
| [adapters/wikidata_statements.py](adapters/wikidata_statements.py) | Statement-level SourceObservation from a preserved payload |
| [operations.py](operations.py) | Named access to the Phase 3 Cypher operations |

## 3. ProposalDraft

A draft names a registered predicate, two existing local IDs, at least one
SourceObservation ID, a rationale, and the proposer identity. It may carry
`prompt_version`, `model_id`, and `ambiguities`. It cannot carry labels, IDs
for the new nodes, statuses, or any other field; unknown fields are rejected.

## 4. Predicate registry v1

Thirteen predicates, chosen from statements present in the preserved Actium
and Agrippa payloads, plus two needed by the Actium use case that no current
source states:

| Predicate | Subject → object | Wikidata evidence | Temporal qualification |
|---|---|---|---|
| `participatedIn` | Person/Group → Event | P710 (inverse), P607 | none |
| `commanded` | Person → Group/Event (v2: Person → Group, a force) | — | none |
| `alliedWith` | Person/Group ↔ Person/Group | — | required |
| `occurredAt` | Event → Place | P276 | none |
| `partOf` | Event → Event | P361 | none |
| `bornAt` / `diedAt` | Person → Place | P19 / P20 | none |
| `childOf` | Person → Person | P22, P25, P40 (inverse) | none |
| `spouseOf` | Person ↔ Person | P26 | when present |
| `siblingOf` | Person ↔ Person | P3373 | none |
| `heldPosition` | Person → Other | P39 | required |
| `describedBy` | any → Work | P1343 | none |
| `distinctFrom` | any ↔ any | P1889 | none |

Symmetric predicates (↔) store endpoints in sorted order so both directions
produce one Assertion. `commanded` and `alliedWith` have no Wikidata evidence
mapping, so they cannot be validated until a non-Wikidata source adapter
exists.

## 5. Validation outcomes

| Outcome | Meaning | Stored? |
|---|---|---|
| `valid` | All checks pass | yes |
| `duplicate` | The Assertion already exists; reports whether this evidence is already attached | no |
| `deferred` | Needs temporal qualification (Phase 7) or clarification of a declared ambiguity | no |
| `invalid` | Refused, with every reason listed | no |

Checks: registered predicate; both endpoints are existing Entities of the
permitted kinds and differ; every observation exists, is `observed`, and is a
Wikidata statement observation; **every observation actually states the
claimed relationship** — its property maps to the predicate and its QIDs match
the endpoints' accepted Wikidata identity links. This last check is what
prevents a proposer from citing real evidence for an invented claim.

Statements whose predicate needs qualification are deferred rather than
flattened (architectural invariant 6). Agrippa's three P26 spouse statements
all carry start/end or earliest/latest date qualifiers, so they are deferred
until Phase 7.

The validator runs again inside the write transaction (`submit`) and again at
review time (`accept`), so a stale or changed graph cannot be accepted on an
old validation.

## 6. Identity and provenance

- Assertion ID: `chr:assertion:<subject slug>:<predicate-kebab>:<object slug>`,
  matching the Phase 2 Actium assertion.
- Proposal ID: `chr:proposal:<assertion suffix>:<12-hex digest of schema,
  assertion, sorted observation IDs>`; an identical retry is a no-op.
- Labels are generated from the registry display phrase and endpoint labels;
  proposers do not write them.
- A stored Proposal records `createdBy`, `rationale`, `draftSchemaVersion`,
  `predicateRegistryVersion`, `promptVersion`, and `modelId`.
- Statement observations record `qualifierPropertyIds` so qualification
  decisions are reproducible. The Phase 2 observation predates this property;
  `participatedIn` does not need it.

The proposer never creates entities. A QID with no accepted local identity
link — or with more than one — is reported as unresolved.

## 7. Validation

Four suites, 40 tests, all passing on 2026-10-11:

```text
python -m unittest GraphRevised.tests.test_wikidata_identity \
  GraphRevised.tests.test_direct_operations_live \
  GraphRevised.tests.test_proposals_offline \
  GraphRevised.tests.test_proposals_live
```

The live suites need `NEO4J_PASSWORD` and run in rolled-back transactions; the
database remained at 4,033 nodes and 4,032 relationships.

Replay results:

- **Actium/Agrippa observation:** proposer produces the same draft; outcome
  `duplicate`, evidence already attached, nothing written.
- **Octavian (Q160387 P710 Q1405):** with an Augustus Entity and Wikidata
  identity link in place, the statement observation is built from the
  preserved payload; the proposer drafts *Augustus participated in Battle of
  Actium*; it is stored `submitted`/`proposed`, an identical retry writes
  nothing, acceptance goes through `validating` to `accepted`, and the
  assertion derives *Battle of Actium, 31 BCE*. Reversal is refused.
- **Without the Augustus Entity:** the proposer reports `Q1405 has no local
  Entity` and creates nothing.
- **Invented evidence:** citing Agrippa's observation for Octavian is
  `invalid`.

The statement-observation builder reproduces the Phase 2 observation ID,
content hash, and payload URI exactly.

## 8. Next: the LLM proposer

For Wikidata statements the deterministic proposer is sufficient; an LLM adds
nothing there. Its value is on unstructured evidence — passages, index
entries — where mapping text to a registered predicate needs judgment. The
recommended next step:

1. Add a passage-observation kind (text, locator, source edition, hash).
2. Extend the validator's evidence check for passage observations: the cited
   locator must exist and the draft must quote the supporting span verbatim.
3. Build the agent on the Anthropic SDK with `ProposalDraft` as structured
   output, a versioned prompt, and the bounded context packet from
   [05-AGENT-BOUNDARIES.md](05-AGENT-BOUNDARIES.md).
4. Use the deterministic proposer as an evaluation baseline: on Wikidata
   statements, the agent must reproduce its drafts.

## 9. First claim through the workflow: Octavian at Actium

Persisted on 2026-10-11 by
a slice script (now the `statementProposals` entry of [curation/actium.json](curation/actium.json)), which is idempotent:

- preserved identity payload
  [wikidata-Q1405-r2555830380.json](phase-5-source/wikidata-Q1405-r2555830380.json)
  (SHA-256 `eedf7ab08fe99d5072e34d72a79897bdfa93edb865f64429c4fa679fad75080b`);
- Entity `chr:entity:augustus` (label `Augustus`, Wikidata's preferred label;
  `provisional`) with an accepted Wikidata identity link;
- statement observation
  `chr:observation:wikidata:Q160387:P710:d9469717:r2555342002`, built from the
  already-preserved Phase 2 Actium payload;
- Proposal `chr:proposal:augustus:participated-in:battle-of-actium:a6067452e73c`,
  submitted by the deterministic proposer and accepted by Tony DeFarlo through
  the review CLI.

A second run of the script wrote nothing (`duplicate`). The graph went from
4,033 nodes / 4,032 relationships to 4,038 / 4,037. Actium now has two
accepted participants, Agrippa and Augustus, both derived as
"Battle of Actium, 31 BCE".

As with Agrippa, the Wikidata statement has no references: this is
demonstration-grade evidence. The live tests now use Mark Antony (Q51673) as
the not-yet-persisted participant.

## 10. Passage evidence and the LLM reader (step 4)

### Source

Plutarch, *Antony* 61–68, trans. Bernadotte Perrin (Loeb, 1920), from the
Perseus TEI edition pinned to commit `70427323`:
[phase-5-source](phase-5-source) (SHA-256 `364e99f8…`, metadata sidecar with
rights). The translation is public domain in the US; the TEI markup is
CC BY-SA 4.0 (Perseus, Tufts).

### Passage observations

[adapters/perseus_passages.py](adapters/perseus_passages.py) turns one CTS
section (for example `urn:cts:greekLit:tlg0007.tlg058.perseus-eng2:65.2`) into
a SourceObservation with `observationKind: passage`, the passage text, its
hash, edition citation, rights, and the file hash. **Editorial notes are
excluded from the passage text** and kept in `editorialNotes`: Perrin's inline
"Sept. 2, 31 B.C." is the translator's scholarship, not Plutarch, and must
never be cited as the ancient source.

### Validation of passage evidence

`proposal-draft-v2` adds `quotations`. Every cited passage needs a quotation
that appears verbatim in the passage text. Matching tolerates only whitespace
and curly-versus-straight quotes; a paraphrase, a quote from an editorial
note, or a quote for an uncited observation is `invalid`. Identity of the
people named cannot be checked mechanically; that is the curator's job, and
the reader must explain its identifications in the rationale.

### Adding evidence to an existing claim

Corroboration needed a new governed path. When a draft's Assertion already
exists with new evidence, the outcome is `adds_evidence` and `submit` stores an
`addEvidence` Proposal. The evidence waits on
`(:Proposal)-[:PROPOSES_EVIDENCE {quotation}]->(:SourceObservation)` and becomes
`SUPPORTED_BY {quotation, addedByProposal}` only when a curator accepts it.
An `addEvidence` decision never changes the Assertion's status; rejecting it
leaves the claim untouched.

### The reader

[proposals/passage_reader.py](proposals/passage_reader.py), prompt
`passage-reader-v2`, model `claude-sonnet-5-5` by default (Opus 5.5 via
`--model`). It receives the target passage, two preceding sections and one
following section as context only, the 13 predicates, and the graph's
entities. Its structured output is a list of claims (each with a verbatim
quotation) and unresolved mentions. Anthropic citations cannot be combined
with structured outputs, so verification is the deterministic verbatim check.
Refusal fallbacks are enabled (`fallbacks: "default"`), and each Proposal
records the model that actually answered.

A section's observation is persisted only when one of its drafts is stored.
Every run writes a JSONL trace to [runs/](runs).

### First run (2026-10-11)

36 sections, 93,536 input and 11,526 output tokens (about $0.31). Results: 7
`adds_evidence` drafts stored, 0 invalid, 0 malformed, 0 new assertions
(Antony, Cleopatra, and the other commanders are not yet Entities, so the
reader reported them as unresolved instead of drafting claims about them).
"Caesar" was consistently identified as Augustus in the Actium narrative.
Graph: 4,051 nodes, 4,051 relationships.

| Section | Claim | Quotation | Assessment |
|---|---|---|---|
| 65.2 | Agrippa | "Caesar posted Agrippa on the left, and reserved the right wing for himself." | strong |
| 65.2 | Augustus | same span | strong |
| 65.3 | Augustus | "Caesar, we are told, who had left his tent while it was yet dark and was going round to visit his ships" | weak: before the fighting |
| 65.5 | Augustus | "When Caesar saw this he was delighted, and ordered his right wing to row backwards" | strong |
| 66.1 | Augustus | "while Caesar’s not only avoided dashing front to front against rough and hard bronze armour" | weak: his ships, not him |
| 66.3 | Agrippa | "as Agrippa was extending the left wing with a view to encircling the enemy" | strong |
| 68.1 | Augustus | "at Actium his fleet held out for a long time against Caesar" | strong; names Actium |

Observed weaknesses for the next prompt version: "Caesar" was sometimes listed
as an unresolved mention in sections where it was identified elsewhere, and
participation was twice inferred from the person's fleet or preparations.

### Curator review (2026-10-11)

Decided by Tony DeFarlo through the review CLI, each with a recorded basis:
accepted 65.2 (Agrippa and Augustus), 65.5, 66.3, and 68.1; rejected 65.3
(pre-battle anecdote) and 66.1 (describes Caesar's ships, not Caesar). Both
assertions stayed `accepted` with unchanged `acceptedAt`; the five accepted
passages became `SUPPORTED_BY` evidence with their quotations, and the two
rejected passages remain only as audit history. Agrippa's participation now
rests on Wikidata plus Plutarch 65.2 and 66.3; Augustus's on Wikidata plus
Plutarch 65.2, 65.5, and 68.1. Graph: 4,051 nodes, 4,056 relationships.

## 11. Antony and Cleopatra (2026-10-11)

[slices/add_entity.py](slices/add_entity.py) generalizes curator-approved
identity setup (preserved Wikidata payload, Entity, accepted identity link; no
Assertions). Added `chr:entity:mark-antony` (Q51673, r2553883228) and
`chr:entity:cleopatra` (Q635, r2553821272). Their Wikidata P710 statements were
deliberately not proposed first, so that Plutarch could ground new claims.

Reader reruns on Antony 61–68:

| Prompt | Change | Result |
|---|---|---|
| v3 | Lessons from review: a person's ships or preparations alone do not show participation; a name identified with an entity is not "unresolved" | 1 new claim (Antony, 65.1); 5 duplicates; the two rejected passages were not re-proposed. Missed Antony's flight (66.5) and Cleopatra entirely: the ships rule overcorrected. |
| v4 | Presence during the engagement (commanding, fighting, aboard, fleeing) counts; ships or troops with no sign of the person do not | Antony +2 evidence proposals (65.2, 66.5); 2 drafts self-flagged as ambiguous and deferred (65.4, 66.4); still no Cleopatra claim. |

The v3/v4 rules were tuned on the same chapters they were run on, so these
results overstate performance on unseen text; the next evaluation should use
different chapters. Cleopatra's presence (66.5 "her ship sailing off", 67.1
"raised a signal on her ship") was read by the model as departure rather than
participation; prompt tuning on these chapters was stopped to avoid
overfitting. Graph after the v4 run: 4,061 nodes, 4,066 relationships.

## 12. Inquiry-scoped reading (prompt v5)

Before v5 the reader stayed on topic only by accident: it could name every
Entity in the graph (all Actium-related at the time), and its prompt contained
Actium- and Plutarch-specific rules. That does not hold as the graph grows.

A run is now bound to an inquiry file such as
[inquiries/actium-plutarch-antony.json](inquiries/actium-plutarch-antony.json):
the Subject, the source edition and chapters, declared candidate entities, and
subject- and source-specific guidance. Following the prompt architecture in
[05-AGENT-BOUNDARIES.md](05-AGENT-BOUNDARIES.md), the system prompt is now a
generic role card; the guidance travels in the task packet.

- **Scope** = the Subject's focus, entities linked to the focus by
  non-rejected Assertions, and the inquiry's declared candidates. Only scope
  entities are offered to the model, and a draft naming anything else is
  refused as `out_of_scope` before validation. An inquiry declaring a
  non-existent entity is refused.
- **Relevance**: every claim states in one sentence how it bears on the
  Subject's focus. `proposal-draft-v3` adds `inquiry_id` and `relevance`, and
  both are stored on the Proposal.
- Each run log starts with the inquiry, its version, the Subject, the resolved
  scope, the prompt version, and the model.

A v5 dry run on 65.1, 65.3, 66.5, and 67.1 reproduced the v4 results for
Antony, drafted nothing for 65.3 (consistent with the curator's rejection of
that passage), and for the first time drafted Cleopatra's participation from
66.5, self-deferred because she is explicitly aboard only in 67.1.

## 13. Why the reader does not add people

The reader may not create entities by design (agents propose claims; identity
is a curator decision). Names in a passage are not identities: "Domitius" in
63.2 could be any of several Domitii Ahenobarbi. Unresolved mentions are
logged with name and quotation in every run; the planned identity-resolution
step turns them into a review queue: mention → Wikidata candidate search
(Phase 4 adapter) → curator choice → `add_entity` → reader rerun.

## 14. Full v5 run and two fixes (2026-10-11)

**Ambiguous drafts now reach the curator.** Drafts the reader flags as
uncertain were previously `deferred` and stored nowhere but the run log. They
are now stored as ordinary Proposals with an `ambiguities` property, shown as
UNCERTAIN in the review listing. Only drafts needing temporal qualification
(Phase 7) are still deferred.

**Evidence already awaiting review is a duplicate.** The duplicate check
looked only at attached evidence, and proposal IDs include the draft-schema
version, so the v5 run re-proposed two pieces of Antony evidence (65.2, 66.5)
already open from the v4 run. The validator now treats evidence in an open
addEvidence Proposal as `duplicate`. The two copies were rejected as
bookkeeping ("Claude (duplicate cleanup)", basis naming the original), not as
judgments on the evidence.

The full run (110,492 input / 13,850 output tokens) stored 8 proposals, 2 of
them the duplicates above. New: Augustus `commanded` Actium (65.5); Cleopatra
participatedIn Actium (66.3, flagged uncertain: only her ships are named);
Augustus evidence 65.4; Antony evidence 66.4, 67.2, 68.2.

**Open design issue.** Rejecting a `create` Proposal rejects its Assertion,
and evidence cannot be added to a rejected Assertion. A curator who rejects
weak *evidence* for a claim that may still be true (Cleopatra 66.3) therefore
closes the claim. Rejecting evidence and rejecting a claim need to be
separable, and a rejected claim needs a re-open path (for example
superseding), before such proposals are decided.

### Curator review of the v4/v5 proposals (2026-10-11)

Decided by Tony DeFarlo. Accepted: Antony 65.1 (new claim), 66.5, 67.2;
Augustus 65.4. Rejected: Antony 65.2 (pre-battle, consistent with Caesar
65.3), 66.4 (characterization), 68.2 (after-the-fact report). Left open
pending the design issue above: Cleopatra participatedIn (66.3) and Augustus
commanded Actium (the predicate cannot say which side was commanded).

*Mark Antony participated in Battle of Actium* is the first accepted claim
grounded only in a source text (Plutarch 65.1, 66.5, 67.2), with no Wikidata
statement. Graph: 4,075 nodes, 4,089 relationships.

## 15. Separating evidence decisions from claim decisions (2026-10-11)

The open design issue from section 14 is resolved. Every Proposal, including
`create`, now holds its evidence on `PROPOSES_EVIDENCE` until acceptance.
`reject` rejects the evidence and leaves the claim open; `reject --claim`
rejects the claim; `reopen` returns a rejected claim to `proposed` with a
recorded basis. Accepting stronger evidence for an open claim accepts it.

[Migration 001](migrations/001-pending-evidence-for-open-proposals.cypher)
moved the evidence of the two open create Proposals (Augustus commanded, 65.5;
Cleopatra participatedIn, 66.3) from `SUPPORTED_BY` to `PROPOSES_EVIDENCE`.
Node and relationship counts were unchanged (4,075 / 4,089); a rerun moved
nothing. Two operations were added (`link_pending_evidence`,
`reopen_assertion`), for 20 in total. The suite has 60 tests.

## 16. Hardcoding fixes (2026-10-11)

- The identity queue's prompts had the source ("Plutarch, Life of Antony")
  and period hardcoded. They now come from the inquiry, the edition's metadata
  sidecar, and the Subject focus's year in the graph. A guard test fails if
  reusable code (`proposals/`, `identity/`, `adapters/`) names a particular
  source or subject.
- Prompt versions are now a label plus a digest of the system prompt and the
  code that builds the task packet
  ([proposals/prompt_version.py](proposals/prompt_version.py)), for example
  `passage-reader-v6-006ea47f`. Editing a prompt without bumping its label
  can no longer leave Proposals recording the wrong prompt.

Remaining structural assumptions, to address with the second source: the
reader reads only Perseus TEI addressed by chapter.section; the context window
(two sections before, one after) and the scope rule are fixed in code; entity
context is Wikidata-only and English-only. The Actium slice scripts are
curation written as code and should become data.

## 17. Command split, part 1: registry v3, reason codes, supersession (2026-10-12)

`commanded` conflated authority held with command exercised. At Actium that
hides the central question: Octavian held supreme authority, while much of the
tradition credits Agrippa with directing the fleet.

- **[predicates-v3](proposals/predicates.v3.json)** adds `heldAuthorityOver`
  (Person → Group: formal or supreme authority, whether or not exercised) and
  narrows `commanded` to command actually exercised. Each carries a
  `definition` that the reader sees in its predicate list. They are different
  predicates, so they are different Assertions, and evidence for one never
  counts for the other.
- **`heldAuthorityOver` requires a date span** (`temporalQualification:
  required`), with no exemption for claims tied to an event. Drafts using it
  are `deferred` until Phase 7 and stored nowhere but the run log.
- **Reason codes** — `false`, `unsupported`, `malformed`, `underspecified`,
  `superseded-by-model` — are required on every rejection
  (`review reject --reason`) and recorded as `decisionReason`. Decisions made
  before v3 have none.
- **Supersession** (`review supersede <assertion> --replacement <assertion>
  ... --reason`): a `proposed` or `accepted` claim becomes `superseded` with
  `SUPERSEDED_BY` links to the claims that replace it. Refused for rejected
  claims, claims with open Proposals, self-replacement, and replacements that
  are missing, rejected, or superseded. A retry naming the same replacements is
  a no-op. Superseded claims take no new evidence and leave inquiry scope.
- Reader prompt `passage-reader-v7`: the predicate list now includes
  definitions.
- 21 operations; 70 tests.

**Not yet done:** the claim qualifiers (event context and role; role
replaced `capacity`, see
[docs/Response - Roman Republican Army Structure.md](docs/Response%20-%20Roman%20Republican%20Army%20Structure.md)). The nine held `commanded` proposals were
drafted under v2, when `commanded` still covered authority held; they are
re-validated against v3 on acceptance, but their meaning needs the curator's
judgment against the narrowed definition. While the model is in design they
stay open: claims are not rejected or superseded merely because a predicate
was redesigned.

### Delegated review of the v6 non-command proposals (2026-10-12)

At the curator's request, Claude decided the ten non-command proposals,
recorded as "Claude (delegated by Tony DeFarlo)" with a basis for each. Each
was re-validated against predicates-v3. Accepted: participation of
Poplicola (65.1, 66.3), Insteius (65.1), Arruntius (66.3), Eurycles (67.2,
attacking Antony's fleeing ship), Antony's fleet (66.1, 68.1), and Octavian's
fleet (66.1); and *Battle of Actium occurred at* the Actium promontory (68.1).
Rejected as `unsupported`: Cleopatra 66.3 (only her ships are named); her
claim stays open. Graph: 4,142 nodes, 4,178 relationships.

## 18. Qualified claims (2026-10-12)

The claim-qualifier design ([22](22-CLAIM-QUALIFIERS.md)) is implemented
except the Work identity act and the reader prompt: registry `predicates-v4`
(per-predicate context, role, time, and modes; unary `occurred`; `authorOf`),
draft schema `proposal-draft-v4`, qualifier validation, qualified and unary
Assertions with derived Year links, Works with `IN_WORK`, and promotion from
attributed to asserted claims. Existing claims keep their IDs. 27 operations;
106 tests. Progress and the one deliberate gap (Wikidata qualifier values)
are in 22 §11.

Plutarch and *Life of Antony* became entities (curator approval), the 16
passages were linked `IN_WORK`, and reader prompt `passage-reader-v8` now
drafts claims attributed to the inquiry's source Work, with qualifiers only
as the passage states them (inquiry v11). 114 tests.

## 19. Second source: Cassius Dio in Cary's translation (2026-10-12)

The curator chose Dio's *Roman History* in Earnest Cary's public-domain Loeb
translation (1917) over the Greek text. It is read from LacusCurtius pages
(one per book), preserved byte-for-byte in `phase-6-source/` with their hash,
retrieval time, and the page's own statement that the text is in the public
domain; the pages also say they have not yet been proofread.

- [adapters/lacuscurtius_passages.py](adapters/lacuscurtius_passages.py)
  turns a section (book.chapter.section) into a passage observation; page
  numbers and note markers are left out of the text and the Loeb editor's
  notes are kept per section in `editorialNotes`.
- [adapters/sources.py](adapters/sources.py) is the source interface: the
  inquiry's `source.type` (`perseus-tei` or `lacuscurtius-html`) selects the
  adapter, so the reader no longer assumes Perseus TEI. All 16 stored
  Plutarch observations are byte-identical through it.
- The reader now links each passage it stores to the inquiry's Work, so
  attributed claims from a newly read passage validate.
- Reader prompt: `time_edtf` uses astronomical years (31 BCE is `-0030`), and
  a day and month without a year get no normalized value (Dio 51.1.1 says "on
  the second of September" without the year).
- [inquiries/actium-dio-roman-history.json](inquiries/actium-dio-roman-history.json)
  (v1): Dio 50.11–51.2, with guidance to draft nothing from inside the speeches
  Dio composes for Antony and Caesar (50.16–30).
- [slices/add_work.py](slices/add_work.py): a data-driven version of the
  Plutarch slice for any author and Work.

Pending the curator's identity approval: Cassius Dio (Q185223) and *Roman
History* (Q3974431). 127 tests.

The review led to the interim [delegation policy](21-REVIEW-DELEGATION.md)
and a `retract` operation (accepted → rejected with a reason code, evidence
kept), so a wrong delegated acceptance can be undone. 22 operations; 72
tests.

## 20. Whole-work runs without cues (2026-10-12)

The curator decided that readers locate passages themselves: inquiries name
whole works, and guidance carries no locators or source wording (a test
enforces it). Earlier Dio guidance had quoted the target passage ("on the
second of September") and cited locators; its run is treated as cued.

| Run | Sections | Stored | Duplicate | Deferred | Cost |
|---|---:|---:|---:|---:|---:|
| Dio, *Roman History* 50–51 (v4) | 371 | 5 | 10 | 1 | about $1.10 |
| Plutarch, *Antony* whole Life (v13) | 359 | 33 | 0 | 2 | about $1.40 |

About 92% of input tokens were read from the prompt cache.

- **Passages located independently.** In all 87 chapters of *Antony*, drafts
  came only from chapters 61 and 64–68; in Dio, only from 50.14, 50.31–34,
  51.1, and 51.5: the battle narratives.
- **The cued Dio run is reproduced.** Ten of its claims were drafted again
  without cues (outcome `duplicate`).
- **Dio's own date.** From 51.1.1 the reader drafted *Battle of Actium
  occurred* attributed to Dio, with the time "the second of September" as a
  source expression and no normalized value, as the rules require for a day
  and month without a year.
- **Open issue: vague time expressions.** Three `heldAuthorityOver` drafts met
  the required time with narrative phrases such as "When the forces came
  together for the war" and "after the defeat". They are verbatim and
  validate, but they date nothing.
- Queue after the runs: 64 submitted Proposals (32 attributed
  `participatedIn`, 25 `commanded`, 3 `heldAuthorityOver`, 2 `occurred`, 2
  `authorOf`). Graph: 4,247 nodes, 4,410 relationships.

**Decision: an expected time is a note, not a gate.** The curator ruled that
a claim is not excluded for lacking a date: it is stored, marked UNDATED in
review, and dated later if a source gives a date ([22 §7](22-CLAIM-QUALIFIERS.md)).
Vague time phrases stay as the source's wording. Reader prompt
`passage-reader-v9`; inquiries Plutarch v14, Dio v5. Rerunning the two
Plutarch sections whose authority claims had been deferred stored both
(64.1, and 68.3 as undated); Dio 50.14.1 drafted nothing on the rerun, a
reminder that model output varies between runs. Passages that add colour
but are not claims ("passages of note") are to be designed with E12.

## 21. First interpretations: Weigall and Hale (2026-10-12)

Reader prompt v10 (passages of note) read two public-domain modern works whole,
with the three Concepts in scope.

| Run | Paragraphs | Claims stored | Notes | Cost |
|---|---:|---:|---:|---:|
| Weigall, *The Life and Times of Cleopatra* (1914) | 465 | 31 | 81 (25 interpretation) | about $3.10 |
| Hale, *Famous Sea Fights* (1911) | 847 | 33 | 34 (14 interpretation) | about $3.55 |

- **Located independently.** Weigall's output came almost entirely from
  chapters 15–18, the war; Hale's from chapter 2 (Actium), with three brief
  mentions in later chapters (Actium as a benchmark for galley tactics at
  Lepanto).
- **Interpretive claims** (according to Hale): *Battle of Actium exemplifies
  decisive battle*, with three supporting passages, and *exemplifies East-West
  contest for the Roman Empire*. Weigall's readings came as notes instead.
- **Two `ledTo` drafts were invalid**: the long-range consequence (the
  imperial regime, the Principate) has no entity, so the reader pointed one at
  Augustus (a Person, not allowed) and left one without an object. A Period or
  Concept for the Principate would let these through.
- **"Interpretations of the battle"** now answers from the graph: two Hale
  claims, ten Hale notes, and thirteen Weigall notes, among them Weigall's
  statement that his facts rest on the early authorities while the explanatory
  theories are his own, and his reading that the battle was forced on Antony
  by those who wanted the Egyptians out of his party.
- Cost was about twice the estimate: modern paragraphs are long and the notes
  add output. The Batch API would halve it.
- Queue: 130 submitted Proposals and 115 flagged Annotations.
