"""
resolve_lcsh_gaps.py

Checks candidate LCSH headings for the 4 gaps flagged in Q17167_subject_schema.json.
Queries the LoC Authorities API for each candidate sh-ID and proposed search terms.
"""

import json
import urllib.request
import urllib.parse
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output/subject_schema"

# ── Gaps to resolve ────────────────────────────────────────────────────────────
GAPS = [
    {
        "label": "Roman Republican Diplomacy and Foreign Relations",
        "candidate_id": "sh85115143",
        "candidate_heading": "Rome--Foreign relations",
        "search_terms": ["Rome foreign relations", "Rome diplomacy"],
    },
    {
        "label": "Roman Republican Prosopography",
        "candidate_id": "sh85115107",
        "candidate_heading": "Rome--Biography",
        "search_terms": ["prosopography Rome", "Rome biography"],
    },
    {
        "label": "Roman Colonization and Land Distribution",
        "candidate_id": None,
        "candidate_heading": None,
        "search_terms": ["Colonies Roman", "Land tenure Rome", "Rome colonization"],
    },
    {
        "label": "Roman Republican Coinage and Numismatics",
        "candidate_id": "sh85027798",
        "candidate_heading": "Coins, Roman",
        "search_terms": ["Coins Roman", "Rome numismatics"],
    },
]

LOC_BASE = "https://id.loc.gov/authorities/subjects"


def fetch_heading(sh_id: str) -> dict:
    """Fetch label + broader terms for a known sh-ID."""
    url = f"{LOC_BASE}/{sh_id}.skos.json"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read())
        # data is a list of nodes; find the one with our URI
        uri = f"http://id.loc.gov/authorities/subjects/{sh_id}"
        node = next((n for n in data if n.get("@id") == uri), None)
        if not node:
            return {"status": "not_found", "id": sh_id}
        label = ""
        for lv in node.get("http://www.w3.org/2004/02/skos/core#prefLabel", []):
            label = lv.get("@value", "")
            break
        broader = [
            b["@id"].split("/")[-1]
            for b in node.get("http://www.w3.org/2004/02/skos/core#broader", [])
        ]
        scope = ""
        for sv in node.get("http://www.w3.org/2004/02/skos/core#scopeNote", []):
            scope = sv.get("@value", "")
            break
        return {
            "status": "found",
            "id": sh_id,
            "prefLabel": label,
            "broader": broader,
            "scopeNote": scope,
        }
    except Exception as e:
        return {"status": "error", "id": sh_id, "error": str(e)}


def search_suggest(term: str) -> list:
    """Use LoC suggest2 API to find headings matching a term."""
    params = urllib.parse.urlencode({"q": term, "count": 5, "searchType": "keyword"})
    url = f"{LOC_BASE}/suggest2?{params}"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read())
        hits = []
        for item in data.get("hits", []):
            hits.append({
                "label": item.get("aLabel") or item.get("label", ""),
                "id": item.get("uri", "").split("/")[-1],
                "count": item.get("count", 0),
            })
        return hits
    except Exception as e:
        return [{"error": str(e)}]


def main():
    results = []

    for gap in GAPS:
        print(f"\n{'=' * 60}")
        print(f"GAP: {gap['label']}")
        print(f"{'=' * 60}")

        result = {"gap": gap["label"], "candidate": None, "searches": []}

        # Check candidate ID if provided
        if gap["candidate_id"]:
            print(f"  Checking candidate {gap['candidate_id']} ...")
            found = fetch_heading(gap["candidate_id"])
            print(f"  -> {found}")
            result["candidate"] = found
            time.sleep(0.5)

        # Search for alternatives
        for term in gap["search_terms"]:
            print(f"  Searching: '{term}' ...")
            hits = search_suggest(term)
            for h in hits[:3]:
                print(f"    {h.get('id', '?'):15} | {h.get('label', h.get('error', '?'))}")
            result["searches"].append({"term": term, "hits": hits[:5]})
            time.sleep(0.5)

        results.append(result)

    out_path = OUTPUT_DIR / "Q17167_lcsh_gap_resolution.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    main()
