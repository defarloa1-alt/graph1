# Agent Session Quick Reference
**For:** Chrystallum Facet Agents  
**Date:** February 15, 2026  
**Steps Implemented:** 1 (Architecture) + 2 (State) + 3 (Federation) + 3.5 (Validation) + 4 (Ontology)

**Architecture Reference:** `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md` (authoritative spec)

## Critical: Session Initialization (REQUIRED)

Every agent session MUST start with this:

```python
from scripts.agents.facet_agent_framework import FacetAgent

# 1. Initialize agent
agent = FacetAgent('military', 'Military', system_prompt=military_prompt)

# 2. CRITICAL: Load session context (Step 2)
context = agent.get_session_context()

# 3. Review current state
print(f"📊 Session initialized at {context['timestamp']}")
print(f"   SubjectConcept nodes: {context['subgraph_sample']['count']}")
print(f"   My pending claims: {len(context['pending_claims'])}")
print(f"   My promoted claims: {context['my_contributions']['promoted_claims']}")
print(f"   Schema version: {context['schema_version']['node_labels']} labels")
```

**Why This Matters:** LLMs don't persist between sessions. Without `get_session_context()`, you don't know what exists in the graph.

---

## Complete Agent Workflow (Steps 1-4)

### Phase 1: Understand Architecture (Step 1)

**Q: What node labels are valid?**
```python
label_def = agent.introspect_node_label('SubjectConcept')
print(f"Tier: {label_def['tier']}")
print(f"Required properties: {label_def['required_properties']}")
```

**Q: What relationships can connect Human to Event?**
```python
rels = agent.discover_relationships_between('Human', 'Event')
for rel in rels:
    print(f"{rel['relationship_name']}: {rel['description']}")
```

**Q: What are the authority tier confidence requirements?**
```python
tier = agent.get_authority_tier(2.5)
print(f"Layer 2.5: {tier['layer_name']}")
print(f"Confidence floor: {tier['confidence_floor']}")
print(f"Properties: {tier['wikidata_properties']}")
```

**Q: What facets exist?**
```python
facets = agent.list_facets()
for facet in facets:
    print(f"{facet['label']}: {facet['definition']}")
```

### Phase 2: Check Current State (Step 2)

**Q: Does "Roman Republic" already exist?**
```python
subgraph = agent.get_subjectconcept_subgraph(limit=500)
existing_labels = [n['label'].lower() for n in subgraph['nodes']]

if "roman republic" in existing_labels:
    print("✓ Roman Republic already exists!")
    node = next(n for n in subgraph['nodes'] if n['label'].lower() == "roman republic")
    print(f"  ID: {node['id_hash']}")
    print(f"  QID: {node['wikidata_qid']}")
else:
    print("✗ Roman Republic not found, safe to create")
```

**Q: Who created this node?**
```python
provenance = agent.get_node_provenance(node_id)
if provenance['created_by_claim']:
    print(f"Created by claim: {provenance['created_by_claim']}")
    
    # Get full history
    history = agent.get_claim_history(node_id)
    print(f"Agents involved: {history['agents_involved']}")
    print(f"Facets involved: {history['facets_involved']}")
else:
    print("Manually created (no claim provenance)")
```

**Q: Are there existing claims about this node?**
```python
claims = agent.find_claims_for_node(node_id)
print(f"Total claims: {len(claims)}")
for claim in claims:
    print(f"  {claim['source_agent']}: {claim['label']}")
    print(f"    Status: {claim['status']}, Confidence: {claim['confidence']:.2f}")
```

### Phase 3: Bootstrap from Wikidata (Step 3)

**Q: How do I initialize on a new topic quickly?**
```python
# Bootstrap from Wikidata QID (e.g., Q17167 = Roman Republic)
result = agent.bootstrap_from_qid(
    qid='Q17167',
    depth=1,                # How many hierarchy levels to traverse
    auto_submit_claims=False  # Review before submitting
)

print(f"✓ Bootstrapped from Wikidata")
print(f"  Nodes created: {result['nodes_created']}")
print(f"  Relationships discovered: {result['relationships_discovered']}")
print(f"  Claims generated: {result['claims_generated']}")
print(f"  Completeness score: {result.get('completeness_score', 'N/A')}")  # Step 3.5
print(f"  CIDOC-CRM class: {result.get('cidoc_crm_class', 'N/A')}")  # Step 4
```

