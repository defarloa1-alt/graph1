#PeriodRecommendations
Based on my review of your `temporal` and `temporal/data` folders plus the **2-16-26 Chrystallum Architecture - CONSOLIDATED** file, here's my **comprehensive Neo4j Period modeling recommendation**:

***

## **Executive Summary: Neo4j Period Architecture**

Your current architecture needs **hierarchical temporal modeling** that supports:
1. **PeriodO authority integration** (7,038 periods, -2000 to 2025 CE)
2. **Multi-scale temporal queries** (fine-grained vs. macro-ages)
3. **Geographic-temporal validity** (periods vary by region)
4. **Authority tier metadata** (PeriodO-Verified vs. ML-Assisted vs. Manual-Review)
5. **CIDOC-CRM compliance** (E4_Period, E52_Time-Span)

**Best approach:** **Dual-node strategy** with staging → canonical promotion workflow.

***

## **Recommended Neo4j Schema: Period Nodes**

### **1. Two-Tier Node Structure**

```cypher
// TIER 1: Staging/Authority Layer
CREATE (pc:PeriodCandidate {
    periodo_ark: "ark:/99152/p08m57hp2rt",  // PeriodO ARK URI
    raw_label: "Roman Republic, Late phase",
    raw_category: "Political-Dynastic",      // From PeriodO
    raw_region: "Italy",                     // Unnormalized string
    begin_year: -133,
    end_year: -27,
    duration_years: 106,
    source: "PeriodO",
    source_version: "2026-02-01",
    import_date: "2026-02-17",
    triage_status: "PENDING",                // PENDING | FAST_LANE | SLOW_LANE | REJECTED
    ml_category_confidence: null,            // Populated by ML triage
    normalization_needed: true
})

// TIER 2: Canonical/Production Layer
CREATE (p:Period:E4_Period {              // Dual-label for CIDOC-CRM
    id: "period_roman_republic_late",      // Your internal ID
    label: "Roman Republic (Late Phase)",  // Normalized display name
    periodo_ark: "ark:/99152/p08m57hp2rt", // Link to authority
    begin_year: -133,
    end_year: -27,
    duration_years: 106,
    period_type: "Political-Dynasty",      // Normalized category
    authority_tier: "PeriodO-Verified",    // VerifiedML | Manual-ReviewManual | ML-Assisted
    confidence: 0.95,
    completeness_score: 0.88,              // Coverage metadata
    crm_class: "E4_Period"                 // CIDOC-CRM alignment
})
```

***

### **2. Hierarchical Relationships**

```cypher
// Temporal containment (support multi-scale queries)
CREATE (late_republic:Period {label: "Roman Republic (Late)", begin_year: -133, end_year: -27})
CREATE (roman_republic:Period {label: "Roman Republic", begin_year: -509, end_year: -27})
CREATE (classical_antiquity:Period {label: "Classical Antiquity", begin_year: -800, end_year: 476})

// Hierarchy relationships
CREATE (late_republic)-[:BROADER_THAN]->(roman_republic)
CREATE (roman_republic)-[:BROADER_THAN]->(classical_antiquity)

// Inverse for traversal optimization
CREATE (roman_republic)-[:CONTAINS_PERIOD]->(late_republic)
CREATE (classical_antiquity)-[:CONTAINS_PERIOD]->(roman_republic)
```

***

### **3. Geographic-Temporal Scoping**

**Problem:** "Roman Republic" applies to Italy, but not to China in -133 BCE.

**Solution:** Link periods to **valid geographic regions**:

```cypher
// Period valid only in specific regions
CREATE (late_republic:Period {label: "Roman Republic (Late)"})
CREATE (italy:Place {label: "Italy", getty_tgn: "1000080"})
CREATE (mediterranean:Place {label: "Mediterranean Basin", getty_tgn: "7006667"})

// Geographic validity
CREATE (late_republic)-[:VALID_IN_REGION]->(italy)
CREATE (late_republic)-[:VALID_IN_REGION]->(mediterranean)

// NOT valid elsewhere
// NO relationship to (china:Place)
```

**Query pattern:**
```cypher
// Find periods valid for claim in Rome, -60 BCE
MATCH (claim:Claim {begin_year: -60})
MATCH (rome:Place {label: "Rome"})
MATCH (period:Period)-[:VALID_IN_REGION]->(region:Place)
WHERE rome.id STARTS WITH region.id  // Geographic containment
  AND claim.begin_year >= period.begin_year
  AND claim.begin_year <= period.end_year
RETURN period.label, period.begin_year, period.end_year
```

