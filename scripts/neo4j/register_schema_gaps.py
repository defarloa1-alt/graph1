"""
Register all missing labels and relationship types into the SYS_NodeType
and SYS_RelationshipType registries.

Approach:
  1. Query all distinct labels in the graph
  2. Query all distinct relationship types in the graph
  3. Diff against existing SYS_NodeType / SYS_RelationshipType nodes
  4. MERGE missing entries with appropriate domain classification

Idempotent (MERGE). Safe to re-run.
"""

from neo4j import GraphDatabase
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

# ── Domain classification for missing node labels ────────────────────────────
# SYS_ labels = infrastructure, others = domain or framework
LABEL_DOMAIN = {
    # Domain entities
    "CorpusWork": ("domain", "Academic corpus work ingested from federation sources"),
    "DigitalPrinciple": ("framework", "Digital hermeneutics principle (Milligan)"),
    "Event": ("domain", "Historical event node"),
    "Fallacy": ("framework", "Logical fallacy (Fischer)"),
    "FallacyFamily": ("framework", "Grouping of related logical fallacies"),
    "Framework": ("framework", "Interpretive framework (PRH, Fischer, Milligan)"),
    "Mechanism": ("framework", "Causal mechanism in repertoire analysis"),
    "MethodologicalDomain": ("framework", "Methodological domain classification"),
    "MethodologyText": ("framework", "Source text for methodological framework"),
    "PlaceName": ("domain", "Alternate or historical name for a Place node"),
    "RepertoireFamily": ("framework", "Family grouping of repertoire patterns"),
    "RepertoirePattern": ("framework", "Contentious politics repertoire pattern (PRH)"),
    "SFA_SubScope": ("infrastructure", "Sub-scope definition within an SFA facet"),
    "SFA_TrainingInsight": ("infrastructure", "Training insight captured from SFA run"),
    "SFA_TrainingRun": ("infrastructure", "Record of an SFA training execution"),
    "SubjectDomain": ("domain", "Top-level subject domain (e.g. Roman Republic)"),
    "TaskType": ("infrastructure", "Type of agent task in workflow system"),
    "WikidataType": ("domain", "Wikidata instance-of type cached locally"),
    # SYS_ infrastructure
    "SYS_ADR": ("infrastructure", "Architecture Decision Record"),
    "SYS_AgentType": ("infrastructure", "Agent type classification"),
    "SYS_AnchorTypeMapping": ("infrastructure", "Maps Wikidata types to entity labels"),
    "SYS_AuthorityTier": ("infrastructure", "Authority tier for source ranking"),
    "SYS_ClaimStatus": ("infrastructure", "Claim lifecycle status"),
    "SYS_ClassificationAlgorithm": ("infrastructure", "Classification algorithm definition"),
    "SYS_ClassificationTier": ("infrastructure", "Tiered classification logic"),
    "SYS_ConfidenceModifier": ("infrastructure", "Modifier applied to confidence scores"),
    "SYS_ConfidenceTier": ("infrastructure", "Confidence tier definition"),
    "SYS_CurationDecision": ("infrastructure", "Curation decision record"),
    "SYS_DecisionRow": ("infrastructure", "Row within a decision table"),
    "SYS_DecisionTable": ("infrastructure", "Decision table for agent logic"),
    "SYS_EdgeType": ("infrastructure", "Edge type metadata"),
    "SYS_FacetRouter": ("infrastructure", "Routes Wikidata properties to facets"),
    "SYS_FederationRegistry": ("infrastructure", "Root registry for federation sources"),
    "SYS_FederationSource": ("infrastructure", "External federation data source"),
    "SYS_HarvestPlan": ("infrastructure", "Plan for a harvest execution"),
    "SYS_NodeType": ("infrastructure", "Node type registry entry"),
    "SYS_OASourcePack": ("infrastructure", "OpenAlex source pack for SFA training"),
    "SYS_OnboardingProtocol": ("infrastructure", "Agent onboarding protocol"),
    "SYS_OnboardingStep": ("infrastructure", "Step in onboarding protocol"),
    "SYS_OutputContract": ("infrastructure", "Output contract for SFA graph deltas"),
    "SYS_Policy": ("infrastructure", "System policy rule"),
    "SYS_PropertyMapping": ("infrastructure", "Wikidata property to facet mapping"),
    "SYS_QueryPattern": ("infrastructure", "Reusable Cypher query pattern"),
    "SYS_RejectionReason": ("infrastructure", "Reason for claim/entity rejection"),
    "SYS_RelationshipType": ("infrastructure", "Relationship type registry entry"),
    "SYS_SchemaBootstrap": ("infrastructure", "Schema bootstrap configuration"),
    "SYS_SchemaRegistry": ("infrastructure", "Root schema registry"),
    "SYS_SubjectConceptRoot": ("infrastructure", "Root node for subject concepts"),
    "SYS_Threshold": ("infrastructure", "Numeric threshold for agent decisions"),
    "SYS_ValidationRule": ("infrastructure", "Validation rule definition"),
    "SYS_Workflow": ("infrastructure", "Workflow definition"),
    "SYS_WorkflowStep": ("infrastructure", "Step within a workflow"),
}

