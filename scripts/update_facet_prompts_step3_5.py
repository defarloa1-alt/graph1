#!/usr/bin/env python3
"""
Update facet agent system prompts with Step 3.5: Completeness Validation
Purpose: Add property pattern validation guidance to federation discovery
Date: February 15, 2026
"""

import json
from pathlib import Path

# Load existing prompts
prompts_file = Path("facet_agent_system_prompts.json")
with open(prompts_file, 'r', encoding='utf-8') as f:
    prompts_data = json.load(f)

# Completeness validation section to add after federation discovery
COMPLETENESS_VALIDATION_SECTION = """

COMPLETENESS VALIDATION (STEP 3.5 - NEW):
Before bootstrapping from Wikidata, validate entity quality using empirical property patterns.

Based on analysis of 841 entities across 12 historical types, we know:
- **Battles (Q178561):** 91% have P276 (location), 88% have P361 (part of larger conflict)
- **Humans (Q5):** 100% have P19/P21/P27 (birthplace/sex/citizenship)
- **Cities (Q515):** 100% have P17/P625 (country/coordinates)
- **Countries (Q6256):** 100% have P1082 (population)

Available validation method:
- validate_entity_completeness(qid, entity_type=None) - Returns completeness score (0.0-1.0)

VALIDATION WORKFLOW:
```python
# Before bootstrap, check entity quality
validation = agent.validate_entity_completeness('Q28048')  # Battle of Pharsalus

print(f"Completeness: {validation['completeness_score']:.1%}")
print(f"Type: {validation['entity_type_label']}")
print(f"Recommendation: {validation['recommendation']}")

if validation['missing_mandatory']:
    print(f"Missing critical: {validation['missing_mandatory']}")
    # Decision: flag for manual review or skip bootstrap

if validation['completeness_score'] >= 0.8:
    # High quality - safe to bootstrap
    result = agent.bootstrap_from_qid('Q28048')
elif validation['completeness_score'] >= 0.6:
    # Moderate quality - bootstrap but review claims
    result = agent.bootstrap_from_qid('Q28048', auto_submit=False)
else:
    # Low quality - manual creation recommended
    print("⚠ Entity incomplete, skipping automatic bootstrap")
```

AUTOMATIC VALIDATION (default behavior):
bootstrap_from_qid() now validates by default:
```python
# Validation happens automatically with min_completeness=0.6
result = agent.bootstrap_from_qid(
    qid='Q28048',
    depth=1,
    validate_completeness=True,  # Default
    min_completeness=0.6         # Threshold
)

if result['status'] == 'rejected':
    print(f"Rejected: {result['reason']}")
    print(f"Completeness: {result['validation']['completeness_score']:.1%}")
```

COMPLETENESS SCORING:
- **Score = (mandatory_coverage × 0.7) + (common_coverage × 0.3)**
- **Mandatory properties:** ≥85% coverage in sample (e.g., P31 for all entities)
- **Common properties:** 50-85% coverage (e.g., P276 location for battles)

Recommendations by score:
- **≥0.8:** bootstrap - Entity is well-formed, proceed confidently
- **0.6-0.8:** manual_review - Bootstrap but review generated claims
- **<0.6:** reject - Entity too incomplete, manual creation recommended

QUALITY METRICS:
After bootstrap, audit quality:
```python
# Get validation for all bootstrapped entities
context = agent.get_session_context()
for node in context['subgraph_sample']['nodes']:
    if qid := node.get('wikidata_qid'):
        validation = agent.validate_entity_completeness(qid)
        if validation['completeness_score'] < 0.7:
            print(f"⚠ Low quality: {node['label']} ({validation['completeness_score']:.1%})")
```

BENEFITS:
- ✅ Reject incomplete Wikidata entities before wasting effort
- ✅ Focus on high-quality sources for automatic discovery
- ✅ Prioritize claims from mandatory properties (higher confidence)
- ✅ Provide quality metrics for audit and debugging"""

# Update each facet's system_prompt
updated_count = 0
for facet in prompts_data['facets']:
    old_prompt = facet['system_prompt']
    
    # Only add if not already present
    if "COMPLETENESS VALIDATION" not in old_prompt:
        # Insert after federation discovery  (STEP 3 - NEW)
        if "FEDERATION-DRIVEN DISCOVERY (STEP 3 - NEW):" in old_prompt:
            facet['system_prompt'] = old_prompt + COMPLETENESS_VALIDATION_SECTION
            updated_count += 1
            print(f"✓ Updated {facet['label']} ({facet['key']})")
        else:
            print(f"⚠ Skipped {facet['label']} (federation discovery not found - has Step 3?)")
    else:
        print(f"⊘ Skipped {facet['label']} (already has completeness validation)")

# Update version
prompts_data['version'] = "2026-02-15-step3.5"

# Write updated prompts back
with open(prompts_file, 'w', encoding='utf-8') as f:
    json.dump(prompts_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Updated {updated_count} facet prompts with completeness validation guidance (Step 3.5)")
print(f"File: {prompts_file.absolute()}")
print(f"Version: {prompts_data['version']}")
