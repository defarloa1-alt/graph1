"""The curator's Obsidian notes: read, checked, and written to the graph (32 §2.1a, §2.1b).

    python -m GraphRevised.capture.notes check [--folder <dir>]
    python -m GraphRevised.capture.notes apply [--folder <dir>] [--note <name>] [--apply]
    python -m GraphRevised.capture.notes suggest [--folder <dir>] [--note <name>]

`suggest` lists, for each note whose `concerns` is unfilled, the entities whose labels the note's
words cover, ready to paste (code only, no model; it never changes the note).

This is the sync without its watcher: what it does when a note is saved. A note is a Markdown file
in the folder (subfolders and files whose name starts with "_" are skipped: templates live there)
with flat frontmatter marked `chrystallum: note` or `chrystallum: image`.

`check` reports every problem that would keep a note out of the graph: frontmatter that does not
parse, a key not in the format, an ISBN that fails its check digit, a `concerns` id or a `work` not
in the graph, a `related` link to no note, a missing quote block or image, a template placeholder.

`apply` writes what a sound note stands for, as the curator's private overlay:

    a book note   the quote block as a transcription of the book (reused when the same words are
                  already transcribed from it), and an Annotation of kind `note`, the curator's own
                  text, ANNOTATES the transcription and CONCERNS its targets
    an image      an `image` observation (the file's hash and path, what it shows, who made it,
                  where from, its rights; never evidence for a claim), and an Annotation of kind
                  `image-note` CONCERNS its targets

The book's footnote to the quote is written the Obsidian way: the mark where the book has it in
the quote (`the camp[^34]`) and the footnote's words, as printed, below (`[^34]: Author 12.3.4`).
It is the book's, not the curator's: the mark is taken out of the quote, and the footnote is kept
on the transcription (its mark, the sentence the mark is in, its words), never in the Annotation.
Following it to the passages it cites is a later step (2026-11-17).

The book is the note's `work`, or the Work whose LCCN record lists the note's ISBN (found among the
LC records already preserved). It writes the note's `id` back into the file, the only change it
makes there. Claims are never drafted here: that is a separate step the curator reviews.
Dry run by default (one transaction, rolled back); --apply commits.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import yaml

from GraphRevised.adapters.lc_catalog import SOURCE_DIRECTORY, isbn_digits, isbn_valid, parse_record
from GraphRevised.capture.core import annotation_id, annotation_label, transcription_id
from GraphRevised.operations import run_write
from GraphRevised import localdb

GRAPH_REVISED = Path(__file__).resolve().parents[1]
DEFAULT_FOLDER = GRAPH_REVISED / "obsidian_book_notes"
NOTE_KEYS = {"chrystallum", "id", "noteType", "status", "visibility", "isbn", "page", "location", "chapter",
             "quoting", "book", "author", "edition", "work", "quotationStatus", "concerns", "related", "tags"}
IMAGE_KEYS = {"chrystallum", "id", "image", "depicts", "madeBy", "madeOn", "rights", "collection", "accession",
              "url", "keep", "isbn", "page", "visibility", "concerns", "related", "tags"}
NOTE_TYPES = ("excerpt", "observation", "question", "hypothesis", "interpretation", "outline", "argument")
RIGHTS = ("own-photo", "copyright", "cc-by", "cc-by-sa", "public-domain", "unknown")
VISIBILITY = {"private": "private", "shared": "team", "team": "team", "public": "public"}
PLACEHOLDERS = ("your own thoughts, if any", "your own note about the image", "the book's words, exactly as printed",
                "replace-me", "file name.png")
ID_PATTERN = re.compile(r"^chr:[a-z]+:[A-Za-z0-9._:-]+$")


class NoteError(ValueError):
    """A file that is not a note at all (no frontmatter, or frontmatter that does not parse)."""


FOOTNOTE_MARK = re.compile(r"\[\^([^\]\s]+)\]")
FOOTNOTE_DEFINITION = re.compile(r"^\[\^([^\]\s]+)\]:\s*(.*)$")
SENTENCE_END = re.compile(r"([.!?](?:\[\^[^\]\s]+\])*)\s+")  # a mark may follow the full stop


@dataclass(frozen=True)
class Footnote:
    """The book's footnote to the quote: its mark, the sentence the mark sits in, its words as printed."""
    mark: str
    sentence: str | None  # None when the mark is not in the quote (check reports it)
    text: str

    def stored(self) -> str:
        import json
        return json.dumps({"mark": self.mark, "sentence": self.sentence, "text": self.text}, ensure_ascii=False)


