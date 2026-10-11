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
not built yet; see section 8.

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
| `commanded` | Person → Group/Event | — | none |
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
[slices/octavian_actium.py](slices/octavian_actium.py), which is idempotent:

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

