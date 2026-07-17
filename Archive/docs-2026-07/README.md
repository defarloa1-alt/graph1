# Archived documentation (2026-07 cleanup)

**Do not use for current design** without verifying against:

- `docs/ARCHITECTURE_CURRENT.md`
- `docs/EPISTEMIC_MODEL.md`
- `docs/FACET_TRAINING_CONTRACT.md`
- `docs/README.md`

Live Neo4j Aura is authoritative for counts and schema state.

## Folders

| Folder | What |
|--------|------|
| `handoffs/` | Advisor and agent handoff snapshots |
| `sessions/` | Phase completion reports, military/diplomatic drafts, node cleanup, transcripts |
| `project-management/` | Roadmaps, SFA status snapshots, documentation completion notes |
| `architecture-discovery/` | Pre-baseline exploration; multi-agent / IGAR early notes (`multiagent_proposal.md`) |
| `agents/` | Superseded SFA prompt and quick-ref drafts |
| `setup/` | Duplicate Cursor MCP setup |
| `tasks/` | Phase cleanup specs |
| `security/` | Security audit reports (may embed credential strings — rotate if still live) |
| `misc/` | Stubs and one-offs |

## Root cleanup (2026-07-16 evening)

Session dumps and superseded guides were moved out of the repository root. Active docs live under `docs/`. Military source directories live under `scripts/agents/military/corpus/`. Root keepers: `README.md`, `REQUIREMENTS.md`, `DECISIONS.md`.

One-off Python/JSON/Cypher from the July 16 node cleanup live under `Archive/scripts-2026-07/node-cleanup/`. Root `mcp-config.json` (had embedded credentials) → `Archive/docs-2026-07/security/`; use `mcp/mcp-config.example.json` instead.
