#!/usr/bin/env python3
"""
cluster_assignment.py
---------------------
Reads harvest reports + harvest_run_summary.json and creates
(entity)-[:MEMBER_OF]->(SubjectConcept) edges.

Assignment rule: anchor-based
  Entity harvested from anchor QID Q105427
  -> Q105427 maps to ["subj_rr_gov_institutions", "subj_rr_gov_senate"]
  -> Entity gets MEMBER_OF edge to BOTH SubjectConcepts

Multiplicity: one entity can belong to multiple SubjectConcepts.

Output modes (choose one or both):
  --cypher    Write a .cypher file for inspection / manual import
  --write     Write directly to Neo4j Aura via driver

Usage:
    # Cypher file only (safe, inspect before committing)
    python scripts/backbone/subject/cluster_assignment.py \\
        --harvest-dir output/backlinks \\
        --summary output/backlinks/harvest_run_summary.json \\
        --output-dir output/cluster_assignment \\
        --cypher

    # Direct Aura write
    python scripts/backbone/subject/cluster_assignment.py \\
        --harvest-dir output/backlinks \\
        --summary output/backlinks/harvest_run_summary.json \\
        --output-dir output/cluster_assignment \\
        --write \\
        --neo4j-uri neo4j+s://YOUR_AURA_URI \\
        --neo4j-user neo4j \\
        --neo4j-password YOUR_PASSWORD

    # Both (generate Cypher AND write to Aura)
    python scripts/backbone/subject/cluster_assignment.py ... --cypher --write

    # Dry run (show what would be created, no output)
    python scripts/backbone/subject/cluster_assignment.py ... --dry-run

    # Include DPRR entities from Neo4j (assign to Q899409 Roman families)
    python scripts/backbone/subject/cluster_assignment.py ... --dprr-neo4j --write

Dependencies:
    pip install neo4j          # only needed for --write mode
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional

# Load Neo4j config from .env when available
try:
    _scripts = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(_scripts))
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
    try:
        from tools.entity_cipher import generate_entity_cipher
    except ImportError:
        generate_entity_cipher = None
except ImportError:
    NEO4J_URI = NEO4J_USERNAME = NEO4J_PASSWORD = NEO4J_DATABASE = None
    generate_entity_cipher = None


# ---------------------------------------------------------------------------
# Federation ID properties (Option B: separate properties per PID, D-022)
# ---------------------------------------------------------------------------
# PID -> Entity property name. Use federation names for legibility.
# D-023: LGPN is P1047, not P1838 (P1838 = PSS-archi building IDs).
FEDERATION_ID_PROPS = {
    "P1584": "pleiades_id",
    "P1696": "trismegistos_id",
    "P1047": "lgpn_id",  # LGPN (Lexicon of Greek Personal Names)
    "P214": "viaf_id",
    "P1014": "getty_aat_id",
    "P2192": "edh_id",
    "P9106": "ocd_id",
}
# All Entity federation props (WRITE_QUERY expects these; lgpn_id has no harvest source)
ALL_FED_PROPS = ["pleiades_id", "trismegistos_id", "lgpn_id", "viaf_id", "getty_aat_id", "edh_id", "ocd_id"]


def external_ids_to_props(ext: dict) -> dict[str, str]:
    """Map external_ids dict (PID -> value) to Entity property names. Returns only non-empty."""
    out = {}
    for pid, prop in FEDERATION_ID_PROPS.items():
        val = ext.get(pid)
        if val and str(val).strip():
            out[prop] = str(val).strip()
    return out


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MemberOfEdge:
    entity_qid: str
    entity_label: str
    subject_qid: str         # SubjectConcept identity (QID-canonical)
    anchor_qid: str         # the anchor QID that connects them
    confidence: float        # from facet classification if available, else 1.0
    primary_facet: str       # from facet classification if available, else ""
    source_report: str      # filename of the harvest report
    external_ids: dict = field(default_factory=dict)  # P1696, P1838, P1584 from harvest
    scoping_status: str = ""       # temporal_scoped, domain_scoped, unscoped (HARVESTER_SCOPING_DESIGN)
    scoping_confidence: float = 0.0  # 0.95, 0.85, 0.40 when scoping_status set
    entity_id: Optional[str] = None  # for DPRR Group C (no qid): person_dprr_{dprr_id}


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_summary(summary_path: Path) -> dict:
    with open(summary_path, encoding="utf-8") as f:
        return json.load(f)


def load_harvest_reports(harvest_dir: Path) -> dict[str, list[dict]]:
    """
    Returns {anchor_qid: [entity_records]} by parsing report filenames.
    Supports: {qid}_report.json (QID-canonical) or {subject_id}_{qid}_report.json (legacy)
    """
    reports: dict[str, list[dict]] = defaultdict(list)
    report_files = list(harvest_dir.glob("*_report.json"))

    if not report_files:
        print(f"[warn] No *_report.json files in {harvest_dir}", file=sys.stderr)
        return reports

    for report_path in report_files:
        # Extract anchor QID from filename
        # Format A: {qid}_report.json (QID-canonical)
        # Format B: {subject_id}_{qid}_report.json (legacy)
        # Format C: {qid}_backlink_harvest_report.json (harvester default)
        stem = report_path.stem.replace("_report", "").replace("_backlink_harvest", "")
        # Try QID-only first (Q1234567)
        if stem.startswith("Q") and stem[1:].replace("_", "").isdigit():
            anchor_qid = stem.split("_")[0] if "_" in stem else stem
        else:
            parts = stem.rsplit("_", 1)
            if len(parts) == 2 and parts[1].startswith("Q") and parts[1][1:].replace("_", "").isdigit():
                anchor_qid = parts[1]
            elif parts[0].startswith("Q"):
                anchor_qid = parts[0].split("_")[0]
            else:
                print(f"  [warn] Cannot parse QID from filename: {report_path.name}", file=sys.stderr)
                continue

        try:
            with open(report_path, encoding="utf-8") as f:
                report = json.load(f)

            accepted = report.get("accepted",
                       report.get("entities",
                       report.get("results", [])))

            for entity in accepted:
                qid = (entity.get("qid") or
                       entity.get("entity_qid") or
                       entity.get("id", ""))
                label = (entity.get("label") or
                         entity.get("entity_label", ""))
                if qid:
                    record = {
                        "entity_qid": qid,
                        "entity_label": label,
                        "source_report": report_path.name,
                    }
                    if "external_ids" in entity:
                        record["external_ids"] = entity["external_ids"]
                    if "scoping_status" in entity:
                        record["scoping_status"] = entity["scoping_status"]
                    if "scoping_confidence" in entity:
                        record["scoping_confidence"] = entity["scoping_confidence"]
                    if "ambiguous_category" in entity:
                        record["ambiguous_category"] = entity["ambiguous_category"]
                    reports[anchor_qid].append(record)

        except Exception as e:
            print(f"  [warn] Failed to load {report_path.name}: {e}", file=sys.stderr)

    return reports


def load_facet_classifications(facet_dir: Optional[Path]) -> dict[str, dict]:
    """
    Optional: load all_facet_classifications.json to enrich edges
    with confidence and primary_facet.
    Returns {entity_qid: {primary_facet, primary_confidence, ...}}
    """
    if not facet_dir:
        return {}

    all_path = facet_dir / "all_facet_classifications.json"
    if not all_path.exists():
        print(f"  [info] No facet classifications found at {all_path} - edges will have confidence=1.0")
        return {}

    with open(all_path, encoding="utf-8") as f:
        records = json.load(f)

    return {
        r["entity_qid"]: r
        for r in records
        if r.get("entity_qid")
    }


# DPRR (Digital Prosopography of the Roman Republic): Q899409 Roman families
DPRR_ANCHOR_QID = "Q899409"


def load_dprr_from_neo4j(
    uri: str,
    user: str,
    password: str,
    only_without_member_of: bool = True,
) -> list[dict]:
    """
    Query Neo4j for entities with dprr_imported=true.
    Returns entity records for cluster assignment (Q899409 Roman families).
    Group A: has qid. Group C: has entity_id (person_dprr_{id}), no qid.
    """
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("  [warn] neo4j driver not installed - skipping DPRR load", file=sys.stderr)
        return []

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        # D-032: DPRR scoping confidence from SYS_Threshold (same as scoping_confidence_temporal_med)
        with driver.session() as session:
            result = session.run(
                "MATCH (t:SYS_Threshold {name: 'scoping_confidence_temporal_med'}) "
                "RETURN t.value AS value"
            )
            record = result.single()
        dprr_confidence = float(record["value"]) if record and record.get("value") is not None else 0.85

        # Include both dprr_imported=true and dprr_id IS NOT NULL (legacy nodes may lack the flag)
        if only_without_member_of:
            q = """
            MATCH (e:Entity)
            WHERE (e.dprr_imported = true OR e.dprr_id IS NOT NULL)
              AND NOT EXISTS((e)-[:MEMBER_OF]->())
            RETURN e.qid AS qid, e.entity_id AS entity_id, e.dprr_uri AS dprr_uri,
                   coalesce(e.label, '') AS label
            """
        else:
            q = """
            MATCH (e:Entity)
            WHERE (e.dprr_imported = true OR e.dprr_id IS NOT NULL)
            RETURN e.qid AS qid, e.entity_id AS entity_id, e.dprr_uri AS dprr_uri,
                   coalesce(e.label, '') AS label
            """
        with driver.session() as session:
            result = session.run(q)
            rows = list(result)
    finally:
        driver.close()

    records = []
    for r in rows:
        qid = r.get("qid")
        entity_id = r.get("entity_id")
        dprr_uri = r.get("dprr_uri")
        label = r.get("label") or ""
        if qid:
            records.append({
                "entity_qid": qid,
                "entity_label": label,
                "source_report": "dprr_neo4j",
                "scoping_status": "temporal_scoped",
                "scoping_confidence": dprr_confidence,
            })
        elif entity_id:
            records.append({
                "entity_qid": "",
                "entity_id": entity_id,
                "entity_label": label,
                "source_report": "dprr_neo4j",
                "scoping_status": "temporal_scoped",
                "scoping_confidence": dprr_confidence,
            })
    return records


# ---------------------------------------------------------------------------
# Edge builder
# ---------------------------------------------------------------------------

def build_edges(
    qid_to_subject_ids: dict[str, list[str]],
    harvest_reports: dict[str, list[dict]],
    facet_classifications: dict[str, dict],
) -> list[MemberOfEdge]:
    """
    Core assignment logic:
      For each anchor QID in harvest reports:
        Look up which SubjectConcepts it maps to (from summary; QID-canonical: [anchor_qid])
        For each accepted entity under that anchor:
          Create one MEMBER_OF edge per SubjectConcept
    DPRR Group C: entity_qid empty, entity_id set (person_dprr_{id}).
    """
    edges: list[MemberOfEdge] = []
    seen: set[tuple[str, str]] = set()  # (entity_key, subject_qid) dedup; entity_key = qid or entity_id

    for anchor_qid, entities in harvest_reports.items():
        subject_qids = qid_to_subject_ids.get(anchor_qid, [])

        if not subject_qids:
            print(f"  [warn] Anchor {anchor_qid} has harvest data but no subject mapping - skipping")
            continue

        for entity in entities:
            entity_qid = entity.get("entity_qid", "")
            entity_id = entity.get("entity_id")
            entity_label = entity.get("entity_label", "")
            source_report = entity.get("source_report", "")

            # Enrich with facet classification if available (only for qid entities)
            facet_data = facet_classifications.get(entity_qid, {}) if entity_qid else {}
            confidence = facet_data.get("primary_confidence", 1.0)
            primary_facet = facet_data.get("primary_facet", "")

            for subject_qid in subject_qids:
                entity_key = entity_qid or (entity_id or "")
                key = (entity_key, subject_qid)
                if key in seen:
                    continue  # deduplicate within run
                seen.add(key)

                edges.append(MemberOfEdge(
                    entity_qid=entity_qid,
                    entity_label=entity_label,
                    subject_qid=subject_qid,
                    anchor_qid=anchor_qid,
                    confidence=confidence,
                    primary_facet=primary_facet,
                    source_report=source_report,
                    external_ids=entity.get("external_ids") or {},
                    scoping_status=entity.get("scoping_status", ""),
                    scoping_confidence=entity.get("scoping_confidence", 0.0),
                    entity_id=entity_id,
                ))

    return edges


# ---------------------------------------------------------------------------
# Cypher generation
# ---------------------------------------------------------------------------

CYPHER_HEADER = """\
// ============================================================
// MEMBER_OF edge creation - generated by cluster_assignment.py
// Generated: {generated_at}
// Total edges: {total_edges}
// Unique entities: {unique_entities}
// Unique SubjectConcepts: {unique_subjects}
//
// MERGE semantics: safe to re-run, will not create duplicates
// ============================================================

