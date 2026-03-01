#!/usr/bin/env python3
"""
Survey LCSH domain landscape — CSV or live from id.loc.gov. Produces FederationSurvey
(schema) or legacy JSON for synthesis. Does not touch Neo4j or agents.

Output (--format schema, default):
  - FederationSurvey JSON at output/nodes/ — FederationNode per heading
  - concept_ref, temporal_range from LCSH; spatial_anchor=None (alignment pass)

Output (--format legacy):
  - ancestors, descendants, related, synthesis_prompt — human-readable

Usage (live, schema — no prerequisites):
  python scripts/backbone/subject/survey_lcsh_domain.py --seed sh85115114

Usage (csv mode):
  python scripts/backbone/subject/survey_lcsh_domain.py \\
    --seed sh85115114 --mode csv --csv Subjects/subjects_simplified.csv
"""
import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# Schema lives in scripts/ — add to path when running from backbone/subject
_SCRIPTS = Path(__file__).resolve().parents[2]  # scripts/
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from federation_node_schema import (
    Federation,
    FederationNode,
    FederationSurvey,
    new_node,
    new_survey,
    parse_temporal_from_lcsh,
    validate_survey,
)

# Heuristic keyword → facet for dimensional_summary
FACET_KEYWORDS = {
    "ARCHAEOLOGICAL": ["archaeolog", "excavat", "antiquit", "artifact", "inscription"],
    "ARTISTIC": ["art", "sculpture", "painting", "architecture", "literature", "poetry"],
    "BIOGRAPHIC": ["biograph", "person", "family", "gens", "prosopograph"],
    "COMMUNICATION": ["rhetoric", "oratory", "speech", "propaganda", "communication"],
    "CULTURAL": ["culture", "custom", "identity", "romanitas", "ideology"],
    "DEMOGRAPHIC": ["population", "demograph", "census", "migration"],
    "DIPLOMATIC": ["diplomac", "treaty", "embassy", "international", "alliance"],
    "ECONOMIC": ["economic", "trade", "commerce", "agriculture", "land", "finance", "tax"],
    "ENVIRONMENTAL": ["environment", "climate", "geography", "natural"],
    "GEOGRAPHIC": ["geograph", "province", "region", "place", "territory", "expansion"],
    "INTELLECTUAL": ["philosoph", "historiograph", "intellectual", "constitution", "law"],
    "LINGUISTIC": ["language", "latin", "greek", "linguistic"],
    "MILITARY": ["military", "war", "battle", "army", "navy", "campaign", "legion"],
    "POLITICAL": ["politic", "government", "senate", "magistrate", "constitution", "republic"],
    "RELIGIOUS": ["religion", "cult", "priest", "ritual", "augur", "temple"],
    "SCIENTIFIC": ["science", "medicine", "astronomy", "mathematic"],
    "SOCIAL": ["social", "society", "patronage", "slavery", "class", "plebeian", "patrician"],
    "TECHNOLOGICAL": ["technology", "engineering", "construction"],
}


def _extract_id(uri: str) -> str:
    """Extract sh... from full URI or return as-is if already short."""
    if not uri:
        return ""
    s = uri.strip()
    if s.startswith("sh") and re.match(r"sh\d{8}(-\d{3})?$", s):
        return s
    return s.split("/")[-1].strip() if "/" in s else s


