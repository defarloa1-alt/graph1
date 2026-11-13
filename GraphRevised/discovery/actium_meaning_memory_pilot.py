"""Preview the Meaning and memory Subject pilot without changing Neo4j.

    python -m GraphRevised.discovery.actium_meaning_memory_pilot --output new-pilot.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from neo4j import GraphDatabase

from GraphRevised.discovery.actium_subject_view import PHASE_PREFIX, SUBJECT_ID, build_view
from GraphRevised.subject_backbone import local_config

PHASE_ID = PHASE_PREFIX + "meaning-memory"
CHILD_ID = "chr:subject:history-of-battle-of-actium-meaning-and-memory"


def build_pilot(view: dict) -> dict:
    parent_assertions = {}
    candidates = {}
    for assertion in view["assertions"]:
        for route in assertion["routes"]:
            events, placements = route["events"], route["placements"]
            for index, placement in enumerate(placements):
                if events[index]["id"] == PHASE_ID:
                    parent_assertions[placement["id"]] = placement
                if events[index + 1]["id"] == PHASE_ID:
                    item = {
                        "event": events[index],
                        "existingPlacement": placement,
                        "reviewStatus": "unreviewed",
                    }
                    previous = candidates.setdefault(placement["id"], item)
                    if previous != item:
                        raise ValueError(f"Conflicting placement data for {placement['id']}")
    if len(parent_assertions) != 1:
        raise ValueError("Expected one live Meaning and memory phase-to-battle assertion.")
    if not candidates:
        raise ValueError("No existing Meaning and memory placements found.")
    return {
        "purpose": "Read-only pilot inventory; no Subject or placement is created or approved.",
        "candidateSubject": {
            "id": CHILD_ID,
            "label": "Meaning and memory of the Battle of Actium",
            "parentSubjectId": SUBJECT_ID,
            "hierarchyDirection": "candidate child NARROWER_THAN parent",
            "status": "proposed for review",
        },
        "existingPhaseId": PHASE_ID,
        "existingPhaseToBattleAssertion": next(iter(parent_assertions.values())),
        "limitations": [
            "Existing partOf placements are leads for topical review, not approved Subject placements.",
            "This inventory does not say an aftermath event was part of the battle.",
            "Depicted events from different sources remain separate; no identity or corroboration is inferred.",
            "Existing graph assertions, statuses and evidence are unchanged.",
            "A placement relationship and review lifecycle are not implemented or approved by this preview.",
        ],
        "candidateCount": len(candidates),
        "candidates": sorted(candidates.values(), key=lambda item: (item["event"]["label"] or "", item["event"]["id"])),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New JSON path; existing files are not overwritten")
    args = parser.parse_args(argv)
    try:
        config = local_config()
        with GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"])) as driver:
            with driver.session(database=config["database"], default_access_mode="READ") as session:
                pilot = build_pilot(session.execute_read(build_view))
        with args.output.open("x", encoding="utf-8") as file:
            json.dump(pilot, file, ensure_ascii=False, indent=2)
            file.write("\n")
        print(f"Pilot inventory written to {args.output}")
        print(f"{pilot['candidateCount']} candidate placements; no graph writes.")
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"Pilot inventory failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
