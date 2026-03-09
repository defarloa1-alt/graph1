#!/usr/bin/env python3
"""
Subject Concept Facet Agents - 18 Specialized Agents for Subject Analysis

Each facet agent analyzes SubjectConcepts from its specialized perspective:
- ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, COMMUNICATION
- CULTURAL, DEMOGRAPHIC, DIPLOMATIC, ECONOMIC
- ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC
- MILITARY, POLITICAL, RELIGIOUS, SCIENTIFIC
- SOCIAL, TECHNOLOGICAL

Architecture:
- On-demand agent creation (not all 1,422 upfront)
- Stateless operation (bootstrap from Chrystallum)
- Claude API with tool-use for reasoning (agents can query the graph live)
- Wikidata SPARQL for enrichment
- Neo4j for persistence
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from neo4j import GraphDatabase
import requests

try:
    import anthropic
except ImportError:
    anthropic = None


# ============================================================================
# CANONICAL FACETS (from bootstrap_packet/facets.json)
# ============================================================================

CANONICAL_FACETS = [
    "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION",
    "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC",
    "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC",
    "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC",
    "SOCIAL", "TECHNOLOGICAL"
]

def _load_forbidden_facets(driver) -> list:
    """Load forbidden facets from SYS_Policy nodes (D-031)."""
    forbidden_policies = [
        "NoTemporalFacet", "NoClassificationFacet",
        "NoPatronageFacet", "NoGenealogicalFacet"
    ]
    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:SYS_Policy)
            WHERE p.name IN $names AND p.facet_key IS NOT NULL
            RETURN p.facet_key AS facet_key
            """,
            names=forbidden_policies
        )
        return [r["facet_key"] for r in result if r["facet_key"]]