def footnote_sentences(quote_with_marks: str) -> dict[str, str]:
    """Each mark's sentence in the quote, the marks themselves taken out."""
    found = {}
    pieces = SENTENCE_END.split(quote_with_marks)  # text, end, text, end, ..., text
    sentences = [pieces[i] + (pieces[i + 1] if i + 1 < len(pieces) else "") for i in range(0, len(pieces), 2)]
    for sentence in sentences:
        for mark in FOOTNOTE_MARK.findall(sentence):
            found.setdefault(mark, " ".join(FOOTNOTE_MARK.sub("", sentence).split()))
    return found


@dataclass
class Note:
    path: Path
    frontmatter: dict[str, Any]
    quote: str  # the quote block's words, one space between lines, footnote marks taken out
    text: str  # the curator's own text: not the quote block, an embedded image, or the book's footnotes
    embeds: list[str] = field(default_factory=list)
    footnotes: list[Footnote] = field(default_factory=list)
    unmarked: list[str] = field(default_factory=list)  # marks in the quote with no footnote written

    @property
    def kind(self) -> str | None:
        return self.frontmatter.get("chrystallum")

    @property
    def name(self) -> str:
        return self.path.stem

    def get(self, key: str) -> Any:
        value = self.frontmatter.get(key)
        return value.strip() if isinstance(value, str) else value

    def ids(self, key: str) -> list[str]:
        return [str(v).strip() for v in (self.frontmatter.get(key) or []) if v is not None]

    def locator(self) -> str | None:
        where = f"p. {self.get('page')}" if self.get("page") not in (None, "") else (
            f"loc. {self.get('location')}" if self.get("location") not in (None, "") else None)
        chapter = self.get("chapter")
        if chapter in (None, ""):
            return where
        chapter = f"ch. {chapter}" if str(chapter).isdigit() else str(chapter)
        return f"{chapter}, {where}" if where else chapter


def read_note(path: Path) -> Note:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise NoteError("the file does not start with --- (no frontmatter)")
    try:
        _, front, body = text.split("---", 2)
        frontmatter = yaml.safe_load(front) or {}
    except (ValueError, yaml.YAMLError) as error:
        raise NoteError(f"the frontmatter does not parse: {error}") from None
    if not isinstance(frontmatter, dict):
        raise NoteError("the frontmatter is not a set of keys")
    quote_lines, own, embeds = [], [], []
    definitions: dict[str, list[str]] = {}
    current = None  # the footnote being written: an indented line after it continues it
    for line in body.splitlines():
        stripped = line.strip()
        definition = FOOTNOTE_DEFINITION.match(stripped)
        if definition:
            current = definition.group(1)
            definitions.setdefault(current, []).append(definition.group(2))
            continue
        if current and stripped and line[:1] in (" ", "\t"):
            definitions[current].append(stripped)
            continue
        current = None
        if stripped.startswith(">"):
            content = stripped[1:].strip()
            if not content.lower().startswith("[!quote]"):
                quote_lines.append(content)
        elif stripped.startswith("![["):
            embeds.append(stripped[3:].split("]]")[0].split("|")[0])
        elif stripped:
            own.append(line.rstrip())
    marked = " ".join(" ".join(quote_lines).split())
    sentences = footnote_sentences(marked)
    footnotes = [Footnote(mark, sentences.get(mark), " ".join(" ".join(parts).split()))
                 for mark, parts in definitions.items()]
    return Note(path=path, frontmatter=frontmatter, quote=" ".join(FOOTNOTE_MARK.sub("", marked).split()),
                text="\n".join(own).strip(), embeds=embeds, footnotes=footnotes,
                unmarked=[m for m in sentences if m not in definitions])


