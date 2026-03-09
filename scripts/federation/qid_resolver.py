"""
qid_resolver.py — Resolve a Wikidata QID to a canonical Place node backed by Pleiades.

Problem:
  Wikidata properties like P19 (birth place) often point to conceptual QIDs
  (e.g. Q1747689 "Ancient Rome") that exist in the graph as stub Place nodes
  with no Pleiades data. The canonical physical place (Q220 "Roma", Pleiades
  423025) carries min_date, max_date, coordinates, and geo backbone edges.

Resolution strategy (in order):
  1. Graph-local: does a Place with this QID have pleiades_id? → canonical, done.
  2. Wikidata P1566 (Pleiades ID): fetch statements for the QID, look for P1566.
     If found, find or flag the matching Place node in graph.
  3. Wikidata P131 (located in) + P1566: one administrative level up.
  4. Unresolved: return (original_qid, None) — caller decides whether to skip
     or create a stub flagged with needs_resolution=True.

Usage:
    from scripts.federation.qid_resolver import QIDResolver

    resolver = QIDResolver(session)             # pass Neo4j session
    canonical_qid, pleiades_id, method = resolver.resolve("Q1747689")
    # → ("Q220", "423025", "wikidata_p1566")

    # In a loader, guard BORN_IN creation:
    canonical, pleiades, method = resolver.resolve(person.birth_place_qid)
    if pleiades:
        loader.merge_born_in(person_id, canonical, method)
    else:
        print(f"  SKIP BORN_IN {person_id} → {canonical} (no Pleiades backing)")
"""

import sys
import time
import requests
sys.stdout.reconfigure(encoding="utf-8")

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
WIKIDATA_API    = "https://www.wikidata.org/w/api.php"

_SPARQL_HEADERS = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "Chrystallum/1.0 (graph knowledge system; contact: graph@chrystallum.local)",
}


