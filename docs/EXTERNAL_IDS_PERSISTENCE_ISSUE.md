# External IDs Persistence Issue

**Status:** Open — blocks efficient enrichment before Pleiades Phase 2  
**Date:** 2026-02-25

---

## Problem

Phase 1 federation scoping works: entities with P1696 (Trismegistos), P1838 (LGPN), P1584 (Pleiades), P6863 (DPRR) in Wikidata are correctly marked `temporal_scoped`. But the external IDs are **not persisted** on Entity nodes.

**Root cause:** `external_ids` were removed from `cluster_assignment` WRITE_QUERY due to Neo4j 5/Aura Map param rejection. The comment in code:

```python
# Note: external_ids omitted from write — Neo4j 5/Aura rejects Map param in this context.
```

**Consequences:**
- Every enrichment script (crosswalk, Pleiades Phase 2, etc.) must re-query Wikidata instead of reading from the graph
- Inefficient: 6,989 entities × N API calls per enrichment
- Will compound as Phase B and C federations run

---

## Current State

| Location | external_ids |
|----------|--------------|
| Harvest reports | ✅ Present in `accepted_entities[].external_ids` |
| member_of_edges.json | ✅ Present (from harvest) |
| Cypher file (generate_cypher) | ✅ Inline map literal in MERGE |
| Neo4j WRITE_QUERY (direct write) | ❌ Omitted |

The Cypher file uses `external_ids_to_cypher_map()` to embed the map as a **string literal** in the query (e.g. `{P1696: '12345'}`), not as a parameter. So the generated Cypher file would work if executed — the Map is not a param there.

---

## Workaround Options

### Option A: JSON string instead of Map

Store as `e.external_ids_json = $json_string` (JSON string). Query with `apoc.convert.fromJsonMap(e.external_ids_json)` when needed.

**Pros:** Single param, no Map type.  
**Cons:** Requires APOC for reads; schema change.

### Option B: Flatten to separate properties

`e.P1696`, `e.P1838`, `e.P1584`, etc. as top-level properties.

**Pros:** No Map; directly queryable.  
**Cons:** Schema grows with each PID; less flexible.

### Option C: Execute generated Cypher file

The generated `member_of_edges.cypher` already includes external_ids as inline literals. Run that file instead of WRITE_QUERY for the initial write.

**Pros:** No code change to cluster_assignment; uses existing Cypher.  
**Cons:** Two write paths (Cypher file vs direct); batch size/format may differ.

### Option D: Re-test Map param with current driver

The "Map param rejection" may be driver-version or context-specific. Try passing `{"P1696": "123"}` as a param again with the latest neo4j Python driver; document the exact error.

**Pros:** Might fix with no schema change.  
**Cons:** May have been tried; Aura may reject.

### Option E: Separate enrichment pass

Keep cluster_assignment as-is. Add a post-pass script that reads member_of_edges.json and writes external_ids to Entity nodes using Option A or B.

**Pros:** Decouples cluster_assignment from enrichment.  
**Cons:** Two write steps; still need to fix the write for Option A/B.

---

## Recommendation

Before Pleiades Phase 2:**
1. **Re-test** Option D — document exact Neo4j/Aura error when passing Map param.
2. If Map still rejected: **Option A** (JSON string) is the cleanest — one property, flexible, no schema explosion. Add a helper or APOC for reads.
3. **Option C** as fallback — run the generated Cypher file for cluster_assignment; it already has external_ids. That would persist them on first run.

---

## Next steps

- [ ] Dev: Re-test Map param with current driver; capture exact error
- [ ] Dev: If Map fails, implement Option A or C
- [ ] Architect: Confirm schema approach (JSON string vs separate props)
