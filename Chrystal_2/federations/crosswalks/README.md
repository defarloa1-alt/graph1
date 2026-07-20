# Biblio crosswalk seeds (LCSH / FAST / LCC)

**Location:** `chrystal_2/federations/crosswalks/`  
**Purpose:** Local **datastore-first** authority candidates for Librarian / Domain
placement. Complements the FederationCard (`../lcsh_fast_lcc.json`), which is a
capability contract — **not** a row crosswalk.

## Hybrid rule (from archived Query Executor chat)

1. **Datastore first** — exact id + vetted label → authorities  
2. **API second** — LoC / OCLC suggest for gaps  
3. **Write-back** — promote reviewed API wins into this folder later  

Target map shapes:

```text
normalized_label -> {lcsh_ids[], fast_ids[], lcc_codes[], confidence, provenance}
qid              -> {authorities...}
```

## Files here

| File | What it is | Rows / size |
|------|------------|-------------|
| `periodo_roman_republic_seed.csv` | Tiny Domain PeriodO seed (5 Rome chrono variants; no bulk survey) |
| `roman_republic_sc_lcsh_fast_lcc.csv` | Production RR **SubjectConcept** props with co-located LCSH+FAST+LCC (+QID when present). Extracted from `CSV/neo4j_query_table_data_2026-2-20.csv`. | ~6 SCs |
| `roman_republic_domain_authority_candidates.csv` | Explicit dual candidates for pack `roman_republic` / Q17167 (WD `sh85115114` vs legacy SC `sh85115055`+`fst01204885`+`DG254`). | 2 |
| `qid_lcsh_fast_lcc_disciplines.csv` | Discipline QIDs with ≥2 of {LCSH,FAST,LCC} from `Disciplines/disciplines_with_authority.csv`. | ~hundreds |
| `cip_lcc_lcsh.csv` | CIP → LCC classes → LCSH terms (`Subjects/CIP/…`). No FAST. | ~58 |
| `lcc_fast_seed_mappings_legacy.json` | LCC letter/class → FAST seeds (`Facets/…`). No LCSH. | legacy |
| `roman_republic_fast_resolution_candidates.json` | Prior RR FAST suggestions (`output/subject_concepts/subject_concept_fast_resolution.json`). Verify labels — some headings may not match OCLC auth labels. | candidates |

## Important discrepancy (do not collapse silently)

| Source | LCSH | FAST | LCC |
|--------|------|------|-----|
| WD P244 / Chrystal_2 Domain tether | `sh85115114` | soft facets via OCLC | soft DG221–269 slices |
| Legacy production SC `subj_roman_republic_q17167` | `sh85115055` | `fst01204885` | `DG` / `DG254` |

Same display string *Rome--History--Republic, 510-30 B.C.* appears on both LCSH ids in older data. Treat as **candidates**, not identity.

## Roman Republic — two aboutnesses, one Domain

Same `roman_republic` SubjectDomain; **not** two packs:

| Strand | About | Typical authorities |
|--------|--------|---------------------|
| `chrono_historical_frame` | Republican era as time | LCSH History—Republic; FAST Rome(Empire)+chrono; PeriodO; DG slices |
| `form_of_government` | Republic as polity / institutions | Politics-and-government LCSH; JC / DG institutional classes |

See `roman_republic_domain_authority_candidates.csv`. Do not force one winner.

## FAST nuance — “Rome (Empire)” is not a bug


For the overall Roman Republic pack, the correct FAST **geographic/political umbrella** is:

- **`fst01204885` / id.worldcat.org/fast/1204885** — preferred label **“Rome (Empire)”**
- Authorized chronological string on that record: **`Roman Republic--510-30 B.C.`**

FAST does **not** mint a standalone preferred-label record “Roman Republic”. It facet-splits the LCSH string *Rome—History—Republic, 510-30 B.C.* into:

1. Geographic / political entity → Rome (Empire) (`1204885`)  
2. Chronological facet text → `Roman Republic--510-30 B.C.` (on that record / as subdivision use)

So Domain `HAS_FAST_AUTHORITY` to `fst01204885` with role soft geographic is **expected**. Pair it mentally (and later as edge props) with chrono facet `Republic, 510-30 B.C.` / `Roman Republic--510-30 B.C.`, not with a search for a FAST auth label literally “Roman Republic”.

A second OCLC suggest hit **History** (`fst00958235`) is a topical facet of the same LCSH decomposition — optional enrichment, not a rival pack identity.

## Rebuild

```powershell
python chrystal_2/agents/librarian/curate_crosswalks.py
```

## Not a three-way OCLC concordance

There is still **no** official LCSH↔FAST↔LCC universal table in-repo. These files are **project-vetted co-locations** and partial pairwise maps. Librarian should prefer them as first lookup, then API.
