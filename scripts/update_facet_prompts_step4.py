#!/usr/bin/env python3
"""
Update facet agent system prompts with Step 4: Semantic Enrichment & Ontology Alignment
Purpose: Add CIDOC-CRM and CRMinf ontology alignment guidance
Date: February 15, 2026
"""

import json
from pathlib import Path

# Load existing prompts
prompts_file = Path("facet_agent_system_prompts.json")
with open(prompts_file, 'r', encoding='utf-8') as f:
    prompts_data = json.load(f)

# Semantic enrichment section
SEMANTIC_ENRICHMENT_SECTION = """

SEMANTIC ENRICHMENT & ONTOLOGY ALIGNMENT (STEP 4 - NEW):
ALL entities and claims are automatically enriched with CIDOC-CRM and CRMinf ontology alignments.

THREE-WAY ALIGNMENT:
Every entity/relationship is tagged with:
1. **Wikidata**: QID + Property (P-code) + Value  
2. **CIDOC-CRM**: Class (E5_Event, E21_Person) + Property (P11_had_participant)
3. **CRMinf**: Belief tracking (I2_Belief) + Confidence (J5_holds_to_be)

Available semantic enrichment methods:
- enrich_with_ontology_alignment(entity) - Add CIDOC-CRM classes and properties
- enrich_claim_with_crminf(claim) - Add CRMinf belief tracking
- generate_semantic_triples(qid) - Full QID+Property+Value+CIDOC+CRMinf triples

AUTOMATIC ENRICHMENT (Already Integrated):
When you call bootstrap_from_qid() or generate_claims_from_wikidata(), enrichment happens automatically:

```python
# Bootstrap automatically enriches with CIDOC + CRMinf  
result = agent.bootstrap_from_qid('Q28048')  # Battle of Pharsalus

# Each created node has:
# - wikidata_qid: 'Q28048'
# - cidoc_crm_class: 'E5_Event' (automatically mapped)
# - cidoc_crm_confidence: 'High'

# Each generated claim has:
# - authority_source: 'Wikidata'
# - authority_ids: {source_qid, property, target_qid}
# - crminf_alignment: {
#     crminf_class: 'I2_Belief',  # CRMinf belief node
#     J4_that: 'claim proposition',
#     J5_holds_to_be: 0.90  # confidence
#   }
```

KEY CIDOC-CRM MAPPINGS (Memorize Common Patterns):
**Entities:**
- Q5 (human) → **E21_Person**
- Q1656682 (event) → **E5_Event**  
- Q178561 (battle) → **E5_Event** (event subclass)
- Q82794 (geographic region) → **E53_Place**
- Q43229 (organization) → **E74_Group**

**Relationships:**
- P31 (instance of) → **P2_has_type**
- P276 (location) → **P7_took_place_at**
- P710 (participant) → **P11_had_participant**
- P580 (start time) → **P4_has_time-span** + **P82a_begin_of_the_begin**
- P582 (end time) → **P4_has_time-span** + **P82b_end_of_the_end**

CRMINF BELIEF TRACKING (Claims):
Every Chrystallum Claim maps to **CRMinf I2_Belief**:
- **I2_Belief**: A belief held by an agent (the claim itself)
- **J4_that**: The proposition (claim label)
- **J5_holds_to_be**: Belief value (confidence 0.0-1.0)
- **I5_Inference_Making**: If claim comes from Bayesian update
- **I4_Proposition_Set**: If claim is part of multi-agent debate

This enables:
✅ Museum/archive interoperability (CIDOC-CRM standard)
✅ Argumentation tracking (CRMinf belief structure)
✅ Semantic web compatibility (RDF/OWL export)
✅ Multi-ontology queries (Wikidata OR CIDOC OR Chrystallum)

SEMANTIC TRIPLE GENERATION:
Generate complete semantic triples with full alignment:

```python
# Get all semantic triples for Battle of Pharsalus
triples = agent.generate_semantic_triples(
    entity_qid='Q28048',
    include_cidoc=True,
    include_crminf=True
)

# Each triple contains:
# {
#   'subject': 'Q28048',
#   'subject_label': 'Battle of Pharsalus',
#   'subject_cidoc': 'E5_Event',
#   'property': 'P276',  # location
#   'property_cidoc': 'P7_took_place_at',
#   'value': 'Q240898',  # Pharsalus
#   'value_label': 'Pharsalus',
#   'value_cidoc': 'E53_Place',
#   'crminf_belief': {
#     'class': 'I2_Belief',
#     'confidence': 0.90,
#     'source': 'Wikidata'
#   }
# }
```

WHEN TO USE SEMANTIC TRIPLES:
1. **Claim generation**: Already automatic in bootstrap
2. **Validation**: Compare claims against CIDOC-CRM constraints
3. **Export**: Generate RDF/OWL for museum systems
4. **Query**: "Find all E5_Event nodes with P11_had_participant"

ONTOLOGY-AWARE VALIDATION:
Use CIDOC constraints to validate claims:

```python
# Check if relationship is valid for entity types
entity = agent.fetch_wikidata_entity('Q28048')
entity_enriched = agent.enrich_with_ontology_alignment(entity)

cidoc_class = entity_enriched['ontology_alignment']['cidoc_crm_class']
# → 'E5_Event'

# E5_Event can have:
# - P7_took_place_at (E53_Place)
# - P11_had_participant (E21_Person, E74_Group)
# - P4_has_time-span (E52_Time-Span)
# But NOT:
# - P98_was_born (only for E21_Person)
# - P53_has_former_or_current_location (for physical objects)
```

BENEFITS FOR YOUR FACET:
- **Military**: E5_Event (battles), P11_had_participant (commanders)
- **Political**: E74_Group (organizations), P107_has_current_or_former_member
- **Geographic**: E53_Place, P89_falls_within (administrative containment)
- **Temporal**: E52_Time-Span, P82a/P82b (begin/end of time)
- **Intellectual**: E28_Conceptual_Object, P129_is_about (subject matter)

CROSSWALK REFERENCE:
All mappings loaded from CSV/cidoc_wikidata_mapping_validated.csv (105 mappings)
- Wikidata QID ↔ CIDOC-CRM Class
- Wikidata Property ↔ CIDOC-CRM Property
- CRMinf Classes (I1-I10, J1-J5) for argumentation"""

# Update each facet's system_prompt
updated_count = 0
for facet in prompts_data['facets']:
    old_prompt = facet['system_prompt']
    
    # Only add if not already present
    if "SEMANTIC ENRICHMENT & ONTOLOGY ALIGNMENT" not in old_prompt:
        # Insert after completeness validation
        if "COMPLETENESS VALIDATION (STEP 3.5 - NEW):" in old_prompt:
            facet['system_prompt'] = old_prompt + SEMANTIC_ENRICHMENT_SECTION
            updated_count += 1
            print(f"✓ Updated {facet['label']} ({facet['key']})")
        else:
            print(f"⚠ Skipped {facet['label']} (completeness validation not found)")
    else:
        print(f"⊘ Skipped {facet['label']} (already has semantic enrichment)")

# Update version
prompts_data['version'] = "2026-02-15-step4"

# Write updated prompts back
with open(prompts_file, 'w', encoding='utf-8') as f:
    json.dump(prompts_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Updated {updated_count} facet prompts with semantic enrichment & ontology alignment (Step 4)")
print(f"File: {prompts_file.absolute()}")
print(f"Version: {prompts_data['version']}")
