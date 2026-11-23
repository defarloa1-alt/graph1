"""Export the exploration view for Cytoscape: entities as nodes, facts as edges.

    python -m GraphRevised.export.cytoscape [--audit] [--out GraphRevised/exports/graph]

Writes <out>.cyjs (Cytoscape JSON: import in Cytoscape desktop with File >
Import > Network from File, or pass `elements` to Cytoscape.js) and
<out>.html (a self-contained Cytoscape.js page to open in a browser).

Read-only. Everything found is shown at once (25-LIVES-AND-PLAYGROUND.md
decision 2): accepted and proposed claims and every entity (proposed ones
too, and those no claim touches yet), labelled with status and source.

One edge is one fact: all claims with the same predicate, subject, and
object (our own asserted claim and each source's attributed version) are
drawn as a single line, kept apart only by category, so imagined versions
form their own line (26-UI-DATA-CONTRACT.md). The fact carries its
attestation in words (export/confidence.py), and each claim behind it is a
voice: who says it ("according to <Work>", or our own statement), its time,
role, and context in that source, the quotations with their locators
(counting evidence still pending on open Proposals), and its review history.
A unary fact (such as `occurred`) has no object and is listed on its subject
node. Proposals, source observations, and Years never become nodes. Each
entity carries the passages of note and mentions that concern it, and its
authority records as a quiet footer: one per system, the best-supported
first, the others counted (26 §4). Rejected
and superseded claims, deprecated entities, and dismissed notes appear only
with --audit. Annotations are included whatever their visibility, so the
output (git-ignored) is the curator's own view. This is a smoke view, not
the explorer (20-EXPLORER-UI.md).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.export import display as display_rules
from GraphRevised.export.confidence import (LIVE, POSITION_LINKS, claim_lines, confidence, family_key,
                                             position_history, position_link_wording)
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.temporal import display_edtf
from GraphRevised.proposals.validator import quantity_key
from GraphRevised import localdb

GRAPH_REVISED = Path(__file__).resolve().parents[1]
AUTHORITIES_PATH = GRAPH_REVISED / "curation" / "authorities.json"  # its "networks": the federation profile

VISIBLE = ["accepted", "proposed"]
AUDIT = VISIBLE + ["rejected", "superseded"]
OPEN_PROPOSALS = ["submitted", "validating", "deferred"]

ENTITY = "{.id, .label, .shortLabel, .status, .description}"
ENTITY_E = "{.id, .label, .shortLabel, .status, .description, kind: head([label IN labels(e) WHERE label <> 'Entity'])}"
ENTITY_S = "{.id, .label, .shortLabel, .status, .description, kind: head([label IN labels(s) WHERE label <> 'Entity'])}"
ENTITY_O = "{.id, .label, .shortLabel, .status, .description, kind: head([label IN labels(o) WHERE label <> 'Entity'])}"

ENTITIES = f"""
MATCH (e:Entity) WHERE $audit OR e.status <> "deprecated"
RETURN e {ENTITY_E} AS entity,
       COLLECT {{
         MATCH (n:Annotation)-[:CONCERNS]->(e) WHERE $audit OR n.status <> "dismissed"
         OPTIONAL MATCH (n)-[:ANNOTATES]->(o:SourceObservation)
         RETURN n {{.id, .kind, .noteType, .note, .status, source: o.shortLabel}} ORDER BY o.shortLabel, n.id
       }} AS notes,
       COLLECT {{
         // where a Place lies, from its gazetteer Location (27): Pleiades first, then GeoNames
         MATCH (e)-[at:AT_LOCATION]->(l:Location)
         WHERE l.location IS NOT NULL AND coalesce(at.status, "accepted") <> "rejected"
         RETURN {{lat: l.location.y, lon: l.location.x, source: l.system + " " + l.identifier}}
         ORDER BY l.system = "Pleiades" DESC, l.identifier
       }}[0] AS coordinates,
       COLLECT {{
         // the gazetteer records a Place is linked to, for the card's Elsewhere block (display rule 7)
         MATCH (e)-[at:AT_LOCATION]->(l:Location)
         WHERE $audit OR coalesce(at.status, "accepted") <> "rejected"
         RETURN {{system: l.system, identifier: l.identifier, label: l.label,
                 status: coalesce(at.status, "accepted"), basis: at.basis}}
         ORDER BY l.system, l.identifier
       }} AS gazetteer,
       COLLECT {{
         // a rejected link is history (retire_entity_identity): readers follow the rest; the audit shows it
         MATCH (e)-[link:HAS_AUTHORITY_RECORD]->(a:AuthorityRecord)
         WHERE $audit OR coalesce(link.status, "accepted") <> "rejected"
         RETURN {{system: a.system, identifier: a.identifier, label: a.label, role: link.role,
                 status: coalesce(link.status, "accepted"), relation: link.relation,
                 rank: link.statementRank, references: link.statementReferences, sourceUri: a.sourceUri}}
       }} AS authority
