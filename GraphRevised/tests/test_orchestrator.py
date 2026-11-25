"""The guided orchestrator (31 §5 step 4): decisions, checkpoints, costs, stops. A fake worker runs,
never a real one, and no model is called; the budgets and the ledger are temporary files."""

import json
import tempfile
import unittest
from pathlib import Path

from GraphRevised.orchestration.contracts import (
    CoverageMap, IdentityCandidate, InquiryPlan, InquiryRunState, PlanItem, ResolvedFocus, RunMode, RunStatus,
    ScopeDecision,
)
from GraphRevised.orchestration.orchestrator import (Locked, answer, approve_all, decide, load, lock, retry, set_budget,
                                                     step)

RUN = "front-door-test-20260101T000000Z"
FOCUS = ResolvedFocus(status="resolved", decided_by="test",
                      chosen=IdentityCandidate(label="Battle of Test", kind="Event", local_entity_id="chr:entity:t", why="test"))


def item(item_id, budget=0.0, depends_on=()):
    return PlanItem(item_id=item_id, action="READ", target="chr:entity:w", rationale="a test reading item",
                    expected_outputs=["proposals"], budget_usd=budget, depends_on=list(depends_on))


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        root = Path(self.dir.name)
        self.run_path = root / f"{RUN}.json"
        self.budgets, self.ledger = root / "budgets.json", root / "ledger.jsonl"
        self.budgets.write_text(json.dumps({"budgets": {"test": {"capUSD": "5"}}}))
        self.ledger.write_text("")
        plan = InquiryPlan(plan_id=RUN, inquiry_id="chr:inquiry:t", version=1, command="graph Battle of Test",
                           mode=RunMode.GUIDED, scope=ScopeDecision(decision="IN_SCOPE", primary_intent="HISTORICAL",
                                                                    explanation="a test battle"),
                           focus=FOCUS, coverage=CoverageMap(), recipe="Event", stopping_rules=["budget"], budget_usd=3,
                           items=[item("P01"), item("P02", budget=1.0, depends_on=["P01"]), item("P03", budget=1.0)])
        InquiryRunState(run_id=RUN, command=plan.command, inquiry_id=plan.inquiry_id, mode=RunMode.GUIDED, owner="test",
                        status=RunStatus.AWAITING_USER, plan=plan, plan_versions=[1]).save(self.run_path)
        calls = {"P01": {"worker": "fake.free", "arguments": ["a"]},
                 "P02": {"worker": "fake.paid", "arguments": ["GraphRevised/inquiries/t.json"]},
                 "P03": {"worker": "fake.draft", "arguments": ["GraphRevised/plans/inquiry-draft-t.json"]}}
        self.run_path.with_name(f"{RUN}.calls.json").write_text(json.dumps({"runId": RUN, "calls": calls}))
        self.ran = []
        self.caps = []
        self.proposals = {"chr:proposal:old"}
        self.code = 0
        self.cost = "0"

    def ids(self):
        return set(self.proposals)

    def runner(self, command, environment, log):
        self.proposals.add(f"chr:proposal:{environment['CHRYSTALLUM_RUN'][-3:]}")
        self.ran.append((command[2], environment.get("CHRYSTALLUM_RUN"), environment.get("CHRYSTALLUM_BUDGET")))
        self.caps.append(environment.get("CHRYSTALLUM_RUN_CAP"))
        log.write_text("fake worker output\n")
        if self.cost != "0":
            with self.ledger.open("a") as out:
                out.write(json.dumps({"budget": "test", "run": environment["CHRYSTALLUM_RUN"], "costUSD": self.cost}) + "\n")
        return self.code

    def step(self, state, calls, budget_name="test"):
        return step(state, calls, self.run_path, budget_name=budget_name, runner=self.runner,
                    proposal_ids=self.ids, budgets=self.budgets, ledger=self.ledger)

    def test_guided_runs_nothing_until_the_curator_decides(self):
        state, calls = load(self.run_path)
        state, message = self.step(state, calls)
        self.assertEqual(self.ran, [])
        self.assertIn("await a decision", message)

    def test_a_decision_makes_a_new_plan_version_and_keeps_the_old(self):
        state, _ = load(self.run_path)
        state = decide(state, self.run_path, "P03", "reject", by="curator", note="not yet")
        self.assertEqual((state.plan.version, state.plan_versions), (2, [1, 2]))
        self.assertTrue(self.run_path.with_name(f"{RUN}.plan-v1.json").exists())
        state = approve_all(state, self.run_path, by="curator")
        self.assertEqual([i.decision.status for i in state.plan.items], ["approved", "approved", "rejected"])

    def test_approved_items_run_in_order_with_their_names_and_costs(self):
        state, calls = load(self.run_path)
        state = decide(state, self.run_path, "P03", "reject", by="curator", note="draft")
        state = approve_all(state, self.run_path, by="curator")
        state, message = self.step(state, calls)
        self.assertEqual(self.ran, [("fake.free", f"{RUN}:P01", None)])  # a free item gets no budget
        self.assertIn("P01 ok", message)
        self.assertEqual(InquiryRunState.load(self.run_path).results[0].proposal_ids, ["chr:proposal:P01"])
        self.cost = "0.80"
        state, message = self.step(state, calls)
        self.assertEqual(self.ran[-1], ("fake.paid", f"{RUN}:P02", "test"))
        self.assertEqual(self.caps, [None, "1.50"])  # the meter caps the paid item at 1.5x its estimate
        self.assertEqual(state.spent_usd, 0.8)
        state, message = self.step(state, calls)
        self.assertEqual(state.status, RunStatus.DONE)
        self.assertTrue(state.stopping_explanation)

    def test_a_paid_item_needs_a_named_budget_with_room(self):
        state, calls = load(self.run_path)
        state = approve_all(state, self.run_path, by="curator")
        state, _ = self.step(state, calls, budget_name=None)  # P01 is free
        state, message = self.step(state, calls, budget_name=None)
        self.assertIn("name a budget", message)
        self.assertEqual(state.status, RunStatus.AWAITING_USER)
        self.assertEqual(len(self.ran), 1)

    def test_a_draft_inquiry_is_not_run(self):
        state, calls = load(self.run_path)
        state = decide(state, self.run_path, "P01", "defer", by="curator")
        state = decide(state, self.run_path, "P03", "approve", by="curator")
        state, message = self.step(state, calls)
        self.assertIn("draft inquiry", message)
        self.assertEqual(self.ran, [])

    def test_a_failure_stops_the_run_and_can_be_retried(self):
        state, calls = load(self.run_path)
        state = approve_all(state, self.run_path, by="curator")
        self.code = 2
        state, message = self.step(state, calls)
        self.assertIn("failed", message)
        self.assertEqual(state.open_interrupts()[0].reason, "deviation")
        state, message = self.step(state, calls)
        self.assertIn("waiting for the curator", message)
        state = retry(state, self.run_path, "P01", by="curator")
        self.code = 0
        state, message = self.step(state, calls)
        self.assertIn("P01 ok", message)
        self.assertEqual([r.status for r in state.results], ["failed", "ok"])

    def test_a_retry_counts_only_its_own_spend(self):
        state, calls = load(self.run_path)
        state = approve_all(state, self.run_path, by="curator")
        state, _ = self.step(state, calls)
        self.code, self.cost = 1, "0.90"
        state, _ = self.step(state, calls)  # P02 fails after spending $0.90
        state = retry(state, self.run_path, "P02", by="curator")
        self.code, self.cost = 0, "0.10"
        state, _ = self.step(state, calls)
        self.assertEqual([r.cost_usd for r in state.results], [0, 0.9, 0.1])
        self.assertAlmostEqual(state.spent_usd, 1.0)

    def test_a_cost_over_the_estimate_asks_before_going_on(self):
        state, calls = load(self.run_path)
        state = approve_all(state, self.run_path, by="curator")
        state, _ = self.step(state, calls)
        self.cost = "1.60"
        state, _ = self.step(state, calls)
        self.assertEqual(state.open_interrupts()[0].reason, "cost")
        state = answer(state, state.open_interrupts()[0].interrupt_id, "go on", by="curator")
        self.assertEqual(state.status, RunStatus.PAUSED)

    def test_a_crash_mid_item_is_recorded_on_resume(self):
        state, calls = load(self.run_path)
        state = approve_all(state, self.run_path, by="curator")

        def crash(command, environment, log):
            raise KeyboardInterrupt

        with self.assertRaises(KeyboardInterrupt):
            step(state, calls, self.run_path, budget_name="test", runner=crash, budgets=self.budgets, ledger=self.ledger)
        state, calls = load(self.run_path)
        self.assertEqual(state.status, RunStatus.RUNNING)  # the checkpoint was saved before the worker
        state, message = self.step(state, calls)
        self.assertIn("no result", message)
        self.assertEqual(state.results[0].status, "failed")

    def test_raising_the_budget_answers_the_cost_question_it_settles(self):
        state, calls = load(self.run_path)
        state = decide(state, self.run_path, "P03", "reject", by="curator", note="draft")
        state = approve_all(state, self.run_path, by="curator")
        state, _ = self.step(state, calls)
        self.cost = "2.50"  # P02 overruns its $1 estimate but stays under its cap
        state, _ = self.step(state, calls)
        state = answer(state, state.open_interrupts()[0].interrupt_id, "go on", by="curator")
        state = InquiryRunState.model_validate(state.model_dump() | {"spent_usd": 2.6})
        with self.assertRaises(ValueError):
            set_budget(state, self.run_path, 2.0, by="curator")  # under what is spent
        state = set_budget(state, self.run_path, 5, by="curator", note="measured rate")
        self.assertEqual((state.plan.budget_usd, state.plan.version), (5, 4))
        self.assertIn("budget $3.00 -> $5.00 by curator", state.plan.unresolved_questions[-1])

    def test_a_step_done_by_hand_waits_for_the_curators_answer(self):
        state, calls = load(self.run_path)
        calls["P01"] = {"worker": "manual", "instructions": "Read the rights at the source and answer with the class"}
        state = decide(state, self.run_path, "P01", "approve", by="curator")
        state, message = self.step(state, calls)
        self.assertIn("done by hand", message)
        self.assertEqual(self.ran, [])  # nothing is run for a manual step
        self.assertEqual(state.open_interrupts()[0].reason, "rights")
        state, message = self.step(state, calls)
        self.assertIn("waiting for the curator", message)
        state = answer(state, state.open_interrupts()[0].interrupt_id, "A: CC BY 4.0, read 2026-11-24", by="curator")
        state, message = self.step(state, calls)
        self.assertEqual(state.results[-1].status, "ok")
        self.assertIn("CC BY 4.0", state.results[-1].outputs[0])

    def test_one_orchestrator_at_a_time(self):
        held = lock(self.run_path)
        with self.assertRaises(Locked):
            lock(self.run_path)
        held.unlink()


