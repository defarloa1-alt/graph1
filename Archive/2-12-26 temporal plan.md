
Here’s a clear ingestion pipeline design for the period data, in three phases: import, classify, and clean. You can turn each phase into Python + Cypher scripts.[time_periods.csv+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cb359094-cf85-41fb-9ef5-e94df223b520/time_periods.csv)

---

## Phase 1 — Ingest `time_periods.csv` as Candidate Periods

**Input:** `time_periods.csv` with columns `QID, Label, Start, End, LocationCount, Locations, Facets, FacetRelationships`.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cb359094-cf85-41fb-9ef5-e94df223b520/time_periods.csv)]​

## 1.1 Normalize QID and basic fields

- Strip angle brackets: `<http://www.wikidata.org/entity/Q202390>` → `Q202390`.
    
- Convert `Start`/`End` to integers, store string versions for your `:Period` schema (`start`, `end`).
    
- Parse `Locations` into an array of QIDs.
    
- Parse `Facets` and `FacetRelationships` from the stringified arrays.
    

## 1.2 Create Period nodes

For each CSV row (before applying Tier logic):

text

`// Ensure uniqueness on qid CREATE CONSTRAINT period_qid IF NOT EXISTS FOR (p:Period) REQUIRE p.qid IS UNIQUE; // Example upsert for one row MERGE (p:Period {qid: $qid}) SET p.period_id = COALESCE(p.period_id, 'prd_' + replace($qid,'Q','')),     p.label     = $label,    p.start     = toString($start),    p.end       = toString($end);`

## 1.3 Attach to Year backbone (minimal wiring)

Assuming `:Year {year: int}` already exists for the full range.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/1f675f67-89d8-4bf8-a447-52317c814ec9/2-12-26-Temporal-Schema.md)]​

text

`// Link Period to start/end Year MATCH (p:Period {qid: $qid}) MATCH (startY:Year {year: toInteger($start)}) MATCH (endY:Year   {year: toInteger($end)}) MERGE (p)-[:STARTS_IN_YEAR]->(startY) MERGE (p)-[:ENDS_IN_YEAR]->(endY);`

## 1.4 Attach facets

Facets arrive as parallel arrays: e.g. `Facets = ["CulturalFacet","ArchaeologicalFacet"]`, `FacetRelationships = ["HAS_CULTURAL_FACET","HAS_ARCHAEOLOGICAL_FACET"]`.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cb359094-cf85-41fb-9ef5-e94df223b520/time_periods.csv)]​

Implementation pattern:

- In Python: zip `Facets[i]` with `FacetRelationships[i]`.
    
- For each pair, call a parametrized Cypher query:
    

text

`// $facet_label like "CulturalFacet", $rel like "HAS_CULTURAL_FACET" MATCH (p:Period {qid: $qid}) MERGE (f:Facet {label: $facet_label}) CALL apoc.create.relationship(p, $rel, {}, f) YIELD rel RETURN rel;`

---

## Phase 2 — Apply Tiered Classification (Period vs Event vs InstitutionalSpan vs Drop)

**Input:** `PERIOD_CLASSIFICATION_PLAN.md` → converted into `period_classification.csv`.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/56d011ad-0a9f-419d-a537-20e8142603dc/PERIOD_CLASSIFICATION_PLAN.md)]​

Example `period_classification.csv`:[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/56d011ad-0a9f-419d-a537-20e8142603dc/PERIOD_CLASSIFICATION_PLAN.md)]​

text

`qid,current_label,classification,action,new_node_type,reason Q185047,Spring and Autumn period,KEEP,none,Period,Standard historiographic period Q129167,barracks emperor,EVENT,convert,Event,Short crisis period Q23019825,Rehnquist Court,INSTITUTIONAL,convert,InstitutionalSpan,Court term Q12793702,Classics,PROBLEMATIC,delete,N/A,Discipline not period ...`

## 2.1 KEEP → leave as Period

No structural change; these remain your canonical `:Period` set.

Optional: mark them explicitly:

text

`MATCH (p:Period {qid: $qid}) SET p.period_status = "canonical";`

## 2.2 EVENT → convert Period to Event

For Tier 2 entries (short crises, phases):[PERIOD_CLASSIFICATION_PLAN.md+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/56d011ad-0a9f-419d-a537-20e8142603dc/PERIOD_CLASSIFICATION_PLAN.md)

text

`MATCH (p:Period {qid: $qid}) SET p:Event        // add Event label REMOVE p:Period    // remove Period label SET  p.event_type  = coalesce(p.event_type, "historical_crisis"),      p.granularity = "composite",     p.period_status = "retyped_to_event";`

You keep temporal edges (`STARTS_IN_YEAR`, `ENDS_IN_YEAR`) and any facet links; they’re still useful for events.

## 2.3 INSTITUTIONAL → convert to InstitutionalSpan

For Tier 3 entries:[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/56d011ad-0a9f-419d-a537-20e8142603dc/PERIOD_CLASSIFICATION_PLAN.md)]​

text

