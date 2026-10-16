# Chrystallum Agent Workflow: Repository State, Proposed Direction, and Recommendations

## Executive assessment

The proposed behavior is directionally sound. Its strongest idea is that Chrystallum exists to **build governed historical subgraphs**, not to summarize books. Its second strong idea is that the system should first learn enough about the requested subject to decide what graph-building work is warranted.

The proposal is not wholly different from the current repository. It revives and clarifies several ideas that the repository previously called the Concierge and Command Agent, while retaining the newer decisions that Works support inquiries rather than organize them. The main conflicts are about terminology, approval timing, the meaning of “reader,” and whether lenses are permanent agents or temporary analytical instructions. The current working area is `graph1/GraphRevised` on the refactoring branch.

The recommended architecture is:

> **One front-door Inquiry Planner, one resumable Orchestrator, reusable worker capabilities, temporary lens assignments, a Claim Reconciler, deterministic validation, an independent semantic Critic, and a controlled commit service.**

This preserves AI judgment where historical reasoning matters without letting language models control identity, provenance, status transitions, or Neo4j writes.

## Current repository direction

The repository contains three architectural generations at once. Some early documents still describe a CCA → SCA → SFA chain; later decisions explicitly retire the standing Subject Concept Agent and Subject Facet Agents; the newest `31-ONE-COMMAND.md` proposes restoring the missing front door as part of a universal `graph "<anything>"` methodology. This is why the design currently feels contradictory: several documents remain useful as boundary specifications even though their named agent chain has been superseded.

The latest repository direction can be summarized as follows:

| Area | Current repository position | Maturity |
|---|---|---|
| Product purpose | Build and explore historical subgraphs with claims, sources, provenance, time, and authorities | Established |
| Front door | Needed, but not implemented; the older Concierge role was retired with the SCA/SFA chain, while the new one-command design restores its necessary functions | Proposed |
| One command | Resolve → scope → classify kind → choose recipe → run → present | Proposed, not built |
| Recipes | Different recipes for Event, Person, Polity, period, and broad subject | Proposed |
| Readers | Passage-oriented workers that extract evidence-bearing claims and depicted events from selected sources | Substantially implemented for event inquiries |
| Facets | No longer permanent agents or graph nodes; retained as analytical lenses | Decided conceptually |
| Enrichment | Routed by entity kind and external identifiers: place, office, event, group, coin type, and so forth | Partly implemented |
| Works | Evidence and interpretation for an inquiry, not the central organizing structure | Decided and partly implemented |
| Proposals | Typed, source-bearing changes separate from accepted knowledge | Implemented |
| Review | Proposed content is visible with status; promotion to accepted knowledge is controlled | Implemented in part |
| Orchestration | Individual generic commands exist, but no universal run controller executes and resumes the whole methodology | Missing |
| Workflow engine | Current documents specify Python/Anthropic SDK and run files rather than LangGraph | Current implementation choice |

The repository already contains useful building blocks: Wikidata harvesting, Wikipedia first contact, authority records, source planning, inquiry construction, passage finding, source briefs, a passage reader, typed proposal schemas, deterministic validation, proposal storage, review operations, event phases, gazetteer integration, and graph views. The missing layer is not another extraction script. It is the **methodology controller** that turns a user command into a coherent, inspectable run.

## Thoughts versus repository