**Q: What if I just need entity data?**
```python
# Fetch Wikidata entity without creating nodes
entity = agent.fetch_wikidata_entity('Q17167')
print(f"Label: {entity['label']}")
print(f"Description: {entity['description']}")
print(f"Statements: {entity['statement_count']}")
print(f"Claims: {list(entity['claims'].keys())}")
```

**Q: How do I enrich an existing node with Wikidata?**
```python
# Node exists but missing Wikidata alignment
result = agent.enrich_node_from_wikidata(
    node_id='abc123def456',
    qid='Q17167',
    create_if_missing=True
)

print(f"Status: {result['status']}")
print(f"Properties added: {result['properties_added']}")
```

**Q: How do I discover related entities?**
```python
# Traverse Layer 2.5 hierarchy properties
hierarchy = agent.discover_hierarchy_from_entity(
    qid='Q17167',
    depth=2,            # Depth 1=immediate, 2=moderate, 3=comprehensive
    limit_per_property=50  # Prevent explosion
)

print(f"Discovered {hierarchy['total_discovered']} entities")
for entity in hierarchy['discovered_entities'][:5]:
    print(f"  {entity['label']} ({entity['qid']}) via {entity['property']}")
```

**Q: How do I auto-generate claims from Wikidata?**
```python
# Generate claims from Wikidata statements
result = agent.generate_claims_from_wikidata(
    qid='Q17167',
    create_nodes=True,   # Create target nodes automatically
    auto_submit=False    # Review before submitting
)

print(f"Generated {result['claims_generated']} claims")
for claim in result['claims']:
    print(f"  {claim['label']}")
    print(f"    Confidence: {claim['confidence']:.2f}")
    print(f"    Authority: {claim['authority_source']}")
    
    # Submit if high confidence
    if claim['confidence'] >= 0.90:
        agent.pipeline.ingest_claim(claim)
```

**Q: What hierarchy properties are traversed?**
```python
# Layer 2.5 properties for semantic inference
layer25 = agent.get_layer25_properties()
for prop in layer25:
    print(f"{prop['wikidata_property']}: {prop['property_name']}")
    print(f"  → {prop['cypher_relationship']} relationship")

# Common properties:
# - P31 (instance of) → INSTANCE_OF
# - P279 (subclass of) → SUBCLASS_OF
# - P361 (part of) → PART_OF
# - P101 (field of work) → FIELD_OF_WORK
# - P921 (main subject) → MAIN_SUBJECT
```

**Q: Are there claims about relationships between nodes?**
```python
rel_claims = agent.find_claims_for_relationship(
    source_id="hash_of_caesar",
    target_id="hash_of_battle",
    rel_type="PARTICIPATED_IN"
)
for claim in rel_claims:
    print(f"{claim['source_agent']}: {claim['label']}")
```

**Q: What claims am I currently waiting on?**
```python
pending = agent.list_pending_claims(facet='military', min_confidence=0.80)
print(f"Pending military claims (≥0.80 confidence): {len(pending)}")
for claim in pending:
    print(f"  {claim['label']} (conf: {claim['confidence']:.2f}, post: {claim['posterior']:.2f})")
```

**Q: What's my track record?**
```python
contrib = agent.find_agent_contributions()
promotion_rate = contrib['promoted_claims'] / contrib['total_claims'] if contrib['total_claims'] > 0 else 0

print(f"📈 My Statistics:")
print(f"   Total claims: {contrib['total_claims']}")
print(f"   Promoted: {contrib['promoted_claims']} ({promotion_rate:.1%})")
print(f"   Pending: {contrib['pending_claims']}")
print(f"   Rejected: {contrib['rejected_claims']}")
```

### Phase 4: Validate Before Proposing (Steps 1-4)

**Before proposing a new claim, ALWAYS:**

