"""The curator's review desk (interim, 2026-11-13).

    python -m GraphRevised.review_desk.app [--entity <entity-id>] [--by "<name>"] [--port 7860]

A local Gradio page on http://127.0.0.1:7860, against the local Neo4j only:

1. Find an entity by name; its summary (when, where, part of) and every live
   claim it is the subject or object of, one row per claim (one voice).
2. Pick a claim: its sentence, who says it, the quotations with their
   passages, the rationale and review history, and its open proposals.
3. Accept, or reject with a reason code and optionally the claim itself.
   The decision runs proposals/store.accept or reject (which re-validate the
   evidence), then rebuilds the fact layer (export/fact_layer.py), in one
   transaction: if anything fails, nothing is written.
4. Go to the claim's other entity, or to the next part of the entity that
   still has open proposals.

Reads NEO4J_PASSWORD (and optional NEO4J_URI, NEO4J_USERNAME, NEO4J_DATABASE).
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from typing import Any

import gradio as gr
from neo4j import GraphDatabase

from GraphRevised.export.cytoscape import passage_url
from GraphRevised.export.fact_layer import rebuild
from GraphRevised.operations import load_operations
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.store import REASON_CODES, ReviewError, accept, reject
from GraphRevised.proposals.temporal import display_edtf

OPEN = ["submitted", "validating", "deferred"]
LIVE = ["accepted", "proposed"]
HEADERS = ["#", "relation", "other end", "status", "according to", "time", "open"]

FIND = """
MATCH (e:Entity) WHERE e.status <> 'deprecated'
  AND (toLower(e.label) CONTAINS toLower($text) OR toLower(coalesce(e.shortLabel, '')) CONTAINS toLower($text)
       OR e.id = $text)
RETURN e.id AS id, e.label AS label, head([l IN labels(e) WHERE l <> 'Entity']) AS kind,
       COUNT { (e)<-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]-(:Assertion) } AS claims
ORDER BY claims DESC, size(e.label) LIMIT 40
"""

ENTITY = """
MATCH (e:Entity {id: $id})
RETURN e.id AS id, e.label AS label, e.status AS status, e.description AS description,
       e.when AS when, e.where AS where, e.partOf AS partOf,
       head([l IN labels(e) WHERE l <> 'Entity']) AS kind
