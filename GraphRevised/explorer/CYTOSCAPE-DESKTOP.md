# Cytoscape Desktop and the Neo4j graph

**For:** the curator, opening the local Neo4j graph in Cytoscape Desktop 3.10.4 (installed in `C:\Program Files\Cytoscape_v3.10.4`).
**Status (2026-10-16):** the flatten step has been run on the current export (195 nodes, 337 fact edges). The import into Cytoscape itself (A, step 3) and routes B and C have not yet been run against a live Cytoscape.

Cytoscape Desktop starts blank because nothing connects it to Neo4j. You load a network into it. There are three ways, from simplest to most flexible:

| Route | What you do | Gets you |
|---|---|---|
| **A. File import** | Export, flatten, then *File › Import › Network from File* | The exploration view (one line per fact). No extra install. |
| **B. One command** | Install `py4cytoscape`, then run the helper with `--push` while Cytoscape is open | The same view, loaded and styled automatically |
| **C. Your own Cypher** | A Python snippet sends any query result to Cytoscape | Any subgraph you choose, including storage nodes, for checking |

All three only **read** Neo4j. Nothing comes back from Cytoscape into the graph.

> Cytoscape Desktop is for looking and checking, like Bloom. The product is the React and Cytoscape.js explorer (20-EXPLORER-UI.md).

## 0. Before you start

1. **Neo4j is running locally**: Neo4j Desktop, database `neo4j`, at `neo4j://127.0.0.1:7687`.
2. **The password is in your shell.** It lives in `GraphRevised/Connections.txt`. Load it without printing it.

   Git Bash:
   ```bash
   cd C:/Projects/Graph1
   export NEO4J_PASSWORD="$(sed -n 's/^neo4j pw is //p' GraphRevised/Connections.txt | tr -d '\r')"
   ```
   PowerShell:
   ```powershell
   cd C:\Projects\Graph1
   $line = Get-Content GraphRevised\Connections.txt | Where-Object { $_ -like 'neo4j pw is *' } | Select-Object -First 1
   $env:NEO4J_PASSWORD = $line.Substring('neo4j pw is '.Length).Trim()
   ```
   Never paste the password into a file, a command you share, or a chat.
3. **Cytoscape Desktop is open** (Start menu › Cytoscape 3.10.4).

## A. File import (no extra install)

**Step 1. Export from Neo4j.** This reads the graph and writes the exploration view: entities as nodes, one edge per fact, each with its attestation and voices.

```bash
python -m GraphRevised.export.cytoscape
```
It prints something like `195 nodes, 337 fact edges` and writes `GraphRevised/exports/graph.cyjs`. Add `--audit` to include rejected and superseded content.

**Step 2. Flatten it for Desktop.** Desktop's table columns hold text, numbers and lists of text, not nested objects. The export nests each fact's voices as objects, so this step drops those and keeps their text versions (`voiceLines`, `reviewLines`).

```bash
python GraphRevised/explorer/cytoscape_desktop.py
```
It writes `GraphRevised/exports/graph-desktop.cyjs`.

**Step 3. Import into Cytoscape.**
1. *File › Import › Network from File…*
2. Choose `C:\Projects\Graph1\GraphRevised\exports\graph-desktop.cyjs`.
3. The network appears in the *Network* panel on the left. If the canvas stays empty, see Troubleshooting.

**Step 4. Lay it out.** The export carries no positions, so everything starts in one spot.
- *Layout › Prefuse Force Directed Layout* (or *Layout › yFiles Organic* if you have yFiles).
- Then *View › Fit Content*.

**Step 5. Style it.** Open the *Style* tab in the Control Panel on the left. Use the arrow beside each property to choose a column and a mapping type.

| Property | Column | Mapping | Values |
|---|---|---|---|
| Node › Label | `label` | Passthrough | |
| Node › Shape | `kind` | Discrete | Person: Ellipse · Event: Diamond · Place: Triangle · Group: Round Rectangle · Office: Hexagon · Work: Rectangle · Concept: Octagon · Period: Parallelogram |
| Node › Border Line Type | `status` | Discrete | proposed: Dash |
| Edge › Label | `label` | Passthrough | |
| Edge › Line Type | `status` | Discrete | proposed: Dash |
| Edge › Source Arrow Shape | `mode` | Discrete | attributed: Open Circle (the fact is "according to" a source only) |
| Edge › Target Arrow Shape | (default) | | Delta |

Save the style once with *Style › ☰ › Create New Style*, named `Chrystallum`, and reuse it on later imports.

