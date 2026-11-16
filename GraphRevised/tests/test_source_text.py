import pytest

from GraphRevised.discovery.source_text import include_source_text
from GraphRevised.discovery.subject_view import deduplicate_source_passages


@pytest.mark.parametrize(("system", "rights"), [
    ("LacusCurtius", "The text is in the public domain. (1917 edition)"),
    ("Project Gutenberg", "Project Gutenberg catalogue: Public domain in the USA."),
    ("Perseus", "Translation public domain in the US (published 1920). TEI markup CC BY-SA 4.0"),
    ("Perseus", "Translation public domain (1920); TEI markup https://creativecommons.org/licenses/by-sa/4.0/"),
    ("Wikipedia", "Creative Commons Attribution-Share Alike 4.0 (https://creativecommons.org/licenses/by-sa/4.0/deed.en), as the wiki states it"),
])
def test_text_and_quotation_require_recognized_rights(system, rights):
    row = include_source_text({"sourceSystem": system, "rights": rights,
                               "passageText": "A preserved passage", "quotation": "A preserved"})
    assert row["textAvailability"] == "available"
    assert row["passageText"] == "A preserved passage"
    assert row["quotation"] == "A preserved"


@pytest.mark.parametrize(("system", "rights"), [
    ("Other", None),
    ("Perseus", "rights not recorded; TEI markup CC BY-SA 4.0"),
    ("LacusCurtius", "Rights not stated on the page."),
    ("Wikipedia", "All rights reserved"),
])
def test_unknown_rights_never_export_text(system, rights):
    row = include_source_text({"sourceSystem": system, "rights": rights,
                               "passageText": "Restricted", "quotation": "Restricted"})
    assert row["textAvailability"] == "rights-unconfirmed"
    assert row["passageText"] is None
    assert row["quotation"] is None


def test_missing_text_is_distinct_from_unknown_rights():
    assert include_source_text({"sourceSystem": None, "rights": None, "passageText": None})["textAvailability"] == "not-recorded"


def test_snapshot_deduplicates_across_evidence_and_mentions():
    evidence = {"observationId": "o1", "passageText": "A passage", "quotation": "A"}
    mention = {"observationId": "o1", "passageText": "A passage"}
    view = {"assertions": [{"evidence": [evidence], "routes": []}],
            "sourceTimeline": {"events": [{"mentions": [mention]}], "assertions": []}}
    deduplicate_source_passages(view)
    assert view["sourcePassages"] == {"o1": "A passage"}
    assert evidence["quotation"] == "A"
    assert "passageText" not in evidence and "passageText" not in mention


def test_snapshot_rejects_conflicting_passage_for_same_observation():
    view = {"assertions": [{"evidence": [{"observationId": "o1", "passageText": "one"}], "routes": []}],
            "sourceTimeline": {"events": [{"mentions": [{"observationId": "o1", "passageText": "two"}]}], "assertions": []}}
    with pytest.raises(ValueError, match="Conflicting source text"):
        deduplicate_source_passages(view)
