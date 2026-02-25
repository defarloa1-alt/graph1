# FederationRegistry Rebuild — Spec for Dev

**Goal:** Replace the current 13 stale Federation nodes with an accurate operational list wired into the self-describing subgraph. This is a bounded, standalone task — no impact on domain data.

**Estimate:** 30–45 minutes dev time. No domain data touched. Safe to run alongside other work in any order.

**Label migration:** Step 1 deletes all `Federation` and `FederationRoot` nodes. The new structure uses `SYS_FederationSource` under `SYS_FederationRegistry`. Scripts that query `Federation` or `FederationRoot` must be updated before or after the rebuild. Known dependencies:
- `scripts/backbone/system/generate_system_description.py` — `MATCH (fr:FederationRoot)-[:HAS_FEDERATION]->(f:Federation)`
- `scripts/agents/sca_agent.py` — `OPTIONAL MATCH (fed_root)-[:HAS_FEDERATION]->(fed:Federation)`
- `output/neo4j/validate_changes.cypher` — validation queries

---

## Step 1 — Clear stale nodes

```cypher
MATCH (f:Federation) DETACH DELETE f
MATCH (fr:FederationRoot) DETACH DELETE fr
```

---

## Step 2 — Create registry root

```cypher
MERGE (sys:Chrystallum {name: "Chrystallum"})
CREATE (fr:SYS_FederationRegistry {system: true, label: "FederationRegistry"})
MERGE (sys)-[:HAS_FEDERATION]->(fr)
```

---

## Step 3 — Create federation nodes (one per source)

Create `SYS_FederationSource` nodes. Properties: `name`, `status`, `confidence`, `scoping_role`, `wikidata_property`, `license`, `access_pattern`, `phase1_complete`, `phase2_complete`, `system: true`

| Name | Status | Confidence | Scoping role | Wikidata property | License | Phase 1 | Phase 2 |
|------|--------|------------|-------------|-------------------|---------|---------|---------|
| Wikidata | operational | 0.90 | discovery_hub | — | CC0 | true | true |
| DPRR | operational | 0.85 | persons | P6863 | CC-BY | true | true |
| Pleiades | operational | 0.92 | places | P1584 | CC-BY | true | false |
| Trismegistos | operational | 0.95 | persons/inscriptions | P1696/P4230 | custom | true | false |
| LGPN | operational | 0.93 | persons | P1047 | custom | true | false |
| PeriodO | operational | 0.85 | temporal | — | CC0 | true | false |
| LCSH/FAST/LCC | operational | 0.90 | subject_classification | P244/P1014 | CC0 | true | true |
| CHRR | planned | — | material_evidence | — | ODbL | false | false |
| CRRO | planned | — | material_evidence | — | CC-BY | false | false |
| OCD | planned | — | taxonomy/grounding | P9106 | public_domain | false | false |
| EDH | planned | — | inscriptions | P2192 | CC-BY | false | false |
| VIAF | partial | 0.85 | persons | P214 | CC0 | false | false |
| Getty AAT | partial | 0.90 | concepts | P1014 | CC-BY | false | false |

Example CREATE:
```cypher
CREATE (f:SYS_FederationSource {
  name: "DPRR",
  status: "operational",
  confidence: 0.85,
  scoping_role: "persons",
  wikidata_property: "P6863",
  license: "CC-BY",
  access_pattern: "sparql",
  phase1_complete: true,
  phase2_complete: true,
  system: true
})
```

---

## Step 4 — Wire each node into registry

```cypher
MATCH (fr:SYS_FederationRegistry)
MATCH (f:SYS_FederationSource)
MERGE (fr)-[:CONTAINS]->(f)
```

---

## Step 5 — Add SCOPES edges

```cypher
// Example — DPRR scopes Entity (persons)
MATCH (f:SYS_FederationSource {name: "DPRR"})
MATCH (et:EntityType {label: "Person"})
MERGE (f)-[:SCOPES]->(et)
```

Repeat for each federation → entity type pair.

---

## Validation query after build

```cypher
MATCH (sys:Chrystallum)-[:HAS_FEDERATION]->(fr:SYS_FederationRegistry)-[:CONTAINS]->(f:SYS_FederationSource)
RETURN f.name, f.status, f.phase1_complete
ORDER BY f.status, f.name
```

Expected: 13 rows, status mix of operational/planned/partial.

---

---

## Rebuild Script

```bash
python scripts/neo4j/rebuild_federation_registry.py
```

Dry-run: `--dry-run`

---

*Spec executed 2026-02-25. Scripts updated first, rebuild complete, validation passed.*
