# TaxonomyHarvester Agent — Specification

**Status:** Draft 2026-03-01
**Author:** Architecture session
**Role in pipeline:** Phase A sub-agent, called by SCA before LLM reasoning

---

## 1. Purpose

The TaxonomyHarvester is a domain-agnostic Wikidata traversal agent.
It takes any seed QID and maps the **classificatory neighborhood** — the abstract ontological structure that situates the entity in the knowledge/library/discipline hierarchy.

It does NOT know about Roman Republic. It knows about P31, P279, P361, authority IDs, and stopping rules.

The SCA uses its output as structured input to LLM reasoning. The 18 SFAs ignore it entirely — they operate in domain content space, not classification space.

---

## 2. What It Traverses (and What It Does Not)

### In scope — hierarchical/classificatory relationships:

| Direction | PIDs | Semantics |
|-----------|------|-----------|
| UP | P31 (instance of), P279 (subclass of), P361 (part of) | "What kind of thing is this?" |
| DOWN | P527 (has parts), P150 (contains administrative) | "What does it contain taxonomically?" |
| SUCCESSION | P155 (follows), P156 (followed by) | "What is adjacent in time at same level?" |

### Out of scope — lateral/domain content:

| PIDs | Handled by |
|------|-----------|
| P36 (capital), P793 (significant events), P194 (legislative body), P38 (currency) | Lateral Explorer |
| P31 backlinks via Ancient Rome → emperors, authors, places | SFAs |
| P1792 (people category) | SFAs |

**The TaxonomyHarvester climbs the abstraction stack. It stops before the meta-ontological ceiling. Everything below the ceiling is a candidate node.**

---

## 3. Stopping Rule — Authority Signal Tiers

The traversal stops at a node when that node has **no authority IDs at all** (pure meta-ontological scaffolding — Wikidata structural nodes with no library/academic footprint).

### Tier definitions:

| Tier | PIDs | Behavior |
|------|------|----------|
| **PRIMARY** | P2163 (FAST), P1149 (LCC), P8814 (Nomisma), P9842 (PACTOLS), P1584 (Pleiades) | Continue traversal. Strong subject candidate. Tag `tier=primary`. |
| **SECONDARY** | P244 (LCSH), P227 (GND), P268 (BnF) | Include as candidate but **STOP traversal** from this node. Tag `tier=secondary`. These authorities are too broad (have records for "aptitude", "abstract noun", "spacetime"). |
| **META** | No authority IDs at all | **STOP and EXCLUDE** — these are pure ontological scaffolding (class, type, metaclass, second-order class, formal ontology concept, variable-order class, scheme). Tag `tier=meta`, include in output as `traversal_boundary=true`. |

**Why LCSH/GND/BnF are secondary, not primary:**
Roman Kingdom (LCSH-only) is more domain-relevant than `ontology` (FAST+LCC). Rules cannot distinguish; LLM reasoning can. Secondary nodes are candidates but don't drive traversal deeper.

### Known meta-ceiling nodes (from Q17167 run, 47 total):

`class`, `type`, `second-order class`, `metaclass`, `variable-order class`, `formal ontology concept`, `scheme`, `universal class`, `abstract object` — these reliably appear at the top of any Wikidata taxonomy traversal. Future runs will encounter them again; the harvester caches by QID.

---

## 4. Input / Output

### Input:
```python
{
    "seed_qid": "Q17167",          # Any Wikidata entity QID
    "max_hops": 5,                  # Default 5 (2 is too shallow for rich taxonomy)
    "sleep_between_fetches": 1.5,   # Seconds — required to avoid 429 from Wikidata
    "cache_dir": "output/taxonomy_cache/"  # Shared across runs — reuses known nodes
}
```

### Output — per-node record:
```python
{
    "qid": "Q11514315",
    "label": "historical period",
    "tier": "primary",              # primary | secondary | meta
    "traversal_boundary": false,    # true if traversal stopped here
    "authority_ids": {
        "FAST": "1235743",
        "LCC": "D11"
    },
    "reached_via": [
        {"from_qid": "Q17167", "via_pid": "P31", "direction": "up", "hop": 1}
    ],
    "hop_depth": 1
}
```

### Output — full harvest:
```python
{
    "seed_qid": "Q17167",
    "seed_label": "Roman Republic",
    "harvested_at": "2026-03-01T22:18:00Z",
    "max_hops": 5,
    "summary": {
        "total_entities": 100,
        "primary_count": 15,      # FAST/LCC/domain-specific present
        "secondary_count": 27,    # LCSH/GND/BnF only
        "meta_count": 47,         # No authority IDs — traversal boundary
        "boundary_nodes": 47
    },
    "entities": [...],            # List of per-node records above
    "relationships": [...]        # List of {from_qid, to_qid, pid, direction, hop}
}
```

---

## 5. Algorithm

```
function harvest(seed_qid, max_hops, cache):
    queue = [(seed_qid, 0)]           # (qid, current_hop)
    visited = set()
    nodes = {}
    rels = []

    while queue:
        qid, hop = queue.pop()
        if qid in visited: continue
        visited.add(qid)

        entity = fetch_wikidata_entity(qid)   # fetch ALL properties
        sleep(1.5)                             # rate limit

        authority_tier = classify_authority(entity)
        nodes[qid] = build_node_record(entity, authority_tier, hop)

        if authority_tier == "meta":
            nodes[qid]["traversal_boundary"] = true
            continue                           # STOP — do not expand further

        if authority_tier == "secondary":
            nodes[qid]["traversal_boundary"] = true
            continue                           # STOP — include but don't expand

        # PRIMARY or SEED — continue traversal
        if hop < max_hops:
            for pid in [P31, P279, P361]:      # UP
                targets = entity.get_values(pid)
                for t in targets:
                    rels.append({from: qid, to: t, pid: pid, dir: "up", hop: hop+1})
                    queue.append((t, hop+1))

            for pid in [P527, P150]:           # DOWN
                targets = entity.get_values(pid)
                for t in targets:
                    rels.append({from: qid, to: t, pid: pid, dir: "down", hop: hop+1})
                    queue.append((t, hop+1))

            for pid in [P155, P156]:           # SUCCESSION
                targets = entity.get_values(pid)
                for t in targets:
                    rels.append({from: qid, to: t, pid: pid, dir: "succession", hop: hop+1})
                    queue.append((t, hop+1))

    return build_output(seed_qid, nodes, rels)
```

