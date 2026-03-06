#!/usr/bin/env python3
"""Unit tests for ADR-008 Layer 1 (dprr_layer1)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dprr_layer1 import (
    parse_dprr_label,
    map_pcode_to_canonical,
    normalise_wikidata_date,
    PRAENOMEN_ABBREV_TO_FULL,
    DPRRLabelParse,
)


def test_parse_pompey():
    """POMP1976 Cn. Pompeius (31) Cn. f. Sex. n. Clu. Magnus"""
    label = "POMP1976 Cn. Pompeius (31) Cn. f. Sex. n. Clu. Magnus"
    p = parse_dprr_label(label)
    assert p.gens_prefix == "POMP"
    assert p.label_dprr_id == "1976"
    assert p.praenomen_abbrev == "Cn."
    assert p.nomen == "Pompeius"
    assert p.dprr_ordinal == "31"
    assert "Cn." in p.filiation_chain and "f." in p.filiation_chain
    assert p.tribe_abbrev == "Clu."
    assert "Magnus" in p.cognomen


def test_parse_unknown_praenomen():
    """-." = unknown praenomen"""
    label = "CORN54 -. Cornelia (54) Clu. "
    p = parse_dprr_label(label)
    assert p.gens_prefix == "CORN"
    assert p.praenomen_abbrev is None  # "-." becomes None
    assert p.nomen == "Cornelia"


def test_parse_minimal():
    """Minimal label"""
    label = "POMP1976 Cn. Pompeius (31) Magnus"
    p = parse_dprr_label(label)
    assert p.gens_prefix == "POMP"
    assert p.nomen == "Pompeius"
    assert p.cognomen == ["Magnus"]


def test_praenomen_ser_servius():
    """Ser. = Servius (not Sergius); Sherk, Rome and the Greek East"""
    assert PRAENOMEN_ABBREV_TO_FULL.get("Ser.") == "Servius"


def test_map_pcode():
    assert map_pcode_to_canonical("P19") == ("BORN_IN", "Place")
    assert map_pcode_to_canonical("P27") == ("CITIZEN_OF", "Polity")
    assert map_pcode_to_canonical("P999") is None


def test_normalise_date_year():
    """Year precision (9)"""
    # +0106 = 106 AD; -0106 = 106 BCE. Test BCE:
    tv2 = {"time": "-0106-09-29T00:00:00Z", "precision": 9}
    e2, l2 = normalise_wikidata_date(tv2)
    assert e2 == "-0106-01-01"
    assert l2 == "-0106-12-31"


def test_normalise_date_day():
    """Day precision (11)"""
    tv = {"time": "-0106-09-29T00:00:00Z", "precision": 11}
    e, l = normalise_wikidata_date(tv)
    assert e == "-0106-09-29"
    assert l == "-0106-09-29"


if __name__ == "__main__":
    test_parse_pompey()
    print("  parse_pompey OK")
    test_parse_unknown_praenomen()
    print("  parse_unknown_praenomen OK")
    test_parse_minimal()
    print("  parse_minimal OK")
    test_praenomen_ser_servius()
    print("  praenomen_ser_servius OK")
    test_map_pcode()
    print("  map_pcode OK")
    test_normalise_date_year()
    print("  normalise_date_year OK")
    test_normalise_date_day()
    print("  normalise_date_day OK")
    print("All Layer 1 tests passed.")