"""

CYPHER_BATCH_COMMENT = "// Batch {n} - anchor QID: {anchor_qid} -> SubjectConcept: {subject_qid}\n"

CYPHER_MERGE = """\
MERGE (e:Entity {{qid: '{entity_qid}'}})
  ON CREATE SET e.entity_id = '{entity_id}', e.entity_cipher = '{entity_cipher}', e.entity_type = 'CONCEPT', e.label = '{entity_label}'{fed_create_clauses}, e.created_at = datetime()
  ON MATCH SET  e.entity_id = coalesce(e.entity_id, '{entity_id}'),
                e.entity_cipher = coalesce(e.entity_cipher, '{entity_cipher}'),
                e.entity_type = coalesce(e.entity_type, 'CONCEPT'),
                e.label = coalesce(e.label, '{entity_label}'){fed_match_clauses}
WITH e
MATCH (sc:SubjectConcept {{qid: '{subject_qid}'}})
MERGE (e)-[r:MEMBER_OF]->(sc)
  ON CREATE SET
    r.anchor_qid         = '{anchor_qid}',
    r.confidence         = {confidence},
    r.primary_facet      = '{primary_facet}',
    r.scoping_status     = '{scoping_status}',
    r.scoping_confidence = {scoping_confidence},
    r.assigned_at        = datetime(),
    r.source             = 'cluster_assignment'
  ON MATCH SET
    r.confidence         = CASE WHEN {confidence} > r.confidence
                               THEN {confidence} ELSE r.confidence END,
    r.scoping_status     = CASE WHEN '{scoping_status}' <> ''
                               THEN '{scoping_status}' ELSE r.scoping_status END,
    r.scoping_confidence = CASE WHEN {scoping_confidence} > 0
                               THEN {scoping_confidence} ELSE r.scoping_confidence END;