---

## 6. Caching Strategy

Cross-run caching is important for two reasons:
1. Meta-ceiling nodes reappear across domains (form_of_government, republic, ancient civilization appear for Ancient Greece just as for Roman Republic)
2. Wikidata rate limiting makes re-fetching expensive

### Cache schema (`output/taxonomy_cache/{qid}.json`):
```python
{
    "qid": "Q1307214",
    "label": "form of government",
    "fetched_at": "2026-02-20T13:57:00Z",
    "tier": "secondary",
    "authority_ids": {"LCSH": "sh85053104"},
    "all_properties": {...}    # Full Wikidata property dump
}
```

On harvest, check cache first. Only fetch from Wikidata if cache miss or cache older than `max_age_days` (default 30).

---

## 7. Relationship to Existing Scripts

| Existing script | Problem | TaxonomyHarvester replacement |
|-----------------|---------|-------------------------------|
| `wikidata_recursive_taxonomy.py` | No authority-signal stopping rule, no sleep, 5-hop hard limit, no tiering, no cache | Replace with TaxonomyHarvester |
| `wikidata_full_fetch_enhanced.py` | Called by recursive script, no sleep between requests → 429 errors | Used internally with 1.5s sleep added |
| `sca_comprehensive_builder.py` | Only 1-hop, misnamed "5 hops", no authority signals | Discard |

**Canonical Feb 20 output** (`output/taxonomy_recursive/Q17167_recursive_20260220_135756.json`) is valid as seed data — 100 entities, complete traversal. TaxonomyHarvester's fresh runs should match or exceed it once rate limiting is fixed.

---

## 8. How SCA Uses TaxonomyHarvester

```
SCA receives: seed_qid = Q17167

Step 1: TaxonomyHarvester.harvest(Q17167)
        → Returns 100-node taxonomy neighborhood, tiered

Step 2: LateralExplorer.explore(Q17167)  [existing script, already done]
        → Returns 12 lateral entities (capital, events, senate, currency)

Step 3: SCA LLM reasoning pass (NOT YET BUILT)
        Inputs: taxonomy neighborhood + lateral entities + authority tiers
        Output:
          - Domain landscape narrative (where RR sits academically)
          - Per-facet resource pointers (what each SFA should start from)
          - Taxonomy candidate flags (form_of_government → future domain node)
          - SFA hand-off document

Step 4: SCA passes hand-off document to 18 SFA instantiations
```

The TaxonomyHarvester is **stateless and reusable**. The SCA is the stateful orchestrator that decides what to do with the harvest.

---

## 9. Implementation Plan

### File: `scripts/agents/taxonomy_harvester.py`

```python
class TaxonomyHarvester:
    """
    Domain-agnostic Wikidata taxonomy traversal agent.
    Climbs the P31/P279/P361 abstraction stack from any seed QID.
    Stops at authority-signal ceiling (no authority IDs = meta node = stop).
    Rate-limited. Cached. Outputs structured tier-annotated candidate set.
    """

    UPWARD_PIDS    = ["P31", "P279", "P361"]
    DOWNWARD_PIDS  = ["P527", "P150"]
    SUCCESSION_PIDS = ["P155", "P156"]

    PRIMARY_AUTH_PIDS   = ["P2163", "P1149", "P8814", "P9842", "P1584"]
    SECONDARY_AUTH_PIDS = ["P244", "P227", "P268"]

    def __init__(self, cache_dir="output/taxonomy_cache", sleep_secs=1.5):
        ...

    def harvest(self, seed_qid, max_hops=5) -> dict:
        ...

    def _classify_authority_tier(self, entity_properties) -> str:
        # Returns "primary", "secondary", or "meta"
        ...

    def _fetch_entity(self, qid) -> dict:
        # Check cache first, then Wikidata API, sleep after
        ...
```

### Outputs:
- `output/taxonomy_cache/{qid}.json` — per-entity cache
- `output/taxonomy_harvest/{seed_qid}_harvest_{timestamp}.json` — full harvest

### Dependencies:
- Existing `wikidata_full_fetch_enhanced.py` fetch logic (extract as utility)
- No Neo4j writes — candidates only

---

## 10. Open Questions

1. **Secondary tier expansion**: Should LCSH/GND-only nodes expand 1 more hop before stopping? Could catch domain-relevant siblings. Recommend: NO — adds noise, LLM handles relevance.

2. **Succession depth**: P155/P156 chains can get long (Roman Kingdom → Roman Republic → Roman Empire → ... → Fall of Western Roman Empire). Cap succession at 3 hops while allowing taxonomy to go 5?

3. **Cache invalidation**: 30-day TTL? Or flag specific QIDs as stable (meta nodes never change)?

4. **Output to Neo4j**: Never from TaxonomyHarvester directly. SCA LLM reasoning layer decides which candidates become SubjectConcept proposals, and only approved proposals write to graph (human-in-the-loop, Phase D).
