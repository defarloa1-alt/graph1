# Choosing a Model and API for a Historical Deep-Research Agent

## Executive recommendation

The best design is **not a single-vendor agent**. Use the **Perplexity Agent API as the research and retrieval layer**, with **Anthropic Claude Opus 5.5 as the principal close-reading and synthesis model**. Perplexity supplies multi-step web search, structured search results, URL fetching, domain controls, background execution, citations, and access to models from several providers through one interface. Anthropic supplies unusually strong document-grounding primitives: passage-level citations, a 1-million-token context window, and visual PDF analysis of text, tables, charts, and page layout.[^1][^2][^3][^4][^5][^6]

For routine historical research, start with Perplexity's **`high` preset**. Escalate genuinely difficult, open-ended investigations to **`xhigh`**; Perplexity currently configures that preset with Claude Opus 5.5, up to 100 agent steps, web search, and a sandbox. Because preset configurations can change automatically, pin the model, prompt, tool limits, and retrieval settings whenever reproducibility matters.[^7]

If only one API can be adopted, choose **Perplexity Agent API**. If the workload is mainly supplied books, articles, archival PDFs, and close reading rather than source discovery, choose **Anthropic's API**. Keep **OpenAI's Responses or Agents API** as a strong challenger for tool-heavy workflows, MCP integrations, and difficult browsing, rather than making it the first default for this particular source- and citation-centered historical system.[^8][^9][^10]

## Why this split works

“Deep research” combines at least four distinct jobs: source discovery, document acquisition, close reading, and evidence-backed synthesis. Treating them as separate stages makes failures observable and allows each model or API to do the work for which it is best suited.

Perplexity's Agent API is primarily valuable as a **research harness**, not merely as a model endpoint. It exposes integrated web search and URL fetching, returns typed search-result objects with stable IDs, supports domain filtering, and can route requests to OpenAI, Anthropic, Google, and other model families. Its raw Search API can also return ranked results without LLM synthesis, which is useful when the application must retain control over source selection and evidence processing.[^11][^12][^13][^1]

Claude is especially well suited to the **reader and analyst role**. Anthropic's citation system associates claims with exact locations in supplied documents, supports PDFs and text documents, and also accepts search results from a custom retrieval pipeline as first-class citation-bearing content blocks. Claude's PDF pipeline processes both extracted text and page images, allowing it to analyze tables, maps, charts, marginalia, and layouts that text-only extraction may lose.[^2][^5]

OpenAI remains attractive where the agent must operate across a large tool ecosystem. Its web-search tool returns inline URL citations and a complete list of consulted sources, supports allowlists or blocklists of up to 100 domains, and integrates with remote MCP servers through the Responses API. OpenAI also offers managed agent infrastructure with long-running sessions, custom functions, MCP, and built-in web search.[^9][^10][^8]

## Vendor fit

| Requirement | Perplexity | Anthropic | OpenAI |
|---|---|---|---|
| Open-web discovery | Best fit: integrated search, domain filters, ranked result objects, presets, and multi-step research[^1][^12] | Strong server-side web search with citations and dynamic filtering[^14] | Strong web search with citations, domain controls, and complete consulted-source lists[^8] |
| Scholarly-source discovery | Strong: academic-domain filtering and citation-chain workflows are documented directly[^15] | Possible through web search or custom tools, but requires more orchestration | Strong with domain filters and MCP/database connectors[^8][^10] |
| Close reading of supplied PDFs | Good, but file behavior depends on the selected provider and model[^16] | Best fit: passage citations plus visual analysis of PDF pages[^2][^5] | Strong file and tool ecosystem, but its web citation interface is principally URL-annotation based[^8] |
| Citation plumbing | Excellent structured search results; citation IDs map to verified result URLs[^17][^18] | Excellent passage-level citations in documents and citations in web search[^14][^2] | Excellent URL annotations and full source lists for web search[^8] |
| Model portability | Best: one API can call multiple frontier-model families[^1][^3] | Anthropic models only | OpenAI models, with outside systems exposed mainly as tools or MCP connections |
| Long-context document work | Depends on selected model | 1-million-token context and up to 128,000 output tokens on current flagship models[^4] | Model-dependent |
| Reproducibility | Pin explicit model and settings; floating presets intentionally inherit future changes[^7] | Strong when model snapshots and prompts are pinned | Strong when model snapshots, tools, and instructions are pinned |
| Best role | Discovery, orchestration, source tracking | Close reading, evidence extraction, synthesis | Independent verifier and tool-heavy alternate |

## Recommended stack

### Research orchestrator

