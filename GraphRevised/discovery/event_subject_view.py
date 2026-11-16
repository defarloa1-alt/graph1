"""Generate a read-only event Subject snapshot from an existing inquiry.

    python -m GraphRevised.discovery.event_subject_view inquiries/<inquiry>.json --output view.json [--section-id chr:subject:...]
"""

import argparse
import json
from pathlib import Path
import sys

from neo4j import GraphDatabase, READ_ACCESS

from GraphRevised.discovery.subject_view import build_with_source_timeline
from GraphRevised.subject_backbone import local_config


def build_event_view(tx, inquiry: dict, section_id: str | None) -> dict:
    if section_id:
        rows = tx.run(
            "MATCH (section:Subject {id: $section})-[:NARROWER_THAN]->"
            "(parent:Subject {id: $parent}) RETURN section.id AS id",
            section=section_id, parent=inquiry["subjectId"],
        ).data()
        if len(rows) != 1:
            raise ValueError(f"Expected exactly one selected child Subject link for {section_id}.")
    return build_with_source_timeline(
        tx, inquiry, subject_id=inquiry["subjectId"],
        focus_id=inquiry["narrativeEventId"], section_id=section_id,
    )


def validate_inquiry(inquiry: object) -> dict:
    if not isinstance(inquiry, dict):
        raise ValueError("Inquiry must be an object.")
    for key, prefix in (("id", "chr:inquiry:"), ("subjectId", "chr:subject:"),
                        ("narrativeEventId", "chr:entity:")):
        value = inquiry.get(key)
        if not isinstance(value, str) or not value.startswith(prefix) or not value[len(prefix):].strip():
            raise ValueError(f"Inquiry requires a valid {key}.")
    sources = inquiry.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("Inquiry requires at least one source.")
    work_ids = []
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("workId"), str) or not source["workId"].startswith("chr:entity:") or not source["workId"][len("chr:entity:"):].strip():
            raise ValueError("Every source requires a valid workId.")
        work_ids.append(source["workId"])
    if len(work_ids) != len(set(work_ids)):
        raise ValueError("Inquiry contains duplicate source work IDs.")
    return inquiry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inquiry", type=Path, help="Existing event inquiry JSON")
    parser.add_argument("--output", type=Path, required=True, help="New JSON path; existing files are not overwritten")
    parser.add_argument("--section-id", help="Explicit child Subject ID for topical placements")
    args = parser.parse_args(argv)
    try:
        inquiry = validate_inquiry(json.loads(args.inquiry.read_text(encoding="utf-8")))
        if args.section_id is not None and (not args.section_id.startswith("chr:subject:") or not args.section_id[len("chr:subject:"):].strip()):
            raise ValueError("Section ID must be a non-empty local Subject ID.")
        config = local_config()
        with GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"])) as driver:
            with driver.session(database=config["database"], default_access_mode=READ_ACCESS) as session:
                view = session.execute_read(
                    lambda tx: build_event_view(tx, inquiry, args.section_id)
                )
        view["viewType"] = "event-subject-view-v1"
        view["inquiryId"] = inquiry["id"]
        with args.output.open("x", encoding="utf-8") as file:
            json.dump(view, file, ensure_ascii=False, indent=2)
            file.write("\n")
        print(f"View written to {args.output}")
        print(json.dumps(view["summary"], indent=2))
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"View failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
