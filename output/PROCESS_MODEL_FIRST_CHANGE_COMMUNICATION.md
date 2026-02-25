# Process: Model-First Change Communication

**Date:** 2026-02-25  
**Principle:** Every structural change to Chrystallum is recorded in the block catalog or DMN tables *before* a build spec goes to dev.

---

## The Sequence

```
1. Conversation → architectural decision reached
2. Architect updates BLOCK_CATALOG_RECONCILED.md or DMN_DECISION_TABLES.md
3. Build spec references catalog entries by block name and port name
4. Dev implements against the spec
5. Acceptance test verifies the implementation matches the catalog
6. Commit
```

**Step 2 happens before step 3.** Dev never receives a spec that references a block not yet in the catalog.

---

## What Belongs in the Block Catalog

Every block has four sections:

- **Identity** — block name, subsystem, decision that created it, current status.
- **Value properties** — attributes the block owns. These are data, not connections. If a value is in a SYS_Threshold node, the property references the threshold by name rather than hardcoding the value. Example: `confidence_threshold: Real [SYS_Threshold: claim_promotion_confidence]` not `confidence_threshold: 0.90`.
- **Ports** — interaction points on the block boundary. Each port has a name, direction (in/out), and flow type. The flow type is one of the named types in the port catalog. If a new flow type is needed, it is added to the port type catalog first.
- **Constraints** — rules that must hold. Business rules that cannot be expressed as a value property. Example: "No agent writes directly to Neo4j." These are the invariants the acceptance tests should verify.

---

## What Belongs in the DMN Tables

Any value that could change and whose change should not require a code deployment. The test: who should own this change? If the answer is architect or domain expert rather than developer, it belongs in a DMN table referencing a SYS_Threshold or SYS_Policy node.

**When a new threshold or policy is needed:**

```
1. Add SYS_Threshold or SYS_Policy node to Neo4j
   (script: scripts/neo4j/add_dmn_threshold_policy_nodes.cypher or a new one)
2. Add row to the relevant decision table in DMN_DECISION_TABLES.md
3. Update the block catalog — the block that reads this value gets a value property
   referencing the new threshold node by name
4. Refactor the script to read from graph instead of hardcoded value
5. Acceptance test: grep confirms no hardcoded value remains; Neo4j query confirms
   SYS_Threshold node exists with correct properties
```

---

## For Dev — Practical Implications

- **When you receive a build spec:** It will always reference blocks by their catalog name. If a block name appears in the spec that you cannot find in `sysml/BLOCK_CATALOG_RECONCILED.md`, that is a gap — flag it before building, don't invent the structure.
- **When you complete a build:** The acceptance test should always include one catalog check: does the implementation match the catalog entry for this block? Ports connected as specified, constraints honoured, value properties reading from the right source.
- **When you discover something in the graph or codebase that doesn't appear in the catalog** — as happened with PropertyMapping, Policy, Threshold, KnowledgeDomain nodes — report it before touching it. The catalog gap is architectural information, not a dev decision.

---

## How D-031 Demonstrated This

Before D-031, `ChrystallumMCPServer` did not exist in the block catalog. The right process would have been:

1. Add `ChrystallumMCPServer` to catalog under new `ToolingSubsystem`
2. Define its ports: `policy_query_in`, `threshold_query_in`, `response_out`
3. Define its value properties: `transport = "stdio"`, `version = "1.0"`, `write_permitted = false`
4. Define its constraint: "Read-only. No write operations. Neo4j credentials never exposed to clients."
5. Write the build spec referencing those catalog entries
6. Dev implements
7. Acceptance test verifies the constraint — grep for any write Cypher in the MCP server

We did this in the right spirit but the catalog update happened after the build. D-031 has been backfilled into the catalog. Going forward the catalog update happens first.
