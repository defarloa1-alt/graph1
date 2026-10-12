"""Capture a passage chosen while reading: a curator transcription and, optionally, an Annotation.

The quotation is evidence of what the author wrote (a SourceObservation of
kind `transcription`, linked IN_WORK to its Work). The curator's note is
commentary (an Annotation that ANNOTATES the passage and CONCERNS entities).
They are kept apart, as editorial notes are kept apart from an ancient text.
Captures are private by default (23-NARRATIVE-AND-NOTES.md §7).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from GraphRevised.operations import run_write

MAX_QUOTATION = 1500  # quotations from works in copyright are kept short
NOTE_TYPES = ("characterization", "anecdote", "omen", "motive", "speech", "atmosphere", "detail", "interpretation")


class CaptureError(ValueError):
    """A capture was refused before anything was written."""


def transcription_id(work_id: str, locator: str, text: str) -> str:
    digest = hashlib.sha256(f"{locator}\n{text}".encode("utf-8")).hexdigest()[:12]
    return f"chr:observation:transcription:{work_id.split(':', 2)[2]}:{digest}"


def annotation_id(author: str, observation_id: str | None, note: str | None, concerns: list[str]) -> str:
    key = "\n".join([author, observation_id or "", note or "", *sorted(concerns)])
    return f"chr:annotation:{hashlib.sha256(key.encode('utf-8')).hexdigest()[:16]}"


def capture(tx: Any, operations: dict[str, str], item: dict[str, Any]) -> dict[str, Any]:
    """Write one capture. `item` keys: workId, locator, locatorType, quote, and optionally
    note, noteType, concerns, edition, language, sourceSystem, capturedBy, capturedAt,
    visibility, rawPayloadUri, contentHash."""
    quote = " ".join(item["quote"].split())
    if not quote:
        raise CaptureError("an empty quotation")
    if len(quote) > MAX_QUOTATION:
        raise CaptureError(f"a quotation of {len(quote)} characters; keep it under {MAX_QUOTATION}")
    note_type = item.get("noteType") or ("detail" if item.get("note") else None)
    if note_type is not None and note_type not in NOTE_TYPES:
        raise CaptureError(f"note type must be one of {list(NOTE_TYPES)}, not {note_type!r}")
    work = tx.run("MATCH (w:Entity {id: $id, kind: 'Work'}) RETURN w.label AS label", id=item["workId"]).single()
    if work is None:
        raise CaptureError(f"{item['workId']} is not a Work entity; the curator adds Works first")

    captured_at = item.get("capturedAt") or datetime.now(timezone.utc).isoformat()
    visibility = item.get("visibility", "private")
    observation_id = transcription_id(item["workId"], item["locator"], quote)
    run_write(tx, operations, "upsert_transcription_observation", {
        "id": observation_id,
        "workId": item["workId"],
        "label": f"{work['label']}, {item['locator']} (transcription)",
        "shortLabel": f"{work['label']} {item['locator']}",
        "sourceSystem": item.get("sourceSystem", "curator"),
        "locator": item["locator"],
        "locatorType": item["locatorType"],
        "passageText": quote,
        "passageHash": hashlib.sha256(quote.encode("utf-8")).hexdigest(),
        "language": item.get("language", "en"),
        "workTitle": work["label"],
        "author": item.get("author"),
        "editionCitation": item.get("edition") or "edition not recorded",
        "rights": "Short quotation transcribed for study; the work may be in copyright.",
        "visibility": visibility,
        "capturedBy": item.get("capturedBy", "curator"),
        "capturedAt": captured_at,
        "contentHash": item.get("contentHash") or hashlib.sha256(quote.encode("utf-8")).hexdigest(),
        "rawPayloadUri": item.get("rawPayloadUri"),
    })

    result: dict[str, Any] = {"observationId": observation_id, "annotationId": None}
    concerns = list(item.get("concerns") or [])
    if item.get("note") or concerns:
        concerns = concerns or [item["workId"]]
        author = item.get("capturedBy", "curator")
        result["annotationId"] = annotation_id(author, observation_id, item.get("note"), concerns)
        run_write(tx, operations, "upsert_annotation", {
            "id": result["annotationId"],
            "label": (item.get("note") or quote)[:120],
            "kind": "passage-of-note",
            "noteType": note_type,
            "note": item.get("note"),
            "author": author,
            "visibility": visibility,
            "createdAt": captured_at,
            "observationId": observation_id,
            "quotation": quote,
            "concerns": concerns,
        })
    return result
