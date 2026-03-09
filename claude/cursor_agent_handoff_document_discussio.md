# Agent handoff document discussion
_Exported on 3/7/2026 at 06:44:39 EST from Cursor (2.6.13)_

---

**User**

true. i think we pull as much wiki geo data as possible as it gives us some options

---

**Cursor**

Here’s a concrete set of Wikidata geo properties to pull:

| Property | What it gives | Store as |
|----------|---------------|----------|
| **P625** | Point coordinates | `lat`, `long` (when missing) |
| **P3896** | Polygon/boundary (Commons GeoJSON) | `geoshape_url` or `geoshape_commons` (Commons path) |
| **P131** | Admin parent (region, country) | `LOCATED_IN` → parent Place by QID |
| **P17** | Country | `country_qid` or link to country Place |
| **P1566** | GeoNames ID | `geonames_id` (if not already set) |
| **P4036** | Pleiades ID | `pleiades_id` (if not already set) |

**SPARQL** can return all of these in one query per batch of QIDs.

**Storage**:
- `geoshape_commons`: Commons path like `Data:Italy/Rome.map` or full URL for map display
- P131/P17: `admin_parent_qid`, `country_qid` for hierarchy links, or create `Place` nodes for missing parents

**Impact**:
- P625 fills gaps when Pleiades/GeoNames coords are missing
- P3896 gives you polygon options for map display
- P131/P17 support admin hierarchy and “where is this place?”
- P1566/P4036 help cross-check existing crosswalk data

This can live in a single `wikidata_geo_enrichment.py` script that:
1. Fetches all Place nodes with QIDs
2. Runs SPARQL for labels + P625 + P3896 + P131 + P17
3. Updates `Place` nodes and creates `LOCATED_IN` edges where needed
4. Leaves `fix_bad_labels.py` focused on label fixes only

---

**User**

but i thought our harvestor had pulled all that

---

**Cursor**

Here’s what the harvesters actually do:

| Script | Pulls from Wikidata | Writes to Place |
|--------|----------------------|------------------|
| **link_place_admin_hierarchy.py** | P131, P17 | LOCATED_IN edges only; no coords, labels, or geoshape |
| **build_wikidata_period_geo_backbone.py** | P131, P17, P625 | Creates wikidata_place_backbone nodes with lat/long; used for Period cohort parents |
| **enrich_places_from_crosswalk.py** | — | qid, geonames_id, tgn_id from CSV only |

**Gaps:**

1. **Pleiades Places** (~40k) get `qid` from the crosswalk and P131/P17 via `link_place_admin_hierarchy`, but that script never fetches or writes P625 or P3896. Their coords come only from Pleiades.

2. **P3896 (geoshape)** is not pulled anywhere. The constitution notes “No P3896 geoshapes harvested.”

3. **P625** is only used in `build_wikidata_period_geo_backbone` for Period cohort places and their parents, not for the main Pleiades Place nodes.

So the harvesters do pull P131, P17, and P625, but only for a subset of places and only for hierarchy/backbone. The main Pleiades Place nodes are not enriched with Wikidata coords or geoshapes.

---

**User**

so yes pull add wikidata geo for place nodes

---

**Cursor**

Creating a script to enrich Place nodes with Wikidata geo data.


Fixing geoshape parsing and the update logic.


Done. Summary of what was added:

## `scripts/backbone/geographic/enrich_places_from_wikidata_geo.py`

**Behavior:**
- Loads all Place nodes with `qid` from Neo4j
- Calls the Wikidata API in batches (40 QIDs per request)
- Extracts:
  - **P625** → `lat`, `long` (only when Place has no coords)
  - **P3896** → `geoshape_commons` (Commons Data path for polygons)
  - **P131** → `LOCATED_IN` edges to parent Place nodes
  - **P17** → `country_qid`
  - **Labels** → fixes cases where `label = qid`

**Usage:**
```bash
# Dry run
python scripts/backbone/geographic/enrich_places_from_wikidata_geo.py --dry-run

# Full run
python scripts/backbone/geographic/enrich_places_from_wikidata_geo.py

# Limit for testing
python scripts/backbone/geographic/enrich_places_from_wikidata_geo.py --limit 500
```

**Place updates:**
- `lat`, `long` – only when missing
- `geoshape_commons` – Commons path (e.g. `Data:Italy.map`) for map polygons
- `country_qid` – from P17
- `coord_source` – set to `"Wikidata"` when coords are added
- `label`, `label_clean` – when `label` equals `qid`

**Graph updates:**
- Ensures parent Place nodes exist for P131 targets
- Creates `(Place)-[:LOCATED_IN {source:'wikidata', wikidata_pid:'P131'}]->(Place)` edges

`Geographic/README.md` has been updated to mention this script.

---

**User**

what about the temporal

---

**Cursor**

Checking how temporal qualifiers are handled and what the Place model expects:


Checking how Wikidata time qualifiers are parsed in the codebase:


Adding temporal qualifier parsing for P3896 (and P625 when present):


Done. The script now parses temporal qualifiers from Wikidata:

**Temporal qualifiers**

| Qualifier | Meaning | Stored as |
|-----------|---------|-----------|
| **P580** | Start time | `geoshape_start_year` / `coord_start_year` |
| **P582** | End time | `geoshape_end_year` / `coord_end_year` |
| **P585** | Point in time | Both start and end set to that year |

**Place properties**

- `geoshape_start_year`, `geoshape_end_year` – validity of the P3896 polygon
- `coord_start_year`, `coord_end_year` – validity of the P625 point (when present)

**Parsing**

- Uses the same logic as `build_wikidata_period_geo_backbone.py` for Wikidata time strings (e.g. `+0200-01-01T00:00:00Z` → 200 CE).

**Dry-run output**

- Counts how many geoshapes and coords have temporal qualifiers
- Sample output includes the temporal range when present

**Note:** Most P625 and many P3896 statements lack qualifiers. Temporal data will mainly appear for historical boundaries (e.g. Roman Empire at a given date). The script records it when available.

---

**User**

run the scripts

---

**Cursor**

The dry run is still in progress. It’s fetching 2,807 QIDs from the Wikidata API in batches of 40 (about 71 requests with 0.5s pauses), so it can take several minutes.

**Run it yourself:**

```powershell
# Dry run first
python scripts/backbone/geographic/enrich_places_from_wikidata_geo.py --dry-run

# Full run (after dry run looks good)
python scripts/backbone/geographic/enrich_places_from_wikidata_geo.py
```

**Faster test with a limit:**

```powershell
python scripts/backbone/geographic/enrich_places_from_wikidata_geo.py --dry-run --limit 100
```

The script needs Neo4j running and network access to the Wikidata API.

---

**User**

lets rethink this entirely this is a wikidata geo item https://www.wikidata.org/wiki/Q475802. look at all the properties and analzye how our system can use the props and external links

1:15 PM

Identified geographic item and planned data extraction approach
Identified geographic item and planned data extraction approach
Q475802 is Zaranj, a city in Afghanistan — not an ancient place. Let me pull the actual property data via SPARQL to do a proper analysis.


Investigated Wikidata properties and system integration possibilities
Investigated Wikidata properties and system integration possibilities
Can't fetch the Wikidata page directly. Can you paste the property list like you did for Pompey, or tell me if Zaranj is intentional (it's a modern Afghan city) — or did you mean a different QID?

In the meantime, based on what a typical Wikidata geo item carries, and against your federation sources, here's the analysis:

Properties Chrystallum can directly use:

PID	Label	How used
P31	instance of	Drives item_type_class in BacklinkRouting — settlement vs region vs archaeological site
P625	coordinate location	lat/long on Place node — already in your Pleiades schema
P1566	Pleiades ID	Primary crosswalk key — already harvested in resolve_place_pleiades()
P856	official website	Attach as URL property, not a node
P17	country	LOCATED_IN_COUNTRY edge to Polity node
P131	located in admin entity	Regional hierarchy — PART_OF edge chain
P18	image	Commons URL — surface in UI only
P571	inception	founded_year property on Place
P576	dissolved/abolished	dissolved_year — important for temporal scoping
P582	end time (on statements)	Qualifies period of control, occupation
P580	start time	Same
External IDs that cross into your federation sources:

PID	Authority	Federation source status
P1566	Pleiades	Operational — primary geo crosswalk
P1667	Getty TGN	Not in your federation list yet — high value
P244	LCNAF	Operational (LCSH/FAST/LCC)
P2163	FAST	Operational
P3293	BAVArt	Not relevant
P1584	Pleiades (place)	Same as P1566
P1700	Trismegistos geo	Trismegistos is operational — this is missing from your geo harvest
P7959	historical counties	Skip
The gap that matters most: Getty TGN

Your federation sources list Getty AAT as partial but Getty TGN (Thesaurus of Geographic Names) isn't listed separately. TGN is the geographic authority — it has hierarchical place relationships, preferred names across languages, and temporal coverage notes that Pleiades doesn't always have for non-classical sites. Wikidata property P1667 carries the TGN ID. That's worth adding to FORWARD_PROPS in a geo harvest script.

Trismegistos geo crosswalk

Trismegistos has its own geographic authority (distinct from its person authority P11252). The Wikidata property for Trismegistos places is P1700 (trismegistos geo). Since Trismegistos is your highest-weight operational federation source (0.95), this is a direct enrichment opportunity for Place nodes — same enrichment-first pattern as the onomastic nodes.

What this suggests for a geo harvest script

The pattern would mirror bio harvest: for each Place node with a QID, fetch Pleiades (already done inline), TGN ID, Trismegistos geo ID, coordinates if missing, inception/dissolution dates, and the admin hierarchy chain (P131 recursively up to country). The admin hierarchy is particularly useful — it lets you answer "all persons associated with places in Roman Italy" without relying purely on coordinates.

Is Q475802 (Zaranj) the item you meant, or is there a specific ancient place you had in mind?

Zaranj (Q475802)
* Item
* Discussion
* Read
* View history
Tools
* 
* 
* 
* 
* 
* 
* 
Appearance
hide
Text
* Small
Standard
Large
Width
* Standard
Wide
Color (beta)
* Automatic
Light
Dark
city in Afghanistan
* Zarang
In more languages
Configure
LanguageLabelDescriptionAlso known asdefault for all languages
No label defined
–
* 
English
Zaranj
city in Afghanistan
* Zarang
Spanish
Zaranj
ciudad de Afganistán
* 
Traditional Chinese
扎蘭季
No description defined
* 
Chinese
扎兰季
阿富汗城市
* 
All entered languages
Statements
instance of
city
0 references
border city
0 references
image
Zaranj in June 2011.jpg 3,000 × 2,100; 778 KB
1 reference
official name
زرنج (Pashto)
1 reference
native label
زرنج (Pashto)
1 reference
country
Afghanistan
1 reference
capital of
Saffarid dynasty
1 reference
Nimruz Province
1 reference
Saffarid State
0 references
located in the administrative territorial entity
Zaranj District
1 reference
located in time zone
UTC+04:30
1 reference
coordinate location

+−
1 km
Wikimedia maps | Map data © OpenStreetMap contributors

30°57'36"N, 61°51'36"E
1 reference
elevation above sea level
476 metre
1 reference
Commons category
Zaranj
1 reference
Identifiers
BBC Things ID
7a0048fd-8e22-4272-9d51-5029acbb04aa
1 reference
De Agostini ID
Zaranj
subject named as
Zaranj
0 references
Freebase ID
/m/03l18g
1 reference
GeoNames ID
1120985
1 reference
GNS Unique Feature ID
-3396598
0 references
museum-digital place ID
31167
0 references
National Historical Museums of Sweden ID
geo/159DE8C0-24EB-4436-8C0B-9DE3AFC7AC7D
0 references
OpenStreetMap node ID
312466967
0 references
SNARC ID
Q2347
0 references
TDV Encyclopedia of Islam ID
zerenc
1 reference
UN/LOCODE
AFZAJ
1 reference
Who's on First ID
1141906161
0 references
Kulturenvanteri taxonomy ID
1891

Show more
1:17 PM

Analyzing Zaranj's geospatial properties and structural applications
Analyzing Zaranj's geospatial properties and structural applications
Good. Now the analysis — and this item is actually more instructive than an ancient place would be precisely because it's modern.

What Zaranj has:

Property	Value	Chrystallum use
instance of	city, border city	place_type — already in your schema
coordinate location	30°57'N, 61°51'E	lat/long — already in schema
country (P17)	Afghanistan	LOCATED_IN_COUNTRY edge to Polity
capital of (P36↑)	Saffarid dynasty, Nimruz Province	CAPITAL_OF edge — encodes political significance; the Saffarid dynasty is a Political SFA item
located in admin entity (P131)	Zaranj District	PART_OF admin hierarchy chain
elevation (P2044)	476m	elevation property — useful for Geographic SFA
official name (P1448)	زرنج	label_native — already have native_name on Person, same pattern for Place
Commons category	Zaranj	UI link only
What Zaranj is missing — and what that tells you:

No P1566 (Pleiades), no P1667 (Getty TGN), no Trismegistos geo. This is the classifier signal for the bio harvest's broken stubs. When a place QID has none of these classical authority IDs, it's outside the ancient world corpus — it should not be written as a Place node at all. It should be flagged and routed differently.

This is exactly the PlaceResolution decision table you already have in the migration. The current implementation has a gap: it checks whether Pleiades resolved, but doesn't check whether the place is classifiable at all. The hash stubs (stub:da4f361feabf6be208ab16b9668811a7) you saw in the bio harvest are Wikidata QIDs that point to places like this — modern cities, medieval towns, non-Mediterranean locations that happen to appear as birth/death places for DPRR-linked persons' extended family.

External IDs — what's useful:

ID	Authority	Assessment
GeoNames ID (P1905 — not P1566)	GeoNames	High value. GeoNames is a universal gazetteer with 11M features. Not in your federation sources yet but natural complement to Pleiades for non-ancient places. Would resolve the stub problem for many items.
Who's on First ID	Geocode.earth	Hierarchical place relationships — useful for admin containment queries but low priority
OpenStreetMap node ID	OSM	Geometry data — useful for spatial analysis but heavy infrastructure
UN/LOCODE	UN	Trade/logistics code — not relevant to classical corpus
SNARC ID	Not classical SNAP — different SNARC	Not applicable
The practical impact on your bio harvest:

