"""The Library of Congress catalog: a book's bibliographic record, found by ISBN, LCCN, or subject heading.

    search   SRU, http://lx2.loc.gov:210/lcdb (bath.isbn, bath.lccn, dc.subject): records as pointers
    record   the same service asked for one LCCN: the response preserved byte for byte with its hash

(LC's limits page names https://lccn.loc.gov/<lccn>/marcxml for records; on 2026-10-17 it answered 404
for a current record, and the permalink https://lccn.loc.gov/<lccn> redirects to search.catalog.loc.gov.)

A record is evidence of what LC's catalogers recorded about one edition: its author heading, title
and statement of responsibility, the editions' ISBNs, its call numbers (LCC, DDC), its contents, and
the subject headings LC assigned. It is never evidence of what the book itself says; a summary the
publisher supplied (520 "Provided by publisher") is the publisher's words, never the author's.

Rights (curation/sources.json, `loc-catalog`): LC states no licence for its catalog records; the
curator decided on 2026-10-17 that preserving and citing them is research use. Records are kept in
phase-5-source/ beside the LCSH records and are not published (the repository ignores them).

LC asks programs for no more than 10 requests a minute across its sites (loc.gov/legal): every
request here waits its turn.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from GraphRevised.adapters.wikidata_identity import polite_get

SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / "phase-5-source"
SRU_ENDPOINT = "http://lx2.loc.gov:210/lcdb"
PERMALINK = "https://lccn.loc.gov/{lccn}"
MARC = "{http://www.loc.gov/MARC21/slim}"
SRW = "{http://www.loc.gov/zing/srw/}"
MIN_INTERVAL_SECONDS = 6.0  # 10 requests a minute, LC's guideline for programs
RIGHTS = ("LC states no licence for its catalog records; preserved and cited as research use "
          "(curator, 2026-10-17; curation/sources.json loc-catalog)")

_last_request = 0.0


class CatalogError(ValueError):
    """A malformed identifier, or a response that is not the record asked for."""


def _get(url: str, params: dict[str, Any] | None = None):
    global _last_request
    wait = _last_request + MIN_INTERVAL_SECONDS - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    try:
        return polite_get(url, params=params, timeout=30, attempts=3)
    finally:
        _last_request = time.monotonic()


# --- Identifiers ------------------------------------------------------------------------------------

def isbn_digits(value: str) -> str:
    """The ISBN's digits (and a final X), with hyphens and spaces removed."""
    return re.sub(r"[^0-9Xx]", "", value or "").upper()


def isbn_valid(value: str) -> bool:
    """Whether an ISBN-10 or ISBN-13 passes its check digit."""
    digits = isbn_digits(value)
    if len(digits) == 13 and digits.isdigit():
        return sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(digits)) % 10 == 0
    if len(digits) == 10 and digits[:9].isdigit() and (digits[9].isdigit() or digits[9] == "X"):
        return sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(digits)) % 11 == 0
    return False


def normalize_lccn(value: str) -> str:
    """LC's normalization: blanks removed, anything after a slash dropped, and a hyphenated serial
    padded to six digits ("2021-7113" becomes "2021007113")."""
    lccn = re.sub(r"\s", "", value or "").split("/")[0]
    if "-" in lccn:
        prefix, serial = lccn.split("-", 1)
        lccn = prefix + serial.zfill(6) if serial.isdigit() else lccn
    if not re.fullmatch(r"[a-z]{0,3}\d{8,10}", lccn):
        raise CatalogError(f"LCCN {value!r} is malformed")
    return lccn


# --- The record -------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Heading:
    """A subject or name heading as LC recorded it, in LC's display form ("A--B--C")."""
    tag: str  # 600 person, 610 body, 611 meeting, 630 uniform title, 650 topic, 651 place, 100/700 names
    text: str
    thesaurus: str  # "lcsh" (second indicator 0), or the source named in $2, or "" for names
    dates: str | None = None
    relator: str | None = None


