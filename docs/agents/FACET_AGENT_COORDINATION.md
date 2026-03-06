# Facet Agent Coordination

**Purpose:** Lightweight protocol for multiple facet agents sharing disciplines without duplicate harvest work.

---

## Context

- A **discipline** (e.g. Q830852, history of ancient Rome) can be primary for multiple **facets** (Biographic, Spatial, etc.).
- Each facet agent may want to harvest the same discipline from the same repo.
- We avoid duplicate harvests by treating `HarvestJob.status` as a lock.

---

## Protocol

1. **Claim:** When discipline X is primary for facets A, B, C, the first agent to claim a harvest job for `(X, facet, repo_key)` sets `status` to `running`. Others skip that job or wait.

2. **Lock semantics:** `status: "running"` means the job is locked. Only the agent that set it should complete or fail it.

3. **Completion:** When done, the claiming agent sets `status` to `completed` or `failed`.

4. **Idempotency:** Job creation is idempotent — same `(discipline_qid, facet_label, repo_key)` yields the same logical job. Agents should not create duplicates.

---

## Implementation Notes

### File-based (current)

- Jobs live in `output/facet_harvest_jobs/{facet_label}/jobs.jsonl`.
- To claim: read file, find first `pending` job, update to `running`, rewrite file. Use file locking or single-process assumption to avoid races.
- For multi-process: consider a `claim_next_pending_job(facet_label)` that does atomic read-modify-write.

### Neo4j (future)

- `(Discipline)-[:HARVEST_JOB]->(HarvestJob)-[:FOR_FACET]->(CanonicalFacet)`
- Claim via Cypher: `MATCH (j:HarvestJob {status: 'pending'}) ... SET j.status = 'running', j.claimed_by = $agent_id RETURN j`
- Use `SET j.status = 'running'` with a `WHERE j.status = 'pending'` to avoid races.

---

## Coordination Rules

| Scenario | Action |
|----------|--------|
| Agent A sees pending job for (X, Biographic, OPENALEX) | Claim it; set status = running |
| Agent B sees same job, status = running | Skip; move to next job or discipline |
| Agent A finishes | Set status = completed or failed |
| Same (X, facet, repo) created twice | Idempotent: same job_id; append-only prevents overwrite |

---

## Optional: needs_harvest_per_facet

Deferred. If needed later, add `needs_harvest_per_facet` on Discipline as a JSON map `{ "Biographic": true, "Spatial": false }` to scope harvest needs per facet.