"""

CLAIMS = f"""
MATCH (a:Assertion) WHERE a.status IN $statuses
MATCH (a)-[:ASSERTION_SUBJECT]->(s:Entity)
OPTIONAL MATCH (a)-[:ASSERTION_OBJECT]->(o:Entity)
RETURN a {{.id, .label, .shortLabel, .predicate, .status, .mode, .category, .basis, .timeEdtf, .timeSourceExpression,
            .quantitySourceExpression, .quantityMinimum, .quantityMaximum, .quantityTypical, .stance, .reception,
            start: a.startEarliestJdn, end: a.endLatestJdn}} AS claim,
       s {ENTITY_S} AS subject, o {ENTITY_O} AS object,
       COLLECT {{ MATCH (a)-[:ASSERTION_CONTEXT]->(c:Entity) RETURN c {{.id, .label}} }}[0] AS context,
       COLLECT {{ MATCH (a)-[:ASSERTION_ROLE]->(r:Entity) RETURN r {{.id, .label}} }}[0] AS role,
       COLLECT {{ MATCH (a)-[:ATTRIBUTED_TO]->(w:Entity) RETURN w {{.id, .label}} }}[0] AS work,
       COLLECT {{ MATCH (a)-[link:SUPPORTED_BY]->(ev:SourceObservation)
                 OPTIONAL MATCH (ev)-[:IN_WORK]->(w:Entity)
                 RETURN {{key: coalesce(w.id, ev.sourceSystem), label: coalesce(w.label, ev.sourceSystem),
                         locator: ev.shortLabel, href: ev.locator, quotation: link.quotation, pending: false}} AS source
                 UNION
                 MATCH (p:Proposal)-[:PROPOSES]->(a) WHERE p.status IN $open
                 MATCH (p)-[link:PROPOSES_EVIDENCE]->(ev:SourceObservation)
                 OPTIONAL MATCH (ev)-[:IN_WORK]->(w:Entity)
                 RETURN {{key: coalesce(w.id, ev.sourceSystem), label: coalesce(w.label, ev.sourceSystem),
                         locator: ev.shortLabel, href: ev.locator, quotation: link.quotation, pending: true}} AS source
               }} AS sources,
       COLLECT {{ MATCH (p:Proposal)-[:PROPOSES]->(a)
                 RETURN p {{.status, .operation, .decidedBy, .decidedAt}} ORDER BY p.decidedAt }} AS proposals,
       COLLECT {{ MATCH (a)-[r:RESTS_ON]->(t) WHERE coalesce(r.status, "accepted") IN ["accepted", "proposed"]
                 // Only text we hold counts: an ancient claim, or a passage; a Work alone does not (D-148).
                 UNWIND CASE WHEN t:Assertion
                        THEN [(t)-[:ATTRIBUTED_TO]->(tw:Entity) | tw.id]
                             + [(t)-[:SUPPORTED_BY]->(:SourceObservation)-[:IN_WORK]->(ew:Entity) | ew.id]
                        WHEN t:SourceObservation THEN [(t)-[:IN_WORK]->(pw:Entity) | pw.id]
                        ELSE [] END AS target
                 RETURN DISTINCT target }} AS restsOn