The three-tier resolution strategy for place QIDs should be:

Has P1566 (Pleiades) → write resolved Place node, link to existing Pleiades node
Has P1905 (GeoNames) but no Pleiades → write Place stub with geonames_id, flag outside_corpus: true, don't link to Pleiades
Has neither → the place is unresolvable in classical terms; write a minimal stub with QID and label only, resolved: false, outside_corpus: true
Right now your code conflates cases 2 and 3 and writes hashes as labels when the QID lookup fails. Adding GeoNames as a fallback check — just P1905 in resolve_place_pleiades() — would clean up most of those stubs and give you a proper authority ID even for non-ancient places.

Worth adding geonames_id to SYS_WikidataProperty (P1905) and to the Place node schema. One SPARQL call alongside P1566 in resolve_place_pleiades().

i rethink approach. forget harvesting details for a moment,  but we harvested wiki for roman republic. now lets say geo SFA starts out by saying for each backlink that has geo data get it in full. get the useful external links, then federate with geonames and pleiades as needed.  it may be that using the llm SFA to reason about what it needs is the right approach

1:21 PM

Reconsidered architecture delegating geographic resolution to specialized agent
Reconsidered architecture delegating geographic resolution to specialized agent
Good rethink. Let me check what's actually staged in the graph for Geographic SFA before designing anything.


Used Chrystal MCP integration
Used Chrystal MCP integration
Good picture. Here's the architecture as I see it:

The situation

6 geo candidates staged from Pompey's harvest — Aquae Sextiae, Bracara Augusta, Lucus Augusti, Emporiae, Porta Romana, Augusta Treverorum. All are real classical places. 42,065 Pleiades nodes already in the graph, 2,422 already crosswalked to Wikidata QIDs. So for most of these, the Pleiades node already exists — the SFA just needs to link the Entity stub to it.

The LLM-SFA approach you're describing

Rather than a rule-scripted harvester, the Geo SFA agent works like this:

Pull the queue — MATCH (e:Entity)-[r:BIO_CANDIDATE_REL]->(p:Person) WHERE r.sfa_queue = 'Geographic'
For each item, fetch the full Wikidata item — all properties, all external IDs
LLM reasons about what it has: Does this have P1566 (Pleiades)? P1667 (Getty TGN)? P1905 (GeoNames)? P131 admin containment chain? P571 inception? What's the relationship to the Person (FOUNDED vs NAMESAKE_OF vs COMMISSIONED)? Can it promote to a canonical edge?
Federate — look up existing Pleiades node by ID, look up GeoNames if needed, merge authorities
Write decisions — promote BIO_CANDIDATE_REL to canonical edge, enrich Place node, record confidence
Why LLM reasoning is right here

The rule-based approach breaks on heterogeneity. Aquae Sextiae (Aix-en-Provence) has Pleiades, TGN, GeoNames, multiple P31 types. Porta Romana is a city gate — it may not have Pleiades at all but has an OSM node. Augusta Treverorum (Trier) has Pleiades, TGN, and is the namesake not the city itself. Each item requires different federation paths and different canonical edge judgments. A decision table can't enumerate those combinations. The LLM can reason across them.

What the LLM needs as context per item:

The Wikidata item JSON (all properties + external IDs)
The relationship to the Person (edge_type, pred_pid, person label/dates)
What Pleiades nodes already exist in the graph (can query by Pleiades ID)
The PlaceResolution and BacklinkRouting policies from the graph
The canonical edge vocabulary
What it outputs:

Pleiades ID to link to (or null)
GeoNames ID to store (or null)
Canonical edge type to promote to
Confidence score
Any flags (outside_corpus, needs_review)
This is essentially the SFA agent as designed — it reads its own policies from the graph, reasons about a specific item, and writes a structured decision. The difference from the bio harvest is that here the LLM is doing the federation reasoning, not a hardcoded SPARQL path.

Want to sketch the agent prompt and I/O contract, or focus on fixing the bio harvest constraint issues first?

what is the bio harvest issue

1:23 PM

Synthesized session history to address bio harvest concern
Synthesized session history to address bio harvest concern
Two constraint violations that are still failing despite multiple fix attempts:

1. Place label constraint WRITE_BIO_ANCHORS creates a Place node but the constraint requires label to be present. The ON CREATE SET pl.label = coalesce(...) fix should work but the Place write is inside a large multi-statement Cypher block. If anything earlier in that block fails, the whole transaction rolls back silently — bio_harvested_at stays null, no Python exception is raised, and the script prints ✓ Written anyway. The latest version splits Place writes into a separate write_place() helper with its own session.run().consume() and try/except, but we haven't confirmed that version ran yet.

2. Entity entity_type constraint WRITE_BACKLINK_CANDIDATE merges an Entity stub. The constraint requires entity_type. The fix adds it to ON CREATE SET and derives it from item_type_label. But several of the failing QIDs (Q270384, Q518068, etc.) are pre-existing DPRR Entity+Person nodes — the MERGE matches them, ON CREATE SET never fires. The ON MATCH SET entity_type = coalesce(candidate.entity_type, $entity_type) fix handles that, but again needs confirmation it's running.

The underlying meta-issue is that we've been patching a downloaded file, re-presenting it, but you may be running a cached or previous version each time. The node IDs in the error messages have been changing each run (different numbers each time), which means the transactions are rolling back cleanly but new broken stub nodes are being created on each attempt — confirming the fixes aren't reaching the running script.

Quickest way to confirm: open the script locally and search for coalesce — if it's not there, you have an old version. Also search for write_place — the helper function should be there.



---

**Cursor**

Here’s what I’m taking from this:

## Rethink: Geo SFA as LLM-driven, not rule-based

**Current approach:** Scripts pull specific Wikidata props (P625, P3896, P131, P17) and apply fixed rules.

**Proposed approach:** Geo SFA agent:

1. **Queue:** `(Entity)-[:BIO_CANDIDATE_REL {sfa_queue:'Geographic'}]->(Person)`
2. **Fetch:** Full Wikidata item (all props, external IDs)
3. **Reason:** LLM decides:
   - P1566 (Pleiades)? P1667 (TGN)? P1905 (GeoNames)?
   - P131 admin chain, P571 inception, P576 dissolution
   - Relationship to Person (FOUNDED vs NAMESAKE_OF vs COMMISSIONED)
   - Whether to promote to a canonical edge
4. **Federate:** Resolve against Pleiades/GeoNames as needed
5. **Write:** Promote edge, enrich Place, set confidence, flags

**Why LLM:** Different items need different handling (Aquae Sextiae vs Porta Romana vs Augusta Treverorum). A single decision table can’t cover all combinations; the LLM can.

---

## Bio harvest constraints (still open)

1. **Place label:** `WRITE_BIO_ANCHORS` creates Place without `label` → constraint violation.
2. **Entity entity_type:** `WRITE_BACKLINK_CANDIDATE` MERGEs Entity; `ON CREATE` doesn’t run for existing nodes → `entity_type` missing.

---

## What to do next

Possible next steps:

1. **Fix bio harvest constraints** – Add `label` and `entity_type` handling so the script passes.
2. **Sketch Geo SFA agent** – Prompt, I/O contract, and how it uses PlaceResolution/BacklinkRouting.
3. **Document the rethink** – Capture the LLM-driven geo approach in `docs/` or `Geographic/`.
4. **Pause `enrich_places_from_wikidata_geo.py`** – Treat it as a stopgap until the Geo SFA agent exists.

Which of these do you want to prioritize?

---

**User**

1

---

**Cursor**

Applying both fixes:


Summary of changes:

## 1. Place label constraint (`place_has_label`)

**WRITE_BIO_ANCHORS** – added `ON MATCH SET` for birth, death, and burial places:

```cypher
ON MATCH SET pl.pleiades_id = coalesce(pl.pleiades_id, $birth_pleiades),
              pl.label = coalesce(pl.label, $birth_place_label, $birth_place_qid)
```

If a Place already exists (e.g. from DPRR) without a label, it is filled from the parameters.

## 2. Entity `entity_type` constraint (`entity_type_exists`)

**WRITE_BACKLINK_CANDIDATE** – added:
- `ON MATCH SET` for `entity_type` and `label`
- `entity_type` derived from `item_type_label` via `_entity_type_from_item_type()`
- `coalesce($item_label, $item_qid)` for `label` on create

**`_entity_type_from_item_type()`**:
- Place-like terms (place, settlement, city, region, historic place, archaeological) → `"Place"`
- Event-like terms (event, conflict, war, battle) → `"EVENT"`
- Otherwise → `"STUB"`

**Call sites updated**:
- `agent.py` – `harvest_person()` backlink loop
- `backlink_harvest.py` – `harvest_backlinks_for_person()`

Run the bio harvest again; the constraint violations should be gone.

---

**User**

which is bio harvest

---

**Cursor**

Bio harvest is split into two scripts:

## 1. Main bio harvest (forward props, places, marriages, events)

```powershell
python -m scripts.agents.biographic --dprr 1976
python -m scripts.agents.biographic --all
python -m scripts.agents.biographic --all --limit 25 --dry
```

Entry point: `scripts/agents/biographic/cli.py` (via `__main__.py`).

## 2. Backlink harvest (BIO_CANDIDATE_REL)

```powershell
python -m scripts.agents.biographic.backlink_harvest --from-graph --limit 25
python -m scripts.agents.biographic.backlink_harvest --from-graph --dry -v
```

Entry point: `scripts/agents/biographic/backlink_harvest.py`.

---

**Suggested order:** Run the main bio harvest first, then the backlink harvest. Both use the constraint fixes.

---

**User**

that is the job that takes 24 hiours

---

**Cursor**

Yes. The **backlink harvest** is the one that can run for many hours (up to ~24 hours) because it:

1. **Queries Wikidata SPARQL per person** – `fetch_backlinks(qid)` for each Person
2. **Processes many persons** – all with `bio_harvested_at IS NOT NULL`
3. **Uses rate limiting** – `SLEEP_SEC` between persons
4. **Can hit timeouts** – heavy entities (e.g. Pompey) trigger large SPARQL results

The **main bio harvest** (`--all`) is usually faster because it uses the Wikidata API for forward props instead of SPARQL.

**Ways to shorten backlink harvest time:**
- `--limit N` – process only N persons
- Run in batches (e.g. `--limit 100` several times, skipping already processed)
- Increase parallelism (would need code changes)
- Skip persons that already have backlinks (would need a filter in the script)

---

**User**

rethink. sfa has a geo backone - which is really just the Pleiades data, which should now be filtered to focus on settlmemts and region place types i believe, but check

---

**Cursor**

Documenting: Geo backbone = Pleiades Place nodes with `place_scope = 'v1_core'` (settlements and regions). Checking the v1_core filter and updating docs.


Adding documentation that the Geo backbone = Pleiades Place nodes with `place_scope = 'v1_core'`.


Summary of changes:

## Geo backbone = Pleiades Place with `place_scope = 'v1_core'`

**v1_core types** (from `tag_place_scope.py`):
- settlement, villa, fort, station, colony, region, province, camp, city, town, village

**deferred** (still in graph, not backbone):
- rivers, mountains, temples, roads, tombs, etc.

## Updates made

1. **Geographic/LOGICAL_MODEL.md** – Added a "Geo Backbone Definition" section.
2. **Geographic/README.md** – Documented `tag_place_scope.py` and the backbone definition.
3. **Key Files/chrystallum_geographic_constitution.jsx** – Added:
   - `GEO_BACKBONE` constant (definition, v1_core types, query, tagging script)
   - `place_scope` to Place optional props
   - Agent instruction: "Geo backbone = Place WHERE place_scope='v1_core'"

## Pipeline order

1. `import_pleiades_to_neo4j.py` – Creates all Place nodes
2. `tag_place_scope.py` – Sets `place_scope` (v1_core vs deferred)
3. `link_pleiades_place_to_geo_backbone.py` – Links Pleiades_Place → Place

The Geo SFA backbone is the subset of Place nodes with `place_scope = 'v1_core'`.

---

**User**

the next step is the federations to geonames and wiki. happy path it finds, unhappy path we discuss\

---

**Cursor**

Summary of what’s in place:

---

## Federation happy path

**`Geographic/FEDERATION_HAPPY_PATH.md`** documents:

1. **Prerequisites** — Place nodes, `place_scope`, crosswalk, GeoNames dump  
2. **Happy path (order)** — 6 steps with exact commands  
3. **One-liner** — Full pipeline as a single command  
4. **Unhappy path** — When things fail and what to do

---

## Pipeline order

| Step | Script | Effect |
|------|--------|--------|
| 1 | `enrich_places_from_crosswalk.py` | Sets `geonames_id`, `qid`, `tgn_id` |
| 2 | `link_place_admin_hierarchy_geonames.py` | GeoNames parents, `LOCATED_IN` |
| 3 | `link_place_admin_hierarchy.py` | Wikidata P131/P17 parents, `LOCATED_IN` |
| 4 | `enrich_places_from_wikidata_geo.py` | P625, P3896, coords, geoshape |
| 5 | `link_pleiades_place_to_geo_backbone.py` | `ALIGNED_WITH_GEO_BACKBONE` |

`run_place_enrichment_pipeline.sh` now runs all five steps in this order.

---

## Unhappy path (when to discuss)

| Failure | Likely cause |
|---------|--------------|
| Crosswalk missing | Run `build_pleiades_geonames_crosswalk.py` and `build_geonames_wikidata_bridge.py` |
| GeoNames hierarchy fails | `geonames_allCountries.zip` missing or wrong path |
| Wikidata API errors | Rate limits, network issues — retry with `--max-places` or `--limit` |
| Place has `qid` but no `geonames_id` | Crosswalk has Wikidata match but no GeoNames — expected for some places |
| Place has `geonames_id` but no `qid` | GeoNames only — `enrich_places_from_wikidata_geo` won’t run (needs `qid`) |

If you want to adjust the unhappy-path handling or add more cases, say which scenario to focus on.

---

**User**

if the agent was looking at just Pleiades, what reaonsing would it do

---

**Cursor**

Here’s what an agent would reason about if it only had Pleiades data:

---