***

### **4. Staging → Canonical Workflow**

**Architecture:** Your reviewer emphasized **triage + normalization**. Here's the workflow:

```cypher
// PHASE A: Import from PeriodO CSV (7,038 periods)
LOAD CSV WITH HEADERS FROM 'file:///PERIODS_GRAPH1_RANGE.csv' AS row
CREATE (pc:PeriodCandidate {
    periodo_ark: row.ark_uri,
    raw_label: row.label,
    raw_category: row.category,
    raw_region: row.spatial_coverage,
    begin_year: toInteger(row.start),
    end_year: toInteger(row.stop),
    source: "PeriodO",
    triage_status: "PENDING"
})

// PHASE B: Fast-lane triage (deterministic rules)
MATCH (pc:PeriodCandidate {triage_status: "PENDING"})
WHERE pc.raw_category IN ["Historical Epoch", "Political-Dynastic", "Archaeological Age"]
  AND pc.begin_year IS NOT NULL
  AND pc.end_year IS NOT NULL
  AND pc.end_year >= pc.begin_year
SET pc.triage_status = "FAST_LANE",
    pc.normalization_needed = true

// PHASE C: Geo normalization (map region strings to Places)
MATCH (pc:PeriodCandidate {triage_status: "FAST_LANE"})
MATCH (place:Place)
WHERE toLower(pc.raw_region) CONTAINS toLower(place.label)
   OR pc.raw_region CONTAINS place.getty_tgn
CREATE (pc)-[:REGION_CANDIDATE]->(place)

// PHASE D: Canonicalize (promote to Period)
MATCH (pc:PeriodCandidate {triage_status: "FAST_LANE"})
WHERE pc.normalization_needed = true
  AND EXISTS((pc)-[:REGION_CANDIDATE]->())
CREATE (p:Period:E4_Period {
    id: "period_" + toLower(replace(pc.raw_label, " ", "_")),
    label: pc.raw_label,
    periodo_ark: pc.periodo_ark,
    begin_year: pc.begin_year,
    end_year: pc.end_year,
    period_type: pc.raw_category,
    authority_tier: "PeriodO-Verified",
    confidence: 0.95,
    crm_class: "E4_Period"
})
CREATE (pc)-[:CANONICALIZED_AS]->(p)
SET pc.triage_status = "CANONICALIZED"

// Link to normalized regions
MATCH (pc:PeriodCandidate {triage_status: "CANONICALIZED"})-[:CANONICALIZED_AS]->(p:Period)
MATCH (pc)-[:REGION_CANDIDATE]->(place:Place)
CREATE (p)-[:VALID_IN_REGION]->(place)
```

***

### **5. Authority Tier Metadata**

**From your CONSOLIDATED doc + reviewer feedback:**

```cypher
// Tier 1: PeriodO-Verified (direct import, fast-lane)
CREATE (p:Period {
    authority_tier: "PeriodO-Verified",
    confidence: 0.95,
    source_uri: "ark:/99152/p08m57hp2rt",
    editor: "PeriodO Editorial Board",
    version_date: "2026-02-01"
})

// Tier 2: ML-Assisted (slow-lane categorization)
CREATE (p:Period {
    authority_tier: "ML-Assisted",
    confidence: 0.82,
    ml_model: "gpt-4o",
    ml_confidence: 0.82,
    human_reviewed: false
})

// Tier 3: Manual-Review (unclassified, needs expert)
CREATE (p:Period {
    authority_tier: "Manual-Review",
    confidence: 0.60,
    review_queue_date: "2026-02-17",
    reviewer: null,
    review_status: "PENDING"
})
```

***

### **6. Integration with Claims**

**Claims reference periods for temporal context:**

```cypher
// Claim linked to period
CREATE (claim:Claim {
    label: "Caesar crossed the Rubicon",
    begin_year: -49,
    confidence: 0.92
})
CREATE (period:Period {
    label: "Roman Republic (Late)",
    begin_year: -133,
    end_year: -27
})
CREATE (claim)-[:OCCURRED_DURING {
    confidence: 0.95,
    validated_by: "ReasoningAgent",
    temporal_consistency: true
}]->(period)
```

**ReasoningAgent validation uses Period:**