# ── Domain classification for relationship types ─────────────────────────────
# Classify rel types into: infrastructure (HAS_*, system wiring),
# wikidata_harvest (came from Wikidata PID expansion), domain (Chrystallum-native)

def classify_rel(rt):
    """Return (domain, description) for a relationship type."""
    # Infrastructure: HAS_* root wiring, system edges
    infra_prefixes = (
        "HAS_ADR", "HAS_AGENT", "HAS_AUTHORITY", "HAS_BRIDGE", "HAS_CABINET",
        "HAS_CAPITAL", "HAS_CHARACTERISTIC", "HAS_CHILD_TYPE", "HAS_CLAIM",
        "HAS_CLASSIFICATION", "HAS_CONFIDENCE", "HAS_CONJUGATION", "HAS_CURATION",
        "HAS_CURRENCY", "HAS_DECISION", "HAS_DISCIPLINE", "HAS_DOMAIN",
        "HAS_EDITION", "HAS_EFFECT", "HAS_ENTITY", "HAS_FACET", "HAS_FALLACY",
        "HAS_FAMILY", "HAS_FEDERATION", "HAS_FRAMEWORK", "HAS_GEO",
        "HAS_GRAMMATICAL", "HAS_LEGISLATIVE", "HAS_LINEAGE", "HAS_LIST",
        "HAS_NAME", "HAS_OFFICIAL", "HAS_ONBOARDING", "HAS_OUTPUT",
        "HAS_PARADIGM", "HAS_PARTS", "HAS_PATTERN", "HAS_POLICY",
        "HAS_PRINCIPLE", "HAS_QUERY", "HAS_REJECTION", "HAS_RELIGION",
        "HAS_ROW", "HAS_SCHEMA", "HAS_SIGNIFICANT", "HAS_STEP",
        "HAS_SUBJECT", "HAS_TASKTYPE", "HAS_TENSE", "HAS_THRESHOLD",
        "HAS_TIER", "HAS_TRACE", "HAS_VALIDATION", "HAS_WORKFLOW",
        "HAS_WORKS", "HAS_BOUNDARY",
        "NEXT_STEP", "CAN_TRANSITION", "GUARDS_TASKTYPE", "USES_THRESHOLD",
        "USES_TYPE", "USES_MECHANISM", "USES_OUTPUT", "USES",
        "IMPOSES_CONSTRAINT", "CONSTRAINED_BY", "MAY_TAG", "INSTANCE_OF_TYPE",
        "ASSESSED_FOR_FACET", "COVERS_FACET", "RELEVANT_TO_FACET",
        "POSITIONED_AS", "FACET_OF",
    )
    if rt.startswith(tuple(infra_prefixes)) or rt in (
        "HAS_ROW", "NEXT_STEP", "CAN_TRANSITION_TO", "GUARDS_TASKTYPE",
        "USES_THRESHOLD", "USES_TYPE", "USES_MECHANISM", "USES_OUTPUT_CONTRACT",
        "IMPOSES_CONSTRAINT_ON", "CONSTRAINED_BY", "MAY_TAG",
        "INSTANCE_OF_TYPE", "ASSESSED_FOR_FACET", "COVERS_FACET",
        "RELEVANT_TO_FACET", "POSITIONED_AS", "FACET_OF", "INSTANCE_OF",
        "HAS_STEP", "HAS_ROW",
    ):
        return "infrastructure", f"System/infrastructure edge: {rt}"

    # Domain: Chrystallum-native historical domain edges
    domain_rels = {
        "ACTIVE_IN_YEAR": "Person active in a given Year node",
        "ALIGNED_WITH_GEO_BACKBONE": "Place aligned to geographic backbone",
        "BIO_CANDIDATE_REL": "Candidate biographic relationship (pre-resolution)",
        "CITIZEN_OF": "Person is citizen of a polity",
        "MEMBER_OF_GENS": "Person belongs to a Roman gens",
        "HAS_NOMEN": "Person has a nomen (family name)",
        "HAS_COGNOMEN": "Person has a cognomen",
        "HAS_PRAENOMEN": "Person has a praenomen",
        "BROADER_THAN": "Broader concept/term relationship",
        "DESCRIBED_BY_SOURCE": "Entity described by a bibliography source",
        "HAS_STATUS": "Entity has a status classification",
        "DIPLOMATIC_RELATION": "Diplomatic relationship between polities",
        "BORN_IN_PLACE": "Person born in a Place",
        "CONTAINS": "Geographic or organizational containment",
        "BORDERS": "Geographic border relationship",
        "DISCIPLINE_SUBCLASS_OF": "Discipline taxonomy subclass",
        "DISCIPLINE_BROADER_THAN": "Discipline taxonomy broader-than",
        "LOCATED_IN_TIMEZONE": "Place located in a timezone",
        "SUB_PERIOD_OF": "Period is sub-period of another",
        "DIFFERENT_FROM": "Wikidata different-from disambiguation",
        "GENDER": "Person gender classification",
        "CONTAINS_PERIOD": "Polity/place contains a historical period",
        "DIED_IN": "Person died in a place",
        "DISCIPLINE_HAS_PART": "Discipline has sub-discipline",
        "TYPE_OF": "Type-of classification relationship",
        "MEMBER_OF_TRIBE": "Person is member of a Roman tribe",
        "ADMINISTRATIVE_PART_OF": "Administrative subdivision relationship",
        "COLLABORATOR_OF": "Person collaborated with another person",
        "DIED_IN_PLACE": "Person died in a specific Place",
        "MAINTAINED_BY_WIKIPROJECT": "Wikidata maintenance tag",
        "LOCATED_IN_CONTINENT": "Place located on a continent",
        "DISCIPLINE_PART_OF": "Discipline is part of another discipline",
        "SPOKE_LANGUAGE": "Person spoke a language",
        "BORN_IN": "Person born in a place (general)",
        "CONSULTED": "Person consulted another person",
        "CONVERTED_TO": "Entity converted to another form",
        "IN_PERIOD": "Event/entity situated in a period",
        "STUDIED_BY": "Subject studied by a discipline/person",
        "BURIED_AT": "Person buried at a place",
        "PUBLISHED_IN": "Work published in a location/venue",
    }
    if rt in domain_rels:
        return "domain", domain_rels[rt]

    # Wikidata harvest: everything else is likely from PID expansion
    return "wikidata_harvest", f"Harvested from Wikidata property expansion: {rt}"


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # ── Step 1: Get existing registries ──────────────────────────────
        existing_labels = {r["name"] for r in session.run(
            "MATCH (n:SYS_NodeType) RETURN n.name AS name"
        )}
        existing_rels = {r["rt"] for r in session.run(
            "MATCH (n:SYS_RelationshipType) RETURN n.rel_type AS rt"
        ) if r["rt"] is not None}

        # ── Step 2: Get actual labels in graph ───────────────────────────
        actual_labels = {}
        for r in session.run(
            "MATCH (n) UNWIND labels(n) AS lbl "
            "WITH lbl, count(*) AS cnt "
            "RETURN lbl, cnt ORDER BY lbl"
        ):
            actual_labels[r["lbl"]] = r["cnt"]

        # ── Step 3: Get actual rel types in graph ────────────────────────
        actual_rels = {}
        for r in session.run(
            "MATCH ()-[r]->() "
            "WITH type(r) AS rt, count(*) AS cnt "
            "RETURN rt, cnt ORDER BY rt"
        ):
            actual_rels[r["rt"]] = r["cnt"]

        # ── Step 4: Register missing labels ──────────────────────────────
        missing_labels = sorted(set(actual_labels.keys()) - existing_labels)
        print(f"\n=== Missing labels to register: {len(missing_labels)} ===")

        label_count = 0
        for lbl in missing_labels:
            domain, desc = LABEL_DOMAIN.get(lbl, ("unknown", f"Unclassified label: {lbl}"))
            session.run(
                "MERGE (n:SYS_NodeType {name: $name}) "
                "ON CREATE SET n.domain = $domain, n.description = $desc",
                name=lbl, domain=domain, desc=desc,
            )
            print(f"  + {lbl} ({actual_labels[lbl]:,} nodes) [{domain}]")
            label_count += 1

        # ── Step 5: Register missing rel types ───────────────────────────
        missing_rels = sorted(set(actual_rels.keys()) - existing_rels)
        print(f"\n=== Missing rel types to register: {len(missing_rels)} ===")

        rel_count = 0
        for rt in missing_rels:
            domain, desc = classify_rel(rt)
            session.run(
                "MERGE (n:SYS_RelationshipType {rel_type: $rt}) "
                "ON CREATE SET n.name = $rt, n.domain = $domain, "
                "n.description = $desc, n.edge_count = $cnt, "
                "n.updated = date()",
                rt=rt, domain=domain, desc=desc, cnt=actual_rels[rt],
            )
            rel_count += 1
            if rel_count <= 30 or rel_count % 50 == 0:
                print(f"  + {rt} ({actual_rels[rt]:,} edges) [{domain}]")

        if rel_count > 30:
            print(f"  ... and {rel_count - 30} more")

        # ── Step 6: Wire new SYS_NodeType + SYS_RelationshipType to SchemaRegistry
        result = session.run(
            "MATCH (sr:SYS_SchemaRegistry), (nt:SYS_NodeType) "
            "MERGE (sr)-[:HAS_NODE_TYPE]->(nt) "
            "RETURN count(*) AS wired"
        )
        print(f"\n  SchemaRegistry -> SYS_NodeType: {result.single()['wired']} wired")

        result = session.run(
            "MATCH (sr:SYS_SchemaRegistry), (rt:SYS_RelationshipType) "
            "MERGE (sr)-[:HAS_RELATIONSHIP_TYPE]->(rt) "
            "RETURN count(*) AS wired"
        )
        print(f"  SchemaRegistry -> SYS_RelationshipType: {result.single()['wired']} wired")

        # ── Summary ──────────────────────────────────────────────────────
        final_labels = session.run(
            "MATCH (n:SYS_NodeType) RETURN count(n) AS c"
        ).single()["c"]
        final_rels = session.run(
            "MATCH (n:SYS_RelationshipType) RETURN count(n) AS c"
        ).single()["c"]

        print(f"\n=== Done ===")
        print(f"  SYS_NodeType:         {final_labels} (was {len(existing_labels)}, added {label_count})")
        print(f"  SYS_RelationshipType: {final_rels} (was {len(existing_rels)}, added {rel_count})")

    driver.close()


if __name__ == "__main__":
    main()