"""

WORKS = """
MATCH (w:Work)
RETURN w.id AS id, w.label AS label, w.shortLabel AS shortLabel, w.standing AS standing, w.form AS form
"""

AUTHORS = """
MATCH (claim:Assertion {predicate: "authorOf"})-[:ASSERTION_SUBJECT]->(author:Entity)
MATCH (claim)-[:ASSERTION_OBJECT]->(work:Entity)
WHERE claim.status IN $live
RETURN work.id AS work, author.id AS author
"""

STYLE = [
    {"selector": "node", "style": {"label": "data(label)", "font-size": 9, "text-wrap": "wrap",
                                   "text-max-width": 110, "background-color": "#8a8f98", "width": 22, "height": 22}},
    {"selector": "node[kind = 'Person']", "style": {"background-color": "#4f7bd9"}},
    {"selector": "node[kind = 'Group']", "style": {"background-color": "#2fa37a", "shape": "round-rectangle"}},
    {"selector": "node[kind = 'Event']", "style": {"background-color": "#d9822b", "shape": "diamond", "width": 30, "height": 30}},
    {"selector": "node[kind = 'Place']", "style": {"background-color": "#a35fc2", "shape": "triangle"}},
    {"selector": "node[kind = 'Work']", "style": {"background-color": "#b8a13a", "shape": "rectangle"}},
    {"selector": "node[kind = 'Period']", "style": {"background-color": "#3a9fb8", "shape": "barrel", "width": 34}},
    {"selector": "node[kind = 'Concept']", "style": {"background-color": "#c2607f", "shape": "hexagon"}},
    {"selector": "node[kind = 'Polity']", "style": {"background-color": "#7a5c3a", "shape": "octagon", "width": 30, "height": 30}},
    {"selector": "node[kind = 'Type']", "style": {"background-color": "#5c6b7a", "shape": "tag"}},
    {"selector": "node[kind = 'Question']", "style": {"background-color": "#6a5acd", "shape": "star", "width": 28, "height": 28}},
    {"selector": "node[kind = 'Position']", "style": {"background-color": "#8f7fe0", "shape": "round-diamond"}},
    {"selector": "node[kind = 'Law']", "style": {"background-color": "#9a6b2f", "shape": "cut-rectangle"}},
    {"selector": "node[kind = 'Decree']", "style": {"background-color": "#b58a52", "shape": "cut-rectangle"}},
    {"selector": "node[status = 'proposed']", "style": {"background-opacity": 0.35, "border-width": 2,
                                                         "border-style": "dashed", "border-color": "#777"}},
    {"selector": "node[status = 'deprecated']", "style": {"opacity": 0.35}},
    {"selector": "edge", "style": {"label": "data(label)", "font-size": 7, "curve-style": "bezier",
                                   "target-arrow-shape": "triangle", "width": 1.5, "line-color": "#666",
                                   "target-arrow-color": "#666", "text-rotation": "autorotate"}},
    {"selector": "edge[status = 'proposed']", "style": {"line-style": "dashed", "line-color": "#b0b0b0",
                                                         "target-arrow-color": "#b0b0b0", "color": "#888"}},
    {"selector": "edge[status = 'rejected']", "style": {"line-style": "dotted", "line-color": "#c0392b",
                                                         "target-arrow-color": "#c0392b", "opacity": 0.6}},
    {"selector": "edge[status = 'superseded']", "style": {"line-style": "dotted", "opacity": 0.45}},
    {"selector": "edge[mode = 'attributed']", "style": {"source-arrow-shape": "circle", "source-arrow-fill": "hollow"}},
    {"selector": "edge[category = 'imaginative']", "style": {"line-color": "#c2607f", "target-arrow-color": "#c2607f",
                                                              "line-style": "dotted", "color": "#a0506b"}},
    # a folded line (export/display.py) stays on its card and in the data; the canvas leaves it out
    {"selector": "edge[fold]", "style": {"display": "none"}},
]


def work_short_name(label: str, short: str | None) -> str:
    """How attestation names a source: the author of an "Author, Title" label, else its short label."""
    return label.split(", ", 1)[0] if ", " in label else (short or label)


def note_line(note: dict[str, Any]) -> str:
    kind = note.get("noteType") if note.get("kind") == "passage-of-note" else note.get("kind")
    where = ", ".join(part for part in (note.get("source"), note.get("status")) if part)
    return f"{kind}: {note.get('note')} ({where})"


RANK_ORDER = {"preferred": 0, "normal": 1}
LINK_ORDER = {"accepted": 0, "proposed": 1, "rejected": 2}


def authority_footer(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The card's quiet footer: one record per system, the identity first, then by system name.
    Within a system an accepted link wins over a proposed one, then the best-supported statement
    (preferred rank, then most references, then identifier); the rest are counted, not listed,
    and stay in the graph. A proposed or rejected (audit only) link keeps its status (rule 3)."""
    systems: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        systems.setdefault(record["system"], []).append(record)
    footer = []
    for system, group in systems.items():
        best = min(group, key=lambda r: (LINK_ORDER.get(r.get("status") or "accepted", 3),
                                         r.get("role") != "entity_identity", RANK_ORDER.get(r.get("rank"), 2),
                                         -(r.get("references") or 0), r["identifier"]))
        footer.append({"system": system, "identifier": best["identifier"], "label": best["label"],
                       "role": best.get("role"), "others": len(group) - 1,
                       "status": best.get("status") or "accepted", "relation": best.get("relation"),
                       # where the record was fetched from; display rule 7 says whose payload that was
                       "sourceUri": best.get("sourceUri")})
    return sorted(footer, key=lambda f: (f["role"] != "entity_identity", f["system"]))


