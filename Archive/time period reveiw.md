<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# suddenly cursor agent doesnt work - it says planning next moves then moves the input back into the input box

This is a known Cursor bug where the Agent gets stuck on “Planning next moves” or immediately bounces your text back into the input instead of executing.[^1_1][^1_2][^1_3]

## Quick checks

Try these in order (they’re reversible and fast):

1. **Check if it’s workspace-specific**
    - Close Cursor completely.
    - Reopen it *without* opening a project (empty window) and start a simple Agent/Ask chat like “2+2”.[^1_3]
    - If that works, the issue is most likely with the current repo’s index or project state.[^1_4][^1_3]
2. **Restart Cursor fully**
    - Fully quit (not just close the window).
    - On macOS: Cursor → Quit Cursor.
    - Reopen and try a new Agent tab. Users report this sometimes fixes it for a few runs.[^1_1]
3. **Try a different mode/model**
    - Switch between Ask / Agent / Plan and try a trivial prompt.[^1_2][^1_5]
    - Try another model (e.g., if you’re on Auto, switch to a specific Claude/OpenAI model) to see if *all* are affected.[^1_6][^1_5]

## Deeper fixes

If it’s still happening:

1. **Disable extensions / plugins**
Some reports show extensions causing infinite “Planning next moves”.[^1_7]
    - Close Cursor.
    - From a terminal, run:
        - `cursor --disable-extensions`
    - Then try the Agent again in that clean session.[^1_7]
2. **Check for network/connection issues**
    - In Cursor, open Diagnostics (Command Palette → search “diagnostics”) and see if it reports network problems.[^1_5][^1_8]
    - If diagnostics show repeated timeouts, the Agent may silently hang at “Planning next moves”.
3. **Project/index issues**
    - If an empty window works but your project doesn’t, the repo’s index may be corrupted.[^1_4][^1_3]
    - Try:
        - Open a *different* small test project and use the Agent.
        - If that works, consider clearing/rebuilding the index for the original workspace (Cursor docs/forum threads suggest this for similar “stuck planning” issues).

## When it just returns text to the box

The specific behavior “type message, press Enter, and it just moves the cursor back into the input with no response” matches a bug report where Agent/Ask/Plan all fail to fire the request.  In that thread, the resolution was tied to a Cursor update plus the same steps above (restart, test empty window, disable extensions).[^1_2][^1_3]

## If it still fails

If none of this works:

- Capture:
    - Cursor version (e.g., 2.x.y).
    - OS (macOS/Windows/Linux).
    - Whether an empty-window chat works.
- Post it on the Cursor forum under Bug Reports; there are active threads for “Planning next moves stuck” and “Agent not working” where Cursor staff are collecting these details.[^1_3][^1_1][^1_2]