```python
# 1. Check schema validity (Step 1)
label_valid = agent.introspect_node_label('SubjectConcept')
if not label_valid:
    print("ERROR: Invalid label!")
    return

rels_valid = agent.discover_relationships_between('Human', 'Event')
if not rels_valid:
    print("ERROR: No valid relationships between Human and Event!")
    return

# 2. Check if entity already exists (Step 2)
subgraph = agent.get_subjectconcept_subgraph(limit=1000)
existing = [n['label'].lower() for n in subgraph['nodes']]

proposed_label = "Battle of Pharsalus"
if proposed_label.lower() in existing:
    print(f"WARNING: {proposed_label} already exists!")
    return

# 3. Validate entity completeness (Step 3.5)
entity = agent.fetch_wikidata_entity('Q28048')
completeness = agent.validate_entity_completeness(entity, 'Q178561')
if completeness['score'] < 0.60:
    print(f"ERROR: Entity quality too low ({completeness['score']:.1%})")
    return

# 4. Check CIDOC-CRM alignment (Step 4)
entity_enriched = agent.enrich_with_ontology_alignment(entity)
cidoc_class = entity_enriched['ontology_alignment']['cidoc_crm_class']
print(f"CIDOC-CRM class: {cidoc_class}")  # E5_Event, E21_Person, etc.

# 5. Check for similar pending claims (Step 2)
    # Check provenance
    prov = agent.get_node_provenance(node['id_hash'])
    print(f"Created by: {prov['created_by_claim']}")
    
    # Check existing claims
    claims = agent.find_claims_for_node(node['id_hash'])
    print(f"Existing claims: {len(claims)}")
    
    # Decision: modify existing or skip?
    return  # Don't duplicate!

# 3. Check if entity already exists (Step 2)
subgraph = agent.get_subjectconcept_subgraph(limit=1000)
existing = [n['label'].lower() for n in subgraph['nodes']]

proposed_label = "Battle of Pharsalus"
if proposed_label.lower() in existing:
    print(f"WARNING: {proposed_label} already exists!")
    return

# 4. Validate entity completeness (Step 3.5 - NEW)
entity = agent.fetch_wikidata_entity('Q28048')
completeness = agent.validate_entity_completeness(entity, 'Q178561')
if completeness['score'] < 0.60:
    print(f"ERROR: Entity quality too low ({completeness['score']:.1%})")
    return

# 5. Check CIDOC-CRM alignment (Step 4 - NEW)
entity_enriched = agent.enrich_with_ontology_alignment(entity)
cidoc_class = entity_enriched['ontology_alignment']['cidoc_crm_class']
if not cidoc_class:
    print("WARNING: No CIDOC-CRM mapping available")

# 6. Check for similar pending claims (Step 2)
pending = agent.list_pending_claims(facet='military')
similar = [c for c in pending if "pharsalus" in c['label'].lower()]
if similar:
    print(f"WARNING: {len(similar)} similar pending claims found")
    for claim in similar:
        print(f"  {claim['source_agent']}: {claim['label']}")
    # Decision: wait or proceed?

# 7. Validate claim structure (Step 1)
test_claim = {
    'claim_id': 'test',
    'cipher': 'test',
    'confidence': 0.92,
    'facet': 'military',
    'status': 'proposed'
}
is_valid, errors = agent.validate_claim_structure(test_claim)
if not is_valid:
    print(f"ERROR: Claim validation failed: {errors}")
    return

# 8. Now safe to propose
print("✓ All validations passed, proposing claim...")
agent.propose_claim(...)
```

---

## Typical Query Patterns

### Exploring the Graph

**"What SubjectConcept nodes exist related to Rome?"**
```python
subgraph = agent.get_subjectconcept_subgraph(limit=1000)
rome_related = [n for n in subgraph['nodes'] if 'rome' in n['label'].lower() or 'roman' in n['label'].lower()]
print(f"Found {len(rome_related)} Rome-related nodes:")
for node in rome_related[:10]:
    print(f"  {node['label']} (QID: {node['wikidata_qid']})")
```

