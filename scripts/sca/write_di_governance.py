"""
write_di_governance.py

Writes Domain Initiator governance nodes to Neo4j:
  - 4 SYS_Policy nodes (cipher formula, LCSH resolution, subject_id pattern, LCSH ceiling)
  - 2 SYS_Threshold nodes (max concepts per domain, token overlap floor)
  - 15 SYS_CurationDecision nodes (one per KNOWN_PATCHES entry, wired to SubjectConcept)

Replaces KNOWN_PATCHES dict in verify_and_patch_lcsh.py with queryable graph data.
Idempotent (MERGE on name/decision_key).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

# ── Policies ─────────────────────────────────────────────────────────────────

MERGE_POLICY = """
MERGE (p:SYS_Policy {name: $name})
SET p.description = $description,
    p.rule = $rule,
    p.active = true,
    p.scope = $scope,
    p.last_updated = datetime(),
    p.updated_by = 'domain_initiator'
"""

POLICIES = [
    {
        "name": "DI_CipherFormula",
        "description": "Deterministic cipher for SubjectConcept identity",
        "rule": 'SHA-256("SUBJECT_CONCEPT|{concept_qid}|{lcsh_sh_id}")',
        "scope": "domain_initiator",
    },
    {
        "name": "DI_LCSHResolution",
        "description": "LCSH ID resolution strategy: LLM cannot generate sh-IDs (opaque numeric codes). LLM outputs heading strings only, LoC API resolves IDs atomically.",
        "rule": "f(heading)->hits (LoC suggest2 API) | g(heading,hits)->id (LLM reasoning) | h(qid,id)->cipher (SHA-256)",
        "scope": "domain_initiator",
    },
    {
        "name": "DI_SubjectIdPattern",
        "description": "MERGE key pattern for SubjectConcept nodes",
        "rule": "subj_{qid_lowercase} where qid = concept Wikidata QID; fallback subj_{cipher[:12]} if QID unknown",
        "scope": "domain_initiator",
    },
    {
        "name": "DI_LCSHCeiling",
        "description": "Some concepts lack dedicated LCSH headings -- share a parent heading. QID differentiates in cipher. Status = lcsh_ceiling.",
        "rule": "When no dedicated LCSH heading exists, use nearest parent heading. Set lcsh_id_status=lcsh_ceiling. Cipher still unique via distinct concept QID.",
        "scope": "domain_initiator",
    },
]

# ── Thresholds ───────────────────────────────────────────────────────────────

MERGE_THRESHOLD = """
MERGE (t:SYS_Threshold {name: $name})
SET t.value = $value,
    t.unit = $unit,
    t.description = $description,
    t.decision_table = $dt,
    t.system = 'domain_initiator',
    t.last_reviewed = datetime()
"""

THRESHOLDS = [
    {
        "name": "di_max_concepts_per_domain",
        "value": 25,
        "unit": "count",
        "description": "Maximum SubjectConcepts a single domain seed should generate before requiring splits or sub-domains",
        "dt": "D12_DETERMINE_SubjectConcept_split_trigger",
    },
    {
        "name": "di_lcsh_token_overlap_floor",
        "value": 0.3,
        "unit": "score",
        "description": "Minimum Jaccard token overlap between expected heading and LoC API hit to consider a match",
        "dt": None,
    },
]

# ── Curation Decisions ───────────────────────────────────────────────────────
# Each entry replaces one line in the old KNOWN_PATCHES dict.

MERGE_CURATION = """
MERGE (cd:SYS_CurationDecision {decision_key: $key})
SET cd.concept_label = $concept_label,
    cd.lcsh_id = $lcsh_id,
    cd.lcsh_heading = $lcsh_heading,
    cd.lcsh_id_status = $status,
    cd.rationale = $rationale,
    cd.seed_qid = $seed_qid,
    cd.decided_by = 'human',
    cd.decided_at = datetime()