def notes_in(folder: Path) -> dict[str, Path]:
    """The folder's notes by name, leaving out anything under a name that starts with "_"."""
    return {p.stem: p for p in sorted(folder.rglob("*.md"))
            if not any(part.startswith("_") or part.startswith(".") for part in p.relative_to(folder).parts)}


def link_target(value: str) -> str:
    return re.sub(r"^\[\[|\]\]$", "", str(value).strip()).split("|")[0].strip()


def find_file(folder: Path, name: str) -> Path | None:
    found = [p for p in folder.rglob(name) if p.is_file()]
    return found[0] if found else None


# --- What the graph is asked ---------------------------------------------------------------------

class NoteReader(Protocol):
    def entities(self, ids: list[str]) -> dict[str, str]: ...  # id -> label, for those that exist
    def work(self, work_id: str) -> str | None: ...  # the Work's label
    def work_for_lccn(self, lccn: str) -> list[str]: ...  # Works holding this LCCN record


class Neo4jNoteReader:
    def __init__(self, tx: Any) -> None:
        self.tx = tx

    def entities(self, ids: list[str]) -> dict[str, str]:
        rows = self.tx.run("MATCH (e:Entity) WHERE e.id IN $ids AND e.status <> 'deprecated' "
                           "RETURN e.id AS id, e.label AS label", ids=ids).data()
        return {r["id"]: r["label"] for r in rows}

    def work(self, work_id: str) -> str | None:
        row = self.tx.run("MATCH (w:Entity:Work {id: $id}) RETURN w.label AS label", id=work_id).single()
        return row["label"] if row else None

    def work_for_lccn(self, lccn: str) -> list[str]:
        return self.tx.run("MATCH (w:Entity:Work)-[:HAS_AUTHORITY_RECORD]->(:AuthorityRecord "
                           "{system: 'LCCN', identifier: $lccn}) RETURN w.id AS id", lccn=lccn).value()


    def candidates(self, words: list[str]) -> list[dict[str, Any]]:
        """Live entities (not Works, not one source's depicted event) whose label holds one of the words."""
        return self.tx.run(
            "MATCH (e:Entity) WHERE NOT e.status IN ['rejected', 'deprecated'] AND NOT e:Work "
            "AND NOT e.id STARTS WITH 'chr:entity:depicted:' "
            "AND any(w IN $words WHERE toLower(e.label) CONTAINS w) "
            "RETURN e.id AS id, e.label AS label, [l IN labels(e) WHERE l <> 'Entity'][0] AS kind, "
            "e.status AS status", words=words).data()


# --- Suggesting what a note concerns ---------------------------------------------------------------

STOPWORDS = {"about", "after", "again", "against", "also", "among", "and", "battle", "been", "before", "being",
             "between", "both", "could", "despite", "does", "during", "each", "even", "from", "have", "having",
             "into", "itself", "large", "lacked", "might", "more", "most", "much", "only", "other", "over",
             "same", "should", "since", "some", "spell", "still", "such", "than", "that", "their", "them",
             "then", "there", "these", "they", "this", "those", "through", "under", "until", "very", "were",
             "what", "when", "where", "which", "while", "with", "would", "your", "chrystallum"}
WORD = re.compile(r"[a-z]+")


def significant_words(text: str) -> list[str]:
    """Lowercase words of four letters or more that are not common words; a possessive 's is dropped."""
    words = WORD.findall(re.sub(r"['’]s\b", "", text.lower()))
    return [w for w in dict.fromkeys(words) if len(w) >= 4 and w not in STOPWORDS]