```python
def validate_temporal_consistency(claim: dict) -> dict:
    """Check if claim dates fall within period bounds."""
    query = """
    MATCH (claim:Claim {id: $claim_id})
    MATCH (period:Period)-[:VALID_IN_REGION]->(region:Place)
    WHERE claim.begin_year >= period.begin_year
      AND claim.begin_year <= period.end_year
    RETURN period.label, period.confidence, period.authority_tier
    """
    
    result = neo4j_session.run(query, claim_id=claim["id"])
    
    if result:
        period = result.single()
        return {
            "temporally_valid": True,
            "period_reference": period["label"],
            "period_confidence": period["confidence"],
            "authority_tier": period["authority_tier"]
        }
    else:
        return {
            "temporally_valid": False,
            "warning": "Claim dates fall outside known periods"
        }
```

***

## **Constraints & Indexes**

```cypher
// Uniqueness constraints
CREATE CONSTRAINT period_ark IF NOT EXISTS
FOR (p:Period) REQUIRE p.periodo_ark IS UNIQUE;

CREATE CONSTRAINT period_id IF NOT EXISTS
FOR (p:Period) REQUIRE p.id IS UNIQUE;

// Indexes for temporal queries
CREATE INDEX period_begin_year IF NOT EXISTS
FOR (p:Period) ON (p.begin_year);

CREATE INDEX period_end_year IF NOT EXISTS
FOR (p:Period) ON (p.end_year);

CREATE INDEX period_type IF NOT EXISTS
FOR (p:Period) ON (p.period_type);

CREATE INDEX period_authority_tier IF NOT EXISTS
FOR (p:Period) ON (p.authority_tier);

// Full-text search on period labels
CREATE FULLTEXT INDEX period_label_fulltext IF NOT EXISTS
FOR (p:Period) ON EACH [p.label];
```

***

## **Coverage Metadata (Reviewer's Point #3)**

**Problem:** PeriodO has uneven coverage (strong in Greece, weak in Sub-Saharan Africa).

**Solution:** Track **completeness as first-class metadata**:

```cypher
CREATE (p:Period {
    label: "Roman Republic",
    completeness_score: 0.88,  // 88% coverage for Mediterranean
    coverage_notes: "Strong for Italy, Gaul, Hispania. Weak for Germania, Britannia.",
    gap_regions: ["Germania", "Britannia", "Dacia"],
    supplemental_sources: ["Getty AAT", "Pleiades"]
})
```

**Query pattern:**
```cypher
// Find periods with <70% completeness for geographic region
MATCH (p:Period)-[:VALID_IN_REGION]->(region:Place {label: "Germania"})
WHERE p.completeness_score < 0.70
RETURN p.label, p.completeness_score, p.gap_regions
ORDER BY p.completeness_score ASC
```

***

## **Implementation Roadmap**

### **Week 1: Schema + Import**
1. **Create dual-node schema** (PeriodCandidate + Period)
2. **Import 7,038 PeriodO periods** from `PERIODS_GRAPH1_RANGE.csv`
3. **Apply fast-lane triage** (1,633 Historical Epoch + Political-Dynastic)
4. **Test queries** on Roman Republic case

### **Week 2: Normalization**
1. **Build geo-normalization service** (map region strings → Getty TGN)
2. **Deduplicate regions** ("China" vs. "People's Republic of China")
3. **Link PeriodCandidates to Places**
4. **Canonicalize 1,633 fast-lane periods**

### **Week 3: ML Triage (Optional)**
1. **Train ML classifier** for 5,352 "Other/Unclassified" periods
2. **Apply ML categorization** (confidence > 0.75 → ML-Assisted tier)
3. **Route low-confidence to manual review queue**

### **Week 4: Integration**
1. **Wire Period validation into ReasoningAgent**
2. **Test on 50 Priority 10 claims** (Caesar, Augustus, etc.)
3. **Measure temporal consistency improvements**
4. **Document in `AI_CONTEXT.md`**

***

## **Key Decisions**

