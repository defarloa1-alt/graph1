import pytest

from GraphRevised.pilots.actium_meaning_memory_placements import decide_placement, submit_placements, validate_manifest


EVENT = "chr:entity:depicted:dio:nicopolis"
ASSERTION = "chr:assertion:example"


def manifest():
    return {"curator": "TD", "placements": [
        {"eventId": EVENT, "sourceAssertionId": ASSERTION, "reason": "Commemoration of the battle."},
    ]}


class Result:
    def __init__(self, rows):
        self.rows = rows

    def data(self):
        return self.rows

    def single(self, strict=False):
        assert strict
        return self.rows[0]


class FakeTx:
    def __init__(self, source=True, prior=None, decision=True):
        self.source = source
        self.prior = prior
        self.decision = decision
        self.calls = []

    def run(self, query, **params):
        self.calls.append((query, params))
        if "RETURN s.id AS id" in query:
            return Result([{"id": params["id"]}])
        if "RETURN s.label AS label" in query:
            return Result([])
        if " AS cycle" in query:
            return Result([{"cycle": False}])
        if "AS eventStatus" in query:
            return Result([{"eventStatus": "proposed", "assertionStatus": "proposed"}] if self.source else [])
        if "RETURN properties(r) AS placement" in query:
            return Result([{"placement": self.prior}] if self.prior else [])
        if "RETURN child.id AS id" in query:
            return Result([{"id": params["child"]}])
        if "RETURN r.status AS status" in query:
            if "decision" in params:
                return Result([{"status": params["decision"], "sourceAssertionId": ASSERTION}] if self.decision else [])
            return Result([{"status": "proposed"}])
        raise AssertionError(query)


def test_manifest_requires_explicit_individual_reasons_and_unique_events():
    assert validate_manifest(manifest())["curator"] == "TD"
    item = manifest()
    item["placements"].append(item["placements"][0])
    with pytest.raises(ValueError, match="Duplicate event"):
        validate_manifest(item)
    item = manifest()
    item["placements"][0]["reason"] = " "
    with pytest.raises(ValueError, match="non-empty"):
        validate_manifest(item)


def test_submission_keeps_source_and_proposes_instead_of_accepting():
    tx = FakeTx()
    result = submit_placements(tx, manifest(), "2026-11-10T00:00:00+00:00")
    assert result["proposedPlacements"] == 1
    query, params = next(call for call in tx.calls if "MERGE (event)-[r:IN_SUBJECT]" in call[0])
    assert "r.status = 'proposed'" in query
    assert params["assertionId"] == ASSERTION and params["curator"] == "TD"


def test_missing_source_and_conflicting_prior_fail_before_write():
    tx = FakeTx(source=False)
    with pytest.raises(ValueError, match="lacks evidence"):
        submit_placements(tx, manifest(), "time")
    assert not any("MERGE " in query for query, _ in tx.calls)
    tx = FakeTx(prior={"status": "accepted"})
    with pytest.raises(ValueError, match="differs or was reviewed"):
        submit_placements(tx, manifest(), "time")
    assert not any("MERGE " in query for query, _ in tx.calls)


def test_decision_is_explicit_guarded_and_terminal():
    tx = FakeTx()
    result = decide_placement(tx, EVENT, "accepted", "TD", "Reviewed evidence.", "time")
    assert result["status"] == "accepted"
    assert "r.status = 'proposed'" in tx.calls[0][0]
    with pytest.raises(ValueError, match="already decided"):
        decide_placement(FakeTx(decision=False), EVENT, "accepted", "TD", "Reviewed.", "time")
    with pytest.raises(ValueError, match="basis"):
        decide_placement(tx, EVENT, "accepted", "TD", "", "time")
