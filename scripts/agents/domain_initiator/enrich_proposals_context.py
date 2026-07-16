#!/usr/bin/env python3
"""
Enrich DI SubjectConcept proposals with labeled bibliography and web research context.

For each decomposition proposal:
  1. Resolve supporting_works IDs to titles/authors/years (corpus + OpenAlex)
  2. Query Perplexity (online) for a scholarly overview of the scope label
  3. Optionally resolve missing LCSH tethers via id.loc.gov
  4. Re-run CCS validation

Usage:
  python scripts/agents/domain_initiator/enrich_proposals_context.py --seed Q17167
  python scripts/agents/domain_initiator/enrich_proposals_context.py --seed Q17167 --limit 3
  python scripts/agents/domain_initiator/enrich_proposals_context.py --seed Q17167 --resolve-lcsh
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "agents" / "domain_initiator"))

from proposal_backbone import (  # noqa: E402
    build_work_index,
    label_supporting_works,
    validate_ccs,
)
from enrich_proposals_lcsh import best_lcsh  # noqa: E402
from scripts.tools.lcc_code_utils import (  # noqa: E402
    label_lcc_code,
    label_lcc_codes,
    load_lcc_label_index,
)
from scripts.agents.republic_graph_context import get_republic_graph_context_prompt_block  # noqa: E402

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
DEFAULT_MODEL = "sonar"


def fetch_web_overview(
    *,
    label: str,
    seed_label: str,
    seed_qid: str,
    source_facet: str,
    description: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    graph_context_block: str = "",
) -> dict[str, Any]:
    """Perplexity online search — Google AI-overview-style synthesis for SFA orientation."""
    query = f"{label} {seed_label} ancient history"
    system = (
        "You are a scholarly research assistant for historical knowledge graph SubjectConcept scoping. "
        "Provide concise, factual overviews grounded in current scholarship. "
        "Always cite sources as markdown links [Title](URL)."
    )
    if graph_context_block and graph_context_block.strip() not in system:
        system = f"{system.rstrip()}\n\n{graph_context_block}"
    user = f"""Research topic for a {source_facet} facet SubjectConcept under {seed_label}:

**Scope label:** {label}
**Scope description:** {description or "(none)"}

Write a 2-3 paragraph scholarly overview covering:
1. What historians/scholars mean by this topic in a {seed_label} context
2. Key subtopics, institutions, events, or methodological concerns
3. Canonical sources or reference works scholars use

