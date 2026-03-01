# Chrystallum Schema Subgraph — Spec

**Purpose:** Single canonical structure for the Chrystallum root and its branches (federations, subjects, facets, biblio, etc.). Resolves the "3 Chrystallum nodes" problem and defines the intended subgraph.

**Date:** 2026-02-27

---

## 1. The Three-Chrystallum Problem

Multiple scripts create Chrystallum nodes with **different match keys**, so MERGE creates separate nodes:

| Script | Match Key | Result |
|--------|-----------|--------|
| `create_federation.cypher` | `{id: 'CHRYSTALLUM_ROOT'}` | Node A |
| `create_authority_federations.cypher` | `{id: 'CHRYSTALLUM_ROOT'}` | Same as A |
| `create_facets_cluster.cypher` | `MATCH (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})` | Uses A |
| `rebuild_federation_registry.py` | `{name: "Chrystallum"}` | **Node B** (different!) |
| `build_complete_chrystallum_architecture.py` | `{name: 'Chrystallum Knowledge Graph'}` | **Node C** (different!) |

**Fix:** Use a single canonical identifier. All scripts should `MERGE (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})` and set `name`, `label` etc. via SET.

---

## 2. Canonical Chrystallum Root

```cypher
MERGE (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
SET c.label = 'Chrystallum',
    c.name = 'Chrystallum Knowledge Graph',
    c.type = 'knowledge_graph_root',
    c.version = '1.0',
    c.description = 'Root node of the Chrystallum federated knowledge graph'
```

**Constraint:** Exactly one Chrystallum node. Use `id: 'CHRYSTALLUM_ROOT'` as the unique key for all MERGE/MATCH.

---

## 3. Intended Subgraph Structure

```
(:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
  │
  ├─[:HAS_FACET_CLUSTER]──────►(:Facets:Category {id: 'FACETS_CATEGORY'})
  │                                └─[:IS_COMPOSED_OF]──►(:CanonicalFacet) × 18
  │
  ├─[:HAS_FEDERATION_CLUSTER]─►(:Federation:Category {id: 'FEDERATION_CATEGORY'})
  │                                └─[:IS_COMPOSED_OF]──►(:Federation:AuthoritySystem)  // LCSH, LCC, Wikidata, Pleiades, etc.
  │
  │   // OR (rebuild path): HAS_FEDERATION → SYS_FederationRegistry → SYS_FederationSource
  │
  ├─[:HAS_SUBJECT_CONCEPT_ROOT]►(:SubjectConceptRoot {id: 'subject_concept_root'})
  │                                ├─[:HAS_SUBJECT_REGISTRY]──►(:SubjectConceptRegistry)
  │                                │                                └─[:CONTAINS]──►(:SubjectConcept)
  │                                └─[:HAS_AGENT_REGISTRY]───►(:AgentRegistry)
  │                                                               └─[:HAS_AGENT]──►(:Agent)
  │
  ├─[:HAS_FEDERATION]──────────►(:SYS_FederationRegistry)   // Rebuild spec
  │                                └─[:CONTAINS]──►(:SYS_FederationSource)
  │
  ├─[:HAS_BIBLIOGRAPHY]────────►(:BibliographyRegistry)      // Planned
  │                                └─[:CONTAINS]──►(:BibliographySource)
  │
  ├─[:HAS_SELF_DESCRIPTION]────►(:SystemDescription)         // Generated narrative
  │
  └─[:HAS_SCHEMA]──────────────►(:SchemaRegistry)             // Planned (data dictionary)
```

---

## 4. Branch Summary

| Branch | Relationship | Target | Status | Script |
|--------|--------------|--------|--------|--------|
| **Facets** | HAS_FACET_CLUSTER | Facets:Category → CanonicalFacet | Active | create_facets_cluster.cypher |
| **Federations (authority)** | HAS_FEDERATION_CLUSTER | Federation:Category → Federation:AuthoritySystem | Active | create_authority_federations.cypher |
| **Federations (SYS)** | HAS_FEDERATION | SYS_FederationRegistry → SYS_FederationSource | Rebuild spec | rebuild_federation_registry.py |
| **Subjects** | HAS_SUBJECT_CONCEPT_ROOT | SubjectConceptRoot → Registry → SubjectConcept | Active | bootstrap_subject_concept_agents.cypher |
| **Bibliography** | HAS_BIBLIOGRAPHY | BibliographyRegistry → BibliographySource | Planned (3 nodes, 0 edges) | — |
| **Self-description** | HAS_SELF_DESCRIPTION | SystemDescription | Active | generate_system_description.py |
| **Schema** | HAS_SCHEMA | SchemaRegistry | Planned | — |

---

## 5. Naming Inconsistencies to Resolve

