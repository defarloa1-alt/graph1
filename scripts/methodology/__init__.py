"""
Chrystallum methodology overlays — Fischer, Milligan, PRH.

Each framework provides constraints agents consult before emitting claims
or narrative sections. Frameworks are graph-resident (Neo4j) and loaded
via methodology_linter or framework-specific modules.
"""
from .fischer import (
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
