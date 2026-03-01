Overall it’s strong: clear purpose, consistent tabular format, and it matches the conceptual docs well. A few focused comments and suggestions:

1. Strengths
Single source of truth: Having all node/relationship types in one place will be invaluable for debugging Cypher, onboarding, and agent design.
​

Good separation of layers: Federation survey nodes, canonical facets, core entities, SubjectConcepts, and temporal backbone are clearly distinguished, which mirrors your pipeline docs.

Provenance hints baked in: Including loaders and script names next to each type makes it easier to trace where data came from and how to regenerate it.

2. Gaps relative to the updated paper
Given what we just added in the “Beyond the Shelf” revision, I’d consider adding or clarifying:

Work / Bib nodes and OA fields

I don’t see a dedicated Work/BibWork node type here (you have WorldCat_Work as a survey node, but not the enriched Work node with ISBN, OA fields, curriculum links).
​

For alignment with the paper, I’d add a section like:

Work node: isbn, doi, title, authors, year, is_open_access, open_access_status, open_access_urls, open_access_source, plus relationships: CLASSIFIED_AS (→ LCC_Class), HAS_SUBJECT_HEADING (→ LCSH_Heading / FAST), ASSIGNED_IN (→ Discipline).

Discipline / Subject Domain nodes

There is a “Discipline (legacy)” section, but the new disciplines registry (cleaned majors/fields) and subject domains (e.g. SubjectDomain or Domain nodes) aren’t explicitly modeled here.

I’d make explicit:

Discipline (new registry): keyed by QID + label, linked to LCSH/FAST when present and to SubjectDomain nodes via :COVERS_DOMAIN or similar.

SubjectDomain: e.g. “Roman Republic,” with relationships to SubjectConcepts and to the temporal backbone.

Agent and framework nodes

SubjectConceptAgent and SubjectFrameworkAgent exist in the guides/contract but don’t appear here.

A minimal section for Agent / SCA_Agent / SFA_Agent with relationships like (:Agent)-[:ANALYZES]->(:SubjectConcept) and (:Agent)-[:PROPOSES]->(:Claim) would make the SCA/SFA loop concrete in the schema reference.

Claim / Proposal representation

The SFA contract talks about claims with provenance and confidence; here, those show up partly on relationships (e.g., POSITIONED_AS has a property bag) but there is no generic Claim pattern.

You might want a short section defining:

Either a Claim node type, or a standard property set (source, confidence, framework) that every SFA-created relationship must carry.

3. Internal consistency and naming
SubjectConcept IDs: In the paper, you use subjectid like subj_roman_republic_q17167; in this doc the property is subject_id and also concept_id.

I’d pick one canonical ID property (e.g., subject_id) and note that it’s also the unique key used by agents and Cypher.

Facet naming: Here you have CanonicalFacet with key and unique_id (e.g. FACET_ARCHAEOLOGICAL); in other docs you refer to Facet nodes keyed by uppercase facet names.

It’s good; just ensure your Cypher examples in other docs refer to CanonicalFacet.key consistently.

4. Relationship coverage
The reference is strong on “classification-side” relationships (MAPS_TO_FACET, BROADER_THAN, etc.), but lighter on entity ↔ SubjectConcept and Work ↔ SubjectConcept relationships which you need for routing.

I’d add a short subsection (even if partially speculative) documenting patterns like:

(e:Entity)-[:CLASSIFIED_BY]->(sc:SubjectConcept)

(w:Work)-[:ABOUT {facets: {...}}]->(sc:SubjectConcept)

That will make it much easier later to enforce consistent relationship names when you start wiring in the agent outputs.

5. Practical use
Finally, this file is long; to keep it usable:

Consider adding a very small “Quick Map” section at top listing:

Core discovery node labels: SubjectConcept, CanonicalFacet, LCC_Class, LCSH_Heading, Work, Human, Place, Event, Period.

Core relationships: MAPS_TO_FACET, CLASSIFIED_BY_LCC, HAS_LCSH_AUTHORITY, CLASSIFIED_BY, ABOUT, ASSIGNED_IN.

That gives you a mental “legend” before diving into the full table.

If you’d like, I can draft the missing Work and Discipline node sections (with OA fields and curriculum relationships) in exactly the same tabular format so you can drop them into this reference.

yes
Here are draft sections you can drop into NEO4J_NODE_AND_RELATIONSHIP_REFERENCE.md, matching your existing format.

3.x Work and Curriculum Nodes
Work
Bibliographic work node representing a distinct intellectual work (book, article, chapter), enriched from MARC, authority data, curricular data, and open-access services.

