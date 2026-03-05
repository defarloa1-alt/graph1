"""
bio_context_harvest.py — thin wrapper for Biographic Subject Agent

DEPRECATED: Use the consolidated package instead:
    python -m scripts.agents.biographic --dprr 1976
    python -m scripts.agents.biographic --all

This script remains for backward compatibility when run from scripts/.
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from scripts.agents.biographic.cli import main

if __name__ == "__main__":
    main()