def authority_line(entry: dict[str, Any]) -> str:
    status = entry.get("status") or "accepted"
    return (entry["label"] + (f" and {entry['others']} more" if entry["others"] else "")
            + (f" ({status})" if status != "accepted" else ""))


OUR_OWN = "our own statement"


def _time(claim: dict[str, Any]) -> str | None:
    return display_edtf(claim["timeEdtf"]) if claim.get("timeEdtf") else claim.get("timeSourceExpression")


def passage_url(locator: str | None) -> str | None:
    """Where a reader can open the passage: the locator when it is already a link (LacusCurtius,
    Gutenberg, Wikipedia keep the page and anchor there), a Scaife reader link for a Perseus CTS
    passage, otherwise none (a curator's page number)."""
    if not locator:
        return None
    if locator.startswith(("https://", "http://")):
        return locator.split(" (", 1)[0]
    if locator.startswith("urn:cts:"):
        return f"https://scaife.perseus.org/reader/{locator}/"
    return None


def _voice(row: dict[str, Any]) -> dict[str, Any]:
    """One claim behind a fact: who says it, in what terms, on what evidence, reviewed how."""
    claim = row["claim"]
    quotes = sorted(({"source": s["label"], "locator": s["locator"], "url": passage_url(s.get("href")),
                      "quotation": s["quotation"], "pending": s["pending"]} for s in row["sources"]),
                    key=lambda q: q["locator"] or "")
    return {
        "claimId": claim["id"], "status": claim["status"], "mode": claim.get("mode") or "asserted",
        "accordingTo": (row["work"] or {}).get("label"), "time": _time(claim),
        "role": (row["role"] or {}).get("label"), "context": (row["context"] or {}).get("label"),
        "quantity": claim.get("quantitySourceExpression"),
        "stance": claim.get("stance"), "reception": claim.get("reception"),
        "quotes": quotes, "review": [p for p in row["proposals"] if p.get("status")],
        "basis": claim.get("basis"), "restsOn": row.get("restsOn", []),
    }


def voice_line(voice: dict[str, Any]) -> str:
    who = f"according to {voice['accordingTo']}" if voice["accordingTo"] else "our own statement"
    terms = "; ".join(part for part in (voice["time"], voice["role"] and f"as {voice['role']}",
                                        voice["context"] and f"during {voice['context']}",
                                        voice.get("quantity") and f"quantity: {voice['quantity']}",
                                        voice.get("stance") and f"stance: {voice['stance']}",
                                        voice.get("reception")) if part)
    quotes = " ".join(f"{q['locator']}: “{q['quotation']}”" + (" (pending)" if q["pending"] else "")
                      for q in voice["quotes"] if q["quotation"]) or "no evidence of its own"
    return f"{who} [{voice['status']}]" + (f" ({terms})" if terms else "") + f" — {quotes}"


