---
status: draft 2026-11-20, for the curator's choices (§6); built: the local-only guard (§5.1, 2026-11-20)
authority: curator, 2026-11-20 (chat): review the scripts for updates and disposition, above all for where reasoning should be invoked instead of deterministic code
depends_on: [33-DECISIONS.md, 41-ENDGAME-PLAN.md, 42-CORROBORATION-AND-CLAIM-KINDS.md, 44-HISTORIOGRAPHY-AND-DEBATES.md]
superseded_by: null
last_reviewed: 2026-11-20
---

# 47 — Where Reasoning Belongs, and a Review of the Scripts

## 1. Why

The scripts in GraphRevised have grown to about 140 modules since October. Many
of them decide things with word matching: whether two labels name one person,
whether two events are one, whether a footnote supports a sentence. Some of those
decisions are then accepted by rule as if they were extraction. This doc lists
where a model's reading should replace or check the code, what must stay code,
and which scripts need an update or can go.

Only the local-only guard (§5.1) is built. §6 lists the choices that are the curator's.

## 2. The test: extraction or judgement

D-145 accepts by rule what a deterministic proposer draws from structured
records, and sends anything that needs reasoning to the curator. The line
this review draws:

- **Extraction:** the record states the fact, and the code copies it. A
  Wikidata statement, a CRRO coin's metal, an AAT broader concept, an LC
  heading by its identifier. Code is right here, and acceptance by rule is right.
- **Judgement:** the code decides that two things are the same, or that one
  supports the other, from words, position or a name pattern. That is a
  reading, even when the code does it. It should be done or checked by
  reasoning, and its result is a proposal.

A model's output never becomes accepted by itself (D-145, rule 12). Where
reasoning is added below, it either *proposes* (the curator decides) or
*checks* code-made links (what it does not confirm goes to the curator; what it
confirms stays as it is).

## 3. Where reasoning should come in

Ranked by what a wrong answer from the code costs.

| # | Script | What the code does now | Reasoning role |
|---|---|---|---|
| 1 | `harvest/wikipedia_footnotes.py` | links a claim to the passage its following footnote cites; 155 RESTS_ON links, accepted by rule | checks |
| 2 | `discovery/period_survey.py` | treats a PeriodO definition as the same period by head word and region; accepted by rule (13 claims) | checks, or out of rule acceptance |
| 3 | `discovery/event_evidence_report.py` | pairs events sharing two or more words | proposes same-event links and disputes |
| 4 | `identity/local_candidates.py`, `capture/notes.py` suggest | candidates by shared label tokens | wider candidates; a model judges |
| 5 | `discovery/duplicate_review.py` (not called) | near-duplicate Questions and Positions are found only by hand | checks at proposal time |
| 6 | `harvest/apply.py` | a Wikidata item of an unknown class "waits for the agent"; there is no such agent | proposes a kind |
| 7 | `harvest/article_citations.py` | modern works found by a "Name, Title (City, Year)" pattern | proposes the Work |
| 8 | `proposals/predicate_needs.py`, `harvest/lc_record.py` | precedents and author headings by word overlap | proposes, small |

### 3.1 Wikipedia footnotes to passages

**Built and run 2026-11-21 (D-169).** `proposals/rests_on_check.py`: one call per claim with every
passage its footnote linked it to; the words that carry a verdict are verified verbatim in code.
22 live claims, 145 links, $0.43 in all (claude-sonnet-5-5): 17 links state the claim, 17 in part,
111 do not, mostly because a cited range (Plutarch, Antony 65-66) links every section in it. Taken
together, the cited passages state 14 claims and 8 in part. A first prompt judged the stored claim
against Wikipedia's fuller words; its 22 checks were superseded by the corrected ones. All 22 wait
for the curator (CURRENT-STATE §5); no link has changed yet.

**Now.** For each claim attributed to a Wikipedia article, the footnote right
after the claim's quotation is followed to our passage at that locator, and the
claim gets `RESTS_ON` with basis `reports`. The module calls this extraction:
"nothing is inferred, only a footnote's own words are followed."

**Risk.** The footnote's words are followed, but the claim it is tied to is
inferred from position. Wikipedia often notes a whole paragraph at its end, or
a different clause of the sentence, and one of our passages can be a whole
chapter. These links count for attestation (D-148): 15 facts moved from
"reference only" to "attested" through them. A wrong link changes what a reader
is told about the evidence.

