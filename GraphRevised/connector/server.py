"""Chrystallum's MCP connector: read-only, typed lookups on the local graph (05 §7).

    python -m GraphRevised.connector.server                    stdio, for Claude Code (.mcp.json starts it)
    python -m GraphRevised.connector.server --tunnel                 HTTP behind a Cloudflare quick tunnel, for claude.ai
    python -m GraphRevised.connector.server --http [--port 8765] [--public-host <tunnel host>] [--show-url]
    python -m GraphRevised.connector.server --new-token        writes an MCP token to Connections.txt

Every tool is a bounded operation with a schema; there is no general Cypher
tool (05 §7). Every query runs in a read transaction on a read session, so
nothing here can write to Neo4j. Facts and entity cards come from the same
projection as the Cytoscape export (26-UI-DATA-CONTRACT.md): one fact per
line, with its attestation in words and its voices, proposed and accepted
together (25 decision 2), rejected and superseded left out.

HTTP mode is for claude.ai through a tunnel. claude.ai cannot send a bearer
token to a custom connector, so the token is part of the path
(/mcp/<token>), and requests with any other path get a 404. The password and
the token are read from the environment or from GraphRevised/Connections.txt
(git-ignored) and never printed; --show-url prints the connector URL, token
included, for pasting into claude.ai's connector settings. --tunnel starts a
Cloudflare quick tunnel (no account; a new address each time), waits for its
address, and prints the connector URL to paste (connector/CONNECTOR.md).
"""

from __future__ import annotations

import argparse
import atexit
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from neo4j import READ_ACCESS, GraphDatabase

from GraphRevised.adapters.wikidata_context import entity_context
from GraphRevised.export.cytoscape import projection
from GraphRevised.identity.local_candidates import tokens

GRAPH_REVISED = Path(__file__).resolve().parents[1]
CONNECTIONS = GRAPH_REVISED / "Connections.txt"
DEAD = ["rejected", "superseded"]
PROJECTION_SECONDS = 60
MAX_FACTS = 100
MAX_NOTES = 30

Kind = Literal["Person", "Event", "Place", "Group", "Office", "Work", "Concept", "Period", "Polity", "Type"]

INSTRUCTIONS = """\
Chrystallum is a graph for exploring historical relations, read here without changing anything.
Entities (people, events, places, groups, works, concepts, periods) are joined by facts. A fact is
one line drawn from one or more claims ("voices"): our own asserted statement, or a source's
version "according to" a Work. Proposed and accepted facts are shown together; say which is which.
Attestation is computed from the voices, in words; quote it rather than inventing a confidence.
Imaginative facts (from plays, poems, films) are a separate category: never present them as history.
Never show an authority code (Wikidata QID, LCSH, LCNAF) without its label.
Start with find_entities or lookup_authority to get an entity id, then get_entity, get_fact,
or event_overview."""


def _connections_value(prefix: str) -> str | None:
    if not CONNECTIONS.exists():
        return None
    match = re.search(rf"^{re.escape(prefix)} (.*)$", CONNECTIONS.read_text(encoding="utf-8"), re.M)
    return match.group(1).strip() if match else None


def neo4j_password() -> str:
    password = os.environ.get("NEO4J_PASSWORD") or _connections_value("neo4j pw is")
    if not password:
        raise SystemExit("No Neo4j password: set NEO4J_PASSWORD or add 'neo4j pw is ...' to Connections.txt")
    return password


def mcp_token() -> str | None:
    return os.environ.get("CHRYSTALLUM_MCP_TOKEN") or _connections_value("mcp token is")


class Graph:
    """One driver, read sessions only, and the exploration projection cached for a minute."""

    def __init__(self) -> None:
        self.driver = GraphDatabase.driver(
            os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
            auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), neo4j_password()),
            notifications_min_severity="OFF",
        )
        self.database = os.environ.get("NEO4J_DATABASE", "neo4j")
        self._lock = threading.Lock()
        self._built = 0.0
        self._index: dict[str, Any] = {}

    def read(self, work, *args, **kwargs):
        with self.driver.session(database=self.database, default_access_mode=READ_ACCESS) as session:
            return session.execute_read(work, *args, **kwargs)

    def rows(self, query: str, **params) -> list[dict[str, Any]]:
        return self.read(lambda tx: tx.run(query, **params).data())

    def index(self) -> dict[str, Any]:
        with self._lock:
            if time.monotonic() - self._built > PROJECTION_SECONDS:
                elements = self.read(projection, False)["elements"]
                nodes = {n["data"]["id"]: n["data"] for n in elements["nodes"]}
                facts = {e["data"]["id"]: e["data"] for e in elements["edges"]}
                by_entity: dict[str, list[str]] = {}
                for fact_id, fact in facts.items():
                    by_entity.setdefault(fact["source"], []).append(fact_id)
                    by_entity.setdefault(fact["target"], []).append(fact_id)
                self._index = {"nodes": nodes, "facts": facts, "by_entity": by_entity}
                self._built = time.monotonic()
            return self._index


