# Backlog — from Perplexity session 2026-02-26
_Extracted: 2026-02-27_
_Source: `2-26-26-perplex-mc--agents.md`_

---

## HIGH VALUE — add to KANBAN

---

### 1. Bayesian Credence Layer on Claim Subgraphs
**What it is:** Attach a numeric credence `P_t(c)` to every claim node. When new evidence arrives, run Fischer's fallacy checks first (governance gating). Only if the evidence passes `H_c ⊨ Γ` does the Bayesian update fire. Fischer is the gatekeeper; Bayes is the update rule.

**Why it matters:** Chrystallum already has Fischer governance and a confidence-layered claim model. Adding credence scores makes the claim lifecycle formally complete: graph structure + logical validity + numeric belief strength. The formula was verified — a blind LLM correctly reconstructed the semantics from math alone, confirming it is self-sufficient for agent consumption.

**Concrete items:**
- Add `credence` float property + `credence_updated_at`, `credence_method`, `prior` to claim nodes
- Implement governed Bayesian update as application-layer procedure (not pure Cypher)
- Express `Γ` constraints as `:GovernanceRule` nodes with Cypher checks that return zero rows when satisfied
- Wire into write path: propose → Fischer check → if passed, commit graph + update credence

**File refs:** `FISCHER_FALLACY_DETECTION_COMPLETE.md`, `FISCHER_REWARD_SYSTEM.md`, `Novel-Aspects-of-Your-Mathematical-Framework-Docum.pdf`

---

### 2. Periodization Guardrails — JSON Policy Block for Agents
**What it is:** A complete JSON policy block (drafted in the session) that any SFA/SCA agent can load as a system prompt insert. Defines exactly how agents must treat periods: as constructed buckets, not natural kinds; how to handle missing QIDs; when to use EXACT_SAME_AS vs APPROX_SAME_AS; when Wikidata is the wrong instrument.

**Why it matters:** Without this, agents silently widen periods, collapse scholarly definitions, and break when Wikidata has no item (e.g., `mittelrepublikanisch` — recognized by iDAI.thesauri but absent from Wikidata as a discrete period item).

**Concrete items:**
- Write `policies/periodization_guardrails_v1.json` — policy block is already drafted, just needs saving
- Load into SFA system prompt as a required pre-amble
- Add `SYS_Policy` node `periodization_guardrails_v1` to Chrystallum graph
- Test against mittelrepublikanisch case: agent should use PeriodO as canon, not demand a QID

---

### 3. Period Canonical / PeriodO / Pleiades Space-Time Pattern
**What it is:** A clean Neo4j pattern connecting canonical period buckets to PeriodO definitions to Pleiades places to time-bounded attestations:

```
(:PeriodCanonical)-[:HAS_DEFINITION]->(:PeriodODef)-[:COVERS]->(:PleiadesPlace)-[:HAS_ATTESTATION]->(:PlaceAttestation)
```

**Why it matters:** This is the space-time grid agents need to reason about "where is this period happening" and "which periods does this place participate in" without touching polities or Wikidata. Pleiades places are date-spanned; PeriodO definitions carry spatial coverage that already links to Pleiades URIs. The two systems are designed to interlock.

**Concrete items:**
- Define `:PeriodCanonical`, `:PeriodODef`, `:PeriodODef`, `:PlaceAttestation` node schemas
- Write canonical traversal query templates (2 standard queries above)
- Populate from `periodo_roman_republic_clean.csv` — 49 Rome-related records already in hand
- Add `(:PeriodCanonical)-[:HAS_DEFINITION]->(:PeriodODef)` edges for all existing PeriodO records in graph

---

### 4. Event-as-Period Dual Typing
**What it is:** Wars, crises, and political episodes in PeriodO can and should be treated as both events and periods. The session established: a war is a valid period. The pattern is either dual-typed nodes (`:WarPeriod:EventSeries`) or a bridge pattern (`:PeriodODef)-[:REFERS_TO_EVENT_SERIES]->(:EventSeries`).

**Why it matters:** PeriodO has no built-in event/period distinction. Computational distinction requires heuristics: label patterns (`* War`, `* Revolution`, `* Siege`), duration thresholds, Wikidata `instance of` check (Q198 = war). This is needed before the adjacency matrix can correctly classify PeriodO nodes.

**Concrete items:**
- Write `classify_periodo_kind.py` — labels heuristic + duration threshold + Wikidata `instance of` check
- Add `kind` property to `:PeriodODef`: `broad_period` / `event_period` / `legislative_period` / `other`
- For event-kind nodes: link to `:EventSeries` where a matching Wikidata war item exists
- Agent policy rule: "When reasoning about participants/battles → follow event-series edges; when reasoning about co-occurrence → follow period edges"

