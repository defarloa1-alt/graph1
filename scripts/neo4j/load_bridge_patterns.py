#!/usr/bin/env python3
"""
Load 15 cross-domain bridge pattern tags as RepertoirePattern nodes.

These patterns enable cross-domain jumping (e.g. Roman senator <-> mollusk)
by tagging claims with abstract relational patterns that recur across domains.

Source: Perplexity conversation "how would my SFA agents learn" (2026-03).

Usage:
    python scripts/neo4j/load_bridge_patterns.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

BRIDGE_PATTERNS = [
    {
        "id": "RP_CENTER_PERIPHERY_ENFRANCHISEMENT",
        "label": "Center-periphery enfranchisement",
        "scope_description": "A center depends on a periphery but withholds full membership/rights.",
        "category": "power_and_scope",
        "mechanisms": ["M_BROKERAGE", "M_ESCALATION"],
    },
    {
        "id": "RP_CENTER_PERIPHERY_EXTRACTION",
        "label": "Center-periphery extraction",
        "scope_description": "A center extracts resources (tax, labor, biomass) from a periphery with asymmetric benefit.",
        "category": "power_and_scope",
        "mechanisms": ["M_ESCALATION"],
    },
    {
        "id": "RP_INSTITUTIONAL_BLINDNESS_TO_EXTERNALITIES",
        "label": "Institutional blindness to externalities",
        "scope_description": "Decision rules ignore harms to actors not represented in the institution (non-citizens, non-humans, future generations).",
        "category": "power_and_scope",
        "mechanisms": ["M_FRAME_ALIGNMENT"],
    },
    {
        "id": "RP_CLIENT_PATRON_DEPENDENCE",
        "label": "Client-patron dependence",
        "scope_description": "Weaker actors depend on stronger patrons for protection or material support, creating loyalty obligations.",
        "category": "power_and_scope",
        "mechanisms": ["M_BROKERAGE"],
    },
    {
        "id": "RP_ARMS_LENGTH_INTERMEDIATION",
        "label": "Arms-length intermediation",
        "scope_description": "A powerful actor uses intermediaries (tax-farmers, contractors, concessionaires) to do extractive or risky work.",
        "category": "power_and_scope",
        "mechanisms": ["M_BROKERAGE", "M_DIFFUSION"],
    },
    {
        "id": "RP_STATUS_QUO_DEFENSE_AGAINST_REFORM",
        "label": "Status-quo defense against reform",
        "scope_description": "Incumbent elites deploy procedural or rhetorical tools to block structural change.",
        "category": "conflict_and_change",
        "mechanisms": ["M_FRAME_ALIGNMENT", "M_POLICING_RESPONSE"],
    },
    {
        "id": "RP_REVOLT_FOR_RECOGNITION",
        "label": "Revolt for recognition",
        "scope_description": "Subordinate actors mobilize (politically or militarily) to demand inclusion or rights.",
        "category": "conflict_and_change",
        "mechanisms": ["M_ESCALATION", "M_NATIONAL_ACTIVATION"],
    },
    {
        "id": "RP_CONCESSION_AFTER_THRESHOLD_CONFLICT",
        "label": "Concession after threshold conflict",
        "scope_description": "Meaningful rights or protections are only granted after severe conflict or crisis.",
        "category": "conflict_and_change",
        "mechanisms": ["M_ESCALATION", "M_BROKERAGE"],
    },
    {
        "id": "RP_MILITARIZED_POLITICS_CONTROL",
        "label": "Militarized politics/control",
        "scope_description": "Coercive forces become decisive arbiters of political outcomes (armies deciding who governs).",
        "category": "conflict_and_change",
        "mechanisms": ["M_ESCALATION", "M_POLICING_RESPONSE"],
    },
    {
        "id": "RP_EXPERT_MEDIATED_KNOWLEDGE",
        "label": "Expert-mediated knowledge",
        "scope_description": "Decision-makers rely on specialized experts or observers to interpret complex systems (ecologists, augurs, engineers).",
        "category": "knowledge_classification_metaphor",
        "mechanisms": ["M_BROKERAGE", "M_FRAME_ALIGNMENT"],
    },
    {
        "id": "RP_INDICATOR_SPECIES_OR_ACTOR",
        "label": "Indicator species or actor",
        "scope_description": "A non-central entity's condition is used as a proxy for system health (mollusks as water-quality indicators, smallholders as social-health indicators).",
        "category": "knowledge_classification_metaphor",
        "mechanisms": ["M_DIFFUSION"],
    },
    {
        "id": "RP_NATURALIZATION_OF_HIERARCHY",
        "label": "Naturalization of hierarchy",
        "scope_description": "Social or political hierarchies are justified by appeal to 'natural' orders or biological metaphors.",
        "category": "knowledge_classification_metaphor",
        "mechanisms": ["M_FRAME_ALIGNMENT"],
    },
    {
        "id": "RP_RHETORICAL_OTHERING",
        "label": "Rhetorical othering",
        "scope_description": "Language frames a group or entity as outside the moral/community boundary ('allies', 'barbarians', 'pests').",
        "category": "knowledge_classification_metaphor",
        "mechanisms": ["M_FRAME_ALIGNMENT", "M_NATIONAL_ACTIVATION"],
    },
    {
        "id": "RP_RESOURCE_CONVERSION_CHAIN",
        "label": "Resource conversion chain",
        "scope_description": "A clear chain links extraction -> processing -> consumption -> waste, potentially across domains (timber -> ships -> trade; dredging -> silt -> mollusk habitat).",
        "category": "economy_and_environment",
        "mechanisms": ["M_DIFFUSION", "M_ESCALATION"],
    },
    {
        "id": "RP_REGULATION_LAG_BEHIND_IMPACT",
        "label": "Regulation lag behind impact",
        "scope_description": "Harm grows faster than institutional response (slow laws vs fast ecological or social damage).",
        "category": "economy_and_environment",
        "mechanisms": ["M_ESCALATION"],
    },
]


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    created = 0
    mech_linked = 0

    with driver.session() as session:
        for bp in BRIDGE_PATTERNS:
            result = session.run(
                """
                MERGE (rp:RepertoirePattern {id: $id})
                ON CREATE SET rp.created_at = datetime()
                SET rp.label = $label,
                    rp.scope_description = $scope_description,
                    rp.category = $category,
                    rp.pattern_type = 'bridge',
                    rp.status = 'active'
                RETURN rp.id AS id, rp.label AS label
                """,
                id=bp["id"],
                label=bp["label"],
                scope_description=bp["scope_description"],
                category=bp["category"],
            )
            rec = result.single()
            print(f"  MERGE {rec['id']}: {rec['label']}")
            created += 1

            for mid in bp.get("mechanisms", []):
                session.run(
                    """
                    MATCH (rp:RepertoirePattern {id: $rp_id})
                    MATCH (m:Mechanism {id: $mech_id})
                    MERGE (rp)-[:USES_MECHANISM]->(m)
                    """,
                    rp_id=bp["id"],
                    mech_id=mid,
                )
                mech_linked += 1

    driver.close()
    print(f"\nDone: {created} bridge patterns merged, {mech_linked} mechanism links created.")


if __name__ == "__main__":
    main()
