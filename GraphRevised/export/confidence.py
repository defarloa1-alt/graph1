"""How well a claim is attested, in words (25-LIVES-AND-PLAYGROUND.md section 6, decision 4).

Computed when the graph is read, never stored, never a number. A claim is
judged with its family: every claim with the same predicate, subject, and
object (the asserted claim and each source's attributed version share an ID
up to the qualifier digest). Rejected and superseded members do not count.

    imagined                  the claim is imaginative (attributed to a creative Work)
    one author's reading      interpretive; "a reading shared by N authors" when more agree
    disputed (N authors)      factual members state the same qualifier differently
    well attested (N ancient sources)   factual, two or more independent ancient lines
    attested (1 ancient source)         factual, one ancient line
    a modern reconstruction (Strauss)   no ancient line; a modern author's own argument
    modern sources only (N works, not traced)   modern claims whose basis is not traced
    reference only (Wikidata)           reference works only
    no evidence yet           factual, nothing behind it

Factual attestation counts independent lines of evidence, not authors
(42-CORROBORATION-AND-CLAIM-KINDS.md, D-148). A line is an ancient source
(a Work of standing `primary`, one line per author), or a modern
reconstruction. A modern claim that reports an ancient source joins that
source's line through its rests-on link; an untraced modern claim and a
reference work add none. The modern and reference works are named in a
suffix ("; retold by Weigall"; "; also in Wikipedia"), never hidden.

Each member carries `lines`: (kind, identity, name) with kind one of
witness, reconstruction, retold, untraced, reference; and `authors` for
the interpretive and dispute counts.
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
    found: dict[str, dict[str, str]] = {kind: {} for kind in KINDS}
    for m in same:
        for kind, identity, name in m.get("lines", ()):
            found[kind].setdefault(identity, name)
    witnesses = len(found["witness"])
    if witnesses:
        base = (f"well attested ({witnesses} ancient sources)" if witnesses >= 2
                else "attested (1 ancient source)")
        tail = ("reconstruction", "retold", "untraced", "reference")
    elif found["reconstruction"]:
        base, tail = f"a modern reconstruction ({_names(found['reconstruction'])})", ("retold", "untraced", "reference")
    elif found["untraced"] or found["retold"]:
        works = len(found["untraced"]) + len(found["retold"])
        base = f"modern sources only ({works} work{'' if works == 1 else 's'}, not traced)"
        tail = ("reference",)
    elif found["reference"]:
        base, tail = f"reference only ({_names(found['reference'])})", ()
    else:
        return "no evidence yet"
    seen = set(found["witness"]) | (set() if "reconstruction" in tail else set(found["reconstruction"]))
    groups: dict[str, dict[str, str]] = {}
    for kind in tail:
        names = {i: n for i, n in found[kind].items() if i not in seen}
        groups.setdefault(SUFFIX[kind], {}).update(names)
        seen |= set(names)
    return "; ".join([base, *(f"{words} {_names(names)}" for words, names in groups.items() if names)])


KINDS = ("witness", "reconstruction", "retold", "untraced", "reference")
SUFFIX = {"reconstruction": "reconstructed by", "retold": "retold by", "untraced": "also in", "reference": "also in"}


def _names(found: dict[str, str], most: int = 4) -> str:
    names = sorted(set(found.values()))
    return ", ".join(names[:most]) + (f" and {len(names) - most} more" if len(names) > most else "")


def claim_lines(keys: Iterable[str], basis: str | None, rests_on: Iterable[str], standing: dict[str, str],
                identity: dict[str, str], name: dict[str, str]) -> list[tuple[str, str, str]]:
    """One claim's lines of evidence from its source keys (its Work and its evidence's Works).

    `standing` maps a Work id to primary, secondary, or tertiary; a key with no standing (a
    source system such as Wikidata, or a Work not yet classified) is a reference. `identity`
    maps a Work to the author who makes it one line (two Lives by one author are one line).
    `basis` (reports, reconstructs, unknown) says what a modern claim is doing, and
    `rests_on` names the Works a report retells."""
    found = []
    for key in dict.fromkeys(keys):
        who, label = identity.get(key, key), name.get(key, key)
        kind = standing.get(key)
        if kind == "primary":
            found.append(("witness", who, label))
        elif basis == "reports" and rests_on and kind in ("secondary", "tertiary"):
            # A retelling joins the ancient line it rests on (a passage we hold), never its own.
            found.append(("retold", who, label))
            found += [("witness", identity.get(t, t), name.get(t, t))
                      for t in dict.fromkeys(rests_on) if standing.get(t) == "primary"]
        elif kind == "secondary":
            found.append(("reconstruction" if basis == "reconstructs" else "untraced", who, label))
        else:
            found.append(("reference", who, label))
    return found
