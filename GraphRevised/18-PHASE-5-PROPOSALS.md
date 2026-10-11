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
