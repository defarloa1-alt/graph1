"""Coin types as evidence: a series' named units, from the CRRO data dump (D-151, 43 §2).

    python -m GraphRevised.harvest.crro_coins <series id> [--apply]

Reads the series named in curation/coin-series.json from the Coinage of the
Roman Republic Online dump (crro/nomisma.rdf, Open Database License 1.0; only
the series' own types are taken). Then:

1. The series is a Work of form `coinage` and standing `primary`: the issuer's
   own voice, an independent line of evidence beside the texts.
2. Each coin type is a record observation in that Work: denomination, date,
   legends and designs, as CRRO gives them, with its rights (ODbL 1.0, CRRO,
   American Numismatic Society) and its permalink.
3. Each unit a reverse legend names (LEG XII, a praetorian cohort) is a
   proposed Group. Spellings of one numeral (IIII and IV) are one unit, and a
   titled legend (LEG XII ANTIQVAE) is the same unit as its number: the title is
   kept as an alternative name (curator, 2026-11-15: the coins are not a system
   of unit names).
4. Each unit is proposed as `partOf` the series' force, attributed to the
   series, dated by the type's dates, with the legend quoted. That a named unit
   served in the force is a reading of the coin, so these Proposals wait for the
   curator (they are not accepted by rule).

CRRO writes years before Christ as negative historical years (-0032 for 32 BC);
EDTF counts a year 0, so 32 BC is -0031. Without --apply it reports and rolls
back. Retry-safe.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, QualifierQuotation, Quotation, TimeQualifier
from GraphRevised.proposals.store import submit

GRAPH_REVISED = Path(__file__).resolve().parents[1]
DUMP = GRAPH_REVISED / "crro" / "nomisma.rdf"
SERIES = GRAPH_REVISED / "curation" / "coin-series.json"
RUNS = GRAPH_REVISED / "runs"
PROPOSER = "crro-coin-series"
LEGEND_PROPOSER = "crro-coin-legend"  # what a legend literally says (LEG: a legion); accepted by rule (D-145)
VERSION = "crro-coins-v1"
RIGHTS = ("Open Database License 1.0 (https://opendatacommons.org/licenses/odbl/1-0/); "
          "Coinage of the Roman Republic Online, American Numismatic Society")
NS = {"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "nmo": "http://nomisma.org/ontology#",
      "skos": "http://www.w3.org/2004/02/skos/core#", "dcterms": "http://purl.org/dc/terms/"}
ABOUT, RESOURCE = f"{{{NS['rdf']}}}about", f"{{{NS['rdf']}}}resource"
NUMERALS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
COHORTS = {"PRAETORIAR": ("praetorian cohorts", "praetorian-cohorts", "cohort"),
           "SPECVLATOR": ("cohort of scouts (speculatores)", "cohort-of-speculatores", "cohort")}


def roman(text: str) -> int | None:
    """A Roman numeral, including the subtractive IIX (8) and the additive IIII; PRI is 1."""
    text = text.upper()
    if text == "PRI":
        return 1
    if text.endswith("IIX"):  # a doubled subtraction (IIX for 8), as some legends write it
        head = roman(text[:-3]) if text[:-3] else 0
        return None if head is None else head + 8
    if not text or set(text) - set(NUMERALS):
        return None
    total = 0
    for i, char in enumerate(text):
        value = NUMERALS[char]
        total += -value if i + 1 < len(text) and NUMERALS[text[i + 1]] > value else value
    return total


def unit(legend: str) -> dict[str, Any] | None:
    """The unit a reverse legend names: {key, name, kind, title}, or None. A title does not make another unit."""
    words = [w for w in re.split(r"[\s·.\u00b7]+", legend.replace(" or ", " | ").split(" | ")[0]) if w]
    if words and words[0].upper() == "LEG" and len(words) >= 2:
        number = roman(words[1])
        if number is None:
            return None
        # The coin's capitals (V for U) and genitive (ANTIQVAE) to the name (Antiqua); LYBICAE is Libyca.
        title = " ".join(w.upper().replace("V", "U").capitalize() for w in words[2:])
        title = re.sub(r"ae$", "a", title).replace("Lybica", "Libyca")
        return {"key": f"legion-{number}", "name": f"legion {number}", "kind": "legion", "title": title or None}
    for stem, (name, key, kind) in COHORTS.items():
        if stem in legend.upper().replace(" ", ""):
            return {"key": key, "name": name, "kind": kind, "title": None}
    return None


def bc(year: str) -> int:
    """A CRRO year (-0032) as the BC year it means (32)."""
    return -int(year)


def edtf_year(year_bc: int) -> str:
    return f"-{year_bc - 1:04d}"


def read_series(path: Path, series: str) -> list[dict[str, Any]]:
    root = ET.parse(path).getroot()
    items, sides = {}, {}
    prefix = f"/crro/id/{series}."
    for element in root:
        about = element.get(ABOUT, "")
        if prefix in about:
            (sides if "#" in about else items)[about] = element

    def text(el, tag):
        found = el.find(tag, NS) if el is not None else None
        return found.text.strip() if found is not None and found.text else None

    def resource(el, tag):
        found = el.find(tag, NS)
        return found.get(RESOURCE).rsplit("/", 1)[-1] if found is not None else None

    types = []
    for uri, el in sorted(items.items()):
        if el.find("nmo:hasReverse", NS) is None:
            continue  # a parent grouping, not a type
        obverse, reverse = sides.get(uri + "#obverse"), sides.get(uri + "#reverse")
        types.append({"uri": uri, "label": text(el, "skos:prefLabel"), "denomination": resource(el, "nmo:hasDenomination"),
                      "issuer": resource(el, "nmo:hasIssuer"), "mint": resource(el, "nmo:hasMint"),
                      "start": text(el, "nmo:hasStartDate"), "end": text(el, "nmo:hasEndDate"),
                      "obverseLegend": text(obverse, "nmo:hasLegend"), "obverse": text(obverse, "dcterms:description"),
                      "reverseLegend": text(reverse, "nmo:hasLegend"), "reverse": text(reverse, "dcterms:description")})
    return types


def record_text(t: dict[str, Any]) -> tuple[str, str, str]:
    """The record's text, the reverse-legend line, and the date line (quoted as evidence)."""
    date = f"Date: {bc(t['start'])}\u2013{bc(t['end'])} BC (CRRO: {t['start']} to {t['end']})"
    legend = f"Reverse legend: {t['reverseLegend']}"
    lines = [f"{t['label']} (Coinage of the Roman Republic Online): {t['denomination']}, issuer {t['issuer']}, "
             f"mint {t['mint']}", date, f"Obverse legend: {t['obverseLegend']}", f"Obverse: {t['obverse']}",
             legend, f"Reverse: {t['reverse']}"]
    return "\n".join(lines), legend, date


