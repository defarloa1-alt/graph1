#!/usr/bin/env python3
"""
Subject Characterization Agent — holistic facet mapping with full context.

Gathers context from LCC, LCSH, Wikidata, Wikipedia (when available), then
calls LLM to characterize: facets, material_type, summary. One addressable
subject unit per input.

Usage:
  python scripts/backbone/subject/subject_characterization_agent.py --input output/nodes/lcc_roman_republic.csv
  python scripts/backbone/subject/subject_characterization_agent.py --identifier DG105 --provider openai
  python scripts/backbone/subject/subject_characterization_agent.py --identifier Q17167 --harvest-dir output/backlinks

With --harvest-dir: adds entity counts, linking properties, federation IDs (Pleiades, LGPN, VIAF) from harvest reports.

Env: OPENAI_API_KEY or PERPLEXITY_API_KEY
Output: output/subject_concepts/subject_characterization_results.json
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import requests

_PROJECT = Path(__file__).resolve().parents[3]
if str(_PROJECT) not in sys.path:
    sys.path.insert(0, str(_PROJECT))

from scripts.config_loader import OPENAI_API_KEY, PERPLEXITY_API_KEY

FACETS = [
    "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION", "CULTURAL",
    "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC", "ENVIRONMENTAL", "GEOGRAPHIC",
    "INTELLECTUAL", "LINGUISTIC", "MILITARY", "POLITICAL", "RELIGIOUS",
    "SCIENTIFIC", "SOCIAL", "TECHNOLOGICAL",
]

# What each facet encompasses — use to reason deeply, not superficially
FACET_SCOPES = """
- ARCHAEOLOGICAL: sites, excavations, artifacts, inscriptions, material culture
- ARTISTIC: art, sculpture, architecture, literature, poetry, aesthetics
- BIOGRAPHIC: individuals, lives, genealogy, prosopography
- COMMUNICATION: oratory, rhetoric, propaganda, media, messaging
- CULTURAL: customs, identity, ideology, cultural movements
- DEMOGRAPHIC: population, census, migration, settlement
- DIPLOMATIC: treaties, alliances, embassies, negotiations
- ECONOMIC: trade, finance, markets, land, currency
- ENVIRONMENTAL: climate, ecology, agriculture, natural resources
- GEOGRAPHIC: regions, territories, expansion, provinces
- INTELLECTUAL: philosophy, historiography, law, scholarship, ideas
- LINGUISTIC: languages, scripts, writing systems
- MILITARY: warfare, army, navy, battles, strategy, legions
- POLITICAL: governance, senate, magistrates, constitution, institutions
- RELIGIOUS: cult, ritual, temple, priesthood
- SCIENTIFIC: medicine, astronomy, mathematics, natural philosophy
- SOCIAL: class, patronage, slavery, kinship, social structure
- TECHNOLOGICAL: roads, aqueducts, military engineering, construction, concrete, siege equipment
"""

CHUNK_SIZE = 25
DEFAULT_INPUT = _PROJECT / "output" / "nodes" / "lcc_roman_republic.csv"
DEFAULT_OUTPUT = _PROJECT / "output" / "subject_concepts" / "subject_characterization_results.json"
DOMAIN_CONTEXT = "Roman Republic (509 BCE – 27 BCE)"


def fetch_wikidata_context(qid: str) -> dict | None:
    """Fetch Wikidata entity: description, P244, P2163, P1149, P1036, Wikipedia sitelink."""
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "format": "json",
        "props": "labels|descriptions|claims|sitelinks",
        "languages": "en",
    }
    headers = {"User-Agent": "ChrystallumBot/1.0 (subject-characterization; research project)"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        entities = data.get("entities", {})
        entity = entities.get(qid)
        if not entity or entity.get("missing"):
            return None

        # Description
        desc = entity.get("descriptions", {}).get("en", {}).get("value", "")

        # Claims: P244, P2163, P1149, P1036
        claims = entity.get("claims", {})
        def _first_val(pid):
            if pid not in claims:
                return None
            snak = claims[pid][0].get("mainsnak", {})
            dv = snak.get("datavalue", {})
            val = dv.get("value")
            if val is None:
                return None
            if isinstance(val, dict):
                return val.get("id") or val.get("amount") or str(val)
            return str(val)

        lcsh = _first_val("P244")
        fast = _first_val("P2163")
        lcc = _first_val("P1149")
        dewey = _first_val("P1036")

        # Wikipedia sitelink
        sitelinks = entity.get("sitelinks", {})
        enwiki = sitelinks.get("enwiki", {})
        wiki_title = enwiki.get("title") if enwiki else None
        wikipedia_url = f"https://en.wikipedia.org/wiki/{wiki_title.replace(' ', '_')}" if wiki_title else None

        label = entity.get("labels", {}).get("en", {}).get("value", qid)

        return {
            "qid": qid,
            "label": label,
            "description": desc,
            "lcsh_id": lcsh,
            "fast_id": fast,
            "lcc_code": lcc,
            "dewey": dewey,
            "wikipedia_url": wikipedia_url,
            "wikipedia_title": wiki_title,
        }
    except Exception as e:
        print(f"  [Wikidata] {e}", file=sys.stderr)
        return None


def fetch_wikipedia_extract(wikipedia_url: str, max_chars: int = 3000) -> str | None:
    """Fetch Wikipedia article intro (plain text) from URL. Returns None on failure."""
    if not wikipedia_url or "wikipedia.org/wiki/" not in wikipedia_url:
        return None
    try:
        title = wikipedia_url.split("/wiki/")[-1].replace("_", " ")
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": title,
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "format": "json",
        }
        headers = {"User-Agent": "ChrystallumBot/1.0 (subject-characterization; research project)"}
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            if pid != "-1" and "extract" in page:
                extract = page["extract"].strip()
                return extract[:max_chars] + ("..." if len(extract) > max_chars else "")
    except Exception as e:
        print(f"  [Wikipedia] {e}", file=sys.stderr)
    return None


# Federation external ID P-codes (inform facet: Pleiades=geo, LGPN=persons, etc.)
FEDERATION_PIDS = {"P1584": "Pleiades", "P1047": "LGPN", "P1696": "Trismegistos", "P214": "VIAF"}


def load_harvest_summary(harvest_dir: Path | None, qid: str) -> str | None:
    """
    Load harvest report for anchor QID and return a short summary for the prompt.
    Report has: accepted entities, properties, p31, external_ids, scoping.
    """
    if not harvest_dir or not harvest_dir.exists() or not qid:
        return None
    report_path = harvest_dir / f"{qid}_report.json"
    if not report_path.exists():
        # Try glob for subject_id_QID_report.json
        matches = list(harvest_dir.glob(f"*{qid}_report.json"))
        report_path = matches[0] if matches else None
    if not report_path:
        return None
    try:
        with open(report_path, encoding="utf-8") as f:
            report = json.load(f)
    except Exception as e:
        print(f"  [Harvest] {report_path.name}: {e}", file=sys.stderr)
        return None

    accepted = report.get("accepted", report.get("entities", []))
    if not accepted:
        return None

    # Aggregate
    prop_counts: dict[str, int] = {}
    p31_counts: dict[str, int] = {}
    fed_counts: dict[str, int] = {}
    for ent in accepted:
        for p in ent.get("properties", []):
            prop_counts[p] = prop_counts.get(p, 0) + 1
        for q in ent.get("p31", []):
            p31_counts[q] = p31_counts.get(q, 0) + 1
        for pid in FEDERATION_PIDS:
            if ent.get("external_ids", {}).get(pid):
                fed_counts[pid] = fed_counts.get(pid, 0) + 1

    scoping = report.get("scoping", {})
    counts = report.get("counts", {})

    lines = [
        f"Harvest: {len(accepted)} accepted entities",
        f"Scoping: temporal={scoping.get('temporal_scoped', 0)}, domain={scoping.get('domain_scoped', 0)}, unscoped={scoping.get('unscoped', 0)}",
    ]
    if prop_counts:
        top_props = sorted(prop_counts.items(), key=lambda x: -x[1])[:10]
        lines.append(f"Top linking properties: {', '.join(f'{p}({c})' for p, c in top_props)}")
    if fed_counts:
        lines.append(f"Federation IDs: {', '.join(f'{FEDERATION_PIDS.get(p, p)}({c})' for p, c in sorted(fed_counts.items(), key=lambda x: -x[1]))}")
    if p31_counts:
        top_p31 = sorted(p31_counts.items(), key=lambda x: -x[1])[:8]
        lines.append(f"Entity types (P31): {', '.join(f'{q}({c})' for q, c in top_p31)}")

    return "\n".join(lines)


def gather_context(unit: dict, harvest_dir: Path | None = None) -> dict:
    """
    Gather context for one addressable subject unit.
    unit: {identifier, lcc_code?, lcc_label?, qid?, lcsh_id?, ...}
    """
    ctx = {
        "identifier": unit.get("identifier") or unit.get("code") or unit.get("id") or "?",
        "lcc_code": unit.get("lcc_code") or unit.get("code"),
        "lcc_label": unit.get("lcc_label") or unit.get("label"),
        "parent_class": unit.get("parent_class"),
        "lcsh_id": unit.get("lcsh_id"),
        "lcsh_heading": unit.get("lcsh_heading"),
        "fast_id": unit.get("fast_id"),
        "dewey": unit.get("dewey"),
        "qid": unit.get("qid"),
        "wikidata_description": None,
        "wikipedia_url": None,
        "wikipedia_extract": None,
        "harvest_summary": None,
    }

    qid = unit.get("qid")
    if qid:
        wd = fetch_wikidata_context(qid)
        if wd:
            ctx["wikidata_description"] = wd.get("description")
            ctx["wikipedia_url"] = wd.get("wikipedia_url")
            ctx["lcsh_id"] = ctx["lcsh_id"] or wd.get("lcsh_id")
            ctx["fast_id"] = ctx["fast_id"] or wd.get("fast_id")
            ctx["lcc_code"] = ctx["lcc_code"] or wd.get("lcc_code")
            ctx["dewey"] = ctx["dewey"] or wd.get("dewey")
            if not ctx["lcc_label"]:
                ctx["lcc_label"] = wd.get("label")

    # Fetch Wikipedia content when we have a URL (guardrails: we control the sources)
    if ctx.get("wikipedia_url"):
        ctx["wikipedia_extract"] = fetch_wikipedia_extract(ctx["wikipedia_url"])

    # Load harvest summary when available (entities, properties, external IDs from backlink harvest)
    if qid and harvest_dir:
        ctx["harvest_summary"] = load_harvest_summary(harvest_dir, qid)

    return ctx


def build_batch_prompt(contexts: list[dict]) -> str:
    """Build holistic prompt for batch of units."""
    parts = []
    for i, ctx in enumerate(contexts, 1):
        wiki_block = ""
        if ctx.get("wikipedia_extract"):
            wiki_block = f"\n- Wikipedia extract:\n{ctx['wikipedia_extract']}"
        elif ctx.get("wikipedia_url"):
            wiki_block = f"\n- Wikipedia: {ctx['wikipedia_url']} (no extract fetched)"
        harvest_block = ""
        if ctx.get("harvest_summary"):
            harvest_block = f"\n- Harvest (backlink entities, properties, federation IDs):\n{ctx['harvest_summary']}"
        parent_line = f"\n- Parent class: {ctx['parent_class']}" if ctx.get("parent_class") else ""
        block = f"""### Concept {i}
