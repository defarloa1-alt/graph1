#!/usr/bin/env python3
"""
Load CIDOC-CRM and CRMinf reference nodes into Neo4j.

Creates:
- (:CIDOC_Class), (:CIDOC_Property)
- (:CRMinf_Class), (:CRMinf_Property)
- (:CRMinf_Class)-[:SUBCLASS_OF]->(:CIDOC_Class|:CRMinf_Class)
- (:CRMinf_Property)-[:DOMAIN|:RANGE]->(:CIDOC_Class|:CRMinf_Class)

This script is safe to re-run (MERGE).
"""
import argparse
import io
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

CIDOC_BASE_URI = "http://www.cidoc-crm.org/cidoc-crm/"
CRMINF_BASE_URI = "http://www.ics.forth.gr/isl/CRMinf/"


def normalize_label(text: str) -> str:
    return text.replace("_", " ").replace("-", " ").strip()


def split_code_label(raw_key: str):
    if "_" in raw_key:
        code, label = raw_key.split("_", 1)
        return code, normalize_label(label)
    return raw_key, ""


def parse_cidoc_context(cidoc_path: Path):
    data = json.loads(cidoc_path.read_text(encoding="utf-8"))
    context = data.get("@context", {})
    classes = []
    props = []

    for raw_key, value in context.items():
        if not isinstance(value, dict):
            continue
        uri = value.get("@id")
        if not uri:
            continue

        if uri.startswith("crm:"):
            uri = CIDOC_BASE_URI + uri.split(":", 1)[1]
        elif not uri.startswith("http"):
            # Skip non-URI entries
            continue

        if raw_key.startswith("E"):
            code, label = split_code_label(raw_key)
            classes.append({
                "id": raw_key,
                "code": code,
                "label": label,
                "uri": uri,
                "source": "cidoc-crm",
                "version": "7.1.2",
                "raw_key": raw_key,
            })
        elif raw_key.startswith("P"):
            code, label = split_code_label(raw_key)
            props.append({
                "id": raw_key,
                "code": code,
                "label": label,
                "uri": uri,
                "source": "cidoc-crm",
                "version": "7.1.2",
                "raw_key": raw_key,
            })

    return classes, props


def parse_crminf_rdfs(crminf_path: Path):
    ns = {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    }

    root = ET.fromstring(crminf_path.read_text(encoding="utf-8"))

    classes = []
    props = []

    for class_el in root.findall("rdfs:Class", ns):
        uri = class_el.attrib.get(f"{{{ns['rdf']}}}about")
        if not uri:
            continue
        raw_key = uri.rsplit("/", 1)[-1]
        code, label = split_code_label(raw_key)
        comment = (class_el.findtext("rdfs:comment", default="", namespaces=ns) or "").strip()

        sub_class_of = []
        for parent in class_el.findall("rdfs:subClassOf", ns):
            parent_uri = parent.attrib.get(f"{{{ns['rdf']}}}resource")
            if parent_uri:
                sub_class_of.append(parent_uri)

        classes.append({
            "id": raw_key,
            "code": code,
            "label": label,
            "uri": uri,
            "source": "crminf",
            "version": "0.7",
            "raw_key": raw_key,
            "comment": comment,
            "sub_class_of": sub_class_of,
        })

    for prop_el in root.findall("rdf:Property", ns):
        uri = prop_el.attrib.get(f"{{{ns['rdf']}}}about")
        if not uri:
            continue
        raw_key = uri.rsplit("/", 1)[-1]
        code, label = split_code_label(raw_key)
        comment = (prop_el.findtext("rdfs:comment", default="", namespaces=ns) or "").strip()

        domains = []
        ranges = []
        for domain in prop_el.findall("rdfs:domain", ns):
            domain_uri = domain.attrib.get(f"{{{ns['rdf']}}}resource")
            if domain_uri:
                domains.append(domain_uri)
        for range_el in prop_el.findall("rdfs:range", ns):
            range_uri = range_el.attrib.get(f"{{{ns['rdf']}}}resource")
            if range_uri:
                ranges.append(range_uri)

        props.append({
            "id": raw_key,
            "code": code,
            "label": label,
            "uri": uri,
            "source": "crminf",
            "version": "0.7",
            "raw_key": raw_key,
            "comment": comment,
            "domain": domains,
            "range": ranges,
        })

    return classes, props


def chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def write_in_batches(session, query, rows, batch_size):
    for batch in chunked(rows, batch_size):
        session.execute_write(lambda tx, b=batch: tx.run(query, rows=b))