---

### 5. Period Normalization Agent — Canonical Envelope from Variants
**What it is:** When multiple PeriodO records describe the same underlying period (e.g., "Roman Republic", "Roman Republican", "Republikanische Zeit" — all pointing at Q17167 with slightly different date spans), an agent must derive a canonical container rather than pick a winner. Rule: cluster by shared QID + overlapping ranges + similar labels → compute `[min_start, max_end]` → create derived canonical container → attach variants as `VARIANT_OF` edges.

**Why it matters:** Without this, the timeline renders three overlapping "Roman Republic" bars, which is noise. The agent cannot pick arbitrarily — it must follow a deterministic normalization rule.

**Concrete items:**
- Write `normalize_period_variants.py` — clustering + envelope derivation
- Output: one `:PeriodCanonical` per cluster, multiple `:PeriodODef` attached as `VARIANT_OF`
- Render canonical only on timelines; variants as provenance tooltips
- Test on the three "Roman Republic" variants already identified: `p083p5rj8d7`, `p08m57h65c8`, `p093ht3z7nc`

---

### 6. iDAI.thesauri as Eighth Federation
**What it is:** The session revealed that `mittelrepublikanisch` — a recognized scholarly periodization absent from Wikidata as a discrete item — exists in **iDAI.thesauri** with multilingual labels: de: *mittelrepublikanisch (264–133 v.Chr.)*, en: *Middle Republic (264–133 B.C.)*, fr: *République moyenne*, it: *media Repubblica*. iDAI is the DAI (German Archaeological Institute) controlled vocabulary.

**Why it matters:** iDAI covers the meso-level periodization that Wikidata doesn't model. For archaeological and continental European scholarship, iDAI is a first-class authority. The federation survey plan currently has six federations; iDAI should be the seventh (alongside Perseus as the eighth).

**Concrete items:**
- Add `Federation.IDAI = "idai"` to `federation_node_schema.py`
- Default dimensions: ARCHAEOLOGICAL, TEMPORAL (iDAI is primarily an archaeological thesaurus)
- Survey seed: `https://thesauri.dainst.org/` — iDAI thesauri SPARQL or JSON-LD API
- Add `survey_idai.py` to round-robin pipeline after PeriodO
- Federation default dimension: `concept_ref` = iDAI URI

---

### 7. Broader-Than / Narrower-Than Derived from Date Spans + Geography
**What it is:** A deterministic algorithm to derive BT/NT-like relations between PeriodO records from temporal logic alone, no human judgment required:
- A ⊂ B (narrower): same spatial anchor, `s_B ≤ s_A` and `e_A ≤ e_B`
- A ⊃ B (broader): inverse
- A overlaps B: `max(s_A,s_B) < min(e_A,e_B)` but neither subsetting
- Disjoint otherwise

**Why it matters:** This gives the adjacency matrix a direct TEMPORAL dimension signal without needing Wikidata alignment. Two PeriodO nodes that are BT/NT are neighbours. Two that merely overlap are weaker neighbours. The Game of Life grid needs this to compute neighbourhood correctly for temporal cells.

**Concrete items:**
- Write `derive_period_hierarchy.py` — implements the four-case temporal logic
- Input: all PeriodO nodes with `temporal_range` and `spatial_anchor`
- Output: `BROADER_THAN` / `NARROWER_THAN` / `OVERLAPS_WITH` edges on `:PeriodODef` nodes
- Feed into adjacency matrix: BT/NT = weight 2, OVERLAPS = weight 1

---

### 8. Pleiades Place-Type as Dimension Evidence
**What it is:** Pleiades place records carry a `place_type` field in the CSV row: `archaeological_site`, `settlement`, `mine`, `well`, `port`, `sanctuary`, etc. These types are direct dimension signals:
- `mine`, `quarry` → ECONOMIC dimension
- `sanctuary`, `oracle` → RELIGIOUS dimension
- `fort`, `camp` → MILITARY dimension
- `port`, `harbour` → ECONOMIC + GEOGRAPHIC (connectivity)
- `settlement`, `city` → SOCIAL + POLITICAL

**Why it matters:** Currently `survey_pleiades.py` would only emit GEOGRAPHIC dimension for all Pleiades nodes. With place-type parsing, individual Pleiades nodes can emit 2-3 dimensions, making them richer adjacency signals and increasing their survival rate in the Game of Life model without needing cross-federation alignment.

