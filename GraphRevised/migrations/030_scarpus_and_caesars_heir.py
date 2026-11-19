"""Migration 030 (2026-11-19): Scarpus and Caesar's heir, two men until the curator decides (46 §5).

    python -m GraphRevised.migrations.030_scarpus_and_caesars_heir [--apply]

Doc 46 §5's first case. Before linking our Scarpus to Wikidata, Smith's Dictionary was read: it
gives the heir and the commander **separate entries** (Pinarius no. 5, the great-nephew named in
Caesar's will; "Scarpus, L. Pinarius", Antony's commander at Cyrene) and does not identify them,
while Wikidata's "Lucius Pinarius" (Q382127) merges them (described as Caesar's nephew or
grandnephew, alias "Lucius Pinarius Scarpus"). The curator chose (chat, 2026-11-19) not to link
Scarpus to Q382127 while the question is open. So:

1. **Sources** (all public domain): Smith, *Dictionary of Greek and Roman Biography and Mythology*
   (1870 printing, vol. 3; Wikisource scan pages, not proofread: OCR errors kept, quotations avoid
   them) for the Scarpus entry (p. 735), Pinarius no. 5 and the gens Pinaria (p. 367); Suetonius,
   *Julius* 83.2 (Rolfe, LacusCurtius); Dio 51.9.1 (Cary, LacusCurtius); Plutarch, *Antony* 69.2
   (Perrin, Perseus); and Wikidata's record for Q382127, transcribed as a passage of the Wikidata
   Work (its label, description, alias and cognomen, at the preserved revision).
2. **Two people**: our Scarpus keeps his entity; Caesar's heir is a new Person, "Lucius Pinarius",
   from Suetonius. If the curator rules them one man, that is a merge (D-152).
3. **The Question** "Is the Lucius Pinarius of Caesar's will the Pinarius Scarpus who commanded in
   Cyrenaica?", `about` both. Wikidata's merged item is one voice: the Position "The heir of
   Caesar's will and the commander in Cyrenaica are one man", held by Wikidata. Smith takes no
   position (separate entries are not an argument), so none is drawn for him. No position is ours.
4. **The gens**: "gens Pinaria", a Group of category gens, from Smith's entry; both men `ofGens`
   it according to Smith (the Scarpus family among the Pinarii; no. 5 among "the few Pinarii, who
   occur without a surname").
5. **Gallus**: Gaius Cornelius Gallus, and Dio's "Gallus takes over Scarpus's army" (51.9.1),
   both men taking part, within "Antony follows Cleopatra" like Scarpus's refusal (017). Plutarch's
   "Antony's forces in Libya defect" (69.2) names no general: Scarpus taking part is our reading.
6. Scarpus's description was Wikidata's ("nephew or grandnephew of Julius Caesar"), which assumes
   the answer; it becomes Smith's account of his command.

Name parts and aliases are the next step (addAlias, 46 §4.5). Everything here is a reading and
stays proposed for the curator. Without --apply it reports and rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from neo4j import GraphDatabase

from GraphRevised.adapters import lacuscurtius_passages as lc
from GraphRevised.adapters import perseus_passages as pp
from GraphRevised.adapters import wikisource_pages as ws
from GraphRevised.export.fact_layer import rebuild
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.entities import propose_depicted_event, propose_entity
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import submit
from GraphRevised.slices.add_entity import preserved_identity_payload

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "phase-6-source"
BY = "curator capture (entered by Claude, 2026-11-19)"
SCARPUS = "chr:entity:lucius-pinarius"
DIO = "chr:entity:cassius-dio-roman-history"
PLUTARCH = "chr:entity:plutarch-life-of-antony"
WIKIDATA = "chr:entity:wikidata"
PHASE = "chr:entity:phase:battle-of-actium:antony-follows"
SMITH = {
    "id": "chr:entity:smith-dictionary-of-greek-and-roman-biography",
    "label": "Smith, Dictionary of Greek and Roman Biography and Mythology",
    "shortLabel": "Smith's Dictionary of Greek and Roman Biography",
    "description": ("William Smith (ed.), A Dictionary of Greek and Roman Biography and Mythology, 3 vols. "
                    "(London: John Murray, 1849; read in the 1870 printing). Public domain. Read from the "
                    "Wikisource transcription of the scans."),
}
SMITH_CITATION = "Smith (ed.), Dictionary of Greek and Roman Biography and Mythology, vol. 3 (London, 1870)"
SMITH_RIGHTS = "Public domain (1849; 1870 printing)"
SUETONIUS = {
    "id": "chr:entity:suetonius-life-of-julius-caesar",
    "label": "Suetonius, Life of Julius Caesar",
    "shortLabel": "Suetonius, Julius",
    "description": ("Suetonius, The Lives of the Twelve Caesars, book 1 (the Deified Julius), in J. C. Rolfe's "
                    "translation (Loeb Classical Library, 1913; public domain), as transcribed on LacusCurtius."),
}
SOURCE_NAMES = {"suetonius": "Suetonius, Julius (Rolfe)", "dio": "Cassius Dio, Roman History (Cary)",
                "gens": "Smith, Dictionary of Greek and Roman Biography", "wikidata": "Wikidata",
                "plutarch": "Plutarch, Antony (Perrin)"}
PAGE = "Page:Dictionary of Greek and Roman Biography and Mythology (1870) - Volume 3.djvu/"
QUESTION_LABEL = "Is the Lucius Pinarius of Caesar's will the Pinarius Scarpus who commanded in Cyrenaica?"
POSITION_LABEL = "The heir of Caesar's will and the commander in Cyrenaica are one man"
SCARPUS_DESCRIPTION = ("Antony's commander over Cyrene and the neighbouring country, with four legions, shortly "
                       "before Actium; after the battle he refused Antony and handed his troops to Cornelius "
                       "Gallus (Smith, Dictionary of Greek and Roman Biography, after Dio 51.5 and 51.9). Whether "
                       "he is the Lucius Pinarius of Caesar's will is an open Question.")
HEIR_DESCRIPTION = ("Great-nephew of Julius Caesar, named in his will as an heir with Quintus Pedius to a quarter "
                    "of the estate, Gaius Octavius taking three quarters (Suetonius, Julius 83.2).")


def _register_work(tx, operations, registry, work: dict, form: str, standing: str, at: str) -> None:
    exists = tx.run("MATCH (e:Entity {id: $id}) RETURN e.id", id=work["id"]).single() is not None
    run_write(tx, operations, "upsert_entity", work | {"kind": "Work", "status": None if exists else "provisional"})
    run_write(tx, operations, "set_work_form", {"workId": work["id"], "form": form,
                                                "allowedForms": sorted(registry.work_forms)})
    run_write(tx, operations, "set_work_standing", {"id": work["id"], "standing": standing, "decidedAt": at,
                                                    "decidedBy": "Claude (agent), migration 030; for the curator to check",
                                                    "decisionBasis": {"tertiary": "a reference work",
                                                                      "primary": "an ancient author"}[standing]})


def _passages(tx, operations, at: str) -> dict[str, tuple[str, str]]:
    """Store every passage; return {key: (observation id, text)}."""
    out: dict[str, tuple[str, str]] = {}
    p735, p367 = ws.preserve_page(PAGE + "747", SOURCES), ws.preserve_page(PAGE + "379", SOURCES)
    t735, w367 = ws.plain(ws.page_wikitext(p735)), ws.page_wikitext(p367)
    smith = {
        "scarpus": (p735, "p. 735, s.v. Scarpus, L. Pinarius",
                    ws.between(t735, "SCARPUS, L. PINA'RIUS", "COIN OF L. PINARIUS SCARPUS")),
        "pinarius5": (p367, "p. 367, s.v. Pinarius 5",
                      ws.between(ws.section(w367, "Pinarius"), "5. L. PiNARius", "6. Pinarius")),
        "gens": (p367, "p. 367, s.v. Pinaria Gens", ws.section(w367, "Pinaria Gens")),
    }
    for key, (path, locator, text) in smith.items():
        params = ws.transcription(path, text, work_id=SMITH["id"], work_label=SMITH["label"], locator=locator,
                                  edition_citation=SMITH_CITATION, rights=SMITH_RIGHTS, captured_by=BY, captured_at=at)
        run_write(tx, operations, "upsert_transcription_observation", params)
        out[key] = (params["id"], text)

    for work, page, ref, key in (
            (SUETONIUS["id"], lc.preserve_page("https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Suetonius/12Caesars/Julius*.html", SOURCES), "83.2", "suetonius"),
            (DIO, next(SOURCES.glob("lacuscurtius-cassius-dio-51-html-*.html")), "51.9.1", "dio")):
        passage = lc.passage_observation(lc.load_edition([page]), ref)
        run_write(tx, operations, "upsert_passage_observation", passage)
        run_write(tx, operations, "link_observation_work", {"observationId": passage["id"], "workId": work})
        out[key] = (passage["id"], passage["passageText"])

    path = next((ROOT / "phase-5-source").glob("perseus-tlg0007.tlg058.perseus-eng2-*.xml"))
    metadata = json.loads(path.with_suffix(".metadata.json").read_text(encoding="utf-8"))
    edition = pp.load_edition(path, source_commit=metadata["sourceRevision"], rights=metadata.get("rights"))
    passage = pp.passage_observation(edition, "69.2", retrieved_at=metadata["retrievedAt"], source_uri=metadata["sourceUri"])
    run_write(tx, operations, "upsert_passage_observation", passage)
    run_write(tx, operations, "link_observation_work", {"observationId": passage["id"], "workId": PLUTARCH})
    out["plutarch"] = (passage["id"], passage["passageText"])

    payload_path, md = preserved_identity_payload("Q382127")
    item = json.loads(payload_path.read_bytes())["entities"]["Q382127"]
    aliases = ", ".join(a["value"] for a in item.get("aliases", {}).get("en", []))
    text = (f"{item['labels']['en']['value']} (Q382127): {item['descriptions']['en']['value']}. "
            f"Also known as: {aliases}. Cognomen: Scarpus (Q121088581). Gens: Pinaria gens (Q1453261).")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    params = {"id": f"chr:observation:transcription:wikidata:q382127:{digest[:12]}", "workId": WIKIDATA,
              "label": f"Wikidata record: Lucius Pinarius (Q382127), revision {md['revision']}",
              "shortLabel": "Wikidata: Lucius Pinarius (Q382127)", "sourceSystem": "Wikidata",
              "locator": f"Q382127 revision {md['revision']}", "locatorType": "record", "passageText": text,
              "passageHash": digest, "language": "en", "workTitle": "Wikidata", "author": None,
              "editionCitation": f"Wikidata, Q382127, revision {md['revision']}", "rights": "CC0 1.0 (Wikidata)",
              "visibility": "public", "capturedBy": BY, "capturedAt": at, "contentHash": md["contentHash"],
              "rawPayloadUri": payload_path.resolve().relative_to(ROOT.parent).as_posix(), "footnotes": None}
    run_write(tx, operations, "upsert_transcription_observation", params)
    out["wikidata"] = (params["id"], text)
    return out


def migrate(tx, operations, registry) -> dict:
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    _register_work(tx, operations, registry, SMITH, "reference", "tertiary", at)
    _register_work(tx, operations, registry, SUETONIUS, "biography", "primary", at)
    obs = _passages(tx, operations, at)
    report: dict = {"passages": {k: v[0] for k, v in obs.items()}, "entities": {}, "claims": []}

    def entity(key, kind, label, source, quote, description=None, note=None):
        proposed = propose_entity(tx, operations, kind=kind, label=label, proposed_by=BY, observation_id=obs[source][0],
                                  quotation=quote, source=SOURCE_NAMES[source], note=note)
        if description:
            run_write(tx, operations, "upsert_entity", {"id": proposed["id"], "kind": kind, "label": None,
                                                        "shortLabel": None, "description": description, "status": None})
        report["entities"][key] = {"id": proposed["id"], "created": proposed["created"],
                                   "candidates": [c["id"] for c in proposed["candidates"]]}
        return proposed["id"]

    heir = entity("heir", "Person", "Lucius Pinarius", "suetonius", "Lucius Pinarius and Quintus Pedius to share the remainder",
                  HEIR_DESCRIPTION, note="Caesar's heir; kept apart from Pinarius Scarpus while the identity Question is open.")
    gallus = entity("gallus", "Person", "Gaius Cornelius Gallus", "dio", "Cornelius Gallus had taken over Scarpus' army",
                    "Octavian's commander who took over Scarpus's army and occupied Paraetonium (Dio 51.9.1); later "
                    "prefect of Egypt.")
    gens = entity("gens", "Group", "gens Pinaria", "gens", "The Pinarii are mentioned in the kingly period",
                  "A Roman gens, the Pinarii, hereditary priests of Hercules with the Potitii; its families include "
                  "the Natta, Posca, Rusca and Scarpus (Smith, Dictionary of Greek and Roman Biography).")
    run_write(tx, operations, "set_group_category", {"id": gens, "category": "gens",
                                                     "allowedCategories": sorted(registry.group_categories),
                                                     "decidedAt": at, "decidedBy": BY,
                                                     "decisionBasis": "Smith's entry is headed Pinaria Gens (46 §4.1)"})
    question = entity("question", "Question", QUESTION_LABEL, "suetonius", "Lucius Pinarius and Quintus Pedius to share the remainder")
    position = entity("position", "Position", POSITION_LABEL, "wikidata", "Also known as: Lucius Pinarius Scarpus")
    run_write(tx, operations, "upsert_entity", {"id": SCARPUS, "kind": "Person", "label": None, "shortLabel": None,
                                                "description": SCARPUS_DESCRIPTION, "status": None})

    taking = propose_depicted_event(tx, operations, work_id=DIO, label="Gallus takes over Scarpus's army", voice="Dio",
                                    proposed_by=BY, observation_id=obs["dio"][0],
                                    quotation="Cornelius Gallus had taken over Scarpus' army")["id"]
    defection = propose_depicted_event(tx, operations, work_id=PLUTARCH, label="Antony's forces in Libya defect",
                                       voice="Plutarch", proposed_by=BY, observation_id=obs["plutarch"][0],
                                       quotation="When the general to whom his forces in Libya had been entrusted "
                                                 "brought about their defection")["id"]
    report["entities"].update({"taking": taking, "defection": defection})

    def q(key, text):
        return Quotation(observation_id=obs[key][0], text=text)

    def draft(predicate, subject, obj, quotes, why, work=None, relevance=None):
        return ProposalDraft(predicate=predicate, subject_id=subject, object_id=obj,
                             mode="attributed" if work else "asserted", attributed_to=work,
                             observation_ids=tuple(dict.fromkeys(x.observation_id for x in quotes)), quotations=tuple(quotes),
                             rationale=why, proposed_by=BY, relevance=relevance)

    scarpus_line = q("scarpus", "SCARPUS, L. PINA'RIUS, was placed by Antonius over Cyrene and the neighbouring country with four legions")
    will_line = q("suetonius", "Lucius Pinarius and Quintus Pedius to share the remainder")
    drafts = [
        draft("about", question, heir, [will_line], "The Question asks whether this heir of Caesar's will is Scarpus.",
              relevance="Puts the identity Question on the heir's page."),
        draft("about", question, SCARPUS, [scarpus_line], "The Question asks whether the commander at Cyrene is Caesar's heir.",
              relevance="Puts the identity Question on Scarpus's page."),
        draft("answers", position, question, [q("wikidata", "nephew or grandnephew of Julius Caesar. Also known as: Lucius Pinarius Scarpus")],
              "Wikidata's one item is described as Caesar's kinsman and also named Scarpus: it answers that they are one man.",
              work=WIKIDATA),
        draft("holds", WIKIDATA, position, [q("wikidata", "nephew or grandnephew of Julius Caesar. Also known as: Lucius Pinarius Scarpus")],
              "Wikidata merges the heir and the commander in one item (our reading of the record; it states no argument).",
              work=WIKIDATA),
        draft("ofGens", SCARPUS, gens, [scarpus_line, q("gens", "we find families of the name of Natta, Posca, Rusca, and ScARPUs")],
              "Smith heads the entry 'Scarpus, L. Pinarius' and names the Scarpus family among the Pinarii.", work=SMITH["id"]),
        draft("ofGens", heir, gens, [q("pinarius5", "the great-nephew of the dictator C. Julius Caesar"),
                                     q("gens", "The few Pinarii, who occur without a surname, are given below.")],
              "Smith lists the heir (no. 5) among the Pinarii without a surname, under the gens.", work=SMITH["id"]),
        draft("participatedIn", gallus, taking, [q("dio", "Cornelius Gallus had taken over Scarpus' army")],
              "Dio: Gallus took over Scarpus's army.", work=DIO),
        draft("participatedIn", SCARPUS, taking, [q("dio", "Cornelius Gallus had taken over Scarpus' army")],
              "Dio: it was Scarpus's army that Gallus took over.", work=DIO),
        draft("partOf", taking, PHASE, [q("dio", "Antony learned that Cornelius Gallus had taken over Scarpus' army")],
              "Dio tells it as news reaching Antony after his flight to Egypt, like Scarpus's refusal (017).",
              relevance="Continues the chain: refusal, Gallus takes the army, Antony turns against Gallus."),
        draft("participatedIn", SCARPUS, defection,
              [q("plutarch", "When the general to whom his forces in Libya had been entrusted brought about their defection")],
              "Plutarch names no general; Antony's general in Libya is Scarpus in Dio (51.5, 51.9). Our reading, for the curator.",
              work=PLUTARCH),
    ]
    for d in drafts:
        result = submit(tx, d, registry, operations)
        report["claims"].append({"predicate": d.predicate, "subject": d.subject_id, "object": d.object_id,
                                 "outcome": result.validation.outcome.value, "reasons": list(result.validation.reasons),
                                 "stored": result.stored})
    report["factLayer"] = rebuild(tx)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                report = migrate(tx, load_operations(), load_registry())
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
