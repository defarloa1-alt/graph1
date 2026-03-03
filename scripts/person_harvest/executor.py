#!/usr/bin/env python3
"""
Person Harvest Executor — ADR-008 Layer 3

Deterministic execution of PersonHarvestPlan. Schema-validated Cypher writes.
"""

from __future__ import annotations

import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_scripts))

try:
    from tools.entity_cipher import generate_entity_cipher
except ImportError:
    generate_entity_cipher = None


def _entity_cipher(qid: str | None, dprr_id, namespace: str) -> str:
    """Generate entity_cipher per schema requirement."""
    if generate_entity_cipher:
        c = generate_entity_cipher(qid or f"dprr_{dprr_id}", "PERSON", namespace)
        if c:
            return c
    return f"ent_per_{qid or f'dprr_{dprr_id}'}"


def execute_plan(plan: dict, session, dry_run: bool = False) -> dict:
    """
    Execute PersonHarvestPlan. Returns {created, updated, skipped, errors}.
    """
    stats = {"created": 0, "updated": 0, "skipped": 0, "errors": []}
    qid = plan.get("person_qid", "")
    dprr_id = plan.get("dprr_id")
    person_class = plan.get("person_class", "CONFIRMED")

    if person_class == "MYTHOLOGICAL":
        stats["skipped"] = 1
        return stats

    # Ensure Entity exists — align with dprr_import entity_id format
    if qid:
        entity_id = f"person_q{qid[1:].lower()}" if qid.startswith("Q") else f"person_q{qid}"
    else:
        entity_id = f"person_dprr_{dprr_id}"
    if not qid and not dprr_id:
        stats["errors"].append("No qid or dprr_id")
        return stats

    # ADR-007 four-label schema
    label_val = plan.get("label") or ""
    if label_val is None:
        label_val = ""
    label_dprr = plan.get("label_dprr")
    label_latin = plan.get("label_latin")
    label_sort = plan.get("label_sort")
    cipher = _entity_cipher(qid or None, dprr_id, "wd" if qid else "dprr")

    # Ensure Entity exists — MATCH then CREATE
    if not dry_run:
        if qid:
            result = session.run("MATCH (e:Entity {qid: $qid}) RETURN e LIMIT 1", qid=qid)
            if result.single() is None:
                session.run("""
                    CREATE (e:Entity {
                        qid: $qid, entity_id: $entity_id, entity_cipher: $cipher,
                        label: $label, label_dprr: $label_dprr, label_latin: $label_latin, label_sort: $label_sort,
                        entity_type: 'PERSON'
                    })
                """, qid=qid, entity_id=entity_id, cipher=cipher,
                     label=label_val, label_dprr=label_dprr, label_latin=label_latin, label_sort=label_sort)
            else:
                session.run("""
                    MATCH (e:Entity {qid: $qid})
                    SET e.entity_id = COALESCE(e.entity_id, $entity_id),
                        e.entity_cipher = COALESCE(e.entity_cipher, $cipher),
                        e.entity_type = COALESCE(e.entity_type, 'PERSON'),
                        e.label = COALESCE(e.label, $label),
                        e.label_dprr = COALESCE(e.label_dprr, $label_dprr),
                        e.label_latin = COALESCE(e.label_latin, $label_latin),
                        e.label_sort = COALESCE(e.label_sort, $label_sort)
                """, qid=qid, entity_id=entity_id, cipher=cipher,
                     label=label_val, label_dprr=label_dprr, label_latin=label_latin, label_sort=label_sort)
        else:
            dprr_uri = f"http://romanrepublic.ac.uk/rdf/entity/Person/{dprr_id}"
            result = session.run("MATCH (e:Entity {dprr_uri: $dprr_uri}) RETURN e LIMIT 1", dprr_uri=dprr_uri)
            if result.single() is None:
                session.run("""
                    CREATE (e:Entity {
                        dprr_uri: $dprr_uri, entity_id: $entity_id, entity_cipher: $cipher,
                        label: $label, label_dprr: $label_dprr, label_latin: $label_latin, label_sort: $label_sort,
                        dprr_id: $dprr_id, entity_type: 'PERSON'
                    })
                """, dprr_uri=dprr_uri, entity_id=entity_id, cipher=cipher,
                     label=label_val, label_dprr=label_dprr, label_latin=label_latin, label_sort=label_sort,
                     dprr_id=str(dprr_id))
            else:
                session.run("""
                    MATCH (e:Entity {dprr_uri: $dprr_uri})
                    SET e.entity_id = COALESCE(e.entity_id, $entity_id),
                        e.entity_cipher = COALESCE(e.entity_cipher, $cipher),
                        e.entity_type = COALESCE(e.entity_type, 'PERSON'),
                        e.label = COALESCE(e.label, $label),
                        e.label_dprr = COALESCE(e.label_dprr, $label_dprr),
                        e.label_latin = COALESCE(e.label_latin, $label_latin),
                        e.label_sort = COALESCE(e.label_sort, $label_sort)
                """, dprr_uri=dprr_uri, entity_id=entity_id, cipher=cipher,
                     label=label_val, label_dprr=label_dprr, label_latin=label_latin, label_sort=label_sort)

        if dprr_id and qid:
            session.run("""
                MATCH (e:Entity {qid: $qid})
                SET e.dprr_id = $dprr_id, e.dprr_uri = $dprr_uri
            """, qid=qid, dprr_id=str(dprr_id), dprr_uri=f"http://romanrepublic.ac.uk/rdf/entity/Person/{dprr_id}")

    stats["updated"] = 1

    # Write FATHER_OF / MOTHER_OF / SIBLING_OF / SPOUSE_OF from attribute_claims
    for claim in plan.get("attribute_claims", []):
        attr = claim.get("attribute", "")
        val = claim.get("value", "")
        if attr == "father_qid" and val:
            _ensure_father_of(session, qid, val, dry_run, stats)
        elif attr == "mother_qid" and val:
            _ensure_mother_of(session, qid, val, dry_run, stats)
        elif attr == "sibling_qid" and val and qid:
            _ensure_sibling_of(session, qid, val, dry_run, stats)
        elif attr == "spouse_qid" and val and qid:
            _ensure_spouse_of(session, qid, val, dry_run, stats)

    # Temporal backbone: BORN_IN_YEAR, DIED_IN_YEAR, birth_date, death_date
    _write_temporal_to_entity(
        session,
        qid=qid,
        dprr_uri=f"http://romanrepublic.ac.uk/rdf/entity/Person/{dprr_id}" if dprr_id else None,
        birth_year=plan.get("birth_year"),
        death_year=plan.get("death_year"),
        birth_date=plan.get("birth_date"),
        death_date=plan.get("death_date"),
        dry_run=dry_run,
    )

    return stats


