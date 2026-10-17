Sequence Diagram
Your proposed reading order is coherent, but I would change the language from **“what governs, in reading order”** to two separate concepts: **reading order** and **authority precedence**. They should not be identical.

I cannot verify the actual contents behind the `vscode-webview://` links because those are local VS Code session addresses, not repository URLs. The assessment below therefore checks the architecture represented by your list, not line-by-line consistency inside the linked files. If you provide GitHub URLs or upload the documents, I can perform the actual cross-document audit.

## Recommended document hierarchy

| Order | Document                      | Proper role                                                                       | Normative authority                                               |
| ----: | ----------------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
|     1 | `19-SESSION-HANDOFF.md`       | Entry point, current state, open decisions, implementation status, and next steps | **Informational**, except for explicitly recorded decisions       |
|     2 | `31-ONE-COMMAND.md`           | Governing end-to-end agent workflow                                               | **Normative for orchestration and agent behavior**                |
|     3 | `30-LOGICAL-MODEL.md`         | Governing semantic and data model                                                 | **Normative for concepts, identities, states, and relationships** |
|     4 | `29-EVENT-CENTRED-INQUIRY.md` | Event-specific specialization of the general workflow                             | **Normative within event inquiries**                              |
|     5 | `32-RESEARCH-WORKSPACE.md`    | Curator/user workflow and research experience                                     | **Normative for workspace behavior**                              |
|     6 | `26-UI-DATA-CONTRACT.md`      | Boundary between stored model and explorer                                        | **Normative for API/view payloads**                               |
|     — | Input research documents      | Rationale and design evidence                                                     | **Informative, not governing**                                    |
|     — | Python, JSON, Cypher, plans   | Current implementation                                                            | Must conform to governing documents                               |

### Important correction

`19-SESSION-HANDOFF.md` should be read first, but it should **not be the highest architectural authority**. A handoff document changes frequently and can contain incomplete work, temporary conclusions, and implementation notes.

The actual governing center should be:

```text
31-ONE-COMMAND.md       governs behavior
30-LOGICAL-MODEL.md     governs meaning and stored structure
32-RESEARCH-WORKSPACE.md governs curator interaction
26-UI-DATA-CONTRACT.md  governs presentation boundaries
29-EVENT-CENTRED-INQUIRY.md specializes 31 for events
```

The handoff tells the next developer where the project stands relative to those specifications.

## Reading order

For a new developer, your proposed reading order mostly works:

1. `19-SESSION-HANDOFF.md`
2. `29-EVENT-CENTRED-INQUIRY.md`
3. `31-ONE-COMMAND.md`
4. `32-RESEARCH-WORKSPACE.md`
5. `26-UI-DATA-CONTRACT.md`
6. `30-LOGICAL-MODEL.md`

However, I would move `31-ONE-COMMAND.md` before `29-EVENT-CENTRED-INQUIRY.md`. The developer should understand the general agent workflow before reading its event-specific application.

### Revised reading order

1. **Session handoff** — Where are we?
2. **One command** — What does the system do?
3. **Logical model** — What objects and states exist?
4. **Event-centred inquiry** — How is the general model applied to Actium?
5. **Research workspace** — How does the curator work with it?
6. **UI data contract** — What does the explorer receive?
7. **Code and data** — What has actually been implemented?

This sequence moves from purpose to semantics to specialization to experience to implementation.

## Authority precedence

When two documents conflict, the project needs a deterministic precedence rule. I suggest:

```text
Recorded architectural decision
        ↓
30-LOGICAL-MODEL.md for semantic conflicts
31-ONE-COMMAND.md for behavioral conflicts
        ↓
29-EVENT-CENTRED-INQUIRY.md for event specialization
32-RESEARCH-WORKSPACE.md for curator interaction
26-UI-DATA-CONTRACT.md for interface representation
        ↓
Implementation code and configuration
        ↓
19-SESSION-HANDOFF.md
        ↓
Research inputs and exploratory notes
```

There is no universal precedence between documents 30 and 31:

- If the disagreement concerns what a `Claim`, `Inquiry`, `Account`, `Phase`, or `Proposal` means, document 30 governs.
- If it concerns which agent runs, in what order, with what review and stopping behavior, document 31 governs.
- If an event inquiry introduces a specialization not covered by 31, document 29 governs—but it should not contradict 31 without recording an explicit architectural decision.

