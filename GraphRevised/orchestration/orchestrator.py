"""The guided orchestrator (31-ONE-COMMAND.md §3.7, §5 step 4): runs a plan's approved items, one at a
time, from the front door's run file, checkpointing every step there.

    python -m GraphRevised.orchestration.orchestrator show <run file>
    python -m GraphRevised.orchestration.orchestrator decide <run file> P03 approve|reject|defer|modify --by NAME [--note ...]
    python -m GraphRevised.orchestration.orchestrator approve-all <run file> --by NAME
    python -m GraphRevised.orchestration.orchestrator answer <run file> <interrupt id> --answer ... --by NAME
    python -m GraphRevised.orchestration.orchestrator retry <run file> P03 --by NAME   # after a failure
    python -m GraphRevised.orchestration.orchestrator budget <run file> 12.5 --by NAME [--note ...]
    python -m GraphRevised.orchestration.orchestrator extend <run file> <items.json> --by NAME [--after P09]
    python -m GraphRevised.orchestration.orchestrator run <run file> [--execute] [--budget-name NAME] [--items N]

The run file is the front door's (orchestration/front_door.py): an InquiryRunState, with each item's
worker call beside it in `<run>.calls.json`. A decision makes a new plan version; the version it
replaces is kept as `<run>.plan-v<N>.json`.

`run` is a dry run by default: it shows what would run, and the exact commands. With --execute, it
runs the next runnable item (the mode, the decision, and the dependencies decide; 31 §3.2), then the
next, until --items have run or it must stop. For each item it:

1. checks the item may run: the plan's remaining budget covers its estimate; a paid item has a named
   budget (--budget-name, in curation/budgets.json) whose cap covers it; its call does not read a
   draft inquiry the curator has not approved;
2. saves the assignment to the run file before the worker starts (a crash leaves it resumable);
3. runs the worker that already exists (`python -m <worker> <arguments>`, from the repo root) with
   CHRYSTALLUM_RUN set to `<run>:<item>`, so its model calls are found in the spend ledger by name,
   and its output goes to `runs/<run>.<item>.log`;
4. records the result: ok or failed by exit code, the cost from the ledger, the proposals stored
   while it ran.

The meter also caps each item (CHRYSTALLUM_RUN_CAP) at 1.5 times its estimate: a call that could pass
it is refused, and the worker fails. It stops (31 §3.12) on a failure or a cost over 1.5 times the estimate (each an interrupt for the
curator), on an open interrupt, on the plan's budget, or when nothing more can run, and says why.
Reconciliation, the critic, and the "no new independent evidence" measure (§3.5, §3.6, §3.8) are not
built: a result counts the proposals it stored, not what they add.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

from GraphRevised.orchestration.contracts import (
    InquiryPlan, InquiryRunState, Interrupt, PlanDecision, PlanItem, RunStatus, WorkerAssignment, WorkerResult,
)

GRAPH_REVISED = Path(__file__).resolve().parents[1]
REPO = GRAPH_REVISED.parent
COST_OVERRUN = 1.5  # a cost past this multiple of the item's estimate stops the run
DECISIONS = {"approve": "approved", "reject": "rejected", "defer": "deferred", "modify": "modified"}

Runner = Callable[[list[str], dict[str, str], Path], int]  # (command, environment, log) -> exit code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- The run file and its companions -------------------------------------------------------------

def calls_path(run_path: Path) -> Path:
    return run_path.with_name(run_path.name.removesuffix(".json") + ".calls.json")


def load(run_path: Path) -> tuple[InquiryRunState, dict[str, dict[str, Any]]]:
    state = InquiryRunState.load(run_path)
    calls = json.loads(calls_path(run_path).read_text(encoding="utf-8"))
    if calls["runId"] != state.run_id:
        raise ValueError(f"{calls_path(run_path).name} is for {calls['runId']}, not {state.run_id}")
    return state, calls["calls"]


def save(state: InquiryRunState, run_path: Path) -> None:
    tmp = run_path.with_name(run_path.name + ".tmp")
    state.save(tmp)
    os.replace(tmp, run_path)  # never a half-written run file


def save_calls(state: InquiryRunState, calls: dict[str, dict[str, Any]], run_path: Path) -> None:
    path = calls_path(run_path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps({"runId": state.run_id, "calls": calls}, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    os.replace(tmp, path)


def new_plan(state: InquiryRunState, plan: InquiryPlan, run_path: Path) -> InquiryRunState:
    """Keep the version replaced in its own file; the run file holds the new one."""
    old = state.plan
    kept = run_path.with_name(run_path.name.removesuffix(".json") + f".plan-v{old.version}.json")
    if not kept.exists():
        kept.write_text(old.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return state.model_copy(update={"plan": plan, "plan_versions": [*state.plan_versions, plan.version]})


# --- The curator's side --------------------------------------------------------------------------

def decide(state: InquiryRunState, run_path: Path, item_id: str, action: str, by: str, note: str | None = None) -> InquiryRunState:
    if state.plan is None:
        raise ValueError("the run has no plan to decide")
    if item_id in {a.item_id for a in state.assignments}:
        raise ValueError(f"{item_id} has already run: a decision now would rewrite history")
    decision = PlanDecision(status=DECISIONS[action], by=by, at=_now(), note=note)
    return new_plan(state, state.plan.decide(item_id, decision), run_path)


def approve_all(state: InquiryRunState, run_path: Path, by: str) -> InquiryRunState:
    if state.plan is None:
        raise ValueError("the run has no plan to approve")
    return new_plan(state, state.plan.approve_all(by), run_path)


def set_budget(state: InquiryRunState, run_path: Path, usd: float, by: str, note: str | None = None) -> InquiryRunState:
    """A new plan version with another budget; the curator's reason is kept with it. An open cost question
    about an item that now fits is answered by the change."""
    if state.plan is None:
        raise ValueError("the run has no plan")
    if usd < state.spent_usd:
        raise ValueError(f"${usd:.2f} is under what the run has spent (${state.spent_usd:.2f})")
    reason = f"budget ${state.plan.budget_usd:.2f} -> ${usd:.2f} by {by} at {_now()}" + (f": {note}" if note else "")
    plan = InquiryPlan.model_validate(state.plan.model_dump() | {
        "budget_usd": usd, "version": state.plan.version + 1, "previous_version": state.plan.version,
        "unresolved_questions": [*state.plan.unresolved_questions, reason]})
    state = new_plan(state, plan, run_path)
    for interrupt in state.open_interrupts():
        item = next((i for i in plan.items if i.item_id == interrupt.item_id), None)
        if interrupt.reason == "cost" and item and item.budget_usd <= state.remaining_budget() + 1e-9:
            state = answer(state, interrupt.interrupt_id, reason, by)
    return state


def answer(state: InquiryRunState, interrupt_id: str, text: str, by: str) -> InquiryRunState:
    found = [i for i in state.interrupts if i.interrupt_id == interrupt_id]
    if not found or not found[0].open:
        raise ValueError(f"no open interrupt {interrupt_id}")
    interrupts = [i.model_copy(update={"answer": text, "answered_by": by, "answered_at": _now()})
                  if i.interrupt_id == interrupt_id else i for i in state.interrupts]
    status = state.status
    if status is RunStatus.AWAITING_USER and not [i for i in interrupts if i.open]:
        status = RunStatus.PAUSED
    return state.model_copy(update={"interrupts": interrupts, "status": status})


def _next_ids(plan: InquiryPlan, n: int) -> list[str]:
    top = max((int(i.item_id[1:]) for i in plan.items), default=0)
    return [f"P{k:02d}" if k < 100 else f"P{k:03d}" for k in range(top + 1, top + 1 + n)]


def extend(state: InquiryRunState, calls: dict[str, dict[str, Any]], run_path: Path, items: list[dict[str, Any]],
           by: str, after: list[str] | None = None) -> tuple[InquiryRunState, dict[str, dict[str, Any]], list[str]]:
    """Add items to the plan as a new version, each awaiting the curator's decision (the "small builder"
    of 26a §5; a storyboard's approved segments and its source-task gaps come in this way).

    Each item is a PlanItem's fields without item_id or decision, plus `call` (its worker call, as in the
    calls file), optional `origin` (where it came from, kept on the call: e.g. {storyboard, segment, gap}),
    and optional `after_index` (earlier entries of this same list it depends on). `after` names plan items
    every new item depends on (e.g. the STORYBOARD item). An item whose action and target, or whose origin,
    the plan already holds is skipped and reported. Returns the state, the calls, and what was skipped."""
    if state.plan is None:
        raise ValueError("the run has no plan to extend")
    plan = state.plan
    after = list(after or [])
    unknown = [a for a in after if a not in {i.item_id for i in plan.items}]
    if unknown:
        raise ValueError(f"--after names {unknown}, which are not items of the plan")
    held = {(i.action, i.target) for i in plan.items}
    origins = [c.get("origin") for c in calls.values() if c.get("origin")]
    kept, skipped, index_to_id = [], [], {}
    for n, raw in enumerate(items):
        if raw.get("origin") and raw["origin"] in origins:
            skipped.append(f"entry {n}: its origin {raw['origin']} is already planned")
            continue
        if (raw["action"], raw["target"]) in held:
            skipped.append(f"entry {n}: {raw['action']} {raw['target']} is already planned")
            continue
        held.add((raw["action"], raw["target"]))
        kept.append((n, raw))
    ids = _next_ids(plan, len(kept))
    new_items, new_calls = [], {}
    for item_id, (n, raw) in zip(ids, kept):
        index_to_id[n] = item_id
        missing = [i for i in raw.get("after_index", []) if i not in index_to_id]
        if missing:
            raise ValueError(f"entry {n} depends on entries {missing}, which are not earlier kept entries")
        fields = {k: v for k, v in raw.items() if k not in ("call", "origin", "after_index")}
        new_items.append(PlanItem.model_validate(fields | {
            "item_id": item_id, "depends_on": [*after, *fields.get("depends_on", []),
                                               *(index_to_id[i] for i in raw.get("after_index", []))]}))
        if "call" not in raw:
            raise ValueError(f"entry {n} has no call: say which worker runs it, or 'manual' with instructions")
        new_calls[item_id] = dict(raw["call"]) | ({"origin": raw["origin"]} if raw.get("origin") else {})
    if not new_items:
        return state, calls, skipped
    total = sum(i.budget_usd for i in plan.items) + sum(i.budget_usd for i in new_items)
    if total > plan.budget_usd + 1e-9:
        raise ValueError(f"the items would need ${total:.2f}, over the plan's ${plan.budget_usd:.2f}: "
                         "raise the plan's budget first (the budget subcommand), or add fewer items")
    note = f"extended by {by} at {_now()}: {', '.join(ids)} added"
    new = InquiryPlan.model_validate(plan.model_dump() | {
        "items": [*(i.model_dump() for i in plan.items), *(i.model_dump() for i in new_items)],
        "version": plan.version + 1, "previous_version": plan.version,
        "unresolved_questions": [*plan.unresolved_questions, note]})
    state = new_plan(state, new, run_path)
    if state.status in (RunStatus.DONE, RunStatus.STOPPED):
        state = state.model_copy(update={"status": RunStatus.AWAITING_USER, "stopping_explanation": None})
    return state, calls | new_calls, skipped


# --- Running -------------------------------------------------------------------------------------

def run_cost(run_label: str, ledger: Path) -> float:
    """What the ledger records for one item's run name."""
    from GraphRevised.spend_meter import read_ledger

    return float(sum((Decimal(e["costUSD"]) for e in read_ledger(ledger) if e.get("run") == run_label), Decimal(0)))