## Agent reasoning with Pleiades only

### What Pleiades provides

- **Place identity** — `pleiades_id`, label, place_type
- **Temporal names** — `names[]` with start_date, end_date, language, romanized, attested
- **Temporal geometries** — `locations[]` with coordinates, GeoJSON, accuracy, date ranges
- **Place types** — settlement, region, fort, villa, etc.
- **Connections** — roads, rivers, “connects to” (not admin containment)

### What the agent would do

| Reasoning | Source | Action |
|----------|--------|--------|
| **Place identity** | P-01 | Treat Place as a stable identity across time; names and geometries are time-bounded variants |
| **Temporal name resolution** | GR-01 | “What was this place called in year X?” → filter `PlaceName` by `start_year` / `end_year` |
| **Temporal geometry resolution** | GR-02 | “Where was this place in year X?” → filter `PlaceGeometry` / `Location` by date range |
| **Place type scope** | GEO_BACKBONE | Use `place_type` to decide v1_core vs deferred; backbone = settlements, regions, villas, forts, etc. |
| **PlaceType normalization** | GR-03 | Split compound `place_type` strings (e.g. `"settlement, archaeological-site"`) into separate types |
| **Connections** | Pleiades `connections[]` | Create `CONNECTED_TO` edges for roads, rivers, etc. |

### What the agent would not do (no GeoNames/Wikidata)

| Reasoning | Needs | Without it |
|-----------|-------|------------|
| **Modern admin containment** | GeoNames | No “all ancient sites in modern Turkey” |
| **Admin hierarchy** | GeoNames / Wikidata P131 | No LOCATED_IN to country/region |
| **Geoshapes for regions** | Wikidata P3896 | No polygon boundaries for provinces/kingdoms |
| **Cross-authority links** | Wikidata qid, GeoNames ID | No links to other authorities |
| **Modern containment bridge** | GeoPlace | GR-04 (LOCATED_IN_MODERN) does not apply |

### Summary

With Pleiades only, the agent focuses on:

1. **Identity** — Place as a stable entity across time  
2. **Temporal resolution** — names and geometries for a given year  
3. **Place type and scope** — v1_core vs deferred  
4. **Connections** — roads, rivers, related places  

It does **not** reason about modern geography, admin hierarchy, or cross-authority links; those require GeoNames and Wikidata.

---

**User**

so now the agent sees where the place is, and could use reasoning to link it to our geographic backbone town - city - region - country etc right possible?

---

**Cursor**

Yes. After federation, the agent can use both coordinates and the admin hierarchy to reason about where a place sits in the backbone.

**What the agent can do**

1. **Follow the LOCATED_IN chain** — From a Place with `pleiades_id`, traverse `LOCATED_IN` upward to get town → city → region → country:
   ```cypher
   MATCH (p:Place {pleiades_id: $id})-[:LOCATED_IN*1..5]->(ancestor:Place)
   RETURN ancestor.label, ancestor.geonames_id, ancestor.qid
   ```

2. **Use coordinates** — With `lat`/`long` (or PlaceGeometry), the agent can reason about proximity, distance, and “nearby” places.

3. **Combine both** — Coordinates say *where* it is; the hierarchy says *how* it fits into town/city/region/country.

**How the backbone is built**

- **GeoNames:** Uses admin codes (admin1, admin2, admin3, admin4) and feature codes (PPL, ADM1, PCLI) to build the containment tree.
- **Wikidata:** Uses P131 (located in) and P17 (country) to build the same kind of chain.

So the agent can answer things like “this ancient site is in modern Ostia → Rome → Lazio → Italy” by:

- Following `LOCATED_IN` edges, and/or  
- Using coordinates plus feature codes to infer the level (town vs city vs region vs country).

The reasoning is: “Place X has coordinates and LOCATED_IN parents; I can traverse up to get the full modern admin path.”

---

**User**

but doesnt, couldnt any llm given a place say i know the hierarchy in the geo backbone

---

**Cursor**

Yes. An LLM can often infer “Ostia is in Italy, near Rome” from its training data without the graph.

The graph still matters because:

| LLM alone | Graph |
|-----------|--------|
| Can be wrong or inconsistent | Canonical, structured data |
| Can’t disambiguate (which Ostia?) | Tied to `pleiades_id`, `geonames_id`, `qid` |
| Can’t run queries (“all places in Latium”) | Supports traversal, filters, joins |
| Not wired into your system | Same Place nodes used by Person, Event, etc. |
| Can hallucinate hierarchy | Hierarchy comes from GeoNames/Wikidata, not the model |

So the LLM can *say* it knows the hierarchy, but the graph is what the system actually uses: for disambiguation, queries, and consistency. The graph is the source of truth; the LLM reasons over it rather than replacing it.

---

**User**

not understanging. with the agent being able to see the backbone why is that enough guardail for it to map

---

**Cursor**

Yes. The backbone is the guardrail because the agent’s mapping comes from the graph, not from its own knowledge.

**How it works**

1. The agent queries the graph (e.g. Cypher) instead of relying on what it “knows.”
2. It finds the Place by `pleiades_id` or label.
3. It follows `LOCATED_IN` to get the hierarchy.
4. Its answer is whatever the graph says.

So the guardrail is: **the agent is instructed to use the graph as the source of truth.** It doesn’t infer “Ostia is in Italy” from training; it runs a query and returns the backbone’s result.

If the graph has no hierarchy for a place, the agent can say “no hierarchy in the backbone” instead of guessing. That’s the guardrail: the graph is the boundary of what the agent can assert.

---

**User**

so after Summary
With Pleiades only, the agent focuses on:
Identity — Place as a stable entity across time
Temporal resolution — names and geometries for a given year
Place type and scope — v1_core vs deferred
Connections — roads, rivers, related places
It does not reason about modern geography, admin hierarchy, or cross-authority links; those require GeoNames and Wikidata. the agent goes thru each Pleiades row and can map to the backbone

---

**Cursor**

Right. After federation, the flow is:

1. **Pleiades only** — Agent can reason about identity, temporal resolution, place type, connections. No modern hierarchy.

2. **Federation** — Crosswalk + GeoNames + Wikidata add `geonames_id`, `qid`, and `LOCATED_IN` edges into the backbone.

3. **Agent mapping** — For each Pleiades Place, the agent queries the graph and follows `LOCATED_IN` to get town → city → region → country. The backbone is the source of truth.

So: **Pleiades row → agent queries graph → backbone hierarchy.** The agent maps by reading the graph, not by inferring from its own knowledge.

---

**User**

then agent gets all items from wikidata that have a Pleiades item in the external links as well as a geonames link. now the federation can be instantiated

---

**Cursor**

You’re describing a **Wikidata-first discovery path**:

1. **Agent queries Wikidata** for items with both:
   - **P4145** (Pleiades ID)
   - **P1566** (GeoNames ID)

2. **Result:** A set of triples (QID, pleiades_id, geonames_id) that can be used to build or extend the crosswalk.

3. **Federation instantiation:** Use those triples to:
   - Enrich Place nodes (set `qid`, `geonames_id`)
   - Create `LOCATED_IN` edges
   - Run the rest of the federation pipeline

So instead of (or in addition to) building the crosswalk from Pleiades+ → GeoNames → Wikidata, you can **derive it from Wikidata** by selecting items that already have both external IDs.

That gives you:
- A Wikidata-sourced crosswalk
- A way to discover new Pleiades–GeoNames links via Wikidata
- A path to federation that doesn’t depend on pleiades_plus or the GeoNames bridge scripts

---

**User**

maybe - i was saying starting with the Pleiades data store filtered map to backbones, temporal and geo. part 2 is query wiki for ALL items that contain pliedes or geo ids

---

**Cursor**

You’re describing a two-part flow:

**Part 1 — Pleiades → backbone**
- Start from the Pleiades data store
- Filter to backbone (place_scope = v1_core)
- Map each row to the backbone (temporal + geo) via the graph

**Part 2 — Wikidata discovery**
- Query Wikidata for all items that have Pleiades (P4145) or GeoNames (P1566) in their external identifiers
- That yields a broad set of entities (people, events, orgs, etc.) that reference places
- Use those to federate into the graph and link them to the backbone

So Part 1 is Pleiades-centric (filter → map to backbone). Part 2 is Wikidata-centric (find everything that points at our place IDs, then federate).

---

**User**

correct. when a place has pliades + geonames + wiki  + temporal and geographic backbone ties that creates a cipher i think for the place which has a high federation score

---

**Cursor**

Right. That combination acts as a strong **federation signature** for a Place:

| Dimension | What it adds |
|-----------|--------------|
| **Pleiades** | Ancient/classical identity |
| **GeoNames** | Modern admin hierarchy |
| **Wikidata** | Cross-authority bridge |
| **Temporal backbone** | Date-bounded names/geometries |
| **Geographic backbone** | LOCATED_IN → town → city → region → country |

When a Place has all of these, it’s well-anchored across authorities and time. That gives it a **high federation score** — a measure of how strongly it’s linked and how reliable it is for reasoning, disambiguation, and joining to other entities.

---

**User**

now what if it cant find a qid for a place. perhaps reasoning with confidence can find an approximation in wiki to get a qid

---

**Cursor**

An **approximation path** when there’s no direct qid:

**Agent reasoning with confidence**

1. **Label search** — Wikidata Search API by place name (e.g. "Ostia Antica").
2. **Coordinate proximity** — SPARQL for items with P625 within a radius of the Place’s lat/long.
3. **Hierarchy overlap** — If GeoNames parent is known, look for Wikidata items with P131/P17 in the same region.
4. **Combined signal** — Combine label match + coord distance + admin overlap into a confidence score.

**Output**

- Candidate qid(s) with confidence (e.g. 0.92).
- Evidence: label match, distance in km, parent region match.
- Threshold: e.g. auto-suggest above 0.9, flag for review below.

**Flow**

```
Place (pleiades_id, geonames_id, label, lat, long) — no qid
    → Agent queries Wikidata (search + SPARQL)
    → Returns candidate qid + confidence + evidence
    → High confidence: propose for crosswalk / auto-enrich
    → Low confidence: human review or leave unlinked
```

So the agent uses name, coordinates, and hierarchy to propose approximate matches instead of requiring an exact crosswalk hit.

---

**User**

so how does this change if it does the logical model

---

**Cursor**

With the **logical model** (Place → PlaceName, PlaceGeometry, LOCATED_IN), the approximation path changes like this:

---

**1. Richer evidence for matching**

| Current (flat) | Logical model |
|---------------|----------------|
| Single `label`, `lat`, `long` | Multiple PlaceNames (Byzantium, Constantinople, Istanbul) with `start_year`/`end_year` |
| One coordinate pair | Multiple PlaceGeometry with different coords and date ranges |

The agent can choose which name(s) and geometry to use for search (e.g. primary name, most recent geometry) instead of a single flat value.

---

**2. Temporal alignment**

- PlaceName/PlaceGeometry have `start_year`/`end_year`.
- Wikidata has temporal qualifiers (P580, P582, P585).
- Confidence can include temporal overlap: “PlaceGeometry 200 BCE–400 CE vs Wikidata P585 100 CE” → temporal agreement.

---

**3. Hierarchy as a constraint**

- `LOCATED_IN` gives parent Place(s), possibly with `qid`.
- Agent can constrain search: “Place X is LOCATED_IN → Rome (qid=Q220)” → search for items with P131 = Q220 and similar label.
- Uses the graph instead of only free-text search.

---

**4. Identity vs. temporal slice**

- Place = identity across time.
- Match target is the Place identity → one Wikidata item.
- PlaceName/PlaceGeometry are evidence for that match, not separate match targets.

---

**5. Confidence formula (logical model)**

```
confidence = f(
  label_match(PlaceName.name_string, wikidata_label),
  coord_proximity(PlaceGeometry.latitude/longitude, P625),
  temporal_overlap(PlaceName/PlaceGeometry date range, Wikidata qualifiers),
  hierarchy_match(LOCATED_IN parent.qid, Wikidata P131)
)
```

So the logical model adds temporal and structural evidence to the approximation path instead of relying only on a single label and coordinates.

---

**User**

great. so next step is agent reads all the properites of that qid and gathers all the properties it can. check what they are

---

**Cursor**

Here’s a consolidated list of Wikidata properties an agent can use when enriching a Place QID:

---

## Wikidata properties for Place enrichment

### Currently used (`enrich_places_from_wikidata_geo.py`)

| PID | Name | Purpose |
|-----|------|---------|
| **P625** | coordinate location | lat/long (with P580/P582/P585 qualifiers for temporal) |
| **P3896** | geoshape | Commons Data polygon path |
| **P131** | located in administrative territorial entity | Admin parent(s) |
| **P17** | country | Country QID |
| **labels** | — | Multilingual display names |

---

### Additional geographic properties (from `analyze_geographic_properties.py` and codebase)

| PID | Name | Purpose |
|-----|------|---------|
| **P30** | continent | Continent QID |
| **P36** | capital | Capital of (for countries/regions) |
| **P276** | location | Physical location (building, monument) |
| **P706** | located in/on physical feature | Mountain, river, island |
| **P47** | shares border with | Neighboring entities |
| **P1376** | capital of | This place is capital of X |
| **P421** | located in timezone | Timezone QID |
| **P150** | contains administrative territorial entity | Child admin units |

---

### External identifiers (cross-authority links)

| PID | Name | Purpose |
|-----|------|---------|
| **P1566** | GeoNames ID | GeoNames identifier |
| **P1584** | Pleiades ID | Pleiades identifier |
| **P1667** | Getty TGN ID | Getty Thesaurus of Geographic Names |
| **P214** | VIAF ID | VIAF |
| **P227** | GND ID | German National Library |
| **P244** | LCNAF ID | Library of Congress |
| **P268** | BnF ID | French National Library |
| **P950** | BNE ID | Spanish National Library |
| **P2427** | GRID ID | Global Research Identifier |
| **P402** | OpenStreetMap ID | OSM way/node ID |

---

### Classification and type

| PID | Name | Purpose |
|-----|------|---------|
| **P31** | instance of | Type (city, archaeological site, etc.) |
| **P279** | subclass of | Type hierarchy |
| **P361** | part of | Part of larger entity |

---