@dataclass(frozen=True)
class CatalogRecord:
    lccn: str
    control_number: str
    isbns: tuple[tuple[str, str | None, bool], ...]  # (digits, qualifier such as "(trade paperback)", cancelled)
    lcc: str | None
    ddc: str | None
    ddc_edition: str | None
    names: tuple[Heading, ...]  # 100 and 700: the author heading first
    title: str
    responsibility: str | None  # 245 $c, as on the title page ("by ...")
    edition: str | None
    publication: str | None  # place : publisher, date
    date: str | None
    extent: str | None
    contents: tuple[str, ...]
    bibliography_note: str | None
    has_index: bool
    language: str | None
    subjects: tuple[Heading, ...]
    publisher_summary: str | None  # never a source's words
    revised: str | None  # 005: the record's last revision
    unmapped_tags: tuple[str, ...] = field(default=())

    def isbn_qualifier(self, isbn: str) -> str | None:
        """The edition an ISBN names in this record, such as "(trade paperback)"."""
        digits = isbn_digits(isbn)
        return next((q for d, q, _ in self.isbns if d == digits), None)


MAPPED = {"001", "005", "008", "010", "020", "050", "082", "100", "245", "250", "260", "264", "300", "504", "505",
          "520", "600", "610", "611", "630", "650", "651", "655", "700"}
SUBJECT_TAGS = {"600", "610", "611", "630", "650", "651"}


def _subfields(datafield: ElementTree.Element) -> list[tuple[str, str]]:
    return [(s.get("code") or "", (s.text or "").strip()) for s in datafield.findall(f"{MARC}subfield")]


def _first(record: ElementTree.Element, tag: str, code: str = "a") -> str | None:
    for datafield in record.findall(f"{MARC}datafield[@tag='{tag}']"):
        for c, value in _subfields(datafield):
            if c == code and value:
                return value
    return None


def _trim(text: str) -> str:
    """Final punctuation that MARC carries between fields (" /", " :", ",", ".") is not part of a value;
    an abbreviation's period (B.C.) stays."""
    text = re.sub(r"\s*[/:;,]\s*$", "", text.strip())
    return text[:-1] if text.endswith(".") and not re.search(r"\b[A-Z]\.$", text) else text


def _name(datafield: ElementTree.Element) -> Heading:
    parts = _subfields(datafield)
    words = [v for c, v in parts if c in "abcq"]
    dates = next((_trim(v) for c, v in parts if c == "d"), None)
    relator = next((_trim(v) for c, v in parts if c == "e"), None)
    text = _trim(" ".join(words) + (f" {dates}" if dates else ""))
    return Heading(tag=datafield.get("tag") or "", text=text, thesaurus="", dates=dates, relator=relator)


def _subject(datafield: ElementTree.Element) -> Heading:
    tag = datafield.get("tag") or ""
    parts = _subfields(datafield)
    ind2 = datafield.get("ind2")
    thesaurus = "lcsh" if ind2 == "0" else next((v for c, v in parts if c == "2"), f"ind2={ind2}")
    main = [v for c, v in parts if c in "abcdq"] if tag in ("600", "610", "611") else [v for c, v in parts if c == "a"]
    divisions = [v for c, v in parts if c in "vxyz"]
    dates = next((_trim(v) for c, v in parts if c == "d"), None) if tag == "600" else None
    text = "--".join([_trim(" ".join(main))] + [_trim(d) for d in divisions])
    return Heading(tag=tag, text=text, thesaurus=thesaurus, dates=dates)


