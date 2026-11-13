"""Migrate Subject BROADER links to NARROWER_THAN, preserving direction and properties."""

import argparse
import sys

from neo4j import GraphDatabase

from GraphRevised.subject_backbone import local_config


def migrate(tx):
    rows = tx.run(
        "MATCH (child:Subject)-[r:BROADER]->(parent:Subject) "
        "RETURN elementId(r) AS rel_id, elementId(child) AS child_id, "
        "elementId(parent) AS parent_id, properties(r) AS props"
    ).data()
    pairs = [(r["child_id"], r["parent_id"]) for r in rows]
    if len(set(pairs)) != len(pairs):
        raise ValueError("Duplicate BROADER links exist; resolve them before migration.")
    for row in rows:
        existing = tx.run(
            "MATCH (child:Subject)-[r:NARROWER_THAN]->(parent:Subject) "
            "WHERE elementId(child) = $child AND elementId(parent) = $parent "
            "RETURN count(r) AS count",
            child=row["child_id"], parent=row["parent_id"],
        ).single(strict=True)["count"]
        if existing:
            raise ValueError("A NARROWER_THAN link already exists for a BROADER link; resolve the conflict.")
    for row in rows:
        count = tx.run(
            "MATCH (child:Subject)-[old:BROADER]->(parent:Subject) "
            "WHERE elementId(old) = $rel_id AND elementId(child) = $child AND elementId(parent) = $parent "
            "CREATE (child)-[new:NARROWER_THAN]->(parent) SET new = $props "
            "DELETE old RETURN count(new) AS count",
            rel_id=row["rel_id"], child=row["child_id"], parent=row["parent_id"], props=row["props"],
        ).single(strict=True)["count"]
        if count != 1:
            raise RuntimeError("Could not uniquely migrate a BROADER link.")
    return len(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="commit the migration; default is rollback preview")
    args = parser.parse_args(argv)
    config = local_config()
    print(f"Target: {config['uri']}, database {config['database']}")
    try:
        with GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"])) as driver:
            with driver.session(database=config["database"]) as session:
                with session.begin_transaction() as tx:
                    count = migrate(tx)
                    if args.apply:
                        tx.commit()
                    else:
                        tx.rollback()
        print(f"{'Migrated' if args.apply else 'Would migrate'} {count} Subject relationships.")
        return 0
    except (ValueError, RuntimeError) as error:
        print(f"Migration refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