def _load_sfa_proposal_confidence_default(driver) -> float:
    """Load sfa_proposal_confidence_default from SYS_Threshold (D8). Fallback 0.75."""
    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (t:SYS_Threshold {name: 'sfa_proposal_confidence_default'})
                RETURN t.value AS value
                LIMIT 1
                """,
            )
            rec = result.single()
            if rec and rec["value"] is not None:
                return float(rec["value"])
    except Exception:
        pass
    return 0.75


# ============================================================================
# BASE SUBJECT CONCEPT FACET AGENT
# ============================================================================

class SubjectConceptFacetAgent:
    """Base class for facet-specific subject concept agents"""
    
    # Claude tools exposed to the SFA agent during reasoning.
    # Each tool executes via the Python Neo4j driver — same data as MCP.
    GRAPH_TOOLS = [
        {
            "name": "query_graph",
            "description": (
                "Execute a read-only Cypher query against the Chrystallum Neo4j graph. "
                "Returns up to 50 rows. Use this to inspect decision tables, thresholds, "
                "federation sources, existing SubjectConcepts, relationship types, etc."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "cypher": {
                        "type": "string",
                        "description": "A read-only Cypher MATCH query (no CREATE/MERGE/DELETE).",
                    },
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
                    "name": {
                        "type": "string",
                        "description": "Threshold name (e.g. 'level2_child_overload').",
                    },
                },
                "required": ["name"],
            },
        },
        {
            "name": "get_decision_table",
            "description": "Get all rows from a SYS_DecisionTable by table_id.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "Decision table ID (e.g. 'D8', 'D12').",
                    },
                },
                "required": ["table_id"],
            },
        },
    ]

    def __init__(self,
                 facet_key: str,
                 facet_label: str,
                 neo4j_driver,
                 anthropic_api_key: Optional[str] = None,
                 model: str = "claude-sonnet-4-20250514"):
        """
        Initialize a facet-specific agent.

        Args:
            facet_key: Facet key (UPPERCASE, e.g., "MILITARY")
            facet_label: Facet label (e.g., "Military")
            neo4j_driver: Neo4j driver instance
            anthropic_api_key: Anthropic API key (falls back to ANTHROPIC_API_KEY env var)
            model: Claude model ID for reasoning
        """
        # Validate facet (D-031: forbidden facets from SYS_Policy)
        forbidden = _load_forbidden_facets(neo4j_driver)
        if facet_key not in CANONICAL_FACETS:
            raise ValueError(f"Invalid facet: {facet_key}. Must be one of {CANONICAL_FACETS}")
        if facet_key in forbidden:
            raise ValueError(f"Forbidden facet: {facet_key}")

        self.facet_key = facet_key
        self.facet_label = facet_label
        self.driver = neo4j_driver
        self.model = model

        # Claude API
        self._anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

        # Agent ID
        self.agent_id = f"SFA_{facet_key}"

        # System context (loaded on demand)
        self.federations = []
        self.entity_types = []
    
    def bootstrap_context(self):
        """Load system context from Chrystallum"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (sys:Chrystallum)
                OPTIONAL MATCH (sys)-[:HAS_FEDERATION_ROOT]->(fed_root)-[:HAS_FEDERATION]->(fed)
                OPTIONAL MATCH (sys)-[:HAS_ENTITY_ROOT]->(entity_root)-[:HAS_ENTITY_TYPE]->(et)
                RETURN 
                  collect(DISTINCT fed) AS federations,
                  collect(DISTINCT et) AS entity_types
            """)
            
            data = result.single()
            self.federations = [dict(f) for f in data['federations']]
            self.entity_types = [dict(et) for et in data['entity_types']]
    
    def accept_facet_pack(self, pack: Dict) -> Dict:
        """Accept a facet pack from the SCA router (DI pipeline step 3).

        The pack contains:
          - facet_delta: candidates with QIDs, scores, signals, federation sources
          - discipline_traversal: academic disciplines with authority IDs
          - corpus_endpoints: 14 sources with query keys and live counts
          - domain_context: seed, LCSH tether, sub-subjects

        Returns an SFA evaluation response with per-candidate assessments
        and optional proposals (within-facet additions, cross-facet links).
        """
        fd = pack["facet_delta"]
        domain = pack.get("domain_context", {})
        seed = domain.get("seed", {})

        candidates = fd.get("candidates", [])
        primary = [c for c in candidates if c.get("role") == "primary"]
        secondary = [c for c in candidates if c.get("role") != "primary"]

        # Build evaluation prompt with full context
        prompt = self._build_pack_evaluation_prompt(pack)

        # Run Claude agent with graph tool access
        evaluation = None
        if self._anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"):
            try:
                system = (
                    f"You are SFA_{self.facet_key}, a specialized {self.facet_label} "
                    f"historian evaluating candidates for the Chrystallum knowledge graph. "
                    f"You have tools to query the live Neo4j graph. Use them to check "
                    f"existing nodes, decision tables, and thresholds before making judgments.\n\n"
                    f"GRAPH SCHEMA HINTS (use these property names in Cypher):\n"
                    f"- SubjectConcept: label, subject_id, wikidata_qid, lcsh_id, seed_qid, concept_cipher\n"
                    f"- Facet: label (e.g. 'Military'), key is just the label\n"
                    f"- SYS_DecisionTable: table_id (e.g. 'D8'), label, description\n"
                    f"- SYS_Threshold: name, value, unit, description\n"
                    f"- SYS_FederationSource: source_id, label, phase\n"
                    f"- SYS_RelationshipType: rel_type, domain\n"
                    f"- Entity: label, qid, dprr_id\n"
                    f"- Place: label, pleiades_id, geonames_id\n\n"
                    f"IMPORTANT: Keep graph queries minimal. You already have the candidates "
                    f"in the prompt — focus on evaluating them, not re-discovering the graph. "
                    f"Return structured JSON."
                )
                evaluation = self._run_claude_agent(system, prompt)
            except Exception as e:
                evaluation = {"error": str(e)}

        return {
            "facet_key": self.facet_key,
            "agent_id": self.agent_id,
            "seed_qid": seed.get("qid"),
            "seed_label": seed.get("label"),
            "status": "evaluated" if evaluation and "error" not in evaluation else "pack_received",
            "candidate_count": len(candidates),
            "primary_count": len(primary),
            "secondary_count": len(secondary),
            "federation_sources": [s.get("source_id") for s in fd.get("federation_sources", [])],
            "disciplines": [
                d.get("label") for d in pack.get("discipline_traversal", {}).get("disciplines", [])
            ],
            "corpus_endpoints_available": len(
                pack.get("corpus_endpoints", {}).get("endpoints", {})
            ),
            "evaluation": evaluation,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _build_pack_evaluation_prompt(self, pack: Dict) -> str:
        """Build an evaluation prompt from a full facet pack."""
        fd = pack["facet_delta"]
        domain = pack.get("domain_context", {})
        seed = domain.get("seed", {})
        disciplines = pack.get("discipline_traversal", {}).get("disciplines", [])

        candidate_lines = []
        for c in fd.get("candidates", [])[:20]:  # cap at 20 for prompt size
            signals = "; ".join(s.get("reason", "") for s in c.get("signals", [])[:3])
            candidate_lines.append(
                f"  - {c['label']} ({c['qid']}) role={c.get('role','?')} score={c.get('score',0)} | {signals}"
            )

        disc_lines = [f"  - {d.get('label', '?')} ({d.get('qid', '?')})" for d in disciplines]

        return f"""You are SFA_{self.facet_key}, a specialized {self.facet_label} historian.

