# Step 1 Complete: Agent Architecture Understanding
**Date:** February 15, 2026  
**Status:** ✅ Complete  
**Decision:** Hybrid approach (Curated docs for rationale + Meta-graph for introspection)

## What Was Implemented

### 1. Meta-Schema Graph (783 lines)
**File:** `Neo4j/schema/06_meta_schema_graph.cypher`

**Contents:**
- **Authority Tiers (5.5 layers):** 6 `_Schema:AuthorityTier` nodes
  - Layer 1: Library Science (LCSH/LCC/FAST) - confidence_floor: 0.95
  - Layer 2: Federation (Wikidata/Wikipedia) - confidence_floor: 0.90
  - Layer 2.5: Hierarchy Query Engine (P31/P279/P361) - confidence_floor: 0.85
  - Layer 3: Facet Authority (17 agents) - confidence_floor: 0.80
  - Layer 4: SubjectConcept Hierarchy - confidence_floor: 0.75
  - Layer 5: Agent-Discovered Claims - confidence_floor: 0.70

- **Node Labels:** 14 `_Schema:NodeLabel` nodes
  - SubjectConcept, Human, Event, Place, Period, Year, Claim
  - Organization, Institution, Dynasty, Gens, Praenomen, Cognomen, LegalRestriction
  - Each with tier, required_properties, optional_properties, uniqueness_constraint

- **Facet Definitions:** 17 `_Schema:FacetReference` nodes (meta-tagged)
  - Military, Political, Economic, Religious, Social, Cultural, Artistic
  - Intellectual, Linguistic, Geographic, Environmental, Technological
  - Demographic, Diplomatic, Scientific, Archaeological, Communication

- **Relationship Types:** Sample relationship definitions (expandable to 312)
  - Classification: INSTANCE_OF (P31), SUBCLASS_OF (P279), PART_OF (P361)
  - Expertise: FIELD_OF_WORK (P101) for expert discovery
  - Content: MAIN_SUBJECT (P921) for source discovery
  - Authorship: AUTHOR (P50), WORK_OF
  - Causality: CAUSED, CAUSED_BY (P828)
  - Temporal: OCCURRED_IN (P585)

- **Property Definitions:** Core properties with validation
  - id_hash (unique identifier), label, wikidata_qid, confidence
  - Claim-specific: claim_id, cipher, status, facet

- **Validation Rules:** 5 validation rules
  - VR001: Node label uniqueness on id_hash
  - VR002: Claim must have cipher
  - VR003: Confidence range 0.0-1.0
  - VR004: Authority alignment required (LCSH or Wikidata)
  - VR005: No year zero in temporal backbone

- **Query Examples:** 6 example queries for agent usage
  - List node labels, find relationships, get facets, check properties
  - Layer 2.5 hierarchy properties, expert discovery

- **Indexes:** 5 indexes for fast meta-graph queries

### 2. Agent Introspection Methods
**File:** `scripts/agents/facet_agent_framework.py`

**Added 8 methods to FacetAgent class:**

```python
introspect_node_label(label_name: str) -> Optional[Dict[str, Any]]
  # Query meta-graph for label definition, tier, properties
  # Example: introspect_node_label('SubjectConcept')

discover_relationships_between(source_label: str, target_label: str) -> List[Dict[str, Any]]
  # Find valid relationship types between labels
  # Example: discover_relationships_between('Human', 'Event')

get_required_properties(label_name: str) -> List[str]
  # Get required properties for validation
  # Example: get_required_properties('Claim')

get_authority_tier(tier: float) -> Optional[Dict[str, Any]]
  # Get layer definition, gates, confidence floor
  # Example: get_authority_tier(2.5)

list_facets(filter_key: Optional[str] = None) -> List[Dict[str, Any]]
  # List facets with Wikidata anchors
  # Example: list_facets('military')

validate_claim_structure(claim_dict: Dict[str, Any]) -> Tuple[bool, List[str]]
  # Validate claim before proposal
  # Returns: (is_valid, errors_list)

get_layer25_properties() -> List[str]
  # Get P31/P279/P361 properties for semantic expansion
  # Returns: ['P31', 'P279', 'P361', 'P101', 'P2578', 'P921', 'P1269']
```

**Impact:**
- Agents can now query schema before generating Cypher
- Validation happens before claim proposal (catch errors early)
- Agents understand authority stack and confidence requirements
- Self-documenting architecture via introspection

### 3. Updated System Prompts
**File:** `facet_agent_system_prompts.json`

**Updated:** All 17 facet prompts now include:

```
SCHEMA INTROSPECTION (NEW):
You now have access to the meta-graph (_Schema layer) for architecture introspection.

Available methods:
- introspect_node_label(label_name)
- discover_relationships_between(source, target)
- get_required_properties(label_name)
- get_authority_tier(tier)
- list_facets(filter_key)
- validate_claim_structure(claim_dict)
- get_layer25_properties()

Example queries:
MATCH (nl:_Schema:NodeLabel {name: 'SubjectConcept'}) RETURN nl
MATCH (rt:_Schema:RelationshipType) WHERE rt.category = 'Military' RETURN rt.name
MATCH (t:_Schema:AuthorityTier {tier: 2.5}) RETURN t.wikidata_properties

VALIDATION WORKFLOW:
1. Check label exists: introspect_node_label('Human')
2. Check relationship is valid: discover_relationships_between('Human', 'Event')
3. Validate claim structure: validate_claim_structure(claim_dict)
4. Verify confidence against tier floor: get_authority_tier(tier).confidence_floor

AUTHORITY STACK (5.5 Layers):
Layer 1: Library Science - confidence_floor: 0.95
Layer 2: Federation - confidence_floor: 0.90
Layer 2.5: Hierarchy Query Engine - confidence_floor: 0.85
Layer 3: Facet Authority - confidence_floor: 0.80
Layer 4: SubjectConcept Hierarchy - confidence_floor: 0.75
Layer 5: Agent-Discovered Claims - confidence_floor: 0.70
```

