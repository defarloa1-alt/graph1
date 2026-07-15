# Edge Labels: PID vs Human-Readable

## Current State (Post-Migration)

**All PID-typed edges have been migrated** to human-readable relationship types:
- P31 → INSTANCE_OF
- P1050 → MEDICAL_CONDITION
- P1343 → DESCRIBED_BY_SOURCE
- etc.

Bloom and Browser now show readable names (e.g. "MEDICAL_CONDITION") because the relationship type itself is human-readable.

## If You See PIDs Again (After New Imports)

New Wikidata imports may create edges with PID types (P31, P1050, etc.). To migrate them:

```bash
python scripts/migrations/migrate_pid_edges_to_readable_types.py --dry-run   # Preview
python scripts/migrations/migrate_pid_edges_to_readable_types.py              # Execute
```

Requires APOC. Uses registry for canonical types; derives from `r.label` for unmapped PIDs.

## Legacy: Bloom Caption Configuration

If you have PID edges and cannot run the migration, configure Bloom to show `r.label`:
1. Legend → click relationship type → Caption → select property `label`.