if __name__ == "__main__":
    unittest.main()


class ExtendTests(unittest.TestCase):
    """The small builder (26a §5): items added as a new plan version, awaiting decisions."""

    setUp = OrchestratorTests.setUp

    def test_extend_adds_awaiting_items_with_calls_and_origin(self):
        from GraphRevised.orchestration.orchestrator import extend, save_calls
        state, calls = load(self.run_path)
        items = [
            {"action": "REGISTER", "target": "nomisma", "rationale": "coins commemorating Actium need Nomisma",
             "expected_outputs": ["its rights quoted"], "budget_usd": 0,
             "call": {"worker": "manual", "instructions": "read the rights"},
             "origin": {"storyboard": "chr:storyboard:t", "segment": 3, "gap": 0}},
            {"action": "FIND", "target": "chr:entity:w2", "rationale": "find the passages for segment 3",
             "expected_outputs": ["found passages"], "budget_usd": 0, "call": {"worker": "fake.free", "arguments": []}},
            {"action": "READ", "target": "chr:entity:w2", "rationale": "read the passages for segment 3",
             "expected_outputs": ["proposals"], "budget_usd": 0, "after_index": [1],
             "call": {"worker": "fake.free", "arguments": []}},
            {"action": "READ", "target": "chr:entity:w", "rationale": "already planned, so skipped",
             "expected_outputs": ["proposals"], "budget_usd": 0, "call": {"worker": "fake.free", "arguments": []}},
        ]
        state, calls, skipped = extend(state, calls, self.run_path, items, "curator", after=["P01"])
        save_calls(state, calls, self.run_path)
        state.save(self.run_path)
        self.assertEqual([i.item_id for i in state.plan.items], ["P01", "P02", "P03", "P04", "P05", "P06"])
        self.assertEqual(len(skipped), 1)
        self.assertEqual(state.plan.item("P06").depends_on, ["P01", "P05"])
        self.assertTrue(all(state.plan.item(i).decision.status == "awaiting" for i in ("P04", "P05", "P06")))
        self.assertEqual(state.plan.version, 2)
        self.assertTrue(self.run_path.with_name(f"{RUN}.plan-v1.json").exists())
        state, calls = load(self.run_path)
        self.assertEqual(calls["P04"]["origin"]["segment"], 3)
        again, _, skipped = extend(state, calls, self.run_path, items[:1], "curator")
        self.assertEqual(again.plan.version, 2)  # the same origin twice adds nothing
        self.assertEqual(len(skipped), 1)

    def test_extend_refuses_past_the_budget(self):
        from GraphRevised.orchestration.orchestrator import extend
        state, calls = load(self.run_path)
        item = {"action": "READ", "target": "chr:entity:w3", "rationale": "a costly reading item",
                "expected_outputs": ["proposals"], "budget_usd": 2.0, "call": {"worker": "fake.paid", "arguments": []}}
        with self.assertRaises(ValueError):
            extend(state, calls, self.run_path, [item], "curator")
