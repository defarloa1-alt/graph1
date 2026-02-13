# Chrystallum Implementation Roadmap: Phase 1 (Neo4j Bootstrap)

**Date:** 2026-02-13  
**Status:** Ready for Implementation  
**Target Completion:** 2026-02-20

---

## Overview

This guide provides a **step-by-step implementation path** for Phase 1: Neo4j Schema Bootstrap. After completing this phase, you will have:

✅ Neo4j database with production schema  
✅ Year backbone (temporal grid -2000 to 2025)  
✅ Foundational entities (Rome, Caesar, key periods, facets)  
✅ Ready-to-ingest FAST subject import pipeline  
✅ Test data for agent development

---

## Phase 1: Neo4j Schema Bootstrap (This Week)

### Step 1: Schema Definition & Deployment (1-2 hours)

**Files to execute:**
- `Neo4j/schema/01_schema_constraints.cypher` - Data integrity rules
- `Neo4j/schema/02_schema_indexes.cypher` - Query performance
- `Neo4j/schema/03_schema_initialization.cypher` - Bootstrap entities

**Commands:**
```bash
# Terminal in c:\Projects\Graph1

# Execute each script in order via cypher-shell or Neo4j Browser
cypher-shell -u neo4j -p <your_password> < Neo4j/schema/01_schema_constraints.cypher
cypher-shell -u neo4j -p <your_password> < Neo4j/schema/02_schema_indexes.cypher
cypher-shell -u neo4j -p <your_password> < Neo4j/schema/03_schema_initialization.cypher
```

**Verify:**
```cypher
-- In Neo4j Browser, run to confirm:
MATCH (n) RETURN labels(n)[0] AS label, count(*) AS count ORDER BY count DESC;

-- Expected output (~4,100 nodes):
-- Year: 4026
-- FacetCategory: 16
-- Place: 3
-- Period: 3
-- Human: 1
-- Organization: 1
-- Gens: 1
```

### Step 2: Test Data Ingestion - FAST Subjects (1-2 hours)

**Current state:** Sample import tested (50 subjects, 100% success)

**Execute full FAST import:**
```bash
cd c:\Projects\Graph1
python Python/fast/scripts/import_fast_subjects_to_neo4j.py \
  "Python/fast/key/FASTTopical_parsed.csv" \
  "Python/fast/output/fast_full_import.cypher"
```

**Parameters:**
- Input: Full FASTTopical extract (~100K subjects)
- Output: Cypher import script (~2-3MB)
- Time: ~5-10 minutes execution

**Import to Neo4j:**
```bash
cypher-shell -u neo4j -p <password> < Python/fast/output/fast_full_import.cypher
```

**Verify:**
```cypher
-- Check subject imports
MATCH (s:Subject {authority_tier: "TIER_3"})
RETURN count(*) AS lcsh_subjects,
       count(DISTINCT s.authority_tier) AS tier_count,
       avg(s.authority_confidence) AS avg_confidence;

-- Expected: 100k+ subjects, all TIER_3, confidence ~0.70
```

### Step 3: Schema Validation & Performance Testing (30 min)

**Query patterns to test:**

```cypher
-- 1. Year backbone integrity
MATCH (y:Year) RETURN count(*) AS total, min(y.year) AS min_year, max(y.year) AS max_year;

-- 2. Entity lookup performance (should be <1ms)
EXPLAIN MATCH (h:Human {qid: "Q1048"}) RETURN h;

-- 3. Temporal range query (should be <50ms)
EXPLAIN MATCH (e:Event)-[:STARTS_IN_YEAR]->(y:Year)
WHERE y.year >= -100 AND y.year <= 0
RETURN count(e);

-- 4. Facet filtering (should be <100ms)
EXPLAIN MATCH (s:Subject {facet_richness: 3})
RETURN count(*);

-- 5. Index usage verification
CALL db.indexes() YIELD name, state RETURN name, state LIMIT 10;
```

**Expected results:**
- All queries use indexes (state = "ONLINE")
- Lookup queries: <1ms
- Temporal range queries: <50ms
- Facet queries: <100ms

