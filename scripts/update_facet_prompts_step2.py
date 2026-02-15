#!/usr/bin/env python3
"""
Update facet agent system prompts with Step 2: Current State Introspection
Purpose: Add state query methods to all 17 facet prompts
Date: February 15, 2026
"""

import json
from pathlib import Path

# Load existing prompts
prompts_file = Path("facet_agent_system_prompts.json")
with open(prompts_file, 'r', encoding='utf-8') as f:
    prompts_data = json.load(f)

# State introspection section to add after schema introspection
STATE_INTROSPECTION_SECTION = """

CURRENT STATE INTROSPECTION (STEP 2 - NEW):
CRITICAL: LLMs don't persist between sessions. You must reload graph state at session start.

Available state query methods:
- get_session_context() - CALL THIS FIRST! Loads SubjectConcept snapshot, pending claims, your stats
- get_subjectconcept_subgraph(limit=100) - Current SubjectConcept nodes and relationships
- find_claims_for_node(node_id) - All claims referencing a specific node
- find_claims_for_relationship(source_id, target_id, rel_type) - Claims about relationships
- get_node_provenance(node_id) - Which claim(s) created/modified this node
- get_claim_history(node_id) - Full audit trail for a node
- list_pending_claims(facet, min_confidence) - Claims awaiting validation
- find_agent_contributions(agent_id) - What this agent has proposed

SESSION INITIALIZATION WORKFLOW:
1. ALWAYS call get_session_context() at start of new session or conversation
2. Review subgraph_sample to see what SubjectConcept nodes exist
3. Check pending_claims to see your unvalidated claims
4. Review recent_promotions to see what's been added recently
5. Use my_contributions stats to understand your track record

BEFORE PROPOSING NEW CLAIMS:
1. Check if node already exists: get_subjectconcept_subgraph()
2. Review existing claims: find_claims_for_node(node_id)
3. Check provenance: get_node_provenance(node_id)
4. Avoid duplicates: list_pending_claims(facet=self.facet_key)

CLAIM LIFECYCLE TRACKING:
Status values: 'proposed' → 'validated' → (promoted=true)
- proposed: Awaiting validation (posterior >= 0.90, confidence >= 0.90 for auto-promotion)
- validated: Passed validation, promoted to canonical graph
- rejected: Failed validation (rare, fallacies don't auto-reject)

PROVENANCE UNDERSTANDING:
- Nodes created by claims have (Node)-[:SUPPORTED_BY]->(Claim) relationships
- Relationships created by claims have promoted_from_claim_id property
- Use get_node_provenance() to see which agent created what

Example session start:
```python
# Load current state
context = agent.get_session_context()
print(f"SubjectConcept nodes: {context['subgraph_sample']['count']}")
print(f"My pending claims: {len(context['pending_claims'])}")
print(f"My promoted claims: {context['my_contributions']['promoted_claims']}")

# Check if entity already exists before proposing
subgraph = agent.get_subjectconcept_subgraph(limit=200)
existing_labels = [n['label'] for n in subgraph['nodes']]
if "Roman Republic" in existing_labels:
    print("Roman Republic already exists, checking claims...")
    claims = agent.find_claims_for_node("hash_of_roman_republic")
```

COLLABORATIVE AWARENESS:
Multiple agents work on the same graph. Always check:
- What other agents have proposed about this topic
- Whether claims conflict or complement
- Provenance to understand agent specialization

Use state introspection to AVOID proposing duplicate or conflicting claims."""

# Update each facet's system_prompt
updated_count = 0
for facet in prompts_data['facets']:
    old_prompt = facet['system_prompt']
    
    # Only add if not already present
    if "CURRENT STATE INTROSPECTION" not in old_prompt:
        # Find the end of the schema introspection section
        if "Use introspection BEFORE generating Cypher to ensure valid queries." in old_prompt:
            # Insert after schema introspection
            facet['system_prompt'] = old_prompt + STATE_INTROSPECTION_SECTION
            updated_count += 1
            print(f"✓ Updated {facet['label']} ({facet['key']})")
        else:
            print(f"⚠ Skipped {facet['label']} (schema introspection not found)")
    else:
        print(f"⊘ Skipped {facet['label']} (already has state introspection)")

# Update version
prompts_data['version'] = "2026-02-15-step2"

# Write updated prompts back
with open(prompts_file, 'w', encoding='utf-8') as f:
    json.dump(prompts_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Updated {updated_count} facet prompts with state introspection guidance (Step 2)")
print(f"File: {prompts_file.absolute()}")
print(f"Version: {prompts_data['version']}")
