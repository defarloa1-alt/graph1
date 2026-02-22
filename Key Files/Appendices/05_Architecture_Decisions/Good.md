Good — now I have the full picture across all three docs. Let me update my review with what these files add.

## Updated Assessment with Full Context

### ADR-001: Clean and Correct

The claim cipher resolution is exactly right: **content-only hash, confidence/agent/timestamp excluded**.  This means the same assertion extracted by two different SFAs produces the same cipher — automatic deduplication across agents and even across Chrystallum instances. The minor documentation issue (outdated "confidence=0.85" comment in Section 6.4.1) is flagged as non-blocking. Nothing to change here. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/3c81a8ac-0403-45cd-9d8c-80b4563c454f/ADR_001_Claim_Identity_Ciphers.md)

### Entity Cipher Spec: Exceptionally Thorough

This is the strongest document in the system.  The architecture is clean: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c138e284-5dd5-410f-9e19-50fb9c7ac5bb/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md)

- **Tier 1 formula** is deterministic, reversible, human-readable (`ent_per_Q1048`). ✅
- **Tier 2 formula** correctly derives from Tier 1 + facet + SubjectConcept. The vertex jump function is pure computation — no graph query needed. ✅ [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c138e284-5dd5-410f-9e19-50fb9c7ac5bb/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md)
- **Authority cascade** (Wikidata → BabelNet → synthetic) with reconciliation workflow when QIDs become available. ✅
- **Test suite** covers determinism, uniqueness, cross-facet/cross-SubjectConcept differentiation, and name normalization. ✅
- **Migration path** for existing entities and backward compatibility is specified. ✅

The index strategy is sound — composite indexes match the query patterns shown in Section 8. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c138e284-5dd5-410f-9e19-50fb9c7ac5bb/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md)

## Revised Issues List (Now With Full Context)

My previous 6 issues still stand, but I can now be more precise:

### Issue 1 (Entity Types): Confirmed — Still a Gap

The entity cipher spec shows 9 types in `ENTITY_TYPE_PREFIXES` with CONCEPT as DEPRECATED.  The test suite only tests PERSON, EVENT, PLACE, SUBJECTCONCEPT, and synthetic — it doesn't test ORGANIZATION, PERIOD, MATERIAL, or OBJECT. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c138e284-5dd5-410f-9e19-50fb9c7ac5bb/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md)

My DEITY / LAW / rehabilitated CONCEPT recommendation still applies. The architect's own process (Section 2.3 rules: "New entity types require a registry update — locked list, like facets") already defines how to add them. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c138e284-5dd5-410f-9e19-50fb9c7ac5bb/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md)

**Additional finding:** The entity cipher spec shows `PERIOD` with prefix `prd` and example `ent_prd_Q17167` — but the same Q17167 also appears as `ent_sub_Q17167` (SUBJECTCONCEPT).  This is the dual-nature problem we solved with `:TemporalAnchor` multi-label. The canonical reference doc (Section 2.2) correctly adopts ADR-002 with `(:Entity:Organization:TemporalAnchor)`, but the **entity cipher spec hasn't been updated** to reflect this. It still shows PERIOD as a separate entity type that would give Q17167 a *different* cipher than its ORGANIZATION cipher. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

**Action needed:** The entity cipher spec needs an addendum clarifying that TemporalAnchor is a **label**, not an entity type. Q17167 gets `ent_org_Q17167` (its primary type is ORGANIZATION), not `ent_prd_Q17167`. The PERIOD entity type is reserved for purely temporal designations (Hellenistic period, Iron Age) that are not institutions. Add this to the decision table in Section 2.3.

### Issue 3 (Edge Properties): Confirmed — The Most Critical Gap

Having now read the full cipher spec, I can see that **edge properties are systematically absent from the entire architecture.**  The entity cipher spec covers node properties exhaustively (Tier 1, Tier 2, Tier 3 all have full property schemas). But look at the relationship sections — in both documents, edges are defined only by **type** and **domain/range**: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c138e284-5dd5-410f-9e19-50fb9c7ac5bb/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md)

```
PARTICIPATEDIN  P710  P11  Caesar → Gallic Wars
```

No property schema. No specification of what goes *on* the edge. The canonical reference doc (Section 3) catalogs 314 relationship types across 37 categories  — all with type, PID, and CRM alignment, but **zero edge property specifications**. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

This is the biggest architectural gap because your edges carry the richest data:

- Caesar's consulship (`:POSITIONHELD`) needs `P580: -59`, `P582: -58`, `P1545: 1` — these are **qualifier properties on the edge**, not on either node
- These same qualifiers feed into Tier 3 claim cipher computation  — the cipher hash includes `temporal_scope` and `qualifier_string` [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c138e284-5dd5-410f-9e19-50fb9c7ac5bb/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md)
- But nowhere does the architecture specify **which properties go on the Neo4j relationship vs. on the FacetClaim node**

**The decision the architect needs to make:**