**Reasoning.** Keep the code as the finder. A checking pass reads each claim
beside its passage and answers *states it*, *partly*, or *not there*, with the
words that carry it. Links not confirmed go to the curator; confirmed ones keep
their acceptance and record the check. 155 short pairs; the passages are public
domain texts we hold.

### 3.2 Period survey

**Now.** `period-survey` is in `RULE_PROPOSERS`. A PeriodO definition counts as
our period when its label carries the period's head word and adds only a region;
when one authority defines it more than once, the widest span is kept.

**Risk.** That is an identity decision made by a name rule and accepted as
extraction. "Late Republic" in one authority's scheme may cut at a different
event from another's, and the head-word rule cannot tell.

**Reasoning.** Two options (§6): take the matching step out of rule acceptance,
so the 13 claims wait for the curator; or add a check that judges each match
*same*, *related* (broader, narrower, regional) or *different*, with a reason,
and keep rule acceptance only for *same*. The spans themselves, once matched,
are extraction.

### 3.3 Same event, and disputes between sources

**Now.** `event_evidence_report` pairs events that share two or more words of
four letters or more, after a list of common words.

**Risk.** Two open items in CURRENT-STATE §8 depend on this: depicted events
stay one source's units until linked as the same event (`depictsSameAs`), and
disputes across claim families are not found (two sources naming different
commanders). Word overlap cannot do either. "Antony's fleet breaks out" and
"Antonius' ships escape" share almost nothing.

**Reasoning.** A pass over each phase's events (43) proposes `depictsSameAs`
links and flags disputes, each with the passages and a reason. Proposals only.
This adds the most to corroboration, since attestation counts independent lines
of evidence (D-148), and it feeds the consistency checks (41 §3.4). A
contradiction is flagged, not resolved (39 §10).

### 3.4 Entity identity candidates

**Now.** Candidates come from shared label tokens. `surface` reuses an Entity
only through its Wikidata identity. The note reader's model may choose only
among the code's candidates.

**Risk.** Known misses: two Cleopatras look alike, and Octavian is missed under
"Augustus". What the token match misses never reaches the model, so the model's
triage cannot recover it.

**Reasoning.** Widen recall in code: aliases (46), `alternativeNames`, Roman name
parts. Then a model judges *same*, *different* or *cannot tell*, with context,
as `duplicate_review` already does for claims. Merges stay the curator's
(D-152); the model drafts the reason.

### 3.5 Near-duplicate Questions and Positions

**Now.** `discovery/duplicate_review.py` holds the reasoning, but nothing calls
it.

**Risk.** Duplicates have turned up three times: the two Lange aim Questions,
seven overlapping ship Positions, and "Antony fought for victory until
Cleopatra fled" beside "Antonius was fighting to win" (CURRENT-STATE §5).

**Reasoning.** The historiography and article readers call it before storing a
new Question or Position. A likely duplicate is stored marked as one, pointing
at the existing item, not as a fresh one. Question links are kept either way
(re-pointing adds, never replaces).

### 3.6 Items left to "the agent"

**Now.** `harvest/apply.py:135` marks a Wikidata target whose classes its kind
table does not cover `kind unknown: waits for the agent`. Nothing picks these up.
"The 30 linked items Wikipedia's first contact left to the agent" have waited
in CURRENT-STATE §5 since October.

**Reasoning.** A small classifier proposes a kind (or *not ours*) from the
item's classes, description and the passage that led to it, with a reason; the
curator confirms. Its confirmed answers can extend the kind table, so the code
covers more next time.

### 3.7 Citation strings to Works

**Now.** Modern works in article footnotes are found by pattern. Unresolved
holders recur in every reading (Kromayer, Tarn, Syme, Gillies, once as
"Gilles"), and each is resolved by hand.

**Reasoning.** A step parses the footnote and proposes the Work: author, title,
edition, and a match to a Work we hold or to an LC record. It runs where the
licensed page lies, as the article reader does, so licensed text stays out of
git and out of the graph.

### 3.8 Smaller ones

- `proposals/predicate_needs.py` finds precedents by shared words; a model could
  draft "`wentOverTo` is `defectedTo`" with a reason.
- `harvest/lc_record.py` matches an author by the heading's name in direct order;
  a model could judge the hard cases (Roman names, translators).

## 4. What stays code

