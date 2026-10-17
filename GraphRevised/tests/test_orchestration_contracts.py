"""The one-command contracts (31 §3): plans, decisions by mode, run state, reconciler and critic outputs."""

import json
import tempfile
import unittest
from pathlib import Path
from typing import get_args

from pydantic import ValidationError

from GraphRevised.orchestration.contracts import (
    AuthorityMatch, CoverageContribution, CoverageMap, CriticVerdict, EvidencePacket, IdentityCandidate, Inquiry,
    InquiryPlan, InquiryRunState, Interrupt, OrientationBrief, OrientationDossier, PlanDecision, PlanItem, Program,
    ReconciliationDecision, ResolvedFocus, RunMode, RunStatus, ScopeDecision, SubjectAnchor, SubjectKind,
    WorkerAssignment, WorkerResult,
)
from GraphRevised.proposals.registry import load_registry

NOW = "2026-01-01T00:00:00+00:00"
INQUIRY = "chr:inquiry:battle-of-test"
FOCUS = ResolvedFocus(status="resolved", decided_by="front-door",
                      chosen=IdentityCandidate(label="Battle of Test", kind="Event", qid="Q1", why="the only match"))
SCOPE = ScopeDecision(decision="IN_SCOPE", primary_intent="HISTORICAL_GRAPH_CONSTRUCTION", explanation="a historical battle")


def item(item_id, depends_on=(), status="awaiting", budget=1.0):
    decision = PlanDecision(status=status, by="curator", at=NOW) if status != "awaiting" else PlanDecision()
    return PlanItem(item_id=item_id, action="READ", target="a work", rationale="read the main narrative",
                    expected_outputs=["proposals"], budget_usd=budget, depends_on=list(depends_on), decision=decision)


