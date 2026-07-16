# **PART IV: OPERATIONAL GOVERNANCE**

---

# **10. Quality Assurance & Validation**

## **10.0 Quality Assurance Overview**

Quality assurance in Chrystallum operates at multiple levels:
1. **Schema Validation**: Ensure all nodes/edges conform to type schemas
2. **Confidence Scoring**: Systematic evaluation of claim reliability
3. **Source Tier Assessment**: Classify sources by scholarly authority
4. **Agent Calibration**: Monitor and adjust agent performance over time

---

## **10.1 Schema Validation Rules**

### **10.1.1 Required Property Validation**

**Enforcement:** Reject writes that violate required property constraints

```cypher
// Constraint: Every Entity must have entity_id, label, qid, entity_type
CREATE CONSTRAINT entity_required_properties IF NOT EXISTS
FOR (e:Entity)
REQUIRE e.entity_id IS NOT NULL
  AND e.label IS NOT NULL
  AND e.qid IS NOT NULL
  AND e.entity_type IS NOT NULL;
```

**Python Validation:**
```python
from pydantic import BaseModel, Field

class EntitySchema(BaseModel):
    """Validation schema for Entity nodes."""
    entity_id: str = Field(..., description="Internal unique identifier")
    label: str = Field(..., description="Primary name/label")
    qid: str = Field(..., pattern=r"^Q\\d+$", description="Wikidata QID")
    entity_type: str = Field(..., description="Entity type classification")
    
    # Optional properties
    fast_id: Optional[str] = None
    lcc_code: Optional[str] = None
    
    def validate_before_write(self):
        """Additional validation before Neo4j write."""
        # Check QID format
        if not self.qid.startswith("Q"):
            raise ValueError(f"Invalid QID format: {self.qid}")
        
        # Check entity_type is in allowed list
        allowed_types = ["Human", "Place", "Event", "Period", "Organization"]
        if self.entity_type not in allowed_types:
            raise ValueError(f"Invalid entity_type: {self.entity_type}")
```

---

### **10.1.2 Relationship Type Validation**

**Validation:** Ensure all relationships use canonical types from registry

```python
def validate_relationship_type(rel_type: str) -> bool:
    """Check if relationship type is in canonical registry."""
    canonical_types = load_canonical_relationship_types()  # From CSV
    return rel_type in canonical_types

def create_relationship_with_validation(from_id: str, to_id: str, rel_type: str, properties: Dict):
    """Create relationship with type validation."""
    if not validate_relationship_type(rel_type):
        raise ValueError(f"Invalid relationship type: {rel_type}. Not in canonical registry.")
    
    # Proceed with creation
    neo4j_writer.create_relationship(from_id, to_id, rel_type, properties)
```

---

## **10.2 Confidence Scoring Methodology**

### **10.2.1 Source Tier Definitions**

Chrystallum classifies sources by scholarly authority:

| Tier | Description | Confidence Range | Examples |
|------|-------------|------------------|----------|
| **Primary** | Original historical sources | 0.90 - 1.00 | Ancient texts, inscriptions, archaeological evidence |
| **Secondary (Academic)** | Peer-reviewed scholarship | 0.80 - 0.90 | Journal articles, university press monographs |
| **Secondary (Trade)** | Non-peer-reviewed but reputable | 0.70 - 0.80 | Popular history by credentialed authors |
| **Tertiary** | Reference works | 0.60 - 0.70 | Encyclopedias, dictionaries |
| **Uncertain** | Unverified or contested | < 0.60 | Wikipedia (pre-verification), forums, blogs |

**Implementation:**
```python
def assign_source_tier(source_work_qid: str) -> Dict:
    """Assign confidence tier based on source classification."""
    work_data = wikidata_api.get_entity(source_work_qid)
    
    # Check work type
    instance_of = work_data.get("claims", {}).get("P31", [])  # P31 = instance of
    
    if "Q5633421" in instance_of:  # Scientific journal article
        return {"tier": "Secondary (Academic)", "base_confidence": 0.85}
    elif "Q571" in instance_of:  # Book
        # Check publisher for university press
        publisher = work_data.get("claims", {}).get("P123", [])
        if is_university_press(publisher):
            return {"tier": "Secondary (Academic)", "base_confidence": 0.85}
        else:
            return {"tier": "Secondary (Trade)", "base_confidence": 0.75}
    elif "Q8242" in instance_of:  # Ancient text
        return {"tier": "Primary", "base_confidence": 0.95}
    else:
        return {"tier": "Uncertain", "base_confidence": 0.50}
```

