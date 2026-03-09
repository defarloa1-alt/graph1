# Person — Logical Model

```
                                    ┌──────────────────────┐
                                    │    Facet (18)         │
                                    │──────────────────────│
                                    │ key: POLITICAL        │
                                    │ label, qid            │
                                    └──────────┬───────────┘
                                               │
                                    HAS_FACET (1,396)
                                               │
                              ┌────────────────┴───────────────┐
                              │   Discipline (675)              │
                              │   qid, label, lcsh_id           │
                              │   → 3,028 external ID nodes     │
                              │   → 3,082 ROUTES_TO federations │
                              └────────────────┬───────────────┘
                                               │
                                   FIELD_OF_WORK (128)
                                               │
┌──────────────────────────────────────────────┴──────────────────────────────────────┐
│                              Person (5,248)                                         │
│─────────────────────────────────────────────────────────────────────────────────────│
│ IDENTITY                                                                            │
│   qid              Wikidata QID (3,336 have)                                       │
│   entity_id        Internal ID                                                      │
│   entity_type      "person"                                                         │
│   entity_cipher    Deterministic hash                                               │
│   dprr_id          DPRR database ID (4,863 have)                                   │
│   dprr_uri         DPRR URI                                                         │
│                                                                                     │
│ NAMING                                                                              │
│   label            Primary display name                                             │
│   label_latin      Latin name form                                                  │
│   label_dprr       DPRR canonical name                                              │
│   label_sort       Sort key                                                         │
│                                                                                     │
│ TEMPORAL                                                                            │
│   birth_year       Year of birth (integer, BCE negative)                            │
│   death_year       Year of death                                                    │
│   floruit_start    Active period start                                              │
│   floruit_end      Active period end                                                │
│   floruit_derived  Whether floruit was computed                                     │
│                                                                                     │
│ DEATH                                                                               │
│   death_place_qid  QID of death location                                            │
│   cause_of_death_qid  QID of cause                                                 │
│                                                                                     │
│ PROVENANCE                                                                          │
│   dprr_imported    Import timestamp                                                 │
│   bio_harvested_at Bio harvest timestamp (2,947 have)                              │
└─────┬──────┬──────┬──────┬──────┬──────────────────────────────────────────────────┘
      │      │      │      │      │
      │      │      │      │      │
 ┌────┘  ┌───┘  ┌───┘  ┌───┘  ┌──┘
 │       │      │      │      │
 │       │      │      │      │
 ▼       ▼      ▼      ▼      ▼

ROMAN NAMING (graph nodes)          KINSHIP (graph edges)
─────────────────────────           ─────────────────────
HAS_PRAENOMEN → Praenomen (3,670)   FATHER_OF      (2,122)
HAS_NOMEN → Nomen (4,619)           MOTHER_OF        (589)
HAS_COGNOMEN → Cognomen (3,882)     CHILD_OF       (2,711)
MEMBER_OF_GENS → Gens (4,840)       SIBLING_OF     (2,158)
MEMBER_OF_TRIBE → Tribe (353)       SPOUSE_OF        (645)

TEMPORAL (graph edges)              POLITICAL/SOCIAL
──────────────────────              ────────────────
ACTIVE_IN_YEAR → Year (18,217)      POSITION_HELD → Position (7,342)
BORN_IN_YEAR → Year (1,746)         CITIZEN_OF → Entity (5,180)
BORN_IN_PLACE → Place (1,635)       HAS_STATUS → StatusType (1,919)
DIED_IN_YEAR → Year (1,483)         PARTICIPATED_IN → Event (273)
DIED_IN_PLACE → Place (313)         HAS_RELIGION → Entity (37)
BURIED_AT → Place (17)

LANGUAGE                            REFERENCE
────────                            ─────────
SPOKE_LANGUAGE → Entity (207)       DESCRIBED_BY_SOURCE → Entity (474)
NATIVE_LANGUAGE → Entity (48)       FIELD_OF_WORK → Discipline (128)
WRITING_LANGUAGE → Entity (46)      OCCUPATION_OF → Entity (111)


    ┌─────────────────────────────────────────────────────────────────┐
    │              External ID Nodes (from Person)                    │
    │─────────────────────────────────────────────────────────────────│
    │                                                                 │
    │  HAS_VIAF ─────────► VIAF_Cluster (843)           P214         │
    │  HAS_GND ──────────► GND_Person (699)             P227         │
    │  HAS_BM ───────────► BritishMuseum_Person (460)   P1711        │
    │  HAS_ISNI ─────────► ISNI_Record (467)            P213         │
    │  HAS_LCNAF ────────► LCNAF_Authority (395)        P244         │
    │  HAS_OCD ──────────► OCD_Entry (341)              P9106        │
    │  HAS_FAST ─────────► FAST_Heading (246)           P2163        │
    │  HAS_BNF ──────────► BnF_Authority (189)          P268         │
    │  HAS_OPENLIBRARY ──► OpenLibrary_Author (169)     P648         │
    │  HAS_TRISMEGISTOS ─► Trismegistos_Author (133)    P11252       │
    │  HAS_PERSEUS ──────► Perseus_Author (88)          P7041        │
    │  HAS_PACTOLS ──────► PACTOLS_Concept (70)         P4212        │
    │  HAS_FINDAGRAVE ───► FindAGrave_Memorial (48)     P535         │
    │  HAS_NDL ──────────► NDL_Authority (47)           P349         │
    │  HAS_ULAN ─────────► ULAN_Person (31)             P245         │
    │  HAS_LCC_CLASS ────► LCC_Class (6)                P1149        │
    │                                                                 │
    │  Total: 4,232 nodes · 4,232 ciphers                            │
    │  Each node carries: id, uri, cipher, pid, authority_qid         │
    │  Cipher format: QID:PID:value                                   │
    └─────────────────────────────────────────────────────────────────┘
```

