#!/usr/bin/env python3
"""Fetch all Wikidata statements (claims) for a given QID.

This script retrieves the full claim set for an entity and returns
statement-level data including:
- main snak (property/value)
- qualifiers
- references
- rank

Usage:
  python scripts/tools/wikidata_fetch_all_statements.py --qid Q1048
  python scripts/tools/wikidata_fetch_all_statements.py --qid Q1048 --output out/q1048_statements.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


API_URL = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Graph1WikidataStatements/1.0 (local tooling)"


def _normalize_entity_id(value: Dict[str, Any]) -> Any:
    entity_type = value.get("entity-type")
    numeric_id = value.get("numeric-id")
    if isinstance(numeric_id, int):
        if entity_type == "item":
            return f"Q{numeric_id}"
        if entity_type == "property":
            return f"P{numeric_id}"
        if entity_type == "lexeme":
            return f"L{numeric_id}"
    return value


def _parse_datavalue(datavalue: Dict[str, Any]) -> Any:
    value_type = datavalue.get("type")
    value = datavalue.get("value")
    if value_type == "wikibase-entityid" and isinstance(value, dict):
        return _normalize_entity_id(value)
    if value_type in {"string", "external-id", "url", "commonsMedia"}:
        return value
    if value_type == "monolingualtext" and isinstance(value, dict):
        return {"text": value.get("text"), "language": value.get("language")}
    if value_type == "time" and isinstance(value, dict):
        return {
            "time": value.get("time"),
            "precision": value.get("precision"),
            "timezone": value.get("timezone"),
            "before": value.get("before"),
            "after": value.get("after"),
            "calendarmodel": value.get("calendarmodel"),
        }
    if value_type == "quantity" and isinstance(value, dict):
        return {
            "amount": value.get("amount"),
            "unit": value.get("unit"),
            "lowerBound": value.get("lowerBound"),
            "upperBound": value.get("upperBound"),
        }
    if value_type == "globecoordinate" and isinstance(value, dict):
        return {
            "latitude": value.get("latitude"),
            "longitude": value.get("longitude"),
            "precision": value.get("precision"),
            "globe": value.get("globe"),
        }
    return value


def _parse_snak(snak: Dict[str, Any]) -> Dict[str, Any]:
    parsed = {
        "property": snak.get("property"),
        "snaktype": snak.get("snaktype"),
        "datatype": snak.get("datatype"),
    }
    datavalue = snak.get("datavalue")
    if isinstance(datavalue, dict):
        parsed["value_type"] = datavalue.get("type")
        parsed["value"] = _parse_datavalue(datavalue)
    return parsed


def _parse_claim(claim: Dict[str, Any]) -> Dict[str, Any]:
    parsed = {
        "statement_id": claim.get("id"),
        "type": claim.get("type"),
        "rank": claim.get("rank"),
        "mainsnak": _parse_snak(claim.get("mainsnak", {})),
    }

    qualifiers = claim.get("qualifiers", {})
    parsed_qualifiers: Dict[str, List[Dict[str, Any]]] = {}
    for prop, snaks in qualifiers.items():
        parsed_qualifiers[prop] = [_parse_snak(snak) for snak in snaks]
    if parsed_qualifiers:
        parsed["qualifiers"] = parsed_qualifiers
        parsed["qualifiers_order"] = claim.get("qualifiers-order", [])

    references = claim.get("references", [])
    parsed_refs: List[Dict[str, Any]] = []
    for ref in references:
        ref_snaks = ref.get("snaks", {})
        parsed_ref_snaks: Dict[str, List[Dict[str, Any]]] = {}
        for prop, snaks in ref_snaks.items():
            parsed_ref_snaks[prop] = [_parse_snak(snak) for snak in snaks]
        parsed_refs.append(
            {
                "hash": ref.get("hash"),
                "snaks_order": ref.get("snaks-order", []),
                "snaks": parsed_ref_snaks,
            }
        )
    if parsed_refs:
        parsed["references"] = parsed_refs

    return parsed


def fetch_entity(qid: str) -> Optional[Dict[str, Any]]:
    params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": qid,
        "languages": "en",
        "props": "labels|descriptions|claims",
    }
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(API_URL, params=params, headers=headers, timeout=40)
    response.raise_for_status()
    payload = response.json()
    entities = payload.get("entities", {})
    entity = entities.get(qid)
    if not entity or "missing" in entity:
        return None
    return entity


def build_statement_payload(entity: Dict[str, Any], qid: str) -> Dict[str, Any]:
    claims = entity.get("claims", {})
    parsed_claims: Dict[str, List[Dict[str, Any]]] = {}
    total = 0
    for prop, claim_list in claims.items():
        parsed = [_parse_claim(claim) for claim in claim_list]
        parsed_claims[prop] = parsed
        total += len(parsed)

    return {
        "qid": qid,
        "label": entity.get("labels", {}).get("en", {}).get("value"),
        "description": entity.get("descriptions", {}).get("en", {}).get("value"),
        "statement_count": total,
        "property_count": len(parsed_claims),
        "claims": parsed_claims,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qid", required=True, help="Wikidata QID (e.g., Q1048)")
    parser.add_argument("--output", help="Optional output JSON file path")
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only summary; do not print full JSON to stdout.",
    )
    args = parser.parse_args()

    qid = args.qid.strip().upper()
    if not qid.startswith("Q") or not qid[1:].isdigit():
        raise ValueError(f"Invalid QID: {qid}")

    entity = fetch_entity(qid)
    if entity is None:
        raise RuntimeError(f"QID not found: {qid}")

    result = build_statement_payload(entity, qid)

    print(
        f"qid={result['qid']} label={result['label']} "
        f"properties={result['property_count']} statements={result['statement_count']}"
    )

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote={out_path}")

    if not args.summary_only:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