def _assign_facet(pref_label: str) -> str:
    """Heuristic facet from heading text."""
    label_lower = (pref_label or "").lower()
    scores = {}
    for facet, keywords in FACET_KEYWORDS.items():
        scores[facet] = sum(1 for k in keywords if k in label_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "CULTURAL"


# --- Live fetch from id.loc.gov ---
BASE_URL = "https://id.loc.gov"
SKOS_BROADER = "http://www.w3.org/2004/02/skos/core#broader"
SKOS_NARROWER = "http://www.w3.org/2004/02/skos/core#narrower"
SKOS_RELATED = "http://www.w3.org/2004/02/skos/core#related"
SKOS_PREFLABEL = "http://www.w3.org/2004/02/skos/core#prefLabel"
SKOS_ALTLABEL = "http://www.w3.org/2004/02/skos/core#altLabel"
MADS_COMPONENT = "http://www.loc.gov/mads/rdf/v1#componentList"
MADS_AUTHLABEL = "http://www.loc.gov/mads/rdf/v1#authoritativeLabel"


def _get_label(obj: dict | list) -> str:
    """Extract @value from label object."""
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict) and "@value" in item:
                return (item.get("@value") or "").strip()
        return ""
    if isinstance(obj, dict) and "@value" in obj:
        return (obj.get("@value") or "").strip()
    return ""


def _get_id_list(obj: dict | list) -> list[str]:
    """Extract @id from object or list of objects."""
    out = []
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict) and "@id" in item:
                uid = item.get("@id", "")
                if uid and not uid.startswith("_:"):
                    out.append(uid)
            elif isinstance(item, dict) and "@list" in item:
                out.extend(_get_id_list(item["@list"]))
    elif isinstance(obj, dict) and "@id" in obj:
        uid = obj.get("@id", "")
        if uid and not uid.startswith("_:"):
            out.append(uid)
    return out