---

## Phase 2: Federation Integration & Data Enrichment (Next Week)

### Step 4: Wikidata Federation Supercharging (PRIORITY) (1-2 days)

**Strategic Insight:** A single Wikidata QID unlocks access to 50+ high-value external authorities.

**Authority Tiers:**
- **Golden Tier (Backbone):** LCSH (P244), FAST (P2163), LCC (P1149), Dewey (P1036)
- **Silver Tier (High-Value):** Getty TGN (P1667), Pleiades (P1584), Trismegistos (P1958), DARE (P1936), PeriodO (P9350), Nomisma (P1928), Perseus (P4046)
- **Bronze Tier (Global):** VIAF (P214), WorldCat Entities (P10832), GND (P227), ISNI (P213)

**Implementation:**

```python
# Python/neo4j/scripts/federation_supercharger.py

class FederationSupercharger:
    def fetch_federation_universe(self, qid):
        """
        Query Wikidata SPARQL for all external authority IDs
        Returns: authority_links = {
            "lcsh": "sh85018693",
            "viaf": "286248284",
            "pleiades": "392998632",
            "getty_tgn": "500077373",
            ...
        }
        """
        sparql = """
        SELECT ?lcsh ?fast ?lcc ?viaf ?gnd ?tgn ?pleiades ?trismegistos WHERE {
          BIND(wd:{qid} AS ?item) .
          OPTIONAL {{ ?item wdt:P244 ?lcsh . }}
          OPTIONAL {{ ?item wdt:P2163 ?fast . }}
          ... [11 more properties]
        }
        """
        return self.query_wikidata_sparql(sparql)
        
    def cache_federation_links(self, entity_id, authority_links):
        """
        Create authority_links supernode on entity
        Enable O(1) lookup for external systems
        """
        cypher = f"""
        MATCH (e:Entity {{entity_id: '{entity_id}'}})
        SET e.authority_links = {authority_links}
        SET e.federation_last_refreshed = datetime()
        """
        pass
        
    def create_federation_edges(self, qid, authority_links):
        """
        Create ALIGNED_WITH edges to external authorities
        Pattern: (:Entity)-[:ALIGNED_WITH {{source, property, confidence}}]->(:ExternalAuthority)
        """
        pass
```

**Expected Impact:**
- 50-80% of entities get enriched with 5-15 external authority IDs each
- Enable federated queries across VIAF/GND/Pleiades/Trismegistos
- Unlock historical place discovery via DARE (Roman geographic coordinates)
- Link to primary texts via Perseus/Trismegistos

### Step 4b: Reverse Relationship Enrichment (Backlink Engine) (~1 day)

**Strategic Insight:** "What links here?" (reverse relationships) provides concept expansion—discovering functional context, influences, participations, and cultural reception.

**The Problem it Solves:**
- Standard retrieval asks "Tell me about Caesar" → birth, death, wars (Known Knowns)
- Backlink retrieval asks "Who lists Caesar as participant/cause/influence?" → Julian Calendar, Caesarism, Shakespeare's Julius Caesar (Unknown Knowns)
- Creates "smarter agents" that discover enrichment without being explicitly prompted

**Implementation Pattern: Backlink Buckets**

