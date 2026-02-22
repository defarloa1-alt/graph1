# **PART II: CORE ONTOLOGY LAYERS**

---

# **3. Entity Layer**

## **3.0 Overview**

The **Entity Layer** represents real-world historical entities: people, places, events, organizations, works, and related historical structures. Entities are the **nodes** in the knowledge graph, connected by relationships.

**Core Principles:**
1. **Entity types are semantic, not structural:** `Human` vs `Organization` matters for reasoning
2. **Entities are identified by authorities:** `qid` (Wikidata), `viaf_id` (persons), `pleiades_id` (places)
3. **Entities have temporal existence:** `start_date`, `end_date`, `date_precision`
4. **Entities are classified by subjects:** `backbone_lcc`, `backbone_fast` for discovery

### **3.0.1 Canonical First-Class Node Set (Normative)**

The canonical first-class node set for active implementation is:
- `SubjectConcept`
- `Human`
- `Gens`
- `Praenomen`
- `Cognomen`
- `Event`
- `Place`
- `Period`
- `Dynasty`
- `Institution`
- `LegalRestriction`
- `Claim`
- `Organization`
- `Year`
- `Work`
- `Material`
- `Object`
- `ConditionState`

**Deprecated (replaced or merged):**
- ~~`Position`~~ → Merged into `Institution` (with typed `HELD_BY` edge) or modeled as typed `Event` (appointment/tenure)
- ~~`Activity`~~ → Concrete instances route to `Event` (with appropriate `action_type`); abstract patterns route to `SubjectConcept`

**Policy lock-ins:**
- `Subject` and `Concept` are legacy labels and MUST map to `SubjectConcept`.
- `Person` is legacy wording and MUST map to `Human`.
- `Communication` is NOT a first-class node label; it is modeled as a facet/domain axis in Section 3.3.
- `Position` is deprecated as of 2026-02-16; use Institution-edge patterns (§3.1.11 migration guide).
- `Activity` is deprecated as of 2026-02-16; use Event or SubjectConcept routing (§3.1.14 migration guide).

---

## **3.1 Core Entity Types** 

### **3.1.1 Human**

**Node Label:** `:Human`

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"hum_000123"`)
- `name` (string): Primary name (e.g., `"Gaius Julius Caesar"`)
- `qid` (string): Wikidata QID (e.g., `"Q1048"`)
- `entity_type` (string): Always `"Human"`

**Optional Properties:**
- `birth_date` (ISO 8601 string): e.g., `"-0100-07-12"` for 100 BCE
- `death_date` (ISO 8601 string): e.g., `"-0044-03-15"` for 44 BCE  
- `date_precision` (string): `"day"`, `"month"`, `"year"`, `"circa"`
- `gender` (string): `"male"`, `"female"`, `"unknown"`
- `viaf_id` (string): Virtual International Authority File ID
- `backbone_lcc` (string): Library of Congress Classification
- `backbone_fast` (array): FAST topic IDs
- `backbone_lcsh` (array): LCSH subject headings

**Authority Alignment:**
- `cidoc_crm_class`: `"E21_Person"`
- `cidoc_crm_version`: `"8.0"`
- `iso_standard`: `"ISO 21127:2023"`

**Temporal Properties:**
- `calendar_system` (string): `"Julian"`, `"Gregorian"`, `"Roman AUC"`
- `temporal_uncertainty` (boolean): Flag for uncertain dates

**Optional Edges:**
- `BORN_IN` â†’ `:Place` (birthplace)
- `DIED_IN` â†’ `:Place` (deathplace)
- `MEMBER_OF` â†’ `:Organization`
- `PART_OF_GENS` â†’ `:Gens` (Roman naming)
- `HAS_POSITION` â†’ `:Position` (offices held)
- `PARTICIPATED_IN` â†’ `:Event`
- `LIVED_DURING` â†’ `:Period`
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept` (classification)
- `SUBJECT_OF` â†’ `:Claim` (provenance)

---

### **3.1.2 Place**

**Node Label:** `:Place`

**Purpose:** Represents stable geographic identity (abstract concept of a location that persists across time).

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"plc_000456"`)
- `label` (string): Primary place name (e.g., `"Rome"`)
- `qid` (string): Wikidata QID (e.g., `"Q220"`)
- `entity_type` (string): Always `"Place"`

**Optional Properties:**
- `pleiades_id` (string): Pleiades gazetteer ID for ancient places
- `tgn_id` (string): Getty Thesaurus of Geographic Names ID
- `latitude` (float): Decimal degrees (modern/primary location)
- `longitude` (float): Decimal degrees
- `place_type` (string): `"city"`, `"province"`, `"region"`, `"settlement"`, `"natural_feature"`
- `modern_country` (string): Modern political entity

**Authority Alignment:**
- `cidoc_crm_class`: `"E53_Place"`

**Required Edges:**
- `LOCATED_IN` â†’ `:Place` (spatial hierarchy)

**Optional Edges:**
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

**Note:** For historical "shifting borders" problem, use **`:PlaceVersion`** pattern (see below).

---

### **3.1.2.1 PlaceVersion (Temporal Instantiation)**

**Node Label:** `:PlaceVersion`

**Purpose:** Represents time-scoped and authority-scoped instantiation of a place (e.g., "Roman Province of Syria, 1st Century CE").

**Required Properties:**
- `pver_id` (string): Internal unique identifier (e.g., `"pver_00123_01"`)
- `label` (string): Temporal description (e.g., `"Antioch (Roman Period)"`)
- `start_date` (ISO 8601 string): Period start
- `end_date` (ISO 8601 string): Period end
- `authority` (string): Source of definition (e.g., `"Pleiades"`, `"TGN"`)
- `confidence` (float): Authority confidence (0.0-1.0)

**Required Edges:**
- `VERSION_OF` â†’ `:Place` (links to stable identity)
- `HAS_GEOMETRY` â†’ `:Geometry` (spatial representation)

**Optional Edges:**
- `BROADER_THAN` â†’ `:PlaceVersion` (administrative hierarchy)
- `NARROWER_THAN` â†’ `:PlaceVersion`

**Use Pattern:**
```cypher
(:Event)-[:TOOK_PLACE_AT]->(:PlaceVersion)-[:VERSION_OF]->(:Place)
```

---

### **3.1.2.2 Geometry (Spatial Data)**

**Node Label:** `:Geometry`

**Purpose:** Stores geographic coordinates/shapes; allows multiple conflicting geometries for same place version.

**Required Properties:**
- `geo_id` (string): Internal unique identifier
- `wkt` (string): Well-Known Text format (e.g., `"POINT(36.16 36.20)"`, `"POLYGON(...)"`)
- `source` (string): Data source (e.g., `"Wikidata"`, `"Pleiades"`)
- `method` (string): Derivation method (e.g., `"centroid"`, `"survey"`, `"estimate"`)

**Required Edges:**
- None (connected via incoming `HAS_GEOMETRY` from PlaceVersion)

---

### **3.1.3 Event**

**Node Label:** `:Event`

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"evt_000987"`)
- `label` (string): Event description (e.g., `"Battle of Actium"`)
- `qid` (string): Wikidata QID (e.g., `"Q193304"`)
- `entity_type` (string): Always `"Event"`

**Temporal Properties:**
- `start_date` (ISO 8601 string): Event start (e.g., `"-0049-01-10"`)
- `end_date` (ISO 8601 string): Event end
- `date_precision` (string): `"day"`, `"month"`, `"year"`, `"circa"`
- `calendar_system` (string): Original calendar system
- `temporal_uncertainty` (boolean)

**Optional Properties:**
- `event_type` (string): `"battle"`, `"treaty"`, `"revolt"`, `"election"`, `"assassination"`
- `casualties_estimate` (integer): Estimated casualties
- `location_qid` (string): Primary location Wikidata ID

**Authority Alignment:**
- `cidoc_crm_class`: `"E5_Event"`

**Action Structure:**
- `action_type` (string): From action structure vocabulary (Appendix B)
- `goal_type` (string): From goal type vocabulary
- `trigger_type` (string): From trigger vocabulary
- `result_type` (string): From result vocabulary

**Required Edges:**
- `OCCURRED_AT` â†’ `:Place` or `:PlaceVersion` (location)
- `OCCURRED_DURING` â†’ `:Period` (temporal context)
- `STARTS_IN_YEAR` â†’ `:Year` (start year)
- `ENDS_IN_YEAR` â†’ `:Year` (end year)

**Optional Edges:**
- `PARTICIPANT` â†’ `:Human`, `:Organization`
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.1.4 Period**

**Node Label:** `:Period`

**Purpose:** Represents named historiographic periods with fuzzy temporal boundaries (e.g., "Roman Republic", "Julio-Claudian Dynasty").

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"prd_000111"`)
- `label` (string): Period name (e.g., `"Roman Republic"`)
- `start` (string): Nominal start year (e.g., `"-0510"`)
- `end` (string): Nominal end year (e.g., `"-0027"`)
- `entity_type` (string): Always `"Period"`

**Optional Properties (Fuzzy Bounds):**
- `earliest_start` (string): Earliest plausible start (e.g., `"-0520"`)
- `latest_start` (string): Latest plausible start (e.g., `"-0500"`)
- `earliest_end` (string): Earliest plausible end (e.g., `"-0035"`)
- `latest_end` (string): Latest plausible end (e.g., `"-0020"`)
- `authority` (string): Source authority (e.g., `"PeriodO"`, `"Wikidata"`)
- `authority_uri` (string): External identifier (PeriodO URI)
- `culture` (string): Cultural frame (e.g., `"Roman"`, `"Greek"`)
- `facet` (string): Facet classification (e.g., `"political"`, `"economic"`, `"technical"`)
- `qid` (string): Wikidata QID
- `spatial_coverage` (array): Geographic scope (e.g., `["Italy", "Mediterranean"]`)

**Required Edges:**
- `STARTS_IN_YEAR` â†’ `:Year` (nominal start)
- `ENDS_IN_YEAR` â†’ `:Year` (nominal end)

**Optional Edges:**
- `BROADER_THAN` â†’ `:Period` (hierarchy, e.g., Empire > Early Empire)
- `NARROWER_THAN` â†’ `:Period`
- `ALIGNED_WITH` â†’ `:Period` (cross-authority alignment)
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.1.5 Year**

**Node Label:** `:Year`

**Purpose:** Atomic temporal entity used for chronological alignment, period boundaries, event dating, and claim temporal grounding. Forms the **global Year backbone** from at least -2000 to 2025.

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"year_-0049"`)
- `year` (integer): Astronomical year notation (BCE = negative, e.g., `-49`)
- `label` (string): Human-readable label (e.g., `"49 BCE"`)
- `entity_type` (string): Always `"Year"`

**Optional Properties:**
- `iso` (string): Zero-padded ISO 8601 year (e.g., `"-0049"`)
- `calendar` (string): Default calendar system (e.g., `"proleptic Julian"`)

**Required Edges:**
- `FOLLOWED_BY` â†’ `:Year` (next year in sequence)
- `PRECEDED_BY` â†’ `:Year` (previous year in sequence)

**Optional Edges:**
- `PART_OF` â†’ `:Decade` / `:Century` / `:Millennium` (if hierarchy nodes exist)

**Usage Pattern:** Every temporally grounded entity or claim must tether to one or more Year nodes.

---

### **3.1.6 Organization**

**Node Label:** `:Organization`

**Purpose:** Represents political bodies, military units, religious colleges, administrative institutions.

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"org_000222"`)
- `label` (string): Organization name (e.g., `"Roman Senate"`)
- `qid` (string): Wikidata QID (e.g., `"Q41410"`)
- `entity_type` (string): Always `"Organization"`

**Optional Properties:**
- `organization_type` (string): `"political_body"`, `"military_unit"`, `"religious_college"`, `"administrative"`, `"commercial"`
- `founding_date` (ISO 8601 string)
- `dissolution_date` (ISO 8601 string)

**Authority Alignment:**
- `cidoc_crm_class`: `"E74_Group"`

**Required Edges:**
- `LOCATED_IN` â†’ `:Place`

**Optional Edges:**
- `HAS_MEMBER` â†’ `:Human`
- `PARTICIPATED_IN` â†’ `:Event`
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.1.7 Institution**

**Node Label:** `:Institution`

**Purpose:** Represents abstract but real-world structures (legal institutions, political institutions, religious institutions, administrative systems). Distinct from Organizations (which have members) and Concepts (which are abstract categories).

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"inst_000333"`)
- `label` (string): Institution name (e.g., `"Roman Dictatorship"`, `"Consulship"`)
- `entity_type` (string): Always `"Institution"`

**Optional Properties:**
- `institution_type` (string): `"legal"`, `"political"`, `"religious"`, `"administrative"`, `"educational"`
- `founding_date` (ISO 8601 string)
- `abolition_date` (ISO 8601 string)

**Required Edges:**
- `LOCATED_IN` â†’ `:Place`

**Optional Edges:**
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.1.8 Dynasty**

**Node Label:** `:Dynasty`

**Purpose:** Represents ruling families or succession lines.

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"dyn_000444"`)
- `label` (string): Dynasty name (e.g., `"Julio-Claudian Dynasty"`)
- `start` (string): Dynasty start year (e.g., `"-0027"`)
- `end` (string): Dynasty end year (e.g., `"0068"`)
- `entity_type` (string): Always `"Dynasty"`

**Required Edges:**
- `RULED` â†’ `:Place` (geographic extent)
- `HAS_MEMBER` â†’ `:Human` (rulers)

**Optional Edges:**
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.1.9 LegalRestriction**

**Node Label:** `:LegalRestriction`

**Purpose:** Represents laws, decrees, bans, privileges, legal statuses.

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"law_000555"`)
- `label` (string): Law name (e.g., `"Senatus Consultum Ultimum"`)
- `date` (string): Enactment date (e.g., `"-0052"`)
- `entity_type` (string): Always `"LegalRestriction"`

**Required Edges:**
- `ISSUED_BY` â†’ `:Organization`
- `APPLIED_TO` â†’ `:Human`, `:Organization`, `:Place`

**Optional Edges:**
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.1.10 Work**

**Node Label:** `:Work`

**Purpose:** Represents texts, inscriptions, manuscripts, artifacts, and modern scholarship. Critical for provenance chain (Work â†’ Passage â†’ Claim).

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"wrk_000666"`)
- `title` (string): Work title (e.g., `"Life of Caesar"`)
- `qid` (string): Wikidata QID (e.g., `"Q2896"`)
- `entity_type` (string): Always `"Work"`

**Optional Properties:**
- `author` (string): Author name or QID
- `publication_date` (ISO 8601 string)
- `work_type` (string): `"ancient_text"`, `"modern_monograph"`, `"inscription"`, `"manuscript"`, `"article"`
- `source_tier` (string): `"Primary"`, `"Secondary"`, `"Tertiary"`
- `language` (string): ISO 639-1 language code

**Authority Alignment:**
- `cidoc_crm_class`: `"E73_Information_Object"`

**Required Edges:**
- `WRITTEN_BY` â†’ `:Human`

**Optional Edges:**
- `ABOUT` â†’ `:Entity`, `:SubjectConcept` (aboutness)
- `CITED_IN` â†’ `:Claim` (provenance)
- `RETRIEVED_FROM` â†’ `:RetrievalContext` (LLM extraction context)

---

### **3.1.11 Position (DEPRECATED)**

⚠️ **Status:** Deprecated as of 2026-02-16. Do not use for new implementations.

**Previous Purpose:** Represented offices, titles, and roles (e.g., Consul, Tribune, Governor).

**Removal Rationale:**
- `Position` redundantly duplicates semantics already expressible via `Institution` + typed edge properties
- In CIDOC-CRM terms, holding an office is an **E7_Activity** (appointment/tenure event), not a distinct entity
- Biographic facet (Section 3.3) models office-holding as career sequence on the Human node

**Migration Guide:**
- **Option A (preferred):** Use rich `HELD_POSITION` edge on Institution with properties: `{position_type, start_date, end_date, source}`
- **Option B:** Model office-holding as typed `Event` with `event_type: "appointment"`

---

### **3.1.11a ConditionState**

**Node Label:** `:ConditionState`

**Purpose:** Represents time-scoped condition observations of artifacts. Enables tracking condition changes over time without full object versioning (mirrors PlaceVersion and PeriodVersion patterns).

**Required Properties:**
- `entity_id` (string): Internal ID (e.g., `"cond_000123"`)
- `state_label` (string): Condition description (e.g., `"mint"`, `"worn"`, `"corroded"`, `"overstruck"`)
- `entity_type` (string): Always `"ConditionState"`

**Optional Properties:**
- `description` (string): Detailed condition notes
- `assessment_date` (ISO 8601 string): When this condition was observed/recorded
- `source` (string): Museum catalog, publication, or assessment source
- `method` (string): Assessment method (e.g., `"visual"`, `"XRF"`, `"X-ray"`, `"conservation report"`)
- `confidence` (float 0-1): Confidence level of assessment

**Edges:**
- `APPLIES_TO` -> `:Object` (which object this condition describes)
- `ASSESSED_DURING` -> `:Period` or `:Year` (when the observation was made)
- `SUBJECT_OF` -> `:Claim` (claims about condition)

**Usage Pattern:**
- Object node remains stable identity
- Each ConditionState is a time-bound observation with provenance
- Query: (obj:Object)-[:HAS_CONDITION_STATE]->(cond:ConditionState) to track state history
- Optional: Denormalize current best-known condition on Object as `current_condition` property (derived from latest validated ConditionState)

---

### **3.1.12 Material**

**Node Label:** `:Material`

**Purpose:** Represents physical materials (E57_Material in CIDOC-CRM). Critical for artifact composition tracking and material culture queries.

**Required Properties:**
- `entity_id` (string): Internal ID (e.g., `"mat_000123"`)
- `label` (string): Canonical name (e.g., `"gold"`, `"marble"`)
- `entity_type` (string): Always `"Material"`

**Authority / Classification Properties:**
- `aat_id` (string): Getty AAT ID (primary authority for materials)
- `aat_pref_label` (string): AAT preferred label
- `aat_broader` (array): Parent AAT IDs (SKOS hierarchy, one direction)
- `wikidata_qid` (string, optional): Wikidata material item
- `bm_material_id` (string, optional): British Museum materials thesaurus ID

**Type Flags (denormalized for query performance):**
- `material_family` (string): "metal", "stone", "ceramic", "glass", "organic", "composite"
- `metal_type` (string, optional): "precious", "base" (for gold/silver vs iron/bronze)
- `period_relevance` (array): e.g., ["Roman Republic", "Hellenistic"]

**Edges:**
- `BROADER_THAN` -> `:Material` (SKOS hierarchy; store one direction only)
- `USED_IN` -> `:Object` (inverse of Object-MADE_OF, optional convenience edge)

---

### **3.1.13 Object**

**Node Label:** `:Object`

**Purpose:** Represents artifacts, tools, weapons, coins, inscriptions, sculptures (E22_Human-Made_Object in CIDOC-CRM). Critical for archaeological and material-culture reasoning.

**Required Properties:**
- `entity_id` (string): Internal ID (e.g., `"obj_000999"`)
- `label` (string): Short description (e.g., `"Denarius of Caesar"`)
- `entity_type` (string): Always `"Object"`

**Optional Descriptive Properties:**
- `object_type` (string): "coin", "weapon", "tool", "inscription", "sculpture", "vessel", etc.
- `date_from` / `date_to` (ISO 8601 strings): Object production/use range
- `cidoc_crm_class` (string): Usually `"E22_Human-Made_Object"`

**Authority / Classification Properties:**
- `aat_id` (string): AAT object-type ID (primary authority)
- `aat_pref_label` (string): AAT preferred label
- `aat_broader` (array): AAT hierarchy
- `wikidata_qid` (string, optional): Wikidata item
- `bm_object_type_id` (string, optional): British Museum object type
- `backbone_fast` (array): FAST topics  (e.g., "Coins, Roman")
- `backbone_lcc` (string, optional): LCC classification

**Authority Precedence:** AAT -> BM/FISH -> Wikidata -> local

**Edges:**
- `MADE_OF` -> `:Material` (multi-edge; edge props: role, fraction, source, confidence)
- `CREATED_BY` -> `:Human` or `:Organization`
- `FOUND_AT` -> `:Place` or `:PlaceVersion`
- `DATED_TO` -> `:Period` and/or `:Year`
- `DEPICTS` -> `:Human` / `:Event` (iconography)
- `HAS_SUBJECT_CONCEPT` -> `:SubjectConcept` (classification)
- `HAS_CONDITION_STATE` -> `:ConditionState` (time-scoped condition observations)
- `SUBJECT_OF` -> `:Claim` (claims about the object)

---

### **3.1.14 Activity (DEPRECATED)**

[DEPRECATED as of 2026-02-16. Do not use for new implementations.]

**Previous Purpose:** Represented actions, rituals, practices, occupations (abstract patterns of behavior).

**Removal Rationale:**
- Conflates two distinct concepts: things-in-the-world vs. concepts-about-the-world
- Concrete activities (specific triumph, specific trade mission) should route to Event nodes with appropriate action_type
- Abstract activity patterns ("Agriculture as a practice", "the institution of Triumph") should route to SubjectConcept nodes

**Migration Guide:**
- **Concrete instances** -> Event with event_type and action_type properties
- **Abstract patterns** -> SubjectConcept with classification properties (e.g., facet_tag: "occupational")
- Example: A specific triumphus = Event; "Triumph as an institution" = SubjectConcept

---

## **3.2 Roman-Specific Entity Types**

These extend the Human entity model with Roman naming conventions.

### **3.2.1 Gens**

**Node Label:** `:Gens`

**Purpose:** Represents Roman family clans (e.g., Julia, Cornelia, Claudia).

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"gens_000001"`)
- `label` (string): Gens name (e.g., `"Julia"`)
- `entity_type` (string): Always `"Gens"`

**Required Edges:**
- `HAS_MEMBER` â†’ `:Human`

**Optional Edges:**
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.2.2 Praenomen**

**Node Label:** `:Praenomen`

