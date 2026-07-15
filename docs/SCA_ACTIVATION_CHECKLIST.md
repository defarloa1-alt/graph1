# SCA Activation Checklist — Roman Republic (Q17167)

**Baseline:** 2026-07-15 — see [BASELINE_Q17167_FACET_HIERARCHY_2026-07-15.md](BASELINE_Q17167_FACET_HIERARCHY_2026-07-15.md)  
**Status:** DI propose **complete** — 63 approved proposals written; 15 FacetUmbrella nodes wired under SubjectDomain.  
**Canonical graph:** ac63a8e5. **Written:** 63 `di_proposal` + 15 `di_facet_umbrella` SubjectConcepts.

---

## Phase 0 — Pre-flight (read-only)

```bash
cd c:\Projects\Graph1
python scripts/config_loader.py   # verify Neo4j ac63a8e5
```

In Neo4j or MCP `run_cypher_readonly`:

```cypher
MATCH (sc:SubjectConcept) RETURN sc.source, count(*) ORDER BY sc.source
MATCH (t:SYS_Threshold) WHERE t.decision_table = 'D12' OR t.name CONTAINS 'child_overload'
RETURN t.name, t.value
```

Open viewer → **SCA constitution** tab for full pre-flight protocol.

---

## Phase 1 — Close DI gaps (optional but recommended)

| Facet | Action |
|-------|--------|
| GEOGRAPHIC | `python scripts/agents/domain_initiator/train.py --pack output/di_route/Q17167_geographic_pack.json --corpus output/di_training/Q17167_GEOGRAPHIC_corpus.json` |
| BIOGRAPHIC | `python scripts/agents/domain_initiator/train.py --pack output/di_route/Q17167_biographic_pack.json --corpus output/di_training/Q17167_BIOGRAPHIC_corpus.json` |

Then re-aggregate:

```bash
python scripts/agents/domain_initiator/propose.py --seed Q17167
```

---

## Phase 2 — Human review ✅ (2026-07-15)

Reviewed `output/di_proposals/Q17167_proposals_enriched.json` — **63 approved**, 0 rejected.

---

## Phase 3 — Graph write + facet wire ✅ (2026-07-15)

- 63 `di_proposal` SubjectConcepts written
- 15 `FacetUmbrella` nodes under SubjectDomain (`Facet — {facet}` labels)
- Hierarchy: SubjectDomain → FacetUmbrella ← PART_OF — di_proposal

Verify:

```cypher
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})-[:HAS_SUBJECT_CONCEPT]->(u:FacetUmbrella)
RETURN u.label, count { ()<-[:PART_OF]-(:SubjectConcept {source:'di_proposal'}) } AS decomps
ORDER BY u.label
```

---

## Phase 4 — SCA dispatch to SFA_MILITARY

Only after pilot SCs exist in graph:

1. SCA pre-flight: confirm `di_proposal` SCs + D12 thresholds
2. Dispatch SFA with military pack: `output/di_route/Q17167_military_pack.json`
3. SFA consumes training: `output/di_training/Q17167_MILITARY_training.json`
4. SFA output → claims (Phase 2) — not yet automated end-to-end

Legacy SFA CLI (older path):

```bash
python -m scripts.agents.sfa propose --facet POLITICAL --seed Q17167
```

Prefer DI train JSON + new SCA contract once pilot SCs are in graph.

---

## Phase 5 — Full activation

- [ ] Write remaining approved proposals (`propose.py --seed Q17167 --write` after review)
- [ ] Deprecate or merge overlapping `ccs_bootstrap` scaffolds
- [ ] Fix geo backbone (restore missing GEO_* SCs, re-run `populate_member_of.py`)
- [ ] Update DI/SCA constitution `STATE` blocks to match live status

---

## Stop conditions

Do **not** `--write` if:

- Proposal fails ADR-020 (entity container, no authority tether)
- Geo SC routing targets missing nodes (GEO_SETTLEMENTS etc.)
- D12 thresholds missing from graph
