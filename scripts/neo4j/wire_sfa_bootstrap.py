#!/usr/bin/env python3
"""
Wire the self-bootstrap subgraph so any SFA agent can discover its full
context by walking edges from the Chrystallum root node.

Walk: Chrystallum → FacetRoot → Facet → Agent → {DecisionTables, Thresholds,
      OutputContract, BridgePatterns, SubjectConcepts}

This script is idempotent (MERGE everywhere).

Usage:
    python scripts/neo4j/wire_sfa_bootstrap.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

# ── Decision tables that govern all SFA agents ──────────────────────────────
SFA_DECISION_TABLES = [
    "D8_DETERMINE_SFA_facet_assignment",
    "D9_DETERMINE_SFA_constitution_layer",
    "D10_DETERMINE_claim_promotion_eligibility",
    "D11_DETERMINE_claim_dispute_trigger",
    "D12_DETERMINE_SubjectConcept_split_trigger",
    "D13_DETERMINE_SFA_drift_alert",
    "D14_DETERMINE_entity_resolution_acceptance",
]

# ── Thresholds that constrain SFA behavior ──────────────────────────────────
SFA_THRESHOLDS = [
    {
        "threshold_id": "T_SFA_CONFIDENCE_CEILING",
        "value": 0.85,
        "description": "Maximum confidence an SFA agent may assign to its own proposals. Agent output is claims, not ground truth.",
    },
    {
        "threshold_id": "T_SC_CHILD_OVERLOAD",
        "value": 12,
        "description": "Split SubjectConcept when child count exceeds this value (D12).",
    },
    {
        "threshold_id": "T_SC_CROSSLINK_RATIO",
        "value": 0.3,
        "description": "Split SubjectConcept when cross-facet link ratio exceeds 30% (D12).",
    },
]

# ── Agent node enrichment ───────────────────────────────────────────────────
# All 4 SFA agents get agent_id + role. Military gets scope detail.
AGENT_ENRICHMENTS = [
    {
        "name": "SFA_MILITARY_RR",
        "agent_id": "SFA_MILITARY_RR",
        "role": "subject_facet_agent",
        "scope_description": (
            "Military facet specialist for the Roman Republic domain (Q17167). "
            "Scope: armies, campaigns, command structures (imperium, promagistracies), "
            "military technology, fortifications, naval operations, military law, "
            "and the intersection of military power with political institutions."
        ),
        "domain_qid": "Q17167",
        "domain_label": "Roman Republic",
    },
    {
        "name": "SFA_POLITICAL_RR",
        "agent_id": "SFA_POLITICAL_RR",
        "role": "subject_facet_agent",
        "scope_description": (
            "Political facet specialist for the Roman Republic domain (Q17167). "
            "Scope: magistracies, senate, assemblies, constitutional law, "
            "electoral systems, and political institutions."
        ),
        "domain_qid": "Q17167",
        "domain_label": "Roman Republic",
    },
    {
        "name": "SFA_SOCIAL_RR",
        "agent_id": "SFA_SOCIAL_RR",
        "role": "subject_facet_agent",
        "scope_description": (
            "Social facet specialist for the Roman Republic domain (Q17167). "
            "Scope: social structure, patron-client relations, slavery, "
            "family/kinship, class relations, and social customs."
        ),
        "domain_qid": "Q17167",
        "domain_label": "Roman Republic",
    },
]

# ── Output contract: the graph delta schema ─────────────────────────────────
OUTPUT_CONTRACT = {
    "contract_id": "SFA_OUTPUT_CONTRACT_V1",
    "label": "SFA Graph Delta Output Contract",
    "description": (
        "All SFA output must be structured as graph_deltas. "
        "Each delta has op_type, claim, and optional edge. "
        "Proposals are claims (not truth) with confidence <= T_SFA_CONFIDENCE_CEILING."
    ),
    "op_types": "CREATE_CLAIM, UPDATE_CLAIM, ADJUST_EDGE, CREATE_DSC",
    "required_fields": (
        "op_type, claim.text, claim.subject_concepts, claim.facet_weights (all 18), "
        "claim.pattern_tags, claim.role (causal|descriptive|evaluative), claim.confidence"
    ),
    "facet_weight_spec": (
        "Score all 18 facets 0.0-1.0: archaeological, artistic, biographic, "
        "communication, cultural, demographic, diplomatic, economic, environmental, "
        "geographic, intellectual, linguistic, military, political, religious, "
        "scientific, social, technological"
    ),
}

# ── 18 canonical facet IDs (for facet_weight_spec reference) ────────────────
FACETS_18 = [
    "archaeological", "artistic", "biographic", "communication", "cultural",
    "demographic", "diplomatic", "economic", "environmental", "geographic",
    "intellectual", "linguistic", "military", "political", "religious",
    "scientific", "social", "technological",
]


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    stats = {
        "agent_enriched": 0,
        "governed_by": 0,
        "constrained_by": 0,
        "may_tag": 0,
        "output_contract": 0,
        "chrystallum_bridge": 0,
    }

    with driver.session() as session:

        # ── 1. Enrich Agent nodes ───────────────────────────────────────
        for ae in AGENT_ENRICHMENTS:
            session.run(
                """
                MATCH (a:Agent {name: $name})
                SET a.agent_id = $agent_id,
                    a.role = $role,
                    a.scope_description = $scope_description,
                    a.domain_qid = $domain_qid,
                    a.domain_label = $domain_label
                """,
                **ae,
            )
            print(f"  ENRICH Agent: {ae['name']}")
            stats["agent_enriched"] += 1

        # ── 2. Wire Agent → Decision Tables (GOVERNED_BY) ──────────────
        for dt_id in SFA_DECISION_TABLES:
            result = session.run(
                """
                MATCH (a:Agent) WHERE a.role = 'subject_facet_agent'
                MATCH (dt:SYS_DecisionTable {table_id: $dt_id})
                MERGE (a)-[:GOVERNED_BY]->(dt)
                RETURN count(*) as cnt
                """,
                dt_id=dt_id,
            )
            cnt = result.single()["cnt"]
            stats["governed_by"] += cnt
            print(f"  GOVERNED_BY → {dt_id} ({cnt} agents)")

        # ── 3. Wire Agent → Thresholds (CONSTRAINED_BY) ────────────────
        for t in SFA_THRESHOLDS:
            session.run(
                """
                MERGE (th:SYS_Threshold {threshold_id: $threshold_id})
                ON CREATE SET th.created_at = datetime()
                SET th.value = $value,
                    th.description = $description
                """,
                **t,
            )
            result = session.run(
                """
                MATCH (a:Agent) WHERE a.role = 'subject_facet_agent'
                MATCH (th:SYS_Threshold {threshold_id: $threshold_id})
                MERGE (a)-[:CONSTRAINED_BY]->(th)
                RETURN count(*) as cnt
                """,
                threshold_id=t["threshold_id"],
            )
            cnt = result.single()["cnt"]
            stats["constrained_by"] += cnt
            print(f"  CONSTRAINED_BY → {t['threshold_id']} ({cnt} agents)")

        # ── 4. Create OutputContract node and wire to agents ────────────
        session.run(
            """
            MERGE (oc:SYS_OutputContract {contract_id: $contract_id})
            ON CREATE SET oc.created_at = datetime()
            SET oc.label = $label,
                oc.description = $description,
                oc.op_types = $op_types,
                oc.required_fields = $required_fields,
                oc.facet_weight_spec = $facet_weight_spec
            """,
            **OUTPUT_CONTRACT,
        )
        result = session.run(
            """
            MATCH (a:Agent) WHERE a.role = 'subject_facet_agent'
            MATCH (oc:SYS_OutputContract {contract_id: $contract_id})
            MERGE (a)-[:USES_OUTPUT_CONTRACT]->(oc)
            RETURN count(*) as cnt
            """,
            contract_id=OUTPUT_CONTRACT["contract_id"],
        )
        stats["output_contract"] = result.single()["cnt"]
        print(f"  USES_OUTPUT_CONTRACT → {OUTPUT_CONTRACT['contract_id']} ({stats['output_contract']} agents)")

        # ── 5. Wire Agent → Bridge Patterns (MAY_TAG) ──────────────────
        result = session.run(
            """
            MATCH (a:Agent) WHERE a.role = 'subject_facet_agent'
            MATCH (rp:RepertoirePattern) WHERE rp.pattern_type = 'bridge'
            MERGE (a)-[:MAY_TAG]->(rp)
            RETURN count(*) as cnt
            """,
        )
        stats["may_tag"] = result.single()["cnt"]
        print(f"  MAY_TAG → bridge patterns ({stats['may_tag']} edges)")

        # ── 6. Wire Chrystallum → RepertoirePatterns ────────────────────
        #    Chrystallum → HAS_REPERTOIRE → Framework {PRH} already exists.
        #    Add: Chrystallum → HAS_BRIDGE_VOCABULARY edge to a container,
        #    or wire directly. Direct is simpler and discoverable.
        result = session.run(
            """
            MATCH (c:Chrystallum)
            MATCH (rp:RepertoirePattern) WHERE rp.pattern_type = 'bridge'
            MERGE (c)-[:HAS_BRIDGE_PATTERN]->(rp)
            RETURN count(*) as cnt
            """,
        )
        stats["chrystallum_bridge"] = result.single()["cnt"]
        print(f"  Chrystallum HAS_BRIDGE_PATTERN ({stats['chrystallum_bridge']} edges)")

        # ── 7. Wire Chrystallum → OutputContract ────────────────────────
        session.run(
            """
            MATCH (c:Chrystallum)
            MATCH (oc:SYS_OutputContract {contract_id: $contract_id})
            MERGE (c)-[:HAS_OUTPUT_CONTRACT]->(oc)
            """,
            contract_id=OUTPUT_CONTRACT["contract_id"],
        )
        print(f"  Chrystallum HAS_OUTPUT_CONTRACT")

        # ── 8. Wire Chrystallum → SYS_Threshold (system-wide) ──────────
        result = session.run(
            """
            MATCH (c:Chrystallum)
            MATCH (th:SYS_Threshold) WHERE th.threshold_id IS NOT NULL
            MERGE (c)-[:HAS_THRESHOLD]->(th)
            RETURN count(*) as cnt
            """,
        )
        print(f"  Chrystallum HAS_THRESHOLD ({result.single()['cnt']} edges)")

        # ── 9. Wire Chrystallum → Decision Tables ───────────────────────
        result = session.run(
            """
            MATCH (c:Chrystallum)
            MATCH (dt:SYS_DecisionTable)
            MERGE (c)-[:HAS_DECISION_TABLE]->(dt)
            RETURN count(*) as cnt
            """,
        )
        print(f"  Chrystallum HAS_DECISION_TABLE ({result.single()['cnt']} edges)")

    driver.close()

    print("\n── Summary ──")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print("\nDone. Full bootstrap walk now available:")
    print("  Chrystallum → FacetRoot → Facet → Agent → {DecisionTables, Thresholds, OutputContract, BridgePatterns}")


if __name__ == "__main__":
    main()
