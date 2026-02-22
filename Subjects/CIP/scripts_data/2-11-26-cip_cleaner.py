import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def resolve_file(candidates):
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("Missing required file. Tried: " + ", ".join(str(p) for p in candidates))


INPUT = resolve_file([
    SCRIPT_DIR / "2-11-26-cip_concept_subject_clean.csv",
    SCRIPT_DIR / "cip_concept_subject_clean.csv",
])
output_prefix = "2-11-26-" if INPUT.name.startswith("2-11-26-") else ""
OUTPUT = SCRIPT_DIR / f"{output_prefix}cip_concept_subject_clean_patched.csv"

PROFESSION_HINTS = {
    "profession", "occupation", "job", "worker",
    "person who", "someone who", "practitioner",
    "artist", "technician", "assistant", "clerk",
    "sommelier", "make-up", "manicurist"
}

JOURNAL_HINTS = {"journal", "academic journal", "scientific journal"}
BOOK_HINTS = {"book", "monograph", "textbook"}
ORG_HINTS = {"organization", "organisation", "institute", "university", "society"}
EVENT_HINTS = {"event", "conference", "workshop", "symposium", "flood", "war"}

DISCIPLINE_HINTS = {
    "academic discipline", "field of study", "branch of science",
    "interdisciplinary academic field", "multidisciplinary academic field"
}

APPLIED_HINTS = {
    "applied science", "applied field", "technology", "management",
    "operations", "production", "practice"
}

def norm(s):
    return (s or "").strip().lower()

def any_in(text, hints):
    t = norm(text)
    return any(h in t for h in hints)

def classify(row):
    text = " | ".join([
        row.get("qid_label", ""),
        row.get("qid_description", ""),
        row.get("P31_labels", ""),
        row.get("P279_labels", "")
    ]).lower()

    p31 = row.get("P31_qids", "")

    # HARD EXCLUSIONS
    if any_in(text, JOURNAL_HINTS):
        return "journal"
    if any_in(text, BOOK_HINTS):
        return "book"
    if any_in(text, EVENT_HINTS):
        return "event"

    # EXCLUDE PROFESSIONS
    if any_in(text, PROFESSION_HINTS):
        return "exclude_profession"
    if "Q28640" in p31 or "Q12737077" in p31:
        return "exclude_profession"

    # ORGANIZATION (but override if discipline)
    if any_in(text, ORG_HINTS):
        if any_in(text, DISCIPLINE_HINTS):
            return "concept_subject"
        return "organization"

    # DISCIPLINE
    if any_in(text, DISCIPLINE_HINTS):
        return "concept_subject"

    # APPLIED FIELD
    if any_in(text, APPLIED_HINTS):
        return "concept_applied"

    # Label heuristics
    label = norm(row.get("qid_label", ""))
    if label.endswith(" studies") or label.endswith(" science") or label.endswith(" sciences"):
        return "concept_subject"

    return "concept_other"

def main():
    with INPUT.open(newline="", encoding="utf-8") as f_in, OUTPUT.open("w", newline="", encoding="utf-8") as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            row["node_type"] = classify(row)
            writer.writerow(row)

if __name__ == "__main__":
    main()
