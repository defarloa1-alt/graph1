"""Period survey: what published periodizations say about a period the graph knows.

    python -m GraphRevised.discovery.period_survey [<entity-id> ...] [--submit]

With no entity IDs, every proposed or provisional Period is surveyed. The
reader runs this itself when it proposes a period, if `curation/
authorities.json` says so; the curator need not feed it anything.

For each Period, the PeriodO gazetteer is searched for definitions that name
it (in any language PeriodO records) and fall near the time the period is
read about: the dated claims of the Works that mention it. A definition
whose name adds nothing to the period's name (beyond its region) and
carries its head word is the "same" period as one authority defines it; others that share a word are
"related" (a phase, a regional variant, a neighbour) and are only listed.
When one authority defines the same period more than once, its widest span
is taken and the rest are listed as related subdivisions.

With --submit, each "same" definition becomes evidence: the authority's
publication is proposed as a Work (reused once it exists), the definition is
stored as a record observation of that Work, and its dates are submitted as
an `occurred` claim attributed to the Work. So the graph holds who draws
which line where, with the sources' own wording; nothing is accepted here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from GraphRevised.adapters.periodo import PeriodDataset, PeriodDefinition, load_dataset
from GraphRevised.adapters.wikidata_context import entity_context
from GraphRevised.identity.local_candidates import STOPWORDS
from GraphRevised.operations import run_write
from GraphRevised.proposals.entities import propose_entity
from GraphRevised.proposals.schema import ProposalDraft, QualifierQuotation, Quotation, TimeQualifier
from GraphRevised.proposals.store import submit
from GraphRevised.proposals.temporal import TimeValueError, parse_edtf, to_astronomical

GRAPH_REVISED = Path(__file__).resolve().parents[1]
CONFIG_PATH = GRAPH_REVISED / "curation" / "authorities.json"
CACHE_DIRECTORY = GRAPH_REVISED / "cache"
SURVEY_ID = "period-survey"
SURVEY_VERSION = "period-survey-v1"
PERIODO_RIGHTS = "PeriodO data: CC0 1.0 public domain dedication"


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def uses_lookup(config: dict[str, Any], kind: str, lookup: str) -> bool:
    return lookup in config.get("kinds", {}).get(kind, {}).get("lookups", [])


def periodo_dataset(config: dict[str, Any]) -> PeriodDataset:
    settings = config["periodo"]
    return load_dataset(CACHE_DIRECTORY, source_uri=settings["sourceUri"], max_age_days=settings["maxAgeDays"])


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def fold(text: str) -> str:
    """Lower case without accents: 'République' -> 'republique', 'Römische' -> 'romische'."""
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)).lower()


def ordered_words(text: str, ignored: set[str]) -> list[str]:
    """Content words of a name in order; dates, numerals, and abbreviations (B.C., ca.) drop out."""
    return [w for w in re.findall(r"[a-z]+", fold(text)) if len(w) >= 3 and w not in ignored and w not in STOPWORDS]


def words(text: str, ignored: set[str]) -> set[str]:
    return set(ordered_words(text, ignored))


def same_word(a: str, b: str) -> bool:
    """Equal, or sharing a five-letter stem across languages and inflections
    (republic, republican, republique, repubblicano; roman, romano, romaine)."""
    return a == b or (len(a) >= 5 and len(b) >= 5 and a[:5] == b[:5])


def covered(word: str, pool: set[str]) -> bool:
    return any(same_word(word, other) for other in pool)


@dataclass(frozen=True)
class Match:
    definition: PeriodDefinition
    fit: str  # "same" or "related"
    name: str  # the period name that matched
    label: str  # the definition label that matched
    note: str | None = None


def match_definitions(
    names: list[str],
    definitions: tuple[PeriodDefinition, ...],
    window: tuple[int, int] | None,
    *,
    near_years: int,
    ignored: set[str],
) -> list[Match]:
    """Definitions naming one of `names` whose span comes within `near_years`
    of `window` (astronomical years). Without a window nothing is matched:
    names alone would mix every empire and republic in the dataset."""
    if window is None:
        return []
    low, high = window[0] - near_years, window[1] + near_years
    found: list[Match] = []
    for definition in definitions:
        span = definition.span
        if span is None or span[1] < low or span[0] > high:
            continue
        region = set()
        for _, place in definition.places:
            region |= words(place, ignored)
        region |= words(definition.place_description or "", ignored)
        best: Match | None = None
        for name in names:
            asked = words(name, ignored)
            head = (ordered_words(name, ignored) or [""])[-1]  # "Republic" in "Roman Republic"
            for label in definition.labels:
                given = words(label, ignored)
                if not asked or not given or not any(covered(w, given) for w in asked):
                    continue
                # The label itself must carry the name's head word; the region may
                # supply qualifiers ("Republic" in Rome), never the period's noun.
                same = (covered(head, given)
                        and all(covered(w, given | region) for w in asked)
                        and all(covered(w, asked | region) for w in given))
                if same:
                    best = Match(definition, "same", name, label)
                    break
                best = best or Match(definition, "related", name, label)
            if best is not None and best.fit == "same":
                break
        if best is not None:
            found.append(best)
    return _widest_per_source(found)


def _widest_per_source(matches: list[Match]) -> list[Match]:
    """One authority defining the same period several times (Republic 510-30,
    510-265, 265-30 B.C.) means one period and its subdivisions: keep the widest."""
    by_source: dict[str, list[Match]] = {}
    for match in matches:
        if match.fit == "same":
            by_source.setdefault(match.definition.source.authority_id, []).append(match)
    demoted = set()
    for group in by_source.values():
        widest = max(group, key=lambda m: m.definition.span[1] - m.definition.span[0])
        for match in group:
            if match is not widest:
                demoted.add(id(match))
    result = []
    for match in matches:
        if id(match) in demoted:
            widest = max(by_source[match.definition.source.authority_id],
                         key=lambda m: m.definition.span[1] - m.definition.span[0])
            result.append(Match(match.definition, "related", match.name, match.label,
                                note=f"within {widest.definition.label!r} in the same source"))
        else:
            result.append(match)
    return result


# ---------------------------------------------------------------------------
# Graph context
# ---------------------------------------------------------------------------

def period_names(tx: Any, entity_id: str) -> list[str]:
    """The entity's label and short label, and its Wikidata label and aliases once linked."""
    row = tx.run(
        """
        MATCH (entity:Entity {id: $id})
        OPTIONAL MATCH (entity)-[link:HAS_AUTHORITY_RECORD]->(record:AuthorityRecord {system: "Wikidata"})
        WHERE link.role = "entity_identity"
        RETURN entity.label AS label, entity.shortLabel AS shortLabel,
               head(collect(record.identifier)) AS qid, head(collect(record.label)) AS qidLabel,
               head(collect(record.rawPayloadUri)) AS payloadUri
        """,
        id=entity_id,
    ).single()
    if row is None:
        return []
    names = [row["label"], row["shortLabel"], row["qidLabel"]]
    names += entity_context(row["payloadUri"], row["qid"]).get("aliases", [])
    return list(dict.fromkeys(name for name in names if name))


