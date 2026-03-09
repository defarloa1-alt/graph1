#!/usr/bin/env python3
"""
Domain Initiator (DI) -- SFA Training.

Heavy corpus training: fetches scholarly works from OpenAlex, Internet Archive,
and Wikidata P921, then runs Claude multi-turn reasoning over the literature
to produce SFA_TrainingInsight nodes persisted to Neo4j.

Architecture (Chrystallum Layer 2 → Layer 3 → Layer 4):
  Layer 2: Deterministic corpus fetch (OpenAlex API, IA API, SPARQL)
  Layer 3: Claude agent reasoning over corpus + candidates + graph
  Layer 4: Deterministic graph write (MERGE SFA_TrainingRun, CorpusWork, SFA_TrainingInsight)

Graph schema written:
  (:SFA_TrainingRun)-[:CONSULTED]->(:CorpusWork)
  (:SFA_TrainingRun)-[:PRODUCED]->(:SFA_TrainingInsight)
  (:SFA_TrainingInsight)-[:RELEVANT_TO_FACET]->(:Facet)
  (:SFA_TrainingInsight)-[:EVIDENCED_BY]->(:CorpusWork)
  (:CorpusWork)-[:RELEVANT_TO_FACET]->(:Facet)

Usage:
  # Train a single facet from its pack file:
  python scripts/agents/domain_initiator/train.py \
    --pack output/di_route/Q17167_military_pack.json

  # Train with custom keywords:
  python scripts/agents/domain_initiator/train.py \
    --pack output/di_route/Q17167_military_pack.json \
    --keywords "Roman army,legion,warfare,military reform"

  # Corpus fetch only (no Claude reasoning, no graph write):
  python scripts/agents/domain_initiator/train.py \
    --pack output/di_route/Q17167_military_pack.json \
    --fetch-only --output output/di_training/

  # Skip corpus fetch, use cached corpus file:
  python scripts/agents/domain_initiator/train.py \
    --pack output/di_route/Q17167_military_pack.json \
    --corpus output/di_training/Q17167_MILITARY_corpus.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

try:
    import anthropic
except ImportError:
    anthropic = None


# ---------------------------------------------------------------------------
# Facet keyword map — domain-specific search terms per facet
# ---------------------------------------------------------------------------

FACET_KEYWORDS: Dict[str, List[str]] = {
    "archaeological": ["archaeology", "excavation", "material culture", "artifacts", "stratigraphy"],
    "artistic": ["Roman art", "sculpture", "mosaic", "fresco", "portraiture"],
    "biographic": ["prosopography", "biography", "career", "cursus honorum", "life"],
    "communication": ["Roman roads", "postal system", "cursus publicus", "inscription", "epigraphy"],
    "cultural": ["Roman culture", "customs", "festivals", "spectacle", "gladiator"],
    "demographic": ["population", "census", "migration", "urbanization", "demography"],
    "diplomatic": ["diplomacy", "treaty", "alliance", "embassy", "foreign relations"],
    "economic": ["trade", "commerce", "currency", "denarius", "taxation", "economy"],
    "environmental": ["climate", "agriculture", "landscape", "deforestation", "environment"],
    "geographic": ["territory", "province", "colony", "geography", "boundaries"],
    "intellectual": ["philosophy", "rhetoric", "education", "Stoicism", "literature"],
    "linguistic": ["Latin", "language", "inscription", "epigraphy", "philology"],
    "military": ["army", "legion", "warfare", "battle", "military reform", "strategy"],
    "political": ["senate", "magistrate", "republic", "constitution", "governance", "law"],
    "religious": ["religion", "ritual", "temple", "priesthood", "augury", "divination"],
    "scientific": ["engineering", "aqueduct", "technology", "medicine", "astronomy"],
    "social": ["social class", "patrician", "plebeian", "slavery", "patronage", "family"],
    "technological": ["construction", "engineering", "concrete", "metallurgy", "technology"],
}


# ===========================================================================
# Layer 2: Corpus Fetch (deterministic, no LLM)
# ===========================================================================

def _reconstruct_abstract(inverted_index: dict) -> str:
    """Reconstruct abstract text from OpenAlex inverted index format."""
    if not inverted_index:
        return ""
    positions = []
    for word, indices in inverted_index.items():
        for idx in indices:
            positions.append((idx, word))
    positions.sort()
    return " ".join(w for _, w in positions)[:500]


def fetch_openalex(
    seed_label: str,
    facet_keywords: List[str],
    topic_id: Optional[str] = None,
    limit: int = 25,
) -> List[Dict]:
    """Fetch top-cited works from OpenAlex matching facet keywords.

    Uses title+abstract search with seed label as required term,
    plus topic filtering when available. Returns list of dicts with:
    work_id, title, authors, year, citation_count, abstract, doi, source_url.
    """
    url = "https://api.openalex.org/works"
    headers = {"User-Agent": "Chrystallum/1.0 (research project)", "Accept": "application/json"}
    select_fields = "id,title,authorships,publication_year,cited_by_count,abstract_inverted_index,doi,primary_location,open_access"

    all_works = []

    # Strategy 1: facet-specific keyword search, relevance-sorted
    # (most ancient history is closed-access, so no OA filter on pre-fetch;
    #  OA status is captured per-work so the SFA can fetch_url gold items)
    for kw in facet_keywords[:3]:
        search_term = f"{seed_label} {kw}"
        params = {
            "filter": f"title_and_abstract.search:{search_term}",
            "sort": "relevance_score:desc",
            "per_page": min(limit // 2, 25),
            "select": select_fields,
        }
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("results", []):
                all_works.append(_parse_openalex_work(item))
        except Exception as e:
            print(f"  [OpenAlex] Error for '{search_term}': {e}")
        time.sleep(0.3)  # rate limit

    # Strategy 2: topic filter if we have a topic_id, citation-sorted
    if topic_id:
        topic_short = topic_id.split("/")[-1] if "/" in topic_id else topic_id
        params = {
            "filter": f"primary_topic.id:{topic_short}",
            "sort": "cited_by_count:desc",
            "per_page": min(limit, 25),
            "select": select_fields,
        }
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("results", []):
                all_works.append(_parse_openalex_work(item))
        except Exception as e:
            print(f"  [OpenAlex] Topic query error: {e}")

    # Deduplicate by work_id, keep first occurrence (preserves relevance order)
    seen = set()
    deduped = []
    for w in all_works:
        wid = w["work_id"]
        if wid not in seen:
            seen.add(wid)
            deduped.append(w)

    works = deduped[:limit]
    print(f"  [OpenAlex] Fetched {len(works)} works ({len(all_works)} raw, {len(deduped)} unique)")
    return works


def _parse_openalex_work(item: dict) -> dict:
    """Parse a single OpenAlex work item into our schema."""
    authors = "; ".join(
        a.get("author", {}).get("display_name", "")
        for a in (item.get("authorships") or [])[:5]
    )
    abstract = _reconstruct_abstract(item.get("abstract_inverted_index") or {})
    oa_id = (item.get("id") or "").split("/")[-1]

    oa = item.get("open_access") or {}
    oa_url = oa.get("oa_url", "")

    return {
        "work_id": f"openalex:{oa_id}",
        "title": item.get("title", ""),
        "authors": authors,
        "year": item.get("publication_year"),
        "citation_count": item.get("cited_by_count", 0),
        "abstract": abstract,
        "doi": item.get("doi", ""),
        "source": "openalex",
        "source_url": item.get("id", ""),
        "is_oa": oa.get("is_oa", False),
        "oa_url": oa_url,
    }


def fetch_internet_archive(
    seed_label: str,
    facet_keywords: List[str],
    limit: int = 15,
) -> List[Dict]:
    """Fetch primary source texts from Internet Archive."""
    query = f'subject:("{seed_label}") AND ({" OR ".join(facet_keywords[:3])}) AND mediatype:texts'
    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": query,
        "fl[]": ["identifier", "title", "creator", "date", "description", "downloads"],
        "sort[]": "downloads desc",
        "rows": min(limit, 50),
        "page": 1,
        "output": "json",
    }
    headers = {"User-Agent": "Chrystallum/1.0 (research project)"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [InternetArchive] Error: {e}")
        return []

    works = []
    for doc in data.get("response", {}).get("docs", []):
        identifier = doc.get("identifier", "")
        works.append({
            "work_id": f"ia:{identifier}",
            "title": doc.get("title", ""),
            "authors": doc.get("creator", "") if isinstance(doc.get("creator"), str) else "; ".join(doc.get("creator", [])[:3]),
            "year": _parse_ia_year(doc.get("date", "")),
            "citation_count": doc.get("downloads", 0),
            "abstract": (doc.get("description", "") or "")[:500] if isinstance(doc.get("description"), str) else "",
            "doi": "",
            "source": "internet_archive",
            "source_url": f"https://archive.org/details/{identifier}",
        })

    print(f"  [InternetArchive] Fetched {len(works)} texts")
    return works


def _parse_ia_year(date_str: str) -> Optional[int]:
    """Extract year from IA date field."""
    if not date_str:
        return None
    try:
        return int(str(date_str)[:4])
    except (ValueError, TypeError):
        return None


def fetch_wikidata_p921(
    seed_qid: str,
    discipline_qids: List[str],
    limit: int = 20,
) -> List[Dict]:
    """Fetch scholarly works from Wikidata whose P921 (main subject) = seed or discipline.

    Requires P50 (author) to filter out journals, series, and stubs.
    Returns authority anchors (LCSH, FAST, OCLC) when available.
    """
    qids = [seed_qid] + discipline_qids[:4]
    values_clause = " ".join(f"wd:{q}" for q in qids)

    sparql = f"""
    SELECT DISTINCT ?work ?workLabel ?authorLabel ?year ?doi ?lcsh ?fast ?oclc WHERE {{
      VALUES ?subject {{ {values_clause} }}
      ?work wdt:P921 ?subject .
      ?work wdt:P50 ?author .
      OPTIONAL {{ ?work wdt:P244 ?lcsh }}
      OPTIONAL {{ ?work wdt:P2163 ?fast }}
      OPTIONAL {{ ?work wdt:P243 ?oclc }}
      OPTIONAL {{ ?work wdt:P577 ?date . BIND(YEAR(?date) AS ?year) }}
      OPTIONAL {{ ?work wdt:P356 ?doi }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    ORDER BY DESC(?year)
    LIMIT {min(limit, 50)}
    """

    endpoint = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "Chrystallum/1.0 (research project)",
        "Accept": "application/sparql-results+json",
    }

    try:
        resp = requests.get(endpoint, params={"query": sparql}, headers=headers, timeout=30)
        resp.raise_for_status()
        bindings = resp.json().get("results", {}).get("bindings", [])
    except Exception as e:
        print(f"  [WikidataP921] Error: {e}")
        return []

    works = []
    for b in bindings:
        work_uri = b.get("work", {}).get("value", "")
        qid = work_uri.split("/")[-1] if work_uri else ""
        title = b.get("workLabel", {}).get("value", "")
        # Skip items whose label is just their QID (no English label)
        if title.startswith("Q") and title[1:].isdigit():
            continue
        authority_ids = {}
        if "lcsh" in b:
            authority_ids["lcsh"] = b["lcsh"]["value"]
        if "fast" in b:
            authority_ids["fast"] = b["fast"]["value"]
        if "oclc" in b:
            authority_ids["oclc"] = b["oclc"]["value"]
        works.append({
            "work_id": f"wd:{qid}",
            "title": title,
            "authors": b.get("authorLabel", {}).get("value", ""),
            "year": int(b["year"]["value"]) if "year" in b and b["year"].get("value") else None,
            "citation_count": 0,
            "abstract": "",
            "doi": b.get("doi", {}).get("value", ""),
            "source": "wikidata_p921",
            "source_url": work_uri,
            "authority_ids": authority_ids,
        })

    print(f"  [WikidataP921] Fetched {len(works)} scholarly works")
    return works


def fetch_corpus_for_facet(
    pack: Dict,
    extra_keywords: Optional[List[str]] = None,
) -> List[Dict]:
    """Seed corpus: quick OpenAlex relevance search for orientation.

    This is intentionally thin — the SFA has research tools (search_scholarly,
    search_wikidata, fetch_url) and the full federation/corpus context from
    the pack. The LLM decides what to research, not the pre-fetch.
    """
    facet_key = pack["facet_key"].lower()
    domain = pack.get("domain_context", {})
    seed = domain.get("seed", {})
    seed_label = seed.get("label", "")

    # Build facet-specific keywords
    keywords = list(FACET_KEYWORDS.get(facet_key, [facet_key]))
    if extra_keywords:
        keywords = extra_keywords + keywords

    # Add top candidate labels as search terms
    candidates = pack.get("facet_delta", {}).get("candidates", [])
    top_labels = [c["label"] for c in candidates[:5] if c.get("role") == "primary"]
    keywords.extend(top_labels[:3])

    print(f"\nFetching seed corpus for {facet_key.upper()} (seed: {seed_label})")
    print(f"  Keywords: {', '.join(keywords[:6])}")

    # Extract OpenAlex topic_id from pack corpus_endpoints if available
    oa_endpoint = pack.get("corpus_endpoints", {}).get("endpoints", {}).get("open_alex", {})
    topic_id = oa_endpoint.get("topic_id")

    # OpenAlex relevance search — just enough to orient the SFA
    works = fetch_openalex(seed_label, keywords, topic_id=topic_id, limit=15)

    print(f"  Seed corpus: {len(works)} works (SFA will research further)")
    return works


# ===========================================================================
# Layer 3: Claude Training Reasoner
# ===========================================================================

TRAINING_SYSTEM_PROMPT = """You are SFA_{facet_key}, a specialized {facet_label} researcher training on the {facet_label} aspects of {seed_label} ({seed_qid}).

You have a small seed corpus of {works_count} works and {candidate_count} candidates from the DI harvest. Your task is DEEP TRAINING — actively research your domain, build scholarly grounding, and produce structured insights that persist in the graph.

YOU ARE A RESEARCHER. The seed corpus is just a starting point. You have tools to:

GRAPH TOOLS (read the live Neo4j knowledge graph):
- query_graph: Run Cypher MATCH queries against Chrystallum (existing nodes, relationships, decision tables, federation sources)
- get_threshold: Look up numeric thresholds (e.g. 'level2_child_overload')
- get_decision_table: Read decision table rows (e.g. 'D8', 'D12')

RESEARCH TOOLS (discover and read scholarly sources):
- search_scholarly: Search OpenAlex (gold OA academic papers), OAPEN (open-access books), or Internet Archive (digitized primary sources). Use targeted facet-specific queries.
- search_wikidata: Run SPARQL queries against Wikidata. Find scholarly works by subject (P921), find items with authority IDs (LCSH, FAST, OCLC), explore related entities.
- fetch_url: Read content from scholarly URLs — OA full texts, metadata pages, Perseus texts. Allowed domains: openalex, archive.org, oapen, doi.org, arxiv, jstor, perseus.tufts.edu, id.loc.gov, wikidata, openlibrary, hathitrust.

RESEARCH STRATEGY:
1. Review the seed corpus and your federation context (sources, authority keys, endpoints).
2. Ask: "What are the best open-access sources for {facet_label} aspects of {seed_label}?"
3. Use your tools to find them:
   - search_scholarly with OAPEN for open-access books on your facet
   - search_scholarly with OpenAlex for gold OA papers (these have full text)
   - search_scholarly with Internet Archive for digitized primary sources
   - search_wikidata to find works with LCSH/FAST/OCLC authority IDs about your topic
   - fetch_url to read Perseus texts, OA articles, archive.org primary sources
4. Use query_graph to check what already exists in the Chrystallum graph.
5. Build your insights from what you actually read, not just metadata.

DECOMPOSITION ASSESSMENT (CRITICAL):
After absorbing the corpus, you MUST ask yourself: "Is my domain manageable or does it need to decompose into smaller sub-agents?"

To answer this, check D12 threshold (use get_threshold for 'level2_child_overload' — currently 12).
Count the distinct conceptual sub-domains you've identified. If your facet covers more than
the threshold number of distinct sub-domains, you MUST propose a decomposition.

For example, a Military SFA might find it covers:
  - Wars & campaigns (Punic, Social, Gallic, Civil)
  - Military organization (legions, manipular system, cohorts)
  - Military reform (Marian reforms, professionalization)
  - Siege & engineering
  - Naval warfare
  - Recruitment & social aspects
  → 6 sub-domains, each with its own scholarly literature = manageable.
  → But if each sub-domain has 10+ concepts = total > 60, needs decomposition.

Your decomposition_assessment must include:
  - Whether to decompose (yes/no)
  - What sub-scopes you'd create (each with a label, scope description, and which candidates belong)
  - What threshold triggered it (or why it's manageable)
  - What each sub-agent would need that you don't have

GRAPH SCHEMA HINTS:
- SubjectConcept: label, subject_id, wikidata_qid, lcsh_id, seed_qid, concept_cipher
- Facet: label (e.g. 'Military')
- SYS_DecisionTable: table_id (e.g. 'D8_DETERMINE_SFA_facet_assignment')
- SYS_Threshold: name, value
- SYS_FederationSource: source_id, label, phase

YOUR OUTPUT must be a JSON object with these exact keys:

{{
  "training_summary": "2-3 sentence summary of what the corpus reveals about this facet",
  "key_works": [
    {{
      "work_id": "openalex:W...",
      "relevance": "high|medium|low",
      "facet_contribution": "What this work teaches about the facet"
    }}
  ],
  "insights": [
    {{
      "insight_type": "within_facet_addition|misroute|cross_facet_link|split_proposal|concept_refinement",
      "qid": "Q... (if known, else null)",
      "label": "Human-readable label",
      "confidence": 0.85,
      "evidence": "Which works and what evidence support this",
      "target_facet": "Only for cross_facet_link — which other facet",
      "reasoning": "Why this insight matters for the knowledge graph",
      "facet_weights": {{
        "archaeological": 0.0, "artistic": 0.0, "biographic": 0.0,
        "communication": 0.0, "cultural": 0.0, "demographic": 0.0,
        "diplomatic": 0.0, "economic": 0.0, "environmental": 0.0,
        "geographic": 0.0, "intellectual": 0.0, "linguistic": 0.0,
        "military": 0.0, "political": 0.0, "religious": 0.0,
        "scientific": 0.0, "social": 0.0, "technological": 0.0
      }},
      "pattern_tags": ["RP_CENTER_PERIPHERY_EXTRACTION (if applicable, else empty list)"],
      "role": "causal|descriptive|evaluative"
    }}
  ],
  "candidate_assessments": [
    {{
      "qid": "Q...",
      "label": "...",
      "verdict": "confirm|reject|reroute",
      "reroute_to": "facet key if rerouting",
      "evidence": "What the corpus says about this candidate"
    }}
  ],
  "discovered_works": [
    {{
      "work_id": "openalex:W... or oapen:... or ia:...",
      "title": "...",
      "authors": "...",
      "year": 2020,
      "source": "openalex|oapen|internet_archive",
      "source_url": "...",
      "is_oa": true,
      "relevance": "high|medium",
      "facet_contribution": "What this work teaches"
    }}
  ],
  "decomposition_assessment": {{
    "should_decompose": true,
    "reason": "Why this facet should or should not split",
    "sub_domain_count": 6,
    "threshold_used": "level2_child_overload=12",
    "total_concepts_estimated": 45,
    "sub_scopes": [
      {{
        "scope_key": "military_wars",
        "scope_label": "Wars & Campaigns",
        "scope_description": "Major wars, battles, and military campaigns of the Republic",
        "candidate_qids": ["Q124988", "Q596373", "Q75813"],
        "estimated_concepts": 15,
        "needs": "Temporal sequencing, DPRR commander positions, geographic theater mapping"
      }}
    ],
    "manageable_as_single": false
  }},
  "corpus_gaps": ["Topics still not well covered even after active research"],
  "facet_confidence": 0.92,
  "methodology_reflection": {{
    "fischer_checks": [
      {{
        "fallacy_id": "HOLIST_FALLACY",
        "status": "checked|triggered|revised",
        "applies_to": "insight or candidate label this check targets",
        "note": "Why this fallacy was checked and whether it applies"
      }}
    ],
    "digital_principles_applied": [
      {{
        "principle_id": "DP_...",
        "status": "applied",
        "note": "How this digital hermeneutic principle shaped your research"
      }}
    ],
    "repertoire_patterns": [
      {{
        "pattern_id": "RP_...",
        "pattern_label": "Contentious Assembly",
        "status": "existing",
        "candidate_qids": ["Q..."],
        "mechanisms": ["M_ESCALATION"],
        "evidence": "Which corpus works or sources support this pattern match",
        "confidence": 0.85
      }}
    ],
    "proposed_patterns": [
      {{
        "proposed_label": "Senatorial Obstruction",
        "scope_description": "Procedural blocking tactics in the Roman Senate",
        "analogous_to": "RP_CONTENTIOUS_ASSEMBLY",
        "mechanisms": ["M_ESCALATION", "M_BROKERAGE"],
        "candidate_qids": ["Q..."],
        "evidence": "What corpus evidence suggests this is a distinct repertoire pattern"
      }}
    ]
  }},
  "backbone_links": {{
    "subject_concepts": ["SubjectConcept labels or IDs this training connects to"],
    "temporal_anchors": [
      {{
        "year_start": -509,
        "year_end": -27,
        "label": "Roman Republic period",
        "evidence": "How this temporal range was determined from corpus"
      }}
    ],
    "geographic_anchors": [
      {{
        "place_label": "Rome",
        "place_qid": "Q220",
        "role": "primary|secondary",
        "evidence": "Why this place is relevant"
      }}
    ]
  }},
  "graph_deltas": [
    {{
      "op_type": "CREATE_CLAIM|UPDATE_CLAIM|ADJUST_EDGE|CREATE_DSC",
      "claim": {{
        "text": "The Social War arose from Italian demands for Roman citizenship.",
        "subject_concepts": ["SC label or ID"],
        "facet_weights": {{
          "archaeological": 0.0, "artistic": 0.0, "biographic": 0.0,
          "communication": 0.0, "cultural": 0.0, "demographic": 0.0,
          "diplomatic": 0.0, "economic": 0.0, "environmental": 0.0,
          "geographic": 0.0, "intellectual": 0.0, "linguistic": 0.0,
          "military": 0.0, "political": 0.0, "religious": 0.0,
          "scientific": 0.0, "social": 0.0, "technological": 0.0
        }},
        "pattern_tags": ["RP_CENTER_PERIPHERY_ENFRANCHISEMENT"],
        "role": "causal|descriptive|evaluative",
        "supporting_works": ["openalex:W..."],
        "confidence": 0.85
      }},
      "edge": {{
        "from_label": "source node label (for ADJUST_EDGE only)",
        "to_label": "target node label",
        "relation_type": "CAUSALLY_LINKED|RELATED_TO|BROADER_THAN",
        "weight_delta": 0.1,
        "justification": "Why this edge should be strengthened/weakened"
      }}
    }}
  ]
}}

IMPORTANT RULES:
1. Every insight needs evidence from specific works in the corpus — no unsourced claims.
2. Proposed additions (within_facet_addition) must include a Wikidata QID if you can identify one.
3. Cross-facet links must name the target facet and explain the relationship.
4. Split proposals should reference D12 threshold (child_overload=12).
5. Be conservative with confidence — 0.9+ only when multiple works agree.
6. Focus on what the CORPUS teaches, not general knowledge.

FACET WEIGHT VECTORS (REQUIRED on every insight and graph_delta claim):
Every insight and claim MUST include a facet_weights object with ALL 18 facets scored 0.0-1.0.
The 18 facets: archaeological, artistic, biographic, communication, cultural, demographic,
diplomatic, economic, environmental, geographic, intellectual, linguistic, military, political,
religious, scientific, social, technological. Your own facet should typically score highest.
Cross-facet insights should show significant weight on both facets involved.

SLIDING WINDOW EXTRACTION:
When reading corpus texts, use a sliding window approach for claim extraction:
- Read 2-4 sentence windows, sliding by 1 sentence
- For each window, ask: "Does this contain a factual claim, a causal assertion, or an evaluative judgment?"
- If YES, extract it as a graph_delta with op_type=CREATE_CLAIM
- Merge overlapping claims that reference the same entities/relationships
- Tag each claim with pattern_tags if it instantiates a reusable relational pattern
  (check the bridge patterns in the framework context: RP_CENTER_PERIPHERY_*, RP_CLIENT_PATRON_*, etc.)
- Score pattern density: prioritize text regions rich in reusable patterns over pure narrative

GRAPH DELTAS (REQUIRED):
In addition to insights, emit graph_deltas — typed operations that propose specific graph changes:
- CREATE_CLAIM: New claim with text, facet weights, pattern tags, and supporting works
- ADJUST_EDGE: Propose strengthening/weakening a relationship between concepts
- CREATE_DSC: Propose a new dynamic subject concept (weighted bag of existing SCs + pattern tags)
Include the claim or edge object as appropriate. Omit the other (set to null).

METHODOLOGY REFLECTION (REQUIRED):
You have three methodology frameworks to apply during your research:

1. FISCHER FALLACY CHECKS: Before finalizing insights, check each against the Fischer fallacies
   listed in the framework context below. If your phrasing triggers a fallacy (e.g. "the whole truth",
   "essence of", sweeping quantifiers like "all" or "never"), revise the insight. Report what you
   checked in fischer_checks with status: checked (clean), triggered (caught it), or revised (rewrote).

2. MILLIGAN DIGITAL PRINCIPLES: You are a digital researcher. Apply the DigitalPrinciple constraints
   — especially around source representativeness (digital archives over-represent certain periods/regions),
   OCR quality, and platform bias. Report which principles you consciously applied.

3. PRH REPERTOIRE PATTERNS: If your facet involves events, collective action, political contention,
   or social movements, check whether any candidates or insights map to existing RepertoirePattern
   nodes (listed in framework context). If you identify a pattern not in the graph, propose it in
   proposed_patterns with analogous_to referencing the closest existing pattern.

BACKBONE TETHERING (REQUIRED):
Your insights and patterns MUST connect to the Chrystallum backbone:
- SUBJECT BACKBONE: Reference which SubjectConcept(s) your training connects to. Use query_graph
  to find existing SubjectConcept nodes for your domain.
- TEMPORAL BACKBONE: If your facet has temporal dimensions, specify year ranges that connect to
  Year nodes in the graph (year_start/year_end in BCE as negative integers).
- GEOGRAPHIC BACKBONE: If your facet has geographic dimensions, specify Place nodes (with QIDs)
  that anchor your insights spatially. Use query_graph to find existing Place nodes.

TURN BUDGET: You have {max_turns} tool-call turns. Reserve the LAST 3 turns for producing your
JSON output. Do not spend all turns on research — budget roughly 70% research, 30% synthesis."""

TRAINING_USER_PROMPT = """## Seed Corpus ({works_count} works — your starting point, not your whole picture)

{corpus_section}

## Candidates from DI Harvest ({candidate_count} total)

{candidates_section}

## Federation Context

Your facet has these active federation sources (data already in the graph or queryable):
{federation_section}

Authority keys available for your domain:
{authority_section}

Corpus endpoints available (use search_scholarly and search_wikidata to query these):
{endpoints_section}

## Discipline Context

{disciplines_section}

---

You are SFA_{facet_key}. Your job is to RESEARCH, not just read.

1. START by reviewing the seed corpus and your federation context above.
2. RESEARCH: Use your tools to find the best sources for {facet_label} aspects of {seed_label}:
   - What open-access books exist? (search OAPEN)
   - What gold OA papers are available? (search OpenAlex)
   - What primary sources are digitized? (search Internet Archive, fetch Perseus)
   - What authority-anchored works exist in Wikidata? (search_wikidata for P921 + LCSH/FAST)
   - What does the Chrystallum graph already know? (query_graph)
3. READ what you find — use fetch_url on OA articles, archive.org texts, Perseus primary sources.
4. PRODUCE structured training output — insights, candidate assessments, gaps, decomposition.

Include ALL works you discovered via your research tools in discovered_works.

## Methodology Framework Context

{framework_section}"""


def _get_anthropic_client(api_key: Optional[str] = None):
    """Get Anthropic client."""
    if not anthropic:
        raise ImportError("anthropic package required. Run: pip install anthropic")
    key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not key:
        env_path = ROOT / ".env"
        if env_path.exists():
            for line in open(env_path):
                if line.startswith("ANTHROPIC_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not found")
    return anthropic.Anthropic(api_key=key)


def _handle_tool_call(driver, tool_name: str, tool_input: dict) -> str:
    """Execute a graph tool call during training reasoning."""
    try:
        if tool_name == "query_graph":
            cypher = tool_input.get("cypher", "")
            upper = cypher.upper().strip()
            if any(kw in upper for kw in ["CREATE", "MERGE", "DELETE", "SET ", "REMOVE", "DROP"]):
                return json.dumps({"error": "Only read-only queries allowed during training"})
            with driver.session() as session:
                result = session.run(cypher)
                rows = [dict(r) for r in result][:50]
                return json.dumps(rows, default=str, ensure_ascii=False)
        elif tool_name == "get_threshold":
            name = tool_input.get("name", "")
            with driver.session() as session:
                result = session.run(
                    "MATCH (t:SYS_Threshold {name: $name}) RETURN t", name=name
                )
                rec = result.single()
                if rec:
                    return json.dumps(dict(rec["t"]), default=str)
                return json.dumps({"error": f"Threshold '{name}' not found"})
        elif tool_name == "get_decision_table":
            table_id = tool_input.get("table_id", "")
            with driver.session() as session:
                result = session.run(
                    """MATCH (dt:SYS_DecisionTable) WHERE dt.table_id STARTS WITH $tid
                    OPTIONAL MATCH (dt)-[:HAS_ROW]->(r:SYS_DecisionRow)
                    RETURN dt, collect(r) AS rows""",
                    tid=table_id,
                )
                rec = result.single()
                if rec:
                    return json.dumps(
                        {"table": dict(rec["dt"]), "rows": [dict(r) for r in rec["rows"]]},
                        default=str,
                    )
                return json.dumps({"error": f"Decision table '{table_id}' not found"})
        elif tool_name == "search_scholarly":
            query = tool_input.get("query", "")
            source = tool_input.get("source", "openalex")
            limit_n = min(tool_input.get("limit", 10), 20)
            return _tool_search_scholarly(query, source, limit_n)

        elif tool_name == "search_wikidata":
            sparql_q = tool_input.get("sparql", "")
            limit_n = min(tool_input.get("limit", 20), 30)
            return _tool_search_wikidata(sparql_q, limit_n)

        elif tool_name == "fetch_url":
            url = tool_input.get("url", "")
            max_chars = min(tool_input.get("max_chars", 3000), 5000)
            return _tool_fetch_url(url, max_chars)

        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _tool_search_scholarly(query: str, source: str, limit: int) -> str:
    """Search for scholarly works across multiple sources."""
    headers = {"User-Agent": "Chrystallum/1.0 (research project)", "Accept": "application/json"}

    if source == "openalex":
        url = "https://api.openalex.org/works"
        params = {
            "filter": f"title_and_abstract.search:{query},open_access.oa_status:gold",
            "sort": "cited_by_count:desc",
            "per_page": limit,
            "select": "id,title,authorships,publication_year,cited_by_count,doi,open_access",
        }
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=20)
            resp.raise_for_status()
            results = []
            for item in resp.json().get("results", []):
                oa = item.get("open_access", {})
                authors = "; ".join(
                    a.get("author", {}).get("display_name", "")
                    for a in (item.get("authorships") or [])[:3]
                )
                results.append({
                    "work_id": f"openalex:{(item.get('id') or '').split('/')[-1]}",
                    "title": item.get("title", ""),
                    "authors": authors,
                    "year": item.get("publication_year"),
                    "citations": item.get("cited_by_count", 0),
                    "doi": item.get("doi", ""),
                    "is_oa": oa.get("is_oa", False),
                    "oa_url": oa.get("oa_url", ""),
                })
            return json.dumps(results, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"OpenAlex search error: {e}"})

    elif source == "oapen":
        # OAPEN — open access books
        url = "https://library.oapen.org/rest/search"
        params = {"query": query, "expand": "metadata", "limit": limit}
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=20)
            resp.raise_for_status()
            results = []
            for item in resp.json():
                meta = item.get("metadata", [])
                title = next((m["value"] for m in meta if m.get("key") == "dc.title"), "")
                author = next((m["value"] for m in meta if m.get("key") == "dc.contributor.author"), "")
                year = next((m["value"] for m in meta if m.get("key") == "dc.date.issued"), "")
                handle = item.get("handle", "")
                results.append({
                    "work_id": f"oapen:{handle}",
                    "title": title,
                    "authors": author,
                    "year": year[:4] if year else "",
                    "source_url": f"https://library.oapen.org/handle/{handle}",
                    "is_oa": True,
                })
            return json.dumps(results, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"OAPEN search error: {e}"})

    elif source == "internet_archive":
        url = "https://archive.org/advancedsearch.php"
        params = {
            "q": f'({query}) AND mediatype:texts',
            "fl[]": ["identifier", "title", "creator", "date", "downloads"],
            "sort[]": "downloads desc",
            "rows": limit,
            "page": 1,
            "output": "json",
        }
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=20)
            resp.raise_for_status()
            results = []
            for doc in resp.json().get("response", {}).get("docs", []):
                ident = doc.get("identifier", "")
                results.append({
                    "work_id": f"ia:{ident}",
                    "title": doc.get("title", ""),
                    "authors": doc.get("creator", ""),
                    "year": str(doc.get("date", ""))[:4],
                    "downloads": doc.get("downloads", 0),
                    "source_url": f"https://archive.org/details/{ident}",
                    "is_oa": True,
                })
            return json.dumps(results, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Internet Archive search error: {e}"})

    else:
        return json.dumps({"error": f"Unknown source: {source}. Use: openalex, oapen, internet_archive"})


def _tool_search_wikidata(sparql: str, limit: int) -> str:
    """Execute a SPARQL query against Wikidata and return results."""
    # Safety: only allow SELECT queries
    stripped = sparql.strip().upper()
    if not stripped.startswith("SELECT"):
        return json.dumps({"error": "Only SELECT queries allowed"})
    if "DELETE" in stripped or "INSERT" in stripped or "DROP" in stripped:
        return json.dumps({"error": "Write queries not allowed"})

    # Inject LIMIT if not present
    if "LIMIT" not in stripped:
        sparql = sparql.rstrip().rstrip(";") + f"\nLIMIT {min(limit, 30)}"

    endpoint = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "Chrystallum/1.0 (research project)",
        "Accept": "application/sparql-results+json",
    }
    try:
        resp = requests.get(endpoint, params={"query": sparql}, headers=headers, timeout=30)
        resp.raise_for_status()
        bindings = resp.json().get("results", {}).get("bindings", [])
        # Flatten bindings to simple dicts
        results = []
        for b in bindings[:limit]:
            row = {}
            for key, val in b.items():
                row[key] = val.get("value", "")
            results.append(row)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Wikidata SPARQL error: {e}"})


def _tool_fetch_url(url: str, max_chars: int) -> str:
    """Fetch a URL and return text content (truncated)."""
    # Safety: only allow scholarly / known-safe domains
    from urllib.parse import urlparse
    parsed = urlparse(url)
    allowed_domains = {
        "openalex.org", "api.openalex.org",
        "archive.org", "ia800", "ia600",
        "library.oapen.org", "oapen.org",
        "doi.org", "dx.doi.org",
        "academia.edu",
        "arxiv.org",
        "jstor.org",
        "perseus.tufts.edu",
        "scirp.org",
        "id.loc.gov",
        "wikidata.org", "query.wikidata.org",
        "openlibrary.org",
        "catalog.hathitrust.org",
    }
    domain = parsed.hostname or ""
    if not any(domain.endswith(d) for d in allowed_domains):
        return json.dumps({"error": f"Domain not in allowlist: {domain}. Allowed: {', '.join(sorted(allowed_domains))}"})

    headers = {
        "User-Agent": "Chrystallum/1.0 (research project)",
        "Accept": "text/html, application/json, text/plain",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")

        if "json" in content_type:
            return json.dumps(resp.json(), ensure_ascii=False, default=str)[:max_chars]
        elif "html" in content_type:
            # Strip HTML tags for readability
            import re
            text = re.sub(r'<script[^>]*>.*?</script>', '', resp.text, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:max_chars]
        else:
            return resp.text[:max_chars]
    except Exception as e:
        return json.dumps({"error": f"Fetch error: {e}"})


# Tools exposed to Claude during training
TRAINING_TOOLS = [
    {
        "name": "query_graph",
        "description": (
            "Execute a read-only Cypher MATCH query against the Chrystallum Neo4j graph. "
            "Returns up to 50 rows."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "cypher": {
                    "type": "string",
                    "description": "A read-only Cypher MATCH query.",
                }
            },
            "required": ["cypher"],
        },
    },
    {
        "name": "get_threshold",
        "description": "Get a specific SYS_Threshold value by name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Threshold name."}
            },
            "required": ["name"],
        },
    },
    {
        "name": "get_decision_table",
        "description": "Get all rows from a SYS_DecisionTable by table_id prefix (e.g. 'D8').",
        "input_schema": {
            "type": "object",
            "properties": {
                "table_id": {"type": "string", "description": "Decision table ID prefix (e.g. 'D8', 'D12')."}
            },
            "required": ["table_id"],
        },
    },
    {
        "name": "search_wikidata",
        "description": (
            "Run a SPARQL SELECT query against Wikidata. Use this to find scholarly works "
            "by subject (P921), items with authority IDs (P244=LCSH, P2163=FAST, P243=OCLC), "
            "or explore related entities. Only SELECT queries allowed, max 30 results. "
            "Example: find works about Roman military with LCSH IDs: "
            "SELECT ?work ?workLabel ?lcsh WHERE { ?work wdt:P921 wd:Q178561 . "
            "?work wdt:P244 ?lcsh . SERVICE wikibase:label { bd:serviceParam wikibase:language 'en' } }"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sparql": {
                    "type": "string",
                    "description": "SPARQL SELECT query to execute against Wikidata.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 20, max 30).",
                },
            },
            "required": ["sparql"],
        },
    },
    {
        "name": "search_scholarly",
        "description": (
            "Search for scholarly works. Sources: 'openalex' (gold OA academic papers — "
            "full text available, use fetch_url on oa_url), 'oapen' (open-access books), "
            "'internet_archive' (digitized texts, primary sources — all readable). "
            "Returns work metadata including title, authors, year, and OA URL when available."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g. 'Roman Republican army manipular legion').",
                },
                "source": {
                    "type": "string",
                    "enum": ["openalex", "oapen", "internet_archive"],
                    "description": "Which source to search.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 10, max 20).",
                },
            },
            "required": ["query", "source"],
        },
    },
    {
        "name": "fetch_url",
        "description": (
            "Fetch content from a URL. Only scholarly/known-safe domains are allowed: "
            "openalex.org, archive.org, oapen.org, doi.org, arxiv.org, jstor.org, "
            "perseus.tufts.edu, id.loc.gov, wikidata.org, openlibrary.org, hathitrust.org, "
            "academia.edu, scirp.org. Returns text content truncated to max_chars. "
            "Use this to read abstracts, OA full texts, or metadata pages."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to fetch.",
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Max characters to return (default 3000, max 5000).",
                },
            },
            "required": ["url"],
        },
    },
]


def _fetch_framework_context(driver) -> str:
    """Pre-fetch methodology framework nodes from graph for SFA prompt context."""
    sections = []
    with driver.session() as session:
        # Repertoire patterns + mechanisms
        rp_result = session.run("""
            MATCH (rp:RepertoirePattern)
            OPTIONAL MATCH (rp)-[:USES_MECHANISM]->(m:Mechanism)
            WITH rp, collect(m.id) AS mechanism_ids, collect(m.label) AS mechanism_labels
            RETURN rp.id AS id, rp.label AS label, mechanism_ids, mechanism_labels
            ORDER BY rp.id
        """)
        patterns = [dict(r) for r in rp_result]
        if patterns:
            lines = ["### Repertoire Patterns (PRH framework — existing graph nodes)"]
            for p in patterns:
                mechs = ", ".join(f"{mid} ({ml})" for mid, ml in zip(p["mechanism_ids"], p["mechanism_labels"])) if p["mechanism_ids"] else "none linked"
                lines.append(f"  - {p['id']}: {p['label']} → mechanisms: [{mechs}]")
            sections.append("\n".join(lines))

        # Fallacies
        f_result = session.run("""
            MATCH (f:Fallacy)
            OPTIONAL MATCH (f)-[:GUARDS_TASKTYPE]->(tt:TaskType)
            WITH f, collect(tt.label) AS task_types
            RETURN f.id AS id, f.label AS label, f.diagnostic_pattern AS pattern, task_types
            ORDER BY f.id
        """)
        fallacies = [dict(r) for r in f_result]
        if fallacies:
            lines = ["### Fischer Fallacies (check your insights against these)"]
            for f in fallacies:
                pattern = f.get("pattern") or ""
                tasks = ", ".join(f["task_types"]) if f["task_types"] else ""
                lines.append(f"  - {f['id']}: {f['label']} | pattern: \"{pattern}\" | guards: [{tasks}]")
            sections.append("\n".join(lines))

        # Digital principles
        dp_result = session.run("""
            MATCH (dp:DigitalPrinciple)
            RETURN dp.id AS id, dp.label AS label, dp.constraint AS constraint
            ORDER BY dp.id
        """)
        principles = [dict(r) for r in dp_result]
        if principles:
            lines = ["### Milligan Digital Principles (apply to your digital research)"]
            for dp in principles:
                constraint = dp.get("constraint") or ""
                lines.append(f"  - {dp['id']}: {dp['label']} | constraint: \"{constraint}\"")
            sections.append("\n".join(lines))

    if not sections:
        return "(No methodology framework nodes found in graph)"
    return "\n\n".join(sections)


def run_training_session(
    pack: Dict,
    corpus_works: List[Dict],
    driver,
    model: str = "claude-sonnet-4-20250514",
    max_turns: int = 40,
) -> Dict:
    """Run Claude multi-turn training over corpus + candidates.

    Returns structured training output (insights, assessments, etc.)
    """
    facet_key = pack["facet_key"]
    domain = pack.get("domain_context", {})
    seed = domain.get("seed", {})
    candidates = pack.get("facet_delta", {}).get("candidates", [])
    disciplines = pack.get("discipline_traversal", {}).get("disciplines", [])

    # Build corpus section for prompt
    corpus_lines = []
    for i, w in enumerate(corpus_works[:40], 1):  # cap at 40 works in prompt
        abstract_preview = (w.get("abstract") or "")[:200]
        corpus_lines.append(
            f"{i}. [{w['source']}] {w['title']} ({w.get('year', '?')})\n"
            f"   Authors: {w.get('authors', 'Unknown')}\n"
            f"   Citations: {w.get('citation_count', 0)} | DOI: {w.get('doi', 'n/a')}\n"
            f"   ID: {w['work_id']}\n"
            f"   Abstract: {abstract_preview}{'...' if len(abstract_preview) >= 200 else ''}"
        )

    # Build candidates section
    candidate_lines = []
    for c in candidates[:25]:
        signals = "; ".join(s.get("reason", "") for s in c.get("signals", [])[:3])
        candidate_lines.append(
            f"  - {c['label']} ({c['qid']}) role={c.get('role','?')} score={c.get('score',0)} | {signals}"
        )

    # Build disciplines section
    disc_lines = []
    for d in disciplines:
        auth = d.get("authority_ids", {})
        auth_str = ""
        if auth:
            auth_str = " | " + ", ".join(f"{k}={v}" for k, v in auth.items() if k != "P910")
        disc_lines.append(f"  - {d.get('label', '?')} ({d.get('qid', '?')}){auth_str}")

    # Build federation sources section
    fed_sources = pack.get("facet_delta", {}).get("federation_sources", [])
    if not fed_sources:
        fed_sources = pack.get("federation_sources", [])
    fed_lines = []
    for fs in fed_sources:
        fed_lines.append(f"  - {fs.get('label', fs.get('source_id', '?'))} (PID: {fs.get('pid', '?')})")

    # Build authority keys section
    corpus_ep = pack.get("corpus_endpoints", {})
    auth_keys = corpus_ep.get("authority_keys", {})
    auth_lines = []
    for key, vals in auth_keys.items():
        if vals:
            unique_vals = list(dict.fromkeys(vals))  # dedupe preserving order
            auth_lines.append(f"  - {key.upper()}: {', '.join(str(v) for v in unique_vals)}")

    # Build endpoints section
    endpoints = corpus_ep.get("endpoints", {})
    ep_lines = []
    for ep_key, ep_info in endpoints.items():
        status = ep_info.get("status", "?")
        count = ep_info.get("works_count")
        count_str = f" ({count} works)" if count else ""
        ep_lines.append(f"  - {ep_info.get('label', ep_key)}: {ep_info.get('description', '')}{count_str} [{status}]")

    # Pre-fetch methodology framework context
    framework_section = _fetch_framework_context(driver)

    system = TRAINING_SYSTEM_PROMPT.format(
        facet_key=facet_key.upper(),
        facet_label=facet_key.capitalize(),
        seed_label=seed.get("label", "?"),
        seed_qid=seed.get("qid", "?"),
        works_count=len(corpus_works),
        candidate_count=len(candidates),
        max_turns=max_turns,
    )

    user_prompt = TRAINING_USER_PROMPT.format(
        facet_key=facet_key.upper(),
        works_count=len(corpus_works),
        corpus_section="\n\n".join(corpus_lines) if corpus_lines else "(no works fetched)",
        candidate_count=len(candidates),
        candidates_section="\n".join(candidate_lines) if candidate_lines else "(none)",
        federation_section="\n".join(fed_lines) if fed_lines else "(none activated)",
        authority_section="\n".join(auth_lines) if auth_lines else "(none)",
        endpoints_section="\n".join(ep_lines) if ep_lines else "(none)",
        disciplines_section="\n".join(disc_lines) if disc_lines else "(none)",
        facet_label=facet_key.capitalize(),
        seed_label=seed.get("label", "?"),
        framework_section=framework_section,
    )

    print(f"\nRunning Claude training session ({model})...")
    print(f"  Corpus: {len(corpus_works)} works | Candidates: {len(candidates)}")

    client = _get_anthropic_client()
    messages = [{"role": "user", "content": user_prompt}]
    tool_log = []
    total_input = 0
    total_output = 0

    for turn in range(max_turns):
        response = client.messages.create(
            model=model,
            max_tokens=8192,
            system=system,
            tools=TRAINING_TOOLS,
            messages=messages,
        )
        total_input += response.usage.input_tokens
        total_output += response.usage.output_tokens

        if response.stop_reason == "tool_use":
            assistant_content = response.content
            tool_results = []
            for block in assistant_content:
                if block.type == "tool_use":
                    print(f"  [Turn {turn+1}] Tool: {block.name}({json.dumps(block.input)[:80]})")
                    result_str = _handle_tool_call(driver, block.name, block.input)
                    tool_log.append({
                        "tool": block.name,
                        "input": block.input,
                        "output_preview": result_str[:200],
                    })
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_str,
                    })
            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})
        else:
            # Final response — extract text
            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text

            print(f"  Training complete: {turn+1} turns, {total_input} in / {total_output} out tokens")

            # Parse JSON from response
            training_output = _extract_json(text)
            training_output["_meta"] = {
                "model": model,
                "turns": turn + 1,
                "tool_calls": tool_log,
                "usage": {"input_tokens": total_input, "output_tokens": total_output},
                "raw_response_length": len(text),
            }
            return training_output

    # max turns exceeded
    print(f"  WARNING: max turns ({max_turns}) exceeded")
    return {
        "error": "max_turns_exceeded",
        "_meta": {
            "model": model,
            "turns": max_turns,
            "tool_calls": tool_log,
            "usage": {"input_tokens": total_input, "output_tokens": total_output},
        },
    }


def _extract_json(text: str) -> Dict:
    """Extract JSON from Claude's response text (may be wrapped in markdown)."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    import re
    match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding JSON object boundaries
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    # Return raw text as fallback
    return {"raw_response": text, "parse_error": "Could not extract JSON"}


# ===========================================================================
# Layer 4: Graph Writer (deterministic, MERGE-based)
# ===========================================================================

def _insight_id(facet_key: str, insight_type: str, label: str, seed_qid: str) -> str:
    """Deterministic insight ID via SHA-256."""
    raw = f"{facet_key}|{insight_type}|{label}|{seed_qid}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def persist_training_to_graph(
    driver,
    pack: Dict,
    corpus_works: List[Dict],
    training_output: Dict,
) -> Dict:
    """Write training results to Neo4j.

    Creates:
      - SFA_TrainingRun node
      - CorpusWork nodes (MERGE by work_id)
      - SFA_TrainingInsight nodes
      - All relationships
    """
    facet_key = pack["facet_key"].upper()
    seed_qid = pack.get("domain_context", {}).get("seed", {}).get("qid", "")
    now = datetime.now(timezone.utc).isoformat()
    meta = training_output.get("_meta", {})

    run_id = f"train_{seed_qid}_{facet_key}_{now[:19].replace(':', '').replace('-', '')}"

    stats = {"run_id": run_id, "corpus_works_written": 0, "insights_written": 0, "errors": []}

    with driver.session() as session:
        # 1. Create SFA_TrainingRun
        session.run(
            """
            MERGE (tr:SFA_TrainingRun {run_id: $run_id})
            SET tr.facet_key = $facet_key,
                tr.seed_qid = $seed_qid,
                tr.model = $model,
                tr.works_consulted = $works_count,
                tr.insights_produced = $insights_count,
                tr.started_at = $now,
                tr.completed_at = $now,
                tr.status = 'completed',
                tr.token_usage_in = $tok_in,
                tr.token_usage_out = $tok_out,
                tr.training_summary = $summary,
                tr.facet_confidence = $confidence
            """,
            run_id=run_id,
            facet_key=facet_key,
            seed_qid=seed_qid,
            model=meta.get("model", "unknown"),
            works_count=len(corpus_works) + len(training_output.get("discovered_works", [])),
            insights_count=len(training_output.get("insights", [])),
            now=now,
            tok_in=meta.get("usage", {}).get("input_tokens", 0),
            tok_out=meta.get("usage", {}).get("output_tokens", 0),
            summary=training_output.get("training_summary", ""),
            confidence=training_output.get("facet_confidence", 0),
        )
        print(f"  Created SFA_TrainingRun: {run_id}")

        # 2. Create CorpusWork nodes + CONSULTED relationships
        key_works_map = {}
        for kw in training_output.get("key_works", []):
            key_works_map[kw.get("work_id", "")] = kw

        for w in corpus_works:
            try:
                kw_info = key_works_map.get(w["work_id"], {})
                session.run(
                    """
                    MERGE (cw:CorpusWork {work_id: $work_id})
                    SET cw.title = $title,
                        cw.authors = $authors,
                        cw.year = $year,
                        cw.citation_count = $citation_count,
                        cw.abstract = $abstract,
                        cw.source = $source,
                        cw.source_url = $source_url,
                        cw.doi = $doi,
                        cw.seed_qid = $seed_qid,
                        cw.facet_relevance = $relevance,
                        cw.facet_contribution = $contribution
                    WITH cw
                    MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                    MERGE (tr)-[:CONSULTED]->(cw)
                    WITH cw
                    MATCH (f:Facet) WHERE f.label = $facet_label
                    MERGE (cw)-[:RELEVANT_TO_FACET]->(f)
                    """,
                    work_id=w["work_id"],
                    title=w.get("title", ""),
                    authors=w.get("authors", ""),
                    year=w.get("year"),
                    citation_count=w.get("citation_count", 0),
                    abstract=w.get("abstract", ""),
                    source=w.get("source", ""),
                    source_url=w.get("source_url", ""),
                    doi=w.get("doi", ""),
                    seed_qid=seed_qid,
                    run_id=run_id,
                    facet_label=facet_key.capitalize(),
                    relevance=kw_info.get("relevance", ""),
                    contribution=kw_info.get("facet_contribution", ""),
                )
                stats["corpus_works_written"] += 1
            except Exception as e:
                stats["errors"].append(f"CorpusWork {w['work_id']}: {e}")

        print(f"  Wrote {stats['corpus_works_written']} CorpusWork nodes (pre-fetched)")

        # 2b. Create CorpusWork nodes for SFA-discovered works
        discovered = training_output.get("discovered_works", [])
        discovered_count = 0
        for dw in discovered:
            try:
                session.run(
                    """
                    MERGE (cw:CorpusWork {work_id: $work_id})
                    SET cw.title = $title,
                        cw.authors = $authors,
                        cw.year = $year,
                        cw.source = $source,
                        cw.source_url = $source_url,
                        cw.seed_qid = $seed_qid,
                        cw.is_oa = $is_oa,
                        cw.facet_relevance = $relevance,
                        cw.facet_contribution = $contribution,
                        cw.discovered_by = $agent_id
                    WITH cw
                    MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                    MERGE (tr)-[:CONSULTED]->(cw)
                    WITH cw
                    MATCH (f:Facet) WHERE f.label = $facet_label
                    MERGE (cw)-[:RELEVANT_TO_FACET]->(f)
                    """,
                    work_id=dw.get("work_id", ""),
                    title=dw.get("title", ""),
                    authors=dw.get("authors", ""),
                    year=dw.get("year"),
                    source=dw.get("source", ""),
                    source_url=dw.get("source_url", ""),
                    seed_qid=seed_qid,
                    is_oa=dw.get("is_oa", False),
                    relevance=dw.get("relevance", ""),
                    contribution=dw.get("facet_contribution", ""),
                    agent_id=f"SFA_{facet_key}",
                    run_id=run_id,
                    facet_label=facet_key.capitalize(),
                )
                discovered_count += 1
            except Exception as e:
                stats["errors"].append(f"DiscoveredWork {dw.get('work_id', '?')}: {e}")

        if discovered_count:
            print(f"  Wrote {discovered_count} CorpusWork nodes (SFA-discovered)")
        stats["corpus_works_written"] += discovered_count
        stats["discovered_works_written"] = discovered_count

        # 3. Create SFA_TrainingInsight nodes + relationships
        for insight in training_output.get("insights", []):
            try:
                iid = _insight_id(
                    facet_key,
                    insight.get("insight_type", ""),
                    insight.get("label", ""),
                    seed_qid,
                )
                session.run(
                    """
                    MERGE (ti:SFA_TrainingInsight {insight_id: $insight_id})
                    SET ti.facet_key = $facet_key,
                        ti.seed_qid = $seed_qid,
                        ti.insight_type = $insight_type,
                        ti.qid = $qid,
                        ti.label = $label,
                        ti.confidence = $confidence,
                        ti.evidence = $evidence,
                        ti.target_facet = $target_facet,
                        ti.reasoning = $reasoning,
                        ti.source = 'sfa_training',
                        ti.status = 'proposed',
                        ti.created_at = $now
                    WITH ti
                    MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                    MERGE (tr)-[:PRODUCED]->(ti)
                    WITH ti
                    MATCH (f:Facet) WHERE f.label = $facet_label
                    MERGE (ti)-[:RELEVANT_TO_FACET]->(f)
                    """,
                    insight_id=iid,
                    facet_key=facet_key,
                    seed_qid=seed_qid,
                    insight_type=insight.get("insight_type", ""),
                    qid=insight.get("qid"),
                    label=insight.get("label", ""),
                    confidence=insight.get("confidence", 0.75),
                    evidence=insight.get("evidence", ""),
                    target_facet=insight.get("target_facet"),
                    reasoning=insight.get("reasoning", ""),
                    now=now,
                    run_id=run_id,
                    facet_label=facet_key.capitalize(),
                )

                # Wire EVIDENCED_BY to specific corpus works mentioned in evidence
                evidence_text = insight.get("evidence", "")
                for w in corpus_works:
                    if w["work_id"] in evidence_text or (w.get("title") and w["title"][:30] in evidence_text):
                        session.run(
                            """
                            MATCH (ti:SFA_TrainingInsight {insight_id: $insight_id})
                            MATCH (cw:CorpusWork {work_id: $work_id})
                            MERGE (ti)-[:EVIDENCED_BY]->(cw)
                            """,
                            insight_id=iid,
                            work_id=w["work_id"],
                        )

                stats["insights_written"] += 1
            except Exception as e:
                stats["errors"].append(f"Insight {insight.get('label', '?')}: {e}")

        print(f"  Wrote {stats['insights_written']} SFA_TrainingInsight nodes")

        # 4. Persist candidate assessments as properties on a batch node
        assessments = training_output.get("candidate_assessments", [])
        if assessments:
            session.run(
                """
                MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                SET tr.candidate_assessments = $assessments,
                    tr.candidates_confirmed = $confirmed,
                    tr.candidates_rejected = $rejected,
                    tr.candidates_rerouted = $rerouted
                """,
                run_id=run_id,
                assessments=json.dumps(assessments, ensure_ascii=False),
                confirmed=len([a for a in assessments if a.get("verdict") == "confirm"]),
                rejected=len([a for a in assessments if a.get("verdict") == "reject"]),
                rerouted=len([a for a in assessments if a.get("verdict") == "reroute"]),
            )
            print(f"  Stored {len(assessments)} candidate assessments on TrainingRun")

        # 5. Store corpus gaps
        gaps = training_output.get("corpus_gaps", [])
        if gaps:
            session.run(
                """
                MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                SET tr.corpus_gaps = $gaps
                """,
                run_id=run_id,
                gaps=json.dumps(gaps, ensure_ascii=False),
            )

        # 6. Store decomposition assessment + create sub-scope nodes if needed
        decomp = training_output.get("decomposition_assessment", {})
        if decomp:
            session.run(
                """
                MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                SET tr.should_decompose = $should_decompose,
                    tr.decomposition_reason = $reason,
                    tr.sub_domain_count = $sub_count,
                    tr.total_concepts_estimated = $total_concepts,
                    tr.decomposition_assessment = $full_json
                """,
                run_id=run_id,
                should_decompose=decomp.get("should_decompose", False),
                reason=decomp.get("reason", ""),
                sub_count=decomp.get("sub_domain_count", 0),
                total_concepts=decomp.get("total_concepts_estimated", 0),
                full_json=json.dumps(decomp, ensure_ascii=False),
            )

            # Create SFA_SubScope nodes for each proposed sub-scope
            sub_scopes = decomp.get("sub_scopes", [])
            if sub_scopes and decomp.get("should_decompose"):
                for ss in sub_scopes:
                    scope_key = ss.get("scope_key", "")
                    session.run(
                        """
                        MERGE (ss:SFA_SubScope {scope_key: $scope_key, facet_key: $facet_key, seed_qid: $seed_qid})
                        SET ss.scope_label = $scope_label,
                            ss.scope_description = $scope_description,
                            ss.candidate_qids = $candidate_qids,
                            ss.estimated_concepts = $estimated_concepts,
                            ss.needs = $needs,
                            ss.status = 'proposed',
                            ss.created_at = $now
                        WITH ss
                        MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                        MERGE (tr)-[:PROPOSED_SUBSCOPE]->(ss)
                        WITH ss
                        MATCH (f:Facet) WHERE f.label = $facet_label
                        MERGE (ss)-[:SUBSCOPE_OF]->(f)
                        """,
                        scope_key=scope_key,
                        facet_key=facet_key,
                        seed_qid=seed_qid,
                        scope_label=ss.get("scope_label", ""),
                        scope_description=ss.get("scope_description", ""),
                        candidate_qids=json.dumps(ss.get("candidate_qids", []), ensure_ascii=False),
                        estimated_concepts=ss.get("estimated_concepts", 0),
                        needs=ss.get("needs", ""),
                        now=now,
                        run_id=run_id,
                        facet_label=facet_key.capitalize(),
                    )
                print(f"  Created {len(sub_scopes)} SFA_SubScope nodes (decomposition)")
                stats["sub_scopes_written"] = len(sub_scopes)
            elif not decomp.get("should_decompose"):
                print(f"  Decomposition: manageable as single agent")

        # 7. Persist methodology_reflection
        meth = training_output.get("methodology_reflection", {})
        if meth:
            # Store fischer checks and digital principles as JSON on TrainingRun
            session.run(
                """
                MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                SET tr.fischer_checks = $fischer,
                    tr.digital_principles_applied = $digital,
                    tr.methodology_reflection = $full_json
                """,
                run_id=run_id,
                fischer=json.dumps(meth.get("fischer_checks", []), ensure_ascii=False),
                digital=json.dumps(meth.get("digital_principles_applied", []), ensure_ascii=False),
                full_json=json.dumps(meth, ensure_ascii=False),
            )

            # Link to existing RepertoirePattern nodes
            rp_linked = 0
            for rp in meth.get("repertoire_patterns", []):
                pid = rp.get("pattern_id", "")
                if not pid:
                    continue
                session.run(
                    """
                    MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                    MATCH (rp:RepertoirePattern {id: $pattern_id})
                    MERGE (tr)-[r:INSTANCES_PATTERN]->(rp)
                    SET r.confidence = $confidence,
                        r.evidence = $evidence,
                        r.candidate_qids = $candidate_qids
                    """,
                    run_id=run_id,
                    pattern_id=pid,
                    confidence=rp.get("confidence", 0.7),
                    evidence=rp.get("evidence", ""),
                    candidate_qids=json.dumps(rp.get("candidate_qids", []), ensure_ascii=False),
                )
                rp_linked += 1

            # Create proposed RepertoirePattern nodes (status=proposed)
            rp_proposed = 0
            for pp in meth.get("proposed_patterns", []):
                proposed_label = pp.get("proposed_label", "")
                if not proposed_label:
                    continue
                prop_id = f"RP_PROPOSED_{hashlib.sha256(proposed_label.encode()).hexdigest()[:8].upper()}"
                session.run(
                    """
                    MERGE (rp:RepertoirePattern {id: $prop_id})
                    SET rp.label = $label,
                        rp.scope_description = $scope_desc,
                        rp.analogous_to = $analogous_to,
                        rp.status = 'proposed',
                        rp.proposed_by = $agent_id,
                        rp.evidence = $evidence,
                        rp.candidate_qids = $candidate_qids,
                        rp.created_at = $now
                    WITH rp
                    MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                    MERGE (tr)-[:PROPOSED_PATTERN]->(rp)
                    """,
                    prop_id=prop_id,
                    label=proposed_label,
                    scope_desc=pp.get("scope_description", ""),
                    analogous_to=pp.get("analogous_to", ""),
                    agent_id=f"SFA_{facet_key}",
                    evidence=pp.get("evidence", ""),
                    candidate_qids=json.dumps(pp.get("candidate_qids", []), ensure_ascii=False),
                    now=now,
                    run_id=run_id,
                )
                # Wire proposed mechanisms
                for mid in pp.get("mechanisms", []):
                    session.run(
                        """
                        MATCH (rp:RepertoirePattern {id: $prop_id})
                        MATCH (m:Mechanism {id: $mech_id})
                        MERGE (rp)-[:USES_MECHANISM]->(m)
                        """,
                        prop_id=prop_id,
                        mech_id=mid,
                    )
                rp_proposed += 1

            if rp_linked or rp_proposed:
                print(f"  Methodology: {rp_linked} pattern links, {rp_proposed} proposed patterns")
            stats["patterns_linked"] = rp_linked
            stats["patterns_proposed"] = rp_proposed

        # 8. Persist backbone_links
        backbone = training_output.get("backbone_links", {})
        if backbone:
            session.run(
                """
                MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                SET tr.backbone_links = $backbone_json
                """,
                run_id=run_id,
                backbone_json=json.dumps(backbone, ensure_ascii=False),
            )

            # Wire to SubjectConcept nodes if identifiable
            for sc_ref in backbone.get("subject_concepts", []):
                session.run(
                    """
                    MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                    MATCH (sc:SubjectConcept) WHERE sc.label = $sc_ref OR sc.subject_id = $sc_ref
                    MERGE (tr)-[:RELEVANT_TO_SUBJECT]->(sc)
                    """,
                    run_id=run_id,
                    sc_ref=sc_ref,
                )

            # Wire to Place nodes if geographic anchors provided
            for geo in backbone.get("geographic_anchors", []):
                qid = geo.get("place_qid", "")
                if qid:
                    session.run(
                        """
                        MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                        MATCH (p:Place) WHERE p.wikidata_qid = $qid
                        MERGE (tr)-[r:ANCHORED_TO_PLACE]->(p)
                        SET r.role = $role, r.evidence = $evidence
                        """,
                        run_id=run_id,
                        qid=qid,
                        role=geo.get("role", "secondary"),
                        evidence=geo.get("evidence", ""),
                    )

            bb_counts = {
                "subjects": len(backbone.get("subject_concepts", [])),
                "temporal": len(backbone.get("temporal_anchors", [])),
                "geographic": len(backbone.get("geographic_anchors", [])),
            }
            if any(bb_counts.values()):
                print(f"  Backbone: {bb_counts['subjects']} subjects, {bb_counts['temporal']} temporal, {bb_counts['geographic']} geographic")
            stats["backbone_links"] = bb_counts

        # 9. Persist graph_deltas
        deltas = training_output.get("graph_deltas", [])
        if deltas:
            # Store full deltas JSON on TrainingRun
            session.run(
                """
                MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                SET tr.graph_deltas = $deltas_json,
                    tr.graph_deltas_count = $count
                """,
                run_id=run_id,
                deltas_json=json.dumps(deltas, ensure_ascii=False),
                count=len(deltas),
            )

            # Persist CREATE_CLAIM deltas as SFA_Claim nodes
            claims_created = 0
            edges_proposed = 0
            for i, delta in enumerate(deltas):
                op = delta.get("op_type", "")
                if op == "CREATE_CLAIM" and delta.get("claim"):
                    claim = delta["claim"]
                    claim_id = f"{run_id}_claim_{i:03d}"
                    session.run(
                        """
                        MATCH (tr:SFA_TrainingRun {run_id: $run_id})
                        MERGE (cl:SFA_Claim {claim_id: $claim_id})
                        SET cl.text = $text,
                            cl.facet_weights = $facet_weights,
                            cl.pattern_tags = $pattern_tags,
                            cl.role = $role,
                            cl.confidence = $confidence,
                            cl.supporting_works = $works,
                            cl.created_at = $now,
                            cl.status = 'proposed'
                        MERGE (tr)-[:PRODUCED_CLAIM]->(cl)
                        """,
                        run_id=run_id,
                        claim_id=claim_id,
                        text=claim.get("text", ""),
                        facet_weights=json.dumps(claim.get("facet_weights", {}), ensure_ascii=False),
                        pattern_tags=json.dumps(claim.get("pattern_tags", []), ensure_ascii=False),
                        role=claim.get("role", "descriptive"),
                        confidence=claim.get("confidence", 0.7),
                        works=json.dumps(claim.get("supporting_works", []), ensure_ascii=False),
                        now=now,
                    )
                    # Wire pattern tags to RepertoirePattern nodes
                    for ptag in claim.get("pattern_tags", []):
                        session.run(
                            """
                            MATCH (cl:SFA_Claim {claim_id: $claim_id})
                            MATCH (rp:RepertoirePattern {id: $pattern_id})
                            MERGE (cl)-[:INSTANCES_PATTERN]->(rp)
                            """,
                            claim_id=claim_id,
                            pattern_id=ptag,
                        )
                    claims_created += 1
                elif op == "ADJUST_EDGE" and delta.get("edge"):
                    edges_proposed += 1

            if claims_created or edges_proposed:
                print(f"  Graph deltas: {claims_created} claims created, {edges_proposed} edge adjustments proposed")
            stats["claims_created"] = claims_created
            stats["edges_proposed"] = edges_proposed

    if stats["errors"]:
        print(f"  Errors: {len(stats['errors'])}")
        for e in stats["errors"][:5]:
            print(f"    - {e}")

    return stats


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="SFA Training: corpus fetch + Claude reasoning + graph persistence"
    )
    parser.add_argument("--pack", required=True, help="Path to facet pack JSON")
    parser.add_argument("--keywords", default=None, help="Comma-separated extra keywords")
    parser.add_argument("--fetch-only", action="store_true", help="Fetch corpus only, no reasoning or graph write")
    parser.add_argument("--corpus", default=None, help="Path to cached corpus JSON (skip fetch)")
    parser.add_argument("--output", default=None, help="Output directory for corpus/training files")
    parser.add_argument("--model", default="claude-sonnet-4-20250514", help="Claude model for training")
    parser.add_argument("--no-graph", action="store_true", help="Skip graph write (output JSON only)")
    args = parser.parse_args()

    pack_path = Path(args.pack)
    if not pack_path.exists():
        print(f"ERROR: pack file not found: {pack_path}")
        sys.exit(1)

    with open(pack_path) as f:
        pack = json.load(f)

    facet_key = pack["facet_key"].upper()
    seed_qid = pack.get("domain_context", {}).get("seed", {}).get("qid", "Q?")
    output_dir = Path(args.output) if args.output else ROOT / "output" / "di_training"
    output_dir.mkdir(parents=True, exist_ok=True)

    extra_keywords = None
    if args.keywords:
        extra_keywords = [k.strip() for k in args.keywords.split(",")]

    print("=" * 70)
    print(f"SFA TRAINING: {facet_key} | Seed: {seed_qid}")
    print("=" * 70)

    # --- Step 1: Corpus Fetch ---
    if args.corpus:
        corpus_path = Path(args.corpus)
        print(f"\nLoading cached corpus from {corpus_path}")
        with open(corpus_path, encoding="utf-8") as f:
            corpus_works = json.load(f)
        print(f"  Loaded {len(corpus_works)} works")
    else:
        corpus_works = fetch_corpus_for_facet(pack, extra_keywords)

        # Save corpus to file
        corpus_file = output_dir / f"{seed_qid}_{facet_key}_corpus.json"
        with open(corpus_file, "w", encoding="utf-8") as f:
            json.dump(corpus_works, f, indent=2, ensure_ascii=False)
        print(f"\nCorpus saved: {corpus_file}")

    if args.fetch_only:
        print("\n--fetch-only: stopping after corpus fetch.")
        return

    # --- Step 2: Connect to Neo4j ---
    from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD or ""))

    try:
        # --- Step 3: Claude Training Reasoning ---
        training_output = run_training_session(
            pack, corpus_works, driver, model=args.model, max_turns=40
        )

        # Save training output to file
        training_file = output_dir / f"{seed_qid}_{facet_key}_training.json"
        with open(training_file, "w", encoding="utf-8") as f:
            json.dump(training_output, f, indent=2, ensure_ascii=False)
        print(f"\nTraining output saved: {training_file}")

        # Print summary
        if "error" not in training_output:
            insights = training_output.get("insights", [])
            assessments = training_output.get("candidate_assessments", [])
            print(f"\n--- Training Summary ---")
            print(f"  {training_output.get('training_summary', '(no summary)')}")
            print(f"  Key works: {len(training_output.get('key_works', []))}")
            print(f"  Insights: {len(insights)}")
            for ins in insights:
                print(f"    [{ins.get('insight_type')}] {ins.get('label')} (conf={ins.get('confidence', '?')})")
            print(f"  Candidate assessments: {len(assessments)}")
            confirmed = len([a for a in assessments if a.get("verdict") == "confirm"])
            rejected = len([a for a in assessments if a.get("verdict") == "reject"])
            rerouted = len([a for a in assessments if a.get("verdict") == "reroute"])
            print(f"    Confirmed: {confirmed} | Rejected: {rejected} | Rerouted: {rerouted}")
            print(f"  Corpus gaps: {training_output.get('corpus_gaps', [])}")
            print(f"  Facet confidence: {training_output.get('facet_confidence', '?')}")

            # Methodology reflection
            meth = training_output.get("methodology_reflection", {})
            if meth:
                print(f"\n--- Methodology Reflection ---")
                fc = meth.get("fischer_checks", [])
                if fc:
                    triggered = len([c for c in fc if c.get("status") == "triggered"])
                    revised = len([c for c in fc if c.get("status") == "revised"])
                    print(f"  Fischer checks: {len(fc)} total, {triggered} triggered, {revised} revised")
                rps = meth.get("repertoire_patterns", [])
                if rps:
                    print(f"  Repertoire patterns matched: {len(rps)}")
                    for rp in rps:
                        print(f"    - {rp.get('pattern_id')}: {rp.get('pattern_label')} (conf={rp.get('confidence', '?')})")
                pps = meth.get("proposed_patterns", [])
                if pps:
                    print(f"  Proposed new patterns: {len(pps)}")
                    for pp in pps:
                        print(f"    - {pp.get('proposed_label')} (analogous to {pp.get('analogous_to', '?')})")

            # Backbone links
            backbone = training_output.get("backbone_links", {})
            if backbone:
                print(f"\n--- Backbone Links ---")
                scs = backbone.get("subject_concepts", [])
                if scs:
                    print(f"  Subjects: {', '.join(str(s) for s in scs)}")
                temps = backbone.get("temporal_anchors", [])
                if temps:
                    for t in temps:
                        print(f"  Temporal: {t.get('label', '?')} ({t.get('year_start', '?')} to {t.get('year_end', '?')})")
                geos = backbone.get("geographic_anchors", [])
                if geos:
                    for g in geos:
                        print(f"  Geographic: {g.get('place_label', '?')} ({g.get('place_qid', '?')}) [{g.get('role', '?')}]")

            # Graph deltas summary
            deltas = training_output.get("graph_deltas", [])
            if deltas:
                print(f"\n--- Graph Deltas ---")
                by_type = {}
                for d in deltas:
                    op = d.get("op_type", "UNKNOWN")
                    by_type[op] = by_type.get(op, 0) + 1
                for op, count in sorted(by_type.items()):
                    print(f"  {op}: {count}")
                # Show pattern tag distribution
                all_tags = []
                for d in deltas:
                    claim = d.get("claim") or {}
                    all_tags.extend(claim.get("pattern_tags", []))
                if all_tags:
                    tag_counts = {}
                    for t in all_tags:
                        tag_counts[t] = tag_counts.get(t, 0) + 1
                    print(f"  Pattern tags used: {len(tag_counts)} distinct")
                    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1])[:5]:
                        print(f"    - {tag}: {count}x")

            # Decomposition assessment
            decomp = training_output.get("decomposition_assessment", {})
            if decomp:
                should = decomp.get("should_decompose", False)
                print(f"\n--- Decomposition Assessment ---")
                print(f"  Should decompose: {should}")
                print(f"  Reason: {decomp.get('reason', '?')}")
                print(f"  Sub-domains: {decomp.get('sub_domain_count', '?')} | "
                      f"Estimated concepts: {decomp.get('total_concepts_estimated', '?')}")
                for ss in decomp.get("sub_scopes", []):
                    print(f"    [{ss.get('scope_key')}] {ss.get('scope_label')} "
                          f"(~{ss.get('estimated_concepts', '?')} concepts)")
                    print(f"      {ss.get('scope_description', '')}")
                    if ss.get("needs"):
                        print(f"      Needs: {ss['needs']}")
        else:
            print(f"\n  ERROR: {training_output.get('error')}")

        # --- Step 4: Graph Write ---
        if not args.no_graph and "error" not in training_output:
            print(f"\n--- Persisting to Neo4j ---")
            stats = persist_training_to_graph(driver, pack, corpus_works, training_output)
            print(f"\n  Run ID: {stats['run_id']}")
            print(f"  CorpusWork nodes: {stats['corpus_works_written']}")
            print(f"  Insights: {stats['insights_written']}")
            if stats["errors"]:
                print(f"  Errors: {len(stats['errors'])}")
        elif args.no_graph:
            print("\n--no-graph: skipping graph write.")

    finally:
        driver.close()

    print("\nDone.")


if __name__ == "__main__":
    main()
