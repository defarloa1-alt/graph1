#!/usr/bin/env python3
"""
Historian logic guardrails:
- Fischer-style fallacy heuristics
- Bayesian-style confidence update
"""

from __future__ import annotations

import re
from typing import Dict, List


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _bayes_update(prior: float, likelihood: float) -> float:
    """
    Binary Bayesian update using:
      P(H|E) = P(E|H)P(H) / [P(E|H)P(H) + P(E|~H)P(~H)]
    With P(E|~H) approximated as (1 - likelihood) for a simple first-pass model.
    """
    p_e_given_h = _clamp(likelihood, 1e-6, 1.0 - 1e-6)
    p_h = _clamp(prior, 1e-6, 1.0 - 1e-6)
    p_e_given_not_h = 1.0 - p_e_given_h
    denominator = (p_e_given_h * p_h) + (p_e_given_not_h * (1.0 - p_h))
    if denominator <= 0:
        return p_h
    return _clamp((p_e_given_h * p_h) / denominator)


class HistorianLogicEngine:
    """Lightweight Fischer-fallacy checks + Bayesian posterior scoring."""

    _FALLACY_RULES = [
        ("post_hoc_causation", re.compile(r"\b(after|following)\b.{0,80}\b(therefore|thus|hence|caused?|proves?)\b", re.IGNORECASE), 0.12),
        ("fallacy_of_motivation", re.compile(r"\b(motive|motivation|must have intended|intended to|wanted to|agenda)\b", re.IGNORECASE), 0.10),
        ("presentism", re.compile(r"\b(by today'?s standards|modern values|in our time|current morality)\b", re.IGNORECASE), 0.08),
        ("overcertainty", re.compile(r"\b(obviously|undeniably|without doubt|certainly proves)\b", re.IGNORECASE), 0.06),
        ("false_dichotomy", re.compile(r"\b(either|only two)\b.{0,40}\bor\b", re.IGNORECASE), 0.05),
    ]

    _EVIDENCE_PATTERNS = [
        re.compile(r"\bQ\d+\b"),
        re.compile(r"\bP\d+\b"),
        re.compile(r"\baccording to\b", re.IGNORECASE),
        re.compile(r"\bsource(s)?\b", re.IGNORECASE),
        re.compile(r"\bcitation(s)?\b", re.IGNORECASE),
        re.compile(r"\binscription(s)?\b", re.IGNORECASE),
        re.compile(r"\bchronicle(s)?\b", re.IGNORECASE),
    ]

    _CRITICAL_FALLACIES = {"post_hoc_causation", "fallacy_of_motivation"}

    def evaluate(self, label: str, reasoning_notes: str, confidence: float) -> Dict[str, object]:
        text = f"{label} {reasoning_notes}".strip()

        evidence_hits = sum(1 for pattern in self._EVIDENCE_PATTERNS if pattern.search(text))
        reasoning_length_bonus = min(len(reasoning_notes.strip()) / 400.0, 1.0) * 0.08
        evidence_score = _clamp(0.45 + (0.07 * evidence_hits) + reasoning_length_bonus, 0.05, 0.95)

        prior_probability = _clamp(0.20 + (0.60 * confidence), 0.05, 0.95)
        likelihood = _clamp((0.55 * confidence) + (0.45 * evidence_score), 0.05, 0.95)

        detected: List[str] = []
        penalty = 0.0
        for name, pattern, weight in self._FALLACY_RULES:
            if pattern.search(text):
                detected.append(name)
                penalty += weight

        fallacy_penalty = _clamp(penalty, 0.0, 0.50)
        posterior_raw = _bayes_update(prior_probability, likelihood)
        posterior_probability = _clamp(posterior_raw * (1.0 - fallacy_penalty), 0.0, 1.0)

        critical_fallacy = any(name in self._CRITICAL_FALLACIES for name in detected)

        return {
            "prior_probability": round(prior_probability, 4),
            "likelihood": round(likelihood, 4),
            "posterior_probability": round(posterior_probability, 4),
            "evidence_score": round(evidence_score, 4),
            "fallacies_detected": detected,
            "fallacy_penalty": round(fallacy_penalty, 4),
            "critical_fallacy": critical_fallacy,
        }