def suggest_concerns(note: Note, rows: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    """Rank entities by how much of their label the note's words cover; a whole label first.

    Code only, no model: a label word counts when it is one of the note's significant words.
    Suggestions are printed for the curator, never written into the note."""
    text = " ".join([note.quote, note.text]).lower()
    words = set(significant_words(text))
    ranked = []
    for row in rows:
        label_words = significant_words(row["label"] or "")
        if not label_words:
            continue
        matched = [w for w in label_words if w in words]
        if not matched:
            continue
        whole = (row["label"] or "").lower().replace("’", "'") in text.replace("’", "'")
        ranked.append({**row, "matched": matched, "whole": whole, "share": len(matched) / len(label_words)})
    ranked.sort(key=lambda r: (not r["whole"], -r["share"], -len(r["matched"]), r["label"]))
    return ranked[:limit]


def lccn_for_isbn(isbn: str, directory: Path = SOURCE_DIRECTORY) -> list[str]:
    """The LCCNs of the preserved LC records that list this ISBN (any edition's)."""
    digits = isbn_digits(isbn)
    found = []
    for path in sorted(directory.glob("lc-*.marcxml")):
        record = parse_record(path.read_bytes())
        if any(d == digits for d, _, _ in record.isbns):
            found.append(record.lccn)
    return found


def book_of(note: Note, reader: NoteReader) -> tuple[str | None, str | None]:
    """The note's Work id and, when there is none, why."""
    if note.get("work"):
        return (note.get("work"), None) if reader.work(note.get("work")) else (None, f"work {note.get('work')} is not a Work in the graph")
    if note.get("isbn"):
        lccns = lccn_for_isbn(str(note.get("isbn")))
        works = sorted({w for lccn in lccns for w in reader.work_for_lccn(lccn)})
        if len(works) == 1:
            return works[0], None
        if len(works) > 1:
            return None, f"more than one Work for ISBN {note.get('isbn')}: {works}"
        return None, (f"no preserved LC record lists ISBN {note.get('isbn')}: look it up with "
                      "`python -m GraphRevised.adapters.lc_catalog <isbn>` first")
    return None, "no work and no isbn: the note cannot name its book"


# --- The check -----------------------------------------------------------------------------------

def check(note: Note, reader: NoteReader, names: set[str], folder: Path = DEFAULT_FOLDER) -> list[str]:
    """Every problem that keeps the note out of the graph; an empty list when it is sound."""
    problems = []
    kind = note.kind
    if kind not in ("note", "image"):
        return [f"chrystallum is {kind!r}: a note says `note` or `image`"]
    unknown = sorted(set(note.frontmatter) - (NOTE_KEYS if kind == "note" else IMAGE_KEYS))
    if unknown:
        problems.append(f"keys not in the format (spelling and capitals count): {unknown}")
    if note.get("id") and not ID_PATTERN.match(str(note.get("id"))):
        problems.append(f"id {note.get('id')!r} is not one the sync wrote")
    if note.get("visibility") not in (None, *VISIBILITY):
        problems.append(f"visibility {note.get('visibility')!r}: private, shared, or public")
    isbn = note.get("isbn")
    if isbn not in (None, "") and not isbn_valid(str(isbn)):
        problems.append(f"isbn {isbn!r} fails its check digit" + (" (quote marks typed into the value?)" if '"' in str(isbn) else ""))
    concerns = note.ids("concerns")
    if not concerns:
        problems.append("concerns names nothing")
    malformed = [c for c in concerns if not ID_PATTERN.match(c)]
    if malformed:
        problems.append(f"concerns entries that are not ids: {malformed}")
    known = reader.entities([c for c in concerns if c not in malformed])
    problems += [f"concerns {c} is not in the graph" + (" (ids are lowercase)" if c != c.lower() else "")
                 for c in concerns if c not in malformed and c not in known]
    problems += [f"related [[{link_target(r)}]] is no note in the folder" for r in note.ids("related")
                 if link_target(r) not in names]
    if kind == "note":
        if note.get("noteType") not in NOTE_TYPES:
            problems.append(f"noteType {note.get('noteType')!r}: one of {list(NOTE_TYPES)}")
        if not note.quote:
            problems.append("no quote block (> [!quote] with the book's words)")
        if not note.locator():
            problems.append("no page or location")
        if note.get("noteType") != "excerpt" and not note.text:
            problems.append("no text of the curator's: write it, or make the noteType excerpt")
        problems += [f"footnote mark [^{m}] in the quote has no footnote written below it" for m in note.unmarked]
        problems += [f"footnote [^{f.mark}] has no mark in the quote: put [^{f.mark}] where the book has it"
                     for f in note.footnotes if f.sentence is None]
        problems += [f"footnote [^{f.mark}] is empty" for f in note.footnotes if not f.text]
        work, why = book_of(note, reader)
        if work is None:
            problems.append(why)
    else:
        if not note.get("depicts"):
            problems.append("depicts is empty: say what the image shows")
        if note.get("rights") not in RIGHTS:
            problems.append(f"rights {note.get('rights')!r}: one of {list(RIGHTS)}")
        target = link_target(note.get("image") or "")
        if not target:
            problems.append("image names no file or URL")
        elif not target.startswith("http") and find_file(folder, target) is None:
            problems.append(f"image file {target!r} is not in the folder")
    lowered = (yaml.safe_dump(note.frontmatter) + note.text + note.quote).lower()
    problems += [f"a template placeholder is left: {p!r}" for p in PLACEHOLDERS if p in lowered]
    return problems


# --- Writing it ----------------------------------------------------------------------------------

def write_back_id(path: Path, note_id: str) -> None:
    """Fill the empty `id:` line of the frontmatter; nothing else in the file changes."""
    text = path.read_text(encoding="utf-8")
    end = text.index("---", 3)
    front, rest = text[:end], text[end:]
    new_front, count = re.subn(r"(?m)^id:[ \t]*$", f"id: {note_id}", front, count=1)
    if count:
        path.write_bytes((new_front + rest).encode("utf-8"))


def apply_note(tx: Any, operations: dict[str, str], note: Note, reader: NoteReader, *, author: str,
               folder: Path = DEFAULT_FOLDER) -> dict[str, Any]:
    """Write one sound note; returns what was written. The caller has checked it."""
    now = datetime.now(timezone.utc).isoformat()
    visibility = VISIBILITY[note.get("visibility") or "private"]
    concerns = note.ids("concerns")
    if note.kind == "note":
        work, _ = book_of(note, reader)
        existing = tx.run(
            "MATCH (o:SourceObservation {observationKind: 'transcription', passageHash: $h})-[:IN_WORK]->(:Entity {id: $w}) "
            "RETURN o.id AS id ORDER BY o.id LIMIT 1",
            h=hashlib.sha256(note.quote.encode("utf-8")).hexdigest(), w=work).single()
        locator = note.locator()
        observation_id = existing["id"] if existing else transcription_id(work, locator, note.quote)
        if not existing:
            label = reader.work(work)
            run_write(tx, operations, "upsert_transcription_observation", {
                "id": observation_id, "workId": work, "label": f"{label}, {locator} (transcription)",
                "shortLabel": f"{label} {locator}", "sourceSystem": "curator", "locator": locator,
                "locatorType": "location" if note.get("location") else "page", "passageText": note.quote,
                "passageHash": hashlib.sha256(note.quote.encode("utf-8")).hexdigest(), "language": "en",
                "workTitle": label, "author": None,
                "editionCitation": (f"ISBN {isbn_digits(str(note.get('isbn')))}" if note.get("isbn") else note.get("edition"))
                                   or "edition not recorded",
                "rights": "Short quotation transcribed for study; the work may be in copyright.",
                "visibility": visibility, "capturedBy": author, "capturedAt": now,
                "contentHash": hashlib.sha256(note.quote.encode("utf-8")).hexdigest(),
                "rawPayloadUri": f"obsidian:{note.path.relative_to(folder).as_posix()}",
                "footnotes": [f.stored() for f in note.footnotes]})
        elif note.footnotes:
            run_write(tx, operations, "add_transcription_footnotes", {
                "id": observation_id, "footnotes": [f.stored() for f in note.footnotes]})
        kind, quotation, note_type = "note", note.quote, note.get("noteType")
    else:
        target = link_target(note.get("image"))
        if target.startswith("http"):
            raise NoteError("an image given by URL is kept as a private copy: not built yet, save the file instead")
        image = find_file(folder, target)
        digest = hashlib.sha256(image.read_bytes()).hexdigest()
        observation_id = f"chr:observation:image:{digest[:16]}"
        run_write(tx, operations, "upsert_image_observation", {
            "id": observation_id, "label": f"Image: {note.get('depicts')}"[:300], "shortLabel": f"Image · {note.name}"[:80],
            "depicts": note.get("depicts"), "madeBy": note.get("madeBy"),
            "madeOn": str(note.get("madeOn")) if note.get("madeOn") else None, "rights": note.get("rights"),
            "collection": note.get("collection"), "accession": note.get("accession"), "sourceUri": note.get("url"),
            "visibility": visibility, "capturedBy": author, "capturedAt": now, "contentHash": digest,
            "rawPayloadUri": f"obsidian:{image.relative_to(folder).as_posix()}"})
        kind, quotation, note_type = "image-note", None, None
    text = note.text or None
    annotation = annotation_id(author, observation_id, text, concerns)
    run_write(tx, operations, "upsert_annotation", {
        "id": annotation,
        "label": annotation_label(tx, kind=kind, note_type=note_type, observation_id=observation_id),
        "kind": kind, "noteType": note_type, "note": text, "author": author, "visibility": visibility,
        "createdAt": now, "observationId": observation_id, "quotation": quotation, "concerns": concerns})
    return {"note": note.name, "observationId": observation_id, "annotationId": annotation,
            "reusedTranscription": note.kind == "note" and existing is not None}


def print_suggestions(note: Note, reader: Any, *, every: bool = False) -> None:
    """For a note whose `concerns` is unfilled (or any note named with --note): candidates to paste."""
    concerns = note.ids("concerns")
    unfilled = not concerns or any("replace-me" in c for c in concerns)
    if not (unfilled or every):
        return
    words = significant_words(" ".join([note.quote, note.text]))
    found = suggest_concerns(note, reader.candidates(words) if words else [])
    print(f"{note.name}" + ("" if unfilled else "  (concerns already filled)"))
    if not found:
        print("    no entity's label matches the note's words; use the Cypher lookup or name a new entity")
        return
    print("    concerns:")
    for row in found:
        why = "whole label in the note" if row["whole"] else "words: " + ", ".join(row["matched"])
        print(f"      - {row['id']:<55} # {row['label']} ({row['kind']}, {row['status']}; {why})")


def main(argv: list[str] | None = None) -> int:
    from neo4j import GraphDatabase
    from GraphRevised.operations import load_operations

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("check", "apply", "suggest"))
    parser.add_argument("--folder", type=Path, default=DEFAULT_FOLDER)
    parser.add_argument("--note", help="only the note of this name")
    parser.add_argument("--author", default=os.environ.get("CHRYSTALLUM_CURATOR", "Tony DeFarlo"))
    parser.add_argument("--apply", action="store_true", help="commit (default: dry run)")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # ✓ and ✗ on a Windows console

    paths = notes_in(args.folder)
    chosen = {n: p for n, p in paths.items() if args.note in (None, n)}
    operations = load_operations()
    driver = GraphDatabase.driver(localdb.uri(),
                                  auth=localdb.auth(),
                                  notifications_min_severity="OFF")
    written, failed = [], 0
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                reader = Neo4jNoteReader(tx)
                for name, path in chosen.items():
                    try:
                        note = read_note(path)
                    except NoteError as error:
                        print(f"✗ {name}: {error}")
                        failed += 1
                        continue
                    if note.kind is None:
                        continue  # not marked for the sync
                    if args.command == "suggest":
                        print_suggestions(note, reader, every=args.note is not None)
                        continue
                    problems = check(note, reader, set(paths), args.folder)
                    if problems:
                        failed += 1
                        print(f"✗ {name}")
                        for problem in problems:
                            print(f"    {problem}")
                        continue
                    if args.command == "check":
                        print(f"✓ {name}")
                        continue
                    result = apply_note(tx, operations, note, reader, author=args.author, folder=args.folder)
                    written.append((note, result))
                    print(f"✓ {name}: {result['annotationId']}" + (" (transcription reused)" if result["reusedTranscription"] else ""))
                if args.apply:
                    tx.commit()
                else:
                    tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    if args.apply:
        for note, result in written:
            if not note.get("id"):
                write_back_id(note.path, result["annotationId"])
    if args.command == "apply":
        print("applied; ids written into the notes" if args.apply else "dry run, rolled back")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