- Identifier: {ctx['identifier']}
- LCC: {ctx['lcc_code'] or '(none)'} — {ctx['lcc_label'] or '(none)'}{parent_line}
- LCSH: {ctx['lcsh_heading'] or ctx['lcsh_id'] or '(none)'}
- FAST: {ctx['fast_id'] or '(none)'}
- Dewey: {ctx['dewey'] or '(none)'}
- Wikidata: {ctx['qid'] or '(none)'} — {ctx['wikidata_description'] or '(none)'}{wiki_block}{harvest_block}"""
        parts.append(block)

    concepts_text = "\n\n".join(parts)
    return f"""Task
You are a subject-domain expert for the Chrystallum knowledge graph.
Your task is to perform FACET TRIAGE for EACH concept.

For each concept and each facet, decide:

"Are there meaningful lines of inquiry for this facet here, based on the evidence I see?
If yes, how strong is the signal that this facet deserves follow-up analysis later?"

You are NOT writing an encyclopedia entry.
You are NOT deciding whether a facet is allowed or excluded in principle.
You are flagging where future work by that facet (and by SFA) might be fruitful,
and how strong that invitation should be.

Use ONLY the structured and textual signals provided for that concept.

Evidence you may use (only when present):
- LCC code and label, and parent class
- LCSH / FAST headings
- Wikidata QID and description
- Dewey number
- Wikipedia URL or extract
- Harvest summary: entity types (P31), linking properties, federation IDs
  (Pleiades, LGPN, Trismegistos, VIAF)

