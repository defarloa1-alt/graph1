"""
Military facet — registry-backed predicates only.

Per docs/FACET_TRAINING_CONTRACT.md: no invented snake_case predicates.
"""

from __future__ import annotations

from scripts.tools.sys_registry import (
    RelationshipValidation,
    load_relationship_registry,
    validate_relationship_type,
)

# Preferred starter set for the Military training pilot (all implemented in CSV).
MILITARY_PILOT_PREDICATES = (
    "FOUGHT_IN",
    "BATTLED_IN",
    "BESIEGED",
    "DEFEATED",
    "COMMANDED_BY",
    "SERVED_UNDER",
    "SACKED",
    "GARRISONED",
    "MILITARY_ACTION",
)


def military_implemented_predicates() -> list[str]:
    """All Military-category relationship types with lifecycle_status=implemented."""
    registry = load_relationship_registry()
    return sorted(
        e.relationship_type
        for e in registry.values()
        if e.category.lower() == "military" and e.lifecycle_status == "implemented"
    )


def validate_military_predicate(
    relationship_type: str,
    *,
    require_implemented: bool = True,
) -> RelationshipValidation:
    """
    Validate a military training predicate against the CSV registry.

    Args:
        relationship_type: Candidate type (any case; normalized to UPPER_SNAKE).
        require_implemented: If True, reject candidate/routing_only (Hold).
    """
    result = validate_relationship_type(relationship_type)
    if not result.valid:
        return result
    if require_implemented and result.registry_status != "implemented":
        return RelationshipValidation(
            relationship_type=result.relationship_type,
            normalized=result.normalized,
            valid=False,
            lifecycle_status=result.lifecycle_status,
            in_csv=result.in_csv,
            in_graph=result.in_graph,
            in_backlink_routing=result.in_backlink_routing,
            wikidata_property=result.wikidata_property,
            message=(
                f"{result.normalized} is registry_status={result.registry_status}; "
                "Military training requires lifecycle_status=implemented "
                "(or Hold with human review for candidate)."
            ),
            registry_status=result.registry_status,
        )
    # Prefer Military category, but allow shared types (e.g. POSITION_HELD) if implemented
    registry = load_relationship_registry()
    entry = registry.get(result.normalized)
    if entry and entry.category.lower() not in {"military", "political", "entity", ""}:
        # Still valid if implemented — caller may use cross-facet types deliberately
        pass
    return result


def assert_military_predicate(relationship_type: str, *, require_implemented: bool = True) -> str:
    """Return normalized type or raise ValueError."""
    result = validate_military_predicate(
        relationship_type, require_implemented=require_implemented
    )
    if not result.valid:
        allowed = ", ".join(military_implemented_predicates()[:12])
        raise ValueError(
            f"{result.message} Allowed Military implemented (sample): {allowed}..."
        )
    return result.normalized
