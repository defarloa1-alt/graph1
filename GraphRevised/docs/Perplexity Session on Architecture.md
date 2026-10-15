Perplexity Session on Architecture
Claude’s approach is broadly sensible, and the transcript clarifies the access issue: **Claude Code is running on your Windows machine and has shell access to `C:\Projects\Graph1\GraphRevised`; I have project memory and whatever files are exposed to this workspace, but not automatic access to that local directory.** Your active refactoring area is indeed `graph1/GraphRevised`.

## Claude’s review

Claude did several things correctly:

- Mapped the repository before attempting to interpret it.
- Excluded `.git`, `node_modules`, `__pycache__`, and much of the repetitive Wikidata cache.
- Started with `README`, the session handoff, architecture, graph model, agent boundaries, and the newly added source document.
- Followed references from the handoff into later documents rather than reading strictly by filename.
- Examined implementation code and curation data after reading the conceptual documentation.
- Connected `Agent resources.md` to the actual source-planning and passage-reading pipeline.

That is the right general pattern: **orientation → architecture → current handoff → implementation → representative data → tests**.

However, “I’ve gone through all the files” would be too strong based on what is shown. Claude surveyed all filenames, read the major documentation, and sampled important code and data. It did not meaningfully read all 661 files—and probably should not read every cached Wikidata response, generated export, compiled Python file, or repetitive run log.

A more accurate statement would be:

> “I inventoried the repository, read the principal design documents, reviewed the active implementation modules, and sampled representative curation, inquiry, source, run, and test artifacts.”

## Main architectural finding

The most important fact in the transcript is that your project already has **two related but different source mechanisms**:

| Mechanism | Present implementation | Purpose |
|---|---|---|
| Known source access | Perseus/Scaife, Gutenberg, LacusCurtius, library authorities, preserved files | Find, retrieve, preserve, and read material from known systems |
| Source discovery | `source_plan.py` plus an LLM-generated candidate list | Propose additional works that may illuminate an inquiry |

Your new `Agent resources.md` appears intended to bootstrap both. That is useful, but the document should not become a closed whitelist. Your intended design is better expressed as:

> **The source guide supplies trusted starting points and discovery routes. It does not define the complete universe of permissible sources.**

The agent should consult registered resources first, then independently discover candidates, while preserving the distinction between:

1. A source mentioned in the guide.
2. A source discovered by an agent.
3. A source whose bibliographic identity has been verified.
4. A digital copy whose location and rights have been verified.
5. A source whose relevant passages have been retrieved.
6. A source whose claims have passed historical review.

## The current limitation

From the displayed code and plan, `source_plan.py` appears more accurately described as **LLM-assisted bibliography proposal with Scaife availability checking**, not yet a complete autonomous source-discovery system.

The sample plan illustrates this well:

```json
{
  "author": "Horace",
  "work": "Odes (Carmina)",
  "locator": "1.37",
  "confidence": "high",
  "catalog": {
    "status": "work found"
  }
}
```

Several different judgments are compressed here:

- Horace’s *Odes* exists.
- The Scaife catalog contains a corresponding work.
- Ode 1.37 may be relevant to Actium.
- A particular digital edition is available.
- The work represents an Augustan interpretation.
- The source should be included in the inquiry.
- Statements extracted from it should be accepted.

Only the first few can be established through catalog matching. The model’s `"confidence": "high"` must not imply that the historical interpretation or proposed graph claims are accepted.

I would rename or divide confidence fields:

```json
{
  "discoveryConfidence": "high",
  "identityStatus": "candidate",
  "catalogMatchStatus": "probable",
  "availabilityStatus": "located",
  "relevanceStatus": "unreviewed",
  "evidentiaryStatus": "unread",
  "curationStatus": "proposed"
}
```

## Source registry design

`Agent resources.md` is valuable as human documentation, but agents ultimately need a machine-readable companion—perhaps:

```text
curation/source-registry.json
```

Each resource should carry fields such as:

```json
{
  "id": "chr:source-system:perseus",
  "label": "Perseus Digital Library",
  "resourceType": "text_repository",
  "domains": ["classics", "ancient-history"],
  "coverage": ["Greek texts", "Latin texts", "translations"],
  "discoveryMethods": ["catalog", "CTS URN", "author", "work"],
  "accessMethods": ["Scaife API", "Perseus XML"],
  "identifierSchemes": ["CTS-URN"],
  "rightsPolicy": "edition-specific",
  "preferredUses": [
    "work discovery",
    "edition discovery",
    "passage retrieval"
  ],
  "limitations": [
    "catalog presence does not establish historical relevance",
    "translation and edition rights vary"
  ],
  "adapter": "adapters.perseus_passages"
}
```

This would let the prose document explain the research universe while the registry tells agents how to act.

## Discovery should produce proposals

Your existing architecture already points in the correct direction: the agent proposes; the curator accepts. The same principle should govern source discovery.

A discovered source should first become something like:

