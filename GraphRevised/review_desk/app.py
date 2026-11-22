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

A second tab, **Footnote checks** (D-169, 2026-11-21), lists the rests-on checks
(`proposals/rests_on_check.py`): for each claim, the model's reading of every
passage its Wikipedia footnote was linked to, grouped as states it, in part, or
does not say it, with the words it relied on (verified verbatim by code). Accept
applies the verdicts to the links and rebuilds the fact layer; reject changes no
link. Both run `rests_on_check.decide`, as the command line does.

Reads NEO4J_PASSWORD (and optional NEO4J_URI, NEO4J_USERNAME, NEO4J_DATABASE).
"""

from __future__ import annotations

import argparse
import os
import re
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
from GraphRevised import localdb

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


CHECKS = """
MATCH (p:Proposal {operation: 'checkRestsOn'})-[:CHECKS_CLAIM]->(a:Assertion)
WHERE $status IS NULL OR p.status = $status
RETURN p.id AS id, p.status AS status, p.checkVerdict AS verdict, a.label AS claim,
       COUNT { (p)-[c:CHECKS_PASSAGE]->() WHERE c.verdict = 'states' } AS states,
       COUNT { (p)-[c:CHECKS_PASSAGE]->() WHERE c.verdict = 'partly' } AS partly,
       COUNT { (p)-[c:CHECKS_PASSAGE]->() WHERE c.verdict = 'absent' } AS absent
ORDER BY states = 0 DESC, claim
"""

CHECK = """
MATCH (p:Proposal {id: $id, operation: 'checkRestsOn'})-[:CHECKS_CLAIM]->(a:Assertion)
RETURN p.id AS id, p.status AS status, p.checkVerdict AS verdict, p.rationale AS rationale,
       p.modelId AS model, p.promptVersion AS promptVersion, p.createdAt AS createdAt,
       p.decidedBy AS decidedBy, p.decidedAt AS decidedAt, p.decisionBasis AS basis, p.decisionReason AS reason,
       a.id AS claimId, a.label AS claim, a.status AS claimStatus,
       COLLECT { MATCH (p)-[c:CHECKS_PASSAGE]->(o:SourceObservation)<-[l:RESTS_ON]-(a)
                 OPTIONAL MATCH (o)-[:IN_WORK]->(w:Entity)
                 RETURN {ref: coalesce(o.shortLabel, o.id), href: o.locator, work: w.label, passage: o.passageText,
                         verdict: c.verdict, words: c.words, reason: c.reason, verified: c.verified,
                         citation: l.citation, quotation: l.quotation, linkStatus: coalesce(l.status, 'accepted'),
                         support: l.support} } AS passages
