# Archived one-off scripts (2026-07)

Point-in-time investigation and cleanup scripts moved out of the repository root.

## `node-cleanup/`

July 16 node-type cleanup / Event consolidation batch:

- `node_cleanup.py` — investigation + consolidation driver
- `fix_event_nodes.py`, `fix_event_qid.py`, `investigate_event_constraint.py`
- `verify_cleanup.py`, `test_entity_q17167.py`
- `node_cleanup_investigation.cypher`, `node_consolidation.cypher`
- `node_cleanup_investigation_report.json`

**Do not re-run against production without reading the companion session notes** in `Archive/docs-2026-07/sessions/NODE_CLEANUP_*`.

Canonical ongoing tools live under `scripts/system/` and `scripts/tools/`.
