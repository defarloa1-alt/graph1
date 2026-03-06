#!/usr/bin/env python3
"""
DPRR → Wikidata LLM Matcher — Group C alignment

Matches Group C entities (DPRR-only, no Wikidata QID) to Wikidata items using:
  1. Graph context (label, offices, family, dates)
  2. Wikidata search (wbsearchentities)
  3. Claude reasoning over context + search results
  4. Verification (compare candidate claims to DPRR data)

Output: JSON proposals to output/dprr_wikidata_proposals/ for review.
Optional --apply writes verified qid to graph.

Usage:
  python scripts/federation/dprr_wikidata_matcher.py --limit 10
  python scripts/federation/dprr_wikidata_matcher.py --limit 50 --apply
  python scripts/federation/dprr_wikidata_matcher.py --dry-run  # no LLM, show sample context

Requires: ANTHROPIC_API_KEY, Neo4j (.env)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

_root = Path(__file__).resolve().parents[2]
_scripts = _root / "scripts"
sys.path.insert(0, str(_scripts))
sys.path.insert(0, str(_root))

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
except ImportError:
    NEO4J_URI = NEO4J_USERNAME = NEO4J_PASSWORD = NEO4J_DATABASE = None

try:
    import anthropic
except ImportError:
    anthropic = None

USER_AGENT = "Chrystallum/1.0 (DPRR-Wikidata matcher)"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
OUT_DIR = _root / "output" / "dprr_wikidata_proposals"
QID_RE = re.compile(r"^Q[1-9]\d*$")

# Roman praenomen abbreviations -> full form (for deterministic Wikipedia match)
PRAENOMEN = {
    "a": "aulus", "ap": "appius", "c": "gaius", "cn": "gnaeus", "d": "decimus",
    "l": "lucius", "m": "marcus", "m'": "manius", "mam": "mamercus",
    "n": "numerius", "p": "publius", "q": "quintus", "ser": "servius",
    "sex": "sextus", "sp": "spurius", "t": "titus", "ti": "tiberius",
}

_fed = Path(__file__).resolve().parent
try:
    if str(_fed) not in sys.path:
        sys.path.insert(0, str(_fed))
    from wikipedia_office_lists import (
        load_cache,
        get_candidates_for_year,
        extract_year_from_offices,
    )
    WIKIPEDIA_OFFICE_KEYS = ("consuls", "praetors")  # consul first (senior office)
except ImportError:
    load_cache = get_candidates_for_year = extract_year_from_offices = None
    WIKIPEDIA_OFFICE_KEYS = ()


def _get_anthropic_key() -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key and (_root / ".env").exists():
        for line in (_root / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"')
                break
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment or .env")
    return api_key


def load_group_c_context(session, limit: int | None = None) -> list[dict]:
    """Load Group C entities (dprr_uri, no qid) with offices, family, dates."""
    query = """
        MATCH (e:Entity)
        WHERE e.dprr_uri IS NOT NULL AND (e.qid IS NULL OR e.qid = '')
        WITH e
        OPTIONAL MATCH (e)-[r:POSITION_HELD]->(p:Position)
        WITH e, collect(DISTINCT {pos: p.label, name: p.label_name, year_start: coalesce(r.start_year, r.year)}) AS offices
        OPTIONAL MATCH (e)-[rel:FATHER_OF|MOTHER_OF|PARENT_OF|SIBLING_OF|SPOUSE_OF|STEPPARENT_OF]-(other:Entity)
        WITH e, offices,
             collect(DISTINCT {type: type(rel), target: other.label, target_qid: other.qid}) AS family
        RETURN e.dprr_id AS dprr_id, e.dprr_uri AS dprr_uri,
               e.label AS label, e.label_dprr AS label_dprr, e.label_latin AS label_latin,
               e.birth_date AS birth_date, e.death_date AS death_date,
               [x IN offices WHERE x.pos IS NOT NULL] AS offices,
               [x IN family WHERE x.target IS NOT NULL] AS family
        ORDER BY e.dprr_id
    """
    if limit:
        query = query.rstrip() + f"\n        LIMIT {limit}"
    result = session.run(query)
    rows = []
    for r in result:
        rec = dict(r)
        rec["offices"] = [o for o in (rec.get("offices") or []) if o.get("pos")]
        rec["family"] = [f for f in (rec.get("family") or []) if f.get("target")]
        rows.append(rec)
    return rows


def wikidata_search(label: str, label_latin: str | None = None, limit: int = 10) -> list[dict]:
    """Search Wikidata by label. Tries label, then label_latin, then last word (nomen/cognomen)."""
    seen_ids: set[str] = set()
    out: list[dict] = []

    def _search(term: str) -> None:
        if not term or len(term.strip()) < 2:
            return
        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "search": term.strip(),
            "limit": limit,
        }
        try:
            r = requests.get(WIKIDATA_API, params=params, headers={"User-Agent": USER_AGENT}, timeout=15)
            r.raise_for_status()
            data = r.json()
            for item in data.get("search", []):
                qid = item.get("id", "")
                if QID_RE.match(qid) and qid not in seen_ids:
                    seen_ids.add(qid)
                    out.append({
                        "id": qid,
                        "label": item.get("label", ""),
                        "description": item.get("description", ""),
                    })
        except Exception:
            pass

    _search(label)
    if label_latin and label_latin != label:
        _search(label_latin)
    # Fallback: last word (cognomen/nomen) often finds more
    for part in (label, label_latin or ""):
        if part:
            words = part.split()
            if len(words) > 1:
                _search(words[-1])
            break
    return out[:limit]


def fetch_wikidata_claims(qid: str) -> dict | None:
    """Fetch main claims for a QID (P569, P570, P6863, P39, P31, etc.)."""
    query = f"""
    SELECT ?prop ?value ?valueLabel WHERE {{
      wd:{qid} ?prop ?value .
      VALUES ?prop {{ wdt:P22 wdt:P25 wdt:P26 wdt:P27 wdt:P31 wdt:P39 wdt:P569 wdt:P570 wdt:P6863 }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    try:
        r = requests.get(WIKIDATA_SPARQL, params={"query": query}, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()
        claims = {}
        for b in data.get("results", {}).get("bindings", []):
            prop = (b.get("prop", {}).get("value") or "").split("/")[-1]
            val = b.get("value", {}).get("value", "")
            val_short = val.split("/")[-1] if "/" in val else val
            if prop not in claims:
                claims[prop] = []
            claims[prop].append({"value": val_short, "label": (b.get("valueLabel", {}).get("value", "") or "").strip()})
        return {"qid": qid, "claims": claims}
    except Exception:
        return None


def call_claude(system: str, user: str, model: str = "claude-sonnet-4-20250514", max_tokens: int = 1024) -> str:
    """Call Claude API."""
    client = anthropic.Anthropic(api_key=_get_anthropic_key())
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text


def propose_qid(dprr_ctx: dict, search_results: list[dict]) -> dict:
    """
    Ask Claude to propose a Wikidata QID from DPRR context + search results.
    Returns {proposed_qid, confidence, reasoning} or {proposed_qid: null, ...}.
    """
    system = """You are matching Roman Republic persons from DPRR (Digital Prosopography of the Roman Republic) to Wikidata items.
Given DPRR context (label, offices, family, dates) and Wikidata search results, propose the best-matching QID if one exists.
Respond with valid JSON only, no markdown:
{"proposed_qid": "Q123" or null, "confidence": "high"|"medium"|"low"|"none", "reasoning": "brief explanation"}
If no good match exists, use proposed_qid: null and confidence: "none".
Prefer items that are human (P31=Q5) and Roman Republic era. Reject obvious mismatches (different centuries, wrong person).
IMPORTANT: Candidates with "source": "wikipedia_praetors" come from the Wikipedia List of Roman praetors for the same year and office. When the DPRR label matches or abbreviates the candidate name (e.g. Cn. Cornelius Scipio Hispanus = Gnaeus Cornelius Scipio Hispanus, M. Atilius = Marcus Atilius Serranus), STRONGLY prefer that candidate - it is high-confidence."""

    ctx_lines = [
        f"DPRR ID: {dprr_ctx.get('dprr_id', '')}",
        f"Label: {dprr_ctx.get('label', '')}",
        f"Label (Latin): {dprr_ctx.get('label_latin', '') or '-'}",
        f"Offices: {json.dumps(dprr_ctx.get('offices', []))}",
        f"Family: {json.dumps(dprr_ctx.get('family', []))}",
        f"Birth: {dprr_ctx.get('birth_date', '-')}",
        f"Death: {dprr_ctx.get('death_date', '-')}",
    ]
    search_str = json.dumps(search_results, indent=2) if search_results else "[]"
    user = "DPRR context:\n" + "\n".join(ctx_lines) + "\n\nWikidata search results:\n" + search_str

    try:
        text = call_claude(system, user)
        if not text or not text.strip():
            return {"proposed_qid": None, "confidence": "none", "reasoning": "Empty LLM response"}
        # Extract JSON from response (handle markdown code blocks)
        text = text.strip()
        for prefix in ("```json", "```"):
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
            if text.endswith("```"):
                text = text[:-3].strip()
        # Find first { and last }
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]
        out = json.loads(text)
        qid = out.get("proposed_qid")
        if qid and not QID_RE.match(str(qid)):
            out["proposed_qid"] = None
            out["confidence"] = "none"
            out["reasoning"] = (out.get("reasoning", "") + " [invalid QID format]").strip()
        return out
    except json.JSONDecodeError as e:
        return {"proposed_qid": None, "confidence": "none", "reasoning": f"JSON parse error: {e}"}
    except Exception as e:
        return {"proposed_qid": None, "confidence": "none", "reasoning": str(e)}


def verify_match(dprr_ctx: dict, qid: str) -> dict:
    """
    Verify proposed QID against DPRR. Check P6863 (should be absent or match), dates, offices.
    Returns {verified: bool, score: float, notes: str}.
    """
    wd = fetch_wikidata_claims(qid)
    if not wd:
        return {"verified": False, "score": 0.0, "notes": "Could not fetch Wikidata claims"}

    claims = wd.get("claims", {})
    score = 0.5  # base
    notes = []

    # P31=Q5 (human) — expected
    if "P31" in claims:
        vals = [c.get("value") for c in claims["P31"]]
        if "Q5" in vals:
            score += 0.2
            notes.append("human")
        else:
            notes.append("not human")
            return {"verified": False, "score": 0.0, "notes": "; ".join(notes)}

    # P6863 — if present, must match dprr_id
    p6863 = [c.get("value") for c in claims.get("P6863", [])]
    if p6863:
        if str(dprr_ctx.get("dprr_id", "")) in p6863:
            score += 0.3
            notes.append("P6863 matches")
        else:
            return {"verified": False, "score": 0.0, "notes": f"P6863 mismatch: {p6863}"}

    # Dates — soft check (Wikidata often has full ISO, DPRR may have year only)
    dprr_birth = str(dprr_ctx.get("birth_date", "") or "")
    dprr_death = str(dprr_ctx.get("death_date", "") or "")
    wd_birth = "".join(c.get("value", "") for c in claims.get("P569", []))[:10]
    wd_death = "".join(c.get("value", "") for c in claims.get("P570", []))[:10]
    if dprr_birth and wd_birth and dprr_birth[:4] in wd_birth:
        score += 0.1
        notes.append("birth year consistent")
    if dprr_death and wd_death and dprr_death[:4] in wd_death:
        score += 0.1
        notes.append("death year consistent")

    verified = score >= 0.6
    return {"verified": verified, "score": min(1.0, score), "notes": "; ".join(notes) or "no strong signals"}


def run_matcher(limit: int | None, dry_run: bool, apply: bool) -> int:
    if not NEO4J_URI or not NEO4J_PASSWORD:
        print("NEO4J_URI and NEO4J_PASSWORD required (.env)", file=sys.stderr)
        return 1
    if not dry_run and not anthropic:
        print("anthropic required. Run: pip install anthropic", file=sys.stderr)
        return 1

    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD))
    db = NEO4J_DATABASE or "neo4j"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = OUT_DIR / f"proposals_{ts}.json"

    with driver.session(database=db) as session:
        rows = load_group_c_context(session, limit=limit)

    if not rows:
        print("No Group C entities found.")
        return 0

    print(f"DPRR -> Wikidata Matcher - {len(rows)} Group C entities, dry_run={dry_run}, apply={apply}")

    # Load Wikipedia office lists (consuls, praetors) from cache for office+year lookup
    wikipedia_caches: dict[str, dict] = {}
    if load_cache and get_candidates_for_year and WIKIPEDIA_OFFICE_KEYS:
        for key in WIKIPEDIA_OFFICE_KEYS:
            try:
                cache = load_cache(office_key=key)
                if cache:
                    wikipedia_caches[key] = cache
                    print(f"  Wikipedia {key} list loaded")
            except Exception as e:
                print(f"  Wikipedia {key} skip: {e}")
    print()

    proposals = []
    applied = 0

    for i, ctx in enumerate(rows):
        dprr_id = ctx.get("dprr_id", "")
        label = ctx.get("label", "") or ctx.get("label_latin", "") or f"dprr_{dprr_id}"
        print(f"  [{i+1}/{len(rows)}] {label[:50]} (dprr:{dprr_id})")

        if dry_run:
            proposals.append({
                "dprr_id": dprr_id,
                "label": label,
                "dry_run": True,
                "context_sample": {k: v for k, v in ctx.items() if k in ("offices", "family", "birth_date", "death_date")},
            })
            continue

        search_results = wikidata_search(label, label_latin=ctx.get("label_latin"), limit=8)

        # Add Wikipedia office-list candidates (consuls, praetors) when office+year match
        wp_candidates: list[dict] = []
        if wikipedia_caches and get_candidates_for_year and extract_year_from_offices:
            offices = ctx.get("offices", [])
            for office_key in WIKIPEDIA_OFFICE_KEYS:
                cache = wikipedia_caches.get(office_key)
                if not cache:
                    continue
                year = extract_year_from_offices(offices, prefer_office=office_key)
                if year:
                    cands = get_candidates_for_year(cache, year, offices, office_key=office_key)
                    seen_ids = {c["id"] for c in wp_candidates}
                    for c in cands:
                        if c["id"] not in seen_ids:
                            seen_ids.add(c["id"])
                            wp_candidates.append(c)

        if wp_candidates:
            seen = {r["id"] for r in search_results}
            for c in wp_candidates:
                if c["id"] not in seen:
                    seen.add(c["id"])
                    search_results.insert(0, c)  # Prefer Wikipedia candidates

            # Deterministic match: DPRR nomen+cognomen in Wikipedia candidate; praenomen when single nomen
            dprr_label = (label or "").replace("?", "").replace("\\'", "'").strip()
            dprr_tokens = re.findall(r"[A-Za-z]+", dprr_label)
            dprr_words = [w for w in dprr_tokens if len(w) > 1 and w.lower() not in ("re", "f", "n", "l")]
            dprr_sig = [w for w in dprr_words if len(w) > 2]  # nomen/cognomen only
            praenomen = PRAENOMEN.get((dprr_tokens[0] or "").lower()) if dprr_tokens else None
            for c in wp_candidates:
                wd_label = (c.get("label") or "").replace("?", "").strip()
                wd_lower = wd_label.lower()
                if not all(w.lower() in wd_lower for w in dprr_sig):
                    continue
                if len(dprr_sig) == 1 and praenomen and praenomen not in wd_lower:
                    continue  # single nomen: require praenomen match
                proposal = {"proposed_qid": c["id"], "confidence": "high", "reasoning": f"Wikipedia list match: {wd_label}"}
                break
            else:
                proposal = propose_qid(ctx, search_results)
        else:
            proposal = propose_qid(ctx, search_results)
        proposed_qid = proposal.get("proposed_qid")

        wp_count = sum(1 for r in search_results if (r.get("source") or "").startswith("wikipedia_"))
        rec = {
            "dprr_id": dprr_id,
            "dprr_uri": ctx.get("dprr_uri"),
            "label": label,
            "proposed_qid": proposed_qid,
            "confidence": proposal.get("confidence", ""),
            "reasoning": proposal.get("reasoning", ""),
            "search_results_count": len(search_results),
            "wikipedia_praetors_candidates": wp_count,
        }

        if proposed_qid:
            verification = verify_match(ctx, proposed_qid)
            rec["verification"] = verification
            if verification.get("verified") and apply:
                with driver.session(database=db) as session:
                    session.run("""
                        MATCH (e:Entity {dprr_uri: $dprr_uri})
                        SET e.qid = $qid
                    """, dprr_uri=ctx.get("dprr_uri"), qid=proposed_qid)
                applied += 1
                print(f"    -> {proposed_qid} (verified, applied)")
            else:
                print(f"    -> {proposed_qid} ({proposal.get('confidence', '')}) {verification.get('notes', '')}")
        else:
            print(f"    -> no match ({proposal.get('reasoning', '')[:60]})")

        proposals.append(rec)

    driver.close()

    out_path.write_text(json.dumps({"proposals": proposals, "meta": {"count": len(proposals), "applied": applied}}, indent=2), encoding="utf-8")
    print()
    print(f"Wrote {out_path}")
    if apply:
        print(f"Applied qid to graph: {applied} entities")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="DPRR → Wikidata LLM matcher for Group C")
    ap.add_argument("--limit", type=int, default=None, help="Max Group C entities to process")
    ap.add_argument("--dry-run", action="store_true", help="No LLM calls, show context sample")
    ap.add_argument("--apply", action="store_true", help="Write verified qid to graph")
    args = ap.parse_args()
    return run_matcher(limit=args.limit, dry_run=args.dry_run, apply=args.apply)


if __name__ == "__main__":
    sys.exit(main())