**"What relationships exist between SubjectConcept nodes?"**
```python
subgraph = agent.get_subjectconcept_subgraph(limit=1000)
print(f"Relationships: {len(subgraph['relationships'])}")
for rel in subgraph['relationships'][:10]:
    print(f"  {rel['relationship_type']}: {rel['source_id']} → {rel['target_id']}")
```

### Tracking Provenance

**"Show me the full history of this node"**
```python
history = agent.get_claim_history(node_id)
print(f"Node: {history['node_label']}")
print(f"Timeline ({len(history['claim_timeline'])} claims):")
for claim in history['claim_timeline']:
    print(f"  {claim['timestamp']}: {claim['agent']} - {claim['label']}")
    print(f"    Status: {claim['status']}, Promoted: {claim['promoted']}")
```

**"What has the political agent contributed?"**
```python
political_contrib = agent.find_agent_contributions(agent_id='political')
print(f"Political Agent Statistics:")
print(f"  Total: {political_contrib['total_claims']}")
print(f"  Promoted: {political_contrib['promoted_claims']}")
print(f"  Promotion rate: {political_contrib['promoted_claims']/political_contrib['total_claims']:.1%}")
```

### Monitoring Quality

**"Show high-confidence pending claims across all facets"**
```python
high_conf_pending = agent.list_pending_claims(min_confidence=0.90, limit=100)
print(f"High-confidence pending ({len(high_conf_pending)}):")
for claim in high_conf_pending[:20]:
    print(f"  {claim['facet']}/{claim['source_agent']}: {claim['label']}")
    print(f"    Conf: {claim['confidence']:.2f}, Post: {claim['posterior']:.2f}")
```

**"What claims are stuck in pending status?"**
```python
from datetime import datetime, timedelta

pending = agent.list_pending_claims(limit=200)
now = datetime.utcnow()

for claim in pending:
    timestamp = datetime.fromisoformat(claim['timestamp'].replace('Z', '+00:00'))
    age = (now - timestamp).days
    
    if age > 7:  # Older than 7 days
        print(f"⚠ Stale claim ({age} days old):")
        print(f"   {claim['label']}")
        print(f"   Conf: {claim['confidence']:.2f}, Post: {claim['posterior']:.2f}")
```

---

## Error Prevention Checklist

Before every claim proposal, verify:

- [ ] ✅ Session context loaded: `context = agent.get_session_context()`
- [ ] ✅ Schema validated: `introspect_node_label()`, `discover_relationships_between()`
- [ ] ✅ Entity checked: `get_subjectconcept_subgraph()` or `find_claims_for_node()`
- [ ] ✅ Provenance reviewed: `get_node_provenance()`
- [ ] ✅ Duplicates avoided: `list_pending_claims(facet=self.facet_key)`
- [ ] ✅ Claim structure valid: `validate_claim_structure()`
- [ ] ✅ Confidence appropriate for tier: `get_authority_tier().confidence_floor`

---

## Common Mistakes to Avoid

**❌ NOT loading session context**
```python
# WRONG: Blind proposal without checking state
agent = FacetAgent('military', 'Military', prompt)
agent.propose_claim(...)  # No idea what exists!
```

**✅ Correct approach**
```python
agent = FacetAgent('military', 'Military', prompt)
context = agent.get_session_context()  # Load state first!
# ... check existing nodes, claims, etc.
agent.propose_claim(...)
```

**❌ Proposing duplicates**
```python
# WRONG: Assuming entity doesn't exist
agent.propose_claim(entity="Roman Republic", ...)
```

**✅ Correct approach**
```python
subgraph = agent.get_subjectconcept_subgraph(limit=500)
if "roman republic" in [n['label'].lower() for n in subgraph['nodes']]:
    print("Already exists, skipping proposal")
else:
    agent.propose_claim(...)
```

**❌ Ignoring provenance**
```python
# WRONG: Modifying node without checking who created it
agent.propose_claim(modify_node_id, ...)
```

**✅ Correct approach**
```python
prov = agent.get_node_provenance(node_id)
history = agent.get_claim_history(node_id)
print(f"Node created by: {prov['created_by_claim']}")
print(f"Agents involved: {history['agents_involved']}")
# Now make informed decision about modification
```

