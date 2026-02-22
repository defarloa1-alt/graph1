# Canonical 18-Facet Cluster Structure

## What This Creates

```
Chrystallum (Root)
    │
    │ [HAS_FACET_CLUSTER]
    ↓
Facets (Category: Canonical 18 Facets)
    │
    │ [IS_COMPOSED_OF] × 18
    ├─→ ARCHAEOLOGICAL
    ├─→ ARTISTIC
    ├─→ BIOGRAPHIC ⭐ (Added in ADR-004)
    ├─→ CULTURAL
    ├─→ DEMOGRAPHIC
    ├─→ DIPLOMATIC
    ├─→ ECONOMIC
    ├─→ ENVIRONMENTAL
    ├─→ GEOGRAPHIC
    ├─→ INTELLECTUAL
    ├─→ LINGUISTIC
    ├─→ MILITARY
    ├─→ POLITICAL
    ├─→ RELIGIOUS
    ├─→ SCIENTIFIC
    ├─→ SOCIAL
    ├─→ TECHNOLOGICAL
    └─→ COMMUNICATION ⭐ (Meta-facet)
```

## Node Structure

**Category Node:**
```cypher
(:Facets:Category {
    id: 'FACETS_CATEGORY',
    label: 'Canonical Facets',
    facet_count: 18,
    source_adr: 'ADR_004_Canonical_18_Facet_System'
})
```

**Each Facet:**
```cypher
(:ArchaeologicalFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_ARCHAEOLOGICAL',
    key: 'ARCHAEOLOGICAL',  // UPPERCASE canonical key
    label: 'Archaeological',
    description: '...'
})
```

## Relationships

- **Chrystallum → Facets:** `HAS_FACET_CLUSTER`
- **Facets → Each Facet:** `IS_COMPOSED_OF`

## Usage

Agents will classify entities using these canonical facets:

```cypher
// Entity classified by facets
MATCH (entity)-[:CLASSIFIED_AS]->(facet:CanonicalFacet)
RETURN entity.label, facet.key
```

## Source

Based on **ADR-004: Canonical 18-Facet System** from Key Files/Appendices/05_Architecture_Decisions/

## Import

Copy-paste: `scripts/federation/create_facets_cluster.cypher` into Neo4j Browser