"""

# DPRR Group C: match by entity_id (person_dprr_{id}), no qid
CYPHER_MERGE_DPRR = """\
MATCH (e:Entity {{entity_id: '{entity_id}'}})
MATCH (sc:SubjectConcept {{qid: '{subject_qid}'}})
MERGE (e)-[r:MEMBER_OF]->(sc)
  ON CREATE SET
    r.anchor_qid         = '{anchor_qid}',
    r.confidence         = {confidence},
    r.primary_facet      = '{primary_facet}',
    r.scoping_status     = '{scoping_status}',
    r.scoping_confidence = {scoping_confidence},
    r.assigned_at        = datetime(),
    r.source             = 'cluster_assignment'
  ON MATCH SET
    r.confidence         = CASE WHEN {confidence} > r.confidence
                               THEN {confidence} ELSE r.confidence END,
    r.scoping_status     = CASE WHEN '{scoping_status}' <> ''
                               THEN '{scoping_status}' ELSE r.scoping_status END,
    r.scoping_confidence = CASE WHEN {scoping_confidence} > 0
                               THEN {scoping_confidence} ELSE r.scoping_confidence END;

"""


def escape_cypher(s: str) -> str:
    """Escape single quotes for Cypher string literals."""
    return s.replace("'", "\\'").replace("\\", "\\\\")


def external_ids_to_cypher_map(ext: dict) -> str:
    """Format external_ids dict as Cypher map literal for Entity.external_ids (legacy)."""
    if not ext:
        return "{}"
    parts = [f"{k}: '{escape_cypher(str(v))}'" for k, v in ext.items()]
    return "{" + ", ".join(parts) + "}"


def external_ids_to_cypher_set_clauses(ext: dict, for_match: bool = False) -> str:
    """Build Cypher SET clauses for federation ID properties (D-022 Option B)."""
    props = external_ids_to_props(ext)
    if not props:
        return ""
    if for_match:
        parts = [f"e.{k} = coalesce(e.{k}, '{escape_cypher(v)}')" for k, v in props.items()]
    else:
        parts = [f"e.{k} = '{escape_cypher(v)}'" for k, v in props.items()]
    return ", " + ", ".join(parts)


def generate_cypher(edges: list[MemberOfEdge], output_path: Path):
    unique_entities = len({e.entity_qid or e.entity_id or "" for e in edges})
    unique_subjects = len({e.subject_qid for e in edges})

    header = CYPHER_HEADER.format(
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_edges=len(edges),
        unique_entities=unique_entities,
        unique_subjects=unique_subjects,
    )

    lines = [header]

    # Group by anchor_qid + subject_qid for readable batches
    by_anchor: dict[tuple[str, str], list[MemberOfEdge]] = defaultdict(list)
    for edge in edges:
        by_anchor[(edge.anchor_qid, edge.subject_qid)].append(edge)

    for n, ((anchor_qid, subject_qid), batch) in enumerate(by_anchor.items(), 1):
        lines.append(CYPHER_BATCH_COMMENT.format(
            n=n, anchor_qid=anchor_qid, subject_qid=subject_qid
        ))
        for edge in batch:
            scoping_status = edge.scoping_status or ""
            scoping_confidence = round(edge.scoping_confidence, 4)
            if edge.entity_id:
                # DPRR Group C: match by entity_id
                lines.append(CYPHER_MERGE_DPRR.format(
                    entity_id=escape_cypher(edge.entity_id),
                    subject_qid=escape_cypher(edge.subject_qid),
                    anchor_qid=escape_cypher(edge.anchor_qid),
                    confidence=round(edge.confidence, 4),
                    primary_facet=escape_cypher(edge.primary_facet),
                    scoping_status=escape_cypher(scoping_status),
                    scoping_confidence=scoping_confidence,
                ))
            else:
                q = edge.entity_qid or ""
                eid = f"concept_q{q[1:]}" if q.startswith("Q") else f"concept_q{q}"
                cipher = generate_entity_cipher(q, "CONCEPT", "wd") if generate_entity_cipher else f"ent_con_{q}"
                ext = edge.external_ids or {}
                fed_create = external_ids_to_cypher_set_clauses(ext, for_match=False)
                fed_match = external_ids_to_cypher_set_clauses(ext, for_match=True)
                lines.append(CYPHER_MERGE.format(
                    entity_qid=escape_cypher(edge.entity_qid),
                    entity_id=escape_cypher(eid),
                    entity_cipher=escape_cypher(cipher),
                    entity_label=escape_cypher(edge.entity_label),
                    fed_create_clauses=fed_create,
                    fed_match_clauses=fed_match,
                    subject_qid=escape_cypher(edge.subject_qid),
                    anchor_qid=escape_cypher(edge.anchor_qid),
                    confidence=round(edge.confidence, 4),
                    primary_facet=escape_cypher(edge.primary_facet),
                    scoping_status=escape_cypher(scoping_status),
                    scoping_confidence=scoping_confidence,
                ))

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"  Cypher file written: {output_path}")
    print(f"  {len(edges)} MERGE statements across {unique_subjects} SubjectConcepts")


# ---------------------------------------------------------------------------
# Neo4j direct write
# ---------------------------------------------------------------------------

# D-022: external_ids as separate properties per federation PID (Option B).
# Properties: pleiades_id, trismegistos_id, lgpn_id, viaf_id, getty_aat_id, edh_id, ocd_id.
WRITE_QUERY = """
MERGE (e:Entity {qid: $entity_qid})
  ON CREATE SET e.entity_id = $entity_id, e.entity_cipher = $entity_cipher, e.entity_type = $entity_type, e.label = $entity_label,
                e.pleiades_id = $pleiades_id, e.trismegistos_id = $trismegistos_id, e.lgpn_id = $lgpn_id,
                e.viaf_id = $viaf_id, e.getty_aat_id = $getty_aat_id, e.edh_id = $edh_id, e.ocd_id = $ocd_id,
                e.created_at = datetime()
  ON MATCH SET  e.entity_id = coalesce(e.entity_id, $entity_id),
                e.entity_cipher = coalesce(e.entity_cipher, $entity_cipher),
                e.entity_type = coalesce(e.entity_type, $entity_type),
                e.label = coalesce(e.label, $entity_label),
                e.pleiades_id = coalesce($pleiades_id, e.pleiades_id),
                e.trismegistos_id = coalesce($trismegistos_id, e.trismegistos_id),
                e.lgpn_id = coalesce($lgpn_id, e.lgpn_id),
                e.viaf_id = coalesce($viaf_id, e.viaf_id),
                e.getty_aat_id = coalesce($getty_aat_id, e.getty_aat_id),
                e.edh_id = coalesce($edh_id, e.edh_id),
                e.ocd_id = coalesce($ocd_id, e.ocd_id)
