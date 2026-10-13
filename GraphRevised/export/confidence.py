"""How well a claim is attested, in words (25-LIVES-AND-PLAYGROUND.md section 6, decision 4).

Computed when the graph is read, never stored, never a number. A claim is
judged with its family: every claim with the same predicate, subject, and
object (the asserted claim and each source's attributed version share an ID
up to the qualifier digest). Rejected and superseded members do not count.

    imagined                 the claim is imaginative (attributed to a creative Work)
    one author's reading     interpretive; "a reading shared by N authors" when more agree
    well attested (N authors) factual, two or more distinct authors behind the family
    attested (1 author)      factual, one author
    disputed (N authors)     factual members state the same qualifier differently
    no evidence yet          factual, nothing behind it

An author is the Person a Work's `authorOf` claim names, or the Work itself
when no author is recorded, or the source system (such as Wikidata) for
evidence outside any Work. A modern author who builds on an ancient one
still counts as a second author.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

LIVE = ("accepted", "proposed")
QUALIFIER_SUFFIX = re.compile(r":q[0-9a-f]{10}$")


def family_key(assertion_id: str) -> str:
    return QUALIFIER_SUFFIX.sub("", assertion_id)


def _differ(values: Iterable[Any]) -> bool:
    return len({value for value in values if value is not None}) > 1


def _times_conflict(members: list[dict[str, Any]]) -> bool:
    """Two members with normalized bounds that do not overlap."""
    bounded = [(m["start"], m["end"]) for m in members if m.get("start") is not None and m.get("end") is not None]
    return any(a_end < b_start or b_end < a_start
               for i, (a_start, a_end) in enumerate(bounded) for b_start, b_end in bounded[i + 1:])


def _quantities_conflict(members: list[dict[str, Any]]) -> bool:
    """Two members giving different figures for times that are not apart: an establishment that
    changed (one figure in one century, another later) is two dated facts, not a dispute."""
    counted = [m for m in members if m.get("quantity") is not None]
    for i, a in enumerate(counted):
        for b in counted[i + 1:]:
            if a["quantity"] != b["quantity"] and not _times_conflict([a, b]):
                return True
    return False


def disputed(members: list[dict[str, Any]], once: bool = False) -> bool:
    """Members that state the same qualifier with different values. Differences in a
    time's wording alone are not a dispute: only normalized bounds are compared.

    A fact that happens once (`once` in the registry: born, occurred) is disputed by any
    differing time, context, or role. Any other fact may recur, so those differences are
    separate occasions (two consulships years apart); only different figures for
    one time dispute it."""
    if once and (_differ(m.get("context") for m in members) or _differ(m.get("role") for m in members)
                 or _times_conflict(members)):
        return True
    return _quantities_conflict(members)


def confidence(claim: dict[str, Any], family: list[dict[str, Any]]) -> str:
    """`claim` and each family member: {status, category, authors, context, role, quantity, start, end};
    the claim may say `once: true` for a fact that happens once."""
    category = claim.get("category") or "factual"
    if category == "imaginative":
        return "imagined"
    live = [m for m in family if m["status"] in LIVE]
    same = [m for m in live if (m.get("category") or "factual") == category]
    authors = {author for m in same for author in m["authors"]}
    count = len(authors)
    plural = f"{count} author{'' if count == 1 else 's'}"
    if category == "interpretive":
        return "one author's reading" if count <= 1 else f"a reading shared by {plural}"
    if disputed(same, once=claim.get("once", False)):
        return f"disputed ({plural})"
    if count >= 2:
        return f"well attested ({plural})"
    return f"attested ({plural})" if count == 1 else "no evidence yet"