def _write_temporal_to_entity(
    session,
    qid: str | None,
    dprr_uri: str | None,
    birth_year: int | None,
    death_year: int | None,
    birth_date: str | None,
    death_date: str | None,
    dry_run: bool = False,
):
    """Link Person to Year backbone via BORN_IN_YEAR, DIED_IN_YEAR; set birth_date, death_date."""
    if dry_run or (not qid and not dprr_uri):
        return
    match_clause = "MATCH (e:Entity)" + (" WHERE e.qid = $qid" if qid else " WHERE e.dprr_uri = $dprr_uri")
    params = {"qid": qid, "dprr_uri": dprr_uri}

    if birth_year is not None:
        session.run(
            match_clause + """
            MERGE (y:Year {year: $birth_year})
            MERGE (e)-[:BORN_IN_YEAR]->(y)
            """,
            **params,
            birth_year=birth_year,
        )
    if death_year is not None:
        session.run(
            match_clause + """
            MERGE (y:Year {year: $death_year})
            MERGE (e)-[:DIED_IN_YEAR]->(y)
            """,
            **params,
            death_year=death_year,
        )
    if birth_date or death_date:
        set_parts = []
        if birth_date:
            set_parts.append("e.birth_date = $birth_date")
        if death_date:
            set_parts.append("e.death_date = $death_date")
        if set_parts:
            session.run(
                match_clause + " SET " + ", ".join(set_parts),
                **params,
                birth_date=birth_date,
                death_date=death_date,
            )


