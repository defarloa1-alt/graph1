"""Migration 035 (2026-11-24): seven places of the Actium campaign, from the passages that name them.

    python -m GraphRevised.migrations.035_actium_campaign_places [--apply]

The Actium scene (scenes/actium-campaign-31bc.proposed.json) names seven places the graph did not hold.
Each is proposed here as a Place from a stored passage that names it (an entity mention), given its
Pleiades record as a crosswalk, and linked to that record's Location in the gazetteer, which carries the
coordinates:

| Place | Named in | Pleiades | Which record, and why |
|---|---|---|---|
| Brundisium | Dio 50.11.6 | 442509 | the port of departure |
| Corcyra | Dio 50.12.2 | 530835 | the island: the graph's Corfu (Wikidata Q121378) is reused; the town is 530834 |
| Toryne | Plutarch 62.3 | 531127 | Pleiades marks its location uncertain ("Toryne?") |
| Leucas | Dio 50.13.5 | 530974 | the town Agrippa took with its ships, not the island (530975) |
| Methone | Dio 50.11.3 | 570483 | the Messenian Methone, among five of the name |
| Taenarum | Plutarch 67.6 | 570702 | the port, for a crossing; the cape is 570703 |
| Paraetonium | Plutarch 69.1 | 716615 | |

Which record answers to the passage's place is a reading, so every entity, record link and location
link stays proposed for the curator. Pleiades records are CC BY 3.0. Without --apply it reports and
rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from neo4j import GraphDatabase

from GraphRevised import localdb
from GraphRevised.adapters.wikidata_statements import REPOSITORY_ROOT
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.entities import propose_entity

ROOT = Path(__file__).resolve().parents[1]
DUMP = ROOT / "cache" / "pleiades" / "pleiades-places-latest.json.gz"
BY = "curator request (entered by Claude, 2026-11-24)"
PLACES = [  # label, observation, phrase that names it, Pleiades id, the record's title, why this record
    ("Brundisium", "chr:observation:lacuscurtius:cassius-dio:50.11.6:1f50fd6b", "From Brundisium", "442509",
     "Brundisium/Brentesion", "the port of departure"),
    ("Corcyra", "chr:observation:lacuscurtius:cassius-dio:50.12.2:1f50fd6b", "seized Corcyra", "530835",
     "Corcyra (island)", "the graph's Corfu is the island (Wikidata Q121378), and Dio's Corcyra is reused as it; "
     "the town, with its Fresh Harbour, is Pleiades 530834"),
    ("Toryne", "chr:observation:perseus:tlg0007.tlg058.perseus-eng2:62.3:70427323", "a place in Epeirus called Torun", "531127",
     "Toryne?", "Pleiades marks the location uncertain"),
    ("Leucas", "chr:observation:lacuscurtius:cassius-dio:50.13.5:1f50fd6b", "captured Leucas", "530974",
     "Leucas", "the town Agrippa took with the ships there; the island is Pleiades 530975"),
    ("Methone", "chr:observation:lacuscurtius:cassius-dio:50.11.3:1f50fd6b", "captured Methone", "570483",
     "Methone/Mothone (Messenian)", "the Messenian Methone, on the route from Egypt; Pleiades has five places of the name"),
    ("Taenarum", "chr:observation:perseus:tlg0007.tlg058.perseus-eng2:67.6:70427323", "from Taenarum", "570702",
     "Tainaron (settlement)", "the port, for a crossing to Libya; the cape is Pleiades 570703"),
    ("Paraetonium", "chr:observation:perseus:tlg0007.tlg058.perseus-eng2:69.1:70427323", "from Paraetonium", "716615",
     "Paraetonium/Ammonia", "the only Pleiades place of the name"),
]


def quotation(tx, observation: str, phrase: str) -> str:
    """The phrase as the stored passage has it, extended to the end of its last word (Torun -> Torunê)."""
    text = tx.run("MATCH (o:SourceObservation {id: $id}) RETURN o.passageText AS t", id=observation).single()["t"]
    start = text.index(phrase)
    end = start + len(phrase)
    while end < len(text) and (text[end].isalpha()):
        end += 1
    return text[start:end]


def migrate(tx, operations) -> dict:
    metadata = json.loads((DUMP.parent / "metadata.json").read_text(encoding="utf-8"))["files"][DUMP.name]
    report = []
    for label, observation, phrase, pid, title, why in PLACES:
        location = f"chr:location:pleiades:{pid}"
        if not tx.run("MATCH (x:Location {id: $id}) RETURN count(x) AS n", id=location).single()["n"]:
            raise SystemExit(f"no Location {location}: load the gazetteer first")
        quote = quotation(tx, observation, phrase)
        entity = propose_entity(tx, operations, kind="Place", label=label, proposed_by=BY, observation_id=observation,
                                quotation=quote, note=f"Place named as \"{label}\" (the Actium scene)")
        run_write(tx, operations, "upsert_authority", {
            "entityId": entity["id"], "id": f"chr:authority:pleiades:{pid}", "system": "Pleiades", "identifier": pid,
            "label": f"{title} in Pleiades (Pleiades {pid})", "shortLabel": f"Pleiades: {title}",
            "description": f"Pleiades place {pid}, {title} (CC BY 3.0), from the Pleiades dump of {metadata['lastModified'][:10]}. Chosen for {label}: {why}.",
            "retrievedAt": metadata["retrievedAt"], "sourceUri": f"https://pleiades.stoa.org/places/{pid}",
            "sourceRevision": None, "contentHash": metadata["sha256"],  # an integer revision is Wikidata's; the dump has none
            "rawPayloadUri": DUMP.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
            "role": "crosswalk", "relation": "closeMatch", "linkStatus": "proposed",
        })
        run_write(tx, operations, "link_place_locations", {"rows": [
            {"entity": entity["id"], "location": location, "status": "proposed", "basis": f"Pleiades {pid} (crosswalk)"}]})
        report.append({"place": label, "entity": entity["id"], "created": entity["created"], "pleiades": pid,
                       "quotation": quote, "nearby": [c["label"] for c in entity["candidates"]][:3]})
    return {"places": report}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(localdb.uri(), auth=localdb.auth(), notifications_min_severity="OFF")
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                report = migrate(tx, load_operations())
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print("applied" if args.apply else "dry run, rolled back")
    print(json.dumps(report, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
