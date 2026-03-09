#!/usr/bin/env python3
"""
Classify disciplines in discipline_taxonomy.csv into 18 facets using Claude.
Operates on CSV directly — no Neo4j dependency.

Reads: output/discipline_taxonomy.csv (with primary_facet column)
Writes: updated CSV with primary_facet + related_facets filled in
Copies: to viewer/public/discipline_taxonomy.csv
"""
import csv
import json
import shutil
import time
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: pip install anthropic")
    raise SystemExit(1)

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass  # rely on environment

PROJECT = Path(__file__).resolve().parents[2]
SRC_CSV = PROJECT / "output" / "discipline_taxonomy.csv"
PUBLIC_CSV = PROJECT / "viewer" / "public" / "discipline_taxonomy.csv"

FACETS = {
    "ARCHAEOLOGICAL":  "Study of material culture, excavation, artifacts, physical remains",
    "ARTISTIC":        "Visual arts, architecture, aesthetics, art history, design, museology",
    "BIOGRAPHIC":      "Life writing, prosopography, personal histories, genealogy",
    "COMMUNICATION":   "Media, information science, journalism, rhetoric, publishing",
    "CULTURAL":        "Cultural practices, traditions, folklore, cultural studies",
    "DEMOGRAPHIC":     "Population studies, migration, census, vital statistics",
    "DIPLOMATIC":      "International relations, treaties, foreign policy, diplomacy",
    "ECONOMIC":        "Trade, finance, labor, agriculture, industry, economic systems",
    "ENVIRONMENTAL":   "Climate, ecology, natural resources, land use, environmental change",
    "GEOGRAPHIC":      "Places, spatial analysis, cartography, topography, historical geography",
    "INTELLECTUAL":    "Ideas, philosophy, historiography, scholarship, education, knowledge",
    "LINGUISTIC":      "Language, philology, grammar, semantics, translation, epigraphy",
    "MILITARY":        "Warfare, armies, strategy, fortification, naval, weapons",
    "POLITICAL":       "Government, law, institutions, administration, political movements",
    "RELIGIOUS":       "Religion, theology, ritual, sacred texts, church history",
    "SCIENTIFIC":      "Natural sciences, mathematics, medicine, technology of observation",
    "SOCIAL":          "Society, class, gender, family, customs, social structures",
    "TECHNOLOGICAL":   "Engineering, tools, construction, manufacturing, applied science",
}

FACET_LIST_STR = "\n".join(f"  {k}: {v}" for k, v in FACETS.items())


def main():
    # Read CSV
    rows = []
    with open(SRC_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    # Ensure columns exist
    if "primary_facet" not in fieldnames:
        fieldnames = list(fieldnames) + ["primary_facet", "related_facets"]

    # Find unclassified
    unclassified = [r for r in rows if not r.get("primary_facet")]
    already = len(rows) - len(unclassified)
    print(f"{len(rows)} total disciplines, {already} already classified, {len(unclassified)} to classify")

    if not unclassified:
        print("Nothing to do.")
        return

    client = anthropic.Anthropic()
    BATCH = 50
    classified = 0

    for i in range(0, len(unclassified), BATCH):
        batch = unclassified[i:i + BATCH]
        batch_str = "\n".join(
            f"  {r['qid']}: {r['label']}"
            + (f" (subclass of: {r['subclass_of_label'].split('|')[0]})" if r.get("subclass_of_label") else "")
            for r in batch
        )

        prompt = f"""Classify each discipline into ONE primary facet and optionally related facets with weights.

FACETS:
{FACET_LIST_STR}

DISCIPLINES TO CLASSIFY:
{batch_str}

Return ONLY a JSON array. Each element:
{{"qid": "...", "primary": "FACET_KEY", "related": [{{"facet": "FACET_KEY", "weight": 0.8}}, ...]}}

Rules:
- primary = the single best-fit facet
- related = other facets this discipline meaningfully touches (weight 0.3-0.9)
- related can be empty if the discipline is purely one facet
- do NOT include the primary facet in related
- Use ONLY the facet keys listed above. No explanation."""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            results = json.loads(text)

            # Build lookup
            result_map = {}
            for item in results:
                qid = item.get("qid", "")
                primary = item.get("primary", "")
                related = item.get("related", [])
                if primary in FACETS:
                    related_str = "|".join(
                        f"{r['facet']}:{r.get('weight', 0.5)}"
                        for r in related
                        if isinstance(r, dict) and r.get("facet") in FACETS and r["facet"] != primary
                    )
                    result_map[qid] = (primary, related_str)

            # Apply to rows
            for r in batch:
                if r["qid"] in result_map:
                    r["primary_facet"] = result_map[r["qid"]][0]
                    r["related_facets"] = result_map[r["qid"]][1]
                    classified += 1

            batch_ok = sum(1 for r in batch if r["qid"] in result_map)
            print(f"  Batch {i // BATCH + 1}/{(len(unclassified) + BATCH - 1) // BATCH}: "
                  f"{batch_ok}/{len(batch)} classified ({classified} total)")

        except Exception as e:
            print(f"  Batch {i // BATCH + 1} ERROR: {e}")

        time.sleep(1)

    # Write updated CSV
    with open(SRC_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nUpdated {SRC_CSV.name}")

    # Copy to viewer
    shutil.copy2(SRC_CSV, PUBLIC_CSV)
    print(f"Copied to {PUBLIC_CSV}")

    # Summary
    facet_counts = {}
    still_empty = 0
    for r in rows:
        pf = r.get("primary_facet", "")
        if pf:
            facet_counts[pf] = facet_counts.get(pf, 0) + 1
        else:
            still_empty += 1

    print(f"\n-- Facet distribution ({len(rows) - still_empty}/{len(rows)} classified) --")
    for facet, cnt in sorted(facet_counts.items(), key=lambda x: -x[1]):
        print(f"  {facet:20s} {cnt}")
    if still_empty:
        print(f"  {'(unassigned)':20s} {still_empty}")


if __name__ == "__main__":
    main()
