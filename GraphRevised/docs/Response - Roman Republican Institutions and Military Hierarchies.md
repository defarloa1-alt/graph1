# Response: Roman Republican Institutions and Military Hierarchies

**Responds to:** [Roman Republican Institutions and Military Hierarchies for Neo4j](Roman%20Republican%20Institutions%20and%20Military%20Hierarchies%20for%20Neo4j.md)
**Date:** 2026-10-13
**Status:** Agreed with the curator. The design for the structure enrichers
(L3 increment 4; [25 §11](../25-LIVES-AND-PLAYGROUND.md)). Follows the earlier
[army response](Response%20-%20Roman%20Republican%20Army%20Structure.md).

## Decision

Adopt the document's content and principles; do not adopt its schema. Its
institutions, offices, roles, powers, unit types, and organizational patterns
become Entities of a few kinds with dated, sourced claims between them. Its
canonical trees are views generated from those claims, as the document itself
recommends, never stored hierarchies. Facets stay lenses: "military" and
"political" filter Types and claims; they are not nodes (curator, option 1).

## Adopted principles

- No timeless constitution or army: office counts, competences, selection,
  and unit composition are dated claims, and Polybius 6 is a snapshot of the
  Hannibalic-war Republic, not a code.
- Office, role, and power are distinct (consul; army commander; *imperium*).
- Historiography is kept: the "Marian reforms" package is an attributed,
  older interpretation; gradual cohort development is the default reading.
- The Polybian template is built first; one source (Polybius 6) feeds both the
  constitution and the army.
- The Republican navy is campaign fleets with parallel shipboard chains
  (command, navigation, propulsion, combat); no back-projected Imperial fleets.
- The "First Triumvirate" is an informal alliance (`alliedWith` claims with
  time); the *tresviri rei publicae constituendae* are an Office.

## Mapping onto the core

| Document | Here |
|---|---|
| `OfficeType` (consul, praetor, tribune) | Entity kind **Office** |
| `Institution` (Senate, assemblies, priestly colleges, courts) | kind **Group**: real, continuing bodies |
| `UnitType`, `OrganizationalPattern`, `RoleType`, `PowerType` | new kind **Type** |
| `MilitaryUnit` (a legion, a campaign fleet) | kind **Group**, `instanceOf` a Type |
| `Polity` (Roman Republic, Ptolemaic Kingdom) | new kind **Polity**; also settles the harvest's "historical country" and "form of government" classes |
| `OfficeTenure` | `heldPosition` with time |
| `CommandAssignment` | `commanded` or `heldAuthorityOver` with role, context, and time |
| `PowerGrant` | new `heldPower` (Person to power Type, the province as context, time) |
| `InstitutionalState` ("two praetors from 242 BCE") | a claim with a quantity qualifier and a time |
| `CompositionClaim` (30 maniples in a Polybian legion) | `partOf` between Types, with a quantity, attributed to its source |
| `UNDER_COMMAND_OF` between assignments | new `servedUnder` (Person to Person, with role, context, time); claims about claims are not in the model |
| `Source`, `SourcePassage` | Work and passage SourceObservation |
| `validFrom` / `validTo`, precision | time qualifiers, tethered to Years |

## Registry v9 (planned)

- `partOf` extended to Groups and Types (the force hierarchy gap: "a wing is
  part of a fleet"); `instanceOf` (Group to Type).
- `precedes` (Office to Office, dated: the cursus order and its changes).
- `electedBy` (Office to an assembly Group, dated).
- `exercisedPower` (Office to power Type, dated competence) and `heldPower`.
- `servedUnder`.
- A **quantity** qualifier (minimum, maximum, typical) for counts and
  establishments, never a headcount.
- Kinds **Type** and **Polity**.

## Not adopted

- The roughly thirty labels.
- Numeric certainty (0.0 to 1.0): attestation is computed and shown in words
  (25 §6, decision 4). The status vocabulary (attested, traditional,
  reconstructed, disputed, superseded interpretation) mostly follows from mode,
  category, and attestation; "traditional" (Livy's foundation dates) may
  become a quiet label.
- Edges between command assignments (claims about claims).