**Purpose:** Represents Roman first names (e.g., Gaius, Marcus, Lucius).

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"prae_000001"`)
- `label` (string): Praenomen (e.g., `"Gaius"`)
- `abbreviation` (string): Standard abbreviation (e.g., `"C."`)
- `entity_type` (string): Always `"Praenomen"`

---

### **3.2.3 Cognomen**

**Node Label:** `:Cognomen`

**Purpose:** Represents Roman family surnames (e.g., Caesar, Cicero, Brutus).

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"cog_000001"`)
- `label` (string): Cognomen (e.g., `"Caesar"`)
- `entity_type` (string): Always `"Cognomen"`

**Optional Properties:**
- `meaning` (string): Etymology or meaning (e.g., `"hairy"` for Caesar)

---

### **3.2.4 AnalysisRun** ðŸŸ¡ **NEW NODE TYPE**

**Node Label:** `:AnalysisRun`

**Purpose:** Represents one execution of the claim evaluation pipeline. Enables re-running analysis and comparing results across evaluation versions.

**Required Properties:**
- `run_id` (string): Unique run identifier (e.g., `"RUN_2026_02_12_001"`)
- `pipeline_version` (string): Version of evaluation pipeline (e.g., `"v1.2"`, `"v2.0_experimental")`

**Optional Properties:**
- `created_at` (ISO 8601 datetime): When analysis run started
- `updated_at` (ISO 8601 datetime): When analysis run completed
- `prompt_set` (string): Identifier for prompt configuration used
- `model_config` (string): Model version/config identifier
- `status` (enum): `"in_progress"`, `"completed"`, `"failed"`

**Required Edges:**
- `HAS_ANALYSIS_RUN` â† `:Claim` (incoming edge from claim being analyzed)

**Related Edges:**
- `HAS_FACET_ASSESSMENT` â†’ `:FacetAssessment` (one per facet evaluated)

**Purpose/Key Insight:**
- Single claim can have multiple AnalysisRuns over time
- Each run contains independent facet assessments
- Enables A/B testing: compare "run v1" vs "run v2" for same claim
- Stores pipeline metadata once per run (not repeated per assessment)

---

### **3.2.5 FacetAssessment**  **NEW NODE TYPE**

**Node Label:** `:FacetAssessment`

**Purpose:** Represents one facet-specific evaluation of a claim within an AnalysisRun. Each claim's AnalysisRun contains multiple FacetAssessments (one per analytical dimension).

**Required Properties:**
- `assessment_id` (string): Unique assessment identifier (e.g., `"FA_CAESAR_POL_001"`)
- `score` (float, 0.0-1.0): Confidence/quality score for this facet
- `status` (enum): `"supported"`, `"challenged"`, `"uncertain"`, `"mostly_supported"`

**Optional Properties:**
- `rationale` (string): Explanation of assessment (e.g., "High confidence based on primary sources")
- `created_at` (ISO 8601 datetime): When assessment created
- `evidence_count` (integer): Number of supporting sources cited

**Required Edges:**
- `HAS_FACET_ASSESSMENT` â† `:AnalysisRun` (incoming edge from parent run)
- [`ASSESSES_FACET`](ASSESSES_FACET) â†’ `:Facet` subclass (e.g., `:PoliticalFacet`, `:MilitaryFacet`)
- [`EVALUATED_BY`](EVALUATED_BY) â†’ `:Agent` (which agent made this assessment)

**Star Pattern Insight:**
- Single claim can have assessments across all 17 facets simultaneously
- Each facet evaluation is independent (political_confidence â‰  military_confidence)
- Each assessment can cite different sources
- Enables UI tabs: "Political view" | "Military view" | "Economic view" etc.
- Enables agent specialization: political expert only evaluates political facets

**Example:**
Battle of Pharsalus (48 BCE) single AnalysisRun with multiple assessments:
```cypher
(run:AnalysisRun {run_id: "RUN_001"})
  -[:HAS_FACET_ASSESSMENT]->(fa1:FacetAssessment {score: 0.95, status: "supported"})
    -[:ASSESSES_FACET]->(mil:MilitaryFacet)
    -[:EVALUATED_BY]->(military_agent)
  -[:HAS_FACET_ASSESSMENT]->(fa2:FacetAssessment {score: 0.92, status: "supported"})
    -[:ASSESSES_FACET]->(pol:PoliticalFacet)
    -[:EVALUATED_BY]->(political_agent)
  -[:HAS_FACET_ASSESSMENT]->(fa3:FacetAssessment {score: 0.80, status: "mostly_supported"})
    -[:ASSESSES_FACET]->(geo:GeographicFacet)
    -[:EVALUATED_BY]->(geography_agent)
```

---

### **3.2.6 FacetCategory**** NEW NODE TYPE**

**Node Label:** `:FacetCategory`

**Purpose:** Organizes 17 analytical facets into semantic categories. Enables UI grouping and agent specialization assignment.

**Required Properties:**
- `key` (string, uppercase enum): Facet category identifier (e.g., `"POLITICAL"`, `"MILITARY"`, `"ECONOMIC"`)
- `label` (string): Display label (e.g., `"Political"`)

**Optional Properties:**
- `definition` (string): Category scope definition
- `color` (hex): UI color for facet category tabs/visualizations

**Related Edges:**
- `IN_FACET_CATEGORY` â† `:Facet` (all facets link to their category)
- `OWNS_CATEGORY` â† `:Agent` (agents specialize in specific facet categories)

**Example:**
```cypher
(:FacetCategory {key: "POLITICAL", label: "Political"})
  â† (:PoliticalFacet {unique_id: "POLITICALFACET_Q3624078"})
  â† (:Agent {agent_id: "AGENT_POLITICAL_V1"})-[:OWNS_CATEGORY]
```

---

## **3.3 Facets (Entity-Level Classification) â€“ Star Pattern Architecture**

Entities can be classified along **18 analytical dimensions** (facets) for multi-dimensional discovery.
Canonical source of truth: `Facets/facet_registry_master.json` (with tabular export at `Facets/facet_registry_master.csv`).
Temporal modeling is handled separately in Section 3.4.

1. **Geographic:** Spatial distribution and location
2. **Political:** Governance, power, authority
3. **Cultural:** Art, literature, customs, identity
4. **Technological:** Tools, methods, innovations
5. **Religious:** Beliefs, practices, institutions
6. **Economic:** Trade, production, finance
7. **Military:** Warfare, tactics, organization
8. **Environmental:** Climate, geography, resources
9. **Demographic:** Population, migration, ethnicity
10. **Intellectual:** Philosophy, science, education
11. **Scientific:** Technical knowledge, inquiry
12. **Artistic:** Visual arts, architecture, aesthetics
13. **Social:** Class, family, social structures
14. **Linguistic:** Languages, writing systems
15. **Archaeological:** Material culture, excavation
16. **Diplomatic:** Treaties, alliances, negotiations
17. **Communication:** mass media, messaging, propaganda, and ideology transmission
18. **Biographic:** Personal history, biography, life events, office-holding careers

Facet policy:
- `Communication` remains a facet/domain dimension and is not materialized as `:Communication` in the first-class node set.

**Implementation:** Entities link to SubjectConcepts representing these facets (see Section 4):
```cypher
(:Human)-[:HAS_SUBJECT_CONCEPT]->(:SubjectConcept {facet: "Political"})
```

---

## **3.4 Temporal Modeling Architecture**

### **3.4.1 Year Backbone**

The **Year backbone** is a continuous linked list of Year nodes from at least -2000 to 2025 (extensible).

**Purpose:**
- Global temporal grid for all historical reasoning
- Atomic temporal resolution
- Period boundary anchoring
- Event dating precision

**Structure:**
```cypher
(:Year {year: -49})-[:FOLLOWED_BY]->(:Year {year: -48})
(:Year {year: -48})-[:PRECEDED_BY]->(:Year {year: -49})
```

**Usage:** Every temporally grounded entity or claim tethers to Year nodes via `STARTS_IN_YEAR`, `ENDS_IN_YEAR`, or `DURING`.

---

### **3.4.2 Period Classification (Tiered)**

Not all temporal spans are periods. Chrystallum uses a **four-tier classification**:

**Tier 1: Historical Periods** (keep as `:Period`)
- Extended spans (decades+)
- Widely used in historiography
- Coherent political/social/cultural patterns
- Examples: Migration Period, Dutch Golden Age, Viking Age

**Tier 2: Events / Phases** (relabel as `:Event`)
- Short duration (< 5-10 years)
- Wars, crises, campaigns
- Examples: Crisis of the Third Century, Reign of Terror, Phoney War

**Tier 3: Institutional Spans** (use `:InstitutionalSpan` or `:Period` with flag)
- Lifetimes of courts, offices, archives
- Administrative intervals, not historiographic periods
- Examples: Rehnquist Court, Birmingham pen trade

**Tier 4: Problematic Entries** (remove or reclassify)
- Disciplines masquerading as periods
- Suspicious date ranges
- Overly broad/vague spans

**Source:** Period data seeded from `Temporal/time_periods.csv` (Wikidata extraction) and `Temporal/periodo-dataset.csv` (PeriodO authority).

---

### **3.4.3 Faceted Periods (Stacked Timelines via Facet Vectors)**

**Vector Jump Pattern:** Periods link to Facet nodes enabling temporal vectors across analytical dimensions.

**Structure:**
```cypher
(:Period {label: "Late Republic", qid: "Q17167"})
  -[:HAS_POLITICAL_FACET]->
(:PoliticalFacet {label: "Roman Republic", unique_id: "POLITICALFACET_Q17167"})

(:Period {label: "Late Republic", qid: "Q17167"})
  -[:HAS_ECONOMIC_FACET]->
(:EconomicFacet {label: "Late Republican economy", unique_id: "ECONOMICFACET_Q17167E"})

(:Period {label: "Late Republic", qid: "Q17167"})
  -[:HAS_MILITARY_FACET]->
(:MilitaryFacet {label: "Imperial wars", unique_id: "MILITARYFACET_Q17167M"})
```

**Period Classification by Facet:**
- Political dimension: "Late Republic" = governance under republican institutions
- Economic dimension: "Late Republican economy" = transition to monetary economy
- Military dimension: "Imperial wars" = conquest phase military operations
- [13 other facet vectors...]

**Query Pattern:** Retrieve all periods for a culture grouped by facet, aligned via `STARTS_IN_YEAR`/`ENDS_IN_YEAR`/`IN_FACET_CATEGORY` to generate stacked timeline visualizations:

```cypher
MATCH (p:Period {culture: "Roman"})-[:STARTS_IN_YEAR]->(y:Year)
MATCH (p)-[:HAS_POLITICAL_FACET|:HAS_MILITARY_FACET|:HAS_ECONOMIC_FACET]->(f:Facet)
MATCH (f)-[:IN_FACET_CATEGORY]->(cat:FacetCategory)
RETURN y.year, cat.key, f.label
ORDER BY y.year, cat.key
// Result: stacked timeline with [Political][Military][Economic] rows per year
```

---

### **3.4.4 Authority Alignment (PeriodO, LCSH)**

Period nodes integrate with two external authorities:

**1. PeriodO (Temporal Period Authority):**
- Curated period definitions with URIs
- Properties: `authority = "PeriodO"`, `authority_uri = <PeriodO URI>`
- Enriches Period nodes with scholarly consensus boundaries

**2. LCSH (Library of Congress Subject Headings):**
- Maps periods to subject headings via `:SubjectConcept`
- Pattern: `(:Period)-[:ALIGNED_WITH]->(:SubjectConcept {authority_id: <LCSH ID>})`
- Enables library catalog interoperability

**Source Files:**
- `Temporal/periodo-dataset.csv`: PeriodO data
- `Temporal/time_periods.csv`: seed period set
- `Temporal/period_classification_decisions.csv`: period classification decisions

---

### **3.4.5 Event-Period-Year Wiring (Minimal Pattern)**

To avoid over-edging (e.g., long-running events creating thousands of edges), use **minimal temporal wiring**:

**Pattern:**
```cypher
(:Event {start_date: "-0049-01-10", end_date: "-0044-03-15"})
  -[:OCCURRED_DURING]->(:Period)
  -[:STARTS_IN_YEAR]->(:Year {year: -49})
  -[:ENDS_IN_YEAR]->(:Year {year: -44})
```

**Intermediate years** (e.g., -48, -47, -46, -45) are **not** stored as edges but expanded at query/UI time.

**Exception:** For specific UIs requiring fast year-by-year browsing, optionally materialize `ACTIVE_IN_YEAR` edges, but test scale carefully.

---

## **3.5 Schema Enforcement & Constraints**

### **3.5.1 Uniqueness Constraints**

```cypher
-- Core Identity
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE;

CREATE CONSTRAINT human_id_unique IF NOT EXISTS
FOR (h:Human) REQUIRE h.entity_id IS UNIQUE;

CREATE CONSTRAINT place_id_unique IF NOT EXISTS
FOR (p:Place) REQUIRE p.place_id IS UNIQUE;

CREATE CONSTRAINT claim_id_unique IF NOT EXISTS
FOR (c:Claim) REQUIRE c.claim_id IS UNIQUE;

-- External Authority Keys
CREATE CONSTRAINT qid_unique IF NOT EXISTS
FOR (e:Entity) REQUIRE e.qid IS UNIQUE;

CREATE CONSTRAINT viaf_id_unique IF NOT EXISTS
FOR (h:Human) REQUIRE h.viaf_id IS UNIQUE;
```

---

### **3.5.2 Architectural Decisions**

**1. SKOS Directionality: `BROADER_THAN` Only**
- **Rationale:** Reduces graph density by 50%. The inverse (`NARROWER_THAN`) is implied and handled at query time by traversing `<-[:BROADER_THAN]-`.
- **Decision:** Store only `BROADER_THAN` relationships in the graph.

**2. Facet Policy (Hybrid)**
- **Primary Facet:** Stored as property for speed (e.g., `Period.facet = "Political"`)
- **Complex Facets:** Stored as nodes for hierarchy (e.g., `(:Period)-[:HAS_FACET]->(:Facet {label: "Naval Warfare"})`)
- **Rationale:** Balances query performance with expressiveness.

---

## **3.6 Example Cypher Patterns**

### **Create a Human Entity**
```cypher
CREATE (p:Human {
  entity_id: "hum_000123",
  name: "Gaius Julius Caesar",
  qid: "Q1048",
  birth_date: "-0100-07-12",
  death_date: "-0044-03-15",
  gender: "male",
  viaf_id: "286265178",
  cidoc_crm_class: "E21_Person"
})
```

### **Link Human to Gens**
```cypher
MATCH (p:Human {qid: "Q1048"}), (g:Gens {label: "Julia"})
CREATE (p)-[:PART_OF_GENS]->(g)
```

### **Create an Event with Temporal and Spatial Context**
```cypher
MATCH (place:PlaceVersion {label: "Rubicon River (49 BCE)"}),
      (period:Period {label: "Roman Republic"}),
      (year_start:Year {year: -49})
CREATE (e:Event {
  entity_id: "evt_000987",
  label: "Caesar Crosses the Rubicon",
  qid: "Q159950",
  start_date: "-0049-01-10",
  event_type: "military_crossing",
  action_type: "deliberate_defiance",
  cidoc_crm_class: "E5_Event"
})
CREATE (e)-[:TOOK_PLACE_AT]->(place)
CREATE (e)-[:OCCURRED_DURING]->(period)
CREATE (e)-[:STARTS_IN_YEAR]->(year_start)
```

### **Link Work to SubjectConcept (Aboutness)**
```cypher
MATCH (w:Work {title: "Life of Caesar"}),
      (sc:SubjectConcept {authority_id: "sh85115055"})
CREATE (w)-[:ABOUT]->(sc)
```

---

# **4. Subject Layer**

## **4.0 Subject Layer Overview**

The **Subject Layer** provides the **conceptual backbone** of Chrystallum's ontology. It defines:

- The **SubjectConcept** node type (conceptual categories, topics, themes)
- The **facet system** (18 active analytical dimensions; see `Facets/facet_registry_master.json`)
- The **SKOS-like hierarchy** (polyhierarchical classification)
- The **multi-authority metadata model** (LCSH, FAST, LCC, Dewey, Wikidata, VIAF, GND)
- The **Topic Spine** (canonical curated hierarchy)
- The **CIP â†’ QID â†’ LCC â†’ LCSH â†’ FAST chain** (cross-authority alignment)
- The **Academic Discipline model**
- The **Entity â†’ Subject mapping rules**
- The **Work â†’ Subject aboutness model**
- The **Agent domain assignment logic**

**Core Principle:** There is **no separate Concept entity**â€”all conceptual categories are **SubjectConcepts**.

**Relationship to Entities:**

| Layer | Represents | Examples |
|-------|-----------|----------|
| **Entity Layer** | Things in the world | Caesar, Rome, Battle of Actium |
| **Subject Layer** | Concepts about the world | Roman politics, civil war, dictatorship |

---

## **4.0.1 Foundational Principles: Structure vs. Topics**

**CRITICAL DISTINCTION** (from ONTOLOGY_PRINCIPLES.md, see also ADR-002 in Appendix H):

### **LCC = Structure (ONE Path)**
- **Purpose:** Organizational backbone for classification
- **Pattern:** ONE entity gets ONE LCC assignment (primary classification)
- **Example:** Julius Caesar â†’ `DG` (Roman History)
- **Usage:** Agent routing, primary subject determination
- **Metaphor:** Library shelf location (one place)

### **FAST = Topics (MANY Tags)**
- **Purpose:** Semantic discovery across multiple dimensions
- **Pattern:** ONE entity gets MANY FAST assignments (faceted tagging)
- **Example:** Julius Caesar â†’ `Roman politics`, `Military leaders`, `Assassinations`, `Civil war`
- **Usage:** Cross-domain queries, thematic research
- **Metaphor:** Index entries (many keywords)

**Why This Matters:**
- **Prevents redundant hierarchies:** LCC provides the primary organizational path, FAST provides multi-dimensional discovery
- **Enables precision + recall:** LCC for focused classification, FAST for broad discovery
- **Supports agent specialization:** Agents can specialize by LCC class (structural expertise) or FAST topic (thematic expertise)

**Implementation:**
```cypher
// LCC: ONE primary classification
(:Human {entity_id: "hum_000123"})
  -[:HAS_PRIMARY_LCC]->(:SubjectConcept {lcc_class: "DG"})

// FAST: MANY topical tags
(:Human {entity_id: "hum_000123"})
  -[:HAS_SUBJECT_CONCEPT]->(:SubjectConcept {fast_id: "fst01234567"})
(:Human {entity_id: "hum_000123"})
  -[:HAS_SUBJECT_CONCEPT]->(:SubjectConcept {fast_id: "fst07654321"})
(:Human {entity_id: "hum_000123"})
  -[:HAS_SUBJECT_CONCEPT]->(:SubjectConcept {fast_id: "fst09876543"})
```

**Source:** `md/Architecture/ONTOLOGY_PRINCIPLES.md` (2025-12-26) â€” foundational architectural decision

---

## **4.1 SubjectConcept Node Schema**

### **Node Label**

```cypher
:SubjectConcept
```

### **Purpose**

Represents a conceptual category, topic, theme, or subject heading, including:
- Topical subjects (e.g., "Roman politics")
- Academic disciplines (e.g., "History", "Archaeology")
- LCSH/FAST headings
- LCC classes
- CIP categories
- Topic Spine nodes
- Facets

### **Required Properties**

| Property | Type | Example |
|----------|------|---------|
| `subject_id` | string | `"subj_000123"` |
| `label` | string | `"Romeâ€”Politics and governmentâ€”510â€“30 B.C."` |
| `facet` | string | `"POLITICAL"` (uppercase canonical key) |

**Facet Normalization Rule:**
- `facet` property values MUST match canonical keys from `Facets/facet_registry_master.json`
- All facet keys are UPPERCASE (e.g., `"POLITICAL"`, `"MILITARY"`, `"ECONOMIC"`, etc.; see Section 4.2 for complete list)
- Lowercase or mixed-case facet values are NOT valid (prevents case-collision bugs in queries)
- Rationale: Deterministic filtering, consistent routing, union-safe deduplication

### **Optional Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `authority_id` | string | `"sh85115055"` | LCSH ID |
| `fast_id` | string | `"fst01234567"` | FAST ID |
| `lcc_class` | string | `"DG"` | LCC class |
| `lcc_subclass` | string | `"DG209"` | LCC subclass |
| `cip_code` | string | `"22.01"` | CIP category (Classification of Instructional Programs) |
| `qid` | string | `"Q123456"` | Wikidata concept QID |
| `broader_label` | string | `"Roman history"` | For convenience |
| `narrower_labels` | array | `["Roman Republic"]` | For convenience |
| `discipline` | boolean | `true` | Flag for academic disciplines |

### **Required Edges**

| Relationship | Target | Notes |
|--------------|--------|-------|
| `BROADER_THAN` | SubjectConcept | SKOS broader relationship |

**Note:** Architectural decision (see Section 3.5.2) is to store **`BROADER_THAN` only** to reduce graph density by 50%. The inverse (`NARROWER_THAN`) is implied and handled at query time by traversing `<-[:BROADER_THAN]-`.

### **Optional Edges**

- `ALIGNED_WITH` â†’ SubjectConcept (cross-authority alignment)
- `HAS_FACET` â†’ Facet (complex facet hierarchies)
- `ABOUT_ENTITY` â†’ Entity (semantic grounding)
- `ABOUT_PERIOD` â†’ Period  
- `ABOUT_EVENT` â†’ Event
- `SUBJECT_OF` â†’ Claim (provenance)

---

## **4.2 Facets (17 Analytical Dimensions)**

Chrystallum uses **17 active facets** for multi-dimensional classification of entities and subjects.
Canonical source of truth: `Facets/facet_registry_master.json` (with tabular export at `Facets/facet_registry_master.csv`).
Temporal modeling is handled separately in Section 3.4.

1. **Geographic:** Spatial distribution and location
2. **Political:** Governance, power, authority
3. **Cultural:** Art, literature, customs, identity
4. **Technological:** Tools, methods, innovations
5. **Religious:** Beliefs, practices, institutions
6. **Economic:** Trade, production, finance
7. **Military:** Warfare, tactics, organization
8. **Environmental:** Climate, geography, resources
9. **Demographic:** Population, migration, ethnicity
10. **Intellectual:** Philosophy, science, education
11. **Scientific:** Technical knowledge, inquiry
12. **Artistic:** Visual arts, architecture, aesthetics
13. **Social:** Class, family, social structures
14. **Linguistic:** Languages, writing systems
15. **Archaeological:** Material culture, excavation
16. **Diplomatic:** Treaties, alliances, negotiations

### **Facet Node Schema**

**Node Label:** `:Facet`

**Required Properties:**
| Property | Type | Example |
|----------|------|---------|
| `facet_id` | string | `"facet_political"` |
| `label` | string | `"Political"` |

**Required Edges:**
- `HAS_FACET` â†’ SubjectConcept (for complex facet hierarchies)

### **Facet Policy (Hybrid Approach)**

**Primary Facet (Property):** Stored as property for fast queries
```cypher
Period {facet: "Political"}
```

**Complex Facets (Nodes):** Stored as nodes for hierarchical facets
```cypher
(:Period)-[:HAS_FACET]->(:Facet {label: "Naval Warfare"})
```

**Rationale:** Balances query performance with expressiveness.

---

## **4.3 SKOS-Like Hierarchy**

SubjectConcepts form a **polyhierarchical** structure using SKOS-inspired relationships:

### **Relationships**

- `BROADER_THAN`: Parent concept (stored)
- `NARROWER_THAN`: Child concept (implied, query via inverse)
- `RELATED_TO`: Associative relationship (optional)

### **Example Hierarchy**

```
"Ancient history"
    BROADER_THAN
        "Roman history"
            BROADER_THAN
                "Roman Republic"
                "Roman Empire"
```

### **Cypher Example**

```cypher
MATCH (parent:SubjectConcept {label: "Roman history"})
MATCH (child:SubjectConcept {label: "Roman Republic"})
CREATE (parent)-[:BROADER_THAN]->(child)

// Query inverse (narrower concepts)
MATCH (parent:SubjectConcept {label: "Roman history"})
      <-[:BROADER_THAN]-(child)
RETURN child.label
```

---

## **4.4 Multi-Authority Metadata Model**

Each SubjectConcept can carry metadata from **multiple authority standards** for cross-domain interoperability:

| Authority | Property | Example | Purpose |
|-----------|----------|---------|---------|
| **LCSH** | `authority_id` | `"sh85115055"` | Library catalog compatibility |
| **FAST** | `fast_id` | `"fst01234567"` | Faceted subject headings |
| **LCC** | `lcc_class`, `lcc_subclass` | `"DG"`, `"DG209"` | Classification backbone |
| **CIP** | `cip_code` | `"22.01"` | Academic program alignment |
| **Wikidata** | `qid` | `"Q12107"` | Linked open data |
| **Dewey** | `dewey_decimal` | `"937"` | Library classification (optional) |
| **VIAF** | `viaf_id` | `"123456789"` | Authority control (optional) |
| **GND** | `gnd_id` | `"4076899-5"` | German National Library (optional) |

**Authority Precedence for SubjectConcepts (Normalization Rule):**

**Tier 1 (Preferred):**
- LCSH (Library of Congress Subject Headings) - established scholarly standard; query-optimized
- FAST (Faceted Application of Subject Terminology) - complementary faceted tagging for cross-domain discovery

**Tier 2 (Secondary):**
- LCC (Library of Congress Classification) - structural backbone for primary classification only
- CIP (Classification of Instructional Programs) - academic discipline alignment

**Tier 3 (Tertiary):**
- Wikidata (QID) - linked open data reference; use when LCSH/FAST coverage gaps exist
- Dewey, VIAF, GND - legacy/supplementary authorities

**Implementation Rule:**
1. When creating SubjectConcept: Prefer LCSH/FAST → LCC/CIP → Wikidata → other
2. When updating: Enrich with lower-tier authorities without replacing higher-tier mappings
3. When querying: Check Tier 1 first; fall through to Tier 3 if needed

**Rationale:** LCSH/FAST are domain-optimized for historical scholarship; Wikidata as fallback; mirrors Entity Layer authority policy (Material/Object precedence)

### **Purpose**

- Unify legacy cataloging systems
- Support agent domain assignment (Section 5)
- Support claim classification (Section 6)
- Enable authority crosswalks

---

## **4.5 Entity â†’ Subject Mapping Rules**

Entities link to SubjectConcepts to establish classification and discoverability.

### **Mapping Pattern**

```cypher
(entity)-[:HAS_SUBJECT_CONCEPT]->(subjectConcept)
```

### **Mapping Rules by Entity Type**

| Entity Type | Mapping Strategy | Example |
|-------------|------------------|---------|
| **Human** | Biography, occupation, era, associated events | Caesar â†’ "Roman politics", "Military leaders", "Dictators" |
| **Event** | Event type, participants, location, historical period | Battle of Actium â†’ "Naval battles", "Roman civil wars", "Greco-Roman warfare" |
| **Place** | Geographic hierarchy, cultural regions | Rome â†’ "Ancient cities", "Italian history", "Capital cities" |
| **Period** | Historical classification, culture, facet | Roman Republic â†’ "Ancient Rome", "Republican government", "Classical period" |
| **Work** | Aboutness (see Section 4.6) | Plutarch's *Life of Caesar* â†’ "Roman biography", "Classical literature" |
| **Organization** | Organization type, function, domain | Roman Senate â†’ "Legislative bodies", "Roman institutions", "Republican government" |

### **Cypher Example**

```cypher
MATCH (p:Human {qid: "Q1048"})
MATCH (sc:SubjectConcept {authority_id: "sh85115055"})
CREATE (p)-[:HAS_SUBJECT_CONCEPT]->(sc)
```

---

## **4.6 Work â†’ Subject Aboutness Model**

Works (texts, inscriptions, scholarship) link to SubjectConcepts via the **aboutness** relationship to support RAG retrieval and claim provenance.

### **Aboutness Pattern**

```cypher
(work)-[:ABOUT]->(subjectConcept)
```

### **Example**

```cypher
MATCH (w:Work {title: "Life of Caesar"})
MATCH (sc:SubjectConcept {label: "Roman politics"})
CREATE (w)-[:ABOUT]->(sc)
```

### **Aboutness Supports**

- **RAG retrieval:** Find relevant texts by subject (Section 5.5)
- **Claim provenance:** Trace claims to source subjects (Section 6.2)
- **Agent training:** Define agent expertise domains (Section 5.3)

---

## **4.7 Topic Spine (Canonical Curated Hierarchy)**

The **Topic Spine** is a **canonical, curated hierarchy** of SubjectConcepts that:

- Spans all 16 active facets
- Provides a stable conceptual backbone
- Supports agent routing (Section 5.6)
- Supports claim classification (Section 6.2)
- Serves as the primary navigation structure

### **Topic Spine Structure**

```
History
    Ancient History
        Roman History
            Roman Republic
                Roman Politics
                    Civil War
                        Caesar's Dictatorship
```

### **Node Label** (Optional)

Can use `:TopicSpine` label or property flag:
```cypher
SubjectConcept {is_spine_node: true}
```

### **Spine Edges**

- `SPINE_PARENT`: Explicit spine hierarchy
- `SPINE_CHILD`: Inverse

---

## **4.8 CIP â†’ QID â†’ LCC â†’ LCSH â†’ FAST Chain**

This is the **cross-authority alignment pipeline** for subject normalization and agent domain inference.

### **Chain Flow**

```
CIP category (modern academic classification)
    â†“ maps to
Wikidata QID (linked open data concept)
    â†“ maps to
LCC class/subclass (library classification backbone)
    â†“ maps to
LCSH heading (library subject authority)
    â†“ maps to
FAST heading (faceted subject tags)
```

### **Example Mapping**

| Layer | Example | ID |
|-------|---------|-----|
| **CIP** | History | 22.01 |
| **QID** | History (concept) | Q11772 |
| **LCC** | World History | D |
| **LCSH** | History | sh85061212 |
| **FAST** | History | fst00958235 |

### **Purpose**

- Unify modern academic classification (CIP) with library standards (LCC/LCSH)
- Enable agent domain assignment via multiple authority paths
- Support subject normalization across different source materials

---

## **4.9 Academic Discipline Model**

Academic disciplines are modeled as SubjectConcepts with special properties.

### **Discipline Schema**

**Properties:**
- `facet: "Intellectual"`
- `discipline: true`

**Examples:**
- History
- Archaeology
- Classics
- Political Science
- Economics
- Art History
- Philology

### **Discipline Edges**

- `BROADER_THAN` â†’ parent discipline (e.g., History â†’ Ancient History)
- `RELATED_TO` â†’ adjacent disciplines (e.g., History â†” Archaeology)

### **Usage**

- Agent specialization by discipline
- Claim review routing by disciplinary expertise (Section 6.3)
- Interdisciplinary query support

### **Discipline Flag Usage in SFA Training Initialization**

**Critical Pattern:** When a SubjectFacetAgent (SFA) is instantiated for a discipline + facet pair, the `discipline: true` flag identifies canonical root concepts for ontology building.

**Initialization Algorithm:**
```
1. Query: Find all SubjectConcepts where discipline=true AND facet=TARGET_FACET
2. Root Node Selection: SFA adopts matched concepts as roots
3. Ontology Building: SFA traverses via BROADER_THAN* to build hierarchical ontology
```

**Example:** MilitarySFA with facet MILITARY finds root concepts like "Military Science", then builds: Military Science → Naval Warfare → Trireme Tactics → ...

**Rationale:**
- `discipline: true` marks canonical entry points for agent specialization
- Prevents SFAs from adopting arbitrary concepts as roots
- Gates SFA scope (e.g., Military SFA doesn't treat "Economic History" as root)
- Enables reproducible SFA initialization across sessions
- Supports disciplinary curriculum alignment (CIP codes → discipline roots)

**See Also:**
- Section 5.1: Agent domain assignment (`OWNS_DOMAIN` edges to SubjectConcepts)
- Section 5.2: Subject Agents (domain expertise patterns)
- REAL_AGENTS_DEPLOYED.md: Current SFA instantiation configurations

---

## **4.10 LCC Official Classification Structure**

The **Library of Congress Classification (LCC)** provides the primary **organizational backbone** for Chrystallum.

### **Why LCC?** (See ADR-003, Appendix H)
- **100% coverage** of history domain (vs. Dewey 12.3%)
- **Deep granularity** for ancient history (DG class for Roman history)
- **Institutional standard** for research libraries
- **Authority alignment** with LCSH and MARC

### **LCC Classes**

| Class | Domain |
|-------|--------|
| A | General Works |
| B | Philosophy, Psychology, Religion |
| C | Auxiliary Sciences of History |
| D | World History |
| Eâ€“F | American History |
| G | Geography, Anthropology |
| H | Social Sciences |
| J | Political Science |
| K | Law |
| L | Education |
| M | Music |
| N | Fine Arts |
| P | Language & Literature |
| Q | Science |
| R | Medicine |
| S | Agriculture |
| T | Technology |
| U | Military Science |
| V | Naval Science |
| Z | Bibliography, Library Science |

### **LCC Subclasses (Example: Roman History)**

| Subclass | Coverage |
|----------|----------|
| DG | Italy, Roman History |
| DG11-365 | Italy (general) |
| DG51-190 | Ancient Italy, Rome to 476 CE |
| DG201-365 | Medieval & Modern Italy |

### **LCC Mapping to SubjectConcepts**

```cypher
(subject:SubjectConcept {label: "Roman Republic"})
  -[:HAS_LCC_CLASS]->(:LCC {class: "DG", subclass: "DG83"})
```

---

## **4.11 Agent Domain Assignment via Subject Layer**

Agents define their expertise domains through connections to SubjectConcepts (see Section 5 for details).

### **Domain Definition Pattern**

```cypher
(agent:Agent)-[:OWNS_DOMAIN]->(subjectConcept:SubjectConcept)
```

### **Example**

```cypher
MATCH (agent:Agent {agent_id: "roman_republic_agent"})
MATCH (sc1:SubjectConcept {label: "Roman Republic"})
MATCH (sc2:SubjectConcept {label: "Roman politics"})
MATCH (sc3:SubjectConcept {label: "Civil war"})
CREATE (agent)-[:OWNS_DOMAIN]->(sc1)
CREATE (agent)-[:OWNS_DOMAIN]->(sc2)
CREATE (agent)-[:OWNS_DOMAIN]->(sc3)
```

### **Domain Inference Paths**

Agents can be assigned domains via:
1. **Direct SubjectConcept assignment:** Explicit domain declaration
2. **LCC class coverage:** All SubjectConcepts with specific LCC class
3. **CIP category alignment:** All SubjectConcepts with CIP code
4. **Topic Spine path:** All descendants of a spine node
5. **Facet membership:** All SubjectConcepts with specific facet

---

## **4.12 Subject Evolution & Versioning**

SubjectConcepts evolve over time as vocabularies update and scholarship advances.

### **Versioning Properties**

| Property | Type | Purpose |
|----------|------|---------|
| `created_at` | ISO 8601 string | Creation timestamp |
| `updated_at` | ISO 8601 string | Last modification |
| `deprecated` | boolean | Deprecated flag |
| `replaced_by` | string | Successor subject_id |

### **Evolution Patterns**

1. **New concepts added:** Emerging fields, refined terminology
2. **Deprecated concepts merged:** Consolidation of redundant terms
3. **Authority metadata updated:** New QID, FAST ID, etc.
4. **Crosswalks refined:** Improved LCC/LCSH/FAST alignment

---

## **4.13 Cypher Examples**

### **Create a SubjectConcept**

```cypher
CREATE (sc:SubjectConcept {
  subject_id: "subj_000123",
  label: "Roman politics",
  facet: "Political",
  authority_id: "sh85115055",
  fast_id: "fst01234567",
  lcc_class: "DG",
  qid: "Q12345",
  discipline: false
})
```

### **Link SubjectConcept to LCC Class**

```cypher
MATCH (sc:SubjectConcept {label: "Roman history"})
MATCH (lcc:LCC {class: "DG"})
CREATE (sc)-[:HAS_LCC_CLASS]->(lcc)
```

### **Map Work to SubjectConcept (Aboutness)**

```cypher
MATCH (w:Work {title: "Life of Caesar"})
MATCH (sc:SubjectConcept {label: "Roman Republic"})
CREATE (w)-[:ABOUT]->(sc)
```

### **Agent Domain Assignment**

```cypher
MATCH (agent:Agent {agent_id: "roman_republic_agent"})
MATCH (sc:SubjectConcept {label: "Roman Republic"})
CREATE (agent)-[:OWNS_DOMAIN]->(sc)
```

### **Query BROADER_THAN Hierarchy**

```cypher
// Get all narrower concepts
MATCH (parent:SubjectConcept {label: "Roman history"})
      -[:BROADER_THAN*]->(child)
RETURN child.label, child.lcc_class
```

### **Cross-Authority Lookup**

```cypher
// Find SubjectConcept by multiple authorities
MATCH (sc:SubjectConcept)
WHERE sc.authority_id = "sh85115055"
   OR sc.fast_id = "fst01234567"
   OR sc.qid = "Q12345"
RETURN sc
```

---

# **5. Agent Layer**

## **5.0 Agent Layer Overview**

The **Agent Layer** defines the **intelligent actors** in Chrystallum that perform classification, extraction, reasoning, validation, and coordination.

**Agents** in Chrystallum are **not** LLMsâ€”they are **graph-native reasoning actors** with:
- **Explicit domain scopes** (defined via Subject Layer)
- **Explicit memory** (cached knowledge, previous decisions)
- **Explicit reasoning traces** (transparent decision logic)
- **Explicit retrieval contexts** (RAG patterns)
- **Explicit claim generation and review protocols** (quality assurance)

### **Agent Types**

1. **Subject Agents:** Experts in conceptual domains (e.g., "Roman Republic Specialist")
2. **Entity Agents:** Experts in entity types (e.g., "Event Validator")
3. **Coordinator Agents:** Orchestrators of multi-agent workflows

### **Agent Responsibilities**

- Classify entities and works to SubjectConcepts
- Generate claims from source material (Section 6)
- Review and validate claims (Section 6.3)
- Perform historical reasoning over knowledge graph
- Retrieve evidence via RAG patterns
- Maintain memory of previous decisions
- Coordinate consensus among multiple agents
- Route tasks across the agent ecosystem

---

## **5.1 Agent Node Schema**

### **Node Label**

```cypher
:Agent
```

### **Required Properties**

| Property | Type | Example |
|----------|------|---------|
| `agent_id` | string | `"roman_republic_agent"` |
| `label` | string | `"Roman Republic Specialist"` |
| `agent_type` | string | `"subject"`, `"entity"`, `"coordinator"` |

### **Optional Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `description` | string | `"Expert in Roman political history"` | Human-readable description |
| `confidence_calibration` | float | `0.92` | Calibration factor for confidence scores |
| `specialization_level` | string | `"high"`, `"medium"`, `"low"` | Generalist vs specialist |
| `created_at` | ISO 8601 string | `"2026-02-12T10:00:00Z"` | Creation timestamp |
| `version` | string | `"v1.2"` | Agent version identifier |

### **Required Edges**

- `OWNS_DOMAIN` â†’ SubjectConcept (domain expertise)
- `REVIEWED` â†’ Review (validation history)
- `MADE_CLAIM` â†’ Claim (claim authorship)

### **Optional Edges**

- `TRAINED_ON` â†’ Work (training corpus)
- `INCLUDES_CONCEPT` â†’ SubjectConcept (expanded domain)
- `MEMORY_OF` â†’ AgentMemory (cached knowledge)
- `PERFORMED_BY` â†’ Synthesis (reasoning activity)

---

## **5.2 Subject Agents**

**Subject Agents** specialize in **conceptual domains** defined by SubjectConcepts, LCC classes, CIP categories, Topic Spine nodes, and facets.

### **Example**

```
roman_republic_agent (Subject Agent)
    OWNS_DOMAIN â†’ "Roman Republic" (SubjectConcept)
    OWNS_DOMAIN â†’ "Roman politics" (SubjectConcept)
    OWNS_DOMAIN â†’ "Civil war" (SubjectConcept)
```

### **Responsibilities**

- Classify claims by subject
- Review claims within domain expertise
- Generate interpretive claims (synthesis, analysis)
- Detect logical fallacies and inconsistencies
- Perform scholarly synthesis across conflicting claims

### **Cypher Example**

```cypher
CREATE (agent:Agent {
  agent_id: "roman_republic_agent",
  label: "Roman Republic Specialist",
  agent_type: "subject",
  description: "Expert in Roman Republican political history (510-27 BCE)",
  confidence_calibration: 0.93,
  specialization_level: "high",
  created_at: "2026-02-12T10:00:00Z"
})

MATCH (sc1:SubjectConcept {label: "Roman Republic"})
MATCH (sc2:SubjectConcept {label: "Roman politics"})
CREATE (agent)-[:OWNS_DOMAIN]->(sc1)
CREATE (agent)-[:OWNS_DOMAIN]->(sc2)
```

---

## **5.3 Entity Agents**

**Entity Agents** specialize in **entity types** and validate entity-level properties.

### **Example**

```
event_agent (Entity Agent)
    OWNS_ENTITY_TYPE â†’ Event
```

### **Responsibilities**

- Validate entity properties (dates, names, identifiers)
- Detect entity-level inconsistencies
- Classify events by type (battle, treaty, election, etc.)
- Support claim grounding (ensure entities exist before creating claims)

### **Cypher Example**

```cypher
CREATE (agent:Agent {
  agent_id: "event_validator_agent",
  label: "Event Validator",
  agent_type: "entity",
  description: "Validates historical event properties and classifications",
  confidence_calibration: 0.95,
  specialization_level: "medium"
})
```

---

## **5.4 Agent Granularity Strategy (Two-Level Architecture)**

**CRITICAL DESIGN DECISION** (see ADR-004, Appendix H):

Chrystallum uses a **two-level agent routing strategy** to balance expertise precision with scalability.

### **Level 1: FAST Broad Topics (22 Agents)**

**Purpose:** Initial routing to general domain experts

**Example Topics:**
- Ancient History
- Roman History
- Military History
- Political History
- Religious History

**Agent Count:** ~22 broad-topic agents covering major historical domains

**Routing Mechanism:**
```cypher
// User query: "Caesar crosses Rubicon"
// Topic classification: "Roman History" (FAST)
// â†’ Route to roman_history_agent
```

### **Level 2: LCC Subdivisions (Dynamic Routing)**

**Purpose:** Fine-grained expertise via LCC classification within broad topics

**Example LCC Classes (Roman History):**
- DG51-190: Ancient Italy, Rome to 476 CE
- DG83: Roman Republic (510-27 BCE)
- DG290-365: Medieval & Modern Italy

**Agent Count:** Dynamicâ€”agents specialize in LCC subclasses as needed

**Routing Mechanism:**
```cypher
// Within roman_history_agent domain
// LCC classification: DG83 (Roman Republic)
// â†’ Route to roman_republic_specialist_agent (LCC DG83)
```

### **Why Two-Level?**

**Problem:** Single-level routing creates agent proliferation
- Too broad: Agents lack expertise (1 agent for all history)
- Too narrow: Too many agents (100+ specialist agents)

**Solution:** Two-level hierarchy
- **FAST (Level 1):** 22 broad agents (manageable, expert routing)
- **LCC (Level 2):** Dynamic specialists (precise expertise, scales with content)

**Benefits:**
- Prevents agent proliferation (22 base agents, not 100+)
- Maintains deep expertise (LCC specialists for narrow domains)
- Scales naturally (add LCC specialists as content grows)
- Familiar to scholars (FAST and LCC are standard authorities)

**Source:** `md/Architecture/Subject_Agent_Granularity_Strategy.md` (2025-12-26)

---

## **5.5 SubjectConceptAgent â†" SubjectFacetAgent Coordination (SCA â†" SFA)**

**CRITICAL ARCHITECTURAL PATTERN** (Finalized February 15, 2026):

Chrystallum implements a **two-phase agent coordination model** with **selective intelligent routing** for claim creation and multi-facet enrichment.

**Reference:** `md/Agents/SCA/SCA_SFA_ROLES_DISCUSSION.md` (complete specification)

### **5.5.1 Agent Types & Roles**

**SubjectConceptAgent (SCA):**
- **Role:** Seed agent & intelligent orchestrator
- **Responsibilities:**
  * Un-faceted exploration (Phase 1: breadth-first)
  * Spawns SubjectFacetAgents (SFAs) on-demand
  * Routes training data to SFAs (Discovery Mode)
  * **Evaluates claims:** Abstract concepts vs Concrete events
  * **Selective routing:** Queues claims for multi-facet review ONLY when warranted
  * Generates bridge claims connecting domains
  * Manages claim lifecycle & convergence detection

**SubjectFacetAgent (SFA):**
- **Role:** Domain-specific experts (18 facets)
- **Canonical Facets (UPPERCASE):** ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, CULTURAL, DEMOGRAPHIC, DIPLOMATIC, ECONOMIC, ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC, MILITARY, POLITICAL, RELIGIOUS, SCIENTIFIC, SOCIAL, TECHNOLOGICAL, COMMUNICATION
- **Registry:** Facets/facet_registry_master.json (authoritative source)
- **Responsibilities:**
  * **Training Phase:** Build domain ontologies independently (abstract concepts)
  * **Perspective Phase:** Analyze concrete claims when queued by SCA
  * Create Claim nodes (cipher-based) + FacetPerspective nodes
  * Inherit all FacetAgent capabilities (Steps 1-5 methods)
  * Stay within facet domain (no cross-domain claim creation)

### **5.5.2 Two-Phase Workflow**

**Phase 1: Training Mode (Independent Domain Study)**

SFAs build subject ontologies for their disciplines **independently**, without cross-facet collaboration.

**Process:**
```
SCA:
  → Spawn all SFAs (Political, Military, Economic, etc.)
  → Route discipline training data to each SFA
  → Collect claims from all SFAs

SFAs (Independent Work):
  → Study discipline (Political Science, Military History, etc.)
  → Build domain ontology (abstract concepts)
  → Create Claim nodes + FacetPerspectives
  → Return claim ciphers to SCA

SCA (Accept All):
  → Receive training claims
  → Evaluate: Are these abstract domain concepts? (YES)
  → Decision: Accept as-is (NO QUEUE to other SFAs)
  → Integrate into graph
```

**Example Training Claims (NO CROSS-FACET REVIEW):**
```
Political SFA:
  → "Senate held legislative authority in Roman Republic"
  → Type: Abstract political concept
  → SCA evaluation: Abstract domain concept → Accept as-is (no queue)

Military SFA:
  → "Legion composed of cohorts and maniples"
  → Type: Abstract military structure
  → SCA evaluation: Abstract domain concept → Accept as-is (no queue)

Economic SFA:
  → "Roman economy based on agricultural production"
  → Type: Abstract economic principle
  → SCA evaluation: Abstract domain concept → Accept as-is (no queue)
```

**Rationale:** These are **disciplinary ontology claims**, not concrete historical events. Political, Military, and Economic SFAs do not need to review each other's abstract domain concepts.

---

**Phase 2: Operational Mode (Selective Multi-Facet Collaboration)**

SFAs encounter **concrete entities/events**. SCA evaluates each claim for multi-facet potential and **selectively queues** to relevant SFAs only.

**Process:**
```
SFA creates concrete claim:
  → Claim cipher: "claim_abc123..."
  → Claim text: "Caesar was appointed dictator in 49 BCE"
  → FacetPerspective: political
  → Returns cipher to SCA

SCA evaluates claim:
  1. Type: Concrete historical event (not abstract concept)
  2. Entities: Caesar (Q1048), Dictator office, 49 BCE
  3. Multi-domain potential: YES

SCA relevance scoring:
  → Military SFA: 0.9 (Caesar = commander) → QUEUE
  → Economic SFA: 0.8 (dictator = treasury control) → QUEUE
  → Cultural SFA: 0.3 (minor impact) → SKIP
  → Religious SFA: 0.2 (no dimension) → SKIP
  → Scientific SFA: 0.1 (irrelevant) → SKIP

SCA decision: Queue to Military + Economic ONLY

Military SFA (Perspective Mode):
  → Receives: claim_cipher="claim_abc123..."
  → Analyzes from military perspective
  → Creates FacetPerspective (military angle)
  → Returns: perspective_id="persp_002"

Economic SFA (Perspective Mode):
  → Receives: claim_cipher="claim_abc123..."
  → Analyzes from economic perspective
  → Creates FacetPerspective (economic angle)
  → Returns: perspective_id="persp_003"

Result:
  1 Claim (cipher="claim_abc123...")
  + 3 FacetPerspectives (political, military, economic)
  Consensus: AVG(0.95, 0.90, 0.88) = 0.91
```

### **5.5.3 Claim Architecture: Cipher + Star Pattern**

**Claims are star pattern subgraphs**, not isolated nodes.

**Claim Cipher (Content-Addressable ID):**
```python
claim_cipher = Hash(
    source_work_qid +           # Where claim came from
    passage_text_hash +          # Exact text
    subject_entity_qid +         # Who/what it's about
    relationship_type +          # What relationship
    temporal_data +              # When
    confidence_score +           # Initial confidence
    extractor_agent_id +         # Which SFA created it
    extraction_timestamp         # When created
)
# Result: "claim_abc123..." (unique cipher)
```

**Benefit:** Two SFAs discovering SAME claim → SAME cipher → Single Claim node (automatic deduplication)

**Star Pattern Structure:**
```
                    (Claim: cipher="claim_abc123...")
                              â"‚
         â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¼â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
         â"‚                        â"‚                        â"‚
    [PERSP_ON]              [PERSP_ON]              [PERSP_ON]
         â"‚                        â"‚                        â"‚
         â–¼                        â–¼                        â–¼
   (FacetPerspective:    (FacetPerspective:    (FacetPerspective:
    Political)            Military)             Economic)
```

**FacetPerspective Node (NEW NODE TYPE):**
```cypher
(:FacetPerspective {
  perspective_id: "persp_001",
  facet: "political",
  parent_claim_cipher: "claim_abc123...",
  facet_claim_text: "Caesar challenged Senate authority",
  confidence: 0.95,
  source_agent_id: "political_sfa_001",
  timestamp: "2026-02-15T10:00:00Z",
  reasoning: "Dictatorship violated Republican norms"
})-[:PERSPECTIVE_ON]->(Claim {cipher: "claim_abc123..."})
```

**Why FacetPerspective instead of separate claims?**
- âœ… **Single source of truth:** One Claim node (via cipher deduplication)
- âœ… **Multi-facet enrichment:** Multiple perspectives attached
- âœ… **Consensus calculation:** AVG(all perspective confidences)
- âœ… **Clear semantics:** Claim = base assertion, Perspective = facet interpretation

### **5.5.4 SCA Routing Criteria (5-Criteria Framework)**

**How SCA determines which claims warrant cross-facet review:**

**Criterion 1: Abstract vs Concrete Detection**
- **Abstract domain concepts** → NO QUEUE (accept as-is)
  * Theoretical frameworks ("Senate legislative authority")
  * Discipline-specific methods ("Manipular tactics")
  * General principles ("Agricultural economy base")
- **Concrete events/entities** → EVALUATE FOR QUEUE
  * Specific historical events ("Caesar crossed Rubicon")
  * Named individuals with roles ("Caesar appointed dictator")
  * Dated occurrences ("49 BCE")

**Criterion 2: Multi-Domain Relevance Scoring (0-1.0 scale)**
- **High Relevance (0.8-1.0)** → Queue to SFA
- **Medium Relevance (0.5-0.7)** → Queue to SFA
- **Low Relevance (0.0-0.4)** → Do NOT queue

**Example: "Caesar was appointed dictator in 49 BCE"**
```
Political SFA (creator): 1.0 (created the claim)
Military SFA: 0.9 (Caesar = commander, dictator = supreme command)
Economic SFA: 0.8 (dictator = treasury control, state finances)
Cultural SFA: 0.3 (minor cultural impact, not primary)
Religious SFA: 0.2 (no significant religious dimension)
Scientific SFA: 0.1 (irrelevant to scientific domain)

SCA Decision:
→ Queue to: Military (0.9), Economic (0.8)
→ Skip: Cultural (0.3), Religious (0.2), Scientific (0.1)
```

**Criterion 3: Entity Type Detection**
- Query Wikidata P31 (instance of)
- Map entity types to facet relevance:
  * Q5 (Human) → Political, Military, Cultural potential
  * Q198 (War) → Military, Political, Economic potential
  * Q216353 (Battle) → Military, Geographic potential

**Criterion 4: Conflict Detection**
- Date discrepancies → Queue for synthesis
- Attribute conflicts → Queue for synthesis
- Relationship disputes → Queue for synthesis

**Criterion 5: Existing Perspectives Check**
```cypher
MATCH (p:FacetPerspective)-[:PERSPECTIVE_ON]->(c:Claim {cipher: $cipher})
RETURN COLLECT(p.facet) AS existing_facets
// Only queue to facets NOT in existing_facets
```

**Complete Routing Pseudocode:**
```python
def evaluate_claim_for_queue(claim: Claim, source_facet: str) -> Dict[str, float]:
    # Step 1: Check if abstract concept
    if is_abstract_concept(claim):
        return {}  # No queue
    
    # Step 2: Extract entities
    entities = extract_entities(claim.text)
    
    # Step 3: Score relevance to each facet
    relevance_scores = {}
    for facet in ALL_FACETS:
        if facet == source_facet:
            continue  # Skip source facet
        
        score = 0.0
        for entity in entities:
            entity_type = get_entity_type(entity.qid)
            score += calculate_relevance(entity_type, facet)
        
        relevance_scores[facet] = score / len(entities)
    
    # Step 4: Check existing perspectives
    existing_facets = get_existing_perspectives(claim.cipher)
    
    # Step 5: Filter by threshold
    queue_targets = {
        facet: score 
        for facet, score in relevance_scores.items()
        if score >= 0.5 and facet not in existing_facets
    }
    
    return queue_targets
```

### **5.5.5 Benefits & Implementation Status**

**Benefits:**
- âœ… **Efficient Collaboration:** Only concrete/multi-domain claims get cross-facet review
- âœ… **Independent Learning:** SFAs build domain ontologies without interference
- âœ… **Selective Enrichment:** Multi-facet analysis applied where it adds value
- âœ… **SCA Intelligence:** Orchestrator makes informed routing decisions
- âœ… **Automatic Deduplication:** Cipher ensures single Claim node per unique assertion
- âœ… **Consensus Calculation:** Multiple perspectives averaged for confidence

**Implementation Status (as of 2026-02-15):**
- âœ… Architecture documented (md/Agents/SCA/SCA_SFA_ROLES_DISCUSSION.md)
- âœ… Workflow models compared (CLAIM_WORKFLOW_MODELS.md)
- âœ… Routing criteria specified (5 criteria with examples)
- âœ… FacetPerspective pattern defined
- âœ… Cipher-based deduplication documented
- â³ FacetPerspective node schema (add to NODE_TYPE_SCHEMAS.md)
- â³ SCA claim evaluation implementation
- â³ SCA relevance scoring implementation
- â³ FacetPerspective creation in SFA
- â³ Selective queue logic in SCA

**References:**
- Complete specification: `md/Agents/SCA/SCA_SFA_ROLES_DISCUSSION.md`
- Workflow comparison: `CLAIM_WORKFLOW_MODELS.md`
- Military SFA methodology: `Facets/MILITARY_SFA_ONTOLOGY_METHODOLOGY.md`

---

## **5.6 Coordinator Agents**

**Coordinator Agents** orchestrate multi-agent workflows, consensus building, and claim promotion.

### **Example**

```
claims_coordinator
    agent_type: "coordinator"
```

### **Responsibilities**

- Identify claims needing review
- Route claims to appropriate subject/entity agents
- Route claims to facet-specialist agents (Section 3.2.6, facet assessment workflow; Section 5.5, SCA â†" SFA coordination)
- Compute `consensus_score` from multiple reviews
- Update `claim.status` based on validation results
- Trigger claim promotion to canonical graph (Section 6.9)
- Synthesize conflicting claims (Section 6.7)

### **Facet-Based Agent Assignment** ðŸŸ¡ **NEW**

**Agent Specialization by Facet Category:**

Each agent specializes in ONE facet category and evaluates claims from that dimensional perspective.

```cypher
// Agent specialization assignment
CREATE (agent:Agent {
  agent_id: "AGENT_POLITICAL_V1",
  label: "Political Historian Agent",
  agent_type: "facet_specialist",
  specialization_facet: "PoliticalFacet",
  description: "Evaluates claims from political/governance dimension"
})

// Link agent to facet category it owns
MERGE (agent)-[:OWNS_CATEGORY]->(:FacetCategory {key: "POLITICAL"})
```

**Agent Roster (18 Facet-Specialists):**

| Agent ID | Specialization | Facet Category | Scope |
|----------|---|---|---|
| AGENT_POLITICAL_V1 | Political | States, empires, governance | Evaluates political implications |
| AGENT_MILITARY_V1 | Military | Warfare, tactics, strategy | Evaluates military accuracy |
| AGENT_ECONOMIC_V1 | Economic | Trade, production, finance | Evaluates economic context |
| AGENT_CULTURAL_V1 | Cultural | Art, customs, identity | Evaluates cultural dimensions |
| AGENT_RELIGIOUS_V1 | Religious | Beliefs, practices, institutions | Evaluates religious aspects |
| AGENT_INTELLECTUAL_V1 | Intellectual | Philosophy, thought | Evaluates intellectual context |
| AGENT_SCIENTIFIC_V1 | Scientific | Scientific paradigms | Evaluates scientific validity |
| AGENT_ARTISTIC_V1 | Artistic | Art, architecture, aesthetics | Evaluates artistic authenticity |
| AGENT_SOCIAL_V1 | Social | Social structures, class | Evaluates social implications |
| AGENT_DEMOGRAPHIC_V1 | Demographic | Population, migration | Evaluates demographic accuracy |
| AGENT_ENVIRONMENTAL_V1 | Environmental | Climate, ecology | Evaluates environmental context |
| AGENT_TECHNOLOGICAL_V1 | Technological | Tools, innovations, technology | Evaluates technical accuracy |
| AGENT_LINGUISTIC_V1 | Linguistic | Languages, scripts | Evaluates linguistic aspects |
| AGENT_ARCHAEOLOGICAL_V1 | Archaeological | Material culture, stratigraphy | Evaluates archaeological validity |
| AGENT_DIPLOMATIC_V1 | Diplomatic | Treaties, alliances, diplomacy | Evaluates diplomatic accuracy |
| AGENT_GEOGRAPHIC_V1 | Geographic | Spatial regions, territories | Evaluates geographic accuracy |

**Coordinator Routing to Facet-Specialists:**

When a claim arrives for evaluation:

1. **Action:** Coordinator creates AnalysisRun node (Section 3.2.4)
2. **Action:** Coordinator queues claim for all 18 facet-specialist agents
3. **Each Facet-Specialist:** Creates independent FacetAssessment (Section 3.2.5)
4. **Result:** Star pattern with 16 dimensional assessments (Section 9.6)

```cypher
// Coordinator routing logic
MATCH (agent:Agent)-[:OWNS_CATEGORY]->(cat:FacetCategory)
MATCH (cat)<-[:IN_FACET_CATEGORY]-(f:Facet)
// Queue (agent, claim) pair for evaluation
CREATE (task:EvaluationTask {
  agent_id: agent.agent_id,
  claim_id: claim.claim_id,
  facet_type: f.label,
  status: "queued"
})
```

### **Cypher Example**

```cypher
CREATE (agent:Agent {
  agent_id: "claims_coordinator",
  label: "Claims Coordination Agent",
  agent_type: "coordinator",
  description: "Orchestrates multi-agent claim review, facet assessment, and promotion"
})
```

---

## **5.6 Agent Routing Logic**

**Agent routing** determines which agent handles which task based on subject classification, entity type, and claim content.

### **Routing Inputs**

1. **Subject classification:** LCC class, FAST topics from SubjectConcepts
2. **Entity type:** Human, Event, Place, etc.
3. **Claim type:** entity_existence, relationship_assertion, property_assertion
4. **Temporal scope:** Period coverage
5. **Geographic scope:** Place coverage

### **Routing Algorithm**

```
1. Extract SubjectConcepts from claim content
2. Identify primary LCC class
3. Route to FAST-level agent (Level 1)
4. Within FAST agent, identify LCC subdivision
5. Route to LCC specialist (Level 2) if available
6. If no specialist, use generalist FAST agent
```

### **Cypher Routing Query**

```cypher
// Find agents for claim about "Caesar crosses Rubicon"
MATCH (claim:Claim {claim_id: "claim_00123"})
      -[:SUBJECT_OF]->(:SubjectConcept)
      <-[:OWNS_DOMAIN]-(agent:Agent)
WHERE agent.agent_type = "subject"
RETURN agent.agent_id, agent.label, COUNT(*) AS domain_overlap
ORDER BY domain_overlap DESC
LIMIT 3
```

---

## **5.7 SFA Ontology Building Methodology**

**Context:** SubjectFacetAgents (SFAs) build domain-specific ontologies during **Training Phase** (Section 5.5.2). This requires filtering federated authority noise to extract clean disciplinary structures.

**Problem:** Wikidata "what links here" queries return massive platform noise (Wikimedia categories, templates, Commons files) overwhelming domain content.

**Solution:** Disciplinary filtering methodology using scholarly roots, property whitelists, and platform blacklists.

### **5.7.1 Military SFA Methodology (Example)**

**Reference:** `Facets/MILITARY_SFA_ONTOLOGY_METHODOLOGY.md` (complete specification with SPARQL queries, validation checklist, expected ontology structure)

**Anchor:** Start from `Q192386` (military science) as scholarly discipline root, not vague "military" label.

**Property Whitelist (PREFER):**
| Property | Code | Purpose | Priority |
|----------|------|---------|----------|
| subclass of | P279 | Taxonomic backbone | HIGH |
| instance of | P31 | Type classification | HIGH |
| part of | P361 | Compositional structure | HIGH |
| has part | P527 | Compositional structure | HIGH |
| conflict | P607 | Military conflicts | HIGH |
| military branch | P241 | Branch of service | HIGH |
| military rank | P410 | Rank classification | HIGH |
| military unit | P7779 | Unit types | HIGH |

**Wikimedia Blacklist (EXCLUDE):**
| QID | Type | Rationale |
|-----|------|-----------|
| Q4167836 | Wikimedia category | Platform navigation |
| Q11266439 | Wikimedia template | Platform scaffolding |
| Q17633526 | Wikinews article | News content |
| Q15184295 | Wikimedia module | Technical infrastructure |
| Q4663903 | Wikimedia portal | Portal organization |

**Inclusion Criteria (items must satisfy MOST of):**
- Has `P279` or `P31` linking to military domain class
- Has `P425` (field of occupation) = military science
- Appears in military science scholarly treatments
- Has meaningful `P361`/`P527`/`P607`/`P241`/`P410` relations
- Fits naturally as a class in hierarchy
- Needed to explain military processes or institutions

**Exclusion Criteria (items must fail ALL of):**
- `P31` is Wikimedia infrastructure class
- Only connects via category/Commons/site links
- Orphaned (no core military properties)
- Over-generic buzzword without military specificity
- Pure media container (image, category)
- Anachronistic (for Roman Republic specialization)

**Roman Republic Refinement:**
- Intersect generic military ontology with Q17167 (Roman Republic)
- Use P1001 (applies to jurisdiction), P361 (part of)
- Temporal overlap: 509 BCE - 27 BCE
- Exclude anachronisms (air force, cyberwarfare, modern operational concepts)

**Expected Results:**
- Generic military ontology: ~500-1,000 concepts (~2,000-5,000 edges after filtering)
- Roman Republican specialization: ~100-200 concepts (~500-1,000 edges after filtering)
- Noise reduction: 80-90% (typical Wikidata query returns 10,000+ items, filtered to ~500-1,000)

**Example Training Claims (Military SFA, NO CROSS-FACET REVIEW):**
```
Claim 1: "Legion was primary Roman military unit"
  → Type: Discovery Mode (abstract domain concept)
  → Source: Wikidata Q170944 + scholarly sources
  → Confidence: 0.95
  → Facet: Military
  → SCA Action: Accept as-is (NO QUEUE)

Claim 2: "Cohort composed of multiple maniples"
  → Type: Discovery Mode (abstract structural relationship)
  → Source: Wikidata Q82955, Q1541817
  → Confidence: 0.90
  → Facet: Military
  → SCA Action: Accept as-is (NO QUEUE)

Claim 3: "Centurion commanded century of soldiers"
  → Type: Discovery Mode (abstract organizational principle)
  → Source: Wikidata Q2747456
  → Confidence: 0.95
  → Facet: Military
  → SCA Action: Accept as-is (NO QUEUE)
```

**Rationale:** These are **disciplinary ontology claims**, not concrete historical events. They do not warrant cross-facet review by Political, Economic, or Cultural SFAs during training phase.

### **5.7.2 Generalized Methodology (All SFAs)**

**Step 1: Identify Disciplinary Root**
- Find Wikidata QID for discipline (e.g., Q192386 for military science, Q36442 for political science)
- Verify `P31` = field of study (Q11862829) or academic discipline (Q11862829)
- Use as scholarly anchor, not arbitrary category

**Step 2: Property Whitelist**
- Select semantic properties (P279, P31, P361, P527, domain-specific properties)
- Exclude platform properties (P373 Commons category, P910 topic's main category, P1151 main portal)

**Step 3: Wikimedia Blacklist**
- Exclude all `P31` → Wikimedia infrastructure classes (Q4167836, Q11266439, etc.)
- Filter out pure media containers (images, galleries, categories)

**Step 4: Polity/Period Refinement**
- Intersect generic ontology with historical context (e.g., Q17167 Roman Republic)
- Use P1001 (jurisdiction), P361 (part of), P580/P582 (temporal bounds)
- Exclude anachronisms for historical specializations

**Step 5: Training Claim Generation**
- Create Discovery Mode claims about abstract concepts
- All claims tagged with facet
- SCA accepts all training claims as-is (no queue to other SFAs)

**Expected Noise Reduction:** 70-90% depending on domain complexity and Wikidata coverage

**Benefits:**
- âœ… Clean disciplinary ontologies (not platform artifacts)
- âœ… Scholarly grounding (from recognized academic disciplines)
- âœ… Efficient training (SFAs don't review irrelevant abstract concepts from other facets)
- âœ… Scalable methodology (applicable to all 17 facet domains)

---

## **5.8 Agent Memory (AgentMemory Node)**

Agents maintain **explicit memory** of previous decisions, patterns, and cached knowledge.

### **AgentMemory Node Schema**

**Node Label:** `:AgentMemory`

**Required Properties:**
| Property | Type | Example |
|----------|------|---------|
| `memory_id` | string | `"mem_000456"` |
| `agent_id` | string | `"roman_republic_agent"` |
| `memory_type` | string | `"decision"`, `"pattern"`, `"cached_knowledge"` |
| `content` | string | Serialized memory content |
| `created_at` | ISO 8601 string | `"2026-02-12T11:00:00Z"` |

**Required Edges:**
- `MEMORY_OF` â†’ Agent

### **Memory Types**

1. **Decision Memory:** Previous review decisions and rationale
2. **Pattern Memory:** Recognized patterns (e.g., "Caesar always spelled with 'ae'")
3. **Cached Knowledge:** Pre-computed facts (e.g., "Roman Republic = 510-27 BCE")

### **Cypher Example**

```cypher
CREATE (mem:AgentMemory {
  memory_id: "mem_000456",
  agent_id: "roman_republic_agent",
  memory_type: "pattern",
  content: "Caesar name variants: Gaius Julius Caesar, C. Julius Caesar, Julius Caesar",
  created_at: "2026-02-12T11:00:00Z"
})

MATCH (agent:Agent {agent_id: "roman_republic_agent"})
CREATE (mem)-[:MEMORY_OF]->(agent)
```

---

## **5.8 Agent Lifecycle & Caching**

**Agent versioning** and **cache management** ensure consistent behavior and efficient operation.

### **Agent Versioning Strategy**

**Version Identifier Format:**
```
{agent_type}_{qid}_{lcc_class}_{version}_{timestamp}
```

**Example:**
```
genericagent_Q1048_DG83_v1.2_20260212T100000Z
```

**Components:**
- `agent_type`: `genericagent`, `subjectagent`, `entityagent`, `coordinator`
- `qid`: Wikidata QID of primary domain concept
- `lcc_class`: Primary LCC classification
- `version`: Semantic version (v1.2)
- `timestamp`: Creation timestamp

### **Cache Versioning**

**Problem:** Agent knowledge evolves; old cached results may be stale.

**Solution:** Cache entries tagged with agent version:

```cypher
AgentMemory {
  agent_version: "v1.2",
  cache_expiry: "2026-03-12T00:00:00Z"
}
```

**Cache Invalidation Rules:**
1. Agent version increments â†’ invalidate all caches
2. Expiry timestamp reached â†’ refresh cache
3. Upstream SubjectConcept updated â†’ invalidate related caches

**Source:** Old conversation analysis (cache versioning for vertex jump concept)

---

## **5.9 Cypher Examples**

### **Create Subject Agent with Domain**

```cypher
CREATE (agent:Agent {
  agent_id: "roman_republic_agent",
  label: "Roman Republic Specialist",
  agent_type: "subject",
  confidence_calibration: 0.93,
  specialization_level: "high",
  version: "v1.0",
  created_at: "2026-02-12T10:00:00Z"
})

MATCH (sc:SubjectConcept {lcc_class: "DG83"})
CREATE (agent)-[:OWNS_DOMAIN]->(sc)
```

### **Route Claim to Agents**

```cypher
// Find agents for a claim
MATCH (claim:Claim {claim_id: "claim_00123"})
      -[:ABOUT_SUBJECT]->(:SubjectConcept)
      <-[:OWNS_DOMAIN]-(agent:Agent)
WHERE agent.agent_type = "subject"
  AND agent.specialization_level IN ["high", "medium"]
RETURN agent.agent_id, agent.label
LIMIT 5
```

### **Agent Review History**

```cypher
// Get agent's review history
MATCH (agent:Agent {agent_id: "roman_republic_agent"})
      -[:REVIEWED]->(review:Review)
      -[:REVIEW_OF]->(claim:Claim)
RETURN claim.claim_id, review.decision, review.confidence
ORDER BY review.review_timestamp DESC
LIMIT 20
```

### **Create Agent Memory**

```cypher
CREATE (mem:AgentMemory {
  memory_id: "mem_000789",
  agent_id: "roman_republic_agent",
  memory_type: "cached_knowledge",
  content: "Roman Republic period boundaries: start=-510, end=-27, uncertainty=Â±5 years",
  agent_version: "v1.0",
  cache_expiry: "2026-03-12T00:00:00Z",
  created_at: "2026-02-12T12:00:00Z"
})

MATCH (agent:Agent {agent_id: "roman_republic_agent"})
CREATE (mem)-[:MEMORY_OF]->(agent)
```

---

### **Link Work to SubjectConcept (Aboutness)**

# **6. Claims Layer**

## **6.0 Claims Layer Overview**

The **Claims Layer** provides evidence-aware assertion management with transparent provenance, multi-agent validation, and cryptographic verification. Claims are not simple edgesâ€”they are **complex subgraphs** representing complete evidence chains.

**Core Concept:** Every assertion in Chrystallum has explicit provenance from source material through agent extraction to validated canonical graph representation.

---

## **6.1 Claims Architecture Components**

The Claims Layer manages the complete lifecycle of evidence-based assertions, from initial extraction through multi-agent validation to canonical graph promotion.

### **Core Node Types:**

**1. Claim** - Structured assertion with provenance
- Represents an agent's assertion about the world
- Includes confidence, provenance, and verification metadata
- Identified by content-addressable cipher (Section 6.4)

**2. Review** - Multi-agent validation decision
- Single agent's evaluation of a claim
- Includes confidence, verdict, fallacy detection
- Feeds into consensus calculation

**3. ProposedEdge** - Relationship awaiting validation
- Represents edges not yet promoted to canonical graph
- Converted to actual relationships upon validation
- Maintains proposed structure separate from verified graph

**4. ReasoningTrace** - Derivation provenance
- How an agent reached a conclusion
- Reasoning steps, sources consulted, confidence chain
- Enables explainability and audit trails

**5. Synthesis** - Multi-agent consensus resolution
- Resolves conflicting claims from multiple agents
- Records consensus method and participating agents
- Produces consolidated output claim

**6. RetrievalContext** - Evidence retrieval record
- Documents and passages retrieved from private vector stores
- Links retrieval actions to reasoning traces
- Maintains query-response provenance

### **Provenance Chain:**
```
Work (Source Entity - Section 3) 
  â†’ Agent (Extraction)
    â†’ Claim (Assertion + Cipher)
      â†’ ReasoningTrace (How derived)
      â†’ RetrievalContext (Evidence used)
      â†’ Review (Validation by peers)
        â†’ Synthesis (Consensus building)
          â†’ Status Update (proposed â†’ validated)
            â†’ Promotion (to canonical graph)
```

### **System Architecture Context**

**Two Separate Systems:**
| System | Storage | Shared? | Purpose |
|--------|---------|---------|---------|
| **Neo4j Graph** | Nodes & edges | âœ… YES | Structural knowledge, claims, provenance |
| **Vector Stores** | Text embeddings | âŒ NO | Semantic retrieval per agent (private) |

**Key Principle:** Claims, Reviews, Reasoning Traces, and Agent Memory live in the **shared graph**. Text embeddings and document chunks live in **private per-agent vector stores**.

---

## **6.2 Claim Node Schema**

**Node Label:** `:Claim`

**Purpose:** Represents an assertion made by an Agent about the world, expressed as proposed or interpreted graph structure (nodes + edges). Claims support multi-agent review, provenance, and gradual promotion of "proposed" structure into validated KG facts.

### **Required Properties**

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `claim_id` | string | text | `"claim_000123"` | Unique ID |
| `cipher` | string | hash | `"claim_b22020c0e271b7d8..."` | **Content-addressable identifier** (Section 6.4) |
| `text` | string | text | `"Caesar crossed the Rubicon on January 10, 49 BCE."` | Human-readable claim text |
| `claim_type` | string | enum | `"factual"` | `"factual"`, `"interpretive"`, `"causal"`, `"temporal"`, `"entity_existence"`, `"relationship_assertion"`, `"property_assertion"` |
| `source_agent` | string | text | `"roman_republic_agent_001"` | Agent that originated the claim |
| `timestamp` | string | ISO 8601 | `"2026-02-12T15:30:00Z"` | When the claim was created |
| `status` | string | enum | `"proposed"` | `"proposed"`, `"validated"`, `"disputed"`, `"rejected"` |
| `confidence` | float | [0,1] | `0.85` | Agent's internal confidence at creation |

### **Provenance Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `source_work_qid` | string | `"Q644312"` | Wikidata ID of source work |
| `passage_text` | string | `"Caesar...Rubicon...49 BCE"` | Actual text supporting claim |
| `passage_hash` | string | `"p_a1b2c3d4..."` | Hash of passage for verification |
| `extractor_agent_id` | string | `"genericagent_Q767253_D_v2.0"` | Agent that extracted claim |
| `extraction_timestamp` | string | `"2026-02-12T10:30:00Z"` | When extracted |
| `provenance` | string[] | `["Plutarch, Caesar 32", "Suetonius, Julius 31"]` | Source citations |

### **Content Properties (varies by claim_type)**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `subject_entity_qid` | string | `"Q1048"` | Primary entity claim is about |
| `object_entity_qid` | string | `"Q644312"` | Secondary entity (for relationships) |
| `relationship_type` | string | `"CAUSED"` | Type of relationship asserted (Section 7) |
| `property_name` | string | `"death_date"` | Property being asserted |
| `property_value` | any | `"-0044-03-15"` | Value of property |
| `temporal_data` | string | `"-0049-01-10"` | Temporal information |
| `action_structure` | JSON | `{"goal": "POL", "trigger": "OPPORT"}` | Goal-trigger-action-result (Section 7.6) |

### **Consensus & Review Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `review_count` | int | `3` | Number of reviews received |
| `consensus_score` | float | `0.78` | Aggregated review confidence |
| `claim_scope` | string | `"Battle of Actium casualties"` | Short label for domain |
| `reasoning_trace_id` | string | `"trace_000987"` | ID of associated ReasoningTrace |
| `proposed_nodes` | string[] | `["event_123", "place_456"]` | IDs of nodes this claim proposes |
| `proposed_edges` | string[] | `["pedge_001", "pedge_002"]` | IDs of ProposedEdge nodes |

### **Verification Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `state_root` | string | `"merkle_root_abc123..."` | Merkle tree root for cryptographic verification |
| `lamport_clock` | integer | `12345` | Logical timestamp for distributed ordering |

### **Required Edges**

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `MADE_CLAIM` | Agent | 1 | `(agent)-[:MADE_CLAIM]->(claim)` |
| `SUBJECT_OF` | Entity/SubjectConcept | 1+ | `(entity OR concept)-[:SUBJECT_OF]->(claim)` |

### **Optional Edges**

| Relationship | Target | Notes |
|--------------|--------|-------|
| `PROPOSES` | Entity | Claim proposes existence/interpretation of a node |
| `PROPOSES` | ProposedEdge | Claim proposes a new relationship |
| `HAS_TRACE` | ReasoningTrace | `(claim)-[:HAS_TRACE]->(trace)` |
| `SUPERSEDES` | Claim | Links newer version to older version |

---

## **6.3 Review Node Schema**

**Node Label:** `:Review`

**Purpose:** Represents a single agent's evaluation of a Claim, including confidence, detected fallacies, and a reasoning summary. Reviews feed into consensus and claim status updates.

### **Required Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `review_id` | string | `"review_000456"` | Unique ID |
| `agent_id` | string | `"naval_warfare_agent"` | Reviewing agent |
| `claim_id` | string | `"claim_000123"` | Reviewed claim |
| `timestamp` | string | `"2026-02-12T16:00:00Z"` | When review was made |
| `confidence` | float | `0.72` | Reviewer's confidence |
| `verdict` | string | `"support"` | `"support"`, `"challenge"`, `"uncertain"` |

### **Optional Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `fallacies_detected` | string[] | `["anachronism", "post_hoc"]` | Fischer-style historical fallacies |
| `reasoning_summary` | string | `"Plutarch exaggerates casualties; Dio provides more conservative estimate"` | Short text summary |
| `evidence_refs` | string[] | `["Goldsworthy p.145", "Dio 50.35"]` | Evidence used in review |
| `bayesian_posterior` | float | `0.68` | Output of Bayesian reasoning engine |
| `weight` | float | `1.0` | Reviewer weight (expertise-based) |

### **Required Edges**

| Relationship | Target | Notes |
|--------------|--------|-------|
| `REVIEWED` | Agent | `(agent)-[:REVIEWED]->(review)` |
| `REVIEWS` | Claim | `(review)-[:REVIEWS]->(claim)` |

### **Example Cypher**

```cypher
// Create review
CREATE (review:Review {
  review_id: "review_000456",
  agent_id: "naval_warfare_agent",
  claim_id: "claim_000123",
  timestamp: "2026-02-12T16:00:00Z",
  confidence: 0.72,
  verdict: "support",
  reasoning_summary: "Dio's account provides corroborating evidence"
})

// Link to agent and claim
MATCH (agent:Agent {agent_id: "naval_warfare_agent"}),
      (claim:Claim {claim_id: "claim_000123"})
CREATE (agent)-[:REVIEWED]->(review)-[:REVIEWS]->(claim)
```

---

## **6.4 Content-Addressable Claim Identification** ðŸ”¥ NEW

### **6.4.1 Claim Cipher Generation**

**Core Innovation:** Claims are uniquely identified by a **content-only cipher** generated from assertion content, NOT provenance:

```python
# Canonical cipher = Hash of CONTENT ONLY (stable across agents/time)
claim_cipher = Hash(
    normalize_unicode(source_work_qid) +      # Q644312 (Plutarch, Life of Caesar)
    normalize_unicode(passage_text_hash) +    # Hash("Caesar...Rubicon...49 BCE")
    normalize_unicode(subject_entity_qid) +   # Q1048 (Julius Caesar)
    normalize_unicode(object_entity_qid) +    # Q644312 (Crossing of Rubicon event QID)
    normalize_unicode(relationship_type) +    # "CAUSED"
    normalize_json(action_structure) +        # {goal: "POL", trigger: "OPPORT", ...}
    normalize_iso8601(temporal_data) +        # {start_date: "-0049-01-10"}
    normalize_unicode(facet_id)               # "POLITICAL"
    # ❌ NO confidence_score - provenance, not content
    # ❌ NO extractor_agent_id - provenance, not content
    # ❌ NO extraction_timestamp - provenance, not content
)

# Result: "claim_kc1-b22020c0e271b7d8e4a5f6c9d1b2a3e4" (stable cipher)
```

**Normalization Functions:**
```python
def normalize_unicode(text: str) -> str:
    """Unicode NFC normalization + strip whitespace"""
    return unicodedata.normalize('NFC', text.strip())

def normalize_json(obj: dict) -> str:
    """Canonical JSON: sorted keys, no whitespace"""
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))

def normalize_iso8601(date_str: str) -> str:
    """ISO 8601 extended format: YYYY-MM-DD or -YYYY-MM-DD"""
    # Ensure leading zero for negative years: "-49-01-10" → "-0049-01-10"
    return format_iso8601_extended(date_str)
```

**Critical Rule:** Cipher identifies the **assertion** (what is being claimed), not the **observation** (who claimed it, when, with what confidence).

### **Why Content-Addressable Claims?**

#### **1. Automatic Deduplication** âœ…

```python
# Agent A extracts claim from Plutarch at 10:00 AM
claim_content_A = {
    "source": "Q644312",
    "passage_hash": hash_text("Caesar crossed the Rubicon..."),
    "subject": "Q1048",
    "object": "Q47043",  # Crossing of Rubicon event
    "relationship": "CAUSED",
    "facet": "POLITICAL",
    "temporal": "-0049-01-10"
}
cipher_A = compute_cipher(claim_content_A)  # → "claim_abc123..."

# Store provenance SEPARATELY (not in cipher!)
provenance_A = {
    "agent_id": "political_sfa_v2.0",
    "timestamp": "2026-02-12T10:00:00Z",
    "confidence": 0.92
}

# Agent B extracts SAME claim from Plutarch at 2:00 PM
claim_content_B = {
    "source": "Q644312",
    "passage_hash": hash_text("Caesar crossed the Rubicon..."),
    "subject": "Q1048",
    "object": "Q47043",
    "relationship": "CAUSED",
    "facet": "POLITICAL",
    "temporal": "-0049-01-10"
}
cipher_B = compute_cipher(claim_content_B)  # → "claim_abc123..." (SAME!)

# Different provenance (not in cipher!)
provenance_B = {
    "agent_id": "military_sfa_v2.0",
    "timestamp": "2026-02-12T14:00:00Z",
    "confidence": 0.95
}

# Graph check prevents duplicate CLAIM node
if exists_in_graph(cipher_B):
    # ✅ Don't create duplicate Claim - add Agent B's FacetPerspective
    create_perspective_node(cipher_B, provenance_B)
    # Consensus logic: two facets agree → confidence boost
    update_consensus(cipher_B)
else:
    # New claim - create Claim node + first FacetPerspective
    create_claim_with_perspective(cipher_B, claim_content_B, provenance_A)
```

**Benefits:**
- Multiple agents validating same claim → higher confidence via consensus, not duplicates
- Provenance tracked separately in FacetPerspective nodes (PERSPECTIVE_ON edges)
- Cipher remains stable even as confidence/reviews change over time

#### **2. Cryptographic Verification** âœ…

```python
# University A creates claim
claim = create_claim(claim_data)
cipher = claim.cipher  # Content-addressable ID
state_root = MerkleRoot([cipher, related_entities, sources])

# Publish with verification receipt
publish({
    "cipher": cipher,
    "state_root": state_root, 
    "timestamp": "2026-02-12T10:30:00Z",
    "institution": "University A"
})

# University B downloads and verifies
downloaded_claim = fetch_claim(cipher)
recomputed_cipher = Hash(downloaded_claim.data)

if recomputed_cipher == cipher:
    # âœ… Claim data matches cipher - integrity verified
    # Can cite with cryptographic proof
    cite_with_proof(cipher, state_root)
else:
    # âŒ Data corrupted or tampered
    reject_claim("Integrity verification failed")
```

**Benefits:**
- Academic claims verifiable with cryptographic proof
- No trust needed - math verifies integrity
- Enables distributed academic knowledge networks

---

#### **3. Claim as Subgraph Cluster** âœ…

**A claim isn't a single nodeâ€”it's a complete evidence structure:**

```cypher
// The cipher identifies the entire subgraph cluster
(claim:Claim {
  cipher: "claim_abc123...",
  claim_id: "claim_00123"  // Also keep internal ID for convenience
})

// Subgraph components attached to cipher
(source:Work {qid: "Q644312"})-[:EXTRACTED_FROM]->(claim)
(passage:Passage {text: "Caesar..."})-[:CITED_BY]->(claim)
(caesar:Human {qid: "Q1048"})-[:SUBJECT_OF]->(claim)
(event:Event {qid: "Q644312"})-[:OBJECT_OF]->(claim)
(rel:CAUSED)-[:ASSERTED_BY]->(claim)
(agent:Agent {agent_id: "genericagent..."})-[:EXTRACTED_BY]->(claim)
```

**The cipher is the cluster key** - all components reference it.

---

#### **4. Framework/Review Attachment via Cipher** âœ…

```cypher
// Frameworks analyze claim via cipher reference
(framework:Framework {name: "W5H1"})
  -[:ANALYZES]->
  (claim:Claim {cipher: "claim_abc123"})

// Reviews validate claim via cipher reference  
(review:Review {
  status: "verified",
  reviewer: "Dr. Smith",
  timestamp: "2026-02-12T11:00:00Z"
})
  -[:VALIDATES]->
  (claim:Claim {cipher: "claim_abc123"})

// Beliefs derive from claim via cipher reference
(belief:Belief {
  confidence: 0.95,
  reasoning: "Two independent sources confirm"
})
  -[:DERIVED_FROM]->
  (claim:Claim {cipher: "claim_abc123"})

// Query: "Find all frameworks analyzing this claim"
MATCH (f:Framework)-[:ANALYZES]->(c:Claim {cipher: $cipher})
RETURN f

// No ambiguity - cipher uniquely identifies claim subgraph
```

**Benefits:**
- Unambiguous attachment point (cipher = unique identifier)
- Works across distributed systems (same cipher everywhere)
- Can query all validations for specific evidence cluster

---

#### **5. Claim Versioning Built-In** âœ…

```cypher
// Original claim extracted with confidence 0.85
(claim_v1:Claim {
  cipher: "claim_abc123...",  // Computed with confidence=0.85
  confidence: 0.85,
  status: "under_review",
  timestamp: "2026-02-12T10:00:00Z"
})

// New evidence raises confidence to 0.95
// Different confidence â†’ different cipher!
(claim_v2:Claim {
  cipher: "claim_xyz789...",  // Different cipher
  confidence: 0.95,
  status: "verified", 
  timestamp: "2026-02-12T14:00:00Z"
})

// Link versions explicitly
(claim_v2)-[:SUPERSEDES]->(claim_v1)
(claim_v2)-[:EVIDENCE_ADDED]->(:Review {
  new_source: "Suetonius",
  reason: "Additional corroboration"
})

// Query claim evolution
MATCH path = (c_new:Claim)-[:SUPERSEDES*]->(c_old:Claim)
WHERE c_new.cipher = "claim_xyz789..."
RETURN path
```

**Benefits:**
- Claim evolution tracked automatically
- Can query historical confidence levels
- Audit trail for scholarly disputes
- Immutable history (old claim preserved with original cipher)

---

### **6.4.1 Facet Claim Node Schema**

**Neo4j Implementation (Facet-Level Claim):**

```cypher
// Create facet claim with stable cipher
CREATE (claim:FacetClaim {
  // Content-addressable ID (primary, stable across provenance changes)
  cipher: "fclaim_pol_b22020c0e271b7d8",
  
  // Internal ID (convenience)
  claim_id: "claim_00123",
  
  // CIPHER COMPONENTS (stable, logical content)
  subject_node_id: "Q1048",           // Caesar
  property_path_id: "CHALLENGED_AUTHORITY_OF",
  object_node_id: "Q1747689",         // Roman Senate
  facet_id: "political",              // Essential!
  temporal_scope: "-0049-01-10",
  source_document_id: "Q644312",       // Plutarch
  passage_locator: "Caesar.32",
  
  // PROVENANCE METADATA (separate from cipher, can change)
  confidence: 0.85,                    // Can update without changing cipher
  extracting_agents: [                 // Multiple agents = evidence accumulation
    "political_sfa_001",
    "military_sfa_001"                // Added later via deduplication
  ],
  extraction_timestamps: [
    "2026-02-12T10:00:00Z",
    "2026-02-12T14:00:00Z"
  ],
  created_by_agent: "political_sfa_001",  // Original extractor
  last_updated: "2026-02-12T14:00:00Z",
  
  // DERIVED PROPERTIES
  assertion_text: "Caesar challenged Senate authority by crossing Rubicon",
  cidoc_crm_property: "P17_was_motivated_by",
  
  // STATUS & VALIDATION (lifecycle, not identity)
  status: "validated",
  review_count: 2,
  consensus_score: 0.91,
  validation_timestamp: "2026-02-12T15:00:00Z",
  
  // CRYPTOGRAPHIC VERIFICATION (optional)
  state_root: "merkle_xyz789...",     // Merkle root of assertion graph
  lamport_clock: 1234567
})

// Indexes
CREATE INDEX facet_claim_cipher_idx FOR (c:FacetClaim) ON (c.cipher);
CREATE INDEX facet_claim_facet_idx FOR (c:FacetClaim) ON (c.facet_id);
```

---

### **6.4.2 Deduplication Query Pattern**

```cypher
// Before creating new claim, check if cipher exists
MATCH (existing:Claim {cipher: $computed_cipher})
RETURN existing

// If found: Add supporting review instead of duplicate
MERGE (existing:Claim {cipher: $computed_cipher})
ON MATCH SET 
  existing.review_count = existing.review_count + 1,
  existing.confidence = existing.confidence + ($new_confidence_boost)
CREATE (review:Review {
  reviewer_agent: $agent_id,
  timestamp: $timestamp,
  status: "confirmed"
})-[:VALIDATES]->(existing)

// If not found: Create new claim subgraph
ON CREATE SET
  existing.claim_id = $internal_id,
  existing.source_work_qid = $source_qid,
  existing.confidence = $initial_confidence,
  existing.status = "proposed",
  existing.review_count = 1
```

---

### **6.4.3 Verification Query Pattern**

```cypher
// Verify claim integrity by recomputing cipher from stable components ONLY
MATCH (c:FacetClaim {cipher: $claimed_cipher})
WITH c, 
  Hash(
    c.subject_node_id + 
    c.property_path_id + 
    c.object_node_id +
    c.facet_id +
    c.temporal_scope +
    c.source_document_id +
    c.passage_locator
    // NOTE: NO confidence, NO agent, NO timestamp!
  ) AS recomputed_cipher
RETURN 
  c.cipher = recomputed_cipher AS integrity_verified,
  c.cipher AS original_cipher,
  recomputed_cipher AS computed_cipher,
  CASE 
    WHEN c.cipher = recomputed_cipher THEN "✅ Claim identity verified"
    ELSE "❌ Cipher mismatch - possible tampering"
  END AS verification_status
```

**Check for Deduplication Candidates:**
```cypher
// Find potential duplicate claims (same content, different provenance)
MATCH (c1:FacetClaim), (c2:FacetClaim)
WHERE c1.subject_node_id = c2.subject_node_id
  AND c1.property_path_id = c2.property_path_id
  AND c1.object_node_id = c2.object_node_id
  AND c1.facet_id = c2.facet_id
  AND c1.cipher <> c2.cipher  // Different ciphers despite same core content
RETURN c1.cipher, c2.cipher, 
       "Potential deduplication issue" AS status,
       c1.extracting_agents AS agents1,
       c2.extracting_agents AS agents2
```

---

### **6.4.4 Framework Attachment Query Pattern**

```cypher
// Attach W5H1 framework analysis to claim
MATCH (claim:Claim {cipher: $cipher})
CREATE (framework:Framework {
  name: "W5H1",
  analysis: {
    who: "Julius Caesar",
    what: "Crossing of Rubicon", 
    when: "-0049-01-10",
    where: "Rubicon River",
    why: "Political opportunity",
    how: "Military action"
  }
})-[:ANALYZES]->(claim)

// Query all frameworks analyzing specific claim
MATCH (f:Framework)-[:ANALYZES]->(c:Claim {cipher: $cipher})
RETURN f.name, f.analysis

// Query all claims analyzed by specific framework
MATCH (f:Framework {name: "W5H1"})-[:ANALYZES]->(c:Claim)
RETURN c.cipher, c.claim_id, c.confidence
```

---

## **6.5 Hybrid Architecture: Entities vs. Claims**

### **Different Layers, Different Patterns:**

| Aspect | Entity Layer | Claims Layer |
|--------|--------------|--------------|
| **Identification** | Multiple authorities (qid, viaf_id, etc.) | Content-addressable cipher |
| **Query Pattern** | Traversal, exploration, discovery | Direct cipher lookup, verification |
| **Purpose** | Represent real-world entities | Represent evidence assertions |
| **Mutability** | Properties can change | Immutable (change = new cipher) |
| **Deduplication** | Via authority matching | Automatic via cipher collision |
| **Verification** | Authority ID validation | Cryptographic hash verification |

### **Why Hybrid Approach?**

**Entities need flexibility:**
- Relationship discovery: "What connects Caesar to Cleopatra?"
- Pattern matching: "Find all senators who opposed Caesar"
- Graph algorithms: PageRank, centrality, community detection
- **Traversal is the answer**

**Claims need verification:**
- Deduplication: "Have we seen this evidence before?"
- Integrity: "Has this claim been tampered with?"
- Provenance: "What exact source supports this?"
- **Content-addressable is the answer**

---

## **6.6 Distributed Academic Knowledge Networks** ðŸš€

### **Vision: P2P Verified Citations**

```python
# University A creates claim about Caesar
claim = {
    "source": "Plutarch_Life_of_Caesar",
    "assertion": "Caesar crossed Rubicon in 49 BCE",
    "evidence": "...",
    "cipher": "claim_abc123..."
}

# Generate verification receipt
state_root = MerkleRoot([claim.cipher, sources, entities])
publish_to_network({
    "cipher": claim.cipher,
    "state_root": state_root,
    "institution": "University A",
    "timestamp": "2026-02-12T10:30:00Z"
})

# University B references claim in their research
cite_claim(
    cipher="claim_abc123...",
    state_root="merkle_xyz789...",
    verification_timestamp="2026-02-12T15:00:00Z"
)

# Anyone can verify citation integrity
downloaded = fetch_claim("claim_abc123...")
verified = verify_cipher(downloaded)  # Cryptographic proof
if verified:
    # âœ… Citation is authentic and unaltered
    use_in_research(downloaded)
```

**Enables:**
- âœ… Federated institutional repositories
- âœ… P2P knowledge sharing
- âœ… Reproducible science
- âœ… Academic claims with built-in provenance
- âœ… No central authority needed

---

## **6.7 Implementation Guidelines**

### **Cipher Generation Function:**

```python
import hashlib
import json

def generate_claim_cipher(claim_data: dict) -> str:
    """
    Generate content-addressable cipher for claim.
    
    Args:
        claim_data: Dictionary with all claim components
        
    Returns:
        Unique cipher string (hex hash)
    """
    # Normalize data for consistent hashing
    normalized = {
        "source_work_qid": claim_data["source_work_qid"],
        "passage_hash": hashlib.sha256(
            claim_data["passage_text"].encode()
        ).hexdigest(),
        "subject_entity_qid": claim_data["subject_entity_qid"],
        "object_entity_qid": claim_data.get("object_entity_qid", ""),
        "relationship_type": claim_data.get("relationship_type", ""),
        "temporal_data": claim_data.get("temporal_data", ""),
        "confidence": f"{claim_data['confidence']:.2f}",
        "extractor_agent_id": claim_data["extractor_agent_id"],
        "extraction_timestamp": claim_data["extraction_timestamp"]
    }
    
    # Sort keys for deterministic ordering
    canonical = json.dumps(normalized, sort_keys=True)
    
    # Generate cipher
    cipher_hash = hashlib.sha256(canonical.encode()).hexdigest()
    
    return f"claim_{cipher_hash[:32]}"  # Prefix + first 32 hex chars

# Example usage
claim = generate_claim_cipher({
    "source_work_qid": "Q644312",
    "passage_text": "Caesar crossed the Rubicon...",
    "subject_entity_qid": "Q1048",
    "object_entity_qid": "Q644312",
    "relationship_type": "CAUSED",
    "temporal_data": "-0049-01-10",
    "confidence": 0.95,
    "extractor_agent_id": "genericagent_Q767253_D_v2.0",
    "extraction_timestamp": "2026-02-12T10:30:00Z"
})
# Returns: "claim_b22020c0e271b7d8e4a5f6c9d1b2a3e4"
```

---

### **Best Practices:**

1. **Always check cipher before creating claim**
   - Prevents duplicates
   - Enables automatic consensus

2. **Include timestamp in cipher components**
   - Different extraction times = same cipher (if content identical)
   - Enables temporal tracking

3. **Version claims explicitly when confidence changes**
   - Create new claim with new cipher
   - Link via `SUPERSEDES` relationship
   - Preserve historical record

4. **Index cipher property for performance**
   - O(1) lookup critical for deduplication
   - Consider composite index with status

5. **Use state roots for distributed verification**
   - Merkle tree enables efficient verification
   - Supports P2P academic networks

---

## **6.8 ProposedEdge Node Schema**

**Node Label:** `:ProposedEdge`

**Purpose:** Represents a canonical claim edge assertion (edge-as-node) attached to a Claim.

**Normative 2026-02-17 update:**
- Canonical claim edge pattern is:
  - `(:Claim)-[:ASSERTS_EDGE]->(:ProposedEdge)-[:FROM]->(source)`
  - `(:ProposedEdge)-[:TO]->(target)`
- `:ProposedEdge` is canonical claim-layer structure, not scaffold bootstrap structure.
- Bootstrap/scaffold uses `:ScaffoldEdge` (Appendix Y), not `:ProposedEdge`.

### **Required Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `edge_id` | string | `"pedge_a1b2c3d4e5f6"` | Deterministic unique ID |
| `claim_id` | string | `"claim_abc123def456"` | Parent claim identifier |
| `relationship_type` | string | `"OCCURRED_DURING"` | Canonical relationship type to materialize |
| `source_entity_id` | string | `"evt_battle_of_actium_q193304"` | Source entity ID |
| `target_entity_id` | string | `"prd_roman_republic_q17167"` | Target entity ID |
| `status` | string | `"proposed"` | Lifecycle status (`proposed|validated|rejected`) |
| `created_at` | string | `"2026-02-17T14:15:00Z"` | Creation timestamp |

### **Optional Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `updated_at` | string | `"2026-02-17T14:20:00Z"` | Last update time |
| `confidence` | float | `0.94` | Edge-level confidence snapshot |
| `source_agent` | string | `"agent_claim_ingestion_pipeline"` | Producing agent |
| `facet` | string | `"military"` | Facet context |
| `promotion_date` | string | `"2026-02-17T14:30:00Z"` | Set when promoted |
| `promotion_status` | string | `"canonical"` | Promotion state marker |

### **Required Edges**

| Relationship | Target | Notes |
|--------------|--------|-------|
| `ASSERTS_EDGE` | ProposedEdge | `(claim)-[:ASSERTS_EDGE]->(proposedEdge)` |
| `FROM` | Entity | `(proposedEdge)-[:FROM]->(source)` |
| `TO` | Entity | `(proposedEdge)-[:TO]->(target)` |

### **Example Cypher**

```cypher
MATCH (claim:Claim {claim_id: "claim_abc123def456"})
MATCH (source {entity_id: "evt_battle_of_actium_q193304"})
MATCH (target {entity_id: "prd_roman_republic_q17167"})
MERGE (pedge:ProposedEdge {edge_id: "pedge_a1b2c3d4e5f6"})
SET pedge.claim_id = claim.claim_id,
    pedge.relationship_type = "OCCURRED_DURING",
    pedge.source_entity_id = source.entity_id,
    pedge.target_entity_id = target.entity_id,
    pedge.status = "proposed",
    pedge.created_at = "2026-02-17T14:15:00Z"
MERGE (claim)-[:ASSERTS_EDGE]->(pedge)
MERGE (pedge)-[:FROM]->(source)
MERGE (pedge)-[:TO]->(target)
```

---

## **6.9 ReasoningTrace Node Schema**

**Node Label:** `:ReasoningTrace`

**Purpose:** Persist the reasoning path by which an agent produced a claim: what was asked, what was retrieved, how steps were chained, and which sources were consulted. Enables explainability and audit trails.

### **Required Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `trace_id` | string | `"trace_000987"` | Unique ID |
| `agent_id` | string | `"roman_republic_agent_001"` | Agent that produced this trace |
| `query_text` | string | `"How did Caesar become dictator?"` | Original natural language query |
| `timestamp` | string | `"2026-02-12T15:30:00Z"` | When reasoning occurred |
| `pattern` | string | `"causal_chain"` | High-level reasoning pattern |

### **Optional Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `steps` | string[] | `["Retrieved passages...", "Connected Xâ†’Y"]` | Human-readable reasoning steps |
| `sources_consulted` | string[] | `["Goldsworthy p.145", "Plutarch 32"]` | Bibliographic strings |
| `retrieved_passages` | JSON[] | `[{"source": "Goldsworthy p.145", "text": "..."}]` | Key passages |
| `intermediate_claims` | string[] | `["claim_000120"]` | Supporting claims |
| `confidence` | float | `0.85` | Confidence in the reasoning chain |
| `reasoning_depth` | int | `3` | Number of reasoning hops |
| `fallacy_checks` | string[] | `["anachronism: pass"]` | Fallacy checks performed |

### **Required Edges**

| Relationship | Target | Notes |
|--------------|--------|-------|
| `TRACE_OF` | Claim | `(trace)-[:TRACE_OF]->(claim)` |
| `USED_FOR` | RetrievalContext | `(retrieval)-[:USED_FOR]->(trace)` (optional) |

### **Example Cypher**

```cypher
// Create reasoning trace
CREATE (trace:ReasoningTrace {
  trace_id: "trace_000987",
  agent_id: "roman_republic_agent_001",
  query_text: "How did Caesar become dictator?",
  timestamp: "2026-02-12T15:30:00Z",
  pattern: "causal_chain",
  steps: [
    "Retrieved passages from Plutarch and Suetonius",
    "Connected civil war â†’ dictatorship promotion",
    "Verified with scholarly sources"
  ],
  confidence: 0.85,
  reasoning_depth: 3
})

// Link to claim
MATCH (claim:Claim {claim_id: "claim_000123"})
CREATE (trace)-[:TRACE_OF]->(claim)
```

---

## **6.10 Synthesis & Consensus Resolution**

### **Synthesis Node Schema**

**Node Label:** `:Synthesis`

**Purpose:** When multiple agents produce conflicting claims or reviews, a Synthesis node records the consensus-building process and final resolution.

**Required Properties:**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `synthesis_id` | string | `"synth_000789"` | Unique ID |
| `timestamp` | string | `"2026-02-12T16:15:00Z"` | When synthesis was performed |
| `synthesis_type` | string | `"claim_consolidation"` | Type of synthesis performed |
| `consensus_method` | string | `"weighted_bayesian"` | Method used |

**Optional Properties:**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `participating_agents` | string[] | `["agent_001", "agent_002"]` | Agents involved |
| `input_claims` | string[] | `["claim_001", "claim_002"]` | Claims being synthesized |
| `output_claim` | string | `"claim_003"` | Resulting synthesized claim |
| `consensus_score` | float | `0.76` | Final consensus confidence |
| `resolution_strategy` | string | `"weighted_average"` | How conflicts were resolved |
| `notes` | string | `"Plutarch's figure accepted as upper bound"` | Summary |

**Required Edges:**

| Relationship | Target | Notes |
|--------------|--------|-------|
| `SYNTHESIZED_FROM` | Claim | Input claims |
| `PRODUCED` | Claim | Output claim |
| `PERFORMED_BY` | Agent | `(agent)-[:PERFORMED_BY]->(synthesis)` |

### **Consensus Calculation Cypher**

```cypher
// Calculate consensus score from reviews
MATCH (claim:Claim {claim_id: "claim_000123"})<-[:REVIEWS]-(review:Review)
WITH claim, 
     avg(review.confidence) AS avg_confidence,
     sum(review.weight * review.confidence) / sum(review.weight) AS weighted_confidence,
     collect(review.verdict) AS verdicts
WITH claim, weighted_confidence,
     size([v IN verdicts WHERE v = "support"]) AS support_count,
     size(verdicts) AS total_count
SET claim.consensus_score = weighted_confidence,
    claim.review_count = total_count,
    claim.status = CASE
        WHEN weighted_confidence >= 0.8 AND support_count >= total_count * 0.7 THEN "validated"
        WHEN weighted_confidence >= 0.5 THEN "disputed"
        ELSE "rejected"
    END
RETURN claim.claim_id, claim.status, claim.consensus_score
```

---

## **6.11 Claim Status Lifecycle**

Claims progress through a validation lifecycle from initial proposal to final disposition:

```
proposed â†’ (validated | disputed | rejected)
```

### **Status Definitions**

**proposed** - Created by a source agent, awaiting review
- Initial state after claim extraction
- Not yet visible in canonical graph
- Requires review by domain agents

**validated** - Supported by sufficient reviews (consensus_score â‰¥ 0.8)
- High confidence from multiple reviewers
- Support from â‰¥70% of reviews
- Proposed subgraph promoted to canonical graph
- Visible in standard queries

**disputed** - Mixed or low-confidence reviews (0.5 â‰¤ consensus_score < 0.8)
- Conflicting agent opinions
- Requires additional evidence or human review
- Not promoted to canonical graph
- Flagged for further investigation

**rejected** - Strong consensus against (consensus_score < 0.5)
- Low confidence from reviewers
- Majority of reviews challenge claim
- Not promoted to canonical graph
- May indicate extraction error or source misinterpretation

### **State Transition Rules**

```cypher
// Automatic status update based on consensus
MATCH (claim:Claim {status: "proposed"})
WHERE claim.review_count >= 3  // Minimum reviews required
WITH claim
MATCH (claim)<-[:REVIEWS]-(review:Review)
WITH claim,
     avg(review.confidence) AS avg_conf,
     sum(CASE WHEN review.verdict = "support" THEN 1 ELSE 0 END) * 1.0 / count(review) AS support_ratio
SET claim.status = CASE
    WHEN avg_conf >= 0.8 AND support_ratio >= 0.7 THEN "validated"
    WHEN avg_conf >= 0.5 THEN "disputed"
    ELSE "rejected"
END
```

---

## **6.12 Promotion Logic**

When a claim reaches `status = "validated"`, its proposed structure is **promoted** to the canonical graph.

### **Promotion Steps**

1. **Mark Claim validated/promoted**
   ```cypher
   MATCH (claim:Claim {claim_id: $claim_id})
   SET claim.status = "validated",
       claim.promoted = true,
       claim.promotion_date = datetime()
   ```

2. **Mark ProposedEdge validated/canonical**
   ```cypher
   MATCH (claim:Claim {claim_id: $claim_id})-[:ASSERTS_EDGE]->(pedge:ProposedEdge)-[:FROM]->(source)
   MATCH (pedge)-[:TO]->(target)
   SET pedge.status = "validated",
       pedge.promoted = true,
       pedge.promotion_status = "canonical",
       pedge.promotion_date = datetime()
   ```

3. **Materialize canonical relationship**
   ```cypher
   MATCH (claim:Claim {claim_id: $claim_id})-[:ASSERTS_EDGE]->(pedge:ProposedEdge)-[:FROM]->(source)
   MATCH (pedge)-[:TO]->(target)
   CALL apoc.create.relationship(
     source,
     pedge.relationship_type,
     {
       promoted_from_claim_id: claim.claim_id,
       promotion_date: datetime(),
       promotion_status: "canonical"
     },
     target
   ) YIELD rel
   RETURN rel
   ```

4. **Attach provenance**
   ```cypher
   MATCH (claim:Claim {claim_id: $claim_id})-[:ASSERTS_EDGE]->(pedge:ProposedEdge)-[:FROM]->(source)
   MATCH (pedge)-[:TO]->(target)
   MERGE (source)-[:SUPPORTED_BY {claim_id: claim.claim_id}]->(claim)
   MERGE (target)-[:SUPPORTED_BY {claim_id: claim.claim_id}]->(claim)
   ```

### **Key Properties**

- **Idempotent:** Promotion can be safely re-run without creating duplicates
- **Reversible:** Claims can be demoted if new evidence challenges consensus
- **Auditable:** Promotional edges maintain provenance trail

### **Query Pattern: Check Promotion Status**

```cypher
// Find all validated but unpromoted claims
MATCH (claim:Claim {status: "validated"})
WHERE claim.promoted IS NULL OR claim.promoted = false
RETURN claim.claim_id, claim.consensus_score, claim.review_count
ORDER BY claim.consensus_score DESC

// Find promoted structure for specific claim
MATCH (claim:Claim {claim_id: "claim_000123"})
MATCH (entity)-[rel:SUPPORTED_BY]->(claim)
RETURN entity, rel, claim
```

---

## **6.13 Integration with Other Layers**

The Claims Layer is deeply integrated with Entity (Section 3), Subject (Section 4), Agent (Section 5), and Relationship (Section 7) layers.

### **6.13.1 Subject Layer Integration**

Claims attach to SubjectConcepts for domain classification:

```cypher
(claim)-[:SUBJECT_OF]->(subjectConcept)
```

**Enables:**
- Topic classification by LCC/FAST
- Agent routing (Section 5.6)
- Facet alignment (Section 4.2)
- Domain-specific review
- Synthesis grouping

**Example: Route claim to domain experts**
```cypher
MATCH (claim:Claim {claim_id: "claim_000123"})-[:SUBJECT_OF]->(sc:SubjectConcept)
MATCH (agent:Agent)-[:OWNS_DOMAIN]->(sc)
RETURN agent.agent_id, agent.label, sc.lcc_class
```

### **6.13.2 Entity Layer Integration**

Claims attach to entities they describe:

```cypher
(entity)-[:SUBJECT_OF]->(claim)
```

**Enables:**
- Entity-centric reasoning
- Event interpretation
- Biographical claims
- Periodization claims
- Geographic claims

**Example: All claims about Caesar**
```cypher
MATCH (p:Human {qid: "Q1048"})-[:SUBJECT_OF]->(claim:Claim)
WHERE claim.status IN ["validated", "proposed"]
RETURN claim.text, claim.confidence, claim.status
ORDER BY claim.confidence DESC
```

### **6.13.3 Agent Layer Integration**

Agents interact with claims throughout their lifecycle:

**Agent Actions:**
- `MADE_CLAIM` - Create claims
- `REVIEWED` - Review claims  
- `PERFORMED_BY` - Perform synthesis
- `OWNS_DOMAIN` - Claim routing (via SubjectConcept)

**Example: Agent's claim history**
```cypher
MATCH (agent:Agent {agent_id: "roman_republic_agent"})-[:MADE_CLAIM]->(claim:Claim)
RETURN claim.claim_id, claim.text, claim.status, claim.consensus_score
ORDER BY claim.timestamp DESC

// Agent's review activity
MATCH (agent:Agent {agent_id: "roman_republic_agent"})-[:REVIEWED]->(review:Review)
      -[:REVIEWS]->(claim:Claim)
RETURN claim.claim_id, review.verdict, review.confidence
```

### **6.13.4 Relationship Layer Integration**

Claims propose relationships via ProposedEdge nodes:

```cypher
(claim)-[:ASSERTS_EDGE]->(proposed_edge:ProposedEdge)-[:FROM]->(source)
(proposed_edge)-[:TO]->(target)
```

**Upon validation:**
- ProposedEdge specifies relationship type from canonical registry (Section 7.1)
- Edge properties include action structure metadata (Section 7.6)
- Promoted edges maintain provenance links to originating claims

**Example: Claim proposing relationships**
```cypher
MATCH (claim:Claim {claim_id: "claim_000123"})-[:ASSERTS_EDGE]->(pedge:ProposedEdge)-[:FROM]->(from)
MATCH (pedge)-[:TO]->(to)
RETURN pedge.relationship_type, from.entity_id, to.entity_id, pedge.confidence

// After promotion: Find promoted relationship
MATCH (claim:Claim {claim_id: "claim_000123", status: "validated"})
MATCH (from)-[rel]->(to)
WHERE rel.promoted_from_claim_id = claim.claim_id
RETURN type(rel), from.name, to.name, rel.promotion_date
```

---

## **6.14 Cypher Query Patterns**

### **Pattern 1: Complete Claim Provenance Chain**

```cypher
// Trace claim from source to validation
MATCH (work:Work {qid: "Q644312"})
      <-[:EXTRACTED_FROM]-(claim:Claim {claim_id: "claim_000123"})
      <-[:MADE_CLAIM]-(agent:Agent)
OPTIONAL MATCH (claim)<-[:REVIEWS]-(review:Review)<-[:REVIEWED]-(reviewer:Agent)
OPTIONAL MATCH (claim)-[:HAS_TRACE]->(trace:ReasoningTrace)
RETURN work.title, agent.agent_id, claim.text, claim.status,
       collect(DISTINCT reviewer.agent_id) AS reviewers,
       trace.reasoning_depth
```

### **Pattern 2: Find Claims Needing Review**

```cypher
// Claims with insufficient reviews
MATCH (claim:Claim {status: "proposed"})
WHERE claim.review_count < 3
  AND duration.between(datetime(claim.timestamp), datetime()).days < 30
RETURN claim.claim_id, claim.text, claim.review_count, claim.confidence
ORDER BY claim.confidence DESC
LIMIT 20
```

### **Pattern 3: Consensus Analysis**

```cypher
// Analyze review distribution for claim
MATCH (claim:Claim {claim_id: "claim_000123"})<-[:REVIEWS]-(review:Review)
WITH claim,
     collect({
       agent: review.agent_id,
       verdict: review.verdict,
       confidence: review.confidence
     }) AS reviews,
     avg(review.confidence) AS avg_confidence
RETURN claim.claim_id,
       claim.consensus_score,
       avg_confidence,
       reviews
```

### **Pattern 4: Conflicting Claims Detection**

```cypher
// Find claims about same subject with conflicting assertions
MATCH (entity {qid: "Q1048"})-[:SUBJECT_OF]->(claim1:Claim)
MATCH (entity)-[:SUBJECT_OF]->(claim2:Claim)
WHERE claim1.claim_id < claim2.claim_id
  AND claim1.relationship_type = claim2.relationship_type
  AND claim1.object_entity_qid <> claim2.object_entity_qid
  AND claim1.status = "validated"
  AND claim2.status = "validated"
RETURN claim1.text, claim2.text, 
       claim1.consensus_score, claim2.consensus_score
```

---

# **7. Relationship Layer**

## **7.0 Relationship Layer Overview**

The **Relationship Layer** defines canonical relationship types connecting entities in the knowledge graph. Unlike Claims (which represent evidence), relationships are **first-class graph edges** supporting traversal, pattern matching, and graph algorithms.

### **Implementation Strategy**

**Tiered Rollout** (see Appendix V - ADR-002):
- **v1.0 Kernel**: 48 essential relationships - operational priority
- **v1.1 Expansion**: 50-75 specialized relationships - staged rollout
- **v2.0 Full Catalog**: 300 comprehensive relationship types - long-term goal

This staged approach enables **operational correctness** before **design completeness**, validating core traversal patterns in production before expanding to specialized research domains.

### **Key Principles**

**1. Triple Alignment Architecture**
- **Chrystallum:** Native relationship types optimized for historical research
- **Wikidata:** P-property alignment for linked data interoperability
- **CIDOC-CRM:** ISO 21127:2023 compliance for museum/archival integration

**2. Semantic Categorization**
- 300 canonical relationship types across 31 semantic categories (full catalog)
- v1.0 Kernel: 48 types across 7 core categories (current focus)
- Categories align with historical domains (Military, Political, Economic, etc.)
- Hierarchical with parent-child specificity levels

**3. Multi-Authority Metadata**
- **LCC classification:** Domain-specific routing (e.g., "D" for History)
- **LCSH heading:** Standardized terminology (e.g., "Military History")
- **FAST ID:** Faceted topic tagging for discovery

**4. Bidirectional Clarity**
- Forward/inverse/symmetric directionality explicitly defined
- Enables natural language expression from either entity perspective
- Reduces query complexity by providing both directions

**5. Lifecycle Management**
- Status tracking: `candidate`, `active`, `deprecated`
- Version control: tracks schema evolution
- Source attribution: links to discovery/import process

---

## **7.1 Relationship Type Schema**

### **Canonical Relationship Type Properties**

```cypher
(:RelationshipType {
  // IDENTIFICATION
  relationship_type: "FOUGHT_IN",           // Canonical type name
  category: "Military",                      // Semantic category
  
  // DESCRIPTION & DIRECTIONALITY
  description: "Person participated in battle/war",
  directionality: "forward",                 // forward | inverse | symmetric | unidirectional
  
  // TRIPLE ALIGNMENT
  wikidata_property: "P607",                 // Wikidata P-ID
  cidoc_crm_property: "P11_had_participant", // CIDOC-CRM property
  cidoc_crm_class: "E7_Activity",           // CRM class (if reified as event)
  
  // HIERARCHY & SPECIFICITY
  parent_relationship: "MILITARY_ACTION",    // Parent type (for hierarchy)
  specificity_level: 2,                      // 1=generic, 2=specific, 3=highly specific
  
  // AUTHORITY ALIGNMENT
  lcc_code: "U",                            // Library of Congress Class
  lcsh_heading: "Military History",         // LCSH subject heading
  fast_id: "fst01021997",                   // FAST topical ID
  
  // LIFECYCLE
  status: "active",                         // candidate | active | deprecated
  lifecycle_status: "implemented",          // candidate | implemented | deprecated
  version: "1.0",                           // Schema version
  source: "bidirectional_csv",              // Discovery source
  note: "Person as participant in military event"
})
```

---

## **7.2 Relationship Categories**

### **Distribution by Category (300 Total Relationship Types)**

| Category | Count | Description | Example Types |
|----------|-------|-------------|--------------|
| **Political** | 39 | Governance, power, institutions | APPOINTED, GOVERNED, ALLIED_WITH |
| **Familial** | 30 | Family relationships | FATHER_OF, MARRIED_TO, COUSIN_OF |
| **Military** | 23 | Warfare, command, battles | DEFEATED, COMMANDED_BY, BESIEGED |
| **Geographic** | 20 | Location, movement | BORN_IN, MIGRATED_TO, LOCATED_IN |
| **Economic** | 16 | Wealth, trade, taxation | TAXED, CONFISCATED_LAND_FROM |
| **Legal** | 13 | Law, justice, punishment | CONVICTED_OF, SENTENCED_TO |
| **Diplomatic** | 13 | Negotiation, alliances, envoys | NEGOTIATED_WITH, SENT_ENVOYS_TO |
| **Authorship** | 12 | Creation, attribution | AUTHOR, COMPOSER, ARCHITECT |
| **Attribution** | 11 | Citation, analysis, mention | EXTRACTED_FROM, DESCRIBES |
| **Application** | 10 | Material usage, production | MATERIAL_USED, PRODUCED_IN |
| **Evolution** | 10 | Change over time | REPLACED_BY, INTRODUCED_IN |
| **Institutional** | 9 | Organization membership | MEMBER_OF, PART_OF |
| **Position** | 8 | Roles, offices held | POSITION_HELD, HELD_POSITION_IN |
| **Cultural** | 8 | Cultural identity, assimilation | ASSIMILATED_TO, EVOLVED_FROM |
| **Honorific** | 8 | Awards, titles, decorations | AWARDED_TO, GRANTED_TITLE |
| **Causality** | 8 | Cause-effect relationships | CAUSED, CONTRIBUTED_TO |
| **Religious** | 6 | Faith, conversion, doctrine | CONVERTED_TO, RELIGIOUS_LEADER_OF |
| **Reasoning** | 6 | Inference, belief adoption | BELIEF_ABOUT, EVIDENCE_FOR |
| **Production** | 6 | Creation, manufacturing | DEPICTS, DISCOVERED_BY |
| **Social** | 6 | Patronage, social ties | PATRON_TO, SUPPORTER_OF |
| **Temporal** | 6 | Time relationships | DURING, PART_OF |
| **Functional** | 4 | Purpose, use | USE, USED_BY |
| **Comparative** | 4 | Superiority, inferiority | SUPERIOR_TO, ADVANTAGE |
| **Trade** | 3 | Commerce, exchange | TRADED_WITH, EXPORTED_TO |
| **Typological** | 3 | Type classification | SUBTYPE_OF, INSTANCE_OF |
| **Moral** | 3 | Ethics, justice | JUSTIFIED_BY, RIGHT_THING |
| **Linguistic** | 2 | Language, translation | TRANSLATION_OF, NAMED_AFTER |
| **Ideological** | 2 | Belief systems | IDEOLOGICAL_ALIGNMENT |
| **Membership** | 2 | Group belonging | TRIBE_MEMBERSHIP |
| **Measurement** | 2 | Quantification | MEASURED_AS |

---

## **7.3 Triple Alignment: Chrystallum â†” Wikidata â†” CIDOC-CRM**

### **Alignment Strategy**

**Purpose:** Enable interoperability with linked data (Wikidata) and cultural heritage systems (CIDOC-CRM) while maintaining Chrystallum's historical research optimizations.

**Benefits:**
1. **Museum/Archival Integration:** Export CIDOC-CRM compatible RDF/OWL
2. **Linked Data Queries:** Query via Wikidata SPARQL endpoints
3. **Academic Standards:** ISO 21127:2023 compliance
4. **Query Flexibility:** All three ontologies available simultaneously

### **Alignment Examples**

| Chrystallum Type | Wikidata Property | CIDOC-CRM Property | CIDOC-CRM Class |
|------------------|-------------------|--------------------|-----------------|
| **LOCATED_IN** | P131 (located in the administrative territorial entity) | crm:P7_took_place_at | â€” |
| **AUTHOR** | P50 (author) | crm:P14_carried_out_by | E12_Production |
| **FOUGHT_IN** | P607 (conflict) | crm:P11_had_participant | E7_Activity |
| **BORN_IN** | P19 (place of birth) | crm:P7_took_place_at | E67_Birth |
| **CAUSED** | P828 (has cause) | crm:P15_was_influenced_by | â€” |
| **APPOINTED** | P39 (position held) | crm:P14.1_in_the_role_of | E13_Attribute_Assignment |
| **PART_OF** | â€” | crm:P86_falls_within | â€” |
| **FOUNDED** | P112 (founded by) | crm:P14_carried_out_by | E63_Beginning_of_Existence |

### **Coverage Statistics**

**Full Catalog (v2.0 Target):**
- **Total Relationship Types:** 300
- **With Wikidata Alignment:** 147 (49%)
- **With CIDOC-CRM Alignment:** 89 (30%)
- **With Both Alignments:** 72 (24%)
- **Chrystallum-Specific:** 153 (51%) - optimized for historical research needs

**v1.0 Kernel (Current Implementation):**
- **Total Relationship Types:** 48 (see Appendix V)
- **With Wikidata Alignment:** 28 (58%)
- **Lifecycle Status:** 100% implemented (production-ready)
- **Categories Covered:** 7 core domains (Familial, Political, Military, Geographic, Authorship, Attribution, Temporal/Institutional)

**Note:** Chrystallum-specific relationships address historical domain needs not covered by general-purpose ontologies (e.g., Roman gens relationships, patron-client ties, proscription lists). The v1.0 kernel focuses on essential relationships that enable core graph traversal (Person↔Event, Person↔Place, Event↔Place, Work↔Person) before expanding to specialized domains.

---

## **7.4 Directionality Patterns**

### **Directionality Types**

**1. Forward (Source â†’ Target)**
```cypher
(:Human {name: "Caesar"})-[:FOUGHT_IN]->(:Event {label: "Battle of Pharsalus"})
```

**2. Inverse (Target â† Source)**
```cypher
(:Event {label: "Battle of Pharsalus"})-[:BATTLE_PARTICIPANT]->(:Human {name: "Caesar"})
```
*Note: Inverse types provide natural language clarity from the opposite entity perspective*

**3. Symmetric (Bidirectional)**
```cypher
(:Human {name: "Caesar"})-[:ALLIED_WITH]->(:Human {name: "Pompey"})
(:Human {name: "Pompey"})-[:ALLIED_WITH]->(:Human {name: "Caesar"})
```
*Note: Symmetric relationships create edges in both directions*

**4. Unidirectional (Single Direction)**
```cypher
(:Event {label: "Death of Caesar"})-[:CAUSED]->(:Event {label: "Second Triumvirate"})
```
*Note: No inverse relationship type defined*

### **Bidirectional Pairs (Forward/Inverse)**

Common patterns enabling natural queries from either entity:

| Forward | Inverse | Example |
|---------|---------|---------|
| FATHER_OF | CHILD_OF | Caesar FATHER_OF Julia / Julia CHILD_OF Caesar |
| FOUNDED | FOUNDED_BY | Caesar FOUNDED colony / Colony FOUNDED_BY Caesar |
| CONQUERED | CONQUERED_BY | Rome CONQUERED Gaul / Gaul CONQUERED_BY Rome |
| AUTHOR | WORK_OF | Plutarch AUTHOR "Life of Caesar" / "Life of Caesar" WORK_OF Plutarch |
| PRODUCES_GOOD | PRODUCED_BY | Factory PRODUCES_GOOD pottery / Pottery PRODUCED_BY factory |

---

## **7.5 Hierarchical Relationships (Parent-Child Specificity)**

### **Specificity Levels**

**Level 1 (Generic):** Broad categories
- `MILITARY_ACTION`, `POLITICAL_ACTION`, `ECONOMIC_ACTION`
- Used when specific relationship type unknown or inapplicable

**Level 2 (Specific):** Common historical relationships
- `FOUGHT_IN`, `APPOINTED`, `TAXED`
- Most common level for historical research

**Level 3 (Highly Specific):** Nuanced distinctions
- `COMMANDED_CAVALRY_IN`, `PROSCRIBED`, `CONDEMNED_WITHOUT_TRIAL`
- Captures fine-grained historical detail

### **Hierarchical Examples**

**Military Hierarchy:**
```
MILITARY_ACTION (level 1)
  â”œâ”€ FOUGHT_IN (level 2)
  â”œâ”€ COMMANDED_BY (level 2)
  â”‚   â””â”€ COMMANDED_CAVALRY_IN (level 3)
  â”œâ”€ DEFEATED (level 2)
  â””â”€ BESIEGED (level 2)
```

**Political Hierarchy:**
```
POLITICAL_ACTION (level 1)
  â”œâ”€ APPOINTED (level 2)
  â”‚   â””â”€ APPOINTED_CONSUL (level 3)
  â”œâ”€ GOVERNED (level 2)
  â””â”€ DEPOSED (level 2)
```

**Economic Hierarchy:**
```
ECONOMIC_ACTION (level 1)
  â”œâ”€ TAXED (level 2)
  â”œâ”€ CONFISCATED_LAND_FROM (level 2)
  â””â”€ DISTRIBUTED_LAND_TO (level 2)
```

**Benefits:**
- Enables query generalization (find all `MILITARY_ACTION` relationships)
- Supports progressive refinement (start broad, drill down to specifics)
- Facilitates agent routing (broad categories â†’ specialist agents)

---

## **7.6 Action Structure Integration**

### **Action Structure Vocabularies**

Chrystallum incorporates **goal-trigger-action-result** framework for understanding historical events. This structured approach enables agents to reason about motivation, causality, and outcomes.

**Vocabulary Categories:**

**1. Goal Types (14 vocabularies)**
- Political, Personal, Military, Economic, Constitutional, Moral, Cultural, Religious, Diplomatic, Survival
- *Example:* "Caesar's goal: Gain political power (POLITICAL)"

**2. Trigger Types (10 vocabularies)**
- Circumstantial, Moral, Emotional, Political, Personal, External Threat, Internal Pressure, Legal, Ambition, Opportunity
- *Example:* "Trigger: Senate threatens prosecution (POLITICAL_TRIGGER)"

**3. Action Types (16 vocabularies)**
- Political Revolution, Military Action, Criminal Act, Diplomatic Action, Constitutional Innovation, Economic Action, Legal Action, Social Action, Religious Action, Personal Action, Administrative, Causal Chain, Tyrannical Governance, Defensive Action, Offensive Action
- *Example:* "Action: Cross Rubicon with army (MILITARY_ACTION)"

**4. Result Types (14 vocabularies)**
- Political Transformation, Institutional Creation, Conquest, Defeat, Alliance, Tragic, Success, Failure, Stability, Instability, Legal Outcome, Cultural Change, Personal Outcome, Economic Outcome
- *Example:* "Result: Civil war begins (POLITICAL_TRANSFORMATION)"

### **Integration with Relationship Types**

Action structure properties are **optional annotations** on relationship edges, enabling richer historical analysis:

```cypher
(:Human {name: "Caesar"})
  -[:CAUSED {
      goal_type: "POLITICAL",
      trigger_type: "POLITICAL_TRIGGER", 
      action_type: "MILITARY_ACTION",
      result_type: "POLITICAL_TRANSFORMATION",
      goal_description: "Assert power against Senate",
      trigger_description: "Senate threatens prosecution",
      action_description: "Cross Rubicon with legion",
      result_description: "Start of civil war"
    }]->
(:Event {label: "Roman Civil War"})
```

### **Wikidata Property Mapping**

Action structure types align with Wikidata qualifiers:

| Action Component | Wikidata Property | Example |
|------------------|-------------------|---------|
| **Goal** | P3712 (objective) | "Gain territory" |
| **Trigger** | P828 (has cause) | "Enemy invasion" |
| **Action** | P279 (subclass of) | "Military campaign" |
| **Result** | P1542 (has effect) | "Conquest completed" |

**Source:** `CSV/action_structure_vocabularies.csv`, `CSV/action_structure_wikidata_mapping.csv`

---

## **7.7 Key Relationship Types by Domain**

### **7.7.1 Military Relationships (23 types)**

| Relationship Type | Directionality | Wikidata | CIDOC-CRM | Description |
|-------------------|----------------|----------|-----------|-------------|
| **FOUGHT_IN** | forward | P607 | P11_had_participant | Person participated in battle/war |
| **BATTLE_PARTICIPANT** | inverse | â€” | P11i_participated_in | Battle had this participant |
| **DEFEATED** | forward | â€” | â€” | Victor defeated vanquished entity |
| **DEFEATED_BY** | inverse | â€” | â€” | Vanquished was defeated by victor |
| **COMMANDED_BY** | forward | â€” | P14_carried_out_by | Military unit commanded by person |
| **SERVED_UNDER** | forward | â€” | â€” | Person served under commander |
| **BESIEGED** | forward | â€” | â€” | Entity besieged location |
| **BESIEGED_BY** | inverse | â€” | â€” | Location was besieged by entity |
| **CONQUERED** | forward | P47 | E8_Acquisition | Entity conquered territory |
| **CONQUERED_BY** | inverse | P47 | E8_Acquisition | Territory conquered by entity |
| **MASSACRED** | forward | â€” | â€” | Entity massacred group |
| **LEVELLED** | forward | â€” | E6_Destruction | Entity destroyed/leveled location |
| **SACKED** | forward | â€” | â€” | Entity sacked/pillaged location |
| **GARRISONED** | forward | â€” | â€” | Entity garrisoned troops at location |
| **BETRAYED** | forward | â€” | â€” | Entity betrayed another entity |
| **DEFECTED_TO** | forward | â€” | E85_Joining | Entity defected to another allegiance |

**Example Cypher:**
```cypher
// Find all battles Caesar fought in
MATCH (caesar:Human {name: "Gaius Julius Caesar"})
      -[:FOUGHT_IN]->(battle:Event {event_type: "battle"})
RETURN battle.label, battle.start_date, battle.location

// Find who defeated Pompey
MATCH (pompey:Human {name: "Pompey"})<-[:DEFEATED]-(victor:Human)
RETURN victor.name, battle.label

// Military command structure
MATCH (commander:Human)-[:COMMANDED_BY*1..3]-(subordinate:Human)
WHERE commander.name = "Caesar"
RETURN subordinate.name, subordinate.rank
```

---

### **7.7.2 Political Relationships (39 types)**

| Relationship Type | Directionality | Wikidata | CIDOC-CRM | Description |
|-------------------|----------------|----------|-----------|-------------|
| **APPOINTED** | forward | P39 | E13_Attribute_Assignment | Appointer appointed person to office |
| **APPOINTED_BY** | inverse | P39 | E13_Attribute_Assignment | Person was appointed by appointer |
| **GOVERNED** | forward | â€” | â€” | Person governed jurisdiction during period |
| **CONTROLLED** | forward | P17 | â€” | Entity controlled territory/institution |
| **ALLIED_WITH** | symmetric | â€” | â€” | Entities formed alliance |
| **OPPOSED** | symmetric | â€” | â€” | Entities were in opposition |
| **DEPOSED** | forward | â€” | E86_Leaving | Entity deposed ruler from power |
| **PROSCRIBED** | forward | â€” | E13_Attribute_Assignment | Authority proscribed person (outlawed with property confiscation) |
| **OUTLAWED** | forward | â€” | E13_Attribute_Assignment | Authority outlawed person |
| **LEGITIMATED** | forward | â€” | â€” | Entity legitimated authority's power |
| **DECLARED_FOR** | forward | â€” | â€” | Entity declared allegiance to another |
| **COMPETED_WITH** | symmetric | â€” | â€” | Entities competed for power/office |
| **ADVISED** | forward | â€” | â€” | Advisor advised leader/institution |
| **MANIPULATED** | forward | â€” | â€” | Entity manipulated another for political aims |
| **HEIR_TO** | forward | P1365 | â€” | Person designated heir to position/realm |

**Example Cypher:**
```cypher
// Find Caesar's political appointments
MATCH (caesar:Human {name: "Caesar"})-[:APPOINTED]->(appointee:Human)
      -[:POSITION_HELD]->(position:Position)
RETURN appointee.name, position.label, position.start_date

// Find who opposed Caesar
MATCH (caesar:Human {name: "Caesar"})-[:OPPOSED]-(opponent:Human)
RETURN opponent.name

// Political alliance network
MATCH path = (entity:Human)-[:ALLIED_WITH*1..3]-(ally:Human)
WHERE entity.entity_id = "hum_caesar"
RETURN ally.name, length(path) AS degrees_of_alliance
```

---

### **7.7.3 Familial Relationships (30 types)**

| Relationship Type | Directionality | Wikidata | CIDOC-CRM | Description |
|-------------------|----------------|----------|-----------|-------------|
| **FATHER_OF** | forward | P40 | â€” | Person is father of child |
| **CHILD_OF** | inverse | P22 | â€” | Person is child of parent |
| **MARRIED_TO** | symmetric | P26 | â€” | Person married to spouse |
| **SIBLING_OF** | symmetric | P3373 | â€” | Person is sibling |
| **HALF_SIBLING_OF** | symmetric | P3373 | â€” | Person is half-sibling |
| **GRANDPARENT_OF** | forward | â€” | â€” | Person is grandparent of grandchild |
| **GRANDCHILD_OF** | inverse | â€” | â€” | Person is grandchild of grandparent |
| **COUSIN_OF** | symmetric | â€” | â€” | Person is cousin |
| **AUNT_OF** | forward | â€” | â€” | Person is aunt/uncle |
| **ADOPTED_BY** | forward | â€” | â€” | Person was adopted by adopter |
| **FATHER_IN_LAW_OF** | forward | â€” | â€” | Person is father-in-law |
| **BROTHER_IN_LAW_OF** | forward | â€” | â€” | Person is brother-in-law |
| **DAUGHTER_IN_LAW_OF** | forward | â€” | â€” | Person is daughter-in-law |

**Roman-Specific Familial:**
| **MEMBER_OF_GENS** | forward | â€” | â€” | Person member of Roman gens (clan) |
| **GENS_OF** | inverse | â€” | â€” | Gens contains this person |
| **HAS_PRAENOMEN** | forward | â€” | â€” | Person has Roman praenomen (personal name) |
| **HAS_COGNOMEN** | forward | â€” | â€” | Person has Roman cognomen (family branch name) |

**Example Cypher:**
```cypher
// Find Caesar's family tree (3 generations)
MATCH path = (caesar:Human {name: "Caesar"})
             -[:FATHER_OF|CHILD_OF|SIBLING_OF*1..3]-(relative:Human)
RETURN relative.name, labels(relative), length(path)

// Roman gens membership
MATCH (person:Human)-[:MEMBER_OF_GENS]->(gens:Gens {name: "Julia"})
RETURN person.name, person.praenomen, person.cognomen

// Marriage alliances
MATCH (person1:Human)-[:MARRIED_TO]->(person2:Human)
WHERE (person1)-[:MEMBER_OF_GENS]->(:Gens {name: "Julia"})
RETURN person1.name, person2.name, person2.gens_name
```

---

### **7.7.4 Geographic Relationships (20 types)**

| Relationship Type | Directionality | Wikidata | CIDOC-CRM | Description |
|-------------------|----------------|----------|-----------|-------------|
| **BORN_IN** | forward | P19 | P7_took_place_at | Person born in location |
| **DIED_IN** | forward | P20 | P7_took_place_at | Person died in location |
| **LIVED_IN** | forward | P551 | â€” | Person resided in location during period |
| **LOCATED_IN** | forward | P131 | P7_took_place_at | Entity located in geographic region |
| **MIGRATED_TO** | forward | â€” | P26_moved_to | Group migrated to destination |
| **MIGRATED_FROM** | forward | â€” | P27_moved_from | Group migrated from origin |
| **EXILED** | forward | â€” | â€” | Authority exiled person to location |
| **FLED_TO** | forward | â€” | â€” | Person fled to safe location |
| **FLED_FROM** | forward | â€” | â€” | Person fled from dangerous location |
| **FOUNDED** | forward | P112 | E63_Beginning_of_Existence | Founder established place/institution in location |
| **CAMPAIGN_IN** | forward | â€” | â€” | Military campaign occurred in region |
| **RENAMED** | forward | P1448 | E15_Identifier_Assignment | Entity renamed place |

**Example Cypher:**
```cypher
// Find where Caesar lived
MATCH (caesar:Human {name: "Caesar"})-[:LIVED_IN]->(place:Place)
RETURN place.label, place.place_type

// Migration patterns
MATCH (group:Group)-[:MIGRATED_FROM]->(origin:Place),
      (group)-[:MIGRATED_TO]->(dest:Place)
RETURN group.name, origin.label, dest.label

// Exile network
MATCH (person:Human)-[:EXILED]->(:Place {label: "Massilia"})
RETURN person.name, person.exile_start_date
```

---

### **7.7.5 Diplomatic Relationships (13 types)**

| Relationship Type | Directionality | Wikidata | Description |
|-------------------|----------------|----------|-------------|
| **NEGOTIATED_WITH** | symmetric | â€” | Entities engaged in negotiations |
| **SENT_ENVOYS_TO** | forward | â€” | Sender dispatched envoys to recipient |
| **RECEIVED_ENVOYS_FROM** | inverse | â€” | Recipient received envoys from sender |
| **APPEALED_TO** | forward | â€” | Appellant requested help from entity |
| **RECEIVED_APPEAL_FROM** | inverse | â€” | Entity received request for help |
| **ACCEPTED_OFFER** | forward | â€” | Entity accepted diplomatic offer |
| **REJECTED_OFFER** | forward | â€” | Entity rejected diplomatic offer |
| **OFFERED_SELF_TO** | forward | â€” | Entity offered allegiance/submission |
| **RECEIVED_OFFER_FROM** | inverse | â€” | Entity received offer of allegiance |

**Example Cypher:**
```cypher
// Diplomatic negotiations between Rome and tribes
MATCH (rome:Organization {name: "Roman Republic"})
      -[:NEGOTIATED_WITH]-(tribe:Group)
WHERE tribe.group_type = "Germanic tribe"
RETURN tribe.name, tribe.treaty_date

// Envoy network
MATCH (sender)-[:SENT_ENVOYS_TO]->(recipient)
WHERE sender.name CONTAINS "Rome"
RETURN recipient.name, COUNT(*) AS envoy_missions
ORDER BY envoy_missions DESC

// Failed diplomacy leading to war
MATCH (entity1)-[:REJECTED_OFFER]->(offer),
      (offer)<-[:MADE_OFFER]-(entity2),
      (entity1)-[:FOUGHT_IN]->(war:Event),
      (entity2)-[:FOUGHT_IN]->(war)
RETURN entity1.name, entity2.name, war.label
```

---

### **7.7.6 Economic Relationships (16 types)**

| Relationship Type | Directionality | Wikidata | Description |
|-------------------|----------------|----------|-------------|
| **CONFISCATED_LAND_FROM** | forward | â€” | Authority confiscated property from owner |
| **DISTRIBUTED_LAND_TO** | forward | â€” | Authority distributed land to recipients |
| **TAXED** | forward | â€” | Authority taxed entity/territory |
| **PRODUCES_GOOD** | forward | P1056 | Entity produces goods/services |
| **PRODUCED_BY** | inverse | P1056 | Goods produced by entity |
| **TRADED_WITH** | symmetric | â€” | Entities engaged in trade |
| **EXPORTED_TO** | forward | â€” | Entity exported goods to destination |
| **IMPORTED_FROM** | forward | â€” | Entity imported goods from source |
| **SOLD_INTO_SLAVERY** | forward | â€” | Entity sold people into slavery |
| **EXPERIENCED_RECESSION** | forward | â€” | Economy experienced recession during period |

**Example Cypher:**
```cypher
// Land confiscation during proscriptions
MATCH (authority)-[:CONFISCATED_LAND_FROM]->(victim:Human)
      -[:PROSCRIBED_BY]->(authority)
WHERE authority.name = "Second Triumvirate"
RETURN victim.name, victim.property_value

// Trade networks
MATCH path = (city1:Place)-[:TRADED_WITH*1..3]-(city2:Place)
WHERE city1.label = "Rome"
RETURN city2.label, length(path) AS trade_distance

// Economic production chains
MATCH (region:Place)-[:PRODUCES_GOOD]->(good:Material)
      -[:EXPORTED_TO]->(destination:Place {label: "Rome"})
RETURN region.label, good.name, COUNT(*) AS export_volume
```

---

### **7.7.7 Legal Relationships (13 types)**

| Relationship Type | Directionality | Wikidata | CIDOC-CRM | Description |
|-------------------|----------------|----------|-----------|-------------|
| **CHARGED_WITH** | forward | â€” | E13_Attribute_Assignment | Person charged with crime |
| **CONVICTED_OF** | forward | P1399 | E13_Attribute_Assignment | Person convicted of crime |
| **SENTENCED_TO** | forward | â€” | E13_Attribute_Assignment | Person sentenced to punishment |
| **EXECUTED** | forward | â€” | E69_Death | Authority executed person |
| **IMPRISONED_IN** | forward | â€” | â€” | Person imprisoned in facility |
| **CONDEMNED_WITHOUT_TRIAL** | forward | â€” | â€” | Authority condemned person without legal process |
| **LEGAL_ACTION** | unidirectional | â€” | â€” | Generic legal proceeding |

**Example Cypher:**
```cypher
// Caesar's assassination conspirators - legal aftermath
MATCH (conspirator:Human)-[:PARTICIPATED_IN]->(:Event {label: "Assassination of Caesar"})
OPTIONAL MATCH (conspirator)-[:CHARGED_WITH]->(crime),
               (conspirator)-[:EXECUTED_BY]->(executor)
RETURN conspirator.name, crime.label, executor.name

// Proscription victims
MATCH (victim:Human)-[:PROSCRIBED]->(authority)
      -[:CONDEMNED_WITHOUT_TRIAL]->(victim)
RETURN victim.name, authority.name, victim.proscription_date

// Prison locations
MATCH (person:Human)-[:IMPRISONED_IN]->(facility:Place)
WHERE facility.place_type = "prison"
RETURN facility.label, COUNT(person) AS prisoner_count
```

---

### **7.7.8 Temporal Relationships (6 types)**

| Relationship Type | Directionality | CIDOC-CRM | Description |
|-------------------|----------------|-----------|-------------|
| **DURING** | forward | P4_has_time-span | Event occurred during period |
| **PART_OF** | forward | P86_falls_within | Year/decade/century falls within larger temporal span |
| **SUB_PERIOD_OF** | forward | P9_consists_of | Period is subdivision of larger period |
| **CONTAINS_EVENT** | inverse | P9i_forms_part_of | Period contains event |
| **START_EDGE** | forward | P4_has_time-span | Marks beginning of period |
| **END_EDGE** | forward | P4_has_time-span | Marks end of period |

**Example Cypher:**
```cypher
// Events during Roman Republic period
MATCH (event:Event)-[:DURING]->(period:Period {label: "Roman Republic"})
RETURN event.label, event.start_date
ORDER BY event.start_date

// Period hierarchy (Roman history)
MATCH path = (sub_period:Period)-[:SUB_PERIOD_OF*1..3]->(period:Period)
WHERE period.label = "Ancient Rome"
RETURN sub_period.label, length(path) AS depth

// Beginning/end markers
MATCH (period:Period {label: "Roman Republic"})
OPTIONAL MATCH (period)-[:START_EDGE]->(start_event:Event)
OPTIONAL MATCH (period)-[:END_EDGE]->(end_event:Event)
RETURN period.label, start_event.label, end_event.label
```

---

### **7.7.9 Attribution & Citation Relationships (11 types)**

| Relationship Type | Directionality | Description |
|-------------------|----------------|-------------|
| **EXTRACTED_FROM** | forward | Claim extracted from source work |
| **DESCRIBES** | forward | Citation describes entity/event |
| **MENTIONS** | forward | Citation mentions entity |
| **ANALYZES** | forward | Citation provides analysis of entity |
| **INTERPRETS** | forward | Citation interprets entity/event |
| **SUMMARIZES** | forward | Citation summarizes entity/event |
| **QUOTES** | forward | Citation is direct quote from source |
| **ATTRIBUTED_TO** | forward | Citation attributed to author |

**Example Cypher:**
```cypher
// Find all sources describing Caesar's death
MATCH (work:Work)-[:DESCRIBES]->(event:Event {label: "Death of Caesar"})
RETURN work.title, work.author_name, work.composition_date

// Citation network for specific claim
MATCH (claim:Claim)-[:EXTRACTED_FROM]->(passage:Passage)
      -[:PART_OF]->(work:Work)
      -[:ATTRIBUTED_TO]->(author:Human)
RETURN author.name, work.title, passage.citation, claim.confidence

// Most frequently cited works
MATCH (work:Work)<-[:EXTRACTED_FROM]-(claim:Claim)
RETURN work.title, COUNT(claim) AS citation_count
ORDER BY citation_count DESC
LIMIT 10
```

---

## **7.8 Relationship Constraints & Validation**

### **Neo4j Schema Constraints**

```cypher
// Ensure relationship types exist in canonical registry
CREATE CONSTRAINT relationship_type_exists
FOR ()-[r]-()
REQUIRE r.relationship_type IN [list of canonical types]

// Require triple alignment metadata on all relationships
CREATE CONSTRAINT relationship_has_alignment
FOR ()-[r]-()
REQUIRE r.relationship_type IS NOT NULL

// Index for relationship type lookups
CREATE INDEX relationship_type_index
FOR ()-[r]-()
ON (r.relationship_type)

// Index for action structure queries
CREATE INDEX action_structure_index
FOR ()-[r]-()
ON (r.goal_type, r.action_type, r.result_type)
```

### **Validation Rules**

**1. Relationship Type Existence**
- All relationships MUST use canonical relationship types from registry
- Agent output validation checks against canonical list
- Unknown types flagged for review

**2. Directionality Compliance**
- Forward relationships: Source â†’ Target  
- Inverse relationships: Target â† Source
- Symmetric relationships: Both directions created
- Unidirectional: Only specified direction allowed

**3. Domain/Range Constraints (Selected)**
```cypher
// BORN_IN: Human â†’ Place
MATCH (h:Human)-[:BORN_IN]->(p)
WHERE NOT p:Place
RETURN "Invalid BORN_IN target" AS error, h.entity_id, id(p)

// AUTHOR: Human â†’ Work
MATCH (h:Human)-[:AUTHOR]->(w)
WHERE NOT w:Work
RETURN "Invalid AUTHOR target" AS error, h.entity_id, id(w)

// FATHER_OF: Human â†’ Human  
MATCH (h1:Human)-[:FATHER_OF]->(h2)
WHERE NOT h2:Human
RETURN "Invalid FATHER_OF target" AS error, h1.entity_id, id(h2)
```

**4. Triple Alignment Completeness**
- Wikidata property stored when alignment exists
- CIDOC-CRM property stored when alignment exists
- NULL allowed for Chrystallum-specific relationships

---

## **7.9 Cypher Query Patterns**

### **Pattern 1: Entity-Centric Relationship Discovery**

```cypher
// Find all relationships for specific entity
MATCH (entity {entity_id: $entity_id})-[r]->(related)
RETURN type(r) AS relationship_type, 
       labels(related) AS related_entity_types,
       related.name AS related_name,
       r.goal_type AS goal,
       r.result_type AS result
```

### **Pattern 2: Relationship Type Filtering**

```cypher
// Find all military relationships
MATCH (e1)-[r]->(e2)
WHERE r.relationship_type IN [
  "FOUGHT_IN", "DEFEATED", "COMMANDED_BY", 
  "BESIEGED", "CONQUERED"
]
RETURN e1.name, type(r), e2.name
```

### **Pattern 3: Action Structure Analysis**

```cypher
// Find relationships with specific goal-action-result pattern
MATCH (entity1)-[r]->(entity2)
WHERE r.goal_type = "POLITICAL"
  AND r.action_type = "MILITARY_ACTION"
  AND r.result_type = "POLITICAL_TRANSFORMATION"
RETURN entity1.name, 
       r.goal_description,
       r.action_description, 
       r.result_description,
       entity2.name
```

### **Pattern 4: Triple Alignment Queries**

```cypher
// Query using Wikidata property
MATCH (e1)-[r]->(e2)
WHERE r.wikidata_property = "P607"  // P607 = conflict
RETURN e1.name, e2.label, r.relationship_type

// Query using CIDOC-CRM property
MATCH (e1)-[r]->(e2)
WHERE r.cidoc_crm_property = "P11_had_participant"
RETURN e1.name, e2.label, r.cidoc_crm_class
```

### **Pattern 5: Multi-Hop Traversal**

```cypher
// Find indirect connections (3 degrees)
MATCH path = (caesar:Human {name: "Caesar"})
             -[*1..3]-(connected)
WHERE connected:Human OR connected:Organization
RETURN connected.name, 
       length(path) AS degrees_of_separation,
       [r IN relationships(path) | type(r)] AS relationship_chain
ORDER BY degrees_of_separation
LIMIT 20
```

### **Pattern 6: Hierarchical Relationship Queries**

```cypher
// Find all specific types under generic MILITARY_ACTION
MATCH (e1)-[r]->(e2)
WHERE r.parent_relationship = "MILITARY_ACTION"
   OR r.relationship_type = "MILITARY_ACTION"
RETURN DISTINCT r.relationship_type, COUNT(*) AS usage_count
ORDER BY usage_count DESC
```

---

## **7.10 Relationship Evolution & Versioning**

### **Lifecycle States**

| Status | Description | Agent Behavior |
|--------|-------------|----------------|
| **candidate** | Proposed relationship type, under review | Agents flag but don't use |
| **active** | Production-ready, validated | Agents use freely |
| **deprecated** | Superseded by newer type | Agents create warnings, suggest replacement |

### **Version Tracking**

```cypher
(:RelationshipType {
  relationship_type: "FOUGHT_IN",
  version: "1.0",
  created_date: "2025-12-01",
  last_modified: "2026-01-15",
  change_log: [
    "1.0: Initial implementation",
    "1.1: Added action structure properties"
  ]
})
```

### **Deprecation Pattern**

```cypher
// Old relationship type deprecated
(:RelationshipType {
  relationship_type: "PARTICIPATED_IN_BATTLE",
  status: "deprecated",
  lifecycle_status: "deprecated",
  deprecated_date: "2026-01-15",
  superseded_by: "FOUGHT_IN",
  deprecation_reason: "Merged into FOUGHT_IN for consistency"
})

// New relationship type active
(:RelationshipType {
  relationship_type: "FOUGHT_IN",
  status: "active",
  replaces: ["PARTICIPATED_IN_BATTLE", "ENGAGED_IN_COMBAT"]
})
```

### **Migration Strategy**

When deprecating relationship types:
1. Mark old type as `deprecated` (don't delete)
2. Create `superseded_by` link to replacement type
3. Add agent validation warnings
4. Provide migration Cypher query
5. Preserve old relationships for historical research

```cypher
// Migration query example
MATCH (e1)-[old:PARTICIPATED_IN_BATTLE]->(e2)
CREATE (e1)-[new:FOUGHT_IN]->(e2)
SET new = properties(old)
SET new.relationship_type = "FOUGHT_IN"
SET new.migrated_from = "PARTICIPATED_IN_BATTLE"
SET new.migration_date = datetime()
// Optionally delete old relationship after verification
```

---

# **PART III: IMPLEMENTATION & TECHNOLOGY**

---

