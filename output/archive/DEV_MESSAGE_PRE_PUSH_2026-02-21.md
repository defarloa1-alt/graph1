# Dev Message — Pre-Push Go-Ahead (2026-02-21)

**From:** Architect  
**To:** Dev  
**Status:** Ready to execute

---

## Schema 5/6 — confirmed duplicates

Both have only `uses_federations: ['Wikidata']` and no other properties. **Delete both.**

---

## Full execution order — schema script

Run `scripts/neo4j/schema_node_actions_pre_d029.cypher`:

1. Delete Schema 3 (Period — D-012 stale)
2. Delete Schema 9 (empty stub)
3. Delete Schema 5 and Schema 6 (duplicate Wikidata-only stubs)
4. Update Schema 8: `uses_federations` → `['LC_SRU', 'Wikidata']`
5. Flag Schema 4: `status` → `"incomplete — required_props missing"`
6. Add `system: true` to Schema 1, 2, 4, 7, 8

**After script runs confirm:**
- How many Schema nodes remain (expect 5: Year, Place, Human-incomplete, Subject, Bibliography)
- No errors on any step

---

## Then

1. **Upload these five scripts to the chat** (for DMN extraction audit):
   - `scripts/agents/sca_agent.py`
   - `scripts/agents/subject_concept_facet_agents.py`
   - `scripts/backbone/subject/cluster_assignment.py`
   - `scripts/tools/wikidata_backlink_harvest.py`
   - `scripts/tools/claim_ingestion_pipeline.py`

2. **Push** with commit message:
   ```
   D-022 through D-029: external_ids fix, LGPN P1047, staging cleanup,
   Schema audit and cleanup, Policy/Threshold/PropertyMapping reclassification,
   Library Authority workstream, SysML block catalog v1.1
   ```

3. **Report commit hash** after push.

---

Script upload and push can happen in parallel — architect runs DMN extraction audit while dev pushes.
