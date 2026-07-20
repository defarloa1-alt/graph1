# Bootstrap status — Chrystal 2 (`7fe339d2`)

**Docs/code home:** [`../INDEX.md`](../INDEX.md) · [`../README.md`](../README.md)

| Step | Status | Notes |
|------|--------|-------|
| Env → `7fe339d2` | Done | URI + `AURA_INSTANCEID` |
| Year backbone | **Done 2026-07-19** | 4025 Years (−2000…2025, no 0); 4024 `FOLLOWED_BY` |
| 18 Facets + FacetRegistry | **Done 2026-07-19** | `python chrystal_2/bootstrap/seed_facets.py` |
| SchemaRegistry + core NodeTypes | **Done 2026-07-19** | `python chrystal_2/bootstrap/seed_schema_registry.py` |
| SYS_AgentType (5) | **Done 2026-07-19** | Domain, SchemaSpecialist, Librarian, SFA, Validation (SCA agent removed) |
| Thin SYS_RelationshipType | **Done 2026-07-19** | ~60 curated types; `seed_relationship_types_thin.py` |
| FederationRegistry + global sources | **Done 2026-07-19** | Wikidata, VIAF, OpenAlex, LCSH/FAST/LCC, **PeriodO**; cards in `chrystal_2/federations/` |
| Decade/Century/Millennium | Not run | Optional temporal hierarchy |
| SYS_Policy (universal) | Pending | Foundational; no claims |
| Decision tables (minimal) | Pending | Foundational; no claims |
| ClaimStatus / RejectionReason | **Deferred** | User: skip claims; stay foundational |
| WD pack library | **Done 2026-07-19** | `JSON/wikidata/packs/Q17167_pack_library.json` (83 stmts, 29 ext IDs, 38 forward, 150 backlinks) |
| Schema Specialist agent | **Done (CLI)** | `python chrystal_2/agents/schema_specialist/__main__.py propose …` |
| Schema proposal (LLM) | **Done 2026-07-19** | Card-only identity tether; see packs JSON |
| Domain apply | **Done** | Code apply + **Domain LLM plan review** (`--review-only` / `--review-write`) |
| Librarian place_domain | **Legacy** (RR done) | Prefer Domain `pipeline.py bootstrap`; do not extend |
| Librarian enrich review | **Legacy** | Folded into bootstrap review |
| Biblio crosswalk seeds | **Done 2026-07-19** | `federations/crosswalks/` curated from prod SC snapshot + disciplines + CIP + LCC→FAST |
| PeriodO FederationCard | **Done 2026-07-19** | Card + Rome seed (4 ids); RR shells enriched |
| PeriodO `apply_periodo_enrich` | **Legacy** | Prefer bootstrap; leave WD→PeriodO map frozen |
| Domain bootstrap pipeline | **CLI ready** | `pipeline.py bootstrap` = biblio+PeriodO+geo propose → review → write |
| Timeline acceptance (RR) | **Pass** | Years stamped on Period shells; `acceptance_view.py` checks.pass |
| Domain geo (thin) | **Done (Rome)** | In bootstrap (`stamp_place_pleiades`); `stamp_place_geo.py` legacy |
| Domain events (pack) | **Ownership + 3-slot tether locked** | Domain shortlist/dates; Bio=participation; any SFA may deepen other facets. `DOMAIN_EVENTS.md` |
| Librarian (SC aboutness) | Later | SC-level suggest/reuse |

## Locked order

Foundation ✓ → pack library ✓ → SubjectDomain shell ✓ → Schema Specialist ✓ → schema apply ✓ → **Domain bootstrap** (biblio+PeriodO) ✓.

See `architecture/DOMAIN_PIPELINE.md`.
