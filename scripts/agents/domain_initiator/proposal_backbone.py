#!/usr/bin/env python3
"""
Backbone enrichment for DI SubjectConcept proposals (ADR-020 / CCS).

Resolves authority tethers, parent bootstrap SCs, facet vectors, bibliography,
and CCS validation for proposals emitted from facet training decompositions.
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from scripts.agents.domain_initiator.candidate_qids import (
    BLOCKED_CANDIDATE_QIDS,
    entities_to_wiki_index,
    label_plausible_for_scope,
    sanitize_proposals,
)

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
LCSH_SUGGEST_URL = "https://id.loc.gov/authorities/subjects/suggest/?q={}"
HTTP_HEADERS = {"User-Agent": "Chrystallum/1.0 (DI proposal backbone; research project)"}

# Bootstrap parent SC per DI facet (ccs_bootstrap targets for PART_OF).
# subject_id values match live Neo4j nodes (sc_*), not legacy sc_rr_* aliases.
FACET_BOOTSTRAP_PARENT: dict[str, dict[str, Any]] = {
    "archaeological": {
        "subject_id": "sc_material_culture",
        "label": "Roman Material Culture, Art & Inscriptions",
        "lcc_primary": "DG37",
        "lcc_codes": ["DG37", "DG75", "DG78", "DG79"],
    },
    "artistic": {
        "subject_id": "sc_material_culture",
        "label": "Roman Material Culture, Art & Inscriptions",
        "lcc_primary": "DG37",
        "lcc_codes": ["DG37", "DG75", "DG78", "DG79"],
    },
    "communication": {
        "subject_id": "sc_historiography",
        "label": "Roman Historiography & Primary Sources",
        "lcc_primary": "DG35",
        "lcc_codes": ["DG31", "DG35"],
    },
    "military": {
        "subject_id": "sc_military",
        "label": "Roman Army & Military Campaigns",
        "lcsh_id": "sh85115130",
        "lcsh_label": "Rome--History, Military",
        "lcc_primary": "DG105",
        "lcc_codes": ["DG105", "DG109"],
    },
    "religious": {
        "subject_id": "sc_religion",
        "label": "Roman Religion, Cults & Priesthoods",
        "lcc_primary": "DG171",
        "lcc_codes": ["DG65", "DG69", "DG171", "DG175"],
    },
    "social": {
        "subject_id": "sc_society",
        "label": "Roman Society — Classes, Slavery & Family",
        "lcc_primary": "DG59",
        "lcc_codes": ["DG59", "DG61", "DG119", "DG121"],
    },
    "political": {
        "subject_id": "sc_constitution",
        "label": "Republican Constitution & Political Institutions",
        "lcsh_id": "sh85115171",
        "lcsh_label": "Rome--Politics and government",
        "lcc_primary": "DG89",
        "lcc_codes": ["DG89", "DG91", "DG95"],
    },
    "economic": {
        "subject_id": "sc_economy",
        "label": "Roman Economy, Finance & Trade",
        "lcc_primary": "DG113",
        "lcc_codes": ["DG113", "DG115"],
    },
    "intellectual": {
        "subject_id": "sc_literature",
        "label": "Roman Literature, Philosophy & Intellectual Life",
        "lcc_primary": "PA6000-6971",
        "lcc_codes": ["DG83", "DG143", "PA6000-6971"],
    },
    "linguistic": {
        "subject_id": "sc_literature",
        "label": "Roman Literature, Philosophy & Intellectual Life",
        "lcc_primary": "PA6000-6971",
        "lcc_codes": ["DG83", "PA6000-6971"],
    },
    "scientific": {
        "subject_id": "sc_science",
        "label": "Roman Science, Technology & Medicine",
        "lcc_primary": "DG135",
        "lcc_codes": ["DG135", "DG139"],
    },
    "technological": {
        "subject_id": "sc_science",
        "label": "Roman Science, Technology & Medicine",
        "lcc_primary": "DG135",
        "lcc_codes": ["DG135", "DG139"],
    },
    "diplomatic": {
        "subject_id": "sc_diplomacy",
        "label": "Roman Diplomacy & Foreign Relations",
        "lcc_primary": "DG21-190",
        "lcc_codes": ["DG21-190"],
    },
    "geographic": {
        "subject_id": "sc_topography",
        "label": "Roman Topography & Urban Space",
        "lcc_primary": "DG41",
        "lcc_codes": ["DG41", "DG42", "DG45"],
    },
    "demographic": {
        "subject_id": "sc_society",
        "label": "Roman Society — Classes, Slavery & Family",
        "lcc_primary": "DG59",
        "lcc_codes": ["DG59", "DG61"],
    },
    "biographic": {
        "subject_id": "sc_society",
        "label": "Roman Society — Classes, Slavery & Family",
        "lcc_primary": "DG59",
        "lcc_codes": ["DG59"],
    },
    "cultural": {
        "subject_id": "sc_society",
        "label": "Roman Society — Classes, Slavery & Family",
        "lcc_primary": "DG59",
        "lcc_codes": ["DG59", "DG61"],
    },
    "environmental": {
        "subject_id": "sc_topography",
        "label": "Roman Topography & Urban Space",
        "lcc_primary": "DG41",
        "lcc_codes": ["DG41"],
    },
}

# Seed-level period LCC (from harvest LCSH sh85115114 → Republic period shelf)
SEED_LCC_PERIOD: dict[str, dict[str, Any]] = {
    "Q17167": {
        "lcc_primary": "DG241-269",
        "lcc_label": "Republic, 509-27 B.C.",
        "lcsh_id": "sh85115114",
    },
}

# Per-scope LCC: institutional (DG105 Army, DG109 Navy) vs period (DG241+ Republic wars)
# DG105/DG109 live under DG21-190 (Ancient Rome — General); correct for army/navy
# institution topics. Wars/campaigns for the Republic seed belong on DG241-269 branch.
SCOPE_LCC_MAP: dict[str, dict[str, Any]] = {
    "military_wars_campaigns": {
        "lcc_primary": "DG241-253",
        "lcc_codes": ["DG241-253", "DG242-249.4", "DG253.5-269"],
        "lcc_rationale": "Republic conquest and war periods (264 BCE–27 BCE), not DG105 institutional army",
    },
    "military_organization_structure": {
        "lcc_primary": "DG105",
        "lcc_codes": ["DG105", "DG241-269"],
        "lcc_rationale": "Roman army as institution; cross-anchor Republic period",
    },
    "military_reforms": {
        "lcc_primary": "DG105",
        "lcc_codes": ["DG105", "DG241-269"],
        "lcc_rationale": "Army reforms (Servian, Marian) — institutional shelf",
    },
    "recruitment_service": {
        "lcc_primary": "DG105",
        "lcc_codes": ["DG105"],
        "lcc_rationale": "Recruitment and service — army institution",
    },
    "siege_engineering": {
        "lcc_primary": "DG105",
        "lcc_codes": ["DG105"],
        "lcc_rationale": "Military engineering under army",
    },
    "naval_warfare": {
        "lcc_primary": "DG109",
        "lcc_codes": ["DG109", "DG242-249.4"],
        "lcc_rationale": "Roman navy; Punic War naval campaigns on period shelf",
    },
    "auxiliary_forces": {
        "lcc_primary": "DG105",
        "lcc_codes": ["DG105"],
        "lcc_rationale": "Auxiliary troops — army institution",
    },
    "military_politics": {
        "lcc_primary": "DG253.5-269",
        "lcc_codes": ["DG253.5-269", "DG105"],
        "lcc_rationale": "Army and constitutional crisis — fall of Republic period",
    },
}

# Default multidimensional facet vectors when training did not supply weights
FACET_DEFAULT_VECTORS: dict[str, dict[str, float]] = {
    "military": {
        "military": 0.95,
        "political": 0.55,
        "geographic": 0.45,
        "biographic": 0.40,
    },
    "archaeological": {
        "archaeological": 0.95,
        "geographic": 0.50,
        "artistic": 0.35,
    },
    "artistic": {
        "artistic": 0.95,
        "archaeological": 0.55,
        "political": 0.35,
    },
    "communication": {
        "communication": 0.95,
        "intellectual": 0.55,
        "political": 0.40,
    },
    "religious": {
        "religious": 0.95,
        "social": 0.60,
        "political": 0.40,
    },
    "social": {
        "social": 0.95,
        "biographic": 0.55,
        "demographic": 0.45,
    },
    "political": {
        "political": 0.95,
        "social": 0.55,
        "communication": 0.40,
        "military": 0.35,
        "intellectual": 0.30,
    },
}

# LCSH suggest queries when Wikidata / harvest have no tether
SCOPE_LCSH_QUERIES: dict[str, list[str]] = {
    "military_wars_campaigns": ["Rome History Military", "Punic Wars"],
    "military_organization_structure": ["Rome army", "Roman legion"],
    "military_reforms": ["Marian reforms", "Roman army reforms"],
    "recruitment_service": ["military service", "Rome army recruitment"],
    "siege_engineering": ["siege warfare", "Roman military engineering"],
    "naval_warfare": ["naval history Rome", "Roman navy"],
    "auxiliary_forces": ["Rome auxiliary troops", "socii"],
    "military_politics": ["civil-military relations", "Rome army politics"],
    "decorative_arts": ["Decorative arts Rome"],
    "architecture_public": ["public buildings Rome", "monuments Rome"],
    "propaganda_commemoration": ["propaganda Rome", "triumph Rome"],
    "materials_techniques": ["Roman art materials"],
    "information_networks": ["information networks Rome"],
    "religious_temples": ["Roman temples"],
    "patronage_clientela": ["patron and client Rome"],
    "social_mobility": ["Social mobility Rome"],
    "marriage_family": ["marriage Rome", "Roman family"],
    "urban_rural": ["city and town life Rome"],
    "cultural_integration": ["acculturation Rome"],
    # Political facet — distinct subject headings per scope (not parent bootstrap)
    "constitutional_institutions": [
        "Rome Politics and government",
        "Rome Constitutional history",
    ],
    "magistracy_cursus_honorum": [
        "Rome Officials and employees",
        "Rome Magistrates",
    ],
    "senatorial_politics": [
        "Rome Senate",
        "Rome Politics and government Senate",
    ],
    "popular_politics_assemblies": [
        "Rome Politics and government Assemblies",
        "Rome Popular assemblies",
    ],
    "conflict_orders_early_republic": [
        "Conflict of the Orders Rome",
    ],
    "late_republican_crisis": [
        "Rome Politics and government 265-30 B.C.",
        "Rome History Republic",
    ],
    "citizenship_enfranchisement": [
        "Citizenship Rome",
        "Rome Citizenship",
    ],
}

# Curated scope-level LCSH when suggest API is ambiguous (pilot-quality anchors)
SCOPE_LCSH_CURATED: dict[str, dict[str, str]] = {
    "military_wars_campaigns": {
        "lcsh_id": "sh85109114",
        "lcsh_label": "Punic Wars",
    },
    "military_organization_structure": {
        "lcsh_id": "sh85115130",
        "lcsh_label": "Rome--History, Military",
    },
    "military_reforms": {
        "lcsh_id": "sh85115130",
        "lcsh_label": "Rome--History, Military",
    },
    "recruitment_service": {
        "lcsh_id": "sh85085289",
        "lcsh_label": "Military service, Compulsory",
    },
    "siege_engineering": {
        "lcsh_id": "sh85009382",
        "lcsh_label": "Sieges",
    },
    "naval_warfare": {
        "lcsh_id": "sh85090384",
        "lcsh_label": "Naval history",
    },
    "auxiliary_forces": {
        "lcsh_id": "sh85083749",
        "lcsh_label": "Auxiliary troops",
    },
    "military_politics": {
        "lcsh_id": "sh85026352",
        "lcsh_label": "Civil-military relations",
    },
    "constitutional_institutions": {
        "lcsh_id": "sh85115171",
        "lcsh_label": "Rome--Politics and government",
        "topic_qid": "Q666680",
    },
    "magistracy_cursus_honorum": {
        "lcsh_id": "sh85115147",
        "lcsh_label": "Rome--Officials and employees",
        "topic_qid": "Q27518",
    },
    "senatorial_politics": {
        "lcsh_id": "sh85115172",
        "lcsh_label": "Rome--Politics and government--510-265 B.C.",
        "topic_qid": "Q130614",
    },
    "popular_politics_assemblies": {
        "lcsh_id": "sh85115154",
        "lcsh_label": "Rome--Politics and government--Assemblies",
        "topic_qid": "Q623086",
    },
    "conflict_orders_early_republic": {
        "lcsh_id": "sh2025000150",
        "lcsh_label": "Conflict of the Orders, Rome, ca. 500-287 B.C.",
        "topic_qid": "Q747480",
    },
    "late_republican_crisis": {
        "lcsh_id": "sh85115173",
        "lcsh_label": "Rome--Politics and government--265-30 B.C.",
        "topic_qid": "Q1812526",
    },
    "citizenship_enfranchisement": {
        "lcsh_id": "sh85115159",
        "lcsh_label": "Citizenship--Rome",
        "topic_qid": "Q15282014",
    },
}

# Per-scope facet vectors when training did not supply weights (CCS-2)
SCOPE_FACET_WEIGHTS: dict[str, dict[str, float]] = {
    "constitutional_institutions": {
        "political": 0.95,
        "intellectual": 0.55,
        "social": 0.35,
    },
    "magistracy_cursus_honorum": {
        "political": 0.95,
        "biographic": 0.50,
        "social": 0.40,
    },
    "senatorial_politics": {
        "political": 0.95,
        "communication": 0.45,
        "social": 0.40,
    },
    "popular_politics_assemblies": {
        "political": 0.95,
        "communication": 0.60,
        "social": 0.45,
    },
    "conflict_orders_early_republic": {
        "political": 0.95,
        "social": 0.70,
        "economic": 0.35,
    },
    "late_republican_crisis": {
        "political": 0.95,
        "military": 0.55,
        "biographic": 0.45,
    },
    "citizenship_enfranchisement": {
        "political": 0.90,
        "demographic": 0.55,
        "social": 0.50,
    },
}

def make_subject_id(seed_qid: str, scope_key: str) -> str:
    """Canonical subject_id for a DI decomposition proposal."""
    seed_slug = seed_qid.lower()
    slug = re.sub(r"[^a-z0-9_]+", "_", scope_key.lower()).strip("_")
    return f"sc_{seed_slug}_{slug}"


def normalize_bootstrap_subject_id(subject_id: str | None) -> str | None:
    """Map legacy sc_rr_* bootstrap IDs to live graph sc_* IDs."""
    if not subject_id:
        return subject_id
    if subject_id.startswith("sc_rr_"):
        return f"sc_{subject_id[len('sc_rr_'):]}"
    return subject_id


def normalize_proposal_for_write(proposal: dict) -> dict:
    """Normalize a review-file proposal before graph write (IDs, QIDs, parents)."""
    normalized = dict(proposal)
    parent_id = normalize_bootstrap_subject_id(proposal.get("parent_subject_id"))
    if parent_id:
        normalized["parent_subject_id"] = parent_id

    qids: list[str] = []
    for item in proposal.get("candidate_qids") or []:
        if isinstance(item, dict):
            qid = item.get("qid")
        else:
            qid = item
        if qid:
            qids.append(str(qid))
    normalized["candidate_qids"] = qids

    if not normalized.get("lcsh_id") and isinstance(proposal.get("authority"), dict):
        normalized["lcsh_id"] = proposal["authority"].get("lcsh_id")
    if not normalized.get("lcsh_label") and isinstance(proposal.get("authority"), dict):
        normalized["lcsh_label"] = proposal["authority"].get("lcsh_label")

    return normalized


def load_proposals_document(path: Path) -> dict:
    """Load proposals JSON (full document or pilot slice)."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if "proposals" not in data:
        raise ValueError(f"{path} missing 'proposals' array")
    return data