**Step 6. Read a fact.** Click an edge. The *Edge Table* at the bottom shows its `sentence`, `attestation` (in words), `times`, and `voiceLines` (one line per source, with locators). Click a node for its `description`, `factLines`, `notes` (passages of note) and `authorityLines`.

## B. One command (styled automatically)

1. Install the client once:
   ```bash
   pip install py4cytoscape
   ```
2. With Cytoscape open (it listens on port 1234 through CyREST, which is built in), run:
   ```bash
   python -m GraphRevised.export.cytoscape
   python GraphRevised/explorer/cytoscape_desktop.py --push
   ```
   This imports the file, creates the `Chrystallum` style with the mappings from step 5, runs a force-directed layout, and fits the view. If a style property is rejected (property names differ slightly between Cytoscape versions), the script stops with the property's name. Set that one by hand as in step 5.

## C. Your own Cypher (any subgraph)

For a question the export doesn't answer, query Neo4j and send the result straight to Cytoscape. This example draws everything one fact away from Mark Antony, with each claim drawn as an edge:

```python
import os
import pandas as pd
import py4cytoscape as p4c
from neo4j import GraphDatabase

QUERY = """
MATCH (a:Assertion)-[:ASSERTION_SUBJECT]->(s:Entity)
MATCH (a)-[:ASSERTION_OBJECT]->(o:Entity)
WHERE (s.id = $focus OR o.id = $focus) AND a.status IN ['accepted', 'proposed']
RETURN s.id AS source, s.label AS source_label, s.kind AS source_kind,
       o.id AS target, o.label AS target_label, o.kind AS target_kind,
       a.predicate AS predicate, a.status AS status, a.mode AS mode
"""

driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", os.environ["NEO4J_PASSWORD"]))
with driver.session(database="neo4j") as session:
    rows = session.execute_read(lambda tx: tx.run(QUERY, focus="chr:entity:mark-antony").data())
driver.close()

df = pd.DataFrame(rows)
nodes = pd.concat([
    df[["source", "source_label", "source_kind"]].set_axis(["id", "label", "kind"], axis=1),
    df[["target", "target_label", "target_kind"]].set_axis(["id", "label", "kind"], axis=1),
]).drop_duplicates("id")
edges = df[["source", "target", "predicate", "status", "mode"]].rename(columns={"predicate": "interaction"})

p4c.create_network_from_data_frames(nodes, edges, title="Antony, one step", collection="Chrystallum")
p4c.layout_network("force-directed")
```

Notes:
- This draws **one edge per claim**. A fact stated by four sources shows four parallel lines. The export (route A) merges them into one line per fact, with the voices on it; prefer it for exploring.
- Raw storage labels (`Assertion`, `Proposal`, `SourceObservation`, `AuthorityRecord`, `Year`) can be queried the same way for checking. They are never part of the explorer's canvas (25 §5).
- Keep queries read-only (`execute_read`).

## Refreshing after the graph changes

Cytoscape keeps a copy and doesn't watch Neo4j. After new harvests or reader runs, re-run the export (and the flatten step), then import again as a new network, or with `--push`. Apply the saved `Chrystallum` style to the new network.

## Troubleshooting

| What you see | Why, and what to do |
|---|---|
| `KeyError: 'NEO4J_PASSWORD'` | The password isn't in this shell. Run step 0.2 again in the same window. |
| `ServiceUnavailable` / connection refused | Neo4j isn't running, or not on port 7687. Start the database in Neo4j Desktop. |
| Import error mentioning a column or a list | You imported `graph.cyjs` instead of `graph-desktop.cyjs`. Run step 2 and import the flat file. |
| The network is listed but the canvas is empty | No view was created, or everything sits at one point. Right-click the network › *Create View*, then run a layout and *View › Fit Content*. |
| Everything is one blob | Expected before a layout. Use Prefuse Force Directed, then select a node and *Select › Nodes › First Neighbors of Selected Nodes* to study one neighbourhood. |
| `py4cytoscape` cannot connect | Cytoscape must be open. Check *Help › Automation › CyREST API* opens; the port is 1234. |
| Octavian appears as "Augustus" | Known: Wikidata's label is stored (26 §7.4). |
| Two "Battle of Actium" nodes, two Fulvias | Real duplicates waiting in the identity queue. They aren't import errors. |

## Rules that still apply

- Read-only: nothing in these routes writes to Neo4j.
- Never print or commit the password; `Connections.txt` stays git-ignored.
- `GraphRevised/exports/` is git-ignored data; the scripts are what live in git.
- Never show an identifier alone. The `authorityLines` column already pairs each code with its label.
