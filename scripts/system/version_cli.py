"""
Version CLI - Command-line interface for Domain subgraph version management.

Domains are versioned top-level subgraphs (roman_republic, military_theory).
SubjectConcepts are organizational units within domains — not versioned here.

Usage:
    python version_cli.py list
    python version_cli.py status roman_republic
    python version_cli.py bump military_theory minor "Added new principles"
    python version_cli.py deps roman_republic
    python version_cli.py history military_theory
"""

import os
import sys
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv
from neo4j import GraphDatabase
from scripts.system.domain_version_manager import DomainVersionManager

load_dotenv()


def cmd_list(manager):
    """List in-scope Domain subgraphs."""
    with manager.driver.session() as session:
        result = session.run("""
            MATCH (d:Domain)
            RETURN d.domain_id AS domain_id, d.label AS label,
                   d.version AS version, d.scope AS scope, d.period AS period
            ORDER BY d.domain_id
        """)
        rows = list(result)
        if not rows:
            print("\n(no Domain nodes found)\n")
            return
        print("\nDomains:")
        for record in rows:
            print(
                f"  {record['domain_id']}: {record['label']} "
                f"v{record['version']} ({record['scope']}, {record['period']})"
            )
        print()


def cmd_status(manager, domain_id):
    """Show current status of a Domain subgraph."""
    with manager.driver.session() as session:
        result = session.run("""
            MATCH (d:Domain {domain_id: $domain_id})
            OPTIONAL MATCH (d)-[:CONTAINS]->(child)
            RETURN
                d.label AS label,
                d.version AS version,
                d.versioned AS versioned,
                d.scope AS scope,
                d.period AS period,
                count(child) AS children
        """, domain_id=domain_id)

        record = result.single()
        if not record:
            print(f"[ERROR] Domain not found: {domain_id}")
            return

        print(f"\n{record['label']} ({domain_id})")
        print(f"  Version: {record['version'] or 'Not versioned'}")
        print(f"  Scope: {record['scope']}")
        print(f"  Period: {record['period']}")
        print(f"  Children: {record['children']}")

        deps = manager.get_dependencies(domain_id)
        if deps:
            print("\n  Dependencies:")
            for dep in deps:
                print(f"    - {dep['dependency']} @ {dep['version_spec']}")

        dependents = manager.get_dependents(domain_id)
        if dependents:
            print("\n  Dependents:")
            for dep in dependents:
                print(f"    - {dep['dependent']} (requires {dep['version_spec']})")

        print()


def cmd_bump(manager, domain_id, bump_type, description):
    """Bump version (major, minor, or patch)."""
    try:
        result = manager.bump_version(
            domain_id,
            bump_type=bump_type,
            description=description
        )

        print(f"\n[OK] {domain_id}: {result['old_version']} -> {result['new_version']}")
        print(f"  Bump: {result['bump_type']}")
        print(f"  Description: {description}\n")

    except Exception as e:
        print(f"[ERROR] {e}\n")


def cmd_deps(manager, domain_id):
    """Show dependency tree."""
    deps = manager.get_dependencies(domain_id)

    print(f"\nDependencies for {domain_id}:")
    if not deps:
        print("  (none)")
    else:
        for dep in deps:
            print(f"  {dep['dependency']} @ {dep['version_spec']}")
            print(f"    Current version: {dep['dep_version']}")

    print()


def cmd_check(manager, domain_id, new_version):
    """Check compatibility before updating."""
    result = manager.check_compatibility(domain_id, new_version)

    print(f"\nCompatibility check: {domain_id} -> {new_version}")
    print(f"  Dependents: {result['dependents_count']}")
    print(f"  Breaking changes: {result['breaking_changes']}")

    if result['issues']:
        print("\n  Issues:")
        for issue in result['issues']:
            status = "[BREAKING]" if issue.get('breaking') else "[WARNING]"
            print(f"    {status} {issue['dependent']}: {issue['issue']}")
    else:
        print("  [OK] No breaking changes")

    print()


def cmd_history(manager, domain_id):
    """Show version history."""
    history = manager.get_version_history(domain_id)

    print(f"\nVersion history for {domain_id}:")
    for v in history:
        print(f"  v{v['version']} - {v['description']}")
        if v.get('changes'):
            for change in v['changes']:
                print(f"    - {change}")

    print()


def cmd_init(manager, domain_id, version, description):
    """Initialize version tracking for a Domain."""
    try:
        result = manager.initialize_version(
            domain_id,
            version=version or "1.0.0",
            description=description
        )

        print(f"\n[OK] Initialized {domain_id} at v{result['version']}\n")

    except Exception as e:
        print(f"[ERROR] {e}\n")


def cmd_link(manager, dependent_id, dependency_id, version_spec):
    """Create dependency link between Domain subgraphs."""
    try:
        result = manager.add_dependency(
            dependent_id,
            dependency_id,
            version_spec=version_spec or "^1.0.0"
        )

        print(f"\n[OK] {result['dependent']} now depends on {result['dependency']}")
        print(f"  Version spec: {result['version_spec']}\n")

    except Exception as e:
        print(f"[ERROR] {e}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Chrystallum Domain Subgraph Version Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command')

    subparsers.add_parser('list', help='List all Domain subgraphs')

    status_parser = subparsers.add_parser('status', help='Show domain status')
    status_parser.add_argument('domain_id', help='Domain ID (e.g. roman_republic)')

    bump_parser = subparsers.add_parser('bump', help='Bump version')
    bump_parser.add_argument('domain_id', help='Domain ID')
    bump_parser.add_argument('type', choices=['major', 'minor', 'patch'], help='Bump type')
    bump_parser.add_argument('description', help='Version description')

    deps_parser = subparsers.add_parser('deps', help='Show dependencies')
    deps_parser.add_argument('domain_id', help='Domain ID')

    check_parser = subparsers.add_parser('check', help='Check compatibility')
    check_parser.add_argument('domain_id', help='Domain ID')
    check_parser.add_argument('version', help='New version to check')

    history_parser = subparsers.add_parser('history', help='Show version history')
    history_parser.add_argument('domain_id', help='Domain ID')

    init_parser = subparsers.add_parser('init', help='Initialize version tracking')
    init_parser.add_argument('domain_id', help='Domain ID')
    init_parser.add_argument('--version', default='1.0.0', help='Initial version')
    init_parser.add_argument('--desc', default='Initial version', help='Description')

    link_parser = subparsers.add_parser('link', help='Create dependency link')
    link_parser.add_argument('dependent', help='Dependent domain')
    link_parser.add_argument('dependency', help='Dependency domain')
    link_parser.add_argument('--spec', default='^1.0.0', help='Version spec')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )

    manager = DomainVersionManager(driver)

    try:
        if args.command == 'list':
            cmd_list(manager)
        elif args.command == 'status':
            cmd_status(manager, args.domain_id)
        elif args.command == 'bump':
            cmd_bump(manager, args.domain_id, args.type, args.description)
        elif args.command == 'deps':
            cmd_deps(manager, args.domain_id)
        elif args.command == 'check':
            cmd_check(manager, args.domain_id, args.version)
        elif args.command == 'history':
            cmd_history(manager, args.domain_id)
        elif args.command == 'init':
            cmd_init(manager, args.domain_id, args.version, args.desc)
        elif args.command == 'link':
            cmd_link(manager, args.dependent, args.dependency, args.spec)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