---

## Quick Reference: All Methods (Steps 1-4)

### Step 1: Schema Introspection (8 methods)
- `introspect_node_label(label_name)` - Label definition
- `discover_relationships_between(source, target)` - Valid relationships
- `get_required_properties(label_name)` - Required properties
- `get_authority_tier(tier)` - Layer definition
- `list_facets(filter_key)` - Facet definitions
- `validate_claim_structure(claim_dict)` - Validate before proposal
- `get_layer25_properties()` - Semantic inference properties

### Step 3: Federation Discovery (6 methods)
- **`bootstrap_from_qid(qid, depth, auto_submit)`** - High-level Wikidata initialization
- `fetch_wikidata_entity(qid)` - Fetch entity from Wikidata API
- `enrich_node_from_wikidata(node_id, qid)` - Create/update with Wikidata properties
- `discover_hierarchy_from_entity(qid, depth)` - Traverse P31/P279/P361 hierarchies
- `generate_claims_from_wikidata(qid)` - Auto-generate claims from statements
- `_map_wikidata_property_to_relationship(prop)` - Internal P-code mapping

### Step 3.5: Completeness Validation (2 methods - NEW)
- **`validate_entity_completeness(entity, entity_type)`** - Score entity quality 0.0-1.0
- `_load_property_patterns()` - Load empirical patterns from 841-entity sample

### Step 4: Semantic Enrichment & Ontology Alignment (4 methods - NEW)
- **`enrich_with_ontology_alignment(entity)`** - Add CIDOC-CRM classes and properties
- **`enrich_claim_with_crminf(claim)`** - Add CRMinf belief tracking
- `generate_semantic_triples(qid, include_cidoc, include_crminf)` - Full semantic triples
- `_load_cidoc_crosswalk()` - Load CIDOC/Wikidata/CRMinf mappings (105 mappings) (8 methods)
- **`get_session_context()`** - **CALL FIRST!** Complete session snapshot
- `get_subjectconcept_subgraph(limit)` - Current nodes and relationships
- `find_claims_for_node(node_id)` - Claims about a node
- `find_claims_for_relationship(source, target, rel_type)` - Claims about relationships
- `get_node_provenance(node_id)` - Creation/modification provenance
- `get_claim_history(node_id)` - Full audit trail
- `list_pending_claims(facet, min_confidence, limit)` - Pending claims
- `find_agent_contributions(agent_id, limit)` - Agent statistics

### Step 3: Federation Discovery (6 methods)
- **`bootstrap_from_qid(qid, depth, auto_submit)`** - High-level Wikidata initialization
- `fetch_wikidata_entity(qid)` - Fetch entity from Wikidata API
- `enrich_node_from_wikidata(node_id, qid)` - Create/update with Wikidata properties
- `discover_hierarchy_from_entity(qid, depth)` - Traverse P31/P279/P361 hierarchies  
- `generate_claims_from_wikidata(qid)` - Auto-generate claims from statements
- `_map_wikidata_property_to_relationship(prop)` - Internal P-code mapping

### Step 3.5: Completeness Validation (2 methods - NEW)
- **`validate_entity_completeness(entity, entity_type)`** - Score entity quality 0.0-1.0
- `_load_property_patterns()` - Load empirical patterns from 841-entity sample

### Step 4: Semantic Enrichment & Ontology Alignment (4 methods - NEW)
- **`enrich_with_ontology_alignment(entity)`** - Add CIDOC-CRM classes and properties  
- **`enrich_claim_with_crminf(claim)`** - Add CRMinf belief tracking
- `generate_semantic_triples(qid, include_cidoc, include_crminf)` - Full semantic triples
- `_load_cidoc_crosswalk()` - Load CIDOC/Wikidata/CRMinf mappings (105 mappings)

**Total Methods:** 28 across 4 completed steps

---

## Next Steps

**Step 5+:** TBD by user (query decomposition? multi-agent debate? RDF export? CIDOC validation?)

**For Now:** Practice combining Steps 1-4 for informed, high-quality, ontology-aligned claim proposals.