Property	Type	Required	Description
work_id	string	✓	Internal ID (e.g. work_9780198149185)
title	string	✓	Work title
subtitle	string		Subtitle
authors	list		List of author names (strings)
isbn	string		Primary ISBN (normalized, no dashes)
isbn_list	list		All known ISBNs
doi	string		DOI if present
publisher	string		Publisher name
publication_year	int		Year of publication
edition	string		Edition statement
language	string		ISO language code (e.g. en, la)
lccn	string		Library of Congress Control Number (if available)
oclc_number	string		OCLC number (if available)
entity_type	string		Work
is_open_access	boolean		True if at least one legitimate full-text OA copy is known
open_access_status	string		e.g. gold, green, bronze, free-to-read, closed, unknown
open_access_urls	list		List of canonical full-text URLs (OA landing pages, repository links, etc.)
open_access_source	list		Sources asserting OA (["OpenAlex","DOAB","OpenLibrary"])
created_from	string		Source of initial record (e.g. worldcat, open_syllabus, local)
last_enriched_at	string		ISO datetime of last OA / authority enrichment
Relationships:

(w:Work)-[:CLASSIFIED_AS]->(lcc:LCC_Class)
Work has an LCC classification (from MARC 050/090/082, or equivalent).

(w:Work)-[:HAS_LCSH_SUBJECT]->(lcsh:LCSH_Heading)
Work has one or more LCSH subject headings (from MARC 6XX).

(w:Work)-[:HAS_FAST_SUBJECT]->(fast:FAST_Subject)
Work has FAST subjects derived from LCSH.

(w:Work)-[:ABOUT {facets, source, confidence}]->(sc:SubjectConcept)
Work is about a SubjectConcept; facets may store a small facet-weight map, source records SCA/SFA, confidence is 0.0–1.0.

(w:Work)-[:ASSIGNED_IN {count, first_year, last_year}]->(d:Discipline)
Work appears in syllabi for a Discipline; count is number of syllabi or courses, temporal fields optional.

(w:Work)-[:HAS_AUTHOR]->(h:Human)
Work authored by a Human (when authority/person reconciliation is available).

(w:Work)-[:HAS_PUBLISHER]->(org:Organization)
Publisher relationship (optional, if publisher nodes are used).

Loaders / Enrichers:

Initial Work creation from WorldCat / Open Syllabus:

scripts/backbone/work/load_worldcat_works.py (example)

scripts/backbone/work/load_open_syllabus_works.py (example)

OA & authority enrichment:

scripts/enrichment/enrich_work_openaccess.py — OpenAlex/DOAB/OpenLibrary OA enrichment.

scripts/enrichment/enrich_work_marc_authorities.py — LCC/LCSH/FAST from MARC (via OCLC/LoC).

Discipline
Domain-level disciplinary node, derived from the cleaned discipline/major registry (excluding institutions, degrees, and occupations).

Property	Type	Required	Description
discipline_id	string	✓	Internal ID (e.g. disc_ancient_history)
qid	string		Wikidata QID for the discipline/field
label	string	✓	Discipline label (e.g. Ancient history, Roman law)
source	string		Origin of registry entry (wikidata_discipline_table, manual)
lcsh_id	string		LCSH heading ID if aligned
fast_id	string		FAST ID if aligned
ddc	string		Dewey numbers (pipe-separated) if applicable
lcc_class	string		Representative LCC class/range for this discipline
aat_id	string		Getty AAT ID if applicable
status	string		e.g. active, deprecated, candidate
entity_type	string		Discipline
Relationships:

(parent:Discipline)-[:BROADER_THAN]->(child:Discipline)
Optional discipline hierarchy.

(d:Discipline)-[:COVERS_DOMAIN]->(sd:SubjectDomain)
Discipline covers a SubjectDomain (e.g. Ancient history → Roman Republic).

(w:Work)-[:ASSIGNED_IN {count, first_year, last_year}]->(d:Discipline)
Work is assigned in this discipline (from Open Syllabus or similar).

(d:Discipline)-[:ALIGNED_WITH_LCSH]->(lcsh:LCSH_Heading)
Discipline mapped to an LCSH heading.

(d:Discipline)-[:ALIGNED_WITH_FAST]->(fast:FAST_Subject)
Discipline mapped to a FAST subject.

Loader:

scripts/backbone/discipline/load_disciplines_registry.py

Input: cleaned discipline_majors_consolidated_disciplines_filtered.csv (disciplines-only registry).

Behavior: creates Discipline nodes, links to LCSH/FAST/LCC when IDs present, optional broader/narrower links from CSV.
​

SubjectDomain
High-level subject region (e.g. Roman Republic, Roman law) that links disciplines, SubjectConcepts, and temporal/geographic scopes.

Property	Type	Required	Description
domain_id	string	✓	Internal ID (e.g. domain_roman_republic)
label	string	✓	Domain label (e.g. Roman Republic)
description	string		Narrative description
temporal_scope	string		e.g. -0509/-0027 (ISO-like interval)
geographic_scope	string		Free-text or coded geographic scope
primary_lcc	string		Primary LCC range(s) (e.g. DG241-269, KJA190-2152)
status	string		e.g. active, experimental
entity_type	string		SubjectDomain
Relationships:

(sd:SubjectDomain)-[:HAS_SUBJECT_CONCEPT]->(sc:SubjectConcept)
SubjectConcepts that constitute this domain.

(d:Discipline)-[:COVERS_DOMAIN]->(sd:SubjectDomain)
Disciplines that commonly encompass this domain.