WITH e
MATCH (sc:SubjectConcept {qid: $subject_qid})
MERGE (e)-[r:MEMBER_OF]->(sc)
  ON CREATE SET
    r.anchor_qid         = $anchor_qid,
    r.confidence         = $confidence,
    r.primary_facet      = $primary_facet,
    r.scoping_status     = $scoping_status,
    r.scoping_confidence = $scoping_confidence,
    r.assigned_at        = datetime(),
    r.source             = 'cluster_assignment'
  ON MATCH SET
    r.confidence         = CASE WHEN $confidence > r.confidence
                               THEN $confidence ELSE r.confidence END,
    r.scoping_status     = CASE WHEN $scoping_status <> ''
                               THEN $scoping_status ELSE r.scoping_status END,
    r.scoping_confidence = CASE WHEN $scoping_confidence > 0
                               THEN $scoping_confidence ELSE r.scoping_confidence END
RETURN e.qid AS entity_qid, sc.qid AS subject_qid
"""

# DPRR Group C: match by entity_id
WRITE_QUERY_DPRR = """
MATCH (e:Entity {entity_id: $entity_id})
MATCH (sc:SubjectConcept {qid: $subject_qid})
MERGE (e)-[r:MEMBER_OF]->(sc)
  ON CREATE SET
    r.anchor_qid         = $anchor_qid,
    r.confidence         = $confidence,
    r.primary_facet      = $primary_facet,
    r.scoping_status     = $scoping_status,
    r.scoping_confidence = $scoping_confidence,
    r.assigned_at        = datetime(),
    r.source             = 'cluster_assignment'
  ON MATCH SET
    r.confidence         = CASE WHEN $confidence > r.confidence
                               THEN $confidence ELSE r.confidence END,
    r.scoping_status     = CASE WHEN $scoping_status <> ''
                               THEN $scoping_status ELSE r.scoping_status END,
    r.scoping_confidence = CASE WHEN $scoping_confidence > 0
                               THEN $scoping_confidence ELSE r.scoping_confidence END
