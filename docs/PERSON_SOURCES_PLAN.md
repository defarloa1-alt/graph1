# Person Sources Integration Plan

**Purpose:** Exploit multiple prosopographical and person-focused sources to populate and align Entity nodes in the Chrystallum knowledge graph.

**Status:** Draft  
**Created:** 2026-03-04

---

## 1. Source Inventory

| Source | Coverage | API / Data | Status | Use Case |
|--------|----------|------------|--------|----------|
| **DPRR** | Roman Republic | RDF/SPARQL | ✅ Integrated | Primary import; Group A/C split |
| **Wikidata P6863** | DPRR-aligned | SPARQL | ✅ Integrated | Alignment mapping |
| **Wikidata P27** | Roman Republic citizens | SPARQL | ✅ Integrated | Person harvest discovery |
| **Wikipedia lists** | Republic + Empire | Parse HTML + pageprops | 🔶 Partial (praetors only) | Deterministic matching |
| **PIR** | Augustus–Diocletian (elite) | RESTful JSON API | ⬜ Planned | ID-level integration |
| **PLRE** | 3rd–7th c. | Scanned PDFs | ❌ Not actionable | Monitor for future |
| **DPLRE** | Late Roman | LOD, no stable API | ❌ Not actionable | Monitor for future |
| **APR** | Foreign allies | Web only | ❌ Not actionable | Monitor for future |

---

## 2. Current Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PERSON INGEST FLOWS                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DPRR Import (dprr_import.py)                                           │
│  ├── Phase 0: Wikidata P6863 alignment → {dprr_id: qid}                  │
│  ├── Phase 1: Fetch persons from DPRR SPARQL                             │
│  └── Phase 2: Group A MERGE (qid) | Group C CREATE (dprr_uri only)      │
│                                                                         │
│  Person Harvest (orchestrator.py)                                        │
│  ├── Discovery: Wikidata P27=Q17167 OR graph (dprr_id/qid)               │
│  ├── Context packet → Agent → Executor                                   │
│  └── Creates/updates Entity with Wikidata properties                    │
│                                                                         │
│  DPRR Wikidata Matcher (dprr_wikidata_matcher.py)                       │
│  ├── Group C only (no qid)                                               │
│  ├── Wikidata search + Wikipedia praetors list → LLM proposal            │
│  └── Verification (P6863, dates, P31) → proposals JSON / --apply        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Phased Plan

### Phase 1: Expand Wikipedia Lists (Low Effort, High Leverage)

**Goal:** Add more office-holder lists to deterministic matching. Reuse `wikipedia_praetors_list.py` pattern.

