"""The one way GraphRevised code reaches Neo4j: the local clean-start database only.

    from GraphRevised import localdb
    driver = GraphDatabase.driver(localdb.uri(), auth=localdb.auth())
    with driver.session(database=localdb.database()) as session: ...

The address comes from NEO4J_URI (default neo4j://127.0.0.1:7687) and the
database from NEO4J_DATABASE (default neo4j), as before, but both are checked
on every read: a non-local address (Aura or any other server), credentials in
the address, or a database other than `neo4j` is refused before a driver is
made. This is the guard that keeps a write from reaching anything but the local
graph (47 §5.1). No module outside this one reads NEO4J_URI or NEO4J_DATABASE
(tests/test_localdb.py).
"""

from __future__ import annotations

import os
from urllib.parse import urlparse

DEFAULT_URI = "neo4j://127.0.0.1:7687"
DATABASE = "neo4j"
SCHEMES = frozenset({"neo4j", "bolt"})
HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


class NotLocal(ValueError):
    """A connection setting that points anywhere but the local clean-start database."""


def check_uri(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in SCHEMES or parsed.hostname not in HOSTS or parsed.username or parsed.password:
        raise NotLocal(f"Refused: Neo4j address {parsed.scheme}://{parsed.hostname} is not the local "
                       "neo4j:// or bolt:// database (127.0.0.1, localhost or ::1, no credentials in the address).")
    return value


def check_database(value: str) -> str:
    if value != DATABASE:
        raise NotLocal(f"Refused: database {value!r} is not the clean-start database {DATABASE!r}.")
    return value


def uri(default: str = DEFAULT_URI) -> str:
    return check_uri(os.environ.get("NEO4J_URI", default))


def database(default: str = DATABASE) -> str:
    return check_database(os.environ.get("NEO4J_DATABASE", default))


def auth() -> tuple[str, str]:
    """(user, password); a missing NEO4J_PASSWORD raises KeyError, as the scripts always did."""
    return os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]


def driver(**kwargs):
    from neo4j import GraphDatabase

    return GraphDatabase.driver(uri(), auth=auth(), **kwargs)
