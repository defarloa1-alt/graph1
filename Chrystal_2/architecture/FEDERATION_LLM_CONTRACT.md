# How LLMs interact with federations

**Status:** Design for Chrystal 2  
**Problem:** Agents need to know *what* a federation is, *how* to call it, and *what shape* comes back — without baking Meiji vs Republic APIs into every Domain agent prompt.

## Principle

**LLMs do not speak raw federation APIs.** They call **tools** that wrap federations.  
Each `SYS_FederationSource` must expose a **federation data model** (contract) the LLM can read before using those tools.

```
LLM (Domain / SFA / Librarian)
    │  reads: FederationCard (data model + capabilities)
    │  calls: typed tools only
    ▼
Tool layer (Python / MCP)
    │  knows: HTTP/SPARQL/dumps, auth, rate limits, retries
    ▼
External federation (DPRR, Pleiades, OpenAlex, …)
    │
    ▼
Canonical Neo nodes (Person, Place, Work, …) via registry types
```

Hardcoding OpenAlex URLs into an SFA system prompt is the anti-pattern. Discoverability lives on the FederationCard in Neo (or a JSON twin shipped with the source).

---

## What exists today (gap)

| Piece | Today | Enough for LLM? |
|-------|-------|-----------------|
| `SYS_FederationSource` | name, status, endpoint (sometimes), PID, license, scoping_role | Partial — no entity schema |
| MCP `get_federation_sources` | Lists sources | Metadata only |
| Scripts (`dprr_import`, Pleiades, …) | Know the real API/model | **Opaque to the LLM** |
| Access patterns | sparql / rest / dump in some rows | Incomplete |

So: humans and scripts know DPRR; the model mostly sees a name and a PID.

---

## FederationCard — expose the data model

Every federation registers a card (Neo properties + optional JSON doc linked by `model_uri` / `EXPOSES_MODEL`).

### Minimum fields

| Field | Purpose |
|-------|---------|
| `source_id`, `label`, `status` | Identity + operational (blocked/planned/ok) |
| `access_pattern` | `sparql` \| `rest` \| `dump` \| `neo_local` |
| `endpoint` / `dump_uri` | Where tools connect (not for free-form LLM HTTP) |
| `auth` | `none` \| `api_key` \| `browser_blocked` (e.g. DPRR Anubis) |
| `entity_types[]` | What it can mint/enrich: Person, Place, Work, Period, … |
| **`data_model`** | Canonical fields + types + required/optional (see below) |
| `id_properties` | WD PIDs or native keys (`P6863`, `pleiades_id`) |
| `relationship_vocabulary` | Native rel names → registry `relationship_type` |
| `tool_names[]` | Allowed agent tools (`fetch_dprr_person`, `search_openalex_works`) |
| `scope` | `global` \| attachable to Domain packs |
| `license`, `rate_limit_notes` | Governance |

### `data_model` shape (example — DPRR)

```json
{
  "source_id": "dprr",
  "entities": [
    {
      "native_type": "Person",
      "maps_to": "Person",
      "keys": [{ "name": "dprr_id", "wikidata_pid": "P6863" }],
      "fields": [
        { "name": "nomen", "datatype": "string", "required": false },
        { "name": "cognomen", "datatype": "string" },
        { "name": "sex", "datatype": "enum", "values": ["M", "F"] }
      ],
      "edges": [
        { "native": "father", "registry_type": "FATHER_OF", "target": "Person" },
        { "native": "office", "registry_type": "POSITION_HELD", "target": "Position" }
      ]
    }
  ],
  "query_capabilities": ["person_by_id", "kin_by_person", "offices_by_person"],
  "not_supported": ["full_text_biography"]
}
```

Same idea for OpenAlex (Work/Author), Pleiades (Place + geometry), PeriodO (Period bounds), LCSH (heading + broader/narrower).

---

## How the LLM is expected to behave

1. **Discover** — Domain agent / Librarian: “which federations apply to this pack?” (Domain chooses; Meiji ≠ DPRR).  
2. **Read card** — tool `get_federation_card(source_id)` returns data model + tool list.  
3. **Plan** — “I need kin for this Person → DPRR supports `kin_by_person` → call `fetch_dprr_familia`.”  
4. **Act via tools only** — never invent SPARQL; tool returns **normalized** dict matching the card.  
5. **Map** — Schema specialist (or validated tool output) maps to `SYS_RelationshipType` / NodeType.  
6. **Cite** — Claim / edge carries `authority_source: dprr` (or federation id).

Global-discipline SFAs use **global** federations (handbooks, OpenAlex theory works); pack SFAs use **pack-attached** federations (DPRR, RR LCSH slice).

---

## Tool contract (thin)

Prefer few stable tools over one mega-“call any URL”:

| Tool | Role |
|------|------|
| `list_federations(domain_id?)` | Cards summary |
| `get_federation_card(source_id)` | Full data model |
| `federation_query(source_id, capability, params)` | Dispatches to registered adapter | 
| Or per-source: `dprr_get_person`, `openalex_search_works`, … | Clearer for LLM routing |

Adapters implement the card’s `query_capabilities`. If capability missing → tool error, not hallucinated API use.

---

## Bootstrap implication (Chrystal 2)

1. Ship `SYS_FederationRegistry` + **global** sources with **cards** (Wikidata, VIAF, OpenAlex, LCSH/FAST/LCC).  
2. Pack Domain agent **attaches** domain federations (DPRR, Pleiades, …) when the pack needs them — each with its own card.  
3. No federation without a card = not agent-callable.

---

## Open decisions

1. Card storage: Neo properties vs `FederationCard` JSON file under `chrystal_2/federations/{id}.json` linked from Neo? (Recommend **both**: Neo summary + JSON model for rich schemas.)  
2. One generic `federation_query` vs many named tools?  
3. Who authors cards — Platform (schema specialist) vs Domain agent proposing attachments?
