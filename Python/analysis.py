#!/usr/bin/env python3
import json, csv, sys, re
from statistics import mean

FACETS = ["PoliticalFacet","CulturalFacet","TechnologicalFacet","ReligiousFacet",
          "EconomicFacet","MilitaryFacet","EnvironmentalFacet","DemographicFacet",
          "IntellectualFacet","ScientificFacet","ArtisticFacet","SocialFacet",
          "LinguisticFacet","ArchaeologicalFacet","DiplomaticFacet"]

def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def parse_scores_and_assessment(rec):
    # Try structured fields first
    scores = {}
    assessment = ""
    # Common shapes: rec['llm_response'] -> choices[0].message.content (string with JSON)
    lr = rec.get("llm_response") or {}
    content = ""
    try:
        content = lr.get("choices",[{}])[0].get("message",{}).get("content","") if lr else ""
    except Exception:
        content = ""
    # If content contains a JSON object, extract it
    if content:
        # find first JSON object
        mstart = content.find("{")
        mend = content.rfind("}")
        if mstart != -1 and mend != -1 and mend > mstart:
            try:
                j = json.loads(content[mstart:mend+1])
                for f in FACETS:
                    if f in j:
                        scores[f] = float(j[f])
            except Exception:
                pass
        # find assessment string of 15 letters
        m = re.search(r"\b([HML]{15})\b", content)
        if m:
            assessment = m.group(1)
        # try to find wiki flag tokens ++ or +
        wiki_flag = None
        if "++" in content:
            wiki_flag = "++"
        elif " wiki " in content.lower() or "wikipedia" in content.lower() or "wikidata" in content.lower():
            # fallback: mark single plus if wiki mentioned
            wiki_flag = "+"
    # fallback structured fields
    if not scores:
        scores = rec.get("scores") or rec.get("llm_scores") or {}
    if not assessment:
        assessment = rec.get("assessment") or rec.get("llm_assessment") or ""
    wiki_flag = rec.get("wiki_flag") if rec.get("wiki_flag") is not None else ( "++" if "++" in content else ("+" if "+" in content else None) )
    return scores, assessment, wiki_flag

def score_to_letters(scores):
    letters = []
    for f in FACETS:
        v = scores.get(f, 0.0)
        if v > 0.75: letters.append("H")
        elif v < 0.5: letters.append("L")
        else: letters.append("M")
    return "".join(letters)

def compute_combined(scores, assessment, wiki_flag):
    # mean facet
    vals = [float(scores.get(f,0.0)) for f in FACETS]
    mean_f = mean(vals)
    h_count = assessment.count("H") if assessment else 0
    wiki_score = 1.0 if wiki_flag == "++" else 0.5 if wiki_flag == "+" else 0.0
    combined = 0.60 * mean_f + 0.25 * wiki_score + 0.15 * (h_count / len(FACETS))
    return {"mean_facet": mean_f, "h_count": h_count, "wiki_score": wiki_score, "combined": combined}

def select_record(rec, metrics):
    # Primary selection rules
    if metrics["wiki_score"] == 1.0 and metrics["combined"] >= 0.5:
        return True
    if metrics["combined"] >= 0.6:
        return True
    return False

def main(infile, outcsv):
    data = load_json(infile)
    records = data if isinstance(data, list) else (data.get("@graph") or data.get("items") or [])
    out_rows = []
    for rec in records:
        subject_id = rec.get("subject_id") or rec.get("id") or rec.get("subject") or ""
        scores, assessment, wiki_flag = parse_scores_and_assessment(rec)
        if not assessment and scores:
            assessment = score_to_letters(scores)
        metrics = compute_combined(scores, assessment, wiki_flag)
        flags = []
        if assessment.count("L") >= 12:
            flags.append("MOSTLY_L")
        if metrics["wiki_score"] == 1.0 and metrics["mean_facet"] < 0.3:
            flags.append("WIKI_LOW_MEAN")
        selected = select_record(rec, metrics)
        out_rows.append({
            "subject_id": subject_id,
            "assessment": assessment,
            "mean_facet": round(metrics["mean_facet"],3),
            "h_count": metrics["h_count"],
            "wiki_flag": wiki_flag or "",
            "combined": round(metrics["combined"],3),
            "selected": "YES" if selected else "NO",
            "flags": ";".join(flags)
        })
    # write CSV
    with open(outcsv, "w", newline="", encoding="utf-8") as f:
        import csv
        w = csv.DictWriter(f, fieldnames=["subject_id","assessment","mean_facet","h_count","wiki_flag","combined","selected","flags"])
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    # print summary
    total = len(out_rows)
    chosen = sum(1 for r in out_rows if r["selected"]=="YES")
    print(f"Processed {total} records; selected {chosen} candidates. CSV written to {outcsv}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python select_candidates.py input.json output.csv")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])