Evidence order (apply in this order, and mention it in your reasoning):
1) LCC label + parent class (e.g. "Sources", "Law", "Army").
2) P31 classes and scoping from the harvest summary.
3) Federation IDs:
   - Pleiades      → strong GEOGRAPHIC (and often ARCHAEOLOGICAL / ENVIRONMENTAL)
   - LGPN          → strong BIOGRAPHIC / SOCIAL
   - Trismegistos  → strong INTELLECTUAL (texts) and often ARCHAEOLOGICAL
   - VIAF          → strong INTELLECTUAL (authors, scholarship)
4) Short descriptions / Wikipedia extract.

If there is a conflict between prose and structural signals, TRUST THE STRUCTURAL SIGNALS.

Facet scopes (reference only, do not paraphrase):
- ARCHAEOLOGICAL: sites, excavations, artifacts, inscriptions, material culture
- ARTISTIC: art, sculpture, architecture, literature, poetry, aesthetics
- BIOGRAPHIC: individuals, lives, genealogy, prosopography
- COMMUNICATION: oratory, rhetoric, propaganda, media, messaging
- CULTURAL: customs, identity, ideology, cultural movements
- DEMOGRAPHIC: population, census, migration, settlement
- DIPLOMATIC: treaties, alliances, embassies, negotiations
- ECONOMIC: trade, finance, markets, land, currency
- ENVIRONMENTAL: climate, ecology, agriculture, natural resources
- GEOGRAPHIC: regions, territories, expansion, provinces
- INTELLECTUAL: philosophy, historiography, law, scholarship, ideas
- LINGUISTIC: languages, scripts, writing systems
- MILITARY: warfare, army, navy, battles, strategy, legions
- POLITICAL: governance, senate, magistrates, constitution, institutions
- RELIGIOUS: cult, ritual, temple, priesthood
- SCIENTIFIC: medicine, astronomy, mathematics, natural philosophy
- SOCIAL: class, patronage, slavery, kinship, social structure
- TECHNOLOGICAL: roads, aqueducts, engineering, construction, concrete, siege equipment