def parse_record(payload: bytes) -> CatalogRecord:
    """A MARCXML record (a bare record, or the first record of an SRU response) read into its parts."""
    root = ElementTree.fromstring(payload)
    record = root if root.tag == f"{MARC}record" else root.find(f".//{MARC}record")
    if record is None:
        raise CatalogError("no MARC record in the payload")
    control = {c.get("tag"): (c.text or "") for c in record.findall(f"{MARC}controlfield")}
    lccn_raw = _first(record, "010")
    if not lccn_raw:
        raise CatalogError("the record carries no LCCN (010)")
    isbns = []
    for datafield in record.findall(f"{MARC}datafield[@tag='020']"):
        parts = _subfields(datafield)
        qualifier = next((v for c, v in parts if c == "q"), None)
        isbns += [(isbn_digits(v.split()[0]), qualifier, c == "z") for c, v in parts if c in "az" and v]
    lcc = " ".join(v for c, v in (_subfields(record.find(f"{MARC}datafield[@tag='050']"))
                                  if record.find(f"{MARC}datafield[@tag='050']") is not None else [])
                   if c in "ab") or None
    ddc_field = record.find(f"{MARC}datafield[@tag='082']")
    ddc = ddc_edition = None
    if ddc_field is not None:
        parts = _subfields(ddc_field)
        ddc = next((v for c, v in parts if c == "a"), None)
        ddc_edition = next((v for c, v in parts if c == "2"), None)
    title_field = record.find(f"{MARC}datafield[@tag='245']")
    title_parts = _subfields(title_field) if title_field is not None else []
    title = _trim(" : ".join(_trim(v) for c, v in title_parts if c in "ab"))
    responsibility = next((_trim(v) for c, v in title_parts if c == "c"), None)
    publication_field = record.find(f"{MARC}datafield[@tag='264'][@ind2='1']")
    if publication_field is None:
        publication_field = record.find(f"{MARC}datafield[@tag='260']")
    publication = date = None
    if publication_field is not None:
        parts = _subfields(publication_field)
        place = next((_trim(v) for c, v in parts if c == "a"), None)
        publisher = next((_trim(v) for c, v in parts if c == "b"), None)
        date = next((_trim(v) for c, v in parts if c == "c"), None)
        publication = ", ".join(p for p in (f"{place} : {publisher}" if place and publisher else place or publisher,
                                            date) if p)
    contents_field = _first(record, "505")
    contents = tuple(_trim(p) for p in re.split(r"\s+--\s+", contents_field)) if contents_field else ()
    fixed = control.get("008", "")
    names = tuple(_name(d) for tag in ("100", "700") for d in record.findall(f"{MARC}datafield[@tag='{tag}']"))
    subjects = tuple(_subject(d) for d in record.findall(f"{MARC}datafield")
                     if d.get("tag") in SUBJECT_TAGS)
    summary_field = record.find(f"{MARC}datafield[@tag='520']")
    summary = None
    if summary_field is not None:
        summary = " ".join(v for c, v in _subfields(summary_field) if c == "a") or None
    tags = {d.get("tag") or "" for d in record.findall(f"{MARC}datafield")}
    unmapped = tuple(sorted(t for t in tags - MAPPED if not t.startswith("9") and t[:1] != "0"))
    return CatalogRecord(
        lccn=normalize_lccn(lccn_raw), control_number=control.get("001", ""), isbns=tuple(isbns),
        lcc=lcc, ddc=ddc, ddc_edition=ddc_edition, names=names, title=title, responsibility=responsibility,
        edition=_trim(_first(record, "250") or "") or None, publication=publication, date=date,
        extent=_trim(" ".join(v for c, v in _subfields(record.find(f"{MARC}datafield[@tag='300']")))
                     ) if record.find(f"{MARC}datafield[@tag='300']") is not None else None,
        contents=contents, bibliography_note=_first(record, "504"),
        has_index=len(fixed) > 31 and fixed[31] == "1", language=fixed[35:38].strip() or None if len(fixed) >= 38 else None,
        subjects=subjects, publisher_summary=summary, revised=control.get("005"), unmapped_tags=unmapped,
    )


# --- Finding and preserving -------------------------------------------------------------------------