Domain seed: {seed.get('label', '?')} ({seed.get('qid', '?')})
Facet: {self.facet_label} -- {fd.get('evidence_summary', '')}

Candidates ({len(fd.get('candidates', []))} total, showing top 20):
{chr(10).join(candidate_lines) if candidate_lines else '  (none)'}

Academic disciplines:
{chr(10).join(disc_lines) if disc_lines else '  (none)'}

Tasks:
1. Which candidates are genuinely relevant to {self.facet_label}? Flag any mis-routed ones.
2. What within-facet concepts did the harvest MISS that should be added?
3. Any cross-facet relationships worth proposing?
4. Confidence that this facet is active for this domain (0-1)?

Provide structured JSON with keys: relevant_candidates, misrouted, proposed_additions, cross_facet_links, confidence.
"""

    def analyze_subject_concept(self, subject_concept_id: str) -> Dict:
        """
        Analyze a SubjectConcept from this facet's perspective
        
        Args:
            subject_concept_id: Subject concept ID
        
        Returns:
            Analysis dict with facet-specific insights
        """
        # Get subject concept from Neo4j
        with self.driver.session() as session:
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: $subject_id})
                RETURN sc
            """, subject_id=subject_concept_id)
            
            record = result.single()
            if not record:
                raise ValueError(f"SubjectConcept {subject_concept_id} not found")
            
            sc = dict(record['sc'])
        
        # Prepare facet-specific analysis prompt
        prompt = self._build_analysis_prompt(sc)

        # Run Claude agent with graph tool access
        system = (
            f"You are SFA_{self.facet_key}, a specialized {self.facet_label} "
            f"historian analyzing subjects for the Chrystallum knowledge graph. "
            f"You have tools to query the live Neo4j graph."
        )
        analysis = self._run_claude_agent(system, prompt)
        
        return {
            'subject_concept_id': subject_concept_id,
            'facet': self.facet_key,
            'agent_id': self.agent_id,
            'analysis': analysis,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _build_analysis_prompt(self, subject_concept: Dict) -> str:
        """Build facet-specific analysis prompt (override in subclasses)"""
        label = subject_concept.get('label', 'Unknown')
        qid = subject_concept.get('qid', 'Unknown')
        
        return f"""
        Analyze this subject concept from a {self.facet_label} perspective:
        
        Subject: {label} (Wikidata {qid})
        
        Questions:
        1. What are the key {self.facet_label.lower()} aspects of this subject?
        2. What related {self.facet_label.lower()} topics should be explored?
        3. What entities (people, events, places) are relevant from a {self.facet_label.lower()} viewpoint?
        4. What time periods are significant for {self.facet_label.lower()} analysis?
        5. Confidence in this facet being relevant (0-1)?
        
        Provide structured, scholarly analysis with sources.
        """
    
    # ------------------------------------------------------------------
    # Claude agentic loop with graph tools
    # ------------------------------------------------------------------

    def _get_anthropic_client(self):
        """Get Anthropic client, reading API key from env or .env file."""
        if not anthropic:
            raise ImportError("anthropic package required. Run: pip install anthropic")
        key = self._anthropic_api_key
        if not key:
            env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
            if os.path.exists(env_path):
                for line in open(env_path):
                    if line.startswith("ANTHROPIC_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
        if not key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or .env")
        return anthropic.Anthropic(api_key=key)

    def _handle_tool_call(self, tool_name: str, tool_input: dict) -> str:
        """Execute a graph tool call and return result as string."""
        try:
            if tool_name == "query_graph":
                cypher = tool_input.get("cypher", "")
                # Safety: reject mutations
                upper = cypher.upper().strip()
                if any(kw in upper for kw in ["CREATE", "MERGE", "DELETE", "SET ", "REMOVE", "DROP"]):
                    return json.dumps({"error": "Only read-only queries allowed"})
                with self.driver.session() as session:
                    result = session.run(cypher)
                    rows = [dict(r) for r in result][:50]
                    # Convert neo4j types to serializable
                    return json.dumps(rows, default=str, ensure_ascii=False)

            elif tool_name == "get_threshold":
                name = tool_input.get("name", "")
                with self.driver.session() as session:
                    result = session.run(
                        "MATCH (t:SYS_Threshold {name: $name}) RETURN t",
                        name=name,
                    )
                    rec = result.single()
                    if rec:
                        return json.dumps(dict(rec["t"]), default=str)
                    return json.dumps({"error": f"Threshold '{name}' not found"})

            elif tool_name == "get_decision_table":
                table_id = tool_input.get("table_id", "")
                with self.driver.session() as session:
                    result = session.run(
                        """
                        MATCH (dt:SYS_DecisionTable {table_id: $tid})
                        OPTIONAL MATCH (dt)-[:HAS_ROW]->(r:SYS_DecisionRow)
                        RETURN dt, collect(r) AS rows
                        """,
                        tid=table_id,
                    )
                    rec = result.single()
                    if rec:
                        dt = dict(rec["dt"])
                        rows = [dict(r) for r in rec["rows"]]
                        return json.dumps({"table": dt, "rows": rows}, default=str)
                    return json.dumps({"error": f"Decision table '{table_id}' not found"})

            else:
                return json.dumps({"error": f"Unknown tool: {tool_name}"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _run_claude_agent(self, system: str, user_prompt: str, max_turns: int = 20) -> Dict:
        """Run a Claude agentic loop with graph tool access.

        Claude can call query_graph / get_threshold / get_decision_table
        during reasoning. The loop continues until Claude produces a final
        text response (no more tool calls) or max_turns is reached.

        Returns dict with 'content' (final text), 'model', 'tool_calls' (list),
        and 'usage' (token counts).
        """
        client = self._get_anthropic_client()
        messages = [{"role": "user", "content": user_prompt}]
        tool_log = []
        total_input = 0
        total_output = 0

        for turn in range(max_turns):
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system,
                tools=self.GRAPH_TOOLS,
                messages=messages,
            )
            total_input += response.usage.input_tokens
            total_output += response.usage.output_tokens

            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Process all tool_use blocks
                assistant_content = response.content
                tool_results = []
                for block in assistant_content:
                    if block.type == "tool_use":
                        result_str = self._handle_tool_call(block.name, block.input)
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
                return {
                    "content": text,
                    "model": self.model,
                    "tool_calls": tool_log,
                    "usage": {"input_tokens": total_input, "output_tokens": total_output},
                }

        # max_turns exceeded — return what we have
        return {
            "content": "[max tool turns exceeded]",
            "model": self.model,
            "tool_calls": tool_log,
            "usage": {"input_tokens": total_input, "output_tokens": total_output},
        }
    
    def discover_related_entities(self, subject_concept_id: str, entity_type: str = "Human") -> List[Dict]:
        """
        Discover entities related to this subject concept from facet perspective
        
        Args:
            subject_concept_id: Subject concept ID
            entity_type: Entity type to discover (Human, Event, etc.)
        
        Returns:
            List of candidate entities
        """
        # Query Wikidata for entities
        sparql = self._build_wikidata_discovery_query(subject_concept_id, entity_type)
        results = self._query_wikidata_sparql(sparql)
        
        candidates = []
        for binding in results:
            item_qid = binding['item']['value'].split('/')[-1]
            candidates.append({
                'qid': item_qid,
                'label': binding.get('itemLabel', {}).get('value', ''),
                'description': binding.get('description', {}).get('value', ''),
                'facet': self.facet_key,
                'entity_type': entity_type
            })
        
        return candidates
    
    def _build_wikidata_discovery_query(self, subject_concept_id: str, entity_type: str) -> str:
        """Build Wikidata SPARQL query (override in subclasses for facet-specific queries)"""
        # Generic query - subclasses should override with facet-specific properties
        return f"""
        SELECT DISTINCT ?item ?itemLabel ?description
        WHERE {{
          ?item wdt:P31 wd:Q5 .  # instance of human
          ?item rdfs:label ?itemLabel .
          OPTIONAL {{ ?item schema:description ?description }}
          FILTER(LANG(?itemLabel) = "en")
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 100
        """
    
    def _query_wikidata_sparql(self, sparql_query: str) -> List[Dict]:
        """Query Wikidata SPARQL endpoint"""
        endpoint = "https://query.wikidata.org/sparql"
        
        headers = {
            'User-Agent': 'Chrystallum/1.0 (research project)',
            'Accept': 'application/sparql-results+json'
        }
        
        response = requests.get(
            endpoint,
            params={'query': sparql_query, 'format': 'json'},
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        return data['results']['bindings']
    
    def create_entity_proposal(self,
                              entity_type: str,
                              qid: str,
                              label: str,
                              properties: Dict,
                              confidence: Optional[float] = None) -> Dict:
        """
        Create entity proposal for this subject concept
        
        Args:
            entity_type: Entity type (Human, Event, etc.)
            qid: Wikidata QID
            label: Entity label
            properties: Additional properties
            confidence: Confidence score; if None, from SYS_Threshold sfa_proposal_confidence_default (D8)
        
        Returns:
            Proposal dict
        """
        if confidence is None:
            confidence = _load_sfa_proposal_confidence_default(self.driver)
        entity_id = f"{entity_type.lower()}_{qid.lower()}"
        
        proposal = {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'properties': {
                'entity_id': entity_id,
                'label': label,
                'qid': qid,
                **properties,
                'discovered_by_facet': self.facet_key,
                'discovered_by_agent': self.agent_id,
                'status': 'pending_approval',
                'proposed_at': datetime.utcnow().isoformat(),
                'confidence': confidence
            }
        }
        
        return proposal


# ============================================================================
# SPECIALIZED FACET AGENTS (Examples)
# ============================================================================

class MilitaryFacetAgent(SubjectConceptFacetAgent):
    """Military facet agent - analyzes warfare, battles, strategy"""
    
    def _build_analysis_prompt(self, subject_concept: Dict) -> str:
        label = subject_concept.get('label', 'Unknown')
        qid = subject_concept.get('qid', 'Unknown')
        
        return f"""
        Analyze this subject from a MILITARY perspective:
        
        Subject: {label} (Wikidata {qid})
        
        Questions:
        1. What military conflicts, battles, or campaigns are associated?
        2. What military leaders, commanders, or generals are relevant?
        3. What military technologies, tactics, or strategies were employed?
        4. What military institutions or organizations existed?
        5. What was the military significance of this subject in its historical context?
        6. Confidence that this subject has significant military aspects (0-1)?
        
        Provide detailed military analysis with scholarly sources.
        """
    
    def _build_wikidata_discovery_query(self, subject_concept_id: str, entity_type: str) -> str:
        # Military-specific Wikidata properties
        if entity_type == "Human":
            return """
            SELECT DISTINCT ?item ?itemLabel ?description
            WHERE {
              {?item wdt:P106 wd:Q4991371 .}  # occupation: military commander
              UNION
              {?item wdt:P106 wd:Q189290 .}   # occupation: military officer
              UNION
              {?item wdt:P31 wd:Q5 ; wdt:P241 ?military_unit .}  # served in military
              OPTIONAL { ?item schema:description ?description }
              SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }
            LIMIT 100
            """
        elif entity_type == "Event":
            return """
            SELECT DISTINCT ?item ?itemLabel ?description
            WHERE {
              {?item wdt:P31 wd:Q178561 .}  # instance of: battle
              UNION
              {?item wdt:P31 wd:Q198 .}     # instance of: war
              UNION
              {?item wdt:P31 wd:Q2001676 .} # instance of: military operation
              OPTIONAL { ?item schema:description ?description }
              SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }
            LIMIT 100
            """
        else:
            return super()._build_wikidata_discovery_query(subject_concept_id, entity_type)


class PoliticalFacetAgent(SubjectConceptFacetAgent):
    """Political facet agent - analyzes governance, rulers, states"""
    
    def _build_analysis_prompt(self, subject_concept: Dict) -> str:
        label = subject_concept.get('label', 'Unknown')
        qid = subject_concept.get('qid', 'Unknown')
        
        return f"""
        Analyze this subject from a POLITICAL perspective:
        
        Subject: {label} (Wikidata {qid})
        
        Questions:
        1. What political entities (states, empires, polities) are involved?
        2. What political leaders, rulers, or statesmen are relevant?
        3. What forms of government or political systems existed?
        4. What political events (elections, coups, reforms) occurred?
        5. What was the political significance of this subject?
        6. Confidence that this subject has significant political aspects (0-1)?
        
        Provide detailed political analysis with scholarly sources.
        """
    
    def _build_wikidata_discovery_query(self, subject_concept_id: str, entity_type: str) -> str:
        if entity_type == "Human":
            return """
            SELECT DISTINCT ?item ?itemLabel ?description
            WHERE {
              {?item wdt:P106 wd:Q82955 .}    # occupation: politician
              UNION
              {?item wdt:P106 wd:Q14212 .}    # occupation: head of state
              UNION
              {?item wdt:P39 ?position . ?position wdt:P279* wd:Q4164871 .}  # political office
              OPTIONAL { ?item schema:description ?description }
              SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }
            LIMIT 100
            """
        else:
            return super()._build_wikidata_discovery_query(subject_concept_id, entity_type)


class EconomicFacetAgent(SubjectConceptFacetAgent):
    """Economic facet agent - analyzes trade, currency, economic systems"""
    
    def _build_analysis_prompt(self, subject_concept: Dict) -> str:
        label = subject_concept.get('label', 'Unknown')
        qid = subject_concept.get('qid', 'Unknown')
        
        return f"""
        Analyze this subject from an ECONOMIC perspective:
        
        Subject: {label} (Wikidata {qid})
        
        Questions:
        1. What economic systems, trade networks, or markets existed?
        2. What currencies, commodities, or trade goods were important?
        3. What economic policies, reforms, or crises occurred?
        4. What economic institutions or merchant organizations were active?
        5. What was the economic impact of this subject?
        6. Confidence that this subject has significant economic aspects (0-1)?
        
        Provide detailed economic analysis with scholarly sources.
        """


# ============================================================================
# FACET AGENT FACTORY
# ============================================================================

class SubjectConceptAgentFactory:
    """Factory for creating facet-specific subject concept agents"""
    
    # Mapping of facet keys to specialized agent classes
    SPECIALIZED_AGENTS = {
        'MILITARY': MilitaryFacetAgent,
        'POLITICAL': PoliticalFacetAgent,
        'ECONOMIC': EconomicFacetAgent,
        # Add more specialized agents as needed
    }
    
    @classmethod
    def create_agent(cls,
                    facet_key: str,
                    neo4j_driver,
                    anthropic_api_key: Optional[str] = None,
                    model: str = "claude-sonnet-4-20250514") -> SubjectConceptFacetAgent:
        """
        Create a facet-specific agent.

        Args:
            facet_key: Facet key (UPPERCASE)
            neo4j_driver: Neo4j driver instance
            anthropic_api_key: Anthropic API key
            model: Claude model ID

        Returns:
            Facet agent instance
        """
        if facet_key not in CANONICAL_FACETS:
            raise ValueError(f"Invalid facet: {facet_key}")

        agent_class = cls.SPECIALIZED_AGENTS.get(facet_key, SubjectConceptFacetAgent)
        facet_label = facet_key.capitalize()

        return agent_class(
            facet_key=facet_key,
            facet_label=facet_label,
            neo4j_driver=neo4j_driver,
            anthropic_api_key=anthropic_api_key,
            model=model,
        )

    @classmethod
    def create_all_agents(cls,
                         neo4j_driver,
                         anthropic_api_key: Optional[str] = None,
                         model: str = "claude-sonnet-4-20250514") -> Dict[str, SubjectConceptFacetAgent]:
        """
        Create all 18 facet agents.

        Args:
            neo4j_driver: Neo4j driver instance
            anthropic_api_key: Anthropic API key
            model: Claude model ID

        Returns:
            Dict mapping facet keys to agent instances
        """
        agents = {}
        for facet_key in CANONICAL_FACETS:
            agents[facet_key] = cls.create_agent(
                facet_key=facet_key,
                neo4j_driver=neo4j_driver,
                anthropic_api_key=anthropic_api_key,
                model=model,
            )
        return agents


# ============================================================================
# MULTI-FACET SUBJECT ANALYZER
# ============================================================================

class MultiFacetSubjectAnalyzer:
    """Analyze a subject concept across multiple facets"""

    def __init__(self, neo4j_driver, anthropic_api_key: Optional[str] = None,
                 model: str = "claude-sonnet-4-20250514"):
        self.driver = neo4j_driver
        self.anthropic_api_key = anthropic_api_key
        self.model = model

    def analyze_subject_all_facets(self, subject_concept_id: str) -> Dict:
        """
        Analyze a subject concept across all 18 facets

        Args:
            subject_concept_id: Subject concept ID

        Returns:
            Combined analysis from all facets
        """
        agents = SubjectConceptAgentFactory.create_all_agents(
            neo4j_driver=self.driver,
            anthropic_api_key=self.anthropic_api_key,
            model=self.model,
        )
        
        analyses = {}
        for facet_key, agent in agents.items():
            print(f"Analyzing from {facet_key} perspective...")
            try:
                analysis = agent.analyze_subject_concept(subject_concept_id)
                analyses[facet_key] = analysis
            except Exception as e:
                print(f"  Error: {e}")
                analyses[facet_key] = {'error': str(e)}
        
        return {
            'subject_concept_id': subject_concept_id,
            'facet_analyses': analyses,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def analyze_subject_selected_facets(self,
                                       subject_concept_id: str,
                                       facet_keys: List[str]) -> Dict:
        """
        Analyze a subject concept from selected facets.

        Args:
            subject_concept_id: Subject concept ID
            facet_keys: List of facet keys to analyze

        Returns:
            Combined analysis from selected facets
        """
        analyses = {}
        for facet_key in facet_keys:
            agent = SubjectConceptAgentFactory.create_agent(
                facet_key=facet_key,
                neo4j_driver=self.driver,
                anthropic_api_key=self.anthropic_api_key,
                model=self.model,
            )
            
            print(f"Analyzing from {facet_key} perspective...")
            try:
                analysis = agent.analyze_subject_concept(subject_concept_id)
                analyses[facet_key] = analysis
            except Exception as e:
                print(f"  Error: {e}")
                analyses[facet_key] = {'error': str(e)}
        
        return {
            'subject_concept_id': subject_concept_id,
            'facet_analyses': analyses,
            'timestamp': datetime.utcnow().isoformat()
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD or "")
    )

    print("=" * 80)
    print("SUBJECT CONCEPT FACET AGENTS - Claude Agent Demo")
    print("=" * 80)
    print()

    print("Creating MILITARY facet agent (Claude + graph tools)...")
    military_agent = SubjectConceptAgentFactory.create_agent(
        facet_key="MILITARY",
        neo4j_driver=driver,
    )
    print(f"  Agent ID: {military_agent.agent_id}")
    print(f"  Model:    {military_agent.model}")
    print(f"  Tools:    {[t['name'] for t in military_agent.GRAPH_TOOLS]}")
    print()

    print("Creating all 18 facet agents...")
    all_agents = SubjectConceptAgentFactory.create_all_agents(neo4j_driver=driver)
    print(f"  Created {len(all_agents)} agents:")
    for facet_key in CANONICAL_FACETS:
        print(f"    - {facet_key}: {all_agents[facet_key].agent_id}")
    print()

    driver.close()
    print("Done.")
