# 2-13-26 Federation Impact

The "universe" of external links you unlock with a single Wikidata QID is massive, effectively turning Chrystallum into a universal translator for historical data.

By holding a QID, you do not just get a link to Wikipedia; you get a Rosetta Stone that maps your entity to over 11,000 external databases.

For History, Geography, and Classics, the practical potential universe is roughly 50 high-value targets.

The QID is the key. The Federated Authorities are the doors. The content lies in the rooms behind those doors.

## 1. Golden Tier (Backbone)

You are already using these. Wikidata acts as the automated resolver for backbone alignment.

| System | Wikidata Property | Why It Matters |
|---|---|---|
| LCSH | `P244` | Primary backbone and LoC authority anchor |
| FAST | `P2163` | Faceted subject access derived from LCSH |
| LCC | `P1149` | Library classification hierarchy (e.g., `DG231`) |
| Dewey | `P1036` | Agent routing and classification support |

## 2. Silver Tier (Domain-Specific High Value)

High leverage for Ancient History and Geography.

| System | Property | Domain | Value Proposition |
|---|---|---|---|
| Getty TGN | `P1667` | Geography | Historical place names and hierarchy |
| Pleiades | `P1584` | Classics | Definitive gazetteer for ancient places |
| Trismegistos | `P1958` | Classics | Master IDs for ancient texts/places |
| DARE | `P1936` | Geography | Digital Atlas of the Roman Empire coordinates |
| PeriodO | `P1927` | Time | Standardized historical period definitions |
| Nomisma | `P1928` | Numismatics | Coin and monetary history alignment |
| Perseus | `P4046` | Texts | Primary source text linking |

## 3. Bronze Tier (Global Authority)

Broad modern authority coverage.

| System | Property | Scope | Why It Matters |
|---|---|---|---|
| VIAF | `P214` | Global | Crosswalk across major national library authorities |
| WorldCat | `P7859` | Bibliographic | Bibliographic discovery and holdings |
| GND | `P227` | German | Key for classical scholarship and authority control |
| ISNI | `P213` | Global | ISO-standard identity link |

## 4. Strategic Implementation: Universal Translator

Do not only store `qid`. When ingestion resolves an entity to a QID, immediately run a federation query to fetch targeted P-codes and cache them locally.

### Super-node pattern (example)

```cypher
(:Person {
  label: "Julius Caesar",
  qid: "Q1048",

  // Cached federation keys for O(1) local lookup
  lcsh_id: "sh85018693",
  viaf_id: "286248284",
  pleiades_id: "392998632",
  getty_tgn_id: "500077373",
  trismegistos_id: "447"
})
```

## 5. SPARQL Pattern to Fetch the Universe

```sparql
SELECT ?lcsh ?fast ?lcc ?dewey ?viaf ?gnd ?isni ?worldcat ?tgn ?pleiades ?trismegistos ?periodo ?nomisma ?perseus WHERE {
  BIND(wd:Q1048 AS ?item) .

  OPTIONAL { ?item wdt:P244 ?lcsh . }          # LCSH
  OPTIONAL { ?item wdt:P2163 ?fast . }         # FAST
  OPTIONAL { ?item wdt:P1149 ?lcc . }          # LCC
  OPTIONAL { ?item wdt:P1036 ?dewey . }        # Dewey
  OPTIONAL { ?item wdt:P214 ?viaf . }          # VIAF
  OPTIONAL { ?item wdt:P227 ?gnd . }           # GND
  OPTIONAL { ?item wdt:P213 ?isni . }          # ISNI
  OPTIONAL { ?item wdt:P7859 ?worldcat . }     # WorldCat
  OPTIONAL { ?item wdt:P1667 ?tgn . }          # Getty TGN
  OPTIONAL { ?item wdt:P1584 ?pleiades . }     # Pleiades
  OPTIONAL { ?item wdt:P1958 ?trismegistos . } # Trismegistos
  OPTIONAL { ?item wdt:P1927 ?periodo . }      # PeriodO
  OPTIONAL { ?item wdt:P1928 ?nomisma . }      # Nomisma
  OPTIONAL { ?item wdt:P4046 ?perseus . }      # Perseus
}
```

## 6. Summary

The potential universe is interoperability.
By holding a QID, Chrystallum can bridge to Pleiades (ancient geography), Trismegistos (ancient texts), VIAF (global libraries), and many other authority systems.

## Appendix A: Data Model Contract (Recommended)

### Node-level fields

- `qid`: canonical Wikidata key
- `authority_links`: map of external IDs keyed by source (`lcsh`, `fast`, `lcc`, `dewey`, `viaf`, `gnd`, `isni`, `tgn`, `pleiades`, `trismegistos`, `periodo`, `nomisma`, `perseus`, `worldcat`)
- `federation_last_refreshed`: datetime

### Edge-level fields for imported assertions

- `source`: provider name (`wikidata`, `loc`, `pleiades`, etc.)
- `property`: source predicate/property (`P244`, `P1584`, etc.)
- `retrieved_at`: datetime
- `confidence`: numeric confidence or policy tier
- `resolution_rule`: policy used if conflicts were resolved

## Appendix B: Federation Graph Pattern

```cypher
(:Entity {qid})-[:ALIGNED_WITH {source, property, retrieved_at}]->(:ExternalAuthority {source, external_id})
(:ExternalAuthority)-[:RESOLVES_TO]->(:ExternalRecord {uri, label})
```

Recommended relation set:
- `ALIGNED_WITH`
- `SAME_AS`
- `DERIVED_FROM`
- `CONFLICTS_WITH`

## Appendix C: Ingestion Workflow (Minimal)

1. Resolve input entity to `qid`.
2. Run federation SPARQL for target property set.
3. Normalize IDs into `authority_links`.
4. Persist authority edges with provenance metadata.
5. Apply policy checks for conflicts and tier confidence.
6. Cache refresh timestamp and enqueue deep-provider pull where needed.
