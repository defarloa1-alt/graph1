"""The Actium campaign as a movement scene (26a shape 7), drawn from the checked animation.

    python -m GraphRevised.scenes.actium_campaign_31bc

Writes scenes/actium-campaign-31bc.proposed.json. Source: docs/Actium/Actium Campaign and Battle, 31 BC
(Animated Terrain Map).html, made by Claude in a chat (curator, 2026-11-24), checked against the stored
passages (docs/Actium/animation-check.md). Every statement carries its basis; every quotation is read from
the graph (SourceObservation passage text) and must be a verbatim substring of it, or the build stops.
Places and their coordinates come from the export (exports/graph.cyjs, run the export first).
Read-only on the graph.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from GraphRevised import localdb

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "scenes" / "actium-campaign-31bc.proposed.json"
WORKS = ["chr:entity:plutarch-life-of-antony", "chr:entity:cassius-dio-roman-history",
         "chr:entity:proposed-work-velleius-paterculus-historiae-romanae", "chr:entity:wikipedia-en-battle-of-actium"]


def read_passages() -> dict:
    """The passages of the three Works, by short label ("Cassius Dio 50.13.5")."""
    driver = localdb.driver()
    try:
        with driver.session(database=localdb.database()) as session:
            rows = session.run("""
                MATCH (o:SourceObservation)-[:IN_WORK]->(w:Entity) WHERE w.id IN $works
                RETURN w.id AS workId, w.label AS work, o.id AS obs, o.shortLabel AS loc, o.passageText AS text,
                       o.locator AS href""", works=WORKS).data()
    finally:
        driver.close()
    return {r["loc"]: r for r in rows}


IDX: dict = read_passages() if __name__ == "__main__" else {}

GEN = "the animation's generator (Claude, in a chat, from Wikipedia and its own knowledge)"
CHK = "the check of 2026-11-24 (Claude Code, against the stored passages)"


def q(loc, phrase):
    """A quotation: the stored passage at loc must contain phrase word for word."""
    x = IDX[loc]
    if phrase not in x["text"]:
        raise SystemExit(f"not verbatim in {loc}: {phrase!r}")
    return {"accordingTo": x["work"], "work": x["workId"], "observation": x["obs"], "locator": loc,
            "url": x.get("href"), "quotation": phrase}


def s(text, basis, evidence=(), by=None, note=None):
    out = {"text": text, "basis": basis, "voices": list(evidence)}
    if by:
        out["by"] = by
    if note:
        out["note"] = note
    return out


# places: held entities where we have them; the rest named, with the animation's point, until the gazetteer holds them
EXPORT = json.loads((ROOT / "exports" / "graph.cyjs").read_text(encoding="utf-8"))
NODES = {e["data"]["id"]: e["data"] for e in EXPORT["elements"]["nodes"]}
QUESTION_LABELS = {i: n.get("label") for i, n in NODES.items() if "question" in i}


def place(label, lon, lat, entity=None, name_of_the_time=None):
    node = NODES.get(entity) if entity else None
    c = (node or {}).get("coordinates")
    p = {"label": name_of_the_time or label, "lonLat": [c["lon"], c["lat"]] if c else [lon, lat],
         "lonLatFrom": f"the place's card ({c['source']})" if c else "the animation (unverified)"}
    if entity:
        p["entity"] = entity
        p["status"] = (node or {}).get("status")
        if node and node.get("label") != p["label"]:
            p["heldAs"] = node.get("label")
    else:
        p["held"] = False
    return p


PLACES = {
    "Brundisium": place("Brundisium", 17.94, 40.64, "chr:entity:proposed-place-brundisium"),
    "Corcyra": place("Corfu", 19.92, 39.62, "chr:entity:corfu", "Corcyra"),
    "Toryne": place("Toryne", 20.40, 39.29, "chr:entity:proposed-place-toryne"),
    "Actium": place("Actium promontory", 20.77, 38.95, "chr:entity:actium-promontory", "Actium"),
    "Octavian's camp": place("Octavian's camp at Actium", 20.735, 39.03, "chr:entity:octavian-camp-at-actium"),
    "Leucas": place("Leucas", 20.71, 38.80, "chr:entity:proposed-place-leucas"),
    "Patrae": place("Patras", 21.73, 38.25, "chr:entity:patras", "Patrae"),
    "Corinth": place("Ancient Corinth", 22.88, 37.91, "chr:entity:ancient-corinth", "Corinth"),
    "Methone": place("Methone", 21.70, 36.82, "chr:entity:proposed-place-methone"),
    "Taenarum": place("Taenarum", 22.48, 36.39, "chr:entity:proposed-place-taenarum"),
    "Paraetonium": place("Paraetonium", 27.23, 31.35, "chr:entity:proposed-place-paraetonium"),
    "Alexandria": place("Alexandria", 29.92, 31.20, "chr:entity:alexandria"),
}

U = {  # units; Octavian is held under his later name (names over time, not built)
    "Octavian": {"entity": "chr:entity:augustus", "label": "Octavian", "heldAs": "Augustus", "side": "Octavian"},
    "Agrippa": {"entity": "chr:entity:marcus-vipsanius-agrippa", "label": "Agrippa", "side": "Octavian"},
    "Antony": {"entity": "chr:entity:mark-antony", "label": "Antony", "side": "Antony"},
    "Cleopatra": {"entity": "chr:entity:cleopatra", "label": "Cleopatra", "side": "Antony"},
    "OL": {"entity": "chr:entity:octavian-fleet-at-actium-left-wing", "label": "Left wing of Octavian's fleet", "side": "Octavian"},
    "OC": {"entity": "chr:entity:octavian-fleet-at-actium-centre", "label": "Centre of Octavian's fleet", "side": "Octavian"},
    "OR": {"entity": "chr:entity:octavian-fleet-at-actium-right-wing", "label": "Right wing of Octavian's fleet", "side": "Octavian"},
    "AR": {"entity": "chr:entity:antony-fleet-at-actium-right-wing", "label": "Right wing of Antony's fleet", "side": "Antony"},
    "AC": {"entity": "chr:entity:antony-fleet-at-actium-centre", "label": "Centre of Antony's fleet", "side": "Antony"},
    "AL": {"entity": "chr:entity:antony-fleet-at-actium-left-wing", "label": "Left wing of Antony's fleet", "side": "Antony"},
    "CL": {"entity": "chr:entity:cleopatra-squadron-at-actium", "label": "Cleopatra's squadron", "side": "Antony"},
    "AN": {"entity": "chr:entity:mark-antony", "label": "Antony's ship", "side": "Antony"},
    "army": {"entity": "chr:entity:antony-army-at-actium", "label": "Antony's land army at Actium", "side": "Antony"},
}


def leg(unit, frm, to, basis, via=(), note=None):
    out = {"unit": U[unit], "from": PLACES[frm], "to": PLACES[to], "basis": basis}
    if via:
        out["via"] = [PLACES[v] for v in via]
    if note:
        out["note"] = note
    return out


# the animation's squadron lines (lon, lat pairs), each an illustrative placement: no passage gives a position
L0 = {"OL": [[20.693, 38.966], [20.700, 38.950]], "OC": [[20.702, 38.946], [20.712, 38.925]], "OR": [[20.714, 38.921], [20.728, 38.900]],
      "AR": [[20.712, 38.958], [20.719, 38.946]], "AC": [[20.721, 38.943], [20.731, 38.926]], "AL": [[20.733, 38.923], [20.745, 38.910]],
      "CL": [[20.737, 38.940], [20.745, 38.931]], "AN": [[20.714, 38.954], [20.716, 38.950]]}
LX = {**L0, "OL": [[20.668, 38.972], [20.682, 38.955]], "AR": [[20.688, 38.966], [20.700, 38.952]], "AN": [[20.692, 38.962], [20.696, 38.958]],
      "OC": [[20.708, 38.944], [20.718, 38.926]], "AC": [[20.722, 38.940], [20.731, 38.924]], "AL": [[20.722, 38.921], [20.733, 38.905]],
      "OR": [[20.710, 38.918], [20.723, 38.897]]}
LE = {**L0, "OL": [[20.684, 38.968], [20.706, 38.957]], "AR": [[20.696, 38.962], [20.708, 38.952]], "OC": [[20.710, 38.944], [20.738, 38.928]],
      "AC": [[20.722, 38.940], [20.731, 38.926]], "AL": [[20.725, 38.920], [20.735, 38.906]], "OR": [[20.716, 38.922], [20.744, 38.904]],
      "CL": [[20.655, 38.872], [20.660, 38.862]], "AN": [[20.660, 38.876], [20.663, 38.868]]}


def placements(lines, why):
    return [{"unit": U[k], "line": v, "basis": "illustrative", "note": why} for k, v in lines.items()]


Q_PLANNED = "chr:entity:proposed-question-did-cleopatra-and-perhaps-antonius-too-secretly-plan-the-flight-before-the-battle-began"
Q_GAP = "chr:entity:proposed-question-did-cleopatra-s-squadron-escape-from-the-battle-through-a-gap-in-the-fleets-line"
Q_INIT = "chr:entity:proposed-question-did-cleopatra-take-the-decisive-initiative-in-the-flight-from-actium"

steps = [
    {"order": 1, "phase": "road-to-war", "timeWords": "winter of 32/31 BC", "view": "overview",
     "title": "Antony holds the coast of western Greece",
     "statements": [
         s("Antony sails back to the Peloponnese and winters at Patrae.", "sourced",
           [q("Cassius Dio 50.9.3", "he sailed back to the Peloponnesus, the season being already late autumn, and passed the winter at Patrae")]),
         s("He spreads his soldiers to guard the strategic points and secure provisions.", "sourced",
           [q("Cassius Dio 50.9.3", "distributing his soldiers in every direction in order that they might keep guard over the strategic points and secure more easily an abundance of provisions")]),
         s("Antony's garrisons hold Corcyra.", "sourced", [q("Cassius Dio 50.12.2", "seized Corcyra, which had been deserted by the garrisons there")]),
         s("Antony holds Methone.", "sourced", [q("Cassius Dio 50.11.3", "Agrippa had captured Methone by storm")],
           note="Implied: Agrippa had to take it from Antony."),
         s("The chain of posts guards the supply route from Egypt.", "inferred", by=GEN, note="Dio gives guard and provisions; Egypt as the route is the generator's."),
     ],
     "places": ["Patrae", "Corcyra", "Actium", "Leucas", "Methone", "Corinth"], "legs": []},
    {"order": 2, "phase": "isolation", "timeWords": "before spring 31 BC", "view": "overview",
     "title": "Agrippa storms Methone",
     "statements": [
         s("Agrippa takes Methone by storm and kills Bogud there.", "sourced", [q("Cassius Dio 50.11.3", "Agrippa had captured Methone by storm and killed Bogud there")]),
         s("From there he watches for the merchant ships and raids the coasts of Greece.", "sourced",
           [q("Cassius Dio 50.11.3", "was now watching for the merchant vessels that came to land and was making descents from time to time on various parts of Greece")]),
         s("The merchant ships were grain ships from Egypt.", "inferred", by=GEN, note="Dio says merchant vessels; Egypt and grain are not in the passage."),
     ],
     "legs": [leg("Agrippa", "Brundisium", "Methone", "inferred", note="Dio gives the capture, not the route or the port of departure.")]},
    {"order": 3, "phase": "road-to-war", "timeWords": "spring 31 BC", "view": "overview",
     "title": "Octavian crosses the Adriatic",
     "statements": [
         s("Octavian crosses the Ionian Gulf from Brundisium with his whole force.", "sourced", [q("Cassius Dio 50.11.6", "Thereupon he crossed the Ionian Gulf with the entire array")]),
         s("His cavalry lands at the foot of the Ceraunian mountains.", "sourced", [q("Cassius Dio 50.12.1", "Caesar disembarked the cavalry at the foot of the Ceraunian mountains")]),
         s("He seizes Corcyra, abandoned by its garrisons.", "sourced", [q("Cassius Dio 50.12.2", "seized Corcyra, which had been deserted by the garrisons there")]),
         s("He occupies Toryne in Epirus.", "sourced", [q("Plutarch Antony 62.3", "occupying a place in Epeirus called Torun")]),
         s("He camps on the high ground north of the strait, where Nicopolis later stood.", "sourced",
           [q("Cassius Dio 50.12.3", "He then occupied the site where Nicopolis now stands"), q("Cassius Dio 50.12.4", "took up a position on high ground there")]),
         s("He marches south from Toryne to the camp.", "inferred", by=GEN),
     ],
     "legs": [leg("Octavian", "Brundisium", "Octavian's camp", "inferred", via=["Corcyra", "Toryne"],
                  note="Each place is sourced; the line between them and its order are ours.")]},
    {"order": 4, "phase": "isolation", "timeWords": "summer 31 BC", "view": "overview",
     "title": "Agrippa closes the ring",
     "statements": [
         s("Agrippa takes Leucas, takes Patrae after beating Nasidius at sea, and later takes Corinth.", "sourced",
           [q("Cassius Dio 50.13.5", "Agrippa made a sudden dash with his fleet and captured Leucas and the vessels which were there, took Patrae by conquering Quintus Nasidius in a sea-fight, and later reduced Corinth also"),
            q("C. Velleius Paterculus 2.84.2", "Marcus Agrippa had stormed Leucas, had captured Patrae, had seized Corinth")]),
         s("Antony's forces lose men to disease and desertion.", "sourced",
           [q("Cassius Dio 50.11.2", "their numbers had been diminished by disease and desertions"),
            q("C. Velleius Paterculus 2.84.1", "from Antony to Caesar someone or other was deserting daily")]),
         s("Cut off from bringing in grain, Antony's provisions begin to fail.", "sourced",
           [q("Cassius Dio 50.14.4", "when provisions also began to fail him because he was shut off from bringing in grain")]),
     ],
     "legs": [leg("Agrippa", "Actium", "Leucas", "inferred"), leg("Agrippa", "Leucas", "Patrae", "inferred"),
              leg("Agrippa", "Patrae", "Corinth", "inferred")]},
    {"order": 5, "phase": "deployment", "timeWords": "2 September 31 BC, morning", "view": "battle",
     "title": "The fleets form up outside the strait",
     "statements": [
         s("The battle is fought on 2 September.", "sourced", [q("Cassius Dio 51.1.1", "Such was the naval battle in which they engaged on the second of September")]),
         s("Antony's fleet draws up its line a little outside the strait and comes no further.", "sourced",
           [q("Cassius Dio 50.31.4", "drew up their line a little outside the strait and advanced no further")]),
         s("Antony orders his ships to hold their position at the narrow mouth of the gulf.", "sourced",
           [q("Plutarch Antony 65.3", "to maintain their position at the mouth of the gulf, which was narrow and difficult")]),
         s("Octavian keeps his ships about eight furlongs (some 1.5 km) away, waiting a long time.", "sourced",
           [q("Plutarch Antony 65.4", "kept his own ships at a distance of about eight furlongs from the enemy"),
            q("Cassius Dio 50.31.5", "ordered his sailors to let their oars rest in the water, and waited for a time")],
           note="1.5 km is the conversion; west of Antony's line is the map's."),
         s("Cleopatra's sixty ships lie behind the line.", "sourced",
           [q("Plutarch Antony 66.3", "they had been posted in the rear of the large vessels"),
            q("Cassius Dio 50.33.1", "Cleopatra, riding at anchor behind the combatants")],
           note="Both sources say the rear; 'behind the centre', as the animation had it, is ours, and the map draws it so."),
     ],
     "ordersOfBattle": {
         "title": "Three orders of battle",
         "note": "The sources disagree: two ancient versions and a modern summary that combines them, shown side by side, never merged. The map draws one arrangement: a reconstruction (curator, 2026-11-25).",
         "alternatives": [
             {"accordingTo": "Plutarch, Life of Antony",
              "antony": {"right": ["Antony", "Publicola"], "centre": ["Marcus Octavius", "Marcus Insteius"], "left": ["Coelius"]},
              "octavian": {"left": ["Agrippa"], "right": ["Octavian"]},
              "voices": [q("Plutarch Antony 65.1", "Antony had the right wing, with Publicola, Coelius the left, and in the centre were Marcus Octavius and Marcus Insteius"),
                         q("Plutarch Antony 65.2", "Caesar posted Agrippa on the left, and reserved the right wing for himself")],
              "note": "Plutarch names no commander for Octavian's centre. That Antony's centre engaged Arruntius (66.3) comes later in the fight; it is not his order of battle."},
             {"accordingTo": "Velleius Paterculus, Historiae Romanae",
              "antony": {"fleet": ["Publicola", "Sosius"]},
              "octavian": {"right": ["Lurius"], "left": ["Arruntius"], "overall": ["Agrippa"], "everywhere": ["Octavian"]},
              "voices": [q("C. Velleius Paterculus 2.85.2", "The command of the right wing of Caesar's fleet was entrusted to Marcus Lurius, of the left to Arruntius, while Agrippa had full charge of the entire conflict at sea"),
                         q("C. Velleius Paterculus 2.85.2", "The command of Antony's fleet was entrusted to Publicola and Sosius")],
              "note": "Velleius gives Sosius no wing; the animation's 'Coelius south (Velleius: Sosius)' was its generator's reading."},
             {"accordingTo": "Wikipedia, Battle of Actium (a modern summary)",
              "antony": {"right": ["Antony", "Gellius Poplicola"], "centre": ["Marcus Octavius", "Marcus Insteius"], "left": ["Sosius"]},
              "octavian": {"left": ["Agrippa"], "centre": ["Arruntius"], "right": ["Lurius"]},
              "voices": [q("Wikipedia 2.4", "led by the experienced admiral Agrippa, commanding from the left wing of the fleet, Lucius Arruntius the centre, and Marcus Lurius the right"),
                         q("Wikipedia 2.4", "Marcus Octavius and Marcus Insteius commanded the centre, while Gaius Sosius commanded the left wing")],
              "note": "It combines the two: Plutarch's Antonian right and centre, Velleius's Arruntius and Lurius, and a left wing for Sosius that neither ancient passage held gives."},
         ]},
     "placements": placements(L0, "A reconstruction: one arrangement drawn to orient the reader, while the sources give three orders of battle and no ship's position (D-172).")},
    {"order": 6, "phase": "engagement", "timeWords": "the sixth hour (about midday)", "view": "battle",
     "title": "Antony's left wing moves first",
     "statements": [
         s("At the sixth hour, with a wind rising from the sea, Antony's men put their left wing in motion.", "sourced",
           [q("Plutarch Antony 65.4", "it was now the sixth hour, and since a wind was rising from the sea, the soldiers of Antony became impatient at the delay")]),
         s("Octavian orders his right wing to row backwards, to draw them out of the gulf and the narrows.", "sourced",
           [q("Plutarch Antony 65.5", "ordered his right wing to row backwards, wishing to draw the enemy still farther out from the gulf and the narrows")]),
     ],
     "placements": placements({**L0, "AL": [[20.722, 38.921], [20.733, 38.905]], "OR": [[20.706, 38.918], [20.719, 38.896]]},
                              "Positions drawn; the movement itself is sourced (Plutarch 65.4-5).")},
    {"order": 7, "phase": "engagement", "timeWords": "afternoon", "view": "battle",
     "title": "Agrippa stretches the northern wing",
     "statements": [
         s("Agrippa extends his wing to encircle; Publicola advances against him and is cut off from the centre.", "sourced",
           [q("Plutarch Antony 66.3", "as Agrippa was extending the left wing with a view to encircling the enemy, Publicola was forced to advance against him, and so was separated from the centre")]),
         s("Antony's centre falls into confusion, engaging Arruntius.", "sourced", [q("Plutarch Antony 66.3", "The centre falling into confusion and engaging with Arruntius")]),
         s("This happens on the northern side of the battle.", "inferred", by=GEN, note="Agrippa held Octavian's left (Plutarch), which faced north as the fleets lay; the compass point is ours."),
     ],
     "placements": placements(LX, "Positions drawn; the movement itself is sourced (Plutarch 66.3).")},
    {"order": 8, "phase": "breakout", "timeWords": "afternoon", "view": "battle",
     "title": "Cleopatra's squadron breaks out",
     "statements": [
         s("Cleopatra's sixty ships hoist their sails and make off through the midst of the fighting.", "sourced",
           [q("Plutarch Antony 66.3", "suddenly the sixty ships of Cleopatra were seen hoisting their sails for flight and making off through the midst of the combatants")]),
         s("They take advantage of the wind and make for the Peloponnese.", "sourced", [q("Plutarch Antony 66.4", "they took advantage of the wind and made for Peloponnesus")]),
         s("She turns to flight from the strain of waiting, and signals her ships.", "sourced",
           [q("Cassius Dio 50.33.2", "she suddenly turned to flight herself and raised the signal for the others")],
           note="Dio's reading: panic. Whether the flight was planned is a debated Question in the graph."),
         s("Velleius puts it on her: Cleopatra took the initiative in the flight, and Antony chose to go with her rather than stay with his fighting men.", "sourced",
           [q("C. Velleius Paterculus 2.85.3", "Cleopatra took the initiative in the flight; Antony chose to be the companion of the fleeing queen rather than of his fighting soldiers")],
           note="One interpretation: the victors' side of the story, told by a soldier of the next reign. Shown beside Dio's panic and the planned-breakout reading, not over them."),
     ],
     "disputed": {"words": "Panic, her initiative, or a planned breakout?", "questions": [Q_PLANNED, Q_INIT, Q_GAP]},
     "locatorNote": "The animation cited Plutarch 66.5 in another edition's numbering; in the text we hold it is 66.3-4.",
     "placements": placements({**LX, "AC": [[20.724, 38.938], [20.735, 38.922]], "CL": [[20.700, 38.930], [20.706, 38.912]]},
                              "The breakout is sourced; the path drawn through the line is ours.")},
    {"order": 9, "phase": "antony-follows", "timeWords": "afternoon", "view": "battle",
     "title": "Antony follows her",
     "statements": [
         s("Antony leaves the fight in a five-oared galley, with only Alexas the Syrian and Scellius, and goes after her.", "sourced",
           [q("Plutarch Antony 66.5", "got into a five-oared galley, where Alexas the Syrian and Scellius were his only companions, and hastened after the woman")]),
         s("Dio: he thought her ships fled from fear, not at her bidding, and so followed.", "sourced",
           [q("Cassius Dio 50.33.3", "Antony thought they were fleeing, not at the bidding of Cleopatra, but through fear because they felt themselves vanquished, and so he followed them")]),
         s("The fleet left behind loses its commander.", "inferred", by=CHK),
     ],
     "corrected": [{"was": "The fleet loses its commander, its reserve and its treasury.",
                    "why": "Dio says the money was still aboard the ships left fighting: Octavian held back from fire to gain it.",
                    "voices": [q("Cassius Dio 50.34.1", "Previously he had wished to avoid using it, in order to gain possession of the money"),
                               q("Cassius Dio 50.35.5", "in the hope that they might possibly gain possession of the money")]}],
     "disputed": {"words": "Desertion, or a planned escape?", "questions": [Q_PLANNED]},
     "locatorNote": "The animation cited Plutarch 66.7; in the text we hold it is 66.5.",
     "placements": placements({**LX, "AR": [[20.690, 38.964], [20.702, 38.950]], "AC": [[20.724, 38.938], [20.735, 38.922]],
                               "CL": [[20.668, 38.884], [20.676, 38.868]], "AN": [[20.680, 38.900], [20.684, 38.890]]},
                              "Positions drawn.")},
    {"order": 10, "phase": "fleet-defeat", "timeWords": "late afternoon, to the tenth hour", "view": "battle",
     "title": "The fleet left behind is destroyed",
     "statements": [
         s("With the fight still even, Octavian sends to the camp for fire.", "sourced",
           [q("Cassius Dio 50.34.1", "As the fight continued equal, Caesar, at a loss what he should do, sent for fire from the camp")]),
         s("His ships attack from many sides with blazing missiles, torches and pots of charcoal and pitch.", "sourced",
           [q("Cassius Dio 50.34.2", "The assailants would approach their victims from many directions at once")]),
         s("Antony's fleet holds out until the tenth hour, worn down by a rising sea; three hundred ships are captured.", "sourced",
           [q("Plutarch Antony 68.1", "only after it had been most severely damaged by the high sea which rose against it did it reluctantly, and at the tenth hour, give up the struggle"),
            q("Plutarch Antony 68.1", "three hundred ships were captured, as Caesar himself has written")],
           note="Plutarch and Dio differ on what ended it: the sea, or the fire. Both are kept."),
     ],
     "placements": placements(LE, "Positions drawn; which ships burned is not known.")},
    {"order": 11, "phase": "army-surrender", "timeWords": "seven days after the battle", "view": "battle",
     "title": "The army goes over without fighting",
     "statements": [
         s("Antony's legions hold together for seven days, ignoring Octavian's messages.", "sourced",
           [q("Plutarch Antony 68.3", "they held together for seven days, paying no heed to the messages which Caesar sent them")]),
         s("Then Canidius runs away by night, and the army goes over to Octavian.", "sourced",
           [q("Plutarch Antony 68.3", "after Canidius their general had run away by night and forsaken the camp, being now destitute of all things and betrayed by their commanders, they went over to the conqueror")]),
     ],
     "corrected": [{"was": "Canidius slips away. After seven days the legions go over.",
                    "why": "Plutarch has the seven days first, and Canidius's flight at their end.", "voices": []}],
     "army": {"unit": U["army"], "at": PLACES["Actium"], "basis": "sourced"},
     "placements": placements(LE, "Positions drawn.")},
    {"order": 12, "phase": None, "context": "after the battle (outside the event's phases)", "timeWords": "September 31 BC", "view": "overview",
     "title": "Flight to Taenarum, then Egypt",
     "statements": [
         s("Antony is taken aboard Cleopatra's ship.", "sourced", [q("Plutarch Antony 67.1", "Antony came up and was taken on board")]),
         s("He means to cross from Taenarum to Libya.", "sourced", [q("Plutarch Antony 67.6", "he purposed to cross from Taenarum to Libya")]),
         s("They go as far as the Peloponnese together; Cleopatra then hastens to Egypt.", "sourced",
           [q("Cassius Dio 51.5.3", "had gone as far as the Peloponnesus together"), q("Cassius Dio 51.5.3", "Cleopatra had hastened to Egypt")]),
         s("Antony reaches the coast of Libya and sends Cleopatra on into Egypt from Paraetonium.", "sourced",
           [q("Plutarch Antony 69.1", "After Antony had reached the coast of Libya and sent Cleopatra forward into Egypt from Paraetonium")]),
         s("Antony is at Paraetonium until the news of Pelusium.", "sourced",
           [q("Cassius Dio 51.10.1", "At the news concerning Pelusium Antony returned from Paraetonium")]),
     ],
     "routes": {
         "note": "Where Cleopatra parted from Antony: the sources differ, and both are kept.",
         "alternatives": [
             {"accordingTo": "Plutarch, Life of Antony", "words": "She went with him to Libya and on into Egypt from Paraetonium.",
              "voices": [q("Plutarch Antony 69.1", "sent Cleopatra forward into Egypt from Paraetonium")]},
             {"accordingTo": "Cassius Dio, Roman History", "words": "From the Peloponnese she hastened to Egypt.",
              "voices": [q("Cassius Dio 51.5.3", "had gone as far as the Peloponnesus together"), q("Cassius Dio 51.5.3", "Cleopatra had hastened to Egypt")]},
         ]},
     "legs": [leg("Antony", "Actium", "Taenarum", "inferred", note="Together on her ship (Plutarch 67.1); the route is ours."),
              leg("Antony", "Taenarum", "Paraetonium", "inferred", note="Plutarch 67.6, 69.1: Taenarum, then Libya; the line is ours."),
              {**leg("Cleopatra", "Paraetonium", "Alexandria", "inferred"), "accordingTo": "Plutarch (69.1)"},
              {**leg("Cleopatra", "Taenarum", "Alexandria", "inferred"), "accordingTo": "Dio (51.5.3)"}]},
    {"order": 13, "phase": None, "context": "the end of the war (another event)", "timeWords": "1 August 30 BC", "view": "overview",
     "title": "Alexandria falls",
     "statements": [
         s("Antony's fleet goes over to Octavian before Alexandria.", "sourced",
           [q("Plutarch Antony 76.1", "on their returning the salute changed sides"),
            q("Cassius Dio 51.10.4", "Cleopatra, upon perceiving this, caused the ships to desert")],
           note="Plutarch tells it as the crews' own choice; Dio has Cleopatra cause it. Both are kept."),
         s("His cavalry deserts, his infantry is beaten, and he retires into the city.", "sourced",
           [q("Plutarch Antony 76.2", "he was deserted by his cavalry, which went over to the enemy, and after being defeated with his infantry he retired into the city")]),
         s("Told that Cleopatra is dead, Antony wounds himself, and dies with her in the tomb.", "sourced",
           [q("Plutarch Antony 76.3", "Antony believed the message"), q("Cassius Dio 51.10.7", "gave himself a wound and fell upon his face"),
            q("Cassius Dio 51.10.9", "So Antony died there in Cleopatra's bosom")]),
         s("Octavian drives into the city.", "sourced", [q("Plutarch Antony 80.1", "And now Caesar himself drove into the city")]),
         s("The city fell on 1 August 30 BC.", "not-checked", by=GEN,
           note="No passage read gives the date. Dio 51.19.6 says the day of the capture was declared a lucky day, without naming it."),
         s("Cleopatra dies; Octavian admires her spirit and has her buried with Antony.", "sourced",
           [q("Plutarch Antony 86.4", "he gave orders that her body should be buried with that of Antony in splendid and regal fashion")]),
         s("Octavian now holds all power alone.", "sourced", [q("Cassius Dio 51.1.1", "Caesar now for the first time held all the power alone")],
           note="Dio dates this from Actium, not from Alexandria."),
     ],
     "legs": []},
]

scene = {
    "id": None,
    "type": "movement",
    "subject": {"id": "chr:entity:battle-of-actium", "label": "Battle of Actium", "kind": "Event"},
    "scope": "the campaign around the battle: steps 1-4 lead to it, 12-13 follow it and belong to other events",
    "sequenceBy": "order",
    "status": "proposed",
    "proposedBy": "Claude Code (for the curator)",
    "proposedAt": "2026-11-24",
    "derivedFrom": {
        "file": "docs/Actium/Actium Campaign and Battle, 31 BC (Animated Terrain Map).html",
        "madeBy": "Claude, in a chat, from the Wikipedia article 'Battle of Actium' and its own knowledge (curator, 2026-11-24)",
        "note": "Most of its detail is not in the revision we hold (1378178531); its locators were claimed, not read. Each statement below was checked against the stored passages.",
        "check": "docs/Actium/animation-check.md",
        "builtBy": "scenes/actium_campaign_31bc.py (quotations read from the graph and checked verbatim)",
    },
    "bases": {
        "sourced": "a stored passage says it; the quotation is verbatim",
        "inferred": "joined up from sourced points; 'by' says whose inference",
        "illustrative": "drawn so the picture reads; no passage (a Generalized Abstraction, D-172)",
        "not-checked": "the passage it rests on is not held yet; 'by' says who asserted it",
    },
    "layers": ["terrain", "places", "unitPaths", "labels", "orderOfBattle"],
    "terrain": {"source": "modern", "note": "Coastlines: Natural Earth (public domain) and OpenStreetMap (ODbL, attribution and share-alike); elevation: Mapzen terrain tiles (SRTM and others). The ancient shore near the strait differed (26a, question 4)."},
    "places": PLACES,
    "steps": steps,
    "footnote": "Not in the scene: the council before the battle (phase 'council'). The date of Alexandria's fall is in no passage held. Places added for the scene (proposed, migration 035): Brundisium, Toryne, Leucas, Methone, Taenarum, Paraetonium; Corcyra is the graph's Corfu (the island).",
}
scene["id"] = "chr:scene:actium-campaign-31bc"
# stable keys for anything keyed to the scene (narration, captions): a step is "<scene>#<order>", a statement
# "<scene>#<order>.<n>"; the content hash changes whenever a word of the scene does, so a keyed narration can
# tell it was written for another version
for st in steps:
    st["id"] = f"{scene['id']}#{st['order']}"
    for n, x in enumerate(st["statements"], 1):
        x["id"] = f"{scene['id']}#{st['order']}.{n}"
scene["contentHash"] = hashlib.sha256(json.dumps(scene, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(scene, ensure_ascii=False, indent=1), encoding="utf-8")

# what a narrator reads (scenes/NARRATION.md §2): the scene without the map's coordinates, which are never narrated
STEP_FIELDS = ("id", "order", "title", "timeWords", "view", "phase", "context", "statements", "ordersOfBattle", "routes",
               "disputed", "corrected")
VOICE_FIELDS = ("accordingTo", "locator", "quotation")


def trim_voices(x):
    return {**x, "voices": [{k: v[k] for k in VOICE_FIELDS} for v in x.get("voices", [])]}


narration_input = {
    "about": "Input for narration: see scenes/NARRATION.md. Key every line to statement ids; record contentHash.",
    **{k: scene[k] for k in ("id", "contentHash", "scope", "status", "bases")},
    "subject": scene["subject"]["label"],
    "steps": [],
}
for st in steps:
    out = {k: st[k] for k in STEP_FIELDS if st.get(k) is not None}
    out["statements"] = [trim_voices(x) for x in st["statements"]]
    for key in ("ordersOfBattle", "routes"):
        if key in out:
            out[key] = {**out[key], "alternatives": [trim_voices(a) for a in out[key]["alternatives"]]}
    if "corrected" in out:
        out["corrected"] = [trim_voices(c) for c in out["corrected"]]
    if "disputed" in out:
        out["disputed"] = {"words": out["disputed"]["words"],
                           "questions": [{"id": q, "label": QUESTION_LABELS.get(q, q)} for q in out["disputed"]["questions"]]}
    narration_input["steps"].append(out)
NARRATION_INPUT = OUT.with_name(OUT.name.replace(".proposed.json", ".narration-input.json"))
NARRATION_INPUT.write_text(json.dumps(narration_input, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", NARRATION_INPUT)
counts = {}
for st in steps:
    for x in st["statements"]:
        counts[x["basis"]] = counts.get(x["basis"], 0) + 1
print("wrote", OUT, counts)
