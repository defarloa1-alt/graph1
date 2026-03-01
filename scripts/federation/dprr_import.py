#!/usr/bin/env python3
"""
DPRR Federation Import

Imports persons, offices (PostAssertions), relationships (RelationshipAssertions),
and status (StatusAssertions) from the Digital Prosopography of the Roman Republic.

Alignment: Wikidata P6863 provides dprr_id -> qid mapping (3,018 aligned).
Group A: P6863-aligned -> MERGE onto existing QID nodes
Group C: No alignment -> CREATE new nodes with dprr_uri as primary id

Reification: Option A (edge provenance) per docs/IMPORT_DECISIONS.md

Usage:
    python scripts/federation/dprr_import.py --dry-run
    python scripts/federation/dprr_import.py --limit-persons 500
    python scripts/federation/dprr_import.py  # full import
    python scripts/federation/dprr_import.py --status-assertions  # Group A status only
    python scripts/federation/dprr_import.py --group-c-posts    # Group C POSITION_HELD + status via dprr_uri
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

_scripts = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_scripts))
try:
    from config_loader import (
        NEO4J_URI,
        NEO4J_USERNAME,
        NEO4J_PASSWORD,
        NEO4J_DATABASE,
        WIKIDATA_SPARQL_ENDPOINT,
    )
    from tools.entity_cipher import generate_entity_cipher
except ImportError:
    NEO4J_URI = NEO4J_USERNAME = NEO4J_PASSWORD = NEO4J_DATABASE = None
    WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
    generate_entity_cipher = None

DPRR_ENDPOINT = "http://romanrepublic.ac.uk/rdf/endpoint/"
DPRR_ONTOLOGY = "http://romanrepublic.ac.uk/rdf/ontology#"
USER_AGENT = "Chrystallum/1.0 (DPRR federation import)"
PAGE_SIZE = 500

# DPRR relationship label -> (canonical_type, swap_subject_object)
# swap=True: DPRR stores (child, parent, "son of") -> we create parent --FATHER_OF--> child
DPRR_REL_MAP = {
    "father of": ("FATHER_OF", False),
    "mother of": ("MOTHER_OF", False),
    "son of": ("FATHER_OF", True),
    "daughter of": ("MOTHER_OF", True),
    "brother of": ("SIBLING_OF", False),
    "sister of": ("SIBLING_OF", False),
    "married to": ("SPOUSE_OF", False),
    "divorced from": ("SPOUSE_OF", False),  # or separate DIVORCED_FROM if added
    "grandfather of": ("FATHER_OF", True),  # person2 is grandson, person1 is grandfather -> person1 ancestor of person2
    "grandson of": ("FATHER_OF", True),
    "grandmother of": ("MOTHER_OF", True),
    "granddaughter of": ("MOTHER_OF", True),
    "related to": ("SIBLING_OF", False),  # fallback to SIBLING for "related to"
    "adopted son of": ("FATHER_OF", True),
    "adoptive father of": ("FATHER_OF", False),
    "nephew of": ("SIBLING_OF", False),  # uncle --SIBLING_OF--> parent, nephew is child; approximate
    "uncle of": ("SIBLING_OF", True),
    "cousin of": ("SIBLING_OF", False),
    "betrothed to": ("SPOUSE_OF", False),
    "great grandfather of": ("FATHER_OF", True),
    "stepbrother of": ("SIBLING_OF", False),
    "great grandson of": ("FATHER_OF", True),
    "stepfather of": ("FATHER_OF", False),
    "stepson of": ("FATHER_OF", True),
    "adoptive brother of": ("SIBLING_OF", False),
    "halfbrother of": ("SIBLING_OF", False),
    "halfsister of": ("SIBLING_OF", False),
    "stepsister of": ("SIBLING_OF", False),
    "adoptive mother of": ("MOTHER_OF", False),
    "aunt of": ("SIBLING_OF", True),
    "niece of": ("SIBLING_OF", False),
    "great uncle of": ("SIBLING_OF", True),
    "great nephew of": ("SIBLING_OF", False),
    "adoptive grandfather": ("FATHER_OF", False),
    "adopted grandson of": ("FATHER_OF", True),
    "great granddaughter of": ("MOTHER_OF", True),
}


def _extract_id(uri: str) -> str | None:
    if not uri:
        return None
    m = re.search(r"/(\d+)$", uri)
    return m.group(1) if m else None


def _query_dprr(sparql: str, timeout: int = 60) -> list[dict]:
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    r = requests.get(DPRR_ENDPOINT, params={"query": sparql}, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json().get("results", {}).get("bindings", [])


def _query_wikidata(sparql: str, timeout: int = 60) -> list[dict]:
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    r = requests.get(WIKIDATA_SPARQL_ENDPOINT, params={"query": sparql}, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json().get("results", {}).get("bindings", [])


# ---------------------------------------------------------------------------
# Phase 0: Wikidata P6863 alignment
# ---------------------------------------------------------------------------
def fetch_wikidata_p6863_alignment() -> dict[str, str]:
    """Returns {dprr_id: qid}."""
    print("[Phase 0] Fetching Wikidata P6863 alignment...")
    sparql = """
    SELECT ?item ?dprrId WHERE {
      ?item wdt:P6863 ?dprrId .
    }
    """
    rows = _query_wikidata(sparql)
    mapping = {}
    for b in rows:
        item = b.get("item", {}).get("value", "")
        qid = item.split("/")[-1] if "/" in item else item
        dprr_id = b.get("dprrId", {}).get("value", "")
        if dprr_id and qid:
            mapping[str(dprr_id)] = qid
    print(f"  Aligned {len(mapping)} DPRR persons to Wikidata QIDs")
    return mapping


# ---------------------------------------------------------------------------
# Phase 1: Fetch DPRR persons
# ---------------------------------------------------------------------------
def fetch_persons(limit: int = 5000, offset: int = 0) -> list[dict]:
    sparql = f"""
    PREFIX vocab: <{DPRR_ONTOLOGY}>
    SELECT ?person ?name ?cognomen WHERE {{
      ?person a vocab:Person .
      OPTIONAL {{ ?person vocab:hasName ?name }}
      OPTIONAL {{ ?person vocab:hasCognomen ?cognomen }}
    }}
    ORDER BY ?person
    LIMIT {limit}
    OFFSET {offset}
    """
    rows = _query_dprr(sparql)
    out = []
    for r in rows:
        uri = r.get("person", {}).get("value", "")
        dprr_id = _extract_id(uri)
        name = r.get("name", {}).get("value", "") if r.get("name") else ""
        cognomen = r.get("cognomen", {}).get("value", "") if r.get("cognomen") else ""
        # Use hasName (full display) as label; fallback to cognomen or dprr_id
        label = name or cognomen or str(dprr_id)
        out.append({
            "dprr_id": dprr_id,
            "dprr_uri": uri,
            "label": label,
            "cognomen": cognomen,
        })
    return out


# ---------------------------------------------------------------------------
# Phase 2: Fetch PostAssertions
# ---------------------------------------------------------------------------
def fetch_post_assertions(limit: int = 15000, offset: int = 0) -> list[dict]:
    sparql = f"""
    PREFIX vocab: <{DPRR_ONTOLOGY}>
    SELECT ?post ?person ?office ?year WHERE {{
      ?post a vocab:PostAssertion ;
            vocab:isAboutPerson ?person ;
            vocab:hasOffice ?office .
      OPTIONAL {{ ?post vocab:inYear ?year }}
    }}
    ORDER BY ?person
    LIMIT {limit}
    OFFSET {offset}
    """
    rows = _query_dprr(sparql)
    out = []
    for r in rows:
        post_uri = r.get("post", {}).get("value", "")
        person_uri = r.get("person", {}).get("value", "")
        office_uri = r.get("office", {}).get("value", "")
        office_label = office_uri.split("/")[-1] if office_uri else ""
        year = r.get("year", {}).get("value", "") if r.get("year") else ""
        out.append({
            "post_uri": post_uri,
            "person_id": _extract_id(person_uri),
            "office_id": _extract_id(office_uri),
            "office_label": office_label,
            "year": year,
        })
    return out


# ---------------------------------------------------------------------------
# Phase 3: Fetch RelationshipAssertions
# ---------------------------------------------------------------------------
def fetch_all_relationship_labels() -> list[tuple[str, int]]:
    """Fetch full DPRR relationship vocabulary with counts. For coverage check."""
    sparql = f"""
    PREFIX vocab: <{DPRR_ONTOLOGY}>
    SELECT ?name (COUNT(?rel) AS ?count) WHERE {{
      ?rel a vocab:RelationshipAssertion ;
           vocab:hasRelationship ?relType .
      ?relType vocab:hasName ?name .
    }}
    GROUP BY ?name
    ORDER BY DESC(?count)
    """
    rows = _query_dprr(sparql)
    return [(r.get("name", {}).get("value", "").lower(), int(r.get("count", {}).get("value", 0))) for r in rows if r.get("name")]


def fetch_relationship_assertions(limit: int = 10000, offset: int = 0) -> list[dict]:
    sparql = f"""
    PREFIX vocab: <{DPRR_ONTOLOGY}>
    SELECT ?rel ?person1 ?person2 ?relType ?name WHERE {{
      ?rel a vocab:RelationshipAssertion ;
           vocab:isAboutPerson ?person1 ;
           vocab:hasRelatedPerson ?person2 ;
           vocab:hasRelationship ?relType .
      OPTIONAL {{ ?relType vocab:hasName ?name }}
    }}
    ORDER BY ?rel
    LIMIT {limit}
    OFFSET {offset}
    """
    rows = _query_dprr(sparql)
    out = []
    for r in rows:
        rel_uri = r.get("rel", {}).get("value", "")
        p1 = r.get("person1", {}).get("value", "")
        p2 = r.get("person2", {}).get("value", "")
        name = r.get("name", {}).get("value", "") if r.get("name") else ""
        out.append({
            "rel_uri": rel_uri,
            "person1_id": _extract_id(p1),
            "person2_id": _extract_id(p2),
            "relationship_label": name.lower() if name else "",
        })
    return out


# ---------------------------------------------------------------------------
# Phase 4: Fetch StatusAssertions
# ---------------------------------------------------------------------------
def fetch_status_assertions(limit: int = 3000, offset: int = 0) -> list[dict]:
    sparql = f"""
    PREFIX vocab: <{DPRR_ONTOLOGY}>
    SELECT ?status ?person ?statusType ?year WHERE {{
      ?status a vocab:StatusAssertion ;
              vocab:isAboutPerson ?person ;
              vocab:hasStatus ?statusType .
      OPTIONAL {{ ?status vocab:inYear ?year }}
    }}
    ORDER BY ?person
    LIMIT {limit}
    OFFSET {offset}
    """
    rows = _query_dprr(sparql)
    out = []
    for r in rows:
        status_uri = r.get("status", {}).get("value", "")
        person_uri = r.get("person", {}).get("value", "")
        st_uri = r.get("statusType", {}).get("value", "")
        st_label = st_uri.split("/")[-1] if st_uri else ""
        year = r.get("year", {}).get("value", "") if r.get("year") else ""
        out.append({
            "status_uri": status_uri,
            "person_id": _extract_id(person_uri),
            "status_label": st_label,
            "year": year,
        })
    return out


# ---------------------------------------------------------------------------
# Phase 5: Neo4j import (stub for dry-run; full impl requires driver)
# ---------------------------------------------------------------------------
def check_relationship_mapping(rels: list[dict] | None = None, verbose: bool = False) -> tuple[list[str], int]:
    """
    Check DPRR relationship labels against mapping. Returns (unmapped_labels, unmapped_count).
    If rels is None, fetches full vocabulary from endpoint.
    """
    if rels is not None:
        labels_with_count: dict[str, int] = {}
        for r in rels:
            lbl = (r.get("relationship_label") or "").strip().lower()
            if lbl:
                labels_with_count[lbl] = labels_with_count.get(lbl, 0) + 1
    else:
        labels_with_count = dict(fetch_all_relationship_labels())
    unmapped = []
    unmapped_count = 0
    for lbl, cnt in labels_with_count.items():
        if lbl and lbl not in DPRR_REL_MAP:
            unmapped.append(lbl)
            unmapped_count += cnt
    if verbose and unmapped:
        print("\n  Unmapped relationship labels (add to DPRR_REL_MAP before full run):")
        for lbl in sorted(unmapped):
            print(f"    - {lbl!r}")
        print(f"  Total unmapped assertions: {unmapped_count}")
    return unmapped, unmapped_count


def run_neo4j_import(
    alignment: dict[str, str],
    persons: list[dict],
    posts: list[dict],
    rels: list[dict],
    statuses: list[dict],
    dry_run: bool,
    unmapped_rel_count: int = 0,
    status_only: bool = False,
) -> dict:
    """Import to Neo4j. Returns stats dict."""
    if dry_run:
        if status_only:
            person_by_id = {str(p.get("dprr_id", "")): p for p in persons if p.get("dprr_id")}
            statuses_with_qid = sum(1 for s in statuses if person_by_id.get(str(s.get("person_id", "")), {}).get("qid"))
            return {"statuses_imported": statuses_with_qid, "statuses_skipped_no_qid": len(statuses) - statuses_with_qid, "dry_run": True}
        group_a = sum(1 for p in persons if p.get("qid"))
        group_c = len(persons) - group_a
        return {
            "group_a_merged": group_a,
            "group_c_created": group_c,
            "posts_imported": len(posts),
            "rels_imported": len(rels),
            "rels_skipped_unmapped": unmapped_rel_count,
            "statuses_imported": len(statuses),
            "dry_run": True,
        }

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("  neo4j package required for --write. pip install neo4j")
        return {"error": "neo4j not installed"}

    if not NEO4J_URI or not NEO4J_PASSWORD:
        print("  NEO4J_URI and NEO4J_PASSWORD required. Set in .env")
        return {"error": "Neo4j not configured"}

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD))
    stats = {"group_a_merged": 0, "group_c_created": 0, "posts_imported": 0, "rels_imported": 0, "rels_skipped_unmapped": 0, "statuses_imported": 0, "statuses_skipped_no_qid": 0}

    with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
        if status_only:
            person_by_id = {str(p.get("dprr_id", "")): p for p in persons if p.get("dprr_id")}
            for s in statuses:
                pid = str(s.get("person_id", ""))
                p = person_by_id.get(pid, {})
                qid = p.get("qid", "") or alignment.get(pid, "")
                if not qid:
                    stats["statuses_skipped_no_qid"] += 1
                    continue
                label = s.get("status_label", "unknown")
                year = s.get("year")
                uri = s.get("status_uri", "")
                session.run(
                    """
                    MATCH (e:Entity {qid: $qid})
                    MERGE (st:StatusType {label: $label})
                    MERGE (e)-[r:HAS_STATUS]->(st)
                    ON CREATE SET r.year = $year, r.source_uri = $uri
                    ON MATCH SET r.year = coalesce(r.year, $year), r.source_uri = coalesce(r.source_uri, $uri)
                    """,
                    qid=qid,
                    label=label,
                    year=year,
                    uri=uri or "",
                )
                stats["statuses_imported"] += 1
            driver.close()
            return stats

        # Ensure bibliography sources exist
        session.run("""
            MERGE (d:BibliographySource {id: "DPRR"})
            SET d.label = "Digital Prosopography of the Roman Republic",
                d.uri = "http://romanrepublic.ac.uk"
            MERGE (b:BibliographySource {id: "Broughton_MRR"})
            MERGE (z:BibliographySource {id: "Zmeskal_Adfinitas"})
        """)

        person_by_id = {p["dprr_id"]: p for p in persons if p.get("dprr_id")}
        for p in persons:
            dprr_id = p.get("dprr_id")
            qid = alignment.get(str(dprr_id)) if dprr_id else None
            label = p.get("label", "").replace("\\", "\\\\").replace("'", "\\'")
            if qid:
                entity_id = f"person_q{qid[1:].lower()}"
                entity_cipher = generate_entity_cipher(qid, "PERSON", "wd") if generate_entity_cipher else f"ent_per_{qid}"
                session.run("""
                    MERGE (e:Entity {qid: $qid})
                    SET e.entity_id = COALESCE(e.entity_id, $entity_id),
                        e.entity_cipher = COALESCE(e.entity_cipher, $entity_cipher),
                        e.label = $label,
                        e.entity_type = COALESCE(e.entity_type, 'PERSON'),
                        e.dprr_id = $dprr_id,
                        e.dprr_uri = $dprr_uri,
                        e.dprr_imported = true,
                        e.scoping_status = 'temporal_scoped',
                        e.scoping_confidence = 0.85,
                        e.scoping_source = 'DPRR'
                """, {"qid": qid, "entity_id": entity_id, "entity_cipher": entity_cipher, "label": label, "dprr_id": str(dprr_id), "dprr_uri": p.get("dprr_uri", "")})
                stats["group_a_merged"] += 1
            else:
                entity_id = f"person_dprr_{dprr_id}"
                entity_cipher = generate_entity_cipher(f"dprr_{dprr_id}", "PERSON", "dprr") if generate_entity_cipher else f"ent_per_dprr_{dprr_id}"
                session.run("""
                    MERGE (e:Entity {dprr_uri: $dprr_uri})
                    SET e.entity_id = $entity_id,
                        e.entity_cipher = $entity_cipher,
                        e.label = $label,
                        e.entity_type = 'PERSON',
                        e.dprr_id = $dprr_id,
                        e.dprr_imported = true,
                        e.scoping_status = 'temporal_scoped',
                        e.scoping_confidence = 0.85,
                        e.scoping_source = 'DPRR',
                        e.source = 'dprr'
                """, {"dprr_uri": p.get("dprr_uri", ""), "entity_id": entity_id, "entity_cipher": entity_cipher, "label": label, "dprr_id": str(dprr_id)})
                stats["group_c_created"] += 1

        # PostAssertions -> POSITION_HELD
        for post in posts:
            pid = post.get("person_id")
            qid = alignment.get(str(pid)) if pid else None
            if not qid:
                continue
            office = post.get("office_label", "office")
            year = post.get("year", "")
            session.run("""
                MATCH (e:Entity {qid: $qid})
                MERGE (o:Position {label: $office})
                ON CREATE SET o.office_uri = 'http://romanrepublic.ac.uk/rdf/office/' + $office,
                              o.source = 'dprr'
                MERGE (e)-[r:POSITION_HELD]->(o)
                SET r.dprr_assertion_uri = $uri,
                    r.secondary_source = 'Broughton_MRR',
                    r.year = $year,
                    r.source = 'dprr'
            """, {"qid": qid, "office": office, "uri": post.get("post_uri", ""), "year": year})
            stats["posts_imported"] += 1

        # RelationshipAssertions — match by qid or dprr_uri for Group C
        person_by_id = {str(p.get("dprr_id")): p for p in persons if p.get("dprr_id")}
        for rel in rels:
            p1_id, p2_id = str(rel.get("person1_id", "")), str(rel.get("person2_id", ""))
            p1 = person_by_id.get(p1_id, {})
            p2 = person_by_id.get(p2_id, {})
            q1 = p1.get("qid") or alignment.get(p1_id)
            q2 = p2.get("qid") or alignment.get(p2_id)
            uri1 = p1.get("dprr_uri") if not q1 else None
            uri2 = p2.get("dprr_uri") if not q2 else None
            if (not q1 and not uri1) or (not q2 and not uri2):
                continue
            label = rel.get("relationship_label", "")
            canonical, swap = DPRR_REL_MAP.get(label, (None, False))
            if not canonical:
                stats["rels_skipped_unmapped"] += 1
                continue
            if swap:
                q1, q2, uri1, uri2 = q2, q1, uri2, uri1
            # Match a,b by qid or dprr_uri
            where_a = "a.qid = $q1" if q1 else "a.dprr_uri = $uri1"
            where_b = "b.qid = $q2" if q2 else "b.dprr_uri = $uri2"
            session.run(f"""
                MATCH (a:Entity) WHERE {where_a}
                MATCH (b:Entity) WHERE {where_b}
                MERGE (a)-[r:{canonical}]->(b)
                SET r.dprr_assertion_uri = $uri,
                    r.secondary_source = 'Zmeskal_Adfinitas',
                    r.source = 'dprr'
            """, {"q1": q1 or "", "q2": q2 or "", "uri1": uri1 or "", "uri2": uri2 or "", "uri": rel.get("rel_uri", "")})
            stats["rels_imported"] += 1

        # StatusAssertions -> HAS_STATUS
        person_by_id = {str(p.get("dprr_id")): p for p in persons if p.get("dprr_id")}
        for s in statuses:
            pid = str(s.get("person_id", ""))
            p = person_by_id.get(pid, {})
            qid = p.get("qid") or alignment.get(pid, "")
            if not qid:
                continue
            label = s.get("status_label", "unknown")
            year = s.get("year")
            uri = s.get("status_uri", "")
            session.run(
                """
                MATCH (e:Entity {qid: $qid})
                MERGE (st:StatusType {label: $label})
                MERGE (e)-[r:HAS_STATUS]->(st)
                ON CREATE SET r.year = $year, r.source_uri = $uri
                ON MATCH SET r.year = coalesce(r.year, $year), r.source_uri = coalesce(r.source_uri, $uri)
                """,
                qid=qid,
                label=label,
                year=year,
                uri=uri or "",
            )
            stats["statuses_imported"] += 1

    driver.close()
    return stats


def run_neo4j_import_group_c_posts(
    persons: list[dict],
    posts: list[dict],
    statuses: list[dict],
    dry_run: bool,
) -> dict:
    """Import Group C POSITION_HELD and HAS_STATUS only. Match by dprr_uri."""
    group_c_ids = {str(p.get("dprr_id", "")) for p in persons if p.get("dprr_id") and not p.get("qid")}
    person_by_id = {str(p.get("dprr_id", "")): p for p in persons if p.get("dprr_id")}
    posts_group_c = [p for p in posts if str(p.get("person_id", "")) in group_c_ids]
    statuses_group_c = [s for s in statuses if str(s.get("person_id", "")) in group_c_ids]

    if dry_run:
        return {
            "group_c_persons": len(group_c_ids),
            "posts_fetched_group_c": len(posts_group_c),
            "statuses_fetched_group_c": len(statuses_group_c),
            "dry_run": True,
        }

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("  neo4j package required. pip install neo4j")
        return {"error": "neo4j not installed"}

    if not NEO4J_URI or not NEO4J_PASSWORD:
        print("  NEO4J_URI and NEO4J_PASSWORD required. Set in .env")
        return {"error": "Neo4j not configured"}

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD))
    stats = {
        "group_c_persons": len(group_c_ids),
        "posts_fetched_group_c": len(posts_group_c),
        "statuses_fetched_group_c": len(statuses_group_c),
        "posts_imported": 0,
        "posts_skipped_no_entity": 0,
        "statuses_imported": 0,
        "statuses_skipped_no_entity": 0,
        "position_nodes_before": 0,
        "position_nodes_after": 0,
    }

    with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
        # Position count before (for delta)
        r = session.run("MATCH (o:Position) RETURN count(o) as c")
        stats["position_nodes_before"] = r.single().get("c", 0) or 0
        for post in posts_group_c:
            pid = str(post.get("person_id", ""))
            p = person_by_id.get(pid, {})
            dprr_uri = p.get("dprr_uri", "")
            if not dprr_uri:
                stats["posts_skipped_no_entity"] += 1
                continue
            office = post.get("office_label", "office")
            year = post.get("year", "")
            result = session.run(
                """
                MATCH (e:Entity {dprr_uri: $dprr_uri})
                MERGE (o:Position {label: $office})
                ON CREATE SET o.office_uri = 'http://romanrepublic.ac.uk/rdf/office/' + $office,
                              o.source = 'dprr'
                MERGE (e)-[r:POSITION_HELD]->(o)
                SET r.dprr_assertion_uri = $uri,
                    r.secondary_source = 'Broughton_MRR',
                    r.year = $year,
                    r.source = 'dprr'
                RETURN 1 as ok
                """,
                dprr_uri=dprr_uri,
                office=office,
                uri=post.get("post_uri", ""),
                year=year,
            )
            if result.single():
                stats["posts_imported"] += 1
            else:
                stats["posts_skipped_no_entity"] += 1

        for s in statuses_group_c:
            pid = str(s.get("person_id", ""))
            p = person_by_id.get(pid, {})
            dprr_uri = p.get("dprr_uri", "")
            if not dprr_uri:
                stats["statuses_skipped_no_entity"] += 1
                continue
            label = s.get("status_label", "unknown")
            year = s.get("year")
            uri = s.get("status_uri", "")
            result = session.run(
                """
                MATCH (e:Entity {dprr_uri: $dprr_uri})
                MERGE (st:StatusType {label: $label})
                MERGE (e)-[r:HAS_STATUS]->(st)
                ON CREATE SET r.year = $year, r.source_uri = $uri
                ON MATCH SET r.year = coalesce(r.year, $year), r.source_uri = coalesce(r.source_uri, $uri)
                RETURN 1 as ok
                """,
                dprr_uri=dprr_uri,
                label=label,
                year=year,
                uri=uri or "",
            )
            if result.single():
                stats["statuses_imported"] += 1
            else:
                stats["statuses_skipped_no_entity"] += 1

        # Position count after (for delta)
        r = session.run("MATCH (o:Position) RETURN count(o) as c")
        stats["position_nodes_after"] = r.single().get("c", 0) or 0

    driver.close()
    return stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="DPRR federation import")
    ap.add_argument("--dry-run", action="store_true", help="Fetch data only, no Neo4j write")
    ap.add_argument("--limit-persons", type=int, default=5000, help="Max persons to fetch")
    ap.add_argument("--limit-posts", type=int, default=15000, help="Max PostAssertions")
    ap.add_argument("--limit-rels", type=int, default=10000, help="Max RelationshipAssertions")
    ap.add_argument("--limit-statuses", type=int, default=3000, help="Max StatusAssertions")
    ap.add_argument("--output", default="output/federation/dprr_import_report.json", help="Report path")
    ap.add_argument("--verbose", "-v", action="store_true", help="Print unmapped relationship labels")
    ap.add_argument("--check-relationship-types", action="store_true", help="Verify full DPRR vocabulary against mapping")
    ap.add_argument("--status-assertions", action="store_true", help="Import only StatusAssertions (fetch persons for matching)")
    ap.add_argument("--group-c-posts", action="store_true", help="Import Group C POSITION_HELD + status via dprr_uri (694 status re-attempt)")
    args = ap.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("DPRR FEDERATION IMPORT")
    print("=" * 70)

    alignment = fetch_wikidata_p6863_alignment()

    if args.group_c_posts:
        # Group C POSITION_HELD + status assertions via dprr_uri
        print("[Group C] Fetching persons for matching...")
        persons = fetch_persons(limit=args.limit_persons)
        for p in persons:
            p["qid"] = alignment.get(str(p.get("dprr_id", "")), "")
        group_c_count = sum(1 for p in persons if p.get("dprr_id") and not p.get("qid"))
        print(f"  Fetched {len(persons)} persons ({group_c_count} Group C)")
        print("[Group C] Fetching PostAssertions...")
        posts = fetch_post_assertions(limit=args.limit_posts)
        print(f"  Fetched {len(posts)} post assertions")
        print("[Group C] Fetching StatusAssertions...")
        statuses = fetch_status_assertions(limit=args.limit_statuses)
        print(f"  Fetched {len(statuses)} status assertions")
        print("[Group C] Neo4j import (POSITION_HELD + HAS_STATUS via dprr_uri)...")
        stats = run_neo4j_import_group_c_posts(persons, posts, statuses, dry_run=args.dry_run)
        report = {"source": "DPRR", "mode": "group_c_posts", "import_stats": stats}
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print()
        print("=" * 70)
        print("GROUP C IMPORT COMPLETE")
        print("=" * 70)
        print(f"  Group C persons: {stats.get('group_c_persons', 0)}")
        print(f"  Posts fetched (Group C): {stats.get('posts_fetched_group_c', 0)}")
        print(f"  Posts imported: {stats.get('posts_imported', 0)}")
        print(f"  Posts skipped (no entity): {stats.get('posts_skipped_no_entity', 0)}")
        print(f"  Statuses fetched (Group C): {stats.get('statuses_fetched_group_c', 0)}")
        print(f"  Statuses imported: {stats.get('statuses_imported', 0)}")
        print(f"  Statuses skipped (no entity): {stats.get('statuses_skipped_no_entity', 0)}")
        ob, oa = stats.get("position_nodes_before", 0), stats.get("position_nodes_after", 0)
        if ob or oa:
            print(f"  Position nodes: {oa} (delta +{oa - ob})")
        print(f"  Report: {out_path}")
        return
    elif args.status_assertions:
        # Status-assertions-only mode
        print("[Status-only] Fetching persons for matching...")
        persons = fetch_persons(limit=args.limit_persons)
        for p in persons:
            p["qid"] = alignment.get(str(p.get("dprr_id", "")), "")
        print(f"  Fetched {len(persons)} persons")
        posts, rels = [], []
        unmapped_labels, unmapped_count = [], 0
        print("[Status-only] Fetching StatusAssertions...")
        statuses = fetch_status_assertions(limit=args.limit_statuses)
        print(f"  Fetched {len(statuses)} status assertions")
        print("[Status-only] Neo4j import (status assertions only)...")
        stats = run_neo4j_import(alignment, persons, posts, rels, statuses, dry_run=args.dry_run, unmapped_rel_count=0, status_only=True)
    else:
        print("[Phase 1] Fetching DPRR persons...")
        persons = fetch_persons(limit=args.limit_persons)
        for p in persons:
            p["qid"] = alignment.get(str(p.get("dprr_id", "")), "")
        print(f"  Fetched {len(persons)} persons")

        print("[Phase 2] Fetching PostAssertions...")
        posts = fetch_post_assertions(limit=args.limit_posts)
        print(f"  Fetched {len(posts)} post assertions")

        print("[Phase 3] Fetching RelationshipAssertions...")
        rels = fetch_relationship_assertions(limit=args.limit_rels)
        print(f"  Fetched {len(rels)} relationship assertions")

        # Relationship mapping completeness check
        rels_for_check = None if args.check_relationship_types else rels
        unmapped_labels, unmapped_count = check_relationship_mapping(rels_for_check, verbose=args.verbose)
        if args.check_relationship_types:
            print("\n[Check] Full DPRR relationship vocabulary vs mapping:")
            if unmapped_labels:
                print(f"  Unmapped: {len(unmapped_labels)} types, {unmapped_count} assertions")
                if args.verbose:
                    for lbl in sorted(unmapped_labels):
                        print(f"    - {lbl!r}")
            else:
                print("  All relationship types mapped.")

        print("[Phase 4] Fetching StatusAssertions...")
        statuses = fetch_status_assertions(limit=args.limit_statuses)
        print(f"  Fetched {len(statuses)} status assertions")

        print("[Phase 5] Neo4j import...")
        stats = run_neo4j_import(alignment, persons, posts, rels, statuses, dry_run=args.dry_run, unmapped_rel_count=unmapped_count)

    report = {
        "source": "DPRR",
        "alignment_count": len(alignment),
        "persons_fetched": len(persons),
        "posts_fetched": len(posts),
        "rels_fetched": len(rels),
        "statuses_fetched": len(statuses),
        "unmapped_rel_labels": unmapped_labels,
        "unmapped_rel_count": unmapped_count,
        "import_stats": stats,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print()
    print("=" * 70)
    print("IMPORT COMPLETE")
    print("=" * 70)
    print(f"  Group A (merged): {stats.get('group_a_merged', 0)}")
    print(f"  Group C (created): {stats.get('group_c_created', 0)}")
    print(f"  Posts: {stats.get('posts_imported', 0)}")
    print(f"  Relationships: {stats.get('rels_imported', 0)}")
    if stats.get("rels_skipped_unmapped", 0):
        print(f"  Rels skipped (unmapped): {stats['rels_skipped_unmapped']}")
    print(f"  Statuses: {stats.get('statuses_imported', 0)}")
    if stats.get("statuses_skipped_no_qid", 0):
        print(f"  Statuses skipped (no qid): {stats['statuses_skipped_no_qid']}")
    print(f"  Report: {out_path}")
    if unmapped_labels:
        print(f"\n  WARNING: {len(unmapped_labels)} unmapped relationship types ({unmapped_count} assertions skipped)")


if __name__ == "__main__":
    main()