def reading_window(tx: Any, entity_id: str) -> tuple[int, int] | None:
    """Astronomical years spanned by the dated claims drawn from the Works
    that mention the period (proposed or accepted). None if there are none."""
    rows = tx.run(
        """
        MATCH (mention:Annotation {kind: "entity-mention"})-[:CONCERNS]->(:Entity {id: $id})
        MATCH (mention)-[:ANNOTATES]->(:SourceObservation)-[:IN_WORK]->(work:Entity)
        MATCH (observation:SourceObservation)-[:IN_WORK]->(work)
        CALL (observation) {
          MATCH (assertion:Assertion)-[:SUPPORTED_BY]->(observation) RETURN assertion
          UNION
          MATCH (assertion:Assertion)<-[:PROPOSES]-(:Proposal)-[:PROPOSES_EVIDENCE]->(observation)
          RETURN assertion
        }
        WITH DISTINCT assertion
        WHERE assertion.timeEdtf IS NOT NULL AND assertion.status IN ["proposed", "accepted"]
        RETURN assertion.timeEdtf AS edtf, assertion.timeCalendar AS calendar
        """,
        id=entity_id,
    ).data()
    years = []
    for row in rows:
        try:
            bounds = parse_edtf(row["edtf"], row["calendar"] or "julian")
        except TimeValueError:
            continue
        years += [to_astronomical(y) for y in (bounds.earliest_year, bounds.latest_year) if y is not None]
    return (min(years), max(years)) if years else None


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------

