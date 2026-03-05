"""
bio_decision_loader.py — DEPRECATED

Use scripts.agents.biographic.decision_loader instead.
This file re-exports for backward compatibility.
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
