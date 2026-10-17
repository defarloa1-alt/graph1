# 31 — One Command: a Methodology for Any Subject

**Date:** 2026-10-16, revised the same day. **Status:** the curator chose this
model (2026-10-16); the contracts are built (§6), nothing else is. §7 items 1
and 2 are settled by the curator's addendum ([32](32-RESEARCH-WORKSPACE.md),
2026-10-17); the others await the curator's veto. §3.8-3.10 added 2026-10-17
from [docs/Source review perplexity.md](docs/Source%20review%20perplexity.md).
**Order:** after Chrystallum's account for the Battle of Actium
([29](29-EVENT-CENTRED-INQUIRY.md) §4), before Hannibal
([19](19-SESSION-HANDOFF.md) §6).
**Builds on:** the curator's notes on agent behaviour and the response to them,
[docs/Chrystallum Agent Workflow ….md](docs/Chrystallum%20Agent%20Workflow%20%20Repository%20State%2C%20Proposed%20Direction%2C%20and%20Recommendations.md)
(the model adopted here); the curator's outline test,
[docs/How to Chapterize a Book on the Battle of Actium.md](docs/How%20to%20Chapterize%20a%20Book%20on%20the%20Battle%20of%20Actium.md);
[29](29-EVENT-CENTRED-INQUIRY.md); [25](25-LIVES-AND-PLAYGROUND.md) §10-13;
[05](05-AGENT-BOUNDARIES.md) (the boundaries that stand); backlog E1, E8, and
acceptance criterion 14 in [04](04-IMPLEMENTATION-PLAN.md).

## 1. Why

The curator (2026-10-16): when development is done and a user wants to
explore ancient Greece, it should not take a person and an agent writing
scripts and logic. A command such as *Graph Alexander the Great* should invoke
one methodology, whatever it names. The system's purpose is to build
subgraphs, not to read works: works are evidence and colour for the subgraph
the user asked for. And the methodology must use the models' reasoning; a run
that only follows fixed rules would need no agents.

The Battle of Actium was built step by step. Most steps are generic code, but
the run was held together by judgement between steps and by files written by
hand ([curation/phases.json](curation/phases.json) is the latest). That
judgement is the methodology, and it is not yet where the system can follow it.

**The claim we make for it** (from the source review): the agent researches a
bounded historical inquiry across approved structured and consultative
sources, reconciles entities, organizes evidence, identifies graph gaps and
disagreements, and proposes provenance-rich additions for curator review. Not:
the agent autonomously researches history and builds an authoritative graph.

## 2. The principle

**Determinism around agents.** Models decide what deserves attention and how
evidence reads: what the command means, which sources and lenses matter, what a
passage shows, whether two claims say the same thing, which phases an event had.
Code decides what may enter the graph and how it is recorded: identifiers,
schemas, predicates and kinds, verbatim evidence, rights, status transitions,
budgets, idempotent writes.

| Models decide | Code enforces | Both |
|---|---|---|
| what the command means; identity candidates | stable ids, schemas | entity resolution |
| federations, sources, lenses worth using | predicate kinds, verbatim quotations | duplicate, refinement, or conflict |
| what a passage shows; source perspective | rights, budgets, stopping | event phases and outlines |
| significance, omissions, uncertainty | status transitions, provenance, writes | when to stop |

## 3. The roles

```text
graph "<anything>"
  1. Front door        scope (08), identity (ask only when ambiguous), Subject anchor, coverage
  2. Orientation       a bounded brief: kind, bounds, candidates, federations, sources, lenses,
                       controversies, identity traps, a stopping rule
  3. Plan              line items with ids, reasons, outputs, budgets, dependencies
  4. Curator           decides per item (guided) or approves the scope (supervised)
  5. Orchestrator      runs the approved items, checkpoints every step in the run file
       workers:        harvester and enrichers by kind, source discoverer and builder,
                       source readers, lens analysts, phases and outline agents
  6. Reconciler        how each candidate claim relates to the graph (§3.5)
  7. Validator, critic deterministic checks first, then an independent critic that advises
  8. Proposals         stored through proposals/, visible at once, labelled
  9. Promotion         the curator (or delegated policy, 21) promotes
```

