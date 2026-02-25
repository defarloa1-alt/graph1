#!/usr/bin/env python3
"""
Diagnostic: Why are Q1764124 and Q271108 so unscoped?

For unscoped entities in those clusters:
- Do they have P6863, P1584, P1696, P1838 (any)?
- What P31 (instance of) values dominate?

Answers: harvester/scoping source gap vs federation coverage gap.
"""
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
EDGES_PATH = ROOT / "output/cluster_assignment/member_of_edges.json"
BACKLINKS_DIR = ROOT / "output/backlinks"


FEDERATION_PIDS = {"P6863", "P1584", "P1696", "P1838"}  # DPRR, Pleiades, Trismegistos, LGPN

# Common P31 labels for interpretation
P31_LABELS = {
    "Q5": "human",
    "Q198": "war",
    "Q178561": "war",
    "Q188055": "event",
    "Q1261499": "battle",
    "Q831663": "military operation",
    "Q11424": "war",
}


def load_p31_from_reports() -> dict[str, list[str]]:
    """Build qid -> p31 values from all harvest reports."""
    qid_to_p31: dict[str, list[str]] = {}
    for fp in BACKLINKS_DIR.glob("*_report.json"):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            for ent in data.get("accepted", []):
                qid = ent.get("qid")
                if not qid:
                    continue
                p31 = ent.get("p31") or []
                if isinstance(p31, list) and p31:
                    qid_to_p31[qid] = p31
        except Exception:
            continue
    return qid_to_p31


def main():
    edges_path = EDGES_PATH
    if not edges_path.exists():
        print(f"Missing {edges_path}. Run cluster assignment first.")
        return

    edges = json.loads(edges_path.read_text(encoding="utf-8"))

    targets = ["Q1764124", "Q271108"]
    qid_to_p31 = load_p31_from_reports()

    for subject_qid in targets:
        unscoped = [
            e
            for e in edges
            if e.get("subject_qid") == subject_qid and e.get("scoping_status") == "unscoped"
        ]
        if not unscoped:
            print(f"\n{subject_qid}: No unscoped edges.")
            continue

        # Dedupe by entity (first occurrence)
        seen = set()
        unique_entities: list[dict] = []
        for e in unscoped:
            qid = e.get("entity_qid") or ""
            if qid and qid not in seen:
                seen.add(qid)
                unique_entities.append(e)

        ext = [e.get("external_ids") or {} for e in unique_entities]
        has_any_fed = sum(1 for ex in ext if FEDERATION_PIDS & set(ex.keys()))
        has_none = sum(1 for ex in ext if not (FEDERATION_PIDS & set(ex.keys())))
        has_p6863 = sum(1 for ex in ext if "P6863" in ex)
        has_p1584 = sum(1 for ex in ext if "P1584" in ex)
        has_p1696 = sum(1 for ex in ext if "P1696" in ex)
        has_p1838 = sum(1 for ex in ext if "P1838" in ex)

        p31_counter: Counter[str] = Counter()
        for e in unique_entities:
            qid = e.get("entity_qid")
            for p in qid_to_p31.get(qid or "", []):
                p31_counter[p] += 1

        label = "External wars" if subject_qid == "Q1764124" else "Factional politics"
        print(f"\n{'='*60}")
        print(f"{subject_qid} ({label})")
        print("=" * 60)
        print(f"Unscoped entities: {len(unique_entities)}")
        print()
        print("Federation IDs (P6863=DPRR, P1584=Pleiades, P1696=Trismegistos, P1838=LGPN):")
        print(f"  Has ANY of these: {has_any_fed}")
        print(f"  Has NONE:        {has_none}")
        print(f"  P6863 (DPRR):    {has_p6863}")
        print(f"  P1584 (Pleiades):{has_p1584}")
        print(f"  P1696 (Trismeg): {has_p1696}")
        print(f"  P1838 (LGPN):    {has_p1838}")
        print()
        print("P31 (instance of) distribution (top 10):")
        for p31_qid, count in p31_counter.most_common(10):
            lbl = P31_LABELS.get(p31_qid, "?")
            print(f"  {p31_qid} ({lbl}): {count}")
        print()
        print("Sample external_ids (first 5 unscoped):")
        for e in unique_entities[:5]:
            ex = e.get("external_ids") or {}
            pids = list(ex.keys())[:8]
            print(f"  {e.get('entity_qid')} {e.get('entity_label','')[:40]}: {pids}")

    print("\n" + "=" * 60)
    print("Interpretation:")
    print("- If has_none = total: federation coverage gap (entities lack ancient-world IDs)")
    print("- If has_any_fed > 0 but still unscoped: harvester/scoping rule gap")
    print("- P31 distribution: wars/events (Q198, Q178561) vs persons (Q5) vs concepts")

if __name__ == "__main__":
    main()
