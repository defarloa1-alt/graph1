"""
verify_and_patch_lcsh.py

Two-pass operation on Q17167_subject_schema.json:
  Pass 1 — Verify all unverified_best_match IDs via LoC SKOS fetch.
  Pass 2 — Plug known correct IDs for not_found entries; search LoC for Science.
  Pass 3 — Fix bad match sh2008106681 (Latin American literature → Latin literature).

Updates the JSON in-place and prints a diff summary.
"""

import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "output/subject_schema/Q17167_subject_schema.json"
LOC_BASE = "https://id.loc.gov/authorities/subjects"

# ── Known correct IDs from LoC API work in previous session ────────────────────
KNOWN_PATCHES = {
    # label → (sh_id, heading, status)
    "Roman Magistracies":                    ("sh85115176", "Rome--Officials and employees",  "verified"),
    "Roman Republican Army":                 ("sh85115090", "Rome--Army",                     "verified"),
    "Roman Navy":                            ("sh87007223", "Rome--Navy",                     "verified"),
    "Roman Republican Economy and Finance":  ("sh85115102", "Rome--Economic conditions",      "verified"),
    "Roman Republican Religion":             ("sh96009771",  "Rome--Religion",                "verified"),
    "Roman Slavery":                         ("sh85123324",  "Slavery--Rome",                 "verified"),
    "Women in Ancient Rome":                 ("sh2010119009","Women--Rome--Social conditions", "verified"),
    "Roman Family and Kinship":              ("sh2009124087","Families--Rome",                 "verified"),
    "Roman Education":                       ("sh2008119007","Education--Rome",                "verified"),
    "Roman Historiography and Sources":      ("sh2008116719","Rome--Historiography",           "verified"),
    "Archaeology of Republican Rome":        ("sh85115088",  "Rome--Antiquities",             "verified"),
    "Roman Republican Literature and Intellectual Life": ("sh2008106708", "Latin literature--History and criticism", "verified"),
    "Roman Science, Technology, and Medicine":           ("sh85118612",   "Science, Ancient",                       "verified"),
    # Senate and Assemblies confirmed to not exist as LCSH headings — use Politics heading
    "Roman Senate":                          ("sh85115178", "Rome--Politics and government",  "lcsh_ceiling"),
    "Roman Popular Assemblies":              ("sh85115178", "Rome--Politics and government",  "lcsh_ceiling"),
}

# ── Cipher builder ─────────────────────────────────────────────────────────────
import hashlib

def make_cipher(qid: str, sh_id: str) -> str:
    raw = f"SUBJECT_CONCEPT|{qid}|{sh_id}"
    return hashlib.sha256(raw.encode()).hexdigest()


# ── LoC SKOS fetch ─────────────────────────────────────────────────────────────
def fetch_label(sh_id: str) -> str | None:
    url = f"{LOC_BASE}/{sh_id}.skos.json"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read())
        uri = f"http://id.loc.gov/authorities/subjects/{sh_id}"
        node = next((n for n in data if n.get("@id") == uri), None)
        if not node:
            return None
        for lv in node.get("http://www.w3.org/2004/02/skos/core#prefLabel", []):
            return lv.get("@value", "")
        return None
    except Exception as e:
        print(f"    ERROR fetching {sh_id}: {e}")
        return None


def _normalize(s: str) -> str:
    """Normalize all dash variants and punctuation to spaces for token comparison."""
    return (s.lower()
             .replace("\u2014", " ")   # em-dash
             .replace("\u2013", " ")   # en-dash
             .replace("--", " ")
             .replace(",", " ")
             .replace(".", " "))


def token_overlap(a: str, b: str) -> float:
    ta = set(_normalize(a).split())
    tb = set(_normalize(b).split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


# ── LoC suggest search ─────────────────────────────────────────────────────────
def search_suggest(term: str, count: int = 8) -> list[dict]:
    params = urllib.parse.urlencode({"q": term, "count": count, "searchType": "keyword"})
    url = f"{LOC_BASE}/suggest2?{params}"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read())
        hits = []
        for item in data.get("hits", []):
            hits.append({
                "label": item.get("aLabel") or item.get("label", ""),
                "id": item.get("uri", "").split("/")[-1],
            })
        return hits
    except Exception as e:
        print(f"    ERROR searching '{term}': {e}")
        return []


