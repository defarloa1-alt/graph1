"""Metals, materials, products and denominations from the Getty AAT, with their broader concepts (45, D-160).

    python -m GraphRevised.harvest.getty_aat [--apply]

For each seed in curation/materials.json (a thing a source we hold names), this
fetches the seed's chain of preferred broader concepts from the Getty Art &
Architecture Thesaurus SPARQL endpoint (ODC-By 1.0), preserves the response in
phase-5-source/, and in one transaction:

1. makes each concept a Type (our label for the seed, the AAT's label above it),
   with its typeCategory and its AAT record as identity (and the coin records'
   Nomisma id as a crosswalk for the seed);
2. stores each concept's record as an observation in the Work "Getty Art &
   Architecture Thesaurus";
3. proposes each concept `subtypeOf` its nearest broader concept, according to
   the AAT, quoting the record's "Broader:" line. The AAT's organizing headings
   (guide terms, hierarchy names, facets) are passed over and named in the line,
   never made Types. The chain stops at the top concept under the hierarchy name.

These are code-made extractions from structured records, accepted by rule
(proposer getty-aat-hierarchy, D-145, D-160). Without --apply it reports and
rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import submit

GRAPH_REVISED = Path(__file__).resolve().parents[1]
SEEDS = GRAPH_REVISED / "curation" / "materials.json"
PAYLOADS = GRAPH_REVISED / "phase-5-source"
ENDPOINT = "https://vocab.getty.edu/sparql.json"
PROPOSER = "getty-aat-hierarchy"
VERSION = "getty-aat-v1"
SYSTEM = "Getty Art & Architecture Thesaurus"
RIGHTS = ("Open Data Commons Attribution License 1.0 (http://opendatacommons.org/licenses/by/1.0/), "
          "as each AAT record states; attribution: The J. Paul Getty Trust, Art & Architecture Thesaurus")
WORK = {"id": "chr:entity:getty-aat", "label": "Getty Art & Architecture Thesaurus", "shortLabel": "Getty AAT",
        "form": "reference",
        "description": "The J. Paul Getty Trust's thesaurus of art, architecture and material culture: what its "
                       "editors place under what. A voice for the hierarchy of materials and objects (45, D-160)."}
CONCEPT = "http://vocab.getty.edu/ontology#Concept"
QUERY = """
SELECT ?c ?label ?type ?parent ?note WHERE {{
  aat:{aat} gvp:broaderPreferred* ?c .
  ?c gvp:prefLabelGVP/xl:literalForm ?label ; a ?type .
  FILTER(?type IN (gvp:Concept, gvp:GuideTerm, gvp:Hierarchy, gvp:Facet))
  OPTIONAL {{ ?c gvp:broaderPreferred ?parent }}
  OPTIONAL {{ ?c skos:scopeNote/rdf:value ?note . FILTER(lang(?note) = "en") }}
}}"""


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def aat_id(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def chain(bindings: list[dict[str, Any]], start: str) -> list[dict[str, Any]]:
    """The seed and the concepts above it, each with its nearest broader concept and the headings passed over.

    Stops at the top concept: the last one before a hierarchy name or facet."""
    nodes: dict[str, dict[str, Any]] = {}
    for b in bindings:
        node = nodes.setdefault(aat_id(b["c"]["value"]), {"id": aat_id(b["c"]["value"]), "label": b["label"]["value"],
                                                          "concept": False, "parent": None, "note": None})
        node["concept"] = node["concept"] or b["type"]["value"] == CONCEPT
        if "parent" in b:
            node["parent"] = aat_id(b["parent"]["value"])
        if "note" in b and node["note"] is None:
            node["note"] = b["note"]["value"]
    found, at = [], start
    while at is not None and nodes.get(at, {}).get("concept"):
        node, through, up = nodes[at], [], nodes[at]["parent"]
        while up is not None and up in nodes and not nodes[up]["concept"] and nodes[up]["label"].startswith("<"):
            through.append(nodes[up]["label"])  # a guide term: an organizing heading, passed over
            up = nodes[up]["parent"]
        broader = up if up is not None and nodes.get(up, {}).get("concept") else None
        found.append({"id": node["id"], "label": node["label"], "note": node["note"], "broader": broader,
                      "broaderLabel": nodes[broader]["label"] if broader else None, "through": through})
        at = broader
    return found


def record_text(concept: dict[str, Any]) -> tuple[str, str | None]:
    """The record's text and its "Broader:" line (quoted as evidence), or None at the top."""
    lines = [f"{concept['label']} (AAT {concept['id']})"]
    if concept["note"]:
        lines.append(f"Scope note: {concept['note']}")
    broader = None
    if concept["broader"]:
        via = f" (under the heading {', '.join(concept['through'])})" if concept["through"] else ""
        broader = f"Broader: {concept['broaderLabel']} (AAT {concept['broader']}){via}"
        lines.append(broader)
    return "\n".join(lines), broader


