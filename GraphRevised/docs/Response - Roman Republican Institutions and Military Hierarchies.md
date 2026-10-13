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

## Registry v9 (built 2026-10-13: [predicates.v9.json](../proposals/predicates.v9.json), `proposal-draft-v6`)

- `partOf` extended to Groups and Types (the force hierarchy gap: "a wing is
  part of a fleet"); `instanceOf` (Group to Type).
- `precedes` (Office to Office, dated: the cursus order and its changes).
- `electedBy` (Office to an assembly Group, dated).
- `exercisedPower` (Office to power Type, dated competence) and `heldPower`.
- `servedUnder`.
- `memberOf` (Person to Group, dated): membership of a college, alliance, or
  body (below).
- Context and role kinds are declared per predicate (`contextKinds`, `roleKinds`;
  defaults Event and Office): context on `heldPower` may be an Event, Place, or
  Group, on `servedUnder` an Event or Group.
- `partOf` pairs its kinds (`kindPairs`: Event-Event, Group-Group, Type-Type).
- Wikidata P361 "part of" evidences whichever of `partOf`, `subperiodOf`, and
  `memberOf` fits its endpoints' kinds; P463 maps to `memberOf`.
- Harvest kind Polity from Wikidata *historical country* (Q3024240), *empire*
  (Q48349), and *Hellenistic kingdom* (Q3932025), after Period in priority.
  Type has no Wikidata classes: types come from the enrichers and the reader.
- A **quantity** qualifier (minimum, maximum, typical) for counts and
  establishments, never a headcount.
- Kinds **Type** and **Polity**.

## Powers: *imperium* (curator, 2026-10-13)

**Decided.** A power is a **Type**, not an Office; this replaces 24 §8
decision 4. *Imperium* was the authority to command on the state's behalf,
granted to a person for a defined command within limits of time and task: not
an office, not a rank, and not a permanent attribute of its holder. Office
and power stay distinct: a consul held *imperium* because of his office, a
proconsul through prorogation or a special grant.

| Curator's sketch | Here |
|---|---|
| `PowerType {key: imperium}` | Entity kind Type: *imperium*, *potestas*, *auspicium*, tribunician power, *imperium maius*. *Auctoritas* is standing and influence, not enforceable power: a Concept |
| `PowerGrant` with `SUBJECT_OF` | a `heldPower` claim, Person to power Type, time required |
| `DERIVED_FROM` an office tenure | the claim's role qualifier: the Office it was held through (consul) |
| `DERIVED_FROM` a law or prorogation | `conferred` (planned in 24 §4, not yet in the registry): the law or decree as an Event, the person as object, the power as role, so its role kinds will include Type |
| `APPLIES_TO` a *provincia*, army, or territory | the claim's context. *Provincia* means a task, enemy, or command as much as a territory, so `heldPower` allows Event, Place, and Group as context; today context is Event only |
| competence of an office | `exercisedPower`, Office to power Type, dated |
| components (military, coercive, judicial authority) | Types linked by `partOf`, **attributed only**: whether *imperium* included civil jurisdiction is a scholarly dispute (the traditional reading against Drogula's), so each reading is a separate attributed claim and the graph does not choose |
| degrees (dictatorial, consular, praetorian; *imperium maius*) | likewise attributed claims, never a stored hierarchy; one reading has commanders fully sovereign within separate *provinciae*, so precedence is not assumed from rank |

The *domi* and *militiae* spheres and the *pomerium* boundary are readings
too, attributed where a source states them.

## Membership (curator, 2026-10-13)

**Decided.** Mark Antony was a **member of** the Second Triumvirate. Wikidata
records it as "part of" (P361) pointing at *triumvirate* (Q83204), the
general class ("political regime ruled or dominated by three powerful
individuals"); the body itself is *Second Triumvirate* (Q212079, "Roman
political alliance (43–32 BC)", an instance of alliance and of triumvirate).
Rules for the harvest:

- P463 (member of) and P361 (part of) on a Person map to `memberOf`, never to
  `partOf` or `subperiodOf`.
- When the target is a class rather than an instance (Q83204), the claim is
  not stored as given: the agent looks for the instance the dates and the
  other members point to (Q212079 for Antony), and records why.
- Membership of the Second Triumvirate sits beside `heldPosition` *triumvir
  rei publicae constituendae* (the Office, 43–33 BC in Wikidata): one says
  he belonged to the college, the other that he held the post.

## Not adopted

- The roughly thirty labels.
- Numeric certainty (0.0 to 1.0): attestation is computed and shown in words
  (25 §6, decision 4). The status vocabulary (attested, traditional,
  reconstructed, disputed, superseded interpretation) mostly follows from mode,
  category, and attestation; "traditional" (Livy's foundation dates) may
  become a quiet label.
- Edges between command assignments (claims about claims).
