# Launching the UIs: a cheat sheet

Checked 2026-11-21. Every command runs from `C:\Projects\Graph1` (the repo root), against the local Neo4j only.

## Before any of them

1. **Neo4j is running:** start the database in Neo4j Desktop.
2. **The password is in the shell**, for the ones marked *needs password*:

   ```powershell
   # PowerShell
   $env:NEO4J_PASSWORD = python -c "from GraphRevised.connector.server import neo4j_password as p; print(p())"
   ```

   ```bash
   # Git Bash
   export NEO4J_PASSWORD=$(python -c 'from GraphRevised.connector.server import neo4j_password as p; print(p())' 2>/dev/null)
   ```

## At a glance

| UI | What it is for | Start it | Opens at |
| --- | --- | --- | --- |
| Review desk | Accept or reject claims, entity by entity | `python -m GraphRevised.review_desk.app --by "Your name"` | <http://127.0.0.1:7860> |
| Graph page (Cytoscape.js) | See the whole graph in a browser | `python -m GraphRevised.export.cytoscape`, then open the page | `GraphRevised\exports\graph.html` |
| Wireframe | The greyscale explorer screen, on live data | export first, then `python GraphRevised/explorer/wireframes/build.py` | `GraphRevised\exports\wireframe.html` |
| Cytoscape Desktop | Look and check, with tables and styles | export first, then `python GraphRevised/explorer/cytoscape_desktop.py --push` | Cytoscape 3.10.4 window |
| Explorer app | The React explorer, on a snapshot | `cd GraphRevised\explorer\app; npm run dev` | the URL it prints (Vite) |
| Storybook | The explorer's parts, one by one | `cd GraphRevised\explorer\app; npm run storybook` | <http://localhost:6006> |
| Connector, Claude Code | Ask Claude about the graph | starts by itself (`.mcp.json`) | the `chrystallum` tools |
| Connector, claude.ai | The same, from claude.ai | `python -m GraphRevised.connector.server --tunnel` | paste the printed URL into claude.ai |
| Neo4j Browser | Raw Cypher, for checking | Neo4j Desktop › Open, or the browser | <http://localhost:7474> |

## Each one

### Review desk *(needs password; writes)*

```powershell
python -m GraphRevised.review_desk.app --by "Your name"
python -m GraphRevised.review_desk.app --by "Your name" --entity chr:entity:<id>   # open on one entity
```

- Opens at <http://127.0.0.1:7860>. `--port` changes the port.
- Decisions are signed with the `--by` name. An accept or a reject rebuilds the fact lines in the same step.
- Stop it with Ctrl+C.

### Graph page in the browser *(needs password; read-only)*

```powershell
python -m GraphRevised.export.cytoscape            # writes exports\graph.cyjs and graph.html
start GraphRevised\exports\graph.html

# the audit view: also rejected and superseded claims, retired entities, dismissed notes
python -m GraphRevised.export.cytoscape --audit --out GraphRevised/exports/graph-audit
start GraphRevised\exports\graph-audit.html
```

- It's a snapshot: run the export again to see new changes.
- Always give `--audit` its own `--out`. Otherwise it overwrites `graph.cyjs`, and the views below would then show rejected claims too.
- The other three file views below read `graph.cyjs`, so export first.

### Wireframe *(no password; reads the export)*

```powershell
python GraphRevised/explorer/wireframes/build.py
start GraphRevised\exports\wireframe.html
```

### Cytoscape Desktop *(no password; reads the export)*

1. Open Cytoscape 3.10.4 from the Start menu, and wait for it to finish starting.
2. Run:

   ```powershell
   python GraphRevised/explorer/cytoscape_desktop.py --push   # loads and styles it (needs py4cytoscape)
   python GraphRevised/explorer/cytoscape_desktop.py          # only writes the files, to import by hand
   ```

- Without `--push`, import `GraphRevised\exports\graph-desktop.cyjs` with File › Import › Network from File.
- More in [CYTOSCAPE-DESKTOP.md](../explorer/CYTOSCAPE-DESKTOP.md).

### Explorer app and Storybook *(no password; read snapshots)*

```powershell
cd GraphRevised\explorer\app
npm install          # first time only
npm run dev          # the app: open the URL it prints
npm run storybook    # the parts: http://localhost:6006
```

- The app reads a snapshot file, not the graph. To make one (this step *needs password*), from the repo root:

  ```powershell
  python -m GraphRevised.discovery.event_subject_view GraphRevised\inquiries\actium-battle.json --section-id chr:subject:history-of-battle-of-actium-meaning-and-memory --output GraphRevised\explorer\snapshots\actium-view-<date>.json
  ```

- Then, in the app, use **Open view JSON** and choose that file. The command refuses to overwrite a file that exists, so give each new snapshot a new name.
- More in [explorer/app/README.md](../explorer/app/README.md).

### The connector, for Claude *(read-only)*

- **Claude Code:** nothing to start. `.mcp.json` launches it, and its tools appear as `chrystallum`.
- **claude.ai:**

  ```powershell
  python -m GraphRevised.connector.server --tunnel
  ```

  - It prints a connector URL that carries the token. Paste it into claude.ai's connector settings, and don't share it.
  - The tunnel gets a new address each time, so paste the new URL after every restart.
  - The first time only, run `--new-token` to make the token.
  - More in [CONNECTOR.md](../connector/CONNECTOR.md).

### Neo4j Browser *(raw access)*

Open it from Neo4j Desktop, or go to <http://localhost:7474>. Use it for reading and checking. Writes belong to the guarded operations, not hand-typed Cypher.

## If something won't start

| Symptom | Likely cause |
| --- | --- |
| `KeyError: 'NEO4J_PASSWORD'` | The password isn't in this shell: see "Before any of them" |
| `NotLocal: Refused …` | `NEO4J_URI` or `NEO4J_DATABASE` points somewhere other than the local graph |
| Connection refused on 7687 | Neo4j isn't running: start it in Neo4j Desktop |
| The page shows old data | The export or the snapshot is old: run it again |
| `--push` can't reach Cytoscape | Cytoscape isn't open yet, or `py4cytoscape` isn't installed (`pip install py4cytoscape`) |