@lru_cache(maxsize=4096)
def aliases(payload_uri: str | None, qid: str | None) -> tuple[str, ...]:
    return tuple(entity_context(payload_uri, qid).get("aliases", []))


def name_score(query: str, name: str) -> float:
    """1.0 for the same words. When every query word starts a word of the name ("Octavian" in
    "Caesar Octavianus"), 0.5 to 1.0 by how much of the name the query covers, so "Battle of Actium"
    outranks a long event title that mentions Actium. Otherwise the share of words in common."""
    asked, named = tokens(query), tokens(name)
    if not asked or not named:
        return 0.0
    if asked == named:
        return 1.0
    hits = sum(any(word == other or (len(word) >= 4 and other.startswith(word)) for other in named)
               for word in asked)
    if hits == len(asked):
        return 0.5 + 0.5 * len(asked) / max(len(named), len(asked) + 1)
    return hits / len(asked | named)


def _brief(node: dict[str, Any]) -> dict[str, Any]:
    return {"id": node["id"], "label": node["fullLabel"], "kind": node["kind"], "status": node.get("status")}


def build_server(graph: Graph, **settings) -> "FastMCP":
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("Chrystallum", instructions=INSTRUCTIONS, **settings)

    @server.tool()
    def find_entities(name: str, kind: Kind | None = None, limit: int = 10) -> dict[str, Any]:
        """Find entities by name: label, short label, or Wikidata alias (so "Octavian" finds Augustus).
        Returns the best matches with their ids, for get_entity or event_overview."""
        name, limit = name.strip()[:200], max(1, min(limit, 25))
        if not name:
            return {"error": "Give a name to search for."}
        rows = graph.rows(
            """
            MATCH (e:Entity) WHERE e.status <> 'deprecated' AND ($kind IS NULL OR e.kind = $kind)
            OPTIONAL MATCH (e)-[l:HAS_AUTHORITY_RECORD]->(r:AuthorityRecord {system: 'Wikidata'})
            WHERE l.role = 'entity_identity'
            RETURN e.id AS id, e.label AS label, e.shortLabel AS shortLabel, e.kind AS kind,
                   e.status AS status, e.description AS description,
                   head(collect(r.identifier)) AS qid, head(collect(r.rawPayloadUri)) AS payload
            """,
            kind=kind,
        )
        found = []
        for row in rows:
            names = [n for n in (row["label"], row["shortLabel"], *aliases(row["payload"], row["qid"])) if n]
            scored = [(name_score(name, n), n) for n in names]
            score, matched = max(scored, default=(0.0, None))
            if score >= 0.3:
                found.append({"id": row["id"], "label": row["label"], "kind": row["kind"], "status": row["status"],
                              "matched": matched, "score": round(score, 2),
                              "description": (row["description"] or "")[:200] or None})
        facts = graph.index()["by_entity"]
        found.sort(key=lambda f: (-f["score"], -len(facts.get(f["id"], [])), f["label"]))
        return {"matches": found[:limit], "more": max(0, len(found) - limit)}

    @server.tool()
    def lookup_authority(system: str, identifier: str) -> dict[str, Any]:
        """Find the entity holding an external code, e.g. system "Wikidata" identifier "Q1048",
        or "LCNAF" "n50051933". A miss lists the systems the graph holds records for."""
        rows = graph.rows(
            """
            MATCH (r:AuthorityRecord {system: $system, identifier: $identifier})
            OPTIONAL MATCH (e:Entity)-[l:HAS_AUTHORITY_RECORD]->(r)
            RETURN r.label AS recordLabel, e.id AS id, e.label AS label, e.kind AS kind,
                   e.status AS status, l.role AS role
            """,
            system=system.strip(), identifier=identifier.strip(),
        )
        if rows:
            return {"record": f"{system} {identifier}: {rows[0]['recordLabel']}",
                    "entities": [{k: r[k] for k in ("id", "label", "kind", "status", "role")} for r in rows if r["id"]]}
        systems = graph.rows("MATCH (r:AuthorityRecord) RETURN r.system AS system, count(*) AS records "
                             "ORDER BY records DESC")
        return {"record": None, "systems": systems}

    @server.tool()
    def get_entity(entity_id: str, offset: int = 0, limit: int = 50) -> dict[str, Any]:
        """An entity's card: description, authority records, passages of note, and its facts
        (one line each, with attestation and how many voices). Page with offset and limit."""
        index = graph.index()
        node = index["nodes"].get(entity_id)
        if node is None:
            rows = graph.rows("MATCH (e:Entity {id: $id}) RETURN e.label AS label, e.status AS status", id=entity_id)
            if rows:
                return {"error": f"{rows[0]['label']} is {rows[0]['status']} and left out of the exploration view."}
            return {"error": f"No entity {entity_id}. Use find_entities to get an id."}
        limit, offset = max(1, min(limit, MAX_FACTS)), max(0, offset)
        fact_ids = index["by_entity"].get(entity_id, [])
        facts = []
        for fact_id in fact_ids[offset:offset + limit]:
            fact = index["facts"][fact_id]
            outgoing = fact["source"] == entity_id
            other = index["nodes"][fact["target"] if outgoing else fact["source"]]
            facts.append({"factId": fact_id, "sentence": fact["sentence"], "predicate": fact["predicate"],
                          "direction": "out" if outgoing else "in", "other": _brief(other),
                          "status": fact["status"], "mode": fact["mode"], "category": fact["category"],
                          "attestation": fact["attestation"], "times": fact["times"], "voices": len(fact["voices"])})
        return {
            **_brief(node), "description": node.get("description"),
            "authority": [{"system": a["system"], "identifier": a["identifier"], "label": a["label"],
                           "others": a["others"]} for a in node["authority"]],
            "notes": node["notes"][:MAX_NOTES], "moreNotes": max(0, len(node["notes"]) - MAX_NOTES),
            "unaryFacts": [{"sentence": f["sentence"], "times": f["times"], "attestation": f["attestation"],
                            "status": f["status"], "category": f["category"], "voices": f["voiceLines"]}
                           for f in node["facts"]],
            "facts": facts, "totalFacts": len(fact_ids), "offset": offset,
        }

    @server.tool()
    def get_fact(fact_id: str) -> dict[str, Any]:
        """One fact in full: every voice (who says it, when, in what role and context), the
        quotations with their locators (pending ones marked), and each voice's review history."""
        fact = graph.index()["facts"].get(fact_id)
        if fact is None:
            return {"error": f"No fact {fact_id}. Fact ids come from get_entity."}
        nodes = graph.index()["nodes"]
        keep = ("sentence", "predicate", "category", "status", "mode", "attestation", "times", "voices")
        return {"factId": fact_id, "subject": _brief(nodes[fact["source"]]), "object": _brief(nodes[fact["target"]]),
                **{k: fact[k] for k in keep}}

    @server.tool()
    def event_overview(event_id: str) -> dict[str, Any]:
        """What the graph holds about one event: counts by kind of thing, its phases, the Works
        that speak of it, and what awaits review (views/battle-overview.cypher, queries 1, 5, 10)."""
        event = graph.rows("MATCH (e:Entity {id: $id}) RETURN e.label AS label, e.kind AS kind", id=event_id)
        if not event:
            return {"error": f"No entity {event_id}. Use find_entities with kind Event."}
        summary = graph.rows(EVENT_SUMMARY, event=event_id, dead=DEAD)
        phases = graph.rows(EVENT_PHASES, event=event_id, dead=DEAD)
        sources = graph.rows(EVENT_SOURCES, event=event_id, dead=DEAD)
        queue = graph.rows(EVENT_QUEUE, event=event_id)
        return {"event": {"id": event_id, **event[0]}, "summary": summary, "phases": phases,
                "sources": sources, "awaitingReview": queue}

    @server.tool()
    def review_queue() -> dict[str, Any]:
        """The review queue as a whole: Proposals by who made them, their status, and what they propose."""
        return {"queue": graph.rows(REVIEW_QUEUE)}

    @server.tool()
    def graph_status() -> dict[str, Any]:
        """How big the graph is: nodes per core label, claims by status, Proposals by status."""
        return {
            "labels": graph.rows(LABEL_COUNTS),
            "claims": graph.rows("MATCH (a:Assertion) RETURN a.status AS status, count(*) AS n ORDER BY n DESC"),
            "proposals": graph.rows("MATCH (p:Proposal) RETURN p.status AS status, count(*) AS n ORDER BY n DESC"),
        }

    return server


