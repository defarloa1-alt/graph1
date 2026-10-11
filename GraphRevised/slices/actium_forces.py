"""Add the forces at Actium as local Group entities and put them in the inquiry's scope.

    python -m GraphRevised.slices.actium_forces

The forces have no Wikidata records; they are provisional local analytical
entities, structured as Plutarch describes the battle line (Antony 65-66).
Commands in that narrative are at wing level, so each fleet's wings are
separate entities. Idempotent.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations
from GraphRevised.slices.add_entity import persist_local_entity

GRAPH_REVISED = Path(__file__).resolve().parents[1]
INQUIRY_PATH = GRAPH_REVISED / "inquiries" / "actium-plutarch-antony.json"
SOURCE_NOTE = "Local analytical entity: a force at the Battle of Actium as described by Plutarch, Antony 65-66."

FORCES = [
    ("octavian-fleet-at-actium", "Octavian's fleet at Actium"),
    ("octavian-fleet-at-actium-left-wing", "Left wing of Octavian's fleet at Actium"),
    ("octavian-fleet-at-actium-centre", "Centre of Octavian's fleet at Actium"),
    ("octavian-fleet-at-actium-right-wing", "Right wing of Octavian's fleet at Actium"),
    ("antony-fleet-at-actium", "Antony's fleet at Actium"),
    ("antony-fleet-at-actium-left-wing", "Left wing of Antony's fleet at Actium"),
    ("antony-fleet-at-actium-centre", "Centre of Antony's fleet at Actium"),
    ("antony-fleet-at-actium-right-wing", "Right wing of Antony's fleet at Actium"),
    ("cleopatra-squadron-at-actium", "Cleopatra's squadron at Actium"),
    ("octavian-army-at-actium", "Octavian's land army at Actium"),
    ("antony-army-at-actium", "Antony's land army at Actium"),
]

COMMAND_GUIDANCE = (
    "commanded relates a person to a force they led, using the force entities in scope: a fleet, "
    "one wing or the centre of a fleet, Cleopatra's squadron, or a land army. Command of a wing or "
    "the centre is not command of the whole fleet; use the most specific force the passage supports."
)


def main() -> int:
    operations = load_operations()
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            for slug, label in FORCES:
                session.execute_write(
                    persist_local_entity, operations,
                    entity_id=f"chr:entity:{slug}", kind="Group", label=label, description=SOURCE_NOTE,
                )
    finally:
        driver.close()

    inquiry = json.loads(INQUIRY_PATH.read_text(encoding="utf-8"))
    ids = [f"chr:entity:{slug}" for slug, _ in FORCES]
    changed = False
    for entity_id in ids:
        if entity_id not in inquiry["candidateEntityIds"]:
            inquiry["candidateEntityIds"].append(entity_id)
            changed = True
    if COMMAND_GUIDANCE not in inquiry["guidance"]:
        inquiry["guidance"].append(COMMAND_GUIDANCE)
        changed = True
    if changed:
        inquiry["version"] += 1
        INQUIRY_PATH.write_text(json.dumps(inquiry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(FORCES)} forces; inquiry v{inquiry['version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
