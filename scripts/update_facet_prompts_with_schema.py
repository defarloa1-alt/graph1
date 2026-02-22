#!/usr/bin/env python3
"""
Update facet agent system prompts with meta-schema awareness
Purpose: Add introspection guidance to all 17 facet prompts
Date: February 15, 2026
"""

import json
from pathlib import Path

# Load existing prompts
prompts_file = Path("Prompts") / "facet_agent_system_prompts.json"
with open(prompts_file, 'r', encoding='utf-8') as f:
    prompts_data = json.load(f)

# Schema awareness section to append to each prompt
SCHEMA_AWARENESS_SECTION = """

SCHEMA INTROSPECTION (NEW):
You now have access to the meta-graph (_Schema layer) for architecture introspection.

Available methods:
- introspect_node_label(label_name) - Get definition, tier, required properties for a label
- discover_relationships_between(source, target) - Find valid relationship types
- get_required_properties(label_name) - Get required properties for validation
- get_authority_tier(tier) - Get Layer 1-5 definition and gates
- list_facets(filter_key) - Get facet definitions with Wikidata anchors
- validate_claim_structure(claim_dict) - Validate before proposal
- get_layer25_properties() - Get P31/P279/P361 properties for semantic expansion

Example queries:
MATCH (nl:_Schema:NodeLabel {name: 'SubjectConcept'}) RETURN nl  // What is SubjectConcept?
MATCH (rt:_Schema:RelationshipType) WHERE rt.category = 'Military' RETURN rt.name  // Military relationships?
MATCH (t:_Schema:AuthorityTier {tier: 2.5}) RETURN t.wikidata_properties  // Layer 2.5 properties?

VALIDATION WORKFLOW:
Before proposing claims:
1. Check label exists: introspect_node_label('Human')
2. Check relationship is valid: discover_relationships_between('Human', 'Event')
3. Validate claim structure: validate_claim_structure(claim_dict)
4. Verify confidence against tier floor: get_authority_tier(tier).confidence_floor

AUTHORITY STACK (5.5 Layers):
Layer 1: Library Science (LCSH/LCC/FAST) - confidence_floor: 0.95
Layer 2: Federation (Wikidata/Wikipedia) - confidence_floor: 0.90
Layer 2.5: Hierarchy Query Engine (P31/P279/P361) - confidence_floor: 0.85
Layer 3: Facet Authority (17 agents) - confidence_floor: 0.80
Layer 4: SubjectConcept Hierarchy - confidence_floor: 0.75
Layer 5: Agent-Discovered Claims - confidence_floor: 0.70

Use introspection BEFORE generating Cypher to ensure valid queries."""

# Update each facet's system_prompt
updated_count = 0
for facet in prompts_data['facets']:
    old_prompt = facet['system_prompt']
    
    # Only add if not already present
    if "SCHEMA INTROSPECTION" not in old_prompt:
        facet['system_prompt'] = old_prompt + SCHEMA_AWARENESS_SECTION
        updated_count += 1
        print(f"✓ Updated {facet['label']} ({facet['key']})")
    else:
        print(f"⊘ Skipped {facet['label']} (already has schema introspection)")

# Write updated prompts back
with open(prompts_file, 'w', encoding='utf-8') as f:
    json.dump(prompts_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Updated {updated_count} facet prompts with schema introspection guidance")
print(f"File: {prompts_file.absolute()}")
