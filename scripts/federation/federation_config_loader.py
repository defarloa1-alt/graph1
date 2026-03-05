#!/usr/bin/env python3
"""
Federation Config Loader — Read scoring rules from Neo4j SYS_Threshold

D-024: Values subject to change by business owner belong in decision tables,
not in code. This module loads federation scoring weights and state boundaries
from SYS_Threshold nodes when Neo4j is available.

Fallback: Returns hardcoded defaults when Neo4j unavailable (dry run, tests).
"""

from typing import Dict, Optional, Tuple

# Fallback defaults (matches federation_scorer.py originals)
DEFAULT_WEIGHTS = {
    'place_qid': 30,
    'period_qid': 30,
    'geo_context_qid': 20,
    'temporal_bounds': 15,
    'relationships': 5,
}

DEFAULT_STATES = {
    'FS0_UNFEDERATED': (0, 39),
    'FS1_BASE': (40, 59),
    'FS2_FEDERATED': (60, 79),
    'FS3_WELL_FEDERATED': (80, 100),
}

# Place simple (D16)
DEFAULT_PLACE_WEIGHTS = {'pleiades': 20, 'qid': 50, 'temporal': 20, 'coords': 10}

# Period simple (D17)
DEFAULT_PERIOD_WEIGHTS = {'periodo': 30, 'qid': 50, 'temporal': 20}

# Subject authority (D18)
DEFAULT_SUBJECT_WEIGHTS = {'lcsh': 30, 'fast': 30, 'lcc': 20, 'qid': 20}


def _get_driver():
    """Lazy Neo4j driver. Returns None if config unavailable."""
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
        if not NEO4J_URI or not NEO4J_PASSWORD:
            return None
        from neo4j import GraphDatabase
        return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD))
    except Exception:
        return None


def load_federation_thresholds(
    driver=None,
) -> Tuple[Dict[str, int], Dict[str, Tuple[int, int]]]:
    """
    Load federation weights and state boundaries from SYS_Threshold.

    Returns:
        (weights, states) — weights dict for place_period_subgraph,
        states dict mapping state_name -> (min_score, max_score)
    """
    drv = driver or _get_driver()
    if not drv:
        return DEFAULT_WEIGHTS.copy(), dict(DEFAULT_STATES)

    try:
        with drv.session() as session:
            result = session.run("""
                MATCH (t:SYS_Threshold)
                WHERE t.name STARTS WITH 'federation_'
                RETURN t.name AS name, t.value AS value
            """)
            rows = [dict(r) for r in result]
    except Exception:
        return DEFAULT_WEIGHTS.copy(), dict(DEFAULT_STATES)
    finally:
        if driver is None and drv:
            drv.close()

    # Build weights from threshold names
    weights = {}
    state_mins = {}  # state_name -> min
    state_maxs = {}  # state_name -> max

    for r in rows:
        name = r.get('name') or ''
        val = r.get('value')
        if val is None:
            continue
        try:
            val = int(float(val))
        except (TypeError, ValueError):
            continue

        if name == 'federation_weight_place_qid':
            weights['place_qid'] = val
        elif name == 'federation_weight_period_qid':
            weights['period_qid'] = val
        elif name == 'federation_weight_geo_context_qid':
            weights['geo_context_qid'] = val
        elif name == 'federation_weight_temporal_bounds':
            weights['temporal_bounds'] = val
        elif name == 'federation_weight_relationships':
            weights['relationships'] = val
        elif name == 'federation_state_FS0_max':
            state_maxs['FS0_UNFEDERATED'] = val
        elif name == 'federation_state_FS1_min':
            state_mins['FS1_BASE'] = val
        elif name == 'federation_state_FS1_max':
            state_maxs['FS1_BASE'] = val
        elif name == 'federation_state_FS2_min':
            state_mins['FS2_FEDERATED'] = val
        elif name == 'federation_state_FS2_max':
            state_maxs['FS2_FEDERATED'] = val
        elif name == 'federation_state_FS3_min':
            state_mins['FS3_WELL_FEDERATED'] = val

    # Build states: FS0 min is 0, FS3 max is 100
    states = {}
    if 'FS0_UNFEDERATED' in state_maxs:
        states['FS0_UNFEDERATED'] = (0, state_maxs['FS0_UNFEDERATED'])
    for sname in ['FS1_BASE', 'FS2_FEDERATED', 'FS3_WELL_FEDERATED']:
        if sname in state_mins and sname in state_maxs:
            states[sname] = (state_mins[sname], state_maxs[sname])
        elif sname == 'FS3_WELL_FEDERATED' and sname in state_mins:
            states[sname] = (state_mins[sname], 100)

    if not weights:
        weights = DEFAULT_WEIGHTS.copy()
    else:
        for k, v in DEFAULT_WEIGHTS.items():
            weights.setdefault(k, v)

    if not states:
        states = dict(DEFAULT_STATES)

    return weights, states


def load_place_periodo_half_credit(driver=None) -> float:
    """Load periodo half-credit ratio (0.5 = half credit when no qid)."""
    drv = driver or _get_driver()
    if not drv:
        return 0.5
    try:
        with drv.session() as session:
            result = session.run("""
                MATCH (t:SYS_Threshold {name: 'federation_periodo_half_credit'})
                RETURN t.value AS value
            """)
            r = result.single()
            if r and r.get('value') is not None:
                return float(r['value'])
    except Exception:
        pass
    finally:
        if driver is None and drv:
            drv.close()
    return 0.5