### 3.1 Front door and orientation

The **front door** classifies the request (in scope, out of scope, reframe),
resolves its identity at Wikidata, ties it to a Subject (an existing one, or a
provisional one labelled as ours with broader and related headings, 28 §6), and
reads what the graph already holds. It proposes nothing to the graph.

The **orientation researcher** (the "general lens" of the curator's notes; a
stage, not a lens) studies the subject broadly but within a budget: Wikidata,
Wikipedia, the registry's catalogues, the graph. Its brief records where each
statement came from, so reconnaissance is never mistaken for evidence. Its
candidate entities and relationship needs are run state, not graph nodes or
claims: that is how "identify the entities and relationships needed" and "do
not propose nodes or claims" both hold.

### 3.2 The plan and the curator

The plan is a list of items with stable ids. A decision or an edit makes a new
plan version and keeps the old. Three modes:

| Mode | Before running | While running | After |
|---|---|---|---|
| guided | the curator decides every item | stops on a deviation from the plan | promotion |
| supervised | the curator approves scope, budget, lenses, sources | stops on ambiguity, cost, rights, or a wider scope | promotion |
| autonomous | the plan is shown and runs | stops at the policy's interrupts | promotion; everything stays proposed |

Guided first, while the planning is young; supervised for routine use later.

### 3.3 Recipes and workers

A recipe is the usual plan for a kind; the front door adapts it, and the
curator sees the result. Recipes are data and name no subject.

| Kind | Usual plan |
|---|---|
| Event | first contact → surfaced entities → source plan → builder (preserve, brief) → finder → readers → lenses → phases → reconcile, critique → outline and account |
| Person | first contact → the person whole, then family (25 §11) → the life's events (§3.4), each an Event sub-inquiry within the budget → readers on the life's own sources → the life's account |
| Polity, period, broad subject | first contact → a constellation of narrower inquiries (07 §3) in the plan → each by its own kind |

**Source readers** read one identifiable Work or corpus and return observations,
depicted events, claims with verbatim evidence, and notes: the reader that
exists. **Lens analysts** take one lens (military, political, economic, …) for
one run: its questions, relevance tests, preferred sources, and expected
relationships; they ask what the readers missed and point the source plan at
gaps. Three pilot lenses first (general significance, military, political); more
only when a query shows the value. **Enrichers** run by kind when an entity
surfaces (25 §11).

### 3.4 Discovered structure

- **A life becomes its events.** For a Person an agent proposes the events of
  the life worth a sub-inquiry, ranked by how much the sources say; the person
  scope the reader lacks (19 §7) is built here.
- **The phases are discovered.** The phases agent proposes an event's phases
  from its depicted events, with reasons and the passages that show them, then
  places the events as today. A curator-decided spine, such as Actium's, is used
  when present and is the first test of the discovered one.