Keep the orchestration logic in the application rather than delegating all behavior to a vendor preset. A Python or LangGraph controller should own the research plan, query decomposition, source hierarchy, retry policy, evidence schema, budget, and stopping rules. This preserves the graph-native governance and claim provenance needed by a historical knowledge system rather than allowing the model's prose answer to become the system of record.

Use the Perplexity Agent API in two modes:

- **Discovery runs:** `high` preset, web search enabled, explicit scholarly-domain filters, bounded search context, and structured `search_results` retained in full.
- **Hard investigations:** `xhigh` or an explicitly pinned frontier model, background execution, larger step allowance, and sandbox access where tabulation or reconciliation is required.[^7]
- **Deterministic retrieval:** raw Search API calls when the application should rank, deduplicate, or reject sources before any model sees them.[^11]
- **Known-source reading:** `fetch_url` after discovery, understanding that binary PDFs and anti-bot pages may yield incomplete extraction.[^13]

### Source adapters

Do not rely on general web search as the sole path to scholarship. Add first-class tools or MCP adapters for the authority and repository systems that matter to the historical domain: library catalogs, scholarly metadata services, open-access repositories, archival finding aids, IIIF manifests, Wikidata, and project-specific Neo4j queries. The agent should receive structured records—including identifiers, edition data, authorship, publication date, repository, language, and access status—rather than reconstructing bibliographic metadata from prose.

Perplexity can restrict discovery to academic domains and has a documented pattern for extracting DOI and paper metadata and building citation chains. OpenAI and Anthropic can both connect to external retrieval systems: OpenAI through remote MCP in the Responses API, and Anthropic by receiving custom search-result content blocks with built-in citation support.[^10][^15][^2]

### Document reader

Send acquired primary and secondary sources to Claude with citations enabled. Use **Claude Opus 5.5** for ambiguous, multilingual, historiographically difficult, or long-horizon work; use **Claude Sonnet 5.5** for routine extraction, classification, and first-pass summaries. Anthropic describes Opus 5.5 as suited to long-running agentic coding and knowledge work, while Sonnet 5.5 balances speed and intelligence.[^19]

The reader should not emit only narrative prose. Require a validated claim packet such as:

```json
{
  "claim_text": "...",
  "claim_type": "event|date|identity|causation|interpretation",
  "entities": [{"label": "...", "qid": "...", "role": "..."}],
  "time_expression": {"verbatim": "...", "normalized": "...", "certainty": "..."},
  "place": {"verbatim": "...", "qid": "..."},
  "source": {
    "work_id": "...",
    "edition_id": "...",
    "author": "...",
    "page_or_section": "...",
    "quotation_span": "..."
  },
  "stance": "supports|contradicts|qualifies|mentions",
  "confidence": 0.0,
  "notes": "..."
}
```

The exact evidence text should remain attached to the claim as a source span; generated summaries should never replace it. For copyrighted works, store only the minimum evidence span needed for verification and preserve pointers to the licensed or controlled source.

### Independent verifier

Use a second provider to verify the reader's outputs. An OpenAI model with web search disabled can check whether each claim is entailed by the supplied evidence, whether uncertainty was preserved, and whether the structured output conforms to the schema. For difficult discovery failures, enable OpenAI web search as an independent retrieval path; it can return both inline citations and the complete list of consulted URLs.[^8]

Verification should reject, not silently repair, any record where:

- The citation does not entail the claim.
- The page, passage, edition, or URL cannot be resolved.
- A primary-source statement is presented as a modern scholarly conclusion.
- Competing interpretations were collapsed into one assertion.
- A normalized date, person, place, or office is more precise than the source supports.
- A generated URL appears without a corresponding tool result; Perplexity explicitly warns against trusting model-generated URLs instead of returned search-result objects.[^18]

### Graph writer

Only validated claim packets should reach Neo4j. Preserve each scholar's or source's assertion as a separate claim node or claim subgraph, with relationships for support, contradiction, qualification, derivation, translation, and edition. This avoids forcing historiographical disputes into a single canonical triple and fits a provenance-first historical knowledge graph.

For the user's Wikidata-centered federation strategy, entity resolution should remain a separate tool-governed stage rather than an incidental model behavior. The model may propose QIDs, but the application should verify labels, aliases, entity classes, dates, and relevant properties through the Wikidata API before committing them.

## Model policy

A practical routing policy is:

