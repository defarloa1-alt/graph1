# 27 — The Gazetteer: a Geographic Backbone

**Date:** 2026-10-14. **Status:** agreed with the curator; built and loaded 2026-10-15 (§4a).
**Priority:** before the remaining next steps (curator, 2026-10-14: "backbone takes priority").
**Builds on:** [03](03-TEMPORAL-YEAR-BACKBONE.md) (the Year backbone, its model), the curator's vision note of 2026-10-14 (temporal, geographic, and subject backbones; not kept), [25](25-LIVES-AND-PLAYGROUND.md) §11 (enrichers by kind).

## 1. Decisions (curator, 2026-10-14)

1. **A gazetteer layer, like the Years**: preloaded, off the canvas, a ninth
   core label `Location`. Places stay Entities of kind Place, which link to
   their gazetteer entry; preloading places as Entities would flood the
   canvas, since every entity is shown (25 decision 2).
2. **Hierarchical, from the most granular to the regional to the
   continental.**
3. **Authorities in order:** Pleiades for the ancient world, then GeoNames
   for the modern tree. TGN is kept as crosswalk identifiers only (Claude's
   call, delegated): its hierarchy would repeat GeoNames'.
4. **All of it**: all of Pleiades, and the whole GeoNames administrative
   tree; other GeoNames features (13.5 million in all) are added on demand.
5. **The ancient tree stays as Pleiades has it**: patchy, several parents
   allowed, each link with its periods. Strictness comes from the modern
   tree.

## 2. The sources (checked 2026-10-14)

| | Pleiades | GeoNames |
|---|---|---|
| Licence | CC BY 3.0 (stated on each record) | CC BY 4.0 (dump readme) |
| Dump | `pleiades-places-latest.json.gz`, 135 MB | `allCountries.zip`, 422 MB; `hierarchy.zip`; `countryInfo.txt`; admin code lists |
| Size | 42,399 places; 34,814 with coordinates; 6,503 typed *unlocated* | 13,472,402 features; 544,012 administrative units and continents; 5,231,990 populated places |
| Hierarchy | 2,845 places with a parent: `part_of_physical` 1,149, `part_of_regional` 871, `part_of_admin` 729, `part_of_analytical` 592, `in_territory_of` 31 | strict, by admin codes: continent → country → ADM1 → … → ADM5 |
| Links out | GeoNames 1,454; Wikidata 11,428; TGN 391 | none to Pleiades |

Worked case: Roma (Pleiades 423025) is `part_of_regional` *Ager Romanus*
(which has no parent) and `part_of_admin` *Italia, Regio I*, which is in
both *Latium* and *Campania*; Roma names GeoNames 3169070 and TGN 7000874.

Both dumps live in `cache/geonames/` and `cache/pleiades/` (git-ignored, 25
§13), with their retrieval time, `Last-Modified`, and SHA-256 recorded in a
metadata file beside them, as the PeriodO cache does.

## 3. The model

```text
(:Location)-[:WITHIN {tree: "modern"}]->(:Location)        one parent, by admin codes
(:Location)-[:WITHIN {tree: "ancient", relation, periods}]->(:Location)   several allowed
(:Location)-[:MODERN_LOCATION {how, distanceKm}]->(:Location)              ancient to modern
(:Entity {kind: Place})-[:AT_LOCATION {status}]->(:Location)
```

- **Location**: `id` (`chr:location:geonames:<id>`, `chr:location:pleiades:<id>`),
  `label`, `system`, `identifier`, `kind` (continent, country, ADM1 … ADM5,
  or Pleiades' place types), `location` (a Neo4j point, with a point index:
  "what else was near here"), `names` (Pleiades' ancient names; the periods
  they are attested in kept as Pleiades' period keys), `dataset` (which
  dump). Unique on `id` and on `(system, identifier)`.
- **The modern tree**: continents (7), countries and dependencies (`PCL*`,
  `TERR`), and `ADM1` to `ADM5`: about 462,000 units. A unit's parent is
  the nearest higher level its admin codes name, so a skipped level does not
  break the chain; `hierarchy.txt` cross-checks. A country's continent comes
  from `countryInfo.txt` (one each: Egypt in Africa, Turkey in Asia).
  Historical divisions (`ADM1H` …) and divisions of no level (`ADMD`) are
  left out of the strict tree.