| Proposed thought | Agreement | Tension | Recommendation |
|---|---|---|---|
| The purpose is to build subgraphs | Strong agreement | None | Make this the product charter and the success criterion for every run |
| The system researches the requested subject broadly | Supported by first contact, source planning, and one-command design | “Research broadly” lacks a stopping rule and could become an unbounded essay task | Produce a bounded `OrientationBrief` and `CoverageMap`, not free-form research |
| It is not primarily a Work reader | Strong agreement | Existing implementation is currently reader-heavy because Actium tested source extraction | Treat readers as worker capabilities inside a graph-building methodology |
| Concierge resolves the request and routes it | Function is required by the newest one-command plan | The named Concierge was earlier retired | Restore the function under a clearer name: `InquiryPlanner` or `FrontDoorAgent` |
| Concierge does not propose claims or nodes | Consistent with governed boundaries | Broad research inevitably identifies candidate entities and relations | Permit planning candidates, but prohibit graph `ProposalDraft` objects at this stage |
| Tie the request to a subject backbone and bibliographic authority | Consistent with Subject, LCSH, FAST, and authority work | Not every valid inquiry has an exact authorized heading | Require authority anchoring when available; allow provisional composite Subjects with broader or related authority links |
| Check the current graph first | Strong agreement | Must occur after enough identity resolution to know what to check | Use a read-only `CoverageQuery` immediately after candidate identity resolution |
| Ask the user when ambiguous | Strong agreement | Asking for every low-level ambiguity would make runs unusable | Interrupt only for identity, materially different scope, rights/cost, or destructive merge decisions |
| Activate a general reader | Partially aligned | “Reader” currently means a source-passage extractor; a general reader would become too broad | Introduce an `OrientationResearcher`; reserve `Reader` for a specific source or corpus |
| Start with a general lens | Useful | “General” is not one of the analytical lenses and could duplicate the OrientationResearcher | Define `GENERAL_ORIENTATION` as a workflow stage, not a historical lens |
| Populate QIDs and properties | Strong agreement | QIDs must not become mandatory local identity | Preserve local IDs; attach QIDs and selected statements as source-attributed identity and claim data |
| Propose backbone and federation links | Strong agreement | Exact-match assertions can be overstated | Record match type: exact, close, broader, narrower, related, or candidate |
| Normally work chronologically | Strong agreement for events and lives | Not all concepts, technologies, institutions, or historiographical debates are best organized chronologically | Make chronology the default sequencing strategy where the subject has a temporal narrative, not a universal invariant |
| Present a line-item plan for approval | More conservative than the repository's latest “run then promote” approach | The current one-command proposal limits curator interruptions to ambiguous identity and final promotion | Support both `guided` and `autonomous` run modes; retain stable plan-item IDs in either mode |
| Discover all applicable resources | Consistent with source planning | “All” is impossible and unbounded | Use channels, relevance ranking, source diversity targets, budgets, and a documented stopping reason |
| Decide duplicate, enhancement, or new claim | Correct and essential | Semantic equivalence cannot be safely left to an unconstrained reader | Add a separate `ClaimReconciler` with deterministic and model-assisted stages |
| Works act like footnotes and add color | Correct that Works are not the focus | “Supplement” understates their evidentiary role | Works are not the backbone, but they remain evidence for historical claims and voices in historiography |
| Add a second model to review proposals | Consistent with limited delegated review | A second model is not automatically independent or correct | Use deterministic validation first, then blind semantic criticism, then risk-based human promotion |
| LangGraph may manage the workflow | Technically appropriate for the new requirements | The repository currently uses SDK calls and JSON run artifacts | Freeze the workflow state contract first; then decide whether to implement it with LangGraph or a smaller custom orchestrator |
| Preserve AI reasoning | Essential | “Less deterministic” must not mean ungoverned writes | Let AI choose and interpret; let code validate, record, and commit |

## Correct the vocabulary

Several terms should be tightened before more code is written.

### “Training”

The system is normally not training a model in the machine-learning sense. It is performing **inquiry-scoped orientation and grounding**. Calling this training risks mixing together model-weight training, retrieval, prompt context, and persistent graph learning.

Recommended terms:

- `OrientationBrief`: what the system has learned about the subject before proposing work.
- `InquiryContext`: compact context passed to later workers.
- `CoverageMap`: what is already represented and what is missing.
- `ResearchDossier`: persistent sources, chronology, vocabulary, identities, and open questions.

### “Reader”

A reader should read something identifiable: a Work, edition, corpus, inscription set, catalogue, or bounded web source. It should produce observations and claim candidates tied to exact evidence. The broad agent that studies the field should instead be called `OrientationResearcher` or `Surveyor`.

### “Lens”

A lens should be a temporary set of questions, relevance tests, preferred source types, and expected relationship patterns. It should not own entities, create duplicate copies, or exist as a permanent autonomous agent. The repository’s move from standing facet agents to lenses is therefore correct.

### “Backbone”

The system has more than one kind of backbone:

- **Subject anchor:** bibliographic organization through LCSH, FAST, LCC, or another subject authority.
- **Identity backbone:** Wikidata, VIAF, ISNI, Pleiades, Nomisma, DPRR, and domain authorities.
- **Temporal backbone:** Year nodes and period models.
- **Geographic backbone:** locations, ancient places, modern containment, and coordinates.
- **Structural backbone:** Types, Groups, Offices, Polities, and institutional relationships.