"""

CHECK_HEADERS = ["#", "claim", "state it", "in part", "do not", "status"]
VERDICT_ORDER = {"states": 0, "partly": 1, "absent": 2}
VERDICT_WORDS = {"states": "States the claim", "partly": "States it in part", "absent": "Does not say it"}


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


def checks(tx: Any, status: str | None = "submitted") -> list[dict[str, Any]]:
    """The footnote checks (D-169), open ones by default: claims no cited passage states first."""
    return tx.run(CHECKS, status=status).data()


def check_detail(tx: Any, proposal_id: str) -> dict[str, Any] | None:
    record = tx.run(CHECK, id=proposal_id).single()
    if not record:
        return None
    info = record.data()
    from GraphRevised.proposals.rests_on_check import _order
    info["passages"].sort(key=lambda p: (VERDICT_ORDER.get(p["verdict"], 3), _order(p["ref"])))
    return info


def decide_check(tx: Any, proposal_id: str, action: str, *, by: str, basis: str,
                 reason: str | None = None) -> dict[str, Any]:
    """Accept (the verdicts apply to the links) or reject a footnote check; the fact layer is rebuilt."""
    from GraphRevised.proposals.rests_on_check import decide as decide_rests_on

    if not by.strip() or not basis.strip():
        raise ReviewError("a decision needs who decided and why")
    if action not in ("accept", "reject"):
        raise ReviewError(f"unknown action {action!r}")
    at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return decide_rests_on(tx, load_operations(), proposal_id, "accepted" if action == "accept" else "rejected",
                           decided_by=by, decision_basis=basis, decided_at=at,
                           reason=reason if action == "reject" else None)


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


def render_check(info: dict[str, Any] | None) -> str:
    """The model's reading first (what to check), then each passage by verdict with the words it relied
    on, then what accepting would change. Rejecting changes no link."""
    if not info:
        return "*Pick a check in the table.*"
    # The rationale is "<preamble> Taken together, <overall reason> <first passage line> | <next> | ...".
    summary = (info.get("rationale") or "").split(" | ")[0]
    summary = summary.split("Taken together, ", 1)[-1] if "Taken together, " in summary else summary
    cuts = [summary.find(f" {p['ref']}: ") for p in info["passages"]]
    summary = summary[:min(c for c in cuts if c >= 0)] if any(c >= 0 for c in cuts) else summary
    # The model saw the passages tagged P1..Pn in reference order (rests_on_check.check_request).
    from GraphRevised.proposals.rests_on_check import _order
    tags = {f"P{n}": ref for n, ref in enumerate(sorted((p["ref"] for p in info["passages"]), key=_order), 1)}
    summary = re.sub(r"\bP\d+\b", lambda m: tags.get(m.group(0), m.group(0)), summary)
    lines = [f"### {info['claim']}",
             f"check {info['status']} · claim {info['claimStatus']} · {info.get('verdict') or ''}",
             "", "**What to check: the model's reading of each cited passage**",
             f"> Taken together, {summary}" if summary else "> *(no overall reason given)*",
             f"<sub>{info.get('model') or '?'} · prompt {info.get('promptVersion') or '?'} · "
             f"{(info.get('createdAt') or '')[:10]}</sub>"]
    quotation = next((p["quotation"] for p in info["passages"] if p.get("quotation")), None)
    citation = next((p["citation"] for p in info["passages"] if p.get("citation")), None)
    if quotation or citation:
        lines += ["", f"*The modern words the claim was drawn from:* “{quotation or '?'}”"
                  + (f" · footnote cites **{citation}**" if citation else "")]
    for verdict in ("states", "partly", "absent"):
        group = [p for p in info["passages"] if p["verdict"] == verdict]
        if not group:
            continue
        lines += ["", f"**{VERDICT_WORDS[verdict]}** ({len(group)})"]
        for p in group:
            url = passage_url(p.get("href"))
            where = f"[{p['ref']}]({url})" if url else p["ref"]
            words = ""
            if p.get("words"):
                words = f": “{p['words']}”" + ("" if p.get("verified") else " **[words not found verbatim]**")
            state = "" if p["linkStatus"] == "accepted" and not p.get("support") else \
                f" *(link {p['linkStatus']}{', ' + p['support'] if p.get('support') else ''})*"
            lines.append(f"- **{where}**{words}{state} — {p.get('reason') or ''}")
            if p.get("passage"):
                passage = " ".join(p["passage"].split())
                lines.append(f"  <details><summary>passage</summary>\n\n  {passage[:1500]}"
                             f"{'…' if len(passage) > 1500 else ''}\n\n  </details>")
    if info["status"] == "submitted":
        absent = sum(p["verdict"] == "absent" for p in info["passages"])
        partly = sum(p["verdict"] == "partly" for p in info["passages"])
        lines += ["", "**If you accept:** "
                  + ", ".join(x for x in (f"{absent} link(s) rejected (kept as history)" if absent else "",
                                          f"{partly} marked partial" if partly else "") if x)
                  + ("" if absent or partly else "no link changes")
                  + "; the fact layer is rebuilt. **If you reject:** every link stays as it is."]
    else:
        lines += ["", f"**Decided:** {info['status']} by {info.get('decidedBy') or '?'} "
                  f"{(info.get('decidedAt') or '')[:10]}" + (f" ({info['reason']})" if info.get("reason") else "")
                  + (f": {info['basis']}" if info.get("basis") else "")]
    lines.append(f"<sub>`{info['id']}`</sub>")
    return "\n".join(lines)


def check_table(rows: list[dict[str, Any]]) -> list[list[Any]]:
    return [[i + 1, r["claim"], r["states"], r["partly"], r["absent"], r["status"]] for i, r in enumerate(rows)]


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

    def load_checks(status: str):
        rows = read(checks, None if status == "all" else status)
        return rows, check_table(rows), None, "*Pick a check in the table.*"

    def pick_check(rows: list[dict[str, Any]], evt: gr.SelectData):
        row = rows[evt.index[0]] if rows and evt.index is not None else None
        if not row:
            return None, "*Pick a check in the table.*"
        return row["id"], render_check(read(check_detail, row["id"]))

    def run_check_decision(proposal_id, action, reason, who, basis, status):
        if not proposal_id:
            return "**Pick a check first.**", *load_checks(status)
        try:
            with driver.session(database=database) as session:
                row = session.execute_write(
                    lambda tx: decide_check(tx, proposal_id, action, by=who, basis=basis, reason=reason))
        except Exception as error:  # shown on the page; nothing was written
            return f"**Not recorded:** {error}", *load_checks(status)
        rows, grid_rows, _, _ = load_checks(status)
        return (f"**{row['status']}** `{row['id']}` · {row['applied']} link(s) changed · fact layer rebuilt",
                rows, grid_rows, proposal_id, render_check(read(check_detail, proposal_id)))

    with gr.Blocks(title="Review Desk") as page:
        current = gr.State(None)
        rows_state = gr.State([])
        row_state = gr.State(None)
        gr.Markdown("## Review desk\nLocal Neo4j. Decisions run the same checks as the review CLI and rebuild the fact layer.")
        with gr.Tab("Claims"):
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

        with gr.Tab("Footnote checks"):
            gr.Markdown("A model read each claim beside every passage its Wikipedia footnote was linked to "
                        "(D-169). Accepting a check applies its verdicts to the links; rejecting it changes none.")
            check_rows = gr.State([])
            check_id = gr.State(None)
            with gr.Row():
                check_status = gr.Radio(["submitted", "accepted", "rejected", "all"], value="submitted",
                                        label="Show checks", scale=4)
                refresh = gr.Button("Refresh", scale=1)
            with gr.Row():
                with gr.Column(scale=5):
                    check_grid = gr.Dataframe(headers=CHECK_HEADERS, interactive=False, wrap=True)
                with gr.Column(scale=5):
                    check_view = gr.Markdown("*Pick a check in the table.*")
                    check_action = gr.Radio(["accept", "reject"], value="accept", label="Decision")
                    check_reason = gr.Dropdown(list(REASON_CODES), value="false", label="Reason (reject only)")
                    check_who = gr.Textbox(value=by, label="Decided by")
                    check_basis = gr.Textbox(label="Why", lines=2)
                    check_btn = gr.Button("Record decision", variant="primary")
                    check_outcome = gr.Markdown()

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

        listed = [check_rows, check_grid, check_id, check_view]
        check_status.change(load_checks, check_status, listed)
        refresh.click(load_checks, check_status, listed)
        check_grid.select(pick_check, check_rows, [check_id, check_view])
        check_btn.click(run_check_decision,
                        [check_id, check_action, check_reason, check_who, check_basis, check_status],
                        [check_outcome, *listed])
        page.load(load_checks, check_status, listed)
    return page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--entity", help="open on this entity id")
    parser.add_argument("--by", default="", help="the name decisions are signed with")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args(argv)
    driver = GraphDatabase.driver(localdb.uri(),
                                  auth=localdb.auth(),
                                  notifications_min_severity="OFF")
    try:
        build(driver, localdb.database(), args.entity, args.by).launch(
            server_name="127.0.0.1", server_port=args.port, inbrowser=False)
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
