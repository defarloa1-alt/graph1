#!/usr/bin/env python3
"""Deprecated wrapper for canonical temporal hierarchy migration.

Canonical path:
  scripts/backbone/temporal/migrate_temporal_hierarchy_levels.py
"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    target = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "backbone"
        / "temporal"
        / "migrate_temporal_hierarchy_levels.py"
    )
    runpy.run_path(str(target), run_name="__main__")
