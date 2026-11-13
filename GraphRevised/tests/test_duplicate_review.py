from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from GraphRevised.discovery.duplicate_review import (
    ASSERTIONS, EVIDENCE, HISTORY, MAX_ASSERTIONS, MAX_OUTPUT_TOKENS, PROPOSALS,
    SELECT_IDS, Review, assess, main, prepare,
)


class Result:
    def __init__(self, rows):
        self.rows = rows

    def data(self):
        return deepcopy(self.rows)


class FakeTx:
    def __init__(self):
        self.ids = ["a", "b"]
        self.assertions = [
            {"id": "a", "properties": {"status": "superseded", "predicate": "occurred",
                                       "timeSourceExpression": "seven days"},
             "endpoints": [{"relation": "ASSERTION_SUBJECT", "id": "event"}]},
            {"id": "b", "properties": {"status": "proposed", "predicate": "occurred",
                                       "timeSourceExpression": "for seven days"},
             "endpoints": [{"relation": "ASSERTION_SUBJECT", "id": "event"}]},
        ]
        self.proposals = [{"assertionId": "b", "properties": {"id": "proposal", "status": "submitted"}}]
        self.history = [{"assertionId": "a", "otherId": "b", "supersededId": "a", "replacementId": "b"}]
        self.evidence = [{
            "assertionId": "b", "proposalId": "proposal", "relation": "PROPOSES_EVIDENCE",
            "observation": {"id": "obs", "sourceSystem": "LacusCurtius",
                            "rights": "The text is in the public domain.", "passageText": "seven days"},
            "link": {"quotation": "seven days", "qualifierQuotations": ["time:seven days"]},
        }]

    def run(self, query, **params):
        rows = {SELECT_IDS: [{"id": item} for item in self.ids],
                ASSERTIONS: self.assertions, PROPOSALS: self.proposals,
                HISTORY: self.history, EVIDENCE: self.evidence}[query]
        return Result(rows)


def model_response(comparisons, stop="end_turn"):
    usage = SimpleNamespace(input_tokens=42, output_tokens=13,
                            cache_read_input_tokens=0, cache_creation_input_tokens=0)
    return SimpleNamespace(model="test", stop_reason=stop,
                           parsed_output=Review.model_validate({"comparisons": comparisons}), usage=usage)


def comparison(ids=("a", "b"), refs=("obs",)):
    return {"assertion_ids": list(ids), "assessment": "uncertain",
            "rationale": "Compare the time expressions and their evidence.",
            "limitations": "The record needs curator review.", "evidence_ids": list(refs)}


def fake_client(response):
    return SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(parse=Mock(return_value=response))))


def test_packet_retains_unary_claim_qualifiers_status_and_history():
    packet = prepare(FakeTx(), "event", [])
    a, b = packet["assertions"]
    assert a["properties"]["status"] == "superseded"
    assert a["history"][0]["replacementId"] == "b"
    assert b["properties"]["timeSourceExpression"] == "for seven days"
    assert b["proposals"][0]["status"] == "submitted"
    assert b["evidence"][0]["observation"]["id"] == "obs"
    assert b["evidence"][0]["link"]["quotation"] == "seven days"
    assert b["evidence"][0]["textAvailability"] == "available"
    assert not any(e["relation"] == "ASSERTION_OBJECT" for e in b["endpoints"])


def test_unconfirmed_text_and_qualifier_quotes_are_withheld():
    tx = FakeTx()
    tx.evidence[0]["observation"]["rights"] = "unknown"
    tx.evidence[0]["observation"]["passageText"] = None
    tx.evidence[0]["link"]["quotation"] = None
    evidence = prepare(tx, None, ["a", "b"])["assertions"][1]["evidence"][0]
    assert evidence["observation"]["passageText"] is None
    assert "qualifierQuotations" not in evidence["link"]
    assert evidence["textAvailability"] == "rights-unconfirmed"


def test_scope_and_missing_assertions_fail_explicitly():
    tx = FakeTx()
    tx.ids = [str(n) for n in range(MAX_ASSERTIONS + 1)]
    with pytest.raises(ValueError, match="more than"):
        prepare(tx, "event", [])
    with pytest.raises(ValueError, match="different assertion"):
        prepare(tx, None, ["a", "a"])
    tx.assertions = tx.assertions[:1]
    with pytest.raises(ValueError, match="not found"):
        prepare(tx, None, ["a", "b"])


def test_review_records_model_reasoning_and_evidence():
    packet = prepare(FakeTx(), None, ["a", "b"])
    client = fake_client(model_response([comparison()]))
    report = assess(packet, client, "test")
    assert report["status"] == "needs-review"
    assert report["comparisons"][0]["assessment"] == "uncertain"
    assert report["comparisons"][0]["evidence_ids"] == ["obs"]
    assert report["usage"]["inputTokens"] == 42
    assert client.beta.messages.parse.call_args.kwargs["max_tokens"] == MAX_OUTPUT_TOKENS
    assert report["packet"] == packet


@pytest.mark.parametrize("comparisons, error", [
    ([], "every selected"),
    ([comparison(), comparison()], "repeated"),
    ([comparison(("a", "c"))], "unknown"),
    ([comparison(refs=("invented",))], "unknown or unrelated"),
    ([comparison(refs=())], "must cite"),
])
def test_invalid_or_incomplete_model_comparisons_fail(comparisons, error):
    packet = prepare(FakeTx(), None, ["a", "b"])
    with pytest.raises(ValueError, match=error):
        assess(packet, fake_client(model_response(comparisons)), "test")


def test_refusal_and_truncated_answer_fail():
    packet = prepare(FakeTx(), None, ["a", "b"])
    for stop in ("refusal", "max_tokens"):
        with pytest.raises(RuntimeError, match="no complete review"):
            assess(packet, fake_client(model_response([comparison()], stop)), "test")


def test_three_assertions_need_every_pair_and_pair_specific_citations():
    tx = FakeTx()
    tx.assertions.append({"id": "c", "properties": {"status": "accepted"}, "endpoints": []})
    tx.proposals.append({"assertionId": "c", "properties": {"id": "other", "status": "accepted"}})
    packet = prepare(tx, None, ["a", "b", "c"])
    comparisons = [comparison(), comparison(("a", "c"), ("other",)),
                   comparison(("b", "c"), ("obs", "other"))]
    assert len(assess(packet, fake_client(model_response(comparisons)), "test")["comparisons"]) == 3
    comparisons[0]["evidence_ids"] = ["other"]
    with pytest.raises(ValueError, match="unrelated"):
        assess(packet, fake_client(model_response(comparisons)), "test")


def test_cli_requires_explicit_sharing_consent_and_no_overwrite(tmp_path):
    path = tmp_path / "report.json"
    with pytest.raises(SystemExit):
        main(["--assertion", "a", "--assertion", "b", "--output", str(path)])
    path.write_text("existing", encoding="utf-8")
    with pytest.raises(FileExistsError):
        main(["--assertion", "a", "--assertion", "b", "--output", str(path), "--prepare-only"])
    assert path.read_text(encoding="utf-8") == "existing"
