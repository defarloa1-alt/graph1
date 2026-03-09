"""
Wire missing edges from Chrystallum root node to all orphaned registries/system nodes.

Gaps identified 2026-03-07:
- EntityRoot, SYS_SubjectConceptRoot, SYS_OnboardingProtocol, SYS_ADR,
  SYS_Policy, SYS_AgentType, Agent, SYS_ClaimStatus, SYS_ConfidenceTier,
  SYS_AuthorityTier, SYS_ValidationRule, SYS_CurationDecision,
  remaining SYS_Threshold (only 4 of 31 linked)

All MERGE — idempotent, safe to re-run.
"""

from neo4j import GraphDatabase
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD


QUERIES = [
    # --- Direct registry links ---
    (
        "Chrystallum -> EntityRoot",
        """
        MATCH (c:Chrystallum), (er:EntityRoot)
        MERGE (c)-[:HAS_ENTITY_ROOT]->(er)
        RETURN count(*) AS wired
        """,
    ),
    (
        "Chrystallum -> SYS_SubjectConceptRoot",
        """
        MATCH (c:Chrystallum), (sc:SYS_SubjectConceptRoot)
        MERGE (c)-[:HAS_SUBJECT_CONCEPT_ROOT]->(sc)
        RETURN count(*) AS wired
        """,
    ),
    (
        "Chrystallum -> SYS_OnboardingProtocol",
        """
        MATCH (c:Chrystallum), (op:SYS_OnboardingProtocol)
        MERGE (c)-[:HAS_ONBOARDING]->(op)
        RETURN count(*) AS wired
        """,
    ),
    # --- Bulk system-node links ---
    (
        "Chrystallum -> all SYS_ADR",
        """
        MATCH (c:Chrystallum), (a:SYS_ADR)
        MERGE (c)-[:HAS_ADR]->(a)
        RETURN count(*) AS wired
        """,
    ),
    (
        "Chrystallum -> all SYS_Policy",
        """
        MATCH (c:Chrystallum), (p:SYS_Policy)
        MERGE (c)-[:HAS_POLICY]->(p)
        RETURN count(*) AS wired
        """,
    ),
    (
        "Chrystallum -> all SYS_AgentType",
        """
        MATCH (c:Chrystallum), (at:SYS_AgentType)
        MERGE (c)-[:HAS_AGENT_TYPE]->(at)
        RETURN count(*) AS wired
        """,
    ),
    (
        "Chrystallum -> all Agent",
        """
        MATCH (c:Chrystallum), (a:Agent)
        MERGE (c)-[:HAS_AGENT]->(a)
        RETURN count(*) AS wired
        """,
    ),
    (
        "Chrystallum -> all SYS_ClaimStatus",
        """
        MATCH (c:Chrystallum), (cs:SYS_ClaimStatus)
        MERGE (c)-[:HAS_CLAIM_STATUS]->(cs)
        RETURN count(*) AS wired
        """,
    ),
    (
        "Chrystallum -> all SYS_ConfidenceTier",
        """
        MATCH (c:Chrystallum), (ct:SYS_ConfidenceTier)
        MERGE (c)-[:HAS_CONFIDENCE_TIER]->(ct)
        RETURN count(*) AS wired
        """,
    ),
    (
        "Chrystallum -> all SYS_AuthorityTier",
        """
        MATCH (c:Chrystallum), (at:SYS_AuthorityTier)
        MERGE (c)-[:HAS_AUTHORITY_TIER]->(at)
        RETURN count(*) AS wired
        """,
    ),
    (
        "Chrystallum -> all SYS_ValidationRule",
        """
        MATCH (c:Chrystallum), (vr:SYS_ValidationRule)
        MERGE (c)-[:HAS_VALIDATION_RULE]->(vr)
        RETURN count(*) AS wired
        """,
    ),
    (
        "Chrystallum -> all SYS_CurationDecision",
        """
        MATCH (c:Chrystallum), (cd:SYS_CurationDecision)
        MERGE (c)-[:HAS_CURATION_DECISION]->(cd)
        RETURN count(*) AS wired
        """,
    ),
    # --- Wire ALL remaining SYS_Threshold (was only 4 of 31) ---
    (
        "Chrystallum -> all SYS_Threshold",
        """
        MATCH (c:Chrystallum), (t:SYS_Threshold)
        MERGE (c)-[:HAS_THRESHOLD]->(t)
        RETURN count(*) AS wired
        """,
    ),
    # --- Wire SYS_ConfidenceModifier ---
    (
        "Chrystallum -> all SYS_ConfidenceModifier",
        """
        MATCH (c:Chrystallum), (cm:SYS_ConfidenceModifier)
        MERGE (c)-[:HAS_CONFIDENCE_MODIFIER]->(cm)
        RETURN count(*) AS wired
        """,
    ),
    # --- Wire SYS_RejectionReason ---
    (
        "Chrystallum -> all SYS_RejectionReason",
        """
        MATCH (c:Chrystallum), (rr:SYS_RejectionReason)
        MERGE (c)-[:HAS_REJECTION_REASON]->(rr)
        RETURN count(*) AS wired
        """,
    ),
    # --- Wire SYS_QueryPattern ---
    (
        "Chrystallum -> all SYS_QueryPattern",
        """
        MATCH (c:Chrystallum), (qp:SYS_QueryPattern)
        MERGE (c)-[:HAS_QUERY_PATTERN]->(qp)
        RETURN count(*) AS wired
        """,
    ),
    # --- Wire SYS_ClassificationTier ---
    (
        "Chrystallum -> all SYS_ClassificationTier",
        """
        MATCH (c:Chrystallum), (ct:SYS_ClassificationTier)
        MERGE (c)-[:HAS_CLASSIFICATION_TIER]->(ct)
        RETURN count(*) AS wired
        """,
    ),
    # --- Wire SYS_FacetPolicy ---
    (
        "Chrystallum -> all SYS_FacetPolicy",
        """
        MATCH (c:Chrystallum), (fp:SYS_FacetPolicy)
        MERGE (c)-[:HAS_FACET_POLICY]->(fp)
        RETURN count(*) AS wired
        """,
    ),
]


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as session:
        for desc, query in QUERIES:
            result = session.run(query)
            record = result.single()
            count = record["wired"] if record else 0
            print(f"  {desc}: {count} edges")
    driver.close()
    print("\nDone. All root edges wired.")


if __name__ == "__main__":
    main()