def best_hit(heading: str, hits: list[dict], threshold: float = 0.5) -> tuple[str | None, str | None, float]:
    """Return (sh_id, label, score) for the best matching hit, or (None, None, 0)."""
    best_id, best_label, best_score = None, None, 0.0
    for h in hits:
        score = token_overlap(heading, h["label"])
        if score > best_score:
            best_score = score
            best_id = h["id"]
            best_label = h["label"]
    if best_score >= threshold:
        return best_id, best_label, best_score
    return None, None, best_score


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        schema = json.load(f)

    seed_qid = schema["seed_qid"]
    concepts = schema["subject_concepts"]
    changes = []

    print(f"\nSchema: {SCHEMA_PATH.name}  ({len(concepts)} concepts)")
    print("=" * 70)

    for sc in concepts:
        label = sc["label"]
        status = sc.get("lcsh_id_status", "")
        sh_id = sc.get("lcsh_id", "")

        # ── Pass 1: verify unverified_best_match ───────────────────────────────
        if status == "unverified_best_match" and sh_id not in ("NEEDS_LOOKUP", ""):
            expected = sc.get("lcsh_heading", "")
            print(f"\n[VERIFY] {label}")
            print(f"         sh_id={sh_id}  expected='{expected}'")
            time.sleep(0.4)
            actual = fetch_label(sh_id)
            if actual is None:
                print(f"         -> NOT FOUND on LoC")
                sc["lcsh_id_status"] = "not_found"
                sc["lcsh_id"] = "NEEDS_LOOKUP"
                sc["concept_cipher"] = None
                sc["cipher_status"] = "pending_curation"
                changes.append(f"  {label}: sh_id {sh_id} not found on LoC -> reset")
            else:
                score = token_overlap(expected, actual)
                print(f"         -> actual='{actual}'  overlap={score:.2f}")
                if score >= 0.6:
                    sc["lcsh_id_status"] = "verified"
                    sc["lcsh_id_resolved_label"] = actual
                    if not sc.get("concept_cipher"):
                        sc["concept_cipher"] = make_cipher(seed_qid, sh_id)
                        sc.pop("cipher_status", None)
                    changes.append(f"  {label}: VERIFIED {sh_id} '{actual}'")
                    print(f"         -> VERIFIED")
                elif score >= 0.35:
                    sc["lcsh_id_status"] = "unverified_best_match"
                    sc["lcsh_id_resolved_label"] = actual
                    changes.append(f"  {label}: still unverified (score={score:.2f}) '{actual}'")
                    print(f"         -> UNVERIFIED (low overlap)")
                else:
                    # Bad match — clear and re-search
                    print(f"         -> BAD MATCH (score={score:.2f}) — searching LoC")
                    sc["lcsh_id_status"] = "not_found"
                    sc["lcsh_id"] = "NEEDS_LOOKUP"
                    sc["concept_cipher"] = None
                    sc["cipher_status"] = "pending_curation"
                    changes.append(f"  {label}: BAD MATCH {sh_id} '{actual}' cleared")

        # ── Pass 2: apply known patches for not_found / any status ───────────────
        if label in KNOWN_PATCHES:
            new_id, new_label, new_status = KNOWN_PATCHES[label]
            print(f"\n[PATCH ] {label}")
            print(f"         applying {new_id} '{new_label}' status={new_status}")
            time.sleep(0.4)
            # Verify the patch ID is real
            actual = fetch_label(new_id)
            if actual:
                score = token_overlap(new_label, actual)
                print(f"         LoC confirms: '{actual}'  overlap={score:.2f}")
                sc["lcsh_id"] = new_id
                sc["lcsh_id_resolved_label"] = actual
                sc["lcsh_id_status"] = new_status
                sc.pop("cipher_status", None)
                if new_status in ("verified", "lcsh_ceiling"):
                    sc["concept_cipher"] = make_cipher(seed_qid, new_id)
                changes.append(f"  {label}: patched -> {new_id} '{actual}' [{new_status}]")
            else:
                print(f"         WARNING: {new_id} not found on LoC — skipping patch")

    # ── Pass 3: fix bad Literature match ──────────────────────────────────────
    lit = next((s for s in concepts if s["label"] == "Roman Republican Literature and Intellectual Life"), None)
    if lit and lit.get("lcsh_id") not in ("sh2008106708",) and lit.get("lcsh_id_status") != "verified":
        print(f"\n[FIX   ] Roman Republican Literature — searching for correct Latin literature heading")
        time.sleep(0.4)
        hits = search_suggest("Latin literature history criticism", count=8)
        time.sleep(0.4)
        for h in hits[:5]:
            print(f"         {h['id']:15} | {h['label']}")
        # Filter for classical Latin literature (not American, not Medieval/modern)
        filtered = [h for h in hits if "latin literature" in h["label"].lower()
                    and "american" not in h["label"].lower()
                    and "medieval" not in h["label"].lower()]
        if filtered:
            best = filtered[0]
            print(f"         -> selected {best['id']} '{best['label']}'")
            actual = fetch_label(best["id"])
            if actual:
                lit["lcsh_id"] = best["id"]
                lit["lcsh_id_resolved_label"] = actual
                lit["lcsh_id_status"] = "verified"
                lit["concept_cipher"] = make_cipher(seed_qid, best["id"])
                lit.pop("cipher_status", None)
                changes.append(f"  Literature: fixed -> {best['id']} '{actual}'")
        else:
            print(f"         No clean hit — trying leftAnchor search")
            time.sleep(0.4)
            params = urllib.parse.urlencode({"q": "Latin literature", "count": 5, "searchType": "leftAnchor"})
            url = f"{LOC_BASE}/suggest2?{params}"
            try:
                with urllib.request.urlopen(url, timeout=15) as r:
                    data = json.loads(r.read())
                for item in data.get("hits", [])[:5]:
                    lbl = item.get("aLabel") or item.get("label", "")
                    uid = item.get("uri", "").split("/")[-1]
                    print(f"         {uid:15} | {lbl}")
                    if ("latin literature" in lbl.lower()
                            and "american" not in lbl.lower()
                            and "medieval" not in lbl.lower()):
                        actual = fetch_label(uid)
                        if actual:
                            lit["lcsh_id"] = uid
                            lit["lcsh_id_resolved_label"] = actual
                            lit["lcsh_id_status"] = "verified"
                            lit["concept_cipher"] = make_cipher(seed_qid, uid)
                            lit.pop("cipher_status", None)
                            changes.append(f"  Literature: fixed -> {uid} '{actual}'")
                            break
            except Exception as e:
                print(f"         ERROR: {e}")

    # ── Pass 4: Science — search if still not_found ────────────────────────────
    sci = next((s for s in concepts if s["label"] == "Roman Science, Technology, and Medicine"), None)
    if sci and sci.get("lcsh_id_status") == "not_found":
        print(f"\n[SEARCH] Roman Science, Technology, and Medicine")
        time.sleep(0.4)
        hits = search_suggest("science ancient Rome", count=8)
        time.sleep(0.4)
        for h in hits[:5]:
            print(f"         {h['id']:15} | {h['label']}")
        best_id, best_label, score = best_hit("Science, Ancient", hits, threshold=0.4)
        if best_id:
            actual = fetch_label(best_id)
            print(f"         -> selected {best_id} '{actual}'  overlap={score:.2f}")
            sci["lcsh_id"] = best_id
            sci["lcsh_id_resolved_label"] = actual
            sci["lcsh_id_status"] = "unverified_best_match" if score < 0.6 else "verified"
            if sci["lcsh_id_status"] != "not_found":
                sci["concept_cipher"] = make_cipher(seed_qid, best_id)
                sci.pop("cipher_status", None)
            changes.append(f"  Science: found {best_id} '{actual}' (score={score:.2f})")

    # ── Write updated schema ───────────────────────────────────────────────────
    with open(SCHEMA_PATH, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    print(f"\n{'=' * 70}")
    print(f"Updated: {SCHEMA_PATH}")
    print(f"\nChanges ({len(changes)}):")
    for c in changes:
        print(c)

    # ── Final status summary ───────────────────────────────────────────────────
    by_status: dict[str, list[str]] = {}
    for sc in concepts:
        s = sc.get("lcsh_id_status", "unknown")
        by_status.setdefault(s, []).append(sc["label"])
    print(f"\nFinal status breakdown:")
    for s, labels in sorted(by_status.items()):
        print(f"  {s:30} {len(labels):2}  {', '.join(labels[:3])}{'...' if len(labels)>3 else ''}")


if __name__ == "__main__":
    main()