Facet triage and weighting rules (VERY IMPORTANT):
Think of each facet as a specialist asking:
"Do I have worthwhile lines of inquiry for this concept, and how strong is the
signal that my follow-up work would matter?"

Interpret weights as FOLLOW-UP STRENGTH for later graph-shaping:

- 0.0–0.2 = Very weak or no signal.
           You see little in the evidence that suggests useful follow-up
           along this facet, though it is not logically excluded.

- 0.4–0.6 = Moderate signal.
           The evidence suggests real lines of inquiry for this facet,
           but it does not seem to be the main lens.

- 0.8–1.0 = Strong signal.
           The evidence clearly indicates that this facet offers important
           lines of inquiry; SFA and facet agents should prioritize follow-up here.

Rules:
- For EVERY facet, you MUST assign a numeric weight between 0.0 and 1.0.
- At most THREE facets per concept may be in the 0.8–1.0 band (strong signal).
- It is acceptable for MANY facets to be 0.0–0.2 if the evidence is narrow.
  Do NOT inflate weights just because the facet could plausibly be involved in reality.
  Only respond to the evidence you see.

Reasoning requirements:
- For any facet with weight ≥ 0.4 OR exactly 0.0, include a SHORT reason.
- Each reason MUST cite specific evidence signals, e.g.:
  - "LCC label 'Army', P31 = military force → MILITARY strong follow-up signal."
  - "No Pleiades ID, no geographic wording in label or description → GEOGRAPHIC very weak signal."
- Do NOT rely on general background knowledge not present in the provided evidence.

Material type:
- primary  = original texts, laws, inscriptions, source documents
- secondary = scholarship, historiography, commentaries
- both     = mixes primary and secondary
- unclear  = cannot determine from the evidence

Choose ONE materialtype per concept, with a brief materialreason that cites evidence
(e.g. "Label 'Sources', no authors or commentary language → primary").