End with a "Sources:" section listing 3-6 URLs (Wikipedia, worldhistory.org, JSTOR abstracts, university pages, Pleiades, DPRR, etc.)."""

    payload = {
        "model": model,
        "temperature": 0.2,
        "max_tokens": 900,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    req = urllib.request.Request(
        PERPLEXITY_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    synthesis = data["choices"][0]["message"]["content"].strip()
    sources = _extract_sources(synthesis)
    return {
        "query": query,
        "provider": "perplexity",
        "model": model,
        "synthesis": synthesis,
        "sources": sources,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def _extract_sources(text: str) -> list[dict[str, str]]:
    """Pull markdown [title](url) links from synthesis."""
    sources: list[dict[str, str]] = []
    seen: set[str] = set()
    for match in re.finditer(r"\[([^\]]+)\]\((https?://[^)]+)\)", text):
        title, url = match.group(1).strip(), match.group(2).strip()
        if url not in seen:
            seen.add(url)
            sources.append({"title": title, "url": url})
    return sources


def enrich_proposal_context(
    proposal: dict,
    *,
    seed_label: str,
    seed_qid: str,
    work_index: dict[str, dict[str, Any]],
    web_cache: dict[str, dict],
    api_key: str | None,
    resolve_lcsh: bool,
    skip_web: bool,
    graph_context_block: str = "",
) -> dict:
    """Add supporting_works_detail, web_context; optionally fix LCSH + revalidate."""
    work_ids = proposal.get("supporting_works") or []
    proposal["supporting_works_detail"] = label_supporting_works(
        work_ids, work_index, fetch_missing=True
    )

    cache_key = proposal.get("scope_key") or proposal.get("label", "")
    if not skip_web and api_key:
        if cache_key in web_cache and web_cache[cache_key].get("synthesis"):
            proposal["web_context"] = web_cache[cache_key]
        else:
            try:
                ctx = fetch_web_overview(
                    label=proposal.get("label", ""),
                    seed_label=seed_label,
                    seed_qid=seed_qid,
                    source_facet=proposal.get("source_facet", ""),
                    description=proposal.get("description", ""),
                    api_key=api_key,
                    graph_context_block=graph_context_block,
                )
                web_cache[cache_key] = ctx
                proposal["web_context"] = ctx
            except Exception as exc:
                proposal["web_context"] = {
                    "query": cache_key,
                    "error": str(exc),
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

    authority = proposal.get("authority") or {}
    needs_lcsh = not (
        authority.get("lcsh_id")
        or authority.get("fast_id")
        or authority.get("topic_qid")
        or proposal.get("candidate_qids")
    )
    if resolve_lcsh and needs_lcsh and not proposal.get("lcsh_id"):
        lcsh_label, lcsh_id = best_lcsh(proposal)
        if lcsh_id:
            authority["lcsh_id"] = lcsh_id
            authority["lcsh_label"] = lcsh_label
            authority["tether_source"] = "loc_suggest_enrichment"
            proposal["authority"] = authority
            proposal["lcsh_id"] = lcsh_id
            proposal["lcsh_label"] = lcsh_label
            proposal["authority_label"] = lcsh_label

    proposal["validation"] = validate_ccs(proposal)
    return proposal


def _lcc_code_value(value: str | dict | None) -> str:
    if isinstance(value, dict):
        return str(value.get("code") or "")
    return str(value or "")


def label_proposal_codes(
    proposal: dict,
    lcc_index: dict[str, str],
    qid_labels: dict[str, str] | None = None,
    lcsh_labels: dict[str, str] | None = None,
) -> dict:
    """Attach human labels to LCC and other authority codes."""
    primary_raw = _lcc_code_value(proposal.get("lcc_primary"))
    if primary_raw:
        proposal["lcc_primary"] = label_lcc_code(primary_raw, lcc_index)

    raw_codes = proposal.get("lcc_codes") or []
    if raw_codes:
        codes = [_lcc_code_value(c) for c in raw_codes]
        proposal["lcc_codes"] = label_lcc_codes([c for c in codes if c], lcc_index)

    authority = proposal.get("authority") or {}
    auth_primary = _lcc_code_value(authority.get("lcc_primary"))
    if auth_primary:
        authority["lcc_primary"] = label_lcc_code(auth_primary, lcc_index)
    auth_codes = authority.get("lcc_codes") or []
    if auth_codes:
        codes = [_lcc_code_value(c) for c in auth_codes]
        authority["lcc_codes"] = label_lcc_codes([c for c in codes if c], lcc_index)

    lcsh_id = proposal.get("lcsh_id") or authority.get("lcsh_id")
    lcsh_label = proposal.get("lcsh_label") or authority.get("lcsh_label")
    if lcsh_id:
        proposal["lcsh"] = {"id": lcsh_id, "label": lcsh_label or lcsh_id}

    topic_lcsh_id = authority.get("topic_lcsh_id")
    if topic_lcsh_id:
        topic_lcsh_label = authority.get("topic_lcsh_label")
        if not topic_lcsh_label and lcsh_labels:
            topic_lcsh_label = lcsh_labels.get(topic_lcsh_id)
        authority["topic_lcsh"] = {
            "id": topic_lcsh_id,
            "label": topic_lcsh_label or topic_lcsh_id,
        }

    topic_qid = authority.get("topic_qid")
    if topic_qid:
        proposal["topic_anchor"] = {
            "qid": topic_qid,
            "label": authority.get("topic_qid_label") or qid_labels.get(topic_qid, topic_qid)
            if qid_labels
            else authority.get("topic_qid_label") or topic_qid,
        }

    raw_candidates = proposal.get("candidate_qids") or []
    if raw_candidates and isinstance(raw_candidates[0], str) and qid_labels:
        proposal["candidate_qids"] = [
            {"qid": qid, "label": qid_labels.get(qid, qid)} for qid in raw_candidates
        ]

    fast_id = authority.get("fast_id")
    if fast_id:
        authority["fast"] = {
            "id": fast_id,
            "label": authority.get("fast_label") or fast_id,
        }

    proposal["authority"] = authority
    return proposal


def load_qid_labels(seed: str) -> dict[str, str]:
    path = ROOT / "JSON" / "wikidata" / "derived" / f"{seed}_seed_index.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("labels") or {}


def load_lcsh_labels_from_proposals(proposals: list[dict]) -> dict[str, str]:
    """Collect known LCSH labels already on proposals."""
    out: dict[str, str] = {}
    for p in proposals:
        for key in ("lcsh_id",):
            lid = p.get(key)
            lbl = p.get("lcsh_label")
            if lid and lbl:
                out[lid] = lbl
        auth = p.get("authority") or {}
        if auth.get("lcsh_id") and auth.get("lcsh_label"):
            out[auth["lcsh_id"]] = auth["lcsh_label"]
        if auth.get("topic_lcsh_id") and auth.get("topic_lcsh_label"):
            out[auth["topic_lcsh_id"]] = auth["topic_lcsh_label"]
    return out


def finalize_proposal_for_review(
    proposal: dict,
    lcc_index: dict[str, str],
    qid_labels: dict[str, str],
    lcsh_labels: dict[str, str],
) -> dict:
    """Shape proposal for human/SFA review: labeled works + top-level overview."""
    detail = proposal.get("supporting_works_detail") or proposal.get("supporting_works") or []
    if detail and isinstance(detail[0], dict):
        proposal["supporting_works"] = detail
    elif detail and isinstance(detail[0], str):
        # Bare work_id list — leave for a later label pass
        pass

    web = proposal.get("web_context") or {}
    synthesis = web.get("synthesis")
    if synthesis:
        proposal["scholarly_overview"] = synthesis
    if web.get("sources"):
        proposal["reference_links"] = web["sources"]

    proposal.pop("supporting_works_detail", None)
    proposal.pop("web_context", None)
    return label_proposal_codes(proposal, lcc_index, qid_labels, lcsh_labels)


def build_review_document(data: dict, lcc_index: dict[str, str], seed: str) -> dict:
    """Return proposals.json-shaped document ready for review (no bare-ID works)."""
    qid_labels = load_qid_labels(seed)
    lcsh_labels = load_lcsh_labels_from_proposals(data.get("proposals", []))
    out = dict(data)
    out["document_type"] = "di_proposals_enriched"
    out["proposals"] = [
        finalize_proposal_for_review(dict(p), lcc_index, qid_labels, lcsh_labels)
        for p in data.get("proposals", [])
    ]
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich DI proposals with labels + web context")
    parser.add_argument("--seed", default="Q17167")
    parser.add_argument("--seed-label", default="Roman Republic")
    parser.add_argument("--proposals-dir", type=Path, default=ROOT / "output" / "di_proposals")
    parser.add_argument("--training-dir", type=Path, default=ROOT / "output" / "di_training")
    parser.add_argument("--limit", type=int, default=0, help="Max proposals to enrich (0=all)")
    parser.add_argument("--resolve-lcsh", action="store_true", help="Query id.loc.gov for missing tethers")
    parser.add_argument("--skip-web", action="store_true", help="Label works only; skip Perplexity")
    parser.add_argument("--reshape-only", action="store_true",
                        help="Reshape existing proposals (labeled works + overview) without API calls")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    from scripts.config_loader import PERPLEXITY_API_KEY

    proposals_path = args.proposals_dir / f"{args.seed}_proposals.json"
    enriched_path = args.proposals_dir / f"{args.seed}_proposals_enriched.json"
    cache_dir = args.proposals_dir / ".cache"
    cache_path = cache_dir / f"{args.seed}_web_context_cache.json"

    if not proposals_path.exists():
        print(f"Not found: {proposals_path}")
        sys.exit(1)

    with open(proposals_path, encoding="utf-8") as f:
        data = json.load(f)

    proposals = data.get("proposals", [])
    targets = [p for p in proposals if p.get("proposal_type") == "decomposition"]
    if args.limit:
        targets = targets[: args.limit]

    if args.reshape_only:
        lcc_index = load_lcc_label_index(ROOT)
        review_doc = build_review_document(data, lcc_index, args.seed)
        if not args.dry_run:
            with open(enriched_path, "w", encoding="utf-8") as f:
                json.dump(review_doc, f, indent=2, ensure_ascii=False)
            with open(proposals_path, "w", encoding="utf-8") as f:
                json.dump(review_doc, f, indent=2, ensure_ascii=False)
        print(f"Reshaped {len(review_doc['proposals'])} proposals")
        print(f"  Review file: {enriched_path}")
        print(f"  Updated:     {proposals_path}")
        return

    web_cache: dict[str, dict] = {}
    if cache_path.exists():
        try:
            with open(cache_path, encoding="utf-8") as f:
                web_cache = json.load(f)
        except json.JSONDecodeError:
            web_cache = {}

    work_index = build_work_index(args.training_dir, args.seed)
    api_key = PERPLEXITY_API_KEY if not args.skip_web else None
    if not args.skip_web and not api_key:
        print("WARNING: PPLX_API_KEY not set — skipping web context (works labels only)")

    graph_context_block = get_republic_graph_context_prompt_block(args.seed)
    print(f"Graph context loaded ({len(graph_context_block)} chars)")

    print(f"Enriching {len(targets)} decomposition proposals from {proposals_path.name}")
    print(f"  Work index: {len(work_index)} entries")
    print(f"  Web cache: {len(web_cache)} entries")
    print(f"  Resolve LCSH: {args.resolve_lcsh}")
    print()

    enriched_count = 0
    ccs_before = sum(1 for p in proposals if p.get("validation", {}).get("ccs_pass"))

    for i, p in enumerate(targets, 1):
        label = p.get("label", "?")
        facet = p.get("source_facet", "?")
        cache_key = p.get("scope_key") or p.get("label", "")
        was_cached = cache_key in web_cache and bool(web_cache[cache_key].get("synthesis"))
        print(f"  [{i}/{len(targets)}] [{facet}] {label}")

        enrich_proposal_context(
            p,
            seed_label=args.seed_label,
            seed_qid=args.seed,
            work_index=work_index,
            web_cache=web_cache,
            api_key=api_key,
            resolve_lcsh=args.resolve_lcsh,
            skip_web=args.skip_web,
            graph_context_block=graph_context_block,
        )
        enriched_count += 1
        works = p.get("supporting_works_detail") or []
        labeled = sum(1 for w in works if w.get("title") and w["title"] != w.get("work_id"))
        web_status = "skip"
        if p.get("web_context", {}).get("synthesis"):
            web_status = "cached" if was_cached else "fetched"
        elif p.get("web_context", {}).get("error"):
            web_status = "error"
        print(f"    works labeled: {labeled}/{len(works)}  web: {web_status}  "
              f"ccs={'OK' if p.get('validation', {}).get('ccs_pass') else 'FAIL'}")
        if not args.skip_web and api_key:
            time.sleep(0.8)

    ccs_after = sum(1 for p in proposals if p.get("validation", {}).get("ccs_pass"))
    data["enriched_at"] = datetime.now(timezone.utc).isoformat()
    data["enrichment"] = {
        "supporting_works_labeled": True,
        "web_context_provider": "perplexity" if api_key and not args.skip_web else None,
        "lcsh_resolved": args.resolve_lcsh,
        "ccs_pass_before": ccs_before,
        "ccs_pass_after": ccs_after,
    }

    review_doc = build_review_document(data, load_lcc_label_index(ROOT), args.seed)

    if not args.dry_run:
        cache_dir.mkdir(parents=True, exist_ok=True)
        with open(enriched_path, "w", encoding="utf-8") as f:
            json.dump(review_doc, f, indent=2, ensure_ascii=False)
        with open(proposals_path, "w", encoding="utf-8") as f:
            json.dump(review_doc, f, indent=2, ensure_ascii=False)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(web_cache, f, indent=2, ensure_ascii=False)
        # Remove legacy cache location if present
        legacy_cache = args.proposals_dir / f"{args.seed}_web_context_cache.json"
        if legacy_cache.exists() and legacy_cache != cache_path:
            legacy_cache.unlink()
        print(f"\nReview file: {enriched_path}")
        print(f"Updated:     {proposals_path}")
        print(f"Cache:       {cache_path}  (internal — not for review)")
    else:
        print("\n(dry-run — not written)")

    print(f"\nCCS pass: {ccs_before} -> {ccs_after} / {len(proposals)}")
    print(f"Enriched: {enriched_count} proposals")


if __name__ == "__main__":
    main()
