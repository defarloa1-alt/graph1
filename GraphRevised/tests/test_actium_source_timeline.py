from GraphRevised.discovery import actium_subject_view
from GraphRevised.discovery.actium_subject_view import add_source_timeline
from GraphRevised.proposals.entities import depicted_event_id


def test_timeline_scopes_events_and_keeps_source_order_and_reviewed_matches():
    view = {"assertions": [{"routes": [{"events": [{"id": "a"}, {"id": "b"}]}]}]}
    report = {
        "sources": [{"workId": "work", "voice": "Source"}],
        "events": [{"id": "a", "status": "proposed"}, {"id": "b", "status": "proposed"},
                   {"id": "outside", "status": "proposed"}],
        "assertions": [
            {"id": "before", "predicate": "happenedBefore", "status": "proposed", "mode": "attributed",
             "subjectId": "a", "objectId": "b"},
            {"id": "match", "predicate": "depictsSameAs", "status": "proposed", "mode": None,
             "subjectId": "a", "objectId": "b"},
            {"id": "outside", "predicate": "happenedBefore", "status": "proposed", "mode": "attributed",
             "subjectId": "a", "objectId": "outside"},
            {"id": "rejected", "predicate": "occurred", "status": "rejected", "mode": "attributed",
             "subjectId": "a", "objectId": None},
            {"id": "asserted", "predicate": "occurred", "status": "accepted", "mode": "asserted",
             "subjectId": "a", "objectId": None},
        ],
    }
    add_source_timeline(view, report)
    assert [event["id"] for event in view["sourceTimeline"]["events"]] == ["a", "b"]
    assert [claim["id"] for claim in view["sourceTimeline"]["assertions"]] == ["before", "match"]


def test_timeline_discovers_scoped_works_outside_inquiry(monkeypatch):
    work_id = "chr:entity:additional-work"
    event_id = depicted_event_id(work_id, "action")
    view = {"assertions": [{"evidence": [], "routes": [{"events": [{"id": event_id}], "placements": []}]}]}
    inquiry = {"sources": [{"workId": "chr:entity:known-work", "voice": "Known"}]}

    class Result:
        def data(self):
            return [{"eventId": event_id, "workId": work_id, "workLabel": "Additional"}]

    class Tx:
        def run(self, query, **params):
            assert params["ids"] == [event_id]
            return Result()

    def report(tx, expanded, candidate_limit):
        assert candidate_limit == 0
        assert expanded["sources"] == inquiry["sources"] + [{"workId": work_id, "voice": "Additional"}]
        return {"sources": expanded["sources"], "events": [{"id": event_id, "status": "proposed", "mentions": []}], "assertions": []}

    monkeypatch.setattr(actium_subject_view, "build_view", lambda tx: view)
    monkeypatch.setattr(actium_subject_view, "build_report", report)
    result = actium_subject_view.build_with_source_timeline(Tx(), inquiry)
    assert result["sourceTimeline"]["events"][0]["id"] == event_id
    assert len(inquiry["sources"]) == 1