| Task | Default | Escalation |
|---|---|---|
| Query classification and facet routing | Low-cost model or deterministic code | Claude Sonnet 5.5 |
| Open-web and scholarly discovery | Perplexity Agent API `high` | Perplexity `xhigh` |
| Long PDF or book analysis | Claude Sonnet 5.5 with citations | Claude Opus 5.5 with citations |
| Historiographical synthesis | Claude Opus 5.5 | Second independent synthesis using an OpenAI frontier model |
| Citation-entailment checking | OpenAI or Claude Sonnet, with source packet only | Human review |
| QID/entity proposal | Small structured-output model | Tool-verified reconciliation |
| Final prose report | Claude Opus or Perplexity `high` using only approved claims | Human editorial pass |

Avoid hard-coding the system around a marketing name such as “Deep Research.” Search quality depends on the entire system—retriever, browsing persistence, source controls, document parser, model, prompts, and verification policy—not on the base model alone. OpenAI's original BrowseComp results illustrate this: a browsing-enabled general model scored far below a purpose-built deep-research agent, showing that tool access without a persistent research policy is insufficient.[^20]

## Evidence from benchmarks

Public benchmarks provide useful signals but do not directly test ancient-history scholarship, source criticism, variant editions, or historiographical disagreement. BrowseComp measures locating hard-to-find facts across 1,266 browsing problems, while DeepResearch Bench evaluates PhD-level reports across 22 fields and includes a citation-trustworthiness framework.[^21][^20]

DeepResearch Bench reported the strongest citation-accuracy result for Perplexity Deep Research among the systems it evaluated, at 90.24%, but benchmark results describe a particular model-and-harness configuration rather than a permanent vendor ranking. A newer cross-domain benchmark, DRACO, reported strong factual, depth, presentation, and citation results from Perplexity's research harness with Claude models, but DRACO was introduced by Perplexity and uses an LLM-as-judge protocol, so it should be treated as supporting evidence rather than a neutral final verdict.[^22][^23][^21]

These benchmarks support the hybrid recommendation: the **research harness** materially affects performance, and a strong underlying reasoning model can improve the same harness. They do not eliminate the need for a project-specific historical evaluation set.

## Historical evaluation harness

Before committing production traffic, run the same 40–60 tasks through at least these configurations:

1. Perplexity `high`.
2. Perplexity `xhigh`.
3. Direct Claude Opus 5.5 with web search and web fetch.
4. Direct OpenAI frontier model with Responses API web search.
5. Hybrid Perplexity discovery plus Claude reading plus independent verification.

The test set should cover:

- **Known-fact retrieval:** offices, dates, battles, laws, treaties, and named individuals.
- **Needle-in-a-source:** facts buried in a long monograph, article, inscription catalog, or translated primary text.
- **Triangulation:** one primary account, one modern scholarly treatment, and one authority record.
- **Disagreement:** contested chronology, causation, identification, or interpretation.
- **Entity resolution:** homonymous people, changing place names, Roman naming ambiguity, and multilingual aliases.
- **Temporal normalization:** regnal, consular, relative, uncertain, and range-based dates.
- **Citation entailment:** whether the cited passage really supports the generated claim.
- **Structured extraction:** schema validity and preservation of uncertainty, stance, edition, page, and provenance.

A suitable weighted score is:

| Measure | Weight |
|---|---:|
| Citation resolves and is accessible | 15% |
| Citation entails the claim | 25% |
| Source authority and appropriateness | 15% |
| Factual accuracy | 15% |
| Coverage of relevant evidence | 10% |
| Contradiction and uncertainty handling | 10% |
| Structured-output validity | 5% |
| Cost and latency | 5% |

Require automatic failure for fabricated citations, nonexistent editions, or unsupported exact dates. Review disagreements blind, without showing evaluators which vendor produced each answer. Retain the full tool trace, search-result objects, prompts, model version, token usage, and rejected claims so changes in performance can be diagnosed.

## Implementation decision

The recommended production path is:

1. **Adopt Perplexity Agent API first** as the unified research gateway.
2. **Use `high` for the default research tier** and reserve `xhigh` for difficult or high-value work.
3. **Call Claude Opus 5.5 directly for document-intensive close reading** with citations enabled.
4. **Use OpenAI as the independent verifier and alternate retrieval path**, especially where MCP and tool breadth are decisive.
5. **Keep source acquisition, citation validation, entity resolution, and graph writes under application control.**
6. **Evaluate configurations on a Roman-Republic-centered gold set** before treating any vendor benchmark as decisive.

This architecture avoids lock-in because Perplexity already exposes multiple providers through one interface, while direct Anthropic and OpenAI adapters remain replaceable modules. More importantly, it makes the durable asset the project's evidence model, evaluation set, provenance graph, and source adapters—not whichever frontier model happens to lead in a given month.[^3][^1]

