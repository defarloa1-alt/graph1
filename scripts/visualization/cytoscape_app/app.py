#!/usr/bin/env python3
"""
Chrystallum cytoscape.js Graph Viewer — FastAPI backend

Parameterised endpoints only — no raw Cypher accepted from the client.
Neo4j credentials stay server-side via config_loader / env vars.
Read-only queries only.

Endpoints:
    GET /                       → HTML viewer
    GET /api/person/{entity_id} → Ego subgraph (person + N hops)
    GET /api/gens/{prefix}      → All members of a gens via MEMBER_OF_GENS
    GET /api/family/{entity_id} → Family tree (depth-limited)
    GET /api/offices/{entity_id}→ Person + POSITION_HELD
    GET /api/search?q=...       → Label search (parameterised CONTAINS)
    GET /api/stats               → Graph summary statistics

Usage:
    cd scripts/visualization/cytoscape_app
    uvicorn app:app --reload --port 8765
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root / "scripts"))

from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from neo4j import GraphDatabase

# ---------------------------------------------------------------------------
# Neo4j connection (read-only session)
# ---------------------------------------------------------------------------

_driver = None

NODE_CAP = 2000
FAMILY_DEPTH = 3


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _driver
    _driver = GraphDatabase.driver(
        NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    _driver.verify_connectivity()
    yield
    _driver.close()


app = FastAPI(title="Chrystallum Graph Viewer", lifespan=lifespan)
app.mount("/static", StaticFiles(
    directory=Path(__file__).parent / "static"), name="static")


def _session():
    return _driver.session(database=NEO4J_DATABASE)


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _node_to_cyto(node) -> dict:
    """Convert a Neo4j node to cytoscape.js element format."""
    props = dict(node)
    nid = (props.get("entity_id")
           or props.get("gens_id")
           or props.get("praenomen_id")
           or props.get("nomen_id")
           or props.get("cognomen_id")
           or props.get("tribe_id")
           or props.get("polity_id")
           or str(node.element_id))
    labels = ",".join(sorted(node.labels))
    display = (props.get("label")
               or props.get("label_latin")
               or props.get("label_en")
               or nid)
    return {
        "group": "nodes",
        "data": {
            "id": str(nid),
            "label": str(display),
            "node_labels": labels,
            **{k: _safe(v) for k, v in props.items()},
        },
    }


def _edge_to_cyto(src: str, tgt: str, rel_type: str,
                   props: dict = None) -> dict:
    """Convert to cytoscape.js edge element."""
    data = {
        "id": f"{src}__{rel_type}__{tgt}",
        "source": str(src),
        "target": str(tgt),
        "rel_type": rel_type,
    }
    if props:
        for k, v in props.items():
            if v is not None:
                data[k] = _safe(v)
    return {"group": "edges", "data": data}


def _safe(v):
    if v is None:
        return None
    if isinstance(v, (int, float, bool)):
        return v
    return str(v)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/api/stats")
async def stats():
    """Graph summary statistics."""
    with _session() as s:
        counts = {}
        for lbl in ["Person", "Gens", "Praenomen", "Nomen", "Cognomen",
                     "Tribe", "Position", "Place", "Pleiades_Place",
                     "Periodo_Period"]:
            r = s.run(f"MATCH (n:{lbl}) RETURN count(n) AS c")
            counts[lbl] = r.single()["c"]
        r = s.run("MATCH ()-[r]->() RETURN count(r) AS c")
        counts["total_edges"] = r.single()["c"]
    return counts


@app.get("/api/person/{entity_id}")
async def person_ego(entity_id: str, hops: int = Query(default=1, ge=1, le=3)):
    """Ego subgraph around a Person node, up to `hops` hops (max 3)."""
    elements = []
    seen_nodes = set()
    with _session() as s:
        result = s.run(
            "MATCH path = (p:Person {entity_id: $eid})-[*1.." + str(hops) + "]-(m) "
            "WITH p, m, relationships(path) AS rels "
            "UNWIND rels AS r "
            "WITH p, m, r, startNode(r) AS sn, endNode(r) AS en "
            "RETURN DISTINCT p, m, type(r) AS rel, properties(r) AS rp, "
            "  COALESCE(sn.entity_id, sn.gens_id, sn.praenomen_id, "
            "           sn.nomen_id, sn.cognomen_id, sn.tribe_id) AS src, "
            "  COALESCE(en.entity_id, en.gens_id, en.praenomen_id, "
            "           en.nomen_id, en.cognomen_id, en.tribe_id) AS tgt "
            "LIMIT $cap",
            eid=entity_id, cap=NODE_CAP,
        )
        for rec in result:
            for node in [rec["p"], rec["m"]]:
                nid = _node_to_cyto(node)["data"]["id"]
                if nid not in seen_nodes:
                    seen_nodes.add(nid)
                    elements.append(_node_to_cyto(node))
            elements.append(_edge_to_cyto(
                rec["src"], rec["tgt"], rec["rel"], rec["rp"]))
    if not elements:
        raise HTTPException(404, f"Person {entity_id} not found")
    return {"elements": elements}


@app.get("/api/gens/{prefix}")
async def gens_members(prefix: str):
    """All persons in a gens, via MEMBER_OF_GENS -> Gens(gens_id=prefix)."""
    prefix_upper = prefix.upper()
    elements = []
    seen = set()
    with _session() as s:
        result = s.run(
            "MATCH (p:Person)-[r:MEMBER_OF_GENS]->(g:Gens {gens_id: $gid}) "
            "RETURN p, g, properties(r) AS rp "
            "LIMIT $cap",
            gid=prefix_upper, cap=NODE_CAP,
        )
        gens_node = None
        for rec in result:
            if gens_node is None:
                gens_node = rec["g"]
                gdata = _node_to_cyto(gens_node)
                seen.add(gdata["data"]["id"])
                elements.append(gdata)
            pdata = _node_to_cyto(rec["p"])
            pid = pdata["data"]["id"]
            if pid not in seen:
                seen.add(pid)
                elements.append(pdata)
            elements.append(_edge_to_cyto(
                pid, gdata["data"]["id"], "MEMBER_OF_GENS", rec["rp"]))
    if not elements:
        raise HTTPException(404, f"Gens '{prefix_upper}' not found")
    return {"elements": elements}


@app.get("/api/family/{entity_id}")
async def family_tree(entity_id: str,
                      depth: int = Query(default=FAMILY_DEPTH, ge=1, le=5)):
    """Family tree rooted at a person, depth-limited (max 5 generations)."""
    elements = []
    seen = set()
    with _session() as s:
        result = s.run(
            "MATCH path = (root:Person {entity_id: $eid})"
            "-[:FATHER_OF|MOTHER_OF|SPOUSE_OF|SIBLING_OF|CHILD_OF*1.."
            + str(depth) + "]-(m:Person) "
            "WITH root, m, relationships(path) AS rels "
            "UNWIND rels AS r "
            "WITH root, m, r, startNode(r) AS sn, endNode(r) AS en "
            "RETURN DISTINCT root, m, type(r) AS rel, properties(r) AS rp, "
            "  sn.entity_id AS src, en.entity_id AS tgt "
            "LIMIT $cap",
            eid=entity_id, cap=NODE_CAP,
        )
        for rec in result:
            for node in [rec["root"], rec["m"]]:
                nd = _node_to_cyto(node)
                nid = nd["data"]["id"]
                if nid not in seen:
                    seen.add(nid)
                    elements.append(nd)
            elements.append(_edge_to_cyto(
                rec["src"], rec["tgt"], rec["rel"], rec["rp"]))
    if not elements:
        raise HTTPException(404, f"Person {entity_id} not found")
    return {"elements": elements}


@app.get("/api/offices/{entity_id}")
async def person_offices(entity_id: str):
    """Person + all POSITION_HELD edges (with temporal properties)."""
    elements = []
    seen = set()
    with _session() as s:
        result = s.run(
            "MATCH (p:Person {entity_id: $eid})-[r:POSITION_HELD]->(pos:Position) "
            "RETURN p, pos, properties(r) AS rp",
            eid=entity_id,
        )
        root = None
        for rec in result:
            if root is None:
                root = rec["p"]
                rd = _node_to_cyto(root)
                seen.add(rd["data"]["id"])
                elements.append(rd)
            pd = _node_to_cyto(rec["pos"])
            pid = pd["data"]["id"]
            if pid not in seen:
                seen.add(pid)
                elements.append(pd)
            elements.append(_edge_to_cyto(
                rd["data"]["id"], pid, "POSITION_HELD", rec["rp"]))
    if not elements:
        raise HTTPException(404, f"Person {entity_id} not found or has no offices")
    return {"elements": elements}


@app.get("/api/search")
async def search_persons(q: str = Query(..., min_length=2, max_length=100),
                         limit: int = Query(default=50, ge=1, le=200)):
    """Search persons by label (parameterised CONTAINS — no Cypher injection)."""
    with _session() as s:
        result = s.run(
            "MATCH (p:Person) "
            "WHERE toLower(p.label) CONTAINS toLower($term) "
            "   OR toLower(p.label_latin) CONTAINS toLower($term) "
            "   OR p.dprr_id = $term "
            "RETURN p "
            "ORDER BY p.label "
            "LIMIT $lim",
            term=q, lim=limit,
        )
        persons = []
        for rec in result:
            node = rec["p"]
            props = dict(node)
            persons.append({
                "entity_id": props.get("entity_id"),
                "label": props.get("label"),
                "label_latin": props.get("label_latin"),
                "dprr_id": props.get("dprr_id"),
                "gens_prefix": props.get("label_dprr", "")[:4] if props.get("label_dprr") else None,
            })
    return {"results": persons, "count": len(persons)}