**Concrete items:**
- Add place-type → dimension mapping table to `federation_node_schema.py` or a config file
- Update `survey_pleiades.py` to read `place_type` from Pleiades CSV/JSON and add dimensions accordingly
- Add `place_type_raw` property to `:PleiadesPlace` nodes
- Use `TYPED_AS` edge to `:PlaceType` controlled vocab node (optional but queryable)

---

### 9. Perseus Catalog as Federation — Text Anchors + Co-occurrence Adjacency
**What it is:** Perseus Catalog is a metadata hub for classical texts. Querying by LCSH heading `sh85115114` returns works with co-occurring subject headings. Two LCSH headings that appear together on the same classical text are neighbours — the cataloguer already made the adjacency judgment. This is a direct input to the adjacency matrix that requires no inference.

**Why it matters:** Perseus provides what no other federation provides: primary source anchors. A SubjectConcept grounded in Livy Book 1 has different epistemic status than one grounded in a 2003 monograph. Co-occurrence on ancient texts is a signal no modern library system generates.

**Concrete items:**
- Add `Federation.PERSEUS = "perseus"` to schema
- Add `text_anchor` alignment field (distinct from `text_ref`) for CTS URNs (ancient texts)
- Write `survey_perseus.py` — query Perseus Catalog API by subject heading, extract co-occurring headings
- Build co-occurrence matrix from multi-headed works as supplementary adjacency signal
- Feed co-occurrence edges directly to adjacency matrix: shared co-occurrence on same work = INTELLECTUAL neighbour

---

### 10. AI-Derived Periodization — Computational Period Discovery
**What it is:** Rather than importing human-curated periods, use ML to discover periods from the data itself: load time-binned features (place counts by type, event density, person counts), normalize and reduce to PCA components, run change-point detection (ruptures library, `model="rbf"`, choose `n_bkps` by penalty), cluster time bins in PC space, derive contiguous AI-period segments. The session referenced `https://arxiv.org/html/2412.20582v1` as relevant.

**Why it matters:** The session established that human periodization is arbitrary at the margins. AI-derived periods provide a bias-free comparison baseline. If the AI periods substantially match the scholarly ones, that validates the scholarly periodization. Where they differ, the discrepancy is itself a finding — evidence that scholarly consensus may be drawing a boundary for narrative convenience rather than structural change.

**Concrete items:**
- Write `ai_periodization.py` — implements the 5-step pipeline: feature loading → PCA → change-point → clustering → period derivation
- Features: Pleiades place-type time bins, DPRR office-holder counts per decade, PeriodO event density
- Output: AI period segments with confidence scores, as `:AIPeriod` nodes in graph
- Compare AI periods against canonical PeriodO periods — produce overlap/divergence report
- Use as validation layer for the canonical period buckets

---

## MEDIUM VALUE — backlog for later

---

### 11. KG Self-Describing Contract — Agent Boot Sequence
**What it is:** A "KG contract" the agent queries before doing anything else: `db.schema.visualization()`, `db.schema.nodeTypeProperties()`, `db.schema.relTypeProperties()`, plus GovernanceRule and TraversalPattern nodes. The session established that agents reliably need three layers: (a) schema inventory, (b) executable governance, (c) canonical query templates. Without (c), agents hallucinate Cypher.

**Concrete items:**
- Write `agent_boot_sequence.cypher` — 3-5 standard queries every agent must run first
- Add `:QueryTemplate` nodes for 10 most common traversals (claim neighborhood, GovernanceRule check, period-space traversal, etc.)
- Document "agent boot sequence" in `SUBJECT_CONCEPT_AGENTS_GUIDE.md`

---

### 12. Oxford Roman Economy Project (OXREP) Mining Bibliography as Dimension Source
**What it is:** OXREP mining bibliography (`oxrep.classics.ox.ac.uk/bibliographies/mining_bibliography/`) provides structured lists of mining districts, metals, and chronological peaks. Gosner 2021 on Roman mining and economic integration provides economic geography patterns. The session identified these as the primary research veins for getting LLM agents into economics, production, and metals of Pleiades places.

**Why it matters:** Once Pleiades places have `place_type = mine/quarry`, the next step is knowing what metal was mined and when. OXREP gives you the site-to-metal-to-period mapping. This is the ECONOMIC dimension evidence that Pleiades alone can't provide.

**Concrete items:**
- Extract OXREP mining bibliography as structured data (site name → metal → period → region)
- Align to Pleiades URIs where possible
- Add `metal_produced`, `production_period` properties to `:PleiadesPlace` for mine-type places
- Use as ECONOMIC dimension evidence in federation node schema