| Property | On Edge? | On FacetClaim? | Rationale |
|----------|----------|----------------|-----------|
| `wikidata_pid` | Yes | Yes | Both need the PID for federation |
| `temporal_start` / `temporal_end` | Yes | Yes | Edge needs it for qualified traversal; claim needs it for cipher |
| `location_qid` (P276) | Yes | Yes | Same |
| `series_ordinal` (P1545) | Yes | Yes | Same |
| `confidence` | **No** | Yes | Confidence is mutable; edges should be stable  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/3c81a8ac-0403-45cd-9d8c-80b4563c454f/ADR_001_Claim_Identity_Ciphers.md) |
| `analysis_layer` | **No** | Yes | In-situ vs retrospective is a claim property, not an edge property |
| `claim_cipher` | Yes | N/A (it IS the claim) | Edge links back to the claim that justifies it |
| `source_qid` | **No** | Yes | Provenance lives on the claim, not the edge |

**The principle:** Entity-to-entity edges carry **immutable structural qualifiers** (when, where, which ordinal). FacetClaims carry **mutable evaluative metadata** (confidence, analysis layer, provenance). The edge's `claim_cipher` property links the two.

### Issue 7 (New): Claim Cipher Hash Input Needs Source Decomposition

The Tier 3 hash input is: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c138e284-5dd5-410f-9e19-50fb9c7ac5bb/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md)

```
f"{subject_qid}|{property_pid}|{object_qid}|{facet_id}|{temporal_scope}|{qualifier_string}|{source_qid}|{passage_locator}"
```

Including `source_qid` and `passage_locator` in the cipher means: **the same assertion from two different sources produces two different ciphers**. That's a design choice, not an accident — ADR-001 says "source work" is part of identity. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/3c81a8ac-0403-45cd-9d8c-80b4563c454f/ADR_001_Claim_Identity_Ciphers.md)

But consider: Plutarch says "Caesar was consul in 59 BCE." Suetonius says "Caesar was consul in 59 BCE." These are the *same assertion* with the *same content*. Under the current spec, they get **different ciphers** because source_qid differs.

This is defensible (you want provenance-distinct claims), but it means deduplication only works when the **same source** produces the same claim twice — not when **different sources** corroborate the same fact. You'll need a separate mechanism (maybe a `content_hash` without source, stored as a property on FacetClaim) to detect cross-source corroboration. The Claims Manager needs this for confidence aggregation.

**Recommendation:** Add a `content_hash` field to FacetClaim that hashes everything *except* source_qid and passage_locator. This gives you both:
- `cipher` = unique claim identity (source-specific) for provenance
- `content_hash` = assertion identity (source-agnostic) for corroboration detection

### Issue 8 (New): Test Coverage Gaps in Entity Cipher Spec

The test suite  covers Tier 1 and Tier 2 well but is missing: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c138e284-5dd5-410f-9e19-50fb9c7ac5bb/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md)

- No test for PERIOD entity type cipher generation
- No test for ORGANIZATION entity type
- No test for MATERIAL or OBJECT types
- No negative test for the deprecated CONCEPT type (should it raise ValueError or still work for backward compatibility?)
- No test for the `enrichentitywithciphers` function
- No integration test for the reconciliation workflow (synthetic → QID)

The `validateciphersuite` function  is a good start for bulk validation but hasn't been connected to the actual 300-entity dataset. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c138e284-5dd5-410f-9e19-50fb9c7ac5bb/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md)

## Updated Priority Actions

| # | Action | Priority | Source |
|---|--------|----------|--------|
| 1 | **Section 3.10: Canonical Edge Property Schema** | **Critical** |  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md) gap |
| 2 | **Reconcile entity cipher spec with ADR-002** (TemporalAnchor = label, not type; PERIOD type = pure temporal only) | **Critical** |  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c138e284-5dd5-410f-9e19-50fb9c7ac5bb/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md) conflicts with  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md) |
| 3 | **Add `content_hash` field** to FacetClaim for cross-source corroboration | High |  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/3c81a8ac-0403-45cd-9d8c-80b4563c454f/ADR_001_Claim_Identity_Ciphers.md) +  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c138e284-5dd5-410f-9e19-50fb9c7ac5bb/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md) interaction |
| 4 | Add DEITY, LAW entity types; rehabilitate CONCEPT | High |  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md) gap |
| 5 | Reconcile 6 unregistered DB relationship types | High |  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md) audit |
| 6 | Expand test suite for all 9 entity types + deprecated CONCEPT | Medium |  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c138e284-5dd5-410f-9e19-50fb9c7ac5bb/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md) gap |
| 7 | Elevate VIAF to required for PERSON | Medium |  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md) |
| 8 | State inverse relationship materialization policy | Medium |  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md) |
| 9 | CONCEPT migration appendix | Medium |  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md) |

The architect has done genuinely excellent work here. The cipher architecture is the most rigorous part of the system — deterministic, reversible, content-addressed, test-covered. The gaps are at the **edges** (literally — relationship property schemas) and at the **seams** between documents (entity cipher spec vs. canonical reference on how PERIOD/TemporalAnchor works). Close those and you have a production-grade identity and addressing system