# Agent Architecture Addendum

## Purpose

This addendum records the curator’s decisions about approval, research notes, domain-pack overlays, and the visibility of proposed claims. It supplements the broader Chrystallum agent-workflow review.

## Decision 1: User and curator

At the present stage, there is no meaningful distinction between the ordinary user and the curator. Tony is currently both. The system should therefore optimize for a single researcher-curator building, exploring, annotating, and governing the Roman Republic graph.

A separate simplified experience for hypothetical future users should not drive the current architecture. The immediate goal is to create an effective research partnership between the curator and the agent system.

### Approval experience

Line-item plan review should be the normal near-term experience, but it must remain low-friction:

- Show the proposed inquiry plan before expensive or graph-changing work.
- Give every plan item a stable identifier.
- Allow individual approval, rejection, modification, or deferral.
- Provide an `approve all` action for routine plans.
- Preserve the original plan and every revised version.
- Interrupt execution only for material identity ambiguity, major scope expansion, rights concerns, destructive reconciliation, or budget overruns.
- Keep agent-generated graph content proposed until it is deliberately promoted.

This is not merely an administrative approval process. The plan is where the curator and agent agree on what historical inquiry they are actually undertaking.

## Primary research use

A principal use case is preparing a book about the Roman Republic. The graph should help reveal non-obvious relationships that may lie several hops away from the starting subject.

The system is not intended to be an encyclopedia, but it must display meaningful content. A graph containing only normalized nodes and edges would be analytically useful but experientially sterile. The researcher needs to understand what the objects mean, why relationships matter, what sources say, and how a discovered path might contribute to an argument.

The system therefore needs four connected content layers:

| Layer | Purpose | Example |
|---|---|---|
| Core knowledge | Governed entities and approved claims | Agrippa participated in the Battle of Actium |
| Source voices | Attributed depictions and interpretations | Plutarch’s account of Antony’s flight |
| Explanatory content | Descriptions, accounts, and contextual narrative | A readable account of the Actium campaign |
| Research workspace | Notes, questions, hypotheses, excerpts, and saved paths | A possible link between naval patronage and veteran settlement |

## Notes as research objects

Notes are first-class research objects, not incidental text fields. They should be creatable and editable from both Obsidian and the graph interface.

A note may concern:

- An Entity.
- An Assertion or relationship.
- A SourceObservation or passage.
- A Work or edition.
- A Subject or inquiry.
- A Proposal or review decision.
- A saved multi-hop path.
- Another note.

Attaching notes to Assertions is essential. It allows the researcher to comment on a relationship without converting the commentary into a historical claim.

### Note contract

```yaml
Note:
  id: note:uuid
  title: "Agrippa, fleet organization, and patronage"
  body: "Markdown content"
  author: "Tony DeFarlo"
  visibility: private | shared | public
  status: draft | active | endorsed | archived
  noteType: observation | question | hypothesis | interpretation | excerpt | outline | argument
  createdAt: timestamp
  modifiedAt: timestamp
  targets:
    - type: Assertion
      id: chr:assertion:...
  sourceLinks:
    - workId: chr:work:...
      locator: "page or location"
      observationId: chr:observation:...
  origin:
    system: obsidian | graph-ui | import | agent
    filePath: optional
  rights:
    quotationStatus: private-copy | public-domain | licensed | permission | review-required
```

The note ID must remain stable when an Obsidian file is renamed or moved. The file path is an editable location, not the note’s identity.

## Obsidian integration

Obsidian should be an editing client for the research overlay, not the authoritative semantic database. Neo4j remains authoritative for entities, assertions, authorities, evidence links, and stable graph identifiers. Markdown may remain authoritative for extended personal prose until selected material is deliberately converted into structured graph content.

Recommended behavior:

1. Store stable note and graph-target IDs in YAML frontmatter.
2. Synchronize designated Obsidian folders through a watcher or explicit sync operation.
3. Never allow an edited note to change an approved historical claim automatically.
4. Preserve note identity through file renames and moves.
5. Allow the graph interface to open a corresponding Obsidian URI.
6. Export graph-created notes to Markdown using the same contract.
7. Preserve both versions when synchronization conflicts cannot be resolved safely.

