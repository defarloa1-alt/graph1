# Response: Use Cases

**Responds to:** [use cases.md](use%20cases.md)
**Date:** 2026-10-11

> **Note (2026-10-13).** Where this response makes review the condition for an edge
> being seen or used (including Phase C's automatic acceptance), it is overtaken:
> everything is visible at once, labelled with its status and source; the curator promotes rather than gates ([25](../25-LIVES-AND-PLAYGROUND.md) decision 2). Acceptance
> still matters for attestation and narrative, not for visibility.

## The governing purpose

Chrystallum is not an encyclopedia. Its purpose is to let a person explore a
network of historical relations, discover connections, and navigate paths
that most minds cannot easily hold or trace on their own: from a Roman senator
to a mollusk through purple dye, from a Spartan freebooter to Cleopatra
through a pursuit at sea.

That purpose changes what to optimize:

| Encyclopedia goal | Exploration goal |
|---|---|
| Complete facts about each subject | Dense, typed, explained edges between diverse things |
| Only accepted facts are useful | A clearly marked proposed or attributed edge is a useful lead |
| Review everything before use | Review where people actually navigate |
| Errors are local (one wrong fact) | Errors propagate: a wrong identity or generic edge creates false paths |
| Depth per subject | Connections across subjects and facets |

Every recommendation below follows from this table.

## Thoughts on each use case

### 1. Domain packs as the commercial unit

Agreed, and the build is already shaped for it. A pack is: predicate registry
extensions, inquiry templates and guidance, a federation profile (adapters
and authorities), curated seed entities, and an evaluation set. The core
(identity, claims, provenance, proposal and review, navigation) stays
unchanged underneath. Much of a pack is already data rather than code
(`predicates.v2.json`, inquiry files).

For exploration, a pack's distinctive value is its **predicates and bridges**:
the relation types that make paths meaningful in that domain, and the edges
that connect it to other packs. Do not sell packs until a second domain runs
on the core unchanged (acceptance criterion 14).

### 2. "Graph X" and drill-down

Drill-down is a Subject focused on the clicked node: click "bronze", the
concierge's scope decision (08) admits it, a Subject *History of bronze* (or
*Roman bronze-working*) is created, and an inquiry opens for it. The node
becomes a doorway into a new region of the network.

The real gap is source discovery. Today a source must be handed to the
reader. For arbitrary X the agent must find sources itself (E10, E9). That is
the capability that makes "Graph X" real.

### 3. User-defined information, annotations, and visibility

Two different things:

- **Edits to knowledge** (add, update, remove nodes and relations) go through
  the same proposal path, with the user as curator, so every change keeps
  provenance. "Remove" means deprecate or supersede, not delete.
- **Annotations** are commentary, not claims: their own node type with owner
  and visibility (private, team, public). They may be deleted freely.
  Annotations are also exploration aids: notes, saved paths, and pins that
  record what a user found.

Visibility must be enforced in the read API, not only stored as a property. A
`visibility: private` property does not stop anyone who can run Cypher. This
requires user identity and the access roles sketched in
[05-AGENT-BOUNDARIES.md](../05-AGENT-BOUNDARIES.md).

### 4. The vertical slice

Agreed. It proved the governance pattern (verbatim quotations gate passage
evidence, identity is a curator decision, evidence and claims are decided
separately) and taught what was missing (depictions versus facts, inquiry
scoping, hardcoding). It has not yet proved generality: unseen text, a second
source, a second domain.

### 5. Where CCA, SCA, and SFA stand

None exists as an agent yet. Their functions exist, split between code and
the curator:

| Planned role | Today |
|---|---|
| CCA (front door, plans) | The curator, writing the inquiry file by hand. The inquiry is the CCA's output contract (InquiryPlan). |
| SCA (coordinates, adjudicates) | The validator and store do the mechanical part (duplicates, scope, evidence checks); the curator does the judgment through the review CLI. |
| SFA (facet research) | The passage reader is closest, but it is source-driven ("read this text within this scope"), not facet-driven. The Wikidata proposer is a deterministic relative; the identity queue is a resolution helper. |

Facets do not need to be separate agents. They can be **lenses**: the same
reader with facet guidance in the inquiry. For exploration, lenses matter
because cross-facet edges are where surprising paths come from: the purple
path runs political → social → technological → biological.

### 6 and 7. Packages versus "Graph the Roman Republic"

Not a choice but a sequence: 7 is 6 with planning and fan-out automated.
Under the exploration purpose, 7 is more attractive than it first looks,
because high volumes of quoted, attributed edges are valuable for navigation
even before review. But three things must be true first:

1. **Volume must be navigable, not just stored.** Thousands of edges without
   path tracing, ranking, and status-aware display are noise.
2. **Review must follow demand.** A curator cannot review thousands of
   proposals. Mechanically verifiable attributed claims (E12) can be accepted
   by policy; human judgment goes to identity, promotion to asserted, contested
   claims, and the edges on paths people actually traverse.
3. **Breadth needs decomposition.** "The Roman Republic" is too broad for one
   SCA. The concierge decomposes it into a subject constellation (07): Social
   status, Life of Cicero, Actium, and so on, each its own inquiry, with facet
   lenses inside each.

