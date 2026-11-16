import pytest

from GraphRevised.discovery import event_subject_view
from GraphRevised.discovery.subject_view import (
    ASSERTIONS_QUERY, EVIDENCE_QUERY, FOCUS_QUERY, HIERARCHY_QUERY,
    PLACEMENTS_QUERY, TOPICAL_QUERY, build_view,
)


INQUIRY = {
    "id": "chr:inquiry:philippi",
    "subjectId": "chr:subject:history-of-philippi",
    "narrativeEventId": "chr:entity:battle-of-philippi",
    "sources": [{"workId": "chr:entity:work"}],
}


class Result:
    def __init__(self, rows):
        self.rows = rows

    def data(self):
        return self.rows


class Tx:
    def __init__(self):
        self.calls = []

    def run(self, query, **params):
        self.calls.append((query, params))
        focus = {"id": INQUIRY["narrativeEventId"], "label": "Philippi", "status": "proposed"}
        phase = {"id": "chr:entity:phase:battle-of-philippi:engagement", "label": "Engagement", "status": "proposed"}
        event = {"id": "chr:entity:depicted:work:action", "label": "Action", "status": "proposed"}
        def place(id, child, parent):
            return {"child": child, "parent": parent,
                    "assertion": {"id": id, "label": id, "status": "proposed", "predicate": "partOf", "mode": None}}
        if query == FOCUS_QUERY:
            assert params == {"subjectId": INQUIRY["subjectId"], "focusId": focus["id"]}
            return Result([{"subject": {"id": INQUIRY["subjectId"], "label": "History", "status": "candidate"}, "focus": focus}])
        if query == HIERARCHY_QUERY:
            return Result([])
        if query == PLACEMENTS_QUERY:
            assert params["phasePrefix"] == "chr:entity:phase:battle-of-philippi:"
            return Result([place("phase-link", phase, focus), place("event-link", event, phase)])
        if query == ASSERTIONS_QUERY:
            assert set(params["eventIds"]) == {focus["id"], phase["id"], event["id"]}
            return Result([{"assertion": {"id": "claim", "label": "Claim", "status": "proposed", "predicate": "occurred", "mode": None, "category": None},
                            "eventId": event["id"], "role": "ASSERTION_SUBJECT", "workId": None, "workLabel": None}])
        if query == EVIDENCE_QUERY:
            return Result([])
        if query == TOPICAL_QUERY:
            return Result([])
        raise AssertionError("Unexpected query")


def test_philippi_builds_focus_specific_routes_without_actium_topical_scope():
    tx = Tx()
    view = build_view(tx, subject_id=INQUIRY["subjectId"], focus_id=INQUIRY["narrativeEventId"], section_id=None)
    assert view["focus"]["id"] == INQUIRY["narrativeEventId"]
    assert [event["id"] for event in view["assertions"][0]["routes"][0]["events"]] == [
        "chr:entity:depicted:work:action", "chr:entity:phase:battle-of-philippi:engagement", INQUIRY["narrativeEventId"]]
    assert not any(query == TOPICAL_QUERY for query, _ in tx.calls)


@pytest.mark.parametrize("change", [
    {"subjectId": None}, {"narrativeEventId": "chr:entity:"}, {"sources": []},
    {"sources": [{"workId": "chr:entity:work"}, {"workId": "chr:entity:work"}]},
])
def test_invalid_inquiries_fail_before_connecting(change):
    with pytest.raises(ValueError):
        event_subject_view.validate_inquiry({**INQUIRY, **change})


def test_selected_child_must_be_linked_and_is_passed_through(monkeypatch):
    captured = []
    monkeypatch.setattr(event_subject_view, "build_with_source_timeline",
                        lambda tx, inquiry, **kwargs: captured.append(kwargs) or {})

    class ChildTx:
        def __init__(self, rows):
            self.rows = rows

        def run(self, query, **params):
            assert params == {"section": "chr:subject:child", "parent": INQUIRY["subjectId"]}
            return Result(self.rows)

    with pytest.raises(ValueError, match="child Subject"):
        event_subject_view.build_event_view(ChildTx([]), INQUIRY, "chr:subject:child")
    event_subject_view.build_event_view(ChildTx([{"id": "chr:subject:child"}]), INQUIRY, "chr:subject:child")
    assert captured == [{"subject_id": INQUIRY["subjectId"], "focus_id": INQUIRY["narrativeEventId"], "section_id": "chr:subject:child"}]


def test_cli_refuses_to_overwrite_and_uses_read_transaction(tmp_path, monkeypatch):
    import json

    inquiry_path = tmp_path / "inquiry.json"
    inquiry_path.write_text(json.dumps(INQUIRY), encoding="utf-8")
    output = tmp_path / "view.json"
    output.write_text("existing", encoding="utf-8")
    calls = []

    class Session:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute_read(self, fn):
            calls.append("read")
            return fn(object())

    class Driver:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def session(self, **kwargs):
            assert kwargs["default_access_mode"] == event_subject_view.READ_ACCESS
            return Session()

    monkeypatch.setattr(event_subject_view, "local_config",
                        lambda: {"uri": "neo4j://localhost", "user": "u", "password": "p", "database": "neo4j"})
    monkeypatch.setattr(event_subject_view.GraphDatabase, "driver", lambda *args, **kwargs: Driver())
    monkeypatch.setattr(event_subject_view, "build_event_view", lambda tx, inquiry, section: {"summary": {}})
    assert event_subject_view.main([str(inquiry_path), "--output", str(output)]) == 1
    assert output.read_text(encoding="utf-8") == "existing"
    assert calls == ["read"]