LABEL_COUNTS = """
UNWIND ['Entity', 'Subject', 'Assertion', 'Proposal', 'SourceObservation', 'Annotation',
        'AuthorityRecord', 'Year', 'Location'] AS label
CALL (label) { MATCH (n:$(label)) RETURN count(n) AS n }
RETURN label, n
"""

EVENT_SUMMARY = """
MATCH (ev:Entity {id: $event})
CALL (ev) {
  MATCH (a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT|ASSERTION_CONTEXT]->(ev) WHERE NOT a.status IN $dead
  RETURN 'claims on the event' AS what, count(a) AS total, sum(CASE a.status WHEN 'accepted' THEN 1 ELSE 0 END) AS accepted
  UNION ALL
  MATCH (n:Entity)<-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]-(a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(ev)
  WHERE n <> ev AND NOT a.status IN $dead
  RETURN 'entities linked to it by a claim' AS what, count(DISTINCT n) AS total,
         count(DISTINCT CASE WHEN n.status IN ['provisional', 'resolved'] THEN n END) AS accepted
  UNION ALL
  MATCH (n:Annotation)-[:CONCERNS]->(ev)
  RETURN 'notes and passages of note on it' AS what, count(n) AS total,
         sum(CASE n.status WHEN 'endorsed' THEN 1 ELSE 0 END) AS accepted
  UNION ALL
  MATCH (ev)-[:HAS_AUTHORITY_RECORD]->(r:AuthorityRecord)
  RETURN 'authority records' AS what, count(r) AS total, count(r) AS accepted
}
RETURN what, total, accepted
"""

