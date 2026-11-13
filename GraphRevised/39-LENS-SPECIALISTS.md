---
status: draft
authority: D-137 (33-DECISIONS.md); this document holds the reasoning and the design
depends_on: [05-AGENT-BOUNDARIES.md, 21-REVIEW-DELEGATION.md, 25-LIVES-AND-PLAYGROUND.md, 31-ONE-COMMAND.md, 33-DECISIONS.md]
superseded_by: null
last_reviewed: 2026-11-12
---

# 39 — Lens Specialists

**Date:** 2026-11-12. **From:** a discussion with the curator about the
vision ([vision.md](vision.md)) and the legacy facet design
([../Facets/](../Facets/)).

The curator's request, in the curator's own words: *"Graph the Roman Republic
across all lenses."* Each lens is a specialist agent that studies its lens for
a long time, proposes the claims that matter to it, and owns its domain.

This document brings back standing specialists, which D-050 retired, and keeps
D-039 (lenses are never nodes) and D-030 (people first).

## 1. Why the specialists come back

D-050 retired the subject facet agents (SFAs) for four failures (25 §11).
None of them was a failure of specialization. Each now has a guard that did
not exist then.

| Why the SFAs failed | The guard now |
|---|---|
| They built categories instead of facts | A specialist proposes only typed claims through the predicate registry |
| The model's paraphrase served as evidence | Every claim cites a preserved passage with a verbatim quotation; the model's own knowledge directs where to look and is never evidence |
| They stored confidence numbers | Attestation is computed from the voices, never stored (D-033) |
| They invented data | The validator, the identity queue, peer review (§5), and the curator |

What the SFAs got right, and the current design lacks: expertise that builds
over time, and someone who answers for a domain's coverage. The lens analyst
of 31 ([discovery/lens_analyst.py](discovery/lens_analyst.py)) reads well (its
Actium run found, for example, that 635 claims hold one religious act), but
it is short-lived, it only reads the graph, and its 46 gaps and 28 predicate
needs stayed in a run file.

## 2. What a specialist is

A specialist is **one lens in one scope**:

```text
specialist = lens × scope
  lens:  military, political, economic, social, religious, technological,
         natural history, artistic, ...  (curation/lenses.json)
  scope: a polity (Roman Republic), a period, or a discipline
```

The scope is not always a polity. The senator-to-mollusk path (06 §14) passes
through murex and purple dye, which belong to no polity. A natural-history
specialist is grounded in a body of knowledge (Pliny, *Natural History* 9;
Aristotle, *History of Animals*), and a technological one in a craft
tradition.

Its id names both parts, and is the `assertedBy` and `createdBy` of what it
proposes, following the existing agent names (`passage-reader`,
`event-phases-agent`):

```text
lens-specialist:military/roman-republic
lens-specialist:natural-history/ancient-mediterranean
```

## 3. The dossier is the training

A model does not learn between runs. What grows is the specialist's
**dossier**, and every run starts from it, so the specialist knows its domain
better on its tenth run than on its first.