---

### **10.2.2 Confidence Adjustment Factors**

Base confidence can be adjusted based on additional factors:

| Factor | Adjustment | Rationale |
|--------|------------|-----------|
| **Multiple attestations** | +0.05 per additional source (max +0.15) | Corroboration increases confidence |
| **Agent consensus** | +0.10 if â‰¥80% agent agreement | Multi-agent validation |
| **Temporal proximity** | +0.05 if contemporary source | Closer to events = more reliable |
| **Conflict detected** | -0.15 | Conflicting claims reduce confidence |
| **Agent expertise** | Â±0.05 | Specialist agents weight higher |

```python
def calculate_adjusted_confidence(base_confidence: float, factors: Dict) -> float:
    """Adjust base confidence score based on additional factors."""
    adjusted = base_confidence
    
    # Multiple attestations
    attestation_count = factors.get("attestation_count", 1)
    adjusted += min(0.15, (attestation_count - 1) * 0.05)
    
    # Agent consensus
    if factors.get("agent_consensus", 0) >= 0.8:
        adjusted += 0.10
    
    # Temporal proximity
    if factors.get("contemporary_source", False):
        adjusted += 0.05
    
    # Conflicts
    if factors.get("conflict_detected", False):
        adjusted -= 0.15
    
    # Agent expertise
    adjusted += factors.get("agent_expertise_adjustment", 0)
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, adjusted))
```

---

## **10.3 Agent Calibration Procedures**

### **10.3.1 Performance Metrics**

Track agent performance across multiple dimensions:

```python
class AgentPerformanceMetrics:
    """Track agent performance over time."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.metrics = {
            "claims_generated": 0,
            "claims_validated": 0,
            "claims_rejected": 0,
            "avg_confidence": 0.0,
            "avg_consensus_score": 0.0,
            "hallucination_rate": 0.0,  # Invalid entity extractions
            "accuracy_rate": 0.0         # Correct entity resolutions
        }
    
    def update_metrics(self, claim_result: Dict):
        """Update metrics after claim processing."""
        self.metrics["claims_generated"] += 1
        
        if claim_result["status"] == "validated":
            self.metrics["claims_validated"] += 1
        elif claim_result["status"] == "rejected":
            self.metrics["claims_rejected"] += 1
        
        # Update averages
        self.metrics["avg_consensus_score"] = (
            (self.metrics["avg_consensus_score"] * (self.metrics["claims_generated"] - 1) 
             + claim_result["consensus_score"]) 
            / self.metrics["claims_generated"]
        )
    
    def get_calibration_adjustment(self) -> float:
        """Calculate agent weight adjustment based on performance."""
        # High-performing agents get higher weight
        performance_score = (
            self.metrics["accuracy_rate"] * 0.4 +
            self.metrics["avg_consensus_score"] * 0.3 +
            (1 - self.metrics["hallucination_rate"]) * 0.3
        )
        
        # Weight adjustment: Â±20% based on performance
        adjustment = (performance_score - 0.5) * 0.4
        return 1.0 + adjustment  # Range: [0.8, 1.2]
```

---

### **10.3.2 Automatic Recalibration**

```python
def recalibrate_agent(agent_id: str):
    """Recalibrate agent based on recent performance."""
    metrics = AgentPerformanceMetrics(agent_id)
    metrics.load_recent_history(days=30)  # Last 30 days
    
    new_weight = metrics.get_calibration_adjustment()
    
    # Update agent configuration
    neo4j_writer.update_agent(agent_id, {
        "weight": new_weight,
        "calibration_date": datetime.now().isoformat(),
        "performance_score": metrics.metrics["accuracy_rate"]
    })
    
    # Alert if performance degraded significantly
    if new_weight < 0.9:
        log.warning(f"Agent {agent_id} performance degraded. New weight: {new_weight:.2f}")
        send_alert(f"Agent {agent_id} requires review")
```