WITH cd
MATCH (sc:SubjectConcept {label: $concept_label, seed_qid: $seed_qid})
MERGE (sc)-[:HAS_CURATION_DECISION]->(cd)
"""

CURATIONS = [
    # (label, sh_id, heading, status, rationale)
    ("Roman Magistracies",           "sh85115176", "Rome--Officials and employees",  "verified",     "LoC heading covers officials/magistrates; exact match for Republican magistracies"),
    ("Roman Republican Army",        "sh85115090", "Rome--Army",                     "verified",     "Direct LoC heading match"),
    ("Roman Navy",                   "sh87007223", "Rome--Navy",                     "verified",     "Direct LoC heading match"),
    ("Roman Republican Economy and Finance", "sh85115103", "Rome--Economic conditions--510-30 B.C.", "verified", "Period-specific LCSH; upgraded from sh85115102 (general)"),
    ("Roman Republican Religion",    "sh96009771", "Rome--Religion",                 "verified",     "Direct LoC heading match"),
    ("Roman Slavery",                "sh85123324", "Slavery--Rome",                  "verified",     "Direct LoC heading match"),
    ("Women in Ancient Rome",        "sh2010119009","Women--Rome--Social conditions", "verified",     "LoC heading covers women in Roman social context"),
    ("Roman Family and Kinship",     "sh2009124087","Families--Rome",                "verified",     "LoC heading for Roman families"),
    ("Roman Education",              "sh2008119007","Education--Rome",               "verified",     "Direct LoC heading match"),
    ("Roman Historiography and Sources","sh2008116719","Rome--Historiography",       "verified",     "Direct LoC heading match"),
    ("Archaeology of Republican Rome","sh85115088", "Rome--Antiquities",             "verified",     "LoC heading covers Roman antiquities/archaeology"),
    ("Roman Republican Literature and Intellectual Life","sh2008106708","Latin literature--History and criticism","verified","Correct era-specific heading; sh2008106711 (Medieval) excluded"),
    ("Roman Science, Technology, and Medicine","sh85118612","Science, Ancient",       "verified",     "Broadest available heading; no Roman-specific science heading exists"),
    ("Roman Senate",                 "sh85115178", "Rome--Politics and government",  "lcsh_ceiling", "No dedicated Senate heading in LCSH; shares with Assemblies, QID differentiates cipher"),
    ("Roman Popular Assemblies",     "sh85115178", "Rome--Politics and government",  "lcsh_ceiling", "No dedicated Assemblies heading in LCSH; shares with Senate, QID differentiates cipher"),
]


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # Policies
        for p in POLICIES:
            session.run(MERGE_POLICY, p).consume()
            print(f"  Policy: {p['name']}")

        # Thresholds
        for t in THRESHOLDS:
            session.run(MERGE_THRESHOLD, t).consume()
            print(f"  Threshold: {t['name']} = {t['value']}")

        # Curation decisions
        for label, sh_id, heading, status, rationale in CURATIONS:
            key = f"di_lcsh|Q17167|{label}"
            session.run(MERGE_CURATION, {
                "key": key,
                "concept_label": label,
                "lcsh_id": sh_id,
                "lcsh_heading": heading,
                "status": status,
                "rationale": rationale,
                "seed_qid": "Q17167",
            }).consume()
            print(f"  Curation: {label:<50} {sh_id} ({status})")

    # Verify
    with driver.session() as session:
        pol = session.run(
            "MATCH (p:SYS_Policy) WHERE p.scope = 'domain_initiator' RETURN count(p) AS c"
        ).single()["c"]
        thr = session.run(
            "MATCH (t:SYS_Threshold) WHERE t.system = 'domain_initiator' RETURN count(t) AS c"
        ).single()["c"]
        cur = session.run(
            "MATCH (cd:SYS_CurationDecision) RETURN count(cd) AS c"
        ).single()["c"]
        edges = session.run(
            "MATCH (:SubjectConcept)-[r:HAS_CURATION_DECISION]->(:SYS_CurationDecision) RETURN count(r) AS c"
        ).single()["c"]
        print(f"\nGraph: {pol} DI policies, {thr} DI thresholds, {cur} curation decisions, {edges} edges")

    driver.close()


if __name__ == "__main__":
    main()
