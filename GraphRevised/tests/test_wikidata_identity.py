import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

from GraphRevised.adapters.wikidata_identity import WikidataIdentityAdapter


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


class FakeSession:
    def __init__(self, responses: list[dict]) -> None:
        self._responses = iter(responses)

    def get(self, *_args, **_kwargs) -> FakeResponse:
        return FakeResponse(next(self._responses))


class WikidataIdentityAdapterTests(unittest.TestCase):
    def test_discovery_persists_raw_payloads_and_returns_candidates(self) -> None:
        search_payload = {
            "search": [
                {
                    "id": "Q160387",
                    "label": "Battle of Actium",
                    "description": "naval battle",
                    "match": {"type": "label"},
                    "concepturi": "http://www.wikidata.org/entity/Q160387",
                }
            ]
        }
        entity_payload = {
            "entities": [
                {
                    "id": "Q160387",
                    "lastrevid": 2555342002,
                    "labels": {"en": {"language": "en", "value": "Battle of Actium"}},
                }
            ]
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            adapter = WikidataIdentityAdapter(
                Path(temporary_directory),
                session=FakeSession([search_payload, entity_payload]),
            )
            result = adapter.discover("Battle of Actium")

            self.assertEqual(result.candidates[0].identifier, "Q160387")
            self.assertEqual(result.candidates[0].label, "Battle of Actium")
            self.assertIsNotNone(result.observation)
            self.assertEqual(result.observation.source_entity_id, "Q160387")
            self.assertEqual(result.observation.revision, "2555342002")
            self.assertEqual(result.observation.status, "observed")

            entity_path = Path(url2pathname(urlparse(result.observation.payload_uri).path))
            self.assertEqual(json.loads(entity_path.read_text(encoding="utf-8")), entity_payload)
            self.assertEqual(
                hashlib.sha256(entity_path.read_bytes()).hexdigest(),
                result.observation.content_hash,
            )
            self.assertTrue(entity_path.with_suffix(".metadata.json").exists())

    def test_discovery_returns_no_observation_when_no_candidate_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            adapter = WikidataIdentityAdapter(
                Path(temporary_directory),
                session=FakeSession([{"search": []}]),
            )
            result = adapter.discover("Unresolvable historical name")

            self.assertEqual(result.candidates, ())
            self.assertIsNone(result.observation)


if __name__ == "__main__":
    unittest.main()
