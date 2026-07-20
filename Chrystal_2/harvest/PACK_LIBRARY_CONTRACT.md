# Pack library harvest contract (Chrystal 2)

**Purpose:** One JSON library per pack seed. The **schema specialist** reads this — not raw Wikidata APIs — to decide SubjectDomain properties vs first-class nodes/relationships.

Wikidata is a **federation hub**, not an authority. Harvest captures candidates;
every extraction needs validation. Schema shapes the graph; Domain **apply** may
use, enrich, or replace WD values from stronger federations or human review.


**Rule:** Never emit PID or QID without a label.

## Pipeline

```
WD harvest (tools)
    → pack library JSON  (this contract)
    → schema specialist proposal
    → (review) writes onto SubjectDomain + first-class graph
```

Foundation (Years, Facets, SYS, Federation cards) must exist first. Librarian runs **after** schema places the SubjectDomain.

## Pack library shape

Path (Republic): `JSON/wikidata/packs/Q17167_pack_library.json`

| Section | Contents |
|---------|----------|
| `_meta` | `labeled`, rule, `generated_at`, `sources[]` |
| `seed` | `qid`, `label`, `description` |
| `statements` | Full labeled claims map (all properties, qualifiers, references) — same shape as `*_statements_full.json` |
| `external_ids[]` | Seed `datatype=external-id` values: `{pid, property_label, value}` |
| `forward_links[]` | Entities the seed points to: `{qid, label, via:[{pid, property_label}]}` |
| `backlinks[]` | Entities pointing at the seed (accepted harvest): `{qid, label, via_properties[], p31[], …}` |
| `counts` | statement/property/external/forward/backlink totals |

## What “ALL” means for v1

| Layer | Included |
|-------|----------|
| All seed properties | Yes — full statements tree |
| External links/IDs | Yes — every external-id snak on the seed |
| Forward links | Yes — every item-valued snak target (1 hop) |
| Backlinks | Yes — accepted backlink harvest (gated), not every noisy inbound |
| Neighbor full statements | **Not** in v1 pack file (too large); neighbors are index cards. Expand on demand via WD tools |

## Schema specialist

Input: pack library + live Neo registry + principles (`architecture/SCHEMA_SPECIALIST.md`).  
Output: `JSON/wikidata/packs/{qid}_schema_proposal.json` (agent-authored only).

Hardcoded propose scripts are archived under `chrystal_2/archive/`.

## Builders

```powershell
python chrystal_2/harvest/build_pack_library.py --qid Q17167
# Schema proposal: Schema Specialist agent (not the archived heuristic script)
```
