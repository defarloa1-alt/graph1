# Explorer UI Direction

> **History (2026-10-19).** This document is the first UI direction and is no
> longer current. What the screen is now (the hub, the command drawer, stage
> modes, configurable sidebars, no top bar, no chat panel) is in
> [26](26-UI-DATA-CONTRACT.md) §1 and decisions D-101 to D-112 in
> [33](33-DECISIONS.md); the drawing is wireframe v7
> (`explorer/wireframes/`). Where this document disagrees with them, they win.
> Still useful here: the cards (§3), charts (§4), visual encoding (§5), and the
> read and write boundary (§6). The map's renderer is open (D-103): §4a's
> Google Maps and deck.gl is one candidate, not a decision.

**Status:** direction agreed 2026-10-11; design not started. Updated
2026-10-13: the curator's layout adds a chat section, and the shapes the UI
receives are fixed in [26-UI-DATA-CONTRACT.md](26-UI-DATA-CONTRACT.md).

**Curator's layout (2026-10-13).** A large centre stage, a chat section, and
borders with various uses: details of the selected node or fact, filtering
options, the time slider. Nobody navigates Proposals, Assertions, or
passages; they appear as text in a sidebar. One line on the canvas is one
fact, however many sources state it, and each source is a voice on the
fact's card (26 §2–3). The chat carries the narrative and answers questions
in the user's persona; for an event the narrative starts from Chrystallum's
stored account, every statement citing a preserved passage (29 §4, which
replaced "from the graph only"; 26 §5). What a user asserts in chat is
captured as a note or proposal, never written as fact. The layout
below is the earlier sketch; where they differ, this paragraph and 26 win.

## 1. Purpose and stack

The explorer is the product surface for Chrystallum's purpose: exploring a
network of historical relations, discovering connections, and navigating
paths that most minds cannot easily trace on their own
([docs/Response - Use Cases.md](docs/Response%20-%20Use%20Cases.md)).

- **Stack:** React + Cytoscape.js, designed in Figma.
- **Neo4j Bloom** is used only for smoke testing during development. It is not
  part of the product.
- **Starting point:** the legacy [viewer](../viewer) already uses React 18,
  Cytoscape.js (`react-cytoscapejs`), the cola layout, and Vite. Per
  [16-LEGACY-TRIAGE.md](16-LEGACY-TRIAGE.md) it is `ADAPT`: reuse components
  once the clean-start read API exists, not its legacy API assumptions.

## 2. Layout: centre stage with ribbons

```text
┌───────────────────────────────────────────────────────────────┐
│ top ribbon: inquiry/subject · search · trace mode · lenses     │
├──────────┬───────────────────────────────────────┬────────────┤
│ left     │                                       │ right      │
│ ribbon:  │          CENTRE STAGE                 │ ribbon:    │
│ navigate │   Cytoscape graph canvas              │ filter     │
│          │   (bounded neighbourhood or path)     │            │
│ subjects │                                       │ status     │
│ history  │                                       │ claim mode │
│ saved    │                                       │ predicates │
│ paths    │                                       │ facets     │
│ pins     │                                       │ sources    │
├──────────┴───────────────────────────────────────┴────────────┤
│ bottom ribbon: timeline slider (years → relative battle time) │
└───────────────────────────────────────────────────────────────┘
          detail cards open over or beside the stage
```

- **Centre stage:** the graph canvas showing one bounded projection at a
  time: a neighbourhood, an expanded relationship family, or a traced path.
  Never the whole database ([06-GRAPH-NAVIGATION.md](06-GRAPH-NAVIGATION.md)).
- **Left ribbon (navigate):** search, subjects and drill-down entry points,
  navigation history and breadcrumbs, saved paths, pinned nodes, annotations.
- **Right ribbon (filter):** status (accepted, proposed, contested, rejected
  in audit mode), claim mode (asserted versus "according to" a source),
  predicate families, facet lenses, sources and works.
- **Top ribbon:** current inquiry and subject, global search, mode switch
  (explore, trace existing path, discover semantic bridge), active lens.
- **Bottom ribbon:** timeline slider. Filters the stage by year, and for event
  inquiries zooms to relative time within an event (the fifth day, the sixth
  hour) once Phase A micro-events exist.

## 3. Cards

Detail cards are where provenance lives; the stage stays readable.

| Card | Shows |
|---|---|
| Entity | label, kind, description, aliases and dates, identity links, status, subjects it belongs to; image with what it depicts, when made, author, and license (E14) |
| Fact (edge) | the fact as a sentence, its attestation in words, status, and one voice per source ("according to Plutarch", or our own statement) with its quotations and locators; decisions and who made them collapsed (26 §2–3) |
| Source / passage | work, author, edition, locator, full passage with the quoted span marked, editorial notes kept separate, rights |
| Path | hop-by-hop explanation, each hop linked to its claim card; weakest hop; how many hops are inferred, proposed, or attributed |
| Proposal (review mode) | the proposal, its pending evidence, uncertainty notes, accept and reject actions |

## 4. Charts

Supporting views beside the stage, all driven by the current projection:
timeline density of events and claims; actor activity across an event; claims
by source and by mode; source chronology (which witnesses are earliest and
independent, from E10); degree and hub indicators that explain why hub paths
are down-ranked.

## 4a. Map panel (E13)

A map panel beside the centre stage, synchronized with it: selecting a node
highlights its places; selecting a place filters the stage; the bottom
timeline drives both.

- **Rendering:** Google Maps JavaScript API with deck.gl on the WebGL overlay;
  historical layers (Pleiades places, ancient coastlines, ORBIS routes) above
  the modern basemap, which alone misleads for antiquity.
- **Data:** coordinates come from Pleiades or Wikidata through the read API,
  never stored from Google.
- **Layers:** places (with precision radius), depicted movement tracks per
  source with status encoding, computed analyses (sightlines, travel times)
  visibly marked as computed.
- **Modes:** place doorway (everything at a place across time); place
  resolution (candidate pins for the identity queue); battle replay by source.

## 5. Visual encoding

Following [06-GRAPH-NAVIGATION.md](06-GRAPH-NAVIGATION.md):

- **Status** on edges: accepted solid; proposed dashed and muted; contested
  with a warning marker; rejected and superseded hidden outside audit mode.
- **Claim mode:** asserted versus attributed must be visibly different (for
  example a filled versus hollow edge marker), so "according to Plutarch" is
  never mistaken for an established fact.
- **Facet colour** shows the active lens, not a permanent classification.
- **Node shape** by role: entity, subject, source, claim when expanded.
- Figma design tokens feed the Cytoscape stylesheet, so design and canvas
  share one source of truth.

## 6. Read and write boundary

The UI reads through the Phase B exploration API (`getNode`,
`getNeighborhood`, `expandRelationshipFamily`, `getAssertionEvidence`,
`traceExistingPath`, `getTemporalContext`). It never sends Cypher. Every write
(proposal decisions, user edits, annotations) is a command through the same
validation and proposal path agents use. Annotation visibility (private,
team, public) is enforced by the API, not by the canvas.

## 7. Sequence

1. Phase B read API and path tracing (no UI dependency; CLI first).
2. Figma: layout, ribbons, cards, encodings, tokens.
3. Adapt the legacy viewer onto the new API: stage, cards, filters.
4. Timeline slider and charts; trace and bridge modes.
5. Review mode (proposal cards) replacing the review CLI for the curator.