def fetch_lcsh_resource(url: str, cache_dir: Path, delay: float) -> dict | list | None:
    """Fetch JSON from id.loc.gov with caching. Returns parsed JSON or None."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    # Cache key: path after id.loc.gov
    path = url.replace(BASE_URL, "").lstrip("/")
    safe = path.replace("/", "_").replace("?", "_")
    cache_file = cache_dir / f"{safe}.json"
    if cache_file.exists():
        with open(cache_file, encoding="utf-8") as f:
            return json.load(f)
    try:
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "Graph1-LCSH-Survey/1.0 (https://github.com/; survey tool)",
        })
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        time.sleep(delay)
        return data
    except Exception as e:
        print(f"  [WARN] Fetch failed {url}: {e}")
        return None


def suggest2_lcsh(q: str, cache_dir: Path, delay: float, count: int = 250) -> list[dict]:
    """Suggest2 API: left-anchored search. Returns list of {uri, label}."""
    url = f"{BASE_URL}/authorities/subjects/suggest2?q={urllib.parse.quote(q)}&count={count}"
    data = fetch_lcsh_resource(url, cache_dir, delay)
    if not data or not isinstance(data, list):
        return []
    # Format: [query, [labels], [counts], [uris]]
    if len(data) >= 4:
        labels, uris = data[1], data[3]
        return [{"uri": u, "label": l} for u, l in zip(uris, labels)]
    return []


def _normalize_uri(uri: str) -> str:
    """Normalize subject URI for comparison (e.g. http vs https, trailing slash)."""
    return (uri or "").replace("https://", "http://").rstrip("/")


def parse_mads_to_record(graph: list, subject_uri: str) -> dict:
    """Parse MADS/SKOS JSON graph into record {prefLabel, broader, narrower, related}."""
    subject_uri = _normalize_uri(subject_uri)
    record = {"prefLabel": "", "broader": [], "narrower": [], "related": []}
    main = None
    id_to_label = {}

    for item in graph:
        if not isinstance(item, dict):
            continue
        iid = _normalize_uri(item.get("@id", ""))
        if iid == subject_uri:
            main = item
        # Collect labels from all nodes
        for pred in [SKOS_PREFLABEL, MADS_AUTHLABEL]:
            val = item.get(pred)
            if val:
                lbl = _get_label(val)
                if lbl and iid and not iid.startswith("_:"):
                    id_to_label[iid] = lbl

    if not main:
        return record

    record["prefLabel"] = _get_label(main.get(SKOS_PREFLABEL) or main.get(MADS_AUTHLABEL))

    for pred, key in [(SKOS_BROADER, "broader"), (SKOS_NARROWER, "narrower"), (SKOS_RELATED, "related")]:
        val = main.get(pred)
        if val:
            record[key] = _get_id_list(val) if isinstance(val, list) else _get_id_list([val])

    # MADS componentList: parent = components without last (for ComplexSubject)
    comp = main.get(MADS_COMPONENT)
    if comp and isinstance(comp, list) and not record["broader"]:
        for c in comp:
            if isinstance(c, dict) and "@list" in c:
                ids = [x.get("@id") for x in c["@list"] if isinstance(x, dict)]
                ids = [x for x in ids if x and not str(x).startswith("_:")]
                if len(ids) >= 2:
                    # Parent = single sh... if only one topic component, else use label lookup
                    parent_sh = [x for x in ids if _extract_id(x).startswith("sh")]
                    if len(parent_sh) == 1:
                        record["broader"] = [f"{BASE_URL}/authorities/subjects/{_extract_id(parent_sh[0])}"]
                    break

    return record


def load_from_live(
    seed_id: str,
    cache_dir: Path,
    delay: float,
    max_depth: int = 5,
) -> tuple[dict, dict, dict]:
    """Traverse id.loc.gov from seed, return (by_id, children_of, parents_of)."""
    by_id = {}
    children_of = {}
    parents_of = {}
    seed_uri = f"{BASE_URL}/authorities/subjects/{seed_id}"
    to_fetch = [seed_uri]
    seen = {seed_uri}

    while to_fetch:
        url = to_fetch.pop(0)
        data = fetch_lcsh_resource(url, cache_dir, delay)
        if not data:
            continue
        graph = data if isinstance(data, list) else data.get("@graph", [data])
        rec = parse_mads_to_record(graph, url)
        cid = _extract_id(url)
        if not cid:
            continue
        pref = rec.get("prefLabel", "")
        by_id[cid] = {"lcsh_id": cid, "prefLabel": pref, "altLabel": "", "broader": "|".join(rec["broader"]), "narrower": "|".join(rec["narrower"])}

        for b in rec["broader"]:
            bid = _extract_id(b)
            if bid and bid.startswith("sh"):
                parents_of.setdefault(cid, set()).add(bid)
                children_of.setdefault(bid, set()).add(cid)
                buri = b if b.startswith("http") else f"{BASE_URL}/authorities/subjects/{bid}"
                if buri not in seen:
                    seen.add(buri)
                    to_fetch.append(buri)

        for n in rec["narrower"]:
            nid = _extract_id(n)
            if nid and nid.startswith("sh"):
                children_of.setdefault(cid, set()).add(nid)
                parents_of.setdefault(nid, set()).add(cid)
                nuri = n if n.startswith("http") else f"{BASE_URL}/authorities/subjects/{nid}"
                if nuri not in seen:
                    seen.add(nuri)
                    to_fetch.append(nuri)

        # Suggest2 fallback for narrower (LCSH subdivision style)
        if not rec["narrower"] and pref and len(by_id) < 500:
            parts = pref.split("--")
            base = "--".join(parts[:2] + [parts[2].split(",")[0].strip()]) if len(parts) >= 3 else pref
            for hit in suggest2_lcsh(base, cache_dir, delay):
                uri = hit.get("uri", "")
                label = hit.get("label", "")
                if not uri or uri == url or not label:
                    continue
                if label == pref:
                    continue
                if not (label.startswith(pref + "--") or (base in label and label != pref)):
                    continue
                nid = _extract_id(uri)
                if nid and nid.startswith("sh") and nid not in by_id:
                    children_of.setdefault(cid, set()).add(nid)
                    parents_of.setdefault(nid, set()).add(cid)
                    if uri not in seen:
                        seen.add(uri)
                        to_fetch.append(uri)

    return by_id, children_of, parents_of


def load_csv(csv_path: Path) -> tuple[dict, dict, dict]:
    """Load CSV, return (by_id, children_of, parents_of)."""
    by_id = {}
    children_of = {}
    parents_of = {}

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_id = row.get("id", "").strip()
            lcsh_id = _extract_id(raw_id)
            if not lcsh_id:
                continue

            pref = (row.get("prefLabel") or "").strip()
            alt = (row.get("altLabel") or "").strip()
            broader = (row.get("broader") or "").strip()
            narrower = (row.get("narrower") or "").strip()

            by_id[lcsh_id] = {
                "lcsh_id": lcsh_id,
                "prefLabel": pref,
                "altLabel": alt,
                "broader": broader,
                "narrower": narrower,
            }

            for b in broader.split("|") if broader else []:
                b_id = _extract_id(b)
                if b_id:
                    parents_of.setdefault(lcsh_id, set()).add(b_id)
                    children_of.setdefault(b_id, set()).add(lcsh_id)

            for n in narrower.split("|") if narrower else []:
                n_id = _extract_id(n)
                if n_id:
                    children_of.setdefault(lcsh_id, set()).add(n_id)
                    parents_of.setdefault(n_id, set()).add(lcsh_id)

    return by_id, children_of, parents_of


def collect_ancestors(seed_id: str, by_id: dict, parents_of: dict, max_depth: int = 20) -> list[dict]:
    """Walk up broader chain. Returns list from root to seed (exclusive)."""
    chain = []
    seen = set()
    current = seed_id
    for _ in range(max_depth):
        if not current or current in seen:
            break
        parents = parents_of.get(current, set())
        if not parents:
            break
        # Take first parent (LCSH usually has one broader)
        parent_id = next(iter(parents))
        if parent_id in seen:
            break
        rec = by_id.get(parent_id, {})
        chain.append({
            "lcsh_id": parent_id,
            "prefLabel": rec.get("prefLabel", ""),
            "depth": len(chain),
        })
        seen.add(parent_id)
        current = parent_id

    # Fallback: build from label prefix (LCSH subdivision style)
    if not chain:
        seed_pref = by_id.get(seed_id, {}).get("prefLabel", "")
        if seed_pref and "--" in seed_pref:
            # e.g. "Rome--History--Republic, 510-30 B.C." -> ["Rome", "History", "Republic, 510-30 B.C."]
            parts = seed_pref.split("--")
            for i in range(len(parts) - 1, 0, -1):
                prefix = "--".join(parts[:i])
                for cid, rec in by_id.items():
                    if rec.get("prefLabel") == prefix:
                        chain.append({
                            "lcsh_id": cid,
                            "prefLabel": prefix,
                            "depth": len(chain),
                        })
                        break
    return chain


def collect_descendants(
    seed_id: str,
    by_id: dict,
    children_of: dict,
    max_depth: int = 5,
) -> list[dict]:
    """Walk down narrower chain. Returns flat list with depth and heuristic facet."""
    out = []
    queue = [(seed_id, 0)]
    seen = {seed_id}

    while queue:
        node_id, depth = queue.pop(0)
        if depth >= max_depth:
            continue
        children = children_of.get(node_id, set())
        for cid in sorted(children):
            if cid in seen:
                continue
            seen.add(cid)
            rec = by_id.get(cid, {})
            pref = rec.get("prefLabel", "")
            facet = _assign_facet(pref)
            out.append({
                "lcsh_id": cid,
                "prefLabel": pref,
                "depth": depth + 1,
                "facet": facet,
            })
            queue.append((cid, depth + 1))

    # Fallback: if no hierarchy links, use label prefix (LCSH subdivision style)
    if not out:
        seed_pref = by_id.get(seed_id, {}).get("prefLabel", "")
        if seed_pref:
            # Base: "Rome--History--Republic" (topic before date)
            parts = seed_pref.split("--")
            if len(parts) >= 3:
                base = "--".join(parts[:2] + [parts[2].split(",")[0].strip()])
            else:
                base = seed_pref
            # Include: direct subdivisions (seed--X) + same-base headings (e.g. 510-265, 265-30, 265-30--Fiction)
            for cid, rec in by_id.items():
                if cid == seed_id:
                    continue
                pref = rec.get("prefLabel", "")
                if pref.startswith(seed_pref + "--"):
                    depth = 1
                elif pref.startswith(base) and pref != seed_pref:
                    depth = 1 + pref.count("--") - base.count("--")
                    depth = min(max(1, depth), max_depth)
                else:
                    continue
                facet = _assign_facet(pref)
                out.append({
                    "lcsh_id": cid,
                    "prefLabel": pref,
                    "depth": depth,
                    "facet": facet,
                })

    return sorted(out, key=lambda x: (x["depth"], x["prefLabel"]))


def collect_related(seed_id: str, by_id: dict, parents_of: dict, children_of: dict) -> dict:
    """Siblings (same broader) and boundary context."""
    siblings = []
    seed_parents = parents_of.get(seed_id, set())
    for pid in seed_parents:
        sibs = children_of.get(pid, set()) - {seed_id}
        for sid in sibs:
            rec = by_id.get(sid, {})
            siblings.append({
                "lcsh_id": sid,
                "prefLabel": rec.get("prefLabel", ""),
            })

    return {
        "siblings": siblings,
    }


def build_position_statement(ancestors: list[dict], seed_pref: str) -> str:
    """Human-readable upward chain: History → Ancient → Rome--History → Republic."""
    labels = [a["prefLabel"] for a in reversed(ancestors)] + [seed_pref]
    return " → ".join(labels) if labels else ""


def build_dimensional_summary(descendants: list[dict]) -> dict[str, int]:
    """Count headings per facet."""
    counts = {f: 0 for f in FACET_KEYWORDS}
    for d in descendants:
        f = d.get("facet", "CULTURAL")
        counts[f] = counts.get(f, 0) + 1
    return counts


def build_synthesis_prompt(
    seed_id: str,
    seed_pref: str,
    position_statement: str,
    ancestors: list[dict],
    descendants: list[dict],
    related: dict,
    dimensional_summary: dict,
) -> str:
    """Ready-to-send prompt for LLM synthesis."""
    lines = [
        "# LCSH Domain Survey — Roman Republic",
        "",
        f"**Seed:** {seed_id} — {seed_pref}",
        "",
        "## Position (upward chain)",
        "",
        position_statement,
        "",
        "## Ancestors (navigation from above)",
        "",
    ]
    for a in ancestors:
        lines.append(f"- L{a['depth']}: {a['prefLabel']} ({a['lcsh_id']})")
    lines.extend(["", "## Descendants (candidate SubjectConcepts, by depth)", ""])

    by_depth = {}
    for d in descendants:
        by_depth.setdefault(d["depth"], []).append(d)
    for depth in sorted(by_depth.keys()):
        lines.append(f"### Depth {depth}")
        for d in by_depth[depth]:
            lines.append(f"- {d['prefLabel']} ({d['lcsh_id']}) [{d['facet']}]")
        lines.append("")

    lines.extend([
        "## Related (boundary)",
        "",
        "Siblings (same broader):",
    ])
    for s in related.get("siblings", [])[:15]:
        lines.append(f"- {s['prefLabel']} ({s['lcsh_id']})")
    lines.extend([
        "",
        "## Dimensional summary",
        "",
        "| Facet | Count |",
        "|-------|-------|",
    ])
    for f, c in sorted(dimensional_summary.items(), key=lambda x: -x[1]):
        if c > 0:
            lines.append(f"| {f} | {c} |")

    lines.extend([
        "",
        "---",
        "",
        "## Synthesis task",
        "",
        "Given this LCSH landscape, propose a set of SubjectConcepts for the Roman Republic domain.",
        "Each SubjectConcept should:",
        "1. Be grounded in one or more sh… headings above",
        "2. Be at a useful navigation granularity (not too broad, not every LCSH subdivision)",
        "3. Have a clear primary facet",
        "4. Support multi-directional entry (place, period, person, bibliography)",
        "",
        "Return structured proposals with: lcsh_id(s), label, primary_facet, rationale.",
    ])
    return "\n".join(lines)


def _write_survey_csv(survey: FederationSurvey, path: Path) -> None:
    """Write survey nodes to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id", "label", "federation", "domain", "uri", "concept_ref",
        "temporal_start", "temporal_end", "spatial_anchor", "person_ref",
        "text_ref", "event_ref", "wikidata_qid", "survey_depth", "is_seed",
        "status", "dimension_score", "survives", "active_dimensions",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for n in survey.nodes:
            row = {
                "id": n.id,
                "label": n.label,
                "federation": n.federation,
                "domain": n.domain,
                "uri": n.uri,
                "concept_ref": n.concept_ref,
                "temporal_start": n.temporal_range[0] if n.temporal_range else "",
                "temporal_end": n.temporal_range[1] if n.temporal_range else "",
                "spatial_anchor": n.spatial_anchor or "",
                "person_ref": n.person_ref or "",
                "text_ref": n.text_ref or "",
                "event_ref": n.event_ref or "",
                "wikidata_qid": n.wikidata_qid or "",
                "survey_depth": n.survey_depth,
                "is_seed": n.is_seed,
                "status": n.status,
                "dimension_score": n.dimension_score,
                "survives": n.survives,
                "active_dimensions": "|".join(sorted(n.active_dimensions)) if n.active_dimensions else "",
            }
            w.writerow(row)
    print(f"  CSV: {path}")


