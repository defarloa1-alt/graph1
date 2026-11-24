"""Spend meter: priced, logged, refused at the cap (41 §3.8). Offline; no model calls."""
import json
import os
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from GraphRevised.spend_meter import (BudgetRefused, Meter, MeteredClient, ceiling, priced, report,
                                      read_ledger, ENV)


def usage(i=1000, o=500, cr=0, cw=0, speed=None):
    return SimpleNamespace(input_tokens=i, output_tokens=o, cache_read_input_tokens=cr,
                           cache_creation_input_tokens=cw, speed=speed)


class FakeClient:
    def __init__(self, u=None):
        self.calls = 0
        endpoint = SimpleNamespace(parse=self._call, create=self._call, count_tokens=lambda **k: "free")
        self.messages = endpoint
        self.beta = SimpleNamespace(messages=endpoint)
        self.u = u or usage()

    def _call(self, **kwargs):
        self.calls += 1
        return SimpleNamespace(model=kwargs["model"], usage=self.u, _request_id="req_1")

    def with_options(self, **kwargs):
        return self


REQUEST = {"model": "claude-opus-5-5", "max_tokens": 1000, "system": "s", "messages": [{"role": "user", "content": "hi"}]}


class SpendMeterTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.ledger = self.dir / "ledger.jsonl"
        self.budgets = self.dir / "budgets.json"
        self.budgets.write_text(json.dumps({"budgets": {"test": {"capUSD": "1"}, "shut": {"capUSD": "1", "closed": True}}}))

    def meter(self, cap="1"):
        return Meter("test", Decimal(cap), "unit", self.ledger)

    def test_prices_usage_including_cache(self):
        cost, tokens = priced("claude-opus-5-5", usage(1_000_000, 1_000_000, 1_000_000, 1_000_000))
        self.assertEqual(cost, Decimal("4") + Decimal("20") + Decimal("0.20") + Decimal("5"))
        self.assertEqual(tokens["cacheReadTokens"], 1_000_000)
        fast, _ = priced("claude-opus-5-5", usage(1_000_000, 0, speed="fast"))
        self.assertEqual(fast, Decimal("8"))

    def test_a_run_cap_refuses_a_call_that_could_pass_it_inside_the_budget(self):
        client = FakeClient()
        capped = Meter("test", Decimal("1"), "unit", self.ledger, run_cap=Decimal("0.03"))
        MeteredClient(client, capped).messages.create(**REQUEST)  # ceiling about $0.025: allowed
        with self.assertRaises(BudgetRefused):
            MeteredClient(client, capped).messages.create(**REQUEST)  # $0.014 spent + the ceiling > $0.03
        self.assertEqual(client.calls, 1)
        again = Meter("test", Decimal("1"), "unit", self.ledger, run_cap=Decimal("0.03"))
        self.assertEqual(again.run_spent, Decimal("0.014"))  # the run's spend is read from the ledger
        with mock.patch.dict(os.environ, {ENV: "test", "CHRYSTALLUM_RUN": "unit", "CHRYSTALLUM_RUN_CAP": "0.5"}):
            self.assertEqual(Meter.from_environment(budgets=self.budgets, ledger=self.ledger).run_cap, Decimal("0.5"))

    def test_ceiling_covers_all_of_max_tokens(self):
        self.assertGreaterEqual(ceiling("claude-opus-5-5", REQUEST), Decimal(1000) * 20 / 1_000_000)

    def test_unknown_model_is_refused_before_the_call(self):
        client = FakeClient()
        with self.assertRaises(BudgetRefused):
            MeteredClient(client, self.meter()).messages.create(**{**REQUEST, "model": "claude-unknown"})
        self.assertEqual(client.calls, 0)

    def test_call_is_logged_and_spend_carries_across_runs(self):
        client = FakeClient()
        MeteredClient(client, self.meter()).beta.messages.parse(**REQUEST)
        [entry] = read_ledger(self.ledger)
        self.assertEqual((entry["budget"], entry["model"], entry["inputTokens"]), ("test", "claude-opus-5-5", 1000))
        self.assertEqual(Decimal(entry["costUSD"]), Decimal("0.014"))
        self.assertEqual(self.meter().spent, Decimal("0.014"))

    def test_a_billed_reply_that_fails_to_parse_is_logged_at_its_ceiling(self):
        client = FakeClient()

        def unparsable(**kwargs):
            client.calls += 1
            raise ValueError("Invalid JSON: EOF while parsing")
        client.beta = SimpleNamespace(messages=SimpleNamespace(parse=unparsable))
        with self.assertRaises(ValueError):
            MeteredClient(client, self.meter()).beta.messages.parse(**REQUEST)
        [entry] = read_ledger(self.ledger)
        self.assertTrue(entry["estimated"])
        self.assertEqual(Decimal(entry["costUSD"]), ceiling("claude-opus-5-5", REQUEST))

    def test_a_refused_request_is_not_logged(self):
        import anthropic
        import httpx
        client = FakeClient()
        response = httpx.Response(400, request=httpx.Request("POST", "https://example.invalid"))

        def refused(**kwargs):
            raise anthropic.BadRequestError("grammar too large", response=response, body=None)
        client.beta = SimpleNamespace(messages=SimpleNamespace(parse=refused))
        with self.assertRaises(anthropic.BadRequestError):
            MeteredClient(client, self.meter()).beta.messages.parse(**REQUEST)
        self.assertEqual(read_ledger(self.ledger), [])

    def test_refuses_when_the_ceiling_would_pass_the_cap(self):
        client = FakeClient()
        metered = MeteredClient(client, self.meter(cap="0.03"))
        metered.messages.create(**REQUEST)  # ceiling ~0.024, spends 0.014
        with self.assertRaises(BudgetRefused):
            metered.with_options(max_retries=0).messages.create(**REQUEST)
        self.assertEqual(client.calls, 1)

    def test_unmetered_paths_and_streaming_are_refused(self):
        metered = MeteredClient(FakeClient(), self.meter())
        self.assertEqual(metered.messages.count_tokens(**REQUEST), "free")
        for attempt in (lambda: metered.messages.stream, lambda: metered.messages.batches,
                        lambda: metered.messages.create(**REQUEST, stream=True), lambda: metered.models):
            with self.assertRaises(BudgetRefused):
                attempt()

    def test_a_budget_must_be_named_open_and_listed(self):
        for env, ok in ((None, False), ("missing", False), ("shut", False), ("test", True)):
            with mock.patch.dict(os.environ, {ENV: env} if env else {}, clear=False):
                if not env:
                    os.environ.pop(ENV, None)
                if ok:
                    self.assertEqual(Meter.from_environment("unit", self.budgets, self.ledger).cap, Decimal("1"))
                else:
                    with self.assertRaises(BudgetRefused):
                        Meter.from_environment("unit", self.budgets, self.ledger)

    def test_the_run_is_named_by_the_caller_the_environment_or_the_script(self):
        from GraphRevised.spend_meter import RUN_ENV, run_name
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(RUN_ENV, None)
            self.assertEqual(run_name("lange-read", "-c"), "lange-read")
            self.assertEqual(run_name(None, "C:/x/rests_on_check.py"), "rests_on_check")
            self.assertEqual(run_name(None, "-c"), "unnamed")
            self.assertEqual(run_name(None, ""), "unnamed")
            os.environ[RUN_ENV] = "adhoc-probe"
            os.environ[ENV] = "test"
            self.assertEqual(run_name(None, "-c"), "adhoc-probe")
            self.assertEqual(Meter.from_environment(None, self.budgets, self.ledger).run, "adhoc-probe")
            self.assertEqual(Meter.from_environment("named", self.budgets, self.ledger).run, "named")

    def test_client_factory_refuses_without_a_budget(self):
        from GraphRevised.proposals.passage_reader import anthropic_client
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(ENV, None)
            with self.assertRaises(BudgetRefused):
                anthropic_client()

    def test_report(self):
        MeteredClient(FakeClient(), self.meter()).messages.create(**REQUEST)
        text = report(read_ledger(self.ledger), {"test": {"capUSD": "1"}})
        self.assertIn("test: $0.01 spent of $1 cap, 1 calls", text)
        self.assertIn("run unit", text)


if __name__ == "__main__":
    unittest.main()