def load_route_packs(route_dir: Path, seed: str) -> dict[str, dict]:
    """Load per-facet route packs keyed by facet."""
    packs: dict[str, dict] = {}
    for path in sorted(route_dir.glob(f"{seed}_*_pack.json")):
        if "dispatch_report" in path.name:
            continue
        parts = path.stem.split("_")
        if len(parts) < 3:
            continue
        facet = "_".join(parts[1:-1]).lower()
        try:
            with open(path, encoding="utf-8") as f:
                packs[facet] = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
    return packs


def load_harvest(harvest_dir: Path, seed: str) -> dict | None:
    path = harvest_dir / f"{seed}_di_harvest.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_qid_authority_index(packs: dict[str, dict], harvest: dict | None) -> dict[str, dict]:
    """Index QID -> {lcsh_id, label} from route packs and harvest."""
    index: dict[str, dict] = {}

    def add(qid: str, lcsh_id: str | None, label: str | None = None) -> None:
        if not qid or not lcsh_id:
            return
        if not lcsh_id.startswith("sh"):
            return
        existing = index.setdefault(qid, {})
        existing["lcsh_id"] = lcsh_id
        if label:
            existing["label"] = label

    for pack in packs.values():
        ctx = pack.get("domain_context", {})
        tether = ctx.get("domain_tether", {})
        if tether.get("qid") and tether.get("lcnaf_id"):
            add(tether["qid"], tether["lcnaf_id"], tether.get("label"))
        for sub in ctx.get("sub_subjects", []):
            add(sub.get("qid", ""), sub.get("lcnaf_id"), sub.get("label"))

    if harvest:
        seed = harvest.get("seed", {})
        for ext in seed.get("external_ids", []):
            if ext.get("pid") == "P244":
                add(seed.get("qid", ""), ext.get("value"), seed.get("label"))
        for bl in harvest.get("backlinks", []):
            qid = bl.get("qid", "")
            label = bl.get("label")
            for ext in bl.get("external_ids", []):
                if ext.get("pid") == "P244":
                    add(qid, ext.get("value"), label)
        for entry in harvest.get("subject_backbone_links", {}).get("lcnaf", []):
            add(entry.get("qid", ""), entry.get("lcnaf_id"), entry.get("label"))

    return index


