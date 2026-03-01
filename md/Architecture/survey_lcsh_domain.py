#!/usr/bin/env python3
"""
survey_lcsh_domain.py
─────────────────────
Phase 0 survey: read the LCSH landscape for a domain seed heading.

Traverses LCSH in three directions from a seed sh… identifier:
  UP    — BT chain to root (what is the Roman Republic part of?)
  DOWN  — NT descendants (what concepts live under it?)
  ACROSS — RT related terms (what sits beside it at the same level?)

Produces a structured JSON landscape file for synthesis.
No Neo4j. No agents. No QIDs. No SubjectConcepts.
Just: what does LCSH say exists in this domain?

TWO MODES:

  --mode live   (default, recommended)
    Fetches directly from LC Linked Data Service (id.loc.gov).
    Returns full BT/NT/RT links. ~200-300 HTTP requests for a domain.
    Results cached to --cache-dir (default: .lcsh_cache/).
    No local file prerequisites.

    python survey_lcsh_domain.py --mode live --seed sh85115114

  --mode csv
    Reads from local subjects_simplified.csv.
    Faster if CSV is complete, but LC's bulk SKOS dump often lacks
    BT/NT links — use live mode for accurate hierarchy traversal.

    python survey_lcsh_domain.py --mode csv \\
      --csv Subjects/subjects_simplified.csv

LC Linked Data API:
  Base: https://id.loc.gov/authorities/subjects/{sh_id}.skos.json
  Rate limit: ~1 req/sec is safe. Script defaults to 0.3s delay.
  No auth required. Free.
"""

import argparse
import csv
import json
import sys
import time
import urllib.request
import urllib.error
from collections import defaultdict, deque
from pathlib import Path
from datetime import datetime, timezone


# ─────────────────────────────────────────────
# FACET MAPPING
# Map each LCSH heading to the 18 canonical facets
# based on keyword heuristics. Rough guide only —
# synthesis step (LLM) makes final facet assignments.
# ─────────────────────────────────────────────

FACET_KEYWORDS = {
    "MILITARY":       ["war", "warfare", "battle", "army", "legion", "soldier", "military",
                       "campaign", "siege", "conquest", "weapon", "navy", "fleet", "triumph"],
    "POLITICAL":      ["government", "republic", "senate", "consul", "magistrate", "constitution",
                       "law", "election", "assembly", "comitia", "tribun", "praetor", "censor",
                       "dictator", "imperium", "politics", "state"],
    "ECONOMIC":       ["trade", "commerce", "money", "coin", "currency", "tax", "contract",
                       "publicani", "market", "economy", "finance", "debt", "slave", "agriculture",
                       "land", "property", "wealth"],
    "SOCIAL":         ["class", "society", "family", "marriage", "kinship", "patron", "client",
                       "plebeian", "patrician", "freedman", "citizen", "status", "order", "rank"],
    "RELIGIOUS":      ["religion", "cult", "ritual", "augur", "priest", "temple", "sacrifice",
                       "divination", "oracle", "festival", "pontifex", "vestal"],
    "CULTURAL":       ["culture", "identity", "tradition", "custom", "mos maiorum", "virtue",
                       "virtus", "honor", "glory", "symbol", "ideology"],
    "INTELLECTUAL":   ["philosophy", "rhetoric", "oratory", "education", "school", "thought",
                       "idea", "theory", "historiography", "history"],
    "LINGUISTIC":     ["language", "latin", "writing", "script", "inscription", "literature",
                       "text", "document"],
    "GEOGRAPHIC":     ["geography", "territory", "province", "colony", "region", "place",
                       "italy", "rome", "peninsula", "mediterranean"],
    "DEMOGRAPHIC":    ["population", "migration", "colonization", "settlement", "census",
                       "manpower", "slave"],
    "DIPLOMATIC":     ["alliance", "treaty", "diplomacy", "foreign", "embassy", "negotiation",
                       "relation"],
    "ARCHAEOLOGICAL": ["archaeology", "excavation", "artifact", "material", "site", "monument",
                       "inscription", "coin"],
    "ARTISTIC":       ["art", "architecture", "sculpture", "painting", "mosaic", "building",
                       "forum", "temple"],
    "BIOGRAPHIC":     ["biography", "person", "individual", "life", "career", "genealogy",
                       "family"],
    "ENVIRONMENTAL":  ["climate", "environment", "nature", "ecology", "landscape", "geography",
                       "agriculture", "land"],
    "SCIENTIFIC":     ["science", "mathematics", "engineering", "medicine", "technology"],
    "TECHNOLOGICAL":  ["engineering", "aqueduct", "road", "construction", "technology",
                       "infrastructure"],
    "COMMUNICATION":  ["communication", "rhetoric", "speech", "propaganda", "media",
                       "message", "forum"],
}


