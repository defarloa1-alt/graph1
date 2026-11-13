"""Preview or import curator-approved local Subject hierarchy manifests.

Preview is offline and is the default. --apply requires an approved manifest,
explicit local connection settings, and the existing Subject.id constraint.
No authority references, facets, entities, or existing subject properties are
created or changed.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "GraphRevised" / "plans" / "roman-republic-subject-review.json"
SUBJECT_ID = re.compile(r"chr:subject:[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def validate_manifest(manifest: object, *, apply: bool = False) -> dict:
    if not isinstance(manifest, dict):
        raise ValueError("Manifest must be an object.")
    subjects, edges = manifest.get("subjects"), manifest.get("broader")
    if not isinstance(subjects, list) or not subjects or not isinstance(edges, list):
        raise ValueError("Manifest requires a non-empty subjects list and a broader list.")
    if apply and (manifest.get("status") != "approved" or not isinstance(manifest.get("approvedBy"), str)
                  or not manifest["approvedBy"].strip()):
        raise ValueError("Apply requires status 'approved' and a non-empty approvedBy in the manifest.")
    nodes = {}
    for row in subjects:
        if not isinstance(row, dict):
            raise ValueError("Every subject must be an object.")
        subject_id, label = row.get("id"), row.get("label")
        if not isinstance(subject_id, str) or not SUBJECT_ID.fullmatch(subject_id):
            raise ValueError(f"Invalid local Subject ID: {subject_id!r}.")
        if subject_id in nodes:
            raise ValueError(f"Duplicate Subject ID: {subject_id}.")
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"Missing label for {subject_id}.")
        if apply and row.get("reviewStatus") != "approved":
            raise ValueError(f"Subject is not approved: {subject_id}.")
        nodes[subject_id] = row

    adjacency = defaultdict(set)
    indegree = {subject_id: 0 for subject_id in nodes}
    pairs = set()
    for row in edges:
        if not isinstance(row, dict):
            raise ValueError("Every broader relationship must be an object.")
        child, parent = row.get("subjectId"), row.get("broaderId")
        if not isinstance(child, str) or not isinstance(parent, str) or child not in nodes or parent not in nodes:
            raise ValueError(f"NARROWER_THAN endpoints must exist in the manifest: {child!r} -> {parent!r}.")
        if child == parent or (child, parent) in pairs:
            raise ValueError(f"Self-link or duplicate NARROWER_THAN relationship: {child} -> {parent}.")
        if apply and (row.get("reviewStatus") != "approved" or not isinstance(row.get("reason"), str)
                      or not row["reason"].strip()):
            raise ValueError(f"NARROWER_THAN relationship needs approval and reason: {child} -> {parent}.")
        pairs.add((child, parent))
        adjacency[child].add(parent)
        indegree[parent] += 1
    ready = deque(subject_id for subject_id, count in indegree.items() if count == 0)
    visited = 0
    while ready:
        subject_id = ready.popleft()
        visited += 1
        for parent in adjacency[subject_id]:
            indegree[parent] -= 1
            if indegree[parent] == 0:
                ready.append(parent)
    if visited != len(nodes):
        raise ValueError("Manifest NARROWER_THAN hierarchy contains a cycle.")
    return manifest


def local_config() -> dict:
    from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

    uri = urlparse(NEO4J_URI)
    if uri.scheme not in {"bolt", "neo4j"} or uri.hostname not in {"127.0.0.1", "localhost", "::1"} or uri.username:
        raise ValueError("Apply is restricted to a local bolt:// or neo4j:// URI.")
    if NEO4J_DATABASE != "neo4j":
        raise ValueError("Apply is restricted to the clean-start neo4j database.")
    if not NEO4J_USERNAME or not NEO4J_PASSWORD:
        raise ValueError("Set the Neo4j username and password in .env or the environment.")
    return {"uri": NEO4J_URI, "user": NEO4J_USERNAME, "password": NEO4J_PASSWORD, "database": NEO4J_DATABASE}


def apply_manifest(tx, manifest: dict) -> dict:
    """Apply in one transaction; refuse conflicting subjects or cyclic links."""
    validate_manifest(manifest, apply=True)
    if tx.run("MATCH (:Subject)-[r:BROADER]->(:Subject) RETURN count(r) AS count").single(strict=True)["count"]:
        raise ValueError("Legacy Subject BROADER links exist; migrate them before importing.")
    rows = [{"id": row["id"], "label": row["label"]} for row in manifest["subjects"]]
    existing = tx.run(
        "UNWIND $rows AS row MATCH (s:Subject {id: row.id}) "
        "RETURN s.id AS id, s.label AS label, s.status AS status",
        rows=rows,
    ).data()
    wanted = {row["id"]: row["label"] for row in rows}
    for row in existing:
        if row["label"] != wanted[row["id"]] or row["status"] not in {"candidate", "provisional", "validated"}:
            raise ValueError(f"Existing Subject conflicts with manifest: {row['id']}. No properties were changed.")

    result = tx.run(
        "UNWIND $rows AS row "
        "MERGE (s:Subject {id: row.id}) "
        "ON CREATE SET s.label = row.label, s.status = 'candidate' "
        "RETURN count(s) AS count",
        rows=rows,
    ).single(strict=True)
    if result["count"] != len(rows):
        raise RuntimeError("Not all subjects were matched or created.")

    for edge in manifest["broader"]:
        params = {"child": edge["subjectId"], "parent": edge["broaderId"]}
        cycle = tx.run(
            "MATCH (parent:Subject {id: $parent}), (child:Subject {id: $child}) "
            "RETURN EXISTS { MATCH (parent)-[:NARROWER_THAN*1..]->(child) } AS cycle",
            **params,
        ).single(strict=True)
        if cycle["cycle"]:
            raise ValueError(f"NARROWER_THAN link would create a cycle: {params['child']} -> {params['parent']}.")
        result = tx.run(
            "MATCH (child:Subject {id: $child}), (parent:Subject {id: $parent}) "
            "MERGE (child)-[r:NARROWER_THAN]->(parent) "
            "ON CREATE SET r.reason = $reason, r.approvedBy = $approvedBy "
            "RETURN count(r) AS count",
            **params, reason=edge["reason"], approvedBy=manifest["approvedBy"],
        ).single(strict=True)
        if result["count"] != 1:
            raise RuntimeError(f"NARROWER_THAN link was not created uniquely: {params['child']} -> {params['parent']}.")
    return {"subjects": len(rows), "broader": len(manifest["broader"])}


def require_subject_constraint(session) -> None:
    constraints = session.run(
        "SHOW CONSTRAINTS YIELD type, labelsOrTypes, properties "
        "RETURN type, labelsOrTypes, properties"
    ).data()
    if not any(row["type"] in {"NODE_PROPERTY_UNIQUENESS", "NODE_KEY"}
               and row["labelsOrTypes"] == ["Subject"] and row["properties"] == ["id"]
               for row in constraints):
        raise ValueError("The database must have a uniqueness or node-key constraint on Subject.id.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--apply", action="store_true", help="write an approved manifest to local Neo4j")
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        validate_manifest(manifest, apply=args.apply)
        print(f"Manifest status: {manifest.get('status', '(missing)')}")
        print(f"Subjects: {len(manifest['subjects'])}; NARROWER_THAN links: {len(manifest['broader'])}")
        for row in manifest["subjects"]:
            print(f"  {row['id']}: {row['label']}")
        for edge in manifest["broader"]:
            print(f"  {edge['subjectId']} -[:NARROWER_THAN]-> {edge['broaderId']}")
        print("QIDs, facets, authority records and entity links are not imported.")
        if not args.apply:
            print("Offline preview only; no database connection or writes.")
            if manifest.get("status") != "approved":
                print("Manifest is not approved for import.")
            return 0

        from neo4j import GraphDatabase

        config = local_config()
        print(f"Target: {config['uri']}, database {config['database']}")
        with GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"])) as driver:
            with driver.session(database=config["database"]) as session:
                require_subject_constraint(session)
                result = session.execute_write(apply_manifest, manifest)
        print(f"Applied {result['subjects']} subjects and {result['broader']} NARROWER_THAN links.")
        return 0
    except (OSError, json.JSONDecodeError, ValueError, RuntimeError) as error:
        print(f"Subject import refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