```python
# Python/neo4j/scripts/federation_backlink_enricher.py

class BacklinkEnricher:
    def fetch_backlinks(self, qid):
        """
        Query Wikidata SPARQL for entities pointing TO this QID
        Bucket by property (P710, P1441, P737, etc.) + P31 (instance_of)
        """
        sparql = """
        SELECT ?source ?sourceLabel ?prop ?propLabel ?p31 ?p31Label WHERE {
          BIND(wd:{qid} AS ?target) .
          
          VALUES ?prop { 
            wdt:P710   # participant in (events, battles, expeditions)
            wdt:P1441  # present in work (cultural reception, depictions)
            wdt:P138   # named after (eponyms)
            wdt:P112   # founded by (legacy)
            wdt:P737   # influenced by (ideological impact)
            wdt:P828   # has cause (causation chains)
          }
          
          ?source ?prop ?target .
          ?source wdt:P31 ?p31 .  # What IS this source?
          
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }
        LIMIT 500
        """
        return self.query_wikidata_sparql(sparql)
    
    def bucket_enrichment(self, backlinks):
        """
        Organize backlinks into semantic buckets based on P31 + property
        
        Example: Caesar (Q1048)
        
        Bucket A: "The Participator"
          Source P31 = Event → PARTICIPATED_IN edges
          - Battle of Pharsalus
          - Siege of Alesia
          - Crossing of the Rubicon
          
        Bucket B: "The Influencer"
          Source P31 = Concept/Ideology → INFLUENCED edges
          - Caesarism (political ideology)
          
        Bucket C: "The Namesake"
          Source P31 = Calendar/Month → EPONYM_OF edges
          - Month of July
          - Julian Calendar
          
        Bucket D: "Cultural Icon"
          Source P31 = Work/Creative → DEPICTED_IN edges
          - Shakespeare's Julius Caesar
          - HBO's Rome
          - Dante's Inferno
        """
        buckets = {
            "participations": [],
            "influences": [],
            "eponyms": [],
            "depictions": [],
            "causations": [],
            "other": []
        }
        
        for link in backlinks:
            prop = link['property']
            p31 = link['p31']  # Instance of classification
            source = link['source']
            
            # Classify by property + P31
            if prop == "P710" and p31 in ["Event", "Battle", "Expedition"]:
                buckets["participations"].append(source)
            elif prop == "P737" and p31 in ["Concept", "Ideology"]:
                buckets["influences"].append(source)
            elif prop == "P138" and p31 in ["Month", "Calendar"]:
                buckets["eponyms"].append(source)
            elif prop == "P1441" and p31 in ["Work", "Film", "Book"]:
                buckets["depictions"].append(source)
            elif prop == "P828":
                buckets["causations"].append(source)
            else:
                buckets["other"].append(source)
        
        return buckets
    
    def materialize_enrichment(self, entity_id, buckets):
        """
        Create Chrystallum edges from backlink buckets
        Only materialize edges from whitelist
        """
        cypher_statements = []
        
        # PARTICIPATED_IN edges (high confidence)
        for event in buckets["participations"]:
            cypher_statements.append(f"""
            MATCH (entity:Entity {{entity_id: '{entity_id}'}})
            MATCH (evt:Event {{qid: '{event['qid']}'}})
            CREATE (entity)-[:PARTICIPATED_IN {{
              source: 'wikidata_backlink',
              property: 'P710',
              confidence: 0.95,
              retrieved_at: datetime()
            }}]->(evt)
            """)
        
        # INFLUENCED edges (high confidence)
        for concept in buckets["influences"]:
            cypher_statements.append(f"""
            MATCH (entity:Entity {{entity_id: '{entity_id}'}})
            MATCH (concept:Concept {{qid: '{concept['qid']}'}})
            CREATE (entity)-[:INFLUENCED {{
              source: 'wikidata_backlink',
              property: 'P737',
              confidence: 0.90,
              retrieved_at: datetime()
            }}]->(concept)
            """)
        
        # EPONYM_OF edges (medium-high confidence)
        for eponym in buckets["eponyms"]:
            cypher_statements.append(f"""
            MATCH (entity:Entity {{entity_id: '{entity_id}'}})
            MATCH (named_thing {{qid: '{eponym['qid']}'}})
            CREATE (entity)-[:EPONYM_OF {{
              source: 'wikidata_backlink',
              property: 'P138',
              confidence: 0.85,
              retrieved_at: datetime()
            }}]->(named_thing)
            """)
        
        # DEPICTED_IN edges (medium confidence - cultural reception)
        for work in buckets["depictions"]:
            cypher_statements.append(f"""
            MATCH (entity:Entity {{entity_id: '{entity_id}'}})
            MATCH (work:Work {{qid: '{work['qid']}'}})
            CREATE (entity)-[:DEPICTED_IN {{
              source: 'wikidata_backlink',
              property: 'P1441',
              confidence: 0.80,
              retrieved_at: datetime()
            }}]->(work)
            """)
        
        # Queue ambiguous/lower-confidence edges for agent review
        for other in buckets["other"]:
            cypher_statements.append(f"""
            MATCH (entity:Entity {{entity_id: '{entity_id}'}})
            CREATE (entity)-[:PENDING_REVIEW {{
              source: 'wikidata_backlink',
              property: '{other['property']}',
              confidence: 0.50,
              requires_agent_assessment: true,
              retrieved_at: datetime()
            }}]->({{qid: '{other['qid']}'}})
            """)
        
        return cypher_statements
    
    def store_provenance(self, entity_id, backlinks):
        """
        Store enrichment provenance on entity for audit trail
        """
        cypher = f"""
        MATCH (e:Entity {{entity_id: '{entity_id}'}})
        SET e.backlink_enrichment_count = {len(backlinks)}
        SET e.backlink_enrichment_retrieved_at = datetime()
        SET e.backlink_enrichment_sources = ['wikidata']
        """
        return cypher
```

