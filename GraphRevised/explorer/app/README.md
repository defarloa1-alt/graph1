# Chrystallum Explorer (app)

The React app for the explorer (D-101): Vite, React, TypeScript, plain CSS variables, Cytoscape.js
for the graph. The screen it builds toward is [26](../../26-UI-DATA-CONTRACT.md) §1 and wireframe v8
(`../wireframes/`); decisions D-101 to D-131 in [33](../../33-DECISIONS.md).

Built one part at a time, each reviewed in Storybook with its states (light and dark, persona):

```bash
npm install
npm run storybook   # the parts, http://localhost:6006
npm run dev         # the app
```

- `src/styles/tokens.css`: the design tokens, the same values as the Figma Color and Size variables.
- `src/icons/`: kind and lens icons, one markup for the React icon and the canvas picture.
- `src/components/`: the parts; `src/stories/`: foundations and proposals (not adopted until decided).
- `src/words.ts`: every word shown for a stored value, in one place.

Data is not in git: keep local explorer snapshots in
`GraphRevised/explorer/snapshots/` (git-ignored). They are opened explicitly
from disk rather than served from the app's public directory.

## Event Subject assertions

The app provides a read-only graph overview and assertion table for an Actium
Subject snapshot, and for versioned event Subject snapshots from other inquiries.
Legacy Actium snapshots remain supported.
From the repository root, create the snapshots directory if needed, then
generate a fresh file with a new name (the command refuses to overwrite an
existing one):

```powershell
New-Item -ItemType Directory -Force GraphRevised\explorer\snapshots
python -m GraphRevised.discovery.actium_subject_view --output GraphRevised\explorer\snapshots\actium-view-new.json
```

For an existing non-Actium event inquiry with a Subject-to-focus link, use
`python -m GraphRevised.discovery.event_subject_view path\to\inquiry.json --output GraphRevised\explorer\snapshots\event-view-new.json`.
Pass `--section-id chr:subject:...` only for an existing direct child Subject
whose explicit topical placements should be included; otherwise none are
included. This command does not create an inquiry, sources or graph data.

In `GraphRevised\explorer\app`, run `npm run dev`, open the displayed local
URL, and choose that JSON file with **Open view JSON**. The file stays in the
browser; no graph credentials or server are needed by the table. The snapshot
does not update automatically: generate and open a new file to refresh it.
The graph starts with the history Subject, focus event, and (when present in
the snapshot) Meaning and memory Subject. Expand phase links and topical
depictions independently and select a node to inspect its status and evidence.
It is a bounded overview, not the complete graph, and calls out the older
phase-to-battle assertion when it appears in the snapshot. Switch to
**Assertion table** for all included assertions.
**Source timeline** shows one source's normalized dates, source time
expressions, explicit `happenedBefore` claims, and events with no normalized
date or order claim separately. Events with only unnormalized time expressions
also appear in the latter group. Dates use EDTF astronomical year numbering
(for example, `-0028` means 29 BCE; `~` means approximate).
**Compare sources** shows two independently selectable
source lanes and their recorded `depictsSameAs` assertions, including proposed
matches with their status. The lists are not a total order; overlapping dates
and disconnected order claims do not establish sequence. Phase placement and
matching depictions never transfer dates or establish independent
corroboration. Claim evidence and statuses are available in each item.
Open **Evidence and assertion details** for the recorded supporting quotation
and preserved passage, or **Source mentions** for passages linked to a depiction
without implying they support a particular claim. Citations, edition, rights,
and source links accompany the text. Text is exported only when recorded rights
match supported public-domain or open-license statements; other text is withheld.
Public-domain statements may be jurisdiction-specific. Older snapshots may
contain references but no source text; regenerate the snapshot to check.
Older snapshots do not contain timeline data; generate a new one.
Search and filter by status, predicate, source, or route; open an assertion's
details to inspect its evidence and each placement path. Proposal evidence
retains its status, including rejected proposals, and paths do not turn
proposed claims into accepted facts. Pilot topical Subject placements are
shown separately from event `partOf` routes with their own review status and
source assertion evidence. The table does not accept or modify
assertions. The source filter applies to the assertion's own voice and evidence,
not evidence on its placement paths. Snapshot files may contain unpublished
graph data.

The status guide distinguishes assertions, placements, proposals and source
observations. Evidence is grouped by observation ID in each evidence list,
while every support and proposal record remains visible with its own status,
quotation and rationale when recorded. Counts are of observations within that
list, not counts of independent authors or corroborating sources. A passage
may also recur across separate assertions and routes.
