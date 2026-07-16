# Chrystallum Architecture

**One document. Read this chain in order:**

| Order | Document | Purpose |
|-------|----------|---------|
| 1 | [docs/EPISTEMIC_MODEL.md](../docs/EPISTEMIC_MODEL.md) | What can be known; Phase 1 vs Phase 2 |
| 2 | **[docs/ARCHITECTURE_CURRENT.md](../docs/ARCHITECTURE_CURRENT.md)** | **Current system — start here** |
| 3 | Agent constitutions (`chrystallum_*_constitution.jsx`) | Operational guides per agent (DI, SCA, SFA, …) |
| 4 | [Appendices/05_Architecture_Decisions/](Appendices/05_Architecture_Decisions/) | ADRs (binding decisions, e.g. ADR-020 CCS) |

**Specialized (not general architecture):**

| Document | Purpose |
|----------|---------|
| [docs/FEDERATION_ARCHITECTURE.md](../docs/FEDERATION_ARCHITECTURE.md) | Federation sources and wire contracts |
| [docs/GEO_BACKBONE_MAPPING_STATUS.md](../docs/GEO_BACKBONE_MAPPING_STATUS.md) | Place hierarchy gaps |
| [docs/DEPRECATED_CHRYSTAL_2.0.md](../docs/DEPRECATED_CHRYSTAL_2.0.md) | Deprecated Aura sandbox |

**Interactive (not markdown spec):**

| File | Purpose |
|------|---------|
| [chrystallum_system_map.jsx](chrystallum_system_map.jsx) | Live graph explorer (viewer) |
| [chrystallum_architecture.jsx](chrystallum_architecture.jsx) | Layer diagram (reference UI) |

---

## Archived — do not use as current architecture

| Archive | Why |
|---------|-----|
| [Architecture_Decomposed_2026-02/](../Archive/Key%20Files/Architecture_Decomposed_2026-02/) | Feb 2026 four-file split (CORE / ONTOLOGY / IMPLEMENTATION / GOVERNANCE) — superseded by `ARCHITECTURE_CURRENT.md` |
| [ARCHITECTURE_OPTIMIZATION_REVIEW.md](../Archive/ARCHITECTURE_OPTIMIZATION_REVIEW.md) | Feb 2026 stakeholder performance review — ideas only, not current design |
| [2-12-26 Chrystallum Architecture - CONSOLIDATED.md](../Archive/Key%20Files/2-12-26%20Chrystallum%20Architecture%20-%20CONSOLIDATED.md) | Pre-decomposition monolith |
| [CLAIM_ID_ARCHITECTURE.md](../Archive/Key%20Files/CLAIM_ID_ARCHITECTURE.md) | Feb 2026 claim cipher spec — use ADR-001 + EPISTEMIC_MODEL |
| [CHRYSTALLUM_HANDOFF.md](../Archive/Key%20Files/CHRYSTALLUM_HANDOFF.md) | Feb 2026 ITGAR handoff — unbuilt governance design |

Deep reference appendices under [Appendices/](Appendices/) remain for ontology detail, authority integration, and implementation patterns — but **agents and developers start with `docs/ARCHITECTURE_CURRENT.md`**.