**Backlink Property Whitelist** (corrected):

| Property | Meaning | Bucket | Edge Type | Confidence |
|----------|---------|--------|-----------|------------|
| P710 | Participant in | Participations | PARTICIPATED_IN | 0.95 |
| P1441 | Present in work | Cultural Reception | DEPICTED_IN | 0.80 |
| P138 | Named after | Eponyms | EPONYM_OF | 0.85 |
| P112 | Founded by | Legacy | FOUNDED | 0.90 |
| P737 | Influenced by | Influences | INFLUENCED | 0.90 |
| P828 | Has cause | Causation | HAS_CAUSE | 0.75 |

**Expected Impact:**
- Discover functional context without explicit prompting (participations, influences, cultural reception)
- Add 50-500 new relationship edges per high-profile entity
- Enable "Reception History" subgraph (depictions in works)
- Unlock causation chains (what this entity caused)
- Solve the "Unknown Unknowns" problem by reverse inference

### Step 3: Poly-Temporal Facet Population (1-2 days)

**Strategic Insight:** Time is contested. A single event exists simultaneously in multiple temporal frames.

**Problem:** Forcing events into one timeline loses context. Solution: Anchor events in multiple `OCCURRED_DURING` edges, each labeled with a facet showing which authority system (Historiographical, Scientific, Religious, Economic, PeriodO, Fuzzy) applies.

**Authority Facets:**
- **Historiographical:** Dynastic, Cultural, Political, Technological, Crisis
- **Scientific:** Geologic (GTS), Astronomical, Climatological, Evolutionary
- **Religious:** Soteriological (AD/CE), Islamic (AH), Hindu (Kali Yuga), Liturgical (Advent, Ramadan)
- **Economic:** Fiscal quarters, budget cycles, legal terms
- **PeriodO:** Academic consensus periods with geographic scope
- **Fuzzy:** User queries ("ancient times", "Boomers", "recently")

**Implementation:**

