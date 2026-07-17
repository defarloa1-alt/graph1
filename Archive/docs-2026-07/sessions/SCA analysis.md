SCA analysis

**New SCA flow (2026-03):** Traversal engine + persist + MCP grounding. See `docs/agents/SCA_AGENT_INSTRUCTIONS.md`.
- `scripts/sca/sca_traversal_engine.py` — recursive P31/P279 backlink traversal
- `scripts/sca/sca_persist.py` — write to Neo4j (WikidataType, SubjectDomain)
- `scripts/sca/sca_run.py` — traverse + persist in one command
- MCP `get_domain_structure(qid)` — ground new Claude sessions

---

Here's what the SCA wrote to the graph for the Roman Republic (Q17167):

SubjectConcept node
Label: SubjectConcept only (no Entity label)
Properties: subject_id: subj_q17167, qid: Q17167, label: Roman Republic, updated_at: 2026-03-02
POSITIONED_AS edges (6) — the SCA's core output
These are the federation positioning anchors the SCA computed from Wikidata P31/P122/P361:

Target	Anchor Type	Confidence	Property	Rel Type	Hops
historical period (Q11514315)	HistoricalPeriod	HIGH	P31	INSTANCE_OF_CLASS	1
form of government (Q1307214)	FormOfGovernment	HIGH	P31	INSTANCE_OF_CLASS	1
empire (Q48349)	FormOfGovernment	MEDIUM	P31	INSTANCE_OF_CLASS	1
historical country (Q3024240)	HistoricalCountry	HIGH	P31	INSTANCE_OF_CLASS	1
aristocratic republic (Q666680)	FormOfGovernmentType	HIGH	P122	TYPE_ANCHOR	1
Ancient Rome (Q1747689)	CivilisationContext	HIGH	P361	COMPOSITIONAL_PARENT	1
All carry federation: wikidata and policy_ref: FederationPositioningHopsSemantics.

Entity node (Q17167) — harvester output, not SCA
The Entity node (labels: Entity, Polity, HistoricalPolity) has a much richer graph written by the harvester, not the SCA:

Outbound from Q17167 (93 edges):

