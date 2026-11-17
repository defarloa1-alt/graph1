"""The event view's debates: Question -> Position -> holders, one hop beyond the event's claims."""
from GraphRevised.discovery.subject_view import (
    EVIDENCE_QUERY, POSITION_LINKS_QUERY, POSITIONS_QUERY, QUESTIONS_QUERY, add_debates,
)

FOCUS = "chr:entity:test-battle"


def claim(id, predicate, status="proposed", **extra):
    return {"id": id, "label": id, "status": status, "predicate": predicate, "mode": "attributed",
            "stance": None, "reception": None, "timeEdtf": None, "timeSourceExpression": None, **extra}


class Result:
    def __init__(self, rows):
        self.rows = rows

    def data(self):
        return self.rows


class Tx:
    def __init__(self, questions=True):
        self.questions = questions
        self.queries = []

    def run(self, query, **params):
        self.queries.append(query)
        assert params.get("live", ["proposed", "accepted"]) == ["proposed", "accepted"]
        if query == QUESTIONS_QUERY:
            assert params["eventIds"] == sorted([FOCUS, "chr:entity:phase"])
            if not self.questions:
                return Result([])
            return Result([{"question": {"id": "q", "label": "Why?", "status": "proposed"},
                            "assertion": claim("about-1", "about"), "about": {"id": FOCUS, "label": "Battle"},
                            "workId": "study", "workLabel": "A study"}])
        if query == POSITIONS_QUERY:
            assert params["questionIds"] == ["q"]
            return Result([{"position": {"id": "p", "label": "To win", "status": "proposed",
                                         "history": "held by A; rejected by B"},
                            "questionId": "q", "assertion": claim("answers-1", "answers"),
                            "workId": "study", "workLabel": "A study"}])
        if query == POSITION_LINKS_QUERY:
            assert params["positionIds"] == ["p"]
            return Result([
                {"positionId": "p", "assertion": claim("holds-1", "holds", stance="originates"),
                 "holder": {"id": "a", "label": "A", "status": "accepted"}, "workId": "study", "workLabel": "A study"},
                {"positionId": "p", "assertion": claim("rejects-1", "rejects"),
                 "holder": {"id": "b", "label": "B", "status": "proposed"}, "workId": "study", "workLabel": "A study"},
                {"positionId": "p", "assertion": claim("reception-1", "hadReception", reception="dominant"),
                 "holder": None, "workId": "study", "workLabel": "A study"},
            ])
        if query == EVIDENCE_QUERY:
            assert params["assertionIds"] == sorted(["about-1", "answers-1", "holds-1", "rejects-1", "reception-1"])
            return Result([{"assertionId": "holds-1", "observationId": "obs", "evidenceState": "proposal",
                            "quotation": "words of a licensed article", "passageText": "more words",
                            "sourceSystem": "licensed-pdf", "rights": "private"}])
        raise AssertionError("Unexpected query")


def view():
    return {"focus": {"id": FOCUS}, "limitations": [], "summary": {},
            "assertions": [{"routes": [{"events": [{"id": "chr:entity:phase"}, {"id": FOCUS}]}]}]}


def test_debates_follow_question_position_and_holders():
    v = view()
    add_debates(Tx(), v)
    [question] = v["debates"]
    assert (question["id"], question["about"][0]["event"]["id"]) == ("q", FOCUS)
    [position] = question["positions"]
    assert position["history"] == "held by A; rejected by B"
    assert [h["holder"]["label"] for h in position["holders"]] == ["A"]
    assert position["holders"][0]["stance"] == "originates"
    assert [h["holder"]["label"] for h in position["rejecters"]] == ["B"]
    assert position["receptions"][0]["reception"] == "dominant"
    assert v["summary"]["debates"] == {"questions": 1, "positions": 1, "claims": 5,
                                       "claimsByStatus": {"proposed": 5}}
    assert v["limitations"]


def test_licensed_words_stay_out_of_the_snapshot():
    v = view()
    add_debates(Tx(), v)
    [evidence] = v["debates"][0]["positions"][0]["holders"][0]["evidence"]
    assert evidence["quotation"] is None and "passageText" not in evidence
    assert evidence["textAvailability"] == "rights-unconfirmed"
    assert v["sourcePassages"] == {}


def test_no_questions_means_no_further_queries():
    v, tx = view(), Tx(questions=False)
    add_debates(tx, v)
    assert v["debates"] == [] and tx.queries == [QUESTIONS_QUERY]
