"""
Wire remaining self-description gaps from SCA_SFA_CONTRACT analysis:
1. SYS_FacetRouter (38 nodes) -> root link
2. Register DI (Domain Initiator) as Agent + AgentType
3. Register SCA (Subject Concept Agent) as Agent + AgentType
4. Fix unnamed Agent node (spec_only)
"""

from neo4j import GraphDatabase
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

QUERIES = [
    # --- FacetRouter -> root ---
    (
        "Chrystallum -> all SYS_FacetRouter",
        """
        MATCH (c:Chrystallum), (fr:SYS_FacetRouter)
        MERGE (c)-[:HAS_FACET_ROUTER]->(fr)
        RETURN count(*) AS wired
        """,
    ),
    # --- Register DI AgentType ---
    (
        "Register DI AgentType",
        """
        MERGE (at:SYS_AgentType {name: 'DOMAIN_INITIATOR'})
        ON CREATE SET
          at.description = 'Harvests a domain QID once, classifies entities by facet, and feeds structured output to the SCA. Runs deterministic classification (not LLM reasoning).'
        RETURN count(*) AS wired
        """,
    ),
    # --- Register SCA AgentType ---
    (
        "Register SCA AgentType",
        """
        MERGE (at:SYS_AgentType {name: 'SCA'})
        ON CREATE SET
          at.description = 'Subject Concept Agent. Coordinates SFAs, routes DI output, manages SubjectConcept lifecycle, re-scores salience when SFA proposals return. LLM reasoning agent.'
        RETURN count(*) AS wired
        """,
    ),
    # --- Register DI Agent node ---
    (
        "Register DI Agent",
        """
        MERGE (a:Agent {name: 'DOMAIN_INITIATOR'})
        ON CREATE SET
          a.status = 'active',
          a.description = 'Domain Initiator: harvests QID domain, classifies by facet, feeds SCA. See docs/DOMAIN_INITIATOR.md.'
        WITH a
        MATCH (at:SYS_AgentType {name: 'DOMAIN_INITIATOR'})
        MERGE (a)-[:INSTANCE_OF]->(at)
        RETURN count(*) AS wired
        """,
    ),
    # --- Register SCA Agent node ---
    (
        "Register SCA Agent",
        """
        MERGE (a:Agent {name: 'SCA'})
        ON CREATE SET
          a.status = 'active',
          a.description = 'Subject Concept Agent: coordinates SFAs, routes DI output, manages SubjectConcept lifecycle. See docs/SCA_SFA_CONTRACT.md.'
        WITH a
        MATCH (at:SYS_AgentType {name: 'SCA'})
        MERGE (a)-[:INSTANCE_OF]->(at)
        RETURN count(*) AS wired
        """,
    ),
    # --- Fix unnamed Agent (spec_only) -> SFA_INDEX_READER ---
    (
        "Fix unnamed Agent -> SFA_INDEX_READER",
        """
        MATCH (a:Agent)
        WHERE a.name IS NULL AND a.status = 'spec_only'
        SET a.name = 'SFA_INDEX_READER',
            a.description = 'Extracts claims from scholarly book index photos. Spec: claude/SFA_INDEX_READER_Spec_v1.docx.'
        RETURN count(*) AS wired
        """,
    ),
    # --- Wire new Agents to root ---
    (
        "Chrystallum -> all Agent (including new)",
        """
        MATCH (c:Chrystallum), (a:Agent)
        MERGE (c)-[:HAS_AGENT]->(a)
        RETURN count(*) AS wired
        """,
    ),
    # --- Wire new AgentTypes to root ---
    (
        "Chrystallum -> all SYS_AgentType (including new)",
        """
        MATCH (c:Chrystallum), (at:SYS_AgentType)
        MERGE (c)-[:HAS_AGENT_TYPE]->(at)
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
            print(f"  {desc}: {count}")
    driver.close()
    print("\nDone. Contract gaps closed.")


if __name__ == "__main__":
    main()
