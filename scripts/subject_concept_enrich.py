"""
subject_concept_enrich.py
─────────────────────────────────────────────────────────────────────────────
For every :SubjectConcept node in the graph:
  1. Harvests P571 (inception) and P576 (dissolved) from Wikidata SPARQL
  2. Computes temporal_bucket (REPUBLICAN / IMPERIAL_EARLY / IMPERIAL_LATE /
     LATE_ANTIQUE / PRE_REPUBLICAN / UNKNOWN)
  3. Corrects primary_facet for geographic and archaeological entities
  4. Computes capability_cipher:
       SHA256(qid | temporal_bucket | sorted_authority_keys |
              sorted_fed_source_ids | sorted_facets)
  5. Writes temporal_start, temporal_end, temporal_bucket,
     primary_facet, secondary_facets, capability_cipher,
     cipher_computed_at back to Neo4j

Usage:
    python subject_concept_enrich.py [--dry-run]

Requires:
    pip install neo4j requests python-dotenv
    .env file (or environment) with NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────

NEO4J_URI  = os.getenv("NEO4J_URI",  "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "")

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
WIKIDATA_HEADERS = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "Chrystallum/1.0 (graph enrichment; contact@chrystallum.io)",
}
WIKIDATA_BATCH  = 20       # QIDs per SPARQL VALUES block
WIKIDATA_DELAY  = 1.0      # seconds between requests (rate limit)
WIKIDATA_RETRY  = 3        # retries on HTTP error

# ── TEMPORAL BUCKETS ──────────────────────────────────────────────────────────
# Years are integers; BCE = negative.  Boundaries:
#   PRE_REPUBLICAN  :  < -509
#   REPUBLICAN      :  -509 to -28  (509 BCE → 27 BCE, inclusive)
#   IMPERIAL_EARLY  :  -27  to  284  (27 BCE → 284 CE, Principate)
#   IMPERIAL_LATE   :   285 to  476  (Dominate / late Empire)
#   LATE_ANTIQUE    :  > 476
#   UNKNOWN         :  no date available

def temporal_bucket(year: int | None) -> str:
    if year is None:
        return "UNKNOWN"
    if year < -509:
        return "PRE_REPUBLICAN"
    if year <= -28:
        return "REPUBLICAN"
    if year <= 284:
        return "IMPERIAL_EARLY"
    if year <= 476:
        return "IMPERIAL_LATE"
    return "LATE_ANTIQUE"


# ── FACET CORRECTION MAP ──────────────────────────────────────────────────────
# Keyed by QID.  Override auto-assigned facets from the batch promotion.
# Derived from constitution review: provinces/settlements → Geographic primary;
# temples/cities → Archaeological primary.

FACET_OVERRIDES: dict[str, dict] = {
    # Roman provinces — Geographic primary, Political secondary
    "Q170062":  {"primary": "Geographic", "secondary": ["Political"]},  # Pannonia
    "Q309270":  {"primary": "Geographic", "secondary": ["Political"]},  # Alpes Maritimae
    "Q221353":  {"primary": "Geographic", "secondary": ["Political"]},  # Arabia Petraea
    "Q1254480": {"primary": "Geographic", "secondary": ["Political"]},  # Roman Armenia
    "Q715376":  {"primary": "Geographic", "secondary": ["Political"]},  # Gallia Aquitania
    "Q10971":   {"primary": "Geographic", "secondary": ["Political"]},  # Gallia Lugdunensis
    "Q734505":  {"primary": "Geographic", "secondary": ["Political"]},  # Mauretania Caesariensis
    "Q1247297": {"primary": "Geographic", "secondary": ["Political"]},  # Lower Pannonia
    "Q642188":  {"primary": "Geographic", "secondary": ["Political"]},  # Upper Pannonia
    "Q156789":  {"primary": "Geographic", "secondary": ["Political"]},  # Raetia
    "Q181238":  {"primary": "Geographic", "secondary": ["Political"]},  # Africa
    "Q210718":  {"primary": "Geographic", "secondary": ["Political"]},  # Asia
    "Q913382":  {"primary": "Geographic", "secondary": ["Political"]},  # Bithynia et Pontus
    "Q26897":   {"primary": "Geographic", "secondary": ["Political"]},  # Gallia Narbonensis
    "Q216791":  {"primary": "Geographic", "secondary": ["Political"]},  # Hispania Tarraconensis
    "Q692775":  {"primary": "Geographic", "secondary": ["Political"]},  # Creta et Cyrenaica
    "Q1003997": {"primary": "Geographic", "secondary": ["Political"]},  # Judaea
    "Q753824":  {"primary": "Geographic", "secondary": ["Political"]},  # Illyricum
    "Q11950672":{"primary": "Geographic", "secondary": ["Political"]},  # Syria Phoenice
    "Q1227719": {"primary": "Geographic", "secondary": ["Political"]},  # Moesia Inferior
    "Q188650":  {"primary": "Geographic", "secondary": ["Political"]},  # Lusitania
    "Q204772":  {"primary": "Geographic", "secondary": ["Political"]},  # Achaea
    "Q670837":  {"primary": "Geographic", "secondary": ["Political"]},  # Moesia Superior
    "Q9030702": {"primary": "Geographic", "secondary": ["Political"]},  # Mauretania Sitifensis
    # Cities / settlements — Archaeological primary
    "Q770030":  {"primary": "Archaeological", "secondary": ["Geographic"]},  # Temple of Augustus
    "Q547910":  {"primary": "Archaeological", "secondary": ["Geographic"]},  # Stabiae
    "Q1012797": {"primary": "Archaeological", "secondary": ["Geographic"]},  # Ostia
    "Q11951603":{"primary": "Archaeological", "secondary": ["Geographic"]},  # Tergeste
    # Mixed / borderline — keep Political but add Geographic secondary
    "Q104028":  {"primary": "Political", "secondary": ["Geographic"]},  # Judea
    "Q17167":   {"primary": "Political", "secondary": []},             # Roman Republic (seed)
}

# Federation source IDs inferred from authority property presence
AUTHORITY_TO_FED: dict[str, str] = {
    "viaf_id":      "VIAF",
    "pleiades_id":  "Pleiades",
    "dprr_id":      "DPRR",
    "fast_id":      "LCSH_FAST_LCC",
    "lcsh_id":      "LCSH_FAST_LCC",
    "lcc_id":       "LCSH_FAST_LCC",
    "getty_aat_id": "Getty_AAT",
    "trismegistos_id": "Trismegistos",
    "lgpn_id":      "LGPN",
}

# ── WIKIDATA SPARQL ───────────────────────────────────────────────────────────

def sparql_temporal(qids: list[str]) -> dict[str, dict]:
    """
    Returns { qid: {"inception": int|None, "dissolved": int|None} }
    for a batch of QIDs.  Years are integers (BCE = negative).
    """
    values = " ".join(f"wd:{q}" for q in qids)
    query = f"""
