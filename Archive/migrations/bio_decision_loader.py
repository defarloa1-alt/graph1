"""
bio_decision_loader.py — ARCHIVED 2026-03-02

Superseded by scripts.agents.biographic.decision_loader

Use:
    from scripts.agents.biographic.decision_loader import BioDecisionModel, load_decision_model
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from scripts.agents.biographic.decision_loader import (
    BioDecisionModel,
    load_decision_model,
)

__all__ = ["BioDecisionModel", "load_decision_model"]