- **The account has an outline.** Historical order (the phases, in the graph)
  and narrative order (the account's sections) are different (Weaving document).
  An outline agent proposes the account's sections, each citing phases, entities,
  and passages; a section no preserved passage supports becomes a signpost, "not
  yet read", and a target for the next source plan. The curator's Perplexity test
  showed an agent can outline an event well; its quality table (scope, source
  criticism, alternatives shown, causation, material evidence, aftermath, data
  discipline) is the outline's and the account's acceptance checklist. Its
  chronological chapters matched our phases; it would split the road to war and
  carry the story on to Alexandria.
- **Seeds become output.** The Subject, the actors for a polity, the Works'
  forms, and the phases are produced by steps and kept for the curator's veto.

### 3.5 Reconciliation

Each candidate claim is classified before it is stored, by code where it can be
(the validator's duplicate and added-evidence checks, the claim family) and by a
model where it needs reading. The reconciler classifies; it never merges.

| Class | Meaning | Action |
|---|---|---|
| exact duplicate | the same claim | nothing new |
| evidence addition | the same claim, new evidence | an addEvidence proposal |
| qualifier addition | adds time, role, context, quantity, or place | a finer claim (22 §3) |
| alternate voice | the same matter in another source's voice | an attributed claim of its own |
| conflict | incompatible with a stored claim | both kept; the conflict recorded (E8) |
| new claim | nothing like it | a proposal |
| identity unresolved | an endpoint cannot be identified | held in the run file for the curator |
| out of scope | interesting, not this inquiry's | the run notes |

Conflict across claim families (19 §7) and a source contradicting a claim (E8)
are built with it.

### 3.6 The critic

A second model reads each stored proposal with a limited evidence packet, blind
to the proposer's rationale on its first reading, and returns one verdict:
supported as written, supported if modified (and how), insufficient evidence,
wrong predicate, identity unresolved, duplicate, conflict to preserve, out of
scope, or escalate to the curator. It advises; it decides nothing (21). Its
disagreements with the proposer go to the curator first. Another vendor is
allowed but is not in itself independence: blind reading, a rubric, and
recorded disagreement are.

### 3.7 The orchestrator

- **State outside the graph:** one run file per command in `runs/`, with the
  orientation, every plan version, each worker's assignment and result (model,
  prompt version, tokens, cost, outputs, proposal ids), reconciliations,
  verdicts, interrupts, and the reason the run stopped. A run resumes from it.
- **What was checked is what is stored:** a worker's reviewed dry run is
  stored as it stood (as `--from-plan` does for the phases).
- **Budget:** a cap per command, split across items; an item that would exceed
  its share stops and says what it would do next.
- **Runtime:** a small custom controller over the existing modules first, on
  Actium; LangGraph only if pause, resume, branching, and recovery code piles
  up. Either way the run state is the contract (§6), and the model runtime (the
  Anthropic SDK) is a separate choice.

### 3.8 Independent witnesses

Five sources saying one thing are not five witnesses: Hale and Weigall retell
Plutarch and Dio, Weigall quotes Plutarch at length, Wikipedia cites them all.
Attestation ([export/confidence.py](export/confidence.py)) counts distinct
authors, so a fact can read "well attested (4 authors)" on one or two
traditions (the known limit in 25 §6; backlog E10 asked for the relation).

- A predicate between Works, `derivesFrom` (Work → Work, attributed or
  asserted, with the passages that show it: a citation, a long quotation, the
  author's own statement of his sources), proposed by the source briefs and the
  event source plan, which already see what each author relies on.
- Attestation counts independent traditions beside authors: "attested by 4
  authors, drawing on 2 traditions". A Work whose sources are unknown counts
  as its own tradition.
- A run's diminishing returns are measured in new independent evidence, not
  in more passages.

### 3.9 A modern-scholarship lane

Our modern voices are old enough to be public domain (Hale 1911, Weigall
1914); recent scholarship (monographs, articles, excavation reports) is in
copyright, and the battle's open questions (battle or breakout, the fleet, the
monument, Augustan memory) live there.

- An agent may find open-access articles, abstracts, and catalogue records
  (consultative, class C) and propose them as Works with their bibliographic
  record and locator: the "Read more" list, signposts, and source-plan targets.
- Their claims enter only through the curator's transcriptions (23 §7, built,
  unused so far) or through openly licensed text, never through the agent's
  paraphrase. A model never declares copyrighted text cleared (32 decision 7).

### 3.10 The registry as the agents' starting point

Today the registry ([curation/sources.json](curation/sources.json)) is read only
to filter where a copy may be located, and its rights rules are restated in
code. Under this design:

1. The orientation researcher and the source discoverer receive the registry
   (systems, coverage, status, limits) and say for each candidate whether its
   system is readable, registered without an adapter, or unregistered (the
   event source plan, `event-source-plan-v2`).