def _heading_to_node(
    lcsh_id: str,
    pref_label: str,
    domain: str,
    depth: int = 0,
    is_seed: bool = False,
) -> FederationNode:
    """Build FederationNode from LCSH heading."""
    uri = f"https://id.loc.gov/authorities/subjects/{lcsh_id}"
    return new_node(
        id=lcsh_id,
        label=pref_label,
        federation=Federation.LCSH,
        domain=domain,
        uri=uri,
        depth=depth,
        is_seed=is_seed,
        concept_ref=uri,
        temporal_range=parse_temporal_from_lcsh(pref_label),
        spatial_anchor=None,
    )


def run_survey(
    seed_id: str,
    out_path: Path,
    mode: str = "csv",
    csv_path: Path | None = None,
    cache_dir: Path | None = None,
    delay: float = 0.35,
    max_depth: int = 5,
    output_format: str = "schema",
    domain: str = "roman_republic",
) -> int:
    """Run survey in csv or live mode. Returns 0 on success."""
    if mode == "csv":
        if not csv_path or not csv_path.exists():
            print(f"ERROR: CSV not found: {csv_path}")
            print("Build it first: build_subjects_simplified_from_gz.py or simplify_skos_to_csv.py in Subjects/")
            return 1
        by_id, children_of, parents_of = load_csv(csv_path)
    else:
        cache_dir = cache_dir or Path(".lcsh_cache")
        print(f"Live mode: fetching from id.loc.gov (cache: {cache_dir}, delay={delay}s)")
        by_id, children_of, parents_of = load_from_live(seed_id, cache_dir, delay, max_depth)

    seed_rec = by_id.get(seed_id)
    if not seed_rec:
        print(f"ERROR: Seed {seed_id} not found")
        return 1

    seed_pref = seed_rec.get("prefLabel", "")
    ancestors = collect_ancestors(seed_id, by_id, parents_of)
    descendants = collect_descendants(seed_id, by_id, children_of, max_depth=max_depth)
    related = collect_related(seed_id, by_id, parents_of, children_of)
    position_statement = build_position_statement(ancestors, seed_pref)
    dimensional_summary = build_dimensional_summary(descendants)

    if output_format == "schema":
        survey = new_survey(
            Federation.LCSH,
            domain,
            seed_id=seed_id,
            seed_label=seed_pref,
            meta={"mode": mode, "cache_dir": str(cache_dir) if mode == "live" and cache_dir else None},
        )
        seen = set()
        for a in ancestors:
            nid = a["lcsh_id"]
            if nid not in seen:
                seen.add(nid)
                survey.add_node(_heading_to_node(nid, a["prefLabel"], domain, depth=a["depth"], is_seed=False))
        survey.add_node(_heading_to_node(seed_id, seed_pref, domain, depth=0, is_seed=True))
        seen.add(seed_id)
        for d in descendants:
            nid = d["lcsh_id"]
            if nid not in seen:
                seen.add(nid)
                rec = by_id.get(nid, {})
                survey.add_node(_heading_to_node(nid, rec.get("prefLabel", d["prefLabel"]), domain, depth=d["depth"], is_seed=False))
        for s in related.get("siblings", []):
            nid = s["lcsh_id"]
            if nid not in seen:
                seen.add(nid)
                survey.add_node(_heading_to_node(nid, s["prefLabel"], domain, depth=1, is_seed=False))
        for w in validate_survey(survey):
            print(f"  [WARN] {w}")
        survey.save(out_path)
        _write_survey_csv(survey, out_path.with_suffix(".csv"))
        return 0

    synthesis_prompt = build_synthesis_prompt(
        seed_id, seed_pref, position_statement,
        ancestors, descendants, related, dimensional_summary,
    )
    result = {
        "meta": {"mode": mode, "seed": seed_id, "cache_dir": str(cache_dir) if mode == "live" and cache_dir else None},
        "seed": seed_id,
        "seed_prefLabel": seed_pref,
        "position_statement": position_statement,
        "ancestors": ancestors,
        "descendants": descendants,
        "related": related,
        "dimensional_summary": dimensional_summary,
        "synthesis_prompt": synthesis_prompt,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Wrote: {out_path}")
    print(f"  Ancestors: {len(ancestors)}")
    print(f"  Descendants: {len(descendants)}")
    safe = position_statement.replace("\u2192", "->")[:80]
    print(f"  Position: {safe}...")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Survey LCSH domain (csv or live from id.loc.gov)")
    parser.add_argument("--seed", required=True, help="LCSH seed ID (e.g. sh85115114)")
    parser.add_argument("--out", type=Path, help="Output path (default: output/nodes/lcsh_roman_republic.json for schema)")
    parser.add_argument("--format", choices=["schema", "legacy"], default="schema", help="schema=FederationSurvey (default), legacy=human-readable JSON")
    parser.add_argument("--domain", default="roman_republic", help="Domain label (default roman_republic)")
    parser.add_argument("--mode", choices=["csv", "live"], default="live", help="csv=from file, live=from id.loc.gov (default)")
    parser.add_argument("--csv", type=Path, help="Path to subjects_simplified.csv (required if mode=csv)")
    parser.add_argument("--cache-dir", type=Path, default=Path(".lcsh_cache"), help="Cache dir for live mode (default .lcsh_cache)")
    parser.add_argument("--delay", type=float, default=0.35, help="Delay between HTTP requests in live mode (default 0.35)")
    parser.add_argument("--max-depth", type=int, default=5, help="Max descendant depth (default 5)")
    args = parser.parse_args()

    seed_id = _extract_id(args.seed)
    if not seed_id.startswith("sh"):
        seed_id = args.seed

    if args.mode == "csv" and not args.csv:
        print("ERROR: --csv required when --mode=csv")
        return 1

    out_path = args.out or Path("output/nodes/lcsh_roman_republic.json")

    return run_survey(
        seed_id=seed_id,
        out_path=out_path,
        mode=args.mode,
        csv_path=args.csv,
        cache_dir=args.cache_dir,
        delay=args.delay,
        max_depth=args.max_depth,
        output_format=args.format,
        domain=args.domain,
    )


if __name__ == "__main__":
    raise SystemExit(main())
