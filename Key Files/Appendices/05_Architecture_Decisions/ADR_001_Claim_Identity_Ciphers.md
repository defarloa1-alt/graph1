# Appendix U: ADR 001 Claim Identity Ciphers

**Version:** 3.2 Decomposed  
**Date:** February 19, 2026  
**Source:** Extracted from Consolidated Architecture Document

---

## Navigation

**Main Architecture:**
- [ARCHITECTURE_CORE.md](../../ARCHITECTURE_CORE.md)
- [ARCHITECTURE_ONTOLOGY.md](../../ARCHITECTURE_ONTOLOGY.md)
- [ARCHITECTURE_IMPLEMENTATION.md](../../ARCHITECTURE_IMPLEMENTATION.md)
- [ARCHITECTURE_GOVERNANCE.md](../../ARCHITECTURE_GOVERNANCE.md)

**Appendices Index:** [README.md](../README.md)

---

## **Appendix U.5: ADR-001 Resolution Status (Architecture Review Issue #4)**

**Status:** ISSUE #4 RESOLVED  
**Date:** 2026-02-16  
**Architecture Review Item:** "Claim identity/cipher semantics internally inconsistent"

**Review Finding:**
> "Cipher generation includes fields like confidence, extractor_agent_id, and extraction_timestamp in the normalized hash input. Elsewhere, the verification pattern explicitly says the recomputation must exclude confidence/agent/timestamp ("NO confidence, NO agent, NO timestamp!"). Those can't both be the definition of "the cipher.""

**Resolution:**
✅ **ADR-001 (Appendix U) adopted Model 1: Content-Only Cipher**
- Cipher INCLUDES only: subject, object, relationship, temporal data, source work, passage hash, facet_id
- Cipher EXCLUDES: confidence_score, extractor_agent_id, extraction_timestamp
- **Consequence**: Same assertion extracted by different agents at different times = same cipher = automatic deduplication
- **Consequence**: Confidence evolution does NOT change cipher (provenance tracked separately in FacetPerspective nodes)
- **Consequence**: Cryptographic verification works across institutions (content-only signature)

**Implementation Compliance:**
- ✅ Section 6.4.1 Cipher Generation specifies content-only hash with explicit "NO confidence, NO agent, NO timestamp!" rule
- ✅ Section 6.4.3 Verification Query Pattern correctly recomputes exclude cipher from content only
- ✅ Section 6.4.2 Deduplication Query Pattern assumes same content = same cipher
- ✅ Appendix U specifies normalization functions and implementation requirements
- ✅ Section 5.5.3 Claim Architecture applies cipher consistently

**Minor Documentation Clarification Needed:**
- Section 6.4.1 "Claim Versioning Built-In" contains outdated comment "Computed with confidence=0.85" 
- Should be: "Content-only cipher (confidence NOT included in hash)"
- Context: Clarifies that confidence updates do NOT change cipher (cipher is stable identifier)
- **Action**: Mark for documentation pass (non-blocking - code behavior is correct)

**Impact on Federation:**
- ✅ Enables Wikidata/CIDOC/external system verification (content hash transcends institutional boundaries)
- ✅ Multiple Chrystallum instances can detect duplicate claims via cipher (distributed deduplication)
- ✅ Confidence can be aggregated separately without re-hashing

---