The graph interface should permit note entry directly from entity, assertion, source, proposal, and path cards. Obsidian integration should expand the workflow, not become a prerequisite for adding a note.

## Core pack and overlays

The architecture should distinguish the governed domain pack from personal and shared overlays.

### Roman Republic core pack

The core pack may contain:

- Governed entities.
- Approved factual claims.
- Explicitly attributed claims.
- Authority mappings.
- Source and edition metadata.
- Public-domain, licensed, or otherwise cleared quotations.
- Approved annotations and explanatory accounts.

### Private research overlay

A private overlay may contain:

- Personal notes.
- Highlights and transcriptions.
- Tentative hypotheses.
- Saved paths.
- Draft outlines and arguments.
- Private source locators or captures.
- Candidate relationships that have not been proposed to the core.

### Shared overlay

A shared overlay may contain:

- Notes released to collaborators.
- Proposed corrections.
- Public commentary that has not been adopted by the core pack.
- Collaborative research questions and saved paths.

The visible workspace is composed at read time:

```text
visible workspace = permitted core pack + permitted overlay layers
```

An overlay should reference core object IDs rather than duplicate the entire core graph.

## Promotion from overlay

Moving private material into the domain pack must be a governed transformation:

```text
private note or excerpt
  → propose to domain pack
  → evidence and rights review
  → edit or transform public form
  → curator decision
  → publish as a pack object
```

Promotion should not merely change `visibility: private` to `visibility: public`. The public form may require a shorter quotation, corrected citation, new paraphrase, redaction of private commentary, stronger source metadata, or separation into several graph objects.

The promoted object must retain provenance back to the originating private note without exposing private text that was not approved for publication.

## Passage capture

If a passage in *The War That Made the Roman Empire* is worth recording, the workflow should be:

1. Identify the Work and edition.
2. Capture the locator and selected passage under a private default.
3. Store the passage as a SourceObservation or researcher transcription.
4. Store the curator’s explanation separately as an Annotation.
5. Link both to relevant entities, assertions, Subjects, or saved paths.
6. Optionally derive attributed or interpretive claim proposals.
7. If the material is proposed for the domain pack, review citation, rights, quotation length, and evidentiary use.
8. Publish only the cleared form.

The author’s words and the curator’s words must remain distinct. A quotation records what the Work says; the Annotation records why the passage was selected or how it may matter.

Correct citation and permission to reproduce copyrighted text are separate questions. Private captures should remain private by default, and a model should never declare copyrighted material publicly cleared solely through its own judgment.

## Saved paths

A multi-hop discovery should be savable as a research object rather than disappearing when the visualization changes.

```yaml
SavedPath:
  id: path:uuid
  title: "Agrippa to veteran settlement through naval patronage"
  nodeIds: []
  assertionIds: []
  generatedBy: user | agent
  explanation: "Why this path may matter"
  visibility: private | shared | public
  noteIds: []
```

A saved path may become:

- A research question.
- A possible causal chain.
- A chapter idea.
- A draft argument.
- A source-discovery task.
- A request for an agent to test whether the apparent connection is historically meaningful.

Saving a path does not assert that the path proves causation or significance.

## Decision 2: Proposal visibility

Proposed claims should be visible immediately within the same graph projection as approved claims. They should not be isolated in a separate research graph.

The reason is contextual: a proposed claim can be evaluated properly only when the researcher can see how it fits into the approved and proposed graph. The researcher must be able to determine whether it:

- Fills a genuine gap.
- Extends an existing path.
- Duplicates another proposal.
- Adds evidence to an approved claim.
- Adds a qualifier to an existing claim.
- Conflicts with approved or proposed content.
- Connects objects that were previously unrelated.

The requirement is therefore **integrated visibility with unmistakable status**. Visibility does not mean that proposed and approved claims have equal authority.

## Unified graph projection

| Concern | Decision |
|---|---|
| Storage | Approved and proposed assertions may coexist with different statuses |
| Visual projection | Show them together so structural fit is visible |
| Matching | Compare new candidates with approved and proposed claim families |
| Pathfinding | Approved-only by default; proposed-inclusive when deliberately enabled |
| Narrative answers | Never present a proposed claim as an unqualified fact |
| Promotion | Changes trust status without moving the claim into a different visual universe |
| Review queue | A focused projection of the same contextual graph, not a separate graph |