**Source:** [Category:Lists of office-holders in ancient Rome](https://en.wikipedia.org/wiki/Category:Lists_of_office-holders_in_ancient_Rome)

| List | Office | DPRR Overlap | Priority |
|------|--------|--------------|----------|
| List of Roman praetors | Praetor | ✅ High | ✅ Done |
| List of Roman consuls | Consul | ✅ High | 1 |
| List of Roman quaestors | Quaestor | ✅ High | 2 |
| List of Roman tribunes | Tribune | ✅ High | 3 |
| List of censors of the Roman Republic | Censor | ✅ Medium | 4 |
| List of Roman dictators | Dictator | ✅ Low | 5 |
| List of Roman moneyers during the Republic | Moneyer | ✅ Low | 6 |

**Tasks:**
1. Generalize `wikipedia_praetors_list.py` → `wikipedia_office_lists.py` with configurable list URL + office type.
2. Add parsers for consuls, quaestors, tribunes (HTML structure may differ; inspect each).
3. Extend matcher to load multiple caches and select by office type.
4. Register each list as a lookup source in matcher (office → cache key).

**Output:** `output/dprr_wikidata_proposals/wikipedia_consuls_cache.json`, `wikipedia_quaestors_cache.json`, etc.

---

### Phase 2: PIR Integration (New Source)

**Goal:** Pull PIR persons (Augustus–Diocletian) for ID-level alignment. Extends coverage beyond Republic.

**Source:** PIR RESTful JSON API (Laravel/Vue app).

**Tasks:**
1. Discover PIR API base URL and endpoint structure (documentation / crawl).
2. Create `scripts/federation/pir_import.py`:
   - Fetch persons (paginated if needed).
   - Extract: canonical name, PIR ID, references, basic fields.
   - Map PIR ID → Wikidata QID (via PIR’s own links or search).
3. Create `Entity` nodes for PIR-only persons; MERGE for PIR+Wikidata.
4. Add `SYS_FederationSource` entry for PIR (status: operational when ready).
5. Store PIR ID on Entity (new property or via SNAP:DRGN-style identifier node).

**Output:** New Entity nodes; PIR ID as provenance.

**Dependency:** PIR API availability and rate limits.

---

### Phase 3: Unified Person Resolution Pipeline

**Goal:** Single pipeline that consults all sources in priority order for matching/creation.

**Flow:**
```
Entity candidate (label, office, year)
    │
    ├─► DPRR (if dprr_uri) ──────────────────► already in graph
    │
    ├─► Wikidata P6863 ──────────────────────► aligned qid
    │
    ├─► Wikipedia lists (by office + year) ──► deterministic match → qid
    │
    ├─► PIR (by name + period) ─────────────► PIR ID → resolve to qid
    │
    └─► Wikidata search + LLM ───────────────► proposal → verify
```

**Tasks:**
1. Refactor `dprr_wikidata_matcher.py` into a generic `person_resolver.py` that:
   - Accepts (label, offices, dates, source_hint).
   - Queries lookup sources in configurable order.
   - Returns best match + provenance.
2. Add `SYS_FederationSource` entries for Wikipedia lists (scoping_role: persons_lookup).
3. Person harvest and DPRR import both call resolver when creating/updating Entity.

---

### Phase 4: Monitor & Backlog

**Monitor for API/dump availability:**
- PLRE: structured data release
- DPLRE: stable public API
- APR: API or dump
- Digital Classicist [Greco-Roman Prosopographies](https://www.digitalclassicist.org/wiki/index.php?title=Greco-Roman_Prosopographies) page for updates

**Backlog:**
- SNAP:DRGN identifier consolidation (DPRR, PIR, PLRE URIs)
- VIAF integration for person disambiguation
- LGPN forward harvest (already in codebase) for onomastic alignment

---

## 4. SYS_FederationSource Additions

| Name | Status | Scoping Role | Wikidata Property | Notes |
|------|--------|--------------|-------------------|------|
| Wikipedia Office Lists | operational | persons_lookup | — | Consuls, praetors, quaestors, tribunes |
| PIR | planned → operational | persons | — | When Phase 2 complete |

---

## 5. Success Metrics

| Metric | Baseline | Target (Phase 1) | Target (Phase 2) |
|-------|----------|------------------|------------------|
| Group C match rate (50 sample) | ~5/50 verified | 15–20/50 | 20–25/50 |
| Deterministic matches (no LLM) | 1 | 5–10 | 10–15 |
| Entity coverage (Republic) | DPRR only | DPRR + Wikipedia | DPRR + Wikipedia |
| Entity coverage (Empire) | — | — | PIR persons added |

---

## 6. Dependencies & Risks

| Risk | Mitigation |
|------|------------|
| DPRR API blocked (OPS-001) | Use graph-local data only; snapshot fallback |
| Wikipedia list structure changes | Cache + periodic refresh; robust HTML parsing |
| PIR API undocumented | Reverse-engineer from web app; respect rate limits |
| P6863 mismatch blocks correct matches | Relax verification for Wikipedia-list provenance (DECISIONS.md) |

---

## 7. File Map

| File | Role |
|------|------|
| `scripts/federation/dprr_import.py` | DPRR primary import |
| `scripts/federation/dprr_wikidata_matcher.py` | Group C → Wikidata matching |
| `scripts/federation/wikipedia_praetors_list.py` | Praetors list (→ generalize) |
| `scripts/person_harvest/orchestrator.py` | Wikidata/graph discovery + harvest |
| `scripts/person_harvest/discovery.py` | Discovery sources |
| `scripts/neo4j/rebuild_federation_registry.py` | SYS_FederationSource population |

---

*Phase 1.1 complete (2026-03-04):*
- `wikipedia_office_lists.py` — generalized fetcher for praetors, consuls
- `wikipedia_praetors_list.py` — thin wrapper (backward compat)
- Matcher loads both caches; deterministic match for consuls + praetors

**Build caches:**
```bash
python scripts/federation/wikipedia_office_lists.py --list praetors --refresh
python scripts/federation/wikipedia_office_lists.py --list consuls --refresh
```