def harvest(tx, operations, registry, config: dict[str, Any], types: list[dict[str, Any]], at: str) -> dict[str, Any]:
    work, force = config["work"], config["force"]
    for entity, kind in ((work, "Work"), (force, "Group")):
        exists = tx.run("MATCH (e:Entity {id: $id}) RETURN e.id", id=entity["id"]).single() is not None
        run_write(tx, operations, "upsert_entity", {"id": entity["id"], "kind": kind, "label": entity["label"],
                                                    "shortLabel": entity["shortLabel"], "description": entity["description"],
                                                    "status": None if exists else "proposed"})
    run_write(tx, operations, "set_work_form", {"workId": work["id"], "form": work["form"],
                                                "allowedForms": sorted(registry.work_forms)})
    run_write(tx, operations, "set_work_standing", {"id": work["id"], "standing": work["standing"], "decidedAt": at,
                                                    "decidedBy": "curator (2026-11-15, D-151)",
                                                    "decisionBasis": "a coin series is its issuer's own ancient voice"})
    payload = DUMP.read_bytes()
    dump_hash = hashlib.sha256(payload).hexdigest()
    by_unit: dict[str, list[tuple[dict, str, str, str]]] = defaultdict(list)
    skipped = []
    for t in types:
        text, legend_line, date_line = record_text(t)
        observation_id = f"chr:observation:crro:{t['uri'].rsplit('/', 1)[-1]}:{dump_hash[:12]}"
        run_write(tx, operations, "upsert_record_observation", {
            "id": observation_id, "label": f"{t['label']}, {t['denomination']} (CRRO)", "shortLabel": t["label"],
            "sourceSystem": "Coinage of the Roman Republic Online", "sourceEntityId": t["uri"], "locator": t["uri"],
            "passageText": text, "passageHash": hashlib.sha256(text.encode("utf-8")).hexdigest(), "editorialNotes": [],
            "language": "la", "workTitle": work["label"], "author": t["issuer"],
            "editionCitation": "M. H. Crawford, Roman Republican Coinage (1974), as Coinage of the Roman Republic Online",
            "rights": RIGHTS, "sourceUri": "http://numismatics.org/crro/nomisma.rdf", "sourceRevision": None,
            "retrievedAt": datetime.fromtimestamp(DUMP.stat().st_mtime, timezone.utc).isoformat(timespec="seconds"),
            "contentHash": dump_hash, "rawPayloadUri": DUMP.relative_to(GRAPH_REVISED.parent).as_posix(),
            "workId": work["id"]})
        named = unit(t["reverseLegend"] or "")
        if named is None:
            skipped.append(t["label"])
            continue
        by_unit[named["key"]].append((named, observation_id, legend_line, date_line, t))
    outcomes = []
    for key, found in sorted(by_unit.items()):
        named = found[0][0]
        unit_id = config["unitIdPrefix"] + key
        exists = tx.run("MATCH (e:Entity {id: $id}) RETURN e.id", id=unit_id).single() is not None
        legends = sorted({f[4]["reverseLegend"] for f in found})
        titles = sorted({f[0]["title"] for f in found if f[0]["title"]})
        description = config["unitDescription"].format(kind=named["kind"])
        if titles:
            also = ", ".join(f"{named['name']} {t}" for t in titles)
            description += f" Named on the coins as {' and '.join(legends)}; also called {also}."
        run_write(tx, operations, "upsert_entity", {
            "id": unit_id, "kind": "Group", "label": config["unitLabel"].format(unit=named["name"]),
            "shortLabel": named["name"].capitalize(), "description": description,
            "status": None if exists else "proposed"})
        starts, ends = [bc(f[4]["start"]) for f in found], [bc(f[4]["end"]) for f in found]
        first, last = max(starts), min(ends)
        draft = ProposalDraft(
            predicate="partOf", subject_id=unit_id, object_id=force["id"], mode="attributed", attributed_to=work["id"],
            observation_ids=tuple(f[1] for f in found),
            quotations=tuple(Quotation(observation_id=f[1], text=f[2]) for f in found),
            time=TimeQualifier(source_expression=found[0][3], edtf=f"{edtf_year(first)}/{edtf_year(last)}",
                               calendar="julian", normalization_basis="scholarship"),
            qualifier_quotations=(QualifierQuotation(observation_id=found[0][1], supports="time", text=found[0][3]),),
            rationale=(f"{work['shortLabel']} of {first}\u2013{last} BC names the {named['name']} on "
                       f"{len(found)} type{'s' if len(found) > 1 else ''} ({', '.join(f[4]['label'] for f in found)}), "
                       f"so the unit served in his forces in those years. A reading of the coin: whether the series "
                       f"names every unit, or only some, is debated, and it does not place the unit at any one battle."),
            proposed_by=PROPOSER, prompt_version=VERSION,
            relevance="Which units the force had, from its commander's own coins: an ancient line independent of the texts.")
        result = submit(tx, draft, registry, operations)
        type_id = config.get("unitTypes", {}).get(named["kind"])
        if type_id:
            kind_draft = ProposalDraft(
                predicate="instanceOf", subject_id=unit_id, object_id=type_id, mode="attributed",
                attributed_to=work["id"], observation_ids=(found[0][1],),
                quotations=(Quotation(observation_id=found[0][1], text=found[0][2]),),
                rationale=f"The legend names the unit as a {named['kind']} ({found[0][4]['reverseLegend']}).",
                proposed_by=LEGEND_PROPOSER, prompt_version=VERSION,
                relevance="What kind of unit each named unit was, in the coin's own words.")
            submit(tx, kind_draft, registry, operations)
        outcomes.append({"unit": unit_id, "types": [f[4]["label"] for f in found], "outcome": result.validation.outcome.value,
                         "stored": result.stored, "reasons": list(result.validation.reasons)})
    return {"types": len(types), "units": len(by_unit), "skipped": skipped, "outcomes": outcomes}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("series", help="a series id in curation/coin-series.json, such as rrc-544")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    config = next((s for s in json.loads(SERIES.read_text(encoding="utf-8"))["series"] if s["id"] == args.series), None)
    if config is None:
        parser.error(f"{args.series} is not in {SERIES.name}")
    types = read_series(DUMP, args.series)
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                report = harvest(tx, load_operations(), load_registry(), config, types, at)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print(f"{report['types']} coin types -> {report['units']} units ({'applied' if args.apply else 'dry run, rolled back'})")
    for o in report["outcomes"]:
        print(f"  {o['outcome']:10} {o['unit']} <- {', '.join(o['types'])}" + (f"  {o['reasons']}" if o["reasons"] else ""))
    if report["skipped"]:
        print("no unit named on:", ", ".join(report["skipped"]))
    RUNS.mkdir(exist_ok=True)
    (RUNS / f"crro-{args.series}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json").write_text(
        json.dumps(report | {"applied": args.apply}, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