def main():
    parser = argparse.ArgumentParser(description="Load CIDOC-CRM and CRMinf into Neo4j")
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--user", default="neo4j", help="Neo4j username")
    parser.add_argument("--password", default="Chrystallum", help="Neo4j password")
    parser.add_argument("--cidoc", default="CIDOC/CIDOC_CRM_v7.1.2_JSON-LD_Context.jsonld", help="CIDOC JSON-LD context")
    parser.add_argument("--crminf", default="CIDOC/CRMinf_v0.7_.rdfs.txt", help="CRMinf RDFS file")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch size for UNWIND")

    args = parser.parse_args()

    cidoc_path = Path(args.cidoc)
    crminf_path = Path(args.crminf)

    if not cidoc_path.exists():
        raise FileNotFoundError(f"CIDOC file not found: {cidoc_path}")
    if not crminf_path.exists():
        raise FileNotFoundError(f"CRMinf file not found: {crminf_path}")

    cidoc_classes, cidoc_props = parse_cidoc_context(cidoc_path)
    crminf_classes, crminf_props = parse_crminf_rdfs(crminf_path)

    print("=" * 80)
    print("CIDOC-CRM + CRMinf LOAD")
    print("=" * 80)
    print(f"CIDOC classes: {len(cidoc_classes)}")
    print(f"CIDOC properties: {len(cidoc_props)}")
    print(f"CRMinf classes: {len(crminf_classes)}")
    print(f"CRMinf properties: {len(crminf_props)}")
    print()

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    cidoc_class_query = """
    UNWIND $rows AS row
    MERGE (c:CIDOC_Class {id: row.id})
    SET c.code = row.code,
        c.label = row.label,
        c.uri = row.uri,
        c.source = row.source,
        c.version = row.version,
        c.raw_key = row.raw_key
    """

    cidoc_prop_query = """
    UNWIND $rows AS row
    MERGE (p:CIDOC_Property {id: row.id})
    SET p.code = row.code,
        p.label = row.label,
        p.uri = row.uri,
        p.source = row.source,
        p.version = row.version,
        p.raw_key = row.raw_key
    """

    crminf_class_query = """
    UNWIND $rows AS row
    MERGE (c:CRMinf_Class {id: row.id})
    SET c.code = row.code,
        c.label = row.label,
        c.uri = row.uri,
        c.source = row.source,
        c.version = row.version,
        c.raw_key = row.raw_key,
        c.comment = row.comment
    """

    crminf_prop_query = """
    UNWIND $rows AS row
    MERGE (p:CRMinf_Property {id: row.id})
    SET p.code = row.code,
        p.label = row.label,
        p.uri = row.uri,
        p.source = row.source,
        p.version = row.version,
        p.raw_key = row.raw_key,
        p.comment = row.comment,
        p.domain = row.domain,
        p.range = row.range
    """

    crminf_subclass_query = """
    UNWIND $rows AS row
    MATCH (child:CRMinf_Class {uri: row.uri})
    UNWIND row.sub_class_of AS parent_uri
    MATCH (parent)
    WHERE (parent:CRMinf_Class OR parent:CIDOC_Class) AND parent.uri = parent_uri
    MERGE (child)-[:SUBCLASS_OF]->(parent)
    """

    crminf_domain_query = """
    UNWIND $rows AS row
    MATCH (p:CRMinf_Property {uri: row.uri})
    UNWIND row.domain AS domain_uri
    MATCH (d)
    WHERE (d:CRMinf_Class OR d:CIDOC_Class) AND d.uri = domain_uri
    MERGE (p)-[:DOMAIN]->(d)
    """

    crminf_range_query = """
    UNWIND $rows AS row
    MATCH (p:CRMinf_Property {uri: row.uri})
    UNWIND row.range AS range_uri
    MATCH (r)
    WHERE (r:CRMinf_Class OR r:CIDOC_Class) AND r.uri = range_uri
    MERGE (p)-[:RANGE]->(r)
    """

    try:
        with driver.session() as session:
            write_in_batches(session, cidoc_class_query, cidoc_classes, args.batch_size)
            write_in_batches(session, cidoc_prop_query, cidoc_props, args.batch_size)
            write_in_batches(session, crminf_class_query, crminf_classes, args.batch_size)
            write_in_batches(session, crminf_prop_query, crminf_props, args.batch_size)
            write_in_batches(session, crminf_subclass_query, crminf_classes, args.batch_size)
            write_in_batches(session, crminf_domain_query, crminf_props, args.batch_size)
            write_in_batches(session, crminf_range_query, crminf_props, args.batch_size)

        print("[OK] Load completed.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