def budget_left(name: str, budgets: Path, ledger: Path) -> float:
    from GraphRevised.spend_meter import load_budgets, spent

    known = load_budgets(budgets)
    if name not in known:
        raise ValueError(f"no budget named {name} in {budgets.name}")
    return float(Decimal(known[name]["capUSD"]) - spent(name, ledger))


def blocked(state: InquiryRunState, item: PlanItem, call: dict[str, Any] | None, budget_name: str | None,
            budgets: Path, ledger: Path) -> tuple[str, str] | None:
    """Why this item may not run now, as (interrupt reason, question); None when it may."""
    if call is None:
        return "plan", f"{item.item_id} has no worker call in the calls file"
    if item.budget_usd > state.remaining_budget() + 1e-9:
        return "cost", (f"{item.item_id} needs about ${item.budget_usd:.2f}; the plan has "
                        f"${state.remaining_budget():.2f} left. Raise the plan's budget, or reject the item?")
    drafts = [a for a in call.get("arguments", []) if "/plans/inquiry-draft-" in a or a.startswith("plans/inquiry-draft-")]
    if drafts:
        return "plan", (f"{item.item_id} reads a draft inquiry ({drafts[0]}): approve it into inquiries/, "
                        "then run the front door again")
    if item.budget_usd > 0:
        if not budget_name:
            return "cost", f"{item.item_id} calls a model (about ${item.budget_usd:.2f}): name a budget with --budget-name"
        left = budget_left(budget_name, budgets, ledger)
        if item.budget_usd > left + 1e-9:
            return "cost", f"budget {budget_name} has ${left:.2f} left, under {item.item_id}'s ${item.budget_usd:.2f}"
    return None