CONCEPTS WITH AGGREGATED CONTEXT
These are your ONLY sources. Do NOT use web search or training data beyond this.

{concepts_text}

Output format
Return ONLY a JSON array. ONE object per concept.

Each object MUST have:
- identifier: string (copied from the concept)
- facets: an array of 18 objects, covering ALL facets, each:
    - facet: facet key in UPPERCASE
    - weight: number between 0.0 and 1.0 (obey the triage rules above)
    - reason: short string explaining the weight when ≥ 0.4 OR 0.0
- materialtype: one of "primary", "secondary", "both", "unclear"
- materialreason: short string citing evidence
- wikipediaurl: URL string if present in evidence, otherwise null
- summary: one-sentence characterization of what this concept is about,
  based ONLY on the provided evidence (no extra facts).

Return ONLY valid JSON. No surrounding text, no comments.
""".strip()


def call_llm(prompt: str, provider: str) -> str:
    """Call OpenAI or Perplexity. Returns raw content. Guardrails: only use provided context."""
    system = "You are a subject-domain expert for the Chrystallum knowledge graph. Use ONLY the context provided in the user message. Do not use external knowledge, web search, or training data beyond the given sources. Base your characterization solely on Wikidata, LCC, LCSH, Wikipedia extract, and Harvest summary (when provided). You MUST evaluate every facet (all 18) for each concept, assigning weight 0.0–1.0. Respond ONLY with valid JSON."
    if provider == "openai":
        key = OPENAI_API_KEY
        if not key:
            raise ValueError("OPENAI_API_KEY not set (config.py, .env, or env var)")
        url = "https://api.openai.com/v1/chat/completions"
        payload = {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "temperature": 0.1}
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    else:
        key = PERPLEXITY_API_KEY
        if not key:
            raise ValueError("PERPLEXITY_API_KEY not set (config.py, .env, or env var)")
        url = "https://api.perplexity.ai/chat/completions"
        payload = {
            "model": "sonar-pro",
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "temperature": 0.1,
            "disable_search": True,  # Guardrails: only use provided context, no web search
        }
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    r = requests.post(url, json=payload, headers=headers, timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def extract_json(content: str) -> list:
    """Extract JSON array from LLM response."""
    text = content.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    start = text.find("[")
    end = text.rfind("]") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return json.loads(text)


def load_units_from_csv(path: Path, subclass_only: bool = False) -> list[dict]:
    """
    Load subject units from LCC CSV.
    If subclass_only: keep only subclasses (start==end, single call number), assign parent_class.
    """
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            start = float(r.get("start", 0))
            end = float(r.get("end", 0))
            rows.append({
                "identifier": r["id"],
                "code": r["id"],
                "lcc_code": r["id"],
                "label": r["label"],
                "lcc_label": r["label"],
                "prefix": r.get("prefix", ""),
                "start": start,
                "end": end,
                "is_range": start != end,
            })

    if not subclass_only:
        return [{k: v for k, v in u.items() if k not in ("prefix", "start", "end", "is_range")} for u in rows]

    # Subclass only: keep single call numbers (start == end)
    subclasses = [u for u in rows if not u["is_range"]]
    # Build class list (ranges) for parent lookup
    classes = [u for u in rows if u["is_range"]]

    def find_parent(sc: dict) -> str | None:
        """Find narrowest containing class (range) for this subclass."""
        p, s = sc["prefix"], sc["start"]
        containing = [c for c in classes if c["prefix"] == p and c["start"] <= s <= c["end"]]
        if not containing:
            return None
        # Narrowest = smallest span
        best = min(containing, key=lambda c: c["end"] - c["start"])
        return best["identifier"]

    units = []
    for u in subclasses:
        parent = find_parent(u)
        unit = {
            "identifier": u["identifier"],
            "code": u["identifier"],
            "lcc_code": u["identifier"],
            "label": u["label"],
            "lcc_label": u["label"],
        }
        if parent:
            unit["parent_class"] = parent
        units.append(unit)
    return units


def main():
    parser = argparse.ArgumentParser(description="Subject Characterization Agent")
    parser.add_argument("--input", type=Path, help="LCC CSV path (batch mode)")
    parser.add_argument("--identifier", type=str, help="Single unit: LCC code or QID")
    parser.add_argument("--provider", choices=["openai", "perplexity"], default="openai")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--harvest-dir", type=Path, default=None,
        help="Harvest reports dir (e.g. output/backlinks) — adds entity/property/federation-ID context when report exists")
    parser.add_argument("--prefix", type=str, default=None,
        help="Filter to LCC prefix only (e.g. DG for Ancient Rome, skip KJA/PA)")
    parser.add_argument("--subclass-only", action="store_true",
        help="Characterize subclasses only (single call numbers); assign parent_class for hierarchy")
    args = parser.parse_args()

    harvest_dir = args.harvest_dir

    # Resolve units
    if args.identifier:
        unit = {"identifier": args.identifier}
        if args.identifier.startswith("Q") and args.identifier[1:].isdigit():
            unit["qid"] = args.identifier
        else:
            unit["lcc_code"] = args.identifier
            unit["lcc_label"] = args.identifier  # placeholder
        units = [unit]
    elif args.input and args.input.exists():
        units = load_units_from_csv(args.input, subclass_only=args.subclass_only)
    else:
        # Default: use lcc_roman_republic.csv
        default = DEFAULT_INPUT
        if not default.exists():
            print(f"No input. Use --input <csv> or --identifier <code|qid>")
            sys.exit(1)
        units = load_units_from_csv(default, subclass_only=args.subclass_only)

    if args.subclass_only:
        with_parent = sum(1 for u in units if u.get("parent_class"))
        print(f"Subclass-only: {len(units)} subclasses, {with_parent} with parent_class")

    if args.prefix:
        prefix = args.prefix.upper()
        units = [u for u in units if (u.get("identifier") or u.get("code") or "").upper().startswith(prefix)]
        print(f"Filtered to prefix {prefix}: {len(units)} units")

    if args.limit:
        units = units[: args.limit]

    print(f"Units: {len(units)}")

    if args.dry_run:
        ctx = gather_context(units[0], harvest_dir)
        print("--- DRY RUN: First unit context ---")
        print(json.dumps(ctx, indent=2))
        return

    # Gather context for all (Wikidata when QID present, harvest when --harvest-dir and QID)
    print("Gathering context...")
    contexts = []
    for u in units:
        ctx = gather_context(u, harvest_dir)
        contexts.append(ctx)
        extras = []
        if ctx.get("wikipedia_extract"):
            extras.append("Wikipedia extract")
        elif ctx.get("wikipedia_url"):
            extras.append("Wikipedia URL only")
        if ctx.get("harvest_summary"):
            extras.append("Harvest")
        if extras:
            print(f"  {ctx['identifier']}: +{', '.join(extras)}")

    # Batch call LLM
    all_results = []
    for i in range(0, len(contexts), CHUNK_SIZE):
        chunk = contexts[i : i + CHUNK_SIZE]
        prompt = build_batch_prompt(chunk)
        print(f"Calling {args.provider} for batch {i // CHUNK_SIZE + 1} ({len(chunk)} units)...")
        content = call_llm(prompt, args.provider)
        results = extract_json(content)
        if not isinstance(results, list):
            results = [results]
        all_results.extend(results)
        print(f"  Got {len(results)} characterizations")

    # Enrich results with parent_class from context (for subclass-only runs)
    # Normalize LLM output keys (materialtype -> material_type, etc.) for pipeline compatibility
    ctx_by_id = {c["identifier"]: c for c in contexts}
    for r in all_results:
        ident = r.get("identifier")
        if ident and ident in ctx_by_id and ctx_by_id[ident].get("parent_class"):
            r["parent_class"] = ctx_by_id[ident]["parent_class"]
        # Normalize prompt output keys for pipeline compatibility
        if "materialtype" in r:
            r["material_type"] = r.pop("materialtype")
        if "materialreason" in r:
            r["material_reason"] = r.pop("materialreason")
        if "wikipediaurl" in r:
            r["wikipedia_url"] = r.pop("wikipediaurl")

    out = {
        "source": str(args.input or "single"),
        "provider": args.provider,
        "total_units": len(units),
        "total_results": len(all_results),
        "subclass_only": args.subclass_only,
        "contexts": contexts,
        "results": all_results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {args.output}")


if __name__ == "__main__":
    main()
