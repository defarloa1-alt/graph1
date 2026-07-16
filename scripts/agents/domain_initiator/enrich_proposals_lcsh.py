#!/usr/bin/env python3
"""
Enrich SC proposals with LCSH identifiers for proposals that have no Wikidata candidate QIDs.

Queries id.loc.gov suggest API with the proposal label, picks the best match,
and writes lcsh_id back to the proposals JSON.

Usage:
  python scripts/agents/domain_initiator/enrich_proposals_lcsh.py
  python scripts/agents/domain_initiator/enrich_proposals_lcsh.py --seed Q17167 --dry-run
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUGGEST_URL = "https://id.loc.gov/authorities/subjects/suggest/?q={}"
HEADERS = {"User-Agent": "Chrystallum/1.0 (LCSH enrichment; research project)"}


def lcsh_suggest(query: str, timeout: int = 15) -> list[tuple[str, str]]:
    """
    Query id.loc.gov suggest API.
    Returns list of (label, lcsh_id) tuples, best match first.
    Response format: [query, [labels], [info], [uris]]
    """
    url = SUGGEST_URL.format(urllib.parse.quote(query))
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"    [LCSH] Error for '{query}': {e}")
        return []

    if not isinstance(data, list) or len(data) < 4:
        return []

    labels = data[1] if isinstance(data[1], list) else []
    uris = data[3] if isinstance(data[3], list) else []

    results = []
    for label, uri in zip(labels, uris):
        # Extract sh ID from URI like http://id.loc.gov/authorities/subjects/sh85089712
        if "/subjects/sh" in uri:
            lcsh_id = uri.rstrip("/").split("/")[-1]
            results.append((label, lcsh_id))

    return results


from proposal_backbone import SCOPE_LCSH_QUERIES as SCOPE_QUERIES


def build_queries(proposal: dict) -> list[str]:
    """Return ordered query candidates for a proposal."""
    scope_key = proposal.get("scope_key", "")
    return SCOPE_QUERIES.get(scope_key, [proposal["label"]])


def best_lcsh(proposal: dict) -> tuple[str | None, str | None]:
    """
    Find the best LCSH match for a proposal using suggest API.
    Tries multiple query strategies. Returns (lcsh_label, lcsh_id) or (None, None).
    """
    for query in build_queries(proposal):
        results = lcsh_suggest(query)
        if results:
            lcsh_label, lcsh_id = results[0]
            print(f"    -> '{lcsh_label}' ({lcsh_id})  [q: '{query}']")
            return lcsh_label, lcsh_id
        time.sleep(0.3)

    return None, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="Q17167")
    parser.add_argument("--proposals-dir", type=Path, default=ROOT / "output" / "di_proposals")
    parser.add_argument("--dry-run", action="store_true", help="Print results without writing")
    args = parser.parse_args()

    proposals_path = args.proposals_dir / f"{args.seed}_proposals.json"
    if not proposals_path.exists():
        print(f"Not found: {proposals_path}")
        return

    with open(proposals_path, encoding="utf-8") as f:
        data = json.load(f)

    proposals = data.get("proposals", [])
    targets = [p for p in proposals if not p.get("candidate_qids")]

    print(f"Proposals total: {len(proposals)}")
    print(f"Needs LCSH:      {len(targets)}")
    print()

    enriched = 0
    failed = 0

    for p in targets:
        facet = p.get("source_facet", "?")
        label = p.get("label", "?")
        print(f"  [{facet}] {label}")

        if p.get("lcsh_id"):
            print(f"    already has lcsh_id={p['lcsh_id']}, skipping")
            continue

        lcsh_label, lcsh_id = best_lcsh(p)
        time.sleep(0.5)

        if lcsh_id:
            p["lcsh_id"] = lcsh_id
            p["lcsh_label"] = lcsh_label
            enriched += 1
        else:
            print(f"    no match found")
            failed += 1

    print()
    print(f"Enriched: {enriched}  No match: {failed}")

    if not args.dry_run:
        with open(proposals_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Written: {proposals_path}")
    else:
        print("(dry-run — not written)")


if __name__ == "__main__":
    main()