### Temporal qualifiers (used with P625, P3896, etc.)

| PID | Name | Purpose |
|-----|------|---------|
| **P580** | start time | When claim becomes valid |
| **P582** | end time | When claim ceases to be valid |
| **P585** | point in time | Single point in time |

---

### Other useful properties

| PID | Name | Purpose |
|-----|------|---------|
| **descriptions** | — | Short descriptions by language |
| **aliases** | — | Alternative names |
| **sitelinks** | — | Wikipedia article links |

---

## Agent workflow: gather all properties

1. **Fetch full entity** — `wbgetentities` with `props=labels|descriptions|aliases|claims|sitelinks`.
2. **Parse claims** — For each PID above, extract values and qualifiers (P580, P582, P585).
3. **Map to Place** — Store as Place properties, PlaceName/PlaceGeometry, or LOCATED_IN edges.
4. **External IDs** — Use P1566, P1584, P1667, etc. for federation and cross-checks.

`wikidata_full_fetch.py` already fetches the full entity; the next step is to extend it (or add a new script) to parse and map these place-specific properties into the graph.

---

**User**

geoshape is key and couild be time spanned as well

---

**Cursor**

Geoshape (P3896) is central for rendering regions and territories, and it can be time-bounded.

**Temporal qualifiers on P3896**

- **P580** (start time) — when the boundary becomes valid  
- **P582** (end time) — when it ceases to be valid  
- **P585** (point in time) — single point in time

`enrich_places_from_wikidata_geo.py` already parses these and stores `geoshape_start_year` and `geoshape_end_year` next to `geoshape_commons`.

**Why this matters**

- A place can have multiple geoshapes for different periods (e.g. Roman province vs Byzantine).
- Time-slider maps can show the correct boundary for a given year.
- This matches the logical model: PlaceGeometry with `start_year` / `end_year`.

**Logical-model alignment**

If PlaceGeometry is used for geoshapes, each P3896 statement with qualifiers becomes a separate PlaceGeometry node with its own `start_year` and `end_year`, instead of a single flat `geoshape_commons` on Place. That would support multiple time-spanned boundaries per place.

---

**User**

right. so now the agent is in a position to go back to the domain qid of roman republic and traverse through the backlinks, looking for items that have geo type data. this will expand the number of places

---

**Cursor**

Right. The flow is:

**1. Domain anchor** — Roman Republic (e.g. Q17167)

**2. Traverse backlinks** — Items that reference it (P31, P279, P361, P1344, P793, etc.)

**3. Filter for geo-type data** — Among those backlinks, keep items with geographic properties:
- P625 (coords)
- P131 (admin parent)
- P17 (country)
- P3896 (geoshape)
- P1584 (Pleiades)
- P1566 (GeoNames)
- P276 (location)
- P706 (physical feature)

**4. Result** — More Place-like entities than Pleiades alone:
- Places mentioned in Roman Republic context
- Events, battles, campaigns with locations
- Administrative units, provinces, regions
- Sites, monuments, roads

**5. Federation** — For each discovered item:
- If it has P1584 → link to existing Place by pleiades_id
- If it has P1566 → link to GeoNames backbone
- If it has P625/P3896 → enrich coordinates and geoshapes
- If it has neither → candidate for approximation matching (label + coords + hierarchy)

So the agent uses the domain QID as a seed, follows backlinks, and expands the geographic backbone by harvesting geo-typed items from that context.

---

**User**

yes. so lets outline the process

---

**Cursor**

Created **`Geographic/GEO_EXPANSION_PROCESS.md`** with this outline:

---

## Process outline

| Phase | Step |
|-------|------|
| **1. Establish backbone** | Pleiades → crosswalk → enrich → GeoNames/Wikidata hierarchy → geo enrichment |
| **2. Backlink discovery** | Domain QID (Roman Republic) → query backlinks → filter for geo-type (P625, P131, P17, P3896, P1584, P1566, etc.) |
| **3. Federation path** | P1584 → link to Place; P1566 → GeoNames; P625/P3896 → coords/geoshape; P131/P17 → LOCATED_IN |
| **4. Approximation match** | No P1584/P1566 → label search + coord proximity + hierarchy → confidence score → propose qid |
| **5. Logical model** | Time-spanned P3896 → PlaceGeometry with start_year/end_year |
| **6. Full property harvest** | Fetch all claims; parse geo + external IDs + temporal qualifiers; map to graph |

---

**Flow:** Domain QID → backlinks → geo filter → federation or approximation → full property harvest → expanded Place backbone.

Also added to the Geographic README index.

---

**User**

right so this is our geo agent. all it has is a thinly populated geo backbone right now so it has to build it out if new items are needed

---

**Cursor**

Right. The **geo agent** starts from a thin backbone and grows it.

**Starting state**
- Sparse geo backbone (Pleiades + some crosswalk enrichment)
- Many geo-type items from backlinks are not yet in the graph

**Agent behavior**
- When it finds a geo-type item (from backlinks or elsewhere) that has no Place node, it **creates** one
- Uses P1584 → link to existing Place when possible
- Uses P1566 → create or link Place(geonames_id)
- Uses P625/P3896/P131/P17 → create Place(qid) and fill properties
- Uses approximation when there’s no direct ID

**Bootstrap loop**
```
Discover geo item (no Place) → Create Place node → Enrich from Wikidata → Add LOCATED_IN → Backbone grows
```

So the agent both enriches existing Places and **builds out** the backbone for new items.

---

**User**

right so at that point, and we do not need to discuss now, the SFA will start general training in geography and be able to make claims about the geographical facets of the roman republic

---

**Cursor**

Once the geo backbone is populated, the SFA can train on geography and make claims about the geographic facets of the Roman Republic.

---

**User**

write up in nice md format so i can hae it reviewd

---

**Cursor**

Created **`docs/GEO_AGENT_REVIEW.md`** for review. It includes:

---

## Document structure

1. **Executive summary** — Geo Agent role and SFA handoff
2. **Geographic backbone** — Definition, federation score, current thin state
3. **Agent as guardrail** — Graph as source of truth, bootstrap loop
4. **Process overview** — Diagram of phases 1–5
5. **Phase 1** — Backbone setup (scripts and effects)
6. **Phases 2–3** — Backlink discovery and geo filter
7. **Phase 4** — Federation path and approximation matching
8. **Phase 5** — Full property harvest (geo, external IDs, temporal qualifiers)
9. **Logical model** — Place, PlaceGeometry, PlaceName
10. **SFA training** — Downstream use of the backbone
11. **Related documents** — Pointers to other docs
12. **Open questions for review** — 5 items for discussion

---

Linked from `Geographic/README.md` for discoverability.

---

**User**

how does our llm read and write the graph - mcp is read only right now

---

**Cursor**

Here’s how the LLM reads and writes the graph today:

---

## Read path

**MCP (Chrystallum)** — `scripts/mcp/chrystallum_mcp_server.py`:

| Tool | Purpose |
|------|---------|
| `run_cypher_readonly` | MATCH-only Cypher (500 char limit, 500 row cap) |
| `get_policy` | SYS_Policy by name |
| `get_threshold` | SYS_Threshold by name |
| `get_federation_sources` | SYS_FederationSource nodes |
| `get_subject_concepts` | SubjectConcept nodes |
| `get_domain_structure` | SubjectDomain + WikidataTypes for a QID |

**Restrictions on `run_cypher_readonly`:**

- Must start with `MATCH`
- Forbidden: CREATE, SET, DELETE, MERGE, CALL, LOAD, DROP, REMOVE, DETACH

So the LLM can only read via MCP.

---

## Write path

**MCP:** No write tools. Chrystallum MCP is read-only.

**Python scripts:** Full read/write via the `neo4j` driver:

- `enrich_places_from_wikidata_geo.py`
- `link_place_admin_hierarchy.py`
- `enrich_places_from_crosswalk.py`
- etc.

These use `session.run()` with CREATE, MERGE, SET, etc., and are run as batch jobs, not by the LLM.

---

## Current flow

```
LLM (via MCP)  →  run_cypher_readonly  →  Read graph
LLM             →  (no write tool)      →  Cannot write

Python scripts  →  neo4j driver         →  Read + write
```

---

## Enabling LLM writes

To let the LLM write:

1. **Add a write MCP tool** — e.g. `run_cypher_mutation` with safety checks (allowlist, dry-run, human approval).
2. **Use the existing neo4j-server MCP** — `mcp/neo4j-server` already has `run_cypher_mutation`; it would need to be enabled and wired into the agent.
3. **Script-based writes** — LLM proposes Cypher or structured changes; a script or human runs them.

Right now the Geo Agent can only read the graph via MCP; any writes go through Python scripts.

---

**User**

As a solution, this Geo Agent design is strong; it aligns well with your “place = settlement‑centric backbone” idea and with how agentic KGs are being built elsewhere.

What’s particularly good
Backbone-first, not LLM-first. You explicitly say the agent must treat the graph as source of truth and only enrich via Pleiades → GeoNames → Wikidata → TGN, with LOCATED_IN hierarchies; that’s exactly the right guardrail.

Clear federation notion. The “federation score” (Pleiades + GeoNames + Wikidata + temporal + admin hierarchy) is a nice operationalization of “well‑anchored place” and gives you a simple filter for where SFAs can safely reason.
​

Incremental, script-backed pipeline. The 7‑step Phase 1 pipeline matches your existing files and scripts (crosswalks, enrichment, hierarchy linking) and can be run offline until the backbone is “thick” enough.
​

Backlink harvesting from domain QID. Using Q17167 (Roman Republic) and backlinks with geo properties (P625, P131, P17, P3896, P1584, P1566, P276, P706) is a good way to discover “geo‑ish” items relevant to your domain without an exhaustive Wikidata crawl.
​
​

Approximate federation with confidence scoring. The fallback path (label search + coordinate proximity + hierarchy constraint → confidence score) is exactly how gazetteers handle indirect links; making threshold vs. review explicit is excellent.
​
​

Explicit Place / PlaceGeometry / PlaceName split. The logical model you sketch (Place as identity; PlaceGeometry per P625/P3896 with time qualifiers; PlaceName from labels/aliases) matches the theoretical “place” decomposition we just discussed.
​
​

Gaps / open questions worth tightening
All of these are acknowledged in your “Open Questions” section, so they’re not flaws so much as next decisions:

Confidence thresholds & review workflow. You’ll want concrete numbers and a place to store “candidate matches” awaiting human review, so SFAs don’t treat low‑confidence links as facts.
​

Creation policy for Place(qid) vs Place(geonames_id). You should encode a simple preference order (e.g., prefer Pleiades‑anchored when ancient; prefer GeoNames‑anchored when modern; allow dual anchoring if both exist) and stick to it for consistency.
​

Scope of place_scope = 'v1_core'. You list “settlements, regions, villas, forts, colonies, etc.”; it may help to explicitly say: v1 focuses on settlements and immediate political centers, with natural features (rivers, coasts) only added when required by a use case.

Handoff criterion to SFA. “Sufficiently populated backbone” needs a metric: e.g., “≥ X% of Pleiades settlements relevant to Roman Republic have federation score ≥ Y” before you let SFAs treat geography as a reliable facet.

Fit with your broader architecture
It matches your desire to treat place primarily as settlement while leaving room for richer roles/geometries later.

It gives SFAs a robust geographic substrate without making them reconstruct geography from text.

It slots neatly into the multi‑agent/graph‑delta world: Geo Agent emits Place/PlaceGeometry/LOCATED_IN deltas; SFAs later emit claims and pattern tags built on those Places.

From here, the most useful next step might be to define a tiny set of Geo Agent output deltas (CREATE_PLACE, ENRICH_PLACE, CREATE_GEOMETRY, CREATE_LOCATED_IN) in the same style as your SFA graph deltas, so all agents share one mutation vocabulary.

Here’s how the LLM reads and writes the graph today:
Read path
MCP (Chrystallum) — scripts/mcp/chrystallum_mcp_server.py:
ToolPurpose
run_cypher_readonly
MATCH-only Cypher (500 char limit, 500 row cap)
get_policy
SYS_Policy by name
get_threshold
SYS_Threshold by name
get_federation_sources
SYS_FederationSource nodes
get_subject_concepts
SubjectConcept nodes
get_domain_structure
SubjectDomain + WikidataTypes for a QID
Restrictions on run_cypher_readonly:
Must start with MATCH
Forbidden: CREATE, SET, DELETE, MERGE, CALL, LOAD, DROP, REMOVE, DETACH
So the LLM can only read via MCP.
Write path
MCP: No write tools. Chrystallum MCP is read-only.
Python scripts: Full read/write via the neo4j driver:
enrich_places_from_wikidata_geo.py
link_place_admin_hierarchy.py
enrich_places_from_crosswalk.py
etc.
These use session.run() with CREATE, MERGE, SET, etc., and are run as batch jobs, not by the LLM.
Current flow
LLM (via MCP)  →  run_cypher_readonly  →  Read graph
LLM             →  (no write tool)      →  Cannot write
Python scripts  →  neo4j driver         →  Read + write
Enabling LLM writes
To let the LLM write:
Add a write MCP tool — e.g. run_cypher_mutation with safety checks (allowlist, dry-run, human approval).
Use the existing neo4j-server MCP — mcp/neo4j-server already has run_cypher_mutation; it would need to be enabled and wired into the agent.
Script-based writes — LLM proposes Cypher or structured changes; a script or human runs them.
Right now the Geo Agent can only read the graph via MCP; any writes go through Python scripts.
Given this setup, the safest and least disruptive path is to keep the LLM read-only and treat writes as a separate, batch “change application” channel, at least for now.

What your current model implies
The LLM (Geo Agent, SFAs) already behaves like a reader + planner: it inspects the graph via run_cypher_readonly, reasons, and then you (or a script) apply changes with full Neo4j access.

All mutation is currently auditable and repeatable because it lives in Python scripts (enrich_places_from_*, link_place_admin_hierarchy.py, etc.), not ad‑hoc Cypher the model emitted.

That is actually a good fit for your “graph deltas” idea: the LLM proposes deltas; trusted code applies them.

A practical “next step” design
You can evolve toward agentic writes without giving the LLM direct mutation power:

Keep MCP read‑only.