A user request should attach to the applicable combination. Requiring every graph object to attach directly to a bibliographic authority would conflate subject access with entity identity.

## Recommended architecture

```text
User graph command
        |
        v
1. Inquiry Planner / Front Door
   - classify historical intent
   - resolve or ask about identity
   - create authority-backed Subject anchor
   - inspect current graph coverage
   - perform bounded orientation research
   - select recipe, lenses, federations, sources, budget
   - produce line-item InquiryPlan
        |
        v
2. User plan decision
   - approve, reject, modify, defer per item
   - optional in autonomous mode except material ambiguity
        |
        v
3. Orchestrator
   - execute approved recipe
   - checkpoint every step
   - enforce budgets and stopping rules
   - dispatch reusable workers
        |
        +--> Authority Harvester / Entity Resolver
        +--> Source Discoverer
        +--> Source Reader(s)
        +--> Kind Enricher(s)
        +--> Lens Analyst(s)
        |
        v
4. Claim Reconciler
   - compare candidates with accepted and proposed graph content
   - classify duplicate, evidence addition, qualification,
     conflict, new claim, or unresolved identity
        |
        v
5. Validation and criticism
   - deterministic schema/provenance/predicate/time checks
   - independent semantic Critic
   - risk and uncertainty assignment
        |
        v
6. Proposal Bundle
   - entities, claims, evidence, annotations, conflicts
   - existing objects reused
   - rejected alternatives and reasons
        |
        v
7. Promotion and commit
   - curator or delegated policy decides promotion
   - bounded idempotent service writes to Neo4j
```

This design does not resurrect the old SCA/SFA hierarchy. It restores the missing front-door function while preserving the repository’s newer capability-based architecture.

## Inquiry Planner contract

The front door should return structured planning data, not prose alone. A useful contract would include:

```yaml
InquiryPlan:
  inquiryId: chr:inquiry:...
  command: "Graph the Battle of Actium"
  scopeDecision: IN_SCOPE
  resolvedFocus:
    candidateEntityId: chr:event:battle-of-actium
    qid: Q...
    confidence: high
    ambiguityStatus: resolved
  subjectAnchor:
    preferredLabel: "Actium, Battle of, 31 B.C."
    authorityMatches:
      - system: LCSH
        identifier: sh85000736
        matchType: exact
      - system: FAST
        identifier: "796265"
        matchType: exact
  existingCoverage:
    reusedEntities: []
    reusedClaims: []
    openProposals: []
    gaps: []
  recipe: Event
  planItems:
    - itemId: P01
      action: FIRST_CONTACT
      status: awaiting_user
      rationale: ...
      expectedOutputs: ...
      estimatedBudget: ...
  lenses:
    - MILITARY
    - POLITICAL
    - GEOGRAPHIC
  federationPlan: []
  sourcePlan: []
  stoppingRules: []
  unresolvedQuestions: []
```

The Planner may identify `CandidateEntity`, `RelationshipNeed`, and `Gap` objects, but these are run-state artifacts. They are not Neo4j entities or claim proposals. This resolves the apparent contradiction between “identify entities and relationships needed” and “do not propose nodes or claims.”

## General orientation stage

The first stage should be a **general orientation**, not a general reader and not a lens. Its purpose is to understand enough of the subject to design the inquiry.

It should produce:

- Resolved identities and unresolved names.
- Subject classification: Person, Event, Place, Polity, Group, Office, Type, Concept, technology, broad topic, or mixed constellation.
- Chronological and geographical bounds.
- Candidate subject headings and authority relationships.
- Existing graph coverage and reusable objects.
- Major entities and relationship families likely to matter.
- Applicable federations and reason for each.
- Candidate Works and other resources, classified by source type and perspective.
- Recommended lenses and explicit reasons.
- Expected controversies, identity traps, and anachronism risks.
- A stopping rule and resource budget.

Wikipedia and Wikidata are appropriate first-contact tools, but they should orient and route the inquiry, not determine final truth. The OrientationBrief should record where each statement came from and clearly distinguish reconnaissance from accepted evidence.

## Reader and lens behavior

### Source Readers

