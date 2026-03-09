"""
apply_openalex_fixes.py

Applies manual review decisions to discipline_taxonomy_openalex_validated.csv:

  1. Upgrades 10 clear-synonym needs_review rows to verified
  2. Replaces 3 suspect IDs with better OpenAlex concept IDs
  3. Writes final output to discipline_taxonomy_openalex_final.csv

Run after validate_openalex_ids.py.
"""

import csv
from pathlib import Path

INPUT_CSV  = Path("output/discipline_taxonomy_openalex_validated.csv")
OUTPUT_CSV = Path("output/discipline_taxonomy_openalex_final.csv")

# QID → (new_primary_id, new_display, new_sim, new_status, note)
MANUAL_FIXES = {
    # Clear synonyms — label wording differs but concept is correct
    "Q207628":  ("C109568592",   "Musical composition",              0.45,  "verified", "synonym:composed_musical_work"),
    "Q1750812": ("C166735990",   "Human factors and ergonomics",     0.526, "verified", "synonym:ergonomics"),
    "Q160289":  ("C3020799230",  "Auditory perception",              0.308, "verified", "synonym:hearing"),
    "Q1344860": ("C2993622096",  "Performance practice",             0.415, "verified", "synonym:historically_informed_performance"),
    "Q122131":  ("C2993637838",  "German history",                   0.438, "verified", "synonym:history_of_germany"),
    "Q646206":  ("C2993800547",  "Roman history",                    0.5,   "verified", "synonym:history_of_rome"),
    "Q1333743": ("C198912144",   "Creative writing",                 0.0,   "verified", "replaced:composition_language;better_match"),
    "Q44497":   ("C2984157484",  "Mining industry",                  0.571, "verified", "synonym:mining"),
    "Q3281534": ("C155405519",   "Modern history",                   0.593, "verified", "synonym:modern_period"),
    "Q14254438":("C59377095",    "Applied ethics",                   0.0,   "verified", "replaced:moral_theology;broader_match"),
    "Q52946":   ("C2989496772",  "Speech communication",             0.462, "verified", "synonym:speech"),
    "Q249":     ("C555944384",   "Wireless",                         0.533, "verified", "synonym:wireless_communication"),
    # S-prefix invalid + manual concept assignment
    "Q623313":  ("C2993946455",  "Ottoman empire",                   0.0,   "verified", "replaced:S4210192759_invalid_source_prefix;best_available_concept"),
}


def main():
    with open(INPUT_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys())

    fixed = 0
    for row in rows:
        qid = row["qid"]
        if qid in MANUAL_FIXES:
            new_id, new_display, new_sim, new_status, note = MANUAL_FIXES[qid]
            old_status = row["openalex_status"]
            row["openalex_primary"]  = new_id
            row["openalex_display"]  = new_display
            row["openalex_sim"]      = new_sim
            row["openalex_status"]   = new_status
            existing_notes = row.get("openalex_notes", "")
            row["openalex_notes"]    = f"manual_fix:{note}" + (f"; {existing_notes}" if existing_notes else "")
            print(f"  {qid} | {row['label']}")
            print(f"    {old_status} -> {new_status} | {new_id} ({new_display})")
            fixed += 1

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # Final summary
    statuses = {}
    for r in rows:
        s = r["openalex_status"]
        statuses[s] = statuses.get(s, 0) + 1

    print(f"\nApplied {fixed} manual fixes.")
    print("\n--- Final Status Summary ---")
    for s, count in sorted(statuses.items()):
        print(f"  {s:25s} {count}")
    print(f"\nOutput: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