def assign_facets(label: str, scope_note: str = "") -> list[str]:
    """Heuristic facet assignment from label + scope note text."""
    text = (label + " " + scope_note).lower()
    matched = []
    for facet, keywords in FACET_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            matched.append(facet)
    return matched or ["CULTURAL"]  # default fallback


# ─────────────────────────────────────────────
# LC LINKED DATA — LIVE FETCH
# id.loc.gov per-heading SKOS JSON
# Full BT/NT/RT links, scope notes, alt labels
# ─────────────────────────────────────────────

LC_LD_BASE = "https://id.loc.gov/authorities/subjects/{sh_id}.skos.json"
LC_LD_DELAY = 0.35   # seconds between requests — stay well under rate limit

# SKOS predicates as they appear in LC JSON-LD
SKOS_BROADER  = "http://www.w3.org/2004/02/skos/core#broader"
SKOS_NARROWER = "http://www.w3.org/2004/02/skos/core#narrower"
SKOS_RELATED  = "http://www.w3.org/2004/02/skos/core#related"
SKOS_PREF     = "http://www.w3.org/2004/02/skos/core#prefLabel"
SKOS_ALT      = "http://www.w3.org/2004/02/skos/core#altLabel"
SKOS_SCOPE    = "http://www.w3.org/2004/02/skos/core#scopeNote"
LC_AUTH_BASE  = "http://id.loc.gov/authorities/subjects/"


def _sh_id_from_uri(uri: str) -> str | None:
    """Extract sh… ID from a URI like http://id.loc.gov/authorities/subjects/sh85115114"""
    if not uri:
        return None
    part = uri.rstrip("/").split("/")[-1]
    return part if part.startswith("sh") else None


def _parse_lc_skos(data: list[dict], sh_id: str) -> dict:
    """
    Parse LC SKOS JSON-LD response into a normalised node dict.
    LC returns a list of graph nodes; find the one matching sh_id.
    """
    target_uri = f"{LC_AUTH_BASE}{sh_id}"

    node = None
    for item in data:
        item_id = item.get("@id", "")
        if item_id == target_uri or item_id.endswith(f"/{sh_id}"):
            node = item
            break

    if not node:
        # Fallback: take first item with a prefLabel
        for item in data:
            if SKOS_PREF in item:
                node = item
                break

    if not node:
        return {}

    def get_labels(key):
        vals = node.get(key, [])
        labels = []
        for v in vals:
            if isinstance(v, dict):
                labels.append(v.get("@value", ""))
            elif isinstance(v, str):
                labels.append(v)
        return [l for l in labels if l]

    def get_uris(key):
        vals = node.get(key, [])
        ids = []
        for v in vals:
            uri = v.get("@id", "") if isinstance(v, dict) else str(v)
            sh = _sh_id_from_uri(uri)
            if sh:
                ids.append(sh)
        return ids

    pref_labels = get_labels(SKOS_PREF)
    alt_labels  = get_labels(SKOS_ALT)
    scope_notes = get_labels(SKOS_SCOPE)

    return {
        "id":        sh_id,
        "prefLabel": pref_labels[0] if pref_labels else "",
        "altLabel":  "|".join(alt_labels),
        "scopeNote": scope_notes[0] if scope_notes else "",
        "broader":   get_uris(SKOS_BROADER),
        "narrower":  get_uris(SKOS_NARROWER),
        "related":   get_uris(SKOS_RELATED),
    }


