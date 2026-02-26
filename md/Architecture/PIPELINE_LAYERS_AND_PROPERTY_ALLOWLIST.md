# Pipeline Layers and Property Allowlist Decision Framework

**Status:** Architectural decision (2026-02-24)  
**Resolves:** The allowlist debate — when to add properties, when to defer to downstream layers.

---

## Four-Layer Architecture

Clean separation of concerns. Each layer does exactly one job.

| Layer | Job | Breadth |
|-------|-----|---------|
| **Harvester** | Entity discovery via backlinks (and forward traversal when implemented) | Narrow — semantic entry points only |
| **Entity Store** | Persist full claims for every accepted entity | Broad — all properties including P373, P910, P1422 |
| **Edge Building** | Create relationships between entities in the store | Broad — uses full property set |
| **SFA** | Reason over the graph, find non-obvious paths | Full graph access |

---

## Key Distinction: Discovery vs. Representation

The property allowlist does **not** filter out relationships. It filters out **traversal entry points**.

- **Discovery** (harvester): "Which properties do we use to find new candidate entities to harvest?"
- **Representation** (entity store + edge building): "Once entities are in the store, which edges exist between them?"

The senator–mollusk connection is real and worth preserving. It does **not** need to be discovered via P373 at harvest time. It needs to be **represented** in the graph once both entities are in the store. If the senator is harvested via P39 (office held) and the mollusk via P138 (named after) or P921 (main subject), then the edge between them — whatever property it is — gets created when you traverse their respective property sets during enrichment.

---

## Decision Framework: "Should we add property X to the harvester?"

**The answer is always:**

> Does X discover entities that no current semantic property would find?

- **If yes** → Add it. (Example: an obscure figure only reachable via P373.)
- **If no** — the entity would get in anyway via a semantic property and you just want the edge → That's the entity store and edge-building layer's job. Do not add X to the harvester.

---

## When Breadth Enters the Pipeline

**Option A — Broad harvester:** Add P373, P910, P1422 to discovery mode. Cost: more garbage in the accepted set, slower runs, harder to audit.

**Option B — Tight harvester, broad enrichment (chosen):** Keep the current allowlist for entity discovery. During enrichment (entity store build), fetch *all* properties for every accepted entity. The senator–mollusk path exists in the graph without contaminating the harvest acceptance logic. Cross-entity edges (P373, etc.) get built in a separate pass over the store.

---

## The One Genuine Gap

Entities that are **only** reachable via P373 (or similar structural properties) and would never be pulled in by any semantic property. For the Roman Republic domain those are probably rare. Forward traversal (the Q2916317 / zero-backlinks case) closes most of that gap without opening the harvester's property gate to structural properties.

---

## SFA Territory

If the senator and the mollusk are both in the store — however they got there — the SFA can find the path between them when it needs to. That's precisely the kind of non-obvious relationship discovery an SFA with access to the full property set is built for.

The harvester doesn't need to anticipate every possible connection. It needs to not exclude entities that belong in the domain.

---

## Summary

- **Current property allowlist:** Fine for now.
- **Revisit when:** Post-SFA analysis shows specific entity classes systematically missing — that's the signal to add properties, not theoretical completeness.
- **More pressing gap:** Dead anchors (zero backlinks). Forward traversal closes most of them.
- **Everything else:** SFA territory.
