# Domain Initiator (DI)

**Purpose:** Introduce the Domain Initiator as the entry point for domain-seeded harvest and classification. The DI tethers a domain to the subject backbone, harvests once, and classifies by facet. The SCA coordinates SFAs; the DI feeds the SCA.

---

## Role

**Domain Initiator (DI)** — Given a QID representing a domain (e.g. Q17167 Roman Republic):

1. **Harvests** from three layers:
   - **Seed QID:** All props and external IDs of the domain
   - **Backlinks:** Props and QIDs of every item that references the seed
   - **External IDs:** Federation IDs (Pleiades, GeoNames, etc.) and subject-backbone links (LCSH, FAST, Dewey) on both seed and backlinks
2. **Finds the most granular subject** from the subject backbone (LCC, LCSH, FAST) using harvested links
3. **Tethers** the domain to that subject
4. **Classifies** each candidate by facet (all 18) in one pass
5. **Outputs** per-facet deltas for the SCA to route to SFAs

**Single harvest, single classification pass.** No duplicate Wikidata calls. Cross-facet reasoning in one go.

---

## Harvest Scope

| Layer | What DI examines |
|-------|------------------|
| **Seed QID** | Props (P31, P279, P17, P131, P276, etc.), external IDs (P1584 Pleiades, P1566 GeoNames, P214 VIAF, etc.), LCSH/FAST/Dewey if present |
| **Backlinks** | Props and QIDs of each backlink; external IDs (Pleiades, GeoNames, etc.); FAST (P2163), Dewey (P1036), LCNAF/LCSH (P244) if present |
| **Subject backbone** | Links from harvested entities into LCC, LCSH, FAST; DI resolves to the **most granular** subject that matches |

Backlinks may carry federation IDs and subject-backbone links that the seed lacks. The DI aggregates these to find the finest-grained subject for the domain.

---

## Architecture

```
Domain (QID)
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  DOMAIN INITIATOR (DI)                                           │
│  1. Harvest: seed props + external IDs; backlink props + QIDs +  │
│     external IDs (Pleiades, GeoNames, LCSH, FAST, Dewey)         │
│  2. Resolve to most granular subject from backbone (LCC/LCSH/FAST)│
│  3. Tether domain to that subject                                │
│  4. Classify by facet (18 facets, one pass)                     │
│  5. Output: per-facet deltas                                     │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  SCA (Subject Concept Agent)                                     │
│  Coordinates 18 SFAs                                             │
│  Routes DI output to facet handlers                              │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  SFAs (Subject Facet Agents)                                     │
│  Geo, Military, Political, etc. — facet specialists              │
│  Apply deltas, propose additions, re-score                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Division of Labor

| | DI | SCA | SFA |
|---|-----|-----|-----|
| **Role** | Domain entry, harvest, backbone tether, facet classification | Orchestrates SFAs, routes deltas | Facet specialist, applies deltas, proposes additions |
| **Input** | Domain QID | DI output | SCA handoff |
| **Output** | Per-facet deltas | SFA assignments, re-scoring | Graph writes, proposals back to SCA |

---

## Geo Agent as DI Facet Slice

The current Geo Agent (discovery → filter → classify → deltas) is a **facet-specific slice** of what the DI would do. When the DI is built:

- Geo discovery + classification becomes the **GEOGRAPHIC** facet output of the DI
- Same harvest feeds Military, Political, Legal, etc.
- One agent, 18 facet outputs

---

## Harvest Script

```bash
python scripts/agents/domain_initiator/harvest.py --seed Q17167
```

**Output:** `output/di_harvest/{seed}_di_harvest.json`

**Rule:** Never pass PID or QID without its label. All properties include `pid`+`label`; all entity references include `value_qid`+`value_label`.

**Contents:** seed (properties, external_ids), backlinks (each with properties, external_ids), subject_backbone_links (FAST, Dewey, LCNAF), property_registry.

---

## Related

- `docs/SCA_SFA_CONTRACT.md` — SCA ↔ SFA division of labor
- `scripts/agents/domain_initiator/harvest.py` — DI harvest (implemented)
- `scripts/agents/domain_initiator/README.md` — DI script docs
- `scripts/backbone/geographic/geo_backlink_discovery.py` — geo-filtered harvest (Geo Agent input)
- `scripts/agents/geo/geo_agent_classify.py` — Geo facet classification (DI facet slice prototype)
- `Facets/facet_registry_master.json` — 18 canonical facets
