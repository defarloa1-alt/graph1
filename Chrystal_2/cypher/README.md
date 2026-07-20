# Chrystal_2 / cypher

Home for **Chrystal 2–only** Cypher (verify snippets, one-off fixes, future migrations).

- Prefer Python CLIs under `agents/` / `bootstrap/` for writes (registry-gated, instance lock).
- Do **not** drop C2 cypher into repo-root `claude/`, `migrations/`, or production `scripts/neo4j/` unless it is deliberately shared — and then link it from [`../INDEX.md`](../INDEX.md).

Empty for now: Domain work has been Python-driven. Add `.cypher` files here when needed.
