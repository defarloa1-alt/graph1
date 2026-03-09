"""
build_subject_schema.py

Takes a seed QID and produces a grounded SubjectConcept schema by reasoning
across classical library classification (LCC/LCSH) through the lens of
Chrystallum's 18 facets.

Philosophy:
  LCSH heading  = concept identity (unique, authoritative, stable)
  LCC code(s)   = shelving position(s) — plural, because one concept can
                  live in multiple LCC sections (e.g. Roman Law in DG and K)
  18 facets     = orthogonal capability axes, all active ones assigned
  Cipher        = SHA-256("SUBJECT_CONCEPT|qid|lcsh_id") — grounded identity

Output: JSON array of SubjectConcept proposals ready for Phase D curation.

Usage:
  python scripts/sca/build_subject_schema.py --qid Q17167 --label "Roman Republic"
"""

import argparse
import csv
import json
import hashlib
import sys
import os
import time
import urllib.request
import urllib.parse
from pathlib import Path

# load .env (picks up ANTHROPIC_API_KEY)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass

# ── paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
DG_CSV       = ROOT / "Subjects/LCC/dg_schedule.csv"
FACET_MAP    = ROOT / "subjectsAgentsProposal/files/lcc_to_chrystallum_facets_v1.1.json"
OUTPUT_DIR   = ROOT / "output/subject_schema"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── 18 facets (canonical) ─────────────────────────────────────────────────────
FACETS = [
    "Archaeological", "Artistic", "Biographic", "Communication",
    "Cultural", "Demographic", "Diplomatic", "Economic",
    "Environmental", "Geographic", "Intellectual", "Linguistic",
    "Military", "Political", "Religious", "Scientific",
    "Social", "Technological",
]

