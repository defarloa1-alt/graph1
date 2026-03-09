# Geo Agent

LLM classification pass for geo backlink candidates. Script gathers; Geo Agent reasons; Delta Applier writes.

---

## Pipeline

| Step | Component | Role |
|------|-----------|------|
| 1 | `geo_backlink_discovery.py` | Gather backlinks, filter by geo properties; output JSON bundle |
| 2 | **Geo Agent (LLM)** | Classify candidates (place_core, place_noncore, event, other); propose deltas |
| 3 | Delta Applier (Python) | Apply CREATE_OR_ENRICH_PLACE to Neo4j |
| 4 | Event Agent (later) | Consume ATTACH_EVENT_TO_PLACE deltas |

---

## Input

JSON from `geo_backlink_discovery.py`:

```json
{
  "seed": {"qid": "Q17167", "label": "Roman Republic"},
  "candidates": [
    {
      "qid": "Q23725",
      "label": "Byzantium",
      "instance_of": [{"qid": "Q15661340", "label": "ancient city"}, {"qid": "Q148837", "label": "polis"}],
      "subclass_of": [],
      "geo_properties": [
        {"pid": "P1584", "label": "Pleiades ID", "value": "520985"},
        {"pid": "P625", "label": "coordinate location", "value": "41.013, 28.984"}
      ]
    }
  ]
}
```

---

## Output

Classification + deltas JSON. See `md/Agents/geo_agent_classification_prompt.md` for full schema.

---

## Prompt

Use `md/Agents/geo_agent_classification_prompt.md` as the Geo Agent prompt. Pass the discovery JSON as input; expect JSON-only output.

---

## Delta Types

- **CREATE_OR_ENRICH_PLACE** — Place node keyed by pleiades_id, geonames_id, or qid
- **ATTACH_EVENT_TO_PLACE** — Event→Place relationship (OCCURRED_AT); for Event Agent later