```python
# Python/neo4j/scripts/temporal_facet_populator.py

class TemporalFacetPopulator:
    def populate_event_temporal_facets(self, event_id):
        """
        Query PeriodO for all periods containing event's date
        Create OCCURRED_DURING edges for each applicable facet
        """
        cypher_statements = []
        
        # Query: Get event's ISO date
        event_date = query_neo4j(f"MATCH (e:Event {{event_id: '{event_id}'}}) RETURN e.iso_date")
        
        # Query: Fetch all PeriodO periods for this date
        periodos_results = self.query_periodo_by_date(event_date)
        
        for periodo in periodos_results:
            # Step 1: Classify by facet (Historiographical, Scientific, Religious, etc.)
            facet = self.classify_facet(periodo)
            
            # Step 2: Calculate confidence based on facet type
            confidence = self.calculate_confidence(facet, periodo)
            
            # Step 3: Create OCCURRED_DURING edge
            cypher = f"""
            MATCH (event:Event {{entity_id: '{event_id}'}})
            MATCH (period:Period {{period_o_id: '{periodo['id']}'}})
            CREATE (event)-[:OCCURRED_DURING {{
              facet: '{facet}',
              period_label: '{periodo['label']}',
              period_o_id: '{periodo['id']}',
              start_date: '{periodo['start']}',
              end_date: '{periodo['end']}',
              geographic_scope: {periodo.get('geographic_scope', [])},
              authority_tier: 'TIER_2',
              confidence: {confidence},
              source: 'PeriodO',
              certainty: 'definite'
            }})->(period)
            """
            cypher_statements.append(cypher)
        
        return cypher_statements
    
    def classify_facet(self, periodo_record):
        """Classify PeriodO period into one of 6 facet types"""
        if periodo_record.get('gts_rank'):
            return "Scientific"
        if 'dynasty' in periodo_record.get('keywords', '').lower():
            return "Historiographical"
        if periodo_record.get('calendar_system'):
            return "Religious"
        if 'fiscal' in periodo_record.get('keywords', '').lower():
            return "Economic"
        return "Historiographical"
    
    def calculate_confidence(self, facet, periodo):
        """Confidence varies by facet (Geologic=0.95, Fuzzy=0.50)"""
        facet_confidence = {
            "Scientific": 0.95,
            "Historiographical": 0.80,
            "Religious": 0.75,
            "Economic": 0.85,
            "PeriodO": 0.90,
            "Fuzzy": 0.50
        }
        return facet_confidence.get(facet, 0.70)
    
    def query_periodo_by_date(self, iso_date):
        """Query PeriodO gazetteer for periods containing this date"""
        # Implementation: SPARQL query to PeriodO API or local mirror
        pass
```

**Example Result (Eruption of Vesuvius 79 AD):**

```cypher
(Event:VesuviusEruption)
  -[:OCCURRED_DURING {facet: "Dynastic", period: "Flavian Dynasty", confidence: 0.85}]->(:Period)
  -[:OCCURRED_DURING {facet: "Political", period: "Roman Empire", confidence: 0.90}]->(:Period)
  -[:OCCURRED_DURING {facet: "Scientific", period: "Holocene Epoch", confidence: 0.99}]->(:Period)
  -[:OCCURRED_DURING {facet: "Cultural", period: "Classical Antiquity", confidence: 0.85}]->(:Period)
```

**Query Pattern: \"According to whom?\"**

```cypher
MATCH (event:Event {label: "Eruption of Vesuvius"})
-[rel:OCCURRED_DURING]->(period:Period)
RETURN period.label, rel.facet, rel.confidence
ORDER BY rel.confidence DESC
// Results: Shows all temporal framings (Dynastic, Scientific, Cultural, etc.)
```

**Expected Impact:**
- 80%+ of events have 3-6 temporal facet anchors
- 70%+ linked to PeriodO authority
- Geographic time variation supported (Late Bronze Age: Greece ≠ Scandinavia)
- Fuzzy temporal queries resolve with confidence ≥0.50

For detailed implementation strategy, see: [Neo4j/TEMPORAL_FACET_STRATEGY.md](TEMPORAL_FACET_STRATEGY.md)

### Step 5: Events & Works Import (1-2 days)

**Source files:** `Events/`, `Nodes/`

**Create import pipeline:**
```python
# Python/neo4j/scripts/import_events.py
# (New file - similar pattern to FAST importer)

class EventImporter:
    def parse_events(self, csv_file):
        # Read Events/ directory
        # Extract: event_id, label, start_date, end_date, event_type
        # Generate Cypher CREATE statements
        
    def link_to_temporal_backbone(self, cypher_statements):
        # Ensure all events have STARTS_IN_YEAR/ENDS_IN_YEAR
        pass
        
    def export_cypher(self, output_file):
        # Write bulk import Cypher
        pass
```

### Step 5: Events & Works Import (1-2 days)

**Source files:** `Events/`, `Nodes/`