# ── load DG schedule ──────────────────────────────────────────────────────────
def load_dg_schedule():
    rows = []
    with open(DG_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows

# ── load facet mapping for DG ─────────────────────────────────────────────────
def load_dg_facet_map():
    with open(FACET_MAP, encoding="utf-8") as f:
        d = json.load(f)
    return d["mappings"].get("DG", {})

# ── cipher ────────────────────────────────────────────────────────────────────
def make_cipher(qid: str, lcsh_id: str) -> str:
    raw = f"SUBJECT_CONCEPT|{qid}|{lcsh_id}"
    return hashlib.sha256(raw.encode()).hexdigest()

# ── build prompt ──────────────────────────────────────────────────────────────
def build_prompt(qid: str, label: str, dg_rows: list, dg_facets: dict) -> tuple[str, str]:

    dg_table = "\n".join(
        f"  {r['code']:20} | {r['label']}"
        for r in dg_rows
    )

    dg_facet_table = "\n".join(
        f"  {code:25} | primary={v['facets'][0] if v['facets'] else '?':15} | all={v['facets']} | {v['label']}"
        for code, v in sorted(dg_facets.get("ranges", {}).items())
    )

    SYSTEM = """You are a subject cataloging specialist and knowledge architect working on
Chrystallum, a federated historical knowledge graph of the Roman Republic.

Your task is to build a MODERN SUBJECT SCHEMA for a given seed concept by reasoning
across classical library classification systems (LCC, LCSH) through the lens of
18 orthogonal facets.

## Core philosophy

LCSH heading  = concept IDENTITY. It is the unique authorized label, curated by the
                Library of Congress. Every proposed SubjectConcept MUST map to an
                LCSH heading (existing sh-ID) or be flagged NEEDS_LOOKUP.

LCC code(s)   = SHELVING POSITION(S). A physical book can only be shelved in one
                place, but an intellectual concept is not constrained. Roman Law
                legitimately lives at DG87 (History of Rome shelf) AND KJA 1-9999
                (Roman Law shelf). Both LCC codes belong on the same concept node.
                Cross-class issues MUST be resolved by merging, not splitting.

18 facets     = ORTHOGONAL CAPABILITY AXES. These are independent dimensions of
                scholarly perspective. A concept like Roman Magistracies is
                simultaneously Political (offices, cursus honorum), Biographic
                (the magistrates as persons), Military (imperium, command), Social
                (class prerequisites), and Economic (financial offices). Assign ALL
                that genuinely apply — do not limit to one.

Cipher        = SHA-256("SUBJECT_CONCEPT|qid|lcsh_id"). Computed from QID + LCSH ID.
                Provides O(1) vertex lookup from any authority system — no graph
                traversal needed. LCSH IDs are resolved by a separate API lookup
                step AFTER you produce this output — do NOT emit sh-IDs yourself.

## The 18 facets
Archaeological, Artistic, Biographic, Communication, Cultural, Demographic,
Diplomatic, Economic, Environmental, Geographic, Intellectual, Linguistic,
Military, Political, Religious, Scientific, Social, Technological

## Rules

1. MERGE cross-class duplicates. If two LCC codes point to the same intellectual
   concept, produce ONE SubjectConcept with both codes in lcc_codes[].

2. DO NOT create SubjectConcepts for period subdivisions (Early Republic,
   Middle Republic, Late Republic). These are temporal scopes, not subject concepts.
   The temporal structure belongs on the seed node itself.

3. DO create SubjectConcepts for THEMATIC topics that persist across periods:
   constitution, magistracies, army, economy, law, religion, etc.

4. Assign facets COMPLETELY. If a topic has 5 genuine facets, list all 5.
   Mark one as primary (the dominant scholarly perspective).

5. Flag GAPS — topics that clearly belong in the domain but lack an LCSH heading.
   Do not invent headings; flag them for human lookup.

6. Keep scope notes concise and domain-specific (Roman Republic context only).

## CRITICAL — IDs

You MUST NOT emit sh-IDs (e.g. sh85115211). You cannot reliably recall LCSH numeric
identifiers — they are opaque assigned codes, not derivable from heading text.
Omit `lcsh_id` entirely from your output. The heading STRING is sufficient;
IDs are resolved atomically by an API lookup pass after your response.

## Output format (strict JSON)

{
  "seed_qid": "Q17167",
  "seed_label": "Roman Republic",
  "subject_concepts": [
    {
      "label": "Roman Constitution",
      "lcsh_heading": "Rome--Constitutional history",
      "wikidata_qid": "Q...",
      "lcc_primary": "DG89",
      "lcc_codes": ["DG89", "DG91", "DG233"],
      "cross_class_notes": "Also shelved at JC81-93 (Political science - Ancient)",
      "facets": {
        "primary": "Political",
        "secondary": ["Legal", "Social", "Biographic"]
      },
      "scope_note": "...",
      "rationale": "why this is a coherent non-redundant concept"
    }
  ],
  "gaps": [
    {
      "label": "...",
      "description": "concept present in domain, no LCSH heading found",
      "lcc_codes": ["..."],
      "facets": ["..."]
    }
  ],
  "merge_log": [
    {
      "merged_from": ["DG87 Law", "DG155 Law general", "DG159 Private law",
                       "DG163 Criminal law", "DG167 Public law"],
      "merged_into": "Roman Law",
      "reason": "All are aspects of the same LCSH concept 'Roman law'"
    }
  ]
}"""

    USER = f"""Seed concept: {label} (Wikidata: {qid})
Temporal scope: 509 BCE – 27 BCE
LCSH identity: sh85115114 "Rome--History--Republic, 510-30 B.C."
MARC heading: 151 0$aRome$xHistory$yRepublic, 510-30 B.C.

## LCC DG Schedule (Ancient Rome, 66 rows)
This is the Library of Congress classification for Ancient Rome/Italy.
The thematic section DG21-190 provides the canonical decomposition of the domain.
The period section DG201-365 provides temporal subdivisions (DO NOT use as concepts).

{dg_table}

## Pre-computed facet signals for DG ranges (from lcc_to_chrystallum_facets_v1.1.json)
Use these as a starting signal, but reason beyond them — the mapping was built for
the general DG range, not specifically for the Republican period.

{dg_facet_table}

## Cross-class references you must consider

Roman Law:
  DG87        Law (shelved under History of Rome)
  DG155-167   Law general / private / criminal / public (same section, subdivided)
  KJA 1-9999  Roman law (shelved under European Law — same content, different audience)
  → These MERGE into one SubjectConcept

Roman Political Thought / Republicanism:
  DG89-101    Constitution, political institutions, magistracies, senate, assemblies
  JC81-93     Ancient political theory (Polybius, Cicero on the mixed constitution)
  → Republicanism as ideology may warrant its own concept separate from constitution

Roman Literature as historical source:
  DG143       Literature (historical context) — shelved under History
  PA6001-6971 Latin language and literature — shelved under Philology
  → The INTELLECTUAL and COMMUNICATION facets activate here

Roman Epigraphy:
  DG79        Inscriptions (shelved under History of Rome)
  CN (general inscriptions class)
  → Activates Linguistic, Archaeological, Biographic facets simultaneously

## Task

Propose the complete first-level SubjectConcept schema for {label} ({qid}).

Focus on the THEMATIC topics from DG21-190 that are meaningful for the
Republican period. Apply the merge, gap, and facet rules strictly.

Aim for 12-18 concepts — enough to cover the domain, few enough to be navigable.
Output strictly valid JSON matching the schema above."""

    return SYSTEM, USER


# ── call Claude API ───────────────────────────────────────────────────────────
def call_claude(system_prompt: str, user_prompt: str) -> str:
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


# ── resolve LCSH headings → sh-IDs via LoC suggest2 API ──────────────────────
LOC_SUGGEST = "https://id.loc.gov/authorities/subjects/suggest2"
LOC_SKOS    = "https://id.loc.gov/authorities/subjects/{}.skos.json"

def _normalize(s: str) -> str:
    """Lowercase, strip punctuation variations for comparison."""
    return s.lower().replace("\u2014", "--").replace("\u2013", "--").strip()


def _token_overlap(a: str, b: str) -> float:
    """Fraction of tokens in `a` that appear in `b`."""
    ta = set(_normalize(a).replace("--", " ").split())
    tb = set(_normalize(b).replace("--", " ").split())
    if not ta:
        return 0.0
    return len(ta & tb) / len(ta)


def _fetch_hits(q: str, mode: str, n: int = 5) -> list:
    params = urllib.parse.urlencode({"q": q, "count": n, "searchType": mode})
    req = urllib.request.Request(
        f"{LOC_SUGGEST}?{params}",
        headers={"User-Agent": "Chrystallum/1.0 (LCSH resolver)"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read()).get("hits", [])


def _loc_suggest(heading: str) -> tuple[str | None, str | None]:
    """
    Return (sh_id, found_label) for the best-matching LCSH heading, or (None, None).

    Strategy:
    1. leftAnchor on full heading (exact prefix match)
    2. keyword on full heading
    3. For subdivided headings (X--Y), keyword on main heading X and filter hits
       that contain subdivision Y
    Accepts a hit only if token overlap with expected heading >= 0.5.
    """
    try:
        heading_norm = _normalize(heading)
        parts = heading_norm.split("--")
        main = parts[0].strip()
        sub  = parts[1].strip() if len(parts) > 1 else None

        candidate_hits: list = []

        # Strategy 1: leftAnchor on full heading
        candidate_hits = _fetch_hits(heading, "leftAnchor", 5)

        # Strategy 2: keyword on full heading
        if not candidate_hits:
            candidate_hits = _fetch_hits(heading, "keyword", 5)

        # Strategy 3: for subdivided headings, search main heading and filter
        if not candidate_hits and sub:
            raw = _fetch_hits(main, "leftAnchor", 10)
            candidate_hits = [
                h for h in raw
                if sub in _normalize(h.get("aLabel") or h.get("label", ""))
            ]

        if not candidate_hits:
            return None, None

        # Score hits by token overlap with expected heading; require >= 0.5
        scored = []
        for h in candidate_hits:
            label = h.get("aLabel") or h.get("label", "")
            score = _token_overlap(heading, label)
            scored.append((score, h, label))
        scored.sort(key=lambda x: -x[0])

        best_score, best_hit, best_label = scored[0]
        if best_score < 0.5:
            return None, None

        sh_id = best_hit.get("uri", "").split("/")[-1]
        return sh_id, best_label

    except Exception:
        return None, None


def _verify_id(sh_id: str, expected_heading: str) -> bool:
    """Fetch the SKOS record and confirm token overlap >= 0.6 with expected heading."""
    url = LOC_SKOS.format(sh_id)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Chrystallum/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        uri = f"http://id.loc.gov/authorities/subjects/{sh_id}"
        node = next((n for n in data if n.get("@id") == uri), None)
        if not node:
            return False
        for lv in node.get("http://www.w3.org/2004/02/skos/core#prefLabel", []):
            actual = lv.get("@value", "")
            return _token_overlap(expected_heading, actual) >= 0.6
        return False
    except Exception:
        return False


def resolve_lcsh_ids(raw_json: dict) -> dict:
    """
    For each SubjectConcept that has an lcsh_heading but no verified lcsh_id,
    query the LoC suggest2 API, verify the returned ID, and write it back.
    Sets lcsh_id_status: 'verified' | 'unverified_best_match' | 'not_found'.
    """
    concepts = raw_json.get("subject_concepts", [])
    total = len(concepts)
    for i, sc in enumerate(concepts):
        heading = sc.get("lcsh_heading", "")
        existing_id = sc.get("lcsh_id", "")
        if existing_id and existing_id != "NEEDS_LOOKUP":
            sc["lcsh_id_status"] = "pre_verified"
            continue
        if not heading:
            sc["lcsh_id"] = "NEEDS_LOOKUP"
            sc["lcsh_id_status"] = "no_heading"
            continue

        print(f"  Resolving [{i+1}/{total}] {heading} ...", end=" ")
        sh_id, found_label = _loc_suggest(heading)
        if sh_id:
            verified = _verify_id(sh_id, heading)
            sc["lcsh_id"] = sh_id
            sc["lcsh_id_status"] = "verified" if verified else "unverified_best_match"
            sc["lcsh_id_resolved_label"] = found_label
            print(f"{sh_id} ({sc['lcsh_id_status']})")
        else:
            sc["lcsh_id"] = "NEEDS_LOOKUP"
            sc["lcsh_id_status"] = "not_found"
            print("NOT FOUND")
        time.sleep(0.4)  # be polite to LoC API

    return raw_json


# ── parse and enrich output ───────────────────────────────────────────────────
def enrich_proposals(raw_json: dict) -> dict:
    """Add computed ciphers to proposals that have both qid and lcsh_id."""
    for sc in raw_json.get("subject_concepts", []):
        qid = sc.get("wikidata_qid") or ""
        lcsh_id = sc.get("lcsh_id") or ""
        if qid and lcsh_id and lcsh_id not in ("NEEDS_LOOKUP", ""):
            sc["concept_cipher"] = make_cipher(qid, lcsh_id)
        else:
            sc["concept_cipher"] = None
            sc["cipher_status"] = "pending_curation"
    return raw_json


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--qid",   default="Q17167",        help="Seed Wikidata QID")
    parser.add_argument("--label", default="Roman Republic", help="Seed label")
    parser.add_argument("--dry-run", action="store_true",   help="Print prompt only, no API call")
    args = parser.parse_args()

    dg_rows   = load_dg_schedule()
    dg_facets = load_dg_facet_map()

    system_prompt, user_prompt = build_prompt(args.qid, args.label, dg_rows, dg_facets)

    if args.dry_run:
        print("=" * 80)
        print("SYSTEM PROMPT")
        print("=" * 80)
        print(system_prompt)
        print()
        print("=" * 80)
        print("USER PROMPT")
        print("=" * 80)
        print(user_prompt)
        return

    print(f"Calling Claude for {args.qid} ({args.label})...")
    raw_text = call_claude(system_prompt, user_prompt)

    # extract JSON block
    import re
    json_match = re.search(r"\{[\s\S]*\}", raw_text)
    if not json_match:
        print("ERROR: No JSON found in response")
        print(raw_text)
        sys.exit(1)

    proposals = json.loads(json_match.group())
    print("Resolving LCSH IDs against LoC API...")
    proposals = resolve_lcsh_ids(proposals)
    proposals = enrich_proposals(proposals)

    out_path = OUTPUT_DIR / f"{args.qid}_subject_schema.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(proposals, f, indent=2, ensure_ascii=False)

    print(f"Written: {out_path}")
    print(f"Concepts proposed: {len(proposals.get('subject_concepts', []))}")
    print(f"Gaps flagged:      {len(proposals.get('gaps', []))}")
    print(f"Merges logged:     {len(proposals.get('merge_log', []))}")

    # summary to stdout
    print()
    print("PROPOSED SUBJECT CONCEPTS:")
    for sc in proposals.get("subject_concepts", []):
        cipher_ok = "Y" if sc.get("concept_cipher") else "?"
        id_status = sc.get("lcsh_id_status", "?")[:10]
        lcsh_id   = sc.get("lcsh_id", "NEEDS_LOOKUP")
        sys.stdout.buffer.write(
            f"  {cipher_ok} {sc['label']:40} | primary={sc['facets']['primary']:15}"
            f"| lcc={sc.get('lcc_primary','?'):8} | {lcsh_id:20} | {id_status}\n"
            .encode("utf-8", errors="replace")
        )


if __name__ == "__main__":
    main()
