"""Wikipedia first contact for an event (29-EVENT-CENTRED-INQUIRY.md §3 steps 1-2, §5).

    python -m GraphRevised.harvest.wikipedia_contact <QID> [--apply] [--limit 50] [--language en]

The focus must be a local Entity with an accepted Wikidata identity. Its article
is found through the preserved Wikidata record's sitelink (never searched for),
fetched at a fixed revision, and preserved with the wiki's rights statement
(phase-8-source/). The article becomes a local Work of form `reference`
("Wikipedia, <title>") and each body paragraph a passage observation of it.

The articles its infobox and body link to are mapped to Wikidata items by the
wiki's own page properties, and each item is met once, as the harvest meets a
target (harvest.apply.surface): an Entity already holding the QID is reused;
otherwise the item's record is preserved and, if the checked class table gives
its kind and the run's budget allows, it becomes a proposed Entity, visible at
once. Infobox links come first, then the body in reading order. Where a
paragraph links the entity, an entity mention records the passage's own words
for it. Links are discovery, not claims: nothing here proposes a relationship.
That is the reader's work, on the same passages, with Wikipedia as one voice.

Without --apply everything runs in one transaction that is rolled back.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.adapters.wikipedia_passages import load_article, passage_observation, preserve_article, resolve_qids
from GraphRevised.capture.core import annotation_id, annotation_label
from GraphRevised.harvest.apply import HarvestError, surface
from GraphRevised.harvest.wikidata_harvest import load_rules
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.store import Neo4jReader
from GraphRevised.slices.add_entity import persist_local_entity, preserved_identity_payload

GRAPH_REVISED = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = GRAPH_REVISED / "phase-8-source"
PROPOSER_ID = "wikipedia-contact"


def work_id_for(article) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", article.title.lower()).strip("-")
    return f"chr:entity:wikipedia-{article.language}-{slug}"


def contact(tx: Any, qid: str, operations: dict[str, str], rules: dict[str, Any], *, limit: int,
            language: str = "en") -> dict[str, Any]:
    reader = Neo4jReader(tx)
    focus_ids = reader.entity_ids_for_wikidata(qid)
    if len(focus_ids) != 1:
        raise HarvestError(f"{qid} needs exactly one local Entity with an accepted identity, not {len(focus_ids)}")
    payload_path, _ = preserved_identity_payload(qid)
    sitelink = json.loads(payload_path.read_bytes())["entities"][qid].get("sitelinks", {}).get(f"{language}wiki")
    if not sitelink:
        raise HarvestError(f"{qid} has no {language} Wikipedia article in its Wikidata record")
    article = load_article(preserve_article(sitelink["title"], SOURCE_DIRECTORY, language))

    work_id = work_id_for(article)
    persist_local_entity(tx, operations, entity_id=work_id, kind="Work", label=f"Wikipedia, {article.title}",
                         description=f"The English Wikipedia article, read at revision {article.revision}.")
    registry = load_registry()
    run_write(tx, operations, "set_work_form", {"workId": work_id, "form": "reference",
                                                "allowedForms": sorted(registry.work_forms)})
    observations = {}
    for ref in article.all_refs():
        observation = passage_observation(article, ref)
        run_write(tx, operations, "upsert_passage_observation", observation)
        run_write(tx, operations, "link_observation_work", {"observationId": observation["id"], "workId": work_id})
        observations[ref] = observation["id"]

    # Linked articles in order: the infobox first, then the body as it reads.
    titles = list(dict.fromkeys([*article.infobox_links,
                                 *(title for p in article.passages.values() for title, _ in p.links)]))
    stem = article.path.name.removesuffix(".json")
    qids = resolve_qids(titles, SOURCE_DIRECTORY, stem, language)
    budget = {"left": limit}
    met: dict[str, dict[str, Any]] = {}
    for title in titles:
        target = qids.get(title)
        if not target or target == qid or target in met:
            continue
        met[target] = {**surface(tx, operations, target, rules, budget), "title": title}

    mentions = 0
    for ref, passage in article.passages.items():
        for title, words in passage.links:
            found = met.get(qids.get(title, ""), {})
            if not found.get("entityId") or not words or words not in passage.text:
                continue
            note = f"Linked in Wikipedia as \"{words}\""
            run_write(tx, operations, "upsert_annotation", {
                "id": annotation_id(PROPOSER_ID, observations[ref], note, [found["entityId"]]),
                "label": annotation_label(tx, kind="entity-mention", note_type="detail",
                                          observation_id=observations[ref], mentioned=words),
                "kind": "entity-mention", "noteType": "detail", "note": note, "author": PROPOSER_ID,
                "visibility": "team", "createdAt": datetime.now(timezone.utc).isoformat(),
                "observationId": observations[ref], "quotation": words, "concerns": [found["entityId"]],
            })
            mentions += 1
    return {"focus": f"{focus_ids[0]} ({qid})", "article": article.citation, "work": work_id,
            "passages": len(observations), "linkedArticles": len(titles), "withWikidataItem": len(qids),
            "met": met, "mentions": mentions, "budgetLeft": budget["left"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("qid")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--limit", type=int, default=50, help="budget of new entities")
    parser.add_argument("--language", default="en")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                result = contact(tx, args.qid, load_operations(), load_rules(), limit=args.limit, language=args.language)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                tx.rollback()
                raise
    finally:
        driver.close()

    states = Counter(item["state"].split(":")[0] for item in result["met"].values())
    print(f"{result['article']} -> {result['work']}: {result['passages']} passages")
    print(f"linked articles {result['linkedArticles']}, with a Wikidata item {result['withWikidataItem']}; "
          f"met {len(result['met'])}: " + ", ".join(f"{n} {s}" for s, n in states.most_common()))
    print(f"mentions recorded: {result['mentions']}; budget left: {result['budgetLeft']}")
    for item in result["met"].values():
        print(f"  {item['title']} ({item['qid']}): {item['state']}" + (f" -> {item['entityId']}" if item.get("entityId") else ""))
    print("applied" if args.apply else "dry run: rolled back")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
