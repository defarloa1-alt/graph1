#Chrystallum-Generic
If you want Chrystallum to serve “historian + social science” now but also feel natural to an astronomer, a chemist, or a law firm later, the cleanest mental model is:

Core is whatever remains true when you swap out (a) the subject matter, (b) the source ecosystems, and (c) the domain-specific correctness rules.

Packages are the “subject ecosystems”: their ontologies, identifier schemes, ingestion formats, validation constraints, and default UI lenses.

Core (domain-agnostic)

1. Claim protocol and identity. A claim is an assertion with a stable content identity, plus attached provenance (who/when/how extracted), and a review/consensus state. This is universal across domains.

2. Evidence and citation model. Every claim should be traceable to sources (documents, datasets, observations, filings) and ideally to locators (page/paragraph, table row, timestamp, dataset field, docket entry).

3. Minimal entity model. “Things” (people, organizations, objects, substances, places, events) with stable IDs, labels, aliases, and links to external IDs. The external ID types vary per domain; the pattern does not.

4. Deterministic validation + resolution boundary. The “LLM proposes; system verifies/normalizes” principle is core. What verification means varies by domain, but the boundary is the same.

5. A small relationship kernel that almost everyone needs. Example categories: “about,” “part_of,” “located_in,” “participant_in,” “occurs_at_time,” “cites,” “derived_from,” “same_as / close_match,” “contradicts/supports,” “version_of/supersedes.”

6. Review workflow primitives. Review items, votes/ratings, dispute reasons, escalation, audit trail.

7. Operational primitives. Queues, backpressure, monitoring, reproducible re-runs, model/version tracking.

Those seven are the pieces you want to be hard to remove without breaking the system.

What is package-like (domain-specific)
A good “package” candidate has at least one of these properties:

* It depends on domain units/measurement conventions (RA/Dec epochs, stoichiometry, jurisdiction).
* It depends on domain authority files / registries (SIMBAD/Gaia, PubChem/InChI, court reporters).
* It needs domain-specific validators that can reject “plausible” text as wrong.
* It introduces specialized node/edge types that aren’t widely reusable.
* It wants its own default UI lenses (sky map, reaction network, matter timeline).
* It has unique privacy/compliance requirements (legal privilege, export controls, lab confidentiality).

Roman Republic as a package fits because it bundles a subject scope, source conventions, and an ontology slice (magistracies, provinces, fasti, prosopography, ancient geography, etc.) that isn’t inherently needed for, say, biochemistry.

How this looks in other domains

Astronomy package
Package-like concepts:

* Astronomical object taxonomy (star, galaxy, exoplanet, transient, etc.) and cross-catalog identity (“same object” across Gaia/SIMBAD/2MASS/SDSS…).
* Coordinate systems + epochs (ICRS vs FK5, J2000 vs observation epoch), proper motion, parallax.
* Observations as first-class data (time series, spectra, images), with uncertainties and calibration metadata.
* Instrument + pipeline provenance (telescope/instrument, reduction pipeline version).
* Domain file formats (FITS, VO tables), and domain query protocols.
  Core concepts reused unchanged:
* Claims (e.g., “Object X has period P,” “Transit depth D,” “Spectral line at λ”) + evidence + provenance + review state.
* External IDs pattern (catalog IDs) + deterministic crosswalk/resolution (cross-match rules become validators/resolvers inside the package).

Chemistry package
Package-like concepts:

* Molecular identity representations (InChI, SMILES, stereochemistry), structure equivalence rules, tautomers/salts.
* Reactions, mechanisms, yields, conditions (temperature/solvent/catalyst), and mass/charge balance validation.
* Spectra/assays (NMR/MS/IR) as evidence types with peak assignments.
* Registry ecosystems (PubChem CID, CAS RN, ChEBI) and mappings.
  Core concepts reused unchanged:
* Claim/evidence/provenance/review.
* Entity abstraction (“substance” is an entity; “reaction” can be an event/observation; “dataset row” is a source locator).
* Deterministic validators: valence checks, mass balance checks, canonicalization of structures.

Law firm package
Package-like concepts:

* “Matter” / “case” as a central container, plus parties, counsel, jurisdiction, docket, filings, deadlines.
* Privilege/confidentiality constraints, access control, redaction workflows, retention/hold policies.
* Legal citations and authorities (case law, statutes, regs) with citation parsing and normalization.
* Procedural events (motions, hearings, orders) and outcomes.
  Core concepts reused unchanged:
* Claims + evidence + provenance (a claim might be “court held X,” evidence is the order PDF + pinpoint cite).
* Review workflow (internal review, partner sign-off, conflict checks become review-like states).
* Operational pipeline and audit trail (arguably more important here).

So what’s “core” vs “package” in practice?
A practical rule: the graph should remain coherent if you uninstall a package. That means package edges/types should either (a) live in a package namespace, or (b) map cleanly onto core primitives.

One pattern that scales:

* Core schema: Claim, Entity, Source, EvidenceLocator, Agent, Review, plus a small kernel of relations.
* Package adds:

  * A domain registry (facet keys, relationship keys, units, allowed external ID types).
  * Domain validators (canonicalization + correctness checks).
  * Domain resolvers (crosswalk logic; e.g., SIMBAD cross-id rules, InChI canonicalization, citation normalization).
  * Domain ingestion adapters (FITS parser, lab notebook parser, ECF scraper).
  * Domain UI lenses (sky plot, reaction graph, docket timeline).

If you want a crisp boundary, define “package = (registry + validators + resolvers + adapters + views) for a domain,” while “core = claim protocol + provenance/review + minimal entity model + operational backbone.”

