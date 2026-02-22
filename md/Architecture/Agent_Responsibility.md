 Agent Responsibility
 Domain Stewardship
Own and maintain a specific, bounded domain or conceptual scope (e.g., "Late Roman Republic," "Atmospheric Science").

Ensure all content within that domain is consistent, complete, and aligned with backbone standards.

2. Knowledge Extraction
Parse and extract structured knowledge (entities, relationships, properties, events) from sources (Wikipedia, Wikidata, academic texts, archives, user inputs).

Identify and resolve entity references (QIDs, backbone codes, canonical names).

3. Claim Validation and Confidence Scoring
Assess the credibility, authority, and quality of every extracted fact or relationship.

Assign confidence scores based on source reliability, consistency, recency, and corroboration.

4. Evidence Tracking and Provenance
Record the full lineage of every claim: who said it, when, where, and with what supporting evidence.

Link claims to citations, references, and primary/secondary sources.

5. Divergence Detection
Identify when new evidence or sources materially contradict existing claims.

Flag significant divergences (above threshold) for human review or escalation.

Distinguish between minor variations (ignore/log) and material conflicts (surface/annotate).

6. School-of-Thought Synthesis
Recognize and represent multiple scholarly or expert perspectives (military history, economics, cultural studies, etc.).

Maintain school-specific confidence scores, source hierarchies, and interpretive rationales.

Surface where schools agree, diverge, or fundamentally conflict.

7. Cross-Domain Linking
Identify and create relationships between entities across different domains (e.g., linking "Caesar" in political history to "Gallic Wars" in military history).

Ensure cross-domain properties and edges use standardized schema from the Property & Edge Registry.

8. Shell Node Creation
Generate lightweight placeholder nodes for related concepts, entities, or events encountered during extraction.

Mark shells for on-demand expansion (lazy loading).

9. Gap Identification
Detect missing information, incomplete relationships, or under-researched areas within the domain.

Prioritize gaps based on user demand, pressure fields, or research importance.

10. Decomposition and Seeding
For broad or complex domains, recursively decompose into smaller, tractable sub-domains using backbone and domain ontologies.

Instantiate child agents for sub-domains when appropriate (reaching "trainable units").

Retire or go dormant once decomposition is complete.

11. Debate Facilitation
When divergences arise, orchestrate evidence-based debate:

Compare sources, methodologies, and confidence levels.

Generate synthesis or highlight irreconcilable conflicts.

Escalate to human curators when necessary.

12. Continuous Re-Evaluation
Monitor for new sources, evidence, or user activity in the domain.

Re-assess confidence scores, detect new divergences, and update claims as knowledge evolves.

13. Backbone Alignment Enforcement
Ensure all nodes, properties, and relationships within the domain comply with backbone standards (LCC/LCSH/FAST).

Validate that domain-specific ontologies are correctly linked to universal backbone codes.

14. Registry Management
Check Agent Registry to avoid duplication (ensure only one agent per domain/scope).

Check Property & Edge Registry to ensure schema compliance and cross-domain interoperability.

Propose new properties/edges when novel relationships are discovered.

15. Dormancy and Activation
Enter dormant state when domain is stable (low pressure, no new evidence, no user activity).

Wake on triggers: new source ingestion, user query, divergence detection, or pressure threshold exceeded.

16. Wikidata Federation
Identify claims that are novel, high-confidence, and well-provenance and prepare them for contribution to Wikidata.

Generate QuickStatements or export formats for human review and submission.

17. User Interaction Support
Respond to user queries about the domain (explain claims, provide evidence, show provenance).

Generate summaries, timelines, or narrative explanations of complex topics.

Present school-of-thought perspectives on demand.

18. Audit Trail Generation
Maintain complete, queryable history of all decisions, updates, and debates within the domain.

Enable full transparency: who changed what, when, why, and based on what evidence.

19. Multi-Lingual Support
Leverage Wikidata QIDs and backbone mappings to provide labels, descriptions, and claims in multiple languages.

Ensure consistency across language variants.

20. Quality Assurance
Enforce universal required properties for key node types (Person, Organization, Event).

Validate data completeness, consistency, and schema compliance.

Flag low-quality or incomplete entries for curation.

Summary: Agent as Knowledge Curator
An agent in Chrystallum is a knowledge curator for a specific domain. It extracts, validates, links, debates, and maintains knowledge while ensuring backbone alignment, cross-domain interoperability, and transparent provenance. It operates autonomously but escalates to human oversight when necessary, and it adapts dynamically as evidence evolves.

