"""
Repertoire classifier — suggest RepertoirePattern and Mechanism for events.

Uses PRH framework nodes from Neo4j. classify_event returns suggestions;
assign_patterns_to_event writes to graph when Event nodes exist.
"""
from __future__ import annotations

from scripts.methodology.prh import fetch_repertoire_patterns, fetch_mechanisms


def classify_event(event: dict, driver=None) -> list[dict]:
    """
    Suggest RepertoirePattern and Mechanism for an event.

    event: {description, date_range?, location?, keywords?}
    Returns list of {pattern_id, pattern_label, mechanism_ids[], confidence, reason}.
    """
    patterns = fetch_repertoire_patterns(driver)
    if not patterns:
        return []

    text = (event.get("description") or "") + " " + " ".join(event.get("keywords") or [])
    text_lower = text.lower()

    suggestions = []
    for p in patterns:
        score = 0
        reasons = []
        label_lower = (p.get("label") or "").lower()
        if "assembly" in label_lower or "contentious" in label_lower:
            if "assembly" in text_lower or "contio" in text_lower or "contiones" in text_lower:
                score += 1
                reasons.append("assembly/contio")
        if "riot" in label_lower or "riot" in text_lower or "violence" in text_lower:
            score += 1
            reasons.append("riot/violence")
        if "food" in label_lower or "bread" in label_lower:
            if "food riot" in text_lower or "bread" in text_lower or "subsistence" in text_lower or "famine" in text_lower:
                score += 1
                reasons.append("food/subsistence")
        if "barricade" in label_lower:
            if "barricade" in text_lower or "barricades" in text_lower:
                score += 1
                reasons.append("barricade")
        if "strike" in label_lower or "strike" in text_lower:
            score += 1
            reasons.append("strike")
        if "procession" in label_lower or "demonstration" in label_lower:
            if "procession" in text_lower or "demonstration" in text_lower or "march" in text_lower:
                score += 1
                reasons.append("procession/demo")
        if "occupation" in label_lower or "occupation" in text_lower or "sit-in" in text_lower:
            score += 1
            reasons.append("occupation")
        if "assassination" in label_lower:
            if "assassination" in text_lower or "assassinated" in text_lower or "murdered" in text_lower:
                score += 1
                reasons.append("assassination")
        if "fiscal" in label_lower or "revolt" in label_lower:
            if "fiscal" in text_lower or "tax" in text_lower or "revolt" in text_lower:
                score += 1
                reasons.append("fiscal/tax")

        if score > 0:
            suggestions.append({
                "pattern_id": p["id"],
                "pattern_label": p["label"],
                "mechanism_ids": p.get("mechanism_ids", []),
                "confidence": min(0.9, 0.3 + score * 0.2),
                "reason": "; ".join(reasons),
            })

    return sorted(suggestions, key=lambda x: -x["confidence"])


def assign_patterns_to_event(event_id: str, pattern_ids: list[str], driver=None) -> bool:
    """
    Write INSTANCES_PATTERN and OPERATES_VIA to Neo4j for an Event node.

    Requires Event node with matching id. Returns True if successful.
    """
    if not driver or not pattern_ids:
        return False

    patterns = fetch_repertoire_patterns(driver)
    pattern_map = {p["id"]: p for p in patterns}

    with driver.session() as session:
        for pid in pattern_ids:
            if pid not in pattern_map:
                continue
            p = pattern_map[pid]
            session.run(
                """
                MATCH (e:Event {id: $event_id})
                MATCH (rp:RepertoirePattern {id: $pattern_id})
                MERGE (e)-[:INSTANCES_PATTERN]->(rp)
                """,
                {"event_id": event_id, "pattern_id": pid},
            )
            for m_id in p.get("mechanism_ids", []):
                session.run(
                    """
                    MATCH (e:Event {id: $event_id})
                    MATCH (m:Mechanism {id: $mechanism_id})
                    MERGE (e)-[:OPERATES_VIA]->(m)
                    """,
                    {"event_id": event_id, "mechanism_id": m_id},
                )
    return True
