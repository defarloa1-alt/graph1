# Wikidata Derived Artifacts

Runtime-consumable indexes built from raw Wikidata exports in `statements/` and `backlinks/`.

## Seed Knowledge Index

**Producer:** `scripts/tools/wikidata_build_seed_index.py`

**Output:** `<QID>_seed_index.json`

**Consumers:**
- `scripts/agents/domain_initiator/candidate_qids.py` — candidate QID validation gate
- `scripts/agents/domain_initiator/propose.py` — auto-builds index if missing

### Build

```bash
python scripts/tools/wikidata_build_seed_index.py --qid Q17167 --fetch-labels
```

### Contents

| Section | Purpose |
|---------|---------|
| `period` | P580/P582 from seed P31 (509–27 BC for Roman Republic) |
| `authority_ids` | P244, P2163, etc. from seed statements |
| `events`, `parts`, `legislative_bodies` | Direct Wikidata structure on seed |
| `accepted_neighbors` | Datatype-gated backlink frontier (150 for Q17167) |
| `allowed_candidate_qids.union` | Whitelist for DI candidate QID validation |
| `facet_signals` | Backlink property → facet routing hints |

Refresh when statements or backlink harvest are updated.
