"""Prepare preserved source text for a portable research snapshot."""

import re


def include_source_text(row: dict) -> dict:
    """Only redistribute text when its recorded rights explicitly allow it."""
    rights = row.get("rights") or ""
    system = row.get("sourceSystem")
    allowed = (
        (system == "LacusCurtius" and rights.startswith("The text is in the public domain."))
        or (system == "Project Gutenberg" and (
            rights.startswith("Project Gutenberg catalogue: Public domain in the USA.")
            or rights.endswith(" Public domain in the United States.")
        ))
        or (system == "Perseus" and bool(re.match(r"Translation public domain(?: in the US)? \(\d{4}\)", rights))
            and ("CC BY-SA 4.0" in rights or "creativecommons.org/licenses/by-sa/4.0/" in rights))
        or (system == "Perseus" and rights.startswith("Translation public domain in the US (published ")
            and "CC BY-SA 4.0" in rights)
        or (system == "Wikipedia" and rights.startswith("Creative Commons Attribution-Share Alike 4.0 (")
            and "creativecommons.org/licenses/by-sa/4.0/" in rights)
    )
    has_text = bool(row.get("passageText") or row.get("quotation"))
    row["textAvailability"] = "available" if allowed and has_text else (
        "rights-unconfirmed" if has_text else "not-recorded"
    )
    if not allowed:
        row["passageText"] = None
        if "quotation" in row:
            row["quotation"] = None
    return row
