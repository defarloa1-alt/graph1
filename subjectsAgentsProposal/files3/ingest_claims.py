#!/usr/bin/env python3
"""Compatibility wrapper.

Canonical implementation:
  subjectsAgentsProposal/files4/ingest_claims.py
"""

import runpy
import sys
from pathlib import Path


if __name__ == "__main__":
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print("Compatibility wrapper: use subjectsAgentsProposal/files4/ingest_claims.py")
        sys.exit(0)
    target = Path(__file__).resolve().parents[1] / "files4" / "ingest_claims.py"
    runpy.run_path(str(target), run_name="__main__")
