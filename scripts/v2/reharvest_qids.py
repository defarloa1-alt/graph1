#!/usr/bin/env python3
"""Re-resolve QIDs for harvest files with degraded resolution.

Reads existing harvest JSONs, re-resolves all concepts missing QIDs,
updates both harvest and classified files.

Run:
  python scripts/v2/reharvest_qids.py
  python scripts/v2/reharvest_qids.py --threshold 80
"""
import sys, json, time, argparse
import urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "output" / "wiki_concept_maps"


def resolve_qids_batch(titles, delay=1.5):
    """Batch resolve Wikipedia titles to QIDs with generous rate limiting."""
    qid_map = {}
    title_list = list(titles)
    for i in range(0, len(title_list), 50):
        batch = title_list[i : i + 50]
        titles_param = "|".join(batch)
        url = (
            "https://en.wikipedia.org/w/api.php"
            f"?action=query&titles={urllib.parse.quote(titles_param)}"
            "&prop=pageprops&ppprop=wikibase_item&format=json"
        )
        req = urllib.request.Request(
            url, headers={"User-Agent": "Chrystallum/2.0 (research)"}
        )
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read())
            pages = data.get("query", {}).get("pages", {})
            normalized = {}
            for n in data.get("query", {}).get("normalized", []):
                normalized[n["from"]] = n["to"]

            for page_id, page_data in pages.items():
                if int(page_id) < 0:
                    continue
                title = page_data.get("title", "")
                qid = page_data.get("pageprops", {}).get("wikibase_item")
                if qid:
                    qid_map[title] = qid
                    for orig, norm in normalized.items():
                        if norm == title:
                            qid_map[orig] = qid
        except Exception as e:
            print(f"    QID batch error at {i}: {e}")

        time.sleep(delay)

    return qid_map


def main():
    parser = argparse.ArgumentParser(description="Re-resolve degraded QIDs")
    parser.add_argument(
        "--threshold", type=float, default=70,
        help="Re-harvest pages below this QID resolution %% (default: 70)"
    )
    args = parser.parse_args()

    sys.stdout.reconfigure(errors="replace")

    harvest_files = sorted(OUT_DIR.glob("*.json"))
    harvest_files = [f for f in harvest_files if "_classified" not in f.name]

    # Find degraded files
    to_fix = []
    for f in harvest_files:
        data = json.load(open(f, encoding="utf-8"))
        s = data["stats"]
        rate = s["qid_resolved"] / s["total_concepts"] * 100 if s["total_concepts"] else 100
        if rate < args.threshold:
            missing = [c["name"] for c in data["concepts"] if not c.get("qid")]
            to_fix.append((f, data, missing, rate))

    print(f"Found {len(to_fix)} harvest files below {args.threshold}% QID resolution\n")

    total_new = 0
    for i, (f, data, missing, old_rate) in enumerate(to_fix):
        page_name = f.stem
        print(f"[{i+1:02d}/{len(to_fix)}] {page_name:50s} ({len(missing)} missing) ", end="", flush=True)

        if not missing:
            print("SKIP (none missing)")
            continue

        new_qids = resolve_qids_batch(missing, delay=1.5)

        # Update concepts in harvest data
        updated = 0
        for c in data["concepts"]:
            if not c.get("qid") and c["name"] in new_qids:
                c["qid"] = new_qids[c["name"]]
                updated += 1

        # Recalculate stats
        resolved = sum(1 for c in data["concepts"] if c.get("qid"))
        data["stats"]["qid_resolved"] = resolved
        new_rate = resolved / data["stats"]["total_concepts"] * 100

        # Save updated harvest
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)

        # Update classified file if it exists
        cls_path = OUT_DIR / f"{page_name}_classified.json"
        cls_updated = 0
        if cls_path.exists():
            cls_data = json.load(open(cls_path, encoding="utf-8"))
            # Rebuild classified with new QIDs
            qid_lookup = {c["name"]: c["qid"] for c in data["concepts"] if c.get("qid")}
            for c in cls_data["classified"]:
                if not c.get("qid") and c["name"] in qid_lookup:
                    c["qid"] = qid_lookup[c["name"]]
                    cls_updated += 1
            with open(cls_path, "w", encoding="utf-8") as fh:
                json.dump(cls_data, fh, indent=2, ensure_ascii=False)

        total_new += updated
        print(f"+{updated} QIDs ({old_rate:.0f}% -> {new_rate:.0f}%) cls+{cls_updated}")

    print(f"\nTotal new QIDs resolved: {total_new}")


if __name__ == "__main__":
    main()