## Document dependency flow

```mermaid
flowchart TD
    H["19 — Session Handoff<br/>Current state and navigation"]

    W["31 — One Command<br/>General agent workflow"]
    M["30 — Logical Model<br/>Semantic model"]
    E["29 — Event-Centred Inquiry<br/>Event specialization"]
    R["32 — Research Workspace<br/>Curator experience"]
    U["26 — UI Data Contract<br/>Explorer payload"]

    P["Input Research Documents<br/>Design evidence"]
    S["curation/sources.json<br/>Source registry"]
    PH["curation/phases.json<br/>Phase definitions"]
    C["Implementation<br/>Python, Cypher and plans"]

    H --> W
    H --> M

    P -.informs.-> W
    P -.informs.-> M
    P -.informs.-> E
    P -.informs.-> R

    W --> E
    M --> E

    W --> R
    M --> R

    M --> U
    R --> U
    E --> U

    S --> W
    PH --> E

    W --> C
    M --> C
    E --> C
    R --> C
    U --> C
```

The dotted edges are important: source reviews and architectural discussions **inform** the specification but do not govern production behavior directly.

## End-to-end sequence

This is the sequence diagram I would place in `31-ONE-COMMAND.md`.

```mermaid
sequenceDiagram
    autonumber

    actor Curator
    participant FD as Front Door
    participant Planner as Inquiry Planner
    participant Graph as Graph Inspector
    participant Dossier as Orientation Dossier
    participant Registry as Source Registry
    participant Adapter as Source Adapters
    participant Reader as Readers and Enrichers
    participant Recon as Claim Reconciler
    participant Rules as Deterministic Validator
    participant Review as Independent Reviewer
    participant Workspace as Research Workspace
    participant Store as Neo4j and Evidence Store

    Curator->>FD: Submit graph command

    FD->>FD: Classify intent and scope

    alt Program-level or unbounded command
        FD-->>Curator: Return coverage map and bounded inquiry choices
    else Material ambiguity
        FD-->>Curator: Request clarification
    else Executable inquiry
        FD->>Planner: Create bounded inquiry
    end

    Planner->>Graph: Inspect accepted and proposed graph
    Graph-->>Planner: Existing entities, claims, gaps, saved paths

    Planner->>Dossier: Search reusable orientation dossiers
    Dossier-->>Planner: Relevant versioned orientation

    Planner->>Registry: Select source families and adapters
    Registry-->>Planner: Access, rights, formats, costs, limitations

    Planner-->>Curator: Present line-item plan

    Curator->>Planner: Approve, reject, or modify items
    Planner->>Store: Persist approved plan and run state

    loop Approved source batches
        Planner->>Adapter: Retrieve bounded source records
        Adapter-->>Reader: Normalized source records
        Reader-->>Recon: Evidence packets and candidate claims

        Recon->>Graph: Match accepted and proposed claims
        Graph-->>Recon: Duplicate, related, conflicting, or absent matches

        Recon-->>Rules: Reconciliation decisions
        Rules-->>Review: Schema-valid proposals and evidence

        Review-->>Workspace: Independent verdicts and recommendations
        Workspace-->>Curator: Show proposals in graph context

        Curator->>Store: Accept, modify, reject, or defer
        Store-->>Planner: Updated coverage and marginal yield
    end

    Planner->>Planner: Apply budget and diminishing-return rule
    Planner->>Dossier: Propose dossier revision
    Planner-->>Curator: Run account, results, gaps, and stopping reason
```

## Event inquiry sequence

This belongs in `29-EVENT-CENTRED-INQUIRY.md`. It shows how the general process specializes for Actium.

