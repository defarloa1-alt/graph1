# Librarian — pack aboutness placement

1. **Aboutness ≠ identity.** LCSH `sh…` = subject heading. LCNAF `n…` = name
   authority (Person helix) — defer; do not mint as LCSH.
2. **Multi-aboutness (not one shelf).** “What is this?” is **not** a single physical
   call number. A SubjectDomain / SubjectConcept may carry **many** LCSH, FAST, and
   LCC tethers at once — facets, soft correlations, and competing legitimate
   aboutnesses. Never collapse to one exclusive answer just because the old card
   catalog / shelving world needed one spine label. Prefer additive edges over
   replace-one-true-class.
   Example — **Roman Republic** is both a **time period** and a **form of
   government**; keep both aboutness strands on the same SubjectDomain rather than
   picking one “true” subject.
3. **FederationCard first.** Only act via `lcsh_fast_lcc` capabilities. No silent
   encyclopedia tethers. No hardcoded LoC URLs outside the tool layer.
4. **Registry gate.** Mint only `SYS_NodeType` / `SYS_RelationshipType` names that
   exist in Neo (`LCSH_Heading`, `HAS_LCSH_AUTHORITY`).
5. **WD is a candidate.** `wd_p244` (or pack P244) nominates an id; LoC resolution
   supplies the authoritative heading label at tether time.
6. **SubjectDomain first.** Place the pack before SC / SFA aboutness.
7. **FAST is often facet soft.** Chronological LCSH rarely maps 1:1; prefer
   scored OCLC facets marked `soft=true` over inventing an exact FAST id.
   For Roman Republic, **Rome (Empire)** (`fst01204885`) + chrono string
   `Roman Republic--510-30 B.C.` is the correct umbrella pattern — not a
   failed label match. Soft ≠ discard; soft = non-exclusive.
8. **LCC is correlation soft** until a cataloger marks an exclusive shelf class
   (and even then other soft alignments may remain).
9. **Idempotent writes.** MERGE by authority key; re-runs must not duplicate.
10. **Dry-run default posture.** CLI requires explicit `--write` to mutate Neo.
11. **Instance lock.** Only Chrystal 2 (`7fe339d2`).