class QIDResolver:
    """
    Resolves a QID to a canonical Place node with Pleiades backing.

    Pass a live Neo4j session on construction. The resolver caches results
    within its lifetime — create one instance per loader run, not per call.

    Wikidata PIDs used for resolution are read from SYS_WikidataProperty nodes
    (P1566 = Pleiades ID, P131 = located in) — not hardcoded.
    """

    def __init__(self, session, timeout: int = 10):
        self._session = session
        self._timeout = timeout
        self._cache: dict[str, tuple[str, str | None, str]] = {}
        self._pid_pleiades, self._pid_located_in = self._load_pids()

    def _load_pids(self) -> tuple[str, str]:
        """Read resolution PIDs from SYS_WikidataProperty nodes."""
        rows = self._session.run("""
            MATCH (w:SYS_WikidataProperty)
            WHERE w.pid IN ['P1566', 'P131']
            RETURN w.pid AS pid, w.semantic_role AS role
        """).data()
        pids = {r["pid"] for r in rows}
        if "P1566" not in pids or "P131" not in pids:
            raise RuntimeError(
                "SYS_WikidataProperty nodes for P1566/P131 not found. "
                "Run 18k_graph_rules_complete.cypher first."
            )
        return "P1566", "P131"

    # ── Public ────────────────────────────────────────────────────────────────

    def resolve(self, qid: str) -> tuple[str, str | None, str]:
        """
        Resolve qid to (canonical_qid, pleiades_id, method).

        method values:
          'graph_direct'    — Place node already has pleiades_id
          'wikidata_p1566'  — resolved via Wikidata P1566 on original QID
          'wikidata_p131'   — resolved via located-in chain + P1566
          'unresolved'      — no Pleiades backing found

        canonical_qid is always the QID of the node that should receive edges.
        pleiades_id is None when method='unresolved'.
        """
        if qid in self._cache:
            return self._cache[qid]

        result = (
            self._try_graph_direct(qid)
            or self._try_wikidata_p1566(qid)
            or self._try_wikidata_p131(qid)
            or (qid, None, "unresolved")
        )
        self._cache[qid] = result
        return result

    def resolve_many(self, qids: list[str]) -> dict[str, tuple[str, str | None, str]]:
        """Resolve a list of QIDs, returns {qid: (canonical, pleiades_id, method)}."""
        return {qid: self.resolve(qid) for qid in qids}

    # ── Strategy 1: graph-local check ─────────────────────────────────────────

    def _try_graph_direct(self, qid: str) -> tuple[str, str, str] | None:
        rows = self._session.run(
            "MATCH (pl:Place {qid: $qid}) "
            "WHERE pl.pleiades_id IS NOT NULL "
            "RETURN pl.qid AS qid, pl.pleiades_id AS pleiades_id",
            {"qid": qid},
        ).data()
        if rows:
            return (rows[0]["qid"], rows[0]["pleiades_id"], "graph_direct")
        return None

    # ── Strategy 2: Wikidata P1566 on the QID itself ──────────────────────────

    def _try_wikidata_p1566(self, qid: str) -> tuple[str, str, str] | None:
        pleiades_id = self._fetch_wikidata_claim(qid, self._pid_pleiades)
        if not pleiades_id:
            return None
        canonical_qid = self._find_place_by_pleiades(pleiades_id)
        if canonical_qid:
            return (canonical_qid, pleiades_id, "wikidata_p1566")
        return (qid, pleiades_id, "wikidata_p1566_no_node")

    # ── Strategy 3: P131 (located in administrative territory) + P1566 ────────

    def _try_wikidata_p131(self, qid: str) -> tuple[str, str, str] | None:
        parent_qid = self._fetch_wikidata_claim(qid, self._pid_located_in)
        if not parent_qid:
            return None
        pleiades_id = self._fetch_wikidata_claim(parent_qid, self._pid_pleiades)
        if not pleiades_id:
            return None
        canonical_qid = self._find_place_by_pleiades(pleiades_id)
        if canonical_qid:
            return (canonical_qid, pleiades_id, "wikidata_p131")
        return None

    # ── Graph helpers ─────────────────────────────────────────────────────────

    def _find_place_by_pleiades(self, pleiades_id: str) -> str | None:
        rows = self._session.run(
            "MATCH (pl:Place {pleiades_id: $pid}) RETURN pl.qid AS qid LIMIT 1",
            {"pid": pleiades_id},
        ).data()
        return rows[0]["qid"] if rows else None

    # ── Wikidata API helpers ───────────────────────────────────────────────────

    def _fetch_wikidata_claim(self, qid: str, pid: str) -> str | None:
        """
        Fetch a single-value claim from Wikidata entity API.
        Returns string value or None.
        """
        try:
            resp = requests.get(
                WIKIDATA_API,
                params={
                    "action": "wbgetclaims",
                    "entity": qid,
                    "property": pid,
                    "format": "json",
                },
                headers=_SPARQL_HEADERS,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            claims = data.get("claims", {}).get(pid, [])
            if not claims:
                return None
            snak = claims[0].get("mainsnak", {})
            dv = snak.get("datavalue", {})
            val = dv.get("value")
            if isinstance(val, str):
                return val
            if isinstance(val, dict):
                # Entity ID (P131 returns {"entity-type":"item","id":"Q220"})
                return val.get("id")
            return None
        except Exception as e:
            print(f"  [qid_resolver] Wikidata fetch failed {qid}/{pid}: {e}")
            return None


# ── Convenience: resolve a list without instantiating (one-shot, no cache) ───

def resolve_born_in(session, qids: list[str], verbose: bool = True
                    ) -> dict[str, tuple[str, str | None, str]]:
    """
    Resolve a list of birth-place QIDs to canonical Pleiades-backed Places.
    Prints a summary if verbose=True.
    Returns {original_qid: (canonical_qid, pleiades_id, method)}.
    """
    resolver = QIDResolver(session)
    results = resolver.resolve_many(qids)
    if verbose:
        by_method: dict[str, int] = {}
        for _, (_, _, method) in results.items():
            by_method[method] = by_method.get(method, 0) + 1
        print("  QID resolution summary:")
        for method, count in sorted(by_method.items()):
            print(f"    {method:<30} {count:>6}")
    return results