---

## References

1. [Migrate from Sonar to the Agent API](https://docs.perplexity.ai/docs/agent-api/migrate-from-sonar/overview) - Sonar Chat Completions support ended on September 27, 2026. Synchronous and streaming requests keep ...

2. [Citations - Claude Platform Docs](https://docs.anthropic.com/en/docs/build-with-claude/citations) - Ground Claude's responses in your source documents. Citations return the exact passages that support...

3. [Perplexity API](https://docs.perplexity.ai/docs/getting-started/overview) - Get web-grounded answers with built-in citations in one call, or access third-party models from Open...

4. [Context windows - Claude Platform Docs](https://docs.anthropic.com/en/docs/build-with-claude/context-windows) - The budget matches the context window available to your request: 1M tokens for Claude Sonnet 5 and C...

5. [PDF support - Claude Platform Docs](https://docs.anthropic.com/en/docs/build-with-claude/pdf-support) - To access Claude's full visual PDF understanding capabilities in the Converse API, you must enable c...

6. [Agent API](https://docs.perplexity.ai/docs/agent-api/quickstart) - Fetch the complete documentation index at: /llms.txt Use this file to discover all available pages b...

7. [Presets](https://docs.perplexity.ai/docs/agent-api/presets) - Explore Perplexity's Agent API presets - pre-configured setups optimized for different use cases wit...

8. [Web search | OpenAI API](https://platform.openai.com/docs/guides/tools-web-search) - Allow models to search the web for the latest information before generating a response.

9. [Introducing the Agents API - OpenAI](https://openai.com/index/introducing-the-agents-api/) - Build and launch cloud agents with the Agents API, a managed service powered by the Codex harness fo...

10. [New tools and features in the Responses API - OpenAI](https://openai.com/index/new-tools-and-features-in-the-responses-api/)

11. [Perplexity Search API](https://docs.perplexity.ai/docs/search/quickstart) - Perplexity's Search API returns real-time, ranked web results as structured data, with controls for ...

12. [Web Search](https://docs.perplexity.ai/docs/agent-api/tools/web-search) - The web_search tool lets the model search the web during an Agent API request. Use it for current in...

13. [Fetch URL Content](https://docs.perplexity.ai/docs/agent-api/tools/fetch-url-content) - The fetch_url tool fetches and extracts content from specific URLs during an Agent API request. Use ...

14. [Web search tool - Claude Platform Docs](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/web-search-tool) - The web search tool gives Claude direct access to real-time web content, The response includes citat...

15. [Academic and Scholarly Search](https://docs.perplexity.ai/docs/cookbook/articles/academic-search/README) - Use the Agent API's domain filtering to restrict search to academic sources, extract DOIs and paper ...

16. [Working with Files](https://docs.perplexity.ai/docs/agent-api/working-with-files) - Send documents to the Agent API, URLs cannot contain credentials or fragments and must use port 443....

17. [How to migrate from Sonar](https://docs.perplexity.ai/docs/agent-api/migrate-from-sonar/how-to) - The Agent API fast , low , medium , and high presets already include inline citations for source-bac...

18. [Streaming Citation Parsing](https://docs.perplexity.ai/docs/cookbook/articles/streaming-citations/README) - This guide shows how to consume streaming responses from the Agent API, extract citations as they ar...

19. [Models overview - Claude Platform Docs](https://docs.anthropic.com/en/docs/about-claude/models) - Claude is a family of state-of-the-art large language models. Pricing $10 / input MTok$50 / output M...

20. [BrowseComp: a benchmark for browsing agents](https://openai.com/index/browsecomp/) - Deep Research, an agent model explicitly trained for persistent web browsing. Deep Research perfectl...

21. [DeepResearch Bench: A Comprehensive Benchmark for ...](https://deepresearch-bench.github.io/) - DeepResearch Bench provides a comprehensive evaluation framework for Deep Research Agents across 22 ...

22. [DRACO: a Cross-Domain Benchmark for Deep Research ...](https://arxiv.org/html/2602.11685v1) - Perplexity Deep Research leads with a score of 70.5% (Opus 4.6) and 67.2% (Opus 4.5), followed by Ge...

23. [Evaluating Deep Research Performance in the Wild with ...](https://www.perplexity.ai/hub/blog/evaluating-deep-research-performance-in-the-wild-with-the-draco-benchmark) - Perplexity's Deep Research harness is model agnostic: as stronger agentic LLMs emerge, we will rerun...

