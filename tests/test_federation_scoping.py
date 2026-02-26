#!/usr/bin/env python3
"""Tests for federation-aware scoping in the harvester."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.tools.wikidata_backlink_harvest import _compute_federation_scoping


def test_temporal_scoped_trismegistos():
    """P1696 (Trismegistos) → temporal_scoped 0.95"""
    status, conf = _compute_federation_scoping({"P1696": "12345"})
    assert status == "temporal_scoped"
    assert conf == 0.95


def test_temporal_scoped_lgpn():
    """P1047 (LGPN) → temporal_scoped 0.95"""
    status, conf = _compute_federation_scoping({"P1047": "abc"})
    assert status == "temporal_scoped"
    assert conf == 0.95


def test_temporal_scoped_pleiades():
    """P1584 (Pleiades) → temporal_scoped 0.95"""
    status, conf = _compute_federation_scoping({"P1584": "423025"})
    assert status == "temporal_scoped"
    assert conf == 0.95


def test_temporal_scoped_dprr():
    """P6863 (DPRR) or has_dprr → temporal_scoped 0.85"""
    status, conf = _compute_federation_scoping({"P6863": "1234"})
    assert status == "temporal_scoped"
    assert conf == 0.85
    status2, conf2 = _compute_federation_scoping({}, has_dprr=True)
    assert status2 == "temporal_scoped"
    assert conf2 == 0.85


def test_domain_scoped_viaf():
    """P214 (VIAF) + domain proximity → domain_scoped 0.85"""
    status, conf = _compute_federation_scoping({"P214": "123"}, has_domain_proximity=True)
    assert status == "domain_scoped"
    assert conf == 0.85


def test_unscoped_no_federation_ids():
    """No federation IDs → unscoped 0.40"""
    status, conf = _compute_federation_scoping({})
    assert status == "unscoped"
    assert conf == 0.40


def test_unscoped_only_non_federation():
    """Only non-federation external IDs (e.g. P2671) → unscoped 0.40"""
    status, conf = _compute_federation_scoping({"P2671": "/g/121t5v4t"})
    assert status == "unscoped"
    assert conf == 0.40


def test_temporal_overrides_viaf():
    """Ancient-world IDs take precedence over VIAF"""
    status, conf = _compute_federation_scoping({"P214": "x", "P1696": "y"})
    assert status == "temporal_scoped"
    assert conf == 0.95


def test_domain_scoped_conceptual_entity():
    """Conceptual entity (Organization, Place, etc.) + domain proximity → domain_scoped 0.85 (HARVESTER_SCOPING_DESIGN)"""
    status, conf = _compute_federation_scoping(
        {}, has_domain_proximity=True, scoping_class="conceptual"
    )
    assert status == "domain_scoped"
    assert conf == 0.85


def test_unscoped_conceptual_without_proximity():
    """Conceptual entity without domain proximity stays unscoped"""
    status, conf = _compute_federation_scoping(
        {}, has_domain_proximity=False, scoping_class="conceptual"
    )
    assert status == "unscoped"
    assert conf == 0.40
