import pytest

from GraphRevised.discovery.actium_meaning_memory_pilot import CHILD_ID, PHASE_ID, build_pilot


def fixture():
    event = {"id": "depicted", "label": "Nicopolis", "status": "proposed"}
    phase = {"id": PHASE_ID, "label": "Meaning and memory", "status": "provisional"}
    focus = {"id": "battle", "label": "Battle", "status": "resolved"}
    placement = {"id": "placement", "status": "proposed", "evidence": [{"proposalStatus": "submitted"}]}
    parent = {"id": "parent", "status": "accepted", "evidence": [{"evidenceState": "supported"}]}
    route = {"events": [event, phase, focus], "placements": [placement, parent]}
    return {"assertions": [{"routes": [route]}, {"routes": [route]}]}


def test_pilot_deduplicates_candidates_and_preserves_evidence_and_status():
    pilot = build_pilot(fixture())
    assert pilot["candidateSubject"]["id"] == CHILD_ID
    assert pilot["candidateCount"] == 1
    assert pilot["candidates"][0]["reviewStatus"] == "unreviewed"
    assert pilot["candidates"][0]["existingPlacement"]["evidence"][0]["proposalStatus"] == "submitted"
    assert pilot["existingPhaseToBattleAssertion"]["status"] == "accepted"
    assert pilot["existingPhaseToBattleAssertion"]["evidence"][0]["evidenceState"] == "supported"


def test_missing_parent_assertion_is_not_silently_ignored():
    data = fixture()
    data["assertions"] = []
    with pytest.raises(ValueError, match="phase-to-battle"):
        build_pilot(data)


def test_conflicting_candidate_is_rejected():
    data = fixture()
    data["assertions"][1] = {"routes": [{
        **data["assertions"][0]["routes"][0],
        "events": [{"id": "other", "label": "Other", "status": "proposed"}]
                  + data["assertions"][0]["routes"][0]["events"][1:],
    }]}
    with pytest.raises(ValueError, match="Conflicting"):
        build_pilot(data)