"""

CLAIMS = """
MATCH (a:Assertion)-[end:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(:Entity {id: $id}) WHERE a.status IN $live
MATCH (a)-[:ASSERTION_SUBJECT]->(s:Entity)
OPTIONAL MATCH (a)-[:ASSERTION_OBJECT]->(o:Entity)
OPTIONAL MATCH (a)-[:ATTRIBUTED_TO]->(w:Entity)
OPTIONAL MATCH (a)-[:ASSERTION_ROLE]->(r:Entity)
RETURN a.id AS id, a.label AS sentence, a.predicate AS predicate, a.status AS status,
       coalesce(a.mode, 'asserted') AS mode, coalesce(a.category, 'factual') AS category,
       a.timeEdtf AS edtf, a.timeSourceExpression AS timeText, type(end) = 'ASSERTION_SUBJECT' AS outgoing,
       s.id AS subjectId, s.label AS subject, o.id AS objectId, o.label AS object, w.label AS work, r.label AS role,
       COLLECT { MATCH (p:Proposal)-[:PROPOSES]->(a) WHERE p.status IN $open RETURN p.id } AS open
"""

DETAIL = """
MATCH (a:Assertion {id: $id})
RETURN a.label AS sentence, a.status AS status, a.mode AS mode, a.category AS category,
       a.timeSourceExpression AS timeText, a.timeEdtf AS edtf,
       COLLECT { MATCH (a)-[:ASSERTION_ROLE]->(r:Entity) RETURN r.label }[0] AS role,
       COLLECT { MATCH (a)-[:ASSERTION_CONTEXT]->(c:Entity) RETURN c.label }[0] AS context,
       COLLECT { MATCH (a)-[l:SUPPORTED_BY]->(o:SourceObservation)
                 RETURN {proposal: null, locator: o.shortLabel, href: o.locator, quotation: l.quotation,
                         passage: o.passageText, system: o.sourceSystem} } AS accepted,
       COLLECT { MATCH (p:Proposal)-[:PROPOSES]->(a)
                 RETURN {id: p.id, status: p.status, by: p.createdBy, rationale: p.rationale,
                         decidedBy: p.decidedBy, decidedAt: p.decidedAt, basis: p.decisionBasis,
                         reason: p.decisionReason,
                         evidence: COLLECT { MATCH (p)-[l:PROPOSES_EVIDENCE]->(o:SourceObservation)
                                             RETURN {locator: o.shortLabel, href: o.locator, quotation: l.quotation,
                                                     passage: o.passageText, system: o.sourceSystem} }}
                 ORDER BY p.status, p.id } AS proposals
"""

PARTS = """
MATCH (part:Entity)<-[:ASSERTION_SUBJECT]-(a:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(:Entity {id: $id})
WHERE a.status IN $live
WITH DISTINCT part
RETURN part.id AS id, part.label AS label,
       COUNT { (part)<-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]-(:Assertion)<-[:PROPOSES]-(p:Proposal)
               WHERE p.status IN $open } AS open
ORDER BY part.label
"""


def find(tx: Any, text: str) -> list[dict[str, Any]]:
    return tx.run(FIND, text=text.strip()).data() if text.strip() else []


def entity(tx: Any, entity_id: str) -> dict[str, Any] | None:
    record = tx.run(ENTITY, id=entity_id).single()
    return record.data() if record else None


def claims(tx: Any, entity_id: str) -> list[dict[str, Any]]:
    """Every live claim the entity takes part in, ordered by relation, then the other end, then the voice."""
    registry = load_registry()
    rows = []
    for row in tx.run(CLAIMS, id=entity_id, live=LIVE, open=OPEN).data():
        definition = registry.get(row["predicate"])
        display = definition.display if definition else row["predicate"]
        if row["outgoing"]:
            relation, other_id, other = display, row["objectId"], row["object"]
        else:
            relation, other_id, other = f"← {display}", row["subjectId"], row["subject"]
        row.update(relation=relation, otherId=other_id, other=other or "—",
                   time=display_edtf(row["edtf"]) if row["edtf"] else row["timeText"],
                   accordingTo=row["work"] or "Chrystallum (ours)")
        rows.append(row)
    rows.sort(key=lambda r: (not r["outgoing"], r["relation"], r["other"], r["accordingTo"]))
    return rows


def detail(tx: Any, assertion_id: str) -> dict[str, Any] | None:
    record = tx.run(DETAIL, id=assertion_id).single()
    return record.data() if record else None


def parts(tx: Any, entity_id: str) -> list[dict[str, Any]]:
    return tx.run(PARTS, id=entity_id, live=LIVE, open=OPEN).data()


def decide(tx: Any, proposal_id: str, action: str, *, by: str, basis: str, reason: str | None = None,
           reject_claim: bool = False) -> tuple[dict[str, Any], dict[str, int]]:
    """One decision and the fact-layer rebuild, in the caller's transaction."""
    if not by.strip() or not basis.strip():
        raise ReviewError("a decision needs who decided and why")
    operations = load_operations()
    at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    if action == "accept":
        decided = accept(tx, proposal_id, decided_by=by, decision_basis=basis, decided_at=at,
                         registry=load_registry(), operations=operations)
    elif action == "reject":
        decided = reject(tx, proposal_id, decided_by=by, decision_basis=basis, decided_at=at,
                         reason=reason or "", operations=operations, reject_claim=reject_claim)
    else:
        raise ReviewError(f"unknown action {action!r}")
    return decided, rebuild(tx)


# --- rendering -------------------------------------------------------------------------------------------

def _evidence_lines(items: list[dict[str, Any]]) -> list[str]:
    lines = []
    for item in sorted(items, key=lambda i: i.get("locator") or ""):
        url = passage_url(item.get("href"))
        where = f"[{item['locator']}]({url})" if url and item.get("locator") else (item.get("locator") or item.get("system") or "?")
        quote = f"“{item['quotation']}”" if item.get("quotation") else "*(no quotation)*"
        lines.append(f"- **{where}**: {quote}")
        if item.get("passage"):
            passage = " ".join(item["passage"].split())
            lines.append(f"  <details><summary>passage</summary>\n\n  {passage[:1500]}{'…' if len(passage) > 1500 else ''}\n\n  </details>")
    return lines


def render_entity(info: dict[str, Any] | None, rows: list[dict[str, Any]]) -> str:
    if not info:
        return "*No entity selected.*"
    lines = [f"### {info['label']}", f"{info['kind']} · {info['status']} · `{info['id']}`"]
    if info.get("description"):
        lines.append(f"\n{info['description']}")
    for key, title in (("when", "When"), ("where", "Where"), ("partOf", "Part of")):
        if info.get(key):
            lines.append(f"- **{title}:** {info[key]}")
    open_count = sum(len(r["open"]) for r in rows)
    lines.append(f"\n{len(rows)} live claims · {open_count} open proposals")
    return "\n".join(lines)


def render_detail(info: dict[str, Any] | None) -> str:
    """Inference first (curator, 2026-11-13: review the reasoning, not the extraction): what the agent
    concluded and why; the quotations follow as context, already checked word for word by code."""
    if not info:
        return "*Pick a claim in the table.*"
    lines = [f"### {info['sentence']}",
             f"{info['status']} · {info.get('mode') or 'asserted'} · {info.get('category') or 'factual'}"]
    inferred = []
    if info.get("edtf") and info.get("timeText"):
        inferred.append(f"read the time “{info['timeText']}” as **{display_edtf(info['edtf'])}**")
    elif info.get("timeText"):
        inferred.append(f"kept the time as written: “{info['timeText']}” (not turned into a date)")
    if info.get("role"):
        inferred.append(f"took the role to be **{info['role']}**")
    if info.get("context"):
        inferred.append(f"set it during **{info['context']}**")
    open_proposals = [p for p in info["proposals"] if p["status"] in OPEN]
    lines += ["", "**What to check: the agent's reasoning**",
              "- the relation and the entities named in the heading"] + [f"- {item}" for item in inferred]
    for proposal in open_proposals:
        lines += ["", f"**Why** ({proposal.get('by') or 'unknown'})",
                  f"> {proposal.get('rationale') or '*(no rationale given)*'}",
                  "", "*From the text (checked word for word by code):*", *_evidence_lines(proposal["evidence"]),
                  f"<sub>`{proposal['id']}`</sub>"]
    if info["accepted"]:
        lines += ["", "**Accepted evidence**", *_evidence_lines(info["accepted"])]
    decided = [p for p in info["proposals"] if p["status"] not in OPEN]
    if decided:
        lines += ["", "**Earlier decisions**"]
        for proposal in decided:
            lines.append(f"- {proposal['status']} by {proposal.get('decidedBy') or '?'} {(proposal.get('decidedAt') or '')[:10]}"
                         + (f" ({proposal['reason']})" if proposal.get("reason") else "")
                         + (f": {proposal['basis']}" if proposal.get("basis") else ""))
    return "\n".join(lines)


def table(rows: list[dict[str, Any]]) -> list[list[Any]]:
    return [[i + 1, r["relation"], r["other"], r["status"], r["accordingTo"], r["time"] or "", len(r["open"]) or ""]
            for i, r in enumerate(rows)]


# --- the page -------------------------------------------------------------------------------------------

def build(driver: Any, database: str, start: str | None, by: str):
    def read(fn, *args):
        with driver.session(database=database) as session:
            return session.execute_read(fn, *args)

    def load(entity_id: str | None):
        if not entity_id:
            return None, [], "*No entity selected.*", [], gr.update(choices=[], value=None), "*Pick a claim in the table.*", None
        info = read(entity, entity_id)
        rows = read(claims, entity_id)
        part_rows = read(parts, entity_id)
        part_choices = [(f"{p['label']}  ·  {p['open']} open", p["id"]) for p in part_rows]
        return (entity_id, rows, render_entity(info, rows), table(rows),
                gr.update(choices=part_choices, value=None), "*Pick a claim in the table.*", None)

    def search(text: str):
        found = read(find, text)
        return gr.update(choices=[(f"{f['label']}  ·  {f['kind']}  ·  {f['claims']} claims", f["id"]) for f in found],
                         value=found[0]["id"] if found else None)

    def pick(rows: list[dict[str, Any]], evt: gr.SelectData):
        row = rows[evt.index[0]] if rows and evt.index is not None else None
        if not row:
            return None, "*Pick a claim in the table.*", gr.update(choices=[], value=None)
        info = read(detail, row["id"])
        open_ids = [p["id"] for p in info["proposals"] if p["status"] in OPEN]
        return row, render_detail(info), gr.update(choices=open_ids, value=open_ids[0] if open_ids else None)

    def goto(entity_id: str | None):
        # The Matches dropdown only accepts a value among its choices, so a jump replaces them with the target.
        if not entity_id:
            return gr.update()
        info = read(entity, entity_id)
        label = f"{info['label']}  ·  {info['kind']}" if info else entity_id
        return gr.update(choices=[(label, entity_id)], value=entity_id)

    def go_other(row: dict[str, Any] | None):
        return goto(row.get("otherId") if row else None)

    def next_open(current: str | None):
        if not current:
            return gr.update()
        pending = [p for p in read(parts, current) if p["open"]]
        return goto(pending[0]["id"]) if pending else gr.update()

    def run_decision(entity_id, row, proposal_id, action, reason, reject_claim, who, basis):
        if not proposal_id:
            return "**Pick an open proposal first.**", *load(entity_id)
        try:
            with driver.session(database=database) as session:
                decided, counts = session.execute_write(
                    lambda tx: decide(tx, proposal_id, action, by=who, basis=basis, reason=reason,
                                      reject_claim=reject_claim))
        except Exception as error:  # shown on the page; nothing was written
            return f"**Not recorded:** {error}", *load(entity_id)
        what = "accepted" if action == "accept" else "rejected" + (" with its claim" if reject_claim else "")
        return (f"**{what}** `{proposal_id}` · fact layer rebuilt ({counts['factEdges']} edges)", *load(entity_id))

    with gr.Blocks(title="Review Desk") as page:
        current = gr.State(None)
        rows_state = gr.State([])
        row_state = gr.State(None)
        gr.Markdown("## Review desk\nLocal Neo4j. Decisions run the same checks as the review CLI and rebuild the fact layer.")
        with gr.Row():
            query = gr.Textbox(label="Find an entity", placeholder="name or id", scale=3)
            results = gr.Dropdown(label="Matches", choices=[], scale=4)
        with gr.Row():
            with gr.Column(scale=5):
                summary = gr.Markdown()
                with gr.Row():
                    part_pick = gr.Dropdown(label="Parts (open proposals)", choices=[], scale=4)
                    next_btn = gr.Button("Next part with open proposals", scale=2)
                grid = gr.Dataframe(headers=HEADERS, interactive=False, wrap=True)
            with gr.Column(scale=4):
                claim = gr.Markdown("*Pick a claim in the table.*")
                other_btn = gr.Button("Go to the other end")
                proposal = gr.Dropdown(label="Open proposal to decide", choices=[])
                action = gr.Radio(["accept", "reject"], value="accept", label="Decision")
                reason = gr.Dropdown(list(REASON_CODES), value="unsupported", label="Reason (reject only)")
                reject_claim = gr.Checkbox(label="Also reject the claim itself (reject only)")
                who = gr.Textbox(value=by, label="Decided by")
                basis = gr.Textbox(label="Why", lines=2)
                decide_btn = gr.Button("Record decision", variant="primary")
                outcome = gr.Markdown()

        loaded = [current, rows_state, summary, grid, part_pick, claim, row_state]
        query.submit(search, query, results)
        results.change(load, results, loaded)
        part_pick.change(goto, part_pick, results)
        next_btn.click(next_open, current, results)
        grid.select(pick, rows_state, [row_state, claim, proposal])
        other_btn.click(go_other, row_state, results)
        decide_btn.click(run_decision, [current, row_state, proposal, action, reason, reject_claim, who, basis],
                         [outcome, *loaded])
        if start:
            page.load(lambda: goto(start), None, results)
    return page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--entity", help="open on this entity id")
    parser.add_argument("--by", default="", help="the name decisions are signed with")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args(argv)
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    try:
        build(driver, os.environ.get("NEO4J_DATABASE", "neo4j"), args.entity, args.by).launch(
            server_name="127.0.0.1", server_port=args.port, inbrowser=False)
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