| Legacy / Alternate | Canonical (this spec) |
|--------------------|------------------------|
| HAS_FACET_ROOT | HAS_FACET_CLUSTER |
| HAS_SUBCLUSTER (federation) | HAS_FEDERATION_CLUSTER |
| FederationRoot → Federation | SYS_FederationRegistry → SYS_FederationSource (rebuild) |
| FacetRoot → Facet | Facets:Category → CanonicalFacet |

**Note:** `create_authority_federations.cypher` uses Federation:AuthoritySystem (LCSH, Wikidata, etc.). The rebuild spec uses SYS_FederationRegistry + SYS_FederationSource. These may be two views of the same thing — authority systems vs. operational federation sources. Decide: merge into one structure or keep both (registry = metadata, cluster = taxonomy).

---

## 6. Consolidation Script (Proposed)

To fix the three-node problem and ensure one root:

```cypher
// 1. Merge all Chrystallum nodes into one
MATCH (c:Chrystallum)
WITH c LIMIT 1
SET c.id = 'CHRYSTALLUM_ROOT',
    c.label = 'Chrystallum',
    c.name = 'Chrystallum Knowledge Graph'

// 2. Move all relationships from other Chrystallum nodes to the canonical one
MATCH (other:Chrystallum) WHERE other.id IS NULL OR other.id <> 'CHRYSTALLUM_ROOT'
MATCH (canon:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (other)-[r]->(target)
WHERE other <> canon
CREATE (canon)-[r2:DUMMY]->(target)
SET r2 = properties(r)
// ... (relationship type migration is manual; run per rel type)

// 3. Delete duplicate Chrystallum nodes
MATCH (dup:Chrystallum) WHERE dup.id IS NULL OR dup.id <> 'CHRYSTALLUM_ROOT'
DETACH DELETE dup
```

**Safer approach:** Run a one-time migration script that:
1. Identifies the "best" Chrystallum (e.g. the one with id: 'CHRYSTALLUM_ROOT' or the one with most relationships)
2. Reattaches any orphaned relationships from other Chrystallum nodes
3. Deletes the duplicates

---

## 7. Bibliography Backbone (Planned)

Currently 3 BibliographySource nodes exist with **zero edges**. Wire them:

```cypher
MERGE (br:BibliographyRegistry {id: 'BIBLIO_REGISTRY'})
MERGE (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MERGE (c)-[:HAS_BIBLIOGRAPHY]->(br)
MATCH (b:BibliographySource)
MERGE (br)-[:CONTAINS]->(b)
```

---

## 8. Phase 0 Federation Survey Nodes

The Phase 0 loaders (LCSH_Heading, Pleiades_Place, etc.) create **domain nodes**, not system nodes. They are **not** under the Chrystallum root. They connect to CanonicalFacet via MAPS_TO_FACET. The Chrystallum subgraph is the **meta/organizational** layer; domain data (Entity, Place, LCSH_Heading, etc.) lives alongside it.

---

## 9. Quick Reference: What Lives Where

| Under Chrystallum | Domain (separate) |
|-------------------|-------------------|
| Facets:Category, CanonicalFacet | LCSH_Heading, Pleiades_Place, etc. |
| Federation:Category, AuthoritySystem | Entity, Place, Period, Event |
| SubjectConceptRoot, Registry | SubjectConcept instances |
| SYS_FederationRegistry, SYS_FederationSource | — |
| SystemDescription | — |
| BibliographyRegistry | — |

---

## 10. Bootstrap Runbook

To create the full system subgraph in one run:

```bash
python scripts/neo4j/bootstrap_system_subgraph.py
```

**Order of operations:**
1. `create_authority_federations.cypher` — Chrystallum + HAS_FEDERATION_CLUSTER
2. `create_facets_cluster.cypher` — HAS_FACET_CLUSTER → 18 CanonicalFacet
3. `bridge_facet_root.cypher` — HAS_FACET_ROOT (for bootstrap compatibility)
4. `rebuild_federation_registry.py` — HAS_FEDERATION → SYS_FederationRegistry
5. `bootstrap_subject_concept_agents.cypher` — HAS_SUBJECT_CONCEPT_ROOT, agents
6. `wire_bibliography.cypher` — HAS_BIBLIOGRAPHY (if BibliographySource exists)

**Visualize the full subgraph:**
- Open `scripts/federation/view_full_system_subgraph.cypher` in Neo4j Browser
- Paste and run to see the complete system structure

**Options:**
- `--dry-run` — print steps only
- `--skip-subject` — skip subject concept bootstrap (faster)
- `--skip-biblio` — skip bibliography wiring

---

## 11. Next Steps

1. **Run consolidation** — merge 3 Chrystallum nodes into 1 with `id: 'CHRYSTALLUM_ROOT'`
2. **Wire BibliographySource** — `wire_bibliography.cypher` (in bootstrap)
3. **Generate self-description** — `python scripts/backbone/system/generate_system_description.py` for HAS_SELF_DESCRIPTION