`// ensure constraint exists CREATE CONSTRAINT institutional_span_qid IF NOT EXISTS FOR (i:InstitutionalSpan) REQUIRE i.qid IS UNIQUE; MATCH (p:Period {qid: $qid}) SET p:InstitutionalSpan REMOVE p:Period SET  p.institution_type  = $institution_type,    // e.g., "court"      p.institution_name  = $institution_name,    // e.g., "US Supreme Court"     p.period_status     = "retyped_to_institutional";`

Again, keep Year and facet edges.

## 2.4 PROBLEMATIC → delete or park for review

For Tier 4 entries:[time_periods.csv+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cb359094-cf85-41fb-9ef5-e94df223b520/time_periods.csv)

text

`// Hard delete MATCH (p:Period {qid: $qid}) DETACH DELETE p;`

If you prefer a soft delete:

text

`MATCH (p:Period {qid: $qid}) SET p.period_status = "problematic",     p.deleted       = true;`

---

## Phase 3 — Sanity Checks and Derived Views

## 3.1 Verify Period cleanliness

Flag any remaining `:Period` nodes that look like events (too short):

text

`MATCH (p:Period)-[:STARTS_IN_YEAR]->(s:Year),       (p)-[:ENDS_IN_YEAR]->(e:Year) WITH p, e.year - s.year AS duration WHERE duration < 2    // or your threshold RETURN p.qid, p.label, duration ORDER BY duration ASC;`

## 3.2 Verify Event/InstitutionalSpan counts

text

`MATCH (p:Period) RETURN count(p) AS period_count; MATCH (e:Event) WHERE exists(e.period_status) RETURN count(e) AS retyped_events; MATCH (i:InstitutionalSpan) RETURN count(i) AS institutional_spans;`

## 3.3 Prepare for authority alignment

After the cleaning pass, you’ll have a stable set of canonical `:Period` nodes keyed by QID. These are the ones you’ll align to PeriodO and LCSH/SubjectConcepts using `periodo-dataset.csv` and the JSON mapping file.[periodo-dataset.csv+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/7bce58bb-f521-40e3-a9e8-690964d81d3c/periodo-dataset.csv)

---

If you want, next I can sketch the **authority alignment phase**:

- Reading `periodo-dataset.csv` to add `authority="PeriodO"` and `authority_uri` to matching Periods.
    
- Reading the LCSH mapping JSON to connect Periods to SubjectConcepts via `ALIGNED_WITH` / `ABOUT_PERIOD`.
- Two parts:

1. Authority alignment for periods
    
2. Archiving older docs
    

---

## 1) Authority alignment pipeline (PeriodO + LCSH/SubjectConcepts)

## 1.1 Align Periods to PeriodO (`periodo-dataset.csv`)

`periodo-dataset.csv` has columns like: `period,label,spatial_coverage,qid,start,stop,authority,source,...`.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/7bce58bb-f521-40e3-a9e8-690964d81d3c/periodo-dataset.csv)]​

Strategy:

- Use `qid` when present to match existing `:Period` nodes.
    
- Where `qid` is missing but label/date range are close to a `:Period`, you can later do fuzzy matching; for now, stick to exact QID matches.
    

Example Cypher (QID-based):

text

`// Add PeriodO authority metadata MATCH (p:Period {qid: $qid}) SET p.authority_periodo    = true,     p.periodo_uri          = $period_uri,    p.periodo_label        = $period_label,    p.periodo_authority    = $authority,      // e.g., "British Museum"    p.periodo_source       = $source,         // if present    p.periodo_start        = toString($start),    p.periodo_end          = toString($stop);`

You can also cross-check ranges:

- If PeriodO `start/stop` differs significantly from your `start/end`, tag for review (`p.periodo_conflict = true`).
    

## 1.2 Align Periods to SubjectConcepts (LCSH, etc.)

The current JSON (`period_lcsh_mapping_phase1_*.json`) is just an error log from an API attempt; it doesn’t yet contain successful matches.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/02d7a1f9-2fd7-426f-b625-9559ebacef78/period_lcsh_mapping_phase1_20260108_134151.json)]​

Design for the future mapping file (once you generate it):

json

`[   {    "qid": "Q201038",    "lcsh_id": "sh85115153",    "lcsh_heading": "Rome -- History -- Kings, 753-510 B.C.",    "confidence": 0.93  },  ... ]`

Then, ingestion would look like:

text

`// For each mapping MERGE (p:Period {qid: $qid}) MERGE (sc:SubjectConcept {authority_id: $lcsh_id, scheme: "LCSH"})   ON CREATE SET sc.heading = $lcsh_heading, sc.facet = "chronological" MERGE (p)-[:ALIGNED_WITH]->(sc) MERGE (sc)-[:ABOUT_PERIOD]->(p) SET p.lcsh_id     = $lcsh_id,     p.lcsh_conf   = $confidence;`

This ties:

- Periods → SubjectConcepts (chronological facet).
    
- Agents → Periods via SubjectConcept domain ownership.
    

---