2. Each system's rights rule becomes a machine-readable check in the registry,
   read by the adapters; a test fails when a readable system has none.
   The registry also records the fields the curator marked in
   [docs/Agent resources.md](docs/Agent%20resources.md): polity, region, and
   dates; languages; lenses; evidentiary type; what reuse permits; and, from
   the source review, the last successful test, failure behaviour, rate
   limits, and the removal procedure.
3. A candidate in a registered system without an adapter is reported as such;
   adapters (Wikisource first, for Shuckburgh) are built when a plan needs them.
4. A registry proposer turns [docs/Agent resources.md](docs/Agent%20resources.md)
   and the agents' discoveries into proposed entries, each with its rights
   statement checked verbatim on the source's own page, for the curator's veto.

From [docs/Deep dive into sources.md](docs/Deep%20dive%20into%20sources.md)
(2026-10-17), an adapter specification for the whole inventory:

5. **One envelope for every new adapter**: the request, the release, the rights
   decision (from the registry's check), a pointer to the native payload
   (preserved byte for byte with its hash, as now), the records mapped from it
   with their unmapped fields kept, warnings, and errors. Text adapters keep
   `PassageSource` ([adapters/sources.py](adapters/sources.py)); coins,
   inscriptions, routes, and map layers need the envelope. Access in the
   registry's bulk-first order: versioned release, Git, dump, API, record,
   browser, and scraping only where expressly permitted.
6. **Consultative observations**: for a source that may be read but not copied
   (PHI, ETCSL, the Persepolis archive) and for modern scholarship (§3.9), one
   observation kind holding the citation, identifier, link, retrieval date, and
   a short permitted extract. A claim may cite it only with words the source
   shows; never the agent's summary.
7. **Object, document, edition, translation, and image as separate records**
   for papyri, inscriptions, and coins (type and specimen apart), built when the
   first such source is read; until then edition details stay on the passage.
8. **Adapters in the order inquiries need them**: Wikisource (Shuckburgh),
   then Nomisma and CRRO (coin types and magistrates: Actium's memory, the
   Republic's moneyers), then Open Greek and Latin (Greek texts beyond Perseus,
   for Alexander); Papyri.info when Ptolemaic Egypt is read.
9. **Every worker reports its coverage contribution** (new entities, claim
   families, evidence, traditions, evidence classes, gaps closed), so a run stops
   when reading no longer adds independent evidence (§3.8).

## 4. The test: a second domain

*Graph Alexander the Great*, from the single command, with no file written by
hand: a Person recipe, a life's battles as Event sub-inquiries, Greek and Persian
sources, another region of the gazetteer (acceptance criterion 14). Identity and
sources are found at run time, never from memory (rule 17). Done when the run
file shows every step and the run ends with proposed entities, claims, phases,
and an account for at least one battle.

## 5. Build order

1. **Contracts** (built 2026-10-16, §6).
1a. **The registry** (§3.10 items 1-3) and **independent witnesses** (§3.8).
1b. **An evaluation set** for Actium (from the source review): known people,
   places, collective actors, events and phases, material things;
   straightforward, qualified, and disputed claims; identity traps, deliberate
   duplicates, and claims the sources do not support, built around the
   curator's 155 decided proposals. Measured: entity precision, identity,
   citation correctness, entailment, duplicate and conflict handling, source
   diversity, rights, rejection of unsupported claims, curator acceptance and
   edits, new claim families per batch, cost per accepted proposal; above all,
   how often an evidence packet lets the curator decide correctly and quickly.
2. **Chrystallum's account for Actium**, with the outline agent (§3.4), so the
   Event recipe is complete.
3. **The front door on Actium**: accept `graph "Battle of Actium"`, resolve,
   anchor, read coverage, write the orientation brief and a line-item plan;
   execute nothing.
4. **Guided orchestration**: run the approved items with the existing modules,
   one resumable run file.
5. **Reconciler and critic** (§3.5, §3.6).
6. **Three pilot lenses** on the same Actium material; keep a lens only if it
   adds proposals or source targets that are not duplicates.
7. **The discovered spine and the Person recipe**, then *Graph Alexander the
   Great*.
8. **Runtime review**: the custom controller against a LangGraph prototype.
9. Hannibal and the other actors (25 §13), each through the command.

## 6. As built: the contracts (2026-10-16)

[orchestration/contracts.py](orchestration/contracts.py) (`inquiry-run-v1`),
Pydantic like [proposals/schema.py](proposals/schema.py), tested in
[tests/test_orchestration_contracts.py](tests/test_orchestration_contracts.py);
the hardcoding guard covers the package.

| Contract | Holds | Refuses |
|---|---|---|
| `ScopeDecision` | in scope, out of scope, or reframe | an out-of-scope answer without historical reframings |
| `ResolvedFocus`, `IdentityCandidate` | the chosen identity or the candidates | "resolved" without who chose; "ambiguous" with one candidate |
| `SubjectAnchor`, `AuthorityMatch` | the Subject, its headings and match types | a non-provisional anchor without an exact heading; a match not checked at its authority |
| `CoverageMap`, `Gap` | what the graph holds, what is missing | |
| `OrientationBrief` | kind, bounds, candidates, needs, federations, sources, lenses, controversies, traps, sourced statements, stopping rule | year zero; reversed bounds |
| `InquiryPlan`, `PlanItem`, `PlanDecision` | versioned line items, their decisions, the mode | duplicate items; dependencies on later items; items over budget; items for a request out of scope; a decision without who and when; a modification without what |
| `WorkerAssignment`, `WorkerResult`, `CoverageContribution` | what ran, with what, at what cost, and what it added that is new and independent | a failure without a reason |
| `ReconciliationDecision` | the eight classes (§3.5) | a related class that names no stored claim |
| `CriticVerdict` | the nine verdicts (§3.6) | a modification on any verdict but "supported if modified", or that verdict without one |
| `Interrupt` | a question that stops the run | |
| `InquiryRunState` | the whole run, saved and loaded from its file; the next runnable item by mode, dependencies, and open questions | a finished run without its reason; running with an open question; a result with no assignment |

## 7. Decisions for the curator

Recommended answers; each is open to veto.

1. ~~Approval mode~~ **Settled 2026-10-17** (32 decision 2): line-item plans
   with approve all; interrupts only for identity, scope, rights, destructive
   reconciliation, or budget.
2. ~~Visibility~~ **Settled 2026-10-17** (32 decision 9): proposed content in
   the same projection, with redundant status; path tracing approved-only by
   default.
3. **No exact heading.** A provisional local Subject linked to broader and
   related headings, labelled as ours (28 §6); the run does not stop for it.
4. **What "train" means.** A persistent research dossier per subject (the
   orientation brief and its sources), kept as a file and reused by later
   inquiries, rather than knowledge that lasts one command.
5. **The general orientation.** Who, what, when, and where, with expected
   controversies and identity traps; no interpretive or causal claims.
6. **The critic's authority.** Advise only; reconsider once its agreement with
   the curator is measured.
7. **Chronology.** The default order for persons, events, polities, and
   transformations; not forced on concepts or technologies.
8. **"All resources".** A budgeted, representative set with diversity targets
   (primary, modern, competing readings, other languages) and a recorded reason
   for stopping.
9. **Works and Wikipedia.** Works remain the evidence for claims; Wikidata and
   Wikipedia orient the inquiry and settle identity, and count as one weak voice
   each when they support a claim. Otherwise most of a subgraph would rest on
   its weakest sources.
10. **Budget.** The default cost cap per command, and whether the run asks
    before exceeding it (the curator's figure).
11. **A life's events.** How many of a person's events become sub-inquiries in
    a first run (all battles, or the agent's top few by sources).
12. **Accounts.** One per event in every run, or only on request.