def _ensure_father_of(session, child_qid: str, father_qid: str, dry_run: bool, stats: dict):
    """Create (father)-[:FATHER_OF]->(child)."""
    if dry_run:
        return
    session.run("""
        MERGE (f:Entity {qid: $father_qid})
        ON CREATE SET f.entity_id = $f_entity_id, f.entity_cipher = $f_cipher, f.label = '', f.entity_type = 'PERSON'
        MERGE (c:Entity {qid: $child_qid})
        MERGE (f)-[:FATHER_OF]->(c)
    """, father_qid=father_qid, f_entity_id=f"person_q{father_qid[1:].lower()}" if father_qid.startswith("Q") else f"person_q{father_qid}", f_cipher=f"ent_per_{father_qid}", child_qid=child_qid)
    stats["created"] += 1


def _ensure_mother_of(session, child_qid: str, mother_qid: str, dry_run: bool, stats: dict):
    """Create (mother)-[:MOTHER_OF]->(child)."""
    if dry_run:
        return
    session.run("""
        MERGE (m:Entity {qid: $mother_qid})
        ON CREATE SET m.entity_id = $m_entity_id, m.entity_cipher = $m_cipher, m.label = '', m.entity_type = 'PERSON'
        MERGE (c:Entity {qid: $child_qid})
        MERGE (m)-[:MOTHER_OF]->(c)
    """, mother_qid=mother_qid, m_entity_id=f"person_q{mother_qid[1:].lower()}" if mother_qid.startswith("Q") else f"person_q{mother_qid}", m_cipher=f"ent_per_{mother_qid}", child_qid=child_qid)
    stats["created"] += 1


def _ensure_sibling_of(session, qid_a: str, qid_b: str, dry_run: bool, stats: dict):
    """Create (a)-[:SIBLING_OF]-(b). Symmetric; MERGE avoids duplicates."""
    if dry_run or qid_a == qid_b:
        return
    session.run("""
        MERGE (a:Entity {qid: $qid_a})
        ON CREATE SET a.entity_id = $a_entity_id, a.entity_cipher = $a_cipher, a.label = '', a.entity_type = 'PERSON'
        MERGE (b:Entity {qid: $qid_b})
        ON CREATE SET b.entity_id = $b_entity_id, b.entity_cipher = $b_cipher, b.label = '', b.entity_type = 'PERSON'
        MERGE (a)-[:SIBLING_OF]-(b)
    """,
        qid_a=qid_a, qid_b=qid_b,
        a_entity_id=f"person_q{qid_a[1:].lower()}" if qid_a.startswith("Q") else f"person_q{qid_a}",
        a_cipher=f"ent_per_{qid_a}",
        b_entity_id=f"person_q{qid_b[1:].lower()}" if qid_b.startswith("Q") else f"person_q{qid_b}",
        b_cipher=f"ent_per_{qid_b}",
    )
    stats["created"] += 1


def _ensure_spouse_of(session, qid_a: str, qid_b: str, dry_run: bool, stats: dict):
    """Create (a)-[:SPOUSE_OF]-(b). Symmetric; MERGE avoids duplicates."""
    if dry_run or qid_a == qid_b:
        return
    session.run("""
        MERGE (a:Entity {qid: $qid_a})
        ON CREATE SET a.entity_id = $a_entity_id, a.entity_cipher = $a_cipher, a.label = '', a.entity_type = 'PERSON'
        MERGE (b:Entity {qid: $qid_b})
        ON CREATE SET b.entity_id = $b_entity_id, b.entity_cipher = $b_cipher, b.label = '', b.entity_type = 'PERSON'
        MERGE (a)-[:SPOUSE_OF]-(b)
    """,
        qid_a=qid_a, qid_b=qid_b,
        a_entity_id=f"person_q{qid_a[1:].lower()}" if qid_a.startswith("Q") else f"person_q{qid_a}",
        a_cipher=f"ent_per_{qid_a}",
        b_entity_id=f"person_q{qid_b[1:].lower()}" if qid_b.startswith("Q") else f"person_q{qid_b}",
        b_cipher=f"ent_per_{qid_b}",
    )
    stats["created"] += 1
