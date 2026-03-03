# ADR-008 OPS-001 Addendum

**When SYS_FederationSource.status = 'blocked' for DPRR**

The harvest agent (or any code that fetches DPRR data) must check `SYS_FederationSource.status` before any external query. When `status = 'blocked'`:

| Context packet field | Use graph-local read |
|----------------------|----------------------|
| `dprr_raw`           | Read from graph: Entity + POSITION_HELD + HAS_STATUS + relationships where `dprr_id IS NOT NULL`. No SPARQL call. |

**Implementation:** `dprr_import.py` already checks federation status and exits with guidance when blocked (unless `--force`). Future harvest agent code must implement the same pattern: `get_dprr_federation_status() == 'blocked'` → load `dprr_raw` from Neo4j, not from DPRR endpoint.
