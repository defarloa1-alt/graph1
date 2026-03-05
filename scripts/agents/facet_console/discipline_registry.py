"""
Facet Console - discipline registry

Returns facet->discipline mapping. Tries Neo4j (CQ-02b) first; falls back to
config/discipline_registry_fallback.json when graph has no Discipline nodes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

CQ_02B = """
MATCH (d:Entity {entity_type:'CONCEPT'})
WHERE $facet_label IN d.facets
RETURN d.qid AS qid, d.label AS label, d.facets AS facets, d.primary_for AS primary_for,
       d.in_graph AS in_graph, d.needs_harvest AS needs_harvest, d.oa_id AS oa_id,
       d.lcsh AS lcsh, d.lcc AS lcc, d.repos AS repos
"""


def _load_fallback() -> list[dict]:
    path = _root / "config" / "discipline_registry_fallback.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("disciplines", [])


def get_facet_disciplines(
    facet_label: str,
    session=None,
    prioritize_primary: bool = True,
    max_disciplines: int | None = None,
) -> list[dict]:
    """
    Return disciplines that serve the given facet.
    Tries Neo4j CQ-02b first; falls back to JSON when graph has no matches.
    """
    disciplines = []

    if session:
        try:
            result = session.run(CQ_02B, facet_label=facet_label)
            for r in result:
                d = dict(r)
                disciplines.append({
                    "qid": d.get("qid"),
                    "label": d.get("label"),
                    "facets": d.get("facets") or [],
                    "primary_for": d.get("primary_for") or [],
                    "in_graph": d.get("in_graph", False),
                    "needs_harvest": d.get("needs_harvest", False),
                    "oa_id": d.get("oa_id"),
                    "lcsh": d.get("lcsh"),
                    "lcc": d.get("lcc"),
                    "repos": d.get("repos") or [],
                })
        except Exception:
            pass

    if not disciplines:
        fallback = _load_fallback()
        for d in fallback:
            if facet_label in (d.get("facets") or []) or facet_label in (d.get("primary_for") or []):
                disciplines.append({
                    "qid": d.get("qid"),
                    "label": d.get("label"),
                    "facets": d.get("facets") or [],
                    "primary_for": d.get("primary_for") or [],
                    "in_graph": d.get("in_graph", False),
                    "needs_harvest": d.get("needs_harvest", False),
                    "oa_id": d.get("oa_id"),
                    "lcsh": d.get("lcsh"),
                    "lcc": d.get("lcc"),
                    "repos": d.get("repos") or [],
                })

    if prioritize_primary:
        disciplines.sort(key=lambda x: (0 if facet_label in (x.get("primary_for") or []) else 1, -len(x.get("facets") or [])))

    if max_disciplines:
        disciplines = disciplines[:max_disciplines]

    return disciplines
