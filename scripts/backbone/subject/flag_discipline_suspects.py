#!/usr/bin/env python3
"""
Flag discipline registry rows that may be non-disciplines for manual review.

Catches slippage from P279/P527 expansion: named persons, biological taxa, places,
occupational -ist/-ologist labels, technical specs, natural languages (not the study
of languages), and generic concepts.

Output:
  - output/discipline_suspects_flagged.csv (all rows + flag_reason column)
  - output/discipline_suspects_review.csv (flagged rows only, for curation)

Usage:
  python scripts/backbone/subject/flag_discipline_suspects.py
  python scripts/backbone/subject/flag_discipline_suspects.py -i output/discipline_taxonomy_new.csv
"""

import argparse
import csv
import re
from pathlib import Path

_PROJECT = Path(__file__).resolve().parents[3]

# Known non-disciplines (slipped through prior filters)
KNOWN_BAD_QIDS = {
    "Q235955",   # Clarice Lispector (person)
    "Q160",      # Cetacea (biological taxon)
    "Q46202",    # Bose–Einstein condensate (physics concept)
    "Q220",      # Rome (place)
    "Q5185",     # Nematoda (biological taxon)
    "Q7161124",  # Universidade de Passo Fundo (university)
    "Q1864603",  # Tibetologist (occupational -ist)
    "Q4773904",  # anthropologist (occupational -ist)
    "Q1147173",  # Malformed (label = QID)
    "Q1370467",  # EuroVoc (vocabulary/spec)
    "Q2551624",  # IPv6 (protocol)
    "Q10322548", # MQTT (protocol)
    "Q11802245", # Integrated software (software category)
    "Q2755217",  # UNIMARC (bibliographic format)
    "Q7048977",  # abstract entity (philosophical concept)
    "Q189533",   # academic degree (credential)
    "Q3882459",  # acoustic wave (physics concept)
    "Q1914636",  # activity (generic concept)
    "Q26185",    # Quaternary (geological period)
}

# Occupational role: label is exactly an -ist or -ologist (person who studies)
# Exclude: list (data structure), specialist (generic)
OCCUPATIONAL_SUFFIX = re.compile(r"^[a-z]+(?:ist|ologist)$", re.I)
OCCUPATIONAL_BLOCKLIST = {"list", "specialist", "scientist"}

# University/institution (non-English terms that slipped through)
UNIVERSITY_PATTERN = re.compile(
    r"\b(universidade|universidad|universität|université|university|college|institute|academy)\b",
    re.I
)

# Technical spec / protocol (all-caps or CamelCase abbreviations)
TECH_SPEC_PATTERN = re.compile(r"^(IPv[46]|MQTT|UNIMARC|API|UML|JSON|XML|HTML|RDF|SKOS|MARC)$")

# Malformed: label looks like a QID
MALFORMED_QID_LABEL = re.compile(r"^Q\d+$")

# Natural languages — the language itself, not the study of it.
# "English" is Q1860 (academic discipline AND language). We flag the bare name;
# "English studies", "English linguistics", "English literature" are legitimate disciplines.
DISCIPLINE_SUFFIXES = {"studies", "linguistics", "literature", "philology", "language studies"}
NATURAL_LANGUAGES = {
    "english", "french", "german", "spanish", "chinese", "japanese", "arabic",
    "russian", "italian", "portuguese", "korean", "hindi", "turkish", "dutch",
    "polish", "swedish", "greek", "latin", "hebrew", "persian", "thai",
    "vietnamese", "malay", "bengali", "ukrainian", "czech", "romanian",
    "hungarian", "finnish", "norwegian", "danish", "indonesian", "tagalog",
    "swahili", "yoruba", "zulu", "tamil", "urdu", "punjabi", "gujarati",
    "catalan", "basque", "welsh", "irish", "scottish gaelic", "breton",
    "albanian", "serbian", "croatian", "bosnian", "slovenian", "slovak",
    "bulgarian", "macedonian", "estonian", "latvian", "lithuanian",
    "icelandic", "maltese", "afrikaans", "hausa", "amharic", "somali",
    "tibetan", "burmese", "khmer", "lao", "mongolian", "kazakh",
    "uzbek", "azerbaijani", "georgian", "armenian", "nepali", "sinhala",
}

# Regional language variants (P527 children of language items)
REGIONAL_VARIANT_PATTERN = re.compile(
    r"^(American|British|Australian|Canadian|Indian|South African|Nigerian|"
    r"Caribbean|Scottish|Irish|New Zealand|European|Pakistani|Jamaican|"
    r"Hong Kong|Singapore|Philippine|Belizean|Quebec|African American)\s+\w+$",
    re.I,
)


def _flag_row(row: dict) -> str | None:
    """Return flag reason if row is suspect, else None."""
    qid = (row.get("qid") or "").strip()
    label = (row.get("label") or "").strip()

    if qid in KNOWN_BAD_QIDS:
        return "known_bad_qid"

    if MALFORMED_QID_LABEL.match(label):
        return "malformed_label"

    if label.lower() not in OCCUPATIONAL_BLOCKLIST and OCCUPATIONAL_SUFFIX.match(label):
        return "occupational_ist"

    if UNIVERSITY_PATTERN.search(label):
        return "university"

    if TECH_SPEC_PATTERN.match(label):
        return "tech_spec"

    # Natural language (bare name, not "X studies" / "X linguistics" / "X literature")
    label_lower = label.lower()
    if label_lower in NATURAL_LANGUAGES:
        # Check it's not "X studies" etc. (bare name = language, not discipline)
        return "natural_language"
    # "X language" but not "X language studies"
    if label_lower.endswith(" language") and not any(label_lower.endswith(s) for s in DISCIPLINE_SUFFIXES):
        stem = label_lower.replace(" language", "").strip()
        if stem and len(stem) > 2:
            return "natural_language"
    # Regional variant (American English, British English, etc.)
    if REGIONAL_VARIANT_PATTERN.match(label):
        return "regional_language_variant"

    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input",
        type=Path,
        default=_PROJECT / "output" / "discipline_taxonomy_new.csv"
    )
    parser.add_argument("-o", "--output-dir", type=Path, default=_PROJECT / "output")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}")
        return

    rows = []
    with open(args.input, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        for r in reader:
            rows.append(r)

    if "flag_reason" not in fieldnames:
        fieldnames.append("flag_reason")

    flagged = []
    for row in rows:
        reason = _flag_row(row)
        row["flag_reason"] = reason or ""
        if reason:
            flagged.append(row)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Full file with flag column
    full_path = args.output_dir / "discipline_suspects_flagged.csv"
    with open(full_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {full_path} ({len(rows)} rows, {len(flagged)} flagged)")

    # Flagged-only for review
    review_path = args.output_dir / "discipline_suspects_review.csv"
    with open(review_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(flagged)
    print(f"Wrote {review_path} ({len(flagged)} rows for manual review)")

    if flagged:
        by_reason = {}
        for r in flagged:
            reason = r["flag_reason"]
            by_reason[reason] = by_reason.get(reason, 0) + 1
        print("\nFlag breakdown:")
        for reason, n in sorted(by_reason.items(), key=lambda x: -x[1]):
            print(f"  {reason}: {n}")


if __name__ == "__main__":
    main()