Preserve run_cypher_readonly exactly as is.

Don’t expose run_cypher_mutation yet.

**Have the Geo Agent (and SFAs) return structured deltas, not Cypher.

Use the minimal schema we sketched for SFA deltas and define a parallel, simpler one for Geo Agent:

CREATE_PLACE, ENRICH_PLACE, CREATE_GEOMETRY, CREATE_LOCATED_IN, etc.

These deltas are just JSON; they do not touch Neo4j directly.

Introduce a small Python “delta applier” script.

It:

Reads a batch of deltas from a file/queue.

Validates them.

Translates them into Cypher CREATE / MERGE / SET calls using the existing Neo4j driver.

This reuses your current script-based write pattern and keeps all mutations in one known place.

Optionally add a human review step.

For low‑confidence or high-impact deltas (e.g., new Place vs merge), you can:

Dump them to a “review” file.

Approve/reject in a simple UI or by editing flags.

Only accepted deltas get applied.

Why this is preferable to immediate run_cypher_mutation
You maintain a clear separation of concerns: LLM = proposes changes; Python = enforces invariants and writes.

You can evolve your invariants (ID strategy, place_scope rules, federation thresholds) in Python without re‑prompting the model.

You keep a clean audit trail of what changed when and why, since each applied delta can be logged with its originating agent and justification.

Later, if you decide you want fully autonomous online updates, you can:

Wrap the Python “delta applier” as an MCP tool instead of exposing raw Cypher.

Give the LLM access to only that tool, so it still can’t run arbitrary CREATE/DELETE; it can only submit deltas for application.

Given what you’ve described, this is already consistent: the Geo Agent stays read‑only at the graph level, but becomes write‑capable at the “proposal” level, and your existing scripts remain the authoritative writers.



---

**Cursor**

Updated **`docs/GEO_AGENT_REVIEW.md`** with the feedback:

---

**Changes made**

1. **Review summary** — Added a short validation note at the top.
2. **Section 11: Graph read/write model** — Describes current read-only MCP and script-based writes.
3. **Delta-based write path** — Documents the recommended approach:
   - Geo Agent returns structured deltas (CREATE_PLACE, ENRICH_PLACE, CREATE_GEOMETRY, CREATE_LOCATED_IN)
   - Python delta applier validates and applies them
   - MCP stays read-only
4. **Section 12: Gaps / open questions** — Refined with:
   - Confidence thresholds and review workflow
   - Place creation policy (Pleiades vs GeoNames preference)
   - `place_scope = 'v1_core'` scope (settlements vs natural features)
   - SFA handoff criterion (metric)
   - Delta schema alignment with SFA deltas

---

**User**

i think we run it without many constraints to see what it returns and then look at quality

---

**Cursor**

A practical approach:

**Phase 0: Exploratory run**

- Run backlink discovery from Q17167 (Roman Republic) with minimal filters.
- Keep all geo-type candidates (P625, P131, P17, P3896, P1584, P1566, etc.).
- No confidence thresholds, no place_scope filters, no row caps beyond API limits.
- Collect the full candidate set and what the agent would propose.

**Then: Quality review**

- Inspect the output: noise, duplicates, wrong types, missing links.
- Decide which constraints to add (confidence thresholds, place_scope, review workflow).
- Iterate on filters based on observed quality.

This gives you real data to tune the pipeline instead of guessing constraints upfront.

---

**User**

yes, so we need a new script?

---

**Cursor**

Creating a dedicated script for exploratory geo discovery. Checking the harvest output format:


Creating a dedicated exploratory script for geo discovery:


Created **`scripts/backbone/geographic/geo_backlink_discovery.py`**.

---

**What it does**

1. **Fetches backlinks** from the seed QID (default Q17167) via P31, P279, P361, P1344, P793, P17, P131, P276, P706.
2. **Loads claims** for each backlink via the Wikidata API.
3. **Keeps geo-type items** — those with any of P625, P131, P17, P3896, P1584, P1566, P276, P706.
4. **Writes** `output/geo_discovery/{seed}_geo_candidates.json` with candidates and geo property counts.

**Usage**

```bash
python scripts/backbone/geographic/geo_backlink_discovery.py --seed Q17167
python scripts/backbone/geographic/geo_backlink_discovery.py --seed Q17167 --limit 500
python scripts/backbone/geographic/geo_backlink_discovery.py --seed Q17167 --output output/geo_discovery/
```

**Output format**

```json
{
  "seed_qid": "Q17167",
  "backlinks_total": 1234,
  "candidates_count": 456,
  "geo_property_counts": {"P625": 200, "P131": 300, ...},
  "candidates": [{"qid": "Q123", "label": "...", "geo_properties": ["P625", "P131"]}, ...]
}
```

Run it, inspect the output, then decide what constraints to add.

---

**User**

which one to run?

---

**Cursor**

Use the exploratory discovery script:

```bash
python scripts/backbone/geographic/geo_backlink_discovery.py --seed Q17167
```

That will:
1. Fetch backlinks to Q17167 (Roman Republic)
2. Filter for items with geo properties (P625, P131, P17, P3896, etc.)
3. Write `output/geo_discovery/Q17167_geo_candidates.json`

Run it from the project root. For a smaller test run, add `--limit 500`.

---

**User**

add labels to all in script. i cant always lookup codes

---

**Cursor**

Updates are in place. The script output now includes labels:

**Top-level reference:**
- `property_labels` — geo properties (P625 → "coordinate location", etc.)
- `backlink_property_labels` — backlink properties (P31 → "instance of", etc.)
- `seed_label` — human-readable name for the seed (e.g. "Roman Republic")
- `geo_property_counts_labeled` — `[{pid, label, count}, ...]` instead of raw counts

**Per candidate:**
- `geo_properties_labeled` — `[{pid, label}, ...]` for each candidate

Example output:

```json
{
  "seed_qid": "Q17167",
  "seed_label": "Roman Republic",
  "property_labels": {
    "P625": "coordinate location",
    "P131": "located in administrative entity",
    "P17": "country",
    ...
  },
  "geo_property_counts_labeled": [
    {"pid": "P17", "label": "country", "count": 79},
    {"pid": "P276", "label": "location", "count": 24},
    ...
  ],
  "candidates": [
    {
      "qid": "Q11948139",
      "label": "Seleuceia in Cilicia",
      "geo_properties": ["P625", "P131", "P17", "P1584", "P276"],
      "geo_properties_labeled": [
        {"pid": "P131", "label": "located in administrative entity"},
        {"pid": "P1584", "label": "Pleiades ID"},
        ...
      ]
    }
  ]
}
```

---

**User**

also add instance of and subclass of

---

**Cursor**

Update complete. Each candidate now includes:

- **`instance_of`** — P31 QIDs
- **`instance_of_labeled`** — `[{qid, label}, ...]` (e.g. `{"qid": "Q178561", "label": "war"}`)
- **`subclass_of`** — P279 QIDs
- **`subclass_of_labeled`** — `[{qid, label}, ...]`

A top-level **`type_property_labels`** section was added: `{"P31": "instance of", "P279": "subclass of"}`.

Example candidate:

```json
{
  "qid": "Q11688220",
  "label": "Battle of Petelia",
  "instance_of": ["Q178561"],
  "instance_of_labeled": [{"qid": "Q178561", "label": "war"}],
  "subclass_of": [],
  "subclass_of_labeled": [],
  "geo_properties": ["P625", "P17", "P276"],
  "geo_properties_labeled": [...]
}
```

---

**User**

try again dont want to see a pid or qid without a label @Q17167_geo_candidates.json (82-92) 

---

**Cursor**

The JSON output is updated so every PID and QID appears with a label:

**Changes:**
- **Candidates:** Only labeled fields:
  - `instance_of`: `[{qid, label}, ...]` (no raw QID list)
  - `subclass_of`: `[{qid, label}, ...]`
  - `geo_properties`: `[{pid, label}, ...]` (no raw PID list)
- **Seed:** `{"qid": "...", "label": "Roman Republic"}`
- **geo_property_counts:** `[{pid, label, count}, ...]`
- **Labels:** Fallback to de, fr, es, it if English is missing; otherwise `"(no label found)"`
- **Reference tables:** Removed `property_labels` and `backlink_property_labels`; labels are inline everywhere

**Example candidate:**
```json
{
  "qid": "Q6082350",
  "label": "Pompeians",
  "instance_of": [{"qid": "Q1393724", "label": "political faction"}],
  "subclass_of": [],
  "geo_properties": [{"pid": "P17", "label": "country"}]
}
```

---

**User**

ok that returned junk. we also need values. it cant say a backlink has a geo location that should map to our geo backbone. this shoiuld not happen @Q17167_geo_candidates.json (181-191) 

---

**Cursor**

Summary of the changes:

---

**1. Stricter filter — backbone-mappable only**

- **Qualifying properties:** P625, P276, P131, P3896, P1584, P1566 (at least one required).
- **P17 (country) alone no longer qualifies** — items like "Buddhism and the Roman world" are excluded.
- **P706** alone also does not qualify.

**2. Geo properties now include values**

- **P17, P131, P276, P706:** `value_qid` + `value_label` (e.g. `{"value_qid": "Q29", "value_label": "Spain"}`).
- **P625:** `value` (e.g. `"41.9, 12.5"`).
- **P1584, P1566:** `value` (e.g. `"423025"`).
- **P3896:** `value` (Commons Data path).

**3. Example output**

```json
{
  "qid": "Q11948139",
  "label": "Seleuceia in Cilicia",
  "geo_properties": [
    {"pid": "P625", "label": "coordinate location", "value": "36.12, 33.93"},
    {"pid": "P131", "label": "located in administrative entity", "value_qid": "Q858", "value_label": "Syria"},
    {"pid": "P1584", "label": "Pleiades ID", "value": "658595"},
    {"pid": "P17", "label": "country", "value_qid": "Q858", "value_label": "Syria"}
  ],
  "instance_of": [{"qid": "Q515", "label": "city"}],
  "subclass_of": []
}
```

**4. Metadata**

- Added `qualifying_filter` to the payload to document the filtering rule.

---

**User**

what are all the distinct subclasses and instance of s were reported

---

**Cursor**

From `Q17167_geo_candidates.json`:

---

## Instance of (18 distinct)

| QID | Label |
|-----|-------|
| Q15661340 | ancient city |
| Q839954 | archaeological site |
| Q178561 | battle |
| Q8465 | civil war |
| Q45382 | coup d'état |
| Q48349 | empire |
| Q1307214 | form of government |
| Q2520735 | government reorganization |
| Q3024240 | historical country |
| Q11514315 | historical period |
| Q511866 | mutiny |
| Q1261499 | naval battle |
| Q148837 | polis |
| Q182547 | Roman province |
| Q104212151 | series of wars |
| Q188055 | siege |
| Q7692360 | volcanic eruption |
| Q198 | war |

---

## Subclass of (0 distinct)

No `subclass_of` values appear in the candidates.

---

**Place-like types:** ancient city (Q15661340), archaeological site (Q839954), polis (Q148837), Roman province (Q182547).

**Event types:** battle, civil war, siege, naval battle, war, series of wars, mutiny, coup d'état, volcanic eruption.

**Other:** empire, form of government, government reorganization, historical country, historical period.

---

**User**

ancient city (Q15661340)
Item
Discussion
Read
View history

Tools
Appearance hide
Text

Small

Standard

Large
Width

Standard

Wide
Color (beta)

Automatic

Light

Dark
city in historical records
historical cityextinct cityancient townformer city
In more languages
Configure
Language	Label	Description	Also known as
default for all languages	
No label defined
–
English	
ancient city
city in historical records
historical city
extinct city
ancient town
former city
Spanish	
ciudad antigua
comunidad urbana mencionada en registros históricos
ciudad histórica
ciudad historica
ciudad de la antigüedad
Traditional Chinese	
古城
No description defined
Chinese	
古城
No description defined
All entered languages
Statements
subclass of
city
0 references
former settlement
0 references
archaeological site
nature of statement
often
0 references
 we need to go back to the process and model we defined, this is suppposed to be llm 

---

**Cursor**

The Geo Agent is meant to be **LLM-driven**, not a script-only pipeline. The model we defined has the agent:

1. **Read** the graph and candidates  
2. **Reason** over instance_of, subclass_of, and Wikidata structure  
3. **Decide** what maps to the backbone and propose deltas  

**What’s missing**

The script does discovery and filtering without the LLM. For something like “ancient city” (Q15661340), the agent should reason:

- Subclass of: city, former settlement  
- Often: archaeological site  
- → Place-like, maps to backbone (settlements, v1_core)  
- Has P625, P1584 → strong federation signal  

**How to put the LLM back in the loop**

1. **Script** → outputs candidates (as now)  
2. **LLM** → receives candidates and their instance_of/subclass_of  
3. **LLM** → reasons over Wikidata ontology (subclass chains, “often” relations)  
4. **LLM** → decides: backbone vs event vs other, and proposes CREATE_PLACE / ENRICH_PLACE / skip  
5. **Delta applier** → applies approved deltas  

So the script is a **data-gathering** step; the **LLM** should do the classification and mapping using the ontology. Next step is to define that LLM step (inputs, prompts, and outputs) and wire it into the process.

---

**User**

he script is doing both gathering and classifying, and you want the LLM to take over the classification/mapping step.

What you already have
Script pulls candidates for Q17167 (Roman Republic) from Wikidata, filtered by geo-ish properties.

Output is a nice JSON bundle: each candidate has qid, label, instance_of, subclass_of (empty here), and geo_properties (P1584, P1566, P625, P276, P17, etc.).

This is the perfect input for an LLM “Geo Agent” classification pass.

In that bundle, for example:

Byzantium (Q23725): instance_of = ancient city, polis, has P1584, P625 → classic v1_core Place.

Seleuceia in Cilicia (Q11948139): instance_of = ancient city, archaeological site, has P1584, P625, P131 → also v1_core Place.

Asia (province) has P1584 + P1566 → Place (region‑level).

Battles, sieges, wars, eruptions, mutiny, “Pompey’s eastern settlement”, “March on Rome” → Events, not Places; they should attach to Place via P276 targets (settlements/regions), not become Place nodes themselves.

