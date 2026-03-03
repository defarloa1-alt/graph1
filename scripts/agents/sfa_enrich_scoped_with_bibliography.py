#!/usr/bin/env python3
"""
SFA Enrich Scoped with Bibliography — Attach works to each scoped item.

WorldCat primary (LCC match) + OpenAlex OA + Open Syllabus Galaxy supplement.
LCSH resolution via id.loc.gov (label, broader, narrower, alt_labels).

Output: scoped JSON with "bibliography" (title, uri, oa_url, toc_url, galaxy_search_url),
"lcsh_resolved" (when --lcsh), "dewey_explanation" (when --dewey), "lcc_explanation" (when --lcc).

Usage:
  python scripts/agents/sfa_enrich_scoped_with_bibliography.py --input output/sfa_scoped/POLITICAL_Q17167_20260302_170241.json
  python scripts/agents/sfa_enrich_scoped_with_bibliography.py --no-openalex  # Skip OpenAlex
  python scripts/agents/sfa_enrich_scoped_with_bibliography.py --no-opensyllabus  # Skip Open Syllabus Galaxy
  python scripts/agents/sfa_enrich_scoped_with_bibliography.py --lcsh  # Resolve LCSH via id.loc.gov
  python scripts/agents/sfa_enrich_scoped_with_bibliography.py --dewey  # Add Dewey explanations (LLM)
  python scripts/agents/sfa_enrich_scoped_with_bibliography.py --lcc   # Add LCC code explanations (LLM)
"""

import argparse
import json
import re
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

try:
    from scripts.agents.openalex_oa_works import fetch_oa_works
except ImportError:
    fetch_oa_works = None
try:
    from scripts.agents.opensyllabus_galaxy import fetch_galaxy_works
except ImportError:
    fetch_galaxy_works = None
try:
    from scripts.agents.lcsh_resolve import resolve_lcsh
except ImportError:
    resolve_lcsh = None
try:
    from scripts.agents.gather_books import enrich_bibliography
except ImportError:
    enrich_bibliography = None


def _lcc_prefix_for_match(code: str) -> str:
    """Prefix for matching: DG200-265 -> DG2, JC -> JC, KJA2100 -> KJA2."""
    if not code:
        return ""
    c = re.sub(r"[-\s].*", "", code.strip().upper())
    m = re.match(r"^([A-Z]+)(\d)?", c)
    if m:
        return m.group(1) + (m.group(2) or "")
    return c[:4]


def _work_matches_lcc(work_lcc: str | None, code: str) -> bool:
    """True if work's LCC matches the code. DG205 matches DG or DG200-265; JC85 matches JC."""
    if not work_lcc or not code:
        return False
    w = work_lcc.strip().upper().split()[0]  # DG205.M56 -> DG205
    prefix = _lcc_prefix_for_match(code)
    return w.startswith(prefix) or (len(prefix) >= 2 and w.startswith(prefix[:2]))