A Source Reader receives a bounded source assignment and an inquiry context. It extracts:

- Source observations.
- Mentioned entities.
- Depicted events.
- Candidate claims with exact locators or quotations where rights permit.
- Source-specific terminology.
- Relevant annotations and narrative detail.
- Explicit uncertainty or unresolved identity.

It should not decide that a candidate becomes accepted knowledge.

### Lens Analysts

A Lens Analyst receives graph coverage, source observations, candidate claims, and a lens definition. It asks questions that would otherwise be missed. For example, a military lens on Actium asks about forces, command, technology, logistics, terrain, sequencing, and tactical disagreement. A diplomatic lens asks about alliances, client rulers, negotiations, defections, legitimacy, and war declarations.

The same model may execute several lens assignments, but each run should have isolated instructions and structured output. This creates analytical diversity without maintaining eighteen permanent agents.

### Kind Enrichers

Enrichers operate when a relevant entity surfaces:

- Person enricher: identity, life dates, family, offices, affiliations.
- Place enricher: Pleiades or other place authority, coordinates, names, containment.
- Event enricher: dates, places, participants, phases, predecessor and successor events.
- Institution enricher: office, powers, membership, hierarchy, jurisdiction.
- Material-culture enricher: object type, findspot, collection, inscription, coin authority.

They should gather and normalize the domain record. Lens Analysts decide why that information matters to the inquiry.

## Claim reconciliation

“Duplicate, enhancement, or new” should become a formal decision vocabulary:

| Classification | Meaning | Default action |
|---|---|---|
| `EXACT_DUPLICATE` | Same canonical endpoints, predicate, qualifiers, and attribution | Do not create another claim |
| `EVIDENCE_ADDITION` | Same claim identity, new independent source observation | Propose evidence on existing claim |
| `QUALIFIER_ADDITION` | Candidate adds time, role, context, quantity, or place | Propose a qualified claim or superseding refinement according to predicate policy |
| `ALTERNATE_VOICE` | Same historical issue stated by a distinct source perspective | Preserve as an attributed voice |
| `CONFLICT` | Incompatible value, date, role, quantity, or interpretation | Preserve both and create a conflict/review relation |
| `NEW_CLAIM` | No matching claim family exists | Propose a new claim |
| `IDENTITY_UNRESOLVED` | Endpoints cannot be safely identified | Hold outside the durable graph and request resolution |
| `OUT_OF_SCOPE` | True or interesting, but not relevant to the approved inquiry | Retain in run notes or discard according to policy |

Exact duplicate detection can be deterministic. Semantic equivalence, qualification, and conflict need model reasoning, but the model should return a classification and explanation rather than execute the merge.

## Review design

A second model is useful, but it should be a **Critic**, not an unrestricted approving agent. The repository’s prior architecture already separated planning, proposal, validation, and controlled commit concepts.[^1]

Recommended order:

1. **Mechanical validator:** schema, IDs, endpoint kinds, predicate registry, quotation presence, source locator, temporal form, authority format, rights, budget, and stale-state checks.
2. **Semantic Critic:** asks whether the evidence supports the exact predicate, whether identities are justified, whether qualifiers are warranted, whether the claim duplicates or conflicts with graph content, and whether a weaker formulation is required.
3. **Risk policy:** routes low-risk evidence additions differently from identity decisions, causal claims, contested interpretations, model changes, and destructive operations.
4. **Human promotion:** accepts, rejects, edits, defers, merges, or requests another source.

A different model provider may reduce correlated errors, but provider diversity alone does not guarantee independence. Better safeguards are blind review, limited evidence packets, explicit rubrics, separate prompts, deterministic checks, disagreement escalation, and permanent recording of both proposer and critic outputs.

Suggested critic verdicts:

- `SUPPORTED_AS_WRITTEN`
- `SUPPORTED_IF_MODIFIED`
- `INSUFFICIENT_EVIDENCE`
- `WRONG_PREDICATE`
- `IDENTITY_UNRESOLVED`
- `DUPLICATE`
- `CONFLICT_REQUIRES_PRESERVATION`
- `OUT_OF_SCOPE`
- `ESCALATE_TO_CURATOR`

## Approval timing

The proposed line-item approval conflicts with the repository’s newest preference for only two curator touchpoints: identity ambiguity at the beginning and promotion at the end. Neither approach should be universal.