```mermaid
sequenceDiagram
    autonumber

    actor Curator
    participant Planner as Inquiry Planner
    participant Event as Event Resolver
    participant Phase as Phase Planner
    participant Account as Stored Account Builder
    participant Sources as Source Workers
    participant Claims as Claim Reconciler
    participant Review as Reviewer
    participant Explorer as Graph Explorer

    Curator->>Planner: Graph the Battle of Actium

    Planner->>Event: Resolve focal event
    Event-->>Planner: Existing Event, identities and graph coverage

    Planner->>Phase: Propose phase spine
    Phase-->>Planner: Context, campaign, battle, aftermath and memory phases

    Planner->>Account: Create proposed inquiry account
    Account-->>Planner: Narrative structure with phase references

    Planner-->>Curator: Show event plan and line items
    Curator->>Planner: Approve or modify

    loop Each approved phase
        Planner->>Sources: Research phase using selected lenses
        Sources-->>Claims: Entities, evidence and candidate assertions
        Claims-->>Review: Reconciled proposals
        Review-->>Curator: Verdicts in event context
        Curator-->>Account: Accept, modify, reject or annotate
    end

    Account->>Explorer: Publish stored account projection
    Explorer-->>Curator: Narrative plus contextual graph

    Note over Account,Explorer: The narrative begins from the stored account,<br/>not from a transient UI-generated summary.
```

## Internal source sequence

The source review and `curation/sources.json` should feed the agent through a controlled registry rather than through prompt instructions. The source inventory distinguishes APIs, bulk downloads, structured editions, linked data, and consultative browser resources; it also distinguishes rights to retrieve, store, index, quote, and redistribute. [Agent resources.md](Agent%20resources.md)

```mermaid
sequenceDiagram
    autonumber

    participant Planner
    participant Registry as sources.json
    participant Policy as Rights and Access Policy
    participant Adapter
    participant External as External Source
    participant Normalizer
    participant Extractor
    participant Packet as Evidence Packet Store

    Planner->>Registry: Find sources for lens, entity kind and period
    Registry-->>Planner: Ranked source capabilities

    Planner->>Policy: Check intended operation
    Policy-->>Planner: Allowed access and storage behavior

    Planner->>Adapter: Execute source request
    Adapter->>External: API, SPARQL, download or consultation
    External-->>Adapter: Native response

    Adapter->>Normalizer: Preserve native payload and normalize fields
    Normalizer-->>Extractor: SourceRecord envelope

    Extractor->>Extractor: Identify mentions, observations and candidate claims
    Extractor->>Packet: Store evidence packet with provenance and rights

    Packet-->>Planner: Coverage contribution and warnings
```

## Proposal review flow

This belongs across `31-ONE-COMMAND.md`, `32-RESEARCH-WORKSPACE.md`, and `views/review-status.cypher`.

```mermaid
flowchart TD
    E["Evidence Packet"] --> C["Candidate Claim"]

    C --> M{"Match against accepted<br/>and proposed graph"}

    M -->|Exact match| D["EXACT_DUPLICATE"]
    M -->|Same assertion, new source| A["EVIDENCE_ADDITION"]
    M -->|Adds context or qualification| Q["QUALIFIER_ADDITION"]
    M -->|Different source framing| V["ALTERNATE_VOICE"]
    M -->|Incompatible assertion| X["CONFLICT"]
    M -->|No matching family| N["NEW_CLAIM"]
    M -->|Endpoint uncertain| I["IDENTITY_UNRESOLVED"]
    M -->|Outside plan| O["OUT_OF_SCOPE"]

    D --> DV["Deterministic Validation"]
    A --> DV
    Q --> DV
    V --> DV
    X --> DV
    N --> DV
    I --> DV
    O --> DV

    DV --> R["Independent Shadow Review"]
    R --> G["Contextual Graph Projection"]

    G --> U{"Curator decision"}

    U -->|Accept| P["Promote"]
    U -->|Modify| RP["Revised Proposal"]
    U -->|Reject| RJ["Rejected with reason"]
    U -->|Defer| DF["Deferred or research gap"]

    RP --> DV
```

## Workspace and private overlay

This should appear in `32-RESEARCH-WORKSPACE.md`.