These are the gates a model's proposals pass through, or are extraction in the
strict sense. Moving them to a model would break the rules they serve.

- **Attestation in words** (`export/confidence.py`, rule 12): computed from the
  voices, never a stored or model-given confidence.
- **Display rules** (`export/display.py`, D-162): one rule for every view.
- **The validator, temporal conversion, the graph type (018), the guarded
  operations (13).**
- **Alias forms by convention** (`proposals/aliases.py`, 46): mechanical, checked
  against our passages.
- **Pure extractors:** CRRO records, the AAT hierarchy, Wikidata statements and
  references, LC headings by identifier.
- **Finders that feed reasoning:** the footnote follower (3.1), the candidate
  search (3.4) and the event pairing (3.3) stay as code. They find, and a model
  judges what they find.

## 5. Updates and disposition

### 5.1 The local-only guard (safety)

`subject_backbone.local_config()` refuses a database address other than the
local one and a database other than `neo4j`. Only 11 modules use it. 70 others
build their connection straight from `NEO4J_URI`: 27 migrations and 43 live
scripts, among them migration 018, migration 019 and the registry sync. The
guard is what keeps a write from reaching Aura or any other server. It also
lives in an untested module and imports the legacy `scripts.config_loader`.

**Built 2026-11-20.** `GraphRevised/localdb.py` is the one guard: `uri()`,
`database()`, `auth()` and `driver()` read the same settings with the same
defaults as before, and refuse a non-local address (Aura or any other server),
credentials in the address, or a database other than `neo4j` (`NotLocal`, a
`ValueError`). All 70 modules, the migrations among them, and the live tests
now go through it; so does the connector, whose fallback to the legacy loader's
values is checked too. `local_config()` keeps reading `.env` through the legacy
loader but checks with `localdb`. `tests/test_localdb.py` covers the refusals
and fails if any module but `localdb` reads `NEO4J_URI` or `NEO4J_DATABASE`
from the environment.

### 5.2 Scripts with no callers

| Script | Disposition |
|---|---|
| `explorer/wireframes/freeze_screens.py` (2026-10-19) | likely obsolete: the wireframe is built from `template.html` and `build.py`; check, then delete |
| `harvest/wikipedia_contact.py` | keep; no importers or tests, but it is where the items of 3.6 come from |
| `explorer/cytoscape_desktop.py` | keep; documented, with open items in `CYTOSCAPE-DESKTOP.md` |
| `discovery/duplicate_review.py`, `discovery/entity_review.py` | keep; wire in (3.4, 3.5) |

### 5.3 Overlaps and gaps

- **`validate_ontology.py`** has no tests, and the graph type now checks part of
  what it does. Keep what 018 cannot check (one subtype per Entity, no year zero,
  an unbroken Year chain), or move those into 018's preflight so there is one
  check.
- **018** hard-codes `SUBTYPES`; a test now holds it to the registry's entity
  kinds (`tests/test_registry_graph.py`). `RELATED_HEADING` is now pinned like
  `BROADER_HEADING` (done 2026-11-21, graph type re-applied).
- **019's** docstring said the rationale came from `decisionBasis`; it is
  written in the migration, spelling that basis out. Docstring fixed 2026-11-21.
- **Migrations 004 to 032** are one-shot records and stay; 032 is committed.
  Gaps in the numbering (008, 022) are expected.
- **`discovery/source_plan.py`, `discovery/inquiry_builder.py`** are October work, still in use.

## 6. The curator's choices

1. **Order.** Proposed: the guard (5.1, done), then 3.1 and 3.3, then 3.5 and 3.4,
   then 3.6 and 3.7.
2. **Period survey (3.2):** take it out of rule acceptance, or add the check?
3. **Footnote check (3.1):** a confirmed link keeps acceptance by rule plus a
   recorded check. Or should every checked link come to the curator?
4. **Paid runs.** 3.1 and 3.3 to 3.7 call a model. Each run needs the curator's
   authorization for scope, provider and budget, as for every paid run.
5. **Where the checks are recorded.** Proposed: a check is a Proposal by the
   checking agent, with its `modelId`, citing the link it checks, so it shows
   in review by bucket (D-166) and can be retracted like any decision.

## 7. Not in this doc

- A per-script inventory (sizes, importers, last commit) was made for this review
  and is not kept; `git log` and a search reproduce it.
- No decision number is claimed. The choices in §6 become a decision when the
  curator makes them.
