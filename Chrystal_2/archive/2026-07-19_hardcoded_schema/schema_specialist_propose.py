#!/usr/bin/env python3
"""DEPRECATED — hardcoded heuristics; NOT the Schema Specialist.

See chrystal_2/architecture/SCHEMA_SPECIALIST.md.

This script must not be used to produce authoritative proposals.
Kept only so old paths fail loudly.
"""

from __future__ import annotations

import sys


def main() -> int:
    print(
        "DEPRECATED: schema_specialist_propose.py is hardcoded heuristics.\n"
        "Use the Schema Specialist agent (architecture/SCHEMA_SPECIALIST.md).\n"
        "Do not treat JSON/wikidata/packs/*_schema_proposal.json from this\n"
        "script as authoritative.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
