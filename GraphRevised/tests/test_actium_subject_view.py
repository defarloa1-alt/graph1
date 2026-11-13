import pytest

from GraphRevised.discovery.actium_subject_view import (
    ASSERTIONS_QUERY, EVIDENCE_QUERY, FOCUS_ID, FOCUS_QUERY, HIERARCHY_QUERY,
    PHASE_PREFIX, PLACEMENTS_QUERY, TOPICAL_QUERY, build_view,
)


def node(id, status="proposed"):
    return {"id": id, "label": id, "status": status}


def placement(id, child, parent, status="proposed"):
    return {
        "child": child, "parent": parent,
        "assertion": {"id": id, "label": id, "status": status, "predicate": "partOf", "mode": "attributed"},
    }


class Result:
    def __init__(self, rows):
        self.rows = rows

    def data(self):
        return self.rows


class FakeTx:
    def __init__(self, missing_focus=False):
        self.missing_focus = missing_focus
        self.focus = node(FOCUS_ID, "resolved")
        self.phase = node(PHASE_PREFIX + "engagement", "provisional")
        self.depiction = node("depiction")
        self.orphan = node("orphan")
        self.queries = []

    def run(self, query, **params):
        self.queries.append((query, params))
        if query == FOCUS_QUERY:
            return Result([] if self.missing_focus else [{"subject": node("subject"), "focus": self.focus}])
        if query == HIERARCHY_QUERY:
            return Result([{"subjects": [node("subject"), node("parent", "candidate")]}])
        if query == PLACEMENTS_QUERY:
            return Result([
                placement("phase-placement", self.phase, self.focus, "accepted"),
                placement("event-placement", self.depiction, self.phase),
                placement("orphan-placement", self.orphan, node(PHASE_PREFIX + "unlinked")),
            ])
        if query == TOPICAL_QUERY:
            return Result([])
        if query == ASSERTIONS_QUERY:
            assert set(params["eventIds"]) == {FOCUS_ID, self.phase["id"], "depiction"}
            a = {"id": "alignment", "label": "alignment", "status": "proposed",
                 "predicate": "depictsSameAs", "mode": None, "category": "interpretive"}
            return Result([{"assertion": a, "eventId": "depiction", "role": "ASSERTION_SUBJECT",
                            "workId": None, "workLabel": None}])
        if query == EVIDENCE_QUERY:
            assert set(params["assertionIds"]) == {"alignment", "phase-placement", "event-placement"}
            return Result([
                {"assertionId": "alignment", "evidenceState": "proposal", "proposalStatus": "submitted",
                 "observationId": "passage"},
                {"assertionId": "event-placement", "evidenceState": "proposal", "proposalStatus": "rejected",
                 "observationId": "placement-passage"},
                {"assertionId": "phase-placement", "evidenceState": "supported", "proposalStatus": None,
                 "observationId": "phase-passage"},
            ])
        raise AssertionError("Unexpected query")


def test_routes_retain_placement_status_evidence_and_subject_hierarchy():
    view = build_view(FakeTx())
    assert view["summary"] == {"eventsReached": 3, "assertions": 1,
                               "assertionsByStatus": {"proposed": 1}, "broaderPaths": 1}
    assert view["broaderSubjectPaths"][0][-1]["status"] == "candidate"
    claim = view["assertions"][0]
    assert (claim["status"], claim["mode"]) == ("proposed", "asserted")
    assert claim["evidence"][0]["proposalStatus"] == "submitted"
    route = claim["routes"][0]
    assert route["assertionRole"] == "ASSERTION_SUBJECT"
    assert [event["id"] for event in route["events"]] == ["depiction", PHASE_PREFIX + "engagement", FOCUS_ID]
    assert [p["status"] for p in route["placements"]] == ["proposed", "accepted"]
    assert route["placements"][0]["evidence"][0]["proposalStatus"] == "rejected"
    assert route["placements"][1]["evidence"][0]["evidenceState"] == "supported"


def test_missing_focus_fails_explicitly():
    with pytest.raises(ValueError, match="exactly one"):
        build_view(FakeTx(missing_focus=True))


def test_queries_scope_live_claims_without_identity_or_other_predicate_propagation():
    assert "['proposed', 'accepted']" in PLACEMENTS_QUERY
    assert "['proposed', 'accepted']" in ASSERTIONS_QUERY
    assert "predicate: 'partOf'" in PLACEMENTS_QUERY
    assert "depictsSameAs" not in PLACEMENTS_QUERY
    assert "link.quotation AS quotation" in EVIDENCE_QUERY
    assert "o.passageText AS passageText" in EVIDENCE_QUERY


def test_topical_route_shows_own_status_and_referenced_assertion_evidence():
    class TopicalTx(FakeTx):
        def run(self, query, **params):
            if query == TOPICAL_QUERY:
                return Result([{
                    "event": self.depiction, "section": node("section", "candidate"),
                    "placement": {"status": "proposed", "sourceAssertionId": "event-placement", "reason": "Aftermath"},
                    "sourceAssertion": {"id": "event-placement", "label": "old placement", "status": "proposed",
                                        "predicate": "partOf", "mode": None},
                }])
            return super().run(query, **params)

    view = build_view(TopicalTx())
    route = next(r for r in view["assertions"][0]["routes"] if r["kind"] == "subjectPlacement")
    assert route["topicalPlacement"]["status"] == "proposed"
    assert route["section"]["status"] == "candidate"
    assert route["sourceAssertion"]["evidence"][0]["proposalStatus"] == "rejected"