def subprocess_runner(command: list[str], environment: dict[str, str], log: Path) -> int:
    with log.open("w", encoding="utf-8") as out:
        return subprocess.run(command, cwd=REPO, env=environment, stdout=out, stderr=subprocess.STDOUT).returncode


PROPOSAL_IDS = "MATCH (p:Proposal) RETURN p.id AS id"  # compared before and after: workers do not all time-stamp


def _interrupt(state: InquiryRunState, reason: str, question: str, item_id: str | None) -> InquiryRunState:
    interrupt = Interrupt(interrupt_id=f"{state.run_id}:{len(state.interrupts) + 1}", reason=reason,
                          question=question, item_id=item_id)
    return state.model_copy(update={"interrupts": [*state.interrupts, interrupt], "status": RunStatus.AWAITING_USER})


def _finish_if_done(state: InquiryRunState) -> InquiryRunState:
    attempted = {a.item_id for a in state.assignments if a.assignment_id not in state.set_aside}
    waiting = [i for i in state.plan.items if i.item_id not in attempted and i.decision.status not in ("rejected", "deferred")]
    if waiting:
        return state.model_copy(update={"status": RunStatus.PAUSED})
    return state.model_copy(update={"status": RunStatus.DONE, "stopping_explanation": (
        "every approved item has run; rejected and deferred items were left (reconciliation, the critic and the "
        "new-evidence measure are not built, so the curator judges whether to plan more)")})


