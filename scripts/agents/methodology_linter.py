#!/usr/bin/env python3
"""
Methodology Linter — re-exports from scripts.methodology for backward compatibility.

Prefer: from scripts.methodology import sca_lint_claim, narrative_lint_section
"""
from scripts.methodology import (
    fetch_relevant_fallacies,
    detect_fallacy_hits,
    sca_lint_claim,
    narrative_lint_section,
)

__all__ = [
    "fetch_relevant_fallacies",
    "detect_fallacy_hits",
    "sca_lint_claim",
    "narrative_lint_section",
]
