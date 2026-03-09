# Geo Agent — Delta Schema

**Purpose:** Structured output format for the Geo Agent classification pass. The LLM returns JSON deltas; the Python delta applier validates and applies them to Neo4j.

---

## Pipeline Position

```
geo_backlink_discovery.py  →  Geo Agent (LLM)  →  Delta Applier (Python)  →  Neo4j
     (gather)                    (classify)              (write)
```

---

## Output Wrapper

```json
{
  "seed_qid": "Q17167",
  "candidates": [
    {
      "qid": "Q23725",
      "label": "Byzantium",
      "classification": "place_core",
      "deltas": [ ... ]
    }
  ]
}
```

| Field | Type | Description |
|-------|------|--------------|
| `seed_qid` | string | Domain QID (e.g. Q17167) |
| `candidates` | array | One entry per input candidate with classification and deltas |

---

## Classifications

| Value | Meaning |
|-------|---------|
| `place_core` | Settlement, city, province, region (v1_core) |
| `place_noncore` | Natural feature (river, mountain, sea); deferred for v1 |
| `event` | Battle, siege, war, mutiny, eruption, coup, etc. |
| `other` | Ignore for geography |

---

## Delta Types

### CREATE_OR_ENRICH_PLACE

Create a new Place node or enrich an existing one. Keyed by `pleiades_id`, `geonames_id`, or `qid`.

```json
{
  "op_type": "CREATE_OR_ENRICH_PLACE",
  "place_key": {
    "pleiades_id": "520985",
    "geonames_id": null
  },
  "source_qid": "Q23725",
  "properties": {
    "label": "Byzantium",
    "qid": "Q23725",
    "pleiades_id": "520985",
    "geonames_id": null,
    "centroid_lat": 41.013,
    "centroid_lng": 28.984,
    "base_type_hint": ["ancient city", "polis"]
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `op_type` | yes | `"CREATE_OR_ENRICH_PLACE"` |
| `place_key` | yes | At least one of `pleiades_id`, `geonames_id`; or omit both and use `source_qid` as key |
| `source_qid` | yes | Wikidata QID of the source item |
| `properties` | yes | Place properties to set |

**place_key precedence:** pleiades_id > geonames_id > qid (when no external IDs)

**properties:** `label`, `qid`, `pleiades_id`, `geonames_id`, `centroid_lat`, `centroid_lng`, `base_type_hint` (array of instance_of labels)

---

### ATTACH_EVENT_TO_PLACE

Record an Event→Place relationship. Does **not** create a Place. For Event Agent later.

```json
{
  "op_type": "ATTACH_EVENT_TO_PLACE",
  "event_qid": "Q60524412",
  "place_qid": "Q11045304",
  "place_label": "Lauro",
  "relation_type": "OCCURRED_AT"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `op_type` | yes | `"ATTACH_EVENT_TO_PLACE"` |
| `event_qid` | yes | Wikidata QID of the event |
| `place_qid` | yes | Wikidata QID of the place (from P276 or similar) |
| `place_label` | no | Human-readable place label |
| `relation_type` | yes | `"OCCURRED_AT"` |

---

## Delta Applier Behavior

### CREATE_OR_ENRICH_PLACE

1. **Lookup:** Check if Place exists by `pleiades_id` or `geonames_id` (or `qid` if no external IDs).
2. **If exists:** MERGE/SET properties (add qid, coords, base_type_hint).
3. **If not:** CREATE new Place node with properties.
4. **Invariants:** place_scope = 'v1_core' for place_core; validate IDs before write.

### ATTACH_EVENT_TO_PLACE

1. **Store:** Record event_qid → place_qid for Event Agent.
2. **No Place creation:** Do not create Place nodes from this delta.
3. **Optional:** Create Event stub or edge if Event model exists.

---

## Related

- `md/Agents/geo_agent_classification_prompt.md` — Prompt for Geo Agent
- `scripts/agents/geo/README.md` — Geo Agent overview
- `docs/GEO_AGENT_REVIEW.md` — Design document