def _label_plausible_for_scope(
    qid: str,
    qid_label: str | None,
    scope_label: str,
    *,
    seed_qid: str = "Q17167",
) -> bool:
    """Reject Wikidata items whose labels are unrelated to Roman Republican scope work."""
    return label_plausible_for_scope(
        qid, qid_label, scope_label, seed_qid=seed_qid
    )


def _lcsh_is_subject_heading(lcsh_id: str | None) -> bool:
    return bool(lcsh_id and lcsh_id.startswith("sh"))


def _apply_topic_qid(
    authority: dict[str, Any],
    qid: str,
    label: str | None,
    lcsh_id: str | None,
    source: str,
    *,
    allow_name_heading: bool = False,
) -> None:
    """Attach a validated topic QID; optionally use its LCSH when no curated heading yet."""
    authority["topic_qid"] = qid
    authority["topic_qid_label"] = label
    if lcsh_id:
        authority["topic_lcsh_id"] = lcsh_id
    if authority.get("lcsh_id"):
        return
    if not lcsh_id:
        return
    if _lcsh_is_subject_heading(lcsh_id) or allow_name_heading:
        authority["lcsh_id"] = lcsh_id
        authority["tether_source"] = source


def _resolve_curated_authority(scope_key: str) -> dict[str, Any] | None:
    curated = SCOPE_LCSH_CURATED.get(scope_key)
    if not curated or not curated.get("lcsh_id"):
        return None
    return {
        "lcsh_id": curated["lcsh_id"],
        "lcsh_label": curated.get("lcsh_label"),
        "topic_qid": curated.get("topic_qid"),
        "tether_source": "curated",
    }