**Create import pipeline:**
```python
# Python/neo4j/scripts/import_events.py
# (New file - similar pattern to FAST importer)

class EventImporter:
    def parse_events(self, csv_file):
        # Read Events/ directory
        # Extract: event_id, label, start_date, end_date, event_type
        # Generate Cypher CREATE statements
        
    def link_to_temporal_backbone(self, cypher_statements):
        # Ensure all events have STARTS_IN_YEAR/ENDS_IN_YEAR
        pass
        
    def export_cypher(self, output_file):
        # Write bulk import Cypher
        pass
```

**Expected output:**
- Events: 5,000-10,000 nodes
- Works: 1,000-2,000 nodes
- All linked to Year backbone

### Step 6: Authority Conflict Resolution (1 day)

**When Wikidata/LCSH/FAST disagree:** Implement conflict detection & resolution policy.

```cypher
-- Pattern: Detect conflicting authority claims
MATCH (e:Entity {qid: "Q1048"})-[:ALIGNED_WITH {source: "lcsh"}]->(a1:ExternalAuthority),
      (e)-[:ALIGNED_WITH {source: "viaf"}]->(a2:ExternalAuthority)
WHERE a1.external_id <> a2.external_id
CREATE (e)-[:CONFLICTS_WITH {sources: ["lcsh", "viaf"], resolution_rule: "pending"}]->(conflict_node)
```

**Resolution Rules:**
1. **Golden Tier Priority:** LCSH/FAST opinion overrides derived sources
2. **Recency Priority:** Wikidata updatemight supersede cached authority
3. **Evidence Priority:** Multiple sources agreement increases confidence
4. **Manual Adjudication:** Flag high-importance conflicts for expert review

---

## Phase 3: Agent & Claims Layer (Week 3)

### Step 7: Multi-Agent Evaluation Setup

**Deploy facet-specialist agents** (based on Section 5 architecture):

```python
# Python/agents/chrystallum_agents.py

from langchain_community.graphs import Neo4jGraph
from langgraph.graph import StateGraph

class ChrystallumCoordinator:
    def __init__(self):
        self.agents = {
            "political": PoliticalAgent(),
            "military": MilitaryAgent(),
            "economic": EconomicAgent(),
            # ... 13 more facets
        }
        
    def evaluate_claim(self, claim_id):
        """
        Route claim to all 16 facet agents
        Collect FacetAssessment nodes
        Synthesize overall_confidence
        """
        pass
```

---

## Configuration Files

### Neo4j Configuration (neo4j.conf)

Add to your Neo4j installation's `neo4j.conf`:

```properties
# Memory settings (adjust to your system)
dbms.memory.heap.initial_size=2G
dbms.memory.heap.max_size=4G

# Transaction settings
dbms.transaction.timeout=60s

# APOC plugin (optional for batch operations)
dbms.security.procedures.allowlist=apoc.* 

# Performance tuning
dbms.index_sampling.sample_size=10000
dbms.cypher.statistics_divergence_threshold=0.5
```

### Python Environment (requirements.txt)

```
neo4j==5.15.0
langchain==0.1.0
langgraph==0.0.1
requests==2.31.0
pandas==2.1.0
```

---

## Timeline & Checkpoints

| Phase | Task | Duration | Target Date | Status |
|-------|------|----------|-------------|--------|
| 1 | Schema Bootstrap | 2 hours | 2026-02-13 | ✅ Ready |
| 1 | FAST Import (full) | 2 hours | 2026-02-13 | ⏳ Queued |
| 1 | Schema Validation | 30 min | 2026-02-13 | ⏳ Queued |
| 2 | Federation Supercharging | 1-2 days | 2026-02-14-15 | ⏳ Planned |
| 2 | Events/Works Import | 1-2 days | 2026-02-15-16 | ⏳ Planned |
| 2 | Authority Conflict Resolution | 1 day | 2026-02-17 | ⏳ Planned |
| 3 | Claims Layer Initialization | 1 day | 2026-02-18 | ⏳ Planned |
| 3 | Agent Deployment | 1-2 days | 2026-02-19-20 | ⏳ Planned |
| **Total** | **Implementation Phase** | **~1 week** | **2026-02-20** | |