def step(state: InquiryRunState, calls: dict[str, dict[str, Any]], run_path: Path, *, budget_name: str | None,
         runner: Runner = subprocess_runner, proposal_ids: Callable[[], set[str]] | None = None,
         budgets: Path | None = None, ledger: Path | None = None) -> tuple[InquiryRunState, str]:
    """Run the next runnable item, or say why not. Saves the run file before and after the worker."""
    from GraphRevised.spend_meter import BUDGETS, ENV, LEDGER, RUN_CAP_ENV, RUN_ENV

    budgets, ledger = budgets or BUDGETS, ledger or LEDGER
    if state.plan is None:
        return state, "the run has no plan"
    answered = {r.assignment_id for r in state.results}
    orphans = [a for a in state.assignments if a.assignment_id not in answered]
    manual = [a for a in orphans if a.worker == "manual"]
    for a in manual:  # a step done by hand: done once the curator answers its question
        asked = [i for i in state.interrupts if i.item_id == a.item_id and i.reason == "rights"]
        if asked and not asked[-1].open:
            result = WorkerResult(assignment_id=a.assignment_id, status="ok",
                                  outputs=[f"done by hand ({asked[-1].answered_by}): {asked[-1].answer}"])
            state = state.model_copy(update={"results": [*state.results, result], "status": RunStatus.PAUSED})
            save(state, run_path)
            return state, f"{a.item_id} done by hand: {asked[-1].answer}"
    orphans = [a for a in orphans if a.worker != "manual"]
    if orphans:  # the run stopped while a worker ran: record it as failed, and ask
        a = orphans[0]
        result = WorkerResult(assignment_id=a.assignment_id, status="failed",
                              error="no result: the run stopped while the worker ran; check the log and the graph")
        state = state.model_copy(update={"results": [*state.results, result], "status": RunStatus.PAUSED})
        state = _interrupt(state, "deviation", f"{a.item_id} has no result (the run stopped while it ran): retry it, "
                           "or reject it?", a.item_id)
        save(state, run_path)
        return state, f"{a.item_id} had no result; recorded as failed and asked about"
    if state.open_interrupts():
        return state, "waiting for the curator: " + "; ".join(i.question for i in state.open_interrupts())
    item = state.next_item()
    if item is None:
        state = _finish_if_done(state)
        save(state, run_path)
        return state, ("done: " + state.stopping_explanation if state.status is RunStatus.DONE
                       else "nothing can run now: the remaining items await a decision or their dependencies")
    call = calls.get(item.item_id)
    why = blocked(state, item, call, budget_name, budgets, ledger)
    if why:
        state = _interrupt(state, why[0], why[1], item.item_id)
        save(state, run_path)
        return state, f"stopped before {item.item_id}: {why[1]}"

    attempt = 1 + sum(a.item_id == item.item_id for a in state.assignments)
    label = f"{state.run_id}:{item.item_id}"
    if call["worker"] == "manual":  # the curator does it; the run waits for the answer
        assignment = WorkerAssignment(assignment_id=f"{label}:{attempt}", item_id=item.item_id, worker="manual",
                                      idempotency_key=hashlib.sha256(label.encode()).hexdigest()[:16])
        state = state.model_copy(update={"assignments": [*state.assignments, assignment]})
        state = _interrupt(state, "rights", call["instructions"], item.item_id)
        save(state, run_path)
        return state, f"{item.item_id} is done by hand: {call['instructions']}"
    command = [sys.executable, "-m", call["worker"], *call["arguments"]]
    key = hashlib.sha256(json.dumps([state.run_id, item.item_id, command[1:]]).encode()).hexdigest()[:16]
    assignment = WorkerAssignment(assignment_id=f"{label}:{attempt}", item_id=item.item_id, worker=call["worker"],
                                  arguments=call["arguments"], lens=item.lens, idempotency_key=key)
    state = state.model_copy(update={"assignments": [*state.assignments, assignment], "status": RunStatus.RUNNING})
    save(state, run_path)  # the checkpoint: the item is recorded as started before anything happens

    environment = os.environ | {RUN_ENV: label}
    if budget_name and item.budget_usd > 0:
        environment[ENV] = budget_name
        # the item's cap, in the meter: a call that could pass it is refused (counting earlier attempts)
        environment[RUN_CAP_ENV] = f"{item.budget_usd * COST_OVERRUN + run_cost(label, ledger):.2f}"
    else:
        environment.pop(ENV, None)  # a free item gets no budget, so a model call in it is refused
        environment.pop(RUN_CAP_ENV, None)
    log = run_path.with_name(f"{state.run_id}.{item.item_id}.log")
    before = proposal_ids() if proposal_ids else set()
    earlier = run_cost(label, ledger)  # what earlier attempts of this item spent
    code = runner(command, environment, log)
    cost = run_cost(label, ledger) - earlier
    stored = sorted(proposal_ids() - before) if proposal_ids else []
    result = WorkerResult(assignment_id=assignment.assignment_id, status="ok" if code == 0 else "failed",
                          outputs=[log.relative_to(GRAPH_REVISED).as_posix() if log.is_relative_to(GRAPH_REVISED) else str(log)],
                          proposal_ids=stored, cost_usd=round(cost, 6),
                          error=None if code == 0 else f"exit code {code}; see the log")
    state = state.model_copy(update={"results": [*state.results, result], "spent_usd": round(state.spent_usd + cost, 6),
                                     "status": RunStatus.PAUSED})
    message = f"{item.item_id} {result.status}: ${cost:.2f}, {len(stored)} proposals stored"
    if code != 0:
        state = _interrupt(state, "deviation", f"{item.item_id} failed ({result.error}): retry, modify, or reject it?",
                           item.item_id)
    elif item.budget_usd > 0 and cost > item.budget_usd * COST_OVERRUN:
        state = _interrupt(state, "cost", f"{item.item_id} cost ${cost:.2f}, over {COST_OVERRUN}x its estimate of "
                           f"${item.budget_usd:.2f}: go on?", item.item_id)
    elif state.remaining_budget() <= 0:
        state = _finish_if_done(state)
        if state.status is not RunStatus.DONE:  # items remain, and nothing is left to run them with
            state = state.model_copy(update={"status": RunStatus.STOPPED, "stopping_explanation": "the plan's budget is spent"})
    save(state, run_path)
    return state, message


