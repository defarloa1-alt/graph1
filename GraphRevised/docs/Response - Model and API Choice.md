# Response: Model and API Choice for the Research Agent

**Responds to:** [Choosing a Model and API for a Historical Deep-Research Agent](Choosing%20a%20Model%20and%20API%20for%20a%20Historical%20Deep-Research%20Agent.md)
**Date:** 2026-10-11
**Status:** Agreed

## Decision

Adopt the document as the long-range design for source discovery and
research. Do not adopt its first step ("adopt Perplexity Agent API first") for
the current phase. The immediate bottleneck is reading supplied evidence
correctly, not discovering sources.

Sequence:

1. **Now (Phase 5, step 4):** Anthropic only. A passage-reading proposer on
   Claude Sonnet 5.5 with citations enabled; Opus 5.5 for difficult passages.
2. **Before scholarly ingestion:** evidence stance and contested assertions
   (backlog E8).
3. **Later:** Perplexity as a source-acquisition adapter (backlog E9), then the
   evaluation harness. An OpenAI verifier only if evaluation shows it is
   needed.

## Agreed

- The application owns orchestration, source hierarchy, entity resolution, and
  graph writes. This is the boundary in
  [05-AGENT-BOUNDARIES.md](../05-AGENT-BOUNDARIES.md).
- Records that fail verification are rejected, not repaired. This matches the
  validator's `invalid` outcome.
- Models may propose QIDs; tools verify them. This matches the identity
  adapter and the Phase 5 proposer, which never create entities.
- Claude's citations return the exact supporting span and its location. This
  lets the validator check passage evidence mechanically — the passage
  counterpart of the existing check that a Wikidata statement actually states
  the claimed relationship.
- The evaluation design: automatic failure for fabricated citations, blind
  review, full traces. The deterministic Wikidata proposer supplies labeled
  baseline cases.

## Amendments

### 1. Search output is never evidence

Perplexity answers and search-result objects are pointers to sources. Only a
document the application has fetched, preserved byte-for-byte, and hashed may
become a `SourceObservation`, under the same rule as the Wikidata payloads in
`phase-*-source/`. A model-synthesized answer citing a URL is not a source.

### 2. The claim packet maps onto ProposalDraft, with limits

| Claim packet field | Treatment |
|---|---|
| `entities` (labels and QIDs) | Resolved to existing local IDs before drafting; unresolved entities are reported, never created |
| `source.quotation_span`, `page_or_section`, `edition_id` | Required on passage evidence; validated verbatim against the preserved passage |
| `claim_type: causation, interpretation` | Not representable in `predicates-v1`; adding them is a model decision |
| `stance` | Requires backlog E8 before use |
| `confidence` | Recorded as a non-binding model note; never an evidence assessment |
| `time_expression` | Preserved verbatim; normalization waits for Phase 7 qualification |

### 3. Deterministic checks gate; model verification advises

Quote presence, locator resolution, and edition match are checked without a
model and decide validity. A second-vendor entailment check may add a flag for
the curator; it does not accept or reject on its own. Add it only if the
evaluation shows Claude's reading errors justify the cost and the second
vendor.

### 4. Record the model that answered

When a vendor preset routes to an underlying model, the Proposal's `modelId`
must record the model actually used, not the preset name.

### 5. Vendor specifics are unverified

Preset configurations, service dates, and benchmark figures in the source
document were not independently verified and may change. Re-check them when
backlog E9 is scheduled.

## Next implementation step

1. Add a passage observation kind: preserved text, locator, edition, content
   hash, rights note.
2. Extend the validator: passage evidence must contain the draft's quoted span
   verbatim at the cited locator.
3. Build the reader on the Anthropic SDK with citations enabled and
   `ProposalDraft` as structured output; record prompt version and model ID.
4. Test against the Actium passages of one public-domain primary source, with
   the deterministic Wikidata proposer as the baseline where both apply.
