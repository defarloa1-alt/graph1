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

Positions (44, D-153) are worded apart: `position_history` gives who held and rejected a
Position, when, and its reception, never a count of evidence; `position_link_wording` says
whether a `holds` or `rejects` link is the Work's own words or another's report.

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


# --- Positions (44-HISTORIOGRAPHY-AND-DEBATES.md, D-153) ------------------------------------------
# A Position is never "well attested": how many held a view is not evidence that it is true. Its
# wording is a history, who held it and who rejected it, when, and how it was received, each part
# saying whose account it is. A `holds` or `rejects` link says whether the Work states it in its own
# words or another Work reports it.

POSITION_LINKS = ("holds", "rejects")


def position_link_wording(holder: str, voices: Iterable[dict[str, Any]]) -> str:
    """How a `holds` or `rejects` link is known: `holder` is the Work's id; each live voice gives
    `work` (the id of the Work it is attributed to) and `name` (how to name that Work)."""
    own, reporters = False, {}
    for voice in voices:
        if voice["status"] not in LIVE:
            continue
        if voice["work"] == holder:
            own = True
        else:
            reporters.setdefault(voice["work"], voice["name"])
    reported = f"reported by {_names(reporters)}" if reporters else ""
    if own:
        return "in its own words" + (f"; also {reported}" if reported else "")
    return reported or "no voice yet"


def _year(time: str | None) -> str | None:
    """"1899 CE" -> "1899"; a BCE year keeps its era."""
    return time.replace(" CE", "") if time else None


_LEADING = {"until", "from", "since", "after", "before", "by", "in", "during", "ever", "throughout", "till"}


def _in_sentence(time: str) -> str:
    """A source's time words inside a sentence: "Until the end ..." -> "until the end ...".
    Only a leading preposition is lowered, so a proper name ("Augustan times") keeps its capital."""
    first, _, rest = time.partition(" ")
    return (first.lower() + (" " + rest if rest else "")) if first.lower() in _LEADING else time


def position_history(links: Iterable[dict[str, Any]], receptions: Iterable[dict[str, Any]] = ()) -> str:
    """A Position's history in words, from its live links and reception claims.

    Each link: {verb: holds|rejects, holder: the Work's id, name: how to name it (its author),
    time: the claim's time in words or None, start: its start (a day number) or None,
    ancient: whether the Work is a primary source, reporter: the name of the Work that says so when
    it is not the holder itself, else None, status}. Each reception: {reception, time, according, status}.

        held by an ancient historian; Scholar A (1807), Scholar B (1899); rejected by Scholar C (1931);
        dominant from 1899 (according to Scholar D); as reported by Scholar D
    """
    live = [link for link in links if link["status"] in LIVE]
    parts = []
    for verb, words in (("holds", "held by"), ("rejects", "rejected by")):
        chosen = sorted({(link["holder"], link["verb"]): link for link in live if link["verb"] == verb}.values(),
                        key=lambda link: (not link.get("ancient"), link.get("start") is None,
                                          link.get("start") or 0, link["name"]))
        if not chosen:
            continue
        ancient = [link["name"] for link in chosen if link.get("ancient")]
        modern = [link["name"] + (f" ({_year(link['time'])})" if link.get("time") else "")
                  for link in chosen if not link.get("ancient")]
        parts.append(f"{words} " + "; ".join(group for group in (", ".join(ancient), ", ".join(modern)) if group))
    for reception in receptions:
        if reception["status"] in LIVE:
            parts.append(reception["reception"] + (f" {_in_sentence(_year(reception['time']))}" if reception.get("time") else "")
                         + (f" (according to {reception['according']})" if reception.get("according") else ""))
    reporters = sorted({link["reporter"] for link in live if link.get("reporter")})
    if reporters:
        parts.append("as reported by " + ", ".join(reporters))
    return "; ".join(parts) if parts else "no holder recorded yet"
