"""
Subject Concept Domain Configuration

Standardizes domain/subject prefixes to avoid hardcoded abbreviations (e.g. "rr").

Canonical pattern:
  - Root: subj_{domain_slug}_{root_qid}  e.g. subj_roman_republic_q17167
  - Children: subj_{root_qid}_{concept_slug}  e.g. subj_q17167_governance

Domain is derived from ROOT_SUBJECT_QID. For multi-domain support, each domain
has its own root; child IDs include the root QID for unambiguous joins.

Legacy: subj_rr_* (Roman Republic shorthand) maps to root Q17167.
New domains should use subj_q{id}_* pattern.
"""
import os
from pathlib import Path

# Config: from env, or default for Roman Republic
ROOT_SUBJECT_QID = os.getenv("SUBJECT_ROOT_QID", "Q17167")
ROOT_SUBJECT_ID = os.getenv("SUBJECT_ROOT_ID", "subj_roman_republic_q17167")

# Prefix for child SubjectConcept IDs (derived from root QID)
# Use lowercase QID without 'Q': q17167
def get_domain_prefix() -> str:
    """Return domain prefix for child subject IDs (e.g. q17167)."""
    qid = ROOT_SUBJECT_QID.strip().upper()
    if qid.startswith("Q"):
        return qid.lower()  # Q17167 -> q17167
    return f"q{qid}"


def make_subject_id(concept_slug: str) -> str:
    """
    Generate standardized subject_id for a child concept.
    
    Args:
        concept_slug: e.g. "governance", "gov_institutions"
    Returns:
        e.g. "subj_q17167_governance"
    """
    prefix = get_domain_prefix()
    return f"subj_{prefix}_{concept_slug}"


# Legacy mapping: subj_rr_* -> subj_q17167_* (for migration)
LEGACY_RR_TO_CANONICAL = {
    "rr": "q17167",
    "roman_republic": "q17167",
}
