# Harvest Job Schema

**Purpose:** Canonical schema for harvest jobs emitted by facet agents. Jobs are stored as JSONL in `output/facet_harvest_jobs/{facet_label}/jobs.jsonl`.

**Implementation:** `scripts/agents/facet_console/harvest_job.py`

---

## JSON Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `job_id` | string (UUID) | yes | Unique job identifier |
| `discipline_qid` | string | yes | Wikidata QID of the discipline (e.g. `Q830852`) |
| `discipline_label` | string | yes | Human-readable discipline name |
| `facet_label` | string | yes | Facet name (e.g. `Biographic`, `Spatial`) |
| `repo_key` | string | yes | Key into `REPOS_TEMPLATES` (e.g. `OPENALEX_WORKS`, `PERSEUS`) |
| `url` | string | yes | Resolved harvest URL |
| `status` | enum | yes | `pending` \| `running` \| `completed` \| `failed` |
| `created_at` | string (ISO8601) | yes | Creation timestamp |
| `completed_at` | string (ISO8601) \| null | no | Completion timestamp |
| `campaign_id` | string \| null | no | Optional campaign grouping |

### Example

```json
{
  "job_id": "7f14d5d6-4fed-458b-a01e-f0674117e053",
  "discipline_qid": "Q830852",
  "discipline_label": "history of ancient Rome",
  "facet_label": "Biographic",
  "repo_key": "OPENALEX_WORKS",
  "url": "https://api.openalex.org/works?filter=concepts.id:C2779756987&sort=cited_by_count:desc&per_page=25",
  "status": "pending",
  "created_at": "2026-03-05T14:48:50.218651Z",
  "completed_at": null,
  "campaign_id": null
}
```

---

## Storage

- **Path:** `output/facet_harvest_jobs/{facet_label}/jobs.jsonl`
- **Format:** One JSON object per line (JSONL)
- **Idempotency:** Same `(discipline_qid, facet_label, repo_key)` yields deterministic job_id via append-only; no overwrite.

---

## Status Lifecycle

```
pending → running → completed
                 → failed
```

- **pending:** Job created, not yet claimed
- **running:** Agent has claimed the job; others should skip or wait
- **completed:** Harvest finished successfully
- **failed:** Harvest failed (error details may be in metadata)

---

## Coordination

See [FACET_AGENT_COORDINATION.md](./FACET_AGENT_COORDINATION.md) for the protocol when multiple facet agents share disciplines.
