"""
ADR-008 Layer 1: Deterministic Pre-Processing for Person Harvest

Provides:
  - DPRR label parsing (tria nomina, filiation, tribe, cognomen)
  - P-code → canonical relationship mapping (Wikidata)
  - Date normalisation (ISO 8601, BCE negative years)

No agent involvement. All operations have defined rules and output schemas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# 3.1 DPRR Label Parsing
# ---------------------------------------------------------------------------
# Format: POMP1976 Cn. Pompeius (31) Cn. f. Sex. n. Clu. Magnus
#   Prefix (4 chars): gens abbreviation
#   Numeric suffix: DPRR person ID (from label; cross-check with URI)
#   Token 2: praenomen abbrev (Cn.) or "-." (unknown)
#   Token 3: nomen (Pompeius)
#   (31): DPRR ordinal within gens
#   f./n. chain: filiation
#   3-4 char: tribe abbrev (Clu.)
#   Final: cognomen(s)

# Known praenomen abbreviations (DPRR convention)
PRAENOMEN_ABBREV = {
    "A.", "Ap.", "C.", "Cn.", "D.", "Dec.", "Faust.", "K.", "L.", "M.", "M'.",
    "Mam.", "Man.", "N.", "Oct.", "P.", "Post.", "Pro.", "Q.", "S.", "Sec.",
    "Ser.", "Sex.", "Sp.", "St.", "T.", "Ti.", "V.", "Vol.", "-.",
}

# Known tribe abbreviations (subset; extend from DPRR)
TRIBE_ABBREV = {
    "Aem.", "Ani.", "Arn.", "Cam.", "Clu.", "Col.", "Cor.", "Esq.", "Fab.",
    "Fal.", "Gal.", "Hor.", "Lem.", "Mac.", "Men.", "Ouf.", "Pal.", "Pap.",
    "Pol.", "Pom.", "Pup.", "Qui.", "Rom.", "Sab.", "Scap.", "Ser.", "Ste.",
    "Sub.", "Suc.", "Ter.", "Tro.", "Vel.", "Vol.", "Vot.",
}


@dataclass
class DPRRLabelParse:
    """Structured output of DPRR label parse. ADR-008 §3.1."""

    gens_prefix: str | None = None
    label_dprr_id: str | None = None  # From label; cross-check with URI dprr_id
    praenomen_abbrev: str | None = None
    nomen: str | None = None
    dprr_ordinal: str | None = None
    filiation_chain: list[str] = field(default_factory=list)
    tribe_abbrev: str | None = None
    cognomen: list[str] = field(default_factory=list)
    dq_flags: list[str] = field(default_factory=list)
    unparsed_tokens: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "gens_prefix": self.gens_prefix,
            "label_dprr_id": self.label_dprr_id,
            "praenomen_abbrev": self.praenomen_abbrev,
            "nomen": self.nomen,
            "dprr_ordinal": self.dprr_ordinal,
            "filiation_chain": self.filiation_chain,
            "tribe_abbrev": self.tribe_abbrev,
            "cognomen": self.cognomen,
            "dq_flags": self.dq_flags,
            "unparsed_tokens": self.unparsed_tokens,
        }


def parse_dprr_label(label: str) -> DPRRLabelParse:
    """
    Parse DPRR label into onomastic components. Grammar-based, no agent.

    Example: "POMP1976 Cn. Pompeius (31) Cn. f. Sex. n. Clu. Magnus"
    """
    result = DPRRLabelParse()
    if not label or not isinstance(label, str):
        result.dq_flags.append("DQ_PARSE_EMPTY_LABEL")
        return result

    tokens = label.split()
    if not tokens:
        return result

    # 1. Prefix (4 chars) + numeric suffix
    first = tokens[0]
    m = re.match(r"^([A-Z]{4})(\d+)$", first)
    if m:
        result.gens_prefix = m.group(1)
        result.label_dprr_id = m.group(2)
        tokens = tokens[1:]
    else:
        result.dq_flags.append("DQ_PARSE_NO_PREFIX")
        # Try to continue; first token might be malformed

    if not tokens:
        return result

    # 2. Praenomen abbreviation (ends with .)
    if tokens and tokens[0].endswith(".") and len(tokens[0]) <= 5:
        result.praenomen_abbrev = tokens[0] if tokens[0] != "-." else None
        tokens = tokens[1:]

    if not tokens:
        return result

    # 3. Nomen (capitalised, no period) — may be multi-word until parenthesis
    nomen_parts = []
    while tokens and not tokens[0].startswith("("):
        t = tokens[0]
        if t[0].isupper() and "." not in t:
            nomen_parts.append(t)
            tokens = tokens[1:]
        else:
            break
    if nomen_parts:
        result.nomen = " ".join(nomen_parts)

    if not tokens:
        return result

    # 4. Parenthesised ordinal
    if tokens and tokens[0].startswith("(") and tokens[0].endswith(")"):
        inner = tokens[0][1:-1]
        if inner.isdigit():
            result.dprr_ordinal = inner
        tokens = tokens[1:]

    if not tokens:
        return result

    # 5. Filiation chain (f. = filius, n. = nepos) — tokens like Cn. f. Sex. n.
    #    Stop when we hit a tribe abbrev (Clu., Aem., etc.) — not a praenomen
    while tokens:
        t = tokens[0]
        if t in ("f.", "n."):
            result.filiation_chain.append(t)
            tokens = tokens[1:]
        elif t.endswith(".") and len(t) <= 5:
            # Could be praenomen (Cn., Sex.) or tribe (Clu.)
            if t in TRIBE_ABBREV:
                break  # Tribe marks end of filiation
            if t in PRAENOMEN_ABBREV or (len(t) >= 2 and t[0].isupper()):
                result.filiation_chain.append(t)
                tokens = tokens[1:]
            else:
                break
        else:
            break

    if not tokens:
        return result

    # 6. Tribe abbreviation (3-4 chars, ends with .)
    if tokens and len(tokens[0]) <= 5 and tokens[0].endswith("."):
        cand = tokens[0]
        if cand in TRIBE_ABBREV or (len(cand) >= 3 and cand[0].isupper()):
            result.tribe_abbrev = cand
            tokens = tokens[1:]

    # 7. Remaining = cognomen(s)
    if tokens:
        result.cognomen = [t for t in tokens if t and t[0].isupper()]
        result.unparsed_tokens = [t for t in tokens if t not in result.cognomen]

    return result


# ---------------------------------------------------------------------------
# ADR-007 four-label schema: label, label_latin, label_dprr, label_sort
# ---------------------------------------------------------------------------
# label_dprr = DPRR string (provenance anchor)
# label_latin = tria nomina for scholarly citation (praenomen + nomen + cognomen)
# label_sort = nomen + cognomen + praenomen lowercased for prosopographical ordering

PRAENOMEN_ABBREV_TO_FULL: dict[str, str] = {
    "A.": "Aulus", "Ap.": "Appius", "C.": "Gaius", "Cn.": "Gnaeus", "D.": "Decimus",
    "Dec.": "Decimus", "K.": "Kaeso", "L.": "Lucius", "M.": "Marcus", "M'.": "Manius",
    "Mam.": "Mamercus", "Man.": "Manius", "N.": "Numerius", "Oct.": "Octavius",
    "P.": "Publius", "Post.": "Postumus", "Pro.": "Proculus", "Q.": "Quintus",
    "S.": "Servius", "Sec.": "Sextus", "Ser.": "Sergius", "Sex.": "Sextus",
    "Sp.": "Spurius", "St.": "Statius", "T.": "Titus", "Ti.": "Tiberius",
    "V.": "Vibius", "Vol.": "Volusus", "Faust.": "Faustus",
}


def derive_label_latin(parsed: DPRRLabelParse) -> str | None:
    """Tria nomina form for scholarly citation. E.g. 'Cn. Pompeius Magnus'."""
    parts = []
    if parsed.praenomen_abbrev:
        parts.append(parsed.praenomen_abbrev)
    if parsed.nomen:
        parts.append(parsed.nomen)
    if parsed.cognomen:
        parts.extend(parsed.cognomen)
    return " ".join(parts) if parts else None


def derive_label_sort(parsed: DPRRLabelParse) -> str | None:
    """Nomen + cognomen + praenomen lowercased for prosopographical list ordering."""
    parts = []
    if parsed.nomen:
        parts.append(parsed.nomen)
    if parsed.cognomen:
        parts.extend(parsed.cognomen)
    if parsed.praenomen_abbrev:
        full = PRAENOMEN_ABBREV_TO_FULL.get(parsed.praenomen_abbrev, parsed.praenomen_abbrev)
        parts.append(full)
    return " ".join(p.lower() for p in parts) if parts else None


# ---------------------------------------------------------------------------
# 3.2 P-code → Canonical Relationship Mapping
# ---------------------------------------------------------------------------
# ADR-008 §3.2: Raw Wikidata P-codes → Chrystallum relationship types

PCODE_TO_CANONICAL: dict[str, tuple[str, str, str]] = {
    # (canonical_rel, target_node_type, notes)
    "P19": ("BORN_IN", "Place", "Target linked to :Place or :Pleiades_Place"),
    "P20": ("DIED_IN", "Place", "Same as P19"),
    "P21": ("gender", "literal", "male/female from target label → property on node"),
    "P27": ("CITIZEN_OF", "Polity", "Target promoted to :Polity if not already"),
    "P102": ("MEMBER_OF_FACTION", "PoliticalFaction", ""),
    "P106": ("occupation", "literal", "Light-weight tag; not first-class node"),
    "P140": ("HAS_RELIGION", "Religion", ""),
    "P241": ("SERVED_IN", "MilitaryBranch", ""),
    "P410": ("HELD_RANK", "Rank", ""),
    "P463": ("MEMBER_OF_FACTION", "PoliticalFaction", "Overlaps P102; both processed"),
    "P509": ("cause_of_death", "literal", ""),
    "P1196": ("manner_of_death", "literal", ""),
    "P1343": ("DESCRIBED_BY", "Entity", "Reference work; HAS_ENTRY_IN derived separately"),
    "P2348": ("IN_PERIOD", "Periodo_Period", ""),
    "P3716": ("IN_SOCIAL_ORDER", "SocialOrder", ""),
    "P5025": ("MEMBER_OF_GENS", "Gens", "Cross-check against DPRR gens_prefix"),
    "P11491": ("MEMBER_OF_TRIBE", "Tribe", "Cross-check against DPRR tribe_abbrev"),
}


def map_pcode_to_canonical(pid: str) -> tuple[str, str] | None:
    """
    Map Wikidata P-code to (canonical_relationship, target_type).
    Returns None if unmapped.
    """
    row = PCODE_TO_CANONICAL.get(pid)
    if row:
        return (row[0], row[1])
    return None


# ---------------------------------------------------------------------------
# 3.3 Date Normalisation
# ---------------------------------------------------------------------------
# ADR-008 §3.3: ISO 8601, negative years for BCE
# Wikidata precision: 7=century, 8=decade, 9=year, 10=month, 11=day

WIKIDATA_PRECISION = {
    7: "century",
    8: "decade",
    9: "year",
    10: "month",
    11: "day",
}


def normalise_wikidata_date(
    time_value: dict | None,
    precision: int | None = None,
) -> tuple[str | None, str | None]:
    """
    Normalise Wikidata time value to (earliest, latest) ISO 8601.
    BCE: negative year (106 BCE = -0106).
    Returns (birth_earliest, birth_latest) or (None, None) if invalid.
    """
    if not time_value:
        return (None, None)

    # Wikidata time: {"time": "+0106-09-29T00:00:00Z", "precision": 11, ...}
    time_str = time_value.get("time") if isinstance(time_value, dict) else None
    if not time_str:
        return (None, None)

    prec = precision if precision is not None else (time_value.get("precision", 9) if isinstance(time_value, dict) else 9)

    # Parse: +0106-09-29 or -0106-01-01
    m = re.match(r"([+-])(\d{4})-(\d{2})-(\d{2})", str(time_str))
    if not m:
        return (None, None)

    sign = -1 if m.group(1) == "-" else 1
    year = int(m.group(2)) * sign
    month = int(m.group(3))
    day = int(m.group(4))

    # Format as -0106 for BCE
    y_str = f"{year:+05d}" if -9999 <= year <= 9999 else str(year)

    if prec >= 11:
        # Day precision: point date
        return (f"{y_str}-{month:02d}-{day:02d}", f"{y_str}-{month:02d}-{day:02d}")
    if prec >= 10:
        # Month: 1st to last of month
        return (f"{y_str}-{month:02d}-01", f"{y_str}-{month:02d}-28")  # Approx last day
    if prec >= 9:
        # Year: Jan 1 to Dec 31
        return (f"{y_str}-01-01", f"{y_str}-12-31")
    if prec >= 8:
        # Decade: year 0 to year 9
        base = (year // 10) * 10
        return (f"{base:+05d}-01-01", f"{base + 9:+05d}-12-31")
    if prec >= 7:
        # Century: full century span
        base = (year // 100) * 100
        return (f"{base:+05d}-01-01", f"{base + 99:+05d}-12-31")

    return (None, None)


def format_iso_bce(year_bce: int) -> str:
    """Format BCE year as ISO (e.g. 106 BCE -> -0106)."""
    return f"{-abs(year_bce):+05d}" if year_bce > 0 else f"{year_bce:+05d}"


def parse_time_value_to_year_and_iso(
    time_str: str | None,
    precision: int = 9,
) -> tuple[int | None, str | None, str | None]:
    """
    Parse a Wikidata time string (from SPARQL or API) to (year, iso_earliest, iso_latest).
    time_str: e.g. "-0106-09-29T00:00:00Z" or "+0106-09-29T00:00:00Z" or "106-09-29T00:00:00Z" (CE)
    Returns (year, iso_earliest, iso_latest) for Person temporal backbone integration.
    """
    if not time_str or not isinstance(time_str, str):
        return (None, None, None)
    s = time_str.strip()
    if s and s[0].isdigit() and not s.startswith(("+", "-")):
        s = "+" + s  # CE years from SPARQL may omit +
    earliest, latest = normalise_wikidata_date({"time": s}, precision)
    if not earliest:
        return (None, None, None)
    m = re.match(r"([+-])(\d{4})-", earliest)
    if not m:
        return (None, earliest, latest)
    year = int(m.group(2)) * (-1 if m.group(1) == "-" else 1)
    return (year, earliest, latest)
