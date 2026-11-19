"""Display rules for the exploration projection: what a view shows, decided once for every view.

The rules mark lines and entities; they never remove them. Every fact stays in the projection with
its voices, because the fact layer (export/fact_layer.py), the coverage report and the audit read
the same projection. A view hides a line with a `fold` reason, and says how many it folded
(display only, never stored as a claim: D-039). From "Explorer Fixes on the Stage Design" (2026-11-18):

1. A part reached through a part: when A is part of B and B is part of C, the line "A part of C"
   folds into the route through B ("via-part"). The battle's moments then sit in its phases
   instead of 162 lines on the battle itself.
2. Kind of statement: each entity counts its lines by category, and an entity whose every line
   is imaginative is marked `imaginedOnly`, so a view with fiction off hides it as well.
3. Same name, different thing: two entities with one name get a short `hint` to tell them apart.
3b. "Distinct from" beside "part of": when a pair has both, the part-of line already says they
   differ, so distinctFrom folds ("part-says-distinct").
5a. Reference works: describedBy lines to tertiary Works fold into a count, "Also in 5 reference
   works" ("reference-work"). Each Work carries its standing, as ancient, modern or reference.
5b. A description that is only a web address is not shown.
6. Subject access (curator, 2026-11-19): an entity with no library heading of its own (LCSH, LCNAF,
   FAST) is reached through the nearest whole it is part of that has one: a moment of the battle
   shows "Actium, Battle of, 31 B.C." via the battle. Derived here, never stored on the moment, so
   it follows the part-of chain if a moment moves. Imagined parts inherit nothing.
"""

from __future__ import annotations

import re
from typing import Any

LIVE_LINES = ("accepted", "proposed")

FOLD_VIA_PART = "via-part"
FOLD_PART_SAYS_DISTINCT = "part-says-distinct"
FOLD_REFERENCE = "reference-work"

# Work.standing in the graph, in the words a reader sees.
STANDING_WORDS = {"primary": "ancient", "secondary": "modern", "tertiary": "reference"}

KIND_WORDS = {"Person": "person", "Event": "event", "Place": "place", "Group": "group", "Office": "office",
              "Work": "work", "Concept": "idea", "Period": "period", "Polity": "state", "Type": "type",
              "Question": "question", "Position": "position"}

ONLY_A_LINK = re.compile(r"\s*https?://\S+\s*")
YEAR = re.compile(r"\b(\d{1,4})\s*(BCE|BC|CE|AD)\b")
HINT_WORDS = 8


def _live(edge: dict[str, Any]) -> bool:
    return edge["status"] in LIVE_LINES


def fold_parts_through_parts(edges: list[dict[str, Any]]) -> None:
    """Rule 1: fold "A partOf C" when a live route A partOf B partOf C exists."""
    parts = [e for e in edges if e["predicate"] == "partOf" and _live(e)]
    wholes: dict[str, set[str]] = {}
    for edge in parts:
        wholes.setdefault(edge["source"], set()).add(edge["target"])
    for edge in parts:
        via = sorted(b for b in wholes.get(edge["source"], ())
                     if b != edge["target"] and edge["target"] in wholes.get(b, ()))
        if via:
            edge["fold"], edge["foldVia"] = FOLD_VIA_PART, via[0]


def fold_distinct_beside_part(edges: list[dict[str, Any]]) -> None:
    """Rule 3b: a pair joined by partOf needs no distinctFrom line as well."""
    pairs = {frozenset((e["source"], e["target"])) for e in edges if e["predicate"] == "partOf" and _live(e)}
    for edge in edges:
        if edge["predicate"] == "distinctFrom" and frozenset((edge["source"], edge["target"])) in pairs:
            edge["fold"] = FOLD_PART_SAYS_DISTINCT


def fold_reference_works(edges: list[dict[str, Any]], nodes: dict[str, dict[str, Any]]) -> None:
    """Rule 5a: describedBy lines to reference (tertiary) Works become a count on the entity."""
    for edge in edges:
        if edge["predicate"] == "describedBy" and nodes[edge["target"]].get("standing") == "tertiary":
            edge["fold"] = FOLD_REFERENCE
            entity = nodes[edge["source"]]
            entity["referenceWorks"] = entity.get("referenceWorks", 0) + 1


def count_lines(edges: list[dict[str, Any]], nodes: dict[str, dict[str, Any]]) -> None:
    """Rule 2: each entity's live lines by category; imaginedOnly when fiction is all there is."""
    for edge in edges:
        if not _live(edge):
            continue
        for end in {edge["source"], edge["target"]}:
            lines = nodes[end].setdefault("lines", {})
            lines[edge["category"]] = lines.get(edge["category"], 0) + 1
    for data in nodes.values():
        lines = data.get("lines") or {}
        data["imaginedOnly"] = bool(lines) and set(lines) == {"imaginative"}