```text
(:SourceCandidate {
    proposedTitle,
    proposedAuthor,
    proposedLocator,
    discoveryQuery,
    discoveredAt,
    proposedBy,
    relevanceRationale,
    status: "unverified"
})
```

Only after identity resolution should it become a canonical `Work`:

```text
(:SourceCandidate)-[:RESOLVED_AS]->(:Work)
```

Similarly, a URL should not automatically establish a work:

```text
(:DigitalRepresentation)-[:REPRESENTS_EDITION]->(:Edition)
(:Edition)-[:EDITION_OF]->(:Work)
```

This prevents the common collapse of:

- Work
- Edition
- Translation
- Digital file
- Web page
- Passage
- Bibliographic candidate

That distinction will matter when the same ancient work appears in Perseus, LacusCurtius, Internet Archive, Project Gutenberg, and a university-hosted transcription.

## Where annotations fit

The files shown in the transcript reveal that your project is already beyond the generic structure I suggested earlier. You have:

- Inquiry-specific guidance.
- Candidate entity scopes.
- Work entities.
- Source adapters.
- Passage readers.
- Assertions and proposals.
- Notes and interpretations.
- Narrative event IDs.
- Predicate-specific instructions.
- Separate formal and operational command relationships.

Therefore, the Actium narrative should not introduce an entirely separate annotation system. It should consume what the pipeline already produces:

```text
Inquiry
   → Source plan
   → Candidate work
   → Verified Work
   → Preserved representation
   → Passage observation
   → Proposed assertion or note
   → Review
   → Accepted assertion
   → Narrative use
```

The missing piece appears to be not evidence modeling but **narrative assembly and sequencing over accepted assertions and notes**.

## Sequencing recommendation

Your narrative layer should distinguish four orders:

| Sequence | Example |
|---|---|
| Historical sequence | Agrippa captures Methone before the principal battle |
| Source sequence | Plutarch discusses a war council before describing deployment |
| Research sequence | The agent discovers Dio after reading Plutarch |
| Narrative sequence | The final account opens with strategic isolation, then explains the war council |

These must not share one generic `sequence` property.

A compact model could be:

```text
(:Narrative)-[:HAS_SECTION {position: 1}]->(:NarrativeSection)

(:NarrativeSection)-[:USES_ASSERTION]->(:Assertion)
(:NarrativeSection)-[:USES_NOTE]->(:Note)
(:NarrativeSection)-[:MENTIONS]->(:Entity)

(:Assertion)-[:SUPPORTED_BY]->(:SourceObservation)
(:SourceObservation)-[:OBSERVED_IN]->(:Passage)
(:Passage)-[:PART_OF]->(:Work)
```

Your `CONCERNS` edges remain useful for retrieval:

```text
(:Work)-[:CONCERNS]->(:Entity)
```

But they should answer:

> “Which works may be relevant to this entity?”

They should not answer:

> “Where should information from this work appear in the narrative?”

## Inquiry guidance

The Hale inquiry is especially strong. Its instructions distinguish:

- Participation from preparation.
- Command of a wing from command of a fleet.
- Operational command from supreme authority.
- Event participation from actions merely performed by someone’s forces.
- Historical Octavian from the entity Wikidata labels Augustus.

Those are exactly the kinds of predicate-level controls needed to prevent shallow LLM extraction.

One improvement would be to move reusable rules out of the individual inquiry file. For example:

```text
commanded relates a person to a force they directed in action
```

belongs in the predicate registry or a shared rule module. The inquiry should then add only Actium-specific qualifications. Otherwise, slightly different definitions of `commanded` may accumulate across inquiry JSON files.

A good division would be:

```text
predicates.vN.json
    canonical predicate meaning

agent-policy/military-command.json
    domain extraction rules

inquiries/actium-hale-famous-sea-fights.json
    source- and inquiry-specific guidance
```

## Agent-resource policy

I would add a short governing section near the beginning of `Agent resources.md`:

> These resources are trusted starting points, not an exhaustive source list. Agents should search registered resources first and may propose additional repositories, catalogs, works, editions, and datasets. Discovery does not constitute acceptance. Newly discovered resources must record provenance, access location, identity evidence, rights information, relevance rationale, and verification status before their contents can support accepted graph assertions.

That captures exactly what you described: **kickstart the agents with a universe of sources without limiting them to that initial universe**.

## Overall judgment

Claude understood the project direction and explored it intelligently. Its strongest move was connecting the new source document to `source_plan.py`, the adapters, inquiries, preserved source files, and passage-reader pipeline instead of treating the document as a detached bibliography.

The next useful task for Claude should not be “read more files.” It should be:

1. Produce a concise architectural map of the current source lifecycle.
2. Compare `Agent resources.md` against actual adapters and discovery code.
3. Identify resources documented but not operationally supported.
4. Identify adapters that lack corresponding registry entries.
5. Specify the candidate-to-verified-source state transitions.
6. Recommend the smallest implementation increment that lets agents discover sources outside the bootstrap list safely.

That would turn Claude’s repository familiarization into an actionable design review.