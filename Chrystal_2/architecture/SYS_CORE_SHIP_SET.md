# SYS core ship set — Chrystal 2

Domain-agnostic graph rules that must exist **before** WD harvest.  
Aligned with conversation 2026-07-19; inventory from live `ac63a8e5` used as reference only.

## Ship

| Piece | Source |
|-------|--------|
| `SYS_SchemaRegistry` | Create empty root |
| `SYS_NodeType` | Core labels only (SubjectDomain, Year, Facet, Claim, Person, Place, Period, … + SYS_* self) |
| `SYS_RelationshipType` | `Relationships/relationship_types_registry_master.csv` |
| `:Facet` × 18 | `Facets/facet_registry_master.csv` (dedupe `facet_key`) |
| `SYS_AgentType` | Domain, SchemaSpecialist, Librarian, SFA, Validation (minimal; no SCA agent) |
| `SYS_ClaimStatus`, `SYS_RejectionReason` | **Deferred** — stay off the claim track until foundation is solid |
| Decision tables | Start with D1, D2, D6/D14, D8, D10 (+ thresholds they need) — non-claim gating only |
| `SYS_Policy` | Universal only (NoTemporalFacet, NoClassificationFacet, LocalFirstCanonicalAuthorities, ApprovalRequired) |
| `:Year` | `genYearsToNeo.py` |
| `SYS_FederationRegistry` | Shell + Wikidata / VIAF / OpenAlex / LCSH-FAST-LCC catalog rows **unattached** to a Domain |

## Do not ship yet

- `SYS_RoutingRule` (roman_republic)  
- Rome-only `SYS_FacetPolicy` / most `SYS_FacetRouter`  
- DPRR, Pleiades, Perseus, CRRO, … as mandatory federations  
- Fat Rome `SYS_WikidataProperty` set  
- Peer SCs / Claims / Persons  

## Facet note

Political vs Social: keep both Facet catalog keys; optional combined SFA dispatch later (`architecture/` TBD). Do not delete SOCIAL from the 18 for v1 ship.