def edtf_year(year: int) -> str:
    return ("-" if year < 0 else "") + f"{abs(year):04d}"


def definition_edtf(definition: PeriodDefinition) -> str:
    """The definition's span as EDTF; a terminus given as a range of years is
    taken at its outer year and marked approximate."""
    (start_early, start_late), (stop_early, stop_late) = definition.start_years, definition.stop_years
    start = edtf_year(start_early) + ("~" if start_early != start_late else "")
    stop = edtf_year(stop_late) + ("~" if stop_early != stop_late else "")
    return start if start == stop else f"{start}/{stop}"


def record_text(definition: PeriodDefinition) -> str:
    """The record's own wording only: its label, its terminus labels, its region."""
    lines = [definition.label, definition.start_label, definition.stop_label, definition.place_description]
    return "\n".join(line.strip() for line in lines if line and line.strip())


def work_label(definition: PeriodDefinition) -> str:
    source = definition.source
    title = source.title or f"PeriodO authority {source.authority_id}"
    if not source.creators:
        return title
    surname = source.creators[0].split(",")[0].strip()
    if fold(surname) in fold(title):
        return title
    return f"{surname}{' et al.' if len(source.creators) > 1 else ''}, {title}"


def record_observation(definition: PeriodDefinition, dataset: PeriodDataset, work_id: str) -> dict[str, Any]:
    source = definition.source
    text = record_text(definition)
    revision = dataset.version or dataset.content_hash[:12]
    where = f", {definition.page}" if definition.page else (f", {source.locator}" if source.locator else "")
    return {
        "id": f"chr:observation:periodo:{definition.id}:{re.sub(r'[^a-z0-9-]+', '-', revision.lower())}",
        "label": f"{work_label(definition)}: \"{definition.label}\" (PeriodO {definition.id})",
        "shortLabel": f"PeriodO {definition.label}"[:80],
        "sourceSystem": "PeriodO", "sourceEntityId": definition.id,
        "locator": f"{definition.uri}{where}",
        "passageText": text, "passageHash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "editorialNotes": [definition.editorial_note] if definition.editorial_note else [],
        "language": definition.language, "workTitle": source.title, "author": "; ".join(source.creators) or None,
        "editionCitation": source.citation or ", ".join(x for x in (source.title, source.year) if x),
        "rights": PERIODO_RIGHTS, "sourceUri": dataset.source_uri, "sourceRevision": revision,
        "retrievedAt": dataset.retrieved_at, "contentHash": dataset.content_hash,
        "rawPayloadUri": f"GraphRevised/cache/periodo-dataset.json#{definition.id}", "workId": work_id,
    }


def definition_draft(match: Match, entity_id: str, observation_id: str, work_id: str,
                     calendar: str) -> ProposalDraft | None:
    """The definition's dates as an attributed `occurred` claim, quoted from the record."""
    definition = match.definition
    if not (definition.start_label and definition.stop_label) or definition.span is None:
        return None
    wording = f"{definition.start_label}\n{definition.stop_label}"
    region = definition.place_description or ", ".join(label for _, label in definition.places) or "no region given"
    return ProposalDraft(
        predicate="occurred", subject_id=entity_id, object_id=None, observation_ids=(observation_id,),
        # The label with its dates: contiguous in the record, and long enough to quote.
        quotations=(Quotation(observation_id=observation_id, text=definition.label + "\n" + wording),),
        qualifier_quotations=(QualifierQuotation(observation_id=observation_id, supports="time", text=wording),),
        time=TimeQualifier(source_expression=wording, edtf=definition_edtf(definition), calendar=calendar,
                           normalization_basis="source"),
        mode="attributed", attributed_to=work_id,
        rationale=(f"PeriodO records {work_label(definition)} defining \"{definition.label}\" from "
                   f"{definition.start_label} to {definition.stop_label} ({region}). Matched to "
                   f"\"{match.name}\" by name, near the time the period is read about."),
        relevance="One authority's periodization: where it draws this period's edges.",
        proposed_by=SURVEY_ID, prompt_version=SURVEY_VERSION,
    )


