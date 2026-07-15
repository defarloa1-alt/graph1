#!/usr/bin/env python3
"""
Validate and sanitize Wikidata candidate QIDs for DI training and proposals.

Filters hallucinated, missing, blocked, and off-topic entities before they reach
proposal JSON or graph writes.
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from scripts.agents.domain_initiator.seed_index import (
    allowed_qid_set,
    is_seed_connected,
    label_from_index,
    load_seed_index,
)

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
HTTP_HEADERS = {"User-Agent": "Chrystallum/1.0 (DI candidate QID validation)"}

QID_PATTERN = re.compile(r"^Q\d+$")

# Known false positives from SFA training noise
BLOCKED_CANDIDATE_QIDS = frozenset(
    {
        "Q160534",  # Jack Kerouac
        "Q189822",  # Mahilyow Region
        "Q2280988",  # Blinker en het Bagbag-juweel (film)
    }
)

# Entity types that are never valid subject-concept anchors
BLOCKED_INSTANCE_QIDS = frozenset(
    {
        "Q11424",  # film
        "Q7889",  # video game
        "Q211912",  # television series episode
        "Q5398426",  # television series
        "Q482994",  # album
        "Q134556",  # single
        "Q4167410",  # Wikimedia disambiguation page
        "Q4167836",  # Wikimedia category
        "Q13406463",  # Wikimedia list article
    }
)

# Roman Republican scope signals — prefer multi-word phrases; avoid bare "roman" (Roman-Catholic)
ROMAN_SCOPE_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\brome\b",
        r"\broman republic\b",
        r"\bancient rome\b",
        r"\broman senate\b",
        r"\broman consul\b",
        r"\broman magistrat",
        r"\broman citizen",
        r"\broman assembl",
        r"\broman army\b",
        r"\broman law\b",
        r"\broman temple\b",
        r"\broman religion\b",
        r"\broman republican\b",
        r"\broman histor",
        r"\broman provinc",
        r"\broman empire\b",
        r"\brepublican rome\b",
        r"\bmos maiorum\b",
        r"\bmixed government\b",
        r"\bimperium\b",
        r"\bcomitia\b",
        r"\bcursus honorum\b",
        r"\bplebeian\b",
        r"\bpatrician\b",
        r"\bconsul\b",
        r"\bpraetor\b",
        r"\baedile\b",
        r"\bcensor\b",
        r"\bquaestor\b",
        r"\btribun",
        r"\bsenatus\b",
        r"\bsenate\b",
        r"\baristocratic republic\b",
        r"\bconflict of the orders\b",
        r"\btwelve tables\b",
        r"\bsocial war\b",
        r"\bcivil war\b",
        r"\btriumvirate\b",
        r"\bgracch",
        r"\bsulla\b",
        r"\bitali\b",
        r"\barchaeolog",
        r"\bepigraph",
        r"\binscription\b",
        r"\bprosopograph",
        r"\bgladiator\b",
        r"\baugur",
        r"\bpriesthood\b",
        r"\bmanumission\b",
        r"\bpatronage\b",
        r"\bclientela\b",
        r"\benfranch",
        r"\bcivitas\b",
        r"\blex ",
        r"\bpolitical (?:office|institution|system|theory)\b",
        r"\bconstitution of the roman republic\b",
    )
)

# Extra anchors beyond topic_qid in SCOPE_LCSH_CURATED (human-reviewed)
SCOPE_CANDIDATE_QIDS_CURATED: dict[str, list[str]] = {
    "constitutional_institutions": [
        "Q2576746",
        "Q361916",
        "Q499146",
        "Q1887031",
        "Q666680",
    ],
    "magistracy_cursus_honorum": [
        "Q27518",
        "Q40779",
        "Q20778343",
        "Q21597597",
    ],
    "senatorial_politics": [
        "Q130614",
        "Q131306",
        "Q20108410",
    ],
    "popular_politics_assemblies": [
        "Q623086",
        "Q1114852",
    ],
    "conflict_orders_early_republic": [
        "Q747480",
    ],
    "late_republican_crisis": [
        "Q715380",
        "Q1812526",
    ],
    "citizenship_enfranchisement": [
        "Q213810",
        "Q15282014",
    ],
}


def _text_matches_roman_scope(text: str) -> bool:
    return any(pattern.search(text) for pattern in ROMAN_SCOPE_PATTERNS)


def _trusted_curated_qids(
    scope_key: str,
    scope_lcsh_curated: dict[str, dict[str, str]] | None,
) -> frozenset[str]:
    trusted: set[str] = set(SCOPE_CANDIDATE_QIDS_CURATED.get(scope_key, []))
    if scope_lcsh_curated:
        topic = scope_lcsh_curated.get(scope_key, {}).get("topic_qid")
        if topic:
            trusted.add(topic)
    return frozenset(trusted)


@dataclass
class CandidateEntity:
    qid: str
    label: str | None = None
    description: str | None = None
    instance_of: list[str] = field(default_factory=list)
    lcsh_id: str | None = None
    fast_id: str | None = None
    missing: bool = False


@dataclass
class SanitizeResult:
    valid: list[str]
    rejected: list[dict[str, str]]

    @property
    def changed(self) -> bool:
        return bool(self.rejected)


def _claim_entity_ids(claims: dict, pid: str) -> list[str]:
    ids: list[str] = []
    for stmt in claims.get(pid, []):
        mainsnak = stmt.get("mainsnak", {})
        if mainsnak.get("snaktype") != "value":
            continue
        dv = mainsnak.get("datavalue", {})
        if dv.get("type") != "wikibase-entityid":
            continue
        val = dv.get("value", {})
        qid = val.get("id")
        if not qid and val.get("numeric-id") is not None:
            qid = f"Q{val['numeric-id']}"
        if qid:
            ids.append(qid)
    return ids


def _claim_string_values(claims: dict, pid: str) -> list[str]:
    values: list[str] = []
    for stmt in claims.get(pid, []):
        mainsnak = stmt.get("mainsnak", {})
        if mainsnak.get("snaktype") != "value":
            continue
        dv = mainsnak.get("datavalue", {})
        if dv.get("type") == "string":
            values.append(dv.get("value", ""))
    return values


def _pick_label(entity: dict) -> str | None:
    labels = entity.get("labels", {})
    for lang in ("en", "la", "de", "fr", "it"):
        if lang in labels:
            return labels[lang].get("value")
    if labels:
        first = next(iter(labels.values()))
        return first.get("value")
    return None


def _pick_description(entity: dict) -> str | None:
    descriptions = entity.get("descriptions", {})
    for lang in ("en", "de", "fr", "it"):
        if lang in descriptions:
            return descriptions[lang].get("value")
    if descriptions:
        first = next(iter(descriptions.values()))
        return first.get("value")
    return None


def _parse_entity(qid: str, entity: dict) -> CandidateEntity:
    if entity.get("missing"):
        return CandidateEntity(qid=qid, missing=True)
    claims = entity.get("claims", {})
    lcsh_vals = _claim_string_values(claims, "P244")
    fast_vals = _claim_string_values(claims, "P2163")
    return CandidateEntity(
        qid=qid,
        label=_pick_label(entity),
        description=_pick_description(entity),
        instance_of=_claim_entity_ids(claims, "P31"),
        lcsh_id=lcsh_vals[0] if lcsh_vals else None,
        fast_id=fast_vals[0] if fast_vals else None,
        missing=False,
    )


def _fetch_entity_batch(batch: list[str], *, retries: int = 3) -> dict[str, CandidateEntity]:
    out: dict[str, CandidateEntity] = {}
    params = urllib.parse.urlencode(
        {
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "props": "labels|descriptions|claims",
            "languages": "en",
            "format": "json",
        }
    )
    url = f"{WIKIDATA_API}?{params}"
    last_error: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers=HTTP_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            for qid, entity in payload.get("entities", {}).items():
                out[qid] = _parse_entity(qid, entity)
            return out
        except Exception as exc:
            last_error = exc
            time.sleep(0.75 * (attempt + 1))
    if last_error:
        for qid in batch:
            out.setdefault(qid, CandidateEntity(qid=qid, missing=True))
    return out


def fetch_candidate_entities(qids: list[str], *, batch_size: int = 20) -> dict[str, CandidateEntity]:
    """Fetch labels, descriptions, P31, and authority IDs via Wikidata API."""
    clean = [q for q in dict.fromkeys(qids) if q and QID_PATTERN.match(q)]
    out: dict[str, CandidateEntity] = {}

    for i in range(0, len(clean), batch_size):
        batch = clean[i : i + batch_size]
        out.update(_fetch_entity_batch(batch))
        time.sleep(0.35)

    missing_after_batch = [qid for qid in clean if out.get(qid) is None or out[qid].missing]
    for qid in missing_after_batch:
        single = _fetch_entity_batch([qid], retries=2)
        if qid in single:
            out[qid] = single[qid]
        else:
            out[qid] = CandidateEntity(qid=qid, missing=True)
        time.sleep(0.25)

    for qid in clean:
        out.setdefault(qid, CandidateEntity(qid=qid, missing=True))
    return out


def label_plausible_for_scope(
    qid: str,
    label: str | None,
    scope_label: str,
    *,
    seed_qid: str = "Q17167",
    description: str | None = None,
) -> bool:
    """Reject Wikidata items whose labels/descriptions are unrelated to Roman scope work."""
    if not qid or qid in BLOCKED_CANDIDATE_QIDS:
        return False
    if qid == seed_qid:
        return True
    label_text = (label or "").strip()
    if not label_text:
        return False
    haystack = f"{label_text} {description or ''}"
    return _text_matches_roman_scope(haystack)


def validate_candidate_qid(
    qid: str,
    entity: CandidateEntity | None,
    *,
    scope_label: str,
    seed_qid: str = "Q17167",
    source_facet: str = "",
    trusted_curated: bool = False,
    seed_index: dict[str, Any] | None = None,
) -> tuple[bool, str]:
    if not qid or not QID_PATTERN.match(qid):
        return False, "invalid_qid_format"
    if qid in BLOCKED_CANDIDATE_QIDS:
        return False, "blocked_qid"
    if entity is None or entity.missing:
        return False, "missing_entity"
    if not entity.label:
        indexed_label = label_from_index(seed_index, qid)
        if indexed_label:
            entity.label = indexed_label
        else:
            return False, "missing_label"
    blocked_types = set(entity.instance_of) & BLOCKED_INSTANCE_QIDS
    if blocked_types:
        return False, f"blocked_instance_type:{','.join(sorted(blocked_types))}"
    if trusted_curated:
        return True, "curated"
    if qid.upper() == seed_qid.upper():
        return True, "seed"
    if seed_index and not is_seed_connected(qid, seed_index):
        return False, "not_seed_connected"
    if seed_index and is_seed_connected(qid, seed_index):
        return True, "seed_index"
    if (
        "Q5" in entity.instance_of
        and source_facet.lower() != "biographic"
        and not label_plausible_for_scope(
            qid,
            entity.label,
            scope_label,
            seed_qid=seed_qid,
            description=entity.description,
        )
    ):
        return False, "human_off_topic"
    if not label_plausible_for_scope(
        qid,
        entity.label,
        scope_label,
        seed_qid=seed_qid,
        description=entity.description,
    ):
        return False, "label_off_scope"
    return True, "ok"


def curated_qids_for_scope(scope_key: str, *, scope_lcsh_curated: dict[str, dict[str, str]] | None = None) -> list[str]:
    """Merge explicit curated anchors with topic_qid from scope LCSH map."""
    qids: list[str] = []
    qids.extend(SCOPE_CANDIDATE_QIDS_CURATED.get(scope_key, []))
    if scope_lcsh_curated:
        topic = scope_lcsh_curated.get(scope_key, {}).get("topic_qid")
        if topic:
            qids.append(topic)
    return list(dict.fromkeys(qids))


def sanitize_candidate_qids(
    raw_qids: list[str],
    *,
    scope_key: str = "",
    scope_label: str = "",
    seed_qid: str = "Q17167",
    source_facet: str = "",
    entities: dict[str, CandidateEntity] | None = None,
    merge_curated: bool = True,
    scope_lcsh_curated: dict[str, dict[str, str]] | None = None,
    seed_index: dict[str, Any] | None = None,
) -> SanitizeResult:
    """Return validated QIDs in stable order; optionally merge curated anchors."""
    ordered: list[str] = list(dict.fromkeys(q for q in raw_qids if q))
    if merge_curated and scope_key:
        for qid in curated_qids_for_scope(scope_key, scope_lcsh_curated=scope_lcsh_curated):
            if qid not in ordered:
                ordered.append(qid)

    if entities is None:
        entities = fetch_candidate_entities(ordered)

    trusted = _trusted_curated_qids(scope_key, scope_lcsh_curated)
    valid: list[str] = []
    rejected: list[dict[str, str]] = []
    seen_valid: set[str] = set()

    for qid in ordered:
        ok, reason = validate_candidate_qid(
            qid,
            entities.get(qid),
            scope_label=scope_label,
            seed_qid=seed_qid,
            source_facet=source_facet,
            trusted_curated=qid in trusted,
            seed_index=seed_index,
        )
        if ok:
            if qid not in seen_valid:
                valid.append(qid)
                seen_valid.add(qid)
        else:
            rejected.append({"qid": qid, "reason": reason})

    return SanitizeResult(valid=valid, rejected=rejected)


def entities_to_wiki_index(entities: dict[str, CandidateEntity]) -> dict[str, dict[str, Any]]:
    """Adapt CandidateEntity map to proposal_backbone wiki_index shape."""
    out: dict[str, dict[str, Any]] = {}
    for qid, entity in entities.items():
        if entity.missing or not entity.label:
            continue
        entry: dict[str, Any] = {"label": entity.label}
        if entity.lcsh_id:
            entry["lcsh_id"] = entity.lcsh_id
        if entity.fast_id:
            entry["fast_id"] = entity.fast_id
        out[qid] = entry
    return out


def _sanitize_qid_list_in_place(
    obj: dict,
    key: str,
    *,
    scope_key: str,
    scope_label: str,
    seed_qid: str,
    source_facet: str,
    entities: dict[str, CandidateEntity],
    rejected_log: list[dict[str, str]],
    seed_index: dict[str, Any] | None = None,
) -> None:
    if key not in obj:
        return
    raw = obj.get(key) or []
    if not isinstance(raw, list):
        return
    result = sanitize_candidate_qids(
        raw,
        scope_key=scope_key,
        scope_label=scope_label,
        seed_qid=seed_qid,
        source_facet=source_facet,
        entities=entities,
        merge_curated=False,
        seed_index=seed_index,
    )
    obj[key] = result.valid
    for item in result.rejected:
        rejected_log.append({**item, "context": key})


def sanitize_training_output(
    training: dict,
    *,
    seed_qid: str,
    source_facet: str,
    scope_lcsh_curated: dict[str, dict[str, str]] | None = None,
    fetch_missing: bool = True,
    seed_index: dict[str, Any] | None = None,
) -> dict:
    """Sanitize candidate_qids throughout a facet training JSON document."""
    if seed_index is None:
        seed_index = load_seed_index(seed_qid)
    if scope_lcsh_curated is None:
        from scripts.agents.domain_initiator.proposal_backbone import SCOPE_LCSH_CURATED

        scope_lcsh_curated = SCOPE_LCSH_CURATED

    all_qids: list[str] = []

    decomp = training.get("decomposition_assessment") or {}
    sub_scopes = decomp.get("sub_scopes") or []
    for scope in sub_scopes:
        all_qids.extend(scope.get("candidate_qids") or [])
        if scope.get("scope_key"):
            all_qids.extend(
                curated_qids_for_scope(scope["scope_key"], scope_lcsh_curated=scope_lcsh_curated)
            )

    meth = training.get("methodology_reflection") or {}
    for rp in meth.get("repertoire_patterns") or []:
        all_qids.extend(rp.get("candidate_qids") or [])
    for pp in meth.get("proposed_patterns") or []:
        all_qids.extend(pp.get("candidate_qids") or [])

    entities: dict[str, CandidateEntity] = {}
    if fetch_missing and all_qids:
        entities = fetch_candidate_entities(list(dict.fromkeys(all_qids)))

    rejected_log: list[dict[str, str]] = []
    for scope in sub_scopes:
        scope_key = scope.get("scope_key", "")
        scope_label = scope.get("scope_label", scope_key)
        merged = sanitize_candidate_qids(
            scope.get("candidate_qids") or [],
            scope_key=scope_key,
            scope_label=scope_label,
            seed_qid=seed_qid,
            source_facet=source_facet,
            entities=entities,
            merge_curated=True,
            scope_lcsh_curated=scope_lcsh_curated,
            seed_index=seed_index,
        )
        scope["candidate_qids"] = merged.valid
        for item in merged.rejected:
            rejected_log.append({**item, "context": f"sub_scope:{scope_key}"})

    for rp in meth.get("repertoire_patterns") or []:
        _sanitize_qid_list_in_place(
            rp,
            "candidate_qids",
            scope_key="",
            scope_label=rp.get("pattern_label", ""),
            seed_qid=seed_qid,
            source_facet=source_facet,
            entities=entities,
            rejected_log=rejected_log,
            seed_index=seed_index,
        )
    for pp in meth.get("proposed_patterns") or []:
        _sanitize_qid_list_in_place(
            pp,
            "candidate_qids",
            scope_key="",
            scope_label=pp.get("proposed_label", ""),
            seed_qid=seed_qid,
            source_facet=source_facet,
            entities=entities,
            rejected_log=rejected_log,
            seed_index=seed_index,
        )

    if rejected_log:
        training["candidate_qids_sanitized"] = {
            "rejected_count": len(rejected_log),
            "rejected": rejected_log,
        }
    return training


def sanitize_proposals(
    proposals: list[dict],
    *,
    seed_qid: str,
    scope_lcsh_curated: dict[str, dict[str, str]] | None = None,
    fetch_missing: bool = True,
    seed_index: dict[str, Any] | None = None,
) -> tuple[list[dict], dict[str, CandidateEntity]]:
    """Sanitize candidate_qids on each proposal; return proposals and entity index."""
    if seed_index is None:
        seed_index = load_seed_index(seed_qid)
    all_qids: list[str] = []
    for proposal in proposals:
        all_qids.extend(proposal.get("candidate_qids") or [])
        scope_key = proposal.get("scope_key", "")
        if scope_key:
            all_qids.extend(
                curated_qids_for_scope(scope_key, scope_lcsh_curated=scope_lcsh_curated)
            )
        qid = proposal.get("authority", {}).get("topic_qid")
        if qid:
            all_qids.append(qid)

    entities: dict[str, CandidateEntity] = {}
    if fetch_missing and all_qids:
        entities = fetch_candidate_entities(list(dict.fromkeys(all_qids)))

    for proposal in proposals:
        scope_key = proposal.get("scope_key", "")
        scope_label = proposal.get("label", scope_key)
        source_facet = proposal.get("source_facet", "")
        result = sanitize_candidate_qids(
            proposal.get("candidate_qids") or [],
            scope_key=scope_key,
            scope_label=scope_label,
            seed_qid=seed_qid,
            source_facet=source_facet,
            entities=entities,
            merge_curated=True,
            scope_lcsh_curated=scope_lcsh_curated,
            seed_index=seed_index,
        )
        proposal["candidate_qids"] = result.valid
        if result.rejected:
            proposal["candidate_qids_rejected"] = result.rejected
        if seed_index:
            proposal["seed_index_qid"] = seed_qid

    return proposals, entities


if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(ROOT))

    parser = argparse.ArgumentParser(description="Sanitize candidate QIDs in DI training JSON files")
    parser.add_argument("--seed", default="Q17167")
    parser.add_argument("--training-dir", type=Path, default=Path("output/di_training"))
    parser.add_argument("--facet", default=None, help="Optional facet key (e.g. political)")
    args = parser.parse_args()

    pattern = f"{args.seed}_*_training.json" if not args.facet else f"{args.seed}_{args.facet.upper()}_training.json"
    files = sorted(args.training_dir.glob(pattern))
    if not files:
        print(f"No training files matching {pattern} in {args.training_dir}")
        raise SystemExit(1)

    for path in files:
        facet = path.stem.replace(f"{args.seed}_", "").replace("_training", "").lower()
        with open(path, encoding="utf-8") as f:
            training = json.load(f)
        before = sum(
            len(ss.get("candidate_qids") or [])
            for ss in (training.get("decomposition_assessment") or {}).get("sub_scopes") or []
        )
        training = sanitize_training_output(
            training, seed_qid=args.seed, source_facet=facet
        )
        after = sum(
            len(ss.get("candidate_qids") or [])
            for ss in (training.get("decomposition_assessment") or {}).get("sub_scopes") or []
        )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(training, f, indent=2, ensure_ascii=False)
        rejected = (training.get("candidate_qids_sanitized") or {}).get("rejected_count", 0)
        print(f"{path.name}: candidates {before} -> {after}, rejected {rejected}")
