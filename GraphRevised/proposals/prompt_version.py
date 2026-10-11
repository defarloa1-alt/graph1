"""Prompt versions that cannot drift from the prompt text.

A version is a human label plus a digest of everything that shapes what the
model sees: the system prompt and the code that builds the task packet. Any
edit changes the digest, so every Proposal records the prompt actually used,
even if nobody remembers to bump the label.
"""

from __future__ import annotations

import hashlib
import inspect
from typing import Any


def prompt_version(label: str, *parts: Any) -> str:
    """`label-<8 hex>` over the given strings and the source of the given functions."""
    texts = [part if isinstance(part, str) else inspect.getsource(part) for part in parts]
    digest = hashlib.sha256("\x1f".join(texts).encode("utf-8")).hexdigest()[:8]
    return f"{label}-{digest}"
