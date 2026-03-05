"""
Biographic Subject Agent

Harvests biographical context for Person nodes with QIDs:
  1. Forward properties — P569/570/19/20/509/119, P26+qualifiers, P607/793/1344/166, external IDs
  2. Backlinks — items that reference the person (undeclared children, subordinates, etc.)
  3. Spouse qualifiers — enriches SPOUSE_OF edges with start_year, end_year, place_of_marriage

Usage:
    python -m scripts.agents.biographic --dprr 1976
    python -m scripts.agents.biographic --all
"""

from .agent import BiographicAgent, harvest_person
from .decision_loader import BioDecisionModel, load_decision_model

__all__ = [
    "BiographicAgent",
    "harvest_person",
    "BioDecisionModel",
    "load_decision_model",
]