def fetch_heading(sh_id: str, cache_dir: Path, delay: float = LC_LD_DELAY) -> dict | None:
    """
    Fetch a single LCSH heading from id.loc.gov.
    Caches result to cache_dir/{sh_id}.json.
    Returns normalised node dict or None on failure.
    """
    cache_file = cache_dir / f"{sh_id}.json"

    # Cache hit
    if cache_file.exists():
        try:
            with open(cache_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass  # corrupt cache — refetch

    # Fetch
    url = LC_LD_BASE.format(sh_id=sh_id)
    try:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json",
                     "User-Agent": "ChrystallumSurvey/1.0 (graph1 project)"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
        time.sleep(delay)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"  [404] {sh_id} — not found")
        else:
            print(f"  [HTTP {e.code}] {sh_id}")
        return None
    except Exception as e:
        print(f"  [ERR] {sh_id}: {e}")
        return None

    # Parse
    node = _parse_lc_skos(raw if isinstance(raw, list) else [raw], sh_id)
    if not node:
        return None

    # Cache
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(node, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return node


class LiveIndex:
    """
    On-demand index that fetches from id.loc.gov as nodes are needed.
    Presents the same interface as the CSV-based index (by_id dict)
    so traversal functions work identically in both modes.
    """

    def __init__(self, cache_dir: Path, delay: float = LC_LD_DELAY):
        self.cache_dir = cache_dir
        self.delay     = delay
        self._cache: dict[str, dict] = {}
        self._fetched  = 0
        self._hits     = 0

    def get(self, sh_id: str) -> dict | None:
        if sh_id in self._cache:
            self._hits += 1
            return self._cache[sh_id]
        node = fetch_heading(sh_id, self.cache_dir, self.delay)
        self._fetched += 1
        if node:
            self._cache[sh_id] = node
        return node

    @property
    def stats(self):
        return {"fetched": self._fetched, "cache_hits": self._hits,
                "total": self._fetched + self._hits}


def build_live_index(seed_id: str, cache_dir: Path,
                     depth_down: int = 5, depth_up: int = 10,
                     max_nodes: int = 500,
                     delay: float = LC_LD_DELAY) -> tuple[LiveIndex, dict]:
    """
    Pre-fetch all nodes needed for the survey by BFS from seed.
    Returns (live_index, {by_id: ..., by_label: ...}) in CSV-index format.
    """
    print(f"Fetching from LC Linked Data (id.loc.gov)...")
    print(f"  Cache: {cache_dir}")
    print(f"  Delay: {delay}s between requests")
    print()

    index = LiveIndex(cache_dir, delay)
    to_fetch = deque([(seed_id, 0, "seed")])
    visited  = set()
    by_id    = {}
    by_label = {}

    while to_fetch:
        sh_id, depth, direction = to_fetch.popleft()
        if sh_id in visited:
            continue
        visited.add(sh_id)

        node = index.get(sh_id)
        if not node:
            continue

        by_id[sh_id] = node
        label = node.get("prefLabel", "")
        if label:
            by_label[label.lower()] = sh_id
        for alt in node.get("altLabel", "").split("|"):
            if alt.strip():
                by_label[alt.strip().lower()] = sh_id

        fetched = index.stats["fetched"]
        cached  = index.stats["cache_hits"]
        print(f"  [{fetched}f/{cached}c] {sh_id}: {label[:60]}", end="\r", flush=True)

        # Queue upward (BT)
        if direction in ("seed", "up") and depth < depth_up:
            for bt in node.get("broader", []):
                if bt not in visited:
                    to_fetch.append((bt, depth + 1, "up"))

        # Queue siblings (other NT of same BT parent — fetch parent's narrower)
        if direction == "seed":
            for bt in node.get("broader", []):
                if bt not in visited:
                    to_fetch.append((bt, depth + 1, "up"))

        # Queue downward (NT)
        if direction in ("seed", "down") and depth < depth_down:
            if len(by_id) < max_nodes:
                for nt in node.get("narrower", []):
                    if nt not in visited:
                        to_fetch.append((nt, depth + 1, "down"))

        # Queue related (RT) — one level only
        if direction == "seed":
            for rt in node.get("related", []):
                if rt not in visited:
                    to_fetch.append((rt, 1, "related"))

    print()  # clear \r line
    s = index.stats
    print(f"  Done: {s['fetched']} fetched, {s['cache_hits']} from cache, "
          f"{len(by_id)} nodes total")
    print()

    return index, {"by_id": by_id, "by_label": by_label}


# ─────────────────────────────────────────────
# CSV LOADER
# ─────────────────────────────────────────────

def load_lcsh_csv(csv_path: str) -> dict:
    """
    Load subjects_simplified.csv into memory.

    Expected columns: id, prefLabel, altLabel, broader, narrower
    broader and narrower are pipe-separated lists of sh… IDs.

    Returns:
      index = {
        'by_id':    {sh_id: {id, prefLabel, altLabel, broader, narrower}},
        'by_label': {normalised_label: sh_id},
      }
    """
    path = Path(csv_path)
    if not path.exists():
        print(f"ERROR: {csv_path} not found.")
        print("Build with:")
        print("  cd Subjects")
        print("  python -c \"import gzip,shutil; gzip.open(...) ...\"  # decompress")
        print("  python simplify_skos_to_csv.py")
        sys.exit(1)

    print(f"Loading LCSH from {csv_path} ...", end=" ", flush=True)
    t0 = time.time()

    by_id    = {}
    by_label = {}

    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sh_id = row.get("id", "").strip()
            if not sh_id or not sh_id.startswith("sh"):
                continue

            pref = row.get("prefLabel", "").strip()
            alt  = row.get("altLabel", "").strip()

            # broader/narrower: pipe-separated sh… IDs
            broader  = [x.strip() for x in row.get("broader", "").split("|") if x.strip()]
            narrower = [x.strip() for x in row.get("narrower", "").split("|") if x.strip()]
            related  = [x.strip() for x in row.get("related", "").split("|") if x.strip()]

            entry = {
                "id":        sh_id,
                "prefLabel": pref,
                "altLabel":  alt,
                "broader":   broader,
                "narrower":  narrower,
                "related":   related,
            }
            by_id[sh_id] = entry

            if pref:
                by_label[pref.lower()] = sh_id
            if alt:
                for a in alt.split("|"):
                    a = a.strip()
                    if a:
                        by_label[a.lower()] = sh_id

    elapsed = time.time() - t0
    print(f"{len(by_id):,} headings loaded in {elapsed:.1f}s")

    return {"by_id": by_id, "by_label": by_label}


# ─────────────────────────────────────────────
# TRAVERSAL — UP (BT chain to root)
# ─────────────────────────────────────────────

def traverse_up(seed_id: str, index: dict, max_depth: int = 10) -> list[dict]:
    """
    Walk BT chain from seed to root.
    Returns ordered list from seed upward: [seed_parent, grandparent, ..., root]
    Each node: {id, prefLabel, depth, children_of}
    """
    by_id = index["by_id"]
    chain = []
    visited = set()
    current_id = seed_id
    depth = 0

    while depth < max_depth:
        node = by_id.get(current_id)
        if not node:
            break
        broader = node.get("broader", [])
        if not broader:
            break  # reached root

        for parent_id in broader:
            if parent_id in visited:
                continue
            visited.add(parent_id)
            parent = by_id.get(parent_id)
            if not parent:
                continue
            depth += 1
            chain.append({
                "id":         parent_id,
                "prefLabel":  parent["prefLabel"],
                "altLabel":   parent["altLabel"],
                "depth_above_seed": depth,
                "child_id":   current_id,
                "narrower_count": len(parent.get("narrower", [])),
                "facets":     assign_facets(parent["prefLabel"]),
            })
            current_id = parent_id
            break  # follow first BT only (LCSH headings usually have one BT)

    return chain


# ─────────────────────────────────────────────
# TRAVERSAL — DOWN (NT descendants, BFS)
# ─────────────────────────────────────────────

def traverse_down(seed_id: str, index: dict, max_depth: int = 5,
                  max_nodes: int = 500) -> dict:
    """
    BFS downward through NT (narrower) relationships.
    Returns nested structure + flat list.

    Returns: {
      'tree':  nested dict,
      'flat':  [{id, prefLabel, depth, parent_id, facets}, ...],
      'count': int,
      'depth_reached': int,
    }
    """
    by_id = index["by_id"]
    flat = []
    visited = set([seed_id])
    queue = deque([(seed_id, 0, None)])  # (id, depth, parent_id)
    depth_reached = 0

    while queue and len(flat) < max_nodes:
        node_id, depth, parent_id = queue.popleft()

        if depth > max_depth:
            continue

        node = by_id.get(node_id)
        if not node:
            continue

        if depth > 0:  # don't include seed itself in flat list
            flat.append({
                "id":         node_id,
                "prefLabel":  node["prefLabel"],
                "altLabel":   node["altLabel"],
                "depth":      depth,
                "parent_id":  parent_id,
                "narrower_count": len(node.get("narrower", [])),
                "related_count":  len(node.get("related", [])),
                "facets":     assign_facets(node["prefLabel"]),
                "is_leaf":    len(node.get("narrower", [])) == 0,
            })
            depth_reached = max(depth_reached, depth)

        for child_id in node.get("narrower", []):
            if child_id not in visited:
                visited.add(child_id)
                queue.append((child_id, depth + 1, node_id))

    return {
        "flat":          flat,
        "count":         len(flat),
        "depth_reached": depth_reached,
        "truncated":     len(flat) >= max_nodes,
    }


# ─────────────────────────────────────────────
# TRAVERSAL — ACROSS (RT related terms)
# ─────────────────────────────────────────────

def traverse_across(seed_id: str, index: dict) -> list[dict]:
    """
    Collect RT (related) terms for the seed heading.
    Also collect siblings — other NT children of the seed's BT parent.
    """
    by_id = index["by_id"]
    seed = by_id.get(seed_id, {})
    related = []

    # Direct RT links
    for rt_id in seed.get("related", []):
        node = by_id.get(rt_id)
        if node:
            related.append({
                "id":           rt_id,
                "prefLabel":    node["prefLabel"],
                "relationship": "RT",
                "facets":       assign_facets(node["prefLabel"]),
            })

    # Siblings — other NT of same BT parent
    for bt_id in seed.get("broader", []):
        parent = by_id.get(bt_id)
        if not parent:
            continue
        for sibling_id in parent.get("narrower", []):
            if sibling_id == seed_id:
                continue
            sibling = by_id.get(sibling_id)
            if sibling:
                related.append({
                    "id":           sibling_id,
                    "prefLabel":    sibling["prefLabel"],
                    "relationship": "SIBLING",
                    "parent_id":    bt_id,
                    "parent_label": parent["prefLabel"],
                    "facets":       assign_facets(sibling["prefLabel"]),
                })

    return related


# ─────────────────────────────────────────────
# DIMENSIONAL SUMMARY
# Group descendants by facet for synthesis
# ─────────────────────────────────────────────

def build_dimensional_summary(descendants: list[dict]) -> dict:
    """
    Group all descendants by their assigned facets.
    Shows which dimensions of the domain LCSH covers most densely.
    """
    by_facet = defaultdict(list)
    for node in descendants:
        for facet in node.get("facets", ["CULTURAL"]):
            by_facet[facet].append({
                "id":        node["id"],
                "prefLabel": node["prefLabel"],
                "depth":     node["depth"],
            })

    summary = {}
    for facet, nodes in sorted(by_facet.items(), key=lambda x: -len(x[1])):
        summary[facet] = {
            "count": len(nodes),
            "sample": nodes[:10],  # first 10 as illustration
        }
    return summary


# ─────────────────────────────────────────────
# HIERARCHY POSITION STATEMENT
# Human-readable summary of where seed sits
# ─────────────────────────────────────────────

def build_position_statement(seed: dict, ancestors: list[dict],
                             descendants: dict, related: list[dict]) -> str:
    """
    Generate a plain-English statement of where the seed sits
    in the LCSH hierarchy. Feeds directly into synthesis prompt.
    """
    lines = []

    label = seed.get("prefLabel", seed.get("id"))
    lines.append(f"LCSH POSITION: {label} ({seed['id']})")
    lines.append("")

    # Upward chain
    if ancestors:
        chain = " → ".join(
            a["prefLabel"] for a in reversed(ancestors)
        )
        lines.append(f"IS PART OF (upward): {chain} → {label}")
    else:
        lines.append("IS PART OF: [root — no broader terms]")

    lines.append("")

    # Downward
    desc = descendants
    lines.append(f"CONTAINS (downward): {desc['count']} subject headings")
    lines.append(f"  Depth reached: {desc['depth_reached']} levels")
    if desc.get("truncated"):
        lines.append("  (truncated — more exist)")

    lines.append("")

    # Siblings
    siblings = [r for r in related if r["relationship"] == "SIBLING"]
    rt_terms = [r for r in related if r["relationship"] == "RT"]

    if siblings:
        sib_labels = ", ".join(s["prefLabel"] for s in siblings[:8])
        lines.append(f"PEERS (siblings under same BT): {sib_labels}")

    if rt_terms:
        rt_labels = ", ".join(r["prefLabel"] for r in rt_terms[:8])
        lines.append(f"RELATED TERMS (RT): {rt_labels}")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# MAIN SURVEY
# ─────────────────────────────────────────────

def run_survey(
    seed_id: str,
    out_path: str,
    mode: str = "live",
    csv_path: str = "Subjects/subjects_simplified.csv",
    cache_dir: str = ".lcsh_cache",
    delay: float = LC_LD_DELAY,
    depth_down: int = 5,
    depth_up: int = 10,
    max_descendants: int = 500,
    include_facets: bool = True,
) -> dict:

    # Load — live or csv
    if mode == "live":
        _, index = build_live_index(
            seed_id    = seed_id,
            cache_dir  = Path(cache_dir),
            depth_down = depth_down,
            depth_up   = depth_up,
            max_nodes  = max_descendants,
            delay      = delay,
        )
    else:
        index = load_lcsh_csv(csv_path)

    by_id = index["by_id"]

    seed = by_id.get(seed_id)
    if not seed:
        print(f"ERROR: Seed {seed_id} not found in LCSH index.")
        print("Check that subjects_simplified.csv contains this heading.")
        sys.exit(1)

    print(f"Seed: {seed['prefLabel']} ({seed_id})")
    print()

    # Traverse
    print("Traversing UP (BT ancestors)...", end=" ", flush=True)
    ancestors = traverse_up(seed_id, index, max_depth=depth_up)
    print(f"{len(ancestors)} levels")

    print("Traversing DOWN (NT descendants)...", end=" ", flush=True)
    descendants = traverse_down(seed_id, index,
                                max_depth=depth_down,
                                max_nodes=max_descendants)
    print(f"{descendants['count']} headings, depth {descendants['depth_reached']}")

    print("Traversing ACROSS (RT + siblings)...", end=" ", flush=True)
    related = traverse_across(seed_id, index)
    siblings = [r for r in related if r["relationship"] == "SIBLING"]
    rt_terms = [r for r in related if r["relationship"] == "RT"]
    print(f"{len(siblings)} siblings, {len(rt_terms)} RT terms")

    print()

    # Dimensional summary
    dim_summary = build_dimensional_summary(descendants["flat"]) if include_facets else {}

    # Position statement
    position = build_position_statement(seed, ancestors, descendants, related)
    print(position)
    print()

    # Build output
    result = {
        "meta": {
            "survey_type":    "lcsh_domain",
            "mode":           mode,
            "seed_id":        seed_id,
            "seed_label":     seed["prefLabel"],
            "seed_altLabel":  seed["altLabel"],
            "surveyed_at":    datetime.now(timezone.utc).isoformat(),
            "source":         "LC Linked Data (id.loc.gov)" if mode == "live" else str(csv_path),
            "parameters": {
                "depth_down":       depth_down,
                "depth_up":         depth_up,
                "max_descendants":  max_descendants,
            },
            "stats": {
                "ancestors":    len(ancestors),
                "descendants":  descendants["count"],
                "depth_reached": descendants["depth_reached"],
                "truncated":    descendants["truncated"],
                "siblings":     len(siblings),
                "rt_terms":     len(rt_terms),
                "total_nodes":  1 + len(ancestors) + descendants["count"] + len(related),
            },
        },

        "seed": {
            "id":        seed_id,
            "prefLabel": seed["prefLabel"],
            "altLabel":  seed["altLabel"],
            "broader":   seed.get("broader", []),
            "narrower":  seed.get("narrower", []),
            "related":   seed.get("related", []),
            "facets":    assign_facets(seed["prefLabel"]) if include_facets else [],
        },

        # Upward chain — what the Roman Republic is PART OF
        "ancestors": ancestors,

        # Downward — what lives WITHIN the Roman Republic in LCSH
        "descendants": {
            "count":         descendants["count"],
            "depth_reached": descendants["depth_reached"],
            "truncated":     descendants["truncated"],
            "nodes":         descendants["flat"],
        },

        # Sideways — peers and related concepts
        "related": {
            "siblings": siblings,
            "rt_terms": rt_terms,
        },

        # Dimensional breakdown by facet
        "dimensional_summary": dim_summary,

        # Plain-English position statement for synthesis prompt
        "position_statement": position,

        # Synthesis prompt — ready to send to LLM
        "synthesis_prompt": build_synthesis_prompt(
            seed, ancestors, descendants, related, dim_summary
        ),
    }

    # Write
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Survey written to {out_path}")
    print(f"Total nodes mapped: {result['meta']['stats']['total_nodes']}")
    return result


# ─────────────────────────────────────────────
# SYNTHESIS PROMPT
# Ready-to-use LLM prompt for domain pack decomposition
# ─────────────────────────────────────────────

def build_synthesis_prompt(seed: dict, ancestors: list[dict],
                           descendants: dict, related: list[dict],
                           dim_summary: dict) -> str:
    """
    Build the synthesis prompt that feeds the next phase.
    The LLM receives this and proposes SubjectConcepts grounded
    in the LCSH landscape.
    """

    ancestor_chain = " → ".join(
        a["prefLabel"] for a in reversed(ancestors)
    ) + f" → {seed['prefLabel']}"

    siblings = [r for r in related if r["relationship"] == "SIBLING"]
    rt_terms = [r for r in related if r["relationship"] == "RT"]

    # Top descendants by depth level
    by_depth = defaultdict(list)
    for node in descendants["flat"]:
        by_depth[node["depth"]].append(node["prefLabel"])

    depth_summary = ""
    for d in sorted(by_depth.keys()):
        labels = by_depth[d]
        sample = ", ".join(labels[:12])
        more = f" (+ {len(labels)-12} more)" if len(labels) > 12 else ""
        depth_summary += f"  Level {d}: {sample}{more}\n"

    dim_lines = ""
    for facet, data in list(dim_summary.items())[:8]:
        sample = ", ".join(n["prefLabel"] for n in data["sample"][:5])
        dim_lines += f"  {facet} ({data['count']} headings): {sample}\n"

    prompt = f"""You are a domain knowledge architect building a navigation structure for the domain: {seed['prefLabel']}.

The Library of Congress Subject Headings (LCSH) has mapped this domain as follows:

HIERARCHY POSITION
{ancestor_chain}

PEER CONCEPTS (same level, same parent)
{chr(10).join('  - ' + s['prefLabel'] for s in siblings[:10])}

RELATED TERMS (RT links in LCSH)
{chr(10).join('  - ' + r['prefLabel'] for r in rt_terms[:10])}

CONCEPTS WITHIN THIS DOMAIN ({descendants['count']} total, depth {descendants['depth_reached']} levels)
{depth_summary}
DIMENSIONAL DISTRIBUTION (by scholarly facet)
{dim_lines}

YOUR TASK

1. POSITION the domain in its hierarchies:
   - What is it politically? (what does it descend from, what are its peers?)
   - What is it temporally? (what period does it occupy, what came before/after?)
   - What is it geographically? (what region, what larger geography?)
   - What is it civilisationally? (what tradition, what broader culture?)

2. PROPOSE SubjectConcepts for a domain navigation pack:
   - Each SubjectConcept should be a navigable node, not a flat category
   - Grounded in the LCSH headings listed above
   - Positioned in multiple hierarchies simultaneously
   - At the right granularity: not so broad as to be useless, 
     not so narrow as to fragment navigation
   - Name the LCSH heading(s) that ground each proposal
   - Assign the primary facet from: ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC,
     COMMUNICATION, CULTURAL, DEMOGRAPHIC, DIPLOMATIC, ECONOMIC, 
     ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC, MILITARY,
     POLITICAL, RELIGIOUS, SCIENTIFIC, SOCIAL, TECHNOLOGICAL

3. IDENTIFY gaps:
   - What aspects of this domain are NOT covered by LCSH?
   - What navigation paths are missing from the LCSH structure?
   - What would a researcher need that the headings don't provide?

Respond with structured JSON:
{{
  "domain_position": {{
    "political_hierarchy": ["...", "...", "{seed['prefLabel']}"],
    "temporal_position": {{"period": "...", "before": "...", "after": "..."}},
    "geographic_position": {{"place": "...", "region": "...", "larger": "..."}},
    "civilisational_position": ["...", "..."]
  }},
  "subject_concept_proposals": [
    {{
      "label": "...",
      "primary_facet": "...",
      "related_facets": ["...", "..."],
      "lcsh_anchors": ["sh...", "sh..."],
      "lcsh_labels": ["...", "..."],
      "navigation_note": "how a researcher arrives at this concept",
      "confidence": 0.0-1.0
    }}
  ],
  "gaps": [
    {{
      "description": "...",
      "why_missing": "..."
    }}
  ]
}}"""

    return prompt


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Survey LCSH domain landscape from a seed heading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Live mode (recommended) — fetches from id.loc.gov, caches locally
  python survey_lcsh_domain.py --seed sh85115114

  # CSV mode — reads local subjects_simplified.csv
  python survey_lcsh_domain.py --mode csv --csv Subjects/subjects_simplified.csv

  # Deeper traversal, more descendants
  python survey_lcsh_domain.py --depth 7 --max-descendants 1000

  # Faster fetching (be polite to LC servers)
  python survey_lcsh_domain.py --delay 0.2
        """
    )
    parser.add_argument("--seed",    default="sh85115114",
                        help="Seed sh ID (default: sh85115114 = Rome--History--Republic)")
    parser.add_argument("--mode",    default="live", choices=["live", "csv"],
                        help="live = fetch from id.loc.gov (default); csv = local file")
    parser.add_argument("--csv",     default="Subjects/subjects_simplified.csv",
                        help="[csv mode] Path to subjects_simplified.csv")
    parser.add_argument("--cache-dir", default=".lcsh_cache",
                        help="[live mode] Directory to cache fetched headings (default: .lcsh_cache)")
    parser.add_argument("--delay",   type=float, default=LC_LD_DELAY,
                        help=f"[live mode] Seconds between HTTP requests (default: {LC_LD_DELAY})")
    parser.add_argument("--out",     default="output/surveys/lcsh_roman_republic.json",
                        help="Output JSON path")
    parser.add_argument("--depth",   type=int, default=5,
                        help="Max depth for downward traversal (default: 5)")
    parser.add_argument("--depth-up", type=int, default=10,
                        help="Max depth for upward traversal (default: 10)")
    parser.add_argument("--max-descendants", type=int, default=500,
                        help="Max descendant nodes (default: 500)")
    parser.add_argument("--no-facets", action="store_true",
                        help="Skip facet assignment (faster)")

    args = parser.parse_args()

    result = run_survey(
        seed_id         = args.seed,
        out_path        = args.out,
        mode            = args.mode,
        csv_path        = args.csv,
        cache_dir       = args.cache_dir,
        delay           = args.delay,
        depth_down      = args.depth,
        depth_up        = args.depth_up,
        max_descendants = args.max_descendants,
        include_facets  = not args.no_facets,
    )

    # Print synthesis prompt preview
    print()
    print("-" * 60)
    print("SYNTHESIS PROMPT (first 800 chars):")
    print("-" * 60)
    print(result["synthesis_prompt"][:800] + "...")
    print()
    print(f"Output: {args.out}")
    print("Next: feed synthesis_prompt to Claude or Perplexity for SubjectConcept proposals")


if __name__ == "__main__":
    main()
