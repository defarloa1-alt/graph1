# Terminology — Chrystal 2 packs

**Locked 2026-07-19**

## SubjectDomain = the pack

When a new pack is requested, create one **`:SubjectDomain`**. That node **is** the domain.

| Term | Meaning |
|------|---------|
| **SubjectDomain** | The pack. Owns `start_year` / `end_year` (+ Year edges), WD reference JSON, federations (later), schema decisions, and inert SFA slots. |
| **domain_id** | Pack key on that node, e.g. `roman_republic`, later `meiji_japan` or `military_theory`. |
| **Domain agent** | Bootstraps the SubjectDomain **and** runs its lifecycle (not a Neo label). |
| **Schema specialist** | Decides which WD fields become **properties on the SubjectDomain** vs **first-class nodes + relationships**. |
| **Librarian** | Places the SubjectDomain in the biblio universe (LCSH/FAST/LCC/…). Aboutness is **multiplicitous** — not one physical shelf answer. |
| **Wikidata** | Federation **hub** (discovery), not authority. Values are candidates until validated / enriched at apply. |
| **SubjectConcept** | Granular scope node under a pack (graph structure — not a separate agent type; not a dumping ground for arbitrary WD items). |
| **SFASlot** | Inert facet agent seat under the SubjectDomain (`CONTAINS` → slot → `HAS_FACET`). |

## Agent types (minimal)

`DOMAIN`, `SCHEMA_SPECIALIST`, `LIBRARIAN`, `SFA`, `VALIDATION`.  

No `SCA` agent type for now — Domain owns lifecycle; SubjectConcepts stay granular nodes. Revisit if that proves too coarse.

## What we do **not** use

| Dropped | Why |
|---------|-----|
| Separate `:Domain` node | Duplicate of SubjectDomain; leftover from `ac63a8e5` `SEED_FOR` bridge. |
| `SEED_FOR` | Only existed to link SubjectDomain → Domain. |
| `:Period` + `OCCURS_DURING` for pack bounds | Dates live on the SubjectDomain (+ Year edges). |

## Dual grounding (later)

Pack facts vs discipline theory are **two SubjectDomains**, distinguished by `kind`:

- `kind: historical_pack` — e.g. `roman_republic`
- `kind: global_theory` — e.g. `military_theory` (created when needed)

Same label `:SubjectDomain`. No second Neo type named `Domain`.

See `DUAL_FACET_GLOBAL_DOMAIN.md` (updated to match).