| Part | Holds |
|---|---|
| Grounding | native terms and their meanings, core sources (today's `curation/lens-grounding/<polity>.json`, now drafted and kept by the specialist) |
| Reading list | sources in scope, each held or not held, ancient or modern, with what reuse permits |
| Reading record | which passages it has read, and when |
| Domain map | the entities that matter in its domain, the controversies, the open questions |
| Questions | the lens's questions (from `lenses.json`), each marked answered, thin, contested, or open, with the claims it rests on |
| Predicates | the registry predicates it owns (§4), and the ones it has asked for |
| Record | its proposals and what became of them: accepted, rejected and why, still open |

"Studying for hours" means building this dossier: reading, mapping, and asking.
The dossier is agent state, not graph content. It lives in files beside the
lenses, versioned in git like the grounding, so it can be reviewed and
diffed:

```text
curation/specialists/<scope>/<lens>/dossier.json
```

The curator reviews a dossier once, when a specialist first drafts it, as
for the grounding today. After that only changes that trip a rule come back
(§7).

## 4. What a specialist owns, and what it does not

| A specialist owns | Meaning |
|---|---|
| Its questions | the coverage of its domain: what is answered, what is thin, what is missing |
| Its claims | everything it proposed, and their evidence |
| Its predicates | its slice of the registry (`commanded`, `servedUnder` for military); it proposes new ones, such as `defectedTo` |
| Its sources | its reading list and the reading still to do |
| First-line review | other agents' proposals that use its predicates (§5) |

**It never owns nodes.** Agrippa is military, political, social, and familial
at once. Entities are shared and come through the identity queue; every
specialist points at the same Agrippa (25 §11: "the person comes first;
lenses refer to it"). There is no `:Facet` label and no `HAS_X_FACET`
relationship (D-039). The legacy facet registry
([../Facets/facet_registry_master.csv](../Facets/facet_registry_master.csv))
may seed new lens definitions; its anchors are checked against Wikidata first,
as its own quality flags warn.

## 5. Peer review

Specialists review each other's proposals that use their predicates: military
checks a political proposal that uses `commanded`. This extends
[21-REVIEW-DELEGATION.md](21-REVIEW-DELEGATION.md) and keeps its limits:

- A specialist decides only what a verbatim quotation lets anyone check:
  does the passage say this?
- A specialist never reviews its own proposals.
- `decidedBy` names it and the delegation:
  `lens-specialist:military/roman-republic (delegated by <curator>)`, so
  delegated decisions can be listed and audited apart from the curator's.
- What 21 reserves for the curator stays with the curator.
- The curator undoes a wrong decision with `review retract`, as today.

## 6. The life of a specialist

```text
1. Orientation (31 §3.1)   the scope, its bounds, which lenses apply, the budget
2. Training               each specialist drafts its dossier: grounding, reading
                          list, domain map, questions; the curator reviews it once
3. Building               each reads passages through its lens (scope rule and
                          questions) and proposes claims with quotations
4. Reconciliation (31)    the reconciler merges duplicate entities and predicate
                          requests across specialists; the critic checks
5. Stewardship            each watches for new entities in its domain, takes
                          gaps sent to it, reviews its peers, keeps its dossier
```

**"Graph the Roman Republic across all lenses"** runs through 31's one
command: the front door, orientation, plan, and orchestrator are 31's; the
specialists are its lens workers, made standing and allowed to propose.

## 7. Where the outputs go

| Output | Where it goes |
|---|---|
| Claims | Proposals, through the validator, as from any agent |
| Findings | recomputed on demand, not stored: the claims they cite change |
| Gaps | work orders for the frontier planner (04), merged across specialists |
| Predicate needs | one queue of registry change requests, merged across specialists ([curation/predicate-needs.json](curation/predicate-needs.json), built 2026-11-12: §7.1) |
| Lens note | an Annotation (`noteType: lens-reading`, author the specialist, status `flagged`), shown on the card in the lens colour (D-118) |
| Dossier changes | the dossier file; changes that trip a rule are shown to the curator |

### 7.1 The predicate-needs queue

`python -m GraphRevised.proposals.predicate_needs collect <runs>` merges the
needs of lens readings (`runs/lens-reader-*.jsonl`) and lens analyses
(`runs/lens-*.json`) into [curation/predicate-needs.json](curation/predicate-needs.json);
`list` shows the open requests, most requested first. Each request keeps every
specialist that asked, every quotation or example, and its **precedents**: the
active registry, the legacy relationship registry ([../Relationships/](../Relationships/),
with Wikidata property, direction, reification hint, and CIDOC code), and the
legacy CIDOC mapping ([../CIDOC/](../CIDOC/)). Precedents are matched by the
rarity-weighted words of the name and definition, so `wentOverTo` finds
`defectedTo`; they are leads, never decisions, and legacy Wikidata ids are
checked at Wikidata before use. A request with the same name merges; similar
requests are listed beside each other (`similarRequests`), never merged
silently. A request names nothing in the registry until the curator adds it.

The reader shows the open requests to every lens reading, so a specialist
reuses a name rather than coining another. Collecting is a separate step:
a dry run writes only its log.

First collection (2026-11-12): 31 needs from the 2026-10-21 Actium lens
analysis and one military lens reading, as 29 requests. `defectedTo` was
asked three times, and once more as `wentOverTo` (listed as similar).

## 8. Three ways a specialist runs

The same specialist is called three ways:

- **Read an object.** The user chooses a lens in the explorer (D-063), or
  stewardship runs it: today's lens analyst, from the dossier.
- **Answer a gap.** The frontier planner sends it a work order: read this
  passage, find this missing claim.
- **Test one hop.** A semantic-bridge trace (06 §14) asks whether one step
  is attested: *does a source say Tyrian purple came from murex?* The answer
  is a cited claim, a gap, or no. A path stays a hypothesis until each hop
  is accepted (06 §15).

Results are cached against the state of the claims they read, so the same
question is not paid for twice.

## 9. Build order

1. **The lens reader.** The reader of [proposals/passage_reader.py](proposals/passage_reader.py)
   with a lens's scope rule and questions, proposing claims. The missing
   piece: it turns a lens from commentary into new facts.
   **Built 2026-11-12** (offline tests only, not yet run on a source):
   `--lens <id> [--lens-scope <scope>]` loads the lens and its grounding
   ([proposals/lens.py](proposals/lens.py)); the prompt gains rules 16 and 17
   and the lens block (prompt `lens-reader-v1`); claims may use only the
   lens's predicates; drafts, notes, and Proposals name
   `lens-specialist:<lens>/<scope>`; periods and depicted events are left to
   the general reader; predicate needs with a verbatim quotation are kept in
   the run log (`runs/lens-reader-<lens>-<scope>-*.jsonl`), not yet queued.
   Tests: `tests/test_lens_reader_offline.py`. First dry runs (military,
   Plutarch's *Antony* 65.1, 65.2, 66.1, 63.3, 68.3, 76.2): eight claims, seven
   of them duplicates of existing claims (the specialist reproduced them
   exactly), one new piece of evidence for an accepted claim, five passages
   of note, one predicate need (`wentOverTo`).
1a. **The predicate-needs queue** (§7.1), built 2026-11-12. Tests:
   `tests/test_predicate_needs.py`. Each request carries a D-138 **shape**
   (event, state, quantity, qualifier; `predicate_needs shape <name> <shape>
   --basis ...`); the reader offers only state requests for reuse and names
   the acts as events to depict. All 29 requests were shaped by Claude as a
   proposal (`by` says so) for the curator to confirm: 24 events, 3 states
   (`delegatedCommandTo`, `commemorates`, `claimedDivineAssociation`), one
   qualifier (`deprivedOfPosition`), one quantity (`hadStrength`).
1b. **Lens readings draft depicted events** (D-138), 2026-11-12. On
   Plutarch 68.1 through the event inquiry (`actium-battle.json`), the
   military specialist reused two existing events ("Octavian's side captures
   three hundred ships") instead of requesting `captured` or
   `surrenderedTo`, and asked for no predicate. An event needs an inquiry
   that allows Event proposals; the single-source inquiries allow only
   Period. Fixed on the way: claims on a new depicted event were refused as
   out of scope (the per-passage scope of the graph-lookup change did not
   receive the new event's id), for the general reader as well; test
   `NewEventScopeTests`.
2. **The dossier**, seeded from today's grounding and the Actium lens run.
3. **One specialist on Actium.** Military on the Roman Republic, on material
   already held, so its output can be compared with the 2026-10-21 run.
4. **Peer review** between two specialists (military and political).
5. **A non-polity specialist.** Natural history, on the purple path: the
   test that grounding by scope works.
6. **"Graph the Roman Republic across all lenses"** through 31.

## 10. Open

- **Predicate or event: decided 2026-11-12 (D-138).** *An act with its own
  time, place, or more than two participants is an Event, its actors joined
  by `participatedIn` (with a role where the source gives one) and its
  outcome by `resultedIn`; a state that holds between two entities over time
  is a predicate.* So `captured`, `declaredWarOn`, `struckCoinage`,
  `decreedThanksgiving`, `conscriptedInto`, and `surrenderedTo` are events;
  a desertion is an event, the allegiance after it a state (`servedUnder`,
  `alliedWith`, with a start); `delegatedCommandTo` is a predicate;
  `deprivedOfPosition` is the end of a `heldPosition` claim; `hadStrength` is
  a quantity. The legacy `reify_as` is a hint, not the rule. Lens readings
  draft depicted events; rule 17 tells the specialists to ask for a
  predicate only for a state. Events add no traversal: every claim of a
  depicted event shares its id prefix, so the event is one index seek
  (02 §6.1, computed cluster addresses). **Roles on participants,
  2026-11-12:** registry v13 lets `participatedIn` take a role of kind
  Office or Type; each participant of a depicted event may carry a
  `role_id` and a verbatim `role_quotation` (an unshown or out-of-scope role
  is dropped, the participant kept; tests `tests/test_event_roles.py`).
  The roles themselves are drafted in [curation/event-roles.json](curation/event-roles.json)
  (22 roles, from the legacy role reference and the requests ruled events,
  revised with the curator: deserter and defector apart, captive for people,
  seized for objects, onlooker and witness defined), awaiting approval before
  they are proposed as Type entities. Registry v14 adds `involvedIn` (Object
  to Event, role expected), so a seized ship is never a participant; a
  source's informant (Plutarch's great-grandfather Nicarchus, *Antony* 68.4)
  is the state request `informedBy` in the queue. Approved and applied the
  same day: the 22 roles are provisional Type entities (`chr:entity:role-*`),
  ten linked to Wikidata (closeMatch). Every inquiry that may depict events
  has them in scope, with the curator's aliases. A depicted event lists
  named `objects` beside its participants, and each becomes `involvedIn`
  with its role. A thing the source only counts stays in the label.
- **Entity review, 2026-11-12.** [discovery/entity_review.py](discovery/entity_review.py)
  reads every entity with its Wikidata classes, its claims and mentions, and
  similarly named entities. It returns one verdict per entity (ok,
  wrong-identity, wrong-kind, duplicate, unsure), each with the review
  command that would carry it out. It writes nothing; the curator vetoes.
  Two review commands came with it: `entity-kind` (refused while an open
  claim names the entity) and `entity-identity`, which retires a wrong
  Wikidata link and keeps it as rejected history. The first full run
  ([queues/entity-review-20261112.json](queues/entity-review-20261112.json),
  256 entities) gave 250 ok. Of the six other findings, the curator accepted
  two and vetoed two:
  - **Accepted:** Tarentum now links Taras, the port city, instead of the
    precinct in the Campus Martius.
  - **Accepted, then reversed:** the British Museum was moved from Work to
    Group, then put back. It is the source PeriodO cites, the museum's own
    thesaurus (`collection.britishmuseum.org/id/thesauri/matcult`), and an
    attributed claim cites it. The review had counted no claims because it
    did not count attributions. It does now, and `entity-kind` refuses to
    move a Work that claims cite or observations come from.
  - **Vetoed:** the Roman Republic and Roman Empire are not duplicates of
    the same-named Periods, because the state and the era stay apart.
  - **Kept as they are:** Wikidata treats the two Domitias as separate
    women, one of them hypothetical. Whether the Campsite Memorial of
    Augustus is a Place or an Object is left open.
- **CIDOC mapping at creation.** Each predicate added from a request carries
  its `wikidata` and `crm` mapping, or says it has none (L2b, 25 §3), so L2b's
  backlog stays the existing predicates.
- **Review volume.** Six or more specialists across the Republic would
  propose tens of thousands of claims. The curator prefers flagging by rule:
  only claims that trip a rule (a conflict with an existing claim, a single
  voice on a contested point, a career-order check that fails, a predicate
  new to the registry, a factual or imaginative category in doubt, a claim
  resting only on a modern source) come to review; the rest stay visible as
  proposed. To be discussed.
- **The lens set.** A stable core plus lenses drafted on demand from the
  legacy registry, or a fixed list.
- **Lens notes.** Whether users see them, as "our reading" on the card.
- **Budgets.** Per specialist, per scope, and per run.
