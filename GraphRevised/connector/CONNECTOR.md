# The Chrystallum connector (MCP)

**For:** the curator, asking Claude about the local graph from Claude Code or claude.ai.
**Status (2026-10-18):** built and checked against the live graph over stdio and local HTTP. The claude.ai route through a Cloudflare quick tunnel has not been tried from claude.ai yet. It replaces the legacy Railway connector (`scripts/mcp/chrystallum_mcp_server.py`, D-034), which read the Aura graph and offered general read-only Cypher.

The connector lets Claude look things up in the graph with a fixed set of tools. It only **reads**: every query runs in a read transaction on a read session. It has no tool that takes Cypher (05 §7). What it shows follows the explorer's contract (26): one fact per line, with its attestation in words and its voices. Proposed and accepted facts are shown together; rejected and superseded ones are left out.

| Tool | Gives |
|---|---|
| `find_entities` | Entities by name, short name, or Wikidata alias ("Octavian" finds Augustus), best first |
| `lookup_authority` | The entity holding an external code (Wikidata Q1048, LCNAF n50051933, ...) |
| `get_entity` | An entity's card: description, authority records, passages of note, its facts (paged) |
| `get_fact` | One fact in full: every voice, its quotations and locators, its review history |
| `event_overview` | One event: counts, phases, the Works that speak of it, what awaits review (as views/battle-overview.cypher) |
| `review_queue` | Proposals by who made them, their status, and what they propose |
| `graph_status` | Nodes per core label, claims and Proposals by status |

Neo4j must be running locally (Neo4j Desktop, `neo4j://127.0.0.1:7687`). The connector reads the password from `NEO4J_PASSWORD` or, failing that, from `GraphRevised/Connections.txt`. Nothing has to be loaded into the shell first.

## In Claude Code

`.mcp.json` at the repository root registers the connector as `chrystallum`. Claude Code starts it by itself (stdio). The first time, it asks whether to trust the project's MCP server: approve it. Then ask, for example, "What does the graph say about Agrippa at Actium?"

## In claude.ai

claude.ai runs in the cloud, so it reaches your PC through a tunnel. The connector stays on your machine. It works only while the command below is running.

1. **Once:** install the tunnel client, `winget install Cloudflare.cloudflared`. The access token is already in `Connections.txt` (line `mcp token is ...`). To replace it, delete that line and run `python -m GraphRevised.connector.server --new-token`.
2. **Each session**, from `C:\Projects\Graph1`:
   ```powershell
   python -m GraphRevised.connector.server --tunnel
   ```
   After a few seconds it prints `connector URL: https://<random>.trycloudflare.com/mcp/<token>`. Leave the window open.
3. In claude.ai: *Settings › Connectors › Chrystal MCP › Edit* (or *Add custom connector*). Paste the URL and leave the OAuth fields empty. A quick tunnel gets a new address each time, so repeat this step whenever you restart the command.

The token in the path is the only lock: claude.ai can't send a key to a custom connector. Any other path gets "not found", so treat the URL like a password. Don't paste it into a document or share it in a chat. If it leaks, make a new token (step 1).

For a URL that stays the same, use a named Cloudflare tunnel on your own domain, or ngrok's free static domain. Then run `--http --public-host <that host>` and set the connector once.

## Checks

- `python -m unittest GraphRevised.tests.test_connector` (offline): the search scoring, and that only the typed lookups are exposed.
- Against the live graph, `event_overview` gives the same sources and review queue as views/battle-overview.cypher queries 5 and 10 for every event (23 on 2026-10-18).

## Not yet

- Proposal submission through the validator (05 §7 allows it; read-only was chosen for the first version).
- Resources (the architecture docs, the predicate registry) and prompts (inquiry workflows).
- A read-only Neo4j user, so the database itself refuses writes from the connector. Today that rests on read sessions and having no write tool.
