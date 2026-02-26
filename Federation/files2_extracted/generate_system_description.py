"""
generate_system_description.py
-------------------------------
Introspects the Chrystallum knowledge graph in Neo4j Aura and generates
a structured self-description stored back as a (:SystemDescription) node.

Architecture:
  1. INTROSPECT  — run Cypher queries against Aura to gather graph state
  2. GENERATE    — call configured LLM to produce narrative section
  3. WRITE BACK  — MERGE (:SystemDescription) onto (:Chrystallum) in Aura

The SystemDescription node contains structured JSON sections covering:
  - system identity (name, version, created)
  - federations (all 13, grouped by type/mode)
  - subject_concepts (counts, facet distribution, authority states)
  - entities (counts, facet distribution, crosswalk coverage)
  - epistemic_state (verified vs synthetic vs unknown)
  - pipeline_state (which steps have run, coverage metrics)
  - narrative (LLM-generated prose from structured data above)

LLM providers (configurable via --llm):
  - claude   : Anthropic API (claude-sonnet-4-6)
  - perplexity: Perplexity API (llama-3.1-sonar-large-128k-online)

Usage:
    # Generate and write to Aura
    python generate_system_description.py \\
        --neo4j-uri neo4j+s://YOUR_AURA_URI \\
        --neo4j-user neo4j \\
        --neo4j-password YOUR_PASSWORD \\
        --llm claude \\
        --anthropic-api-key YOUR_KEY

    # Perplexity instead
    python generate_system_description.py \\
        --neo4j-uri ... \\
        --llm perplexity \\
        --perplexity-api-key YOUR_KEY

    # Dry run — introspect and print, no write
    python generate_system_description.py \\
        --neo4j-uri ... \\
        --dry-run

    # Skip LLM — structured JSON only, no narrative
    python generate_system_description.py \\
        --neo4j-uri ... \\
        --no-narrative

Dependencies:
    pip install neo4j requests
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests


# ---------------------------------------------------------------------------
# Cypher introspection queries
# ---------------------------------------------------------------------------

QUERIES = {

    "system_identity": """
        MATCH (c:Chrystallum)
        RETURN
          c.name    AS name,
          c.version AS version,
          toString(c.created) AS created
        LIMIT 1
    """,

    "federations": """
        MATCH (fr:FederationRoot)-[:HAS_FEDERATION]->(f:Federation)
        RETURN
          f.name           AS name,
          f.type           AS type,
          f.mode           AS mode,
          f.coverage       AS coverage,
          f.coverage_type  AS coverage_type,
          f.license        AS license,
          f.entity_types   AS entity_types,
          f.federation_state AS federation_state,
          f.geographic_scope AS geographic_scope
        ORDER BY f.type, f.name
    """,

    "subject_concepts_summary": """
        MATCH (sc:SubjectConcept)
        RETURN
          count(sc)                                          AS total,
          count(sc.qid)                                      AS with_anchor,
          count(CASE WHEN sc.source = 'wikidata' THEN 1 END) AS wikidata_anchored,
          count(CASE WHEN sc.source = 'synthetic' THEN 1 END) AS synthetic,
          count(CASE WHEN sc.authority_federation_state = 'FS0_SYNTHETIC' THEN 1 END) AS fs0_synthetic,
          count(CASE WHEN sc.authority_federation_score = 100 THEN 1 END) AS authority_score_100,
          count(CASE WHEN sc.authority_jump_enabled = true THEN 1 END) AS authority_jump_enabled
        LIMIT 1
    """,

    "subject_concepts_by_level": """
        MATCH (sc:SubjectConcept)
        RETURN sc.level AS level, count(sc) AS count
        ORDER BY sc.level
    """,

    "subject_concepts_by_facet": """
        MATCH (sc:SubjectConcept)
        WHERE sc.primary_facet IS NOT NULL
        RETURN sc.primary_facet AS facet, count(sc) AS count
        ORDER BY count DESC
    """,

    "entities_summary": """
        OPTIONAL MATCH (e:Entity)
        RETURN
          count(e)                                                    AS total,
          count(e.primary_facet)                                      AS with_facet,
          count(e.trismegistos_id)                                    AS trismegistos_enriched,
          count(e.lgpn_id)                                            AS lgpn_enriched,
          count(CASE WHEN e.primary_facet = 'BIOGRAPHICAL' THEN 1 END) AS biographical,
          count(CASE WHEN e.primary_facet = 'GEOGRAPHIC'   THEN 1 END) AS geographic,
          count(CASE WHEN e.primary_facet = 'MILITARY'     THEN 1 END) AS military,
          count(CASE WHEN e.primary_facet = 'POLITICAL'    THEN 1 END) AS political,
          count(CASE WHEN e.primary_facet = 'INSTITUTIONAL' THEN 1 END) AS institutional
        LIMIT 1
    """,

    "member_of_summary": """
        OPTIONAL MATCH (e:Entity)-[r:MEMBER_OF]->(sc:SubjectConcept)
        RETURN
          count(r)                AS total_edges,
          count(DISTINCT e)       AS unique_entities,
          count(DISTINCT sc)      AS subject_concepts_populated
        LIMIT 1
    """,

    "subject_concepts_populated": """
        MATCH (sc:SubjectConcept)
        OPTIONAL MATCH (e:Entity)-[:MEMBER_OF]->(sc)
        WITH sc, count(e) AS member_count
        RETURN
          count(CASE WHEN member_count > 0 THEN 1 END)  AS populated,
          count(CASE WHEN member_count = 0 THEN 1 END)  AS empty,
          max(member_count)                              AS max_members,
          round(avg(member_count), 1)                   AS avg_members
        LIMIT 1
    """,

    "design_decisions": """
        OPTIONAL MATCH (dd:DesignDecision)
        RETURN
          dd.id         AS id,
          dd.decision   AS decision,
          dd.method     AS method,
          dd.conclusion AS conclusion,
          toString(dd.validated_at) AS validated_at
        ORDER BY dd.validated_at DESC
        LIMIT 10
    """,
}


# ---------------------------------------------------------------------------
# Neo4j introspection
# ---------------------------------------------------------------------------

def run_introspection(uri: str, user: str, password: str) -> dict:
    """Run all introspection queries and return structured results dict."""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("Error: pip install neo4j", file=sys.stderr)
        sys.exit(1)

    driver = GraphDatabase.driver(uri, auth=(user, password))
    results = {}

    try:
        with driver.session() as session:
            for key, query in QUERIES.items():
                try:
                    records = session.run(query).data()
                    results[key] = records
                    print(f"  ✓ {key}: {len(records)} record(s)")
                except Exception as e:
                    print(f"  ✗ {key}: {e}", file=sys.stderr)
                    results[key] = []
    finally:
        driver.close()

    return results


# ---------------------------------------------------------------------------
# Structured JSON assembly
# ---------------------------------------------------------------------------

def assemble_structured_description(raw: dict) -> dict:
    """
    Transform raw Cypher query results into a clean structured description dict.
    This is the canonical self-description — LLM narrative is derived from this.
    """
    now = datetime.now(timezone.utc).isoformat()

    # -- System identity --------------------------------------------------
    identity = raw.get("system_identity", [{}])[0]

    # -- Federations ------------------------------------------------------
    feds = raw.get("federations", [])
    fed_by_type: dict[str, list] = {}
    for f in feds:
        ftype = f.get("type", "unknown")
        fed_by_type.setdefault(ftype, []).append({
            "name":     f.get("name"),
            "mode":     f.get("mode"),
            "coverage": f.get("coverage"),
            "license":  f.get("license"),
            "state":    f.get("federation_state"),
        })

    # -- Subject concepts -------------------------------------------------
    sc_summary = raw.get("subject_concepts_summary", [{}])[0]
    sc_by_level = {r.get("level"): r.get("count")
                   for r in raw.get("subject_concepts_by_level", [])}
    sc_by_facet = {r.get("facet"): r.get("count")
                   for r in raw.get("subject_concepts_by_facet", [])}

    total_sc = sc_summary.get("total", 0)
    with_anchor = sc_summary.get("with_anchor", 0)
    anchor_coverage = round(with_anchor / total_sc * 100, 1) if total_sc else 0

    # -- Entities ---------------------------------------------------------
    ent = raw.get("entities_summary", [{}])[0]
    mem = raw.get("member_of_summary", [{}])[0]
    pop = raw.get("subject_concepts_populated", [{}])[0]

    total_entities = ent.get("total", 0)
    tm_enriched = ent.get("trismegistos_enriched", 0)
    lgpn_enriched = ent.get("lgpn_enriched", 0)

    # -- Epistemic state --------------------------------------------------
    epistemic = {
        "subject_concepts": {
            "total":                total_sc,
            "wikidata_anchored":    sc_summary.get("wikidata_anchored", 0),
            "synthetic":            sc_summary.get("synthetic", 0),
            "authority_score_100":  sc_summary.get("authority_score_100", 0),
            "anchor_coverage_pct":  anchor_coverage,
            "authority_jump_enabled": sc_summary.get("authority_jump_enabled", 0),
        },
        "entities": {
            "total":                total_entities,
            "with_facet_assigned":  ent.get("with_facet", 0),
            "trismegistos_enriched": tm_enriched,
            "lgpn_enriched":        lgpn_enriched,
            "prosopographic_coverage_pct": round(
                max(tm_enriched, lgpn_enriched) / total_entities * 100, 1
            ) if total_entities else 0,
        },
        "graph_completeness": {
            "subject_concepts_populated": pop.get("populated", 0),
            "subject_concepts_empty":     pop.get("empty", 0),
            "total_member_of_edges":      mem.get("total_edges", 0),
            "avg_members_per_subject":    pop.get("avg_members"),
            "max_members_per_subject":    pop.get("max_members"),
        },
    }

    # -- Design decisions -------------------------------------------------
    decisions = [
        {k: v for k, v in d.items() if v is not None}
        for d in raw.get("design_decisions", [])
        if d.get("id")
    ]

    # -- Assemble ---------------------------------------------------------
    description = {
        "generated_at":    now,
        "schema_version":  "1.0",

        "system": {
            "name":    identity.get("name", "Chrystallum Knowledge Graph"),
            "version": identity.get("version", "1.0"),
            "created": identity.get("created"),
        },

        "federations": {
            "total":      len(feds),
            "by_type":    fed_by_type,
            "modes_used": sorted(set(f.get("mode") for f in feds if f.get("mode"))),
        },

        "subject_concepts": {
            "total":          total_sc,
            "by_level":       sc_by_level,
            "by_facet":       sc_by_facet,
            "anchor_coverage_pct": anchor_coverage,
        },

        "entities": {
            "total":     total_entities,
            "by_facet": {
                "BIOGRAPHICAL":  ent.get("biographical", 0),
                "GEOGRAPHIC":    ent.get("geographic", 0),
                "MILITARY":      ent.get("military", 0),
                "POLITICAL":     ent.get("political", 0),
                "INSTITUTIONAL": ent.get("institutional", 0),
            },
            "member_of_edges": mem.get("total_edges", 0),
        },

        "epistemic_state": epistemic,

        "design_decisions": decisions,
    }

    return description


# ---------------------------------------------------------------------------
# LLM narrative generation
# ---------------------------------------------------------------------------

NARRATIVE_PROMPT_SYSTEM = """You are a knowledge architect. Given a structured JSON
description of a knowledge graph system, write a concise, precise self-description
of the system in 3-4 paragraphs.