If you tell what OS you’re on and whether the Agent works in an empty window or another repo, a more targeted next step (like exactly what to delete/reset) can be suggested.
<span style="display:none">[^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://forum.cursor.com/t/planning-next-moves-stuck/143985

[^1_2]: https://forum.cursor.com/t/the-agent-is-not-working/145743

[^1_3]: https://forum.cursor.com/t/stuck-in-planning-next-move/148585

[^1_4]: https://www.reddit.com/r/cursor/comments/1pisssv/stuck_at_planning_next_moves/

[^1_5]: https://forum.cursor.com/t/slow-or-no-response-from-the-agent/143963

[^1_6]: https://forum.cursor.com/t/planning-next-moves-stuck/143985?page=5

[^1_7]: https://forum.cursor.com/t/planning-next-moves-stuck/143985?page=4

[^1_8]: https://forum.cursor.com/t/persistent-connection-issues-causing-cursor-to-be-unworkable/147617

[^1_9]: https://www.youtube.com/watch?v=1sZkTeXxADs

[^1_10]: https://forum.cursor.com/t/difficult-to-know-when-agent-llm-are-done-working-on-prompt/129431

[^1_11]: https://forum.cursor.com/t/hook-ask-output-not-stopping-agent/149002

[^1_12]: https://forum.cursor.com/t/cursor-not-responding-on-agent-mode/138996

[^1_13]: https://forum.cursor.com/t/agent-terminal-not-working/145338

[^1_14]: https://www.reddit.com/r/cursor/comments/1orun7d/here_is_a_solution_to_the_common_windows_issue_of/

[^1_15]: https://forum.cursor.com/t/auto-model-misidentifies-ask-vs-agent-mode-and-attempts-write-actions-in-ask-mode/147013


---

# Review of `time_periods.csv` for Global Historical Time Periods

## 1. High‑level assessment

The file is a **strong starting point for a knowledge-graph-style catalog of named historical periods**, but it is **not yet “comprehensive”** as a global framework, especially if the goal is:

- global coverage across all major world regions, and
- systematic coverage across multiple “facets” (cultural, political, archaeological, artistic, etc.),
- suitable for consistent world-building or a web app timeline.

You have good raw material drawn from Wikidata, but there are structural issues (granularity, overlap, facet model, region bias, and CSV encoding of arrays) that you’ll want to address if you want this to be a canonical backbone for a world-simulation or historical UI.

Below is a structured review.

***

## 2. What the dataset currently does well

### 2.1 Schema and structure

Each row has:

- `QID`: a stable Wikidata identifier.
- `Label`: human-readable name of the period.
- `Start`, `End`: numeric years, with negatives for BCE.
- Spatial context:
    - `LocationCount`
    - `Locations`: list of Wikidata entities (regions, states, cities) encoded as a stringified array.
- Conceptual context:
    - `Facets` (e.g., `CulturalFacet`, `PoliticalFacet`, `ArtisticFacet`, `ArchaeologicalFacet`),
    - `FacetRelationships` (e.g., `HAS_CULTURAL_FACET`).

Strengths:

- **Directly linkable** to Wikidata for richer metadata or multilingual labels.
- **Facet field** already distinguishes different types of periods (political vs cultural vs artistic).
- **Location links** let you filter or visualize by region or locality.

For a web-based app, this is a solid foundation for:

- filtering timelines (by region, facet),
- linking out to richer entity data,
- potentially integrating with other datasets.


### 2.2 Temporal coverage

From the sample:

- Earliest: `pre-Columbian era` starting at about `-48000`.
- Long tail into 21st century: entries up to 2017–2021.

Coverage includes:

- Deep prehistory (on at least one axis: pre-Columbian Americas).
- Bronze/Iron Age and early complex societies (Proto-Elamite, Helladic, Minoan, Early Dynastic Egypt, Ur III, Iron Age India, Ancient China).
- Major “classical” periods (Classical Greece, Roman Kingdom, Second Temple period, Classical antiquity).
- Medieval Europe and derivatives (Migration Period, Middle Ages, Early/High/Late Middle Ages, Viking Age, Burgundian Netherlands, Carolingian/Reginarid/Brussels variants).
- Early modern \& modern (Renaissance variants, Ottoman Palestine/Syria, Scientific Revolution, Dutch Golden Age, Baroque, High Renaissance, various local “Golden Ages”).
- Contemporary periods (Cold War, American Century, Years of Lead, Rehnquist Court, Soviet era, History of Crimea 1991–2014, etc.).

So **chronological coverage is broad**. You can track periods from deep prehistory to contemporary politics.

***

## 3. Where the dataset falls short for “comprehensive global” coverage

### 3.1 Geographic balance and globality

From the rows visible, coverage is **heavily skewed toward**:

- Europe (Brussels, Italy, Netherlands, London, Abkhazia, etc.).
- The broader Middle East and Mediterranean (Egypt, Palestine, Syria, Ottoman Empire).
- East Asia (China, Korea, some Japan/Okinawa periods).
- South Asia (e.g., Iron Age India, Medieval India).
- North America and Latin America are present, but more sporadically (pre-Columbian era, Woodland period, Antebellum South, Platine Wars, etc.).

Underrepresented or missing in the sample:

- **Sub-Saharan Africa** beyond isolated political entities; very little systematic periodization (e.g., Sahelian empires, Swahili coast periods, precolonial West African trading eras).
- **Central Asia and Inner Asia** outside of big empires; few local periodizations.
- **Pacific and Oceania** (Polynesian, Micronesian, Melanesian cultural-historical periods) are mostly absent.
- **Indigenous Americas** beyond high-level “pre-Columbian” or a few specific cultures (e.g., Sican).

As a result, if your goal is a **global timeline where every major region has equivalent resolution**, this dataset is not yet there. It reflects **where Wikidata’s periodization is better curated**, not a deliberately balanced global design.

### 3.2 Facet coverage

Current facets include:

- `CulturalFacet`
- `ArchaeologicalFacet`
- `ArtisticFacet`
- `PoliticalFacet`

These cover a lot, but for “comprehensive facets” in historical world-building, you likely also want:

- **Economic / Technological**: e.g., Industrial Revolution, post-industrial era, Age of Sail, Age of Steam, Information Age, Digital Revolution, Green Revolution, etc.
- **Scientific / Intellectual**: e.g., Enlightenment, Romanticism, Age of Reason, modernism, postmodernism, etc. (some are present but labeled mostly as cultural/artistic).
- **Religious**: e.g., Axial Age, Reformation, Counter-Reformation, various regional religious revivals or dominances.
- **Military / Geopolitical**: beyond Cold War and “European Civil War” style terms, you might want eras like “Pax Mongolica,” “Pax Britannica,” etc.
- **Environmental / Climatic**: e.g., Little Ice Age, Holocene climatic optima, Dust Bowl, etc., if environment matters in your worlds.

Right now, many such eras are either missing or represented only as generic `CulturalFacet`, which **flattens important differences in how the period functions** in a simulation or narrative.

### 3.3 Granularity and overlap

A major structural issue is **heterogeneous granularity**:

- Very broad eras:
    - `pre-Columbian era` (-48000 to 1492),
    - `Middle Ages` (476–1500),
    - `American Century` (1898–2000),
    - `Cold War` (1945–1991),
    - etc.
- Nested regional eras:
    - `Early Middle Ages`, `High Middle Ages`, `Late Middle Ages`,
    - `Early Middle Ages in the Iberian Peninsula`,
    - `Medieval India`,
    - various Brussels-specific periods (Merovingian, Carolingian, Burgundian, Habsburg, Dutch, French, etc.).
- Highly local/micro periods:
    - `Boldino autumn` (1830),
    - `Black Week` (1899–1899),
    - `Reign of Terror` (1793–1794),
    - `Thermidorian Reaction` (1794–1795),
    - `Maximato`, `Pre-Code Hollywood`, particular mayoralties.

This is fine if your usage is **“show all known named periods for a given place”**, but it is **problematic if you want a readable, canonical global periodization** because:

- Overlapping periods of different sizes make it difficult to derive a single “current period” for any given year/location.
- The relative importance of periods varies wildly (global Cold War vs. one city’s mayor).
- Some intervals are oversaturated (e.g., Europe 1500–1950) while others are sparse.

A typical user-facing timeline or simulation wants:

- a **coarse-grained, hierarchical “spine”** (e.g., Prehistory → Ancient → Classical → Post-Classical → Early Modern → Modern → Contemporary),
- with **nested region-specific layers** and **facet-specific overlays**.
Your dataset contains the nested detail, but you still need to **design the spine and hierarchy**.


### 3.4 Data noise / definitional quality

Because this is drawn from Wikidata:

- Some time spans look **historically debatable or simply wrong** (e.g., Phoney War given as 1939–1958; historically it’s mostly 1939–1940).
- Some items like `Q123385052`, `Q127237209`, `Q120239797` are anonymous QIDs with minimal or obscure labels — not great for UI or worldbuilding unless you selectively curate them.
- Some periods are more like **archival coverage windows** (e.g., “The Alfred Nobel Family Archives 1868–1905”) than actual historical periods.

In other words, **raw Wikidata is noisy** for your likely use-case. You will need **post-processing and curation**, not just ingestion.

***

## 4. Verdict on quality and completeness

### 4.1 Quality

**Quality is good as an integration of Wikidata entities**, but not yet good enough as:

- a curated canonical list of periods for storytelling or simulation,
- a pedagogical world-history schema.

Issues to address:

- Normalizing and validating start/end years for major canonical periods.
- Filtering out niche or archival-only “periods” that clutter the space.
- Consolidating or annotating overlapping periods and nested hierarchies.


### 4.2 Completeness

For **“comprehensive global historical time periods across facets”**, this is **incomplete** because:

- Global geographic coverage is uneven; many major regions and civilizations are underrepresented or missing suitable local periodizations.
- Key facets (economic, technological, scientific, religious, environmental) are either absent or implicitly folded into `CulturalFacet`.
- Periods are not organized into a clear **hierarchy** (global → regional → local) and **facet-specific lenses**.

Treat this dataset as:

- a **rich pool of known named periods**, not as the finished model.
- a **backbone for further curation** and ontology-building.

***

## 5. Concrete recommendations to improve it

### 5.1 Strengthen the schema

For use in a web app / world-building engine, consider:

1. **Break arrays into normalized tables**

```
- Instead of CSV fields like `"[<uri1>, <uri2>]"`, create:
```

    - `time_periods` (QID, label, start, end, etc.)
    - `time_period_locations` (QID, location_QID)
    - `time_period_facets` (QID, facet_type, relationship_type)
    - This will make querying/filtering much easier.
2. **Add hierarchy fields**
    - Example columns:
        - `global_era` (e.g., “Ancient”, “Medieval”, “Early Modern”, “Modern”, “Contemporary”),
        - `region_family` (e.g., “Europe”, “East Asia”, “Sub-Saharan Africa”),
        - `importance_rank` (e.g., 1 = global canonical, 2 = major regional, 3 = local/specialized).
    - You can derive these partially algorithmically (by location + time) and refine manually.
3. **Expand `Facet` taxonomy**
    - Add new facet values: `EconomicFacet`, `TechnologicalFacet`, `ScientificFacet`, `ReligiousFacet`, `EnvironmentalFacet`, `MilitaryFacet`.
    - For existing rows, you can:
        - auto-infer some based on label/patterns (e.g., “Scientific Revolution” → `ScientificFacet`),
        - then hand-tune.

### 5.2 Design a canonical periodization “spine”

Define a **top-level, relatively small set of global eras**:

- Prehistory (to ~3000 BCE),
- Ancient / Bronze Age (3000–500 BCE),
- Classical (500 BCE–500 CE),
- Post-Classical / Medieval (500–1500),
- Early Modern (1500–1800),
- Long 19th century (c. 1789–1914),
- Short 20th century (1914–1991),
- Contemporary (1991–present).

Then, for each region:

- Choose key regional periodizations that map nicely into these bands (e.g., Three Kingdoms, Heian, Edo; Gupta, Mughal; Abbasid, Ottoman; etc.).
- Attach each row to one or more of these canonical bands.

Your current rows can be aligned to this spine and nested inside it, but you may need to:

- add **missing canonical entries** for regions/facets that are currently thin,
- demote highly local or questionable entries (importance_rank 3) so they don’t dominate.


### 5.3 Fill obvious gaps

For a “creator of worlds” toolkit, you probably want to explicitly add:

- **Global technological/economic eras**:
    - Agricultural Revolution, Bronze Age, Iron Age (globally normalized),
    - Commercial Revolution, Age of Discovery, Age of Sail,
    - Industrial Revolution(s), Second Industrial Revolution,
    - Age of Oil, Information Age, Digital Age, etc.
- **Major world religions / intellectual eras**:
    - Axial Age,
    - spread and regional dominance of Buddhism, Christianity, Islam, Hindu reform periods,
    - Reformation, Counter‑Reformation, Enlightenment, Romanticism, modernism, etc.
- **Environmental eras** (if relevant):
    - Little Ice Age,
    - Anthropocene (if you want to include the concept),
    - major drought/plague eras (e.g., Black Death) as cross-cutting events/periods.

Many of these may exist in Wikidata but not be in your subset; you may want a **second pass query** specifically targeting these canonical categories and then merging.

### 5.4 Curate and clean

Steps that will raise the “quality” dramatically:

- **Whitelist**: create a manually curated list of “canonical” periods by region/facet that you want to expose prominently.
- **Blacklist or down-rank**:
    - archival windows, single-year micro-periods unless they’re truly central,
    - obscure QIDs with no clear narrative importance.
- **Correct or bound-check** weird start/end years against external references for the top ~200 most important periods.

***

## 6. Summary

- The dataset is **rich and promising** as a raw inventory of named periods linked to Wikidata, with useful facet and location metadata.
- It is **not yet a balanced, comprehensive, global schema** of historical time periods across all relevant facets.
- With **normalization, hierarchy design, facet expansion, and selective curation**, it can become an excellent backbone for a world-building or historical web app.

If you share your intended usage pattern (e.g., “I want a scrollable global timeline with filters for culture/politics/tech” vs “I want to power a simulation engine that needs a single active period per region-year”), a more concrete refinement strategy (including candidate schema and ranking heuristics) can be sketched out.
<span style="display:none">[^2_1]</span>

<div align="center">⁂</div>

[^2_1]: time_periods.csv


---

# this sits on top of a neoj year by year time line 2000 bce until today. we have those other facets but the llm did not return any periods with those facets - perhaps it is wrong. yes a scrollable timeline is good, but the primary ui is a react cytospace graph traversal view. the issue is it is hard to find online relatively clean data

Great—now I see the real problem. The issue isn't the timeline structure; it's that **LLM facet extraction from Wikidata/Wikipedia is unreliable**, especially for economic, technological, scientific, and environmental facets that don't exist as explicit Wikidata predicates.

## The Core Problem: Why LLM Extraction Fails

Wikidata doesn't have dedicated properties for many "facet" types. For example:

- **No "technologicalFacet" property** linking periods to technological innovations.
- **No "economicFacet"** linking to economic systems or revolutions.
- **No "scientificFacet"** linking to intellectual movements.

The LLM is asked to infer these from:

- Labels and descriptions (which are often sparse or ambiguous),
- Wikipedia article text (which is noisy),
- Weak signals from related entities.

Result: it mostly defaults to `CulturalFacet` or `ArchaeologicalFacet` because those are safe bets visible in the data.

***

## Practical Solutions for Your Neo4j + Cytoscape Setup

### 1. **Explicit Curated Mapping Table (Quick Win)**

Create a **secondary CSV or JSON file** that hardcodes known periods + their facets. This bypasses LLM extraction:

```csv
wikidata_qid,label,start,end,tech_facet,econ_facet,sci_facet,relig_facet,env_facet
Q2996050,Industrial Revolution,1760,1840,steam machinery & coal,shift to factories,scientific method advances,secularization,pollution & urbanization
Q12554,Middle Ages,476,1500,feudal agriculture,feudal economy,scholasticism,Christian dominance,land-based
Q185047,Spring and Autumn period,-770,-475,iron tools,warring states trade,early philosophy,ancestor veneration,deforestation
... (continue for canonical global periods)
```

Then in Neo4j:

- **Main graph nodes**: 2000 BCE to today year-by-year timeline (coarse backbone).
- **Period nodes**: periods from your CSV, tagged with all facets upfront.
- **Relationship**: `YEAR_IN_PERIOD` or similar.

**Advantage**: Fast to build, deterministic, good for Cytoscape traversal (users click a period, see all years inside it).

**Drawback**: Manual curation. Doesn't scale to 500+ periods automatically.

***

### 2. **Hybrid: LLM + Structured Validation**

Instead of relying on LLM to extract facets from Wikidata raw text, **feed it a structured template**:

```json
{
  "qid": "Q2996050",
  "label": "Industrial Revolution",
  "start": 1760,
  "end": 1840,
  "wikidata_desc": "period of human history marked by transition from agrarian economies to industrial ones...",
  "canonical_tags": ["manufacturing", "steam power", "textile production", "coal mining"],
  "question_for_llm": "Given the above tags and description, classify this period's facets as: (1) TechnologicalFacet if machinery/energy advances, (2) EconomicFacet if production/trade systems shift, (3) ScientificFacet if intellectual breakthroughs, etc. Provide confidence scores (0-1) for each."
}
```

Then:

- **LLM returns**:

```json
{
  "TechnologicalFacet": 0.95,
  "EconomicFacet": 0.98,
  "ScientificFacet": 0.70,
  "ArchaeologicalFacet": 0.10
}
```

- **Threshold filter**: only facets with score > 0.6 are added.
- **Store results in Neo4j** with confidence scores as edge weights.

**Advantage**: Semi-automated, structured, you get confidence metrics for Cytoscape (could color edges by confidence).

**Drawback**: Still requires you to create the `canonical_tags` mapping upfront. But fewer manual rows than full curation.

***

### 3. **Best Source: Histropedia + DBpedia Events**

The search results show some prior work:

- **Histropedia** () generates timelines from Wikipedia/Wikidata automatically. Check if they expose their periodization or events layer.[^3_1]
- **Wikipedia "Year" articles** (): Wikipedia pages like `https://en.wikipedia.org/wiki/2000_BCE` have curated, categorized events under headings like "Politics", "Science", "Culture", "Economy". These are **pre-classified by humans** and relatively clean.[^3_2]
- **DBpedia extraction**: The arXiv paper  describes extracting events from Wikipedia years and linking to DBpedia entities. They extracted **~121k events** with language support.[^3_2]

**Recommendation**:

- Instead of pulling generic "periods" from Wikidata, query **Wikipedia year articles directly** (2000 BCE – today) and parse the category headings.
- For each year, extract events under "Science", "Economy", "Technology", "Religion", "War/Politics", "Culture", "Art".
- Aggregate these by decade/century to create **facet-weighted periods**.
- Load into Neo4j as event nodes linked to years, periods become aggregate nodes over events.

***

### 4. **Academic Periodization Spine** (, )[^3_3][^3_4]

For your Neo4j backbone, use a **standard scholarly periodization** as the canonical spine:

From UCLA/NCHS standards:

```
Era 1: Prehistory & Early Civilizations (–3000 BCE)
Era 2: Ancient (3000 BCE – 500 CE)
  - Sub: Classical Antiquity (500 BCE – 500 CE)
Era 3: Post-Classical / Medieval (500 – 1500)
  - Sub: Early Medieval, High Medieval, Late Medieval
Era 4: Early Modern (1450 – 1800)
Era 5: Long 19th Century (1789 – 1914)
Era 6: 20th Century Crisis (1900 – 1945)
Era 7: Cold War & Decolonization (1945 – 1989)
Era 8: Contemporary Global (1989 – present)
```

Then:

- **Each era is a period node in Neo4j.**
- **Wikidata periods (your CSV) nest inside these** (regional/facet-specific sub-periods).
- **Years link to eras + candidate sub-periods** (a year can be in multiple sub-periods).

For Cytoscape:

- Start at top level (8 eras).
- Drill down to see regional sub-periods.
- Further drill to see years and events.

***

## Concrete Action Plan for Your Neo4j Graph

1. **Create a "canonical periods" table** (manually curated, ~50–100 global/regional top-level entries):

```csv
qid,label,start,end,global_era,region_family,facet_list,importance
Q2996050,Industrial Revolution,1760,1840,Early Modern,Europe,TechnologicalFacet;EconomicFacet;ScientificFacet,1
Q63226529,Early Middle Ages Iberia,500,1100,Post-Classical,Iberia,CulturalFacet;PoliticalFacet,2
Q185047,Spring and Autumn,-770,-475,Post-Classical,East Asia,PoliticalFacet;CulturalFacet,2
...
```

2. **LLM post-processing** (for Wikidata periods you already have):
    - Feed each period's label + description to an LLM with **structured facet instructions**.
    - Ask it to pick facets with confidence, threshold at 0.5–0.6.
    - Store confidence scores in Neo4j edge properties.
3. **Enrich from Wikipedia year articles**:
    - Parse `https://en.wikipedia.org/wiki/[YEAR]` for major events.
    - Extract category tags (Politics, Science, Economy, Technology, Culture, Religion).
    - Create event nodes in Neo4j, link to years.
    - Aggregate events to infer which facets "light up" in a given year.
4. **Cytoscape Visualization**:
    - **Nodes**: Years (or year-clusters), Periods, Eras, Events.
    - **Edges**:
        - `CONTAINS` (era → period → year).
        - `EVENT_IN` (event → year).
        - `FACET_ACTIVE` (edge with facet type + confidence weight as width/color).
    - **Graph traversal query**: Given a year, show:
        - The era + periods it belongs to (upward).
        - Events in that year + their facets (inward neighbors).
        - Neighboring years + shared periods (lateral).

***

## Why "Clean Data Online" Is Hard

surveyed 50 DH projects using Wikidata. Conclusion: **Wikidata is "content provider, platform, and infrastructure,"** but projects always need significant **domain-specific post-processing**:[^3_5]

- Wikidata has incomplete property coverage (facets like "technological revolution" aren't first-class predicates).
- Wikipedia's structure (year articles with human-curated event lists) is more reliable **for events**, but less linked.
- Academic sources (UCLA standards, Korotayev/Grinin work ) provide **normative periodizations**, but they're scattered.[^3_4]

**Bottom line**: There's no single "clean global historical periods + facets" dataset online. You're building a reasonable proxy by:

1. Starting with Wikidata periods + canonical spine.
2. Layering Wikipedia events + categorical extraction.
3. Applying manual or LLM-assisted facet tagging with validation.

***

## Immediate Quick Win

If you want facets populated **right now** without manual curation:

**Use a hand-built lookup table keyed by period label patterns**:

```python
# Python/Node.js pseudo-code
facet_patterns = {
  r"(revolution|industrial|technological)": ["TechnologicalFacet", "EconomicFacet"],
  r"(renaissance|enlightenment|romanticism)": ["ScientificFacet", "CulturalFacet"],
  r"(reformation|counter-reformation)": ["ReligiousFacet", "CulturalFacet"],
  r"(reformation|religious|jihad|crusade)": ["ReligiousFacet"],
  r"(war|conflict|empire|kingdom|dynasty)": ["PoliticalFacet"],
  r"(art|music|literature|baroque|gothic)": ["ArtisticFacet"],
  r"(ice age|climate|holocene|pleistocene)": ["EnvironmentalFacet"],
}

for period in periods:
    facets = set()
    for pattern, facet_list in facet_patterns.items():
        if re.search(pattern, period['label'], re.I):
            facets.update(facet_list)
    period['Facets'] = list(facets) if facets else ["CulturalFacet"]  # fallback
```

This would catch ~60-70% of "obvious" periods and beats the current all-defaulting-to-cultural approach.

***

**What would help most right now**: Can you share a small sample of 10-20 periods where the LLM *should* have detected TechnologicalFacet or EconomicFacet but didn't? I can show you exactly what the LLM prompt should look like to fix it.
<span style="display:none">[^3_10][^3_11][^3_12][^3_13][^3_14][^3_15][^3_16][^3_6][^3_7][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: https://www.wikidata.org/wiki/Wikidata:Tools/Visualize_data/it

[^3_2]: https://arxiv.org/pdf/1205.4138.pdf

[^3_3]: https://phi.history.ucla.edu/nchs/preface/developing-standards/

[^3_4]: https://www.sociostudies.org/journal/files/seh/2007_2/production_revolutions_and_periodization_of_history.pdf

[^3_5]: https://academic.oup.com/dsh/article/38/2/852/6964525

[^3_6]: time_periods.csv

[^3_7]: https://desapublications.un.org/file/126/download

[^3_8]: https://ceur-ws.org/Vol-3322/short1.pdf

[^3_9]: https://www.sociostudies.org/almanac/articles/technological_dynamics_since_40-000_bp_to_the_22nd_century/

[^3_10]: https://www.academia.edu/108264364/Historical_Periodization_an_Exploration_and_Defence

[^3_11]: https://thedocs.worldbank.org/en/doc/35e717a3a48dcbbbe3a74c35a56dd9a8-0280032025/original/85-global-industrial-revolution.pdf

[^3_12]: https://www.nber.org/research/data/historical-cross-country-technology-adoption-hccta-dataset

[^3_13]: https://uta.pressbooks.pub/historicalresearch/chapter/how-historians-approach-history/

[^3_14]: https://www.semantic-web-journal.net/system/files/swj3842.pdf

[^3_15]: https://ourworldindata.org/grapher/global-gdp-over-the-long-run

[^3_16]: https://eric.ed.gov/?id=EJ365357

