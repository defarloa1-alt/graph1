#!/usr/bin/env python3
"""Deprecated wrapper for Roman Republic Pleiades ingest workflow.

Canonical path:
  scripts/backbone/geographic/pleiades_bulk_ingest_roman_republic.py
"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    target = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "backbone"
        / "geographic"
        / "pleiades_bulk_ingest_roman_republic.py"
    )
    runpy.run_path(str(target), run_name="__main__")