def fetch(aat: str) -> tuple[bytes, dict[str, Any]]:
    """Fetch a seed's chain and preserve it; returns the payload and its metadata."""
    query = QUERY.format(aat=aat)
    # The endpoint answers 400 to a request with no Accept header (Python's default).
    request = urllib.request.Request(ENDPOINT + "?" + urllib.parse.urlencode({"query": query}),
                                     headers={"User-Agent": "chrystallum-harvest/0.1",
                                              "Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    retrieved = datetime.now(timezone.utc).isoformat(timespec="seconds")
    digest = hashlib.sha256(payload).hexdigest()
    path = PAYLOADS / f"aat-{aat}.json"
    path.write_bytes(payload)
    metadata = {"aat": aat, "sourceUri": ENDPOINT, "query": query, "retrievedAt": retrieved, "contentHash": digest,
                "rights": RIGHTS}
    (PAYLOADS / f"aat-{aat}.metadata.json").write_text(json.dumps(metadata, indent=1), encoding="utf-8")
    return payload, metadata


def type_id(label: str) -> str:
    return f"chr:entity:type-{slug(label)}"


def our_label(concept: dict[str, Any], seeds: dict[str, str], labels: dict[str, str]) -> str:
    """Our wording: the seed's label, a label the curation file gives, or the AAT's without its qualifier."""
    return seeds.get(concept["id"]) or labels.get(concept["id"]) or re.sub(r"\s*\([^)]*\)$", "", concept["label"])


def harvest(tx, operations, registry, config: dict[str, Any], fetched: dict[str, tuple[bytes, dict]], at: str) -> dict:
    exists = tx.run("MATCH (e:Entity {id: $id}) RETURN e.id", id=WORK["id"]).single() is not None
    run_write(tx, operations, "upsert_entity", {k: WORK[k] for k in ("id", "label", "shortLabel", "description")}
              | {"kind": "Work", "status": None if exists else "provisional"})
    run_write(tx, operations, "set_work_form", {"workId": WORK["id"], "form": WORK["form"],
                                                "allowedForms": sorted(registry.work_forms)})
    overrides, labels = config.get("categories", {}), config.get("labels", {})
    seed_labels = {s["aat"]: s["label"] for s in config["seeds"]}
    report: dict[str, Any] = {"types": [], "claims": []}
    done: set[str] = set()
    drafts = []  # submitted once every Type exists: a broader concept may come later in the chain
    for seed in config["seeds"]:
        payload, metadata = fetched[seed["aat"]]
        concepts = chain(json.loads(payload)["results"]["bindings"], seed["aat"])
        ids = {c["id"]: type_id(our_label(c, seed_labels, labels)) for c in concepts}
        for concept in concepts:
            if concept["id"] in done:
                continue  # a shared ancestor (metal, coins) is made once
            done.add(concept["id"])
            entity_id, is_seed = ids[concept["id"]], concept["id"] == seed["aat"]
            label = our_label(concept, seed_labels, labels)
            category = seed["category"] if is_seed else overrides.get(concept["id"], seed["ancestorCategory"])
            present = tx.run("MATCH (e:Entity {id: $id}) RETURN e.id", id=entity_id).single() is not None
            run_write(tx, operations, "upsert_entity", {
                "id": entity_id, "kind": "Type", "label": None if present else label,
                "shortLabel": None if present else label,
                "description": None if present else (concept["note"] or f"{concept['label']}, in the Getty AAT."),
                "status": None if present else "provisional"})
            run_write(tx, operations, "set_type_category", {
                "id": entity_id, "category": category, "allowedCategories": sorted(registry.type_categories),
                "decidedAt": at, "decidedBy": f"{VERSION} (curation/materials.json)",
                "decisionBasis": "45 §4.1: taxa, materials, products and denominations are Types by category"})
            rel = (PAYLOADS / f"aat-{seed['aat']}.json").relative_to(GRAPH_REVISED.parent).as_posix()
            run_write(tx, operations, "upsert_authority", {
                "entityId": entity_id, "id": f"chr:authority:getty-aat:{concept['id']}", "system": "Getty AAT",
                "identifier": concept["id"], "label": f"Getty AAT record: {concept['label']} (AAT {concept['id']})",
                "shortLabel": f"Getty AAT: {concept['label']}", "description": concept["note"],
                "retrievedAt": metadata["retrievedAt"], "sourceUri": f"http://vocab.getty.edu/aat/{concept['id']}",
                "sourceRevision": None, "contentHash": metadata["contentHash"], "rawPayloadUri": rel,
                "role": "entity_identity", "relation": "closeMatch", "linkStatus": "accepted"})
            if is_seed and seed.get("nomisma"):
                run_write(tx, operations, "upsert_authority", {
                    "entityId": entity_id, "id": f"chr:authority:nomisma:{seed['nomisma']}", "system": "Nomisma",
                    "identifier": seed["nomisma"], "label": f"Nomisma: {label} (nm:{seed['nomisma']})",
                    "shortLabel": f"Nomisma: {label}", "description": None, "retrievedAt": metadata["retrievedAt"],
                    "sourceUri": f"http://nomisma.org/id/{seed['nomisma']}", "sourceRevision": None,
                    "contentHash": None, "rawPayloadUri": None,
                    "role": "crosswalk", "relation": "closeMatch", "linkStatus": "accepted"})
            text, broader_line = record_text(concept)
            # Keyed by the record's text, not the response: a re-fetch that returns rows in another order is the same record.
            observation_id = f"chr:observation:aat:{concept['id']}:{hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]}"
            run_write(tx, operations, "upsert_record_observation", {
                "id": observation_id, "label": f"{concept['label']} (Getty AAT {concept['id']})",
                "shortLabel": f"AAT {concept['id']}", "sourceSystem": SYSTEM, "sourceEntityId": concept["id"],
                "locator": f"http://vocab.getty.edu/aat/{concept['id']}", "passageText": text,
                "passageHash": hashlib.sha256(text.encode("utf-8")).hexdigest(), "editorialNotes": [],
                "language": "en", "workTitle": WORK["label"], "author": "The J. Paul Getty Trust",
                "editionCitation": "Getty Art & Architecture Thesaurus, Linked Open Data (vocab.getty.edu)",
                "rights": RIGHTS, "sourceUri": ENDPOINT, "sourceRevision": None,
                "retrievedAt": metadata["retrievedAt"], "contentHash": metadata["contentHash"], "rawPayloadUri": rel,
                "workId": WORK["id"]})
            report["types"].append(f"{category:12} {label} (AAT {concept['id']}: {concept['label']})")
            if broader_line is None:
                continue
            drafts.append(ProposalDraft(
                predicate="subtypeOf", subject_id=entity_id, object_id=ids[concept["broader"]], mode="attributed",
                attributed_to=WORK["id"], observation_ids=(observation_id,),
                quotations=(Quotation(observation_id=observation_id, text=broader_line),),
                rationale=f"The AAT places {concept['label']} under {concept['broaderLabel']}.",
                proposed_by=PROPOSER, prompt_version=VERSION,
                relevance="The authority's hierarchy, so a material or object can be navigated upward (45 §4.3)."))
    for draft in drafts:
        result = submit(tx, draft, registry, operations)
        report["claims"].append({"subject": draft.subject_id, "object": draft.object_id,
                                 "outcome": result.validation.outcome.value,
                                 "reasons": list(result.validation.reasons), "stored": result.stored})
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    config = json.loads(SEEDS.read_text(encoding="utf-8"))
    fetched = {seed["aat"]: fetch(seed["aat"]) for seed in config["seeds"]}
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                report = harvest(tx, load_operations(), load_registry(), config, fetched, at)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print("applied" if args.apply else "dry run, rolled back")
    print("\n".join(report["types"]))
    held = [c for c in report["claims"] if c["outcome"] == "duplicate"]  # a re-run: the link is already held
    bad = [c for c in report["claims"] if c["outcome"] not in ("valid", "duplicate")]
    print(f"{len(report['claims'])} subtypeOf claims: {len(report['claims']) - len(held) - len(bad)} new, "
          f"{len(held)} already held, {len(bad)} not valid")
    for c in bad:
        print(" ", c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
