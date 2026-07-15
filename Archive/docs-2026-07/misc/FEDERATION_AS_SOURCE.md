# Federation as Source

> **Superseded by FEDERATION_ARCHITECTURE.md**
>
> This document was created before the dev produced `FEDERATION_ARCHITECTURE.md`,
> which covers the same architectural decision more concisely and is already linked
> from `HARVESTER_SCOPING_DESIGN.md`.
>
> **Canonical reference:** `FEDERATION_ARCHITECTURE.md`
>
> Additional detail not in FEDERATION_ARCHITECTURE.md:
> - Per-federation breakdown of what Wikidata lacks vs what each federation provides
>   (Trismegistos attestations, LGPN onomastics, Pleiades period-specific names)
> - Bootstrap readiness three-state model (BOOTSTRAP_REQUIRED / PHASE1_COMPLETE / PHASE2_COMPLETE)
>   — now in chrystallum_schema.json epistemological_frameworks.bootstrap_readiness.states
> - Dev implementation anti-patterns (write claims not metadata fields; keep fetch
>   function separate from scoping gate; log federation fetches for idempotency)
>   — now in FEDERATION_ARCHITECTURE.md Phase 1 design constraint table

*Created: 2026-02-24 — Superseded same day by dev's FEDERATION_ARCHITECTURE.md*