The short-lived, stateless agents in item 7 are the right model: the graph,
inquiries, and queues are the memory; each agent loads current state when it
starts (as inquiry scope loading already does), and deterministic IDs plus
duplicate detection already make parallel agents safe. The legacy repository
attempted 7 first (eighteen facets, batch training, SFAs) and accumulated
complexity before the core was proven; that is why the clean start exists.

## Recommendation in detail

Build toward 6 in a way that makes 7 mostly a scheduler. Each phase lists
what it delivers, why it matters for exploration, and how it is known to work.

### Phase A — Attributed claims and micro-events (E12, E11 pilot)

- **Deliver:** claim mode (`asserted` / `attributed` with `attributedTo`);
  Work entities (Plutarch, *Life of Antony*); depicted micro-events from
  *Antony* 65–68 (about fifteen) proposed as entities and reviewed;
  performedBy, movedTo/From, triggeredBy, resultedIn, and precededBy claims
  between them, attributed to Plutarch; relative time markers ("fifth day",
  "sixth hour") as a minimal temporal qualifier.
- **Why:** micro-events are the connective tissue of exploration. They join
  people, forces, places, and moments, so the network gains many short,
  meaningful paths ("Eurycles → pursued → Antony's galley → joined →
  Cleopatra's ship").
- **Done when:** the battle can be walked step by step (Bloom for smoke testing), every step
  quoted and labelled "according to Plutarch"; sequence comes from time
  markers, not narration order.

### Phase B — Exploration read API and path tracing

- **Deliver:** `getNeighborhood` and `traceExistingPath` from
  [06-GRAPH-NAVIGATION.md](../06-GRAPH-NAVIGATION.md) as a small API or CLI
  over the committed graph: bounded hops; filters by predicate family, status,
  and claim mode; hop-by-hop explanation built from quotations; ranking by
  predicate specificity and evidence, with **hub penalties** and with Year and
  Subject nodes excluded as shortcuts (otherwise everything connects through
  "31 BCE"); annotations and saved paths with enforced visibility (use case 3).
- **Why:** this is what the explorer UI
  ([20-EXPLORER-UI.md](../20-EXPLORER-UI.md): React + Cytoscape.js, designed in
  Figma) is built on. Bloom is used only for smoke testing.
- **Done when:** "trace Eurycles to Cleopatra" returns a ranked, explained
  path with each hop's status, mode, and quotation, and generic or hub paths
  are suppressed.

### Phase C — Measurement and review policy

- **Deliver:** the reader run unchanged on unseen text (another stretch of
  *Antony* or another Life) with measured curator acceptance; an automatic
  acceptance policy for attributed claims that pass every mechanical check;
  demand-driven review (edges on traced or saved paths are flagged for the
  curator); visible confidence and mode in every projection.
- **Why:** this makes volume safe. Without it, item 7 either floods the
  curator or fills the network with unmarked guesses.
- **Governance:** route review by impact (E15): low-impact changes inside
  one cluster follow the policy; changes crossing clusters or touching shared
  vertices go to each affected cluster's curators.
- **Done when:** acceptance rate on unseen text is known; the policy is
  written and enforced in code; the curator's queue contains only judgment
  calls.

### Phase D — Lenses, second source, concierge-lite

- **Deliver:** facet lenses in the inquiry; `source.type` and an adapter
  interface (the reader stops assuming Perseus TEI); context window and scope
  rule in the inquiry; slice scripts as data; a concierge that turns "Graph X"
  or a node drill-down into an inquiry file (scope decision, Subject, scope,
  guidance, candidate sources).
- **Why:** cross-facet edges create bridges; a second source tests that
  depictions coexist; the concierge makes drill-down (use case 2) a single
  action.
- **Done when:** Plutarch and a second source describe the same battle as
  separate attributed narratives, and "Graph bronze" produces a valid inquiry
  without hand editing.

### Phase E — Source discovery (E10, E9)

- **Deliver:** candidate sources from in-text citations (*Antony* 68.1 →
  Augustus's memoir), Wikidata `described by source`, CTS catalogues, and the
  research API; Work entities with dates; a source plan ranked by date, genre,
  and independence.
- **Why:** exploration across sources (who said what, when, relying on whom)
  is itself a network to navigate.
- **Done when:** for Actium the agent proposes Horace, Virgil, Propertius, and
  Velleius before Plutarch, each with a reason.

### Phase F — Orchestrated fan-out (use case 7)

- **Deliver:** a scheduler that expands a subject constellation into inquiries
  × lenses × sources with budgets and stopping rules; workflow state outside
  Neo4j; run dashboards (proposals, acceptance, cost).
- **Gates:** Phase C acceptance rate and policy in force; Phase B tracing
  works at the current scale; a second domain runs on the core unchanged.
- **Done when:** "Graph the Roman Republic" produces a navigable, ranked,
  status-marked network whose review load stays within the curator's
  capacity.

### Alongside

- Phase 7 temporal qualification grows from Phase A's relative markers into
  dates, ranges, offices, and marriages.
- Identity stays curator-governed throughout: in an exploration graph, a wrong
  identity is a false bridge.
- Domain packs (use case 1) follow the second domain.

## One-line summary

Make every edge typed, quoted, attributed, and status-marked; make the network
walkable with explained paths; then let agents fill it in at volume, with
review following where people actually explore.
