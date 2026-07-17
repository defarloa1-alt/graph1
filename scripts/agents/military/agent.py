"""
Military Subject Facet Agent (registry-backed)

Writes claims only with relationship types from
Relationships/relationship_types_registry_master.csv.

See docs/FACET_TRAINING_CONTRACT.md.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from neo4j import GraphDatabase

_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from scripts.agents.claim_registry import ClaimRegistry
from scripts.agents.military.registry_predicates import (
    MILITARY_PILOT_PREDICATES,
    assert_military_predicate,
    military_implemented_predicates,
)
from scripts.agents.peer_reviewer import PeerReviewer

try:
    from scripts.agents.subject_concept_facet_agents import SubjectConceptFacetAgent
except ImportError:
    class SubjectConceptFacetAgent:  # type: ignore[no-redef]
        def __init__(self, facet_key, facet_label=None, neo4j_driver=None, **kwargs):
            self.facet_key = facet_key
            self.facet_label = facet_label or facet_key
            self.driver = neo4j_driver
            self.agent_id = f"{facet_key.lower()}_sfa_001"


class MilitarySFA(SubjectConceptFacetAgent):
    """Military SFA — registry predicates only; no invented ontology labels."""

    # Wikidata PIDs useful for harvest / enrichment (not claim relationship types)
    MILITARY_PROPERTIES = {
        "P607": "conflict",
        "P361": "part_of",
        "P710": "participant",
        "P276": "location",
        "P585": "point_in_time",
        "P1344": "participant_in",
        "P828": "has_cause",
        "P1120": "number_of_deaths",
    }

    def __init__(self, neo4j_driver, anthropic_api_key: Optional[str] = None, **kwargs):
        super().__init__(
            facet_key="MILITARY",
            facet_label="Military",
            neo4j_driver=neo4j_driver,
            anthropic_api_key=anthropic_api_key,
            **kwargs,
        )
        self.agent_id = kwargs.get(
            "agent_id", "SFA_sc_q17167_military_wars_campaigns_MILITARY"
        )
        self.claim_registry = ClaimRegistry(neo4j_driver)
        self.peer_reviewer = PeerReviewer(neo4j_driver)

    def get_all_predicates(self) -> List[str]:
        """Implemented Military registry types."""
        return military_implemented_predicates()

    def get_pilot_predicates(self) -> List[str]:
        return list(MILITARY_PILOT_PREDICATES)

    def submit_military_claim(
        self,
        entity: Dict,
        relationship_type: str,
        confidence: float,
        source_qid: Optional[str] = None,
        source_uri: Optional[str] = None,
        passage_locator: Optional[str] = None,
        igar_chain: Optional[Dict] = None,
        predicate_gloss: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Submit a military claim via ClaimRegistry with registry validation.

        Prefer the Claims-track pilot (`training_pilot.py`) for staged Claim nodes.
        This method is for multi-agent ASSERTS about existing canonical entities.
        """
        normalized = assert_military_predicate(relationship_type, require_implemented=True)
        return self.claim_registry.submit_claim(
            entity=entity,
            predicate=predicate_gloss or normalized,
            facet="MILITARY",
            agent_id=self.agent_id,
            confidence=confidence,
            source_qid=source_qid,
            source_uri=source_uri,
            passage_locator=passage_locator,
            igar_chain=igar_chain,
            relationship_type=normalized,
            domain_id=kwargs.pop("domain_id", "roman_republic"),
            **kwargs,
        )

    def review_peer_claims(
        self,
        entity_cipher: str,
        subjectconcept_id: Optional[str] = None,
    ) -> List[Dict]:
        reviews = self.peer_reviewer.review_entity_claims(
            entity_cipher=entity_cipher,
            reviewing_facet="MILITARY",
            reviewing_agent=self.agent_id,
            subjectconcept_id=subjectconcept_id,
        )
        allowed = set(self.get_all_predicates())
        for review in reviews:
            pred = (review.get("reviewed_predicate") or "").upper()
            conf = review.get("review_confidence", 0.0)
            if pred in allowed and conf >= 0.85:
                review["agrees"] = True
                review["note"] = f"Military facet: registry type {pred} at confidence {conf}"
        return reviews


def create_military_sfa(neo4j_uri: str, neo4j_user: str, neo4j_password: str) -> MilitarySFA:
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    return MilitarySFA(driver)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    sfa = create_military_sfa(
        os.getenv("NEO4J_URI"),
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD"),
    )
    print(f"agent_id={sfa.agent_id}")
    print(f"predicates={len(sfa.get_all_predicates())}")
    print("pilot=", ", ".join(sfa.get_pilot_predicates()))
    # Prove unregistered types are rejected
    try:
        sfa.submit_military_claim(
            entity={"type": "EVENT", "qid": "Q36456", "label": "Battle of Cannae"},
            relationship_type="employed_tactic",
            confidence=0.9,
        )
        print("ERROR: unregistered type was accepted")
    except ValueError as exc:
        print(f"[OK] rejected unregistered type: {exc}")