DATED_FIRST = {"Event", "Period"}  # a battle is told apart by when; a person by who they were


def _year(data: dict[str, Any]) -> str | None:
    """The first dated time on the entity's own facts, with its verb ("born 77 BCE"); a span is too vague."""
    for fact in data.get("facts") or []:
        verb = fact.get("sentence", "").replace(data.get("fullLabel") or "", "", 1).replace(" was ", " ").strip()
        for time in fact.get("times") or []:
            if YEAR.search(time) and "–" not in time:
                return time if fact.get("predicate") == "occurred" or not verb else f"{verb} {time}"
    match = YEAR.search(data.get("description") or "")
    return match.group(0) if match else None


def _gist(description: str | None) -> str | None:
    if not description:
        return None
    first = re.split(r"[;,(]", description, maxsplit=1)[0].strip()
    words = first.split()
    return " ".join(words[:HINT_WORDS]) + ("…" if len(words) > HINT_WORDS else "") if words else None


def name_hints(nodes: dict[str, dict[str, Any]]) -> None:
    """Rule 3: a short hint on every entity that shares its name with another.

    The kind when the kinds differ (a period and a state); for an event or period its date, for
    anything else the gist of its description, each falling back to the other; else a plain
    "another <kind>". Never an authority code (doc 26)."""
    same: dict[str, list[dict[str, Any]]] = {}
    for data in nodes.values():
        same.setdefault((data.get("fullLabel") or data["label"]).casefold(), []).append(data)
    for group in same.values():
        if len(group) < 2:
            continue
        kinds = {d["kind"] for d in group}
        for data in group:
            if len(kinds) > 1:
                hint = KIND_WORDS.get(data["kind"], data["kind"].lower())
            elif data["kind"] in DATED_FIRST:
                hint = _year(data) or _gist(data.get("description"))
            else:
                hint = _gist(data.get("description")) or _year(data)
            data["hint"] = hint or f"another {KIND_WORDS.get(data['kind'], 'entity')}"
        hints = [d["hint"] for d in group]
        for data in group:  # two hints alike tell nothing apart: fall back to the description's gist
            if hints.count(data["hint"]) > 1:
                data["hint"] = _gist(data.get("description")) or data["hint"]


LIBRARY_SYSTEMS = ("LCSH", "LCNAF", "FAST")
MAX_DEPTH = 4  # a moment, its phase, the battle, the war: far enough


def subject_access(edges: list[dict[str, Any]], nodes: dict[str, dict[str, Any]]) -> None:
    """Rule 6: headings inherited through live, non-imaginative part-of links, from the nearest whole."""
    wholes: dict[str, list[str]] = {}
    for edge in edges:
        if edge["predicate"] == "partOf" and _live(edge) and edge["category"] != "imaginative":
            wholes.setdefault(edge["source"], []).append(edge["target"])

    def headings(data: dict[str, Any]) -> list[str]:
        return [a["label"] for a in data.get("authority") or [] if a.get("system") in LIBRARY_SYSTEMS]

    for data in nodes.values():
        if headings(data) or data["id"] not in wholes:
            continue
        seen, level = {data["id"]}, wholes[data["id"]]
        for _ in range(MAX_DEPTH):
            found = [(w, headings(nodes[w])) for w in sorted(set(level)) if w in nodes and headings(nodes[w])]
            if found:
                data["subjectAccess"] = [{"heading": h, "via": w, "viaLabel": nodes[w]["fullLabel"]}
                                         for w, hs in found for h in hs]
                break
            seen |= set(level)
            level = [p for w in level for p in wholes.get(w, []) if p not in seen]
            if not level:
                break


def apply(elements: dict[str, Any], standing: dict[str, str]) -> dict[str, Any]:
    """Mark the projection's elements in place with every display rule, and return them."""
    nodes = {n["data"]["id"]: n["data"] for n in elements["nodes"]}
    edges = [e["data"] for e in elements["edges"]]
    for node_id, data in nodes.items():
        if node_id in standing:
            data["standing"] = standing[node_id]
            data["standingWords"] = STANDING_WORDS.get(standing[node_id])
        if data.get("description") and ONLY_A_LINK.fullmatch(data["description"]):
            data["description"] = None  # 5b: the address is not a description
    fold_parts_through_parts(edges)
    fold_distinct_beside_part(edges)
    fold_reference_works(edges, nodes)
    count_lines(edges, nodes)
    name_hints(nodes)
    subject_access(edges, nodes)
    for edge in edges:  # each end says how many of its lines a view folds, and why
        if edge.get("fold"):
            for end in {edge["source"], edge["target"]}:
                folded = nodes[end].setdefault("folded", {})
                folded[edge["fold"]] = folded.get(edge["fold"], 0) + 1
    return elements