RETURN e.entity_id AS entity_id, sc.qid AS subject_qid
"""

PREFLIGHT_QUERY = """
MATCH (sc:SubjectConcept)
RETURN sc.qid AS subject_qid
"""


def write_to_neo4j(
    edges: list[MemberOfEdge],
    uri: str,
    user: str,
    password: str,
    database: str = "neo4j",
    batch_size: int = 500,
):
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("Error: neo4j driver not installed. Run: pip install neo4j", file=sys.stderr)
        sys.exit(1)

    driver = GraphDatabase.driver(uri, auth=(user, password))

    # Use server default database (no database= param) - matches rebuild_system_subgraph,
    # load_roman_republic_ontology, etc. Explicit database="neo4j" can trigger
    # "Database neo4j not found" on some Aura/Neo5 setups despite SHOW DATABASES listing it.

    try:
        # Preflight: verify SubjectConcept nodes exist
        with driver.session() as session:
            result = session.run(PREFLIGHT_QUERY)
            existing_subjects = {r["subject_qid"] for r in result}

        if not existing_subjects:
            print("  [warn] No SubjectConcept nodes found in graph - check connection and data")
        else:
            print(f"  Preflight: {len(existing_subjects)} SubjectConcept nodes found in graph")

        # Check which subject_qids in our edges exist
        edge_subjects = {e.subject_qid for e in edges}
        missing = edge_subjects - existing_subjects
        if missing:
            print(f"  [warn] {len(missing)} subject_qids in edges have no matching node in graph:")
            for s in sorted(missing)[:10]:
                print(f"    {s}")
            if len(missing) > 10:
                print(f"    ... and {len(missing) - 10} more")

        # Write in batches
        created = 0
        failed = 0

        with driver.session() as session:
            for i in range(0, len(edges), batch_size):
                batch = edges[i:i+batch_size]
                for edge in batch:
                    try:
                        if edge.entity_id:
                            # DPRR Group C: match by entity_id
                            session.run(
                                WRITE_QUERY_DPRR,
                                entity_id=edge.entity_id,
                                subject_qid=edge.subject_qid,
                                anchor_qid=edge.anchor_qid,
                                confidence=edge.confidence,
                                primary_facet=edge.primary_facet or "",
                                scoping_status=edge.scoping_status or "",
                                scoping_confidence=edge.scoping_confidence or 0.0,
                            )
                        else:
                            q = edge.entity_qid or ""
                            eid = f"concept_q{q[1:]}" if q.startswith("Q") else f"concept_q{q}"
                            cipher = generate_entity_cipher(q, "CONCEPT", "wd") if generate_entity_cipher else f"ent_con_{q}"
                            fed_props = {p: None for p in ALL_FED_PROPS}
                            fed_props.update(external_ids_to_props(edge.external_ids or {}))
                            session.run(
                                WRITE_QUERY,
                                entity_qid=edge.entity_qid,
                                entity_id=eid,
                                entity_cipher=cipher,
                                entity_type="CONCEPT",
                                entity_label=edge.entity_label,
                                subject_qid=edge.subject_qid,
                                anchor_qid=edge.anchor_qid,
                                confidence=edge.confidence,
                                primary_facet=edge.primary_facet,
                                scoping_status=edge.scoping_status or "",
                                scoping_confidence=edge.scoping_confidence or 0.0,
                                **fed_props,
                            )
                        created += 1
                    except Exception as e:
                        failed += 1
                        if failed <= 5:
                            ident = edge.entity_qid or edge.entity_id or "?"
                            print(f"  [warn] Edge failed {ident}->{edge.subject_qid}: {e}")

                done = min(i + batch_size, len(edges))
                print(f"  {done}/{len(edges)} edges written...", file=sys.stderr)

        print(f"  Write complete: {created} succeeded, {failed} failed")

        # De facto confirmation: SubjectConcepts with MEMBER_OF edges are confirmed
        with driver.session() as session:
            result = session.run("""
                MATCH (sc:SubjectConcept)
                WHERE EXISTS((sc)<-[:MEMBER_OF]-())
                SET sc.harvest_status = 'confirmed'
                RETURN count(sc) AS updated
            """)
            row = result.single()
            updated = row["updated"] if row else 0
            if updated:
                print(f"  harvest_status updated: {updated} SubjectConcepts marked confirmed (entity_count > 0)")

        return created, failed

    finally:
        driver.close()


# ---------------------------------------------------------------------------
# Run summary
# ---------------------------------------------------------------------------

def write_assignment_summary(
    output_dir: Path,
    edges: list[MemberOfEdge],
    args,
    started_at: datetime,
    write_result: Optional[tuple] = None,
):
    # Distribution stats
    entities_per_subject: dict[str, int] = defaultdict(int)
    subjects_per_entity: dict[str, int] = defaultdict(int)
    for edge in edges:
        entities_per_subject[edge.subject_qid] += 1
        subjects_per_entity[edge.entity_qid] += 1

    multi_subject_entities = sum(1 for c in subjects_per_entity.values() if c > 1)

    summary = {
        "run_at": started_at.isoformat(),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "total_edges": len(edges),
        "unique_entities": len(subjects_per_entity),
        "unique_subject_concepts": len(entities_per_subject),
        "multi_subject_entities": multi_subject_entities,
        "avg_entities_per_subject": round(
            sum(entities_per_subject.values()) / len(entities_per_subject), 1
        ) if entities_per_subject else 0,
        "top_subjects_by_entity_count": sorted(
            entities_per_subject.items(), key=lambda x: x[1], reverse=True
        )[:20],
        "write_mode": {
            "cypher": args.cypher,
            "direct_write": args.write,
            "dry_run": args.dry_run,
        },
        "write_result": {
            "created": write_result[0] if write_result else None,
            "failed": write_result[1] if write_result else None,
        },
    }

    out_path = output_dir / "assignment_summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_summary(summary: dict):
    sep = "=" * 70
    print(f"\n{sep}")
    print("CLUSTER ASSIGNMENT SUMMARY")
    print(sep)
    print(f"Total MEMBER_OF edges   : {summary['total_edges']}")
    print(f"Unique entities         : {summary['unique_entities']}")
    print(f"Unique SubjectConcepts  : {summary['unique_subject_concepts']}")
    print(f"Multi-subject entities  : {summary['multi_subject_entities']}")
    print(f"Avg entities/subject    : {summary['avg_entities_per_subject']}")
    print(f"\nTop SubjectConcepts by entity count:")
    for subject_qid, count in summary["top_subjects_by_entity_count"][:10]:
        bar = "#" * min(count // 5, 40)
        print(f"  {subject_qid:<45} {count:>4}  {bar}")
    print(sep)


def main():
    parser = argparse.ArgumentParser(
        description="Create (entity)-[:MEMBER_OF]->(SubjectConcept) edges from harvest reports"
    )
    parser.add_argument("--harvest-dir", "-d", default=None,
        help="Directory containing *_report.json harvest files (optional if --dprr-neo4j)")
    parser.add_argument("--summary", "-s", required=True,
        help="Path to harvest_run_summary.json")
    parser.add_argument("--dprr-neo4j", action="store_true",
        help="Also load DPRR entities from Neo4j and assign to Q899409")
    parser.add_argument("--dprr-all", action="store_true",
        help="With --dprr-neo4j: load all DPRR entities (default: only those without MEMBER_OF)")
    parser.add_argument("--output-dir", "-o", default="output/cluster_assignment",
        help="Output directory (default: output/cluster_assignment)")
    parser.add_argument("--facet-dir", default=None,
        help="Optional: output/facet_classifications dir to enrich edges with facet data")

    # Output modes
    parser.add_argument("--cypher", action="store_true",
        help="Generate Cypher file for manual import")
    parser.add_argument("--write", action="store_true",
        help="Write directly to Neo4j Aura")
    parser.add_argument("--dry-run", action="store_true",
        help="Build edges and print summary, no output")

    # Neo4j connection (required if --write; falls back to .env)
    parser.add_argument("--neo4j-uri", default=NEO4J_URI,
        help="Neo4j URI (default: NEO4J_URI from .env)")
    parser.add_argument("--neo4j-user", default=NEO4J_USERNAME or "neo4j",
        help="Neo4j username (default: neo4j)")
    parser.add_argument("--neo4j-password", default=NEO4J_PASSWORD,
        help="Neo4j password (default: NEO4J_PASSWORD from .env)")
    parser.add_argument("--neo4j-database", default=NEO4J_DATABASE or "neo4j",
        help="Neo4j database name (default: NEO4J_DATABASE from .env or neo4j)")
    parser.add_argument("--batch-size", type=int, default=500,
        help="Write batch size for Neo4j (default: 500)")

    args = parser.parse_args()

    # Validate
    if not args.cypher and not args.write and not args.dry_run:
        print("Error: specify at least one of --cypher, --write, or --dry-run", file=sys.stderr)
        sys.exit(1)

    if args.write and not args.neo4j_uri:
        print("Error: --write requires --neo4j-uri (or set NEO4J_URI in .env)", file=sys.stderr)
        sys.exit(1)

    if args.write and not args.neo4j_password:
        import getpass
        args.neo4j_password = getpass.getpass("Neo4j password: ")

    harvest_dir = Path(args.harvest_dir) if args.harvest_dir else None
    summary_path = Path(args.summary)
    output_dir = Path(args.output_dir)
    facet_dir = Path(args.facet_dir) if args.facet_dir else None

    if not harvest_dir and not args.dprr_neo4j:
        print("Error: specify --harvest-dir and/or --dprr-neo4j", file=sys.stderr)
        sys.exit(1)
    if harvest_dir and not harvest_dir.exists():
        print(f"Error: not found: {harvest_dir}", file=sys.stderr)
        sys.exit(1)
    if not summary_path.exists():
        print(f"Error: not found: {summary_path}", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc)

    # Load
    print(f"\n{'='*70}")
    print("CLUSTER ASSIGNMENT")
    print(f"{'='*70}")

    summary_data = load_summary(summary_path)
    qid_to_subject_ids = summary_data.get("qid_to_subject_ids", {})
    print(f"Anchor mappings loaded : {len(qid_to_subject_ids)} anchor QIDs")

    if summary_data.get("dry_run") and harvest_dir:
        print(f"[warn] harvest_run_summary has dry_run=true - no harvest reports were written.")
        print(f"       Run harvest_all_anchors without --dry-run to produce reports, then retry.")

    harvest_reports = defaultdict(list, load_harvest_reports(harvest_dir) if harvest_dir else {})
    total_harvested = sum(len(v) for v in harvest_reports.values())
    print(f"Harvest reports loaded : {len(harvest_reports)} anchors, {total_harvested} entities")

    if args.dprr_neo4j and args.neo4j_uri and args.neo4j_password:
        dprr_entities = load_dprr_from_neo4j(
            args.neo4j_uri, args.neo4j_user, args.neo4j_password,
            only_without_member_of=not getattr(args, "dprr_all", False),
        )
        if dprr_entities:
            harvest_reports[DPRR_ANCHOR_QID].extend(dprr_entities)
            total_harvested += len(dprr_entities)
            scope = "all" if getattr(args, "dprr_all", False) else "no MEMBER_OF"
            print(f"DPRR from Neo4j       : {len(dprr_entities)} entities ({scope}) -> {DPRR_ANCHOR_QID}")
    elif args.dprr_neo4j:
        print(f"[warn] --dprr-neo4j requires Neo4j credentials (--neo4j-uri, --neo4j-password)")

    facet_classifications = load_facet_classifications(facet_dir)
    if facet_classifications:
        print(f"Facet classifications  : {len(facet_classifications)} entities enriched")

    # Build edges
    edges = build_edges(qid_to_subject_ids, harvest_reports, facet_classifications)
    print(f"\nEdges built            : {len(edges)} MEMBER_OF relationships")

    if not edges:
        print("No edges to process. Check that harvest reports match anchor QIDs in summary.")
        sys.exit(0)

    # Save edge list as JSON (always - useful for debugging)
    edges_path = output_dir / "member_of_edges.json"
    with open(edges_path, "w", encoding="utf-8") as f:
        json.dump([asdict(e) for e in edges], f, indent=2)
    print(f"Edge list saved        : {edges_path}")

    write_result = None

    if args.dry_run:
        print("\n[DRY RUN] No output written.")

    if args.cypher:
        cypher_path = output_dir / "member_of_edges.cypher"
        print(f"\nGenerating Cypher...")
        generate_cypher(edges, cypher_path)

    if args.write:
        print(f"\nWriting to Neo4j: {args.neo4j_uri} (using server default database)")
        write_result = write_to_neo4j(
            edges,
            uri=args.neo4j_uri,
            user=args.neo4j_user,
            password=args.neo4j_password,
            database=args.neo4j_database,
            batch_size=args.batch_size,
        )

    # Summary
    run_summary = write_assignment_summary(
        output_dir, edges, args, started_at, write_result
    )
    print_summary(run_summary)


if __name__ == "__main__":
    main()
