import pytest

from GraphRevised.discovery.event_evidence_report import (
    ASSERTIONS_QUERY, EVIDENCE_QUERY, EVENTS_QUERY, MENTIONS_QUERY, build_report, candidates,
)


def event(id, label, work, status="proposed"):
    return {"id": id, "label": label, "shortLabel": label, "status": status, "sourceWorkId": work}


def test_lexical_candidates_only_between_sources_and_never_accepted():
    events = [
        event("a", "Queen flees sailing east", "work1"),
        event("b", "Queen flees sailing south", "work2"),
        event("c", "Queen flees sailing north", "work1"),
        event("d", "Queen flees sailing west", "work3", "rejected"),
        event("e", "Queen flees sailing west", None),
    ]
    leads, total = candidates(events)
    assert total == 2
    assert {(p["leftId"], p["rightId"]) for p in leads} == {("a", "b"), ("b", "c")}
    assert all(p["reviewStatus"] == "unreviewed" for p in leads)
    assert all(p["sharedTerms"] == ["flees", "queen", "sailing"] for p in leads)
    limited, total = candidates(events, limit=1)
    assert len(limited) == 1 and total == 2


class Result:
    def __init__(self, rows):
        self.rows = rows

    def data(self):
        return self.rows


class FakeTx:
    def run(self, query, **params):
        if query == EVENTS_QUERY:
            return Result([
                {"id": "chr:entity:depicted:work-one:flight", "label": "Queen flees sailing east",
                 "shortLabel": None, "status": "proposed"},
                {"id": "chr:entity:depicted:work-two:flight", "label": "Queen flees sailing south",
                 "shortLabel": None, "status": "proposed"},
            ])
        if query == MENTIONS_QUERY:
            return Result([{"eventId": "chr:entity:depicted:work-one:flight",
                            "observationId": "passage", "workId": "chr:entity:work-one"}])
        if query == ASSERTIONS_QUERY:
            return Result([{"id": "assertion1", "predicate": "happenedBefore", "status": "proposed"}])
        if query == EVIDENCE_QUERY:
            return Result([{"assertionId": "assertion1", "observationId": "passage",
                            "evidenceState": "proposal", "proposalStatus": "submitted"}])
        assert "phase:" in params["prefix"]
        return Result([])


def test_report_preserves_proposed_status_pending_evidence_and_unmentioned_event():
    inquiry = {"id": "inquiry", "narrativeEventId": "chr:entity:battle-of-actium",
               "sources": [{"workId": "chr:entity:work-one"}, {"workId": "chr:entity:work-two"}]}
    report = build_report(FakeTx(), inquiry)
    assert report["summary"]["events"] == 2
    assert report["summary"]["eventsWithoutMentions"] == 1
    assert report["assertions"][0]["status"] == "proposed"
    assert report["assertions"][0]["evidence"][0]["evidenceState"] == "proposal"
    assert report["alignmentCandidates"][0]["reviewStatus"] == "unreviewed"


def test_duplicate_inquiry_source_refused():
    inquiry = {"narrativeEventId": "chr:entity:battle-of-actium",
               "sources": [{"workId": "chr:entity:work"}, {"workId": "chr:entity:work"}]}
    with pytest.raises(ValueError, match="duplicate source"):
        build_report(FakeTx(), inquiry)
