"""Preview an inquiry's graph context without model calls or graph writes."""

import argparse
import json
from pathlib import Path

from neo4j import GraphDatabase, READ_ACCESS

from GraphRevised.proposals.passage_reader import load_inquiries
from GraphRevised.subject_backbone import local_config


def build_review(tx, path: Path) -> dict:
    inquiries = load_inquiries(path, tx, briefs=None)
    if not inquiries:
        raise ValueError("The inquiry has no sources.")
    inquiry = inquiries[0]
    if inquiry.graph_context is None:
        raise ValueError("Graph review requires an event inquiry with computed scope and reading rules.")
    return {
        "inquiryId": inquiry.id,
        "inquiryVersion": inquiry.version,
        "subject": inquiry.subject,
        "focus": inquiry.focus,
        "scope": inquiry.scope,
        "graphContext": inquiry.graph_context,
        "limitations": [
            "Selected graph assertions are context, not evidence from the passage being read.",
            "Assertion status is separate from evidence and proposal review status.",
            "Scope inclusion does not establish participation or identity across events.",
            "Repeated assertions are not necessarily independent corroboration.",
            "All groups require review; other-event participation lists only direct non-depicted event assertions.",
            "This is a preview, not an approval gate or a complete provenance report.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inquiry", type=Path, help="Inquiry JSON, including a Subject with a focus and at least one Work")
    parser.add_argument("--output", type=Path, required=True, help="New JSON path; existing files are not overwritten")
    args = parser.parse_args(argv)
    config = local_config()
    with GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"])) as driver:
        with driver.session(database=config["database"], default_access_mode=READ_ACCESS) as session:
            review = session.execute_read(lambda tx: build_review(tx, args.inquiry))
    with args.output.open("x", encoding="utf-8") as file:
        json.dump(review, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(f"Graph context review written to {args.output}")
    print(f"Entities: {len(review['scope'])}; groups to review: {len(review['graphContext']['groupsToReview'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