14x P793 (significant events: Punic Wars, Gallic War, Caesar's Civil War, etc.)
7x P31/INSTANCE_OF, 7x HAS_SIGNIFICANT_EVENT
6x POSITIONED_AS (SCA), 6x P527/P30
Temporal: STARTS_IN_YEAR → 509 BCE, ENDS_IN_YEAR → 27 BCE
IN_PERIOD → classical antiquity
PART_OF → Ancient Rome
FOLLOWED_BY → Roman Empire, Principate
HAS_CAPITAL → Rome, HAS_OFFICIAL_LANGUAGE → Latin, HAS_CURRENCY → Roman currency, HAS_OFFICIAL_RELIGION → ancient Roman religion
Inbound to Q17167 (4,964 edges):

4,880x CITIZEN_OF — the DPRR persons
9x LOCATED_IN_COUNTRY, 9x CONTROLLED_BY
7x P710 (participants), 5x IN_PERIOD (sub-periods pointing back)
3x PART_OF (Early/Middle/Late Roman Republic)
Summary
The SCA specifically wrote 7 things: 1 SubjectConcept node + 6 POSITIONED_AS edges. Its job was to classify what kind of entity the Roman Republic is (historical period, historical country, aristocratic republic, part of Ancient Rome civilisation). The "empire" anchor at MEDIUM confidence is an interesting artefact — Wikidata has Q17167 as P31→Q48349 (empire) which is debatable for a republic.

Everything else (the 4,880 citizen links, the temporal backbone, the significant events) came from the Wikidata backlink harvester and DPRR adapter, not the SCA.

our scripts in some cases act like an sca. the sca was supposed to - in this case in particular as a seed agent, traverse up down and across to place the subject in academic, bibliographical landscape



You're right — let me look at what's actually in the graph around Q17167 that should have been SCA work, and which scripts produced it instead.


Queried LCC classification database for Rome-related subjects and Rome entity connections
Queried LCC classification database for Rome-related subjects and Rome entity connections

That confirms it. Here's the gap:

What the SCA was supposed to do for Roman Republic as a seed SubjectConcept:

Traverse up — P31/P279 class hierarchy to position it in KBpedia/LCC academic landscape
Traverse down — find sub-periods (Early/Middle/Late Republic), constituent entities
Traverse across — map to LCSH headings, LCC classes (DG231–DG269 for the Republic period), FAST topics, bibliography sources like DPRR, Cambridge Ancient History, etc.
What actually happened:

The SubjectConcept node has zero connections to any LCC_Class, LCSH, FAST, or BibliographySource
4,490 LCC_Class nodes exist in the graph, including "Roman History by period", "Ancient Italy. Ancient Rome", "Ancient Rome (General)" — none linked to Q17167
The only outbound edges from the SubjectConcept are 6 POSITIONED_AS edges — which are just a shallow 1-hop P31/P122/P361 readout from Wikidata
No facet assignments at all (facets: null from the MCP)
What scripts did the SCA's job instead:

The harvester wrote the temporal backbone (STARTS_IN_YEAR → 509 BCE, ENDS_IN_YEAR → 27 BCE, IN_PERIOD → classical antiquity)
The harvester wrote the compositional structure (PART_OF → Ancient Rome, FOLLOWED_BY → Roman Empire)
The harvester pulled in sub-periods as Entity nodes (Early/Middle/Late Republic with PART_OF back to Q17167)
The DPRR adapter wrote the 4,880 CITIZEN_OF edges
The backlink harvester wrote the significant events (P793 — wars)
So the scripts collectively built a rich entity graph around Q17167, but the SCA's actual mandate — positioning it in the academic/bibliographical landscape (LCC classification, LCSH subject headings, facet assignment, bibliography source linkage) — was never executed. The POSITIONED_AS edges are just the federation positioning step from sca_federation_positioning.py, not the full SCA traversal. The SCA stopped at "what is this thing?" and never got to "where does this thing sit in the library."

For family tree work this matters because the LCC/LCSH positioning is what would tell the system "persons under this SubjectConcept belong in DG203–DG269 (Roman Republic biography)" vs "DG271+ (Roman Empire)" — which drives how the 4,880 persons get classified, which facets they inherit, and how bibliography sources are scoped to them.

what is teh fix?



The SubjectConcept is a bare stub. The fix is to complete the seed — connect it to the LCC/LCSH/bibliography nodes that already exist in the graph. Two parts:

1. Immediate seed completion (data)

The 4,490 LCC_Class nodes include the right targets. Wire them:

SubjectConcept(Q17167) -[:CLASSIFIED_UNDER]-> LCC_Class("Ancient Italy. Ancient Rome")
SubjectConcept(Q17167) -[:CLASSIFIED_UNDER]-> LCC_Class("Roman History by period")
SubjectConcept(Q17167) -[:CLASSIFIED_UNDER]-> LCC_Class("Roman life and customs")
SubjectConcept(Q17167) -[:HAS_BIBLIOGRAPHY]-> BibliographySource("Digital Prosopography of the Roman Republic")

Plus LCSH headings (Rome -- History -- Republic, 510-30 B.C.), FAST topics, and facet assignments (POLITICAL, MILITARY, RELIGIOUS at minimum for the Republic).

That gives the 4,880 persons somewhere to inherit from — "you belong in DG203–DG269, your bibliography authority is DPRR, your facets are POLITICAL/MILITARY."

2. Structural fix (code)

The sca_federation_positioning.py script does 1-hop P31/P122/P361 readout and writes POSITIONED_AS. That's step 1 of the SCA's job. Steps 2–4 never got built:

Step	What	Status
1	Federation positioning (P31/P122/P361 → POSITIONED_AS)	Done
2	LCC/LCSH mapping (traverse P31 class hierarchy → match to LCC_Class nodes)	Missing
3	Bibliography source linkage (which authority sources cover this subject)	Missing
4	Facet assignment (D8 table — which of the 18 canonical facets apply)	Missing
The scripts that did some of this work (harvester wrote temporal backbone, DPRR adapter wrote citizen edges) did it as side effects of entity harvesting, not as deliberate subject positioning. The SubjectConcept node doesn't benefit from any of that — it just sits there with 6 POSITIONED_AS edges and an empty academic address.

For the family tree exercise specifically: step 2 is the critical one. The LCC_Class nodes have no class_id property (all null in the graph), which means even if you wired the edges today, downstream scripts can't do range-based classification (is this person DG231–DG269 Republic or DG271+ Empire?). So the fix is actually two writes:

Backfill class_id on the relevant LCC_Class nodes (DG, DG11–DG365 range)
Wire SubjectConcept → LCC_Class + BibliographySource + facets
Want me to write the seed completion cypher and/or spec out what a proper step 2–4 SCA script would look like?

yes



Updated todo list with Roman Republic cypher and SCA script tasks
Updated todo list with Roman Republic cypher and SCA script tasks

First let me understand the LCC_Class node structure and what bibliography sources exist.


Queried Library of Congress classification and bibliography data for Roman/Ancient history records
Queried Library of Congress classification and bibliography data for Roman/Ancient history records

Good — LCC_Class nodes have code, prefix, start, end, label, uri. And the bibliography sources include DPRR, Broughton MRR, and Zmeskal Adfinitas. Now let me find the DG range.


Queried graph database for federation and bibliography sources
Queried graph database for federation and bibliography sources

The LCC hierarchy is beautifully structured. DG221–239 (Early Republic), DG241–259 (Middle Republic), DG261–269 (Late Republic) — exactly what we need. And the BROADER_THAN edges between LCC_Class nodes are already wired. The BibliographySource nodes exist (DPRR, Broughton_MRR, Zmeskal_Adfinitas) but are orphaned — no edges to anything.

Now let me check what relationship types exist between SubjectConcepts and LCC in the rest of the graph, so the seed uses the right vocabulary.


Searched codebase for LCC classification node patterns
Searched codebase for LCC classification node patterns

The canonical relationship type is CLASSIFIED_BY_LCC. Let me check the existing subject_concept_operations.cypher to see the pattern.


Reviewed Cypher query files for subject concept and FAST authority linking operations
Reviewed Cypher query files for subject concept and FAST authority linking operations

Now I see the full picture. The bootstrap cypher was written to do exactly this (LCSH, FAST, LCC links) but the SubjectConcept in the graph has subject_id: subj_q17167 while the scripts target subj_roman_republic_q17167. Let me verify that mismatch.


Queried subject concept database for Roman Republic metadata
Queried subject concept database for Roman Republic metadata

There it is. The bootstrap scripts wrote for subj_roman_republic_q17167. The actual node in the graph is subj_q17167. The MERGE never matched, so none of the LCSH, FAST, LCC, or facet assignments from the bootstrap cypher ever landed. And the FAST_Subject, LCSH_Subject nodes don't exist either — the whole chain failed silently.

Now let me also check what facet-related properties or edges exist.


Read Cypher script for subject concept agent bootstrap configuration
Read Cypher script for subject concept agent bootstrap configuration

Now I have the full picture. Let me write the seed completion cypher and the SCA spec.


Created Neo4j seed script for Roman Republic subject concept
Created Neo4j seed script for Roman Republic subject concept

Now the SCA steps 2–4 spec.


Examined sca_federation_positioning.py script for classification mapping definitions
Examined sca_federation_positioning.py script for classification mapping definitions

Good — the SCA script already has CLASSIFICATION_PROPS with P1149 (LCC), P244 (LCSH), P2163 (FAST). It fetches them from Wikidata targets but never writes the linkage to the graph's existing LCC_Class/LCSH_Subject/FAST_Subject nodes. Let me check the write step.


Read SCA federation positioning script file
Read SCA federation positioning script file

Now I see it clearly. The write_position_map function writes POSITIONED_AS edges and ClassificationAnchor nodes. It fetches the LCC/LCSH/FAST IDs from Wikidata (step 1, lines 711-716) but only stores them in the position_map dict. It never creates LCSH_Subject / FAST_Subject / CLASSIFIED_BY_LCC nodes. That's the missing Step 2.

Now let me write the SCA spec.


Completed seed cypher for Roman Republic concept and designed SCA steps 2-4 script
Completed seed cypher for Roman Republic concept and designed SCA steps 2-4 script

Done. Two files committed and pushed:

scripts/neo4j/seed_roman_republic_subject_concept.cypher — Immediate fix. Wires the existing subj_q17167 node to:

LCSH (sh85115087: Rome--History--Republic, 265-30 B.C.)
FAST (fst01204885)
12 LCC_Class links — DG201-365 (primary), DG221-239/241-259/261-269 (period subdivisions), DG89/91/95/99/105/125 (thematic: constitution, political institutions, magistracies, senate, army, family), KJA2-3660 (Roman Law cross-schedule), JC51-93 (Ancient state), CJ/CN (numismatics, inscriptions)
3 BibliographySource bindings — DPRR (primary/prosopography), Broughton MRR (secondary/magistracies), Zmeskal Adfinitas (secondary/family networks)
Facet assignment — POLITICAL primary + MILITARY, LEGAL, RELIGIOUS, SOCIAL, ECONOMIC
Temporal tethering — Year -509 to Year -27
Person/sca_academic_positioning_spec.md — Structural fix spec. The root cause: sca_federation_positioning.py already fetches LCC/LCSH/FAST from Wikidata (lines 711-716) but discards them — they never get written as graph relationships. The spec covers extending the script with three new functions (write_authority_links, write_bibliography_bindings, write_facet_assignments) that convert the already-fetched data into the graph edges the SubjectConcept needs. Also documents the subject_id mismatch (subj_roman_republic_q17167 in bootstrap cypher vs subj_q17167 in live graph) that caused the original silent failure.

what is the cli to pull them



To run the seed cypher against your Neo4j instance:

# If using cypher-shell (bundled with Neo4j)
cypher-shell -u neo4j -p YOUR_PASSWORD \
  -f scripts/neo4j/seed_roman_republic_subject_concept.cypher

# Or if using a remote Aura/hosted instance
cypher-shell -a neo4j+s://YOUR_URI -u neo4j -p YOUR_PASSWORD \
  -f scripts/neo4j/seed_roman_republic_subject_concept.cypher

Each statement is separated by semicolons and returns a confirmation line ('LCSH linked', 'LCC primary linked', etc.), so you'll see step-by-step output. The verification queries at the end will show the full edge count and all linked authorities.

If you're running from the Python scripts instead (like the SCA positioning script does):

python scripts/sca/sca_federation_positioning.py --write \
  --neo4j-uri neo4j+s://YOUR_URI \
  --neo4j-password YOUR_PASSWORD

That only runs Step 1 though (the POSITIONED_AS edges that are already there). The seed cypher is the one that fills the gap.