---

## **10.4 Validation Query Patterns**

### **10.4.1 Data Integrity Checks**

```cypher
// Check for orphaned claims (no source work)
MATCH (c:Claim)
WHERE NOT EXISTS((c)-[:EXTRACTED_FROM]->(:Work))
RETURN c.claim_id, c.text, c.timestamp
ORDER BY c.timestamp DESC
LIMIT 100;

// Check for entities missing required properties
MATCH (e:Entity)
WHERE e.qid IS NULL OR e.label IS NULL
RETURN e.entity_id, e.entity_type, labels(e)
LIMIT 100;

// Check for duplicate QIDs
MATCH (e:Entity)
WITH e.qid AS qid, collect(e) AS entities
WHERE size(entities) > 1
RETURN qid, [e IN entities | e.entity_id] AS duplicate_ids;

// Check for claims without reviews
MATCH (c:Claim {status: "proposed"})
WHERE NOT EXISTS((c)<-[:REVIEWS]-(:Review))
  AND datetime(c.timestamp) < datetime() - duration({days: 7})
RETURN c.claim_id, c.text, c.timestamp
ORDER BY c.timestamp
LIMIT 50;
```

---

### **10.4.2 Performance Monitoring Queries**

```cypher
// Agent productivity (claims per agent)
MATCH (a:Agent)-[:MADE_CLAIM]->(c:Claim)
WITH a.agent_id AS agent, 
     count(c) AS claims_total,
     sum(CASE WHEN c.status = "validated" THEN 1 ELSE 0 END) AS claims_validated
RETURN agent, claims_total, claims_validated,
       round(claims_validated * 100.0 / claims_total, 1) AS validation_rate_pct
ORDER BY validation_rate_pct DESC;

// Consensus distribution
MATCH (c:Claim)
WHERE c.consensus_score IS NOT NULL
RETURN 
  count(CASE WHEN c.consensus_score >= 0.8 THEN 1 END) AS high_confidence,
  count(CASE WHEN c.consensus_score >= 0.5 AND c.consensus_score < 0.8 THEN 1 END) AS medium_confidence,
  count(CASE WHEN c.consensus_score < 0.5 THEN 1 END) AS low_confidence;

// Average review time
MATCH (c:Claim)-[:REVIEWS]-(r:Review)
WITH c, collect(r) AS reviews
WHERE size(reviews) >= 3
WITH c.timestamp AS claim_time,
     max([r IN reviews | datetime(r.timestamp)]) AS last_review_time
RETURN avg(duration.between(datetime(claim_time), last_review_time).days) AS avg_review_days;
```

---

# **11. Graph Governance & Maintenance**

## **11.0 Governance Overview**

Graph governance ensures long-term system health through:
1. **Schema Versioning**: Track schema changes over time
2. **Neo4j Indexing Strategy**: Optimize query performance
3. **Backup & Recovery**: Protect against data loss
4. **Monitoring & Alerts**: Detect issues proactively

---

## **11.1 Schema Versioning Strategy**

### **11.1.1 Version Metadata**

Track schema versions in dedicated nodes:

```cypher
CREATE (schema:SchemaVersion {
  version: "3.2",
  release_date: "2026-02-12",
  description: "Added identifier safety validation, expanded relationship types",
  breaking_changes: ["Claim cipher generation algorithm updated"],
  migration_required: false
});
```

---

### **11.1.2 Migration Patterns**

When schema changes require data migration:

```cypher
// Example: Add new required property to existing nodes
MATCH (e:Entity)
WHERE e.backbone_marc IS NULL
SET e.backbone_marc = ""  // Default empty string
SET e.schema_version = "3.2",
    e.migration_date = datetime();

// Track migration completion
CREATE (m:Migration {
  migration_id: "add_backbone_marc_2026_02_12",
  start_time: datetime(),
  end_time: datetime(),
  nodes_affected: count(e),
  status: "completed"
});
```