```mermaid
sequenceDiagram
    autonumber

    actor Curator
    participant Obsidian
    participant Workspace
    participant Graph
    participant Planner
    participant Review

    Curator->>Obsidian: Write note or excerpt
    Obsidian->>Workspace: Synchronize note with target identifier

    Workspace->>Graph: Resolve node, claim, Work, passage or saved path
    Graph-->>Workspace: Stable target and contextual neighborhood

    Workspace->>Workspace: Store private overlay annotation

    alt Note only
        Workspace-->>Curator: Display note over core graph
    else Hypothesis
        Workspace-->>Curator: Mark as private hypothesis
    else Request graph expansion
        Workspace->>Planner: Create bounded inquiry from note
        Planner-->>Curator: Present line-item plan
    end

    Planner->>Review: Produce and review proposals
    Review-->>Workspace: Proposed additions in context

    Curator->>Workspace: Select material for promotion
    Workspace->>Workspace: Create governed public form
    Workspace->>Graph: Submit reviewed proposal

    Note over Workspace,Graph: Promotion creates a governed graph object;<br/>it does not merely change a visibility flag.
```

## Model consistency checks

Based on the document descriptions, these are the specific consistency questions the developer should answer.

| Question | Documents/code to compare |
|---|---|
| Is an `Event` the inquiry itself, or the focus of an `Inquiry`? | 29 vs. 30 vs. `contracts.py` |
| Is the stored `Account` an entity, document, projection, or versioned narrative artifact? | 29 §4a vs. 26 vs. 30 |
| Are phases graph objects, configuration records, or both? | 29 §10, `phases.json`, `event_phases.py`, 30 |
| Are proposed claims stored in Neo4j or a separate proposal store? | 30, 32, `review-status.cypher` |
| Can proposed claims participate in pathfinding by default? | 32 vs. 26 |
| Does the UI receive raw claims or already assembled graph projections? | 26 vs. 30 |
| Does the narrative account reference claim IDs, evidence IDs, or only entities and phases? | 26, 29, 30 |
| Are notes allowed on native Neo4j relationships, or only on reified claims/assertions? | 30 vs. 32 |
| Is the orientation dossier a graph object, document artifact, or orchestration record? | 31 vs. 30 |
| Does `sources.json` govern source capability, rights, access, and adapter selection separately? | 31 vs. `sources.json` |
| Are independent witnesses represented as source records, evidence objects, or source traditions? | 31 vs. 30 |
| Does the reviewer return advice only, with no promotion transition? | 31, 32, `contracts.py` |
| Are program, inquiry, and run represented distinctly? | 31 vs. 30 vs. `contracts.py` |
| Can one inquiry contain multiple focal events? | 29 vs. general workflow |
| Does every status used by the UI exist in the logical model and Cypher view? | 26, 30, `review-status.cypher` |

## Likely modeling issue

The phrase **“the event as the inquiry”** deserves scrutiny.

It can mean either:

```text
Event = Inquiry
```

or:

```text
Inquiry --FOCUSES_ON--> Event
```

The second is safer.

The Battle of Actium is a historical entity. An inquiry about Actium is a research activity with scope, budget, lenses, plans, source selections, runs, stopping conditions, and curator decisions. Several distinct inquiries may focus on the same event:

- The naval campaign.
- Coalition networks.
- Ship technology.
- Augustan commemoration.
- Ancient narrative traditions.
- Archaeology of the victory monument.

Therefore, the logical model should not collapse the event and inquiry into one object.

```mermaid
classDiagram
    class Program {
        +programId
        +title
        +status
    }

    class Inquiry {
        +inquiryId
        +question
        +scope
        +organizingMode
        +status
    }

    class InquiryRun {
        +runId
        +budget
        +startedAt
        +stoppingReason
        +status
    }

    class HistoricalEntity {
        +entityId
        +kind
        +label
    }

    class Event {
        +startDate
        +endDate
    }

    class Phase {
        +phaseId
        +label
        +sequence
        +temporalBounds
    }

    class Account {
        +accountId
        +version
        +status
    }

    class Claim {
        +claimId
        +predicate
        +status
    }

    class Evidence {
        +evidenceId
        +sourceRecordId
        +locator
    }

    HistoricalEntity <|-- Event
    Program "1" --> "many" Inquiry : contains
    Inquiry "1" --> "many" InquiryRun : executedBy
    Inquiry "many" --> "many" HistoricalEntity : focusesOn
    Event "1" --> "many" Phase : organizedInto
    Inquiry "1" --> "many" Account : produces
    Account "many" --> "many" Phase : structures
    Account "many" --> "many" Claim : cites
    Claim "many" --> "many" Evidence : supportedBy
```