EVENT_PHASES = """
MATCH (ph:Entity)<-[:ASSERTION_SUBJECT]-(a:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(:Entity {id: $event})
WHERE ph.id STARTS WITH 'chr:entity:phase:' AND NOT a.status IN $dead
OPTIONAL MATCH (e:Entity)<-[:ASSERTION_SUBJECT]-(pl:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ph)
WHERE NOT pl.status IN $dead
RETURN ph.id AS id, coalesce(ph.shortLabel, ph.label) AS phase, a.status AS claim,
       count(e) AS eventsPlaced, ph.description AS description
ORDER BY phase
"""

# The event's neighbourhood as in views/battle-overview.cypher, found from the event outwards:
# its phases (partOf the event) and what is placed in them (partOf a phase).
EVENT_REACH = """
MATCH (ev:Entity {id: $event})
OPTIONAL MATCH (ph:Entity)-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ev)
OPTIONAL MATCH (x:Entity)<-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ph)
WITH ev, collect(DISTINCT ph) AS phases, collect(DISTINCT x) AS placed
"""

EVENT_SOURCES = EVENT_REACH + """
CALL (ev, placed) {
  CALL (ev, placed) {
    MATCH (a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT|ASSERTION_CONTEXT]->(ev) RETURN a
    UNION
    UNWIND placed AS x MATCH (a:Assertion)-[:ASSERTION_SUBJECT]->(x) RETURN a
  }
  CALL (a) {
    MATCH (a)-[:SUPPORTED_BY|PROPOSES_EVIDENCE]->(o:SourceObservation) RETURN o
    UNION
    MATCH (a)<-[:PROPOSES]-(:Proposal)-[:SUPPORTED_BY|PROPOSES_EVIDENCE]->(o:SourceObservation) RETURN o
  }
  RETURN collect(o) AS observed
}
CALL (ev) { MATCH (ev)<-[:CONCERNS]-(:Annotation)-[:ANNOTATES]->(o:SourceObservation) RETURN collect(o) AS noted }
UNWIND observed + noted AS o
MATCH (o)-[:IN_WORK]->(w:Entity {kind: 'Work'})
WITH w, count(DISTINCT o) AS passages
OPTIONAL MATCH (a:Assertion)-[:ATTRIBUTED_TO]->(w) WHERE NOT a.status IN $dead
RETURN w.id AS id, w.label AS work, w.form AS form, w.status AS status, passages, count(DISTINCT a) AS claimsAttributed
ORDER BY passages DESC
"""

