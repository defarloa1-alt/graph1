---
status: complete
authority: migration validation record
depends_on: [02-GRAPH-MODEL.md, 03-TEMPORAL-YEAR-BACKBONE.md, 34-ENTITY-SUBTYPE-MIGRATION.cypher]
superseded_by: null
last_reviewed: 2026-10-19
---

# 35 — Entity subtype migration results

The clean-start graph was migrated from the transitional `Entity.kind`
discriminator to explicit Neo4j subtype labels on 2026-10-19.

## Result

Every `Entity` has exactly one approved subtype label in addition to `Entity`.
The `kind` property was removed from migrated nodes. No untyped `Entity` nodes
remain.

| Subtype | Count |
|---|---:|
| Person | 97 |
| Place | 25 |
| Event | 483 |
| Group | 19 |
| Work | 50 |
| Object | 0 |
| Period | 3 |
| Office | 19 |
| Concept | 3 |
| Polity | 3 |
| Type | 0 |
| Other | 0 |
| **Total Entity nodes** | **702** |

The Battle of Actium event also has `eventType: "battle"`.

## Preservation checks

| Measure | Result |
|---|---:|
| Total nodes | 516,873 |
| Total relationships | 519,146 |
| Year nodes | 4,025 |
| `FOLLOWED_BY` relationships | 4,024 |

These counts were unchanged by the migration. `Year` nodes remain separate
from `Entity:Period`, and the BCE/CE temporal backbone was not rewritten.

## Operational compatibility

The direct-operation contract still accepts the caller parameter named `kind`
as an in-memory subtype vocabulary for compatibility. It writes the
corresponding Neo4j label and never persists a `kind` property. Read APIs
derive the same compatibility value from the subtype labels.

## Permanent validation

The read-only invariant check is:

```text
python -m GraphRevised.validate_ontology
```

It verifies that every Entity has exactly one approved subtype, no Entity
retains a `kind` property, `Year` remains outside the Entity hierarchy, year
zero is absent, and the `FOLLOWED_BY` chain has one link per adjacent Year.