Use three operating modes:

| Mode | Before execution | During execution | Final stage |
|---|---|---|---|
| `GUIDED` | User approves, rejects, or edits every plan item | Pause on material deviations | User promotes proposals |
| `SUPERVISED` | User approves scope, budget, lenses, and source strategy | Pause only on ambiguity, cost, rights, or major scope expansion | User promotes proposals |
| `AUTONOMOUS_RESEARCH` | Plan is displayed but execution proceeds | Stop at policy-defined interrupts | Everything remains proposed until promotion |

For development and the Actium pilot, `GUIDED` is preferable because it exposes bad planning logic. For mature routine inquiries, `SUPERVISED` will likely provide the best balance.

Each plan item needs a stable ID and version. User modification should create a new plan version while preserving the original. This enables “approve all except P07,” “replace source in P12,” or “run military and political lenses but defer economic.”

## LangGraph decision

LangGraph is a reasonable fit for the workflow now being described because it supports stateful long-running orchestration, deterministic and model-driven steps in the same workflow, persistence, conditional routing, and human-in-the-loop interrupts. Its orchestrator-worker pattern also supports dynamic worker creation and shared structured state, which maps naturally to source readers, enrichers, and lens assignments.[^2][^3]

However, LangGraph should not define the intellectual architecture. First define an implementation-neutral `InquiryRunState` containing:

- Command and resolved focus.
- Plan version and item decisions.
- Current recipe step.
- Budgets and costs.
- Existing coverage snapshot.
- Worker assignments and outputs.
- Open ambiguities and interrupt reasons.
- Proposal and review IDs.
- Retry and idempotency keys.
- Terminal status and stopping explanation.

Then implement one Actium run with the current Python modules behind this interface. If custom pause/resume, branching, parallelism, and recovery code begins accumulating, move the state machine to LangGraph. LangGraph interrupts can persist a paused state and resume it after human input, which directly supports line-item approval and ambiguity resolution.[^4][^5]

The model runtime and workflow runtime are separate decisions. Anthropic or OpenAI can supply the reasoning workers while LangGraph coordinates them. Structured-output support allows agents to use tools but still return validated data matching a declared JSON schema.[^6]

## Reasoning versus rules

The design principle should be:

> **AI decides what deserves attention and how evidence should be interpreted; deterministic services enforce what may enter the graph and how it is recorded.**

| Prefer agent reasoning | Prefer deterministic code | Hybrid decision |
|---|---|---|
| Interpret user intent | Stable IDs | Entity resolution |
| Rank candidate identities | Schema validation | Duplicate versus enhancement |
| Choose useful federations | Authority identifier syntax | Source relevance |
| Select and rank sources | Rights and access rules | Lens selection |
| Decide which lenses matter | Predicate endpoint constraints | Event phase discovery |
| Detect historical significance | Temporal normalization | Conflict detection |
| Interpret source perspective | Idempotent writes | Stopping decision |
| Identify likely omissions | Status transitions | Claim-strength judgment |
| Explain uncertainty | Budget enforcement | Reviewer escalation |
| Propose chronology or phases | Provenance attachment | Scope expansion |

This is not “determinism versus agents.” It is **determinism around agents**. A pure script cannot decide which aspects of Actium deserve deeper research, whether two historians are actually disagreeing, or which sources should be sought next. A pure agent should not invent IDs, alter accepted claims, flatten qualifiers, or decide that two historical people are the same entity without a governed record.

## Recommended build order

### Increment 1: Freeze contracts

- Finalize `InquiryPlan`, `PlanItem`, `OrientationBrief`, `CoverageMap`, `WorkerAssignment`, `ReconciliationDecision`, `CriticVerdict`, and `InquiryRunState` schemas.
- Add explicit separation between run-state candidates and graph proposals.
- Mark superseded CCA/SCA/SFA sections more prominently or move them into a historical design folder.

### Increment 2: Actium front door

- Accept `graph "Battle of Actium"`.
- Resolve identity and authority-backed Subject.
- Query current Actium coverage.
- Generate an orientation brief.
- Propose a line-item plan using existing repository capabilities.
- Do not execute automatically in the first version.

### Increment 3: Guided orchestration