def search(index: str, value: str, maximum: int = 10) -> list[CatalogRecord]:
    """Records the catalog's SRU service finds: `isbn`, `lccn`, or `subject` (a heading). Pointers only:
    nothing is preserved; a record becomes evidence through `preserved_record`."""
    builders = {"isbn": lambda: f'bath.isbn="{isbn_digits(value)}"',
                "lccn": lambda: f'bath.lccn="{normalize_lccn(value)}"',
                "subject": lambda: f'dc.subject="{value}"'}
    if index not in builders:
        raise CatalogError(f"unknown search index {index!r}")
    query = builders[index]()
    response = _get(SRU_ENDPOINT, {"version": "1.1", "operation": "searchRetrieve", "query": query,
                                   "maximumRecords": str(maximum), "recordSchema": "marcxml"})
    root = ElementTree.fromstring(response.content)
    found = []
    for data in root.iter(f"{SRW}recordData"):
        record = data.find(f"{MARC}record")
        if record is not None:
            try:
                found.append(parse_record(ElementTree.tostring(record)))
            except CatalogError:
                continue  # a record without an LCCN cannot be preserved or cited
    return found


def preserved_record(lccn: str, directory: Path = SOURCE_DIRECTORY) -> tuple[Path, dict[str, Any]]:
    """The record for an LCCN, preserved byte for byte with its hash; fetched only if none is kept."""
    lccn = normalize_lccn(lccn)
    path = directory / f"lc-{lccn}.marcxml"
    metadata_path = directory / f"lc-{lccn}.metadata.json"
    if path.exists() and metadata_path.exists():
        return path, json.loads(metadata_path.read_text(encoding="utf-8"))
    response = _get(SRU_ENDPOINT, {"version": "1.1", "operation": "searchRetrieve", "query": f'bath.lccn="{lccn}"',
                                   "maximumRecords": "2", "recordSchema": "marcxml"})
    payload, source_uri = response.content, response.url
    count = ElementTree.fromstring(payload).findtext(f"{SRW}numberOfRecords")
    if count != "1":
        raise CatalogError(f"LCCN {lccn}: the catalog returned {count} records, not one")
    record = parse_record(payload)
    if record.lccn != lccn:
        raise CatalogError(f"asked for LCCN {lccn}, the record is {record.lccn}")
    metadata = {
        "sourceSystem": "Library of Congress catalog",
        "sourceUri": source_uri,
        "permalink": PERMALINK.format(lccn=lccn),
        "identifier": lccn,
        "label": record.title,
        "recordRevised": record.revised,
        "rights": RIGHTS,
        "retrievedAt": datetime.now(timezone.utc).isoformat(),
        "contentHash": hashlib.sha256(payload).hexdigest(),
    }
    directory.mkdir(exist_ok=True)
    path.write_bytes(payload)
    metadata_path.write_bytes((json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return path, metadata


def main(argv: list[str] | None = None) -> int:
    """Look a book up by ISBN and preserve its record: `python -m GraphRevised.adapters.lc_catalog <isbn>`."""
    import argparse
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("isbn")
    args = parser.parse_args(argv)
    if not isbn_valid(args.isbn):
        raise SystemExit(f"{args.isbn} fails the ISBN check digit")
    found = search("isbn", args.isbn, maximum=3)
    if len(found) != 1:
        raise SystemExit(f"{len(found)} records for ISBN {args.isbn}: " + "; ".join(r.lccn for r in found))
    path, metadata = preserved_record(found[0].lccn)
    record = parse_record(path.read_bytes())
    print(f"{record.title} | {record.responsibility} | {record.publication}")
    print(f"LCCN {record.lccn} | this ISBN: {record.isbn_qualifier(args.isbn)} | LCC {record.lcc} | DDC {record.ddc}")
    print(f"names: {[n.text for n in record.names]}")
    print(f"subjects: {[(s.tag, s.text) for s in record.subjects]}")
    print(f"preserved {path.name} ({metadata['contentHash'][:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
