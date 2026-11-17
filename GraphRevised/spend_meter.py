"""Spend meter: every model call is priced, logged, and stopped at a cap (41 §3.8).

All model paths get their client from `proposals.passage_reader.anthropic_client()`,
which wraps it here. Before each call the meter computes a ceiling (a generous
input estimate plus the full `max_tokens` as output) and refuses the call if the
ceiling would take the named budget past its cap. After the call it prices the
reported usage and appends one line to the ledger.

A model call needs a named budget: set CHRYSTALLUM_BUDGET to a name in
curation/budgets.json (the curator's). With no budget named, or a model with no
known price, no call is made.

    python -m GraphRevised.spend_meter            # spend by budget, run and model
    python -m GraphRevised.spend_meter --budget actium

Prices are USD per million tokens, first-party API rates (cached 2026-11-03).
Cache reads default to 0.1x input and cache writes to 1.25x input (5-minute
cache) unless a model lists its own. Fast mode is priced at 2x.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
BUDGETS = ROOT / "curation" / "budgets.json"
LEDGER = ROOT / "runs" / "spend-ledger.jsonl"
ENV = "CHRYSTALLUM_BUDGET"

# (input, output, cache read or None for 0.1x input)
PRICES: dict[str, tuple[str, str, str | None]] = {
    "claude-fable-5-2": ("8", "40", "0.20"),
    "claude-fable-5-1": ("10", "50", None),
    "claude-fable-5": ("10", "50", None),
    "claude-opus-5-5": ("4", "20", "0.20"),
    "claude-opus-5": ("5", "25", None),
    "claude-opus-4-8": ("5", "25", None),
    "claude-opus-4-7": ("5", "25", None),
    "claude-opus-4-6": ("5", "25", None),
    "claude-sonnet-5-5": ("2", "10", "0.10"),
    "claude-sonnet-5": ("2", "10", None),
    "claude-sonnet-4-6": ("3", "15", None),
    "claude-haiku-5-5": ("0.10", "0.50", None),  # prompts up to 100K tokens
    "claude-haiku-4-5": ("1", "5", None),
}
MILLION = Decimal(1_000_000)
CHARS_PER_TOKEN = 2  # deliberately low: over-estimates input, so the ceiling errs high


class BudgetRefused(RuntimeError):
    """No model call was made."""


@dataclass(frozen=True)
class Rates:
    input: Decimal
    output: Decimal
    cache_read: Decimal
    cache_write: Decimal


def rates(model: str) -> Rates:
    if model not in PRICES:
        raise BudgetRefused(f"No known price for model {model!r}; add it to spend_meter.PRICES first.")
    i, o, cr = PRICES[model]
    inp = Decimal(i)
    return Rates(inp, Decimal(o), Decimal(cr) if cr else inp / 10, inp * Decimal("1.25"))


def ceiling(model: str, request: dict[str, Any]) -> Decimal:
    """Most this call can cost: estimated input at the cache-write rate plus all of max_tokens."""
    r = rates(model)
    body = {k: request.get(k) for k in ("system", "messages", "tools", "output_format", "output_config")}
    est_in = len(json.dumps(body, default=str, ensure_ascii=False)) // CHARS_PER_TOKEN + 1000
    out = int(request.get("max_tokens") or 0)
    cost = (Decimal(est_in) * max(r.input, r.cache_write) + Decimal(out) * r.output) / MILLION
    return cost * 2 if request.get("speed") == "fast" else cost


def priced(model: str, usage: Any) -> tuple[Decimal, dict[str, int]]:
    r = rates(model)
    tokens = {
        "inputTokens": int(getattr(usage, "input_tokens", 0) or 0),
        "outputTokens": int(getattr(usage, "output_tokens", 0) or 0),
        "cacheReadTokens": int(getattr(usage, "cache_read_input_tokens", 0) or 0),
        "cacheWriteTokens": int(getattr(usage, "cache_creation_input_tokens", 0) or 0),
    }
    cost = (tokens["inputTokens"] * r.input + tokens["outputTokens"] * r.output
            + tokens["cacheReadTokens"] * r.cache_read + tokens["cacheWriteTokens"] * r.cache_write) / MILLION
    return (cost * 2 if getattr(usage, "speed", None) == "fast" else cost), tokens


def load_budgets(path: Path = BUDGETS) -> dict[str, dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8")).get("budgets", {}) if path.exists() else {}


def read_ledger(path: Path = LEDGER) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def spent(budget: str, path: Path = LEDGER) -> Decimal:
    return sum((Decimal(e["costUSD"]) for e in read_ledger(path) if e.get("budget") == budget), Decimal(0))


class Meter:
    """One budget, its cap, and the ledger it writes to."""

    def __init__(self, budget: str, cap: Decimal, run: str, ledger: Path = LEDGER):
        if not cap.is_finite() or cap <= 0:
            raise BudgetRefused(f"Budget {budget!r} has no positive cap.")
        self.budget, self.cap, self.run, self.ledger = budget, cap, run, ledger
        self.spent = spent(budget, ledger)

    @classmethod
    def from_environment(cls, run: str | None = None, budgets: Path = BUDGETS, ledger: Path = LEDGER) -> "Meter":
        name = os.environ.get(ENV)
        if not name:
            raise BudgetRefused(f"No budget named: set {ENV} to a budget in {budgets.name} before any model call.")
        entry = load_budgets(budgets).get(name)
        if not entry:
            raise BudgetRefused(f"Budget {name!r} is not in {budgets.name}.")
        if entry.get("closed"):
            raise BudgetRefused(f"Budget {name!r} is closed.")
        return cls(name, Decimal(str(entry["capUSD"])), run or Path(sys.argv[0]).stem or "python", ledger)

    def reserve(self, request: dict[str, Any]) -> Decimal:
        top = ceiling(request["model"], request)
        if self.spent + top > self.cap:
            raise BudgetRefused(
                f"Budget {self.budget!r}: ${self.spent:.4f} spent of ${self.cap}; this call could cost up to "
                f"${top:.4f}. No model call made.")
        return top

    def record(self, request: dict[str, Any], response: Any, top: Decimal) -> Decimal:
        model = getattr(response, "model", None) or request["model"]
        if model not in PRICES:
            model = request["model"]
        cost, tokens = priced(model, response.usage)
        self.spent += cost
        entry = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "budget": self.budget,
                 "run": self.run, "model": model, **tokens, "costUSD": str(cost.quantize(Decimal("0.000001"))),
                 "ceilingUSD": str(top.quantize(Decimal("0.000001"))),
                 "requestId": getattr(response, "_request_id", None)}
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return cost

    def record_estimate(self, request: dict[str, Any], top: Decimal, reason: str) -> Decimal:
        """A billed call whose usage is unknown: logged at its ceiling, marked estimated."""
        self.spent += top
        entry = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "budget": self.budget,
                 "run": self.run, "model": request["model"], "costUSD": str(top.quantize(Decimal("0.000001"))),
                 "ceilingUSD": str(top.quantize(Decimal("0.000001"))), "estimated": True, "failure": reason}
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return top


def _is_api_status_error(error: Exception) -> bool:
    try:
        import anthropic
    except ImportError:  # pragma: no cover
        return False
    return isinstance(error, (anthropic.APIStatusError, anthropic.APIConnectionError))


class _Messages:
    def __init__(self, inner: Any, meter: Meter):
        self._inner, self._meter = inner, meter

    def _metered(self, method: str, kwargs: dict[str, Any]) -> Any:
        if kwargs.get("stream"):
            raise BudgetRefused("Streaming calls are not metered yet; no model call made.")
        top = self._meter.reserve(kwargs)
        try:
            response = getattr(self._inner, method)(**kwargs)
        except Exception as error:
            # A refused request (an API status error, such as a 400) is not billed. Any other failure
            # came after the model answered (a reply that does not parse): billed, usage unknown, so it
            # is logged at its ceiling, marked estimated, to overstate rather than miss it (2026-11-16).
            if not _is_api_status_error(error):
                self._meter.record_estimate(kwargs, top, type(error).__name__)
            raise
        self._meter.record(kwargs, response, top)
        return response

    def create(self, **kwargs: Any) -> Any:
        return self._metered("create", kwargs)

    def parse(self, **kwargs: Any) -> Any:
        return self._metered("parse", kwargs)

    def count_tokens(self, **kwargs: Any) -> Any:  # free
        return self._inner.count_tokens(**kwargs)

    def __getattr__(self, name: str) -> Any:
        raise BudgetRefused(f"messages.{name} is not metered; no model call made.")


class _Beta:
    def __init__(self, inner: Any, meter: Meter):
        self._inner, self._meter = inner, meter

    @property
    def messages(self) -> _Messages:
        return _Messages(self._inner.messages, self._meter)

    def __getattr__(self, name: str) -> Any:
        raise BudgetRefused(f"beta.{name} is not metered; no model call made.")


class MeteredClient:
    """Passes calls to the Anthropic client, priced and capped by a Meter."""

    def __init__(self, client: Any, meter: Meter):
        self._client, self.meter = client, meter

    @property
    def messages(self) -> _Messages:
        return _Messages(self._client.messages, self.meter)

    @property
    def beta(self) -> _Beta:
        return _Beta(self._client.beta, self.meter)

    def with_options(self, **kwargs: Any) -> "MeteredClient":
        return MeteredClient(self._client.with_options(**kwargs), self.meter)

    def __getattr__(self, name: str) -> Any:
        raise BudgetRefused(f"client.{name} is not metered; no model call made.")


def report(entries: list[dict[str, Any]], budgets: dict[str, dict[str, Any]], only: str | None = None) -> str:
    by: dict[str, dict[str, Any]] = defaultdict(lambda: {"cost": Decimal(0), "calls": 0,
                                                         "runs": defaultdict(Decimal), "models": defaultdict(Decimal)})
    for e in entries:
        if only and e["budget"] != only:
            continue
        b = by[e["budget"]]
        c = Decimal(e["costUSD"])
        b["cost"] += c
        b["calls"] += 1
        b["runs"][e["run"]] += c
        b["models"][e["model"]] += c
    names = [only] if only else sorted(set(by) | set(budgets))
    lines = []
    for name in names:
        b, cap = by[name], budgets.get(name, {}).get("capUSD")
        lines.append(f"{name}: ${b['cost']:.2f} spent" + (f" of ${cap} cap" if cap else " (no budget entry)")
                     + f", {b['calls']} calls")
        for label, part in (("run", b["runs"]), ("model", b["models"])):
            for key, cost in sorted(part.items(), key=lambda kv: -kv[1]):
                lines.append(f"  {label} {key}: ${cost:.4f}")
    return "\n".join(lines) or "No budgets and no spend recorded."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--budget", help="report one budget only")
    args = parser.parse_args(argv)
    print(report(read_ledger(), load_budgets(), args.budget))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