def _lookup_qid_label(
    qid: str,
    qid_index: dict[str, dict],
    wiki_index: dict[str, dict],
) -> str | None:
    if qid in qid_index and qid_index[qid].get("label"):
        return qid_index[qid]["label"]
    if qid in wiki_index and wiki_index[qid].get("label"):
        return wiki_index[qid]["label"]
    return None


def fetch_wikidata_authorities(qids: list[str]) -> dict[str, dict]:
    """Batch-fetch P244/P2163/P1149/P1036 for candidate QIDs."""
    clean = [q for q in qids if q and q.startswith("Q")]
    if not clean:
        return {}

    values = " ".join(f"wd:{q}" for q in clean[:50])
    query = f"""
    SELECT ?item ?itemLabel ?lcsh ?fast ?lcc ?dewey WHERE {{
      VALUES ?item {{ {values} }}
      OPTIONAL {{ ?item wdt:P244 ?lcsh }}
      OPTIONAL {{ ?item wdt:P2163 ?fast }}
      OPTIONAL {{ ?item wdt:P1149 ?lcc }}
      OPTIONAL {{ ?item wdt:P1036 ?dewey }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    url = WIKIDATA_SPARQL + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    req = urllib.request.Request(url, headers=HTTP_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {}

    out: dict[str, dict] = {}
    for row in data.get("results", {}).get("bindings", []):
        qid = row.get("item", {}).get("value", "").rsplit("/", 1)[-1]
        entry = out.setdefault(qid, {"label": row.get("itemLabel", {}).get("value")})
        if "lcsh" in row:
            entry["lcsh_id"] = row["lcsh"]["value"]
        if "fast" in row:
            entry["fast_id"] = row["fast"]["value"]
        if "lcc" in row:
            entry["lcc"] = row["lcc"]["value"]
        if "dewey" in row:
            entry["dewey"] = row["dewey"]["value"]
    return out


def lcsh_suggest(query: str) -> tuple[str | None, str | None]:
    url = LCSH_SUGGEST_URL.format(urllib.parse.quote(query))
    req = urllib.request.Request(url, headers=HTTP_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None, None

    if not isinstance(data, list) or len(data) < 4:
        return None, None

    labels = data[1] if isinstance(data[1], list) else []
    uris = data[3] if isinstance(data[3], list) else []
    for label, uri in zip(labels, uris):
        if "/subjects/sh" in uri:
            lcsh_id = uri.rstrip("/").split("/")[-1]
            return label, lcsh_id
    return None, None


def resolve_scope_lcsh(scope_key: str, working_label: str) -> tuple[str | None, str | None, str]:
    """Return (lcsh_label, lcsh_id, source_tag)."""
    curated = SCOPE_LCSH_CURATED.get(scope_key)
    if curated:
        return curated["lcsh_label"], curated["lcsh_id"], "curated"

    for query in SCOPE_LCSH_QUERIES.get(scope_key, [working_label]):
        label, lcsh_id = lcsh_suggest(query)
        if lcsh_id:
            return label, lcsh_id, "lcsh_suggest"
        time.sleep(0.25)

    return None, None, "none"


def resolve_lcc_for_proposal(
    proposal: dict,
    seed_qid: str,
    parent: dict,
    pack: dict | None,
) -> tuple[str, list[str], str | None]:
    """Return (lcc_primary, lcc_codes, rationale) for a proposal."""
    scope_key = proposal.get("scope_key", "")
    if scope_key in SCOPE_LCC_MAP:
        entry = SCOPE_LCC_MAP[scope_key]
        return (
            entry["lcc_primary"],
            list(entry["lcc_codes"]),
            entry.get("lcc_rationale"),
        )

    source_facet = proposal.get("source_facet", "")
    seed_period = SEED_LCC_PERIOD.get(seed_qid, {})

    if seed_period and source_facet in ("military", "political", "diplomatic"):
        return (
            seed_period["lcc_primary"],
            [seed_period["lcc_primary"]],
            f"Seed {seed_qid} period default ({seed_period.get('lcc_label', '')})",
        )

    primary, codes = extract_lcc_from_pack(pack, parent)
    return primary, codes, "parent bootstrap default"


def extract_lcc_from_pack(pack: dict | None, parent: dict) -> tuple[str, list[str]]:
    """Pick lcc_primary and lcc_codes from discipline traversal or parent bootstrap."""
    codes: list[str] = list(parent.get("lcc_codes", []))
    primary = parent.get("lcc_primary", "")

    if not pack:
        return primary, codes

    for disc in pack.get("discipline_traversal", {}).get("disciplines", []):
        auth = disc.get("authority_ids", {})
        p1036 = auth.get("P1036", {})
        if isinstance(p1036, dict) and p1036.get("value"):
            # Dewey on discipline — keep parent LCC as primary for Roman Republic
            pass

    return primary, codes


def supporting_works_for_facet(training: dict | None) -> list[str]:
    if not training:
        return []
    works: list[str] = []
    for item in training.get("key_works", []):
        wid = item.get("work_id")
        if wid:
            works.append(wid)
    for item in training.get("discovered_works", [])[:5]:
        wid = item.get("work_id")
        if wid and wid not in works:
            works.append(wid)
    return works


def work_id_from_item(item: dict[str, Any]) -> str:
    wid = (item.get("work_id") or "").strip()
    if wid:
        return wid
    uri = (item.get("work") or "").strip()
    if not uri:
        return ""
    tail = uri.rstrip("/").split("/")[-1]
    if "wikidata.org" in uri:
        return f"wd:{tail}"
    if "openalex.org" in uri:
        return f"openalex:{tail}"
    return tail


def _looks_like_work_id(value: str) -> bool:
    return bool(
        value.startswith(("openalex:", "ia:", "oapen:", "domain_src:", "wd:Q"))
        or (value.startswith("Q") and len(value) > 1 and value[1:].isdigit())
    )


def title_quality(title: str, work_id: str) -> int:
    if not title or title.strip() == work_id:
        return 0
    if _looks_like_work_id(title):
        return 0
    return len(title)


def corpus_work_title(item: dict[str, Any], work_id: str) -> str:
    """Resolve display title; map legacy label/workLabel into title."""
    for key in ("title", "workLabel", "label"):
        val = (item.get(key) or "").strip()
        if val and val != work_id and not _looks_like_work_id(val):
            return val
    return work_id


_PRIMARY_AUTHOR_HINTS = (
    "plutarch",
    "suetonius",
    "livy",
    "appian",
    "cicero",
    "caesar",
    "nepos",
    "polybius",
    "sallust",
    "diodorus",
    "dionysius",
)

_REFERENCE_SOURCE_HINTS = (
    "stanford encyclopedia",
    "khan academy",
    "openculture",
    "coursera",
    "ocw",
    "course_index",
    "mooc_index",
    "primer",
)


def infer_corpus_tier(raw: dict[str, Any]) -> str:
    """ADR-021: primary | secondary | reference."""
    explicit = (raw.get("corpus_tier") or "").strip().lower()
    if explicit in {"primary", "secondary", "reference"}:
        return explicit

    work_type = (raw.get("type") or "").strip().lower()
    source = (raw.get("source") or "").strip().lower()
    hay = " ".join(
        str(raw.get(k) or "")
        for k in ("title", "authors", "abstract", "source_url")
    ).lower()

    if work_type == "primary_source" or "primary_source" in source:
        return "primary"
    if any(h in hay for h in _PRIMARY_AUTHOR_HINTS):
        return "primary"
    if any(h in hay or h in work_type for h in _REFERENCE_SOURCE_HINTS):
        return "reference"
    return "secondary"


def infer_source_era(raw: dict[str, Any], *, corpus_tier: str | None = None) -> str:
    """ADR-021: contemporary | near_contemporary | antiquarian | modern_scholarly."""
    explicit = (raw.get("source_era") or "").strip().lower()
    if explicit in {"contemporary", "near_contemporary", "antiquarian", "modern_scholarly"}:
        return explicit

    tier = corpus_tier or infer_corpus_tier(raw)
    if tier != "primary":
        return "modern_scholarly"

    try:
        year = int(raw.get("year"))
    except (TypeError, ValueError):
        year = None

    if year is not None and year < 400:
        if year < -27:
            return "contemporary"
        return "near_contemporary"
    return "near_contemporary"


def normalize_corpus_work(raw: dict[str, Any]) -> dict[str, Any]:
    """Canonical bibliographic entry for CorpusWork / supporting_works (always uses title)."""
    work_id = work_id_from_item(raw)
    if not work_id:
        return {}
    corpus_tier = infer_corpus_tier(raw)
    return {
        "work_id": work_id,
        "title": corpus_work_title(raw, work_id),
        "authors": raw.get("authors") or "",
        "year": raw.get("year"),
        "source": raw.get("source") or "",
        "source_url": raw.get("source_url") or raw.get("oa_url") or "",
        "doi": raw.get("doi") or "",
        "citation_count": raw.get("citation_count"),
        "corpus_tier": corpus_tier,
        "source_era": infer_source_era(raw, corpus_tier=corpus_tier),
    }


def build_work_index(training_dir: Path, seed: str) -> dict[str, dict[str, Any]]:
    """Index work_id -> bibliographic metadata from corpus + training files."""
    index: dict[str, dict[str, Any]] = {}

    def _ingest(item: dict, source_hint: str = "") -> None:
        incoming = normalize_corpus_work({**item, "source": item.get("source") or source_hint})
        wid = incoming.get("work_id")
        if not wid:
            return
        existing = index.get(wid)
        if existing and title_quality(existing.get("title", ""), wid) >= title_quality(
            incoming.get("title", ""), wid
        ):
            return
        index[wid] = incoming

    for path in sorted(training_dir.glob(f"{seed}_*_corpus.json")):
        try:
            with open(path, encoding="utf-8") as f:
                for item in json.load(f):
                    _ingest(item, source_hint="corpus")
        except (json.JSONDecodeError, OSError, TypeError):
            continue

    for path in sorted(training_dir.glob(f"{seed}_*_training.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for key in ("key_works", "discovered_works"):
                for item in data.get(key, []):
                    _ingest(item, source_hint="training")
            # Titles sometimes appear only in tool-call previews during training
            for tc in data.get("_meta", {}).get("tool_calls", []):
                preview = tc.get("output_preview") or ""
                if preview.startswith("[{") and "work_id" in preview:
                    try:
                        for item in json.loads(preview):
                            if isinstance(item, dict) and item.get("work_id"):
                                _ingest(item, source_hint="training_tool")
                    except json.JSONDecodeError:
                        pass
        except (json.JSONDecodeError, OSError, TypeError):
            continue

    return index


def fetch_internet_archive_meta(work_id: str) -> dict[str, Any] | None:
    """Fetch title/metadata for ia:identifier works."""
    if not work_id.startswith("ia:"):
        return None
    ident = work_id.split(":", 1)[1]
    url = f"https://archive.org/metadata/{ident}"
    req = urllib.request.Request(url, headers=HTTP_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None
    meta = data.get("metadata") or {}
    title = meta.get("title") or ident
    creators = meta.get("creator") or meta.get("creators") or ""
    if isinstance(creators, list):
        creators = "; ".join(str(c) for c in creators[:3])
    return {
        "work_id": work_id,
        "title": title,
        "authors": str(creators),
        "year": meta.get("year") or meta.get("date"),
        "source": "internet_archive",
        "source_url": f"https://archive.org/details/{ident}",
        "doi": "",
        "citation_count": None,
    }


def fetch_openalex_work_meta(work_id: str) -> dict[str, Any] | None:
    """Fetch title/authors/year for openalex:W... ids not in local index."""
    if not work_id.startswith("openalex:"):
        return None
    oa_ref = work_id.split(":", 1)[1]
    url = f"https://api.openalex.org/works/{oa_ref}"
    req = urllib.request.Request(url, headers=HTTP_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None

    authors = "; ".join(
        a.get("author", {}).get("display_name", "")
        for a in data.get("authorships", [])[:4]
        if a.get("author", {}).get("display_name")
    )
    loc = data.get("primary_location") or {}
    source_url = loc.get("landing_page_url") or data.get("id", "")
    return {
        "work_id": work_id,
        "title": data.get("display_name") or data.get("title") or work_id,
        "authors": authors,
        "year": data.get("publication_year"),
        "source": "openalex",
        "source_url": source_url,
        "doi": data.get("doi") or "",
        "citation_count": data.get("cited_by_count"),
    }


def label_supporting_works(
    work_ids: list[str],
    work_index: dict[str, dict[str, Any]],
    *,
    fetch_missing: bool = True,
) -> list[dict[str, Any]]:
    """Resolve supporting work IDs to titled bibliography entries (title, not label)."""
    labeled: list[dict[str, Any]] = []
    for wid in work_ids:
        if wid in work_index:
            entry = dict(work_index[wid])
            if fetch_missing and title_quality(entry.get("title", ""), wid) == 0:
                meta = fetch_openalex_work_meta(wid) or fetch_internet_archive_meta(wid)
                if meta and title_quality(meta.get("title", ""), wid) > 0:
                    entry = normalize_corpus_work({**entry, **meta})
                    work_index[wid] = entry
            labeled.append(normalize_corpus_work(entry))
            continue
        if fetch_missing:
            meta = fetch_openalex_work_meta(wid) or fetch_internet_archive_meta(wid)
            if meta:
                row = normalize_corpus_work(meta)
                work_index[wid] = row
                labeled.append(dict(row))
                continue
        labeled.append(
            normalize_corpus_work(
                {
                    "work_id": wid,
                    "source": wid.split(":", 1)[0] if ":" in wid else "unknown",
                }
            )
        )
    return labeled


def infer_facet_weights(proposal: dict, training: dict | None) -> dict[str, float]:
    """Use scope-level weights from training if present, else scope/facet defaults."""
    scope_key = proposal.get("scope_key", "")
    source_facet = proposal.get("source_facet", "")

    if training:
        for scope in training.get("decomposition_assessment", {}).get("sub_scopes", []):
            if scope.get("scope_key") == scope_key and scope.get("facet_weights"):
                weights = {
                    k: float(v)
                    for k, v in scope["facet_weights"].items()
                    if float(v) > 0.05
                }
                if len(weights) >= 2:
                    return weights

    scope_defaults = SCOPE_FACET_WEIGHTS.get(scope_key, {})
    if scope_defaults:
        return scope_defaults

    defaults = FACET_DEFAULT_VECTORS.get(source_facet, {})
    if defaults:
        return defaults

    return {source_facet: 1.0}


def resolve_authority(
    proposal: dict,
    qid_index: dict[str, dict],
    wiki_index: dict[str, dict],
    parent: dict,
    *,
    resolve_lcsh_online: bool = True,
    seed_qid: str = "Q17167",
) -> dict[str, Any]:
    """Build authority block for one proposal."""
    scope_key = proposal.get("scope_key", "")
    working_label = proposal.get("label", "")
    candidate_qids = proposal.get("candidate_qids", [])

    authority: dict[str, Any] = {
        "lcsh_id": None,
        "lcsh_label": None,
        "fast_id": None,
        "lcc_primary": parent.get("lcc_primary"),
        "lcc_codes": list(parent.get("lcc_codes", [])),
        "topic_qid": None,
        "topic_qid_label": None,
        "topic_lcsh_id": None,
        "tether_source": None,
    }

    curated = _resolve_curated_authority(scope_key)
    if curated:
        authority["lcsh_id"] = curated["lcsh_id"]
        authority["lcsh_label"] = curated["lcsh_label"]
        authority["tether_source"] = curated["tether_source"]
        if curated.get("topic_qid"):
            topic_qid = curated["topic_qid"]
            authority["topic_qid"] = topic_qid
            authority["topic_qid_label"] = _lookup_qid_label(
                topic_qid, qid_index, wiki_index
            )
            harvest_lcsh = qid_index.get(topic_qid, {}).get("lcsh_id")
            if harvest_lcsh:
                authority["topic_lcsh_id"] = harvest_lcsh

    # Validated candidate QIDs — topic anchor and optional LCSH (subject headings only)
    for qid in candidate_qids:
        if qid in BLOCKED_CANDIDATE_QIDS:
            continue
        label = _lookup_qid_label(qid, qid_index, wiki_index)
        if not _label_plausible_for_scope(qid, label, working_label, seed_qid=seed_qid):
            continue

        harvest_lcsh = qid_index.get(qid, {}).get("lcsh_id")
        if harvest_lcsh and _lcsh_is_subject_heading(harvest_lcsh):
            if not authority.get("topic_qid"):
                _apply_topic_qid(
                    authority, qid, label, harvest_lcsh, "harvest_qid"
                )
            elif not authority.get("lcsh_id"):
                authority["lcsh_id"] = harvest_lcsh
                authority["lcsh_label"] = label
                authority["tether_source"] = "harvest_qid"
            continue

        wiki = wiki_index.get(qid, {})
        wiki_lcsh = wiki.get("lcsh_id")
        if wiki_lcsh and _lcsh_is_subject_heading(wiki_lcsh):
            if not authority.get("topic_qid"):
                _apply_topic_qid(
                    authority, qid, label, wiki_lcsh, "wikidata_qid"
                )
            elif not authority.get("lcsh_id"):
                authority["lcsh_id"] = wiki_lcsh
                authority["lcsh_label"] = label
                authority["tether_source"] = "wikidata_qid"
            if wiki.get("fast_id") and not authority.get("fast_id"):
                authority["fast_id"] = wiki["fast_id"]
            continue

        if not authority.get("topic_qid"):
            authority["topic_qid"] = qid
            authority["topic_qid_label"] = label
            if wiki_lcsh:
                authority["topic_lcsh_id"] = wiki_lcsh

    # Online LCSH suggest — never parent bootstrap (too generic for L2 scopes)
    if not authority["lcsh_id"] and resolve_lcsh_online:
        lcsh_label, lcsh_id, source = resolve_scope_lcsh(scope_key, working_label)
        if lcsh_id:
            authority["lcsh_id"] = lcsh_id
            authority["lcsh_label"] = lcsh_label
            authority["tether_source"] = source

    return authority


def validate_ccs(proposal: dict) -> dict[str, Any]:
    """ADR-020 validity check (deterministic)."""
    failures: list[str] = []
    authority = proposal.get("authority", {})

    has_tether = bool(
        authority.get("lcsh_id")
        or authority.get("fast_id")
        or authority.get("topic_qid")
        or authority.get("topic_lcsh_id")
        or proposal.get("candidate_qids")
    )
    if not has_tether:
        failures.append(
            "CCS-1: missing authority tether (need LCSH, FAST, topic QID, or candidate QIDs; "
            "LCC codes alone are classification placement, not subject-heading authority)"
        )

    weights = proposal.get("facet_weights", {})
    significant = [k for k, v in weights.items() if float(v) > 0.1]
    if len(significant) < 2:
        failures.append("CCS-2: fewer than 2 facet weights > 0.1")

    label = (proposal.get("label") or "").lower()
    type_bucket_markers = ["figures", "persons", "people", "entities", "commanders &"]
    if any(m in label for m in type_bucket_markers):
        failures.append("CCS-4: label looks like entity-type bucket")

    populatable = bool(proposal.get("candidate_qids")) or bool(
        proposal.get("supporting_works")
    )
    if not populatable:
        failures.append("CCS-3: no candidate members or corpus works (flag only)")

    return {
        "ccs_pass": len([f for f in failures if not f.startswith("CCS-3")]) == 0,
        "failures": failures,
    }


def enrich_proposal(
    proposal: dict,
    *,
    seed_qid: str,
    pack: dict | None,
    training: dict | None,
    qid_index: dict[str, dict],
    wiki_index: dict[str, dict],
    resolve_lcsh_online: bool = True,
    work_index: dict[str, dict[str, Any]] | None = None,
) -> dict:
    """Add backbone fields to a single proposal dict (in place + return)."""
    source_facet = proposal.get("source_facet", "")
    scope_key = proposal.get("scope_key") or proposal.get("label", "scope")
    parent = FACET_BOOTSTRAP_PARENT.get(source_facet, {})

    proposal["subject_id"] = make_subject_id(seed_qid, scope_key)
    proposal["source"] = "di_proposal"
    proposal["parent_subject_id"] = parent.get("subject_id")
    proposal["parent_label"] = parent.get("label")

    primary, codes, rationale = resolve_lcc_for_proposal(proposal, seed_qid, parent, pack)
    proposal["lcc_primary"] = primary
    proposal["lcc_codes"] = codes
    proposal["lcc_rationale"] = rationale

    if not resolve_lcsh_online and not proposal.get("authority"):
        authority = resolve_authority(
            proposal,
            qid_index,
            wiki_index,
            parent,
            resolve_lcsh_online=False,
            seed_qid=seed_qid,
        )
        authority["lcc_primary"] = primary
        authority["lcc_codes"] = codes
    else:
        authority = resolve_authority(
            proposal,
            qid_index,
            wiki_index,
            parent,
            resolve_lcsh_online=resolve_lcsh_online,
            seed_qid=seed_qid,
        )
        authority["lcc_primary"] = primary
        authority["lcc_codes"] = codes

    proposal["authority"] = authority
    if authority.get("lcsh_id"):
        proposal["lcsh_id"] = authority["lcsh_id"]
    if authority.get("lcsh_label"):
        proposal["lcsh_label"] = authority["lcsh_label"]
    elif authority.get("topic_qid_label") and not authority.get("lcsh_id"):
        proposal["lcsh_label"] = authority["topic_qid_label"]
    if authority.get("fast_id"):
        proposal["fast_id"] = authority["fast_id"]

    proposal["display_label"] = proposal.get("label")
    proposal["authority_label"] = authority.get("lcsh_label") or proposal.get("label")

    proposal["facet_weights"] = infer_facet_weights(proposal, training)
    # Tentative training corpus — review JSON only; SFA promotes important works via claims.
    proposal["supporting_works"] = supporting_works_for_facet(training)
    if work_index is not None:
        proposal["supporting_works_detail"] = label_supporting_works(
            proposal["supporting_works"], work_index
        )
    proposal["validation"] = validate_ccs(proposal)
    proposal["status"] = proposal.get("status", "proposed")

    return proposal


def enrich_proposals(
    proposals: list[dict],
    *,
    seed_qid: str,
    trainings: dict[str, dict],
    packs: dict[str, dict],
    harvest: dict | None = None,
    fetch_wikidata: bool = True,
    resolve_lcsh_online: bool = False,
    training_dir: Path | None = None,
) -> list[dict]:
    """Enrich all proposals with backbone metadata."""
    qid_index = build_qid_authority_index(packs, harvest)

    proposals, entity_index = sanitize_proposals(
        proposals,
        seed_qid=seed_qid,
        scope_lcsh_curated=SCOPE_LCSH_CURATED,
        fetch_missing=True,
    )
    rejected_total = sum(len(p.get("candidate_qids_rejected", [])) for p in proposals)
    if rejected_total:
        print(f"  Sanitized candidate QIDs: rejected {rejected_total} junk/missing/off-scope items")
    from scripts.agents.domain_initiator.seed_index import load_seed_index

    if load_seed_index(seed_qid):
        print(f"  Seed index: JSON/wikidata/derived/{seed_qid}_seed_index.json (connected QID gate active)")

    wiki_index = entities_to_wiki_index(entity_index)
    if fetch_wikidata:
        all_qids = [qid for p in proposals for qid in p.get("candidate_qids", [])]
        sparql_index = fetch_wikidata_authorities(list(dict.fromkeys(all_qids)))
        for qid, entry in sparql_index.items():
            wiki_index.setdefault(qid, {}).update(entry)

    training_dir = training_dir or Path(__file__).resolve().parents[3] / "output" / "di_training"
    work_index = build_work_index(training_dir, seed_qid)

    enriched: list[dict] = []
    for p in proposals:
        facet = p.get("source_facet", "")
        enriched.append(
            enrich_proposal(
                p,
                seed_qid=seed_qid,
                pack=packs.get(facet),
                training=trainings.get(facet),
                qid_index=qid_index,
                wiki_index=wiki_index,
                resolve_lcsh_online=resolve_lcsh_online,
                work_index=work_index,
            )
        )
    return enriched