Your script can’t easily generalize that “ancient city” and “archaeological site” are Place‑like while “battle” and “civil war” are Events; the LLM can.

What the missing LLM step should do
Define a Geo Agent step like this:

Inputs (per batch)
The JSON you showed:

Seed: {"qid": "Q17167", "label": "Roman Republic"}

candidates[] with:

qid, label

instance_of[] (qid, label)

subclass_of[] if present

geo_properties[] (pid, label, value/value_qid/value_label)

Optionally also pass:

A small, fixed ontology sketch of what counts as v1_core Place: e.g. labels/IDs for “city”, “ancient city”, “settlement”, “Roman province”, etc., and for Event types (“battle”, “war”, “siege”, “eruption”, “mutiny”, “government reorganization”, “coup d’état”).

Tasks for the LLM
For each candidate:

Classify as:

place_core (v1_core: settlement, city, ancient city, archaeological site that is a former settlement, province/region you care about).

place_noncore (natural feature, river, mountain, etc.; maybe defer for now).

event (battle, siege, war, mutiny, eruption, coup, etc.).

other (ignore).

If Place-like: decide federation path.

If has P1584 → link to Pleiades‑backed Place (maybe create if missing).

Else if has P1566 → link to GeoNames‑backed Place (create if missing).

Else if has P625 (+ maybe P131/P17) → propose a fresh Place(qid) with coordinates and LOCATED_IN.

If Event-like: propose only event→place attachments.

Do not propose new Place; instead:

For each P276 or other location property that points to a Place‑type QID, propose an event→Place relationship (for later Event Agent).

Output one or more deltas per candidate.

Output format (Geo Agent deltas)
You can keep it simple and aligned with your earlier graph‑delta idea, e.g.:

json
{
  "seed_qid": "Q17167",
  "candidates": [
    {
      "qid": "Q23725",
      "label": "Byzantium",
      "classification": "place_core",
      "deltas": [
        {
          "op_type": "CREATE_OR_ENRICH_PLACE",
          "place_key": {
            "pleiades_id": "520985"
          },
          "source_qid": "Q23725",
          "properties": {
            "label": "Byzantium",
            "qid": "Q23725",
            "pleiades_id": "520985",
            "centroid_lat": 41.013416666666664,
            "centroid_lng": 28.98363888888889,
            "base_type_hint": ["ancient city", "polis"]
          }
        }
      ]
    },
    {
      "qid": "Q60524412",
      "label": "Battle of Lauron",
      "classification": "event",
      "deltas": [
        {
          "op_type": "ATTACH_EVENT_TO_PLACE",
          "event_qid": "Q60524412",
          "place_qid": "Q11045304",
          "place_label": "Lauro",
          "relation_type": "OCCURRED_AT"
        }
      ]
    },
    {
      "qid": "Q210718",
      "label": "Asia",
      "classification": "place_core",
      "deltas": [
        {
          "op_type": "CREATE_OR_ENRICH_PLACE",
          "place_key": {
            "pleiades_id": "981509",
            "geonames_id": "8378482"
          },
          "source_qid": "Q210718",
          "properties": {
            "label": "Asia",
            "qid": "Q210718",
            "pleiades_id": "981509",
            "geonames_id": "8378482",
            "centroid_lat": 38.4,
            "centroid_lng": 28.3,
            "base_type_hint": ["Roman province"]
          }
        }
      ]
    }
  ]
}
Your delta applier then:

For CREATE_OR_ENRICH_PLACE:

Checks if a Place with that pleiades_id or geonames_id already exists.

If yes, merges/enriches (adds qid, coords).

If not, creates a new Place node.

For ATTACH_EVENT_TO_PLACE:

Does not create a Place; just records the Event→Place relationship (to be handled by an Event Agent later).

Where this sits in your pipeline
Revised pipeline:

Script:

Given domain QID (Q17167), query Wikidata for backlinks, filter by “geo-ish” properties as you already do.

Produce the JSON bundle you pasted.

LLM Geo Agent:

Takes the bundle as input.

Outputs classification + deltas JSON.

Delta Applier (Python):

Reads Geo Agent output.

Applies CREATE_OR_ENRICH_PLACE and other place-related deltas into Neo4j.

(Later) Event Agent:

Consumes ATTACH_EVENT_TO_PLACE deltas to build out event facets.

Why this puts the LLM “back in the loop”
The script becomes pure data gathering and minimal filtering.

The LLM does the ontological reasoning: “ancient city” is Place; “battle” is Event; “Roman province” is Place; “volcanic eruption” is Event; etc.

The applier maintains your invariants and keeps writes safe.

If you’d like, I can next sketch a minimal prompt template for the Geo Agent that would take exactly your JSON snippet and ask for this classification + delta output.

yes
Here’s a compact prompt you can drop into your Geo Agent, tuned to the JSON you just showed.

Prompt skeleton for Geo Agent classification
System / tool context (once):

You are the Geo Agent for the Chrystallum project.
The graph already contains Place nodes for many Pleiades and GeoNames records.
Your job is to:

Decide which Wikidata items are places (settlements, cities, provinces, regions) and which are events or other types.

For place-like items, decide how they should map to existing or new Place nodes.

Propose structured graph deltas; you do NOT write Cypher or directly modify the graph.

A v1_core Place is: human settlement (city, town, village, ancient city, colony, villa, fort, camp) or closely related political region (Roman province, region) relevant to the Roman Republic.
Events (battles, wars, sieges, eruptions, mutinies, coups, government reorganizations) are not Places. They should attach to Places via their location.

You may use the instance_of and subclass_of types to infer whether something is a Place or an Event, and you should pay special attention to geo properties:

P1584 (Pleiades ID), P1566 (GeoNames ID), P625 (coordinate location), P131 (located in admin entity), P17 (country), P276 (location).

User / task prompt (per batch):

Input (JSON):

json
{ ... your bundle exactly as provided ... }
Tasks:

For each candidate:

Classify as one of: "place_core", "place_noncore", "event", "other".

"place_core": settlements (city, town, village, ancient city, colony, archaeological site that is a former settlement), Roman provinces/regions relevant to Q17167.

"place_noncore": natural features (rivers, mountains, volcanoes, seas, etc.) and very broad regions you do not want in v1.

"event": battles, sieges, wars, mutinies, coups, eruptions, reorganizations, etc.

"other": anything else that should be ignored for geography.

For "place_core" and "place_noncore":

If the candidate has P1584 (Pleiades ID), propose a CREATE_OR_ENRICH_PLACE delta keyed by that Pleiades ID.

Else if it has P1566 (GeoNames ID), propose a CREATE_OR_ENRICH_PLACE delta keyed by that GeoNames ID.

Else if it has P625 (coordinates), propose a CREATE_OR_ENRICH_PLACE delta keyed by its qid, using the coordinates.

In properties, include at least:

label (the candidate label)

qid

Any Pleiades/GeoNames IDs

centroid_lat and centroid_lng if P625 is present

base_type_hint: array of instance_of labels that suggest settlement/province/region.

For "event":

Do not propose new Place nodes.

For each P276 (location) whose value_qid looks place-like (city, region, province, etc.), propose an ATTACH_EVENT_TO_PLACE delta:

event_qid (the candidate’s qid)

place_qid (the P276 value_qid)

place_label (the P276 value_label)

relation_type: "OCCURRED_AT".

For "other": no deltas.

Output:

Return a single JSON object with this structure:

json
{
  "seed_qid": "Q17167",
  "candidates": [
    {
      "qid": "...",
      "label": "...",
      "classification": "place_core | place_noncore | event | other",
      "deltas": [ ... zero or more deltas as specified ... ]
    }
  ]
}
Each delta must be one of:

json
{
  "op_type": "CREATE_OR_ENRICH_PLACE",
  "place_key": {
    "pleiades_id": "…",        // if available
    "geonames_id": "…"         // if available
  },
  "source_qid": "Q23725",
  "properties": {
    "label": "Byzantium",
    "qid": "Q23725",
    "pleiades_id": "520985",
    "geonames_id": null,
    "centroid_lat": 41.013416666666664,
    "centroid_lng": 28.98363888888889,
    "base_type_hint": ["ancient city", "polis"]
  }
}
or

json
{
  "op_type": "ATTACH_EVENT_TO_PLACE",
  "event_qid": "Q60524412",
  "place_qid": "Q11045304",
  "place_label": "Lauro",
  "relation_type": "OCCURRED_AT"
}
Do not emit Cypher or natural-language explanations. Produce valid JSON only.

This gives you:

A clear place for the LLM to re‑enter the loop.

A strict output format your Python delta‑applier can consume.

A clean separation: script gathers; Geo Agent reasons; Python writes.

---

**Cursor**

Summary of what was added and updated:

## Created

1. **`md/Agents/geo_agent_classification_prompt.md`** — Prompt for the Geo Agent:
   - System context (v1_core Place, Events, geo properties)
   - Task prompt (classify each candidate, emit deltas)
   - Output schema with examples
   - Delta types: `CREATE_OR_ENRICH_PLACE`, `ATTACH_EVENT_TO_PLACE`

2. **`Geographic/GEO_AGENT_DELTA_SCHEMA.md`** — Delta schema:
   - Output wrapper (`seed_qid`, `candidates[]`)
   - Classifications: `place_core`, `place_noncore`, `event`, `other`
   - Delta specs and field descriptions
   - Delta applier behavior (lookup, MERGE/CREATE, invariants)

3. **`scripts/agents/geo/README.md`** — Geo Agent overview:
   - Pipeline steps
   - Input/output formats
   - Pointers to prompt and schema

## Updated

4. **`docs/GEO_AGENT_REVIEW.md`** — Pipeline and references:
   - Phase 3b: Geo Agent (LLM) classification step
   - Table: Script → Geo Agent → Delta Applier → Event Agent
   - Delta types updated to `CREATE_OR_ENRICH_PLACE`, `ATTACH_EVENT_TO_PLACE`
   - Related docs: delta schema, prompt, Geo Agent README
   - Gap #5 marked as done

5. **`Geographic/GEO_EXPANSION_PROCESS.md`** — LLM classification:
   - Phase 3a: Geo Agent (LLM) classification
   - Phase 3b: Delta Applier behavior
   - Summary flow updated to include the Geo Agent step

6. **`Geographic/README.md`** — Index:
   - `GEO_AGENT_DELTA_SCHEMA.md`
   - `geo_agent_classification_prompt.md`
   - `geo_backlink_discovery.py` description updated

The Geo Agent prompt is ready to use with the discovery JSON. Next step is implementing the Python delta applier that reads the Geo Agent output and applies the deltas to Neo4j.

---

**User**

dont want it in neo yet but want to see the output

---

**Cursor**

Creating a script that invokes the Geo Agent (LLM) and writes the output to a file, without writing to Neo4j.


The Geo Agent classification script is in place and has been run. Summary:

## Script

**`scripts/agents/geo/geo_agent_classify.py`**

- Reads geo discovery JSON (default: `output/geo_discovery/Q17167_geo_candidates.json`)
- Sends it to Claude (Anthropic) for classification
- Writes output to `output/geo_discovery/Q17167_geo_agent_output.json`
- Does not write to Neo4j

## Run

```bash
python scripts/agents/geo/geo_agent_classify.py
```

## Output

**`output/geo_discovery/Q17167_geo_agent_output.json`**

- **23 events** (battles, wars, eruption, etc.) → `ATTACH_EVENT_TO_PLACE` deltas
- **3 place_core** (Byzantium, Seleuceia in Cilicia, Asia province) → `CREATE_OR_ENRICH_PLACE` deltas
- **1 other** (ignored)

Example place_core (Byzantium):

```json
{
  "qid": "Q23725",
  "label": "Byzantium",
  "classification": "place_core",
  "deltas": [{
    "type": "CREATE_OR_ENRICH_PLACE",
    "place_key": "pleiades_id:520985",
    "source_qid": "Q23725",
    "properties": {
      "label": "Byzantium",
      "qid": "Q23725",
      "pleiades_id": "520985",
      "centroid_lat": 41.013...,
      "centroid_lng": 28.983...,
      "base_type_hint": ["ancient city", "polis"]
    }
  }]
}
```

Example event (Battle of Saguntum):

```json
{
  "qid": "Q9173528",
  "label": "Battle of Saguntum",
  "classification": "event",
  "deltas": [{
    "type": "ATTACH_EVENT_TO_PLACE",
    "event_qid": "Q9173528",
    "place_qid": "Q47483",
    "place_label": "Sagunto",
    "relation_type": "OCCURRED_AT"
  }]
}
```

**Note:** The LLM used `"type"` instead of `"op_type"` and `place_key` as a string instead of an object. When you add the delta applier, it can normalize these or the prompt can be tightened to match the schema.

---

**User**

is that paginated or looking at all backlins, is it transversing up or down 

---

**Cursor**

From `geo_backlink_discovery.py`:

## Pagination

**Not paginated.** It does one SPARQL query per backlink property, each with a fixed limit:

```python
# Line 88-97
def fetch_backlinks(seed_qid: str, limit: int = 2000) -> List[str]:
    for prop in BACKLINK_PROPERTIES:
        query = f"""
        SELECT DISTINCT ?item
        WHERE {{
          ?item wdt:{prop} wd:{seed_qid} .
        }}
        LIMIT {limit}
        """
```

- One request per property (P31, P279, P361, P1344, P793, P17, P131, P276, P706)
- Up to 2000 items per property
- No `OFFSET` or cursor; no follow-up pages
- Results are merged and deduplicated across properties

So you get at most ~20k items (10 properties × 2000), and if there are more backlinks than that, some are never fetched.

---

## Direction (up vs down)

**Traversing down (inbound to the seed).**

The pattern is:

```sparql
?item wdt:{prop} wd:{seed_qid}
```

So: items whose `prop` points **to** the seed (Q17167 Roman Republic).

Examples:

- Battle of Saguntum has `P17 country = Roman Republic` → Battle points to Roman Republic
- Byzantium has `P131 located in = Roman Republic` → Byzantium points to Roman Republic

So the seed is the **target**; the script collects **sources** (backlinks). In hierarchy terms, that’s “down” from the domain to things that are in it or related to it (battles, places, events, etc.), not “up” to broader concepts.

---

**User**