def review_line(voice: dict[str, Any]) -> str:
    steps = ", ".join(f"{p['operation'] or 'proposal'} {p['status']}"
                      + (f" by {p['decidedBy']} {p['decidedAt'][:10]}" if p.get("decidedBy") else "")
                      for p in voice["review"])
    return f"{voice['accordingTo'] or 'our own statement'}: {steps or 'no review records'}"


def projection(tx: Any, audit: bool = False) -> dict[str, Any]:
    registry = load_registry()
    nodes: dict[str, dict[str, Any]] = {}

    def node(entity: dict[str, Any], notes: list[dict[str, Any]] = (), authority: list[dict[str, Any]] = (),
             coordinates: dict[str, Any] | None = None, gazetteer: list[dict[str, Any]] = ()) -> None:
        footer = authority_footer(list(authority))
        nodes.setdefault(entity["id"], {"data": {
            "id": entity["id"], "label": entity.get("shortLabel") or entity["label"], "fullLabel": entity["label"],
            "kind": entity["kind"], "status": entity.get("status"), "description": entity.get("description"),
            "notes": [note_line(n) for n in notes], "facts": [], "factLines": [],
            "authority": footer, "authorityLines": [authority_line(entry) for entry in footer],
            **({"coordinates": coordinates} if coordinates else {}),
            **({"gazetteer": list(gazetteer)} if gazetteer else {}),
        }})

    for row in tx.run(ENTITIES, audit=audit):
        node(row["entity"], row["notes"], row["authority"], row["coordinates"], row["gazetteer"])
    author_of = dict(tx.run(AUTHORS, live=list(LIVE)).values("work", "author"))
    works = list(tx.run(WORKS))
    standing = {w["id"]: w["standing"] for w in works if w["standing"]}
    work_name = {w["id"]: work_short_name(w["label"], w["shortLabel"]) for w in works}
    rows = list(tx.run(CLAIMS, statuses=AUDIT if audit else VISIBLE, open=OPEN_PROPOSALS))

    def holder_name(work: dict[str, Any]) -> str:
        """A Work as a historiography names it: by its author when an authorOf claim gives one."""
        author = nodes.get(author_of.get(work["id"], ""))
        return author["data"]["label"] if author else work_name.get(work["id"], work["label"])

    position_links: dict[str, list[dict[str, Any]]] = {}
    receptions: dict[str, list[dict[str, Any]]] = {}

    # Attestation is judged over the whole family; a fact is the family's members of one category.
    families: dict[str, list[dict[str, Any]]] = {}
    facts: dict[tuple[str, str], list[Any]] = {}
    for row in rows:
        claim = row["claim"]
        keys = [row["work"]["id"]] if row["work"] else []
        keys += [source["key"] for source in row["sources"]]
        member = {
            "status": claim["status"], "category": claim.get("category") or "factual",
            "authors": {author_of.get(key, key) for key in keys},
            "lines": claim_lines(keys, claim.get("basis"), row["restsOn"], standing, author_of, work_name),
            "context": (row["context"] or {}).get("id"), "role": (row["role"] or {}).get("id"),
            "quantity": quantity_key({key: claim.get("quantity" + key.capitalize())
                                      for key in ("minimum", "maximum", "typical")}),
            "start": claim.get("start"), "end": claim.get("end"),
        }
        families.setdefault(family_key(claim["id"]), []).append(member)
        facts.setdefault((family_key(claim["id"]), member["category"]), []).append(row)

    edges = []
    for (family, category), members in facts.items():
        first = members[0]
        subject, obj, predicate = first["subject"], first["object"], first["claim"]["predicate"]
        definition = registry.get(predicate)
        display = definition.display if definition else predicate
        statuses = {row["claim"]["status"] for row in members}
        status = next(s for s in ("accepted", "proposed", "rejected", "superseded") if s in statuses)
        live_modes = {row["claim"].get("mode") or "asserted" for row in members if row["claim"]["status"] in LIVE}
        voices = sorted((_voice(row) for row in members),
                        key=lambda v: (v["accordingTo"] is not None, v["accordingTo"] or "", v["claimId"]))
        attestation = confidence({"category": category, "once": bool(definition and definition.once)},
                                 families[family])
        if predicate in POSITION_LINKS and obj is not None:  # 44: a history, never a count of evidence
            attestation = position_link_wording(subject["id"], (
                {"status": row["claim"]["status"], "work": (row["work"] or {}).get("id"),
                 "name": holder_name(row["work"]) if row["work"] else OUR_OWN} for row in members))
            for row in members:
                work = row["work"] or {}
                position_links.setdefault(obj["id"], []).append({
                    "verb": predicate, "holder": subject["id"], "name": holder_name(subject),
                    "time": _time(row["claim"]), "start": row["claim"].get("start"),
                    "ancient": standing.get(subject["id"]) == "primary", "stance": row["claim"].get("stance"),
                    "reporter": holder_name(work) if work and work["id"] != subject["id"] else None,
                    "status": row["claim"]["status"], "claimId": row["claim"]["id"]})
        if predicate == "hadReception":
            for row in members:
                receptions.setdefault(subject["id"], []).append({
                    "reception": row["claim"].get("reception") or "reception not given",
                    "time": _time(row["claim"]), "according": holder_name(row["work"]) if row["work"] else None,
                    "status": row["claim"]["status"], "claimId": row["claim"]["id"]})
        fact = {
            "sentence": f"{subject['label']} {display}" + (f" {obj['label']}" if obj else ""),
            "predicate": predicate, "category": category, "status": status,
            "mode": "asserted" if "asserted" in live_modes else "attributed",
            "attestation": attestation,
            "times": sorted({v["time"] for v in voices if v["time"]}),
            "voices": voices,
            "voiceLines": [voice_line(v) for v in voices],
            "reviewLines": [review_line(v) for v in voices],
        }
        node(subject)  # an endpoint hidden from the entity list (deprecated) still anchors its fact
        if obj is None:
            nodes[subject["id"]]["data"]["facts"].append(fact)
            nodes[subject["id"]]["data"]["factLines"].append(
                f"{fact['sentence']} ({'; '.join(fact['times']) or 'undated'}) — {fact['attestation']}")
            continue
        node(obj)
        edges.append({"data": {"id": f"{family}#{category}", "source": subject["id"], "target": obj["id"],
                               "label": display, **fact}})

    # A Position's history and timeline (44 §3): who held and rejected it, when, and its reception.
    for position in set(position_links) | set(receptions):
        data = nodes[position]["data"]
        links, received = position_links.get(position, []), receptions.get(position, [])
        data["history"] = position_history(links, received)
        data["timeline"] = sorted(
            ({key: link[key] for key in ("verb", "holder", "name", "time", "start", "ancient", "stance",
                                         "reporter", "status", "claimId")} for link in links),
            key=lambda link: (not link["ancient"], link["start"] is None, link["start"] or 0, link["name"]))
        data["receptions"] = received
    # What each view shows is decided here, once: folds and hints that mark, never remove (export/display.py).
    for work in works:  # a Work's form (history, coinage, inscription...) says what kind of evidence it is
        if work["form"] and work["id"] in nodes:
            nodes[work["id"]]["data"]["form"] = work["form"]
    profile = json.loads(AUTHORITIES_PATH.read_text(encoding="utf-8")).get("networks")
    return {"elements": display_rules.apply({"nodes": list(nodes.values()), "edges": edges}, standing,
                                            networks=profile, creative_forms=registry.creative_forms)}


HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Graph Smoke View</title>
<style>
  :root {{ --bg: #fbfbfa; --fg: #1d1d1f; --muted: #6b6b70; --panel: #ffffff; --line: #e3e3e0; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg: #17181a; --fg: #ececec; --muted: #9a9aa0; --panel: #222326; --line: #333; }} }}
  html, body {{ margin: 0; height: 100%; background: var(--bg); color: var(--fg); font: 13px/1.4 system-ui, sans-serif; }}
  #cy {{ position: absolute; inset: 0 320px 0 0; }}
  #card {{ position: absolute; top: 0; right: 0; bottom: 0; width: 320px; box-sizing: border-box; padding: 16px;
          overflow: auto; background: var(--panel); border-left: 1px solid var(--line); }}
  #card h2 {{ font-size: 15px; margin: 0 0 8px; }} #card dt {{ color: var(--muted); margin-top: 8px; }} #card dd {{ margin: 0; }}
  #card ul {{ margin: 0; padding-left: 18px; }} #card li {{ margin-bottom: 4px; }}
  @media (max-width: 700px) {{ #cy {{ inset: 0 0 45% 0; }} #card {{ top: 55%; width: 100%; border-left: 0; border-top: 1px solid var(--line); }} }}
</style></head>
<body><div id="cy"></div><aside id="card"><h2>Click a node or claim</h2>
<p>One line per fact. Solid: accepted. Dashed: proposed. Hollow circle at the start: only "according to" its sources. Pink dotted: imagined.
Faded with a dashed border: a proposed entity. Nothing here is hidden for being unreviewed. A line another route already says (a moment in a phase, a reference work) is folded: its node card counts it.</p></aside>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.30.2/cytoscape.min.js"></script>
<script>
const graph = {graph};
const cy = cytoscape({{ container: document.getElementById("cy"), elements: graph.elements, style: {style},
                        layout: {{ name: "cose", animate: false, nodeRepulsion: 9000, idealEdgeLength: 120 }} }});
const card = document.getElementById("card");
const esc = s => String(s ?? "").replace(/[&<>]/g, c => ({{"&": "&amp;", "<": "&lt;", ">": "&gt;"}}[c]));
function show(title, fields) {{
  card.innerHTML = `<h2>${{esc(title)}}</h2><dl>` + fields.filter(([, v]) => v !== null && v !== undefined && v !== "" &&
    !(Array.isArray(v) && !v.length)).map(([k, v]) => `<dt>${{esc(k)}}</dt><dd>${{Array.isArray(v) ?
    "<ul>" + v.map(item => `<li>${{esc(item)}}</li>`).join("") + "</ul>" : esc(v)}}</dd>`).join("") + "</dl>";
}}
cy.on("tap", "node", e => {{ const d = e.target.data(); show(d.fullLabel, [["not to be confused with others named so", d.hint],
  ["kind", d.kind], ["status", d.status], ["standing", d.standingWords],
  ["lines folded on the canvas", Object.entries(d.folded || {{}}).map(([why, n]) => `${{n}} ${{why}}`)],
  ["description", d.description], ["history", d.history], ["facts", d.factLines], ["passages of note and mentions", d.notes],
  ["authority records", d.authorityLines], ["id", d.id]]); }});
cy.on("tap", "edge", e => {{ const d = e.target.data(); show(d.sentence, [["attestation", d.attestation],
  ["status", d.status], ["category", d.category], ["when", d.times.join("; ")], ["voices", d.voiceLines],
  ["review history", d.reviewLines], ["folded on the canvas", d.fold && (d.fold + (d.foldVia ? " (via " + d.foldVia + ")" : ""))],
  ["fact id", d.id]]); }});
</script></body></html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--audit", action="store_true",
                        help="also show rejected and superseded claims, deprecated entities, and dismissed notes")
    parser.add_argument("--out", type=Path, default=GRAPH_REVISED / "exports" / "graph")
    args = parser.parse_args(argv)
    driver = GraphDatabase.driver(
        localdb.uri(),
        auth=localdb.auth(),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=localdb.database()) as session:
            graph = session.execute_read(projection, args.audit)
    finally:
        driver.close()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cyjs = {"format_version": "1.0", "generated_by": "GraphRevised.export.cytoscape", "data": {"name": args.out.stem},
            **graph}
    args.out.with_suffix(".cyjs").write_text(json.dumps(cyjs, ensure_ascii=False, indent=1), encoding="utf-8")
    page = HTML.format(graph=json.dumps(graph, ensure_ascii=False).replace("</", "<\\/"), style=json.dumps(STYLE))
    args.out.with_suffix(".html").write_text(page, encoding="utf-8")
    elements = graph["elements"]
    print(f"{len(elements['nodes'])} nodes, {len(elements['edges'])} fact edges")
    print(f"{args.out.with_suffix('.cyjs')}\n{args.out.with_suffix('.html')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