---

## **11.2 Neo4j Indexing Strategy**

### **11.2.1 Required Indexes**

```cypher
// Core entity lookups
CREATE INDEX entity_id_index IF NOT EXISTS FOR (e:Entity) ON (e.entity_id);
CREATE INDEX qid_index IF NOT EXISTS FOR (e:Entity) ON (e.qid);
CREATE INDEX fast_id_index IF NOT EXISTS FOR (s:SubjectConcept) ON (s.fast_id);

// Temporal indexes
CREATE INDEX year_index IF NOT EXISTS FOR (y:Year) ON (y.year);
CREATE INDEX event_start_date_index IF NOT EXISTS FOR (e:Event) ON (e.start_date);

// Claims workflow
CREATE INDEX claim_status_index IF NOT EXISTS FOR (c:Claim) ON (c.status);
CREATE INDEX claim_cipher_index IF NOT EXISTS FOR (c:Claim) ON (c.cipher);

// Full-text search
CREATE FULLTEXT INDEX entity_search IF NOT EXISTS
FOR (e:Entity) ON EACH [e.label, e.name];

CREATE FULLTEXT INDEX claim_text_search IF NOT EXISTS
FOR (c:Claim) ON EACH [c.text, c.passage_text];
```

---

### **11.2.2 Composite Indexes**

For common multi-property queries:

```cypher
// Agent + status lookup
CREATE INDEX agent_claim_status IF NOT EXISTS
FOR (c:Claim) ON (c.source_agent_id, c.status);

// Date range queries
CREATE INDEX period_date_range IF NOT EXISTS
FOR (p:Period) ON (p.start_date, p.end_date);

// Action structure queries
CREATE INDEX action_structure_index IF NOT EXISTS
FOR ()-[r:RELATIONSHIP]-() ON (r.goal_type, r.action_type);
```

---

## **11.3 Backup & Recovery Procedures**

### **11.3.1 Backup Strategy**

```bash
# Daily incremental backups
neo4j-admin backup \\
  --from=localhost:6362 \\
  --backup-dir=/backups/incremental \\
  --name=chrystallum_$(date +%Y%m%d)

# Weekly full backups
neo4j-admin backup \\
  --from=localhost:6362 \\
  --backup-dir=/backups/full \\
  --name=chrystallum_full_$(date +%Y%m%d) \\
  --fallback-to-full=true
```

---

### **11.3.2 Recovery Procedures**

```bash
# Restore from backup
neo4j-admin restore \\
  --from=/backups/full/chrystallum_full_20260212 \\
  --database=chrystallum \\
  --force

# Verify restored data integrity
cypher-shell -u neo4j -p password \\
  "MATCH (n) RETURN count(n) AS node_count;"
```

---

## **11.4 Monitoring & Alerts**

### **11.4.1 Health Check Queries**

```cypher
// Daily health check: Count nodes by type
CALL apoc.meta.stats() YIELD labels
RETURN labels;

// Check for schema violations
MATCH (e:Entity)
WHERE e.qid IS NULL OR NOT e.qid STARTS WITH "Q"
RETURN count(e) AS invalid_qids;

// Check consensus score distribution
MATCH (c:Claim)
RETURN 
  avg(c.consensus_score) AS avg_consensus,
  stdev(c.consensus_score) AS stdev_consensus,
  percentileCont(c.consensus_score, 0.5) AS median_consensus;
```

---

### **11.4.2 Alert Conditions**