## Relationship Summary

| Relationship | From | To | Count | Source |
|---|---|---|---|---|
| **Domain** |
| FIELD_OF_WORK | Person | Discipline | 128 | Wikidata P101/P106 |
| POSITION_HELD | Person | Position | 7,342 | DPRR |
| CITIZEN_OF | Person | Entity | 5,180 | Wikidata P27 |
| HAS_STATUS | Person | StatusType | 1,919 | DPRR |
| PARTICIPATED_IN | Person | Event | 273 | Wikidata P607 |
| OCCUPATION_OF | Person | Entity | 111 | Wikidata P106 |
| HAS_RELIGION | Person | Entity | 37 | Wikidata P140 |
| **Naming** |
| HAS_NOMEN | Person | Nomen | 4,619 | DPRR |
| MEMBER_OF_GENS | Person | Gens | 4,840 | DPRR |
| HAS_COGNOMEN | Person | Cognomen | 3,882 | DPRR |
| HAS_PRAENOMEN | Person | Praenomen | 3,670 | DPRR |
| MEMBER_OF_TRIBE | Person | Tribe | 353 | DPRR |
| **Kinship** |
| CHILD_OF | Person | Person | 2,711 | Wikidata/DPRR |
| SIBLING_OF | Person | Person | 2,158 | Wikidata/DPRR |
| FATHER_OF | Person | Person | 2,122 | Wikidata/DPRR |
| SPOUSE_OF | Person | Person | 645 | Wikidata/DPRR |
| MOTHER_OF | Person | Person | 589 | Wikidata/DPRR |
| **Temporal/Spatial** |
| ACTIVE_IN_YEAR | Person | Year | 18,217 | DPRR |
| BORN_IN_YEAR | Person | Year | 1,746 | Wikidata P569 |
| BORN_IN_PLACE | Person | Place | 1,635 | Wikidata P19 |
| DIED_IN_YEAR | Person | Year | 1,483 | Wikidata P570 |
| DIED_IN_PLACE | Person | Place | 313 | Wikidata P20 |
| BURIED_AT | Person | Place | 17 | Wikidata P119 |
| **Language** |
| SPOKE_LANGUAGE | Person | Entity | 207 | Wikidata P1412 |
| NATIVE_LANGUAGE | Person | Entity | 48 | Wikidata P103 |
| WRITING_LANGUAGE | Person | Entity | 46 | Wikidata P6886 |
| **Reference** |
| DESCRIBED_BY_SOURCE | Person | Entity | 474 | Wikidata P1343 |
| **External IDs** |
| HAS_VIAF | Person | VIAF_Cluster | 843 | Wikidata P214 |
| HAS_GND | Person | GND_Person | 699 | Wikidata P227 + property |
| HAS_ISNI | Person | ISNI_Record | 467 | Wikidata P213 |
| HAS_BM | Person | BritishMuseum_Person | 460 | Wikidata P1711 |
| HAS_LCNAF | Person | LCNAF_Authority | 395 | Wikidata P244 + property |
| HAS_OCD | Person | OCD_Entry | 341 | Wikidata P9106 |
| HAS_FAST | Person | FAST_Heading | 246 | Wikidata P2163 |
| HAS_BNF | Person | BnF_Authority | 189 | Wikidata P268 |
| HAS_OPENLIBRARY | Person | OpenLibrary_Author | 169 | Wikidata P648 |
| HAS_TRISMEGISTOS | Person | Trismegistos_Author | 133 | Wikidata P11252 |
| HAS_PERSEUS | Person | Perseus_Author | 88 | Wikidata P7041 |
| HAS_PACTOLS | Person | PACTOLS_Concept | 70 | Wikidata P4212 |
| HAS_FINDAGRAVE | Person | FindAGrave_Memorial | 48 | Wikidata P535 |
| HAS_NDL | Person | NDL_Authority | 47 | Wikidata P349 |
| HAS_ULAN | Person | ULAN_Person | 31 | Wikidata P245 |
| HAS_LCC_CLASS | Person | LCC_Class | 6 | Wikidata P1149 |

## Key Counts

- 5,248 Person nodes (3,336 with Wikidata QID, 4,863 with DPRR ID)
- 4,232 external ID nodes across 16 types (all with ciphers)
- 128 FIELD_OF_WORK links to 59 Disciplines
- 78 persons connected to Discipline → Facet chain

## Agent Traversal Path

```
Person (Q2263 Cicero)
  ├── FIELD_OF_WORK → Discipline (Q5891 philosophy)
  │     ├── HAS_FACET → Facet (INTELLECTUAL, weight 1.0)
  │     ├── HAS_FACET → Facet (SCIENTIFIC, weight 0.6)
  │     ├── HAS_GND → GND_Concept {cipher: Q5891:P227:4045791-6}
  │     ├── HAS_OPENALEX → OpenAlex_Concept {cipher: Q5891:P10283:C138885662}
  │     └── ... (12 more external ID types)
  ├── HAS_VIAF → VIAF_Cluster {cipher: Q2263:P214:27062070}
  ├── HAS_GND → GND_Person {cipher: Q2263:P227:118520814}
  ├── HAS_LCNAF → LCNAF_Authority {cipher: Q2263:P244:n79032166}
  ├── HAS_BM → BritishMuseum_Person {cipher: Q2263:P1711:58909}
  ├── POSITION_HELD → Position (consul, augur, ...)
  ├── MEMBER_OF_GENS → Gens (Tullia)
  └── ACTIVE_IN_YEAR → Year (-63, -62, ..., -43)
```
