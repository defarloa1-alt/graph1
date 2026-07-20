# Domain landing — inert SubjectDomain shell (Roman Republic)

**Instance:** Chrystal 2 (`7fe339d2`)  
**Pack library:** `JSON/wikidata/packs/Q17167_pack_library.json`  
**Contract:** `chrystal_2/harvest/PACK_LIBRARY_CONTRACT.md`  
**Schema agent:** `architecture/SCHEMA_SPECIALIST.md`  
**Terms:** `architecture/TERMINOLOGY.md`

## Agreed pipeline

1. **Harvest** — all seed properties + external IDs + forward links + accepted backlinks → pack library  
2. **Schema specialist** — Neo-grounded agent proposes property vs first-class; human review; then write  
3. **Shell** — SubjectDomain exists so the pack has an owner; slots inert  
4. **Librarian** — after schema places the pack (`agents/librarian/place_domain.py`)  

Landing script only creates the **shell** (identity, year bounds, slots, pointers). It does **not** replace the schema specialist. Hardcoded PID maps are **forbidden** (archived under `archive/2026-07-19_hardcoded_schema/`).

## What the shell lands

| Node | Key | Notes |
|------|-----|--------|
| `:SubjectDomain` | `domain_id: roman_republic` | `kind: historical_pack`; `start_year`/`end_year` + Year edges; `reference_json` → pack library |
| `:SFASlot` ×18 | `sfa_roman_republic_{facet}` | `status: inert` |

## Refresh shell

```powershell
python chrystal_2/harvest/build_pack_library.py --qid Q17167 --refresh-statements
python chrystal_2/bootstrap/land_domain_roman_republic.py
```

Schema proposals will come from the Schema Specialist agent (not yet implemented).

## Explicitly not in shell pass

- Applying schema proposal to Neo (first-class Places, Events, …)  
- Claims / Librarian tethers  
- Neighbor full-statement expansion  

## Smoke

```cypher
MATCH (sd:SubjectDomain {domain_id:'roman_republic'})
OPTIONAL MATCH (sd)-[:CONTAINS]->(s:SFASlot)
RETURN sd.reference_json, sd.start_year, sd.end_year, count(s) AS slots
```
