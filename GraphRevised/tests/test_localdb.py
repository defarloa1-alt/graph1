"""The local-only guard (47 §5.1): every connection goes through GraphRevised.localdb."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from GraphRevised import localdb

GRAPH_REVISED = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("uri", ["neo4j://127.0.0.1:7687", "bolt://localhost:7687", "neo4j://[::1]:7687"])
def test_local_addresses_pass(uri):
    assert localdb.check_uri(uri) == uri


@pytest.mark.parametrize("uri", [
    "neo4j+s://abcd1234.databases.neo4j.io",  # Aura
    "neo4j+ssc://127.0.0.1:7687",
    "bolt://10.0.0.5:7687",
    "neo4j://example.org:7687",
    "neo4j://neo4j:secret@127.0.0.1:7687",  # credentials in the address
    "http://127.0.0.1:7474",
    "",
])
def test_other_addresses_refused(uri):
    with pytest.raises(localdb.NotLocal):
        localdb.check_uri(uri)


@pytest.mark.parametrize("name", ["system", "chrystallum", "Neo4j", ""])
def test_other_databases_refused(name):
    with pytest.raises(localdb.NotLocal):
        localdb.check_database(name)


def test_environment_is_checked(monkeypatch):
    monkeypatch.setenv("NEO4J_URI", "neo4j+s://abcd1234.databases.neo4j.io")
    with pytest.raises(localdb.NotLocal):
        localdb.uri()
    with pytest.raises(localdb.NotLocal):
        localdb.driver()
    monkeypatch.delenv("NEO4J_URI")
    assert localdb.uri() == localdb.DEFAULT_URI
    monkeypatch.setenv("NEO4J_DATABASE", "system")
    with pytest.raises(localdb.NotLocal):
        localdb.database()


def test_local_config_uses_the_guard(monkeypatch):
    from scripts import config_loader
    from GraphRevised.subject_backbone import local_config

    monkeypatch.setattr(config_loader, "NEO4J_URI", "neo4j+s://abcd1234.databases.neo4j.io")
    with pytest.raises(localdb.NotLocal):
        local_config()


READS = re.compile(r"""(environ(\.get)?\(?\[?|getenv\()\s*["']NEO4J_(URI|DATABASE)["']""")


def test_no_module_reads_the_address_itself():
    """Only localdb reads NEO4J_URI and NEO4J_DATABASE from the environment."""
    offenders = [
        f"{path.relative_to(GRAPH_REVISED)}:{n}"
        for path in GRAPH_REVISED.rglob("*.py")
        if path.name != "localdb.py" and "__pycache__" not in path.parts
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if READS.search(line)
    ]
    assert not offenders, offenders