- Execute approved plan items using current harvest, source-plan, finder, reader, phase, and proposal modules.
- Maintain one resumable run-state file.
- Record every worker input, structured output, cost, model, prompt version, and failure.

### Increment 4: Reconciliation and critic

- Implement the formal reconciliation classes.
- Add deterministic validation before model criticism.
- Run the critic with an evidence packet that does not include the proposer’s persuasive rationale unless needed after an initial verdict.
- Present proposer/critic disagreement to the curator.

### Increment 5: Lenses

- Implement only three pilot lens definitions: general historical significance, military, and political.
- Run them against the same Actium coverage and source observations.
- Measure whether each lens produces non-duplicate, useful graph proposals or better source targets.
- Add more lenses only after a concrete query demonstrates their value.

### Increment 6: Second subject

- Run `graph "Alexander the Great"` without subject-specific code.
- Test Person → life events → Event recipe composition.
- Require the system to discover authorities, sources, federations, and lenses at run time.

### Increment 7: Choose orchestration runtime

- Compare the completed custom run controller with a LangGraph prototype.
- Adopt LangGraph if durable interrupts, branching, parallel workers, resumability, and observability materially reduce custom code.
- Keep orchestration state outside the historical semantic graph regardless of runtime choice.

## Questions requiring decisions

1. **Approval mode:** Should every ordinary user approve the plan line by line, or is that primarily a curator/development mode while normal users see the plan and permit automatic execution?
2. **Visibility:** Should unreviewed entities and claims remain immediately visible as `proposed`, as the repository currently intends, or should ordinary users see them only in a separate research layer?
3. **Authority gaps:** If no exact LCSH or FAST heading exists, may the system create a provisional local Subject linked to broader and related headings, or must it stop for curatorial approval?
4. **Meaning of “train”:** Is the desired subject learning temporary for one command, or should the OrientationBrief become a persistent, reusable research dossier in the project?
5. **General lens:** Is “general” meant to discover the basic who/what/when/where structure, or also to propose significance, causation, and interpretation?
6. **Reviewer authority:** Should the second model only advise, or may it promote tightly bounded low-risk proposals such as an additional quotation supporting an already accepted participation claim?
7. **Default chronology:** Should chronological processing govern all inquiries, or only Persons, Events, Polities, and transformations where sequence is central?
8. **Source completeness:** Does “discover all applicable resources” mean exhaustive cataloguing, or a budgeted representative source set covering primary evidence, modern scholarship, different languages, and competing interpretations?

## Principal recommendation

Do not rebuild the retired hierarchy of one Subject Concept Agent plus many standing facet agents. Restore the **front-door planning function**, retain **lenses as temporary analytical assignments**, retain **enrichers as kind-routed capabilities**, and separate **source reading** from **subject orientation**.

The most important immediate artifact is not a new agent prompt. It is a typed `InquiryPlan` plus `InquiryRunState`. Once those contracts are stable, the existing code can be arranged into a coherent methodology, user approval can operate at the line-item level, a second model can critique defined proposal packets, and LangGraph can be adopted—or rejected—based on an actual orchestration requirement rather than architectural fashion.

---

## References

1. [Excellent! now what do you propose the various prompts to the agents to be? I think we need a concierge agent to take the user commmand "Graph Bismark" and determine which SCA(s) it should go to. I assume those agents should understand the entire architecture, even doing a self-documenting system with neo itself](https://www.perplexity.ai/search/f82d32a1-c51b-4f1b-9dbd-f335e8b9047f) - Yes—the missing front-door role is a Concierge and Command Agent (CCA). It should translate “Graph B...

2. [LangGraph overview - Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/overview) - LangGraph is focused on the underlying capabilities important for agent orchestration: durable execu...

3. [Workflows and agents - Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/workflows-agents) - This guide reviews common workflow and agent patterns. Workflows have predetermined code paths and a...

4. [Human-in-the-Loop - Frontend](https://docs.langchain.com/oss/python/langchain/frontend/human-in-the-loop) - The Human-in-the-Loop (HITL) pattern lets your agent pause execution, present the pending action to ...

5. [Interrupts - Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/interrupts) - Interrupts allow you to pause graph execution at specific points and wait for external input before ...

6. [Get structured output from agents - Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/structured-outputs) - Structured outputs let you define the exact shape of data you want back from an agent. The agent can...

