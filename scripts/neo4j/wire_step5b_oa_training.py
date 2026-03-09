#!/usr/bin/env python3
"""
Wire Step 5b (OA External Training) into the SFA workflow.

Inserts between Step 5 (Train on Corpus) and Step 6 (Propose Graph Deltas).
When an SFA hits a TRAINING_DATA_GAP in Step 5, Step 5b authorizes a
controlled web pass over open-access sources with lower confidence.

Also adds:
- SYS_Threshold for external OA confidence cap
- SYS_OASourcePack node for Military facet with curated OA sources

Idempotent (MERGE everywhere).

Usage:
    python scripts/neo4j/wire_step5b_oa_training.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

STEP_5B = {
    "step_id": "STEP_5B_OA_TRAINING",
    "sequence": 5.5,
    "label": "Train on Open-Access Sources",
    "action": "EXTRACT_CLAIMS_FROM_OA_SOURCES",
    "description": (
        "TRIGGERED ONLY when Step 5 reports TRAINING_DATA_GAP. "
        "Query your facet's OA Source Pack for curated open-access texts. "
        "Apply the same sliding-window extraction as Step 5, but mark all "
        "claims with provenance_type='external_oa' and apply the lower "
        "T_SFA_OA_CONFIDENCE_CEILING. Claims from OA sources are upgradeable "
        "when corroborated by multiple sources or by internal corpus evidence."
    ),
    "cypher_template": (
        "MATCH (a:Agent {agent_id: $agent_id})-[:ASSIGNED_TO_FACET]->(f:Facet) "
        "MATCH (sp:SYS_OASourcePack)-[:COVERS_FACET]->(f) "
        "RETURN sp.pack_id, sp.sources, sp.scope_note, sp.priority_texts"
    ),
    "assessment_rule": (
        "Apply sliding-window extraction (2-4 sentences, slide by 1) to OA texts. "
        "All extracted claims must carry provenance_type='external_oa' and "
        "source_url. Confidence cap: T_SFA_OA_CONFIDENCE_CEILING (0.70). "
        "Claims corroborated by 2+ independent OA sources may be upgraded to "
        "T_SFA_CONFIDENCE_CEILING (0.85) with corroboration_count noted. "
        "Prefer extracting from primary ancient sources (Polybius, Livy, Appian) "
        "over secondary modern commentary."
    ),
    "on_gap": (
        "If no OA Source Pack exists for your facet, note as OA_PACK_MISSING "
        "and proceed to Step 6 with internal claims only."
    ),
}

OA_THRESHOLD = {
    "threshold_id": "T_SFA_OA_CONFIDENCE_CEILING",
    "value": 0.70,
    "description": (
        "Maximum confidence for claims extracted from external open-access sources. "
        "Lower than internal corpus ceiling (0.85) because OA texts lack curation. "
        "Upgradeable to 0.85 when corroborated by 2+ independent sources."
    ),
}

MILITARY_OA_PACK = {
    "pack_id": "OA_PACK_MILITARY_RR",
    "label": "Military Roman Republic OA Source Pack",
    "facet": "Military",
    "scope_note": (
        "Curated open-access sources for the Roman Republic military domain. "
        "Prioritizes public-domain ancient primary sources available through "
        "LacusCurtius, Perseus Digital Library, and Fordham Ancient History Sourcebook."
    ),
    "sources": (
        "LacusCurtius (penelope.uchicago.edu) - Polybius, Livy, Appian, Frontinus; "
        "Perseus Digital Library (perseus.tufts.edu) - Livy Ab Urbe Condita, Appian; "
        "Fordham Ancient History Sourcebook (sourcebooks.fordham.edu) - public-domain excerpts; "
        "Open Content Alliance via Internet Archive - classical military texts"
    ),
    "priority_texts": (
        "Polybius Histories Book 6 (army structure, camp layout, command); "
        "Polybius Histories Books 3,10,11 (Cannae, New Carthage, Punic War campaigns); "
        "Livy Ab Urbe Condita Books 21-30 (Second Punic War); "
        "Livy Ab Urbe Condita Books 31-45 (Eastern campaigns); "
        "Appian Hannibalic War; "
        "Appian Civil Wars Books 1-5; "
        "Frontinus Strategemata (military stratagems); "
        "Vegetius Epitoma rei militaris (military organization, though late)"
    ),
    "extraction_guidance": (
        "For Polybius Book 6: extract claims about legion structure, maniple formation, "
        "camp layout, officer roles, military discipline, and equipment. "
        "For campaign narratives: extract claims about command decisions, troop movements, "
        "battle tactics, siege operations, and casualty/outcome data. "
        "For Appian Civil Wars: extract claims about military-political intersection, "
        "army loyalty, veteran settlement, and command rivalry."
    ),
}


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:

        # ── 1. Create Step 5b node ──────────────────────────────────
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
            MATCH (w:SYS_Workflow {workflow_id: 'SFA_SELF_DIRECTED_WORKFLOW_V1'})
            MERGE (w)-[:HAS_STEP]->(s)
            """,
            **STEP_5B,
        )
        print("  MERGE Step 5b: Train on OA Sources")

        # ── 2. Rewire NEXT_STEP chain: 5 -> 5b -> 6 ───────────────
        # Remove old 5 -> 6 edge
        session.run(
            """
            MATCH (s5:SYS_WorkflowStep {step_id: 'STEP_5_TRAIN'})
                  -[r:NEXT_STEP]->
                  (s6:SYS_WorkflowStep {step_id: 'STEP_6_PROPOSE'})
            DELETE r
            """
        )
        # Wire 5 -> 5b
        session.run(
            """
            MATCH (s5:SYS_WorkflowStep {step_id: 'STEP_5_TRAIN'})
            MATCH (s5b:SYS_WorkflowStep {step_id: 'STEP_5B_OA_TRAINING'})
            MERGE (s5)-[:NEXT_STEP]->(s5b)
            """
        )
        # Wire 5b -> 6
        session.run(
            """
            MATCH (s5b:SYS_WorkflowStep {step_id: 'STEP_5B_OA_TRAINING'})
            MATCH (s6:SYS_WorkflowStep {step_id: 'STEP_6_PROPOSE'})
            MERGE (s5b)-[:NEXT_STEP]->(s6)
            """
        )
        print("  Rewired chain: STEP_5 -> STEP_5B -> STEP_6")

        # ── 3. Create OA confidence threshold ──────────────────────
        session.run(
            """
            MERGE (th:SYS_Threshold {threshold_id: $threshold_id})
            ON CREATE SET th.created_at = datetime()
            SET th.value = $value,
                th.description = $description
            """,
            **OA_THRESHOLD,
        )
        # Wire to all SFA agents
        result = session.run(
            """
            MATCH (a:Agent) WHERE a.role = 'subject_facet_agent'
            MATCH (th:SYS_Threshold {threshold_id: $threshold_id})
            MERGE (a)-[:CONSTRAINED_BY]->(th)
            RETURN count(*) AS cnt
            """,
            threshold_id=OA_THRESHOLD["threshold_id"],
        )
        print(f"  CONSTRAINED_BY T_SFA_OA_CONFIDENCE_CEILING ({result.single()['cnt']} agents)")

        # Wire to Chrystallum
        session.run(
            """
            MATCH (c:Chrystallum)
            MATCH (th:SYS_Threshold {threshold_id: $threshold_id})
            MERGE (c)-[:HAS_THRESHOLD]->(th)
            """,
            threshold_id=OA_THRESHOLD["threshold_id"],
        )

        # ── 4. Create Military OA Source Pack ──────────────────────
        session.run(
            """
            MERGE (sp:SYS_OASourcePack {pack_id: $pack_id})
            ON CREATE SET sp.created_at = datetime()
            SET sp.label = $label,
                sp.scope_note = $scope_note,
                sp.sources = $sources,
                sp.priority_texts = $priority_texts,
                sp.extraction_guidance = $extraction_guidance
            """,
            pack_id=MILITARY_OA_PACK["pack_id"],
            label=MILITARY_OA_PACK["label"],
            scope_note=MILITARY_OA_PACK["scope_note"],
            sources=MILITARY_OA_PACK["sources"],
            priority_texts=MILITARY_OA_PACK["priority_texts"],
            extraction_guidance=MILITARY_OA_PACK["extraction_guidance"],
        )
        # Wire to Military facet
        session.run(
            """
            MATCH (sp:SYS_OASourcePack {pack_id: $pack_id})
            MATCH (f:Facet {label: $facet})
            MERGE (sp)-[:COVERS_FACET]->(f)
            """,
            pack_id=MILITARY_OA_PACK["pack_id"],
            facet=MILITARY_OA_PACK["facet"],
        )
        print(f"  MERGE OA Source Pack: {MILITARY_OA_PACK['pack_id']}")

    driver.close()
    print("\nDone. Step 5b wired into workflow.")
    print("Chain: ... -> STEP_5_TRAIN -> STEP_5B_OA_TRAINING -> STEP_6_PROPOSE -> ...")


if __name__ == "__main__":
    main()