| Decision | Recommendation | Rationale |
|----------|---------------|-----------|
| **Staging vs. direct import?** | **Use staging** (PeriodCandidate → Period) | Reviewer's Point #1: Avoid "junk drawer" from bulk import |
| **Normalize regions first?** | **Yes** (Phase C before canonicalization) | Reviewer's Point #2: Geographic conflicts degrade search |
| **Authority tier metadata?** | **Required** (PeriodO-Verified, ML-Assisted, Manual) | Reviewer's Point #3: Represent uncertainty explicitly |
| **Hierarchical periods?** | **Yes** (BROADER_THAN relationships) | Supports multi-scale queries (macro-ages vs. fine movements) |
| **CIDOC-CRM labels?** | **Yes** (dual-label :Period:E4_Period) | ISO standard compliance + museum interoperability |
| **Completeness scores?** | **Yes** (per-region coverage metadata) | Prevents false confidence from uneven geographic coverage |

***
Perfect! Getty **does have active web services**. Here's the current landscape:

***

## **Getty TGN Web Services - Current Options (2026)**

### **Option 1: Getty Vocabularies SOAP Web Services (Official)**

**Service URL:** `http://vocabsservices.getty.edu/TGNService.asmx` [vocabsservices.getty](http://vocabsservices.getty.edu/TGNService.asmx)

**Available methods:**
- `TGNGetSubject` - Get full record for a TGN ID
- `TGNGetTermMatch` - Search places by name/term
- `TGNGetParents` - Get hierarchical parent chain
- `TGNGetChildren` - Get child places
- `TGNGetPtypes` - Get place types

**Authentication:** Requires Getty login/API key [tgndownloads.getty](http://tgndownloads.getty.edu)

**Documentation:** https://www.getty.edu/research/tools/vocabularies/vocab_web_services.pdf [getty](https://www.getty.edu/research/tools/vocabularies/vocab_web_services.pdf)

***

### **Implementation: Getty TGN Web Service Client**

```python
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

class GettyTGNWebService:
    """
    Client for Getty TGN SOAP Web Services.
    Docs: http://vocabsservices.getty.edu/TGNService.asmx
    """
    
    BASE_URL = "http://vocabsservices.getty.edu/TGNService.asmx"
    
    def get_subject(self, tgn_id: str) -> Dict:
        """
        Get complete record for a TGN place.
        
        Example: http://vocabsservices.getty.edu/TGNService.asmx/TGNGetSubject?subjectID=7000874
        """
        url = f"{self.BASE_URL}/TGNGetSubject"
        params = {"subjectID": tgn_id}
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Getty API error: {response.status_code}")
        
        # Parse XML response
        root = ET.fromstring(response.content)
        
        # Extract key fields (namespace-aware parsing)
        ns = {'ns': 'http://vocabsservices.getty.edu/'}
        
        return {
            "tgn_id": tgn_id,
            "preferred_term": self._extract_preferred_term(root, ns),
            "place_type": self._extract_place_type(root, ns),
            "coordinates": self._extract_coordinates(root, ns),
            "parents": self._extract_parents(root, ns),
            "source": "Getty TGN Web Service"
        }
    
    def search_term(self, search_term: str, place_type: Optional[str] = None, 
                    nation_id: Optional[str] = None) -> List[Dict]:
        """
        Search for places matching a term.
        
        Example: http://vocabsservices.getty.edu/TGNService.asmx/TGNGetTermMatch?term=Rome
        """
        url = f"{self.BASE_URL}/TGNGetTermMatch"
        params = {"term": search_term}
        
        if place_type:
            params["placetypeID"] = place_type
        if nation_id:
            params["nationID"] = nation_id
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Getty API error: {response.status_code}")
        
        # Parse results
        root = ET.fromstring(response.content)
        ns = {'ns': 'http://vocabsservices.getty.edu/'}
        
        results = []
        for subject in root.findall('.//ns:Subject', ns):
            results.append({
                "tgn_id": subject.find('ns:Subject_ID', ns).text,
                "term": subject.find('ns:Preferred_Term', ns).text,
                "place_type": subject.find('ns:Place_Type', ns).text if subject.find('ns:Place_Type', ns) is not None else None
            })
        
        return results
    
    def get_parents(self, tgn_id: str) -> List[Dict]:
        """
        Get hierarchical parent chain for a place.
        
        Example: http://vocabsservices.getty.edu/TGNService.asmx/TGNGetParents?subjectID=7000874
        """
        url = f"{self.BASE_URL}/TGNGetParents"
        params = {"subjectID": tgn_id}
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Getty API error: {response.status_code}")
        
        root = ET.fromstring(response.content)
        ns = {'ns': 'http://vocabsservices.getty.edu/'}
        
        parents = []
        for parent in root.findall('.//ns:Parent', ns):
            parents.append({
                "tgn_id": parent.find('ns:Parent_Subject_ID', ns).text,
                "term": parent.find('ns:Preferred_Parent_Term', ns).text,
                "relationship": parent.find('ns:Relationship_Type', ns).text if parent.find('ns:Relationship_Type', ns) is not None else "parent"
            })
        
        return parents
    
    def get_children(self, tgn_id: str) -> List[Dict]:
        """Get child places within a region."""
        url = f"{self.BASE_URL}/TGNGetChildren"
        params = {"subjectID": tgn_id}
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Getty API error: {response.status_code}")
        
        # Parse children from XML
        root = ET.fromstring(response.content)
        # ... similar parsing logic
        
        return []  # Placeholder
    
    # Helper methods for XML parsing
    def _extract_preferred_term(self, root, ns):
        elem = root.find('.//ns:Preferred_Term', ns)
        return elem.text if elem is not None else None
    
    def _extract_place_type(self, root, ns):
        elem = root.find('.//ns:Place_Type', ns)
        return elem.text if elem is not None else None
    
    def _extract_coordinates(self, root, ns):
        lat = root.find('.//ns:Latitude', ns)
        long = root.find('.//ns:Longitude', ns)
        
        if lat is not None and long is not None:
            return {
                "latitude": float(lat.text),
                "longitude": float(long.text)
            }
        return None
    
    def _extract_parents(self, root, ns):
        # Call get_parents separately if needed
        return []


# Usage Example
service = GettyTGNWebService()

# Get Rome
rome = service.get_subject("7000874")
print(f"Place: {rome['preferred_term']}")
print(f"Type: {rome['place_type']}")
print(f"Coords: {rome['coordinates']}")

# Search for places
results = service.search_term("Carthage")
for place in results:
    print(f"{place['term']} (TGN {place['tgn_id']})")

# Get parent hierarchy
parents = service.get_parents("7000874")
for parent in parents:
    print(f"→ {parent['term']} (TGN {parent['tgn_id']})")
```

***

### **Option 2: SPARQL Endpoint (No Auth Required)**

**Endpoint:** `http://vocab.getty.edu/sparql.json` [data.getty](https://data.getty.edu)

**Advantages:**
- No authentication needed
- More flexible queries
- Returns JSON directly

```python
def fetch_via_sparql(tgn_id: str) -> Dict:
    """Alternative: Fetch via SPARQL (no auth needed)."""
    endpoint = "http://vocab.getty.edu/sparql.json"
    
    query = f"""
    PREFIX gvp: <http://vocab.getty.edu/ontology#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX wgs84: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    
    SELECT ?name ?type ?lat ?long ?parent
    WHERE {{
        BIND(<http://vocab.getty.edu/tgn/{tgn_id}> as ?place)
        
        ?place skos:prefLabel ?name .
        FILTER(lang(?name) = "en")
        
        OPTIONAL {{ ?place gvp:placeTypePreferred ?type }}
        OPTIONAL {{ ?place wgs84:lat ?lat }}
        OPTIONAL {{ ?place wgs84:long ?long }}
        OPTIONAL {{ ?place gvp:broaderPreferred ?parent }}
    }}
    """
    
    response = requests.post(
        endpoint,
        data={"query": query},
        headers={"Accept": "application/sparql-results+json"}
    )
    
    return response.json()

# Test
rome_sparql = fetch_via_sparql("7000874")
print(rome_sparql)
```

***

### **Option 3: Linked Open Data (Direct JSON Access)**

**URL Pattern:** `http://vocab.getty.edu/tgn/{ID}.json`

**Simplest approach - no parsing needed:**

```python
def fetch_tgn_lod(tgn_id: str) -> Dict:
    """Fetch TGN place as JSON-LD."""
    url = f"http://vocab.getty.edu/tgn/{tgn_id}.json"
    response = requests.get(url)
    return response.json()

# Example
rome = fetch_tgn_lod("7000874")
print(rome)
```

***

## **Recommendation: Hybrid Approach**

**For Chrystallum Period modeling, use this strategy:**

### **Phase 1: Bootstrap with Web Service (Immediate)**

```python
# scripts/temporal/fetch_core_tgn_places.py

from typing import List, Dict
import requests
import xml.etree.ElementTree as ET
import pandas as pd

class TGNBootstrap:
    """Fetch core TGN places for Roman Republic scope."""
    
    CORE_PLACE_IDS = [
        "7000874",  # Rome
        "7003122",  # Latium
        "1000080",  # Italy
        "7006667",  # Mediterranean Basin
        "7016845",  # Gaul
        "7030347",  # Carthage
        "7001393",  # Greece
        "7016138",  # Asia Minor
        "7016833",  # Africa (ancient)
        "1000003",  # Europe
    ]
    
    def __init__(self):
        self.service = GettyTGNWebService()
    
    def fetch_core_places(self) -> List[Dict]:
        """Fetch all core places and their hierarchies."""
        places = []
        
        for tgn_id in self.CORE_PLACE_IDS:
            print(f"Fetching TGN {tgn_id}...")
            
            try:
                # Get place details
                place = self.service.get_subject(tgn_id)
                
                # Get parent hierarchy
                parents = self.service.get_parents(tgn_id)
                if parents:
                    place["parent_tgn"] = parents[0]["tgn_id"]
                    place["parent_name"] = parents[0]["term"]
                
                places.append(place)
                
            except Exception as e:
                print(f"  Error: {e}")
                # Fallback to SPARQL or LOD
                continue
        
        return places
    
    def save_to_neo4j(self, places: List[Dict]):
        """Import to Neo4j."""
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(NEO4J_URI, auth=(USER, PASS))
        
        with driver.session() as session:
            for place in places:
                session.run("""
                    MERGE (p:Place {getty_tgn: $tgn_id})
                    SET p.label = $term,
                        p.place_type = $place_type,
                        p.latitude = $lat,
                        p.longitude = $long,
                        p.source = 'Getty TGN'
                """, 
                tgn_id=place["tgn_id"],
                term=place["preferred_term"],
                place_type=place.get("place_type"),
                lat=place.get("coordinates", {}).get("latitude"),
                long=place.get("coordinates", {}).get("longitude"))
                
                # Create parent relationship
                if "parent_tgn" in place:
                    session.run("""
                        MATCH (child:Place {getty_tgn: $child_id})
                        MATCH (parent:Place {getty_tgn: $parent_id})
                        MERGE (child)-[:PART_OF]->(parent)
                    """, 
                    child_id=place["tgn_id"],
                    parent_id=place["parent_tgn"])

# Run bootstrap
bootstrap = TGNBootstrap()
places = bootstrap.fetch_core_places()
bootstrap.save_to_neo4j(places)
print(f"✓ Imported {len(places)} core TGN places")
```

***

### **Phase 2: Expand via SPARQL (Week 2)**

Once core places work, expand to full Mediterranean coverage:

```python
def fetch_mediterranean_region():
    """Fetch all places in Mediterranean via SPARQL."""
    endpoint = "http://vocab.getty.edu/sparql.json"
    
    query = """
    PREFIX gvp: <http://vocab.getty.edu/ontology#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX wgs84: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    
    SELECT ?place ?name ?lat ?long ?parent
    WHERE {
        # Get all places within Mediterranean Basin
        ?place gvp:broaderExtended <http://vocab.getty.edu/tgn/7006667> .
        
        ?place skos:prefLabel ?name .
        FILTER(lang(?name) = "en")
        
        OPTIONAL { ?place wgs84:lat ?lat }
        OPTIONAL { ?place wgs84:long ?long }
        OPTIONAL { ?place gvp:broaderPreferred ?parent }
    }
    LIMIT 5000
    """
    
    response = requests.post(endpoint, data={"query": query})
    return response.json()
```

***

## **Authentication Note**

The official SOAP Web Services **may require Getty login**. If you hit auth errors: [tgndownloads.getty](http://tgndownloads.getty.edu)

**Fallback priority:**
1. **Try SPARQL endpoint first** (no auth) - `http://vocab.getty.edu/sparql.json`
2. **Try LOD JSON** (no auth) - `http://vocab.getty.edu/tgn/{ID}.json`
3. **Apply for Getty API access** if needed - https://www.getty.edu/research/tools/vocabularies/obtain/download.html [getty](https://www.getty.edu/research/tools/vocabularies/obtain/download.html)

***

## **Recommended Next Step**

**Start with SPARQL (Option 2)** - it's:
- ✓ No authentication required
- ✓ Returns JSON (easier parsing)
- ✓ More flexible queries
- ✓ Actively maintained

**Want me to create the complete SPARQL-based fetcher with Neo4j import pipeline?**