def retry(state: InquiryRunState, run_path: Path, item_id: str, by: str) -> InquiryRunState:
    """Let a failed item run again: its failed attempt stays in the record, set aside, and the curator's
    answer closes the item's interrupt."""
    failed = {r.assignment_id for r in state.results if r.status != "ok"}
    mine = [a for a in state.assignments if a.item_id == item_id]
    if not mine or mine[-1].assignment_id not in failed:
        raise ValueError(f"{item_id} has no failed attempt to retry")
    state = InquiryRunState.model_validate(state.model_dump() | {"set_aside": [*state.set_aside, mine[-1].assignment_id]})
    for interrupt in state.open_interrupts():
        if interrupt.item_id == item_id:
            state = answer(state, interrupt.interrupt_id, "retry", by)
    return state


class Locked(RuntimeError):
    pass


def lock(run_path: Path) -> Path:
    path = run_path.with_name(run_path.name + ".lock")
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise Locked(f"{path.name} exists: another orchestrator is running this plan (delete it if none is)")
    os.write(fd, _now().encode())
    os.close(fd)
    return path


# --- Showing it ----------------------------------------------------------------------------------

def text(state: InquiryRunState, calls: dict[str, dict[str, Any]]) -> str:
    lines = [f"Run {state.run_id}: {state.status.value}, {state.mode.value}; command {state.command}"]
    if state.plan is None:
        lines.append("No plan yet.")
    else:
        plan = state.plan
        lines.append(f"Plan v{plan.version} for {plan.inquiry_id}; spent ${state.spent_usd:.2f} of ${plan.budget_usd:.2f}")
        results = {r.assignment_id: r for r in state.results}
        for item in plan.items:
            runs = [a for a in state.assignments if a.item_id == item.item_id]
            done = results.get(runs[-1].assignment_id) if runs else None
            ran = (f"ran: {done.status}, ${done.cost_usd:.2f}, {len(done.proposal_ids)} proposals" if done
                   else "started, no result" if runs else "not run")
            decision = item.decision.status + (f" by {item.decision.by}" if item.decision.by else "")
            lines.append(f"  {item.item_id} {item.action}{' ' + item.lens if item.lens else ''} — {item.target}"
                         f"  ${item.budget_usd:.2f}  [{decision}; {ran}]")
        nxt = state.next_item()
        if nxt:
            call = calls.get(nxt.item_id, {})
            if call.get("worker") == "manual":
                lines.append(f"Next: {nxt.item_id}, by hand: {call.get('instructions')}")
            else:
                lines.append(f"Next: {nxt.item_id}: python -m {call.get('worker')} {' '.join(call.get('arguments', []))}")
    for i in state.open_interrupts():
        lines.append(f"Open question {i.interrupt_id} ({i.reason}): {i.question}")
    if state.stopping_explanation:
        lines.append(f"Stopped: {state.stopping_explanation}")
    return "\n".join(lines)


