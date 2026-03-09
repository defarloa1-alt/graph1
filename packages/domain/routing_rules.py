"""
packages/domain/routing_rules.py — Load SYS_RoutingRule nodes from graph.

Shared by:
  backbone/subject/populate_member_of.py  — wires MEMBER_OF edges
  di/                                     — corpus routing per SC
  agents/                                 — SC-aware agents

The graph (SYS_RoutingRule nodes, script 18j) is the single source of truth.
No routing logic lives here — this module is a pure reader.
"""

from collections import defaultdict


def load_rules(session, domain: str = "roman_republic") -> tuple[dict, list, str | None]:
    """
    Load routing rules for a domain from SYS_RoutingRule nodes.

    Returns:
      person_routes : {sc_id: [position_labels]}
          Exact-match rules for Person POSITION_HELD routing.

      place_routes  : [(sc_id, [substrings])]
          CONTAINS-match rules for Place place_type routing, ordered by priority.

      catch_all_sc  : sc_id of the catch-all SC (match_mode='catch_all'), or None.
    """
    rows = session.run("""
        MATCH (r:SYS_RoutingRule {domain: $domain})
        RETURN r.source_type AS source_type,
               r.sc_id       AS sc_id,
               r.match_value AS match_value,
               r.match_mode  AS match_mode,
               r.priority    AS priority
        ORDER BY r.priority ASC, r.sc_id
    """, {"domain": domain}).data()

    if not rows:
        raise ValueError(
            f"No SYS_RoutingRule nodes found for domain='{domain}'. "
            f"Run 18j_routing_rules.cypher first."
        )

    person_routes: dict[str, list[str]] = defaultdict(list)
    place_by_priority: dict[int, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    catch_all_sc: str | None = None

    for row in rows:
        if row["source_type"] == "position_held":
            person_routes[row["sc_id"]].append(row["match_value"])

        elif row["source_type"] == "place_type":
            if row["match_mode"] == "catch_all":
                catch_all_sc = row["sc_id"]
            else:
                place_by_priority[row["priority"]][row["sc_id"]].append(row["match_value"])

    # Flatten place routes preserving priority order; sc_id unique per slot
    place_routes: list[tuple[str, list[str]]] = []
    seen: set[str] = set()
    for priority in sorted(place_by_priority.keys()):
        for sc_id, substrings in place_by_priority[priority].items():
            if sc_id not in seen:
                place_routes.append((sc_id, substrings))
                seen.add(sc_id)

    return dict(person_routes), place_routes, catch_all_sc


def summarise(person_routes: dict, place_routes: list, catch_all_sc: str | None) -> str:
    """Return a one-line summary for logging."""
    n_person = sum(len(v) for v in person_routes.values())
    n_place  = sum(len(s) for _, s in place_routes)
    total    = n_person + n_place + (1 if catch_all_sc else 0)
    return (
        f"{total} rules — "
        f"{len(person_routes)} person SCs ({n_person} labels), "
        f"{len(place_routes)} place SCs ({n_place} substrings), "
        f"catch_all={catch_all_sc}"
    )