## Stored account concern

The stored account should not become a second uncontrolled truth layer. It should be a **versioned narrative assembly** that references claims, evidence, phases, entities, and source voices.

A paragraph in the account should be traceable to:

```text
AccountSection
    → Phase
    → Claim
    → Evidence
    → SourceRecord
```

Interpretive prose may exceed any one claim, but it must be marked as authored synthesis and remain distinguishable from quoted or paraphrased source content.

The explorer can then start from the account while allowing the curator to move outward into the graph and evidence.

## Phase-model concern

`curation/phases.json` and `discovery/event_phases.py` should not imply that every event receives a rigid chronological template. The phase service should propose an ordered or partially ordered phase plan when chronology is appropriate.

For Actium, the phases might include:

```text
Political rupture
    → Coalition formation
    → Strategic preparation
    → Agrippa's maritime campaign
    → Encampment and blockade
    → Battle
    → Surrender and pursuit
    → Alexandria
    → Settlement and commemoration
```

Some event inquiries may use overlapping phases, uncertain boundaries, or thematic rather than strictly sequential structures. The logical model should therefore support:

- `PRECEDES`
- `OVERLAPS`
- `PART_OF`
- `ALTERNATIVE_TO`
- `TEMPORALLY_UNCERTAIN`
- `PHASE_OF_ACCOUNT`

A phase plan may be an inquiry structure before it becomes an approved historical structure.

## Recommended document headers

Every governing document should begin with metadata like:

```yaml
---
document_id: CHR-ARCH-031
title: One Command
status: governing
authority_scope:
  - agent orchestration
  - source selection
  - review workflow
supersedes:
  - CHR-ARCH-OLD-CONCIERGE
depends_on:
  - CHR-MODEL-030
specialized_by:
  - CHR-METHOD-029
implemented_by:
  - orchestration/contracts.py
  - curation/sources.json
last_reviewed: 2026-10-17
open_decisions: []
---
```

This removes ambiguity about whether a document is governing, explanatory, superseded, or merely an input.

## Recommended decision register

The seven decisions developed in the addendum should not remain embedded only in narrative documents. Create a compact decision register:

| ID | Decision |
|---|---|
| ADR-001 | User and curator are presently the same role; guided approval is the default |
| ADR-002 | Approved and proposed claims appear in one contextual graph projection |
| ADR-003 | Local Subjects may be created when authority vocabularies lack the needed compound concept |
| ADR-004 | Orientation dossiers persist as versioned research assets |
| ADR-005 | Independent reviewers operate in shadow mode without promotion authority |
| ADR-006 | Source discovery begins with a budget and stops on measured diminishing returns |
| ADR-007 | Chronology is used when explanatory, not imposed on abstract inquiries |
| ADR-008 | Broad commands become Programs and bounded Inquiries rather than unbounded runs |

Each ADR should record:

- Decision.
- Rationale.
- Consequences.
- Alternatives rejected.
- Documents affected.
- Code affected.
- Date.
- Status.

## Developer handoff checklist

Before implementation continues, the developer should verify:

1. `contracts.py` contains distinct `Program`, `Inquiry`, `InquiryRun`, `PlanItem`, `OrientationDossier`, `EvidencePacket`, `Proposal`, and `ReviewerVerdict` contracts.
2. `sources.json` describes retrieval capability separately from legal permission.
3. `phases.json` represents phase templates or proposals—not universal historical facts.
4. `event_phases.py` generates a proposed structure and does not directly promote phases.
5. `review-status.cypher` returns accepted and proposed claims together with explicit status.
6. The UI contract includes stable identifiers for annotations and saved paths.
7. The stored account references claims and evidence rather than duplicating historical statements as unaudited prose.
8. The reviewer cannot invoke a promotion transition.
9. Source batches record marginal yield and stopping reasons.
10. The implementation emits state transitions that can be resumed after interruption.

The architecture is now internally plausible. The highest-priority audit is the boundary among **Event, Inquiry, Phase Plan, approved Phase, and stored Account**. If those five objects are cleanly distinguished, the rest of the orchestration and UI flow becomes much easier to implement correctly.