def plan(mode=RunMode.GUIDED, items=None, scope=SCOPE, **extra):
    return InquiryPlan(plan_id="run-1", inquiry_id=INQUIRY, version=1, command="graph Battle of Test", mode=mode, scope=scope,
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

    def test_approve_all_decides_only_what_awaits(self):
        first = plan(items=[item("P01"), item("P02", status="deferred")])
        second = first.approve_all(by="curator", at=NOW)
        self.assertEqual(second.version, 2)
        self.assertEqual(second.item("P01").decision.status, "approved")
        self.assertEqual(second.item("P02").decision.status, "deferred")

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
        return InquiryRunState(run_id="run-1", command=approved.command, inquiry_id=INQUIRY, mode=RunMode.GUIDED,
                               owner="curator", plan=approved, **extra)

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
        state.assignments.append(WorkerAssignment(assignment_id="a1", item_id="P01", worker="GraphRevised.x",
                                                  idempotency_key="run-1:P01:1"))
        state.results.append(WorkerResult(assignment_id="a1", status="ok", coverage=CoverageContribution(
            new_claim_families=3, new_traditions=1, new_evidence_classes=["coin"])))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            state.save(path)
            self.assertEqual(InquiryRunState.load(path), state)


class InquiryProgramDossierTests(unittest.TestCase):
    def test_an_inquiry_focuses_on_entities_and_is_not_one(self):
        with self.assertRaises(ValidationError):
            Inquiry(inquiry_id=INQUIRY, question="What happened at the battle?", focus_ids=[], kind="Event")
        with self.assertRaises(ValidationError):
            Inquiry(inquiry_id="chr:entity:battle-of-test", question="What happened at the battle?",
                    focus_ids=["chr:entity:battle-of-test"], kind="Event")
        two = Inquiry(inquiry_id=INQUIRY, question="How did the two battles differ?", kind="Event",
                      focus_ids=["chr:entity:battle-a", "chr:entity:battle-b"])
        self.assertEqual(len(two.focus_ids), 2)

    def test_an_inquiry_may_be_about_any_kind_the_registry_has(self):
        kinds = set(load_registry().entity_kinds) - {"Other"}
        self.assertEqual(kinds, set(get_args(SubjectKind)) - {"Constellation"})
        for kind, focus in (("Person", "chr:entity:mark-antony"), ("Place", "chr:entity:actium"),
                            ("Object", "chr:entity:nicopolis-monument"), ("Group", "chr:entity:antonys-fleet")):
            Inquiry(inquiry_id=INQUIRY, question="What does the graph hold about it?", focus_ids=[focus], kind=kind)

    def test_a_closed_inquiry_says_why(self):
        common = dict(inquiry_id=INQUIRY, question="What happened at the battle?", focus_ids=["chr:entity:b"],
                      kind="Event")
        with self.assertRaises(ValidationError):
            Inquiry(status="closed", **common)
        Inquiry(status="closed", closed_reason="no new independent evidence", **common)

    def test_an_inquiry_file_stands_for_its_inquiry_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inquiry.json"
            path.write_text(json.dumps({"id": INQUIRY, "version": 3, "label": "The Battle of Test, as told",
                                        "subjectId": "chr:subject:test", "narrativeEventId": "chr:entity:b"}),
                            encoding="utf-8")
            before = path.read_bytes()
            inquiry = Inquiry.from_reading_file(path, root=Path(directory))
            self.assertEqual(path.read_bytes(), before)
        self.assertEqual((inquiry.inquiry_id, inquiry.focus_ids, inquiry.reading_file),
                         (INQUIRY, ["chr:entity:b"], "inquiry.json"))

    def test_a_program_lists_inquiries_once(self):
        with self.assertRaises(ValidationError):
            Program(program_id="chr:program:test", command="graph Test", title="Test", inquiry_ids=[INQUIRY, INQUIRY])
        with self.assertRaises(ValidationError):
            Program(program_id="chr:program:test", command="graph Test", title="Test", inquiry_ids=["chr:entity:x"])

    def test_a_dossier_revision_is_a_new_version_and_both_are_kept(self):
        brief = OrientationBrief(focus=FOCUS, kind="Event", stopping_rule="enough")
        first = OrientationDossier(dossier_id="chr:dossier:battle-of-test", version=1, focus_ids=["chr:entity:b"],
                                   brief=brief)
        second = first.revise(brief.model_copy(update={"controversies": ["battle or breakout"]}), run_id="run-2",
                              inquiry_id=INQUIRY)
        self.assertEqual((second.version, second.previous_version, second.used_by_inquiries), (2, 1, [INQUIRY]))
        self.assertEqual(first.brief.controversies, [])
        with tempfile.TemporaryDirectory() as directory:
            paths = {first.save(Path(directory)), second.save(Path(directory))}
            self.assertEqual(len(paths), 2)
            self.assertEqual({OrientationDossier.load(p).version for p in paths}, {1, 2})
        with self.assertRaises(ValidationError):
            OrientationDossier(dossier_id="chr:dossier:x", version=2, focus_ids=["chr:entity:b"], brief=brief)


class EvidencePacketTests(unittest.TestCase):
    def state(self, **extra):
        approved = plan(items=[item("P01", status="approved")])
        state = InquiryRunState(run_id="run-1", command=approved.command, inquiry_id=INQUIRY, mode=RunMode.GUIDED,
                                owner="curator", plan=approved)
        state.assignments.append(WorkerAssignment(assignment_id="a1", item_id="P01", worker="GraphRevised.x",
                                                  idempotency_key="run-1:P01:1"))
        return InquiryRunState.model_validate(state.model_dump() | extra)

    def packet(self, **extra):
        return EvidencePacket(**({"packet_id": "k1", "inquiry_id": INQUIRY, "assignment_id": "a1",
                                  "observation_ids": ["chr:observation:test:work:1.1:abc"]} | extra))

    def test_a_packet_holds_preserved_observations_only(self):
        with self.assertRaises(ValidationError):
            self.packet(observation_ids=[])
        with self.assertRaises(ValidationError):
            self.packet(observation_ids=["https://example.org/search?q=battle"])

    def test_a_run_holds_its_packets_and_what_cites_them(self):
        packet = self.packet().model_dump()
        self.state(packets=[packet], results=[{"assignment_id": "a1", "status": "ok", "packet_ids": ["k1"]}])
        with self.assertRaises(ValidationError):
            self.state(packets=[self.packet(assignment_id="a9").model_dump()])
        with self.assertRaises(ValidationError):
            self.state(packets=[self.packet(inquiry_id="chr:inquiry:other").model_dump()])
        with self.assertRaises(ValidationError):
            self.state(results=[{"assignment_id": "a1", "status": "ok", "packet_ids": ["k2"]}])

    def test_a_plan_is_run_for_its_own_inquiry(self):
        with self.assertRaises(ValidationError):
            self.state(inquiry_id="chr:inquiry:other")


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
