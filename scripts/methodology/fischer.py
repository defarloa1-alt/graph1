"""
Fischer methodology overlay — fallacy checks for SCA and narrative agents.

Agents call fetch_relevant_fallacies(task_types) and detect_fallacy_hits(claim_text, fallacies)
before emitting claims or narrative sections. Optionally log TRIGGERED_FALLACY to graph.

Usage:
    from scripts.methodology.fischer import sca_lint_claim, narrative_lint_section
    result = sca_lint_claim(proposed_claim, driver=neo4j_driver)
"""
from __future__ import annotations

from typing import Any


def fetch_relevant_fallacies(task_types: list[str], driver=None) -> list[dict]:
    """
    Fetch fallacies that guard the given TaskTypes from Neo4j.

    Returns list of {id, label, diagnostic_pattern}.
    """
    if not driver:
        return []
    cypher = """
    MATCH (f:Fallacy)-[:GUARDS_TASKTYPE]->(tt:TaskType)
    WHERE tt.id IN $task_types
    RETURN DISTINCT f.id AS id, f.label AS label, f.diagnostic_pattern AS pattern
    """
    with driver.session() as session:
        result = session.run(cypher, {"task_types": task_types})
        return [dict(record) for record in result]


def detect_fallacy_hits(claim_text: str, fallacies: list[dict]) -> list[dict]:
    """
    Check claim text for phrases that trigger known fallacies.
    Returns list of {fallacy_id, reason}.
    """
    hits = []
    text_lower = claim_text.lower()
    for f in fallacies:
        fid = f.get("id", "")
        pattern = (f.get("pattern") or "").lower()
        if fid == "HOLIST_FALLACY":
            if any(p in text_lower for p in ["whole truth", "entire past", "spirit of the age", "captures the whole", "past in its entirety"]):
                hits.append({"fallacy_id": fid, "reason": "holist-phrasing"})
        if fid == "ESSENCE_FALLACY":
            if any(p in text_lower for p in ["essence of", "true character of", "essential character of", "true essence of"]):
                hits.append({"fallacy_id": fid, "reason": "essence-phrasing"})
        if fid == "OVERGENERALIZATION":
            if any(p in text_lower for p in ["all ", "everyone ", "always ", "never ", "the entire "]):
                hits.append({"fallacy_id": fid, "reason": "sweeping-quantifier"})
        if fid == "QUANTITATIVE_FALLACY":
            if "what can be measured" in text_lower or "only data that can be counted" in text_lower:
                hits.append({"fallacy_id": fid, "reason": "measurement-as-significance"})
        if fid == "AESTHETIC_FALLACY":
            if any(p in text_lower for p in ["beautiful story", "splendid tale"]):
                hits.append({"fallacy_id": fid, "reason": "aesthetic-prioritized"})
    return hits


def sca_lint_claim(proposed_claim: dict, driver=None) -> dict:
    """
    Lint a proposed claim against Fischer fallacies.

    proposed_claim: {id, text, task_types: [...], metadata: {}}
    Returns: {claim, fallacy_hits, status: 'clean'|'flagged'}
    """
    task_types = proposed_claim.get("task_types") or ["FACT_SIGNIFICANCE", "COMPOSITION"]
    fallacies = fetch_relevant_fallacies(task_types, driver)
    hits = detect_fallacy_hits(proposed_claim.get("text", ""), fallacies)

    if not hits:
        return {"claim": proposed_claim, "fallacy_hits": [], "status": "clean"}

    claim = dict(proposed_claim)
    meta = dict(claim.get("metadata") or {})
    meta["methodology_flags"] = hits
    if "confidence" in meta:
        meta["confidence"] = meta.get("confidence", 1.0) * 0.6
    claim["metadata"] = meta

    return {"claim": claim, "fallacy_hits": hits, "status": "flagged"}


def narrative_lint_section(section: dict, driver=None) -> dict:
    """
    Lint a narrative section against Fischer fallacies.

    section: {id, text, task_types: [...], metadata: {}}
    Returns: {section, fallacy_hits, status: 'clean'|'flagged'}
    """
    task_types = section.get("task_types") or ["NARRATION", "CAUSATION", "COMPOSITION", "SEMANTICS"]
    fallacies = fetch_relevant_fallacies(task_types, driver)
    hits = detect_fallacy_hits(section.get("text", ""), fallacies)

    if not hits:
        return {"section": section, "fallacy_hits": [], "status": "clean"}

    sec = dict(section)
    meta = dict(sec.get("metadata") or {})
    meta["methodology_flags"] = hits
    sec["metadata"] = meta

    return {"section": sec, "fallacy_hits": hits, "status": "flagged"}