---

## Success Criteria

**Phase 1 Complete When:**
- [ ] Neo4j database initialized with all constraints & indexes
- [ ] Year backbone confirmed (4,026 nodes linked sequentially)
- [ ] 100K+ FAST subjects imported with TIER_3 classification
- [ ] All queries return in <100ms
- [ ] Foundational entities (Caesar, Rome, Senate) linked correctly
- [ ] Schema documentation complete

**Phase 2 Complete When:**
- [ ] 5K-10K events imported and linked to Year backbone
- [ ] 1K-2K works imported with author/publication data
- [ ] Federation universe resolved for 80%+ of entities (50+ authority properties cached per entity)
- [ ] Multi-hop authority chains established (QID → VIAF/GND/Pleiades/Trismegistos/DARE/etc.)
- [ ] Conflict detection & resolution rules deployed
- [ ] 30-50% of subjects upgraded to TIER_2 via federation enrichment

**Phase 3 Complete When:**
- [ ] 100+ test claims created in Neo4j
- [ ] All 16 facet-specialist agents deployed
- [ ] Coordinator successfully routes claims to agents
- [ ] FacetAssessment nodes generated and stored
- [ ] Overall confidence scoring functional


---

## Key Files & Locations

```
c:\Projects\Graph1\
├── Neo4j/schema/
│   ├── 01_schema_constraints.cypher        [Constraints & uniqueness]
│   ├── 02_schema_indexes.cypher            [Performance indexes]
│   ├── 03_schema_initialization.cypher     [Bootstrap + Year backbone]
│   └── SCHEMA_BOOTSTRAP_GUIDE.md           [This is the guide]
├── Python/fast/
│   ├── scripts/import_fast_subjects_to_neo4j.py  [FAST → Cypher converter]
│   ├── output/subjects_import_sample.cypher      [Sample output]
│   └── IMPORT_GUIDE.md                           [Usage docs]
├── Python/neo4j/scripts/
│   ├── (TBD) import_events.py
│   ├── (TBD) import_works.py
│   ├── (TBD) enhance_wikidata_linkage.py
│   └── (TBD) claims_initialization.py
└── Key Files/
    └── 2-12-26 Chrystallum Architecture - CONSOLIDATED.md  [Reference]
```

---

## Next Immediate Action

**🟢 Start Here (Next 30 minutes):**

1. Open Neo4j Browser or cypher-shell
2. Run: `Neo4j/schema/01_schema_constraints.cypher`
3. Run: `Neo4j/schema/02_schema_indexes.cypher`
4. Run: `Neo4j/schema/03_schema_initialization.cypher`
5. Verify with query: `MATCH (n) RETURN labels(n)[0] AS label, count(*) AS count ORDER BY count DESC`

**Expected output:**
```
Year:            4026
FacetCategory:   16
Place:           3
Period:          3
Human:           1
Organization:    1
Gens:            1
```

If all counts match → Schema Bootstrap ✅ Complete!

---

## Support & Troubleshooting

**Issue: Neo4j connection refused**
- Check: `neo4j status` (Windows Services or Docker)
- Solution: Start Neo4j service or container

**Issue: Constraint creation fails**
- Cause: Schema already exists
- Solution: Delete database and restart, or skip to Step 2

**Issue: Import takes >5 hours**
- Cause: Insufficient memory or slow disk I/O
- Solution: Increase `dbms.memory.heap.max_size` in neo4j.conf

**Issue: Index creation timeout**
- Cause: Background reindexing
- Solution: Wait 5-10 minutes and retry, or monitor `/var/log/neo4j.log`

---

## References

- **Main Architecture:** Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md
- **Entity Layer Spec:** Section 3
- **Temporal Design:** Section 3.4
- **Technology Stack:** Section 8 (Neo4j + LangGraph)
- **FAST Import:** Python/fast/IMPORT_GUIDE.md

---

**Ready to begin?** → Follow the "Next Immediate Action" section above!