**Facets Updated:**
- ✅ Military, Political, Economic, Religious, Social, Cultural, Artistic
- ✅ Intellectual, Linguistic, Geographic, Environmental, Technological
- ✅ Demographic, Diplomatic, Scientific, Archaeological, Communication

## Deployment Instructions

### Option 1: Deploy Meta-Schema Now (If Neo4j is Running)

```bash
# Check Neo4j is accessible
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'YOUR_PASSWORD')); driver.verify_connectivity(); print('✓ Connected')"

# Deploy meta-schema
python Neo4j/schema/run_cypher_file.py Neo4j/schema/06_meta_schema_graph.cypher

# Verify deployment
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'YOUR_PASSWORD'))
with driver.session() as session:
    result = session.run('MATCH (n:_Schema:NodeLabel) RETURN count(n) AS count')
    print(f'Node labels: {result.single()[\"count\"]}')  # Should be 14
    
    result = session.run('MATCH (t:_Schema:AuthorityTier) RETURN count(t) AS count')
    print(f'Authority tiers: {result.single()[\"count\"]}')  # Should be 6
"
```

### Option 2: Deploy Later (After Neo4j Setup)

If NEO4J_PASSWORD is not yet configured:
1. Run `setup_config.bat` or create `config.py` from `config.py.example`
2. Set Neo4j credentials
3. Then run deployment commands from Option 1

## Verification Tests

Once deployed, test agent introspection:

```python
from scripts.agents.facet_agent_framework import FacetAgent

# Initialize any facet agent (e.g., Military)
agent = FacetAgent('military', 'Military', system_prompt='...')

# Test introspection methods
label_def = agent.introspect_node_label('SubjectConcept')
print(f"SubjectConcept definition: {label_def}")

relationships = agent.discover_relationships_between('Human', 'Event')
print(f"Human→Event relationships: {relationships}")

tier_def = agent.get_authority_tier(2.5)
print(f"Layer 2.5 properties: {tier_def['wikidata_properties']}")

facets = agent.list_facets()
print(f"Available facets: {len(facets)}")

# Test claim validation
test_claim = {
    'claim_id': 'TEST_001',
    'cipher': 'MATCH (n) RETURN n',
    'confidence': 0.85,
    'facet': 'military',
    'status': 'proposed'
}
is_valid, errors = agent.validate_claim_structure(test_claim)
print(f"Claim valid: {is_valid}, Errors: {errors}")
```

## Benefits Achieved

### For Agents:
1. **Self-Discovery:** Agents can query schema without hardcoding
2. **Validation:** Catch schema violations before submitting claims
3. **Authority Awareness:** Understand confidence requirements per layer
4. **Relationship Discovery:** Find valid connections between entities
5. **Facet Awareness:** Understand domain boundaries and anchors

### For Developers:
1. **Single Source of Truth:** Schema defined once in meta-graph
2. **Queryable Documentation:** No need to read multiple files
3. **Easy Extension:** Add new labels/relationships via Cypher CREATE
4. **Consistent Validation:** All agents use same schema rules

### For Historians:
1. **Transparency:** Query meta-graph to understand system structure
2. **Traceable Decisions:** Rationale still in curated docs
3. **Authority Stack Visible:** See confidence floors per layer
4. **Facet Definitions Clear:** Understand domain boundaries

## Architecture Decisions Preserved

### Why Hybrid Approach?
- **Meta-Graph:** Agents need queryable schema (WHAT the system IS)
- **Curated Docs:** Historians need rationale (WHY decisions were made)
- **No SysML v2:** Not needed unless formal verification required

### Why 5.5 Layers?
- Layer 2.5 added for Wikidata semantic inference (P31/P279/P361)
- Transitive queries need separate handling from simple federation
- Centralized hierarchy engine prevents agent duplication

### Why 14 First-Class Labels?
- SubjectConcept is canonical (not Concept)
- Communication is facet, not node type
- Roman domain labels (Gens, Praenomen, Cognomen) domain-specific

### Why Layer 3 for Facets?
- Facets enforce disciplinary knowledge boundaries
- Agents route queries to appropriate domain experts
- 17 facets with Wikidata anchors ensure precision

## Next Steps (Step 2-N)

User will guide step-by-step review:
- Step 2: Agent Query Lifecycle (TBD)
- Step 3: Claim Proposal Process (TBD)
- Step 4: Authority Stack Integration (TBD)
- Step N: Additional topics (TBD)

After all steps complete:
- Refactor architecture docs to focus on rationale
- Remove schema duplication (now in meta-graph)
- Create META_GRAPH_USAGE_GUIDE.md for developers

## Files Modified

1. ✅ `Neo4j/schema/06_meta_schema_graph.cypher` (already existed, 783 lines)
2. ✅ `scripts/agents/facet_agent_framework.py` (added 8 introspection methods)
3. ✅ `facet_agent_system_prompts.json` (updated all 17 prompts)
4. ✅ `scripts/update_facet_prompts_with_schema.py` (created automation script)

## Completion Checklist

- ✅ Meta-schema Cypher script complete (783 lines)
- ✅ Agent introspection methods added (8 methods)
- ✅ System prompts updated (17 facets)
- ⏸️ Meta-schema deployed to Neo4j (waiting for credentials)
- ⏸️ Introspection tests verified (waiting for deployment)

**Status:** Step 1 implementation complete, awaiting Neo4j deployment for verification.