find it hard to believe this is the entire extent of it 
[1] Fetching backlinks...
  Found 80 unique backlink QIDs

[2] Fetching entity claims...
  Fetched 81 entities

[3] Geo-type candidates: 27

[3b] Fetching instance-of/subclass-of labels...

[3c] Fetching geo value labels...

  Geo property distribution:
    P131 (located in administrative entity): 2
    P1566 (GeoNames ID): 1
    P1584 (Pleiades ID): 3
    P17 (country): 32
    P276 (location): 28
    P3896 (geoshape): 0
    P625 (coordinate location): 14
    P706 (located in/on physical feature): 0

  Wrote: output\geo_discovery\Q17167_geo_candidates.json

c:\Projects\Graph1>python scripts/agents/geo/geo_agent_classify.py

---

**Cursor**

Checking what's limiting the results:


Checking the full picture:


Here's what the data shows:

## What’s going on

**80 backlinks is correct for direct links to Q17167.** The SPARQL counts are:

| Property | Count |
|----------|-------|
| P17 (country) | 79 |
| P361 (part of) | 3 |
| P276 (location) | 1 |
| P31, P279, P1344, P793, P131, P706 | 0 |

So Wikidata has only ~80 items that directly reference Roman Republic (Q17167). The script is not truncating results.

## Why it feels too small

Most Roman Republic–related items don’t point at Q17167 directly. They point at:

- **Provinces** (Hispania, Asia, etc.) via P131 / P276
- **Cities** (Rome, Saguntum, etc.) via P276
- **Regions** (Gaul, etc.)

Example: Hispania (Q186513) alone has 13 items with P131 and 28 with P276.

## How to get more coverage

You need to expand the seed set beyond Q17167:

1. **Multi-hop seeds**  
   - Get entities that are part of Roman Republic (P361=Q17167) → e.g. provinces.  
   - Get entities located in those provinces (P131=province).  
   - Union backlinks for Q17167 + provinces + major regions.

2. **Province-centric queries**  
   - Use Roman provinces (e.g. Asia Q210718, Hispania Q186513) as seeds.  
   - Run the same backlink logic for each province and merge results.

3. **Transitive expansion**  
   - Start from Q17167.  
   - Add all items with P361=Q17167 or P131=Q17167.  
   - Recursively add their backlinks (with a depth limit).

I can sketch or implement a multi-hop expansion in `geo_backlink_discovery.py` if you want.

---

**User**

yes

---

**Cursor**

Checking the 3 expansion seeds and adding province-based expansion:


Adding a curated list of Roman provinces as expansion seeds.


The expansion run finished successfully. Updated results:

## Results with `--expand`

| Metric | Before | After |
|--------|--------|-------|
| **Backlinks** | 80 | **6,641** |
| **Geo candidates** | 27 | **5,726** |

`expansion_seeds` now includes:
- 3 temporal subdivisions (Late/Early/Middle Roman Republic)
- 16 Roman provinces (Hispania, Asia, Gaul, Macedonia, Syria, Sicily, Sardinia, Corsica, Lusitania, Baetica, Tarraconensis, Ulterior, Citerior, Illyria, Cisalpine Gaul, Transalpine Gaul)
- Roman Egypt (Q10289)

## Changes made

1. **`fetch_expansion_seeds()`** – Fetches child entities via P361 (part of) and P131 (located in).
2. **Curated province list** – For Q17167, adds `ROMAN_REPUBLIC_PROVINCES` (Hispania, Asia, Gaul, Macedonia, Syria, Sicily, etc.).
3. **`--expand` flag** – When set, merges all expansion seeds and backlinks for them.
4. **`fetch_backlinks()`** – Accepts a list of seeds and unions backlinks for each.

## Usage

```bash
python scripts/backbone/geographic/geo_backlink_discovery.py --seed Q17167 --expand
```

Output is written to `output/geo_discovery/Q17167_geo_candidates.json`. The expanded run takes ~3–5 minutes for ~6k backlinks and entity fetching.

---

**User**

remind me of filter again

---

**Cursor**

Here’s the filter used in geo backlink discovery:

## Qualifying filter

**A candidate is kept only if it has at least one of these geo properties:**

| PID | Property |
|-----|----------|
| P625 | coordinate location |
| P276 | location |
| P131 | located in administrative entity |
| P3896 | geoshape |
| P1584 | Pleiades ID |
| P1566 | GeoNames ID |

**P17 (country) alone does not qualify** — many non-place items (people, events, concepts) have P17, so it’s not enough to treat something as a place.

## Flow

1. **Backlinks** – Items that reference the seed via P31, P279, P361, P1344, P793, P17, P131, P276, P706.
2. **Filter** – Keep only those that have at least one of P625, P276, P131, P3896, P1584, P1566.
3. **Output** – Those that pass the filter become geo candidates.

---

**User**

show flow with labels

---

**Cursor**

## Geo backlink discovery flow (with labels)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SEED                                                                        │
│  Q17167 (Roman Republic)                                                     │
│  + optional --expand: provinces (Hispania, Asia, Gaul, etc.)                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: BACKLINKS                                                           │
│  Items that reference the seed via any of:                                  │
│  P31  instance of                                                            │
│  P279 subclass of                                                            │
│  P361 part of                                                                │
│  P1344 participated in                                                       │
│  P793 significant event                                                      │
│  P17  country                                                                │
│  P131 located in administrative entity                                       │
│  P276 location                                                               │
│  P706 located in/on physical feature                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: QUALIFYING FILTER                                                   │
│  Keep only items that have at least one of:                                 │
│  P625  coordinate location                                                   │
│  P276  location                                                              │
│  P131  located in administrative entity                                     │
│  P3896 geoshape                                                              │
│  P1584 Pleiades ID                                                           │
│  P1566 GeoNames ID                                                           │
│                                                                              │
│  P17 (country) alone does NOT qualify                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: GEO CANDIDATES                                                      │
│  Output: JSON bundle with qid, label, instance_of, subclass_of,             │
│          geo_properties (P625, P276, P131, P17, P1584, P1566, etc.)          │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: GEO AGENT (LLM)                                                     │
│  Classify: place_core | place_noncore | event | other                        │
│  Propose deltas: CREATE_OR_ENRICH_PLACE, ATTACH_EVENT_TO_PLACE               │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: DELTA APPLIER (Python)                                             │
│  Apply deltas to Neo4j (Place nodes, Event→Place edges)                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**User**

no this in english Backlinks – Items that reference the seed via P31, P279, P361, P1344, P793, P17, P131, P276, P706.
Filter – Keep only those that have at least one of P625, P276, P131, P3896, P1584, P1566.
Output – Those that pass the filter become geo candidates.

---

**Cursor**

## Geo backlink discovery flow (plain English)

**Backlinks** — Items that reference the seed via any of:
- instance of
- subclass of
- part of
- participated in
- significant event
- country
- located in administrative entity
- location
- located in/on physical feature

**Filter** — Keep only items that have at least one of:
- coordinate location
- location
- located in administrative entity
- geoshape
- Pleiades ID
- GeoNames ID

**Output** — Items that pass the filter become geo candidates.

---

**User**

so maybe backlinks to backlinks transversa is the problem, thesae are not really reakated to seed

---

**Cursor**

Here’s what’s going on:

## The issue

**Direct backlinks** (items pointing to Roman Republic):
- P17 = Roman Republic, P131 = Roman Republic, etc.
- These are clearly Roman Republic–related.

**Expansion backlinks** (items pointing to provinces):
- P131 = Hispania, P276 = Gaul, etc.
- Provinces span many centuries (Republic, Empire, Byzantium).
- So we also pull in:
  - Empire-era places and events
  - Medieval and later items
  - Modern people/places “in Hispania” in a broad sense

So we’re effectively doing **backlinks to backlinks**: seed → provinces → items that reference provinces. Many of those items are only loosely related to the Roman Republic.

## Possible fixes

1. **Drop expansion** — Use only direct backlinks to Q17167 (smaller, more focused set).
2. **Tighten expansion seeds** — Use only provinces that are clearly Republican (e.g. exclude Egypt, later provinces).
3. **Add a temporal filter** — Keep only items with dates in the Republican period (e.g. P585, P580, P582).
4. **Rely on the Geo Agent** — Keep the broad set and let the LLM classify; many will become `other` or `place_noncore`.

If you say which direction you prefer (stricter discovery vs. broad + LLM filter), we can adjust the pipeline accordingly.

---

**User**

drop expansion

---

**Cursor**

Expansion is removed. The script now only uses direct backlinks to the seed:

- **80 backlinks** (from Q17167)
- **27 geo candidates**

---

**User**

lloks good. what does llm do with this

---

**Cursor**

## What the LLM does with the geo candidates JSON

The Geo Agent uses the discovery JSON as input and produces a classification and delta JSON.

### Input

The JSON bundle from `geo_backlink_discovery.py`:
- `seed` (qid, label)
- `candidates[]` with `qid`, `label`, `instance_of`, `subclass_of`, `geo_properties`

### What the LLM does

For each candidate:

1. **Classify** as one of:
   - `place_core` — settlements, cities, provinces, regions (v1_core)
   - `place_noncore` — rivers, mountains, seas (deferred)
   - `event` — battles, sieges, wars, mutinies, eruptions, coups
   - `other` — anything else

2. **For place_core / place_noncore** — propose `CREATE_OR_ENRICH_PLACE` deltas:
   - If P1584 (Pleiades ID) → key by `pleiades_id`
   - Else if P1566 (GeoNames ID) → key by `geonames_id`
   - Else if P625 (coordinates) → key by `qid` and use coords
   - Include `label`, `qid`, `centroid_lat`, `centroid_lng`, `base_type_hint` (from `instance_of`)

3. **For event** — propose `ATTACH_EVENT_TO_PLACE` deltas (no new Place nodes):
   - For each P276 (location) whose value_qid is place-like → `event_qid`, `place_qid`, `place_label`, `relation_type: "OCCURRED_AT"`

4. **For other** — no deltas

### Output

A JSON object with:
- `seed_qid`
- `candidates[]` with `qid`, `label`, `classification`, `deltas[]`

### Why the LLM

The script can’t decide that “ancient city” and “archaeological site” are Place-like while “battle” and “civil war” are Events. The LLM does that ontology and mapping, then produces structured deltas for the delta applier to apply to Neo4j.

---

**User**

is that part reaady

---

**Cursor**

Yes. The LLM piece is ready.

**Implemented:**
- `scripts/agents/geo/geo_agent_classify.py` — reads discovery JSON, calls Claude, writes classification + deltas
- Prompt is in the script
- Output: `output/geo_discovery/Q17167_geo_agent_output.json`

**How to run:**
```bash
python scripts/agents/geo/geo_agent_classify.py
```
Requires `ANTHROPIC_API_KEY` in `.env` or environment.

**Not implemented yet:**
- Delta applier — Python script that reads the Geo Agent output and applies `CREATE_OR_ENRICH_PLACE` and `ATTACH_EVENT_TO_PLACE` to Neo4j.

---

**User**

q122918768 To an LLM (and to your Geo SFA), this Wikidata item clearly says:

- This is an **event / process**, not a place.  
  - `instance of: government reorganization (Q2520735)` → it’s a political act or settlement, not a city or province.

- It’s an event **of the Roman Republic**, done by Pompey, in the 60s BCE.  
  - `country: Roman Republic (Q17167)`  
  - `agent of action: Pompey (Q125414)`  
  - `point in time: 60s BCE`

- It affected multiple **eastern provinces / regions** rather than a single point:  
  - `location: Asia (Roman province, Q210718)`  
  - `location: Bithynia et Pontus (Q913382)`  
  - `location: Cilicia (Q4819648)`  
  - `location: Roman Syria (Q207118)`

So, for your agents:

- **Geo Agent**  
  - Sees a non‑place item (government reorganization) that has P276 links to Places (provinces).  
  - Action: ensure those provinces exist as Place nodes, with proper federation (Pleiades, GeoNames) and LOCATED_IN hierarchy. It does *not* create a Place for Q122918768.

- **Event / Political SFA**  
  - Treats Q122918768 as an event:
    - “Pompey’s eastern settlement is a government reorganization of several eastern provinces of the Roman Republic in the 60s BCE.”  
  - Creates Claims and edges like:
    - EVENT_POMPEY_EASTERN_SETTLEMENT –[:OCCURRED_IN]-> (Asia, Bithynia et Pontus, Cilicia, Roman Syria)  
    - EVENT –[:HAS_AGENT]-> Pompey  
    - EVENT –[:IN_COUNTRY]-> Roman Republic  
  - Facets: Political 0.95, Geographic 0.7, Legal/Institutional 0.7.

So the signal to the LLM is:

- “This is a *political event* with a **multi‑place footprint**, not a place itself. Use it to connect Pompey, the Roman Republic, and specific eastern provinces, but don’t treat it as a settlement.”

---

**Cursor**

## Signal for Q122918768 (Pompey's eastern settlement)

**Geo Agent:**
- **Classification:** `event` (instance of: government reorganization)
- **Action:** Do not create a Place for Q122918768
- **Deltas:** For each P276 (location) that is place-like, emit `ATTACH_EVENT_TO_PLACE`:
  - Asia (Q210718)
  - Bithynia et Pontus (Q913382)
  - Cilicia (Q4819648)
  - Roman Syria (Q207118)
- **Side effect:** Ensure those provinces exist as Place nodes (via CREATE_OR_ENRICH_PLACE if they appear as candidates elsewhere)

**Event / Political SFA (later):**
- Treat as event: government reorganization, agent Pompey, country Roman Republic, 60s BCE
- Edges: OCCURRED_IN → those provinces, HAS_AGENT → Pompey, IN_COUNTRY → Roman Republic
- Facets: Political, Geographic, Legal/Institutional

**Core rule:** Political event with a multi-place footprint → not a place; use it to connect agent, country, and provinces, but do not create a Place for the event itself.

The current Geo Agent prompt already covers this (government reorganizations as events, ATTACH_EVENT_TO_PLACE per P276). If you want, we can add Q122918768 as an explicit example in the prompt.

---

**User**

Yes: for this class of item, the Geo agent’s job is to wire **places** to persons and events, not to reify the “settlement” itself as a Place.

## What the Geo agent should do here