```python
class SystemMonitor:
    """Monitor system health and send alerts."""
    
    THRESHOLDS = {
        "claim_review_backlog": 100,        # Alert if >100 unreviewed claims
        "invalid_qid_rate": 0.05,           # Alert if >5% invalid QIDs
        "agent_failure_rate": 0.10,         # Alert if >10% agent failures
        "consensus_score_drop": 0.15        # Alert if avg drops >0.15
    }
    
    def check_health(self):
        """Run all health checks."""
        issues = []
        
        # Check claim backlog
        unreviewed = self.query_neo4j("""
            MATCH (c:Claim {status: 'proposed'})
            WHERE NOT EXISTS((c)<-[:REVIEWS]-())
            RETURN count(c) AS count
        """)[0]["count"]
        
        if unreviewed > self.THRESHOLDS["claim_review_backlog"]:
            issues.append(f"Claim review backlog: {unreviewed} claims awaiting review")
        
        # Check invalid QIDs
        invalid_rate = self.get_invalid_qid_rate()
        if invalid_rate > self.THRESHOLDS["invalid_qid_rate"]:
            issues.append(f"High invalid QID rate: {invalid_rate:.1%}")
        
        # Send alerts if issues found
        if issues:
            self.send_alert("System Health Issues", "\n".join(issues))
```

---

# **12. Future Directions**

## **12.0 Roadmap Overview**

Chrystallum's future development focuses on three areas:
1. **Scalability**: Federated graph networks, distributed consensus
2. **Enrichment**: Expanded authority integration, multilingual support
3. **Research Tools**: Advanced visualization, hypothesis testing

---

## **12.1 Federated Graph Networks**

**Vision**: Multiple Chrystallum instances share knowledge via content-addressable claims

**Architecture:**
```
University A Graph â”€â”
University B Graph â”€â”¼â”€> Shared Claim Registry (ciphers)
Research Lab Graph â”€â”˜         â†“
                          Cross-instance validation
```

**Benefits:**
- Distributed scholarly collaboration
- No central authority required
- Cipher ensures claim integrity across networks
- Consensus emerges from multiple independent validations

**Technical Challenges:**
- Cipher collision resolution
- Cross-instance claim synchronization
- Trust models for foreign claims

---

## **12.2 Multilingual Entity Support**

**Current State**: English-primary with Wikidata multilingual labels

**Future Enhancement:**
- Native support for Latin, Ancient Greek primary sources
- Non-Latin script support (Arabic, Chinese for Silk Road research)
- Language-specific agents with cultural domain expertise

**Implementation:**
```python
# Multi-language entity representation
{
  "qid": "Q1048",
  "labels": {
    "en": "Gaius Julius Caesar",
    "la": "Gaius Iulius Caesar",
    "fr": "Jules CÃ©sar",
    "de": "Gaius Julius CÃ¤sar"
  },
  "primary_language": "la",  # Latin for ancient Roman figure
  "label_preferred": "Gaius Iulius Caesar"  # Use Latin form
}
```

---

## **12.3 Advanced Visualization**

**Planned Features:**
- **Timeline Views**: Stacked timelines by facet (political, military, economic eras)
- **Geographic Maps**: Animated territorial changes over time (PlaceVersion sequence)
- **Network Graphs**: Relationship networks with confidence-weighted edges
- **Provenance Trees**: Visualize complete evidence chains for any claim

**Technology Stack:**
- Cytoscape.js for graph visualization
- D3.js for custom timeline/map rendering
- Neo4j graph algorithms for network analysis

---

## **12.4 Hypothesis Testing Framework**

**Vision**: Researchers propose historical hypotheses, system validates against evidence

**Workflow:**
```
Researcher Hypothesis â†’ Decompose into testable claims â†’ Query graph for supporting/challenging evidence â†’ Calculate hypothesis confidence
```

**Example:**
- Hypothesis: "Caesar's military success was primarily due to loyal veteran legions"
- Decomposition: Check for COMMANDED relationships, VETERAN properties, loyalty indicators
- Evidence: Retrieve all Caesar military campaigns, analyze legion composition
- Result: Confidence score + supporting evidence summary

---

## **12.5 Integration with Emerging Standards**

**Planned Integrations:**
- **IIIF (International Image Interoperability Framework)**: Link to digitized manuscripts
- **TEI (Text Encoding Initiative)**: XML markup for primary source texts
- **Schema.org**: Web semantic markup for public-facing data
- **Linked Open Data (LOD)**: Full RDF export capability

---

---

