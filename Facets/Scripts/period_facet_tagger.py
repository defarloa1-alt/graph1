#!/usr/bin/env python3
"""Deprecated wrapper for the canonical temporal facet tagger.

Canonical path:
  scripts/backbone/temporal/period_facet_tagger.py
"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    target = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "backbone"
        / "temporal"
        / "period_facet_tagger.py"
    )
    runpy.run_path(str(target), run_name="__main__")