---

### 13. ClassificationAnchor Nodes — Federation Positioning Step
**What it is:** When the SCA traverses a QID and finds Dewey/LCC/LCSH/FAST coordinates, it should create lightweight `:ClassificationAnchor` nodes (not domain entities) carrying those coordinates. These anchors are schema coordinates, not domain facts. The POSITIONED_AS relationship with a `federation` tag handles the "same node means different things in different ontologies" problem.

**Concrete items:**
- Implement `position_in_federated_schemas(seed_qid)` method in SCAAgent
- Run on Q17167 only first (proof of concept)
- Layer 1 only: deterministic Wikidata P31/P279 traversal
- Write CLASSIFICATION_PARENT / INSTANCE_OF_CLASS / TYPE_ANCHOR / POSITIONED_AS relationships
- Include `federation` tag on all POSITIONED_AS edges from day one (retrofitting is harder)

**Note:** This is the SCA Federation Positioning Spec v2 reviewed in the session and validated as "solid design." It is the missing foundation for re-running SubjectConcept generation with federation parameters.

---

### 14. Connectedness / Economic Geography Features for AI Periodization
**What it is:** The session referenced "Connectedness and the Location of Economic Activity in the Iron Age" (MIT/CEPR) and related work. Port density, coastal connectedness, settlement density are all proxies for economic intensity. These can be derived from Pleiades place-type distributions per time bin and used as AI-periodization features.

**Concrete items:**
- Derive features per time bin: `num_ports`, `num_mines`, `num_settlements`, `coastal_connectivity_index`
- Feed into `ai_periodization.py` feature matrix alongside event density and person counts
- Document the feature schema so SFAs can explain "why did the AI cut the period here" in terms of these proxies

---

## INFORMATIONAL / ALREADY VALIDATED — no immediate action

- **Formula is agent-self-sufficient:** The Fischer+Bayes governed update formula was tested on a blind LLM which correctly reconstructed full semantics from math alone. The formal specification is solid; no narrative needed for capable models.
- **Wikidata is not the arbiter of period reality:** Confirmed. PeriodO + Pleiades + citable scholarly works are first-class even without QIDs. This is now encoded in the guardrails policy.
- **DDC is proprietary (OCLC):** Numbers (e.g., "321.8") are free to use; caption text is licensed. WebDewey access ~$300/year per user. WorldCat full API access requires institutional subscription (thousands/year). Individual access path: WebDewey subscription + LC SRU as WorldCat substitute.
- **Period normalization requires an agent, not a human pick:** Three "Roman Republic" variants in PeriodO differ by 1-2 years start/end and one is German. Canonical envelope derivation is the correct answer, not arbitrary selection.
- **Wars are valid periods:** PeriodO itself makes no distinction. Heuristic tagging (label patterns + duration + Wikidata P31 check against Q198 war) can derive `kind` property computationally.

---

## PRIORITY ORDER FOR KANBAN

Immediate (Phase 0 unblock):
1. **Periodization guardrails JSON** (item 2) — needed before any SFA runs on PeriodO data
2. **Broader-than/narrower-than algorithm** (item 7) — direct input to adjacency matrix
3. **Pleiades place-type → dimensions** (item 8) — improves survival rate without new federation
4. **Event-as-period classification** (item 4) — needed before PeriodO survey output is useful

Medium term (after Phase 0a surveys):
5. **Period canonical/PeriodO/Pleiades pattern** (item 3) — needed for Phase 0b alignment
6. **Period normalization agent** (item 5) — needed before adjacency matrix handles PeriodO correctly
7. **Perseus federation** (item 9) — add to round-robin after core 6 are running
8. **iDAI federation** (item 6) — add alongside Perseus

Later:
9. **Bayesian credence layer** (item 1) — Fischer governance must be complete first
10. **ClassificationAnchor / federation positioning** (item 13) — Phase 3 SCA work
11. **AI periodization** (item 10) — needs all federation surveys complete first
12. **OXREP mining data** (item 12) — enrichment after base graph is stable
13. **KG agent boot sequence** (item 11) — needed before multi-agent deployment
14. **Connectedness features** (item 14) — feeds into AI periodization

---

_Source document: 56 Q&A exchanges covering Bayesian claim governance, agent self-description, federation positioning, PeriodO period analysis (49 Rome records), Game of Life review, LCSH sh85115114 cross-system reach, Perseus catalog, AI-derived periodization, Pleiades place types, and OXREP economic geography._