SELECT ?item ?inception ?dissolved WHERE {{
  VALUES ?item {{ {values} }}
  OPTIONAL {{ ?item wdt:P571 ?inception. }}
  OPTIONAL {{ ?item wdt:P576 ?dissolved. }}
}}
"""
    for attempt in range(1, WIKIDATA_RETRY + 1):
        try:
            resp = requests.get(
                WIKIDATA_SPARQL,
                params={"query": query, "format": "json"},
                headers=WIKIDATA_HEADERS,
                timeout=30,
            )
            resp.raise_for_status()
            bindings = resp.json()["results"]["bindings"]
            result: dict[str, dict] = {}
            for row in bindings:
                qid = row["item"]["value"].split("/")[-1]
                def _year(key: str) -> int | None:
                    if key not in row:
                        return None
                    raw = row[key]["value"]          # e.g. "-0508-01-01T00:00:00Z"
                    try:
                        year_str = raw.split("-")[0] if not raw.startswith("-") \
                                   else "-" + raw[1:].split("-")[0]
                        return int(year_str)
                    except (ValueError, IndexError):
                        return None
                entry = result.setdefault(qid, {"inception": None, "dissolved": None})
                if "inception" in row and entry["inception"] is None:
                    entry["inception"] = _year("inception")
                if "dissolved" in row and entry["dissolved"] is None:
                    entry["dissolved"] = _year("dissolved")
            return result
        except requests.RequestException as exc:
            print(f"  [WARN] Wikidata attempt {attempt}/{WIKIDATA_RETRY}: {exc}")
            if attempt < WIKIDATA_RETRY:
                time.sleep(2 ** attempt)
    return {}


# ── CIPHER ────────────────────────────────────────────────────────────────────

def compute_cipher(
    qid: str,
    temporal_bkt: str,
    authority_keys: list[str],
    fed_source_ids: list[str],
    primary_facet: str,
    secondary_facets: list[str],
) -> str:
    facets = sorted(set([primary_facet] + secondary_facets))
    raw = "|".join([
        qid,
        temporal_bkt,
        ",".join(sorted(authority_keys)),
        ",".join(sorted(set(fed_source_ids))),
        ",".join(facets),
    ])
    return hashlib.sha256(raw.encode()).hexdigest()


# ── NEO4J ─────────────────────────────────────────────────────────────────────

FETCH_QUERY = """
MATCH (n:SubjectConcept)
RETURN
  n.qid            AS qid,
  n.label          AS label,
  n.subject_id     AS subject_id,
  n.primary_facet  AS primary_facet,
  n.viaf_id        AS viaf_id,
  n.pleiades_id    AS pleiades_id,
  n.dprr_id        AS dprr_id,
  n.fast_id        AS fast_id,
  n.lcsh_id        AS lcsh_id,
  n.lcc_id         AS lcc_id,
  n.getty_aat_id   AS getty_aat_id,
  n.trismegistos_id AS trismegistos_id,
  n.lgpn_id        AS lgpn_id