- **The ancient tree**: every Pleiades place is a Location; its
  `part_of_*` and `in_territory_of` connections become `WITHIN` links with
  the relation and Pleiades' periods. Period keys, not dates: they resolve to
  years through Pleiades' period vocabulary at read time, so no bare date is
  stored (handoff rule 18).
- **The bridge**, so every located ancient place reaches a continent:
  1. where Pleiades names a GeoNames feature (1,454), that feature is loaded
     and linked (`how: "pleiades reference"`);
  2. otherwise (about 33,000), the nearest GeoNames populated place, found in
     the dump outside the graph, gives the admin codes, and the place links
     to the most specific unit they name (`how: "nearest place"`, derived,
     with the distance). Beyond 50 km (curator, 2026-10-14; rules data)
     no link is made and the place is listed;
  3. unlocated places (about 7,600) get no modern link; their ancient
     parents may still place them.
- **Entities of kind Place** link to their Location by an identifier they
  already hold (their Pleiades or GeoNames crosswalk record, or a Wikidata QID
  that Pleiades names): `status: accepted`, as crosswalk links are. Any
  other match (name, coordinates) is proposed for the curator: identity stays
  the curator's ([19](19-SESSION-HANDOFF.md) rule 1).
- **Visibility**: Locations never appear on the canvas; a Place's card shows
  its chain ("Roma · Italia, Regio I · Latium | Rome · Lazio · Italy ·
  Europe") and its coordinates, quietly.
- **Writes**: through named operations, in batches (`UNWIND $rows`),
  retry-safe, dry run by default, like the migrations. The loader never
  creates an Entity.

## 4. What it enables

- The geographic enricher (25 §11): a surfaced Place gets coordinates,
  ancient names, and its chain without a model call.
- Hannibal's campaigns: the places of his route, ancient and modern.
- Synchronism by place (25 §3 L5): what happened in the same region in the
  same years, through `WITHIN` and the Year backbone together.

## 4a. As built (2026-10-15)

`python -m GraphRevised.gazetteer.load [--apply]` ([gazetteer/](gazetteer)): dry run
by default; rules in [curation/gazetteer.json](curation/gazetteer.json) (the 50 km
bridge, which GeoNames codes form the tree, which Pleiades relations are parents);
four batched operations (`upsert_locations`, `link_location_parents`,
`link_modern_locations`, `link_place_locations`); the schema in
[gazetteer/schema.cypher](gazetteer/schema.cypher) (both uniqueness constraints
and the point index `location_point`). Each run writes a report to `runs/`,
listing what was left out. Loaded from the dumps of 2026-10-14:

| | Count |
|---|---:|
| Locations | 505,546 |
| Modern units: 7 continents, 252 countries (countryInfo's), ADM1 3,865, ADM2 47,642, ADM3 170,131, ADM4 224,761, ADM5 15,042 | 461,700 |
| GeoNames features Pleiades names, not already units | 1,447 (1,503 found; 3 not in the dump; 9 with no unit to sit in) |
| Pleiades places | 42,399 |
| `WITHIN` modern / ancient | 463,131 / 3,363 (8 ancient parents not in the dump) |
| `MODERN_LOCATION`: by Pleiades' reference / nearest populated place | 1,509 / 33,164 |
| Unlocated (no modern link) / beyond 50 km of any populated place | 7,577 / 207 (seas, gulfs, deserts) |
| Place Entities linked (`AT_LOCATION`, accepted, by an identifier they hold) | 12 links, 11 entities (Rome by Pleiades and GeoNames) |

Checks: every unit has a parent; the code-derived parents agree with
`hierarchy.txt` everywhere; no two units share a code path; 179 ADM5 units with
no parent in `hierarchy.txt` are left out. Built differently from §3:
countries are countryInfo's rows (each names its geonameid and continent), not
every `PCL*` or `TERR` feature; a unit with an empty code above it (a skipped
level) is kept and takes the nearest level its codes name. Not matched:
Farsala and İzmir, whose Wikidata items Pleiades does not name (identity is
the curator's). A Place's chain: [views/place-chain.cypher](views/place-chain.cypher)
("Roma · Italia, Regio I · Latium | Roma · Città metropolitana di Roma Capitale ·
Lazio · Italian Republic · Europe"). Tests and snapshots that compare the whole
graph leave Locations out, as they leave out Years.

## 5. Open

- How the reader's proposed Places (step 3 of the handoff) are matched to
  Locations before an Entity is created.
- GeoNames alternate names (English labels for administrative units below
  country level) are not loaded at first.