Given Q122918768 (Pompey’s eastern settlement), the Geo agent sees:

- An **event** (government reorganization) with locations: Asia, Bithynia et Pontus, Cilicia, Roman Syria. [en.wikipedia](https://en.wikipedia.org/wiki/Pompey's_eastern_settlement)
- An **agent**: Pompey, plus a country: Roman Republic. [en.wikipedia](https://en.wikipedia.org/wiki/Pompey's_eastern_settlement)

The Geo agent should:

- Ensure each listed region is present as a **Place** node with proper hierarchy (province → larger region, etc.).  
- Create or confirm edges:
  - Place ↔ Event: each province is `LOCATED_IN_EVENT` / `OCCURRED_IN` for this settlement.  
  - Place ↔ Person: Pompey as `AGENT_OF_ACTION` acting in those places; optionally later persons (governors, client kings) if other data supplies them.  
  - Place ↔ Place: maintain spatial relationships (e.g., Bithynia et Pontus is in Asia Minor; Syria in the Levant).

## What it should not do

- It should **not** create a Place node called “Pompey’s eastern settlement”.  
- It should leave the **event modeling** (creating an Event node, time span, political facet, etc.) to your Event/Political SFA and just cooperate by supplying the place nodes and their spatial context.

So yes: the Geo agent’s role here is basically to be a **place–centric router**, mapping provinces and regions to the persons and events that touch them, while other agents own the semantics of the event itself. Is that the behavior you want globally for all “X’s settlement/treaty” type items, or only when `instance of` is clearly non-geographic?

---

**Cursor**

Use `instance_of` as the main signal, not the label.

## Recommended rule

**Use `instance_of` (and `subclass_of`) as the primary discriminator.**

| instance_of suggests | Geo Agent behavior |
|---------------------|---------------------|
| **Event/process** (government reorganization, treaty, battle, coup, political event, etc.) | Event. Ensure P276 targets are Place nodes; emit ATTACH_EVENT_TO_PLACE. Do not create a Place for the item. |
| **Place** (ancient city, colony, archaeological site, Roman province, etc.) | Place. Emit CREATE_OR_ENRICH_PLACE. |
| **Ambiguous** | LLM uses context (label, P276, other properties). |

## Why not rely on labels like "settlement" or "treaty"

- **"Settlement"** can mean:
  - Political event (Pompey’s eastern settlement) → event
  - Physical place (Roman settlement at X = colony/archaeological site) → place
- **"Treaty"** is usually an event, but labels alone can be misleading.
- `instance_of` is more reliable: government reorganization, treaty, battle, etc. vs. ancient city, colony, province.

## Summary

Apply the place-centric router behavior whenever `instance_of` clearly indicates an event or process, regardless of label. When `instance_of` is place-like, treat it as a place. When it’s ambiguous, let the LLM use the rest of the context.

---

**User**

yes

---

**Cursor**

Updates are in place in both `geo_agent_classify.py` and `md/Agents/geo_agent_classification_prompt.md`:

**Changes:**
- **Place-centric router** — Geo Agent wires places to persons and events; it does not create Places for events.
- **Primary signal** — `instance_of` / `subclass_of` decide Place vs Event.
- **"Settlement" disambiguation** — Political acts (e.g. Pompey’s eastern settlement) vs physical sites (e.g. Roman settlement at X); `instance_of` resolves this.
- **Q122918768 example** — Government reorganization with P276 locations; emit ATTACH_EVENT_TO_PLACE for each province; do not create a Place for the event.
- **Treaties** — Included in the event types list.

---

**User**

hmm what if this was actually the SCA - it harvests the all the wikidata props and external ids for the given qid - in this case roman republic, it ties into the subject backbone (lcc lcsh etc) then then goes thru the props and the backlinks and does this by logic. meaning with 18 dimenstions we have how many possible combos do we have

---

**Cursor**

## SCA reframing

**SCA as central harvester:**
1. Harvest all Wikidata props and external IDs for the seed QID (e.g. Q17167).
2. Tie into the subject backbone (LCC, LCSH, FAST).
3. Walk props and backlinks and apply logic (place vs event, facet assignment, etc.).
4. Route to facet agents (including Geo) instead of having Geo do its own discovery.

## 18 dimensions → combinatorics

**18 facets** (from `facet_registry_master.json`):
ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, CULTURAL, DEMOGRAPHIC, DIPLOMATIC, ECONOMIC, ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC, MILITARY, POLITICAL, RELIGIOUS, SCIENTIFIC, SOCIAL, TECHNOLOGICAL, COMMUNICATION

**Possible facet combinations per entity:**

| Interpretation | Formula | Count |
|----------------|---------|-------|
| Any subset of facets | 2^18 | **262,144** |
| Primary facet only | 18 | 18 |
| Primary + up to k related | 18 × Σ C(17,k) for k=0..5 | ~1.2M (if k=5) |
| At least one facet | 2^18 − 1 | 262,143 |

So the full space is **2^18 = 262,144** possible facet subsets per entity.

**In practice:**
- Most entities get 1 primary facet and 0–5 related facets.
- Property→facet mapping (e.g. `property_facet_mapping_COMPLETE.csv`) constrains this.
- Logic (instance_of, P276, etc.) drives classification instead of enumerating all combos.

**Implication:** The SCA would use property mappings and instance_of-style rules to assign a small subset of facets per entity, not to explore all 262k combinations.

---

**User**

i suggest that rather than have 18 sfas do what we just did for geo, one agent could do this by facet

---

**Cursor**

## One agent, facet-aware

**Current (18 separate SFAs):**
- Geo Agent: discovery → geo filter → classify → deltas
- Military SFA: its own discovery, filter, classify
- Political SFA: its own discovery, filter, classify
- … × 18

**Proposed (one SCA, facet-aware):**
- **Single harvest:** Wikidata props, external IDs, backlinks for the seed (e.g. Q17167)
- **Single classification pass:** For each candidate, apply logic for all 18 facets
- **Per-facet output:** One structured result with facet-specific deltas

```
Harvest (once) → Classify by facet (once) → Route deltas to facet handlers
```

**Benefits:**
- One Wikidata harvest instead of 18
- Cross-facet reasoning in one pass (e.g. “government reorganization” → Political + Geographic + Legal)
- Shared context (instance_of, P276, P17, etc.) for all facets
- One prompt/schema to maintain, with facet-specific rules

**Output shape:**
```json
{
  "qid": "Q122918768",
  "label": "Pompey's eastern settlement",
  "facets": {
    "geographic": { "classification": "event", "deltas": [ATTACH_EVENT_TO_PLACE × 4] },
    "political": { "classification": "event", "deltas": [...] },
    "legal": { "classification": "event", "deltas": [...] }
  }
}
```

**Implication:** The Geo Agent becomes a facet-specific slice of this unified SCA, not a separate pipeline. The same harvest feeds all facets; the SCA’s logic decides what each facet does with each entity.

---

**User**

yes so lets have a new term Domain Initiator - DI. given a qid represented by a domain, the di tethers the domain to the lcc, lcsh etc backbone tand then does this. the sca is still needed to coordinate sfas

---

**Cursor**

Documenting the Domain Initiator (DI) and its role in the architecture:


Changes made:

## Created: `docs/DOMAIN_INITIATOR.md`

**Domain Initiator (DI)** — Given a domain QID:
1. **Tethers** the domain to LCC, LCSH, FAST
2. **Harvests** Wikidata props, external IDs, backlinks
3. **Classifies** each candidate by facet (all 18) in one pass
4. **Outputs** per-facet deltas for the SCA to route

**Architecture:**
```
Domain (QID) → DI (harvest + tether + classify) → SCA (coordinates SFAs) → SFAs (facet specialists)
```

**Division of labor:**
| | DI | SCA | SFA |
|---|-----|-----|-----|
| **Role** | Domain entry, harvest, backbone tether, facet classification | Orchestrates SFAs, routes deltas | Facet specialist |

## Updated

- **`docs/AGENT_HANDOFF_2026-03-06.md`** — Added DOMAIN_INITIATOR.md to Important Docs
- **`docs/SCA_SFA_CONTRACT.md`** — Added note that the DI feeds the SCA

---

**User**

also di should examine the props of the qid for harvesting, as well as the props and qids of the backlinks and also the external ids - since the backlinks may have federation ids and lcsh, fast dewey links. the di needs to find the most granular subject from the subject backbone

---

**Cursor**

Updated `docs/DOMAIN_INITIATOR.md` with:

**Harvest scope**
- **Seed QID:** Props, external IDs (Pleiades, GeoNames, VIAF, etc.), LCSH/FAST/Dewey when present
- **Backlinks:** Props and QIDs, external IDs, federation IDs, LCSH (P244), FAST (P2163), Dewey (P1036)
- **Subject backbone:** Use harvested links to choose the most granular subject

**Flow**
1. Harvest seed props + external IDs; backlink props + QIDs + external IDs (Pleiades, GeoNames, LCSH, FAST, Dewey)
2. Resolve to the most granular subject in the backbone (LCC/LCSH/FAST)
3. Tether the domain to that subject
4. Classify by facet (18 facets, one pass)
5. Output per-facet deltas

**Note:** Backlinks can carry federation IDs and subject-backbone links that the seed lacks; the DI aggregates these to find the finest-grained subject for the domain.

---

**User**

yes write it. remember never pass pid qid without labels

---

**Cursor**

Summary of what was added:

## Domain Initiator harvest

**`scripts/agents/domain_initiator/harvest.py`**

**Rule:** Every PID and QID is paired with a label. No bare IDs in the output.

**Harvest scope:**
- **Seed:** All properties and external IDs (Pleiades, GeoNames, FAST, Dewey, LCNAF, VIAF, GND)
- **Backlinks:** Properties and QIDs for each backlink, plus external IDs
- **Subject backbone links:** FAST (P2163), Dewey (P1036), LCNAF (P244) from seed and backlinks

**Output:** `output/di_harvest/Q17167_di_harvest.json`

```json
{
  "seed": {
    "qid": "Q17167",
    "label": "Roman Republic",
    "properties": [
      { "pid": "P31", "label": "instance of", "value_qid": "Q11514315", "value_label": "historical period" },
      ...
    ],
    "external_ids": [...]
  },
  "backlinks": [
    {
      "qid": "Q122918768",
      "label": "Pompey's eastern settlement",
      "properties": [...],
      "external_ids": [...]
    }
  ],
  "subject_backbone_links": {
    "fast": [],
    "dewey": [{"qid": "Q124988", "label": "Punic Wars", "dewey_id": "937.04"}],
    "lcnaf": [{"qid": "Q17167", "label": "Roman Republic", "lcnaf_id": "sh85115114"}]
  },
  "property_registry": [{"pid": "P31", "label": "instance of"}, ...]
}
```

**Usage:**
```bash
python scripts/agents/domain_initiator/harvest.py --seed Q17167
```

**Also added:** `scripts/agents/domain_initiator/README.md`, `__init__.py`, and updates to `docs/DOMAIN_INITIATOR.md` and `docs/AGENT_HANDOFF_2026-03-06.md`.

---

**User**

but it not recommend an action like the others did

---

**Cursor**

Adding a `recommended_actions` section to the DI harvest output.


The DI harvest output now includes recommended actions.

**Top-level `recommended_next_steps`:**
```json
[
  {
    "action": "DI_CLASSIFY",
    "reason": "Run LLM classification for all 18 facets",
    "hint": "Consume this harvest; output per-facet deltas for SCA routing"
  },
  {
    "action": "RESOLVE_SUBJECT",
    "reason": "Harvest contains FAST/Dewey/LCNAF links",
    "hint": "Resolve to most granular subject in LCC/LCSH/FAST backbone; tether domain"
  },
  {
    "action": "GEO_FACET",
    "reason": "13 backlinks have geo properties",
    "hint": "Run Geo Agent classify on geo-filtered subset, or consume via DI classify"
  }
]
```

**Per-backlink `recommended_actions`** (when applicable):
- **RESOLVE_SUBJECT** — when the entity has FAST, Dewey, or LCNAF
- **GEO_FACET** — when the entity has geo properties (P625, P276, P131, P1584, P1566, etc.), with hints like "Pleiades ID → consider CREATE_OR_ENRICH_PLACE"

---

**User**

not understanding. 

---

**Cursor**

What needs clarification? For example:

1. **What the recommended actions are for** — how they’re used in the pipeline
2. **How the DI harvest relates to the Geo Agent** — how they fit together
3. **The overall flow** — DI harvest → DI classify → SCA → SFAs
4. **Something in the JSON output** — structure or meaning of a field
5. **Something else** — describe what’s unclear

If you can point to the part that’s confusing (e.g. “the recommended_actions per backlink” or “why we have both recommended_next_steps and recommended_actions”), I can explain that specifically.

---

**User**

i expected output to be like @output/geo_discovery \ json. this is just a list of properties

---

**Cursor**

Restructuring the DI harvest to match the geo_candidates format: candidates with `instance_of`, `subclass_of`, and `geo_properties` instead of a flat `properties` list.


The DI harvest output is now aligned with the geo_candidates format:

**Structure (matches geo_candidates):**
```json
{
  "seed": { "qid": "Q17167", "label": "Roman Republic" },
  "backlinks_total": 32,
  "candidates_count": 32,
  "candidates": [
    {
      "qid": "Q1228632",
      "label": "victoriatus",
      "instance_of": [{ "qid": "Q8142", "label": "currency" }, ...],
      "subclass_of": [],
      "geo_properties": [
        { "pid": "P17", "label": "country", "value_qid": "Q17167", "value_label": "Roman Republic" }
      ],
      "external_ids": [],
      "recommended_actions": [...]
    }
  ],
  "subject_backbone_links": { "fast": [], "dewey": [...], "lcnaf": [...] },
  "recommended_next_steps": [...]
}
```

**Differences from geo_candidates:**
- **geo_candidates:** Only items with geo properties (P625, P276, P131, P3896, P1584, P1566; P17 alone excluded) → 27 candidates.
- **DI harvest:** All backlinks → 32+ candidates, each with `instance_of`, `subclass_of`, `geo_properties`, plus `external_ids` and `recommended_actions`.

The flat `properties` list is removed; each candidate uses the same structured fields as geo_candidates.