def _graph_proposals() -> tuple[Callable[[str], list[str]], Callable[[], None]]:
    from neo4j import GraphDatabase
    from GraphRevised import localdb

    driver = GraphDatabase.driver(localdb.uri(), auth=localdb.auth(), notifications_min_severity="OFF")

    def ids() -> set[str]:
        with driver.session(database=localdb.database()) as session:
            return {r["id"] for r in session.run(PROPOSAL_IDS)}
    return ids, driver.close


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("show", "decide", "approve-all", "answer", "retry", "budget", "extend", "run"):
        p = sub.add_parser(name)
        p.add_argument("run_file", type=Path)
        if name == "decide":
            p.add_argument("item")
            p.add_argument("decision", choices=list(DECISIONS))
            p.add_argument("--note")
        if name == "answer":
            p.add_argument("interrupt")
            p.add_argument("--answer", required=True)
        if name == "retry":
            p.add_argument("item")
        if name == "budget":
            p.add_argument("usd", type=float)
            p.add_argument("--note")
        if name == "extend":
            p.add_argument("items_file", type=Path, help="a JSON list of items to add (see extend())")
            p.add_argument("--after", action="append", default=[], help="a plan item every new item depends on")
        if name in ("decide", "approve-all", "answer", "retry", "budget", "extend"):
            p.add_argument("--by", required=True)
        if name == "run":
            p.add_argument("--execute", action="store_true", help="run the items (default: show what would run)")
            p.add_argument("--budget-name", help="the budget in curation/budgets.json that paid items spend")
            p.add_argument("--items", type=int, default=1, help="how many items to run at most (default 1)")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    run_path = args.run_file.resolve()
    state, calls = load(run_path)

    if args.action == "show":
        print(text(state, calls))
        return 0
    if args.action != "run" or args.execute:
        held = lock(run_path)
    else:
        held = None
    try:
        if args.action == "decide":
            state = decide(state, run_path, args.item, args.decision, args.by, args.note)
        elif args.action == "approve-all":
            state = approve_all(state, run_path, args.by)
        elif args.action == "answer":
            state = answer(state, args.interrupt, args.answer, args.by)
        elif args.action == "retry":
            state = retry(state, run_path, args.item, args.by)
        elif args.action == "budget":
            state = set_budget(state, run_path, args.usd, args.by, args.note)
        elif args.action == "extend":
            items = json.loads(args.items_file.read_text(encoding="utf-8"))
            state, calls, skipped = extend(state, calls, run_path, items, args.by, args.after)
            for line in skipped:
                print(f"skipped {line}")
            save_calls(state, calls, run_path)
        elif not args.execute:
            print(text(state, calls))
            print("\nDry run: nothing was run. Add --execute to run the next item"
                  + (f" (and up to {args.items})" if args.items > 1 else "") + ".")
            return 0
        else:
            ids, close = _graph_proposals()
            try:
                for _ in range(args.items):
                    state, message = step(state, calls, run_path, budget_name=args.budget_name, proposal_ids=ids)
                    print(message)
                    if state.status is not RunStatus.PAUSED:
                        break
            finally:
                close()
            return 0
        save(state, run_path)
        print(text(state, calls))
        return 0
    finally:
        if held:
            held.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