## Status presentation

Status must be encoded redundantly. Color alone is insufficient because the graph must remain understandable in monochrome, accessibility modes, screenshots, printouts, exports, and textual path explanations.

| Status | Visual treatment | Card label |
|---|---|---|
| Approved | Solid line with normal emphasis | `APPROVED` |
| Proposed | Dashed or otherwise distinct line | `PROPOSED — NOT REVIEWED` |
| Contested | Distinct contrasting or double treatment | `CONTESTED` |
| Rejected | Hidden from normal exploration; available in history | `REJECTED` |
| Superseded | Hidden or faint in normal exploration; linked to replacement | `SUPERSEDED` |

Every proposed claim card should display:

- Proposal status.
- Proposing agent or person.
- Inquiry and run.
- Creation time.
- Source and evidence.
- Qualifiers.
- Validation state.
- Critic or reviewer verdict, if any.
- Possible duplicate or conflict matches.

## Filters

The interface should provide at least these graph filters:

- Approved only.
- Approved plus proposed.
- Proposed only.
- Contested.
- Attributed source claims.
- Interpretive claims.
- Rejected or superseded history.
- Private-overlay content.
- Shared-overlay content.

The normal research view should show approved and proposed content together. A publication or trusted-answer view may default to approved content only.

## Matching before storage

Before another claim proposal is persisted, the Claim Reconciler must inspect:

1. Approved claims with the same canonical endpoints and predicate.
2. Proposed claims with the same canonical endpoints and predicate.
3. The broader claim family with different time, role, context, quantity, attribution, or direction.
4. Related predicates that could indicate duplication, refinement, or conflict.

The reconciliation result should be one of:

- `EXACT_DUPLICATE`
- `EVIDENCE_ADDITION`
- `QUALIFIER_ADDITION`
- `ALTERNATE_VOICE`
- `CONFLICT`
- `NEW_CLAIM`
- `IDENTITY_UNRESOLVED`
- `OUT_OF_SCOPE`

An exact duplicate should not create another visible edge. New evidence should attach to the existing claim. Alternative source voices and genuine conflicts should remain distinct but visually grouped.

## Pathfinding policy

Proposed claims may be valuable precisely because they reveal possible multi-hop relationships. They should therefore be available to exploratory pathfinding when the researcher deliberately includes them.

Every generated path must explain the status of each hop:

```text
Agrippa
  --[APPROVED: participated in]-->
Battle of Actium
  --[PROPOSED: led to]-->
Veteran settlement policy
```

A path containing proposed or interpretive edges must not be described as an established factual chain. It should be presented as a research lead and should offer actions such as:

- Inspect evidence.
- Find an independent source.
- Challenge this connection.
- Save the path.
- Add a private note.
- Convert the path into a research task.

## Architecture consequences

These decisions add the following requirements:

1. `InquiryRunState` needs an owner, workspace, and visibility context.
2. Notes and Annotations must target Assertions and saved paths as well as Entities and SourceObservations.
3. The read API must compose the core pack with authorized overlay layers.
4. The write API must distinguish saving a private note from proposing a historical claim.
5. Obsidian synchronization needs stable IDs, frontmatter contracts, and conflict handling.
6. Multi-hop search must include or exclude approved, proposed, attributed, interpretive, private, and shared layers explicitly.
7. Export must enforce both visibility and quotation-rights rules.
8. Promotion from overlay to pack must be a reviewable transformation, not a visibility toggle.
9. Proposed claims must be matched against both approved and proposed claim families before another edge is created.
10. Narrative and explanatory content is a product requirement, not optional decoration.

## Decisions still open

The following decisions remain open:

- What should happen when no exact bibliographic authority heading exists?
- Should OrientationBriefs and research dossiers persist across inquiries?
- What authority, if any, may the second reviewing model exercise?
- Should resource discovery be exhaustive or budgeted and representative?
- For which kinds of inquiry should chronology be the default organizing principle?