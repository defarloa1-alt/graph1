# Librarian agent — Chrystal 2

**Status:** Active 2026-07-19  
**Neo role:** `SYS_AgentType` name `LIBRARIAN`  
**Primary federation:** `lcsh_fast_lcc` (`federations/lcsh_fast_lcc.json`)

## Job

Place a **SubjectDomain** (the pack) in the bibliographic universe via **aboutness**
authorities. First cut: resolve Domain identity-tether candidates that map to the
LCSH/FAST/LCC FederationCard and write registry-gated edges.

Does **not** invent history, Person identity helix (VIAF/LCNAF/ISNI), or Claims.

**Trap to avoid:** old physical-library “one call number = what this is.” In the
subject backbone something can always be **multiple** things — multiple LCSH,
FAST facets, and LCC correlations on the same Domain/SC. Soft means non-exclusive,
not second-class trash.

**Roman Republic example (same pack, two aboutnesses):**
- **Chronological / historical frame** — “Rome in the Republican era”
  (LCSH *Rome—History—Republic, 510-30 B.C.*, PeriodO variants, DG history slices).
- **Form of government** — republic as polity / institutional type
  (e.g. politics-and-government headings, JC form-of-state classes — not a second
  pack). Both may tether to `roman_republic`; do not force one winner.

## Pipeline position

```
Schema Specialist (proposal)
  → Domain apply (wd_* candidates + identity_federations)
    → Librarian place_domain (FederationCard tools → Neo tethers)
      → later: SC / SFA aboutness
```

Domain apply may store `wd_p244` (provisional WD candidate). Librarian **resolves**
that id against LoC and mints `:LCSH_Heading` + `HAS_LCSH_AUTHORITY`.

## Principles

1. Aboutness ≠ identity. `sh…` → LCSH subject; `n…` → LCNAF name (out of scope here).
2. Tools only — read FederationCard; do not hardcode LoC URLs in prompts.
3. Registry-gated writes: `LCSH_Heading` / `HAS_LCSH_AUTHORITY` must exist in SYS.
4. WD P244 is a candidate; LoC label wins at tether time.
5. No encyclopedia “tethers.” Card required.
6. SubjectDomain placement first; SubjectConcept aboutness later.

## Tools (thin)

| Tool | Returns |
|------|---------|
| `get_federation_card(source_id)` | Card JSON (data model + tool_names) |
| `loc_fetch_heading(lcsh_id)` | label, uri, broader/narrower (id.loc.gov) |
| `get_subject_domain(domain_id)` | Current Domain props + existing LCSH edges |
| `list_registry_aboutness()` | Allowed NodeType / RelType for biblio |

Write actions (CLI gated `--write`):

| Action | Neo |
|--------|-----|
| `merge_lcsh_heading` | `:LCSH_Heading {lcsh_id}` |
| `tether_domain_lcsh` | `(SubjectDomain)-[:HAS_LCSH_AUTHORITY]->(LCSH_Heading)` |
| `merge_fast_heading` | `:FAST_Heading {fast_id}` (soft facets OK) |
| `tether_domain_fast` | `(SubjectDomain)-[:HAS_FAST_AUTHORITY]->(FAST_Heading)` |
| `merge_lcc_class` / `align_domain_lcc` | `(SubjectDomain)-[:ALIGNED_WITH_LCC]->(LCC_Class)` soft |

## CLI

```powershell
python chrystal_2/agents/librarian/place_domain.py --domain-id roman_republic --dry-run
python chrystal_2/agents/librarian/place_domain.py --domain-id roman_republic --write
python chrystal_2/agents/librarian/place_domain.py --domain-id roman_republic --enrich-fast-lcc --dry-run
python chrystal_2/agents/librarian/place_domain.py --domain-id roman_republic --review-only
python chrystal_2/agents/librarian/place_domain.py --domain-id roman_republic --review-write
```

Chronological LCSH rarely has a 1:1 FAST id. Enrich proposes geographic umbrella (+ chrono facet from OCLC RDF). Bare topical middles (*History*) are filtered in code; **LLM enrich review** (`--review-only` / `--review-write`) is the judgment gate before write.

**Local crosswalk seeds (datastore-first):** `federations/crosswalks/` — project co-locations of LCSH/FAST/LCC (+QID). See that folder’s README. Not an official OCLC concordance.

**FAST for RR pack:** `fst01204885` (*Rome (Empire)*) is the correct umbrella id; chrono facet on the record is `Roman Republic--510-30 B.C.` (FAST facet-splits LCSH; there is no auth-label-only “Roman Republic” FAST).

## Out of scope (this pass)

- SubjectConcept suggest/reuse (legacy `scripts/agents/librarian` patterns)
- VIAF / OpenAlex
- Hard exclusive LCC shelf mark as if catalogued
