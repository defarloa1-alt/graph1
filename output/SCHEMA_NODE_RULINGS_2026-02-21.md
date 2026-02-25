# Schema Node Rulings (2026-02-21)

**Architect rulings before D-029 relabeling.** Schema nodes have a separate migration path — they become SYS_PropertyDefinition under SYS_SchemaRegistry, not part of D-029.

---

## Rulings Summary

| Schema | Inferred type | Action |
|--------|---------------|--------|
| 1 | Year | Keep → SYS_PropertyDefinition (SchemaRegistry build) |
| 2 | Place | Keep → SYS_PropertyDefinition |
| 3 | Period | **Delete** — D-012 stale artifact (Period nodes deleted) |
| 4 | Human | Keep but **incomplete** — add status, populate required_props before migration |
| 5 | Unknown | **Delete** — duplicate Wikidata-only stub |
| 6 | Unknown | **Delete** — duplicate Wikidata-only stub |
| 7 | Subject | Keep → SYS_PropertyDefinition after Library Authority design |
| 8 | Bibliography | Keep but **update** WorldCat → LC_SRU |
| 9 | Empty stub | **Delete** |

---

## Schema 5/6 Investigation Result

**Query:** `MATCH (n:Schema) WHERE 'Wikidata' IN n.uses_federations AND size(n.uses_federations) = 1 RETURN elementId(n), keys(n), n`

**Result:** Two nodes with identical properties — only `uses_federations: ['Wikidata']`. No required_props, no optional_props, no other distinguishing properties. **Duplicates.** Delete both.

---

## Actions (run `scripts/neo4j/schema_node_actions_pre_d029.cypher`)

1. **Delete** Schema 3 (Period), Schema 9 (empty), Schema 5 and 6 (duplicates)
2. **Update** Schema 8: `uses_federations` from `[WorldCat, Wikidata]` to `[LC_SRU, Wikidata]`
3. **Flag** Schema 4: add `status: "incomplete — required_props missing"`, `system: true`
4. **Add** `system: true` to all remaining Schema nodes

**Do NOT relabel Schema in D-029.** Schema → SYS_PropertyDefinition is a SchemaRegistry build task.