def store_evidence(tx: Any, operations: dict[str, str], registry: Any, dataset: PeriodDataset,
                   match: Match, entity_id: str, calendar: str) -> dict[str, Any]:
    definition = match.definition
    work = propose_entity(tx, operations, kind="Work", label=work_label(definition), proposed_by=SURVEY_ID,
                          observation_id=None, quotation=None, source="PeriodO",
                          note=f"Work named as the source of PeriodO definitions: "
                               f"{definition.source.citation or work_label(definition)}"[:500])
    observation = record_observation(definition, dataset, work["id"])
    run_write(tx, operations, "upsert_record_observation", observation)
    draft = definition_draft(match, entity_id, observation["id"], work["id"], calendar)
    entry = {"definition": definition.id, "label": definition.label, "work": work["id"],
             "workCreated": work["created"], "observation": observation["id"], "claim": None}
    if draft is not None:
        submission = submit(tx, draft, registry, operations)
        entry["claim"] = {"outcome": submission.validation.outcome.value,
                          "reasons": list(submission.validation.reasons), "stored": submission.stored,
                          "assertion": submission.validation.assertion_id}
    return entry


def survey_period(tx: Any, operations: dict[str, str], registry: Any, dataset: PeriodDataset,
                  config: dict[str, Any], entity_id: str, *, store: bool) -> dict[str, Any]:
    settings = config["periodo"]
    names = period_names(tx, entity_id)
    window = reading_window(tx, entity_id)
    matches = match_definitions(names, dataset.definitions, window, near_years=settings["nearYears"],
                                ignored=set(settings["ignoredWords"]))
    same = [m for m in matches if m.fit == "same"]
    places = Counter(f"{qid} {label}" for m in same for qid, label in m.definition.places if qid.startswith("Q"))
    stored = [store_evidence(tx, operations, registry, dataset, m, entity_id, settings["calendar"])
              for m in same] if store else []
    return {"entity": entity_id, "names": names, "window": window, "same": same,
            "related": [m for m in matches if m.fit == "related"], "places": places, "stored": stored}


def describe(match: Match) -> str:
    d = match.definition
    region = d.place_description or ", ".join(label for _, label in d.places[:3])
    dates = f"{d.start_label or '?'} – {d.stop_label or '?'}"
    return f"{work_label(d)}: \"{d.label}\" {dates} [{region}]" + (f" ({match.note})" if match.note else "")


def main(argv: list[str] | None = None) -> int:
    from neo4j import GraphDatabase

    from GraphRevised.operations import load_operations
    from GraphRevised.proposals.registry import load_registry

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("entities", nargs="*", help="Period entity IDs (default: every proposed or provisional Period)")
    parser.add_argument("--submit", action="store_true", help="store records, Works, and claims as proposals")
    args = parser.parse_args(argv)

    config, operations, registry = load_config(), load_operations(), load_registry()
    dataset = periodo_dataset(config)
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            entities = args.entities or [row["id"] for row in session.run(
                "MATCH (e:Entity {kind: 'Period'}) WHERE e.status IN ['proposed', 'provisional'] "
                "RETURN e.id AS id ORDER BY id")]
            print(f"PeriodO {dataset.version or dataset.content_hash[:12]}: {len(dataset.definitions)} definitions\n")
            for entity_id in entities:
                with session.begin_transaction() as tx:
                    result = survey_period(tx, operations, registry, dataset, config, entity_id, store=args.submit)
                    tx.commit()
                window = result["window"]
                print(f"{entity_id}  names: {', '.join(result['names'])}")
                print(f"  read about: {'no dated claims' if window is None else f'{window[0]} to {window[1]} (astronomical)'}")
                for match in result["same"]:
                    print(f"  same     {describe(match)}")
                for match in result["related"][:12]:
                    print(f"  related  {describe(match)}")
                if len(result["related"]) > 12:
                    print(f"  related  ... {len(result['related']) - 12} more")
                for place, count in result["places"].most_common(4):
                    print(f"  PeriodO places it in {place} ({count})")
                for entry in result["stored"]:
                    claim = entry["claim"] or {}
                    print(f"  stored   {entry['label']} -> {claim.get('outcome', 'no dates')}"
                          + (f" {claim['reasons']}" if claim.get("reasons") and claim.get("outcome") == "invalid" else ""))
                print()
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
