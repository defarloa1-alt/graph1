#!/usr/bin/env python3
"""
Update facet agent system prompts with Step 3: Federation-Driven Discovery
Purpose: Add Wikidata integration and automatic claim generation guidance
Date: February 15, 2026
"""

import json
from pathlib import Path

# Load existing prompts
prompts_file = Path("facet_agent_system_prompts.json")
with open(prompts_file, 'r', encoding='utf-8') as f:
    prompts_data = json.load(f)

# Federation discovery section to add after state introspection
FEDERATION_DISCOVERY_SECTION = """

FEDERATION-DRIVEN DISCOVERY (STEP 3 - NEW):
You can now bootstrap knowledge directly from Wikidata via Layer 2 Federation Authority.

Available federation methods:
- fetch_wikidata_entity(qid) - Get full entity data (label, description, all claims)
- enrich_node_from_wikidata(node_id, qid) - Add Wikidata properties to existing node
- discover_hierarchy_from_entity(qid, depth) - Traverse P31/P279/P361 hierarchies
- generate_claims_from_wikidata(qid) - Auto-generate claims from Wikidata statements
- bootstrap_from_qid(qid, depth, auto_submit) - Complete workflow from QID

BOOTSTRAP WORKFLOW (when starting on new topic):
1. User provides a seed QID (e.g., Q17167 for Roman Republic)
2. Call: result = agent.bootstrap_from_qid('Q17167', depth=1)
3. This automatically:
   - Fetches Wikidata entity
   - Creates SubjectConcept nodes
   - Discovers related entities via Layer 2.5 properties (P31/P279/P361)
   - Generates claims for discovered relationships
   - Optionally submits claims >= 0.90 confidence

HIERARCHY TRAVERSAL:
Layer 2.5 properties automatically followed:
- P31 (instance of) → INSTANCE_OF relationship
- P279 (subclass of) → SUBCLASS_OF relationship
- P361 (part of) → PART_OF relationship
- P101 (field of work) → FIELD_OF_WORK relationship
- P921 (main subject) → MAIN_SUBJECT relationship
- P2578 (studies) → STUDIES relationship
- P1269 (facet of) → FACET_OF relationship

Example: "Roman Republic" (Q17167)
- P31: Q6256 (country) → Creates INSTANCE_OF relationship
- P361: Q1747689 (Ancient Rome) → Creates PART_OF relationship
- Discovers entities recursively up to specified depth

CLAIM GENERATION:
Wikidata statements automatically transform to claims:
- High confidence (0.90) because from authoritative source
- Authority tracking: {source_qid, property, target_qid}
- Provenance: "Discovered via Layer 2.5 property P31 from Wikidata"
- Facet assignment: Your facet takes ownership

ENRICHMENT WORKFLOW (for existing nodes):
1. Check if node already has wikidata_qid: get_subjectconcept_subgraph()
2. If missing QID, fetch from Wikidata: fetch_wikidata_entity(qid)
3. Enrich node: enrich_node_from_wikidata(node_id, qid)
4. Discover related entities: discover_hierarchy_from_entity(qid)
5. Generate claims: generate_claims_from_wikidata(qid)

WHEN TO USE FEDERATION:
- Agent starts work on new historical topic
- SubjectConcept node missing Wikidata alignment
- Need to discover related entities quickly
- Building out domain knowledge graph
- Validating against authoritative sources

AUTHORITY STACK INTEGRATION:
- Layer 1 (LCSH/LCC): Still primary for subject validation
- Layer 2 (Wikidata): Federation authority provides entity data
- Layer 2.5 (Hierarchy): Discovers semantic relationships automatically
- Layer 3 (Facet): You interpret discoveries through domain lens
- Claims submitted with federated authority tracking

Example bootstrap session:
```python
# Bootstrap military knowledge from Battle of Pharsalus
result = agent.bootstrap_from_qid('Q28048', depth=2, auto_submit=False)
print(f"Discovered {result['nodes_created']} entities")
print(f"Generated {result['claims_generated']} claims")

# Review generated claims before submitting
for claim in result['claims']:
    print(f"  {claim['label']} (conf: {claim['confidence']:.2f})")

# Submit selectively or all at once
# (auto_submit=True would have submitted automatically)
```

COLLABORATIVE FEDERATION:
Multiple agents can bootstrap from same QID:
- Each agent interprets through their facet lens
- Military agent: focuses on warfare relationships
- Political agent: focuses on governance relationships
- Claims are facet-specific even from same source"""

# Update each facet's system_prompt
updated_count = 0
for facet in prompts_data['facets']:
    old_prompt = facet['system_prompt']
    
    # Only add if not already present
    if "FEDERATION-DRIVEN DISCOVERY" not in old_prompt:
        # Insert after state introspection
        if "Use state introspection to AVOID proposing duplicate or conflicting claims." in old_prompt:
            facet['system_prompt'] = old_prompt + FEDERATION_DISCOVERY_SECTION
            updated_count += 1
            print(f"✓ Updated {facet['label']} ({facet['key']})")
        else:
            print(f"⚠ Skipped {facet['label']} (state introspection not found)")
    else:
        print(f"⊘ Skipped {facet['label']} (already has federation discovery)")

# Update version
prompts_data['version'] = "2026-02-15-step3"

# Write updated prompts back
with open(prompts_file, 'w', encoding='utf-8') as f:
    json.dump(prompts_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Updated {updated_count} facet prompts with federation discovery guidance (Step 3)")
print(f"File: {prompts_file.absolute()}")
print(f"Version: {prompts_data['version']}")