def load_worldcat(worldcat_path: Path) -> list[dict]:
    """Load WorldCat nodes from survey JSON."""
    if not worldcat_path.exists():
        return []
    with open(worldcat_path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("nodes", [])


def load_scoped(scoped_path: Path) -> dict:
    """Load scoped output."""
    with open(scoped_path, encoding="utf-8") as f:
        return json.load(f)


LOC_TOC_BASE = "https://catdir.loc.gov/catdir/toc"


def _worldcat_summary(w: dict) -> dict:
    props = w.get("properties", {})
    lccn = props.get("lccn")
    uri = w.get("uri") or (f"http://lccn.loc.gov/{lccn}" if lccn else None)
    out = {
        "title": w.get("label", "") or "",
        "lccn": lccn,
        "lcc": props.get("lcc"),
        "uri": uri,
        "source": "WorldCat",
    }
    if lccn:
        out["toc_url"] = f"{LOC_TOC_BASE}/{lccn}.html"
    return out


def _merge_bibliography(primary: list[dict], supplement: list[dict], cap: int = 25) -> list[dict]:
    """Merge primary + supplement, dedupe by title, cap total."""
    seen = set()
    out = []
    for w in primary + supplement:
        key = (w.get("title") or "").lower()[:80]
        if key and key in seen:
            continue
        seen.add(key)
        out.append(w)
        if len(out) >= cap:
            break
    return out


def enrich(
    scoped: dict,
    worldcat: list[dict],
    facet: str | None = None,
    use_openalex: bool = True,
    use_opensyllabus: bool = True,
    use_gather_books: bool = True,
    domain_label: str = "Roman Republic",
) -> dict:
    """Add bibliography. WorldCat primary (LCC match). OpenAlex OA + Open Syllabus Galaxy as supplement.
    When use_gather_books: enrich Open Library works with ia_url, toc_url, publisher from OL editions."""
    out = scoped.get("output", scoped)
    if not out:
        return scoped

    facet = facet or out.get("facet", "")
    works = [w for w in worldcat if not facet or w.get("properties", {}).get("semantic_facet") == facet]
    if not works and worldcat:
        works = worldcat

    def works_for_prefix(code: str) -> list[dict]:
        if not code:
            return []
        matched = [w for w in works if _work_matches_lcc(w.get("properties", {}).get("lcc"), code)]
        seen = set()
        unique = []
        for w in matched:
            k = w.get("properties", {}).get("lccn") or w.get("id")
            if k and k not in seen:
                seen.add(k)
                unique.append(w)
        return [_worldcat_summary(w) for w in unique[:25]]

    # Supplement: OpenAlex OA + Open Syllabus Galaxy (syllabus-assigned works)
    supplement: list[dict] = []
    if fetch_oa_works and use_openalex and domain_label:
        supplement.extend(fetch_oa_works(domain_label, per_page=25))
    if fetch_galaxy_works and use_opensyllabus and domain_label:
        supplement.extend(fetch_galaxy_works(domain_label, size=25))

    # scoped_lcc — WorldCat primary (LCC = Roman Republic survey)
    for item in out.get("scoped_lcc", []):
        code = item.get("code", "")
        wc = works_for_prefix(code)
        item["bibliography"] = _merge_bibliography(wc, supplement)

    # scoped_disciplines — WorldCat primary
    for item in out.get("scoped_disciplines", []):
        lcc = item.get("lcc")
        wc = works_for_prefix(lcc) if lcc else []
        item["bibliography"] = _merge_bibliography(wc, supplement)

    # scoped_lcsh — no LCC match in WorldCat; supplement only
    for item in out.get("scoped_lcsh", []):
        item["bibliography"] = _merge_bibliography([], supplement, cap=25)
        if not item["bibliography"]:
            item["bibliography_note"] = "LCSH→works requires OpenAlex/OpenSyllabus or LC SRU"

    # scoped_entities — WorldCat key works (+ supplement)
    general_wc = [_worldcat_summary(w) for w in works[:25]] if works else []
    general = _merge_bibliography(general_wc, supplement, cap=25)
    for item in out.get("scoped_entities", []):
        item["bibliography"] = general
        item["bibliography_note"] = "Key works from Roman Republic survey"

    # Gather books: enrich Open Library works with ia_url, toc_url, publisher
    if enrich_bibliography and use_gather_books:
        for item in out.get("scoped_lcc", []) + out.get("scoped_disciplines", []) + out.get("scoped_lcsh", []) + out.get("scoped_entities", []):
            bib = item.get("bibliography", [])
            if bib:
                item["bibliography"] = enrich_bibliography(bib, max_enrich=15, timeout=6)

    return scoped


def _get_anthropic_key() -> str | None:
    import os
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key and (_root / ".env").exists():
        for line in (_root / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                key = line.split("=", 1)[1].strip()
                break
    return key or None


DEWEY_SYSTEM_PROMPT = """You are a Dewey Decimal Classification expert. For a given Dewey number and its context (discipline/subject label), provide a concise explanation in the following structure. Use markdown. Be concise but include:

1. **Where it sits in Dewey** — 3-digit parent (e.g. 300 = Social sciences), 320s division (e.g. 321–328), and this number's place.

2. **What it covers conceptually** — Main topics and scope of this class.

3. **How it can be extended** — Decimal expansion (e.g. 323.11 for ethnic groups), use of tables when relevant.

4. **Practical reading** — When you see this number in a record, what does it mean?

Keep it to ~400–600 words. No preamble."""


def _explain_dewey(dewey: str, label: str, api_key: str) -> str:
    """Call Claude to explain a Dewey number in context."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=DEWEY_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Dewey number: **{dewey}**\nContext: {label}"}],
    )
    return msg.content[0].text


def enrich_dewey(scoped: dict) -> None:
    """Add dewey_explanation to scoped items that have a dewey field. Requires ANTHROPIC_API_KEY."""
    api_key = _get_anthropic_key()
    if not api_key:
        print("  Dewey: skipped (ANTHROPIC_API_KEY not set)")
        return
    out = scoped.get("output", scoped)
    if not out:
        return
    items_with_dewey = []
    for section in ("scoped_disciplines", "scoped_lcc", "scoped_lcsh"):
        for item in out.get(section, []):
            d = item.get("dewey")
            if d and isinstance(d, str) and d.strip():
                items_with_dewey.append((item, d, item.get("label", "")[:40]))
    if not items_with_dewey:
        print("  Dewey: no items with dewey field")
        return
    seen_dewey: dict[str, str] = {}
    for item, dewey, label in items_with_dewey:
        if dewey in seen_dewey:
            item["dewey_explanation"] = seen_dewey[dewey]
            continue
        try:
            expl = _explain_dewey(dewey, label, api_key)
            item["dewey_explanation"] = expl
            seen_dewey[dewey] = expl
        except Exception as e:
            item["dewey_explanation"] = None
            item["dewey_explanation_error"] = str(e)
    print(f"  Dewey: explained {len(items_with_dewey)} items ({len(seen_dewey)} unique numbers)")


LCC_SYSTEM_PROMPT = """You are a Library of Congress Classification (LCC) expert. For a given LCC code and its context (subject/discipline label), provide a concise explanation in the following structure. Use markdown. Be concise but include:

1. **Where it sits in LCC** — Parent class (e.g. J = Political science), letter range (e.g. JA–JS, JN), and this code's place in the schedule.

2. **What it covers conceptually** — Main topics and scope. E.g. JN = political institutions and public administration of Europe (national governments, constitutions, parliaments, executive structures).

3. **Practical reading** — When you see this LCC code on a record, what does it tell you about the work's subject and shelving?

Keep it to ~200–400 words. No preamble."""


def _explain_lcc(code: str, label: str, api_key: str) -> str:
    """Call Claude to explain an LCC code in context."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=LCC_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"LCC code: **{code}**\nContext: {label}"}],
    )
    return msg.content[0].text


def enrich_lcc(scoped: dict) -> None:
    """Add lcc_explanation to scoped items that have an LCC code. Requires ANTHROPIC_API_KEY."""
    api_key = _get_anthropic_key()
    if not api_key:
        print("  LCC: skipped (ANTHROPIC_API_KEY not set)")
        return
    out = scoped.get("output", scoped)
    if not out:
        return
    items_with_lcc = []
    for item in out.get("scoped_lcc", []):
        c = item.get("code")
        if c and isinstance(c, str) and c.strip():
            items_with_lcc.append((item, c.strip(), item.get("label", "")[:40]))
    for item in out.get("scoped_disciplines", []):
        c = item.get("lcc")
        if c and isinstance(c, str) and c.strip():
            items_with_lcc.append((item, c.strip(), item.get("label", "")[:40]))
    if not items_with_lcc:
        print("  LCC: no items with LCC code")
        return
    seen_lcc: dict[str, str] = {}
    for item, code, label in items_with_lcc:
        if code in seen_lcc:
            item["lcc_explanation"] = seen_lcc[code]
            continue
        try:
            expl = _explain_lcc(code, label, api_key)
            item["lcc_explanation"] = expl
            seen_lcc[code] = expl
        except Exception as e:
            item["lcc_explanation"] = None
            item["lcc_explanation_error"] = str(e)
    print(f"  LCC: explained {len(items_with_lcc)} items ({len(seen_lcc)} unique codes)")


def enrich_lcsh(scoped: dict) -> None:
    """Resolve LCSH IDs via id.loc.gov: add label, broader, narrower, alt_labels."""
    if not resolve_lcsh:
        print("  LCSH: skipped (lcsh_resolve not available)")
        return
    out = scoped.get("output", scoped)
    if not out:
        return
    items_with_lcsh = []
    for section in ("scoped_lcsh", "scoped_disciplines"):
        for item in out.get(section, []):
            lid = item.get("lcsh_id")
            if lid and isinstance(lid, str) and lid.strip():
                items_with_lcsh.append((item, lid.strip()))
    if not items_with_lcsh:
        print("  LCSH: no items with lcsh_id")
        return
    seen: dict[str, dict] = {}
    for item, lid in items_with_lcsh:
        if lid in seen:
            item["lcsh_resolved"] = seen[lid]
            continue
        data = resolve_lcsh(lid)
        if data:
            item["lcsh_resolved"] = data
            seen[lid] = data
        else:
            item["lcsh_resolved"] = None
    print(f"  LCSH: resolved {len(items_with_lcsh)} items ({len(seen)} unique)")


def main():
    parser = argparse.ArgumentParser(description="Enrich scoped output with bibliography (OpenAlex OA + WorldCat)")
    parser.add_argument("--input", type=Path, default=None,
                        help="Path to scoped JSON (default: latest in output/sfa_scoped)")
    parser.add_argument("--worldcat", type=Path, default=None,
                        help="Path to WorldCat survey (default: output/nodes/worldcat_roman_republic.json)")
    parser.add_argument("--no-facet-filter", action="store_true",
                        help="Include all works, not just facet-matched")
    parser.add_argument("--no-openalex", action="store_true",
                        help="Disable OpenAlex; use WorldCat only")
    parser.add_argument("--no-opensyllabus", action="store_true",
                        help="Disable Open Syllabus Galaxy")
    parser.add_argument("--no-gatherbooks", action="store_true",
                        help="Disable gather_books (ia_url, toc_url, publisher from Open Library editions)")
    parser.add_argument("--domain", type=str, default="Roman Republic",
                        help="Domain label for OpenAlex/OpenSyllabus search (default: Roman Republic)")
    parser.add_argument("--dewey", action="store_true",
                        help="Add Dewey number explanations via LLM (requires ANTHROPIC_API_KEY)")
    parser.add_argument("--lcc", action="store_true",
                        help="Add LCC code explanations via LLM (requires ANTHROPIC_API_KEY)")
    parser.add_argument("--lcsh", action="store_true",
                        help="Resolve LCSH IDs via id.loc.gov (label, broader, narrower, alt_labels)")
    args = parser.parse_args()

    scoped_dir = _root / "output" / "sfa_scoped"
    worldcat_path = args.worldcat or _root / "output" / "nodes" / "worldcat_roman_republic.json"

    if args.input and args.input.exists():
        scoped_path = args.input
    else:
        files = sorted(scoped_dir.glob("*.json"))
        if not files:
            print("No scoped files in output/sfa_scoped. Run sfa_scope_federated_view.py first.")
            return
        scoped_path = files[-1]

    print(f"Loading scoped: {scoped_path.name}")
    scoped = load_scoped(scoped_path)
    print(f"Loading WorldCat: {worldcat_path}")
    worldcat = load_worldcat(worldcat_path)
    print(f"  {len(worldcat)} works")
    if not args.no_openalex and fetch_oa_works:
        print("OpenAlex: enabled (domain-level OA)")
    else:
        print("OpenAlex: disabled")
    if not args.no_opensyllabus and fetch_galaxy_works:
        print("Open Syllabus Galaxy: enabled")
    else:
        print("Open Syllabus Galaxy: disabled")
    if not args.no_gatherbooks and enrich_bibliography:
        print("Gather books: enabled (ia_url, toc_url, publisher from OL editions)")
    else:
        print("Gather books: disabled")

    facet = None if args.no_facet_filter else scoped.get("output", {}).get("facet")
    enrich(scoped, worldcat, facet=facet, use_openalex=not args.no_openalex,
           use_opensyllabus=not args.no_opensyllabus, use_gather_books=not args.no_gatherbooks,
           domain_label=args.domain)

    if args.dewey:
        enrich_dewey(scoped)
    if args.lcc:
        enrich_lcc(scoped)
    if args.lcsh:
        enrich_lcsh(scoped)

    out_path = scoped_path.parent / f"{scoped_path.stem}_bibliography.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(scoped, f, indent=2, ensure_ascii=False)
    print(f"Saved: {out_path}")

    out = scoped.get("output", {})
    for item in out.get("scoped_lcc", []) + out.get("scoped_disciplines", []) + out.get("scoped_lcsh", []):
        bib = item.get("bibliography", [])
        key = item.get("code") or item.get("label", "")[:40]
        if bib:
            print(f"\n{key}:")
            for b in bib[:5]:
                title = (b.get("title") or "")[:70]
                url = b.get("oa_url") or b.get("uri") or ""
                print(f"  • {title}...")
                print(f"    {url}")
            if len(bib) > 5:
                print(f"  ... and {len(bib) - 5} more")


if __name__ == "__main__":
    main()