"""

WRITE_QUERY = """
UNWIND $rows AS row
MATCH (n:SubjectConcept {qid: row.qid})
SET
  n.temporal_start    = row.temporal_start,
  n.temporal_end      = row.temporal_end,
  n.temporal_bucket   = row.temporal_bucket,
  n.primary_facet     = row.primary_facet,
  n.secondary_facets  = row.secondary_facets,
  n.capability_cipher = row.capability_cipher,
  n.cipher_computed_at = row.cipher_computed_at
RETURN count(n) AS updated
"""


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main(dry_run: bool = False) -> None:
    print(f"{'[DRY RUN] ' if dry_run else ''}subject_concept_enrich.py")
    print(f"  Neo4j : {NEO4J_URI}")
    print(f"  Time  : {datetime.now(timezone.utc).isoformat()}")
    print()

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    # 1 ── Fetch all SubjectConcept nodes
    with driver.session() as session:
        records = session.run(FETCH_QUERY).data()

    print(f"Fetched {len(records)} SubjectConcept nodes")

    # 2 ── Harvest temporal data from Wikidata in batches
    qids = [r["qid"] for r in records if r.get("qid")]
    temporal_data: dict[str, dict] = {}

    for i in range(0, len(qids), WIKIDATA_BATCH):
        batch = qids[i : i + WIKIDATA_BATCH]
        print(f"  Wikidata batch {i // WIKIDATA_BATCH + 1}: {batch}")
        result = sparql_temporal(batch)
        temporal_data.update(result)
        time.sleep(WIKIDATA_DELAY)

    print(f"  Temporal data retrieved for {len(temporal_data)} / {len(qids)} QIDs")
    print()

    # 3 ── Build enriched rows
    rows = []
    now_iso = datetime.now(timezone.utc).isoformat()

    for rec in records:
        qid   = rec.get("qid", "")
        label = rec.get("label", "")

        # Temporal
        td       = temporal_data.get(qid, {})
        t_start  = td.get("inception")
        t_end    = td.get("dissolved")
        t_bucket = temporal_bucket(t_start)

        # Authority keys present on node
        auth_keys = [
            k for k in AUTHORITY_TO_FED
            if rec.get(k) is not None
        ]
        fed_ids = sorted(set(AUTHORITY_TO_FED[k] for k in auth_keys))

        # Facet — apply override map, else keep existing
        override = FACET_OVERRIDES.get(qid)
        if override:
            primary   = override["primary"]
            secondary = override["secondary"]
        else:
            primary   = rec.get("primary_facet") or "Political"
            secondary = []

        # Cipher
        cipher = compute_cipher(qid, t_bucket, auth_keys, fed_ids, primary, secondary)

        row = {
            "qid":              qid,
            "temporal_start":   t_start,
            "temporal_end":     t_end,
            "temporal_bucket":  t_bucket,
            "primary_facet":    primary,
            "secondary_facets": secondary,
            "capability_cipher": cipher,
            "cipher_computed_at": now_iso,
        }
        rows.append(row)

        status = "✓" if t_start is not None else "?"
        print(f"  [{status}] {qid:12s}  {label:35s}  "
              f"bucket={t_bucket:20s}  facet={primary:15s}  cipher={cipher[:12]}…")

    print()
    print(f"Built {len(rows)} enriched rows")

    # 4 ── Write back
    if dry_run:
        print("[DRY RUN] Skipping Neo4j write. Sample row:")
        print(json.dumps(rows[0], indent=2, default=str))
    else:
        with driver.session() as session:
            result = session.run(WRITE_QUERY, rows=rows)
            summary = result.single()
            updated = summary["updated"] if summary else 0
        print(f"Neo4j write complete — {updated} nodes updated")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich SubjectConcept nodes")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch and compute but do not write to Neo4j")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