EVENT_QUEUE = EVENT_REACH + """
CALL (ev, phases, placed) {
  MATCH (a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT|ASSERTION_CONTEXT]->(ev) RETURN a
  UNION
  UNWIND placed AS x MATCH (a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(x) RETURN a
  UNION
  UNWIND phases AS ph MATCH (a:Assertion)-[:ASSERTION_OBJECT]->(ph) RETURN a
}
MATCH (p:Proposal {status: 'submitted'})-[:PROPOSES]->(a)
RETURN p.createdBy AS proposedBy, a.predicate AS predicate, count(*) AS waiting
ORDER BY proposedBy, waiting DESC
"""

REVIEW_QUEUE = """
MATCH (p:Proposal)-[:PROPOSES]->(a:Assertion)
WITH coalesce(p.createdBy, '?') AS createdBy, a.predicate AS predicate, p.status AS status, count(*) AS n
ORDER BY n DESC
WITH createdBy, status, sum(n) AS proposals, collect(predicate + ' ' + n) AS byPredicate
RETURN createdBy, status, proposals, byPredicate[..8] AS topPredicates
ORDER BY status DESC, proposals DESC
"""


def new_token() -> int:
    if mcp_token():
        print("Connections.txt already has an MCP token; remove its line first to replace it.")
        return 1
    with CONNECTIONS.open("a", encoding="utf-8") as handle:
        handle.write(f"\nmcp token is {secrets.token_urlsafe(32)}\n")
    print(f"Token written to {CONNECTIONS} (not shown).")
    return 0


CLOUDFLARED_PATHS = [r"C:\Program Files (x86)\cloudflared\cloudflared.exe", r"C:\Program Files\cloudflared\cloudflared.exe"]


def start_quick_tunnel(port: int, wait: float = 60) -> str:
    """Start `cloudflared tunnel --url`, stopped when this process exits; return its trycloudflare host."""
    exe = shutil.which("cloudflared") or next((p for p in CLOUDFLARED_PATHS if Path(p).exists()), None)
    if not exe:
        raise SystemExit("cloudflared not found: install it (winget install Cloudflare.cloudflared).")
    tunnel = subprocess.Popen([exe, "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{port}"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    atexit.register(tunnel.terminate)
    found: list[str] = []
    ready = threading.Event()

    def drain() -> None:  # cloudflared logs to stderr; keep reading so it never blocks
        for line in tunnel.stderr:
            match = re.search(r"https://([a-z0-9-]+\.trycloudflare\.com)", line)
            if match and not found:
                found.append(match.group(1))
                ready.set()

    threading.Thread(target=drain, daemon=True).start()
    if not ready.wait(wait):
        tunnel.terminate()
        raise SystemExit(f"cloudflared gave no address within {wait:.0f}s.")
    return found[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--http", action="store_true", help="serve over HTTP for claude.ai (behind a tunnel)")
    parser.add_argument("--tunnel", action="store_true", help="--http behind a Cloudflare quick tunnel; prints the URL")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--public-host", default=os.environ.get("CHRYSTALLUM_MCP_PUBLIC_HOST"),
                        help="the tunnel's host name, e.g. chrystallum.example.org")
    parser.add_argument("--show-url", action="store_true", help="print the connector URL, token included")
    parser.add_argument("--new-token", action="store_true", help="write a new MCP token to Connections.txt")
    args = parser.parse_args(argv)
    if args.new_token:
        return new_token()
    graph = Graph()
    if not (args.http or args.tunnel):
        build_server(graph).run("stdio")
        return 0

    from mcp.server.transport_security import TransportSecuritySettings

    token = mcp_token()
    if not token:
        raise SystemExit("No MCP token: run with --new-token first (it goes in Connections.txt).")
    if args.tunnel:
        args.public_host, args.show_url = start_quick_tunnel(args.port), True
    hosts = ["127.0.0.1:*", "localhost:*"] + ([args.public_host] if args.public_host else [])
    server = build_server(
        graph, host="127.0.0.1", port=args.port, streamable_http_path=f"/mcp/{token}", stateless_http=True,
        transport_security=TransportSecuritySettings(allowed_hosts=hosts, allowed_origins=["https://claude.ai"]),
    )
    base = f"https://{args.public_host}" if args.public_host else f"http://127.0.0.1:{args.port}"
    shown = token if args.show_url else "<token from Connections.txt>"
    print(f"Chrystallum connector on http://127.0.0.1:{args.port}; connector URL: {base}/mcp/{shown}", file=sys.stderr)
    server.run("streamable-http")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
