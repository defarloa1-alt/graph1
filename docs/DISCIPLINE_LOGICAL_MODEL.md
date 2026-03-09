# Discipline Taxonomy — Logical Model

```
                                    ┌──────────────────────┐
                                    │    Facet (18)         │
                                    │──────────────────────│
                                    │ key: POLITICAL        │
                                    │ label: Political      │
                                    │ qid: Q1147507         │
                                    │ wikidata_label        │
                                    └──────────┬───────────┘
                                               │
                          HAS_PRIMARY_FACET (500)│  HAS_SECONDARY_FACET (195)
                          ─────────────────────┘│└──────────────────────────
                                               │
                              ┌─────────────────┴──────────────────┐
                              │   SYS_PropertyMapping (500)        │
                              │   SYS_FacetRouter (38+75)          │
                              │   CorpusWork (48)                  │
                              └────────────────────────────────────┘


    ┌─────────────────────────────────────────────────────────────────────────┐
    │                          Discipline (675)                               │
    │─────────────────────────────────────────────────────────────────────────│
    │ qid, label, lcsh_id, fast_id, lcc, ddc, subclass_of                    │
    │ getty_aat_id, openalex_id, gnd_id, bnf_id, mesh_id, ...                │
    │ source: wikidata_sparql                                                 │
    └───┬──────┬──────┬──────┬──────────────────┬─────────────────────────────┘
        │      │      │      │                  │
        │      │      │      │                  │
   ┌────┘  ┌───┘  ┌───┘  ┌───┘                 │
   │       │      │      │                     │
   │SUBCLASS_OF  HAS_    HAS_    FEDERATED_BY   │ ROUTES_TO
   │(805)  │LCSH  │LCC   │(1,289)              │ (3,082)
   │       │(619) │CLASS  │                     │
   │       │      │(120)  │                     │
   ▼       ▼      ▼      ▼                     ▼
┌──────┐ ┌─────┐ ┌─────┐ ┌───────────────────────────┐
│Disc. │ │LCSH_│ │LCC_ │ │  SYS_FederationSource (17) │
│(self)│ │Head.│ │Class│ │─────────────────────────────│
└──────┘ │(628)│ │(4490│ │ source_id: dprr             │
         └──┬──┘ └─────┘ │ label: DPRR                 │
            │             │ pid: Q17095051 (16/17 have) │
   BROADER_THAN           │ endpoint, phase, ...        │
      (464)               └─────────────────────────────┘
            │
            ▼
         ┌─────┐
         │LCSH_│
         │Head.│
         └─────┘


    ┌─────────────────────────────────────────────────────────────────┐
    │              External ID Nodes (from Discipline)                │
    │─────────────────────────────────────────────────────────────────│
    │                                                                 │
    │  HAS_FAST ──────────► FAST_Heading (249)                       │
    │  HAS_GETTY_AAT ─────► Getty_AAT_Concept (189)                  │
    │  HAS_OPENALEX ──────► OpenAlex_Concept (416)                   │
    │  HAS_GND ───────────► GND_Concept (407)                        │
    │  HAS_BNF ───────────► BnF_Concept (373)                       │
    │  HAS_MESH ──────────► MeSH_Descriptor (188)                    │
    │  HAS_BNCF ──────────► BNCF_Concept (343)                      │
    │  HAS_NDL ───────────► NDL_Concept (229)                        │
    │  HAS_UNESCO ────────► UNESCO_Concept (218)                     │
    │  HAS_BABELNET ──────► BabelNet_Concept (167)                   │
    │  HAS_OPENLIBRARY ───► OpenLibrary_Work (115)                   │
    │  HAS_PACTOLS ───────► PACTOLS_Concept (134)                    │
    │                                                                 │
    │  Total: 3,028 nodes · 3,033 relationships                      │
    │  Each node carries: uri (resolvable), source                    │
    └─────────────────────────────────────────────────────────────────┘
```

## Relationship Summary

| Relationship | From | To | Count | Meaning |
|---|---|---|---|---|
| SUBCLASS_OF | Discipline | Discipline | 805 | Wikidata P279 hierarchy |
| HAS_LCSH | Discipline | LCSH_Heading | 619 | LCSH authority link |
| HAS_LCC_CLASS | Discipline | LCC_Class | 120 | Library of Congress classification |
| BROADER_THAN | LCSH_Heading | LCSH_Heading | 464 | LOC SKOS hierarchy |
| FEDERATED_BY | Discipline | SYS_FederationSource | 1,289 | Has external ID in this source |
| ROUTES_TO | Discipline | SYS_FederationSource | 3,082 | Scope-relevant to this source |
| HAS_FAST | Discipline | FAST_Heading | 250 | Subject heading authority |
| HAS_GETTY_AAT | Discipline | Getty_AAT_Concept | 189 | Art & Architecture Thesaurus |
| HAS_OPENALEX | Discipline | OpenAlex_Concept | 416 | Scholarly works concept |
| HAS_GND | Discipline | GND_Concept | 407 | German National Library |
| HAS_BNF | Discipline | BnF_Concept | 375 | French National Library |
| HAS_MESH | Discipline | MeSH_Descriptor | 188 | Medical Subject Headings |
| HAS_BNCF | Discipline | BNCF_Concept | 343 | Italian National Library |
| HAS_NDL | Discipline | NDL_Concept | 229 | Japan National Library |
| HAS_UNESCO | Discipline | UNESCO_Concept | 218 | UNESCO thesaurus |
| HAS_BABELNET | Discipline | BabelNet_Concept | 169 | Multilingual synsets |
| HAS_OPENLIBRARY | Discipline | OpenLibrary_Work | 115 | Book/work data |
| HAS_PACTOLS | Discipline | PACTOLS_Concept | 134 | Archaeology thesaurus |

## Two Hierarchies on the Same Set

1. **Wikidata P279** — `(:Discipline)-[:SUBCLASS_OF]->(:Discipline)` — 805 edges
2. **LOC SKOS broader** — `(:LCSH_Heading)-[:BROADER_THAN]->(:LCSH_Heading)` — 464 edges

## Two Federation Link Types

1. **FEDERATED_BY** — "this discipline HAS an external ID in this source" (evidence-based)
2. **ROUTES_TO** — "this discipline's SCOPE overlaps this source" (seed + descendant propagation)

## Key Counts

- 675 Discipline nodes (from Wikidata Q11862829, filtered to authority-linked + connected)
- 18 Facet nodes (all have QIDs)
- 17 SYS_FederationSource nodes (16/17 have QIDs; CHRR missing)
- 628 LCSH_Heading nodes (615 discipline-linked + 13 prior domain headings)
- 3,028 External ID nodes across 12 types
- 4,490 LCC_Class nodes (pre-existing)