(sd:SubjectDomain)-[:ALIGNED_WITH_LCC]->(lcc:LCC_Class)
Domain anchored to major LCC ranges.

(sd:SubjectDomain)-[:OCCURS_DURING]->(p:Period)
Domain linked to temporal backbone.

Loader / Bootstrap:

scripts/backbone/domain/bootstrap_subject_domains.py

Creates SubjectDomain nodes from configuration (e.g. JSON/YAML listing domains, temporal and LCC anchors).

Links to initial SubjectConcept anchors (e.g. Q17167 Roman Republic).
​

If you’d like, I can also draft a short Agent / Claim section in the same style to complete the SCA/SFA representation.

yes
Here are matching sections for Agents and Claims you can append to the reference.

5. Agent and Claim Nodes
Agent
Abstract agent node for automated actors operating on the graph (Subject Concept Agents, Subject Framework Agents, and specialized facet agents).

Property	Type	Required	Description
agent_id	string	✓	Unique ID (e.g. SCA_holistic_v1, SFA_polybian_v1)
label	string	✓	Human-readable label
agent_type	string	✓	SCA, SFA, FacetAgent, WorkflowAgent, etc.
facet_key	string		For facet agents, canonical facet key (e.g. MILITARY)
framework_key	string		For SFAs, framework identifier (e.g. polybian, clash_civ)
version	string		Agent version (e.g. 1.0.0)
provider	string		LLM provider or engine (perplexity, openai, rule_based)
config_ref	string		Path or ID for config/prompt used
status	string		active, deprecated, experimental
created_at	string		ISO datetime
updated_at	string		ISO datetime
entity_type	string		Agent
Relationships:

(agent:Agent)-[:ANALYZES]->(sc:SubjectConcept)
Agent analyzes a SubjectConcept (SCA or FacetAgent runs).

(agent:Agent)-[:ANALYZES]->(w:Work)
Agent analyzes a Work (e.g. for Work→SubjectConcept links).

(agent:Agent)-[:PRODUCED]->(c:Claim)
Agent produced a Claim node.

(registry:AgentRegistry)-[:REGISTERS]->(agent:Agent)
Agent registered in an AgentRegistry node (if present).

Bootstrap:

scripts/agents/bootstrap_agents.cypher

Creates core SCA and SFA agent nodes from configuration.

Claim
Generic node capturing an interpretive or empirical assertion made by an agent about a relationship or classification. Claims can be attached to edges or represent higher-level statements.

Property	Type	Required	Description
claim_id	string	✓	Unique ID (e.g. claim_sc_subjromanarmy_sfa_polybian_001)
claim_type	string	✓	e.g. ABOUT, POSITIONING, RELATIONSHIP, FACET_ASSIGNMENT
subject_id	string		ID of subject node (SubjectConcept, Work, Entity) involved
object_id	string		ID of object node involved
relation_key	string		Relationship type proposed (e.g. BROADER_CONCEPT, VETO_MECHANISM)
facets	object		Optional facet-weight map for this claim
source_agent_id	string		agent_id of Agent that produced the claim
framework_key	string		Framework identifier (for SFA claims; optional for SCA)
evidence_type	string		authority, harvested_graph, full_text, abstract, metadata
evidence_ref	string		Reference to logs, prompt, or external source (e.g. file path, URL)
confidence	float		Confidence score 0.0–1.0
status	string		pending, approved, rejected, superseded
created_at	string		ISO datetime
updated_at	string		ISO datetime
entity_type	string		Claim
Relationships:

(agent:Agent)-[:PRODUCED]->(c:Claim)
Agent produced this claim.

(c:Claim)-[:ABOUT_SUBJECT]->(s:SubjectConcept | Work | Entity)
Claim refers to a subject node.

(c:Claim)-[:ABOUT_OBJECT]->(o:SubjectConcept | Work | Entity)
Claim refers to an object node.

(c:Claim)-[:ASSERTS_RELATION {rel_type}]->(rel_node:RelationshipProxy)
Optional pattern if you materialize relationships as proxy nodes.

(c:Claim)-[:EVIDENCE_IN]->(w:Work)
Claim grounded in a particular Work (e.g. from full text).

(c:Claim)-[:SUPPORTS]->(r)-[:ASSERTED_BY]->(c)
Pattern if you attach claim IDs to existing relationships (see note below).

Note on edge-level claims:

If you prefer to avoid RelationshipProxy nodes, you can:

Store source, confidence, framework_key directly on relationships created by agents (e.g. :ABOUT, :BROADER_CONCEPT, :POSITIONED_AS).

Use Claim nodes primarily for higher-level tracking (who proposed what, when, with what evidence) and for conflicting proposals, while relationships carry a subset of the same properties.

Loader / Writer:

scripts/agents/sca_sfa_claim_writer.py

Reads agent outputs (JSON) and creates Claim nodes and associated relationships for SCA/SFA proposals.

These additions should give you a clean, explicit representation of agents and their claims, consistent with the SCA/SFA contract and with how you’re already using provenance properties on edges.