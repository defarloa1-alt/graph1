"""The one-command contracts (31 §3): plans, decisions by mode, run state, reconciler and critic outputs."""

import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from GraphRevised.orchestration.contracts import (
    AuthorityMatch, CoverageMap, CriticVerdict, IdentityCandidate, InquiryPlan, InquiryRunState, Interrupt,
    OrientationBrief, PlanDecision, PlanItem, ReconciliationDecision, ResolvedFocus, RunMode, RunStatus,
    ScopeDecision, SubjectAnchor, WorkerAssignment, WorkerResult,
)

NOW = "2026-01-01T00:00:00+00:00"
FOCUS = ResolvedFocus(status="resolved", decided_by="front-door",
                      chosen=IdentityCandidate(label="Battle of Test", kind="Event", qid="Q1", why="the only match"))
SCOPE = ScopeDecision(decision="IN_SCOPE", primary_intent="HISTORICAL_GRAPH_CONSTRUCTION", explanation="a historical battle")


def item(item_id, depends_on=(), status="awaiting", budget=1.0):
    decision = PlanDecision(status=status, by="curator", at=NOW) if status != "awaiting" else PlanDecision()
    return PlanItem(item_id=item_id, action="READ", target="a work", rationale="read the main narrative",
                    expected_outputs=["proposals"], budget_usd=budget, depends_on=list(depends_on), decision=decision)


def plan(mode=RunMode.GUIDED, items=None, scope=SCOPE, **extra):
    return InquiryPlan(plan_id="run-1", version=1, command="graph Battle of Test", mode=mode, scope=scope,
                       focus=FOCUS, coverage=CoverageMap(), recipe="Event", stopping_rules=["budget spent"],
                       budget_usd=10, items=items if items is not None else [item("P01"), item("P02", ["P01"])],
                       **extra)


class FrontDoorTests(unittest.TestCase):
    def test_a_focus_is_resolved_by_someone_or_ambiguous_between_candidates(self):
        with self.assertRaises(ValidationError):
            ResolvedFocus(status="resolved", chosen=FOCUS.chosen)
        with self.assertRaises(ValidationError):
            ResolvedFocus(status="ambiguous", candidates=[FOCUS.chosen])

    def test_out_of_scope_offers_reframings_and_plans_nothing(self):
        with self.assertRaises(ValidationError):
            ScopeDecision(decision="OUT_OF_SCOPE", primary_intent="PROCEDURAL_INSTRUCTION", explanation="a recipe request")
        out = ScopeDecision(decision="OUT_OF_SCOPE", primary_intent="PROCEDURAL_INSTRUCTION",
                            explanation="a recipe request", reframings=["the history of the dish"])
        with self.assertRaises(ValidationError):
            plan(scope=out)

    def test_an_anchor_without_an_exact_checked_heading_is_provisional(self):
        broader = AuthorityMatch(system="LCSH", identifier="sh1", label="Wars", match_type="broader", checked_at=NOW)
        with self.assertRaises(ValidationError):
            SubjectAnchor(proposed_label="Battle of Test", matches=[broader], provisional=False)
        SubjectAnchor(proposed_label="Battle of Test", matches=[broader], provisional=True)
        with self.assertRaises(ValidationError):
            AuthorityMatch(system="FAST", identifier="1", label="Test", match_type="exact")

    def test_there_is_no_year_zero(self):
        with self.assertRaises(ValidationError):
            OrientationBrief(focus=FOCUS, kind="Event", earliest_year=0, stopping_rule="enough")


class PlanTests(unittest.TestCase):
    def test_items_are_unique_depend_on_earlier_items_and_fit_the_budget(self):
        with self.assertRaises(ValidationError):
            plan(items=[item("P01"), item("P01")])
        with self.assertRaises(ValidationError):
            plan(items=[item("P01", ["P02"]), item("P02")])
        with self.assertRaises(ValidationError):
            plan(items=[item("P01", budget=11)])

    def test_a_decision_makes_a_new_version_and_keeps_the_old(self):
        first = plan()
        second = first.decide("P01", PlanDecision(status="approved", by="curator", at=NOW))
        self.assertEqual((second.version, second.previous_version), (2, 1))
        self.assertEqual(first.item("P01").decision.status, "awaiting")
        self.assertEqual(second.item("P01").decision.status, "approved")
        with self.assertRaises(ValidationError):
            PlanDecision(status="modified", by="curator", at=NOW)

    def test_what_runs_depends_on_the_mode(self):
        awaiting = item("P01")
        self.assertFalse(plan(RunMode.GUIDED).runnable(awaiting))
        self.assertFalse(plan(RunMode.SUPERVISED).runnable(awaiting))
        self.assertTrue(plan(RunMode.SUPERVISED, scope_approved=True).runnable(awaiting))
        self.assertTrue(plan(RunMode.AUTONOMOUS).runnable(awaiting))
        self.assertFalse(plan(RunMode.AUTONOMOUS).runnable(item("P01", status="deferred")))


class RunStateTests(unittest.TestCase):
    def run_state(self, **extra):
        approved = plan(items=[item("P01", status="approved"), item("P02", ["P01"], status="approved")])
        return InquiryRunState(run_id="run-1", command=approved.command, mode=RunMode.GUIDED, plan=approved, **extra)

    def test_the_next_item_waits_for_its_dependencies_and_for_open_questions(self):
        state = self.run_state()
        self.assertEqual(state.next_item().item_id, "P01")
        state.assignments.append(WorkerAssignment(assignment_id="a1", item_id="P01", worker="GraphRevised.x",
                                                  idempotency_key="run-1:P01:1"))
        self.assertIsNone(state.next_item())  # P01 attempted, P02 waits for it to finish
        state.results.append(WorkerResult(assignment_id="a1", status="ok"))
        self.assertEqual(state.next_item().item_id, "P02")
        state.interrupts.append(Interrupt(interrupt_id="i1", reason="identity", question="Which battle is meant?"))
        self.assertIsNone(state.next_item())

    def test_a_finished_run_says_why_and_a_failure_says_what(self):
        with self.assertRaises(ValidationError):
            self.run_state(status=RunStatus.DONE)
        with self.assertRaises(ValidationError):
            WorkerResult(assignment_id="a1", status="failed")

    def test_the_state_round_trips_through_its_file(self):
        state = self.run_state()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            state.save(path)
            self.assertEqual(InquiryRunState.load(path), state)


class ReconcilerAndCriticTests(unittest.TestCase):
    def test_a_related_classification_names_the_stored_claims(self):
        with self.assertRaises(ValidationError):
            ReconciliationDecision(candidate="d1", classification="CONFLICT", explanation="other date", decided_by="model")
        ReconciliationDecision(candidate="d1", classification="NEW_CLAIM", explanation="nothing similar",
                               decided_by="deterministic")

    def test_only_a_supported_if_modified_verdict_carries_a_modification(self):
        common = dict(proposal_id="chr:proposal:x", explanation="see the passage", critic_model="m",
                      prompt_version="critic-v1", saw_rationale=False)
        with self.assertRaises(ValidationError):
            CriticVerdict(verdict="SUPPORTED_IF_MODIFIED", **common)
        with self.assertRaises(ValidationError):
            CriticVerdict(verdict="SUPPORTED_AS_WRITTEN", modification="weaker predicate", **common)
        CriticVerdict(verdict="SUPPORTED_IF_MODIFIED", modification="participatedIn, not commanded", **common)


if __name__ == "__main__":
    unittest.main()