Write as if the system is describing itself to a new agent or researcher connecting
for the first time. Be specific about numbers, coverage, and epistemic state.
Be honest about what is verified vs synthetic. Do not use marketing language.
Respond with plain prose only — no headers, no bullet points, no JSON."""

NARRATIVE_PROMPT_USER = """Here is the current state of the knowledge graph system.
Write a self-description based on this data:

{structured_json}"""


def generate_narrative_claude(
    structured: dict,
    api_key: str,
    model: str = "claude-sonnet-4-6",
) -> str:
    """Generate narrative using Anthropic Claude API."""
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 800,
        "system": NARRATIVE_PROMPT_SYSTEM,
        "messages": [{
            "role": "user",
            "content": NARRATIVE_PROMPT_USER.format(
                structured_json=json.dumps(structured, indent=2)
            )
        }]
    }
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"].strip()


def generate_narrative_perplexity(
    structured: dict,
    api_key: str,
    model: str = "llama-3.1-sonar-large-128k-online",
) -> str:
    """Generate narrative using Perplexity API (OpenAI-compatible)."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "temperature": 0.3,
        "max_tokens": 800,
        "messages": [
            {"role": "system", "content": NARRATIVE_PROMPT_SYSTEM},
            {"role": "user",   "content": NARRATIVE_PROMPT_USER.format(
                structured_json=json.dumps(structured, indent=2)
            )},
        ]
    }
    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def generate_narrative(
    structured: dict,
    llm: str,
    anthropic_api_key: Optional[str] = None,
    perplexity_api_key: Optional[str] = None,
) -> Optional[str]:
    """Dispatch to configured LLM provider."""
    if llm == "claude":
        if not anthropic_api_key:
            print("  [warn] --anthropic-api-key required for --llm claude", file=sys.stderr)
            return None
        print("  Calling Claude (claude-sonnet-4-6)...")
        return generate_narrative_claude(structured, anthropic_api_key)

    elif llm == "perplexity":
        if not perplexity_api_key:
            print("  [warn] --perplexity-api-key required for --llm perplexity", file=sys.stderr)
            return None
        print("  Calling Perplexity (llama-3.1-sonar-large-128k-online)...")
        return generate_narrative_perplexity(structured, perplexity_api_key)

    else:
        print(f"  [warn] Unknown LLM provider: {llm}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Write back to Aura
# ---------------------------------------------------------------------------

WRITE_QUERY = """
MATCH (c:Chrystallum)
MERGE (c)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
SET
  sd.generated_at         = datetime($generated_at),
  sd.generated_from_version = $system_version,
  sd.schema_version       = $schema_version,

  // Core sections as JSON strings (queryable via apoc.convert.fromJsonMap if needed)
  sd.system_json          = $system_json,
  sd.federations_json     = $federations_json,
  sd.subject_concepts_json = $subject_concepts_json,
  sd.entities_json        = $entities_json,
  sd.epistemic_state_json = $epistemic_state_json,
  sd.design_decisions_json = $design_decisions_json,

  // Key metrics as native properties (directly queryable without JSON parsing)
  sd.federation_count     = $federation_count,
  sd.subject_concept_count = $subject_concept_count,
  sd.entity_count         = $entity_count,
  sd.member_of_edge_count = $member_of_edge_count,
  sd.anchor_coverage_pct  = $anchor_coverage_pct,

  // LLM-generated narrative
  sd.narrative            = $narrative,
  sd.narrative_llm        = $narrative_llm,
  sd.narrative_generated_at = CASE WHEN $narrative IS NOT NULL
                               THEN datetime($generated_at)
                               ELSE sd.narrative_generated_at END
RETURN sd.generated_at AS written_at,
       sd.federation_count AS federations,
       sd.subject_concept_count AS subject_concepts,
       sd.entity_count AS entities
"""

STALE_CHECK_QUERY = """
MATCH (c:Chrystallum)
OPTIONAL MATCH (c)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
RETURN
  c.version AS current_version,
  sd.generated_from_version AS description_version,
  toString(sd.generated_at) AS last_generated,
  CASE
    WHEN sd IS NULL THEN true
    WHEN sd.generated_from_version <> c.version THEN true
    WHEN duration.between(sd.generated_at, datetime()).hours >= 24 THEN true
    ELSE false
  END AS is_stale
LIMIT 1
"""


def check_staleness(uri: str, user: str, password: str) -> dict:
    """Check if SystemDescription needs regeneration."""
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            result = session.run(STALE_CHECK_QUERY).data()
            return result[0] if result else {"is_stale": True}
    finally:
        driver.close()


def write_description(
    uri: str,
    user: str,
    password: str,
    structured: dict,
    narrative: Optional[str],
    narrative_llm: Optional[str],
):
    """Write SystemDescription node to Aura."""
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        with driver.session() as session:
            result = session.run(
                WRITE_QUERY,
                generated_at=structured["generated_at"],
                system_version=structured["system"].get("version", "1.0"),
                schema_version=structured.get("schema_version", "1.0"),

                system_json=          json.dumps(structured["system"]),
                federations_json=     json.dumps(structured["federations"]),
                subject_concepts_json=json.dumps(structured["subject_concepts"]),
                entities_json=        json.dumps(structured["entities"]),
                epistemic_state_json= json.dumps(structured["epistemic_state"]),
                design_decisions_json=json.dumps(structured.get("design_decisions", [])),

                federation_count=     structured["federations"]["total"],
                subject_concept_count=structured["subject_concepts"]["total"],
                entity_count=         structured["entities"]["total"],
                member_of_edge_count= structured["entities"]["member_of_edges"],
                anchor_coverage_pct=  structured["subject_concepts"]["anchor_coverage_pct"],

                narrative=      narrative,
                narrative_llm=  narrative_llm,
            ).data()

            if result:
                r = result[0]
                print(f"  ✓ SystemDescription written")
                print(f"    federations={r['federations']}  "
                      f"subject_concepts={r['subject_concepts']}  "
                      f"entities={r['entities']}")
    finally:
        driver.close()


# ---------------------------------------------------------------------------
# Staleness check query (for agents to call)
# ---------------------------------------------------------------------------

READ_DESCRIPTION_QUERY = """
MATCH (c:Chrystallum)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
RETURN
  toString(sd.generated_at)   AS generated_at,
  sd.federation_count         AS federation_count,
  sd.subject_concept_count    AS subject_concept_count,
  sd.entity_count             AS entity_count,
  sd.member_of_edge_count     AS member_of_edge_count,
  sd.anchor_coverage_pct      AS anchor_coverage_pct,
  sd.narrative                AS narrative,
  sd.narrative_llm            AS narrative_llm,
  sd.federations_json         AS federations_json,
  sd.epistemic_state_json     AS epistemic_state_json
LIMIT 1
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_structured(structured: dict):
    sep = "=" * 70
    print(f"\n{sep}")
    print("SYSTEM DESCRIPTION — STRUCTURED SECTIONS")
    print(sep)
    print(json.dumps(structured, indent=2))
    print(sep)


def main():
    parser = argparse.ArgumentParser(
        description="Generate and store Chrystallum self-description in Neo4j Aura"
    )
    # Neo4j connection
    parser.add_argument("--neo4j-uri",      required=True)
    parser.add_argument("--neo4j-user",     default="neo4j")
    parser.add_argument("--neo4j-password", default=None)

    # LLM config
    parser.add_argument("--llm", default="claude",
        choices=["claude", "perplexity"],
        help="LLM provider for narrative generation (default: claude)")
    parser.add_argument("--anthropic-api-key",  default=None,
        help="Anthropic API key (for --llm claude)")
    parser.add_argument("--perplexity-api-key", default=None,
        help="Perplexity API key (for --llm perplexity)")
    parser.add_argument("--no-narrative", action="store_true",
        help="Skip LLM narrative generation — structured JSON only")

    # Behaviour
    parser.add_argument("--dry-run", action="store_true",
        help="Introspect and print, do not write to Aura")
    parser.add_argument("--force", action="store_true",
        help="Regenerate even if description is not stale")
    parser.add_argument("--output", default=None,
        help="Optional: also save description JSON to file")

    args = parser.parse_args()

    if not args.neo4j_password:
        import getpass
        args.neo4j_password = getpass.getpass("Neo4j password: ")

    print(f"\n{'='*70}")
    print("CHRYSTALLUM SELF-DESCRIPTION GENERATOR")
    print(f"{'='*70}")
    print(f"Neo4j : {args.neo4j_uri}")
    print(f"LLM   : {'none (--no-narrative)' if args.no_narrative else args.llm}")
    print(f"Mode  : {'DRY RUN' if args.dry_run else 'WRITE'}")

    # Staleness check
    if not args.force and not args.dry_run:
        print(f"\nChecking staleness...")
        stale_info = check_staleness(args.neo4j_uri, args.neo4j_user, args.neo4j_password)
        is_stale = stale_info.get("is_stale", True)
        print(f"  Current version : {stale_info.get('current_version')}")
        print(f"  Last generated  : {stale_info.get('last_generated', 'never')}")
        print(f"  Stale           : {is_stale}")

        if not is_stale:
            print("\nDescription is current. Use --force to regenerate.")
            sys.exit(0)

    # Introspect
    print(f"\nIntrospecting graph...")
    raw = run_introspection(args.neo4j_uri, args.neo4j_user, args.neo4j_password)

    # Assemble structured description
    print(f"\nAssembling structured description...")
    structured = assemble_structured_description(raw)

    # Generate narrative
    narrative = None
    narrative_llm = None

    if not args.no_narrative and not args.dry_run:
        print(f"\nGenerating narrative ({args.llm})...")
        narrative = generate_narrative(
            structured,
            llm=args.llm,
            anthropic_api_key=args.anthropic_api_key,
            perplexity_api_key=args.perplexity_api_key,
        )
        if narrative:
            narrative_llm = args.llm
            print(f"  Narrative generated ({len(narrative)} chars)")

    # Print structured output
    print_structured(structured)

    if narrative:
        print(f"\n{'='*70}")
        print("NARRATIVE")
        print(f"{'='*70}")
        print(narrative)

    # Save to file if requested
    if args.output:
        output = {**structured, "narrative": narrative, "narrative_llm": narrative_llm}
        Path(args.output).write_text(json.dumps(output, indent=2), encoding="utf-8")
        print(f"\nSaved to: {args.output}")

    # Write to Aura
    if not args.dry_run:
        print(f"\nWriting to Aura...")
        write_description(
            uri=args.neo4j_uri,
            user=args.neo4j_user,
            password=args.neo4j_password,
            structured=structured,
            narrative=narrative,
            narrative_llm=narrative_llm,
        )

    print(f"\n{'='*70}")
    print("DONE")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
