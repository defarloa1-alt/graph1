#!/usr/bin/env python3
"""
Wire the SFA self-directing workflow into the graph.

Creates SYS_Workflow and SYS_WorkflowStep nodes so that any SFA agent
can discover WHAT TO DO NEXT by walking edges from its Agent node.

Walk: Agent →HAS_WORKFLOW→ SYS_Workflow →HAS_STEP→ SYS_WorkflowStep (ordered)

Each step contains:
  - action: what to do
  - cypher_template: the query to run (with $facet param)
  - assessment_rule: how to interpret the result
  - on_gap: what to do if a gap is found

Idempotent (MERGE everywhere).

Usage:
    python scripts/neo4j/wire_sfa_workflow.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

WORKFLOW = {
    "workflow_id": "SFA_SELF_DIRECTED_WORKFLOW_V1",
    "label": "SFA Self-Directed Workflow",
    "description": (
        "The standard workflow for any Subject Facet Agent. "
        "Walk these steps in order. Each step tells you what to query, "
        "how to assess the result, and what to do about gaps."
    ),
    "version": "1",
}

STEPS = [
    # ── Step 1: ORIENT ──────────────────────────────────────────────
    {
        "step_id": "STEP_1_ORIENT",
        "sequence": 1,
        "label": "Orient",
        "action": "DISCOVER_IDENTITY",
        "description": (
            "Find yourself. Walk from Chrystallum to your Agent node. "
            "Read your agent_id, role, scope_description, and domain_qid. "
            "Identify your assigned facet."
        ),
        "cypher_template": (
            "MATCH (c:Chrystallum)-[:HAS_FACET_ROOT]->(fr)-[:HAS_FACET]->(f:Facet {label: $facet})"
            "<-[:ASSIGNED_TO_FACET]-(a:Agent) "
            "RETURN a.agent_id, a.role, a.scope_description, a.domain_qid, f.label AS facet"
        ),
        "assessment_rule": "You must find exactly one Agent node assigned to your facet. If not found, stop.",
        "on_gap": "HALT - agent node missing, cannot proceed.",
    },
    # ── Step 2: READ RULES ──────────────────────────────────────────
    {
        "step_id": "STEP_2_READ_RULES",
        "sequence": 2,
        "label": "Read Rules",
        "action": "DISCOVER_GOVERNANCE",
        "description": (
            "Read all decision tables, thresholds, and the output contract "
            "that govern your behavior. These are your operating constraints."
        ),
        "cypher_template": (
            "MATCH (a:Agent {agent_id: $agent_id})-[:GOVERNED_BY]->(dt:SYS_DecisionTable) "
            "RETURN dt.table_id, dt.label "
            "UNION ALL "
            "MATCH (a:Agent {agent_id: $agent_id})-[:CONSTRAINED_BY]->(t:SYS_Threshold) "
            "RETURN t.threshold_id AS table_id, t.description AS label "
            "UNION ALL "
            "MATCH (a:Agent {agent_id: $agent_id})-[:USES_OUTPUT_CONTRACT]->(oc:SYS_OutputContract) "
            "RETURN oc.contract_id AS table_id, oc.description AS label"
        ),
        "assessment_rule": (
            "You must find decision tables, at least one threshold, and an output contract. "
            "The confidence ceiling threshold (T_SFA_CONFIDENCE_CEILING) caps all your output confidence scores."
        ),
        "on_gap": "WARN - operating without full governance. Note missing rules in output.",
    },
    # ── Step 3: INVENTORY ───────────────────────────────────────────
    {
        "step_id": "STEP_3_INVENTORY",
        "sequence": 3,
        "label": "Inventory Owned Concepts",
        "action": "COUNT_SUBJECT_CONCEPTS",
        "description": (
            "Count and list all SubjectConcepts assigned to your facet "
            "(primary and secondary). Also count CorpusWork nodes, "
            "FacetRouter rules, and existing Claims in your scope."
        ),
        "cypher_template": (
            "MATCH (sc:SubjectConcept)-[:HAS_PRIMARY_FACET]->(f:Facet {label: $facet}) "
            "RETURN 'primary_sc' AS category, sc.label AS item, count(*) AS ct "
            "UNION ALL "
            "MATCH (sc:SubjectConcept)-[:HAS_SECONDARY_FACET]->(f:Facet {label: $facet}) "
            "RETURN 'secondary_sc' AS category, sc.label AS item, count(*) AS ct "
            "UNION ALL "
            "MATCH (cw:CorpusWork)-[:RELEVANT_TO_FACET]->(f:Facet {label: $facet}) "
            "RETURN 'corpus_works' AS category, 'total' AS item, count(cw) AS ct "
            "UNION ALL "
            "MATCH (fr:SYS_FacetRouter)-[:HAS_PRIMARY_FACET]->(f:Facet {label: $facet}) "
            "RETURN 'facet_routers' AS category, fr.label AS item, count(*) AS ct "
            "UNION ALL "
            "MATCH (c:Claim)-[:PROPOSED_BY]->(a:Agent)-[:ASSIGNED_TO_FACET]->(f:Facet {label: $facet}) "
            "RETURN 'existing_claims' AS category, c.status AS item, count(*) AS ct"
        ),
        "assessment_rule": (
            "Compare primary SubjectConcept count against facet router count and corpus work count. "
            "If primary_sc_count is low relative to router rules, the facet is UNDER-MODELED. "
            "If corpus_works > 10 * primary_sc_count, there is unexploited training material."
        ),
        "on_gap": "Proceed to STEP_4_ASSESS_GAPS with under-modeled flag.",
    },
    # ── Step 4: ASSESS GAPS ─────────────────────────────────────────
    {
        "step_id": "STEP_4_ASSESS_GAPS",
        "sequence": 4,
        "label": "Assess Gaps",
        "action": "IDENTIFY_COVERAGE_GAPS",
        "description": (
            "Compare your routing surface (facet routers) against your "
            "concept ownership (SubjectConcepts). Each router rule implies "
            "a domain area. If no SubjectConcept covers that area, it is a gap. "
            "Also check: do any of your CorpusWork abstracts reference topics "
            "not covered by existing SubjectConcepts?"
        ),
        "cypher_template": (
            "MATCH (fr:SYS_FacetRouter)-[:HAS_PRIMARY_FACET]->(f:Facet {label: $facet}) "
            "RETURN fr.label AS item_label "
            "UNION ALL "
            "MATCH (cw:CorpusWork)-[:RELEVANT_TO_FACET]->(f:Facet {label: $facet}) "
            "RETURN cw.title AS item_label"
        ),
        "assessment_rule": (
            "For each facet router rule and corpus work title, ask: "
            "does an existing primary SubjectConcept cover this topic? "
            "Group uncovered items into candidate concept areas. "
            "Cross-reference with bridge patterns (MAY_TAG) to identify "
            "cross-domain themes that need dedicated concepts."
        ),
        "on_gap": "Proceed to STEP_5_TRAIN with identified gap areas.",
    },
    # ── Step 5: TRAIN ───────────────────────────────────────────────
    {
        "step_id": "STEP_5_TRAIN",
        "sequence": 5,
        "label": "Train on Corpus",
        "action": "EXTRACT_CLAIMS_FROM_CORPUS",
        "description": (
            "Read your CorpusWork nodes. For each work with an abstract, "
            "apply sliding-window claim extraction (2-4 sentence windows, "
            "slide by 1). For each extracted claim: "
            "score all 18 facet weights, tag applicable bridge patterns, "
            "assign role (causal/descriptive/evaluative), "
            "and link to the gap area it addresses."
        ),
        "cypher_template": (
            "MATCH (cw:CorpusWork)-[:RELEVANT_TO_FACET]->(f:Facet {label: $facet}) "
            "WHERE cw.abstract IS NOT NULL "
            "RETURN cw.work_id, cw.title, cw.abstract, cw.year, cw.authors "
            "ORDER BY cw.citation_count DESC"
        ),
        "assessment_rule": (
            "Use sliding-window extraction: 2-4 sentence windows, sliding by 1 sentence. "
            "Merge overlapping claims that share >80%% entity overlap. "
            "Tag every claim with bridge patterns from your MAY_TAG set. "
            "Score pattern density per window: windows with 2+ pattern tags are high priority. "
            "Confidence ceiling: apply T_SFA_CONFIDENCE_CEILING to all output."
        ),
        "on_gap": "If no abstracts available, note as TRAINING_DATA_GAP in output.",
    },
    # ── Step 6: PROPOSE ─────────────────────────────────────────────
    {
        "step_id": "STEP_6_PROPOSE",
        "sequence": 6,
        "label": "Propose Graph Deltas",
        "action": "EMIT_GRAPH_DELTAS",
        "description": (
            "Emit structured graph deltas following the output contract. "
            "For new SubjectConcepts, use op_type CREATE_DSC. "
            "For new claims extracted from corpus, use CREATE_CLAIM. "
            "For cross-facet links discovered, use ADJUST_EDGE. "
            "All output is proposals, not truth. Human curator approves writes."
        ),
        "cypher_template": (
            "MATCH (a:Agent {agent_id: $agent_id})-[:USES_OUTPUT_CONTRACT]->(oc:SYS_OutputContract) "
            "RETURN oc.op_types, oc.required_fields, oc.facet_weight_spec"
        ),
        "assessment_rule": (
            "Every delta must include: op_type, claim.text, claim.subject_concepts, "
            "claim.facet_weights (all 18 scored 0.0-1.0), claim.pattern_tags, "
            "claim.role, claim.confidence (<= T_SFA_CONFIDENCE_CEILING). "
            "CREATE_DSC proposals must justify why the concept is separate from existing SCs."
        ),
        "on_gap": "If no gaps found and no claims extracted, emit confirmation report only.",
    },
    # ── Step 7: REPORT ──────────────────────────────────────────────
    {
        "step_id": "STEP_7_REPORT",
        "sequence": 7,
        "label": "Report to SCA",
        "action": "EMIT_STATUS_REPORT",
        "description": (
            "Summarize your session. Report: concepts owned, gaps identified, "
            "claims extracted, deltas proposed, training data gaps. "
            "This report goes to the SCA for cross-facet coordination."
        ),
        "cypher_template": None,
        "assessment_rule": (
            "Include: facet, agent_id, primary_sc_count, secondary_sc_count, "
            "corpus_works_read, claims_extracted, deltas_proposed, "
            "gap_areas (list), training_data_gaps (list), "
            "cross_facet_proposals (list with target facet)."
        ),
        "on_gap": "Always emit a report, even if no work was done.",
    },
]


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    stats = {"workflow": 0, "steps": 0, "agent_links": 0, "chrystallum_link": 0}

    with driver.session() as session:

        # ── 1. Create the Workflow node ─────────────────────────────
        session.run(
            """
            MERGE (w:SYS_Workflow {workflow_id: $workflow_id})
            ON CREATE SET w.created_at = datetime()
            SET w.label = $label,
                w.description = $description,
                w.version = $version
            """,
            **WORKFLOW,
        )
        print(f"  MERGE Workflow: {WORKFLOW['workflow_id']}")
        stats["workflow"] = 1

        # ── 2. Create WorkflowStep nodes and wire to Workflow ───────
        for step in STEPS:
            params = {
                "workflow_id": WORKFLOW["workflow_id"],
                "step_id": step["step_id"],
                "sequence": step["sequence"],
                "label": step["label"],
                "action": step["action"],
                "description": step["description"],
                "cypher_template": step["cypher_template"] or "",
                "assessment_rule": step["assessment_rule"],
                "on_gap": step["on_gap"],
            }
            session.run(
                """
                MERGE (s:SYS_WorkflowStep {step_id: $step_id})
                ON CREATE SET s.created_at = datetime()
                SET s.sequence = $sequence,
                    s.label = $label,
                    s.action = $action,
                    s.description = $description,
                    s.cypher_template = $cypher_template,
                    s.assessment_rule = $assessment_rule,
                    s.on_gap = $on_gap

                WITH s
                MATCH (w:SYS_Workflow {workflow_id: $workflow_id})
                MERGE (w)-[:HAS_STEP]->(s)
                """,
                **params,
            )
            print(f"  MERGE Step {step['sequence']}: {step['label']} ({step['action']})")
            stats["steps"] += 1

        # ── 3. Wire step ordering (NEXT_STEP edges) ────────────────
        for i in range(len(STEPS) - 1):
            session.run(
                """
                MATCH (s1:SYS_WorkflowStep {step_id: $from_id})
                MATCH (s2:SYS_WorkflowStep {step_id: $to_id})
                MERGE (s1)-[:NEXT_STEP]->(s2)
                """,
                from_id=STEPS[i]["step_id"],
                to_id=STEPS[i + 1]["step_id"],
            )
        print(f"  NEXT_STEP chain: {len(STEPS) - 1} edges")

        # ── 4. Wire all SFA agents to the workflow ──────────────────
        result = session.run(
            """
            MATCH (a:Agent) WHERE a.role = 'subject_facet_agent'
            MATCH (w:SYS_Workflow {workflow_id: $workflow_id})
            MERGE (a)-[:HAS_WORKFLOW]->(w)
            RETURN count(*) AS cnt
            """,
            workflow_id=WORKFLOW["workflow_id"],
        )
        stats["agent_links"] = result.single()["cnt"]
        print(f"  HAS_WORKFLOW: {stats['agent_links']} agents linked")

        # ── 5. Wire Chrystallum to Workflow for discoverability ─────
        session.run(
            """
            MATCH (c:Chrystallum)
            MATCH (w:SYS_Workflow {workflow_id: $workflow_id})
            MERGE (c)-[:HAS_WORKFLOW]->(w)
            """,
            workflow_id=WORKFLOW["workflow_id"],
        )
        stats["chrystallum_link"] = 1
        print(f"  Chrystallum HAS_WORKFLOW")

    driver.close()

    print("\n-- Summary --")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"\nDone. {stats['steps']}-step workflow wired.")
    print("Walk: Agent ->HAS_WORKFLOW-> SYS_Workflow ->HAS_STEP-> SYS_WorkflowStep (ordered by sequence)")
    print("      SYS_WorkflowStep ->NEXT_STEP-> SYS_WorkflowStep (chain)")


if __name__ == "__main__":
    main()
