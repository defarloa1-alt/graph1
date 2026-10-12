# Roman Republican Army Structure for a Neo4j Knowledge Graph
## Direct answer
The Roman Republican army should not be represented as one stable hierarchy. Between 509 and 27 BCE it evolved from a poorly documented, property-graded citizen levy, through the well-attested manipular legion of the middle Republic, into the cohort-based armies of the first-century civil wars. The safest Neo4j design therefore separates **organizational models**, **unit types**, **historical unit instances**, and **source-backed claims valid for particular periods**.

The central structural sequence is:

1. **Early Republic:** levy organized by citizenship, age, and property; a probable hoplite-style heavy infantry core, light infantry, and aristocratic cavalry, but no securely reconstructable universal tactical hierarchy.
2. **Middle Republic:** a legion of approximately 4,200 infantry and 300 citizen cavalry, with heavy infantry divided into 30 maniples arranged as *hastati*, *principes*, and *triarii*, plus distributed *velites*.
3. **Transitional period:** maniples and cohorts overlapped during the second century BCE; the cohort was not suddenly invented by Gaius Marius.
4. **Late Republic:** the cohort became the principal legionary maneuver unit; ten cohorts normally formed a legion, while non-Italian auxiliaries increasingly supplied cavalry and specialist light infantry.
## Chronological framework
Period boundaries are analytical conveniences rather than Roman regulations. They should be represented as approximate intervals with competing scholarly claims, not hard-coded as exact global change dates.

| Model | Approximate span | Dominant organization | Evidence quality | Modeling note |
|---|---:|---|---|---|
| Archaic/Servian inheritance | 509–c. 400 BCE | Census-based citizen levy; probable heavy-infantry core with lighter troops and cavalry | Low | Distinguish political census centuries from tactical centuries |
| Early manipular development | c. 400–290 BCE | Gradual replacement or modification of dense spear formations by smaller units and multiple lines | Low–medium | Model as transition, not a single reform event |
| Polybian/manipular system | c. 290–150/130 BCE | Legion → troop classes → maniples → centuries; citizen cavalry in *turmae* | High for mid-second century | Polybius is the principal structural snapshot |
| Maniple–cohort transition | c. 150–88 BCE | Cohorts increasingly used alongside maniples, especially in Spain | Medium | Permit both structures to be valid simultaneously |
| Cohortal late Republic | c. 88–27 BCE | Legion → ten cohorts → centuries; homogeneous legionary heavy infantry | Medium–high | Avoid importing the enlarged Imperial first cohort backward |

The traditional sequence from tribal army to hoplite phalanx to manipular legion is itself a reconstruction; a Cambridge overview notes that the model may date back to ancient or early modern interpretation rather than contemporary early-Republican documentation. The adaptation of more mobile, sword-oriented tactics is commonly placed in the later fourth century BCE, but the process and precise date remain disputed.[^1][^2]
## Early Republic
### Mobilization basis
The early Republican army was fundamentally a **levy of citizens**, not a permanent standing organization. Ancient tradition attributed to Servius Tullius a division into property classes and 193 voting centuries, with younger men assigned to field service and older men to home defense; Dionysius explicitly connects these divisions to military levies and taxation. This tradition is important but retrospective, since Dionysius wrote centuries after the system he described.[^3]

For the graph, do not equate a `CensusCentury` with a `TacticalCentury`. The former was a civic, fiscal, and voting division expected to furnish men; the latter was a battlefield and administrative subdivision commanded by a centurion. They share the Latin term *centuria* but are different entities.
### Probable field structure
The common reconstruction gives the early army a property-qualified heavy infantry core equipped in a broadly hoplite manner, supported by less wealthy light infantry and cavalry drawn from citizens able to maintain horses. The evidence does not justify generating a complete early-Republic table of fixed legions, centuries, and strengths as if it were equivalent to Polybius’s later account.[^4][^5]

Use broad unit types for this phase:

- `HeavyInfantryBody`
- `LightInfantryBody`
- `CitizenCavalryBody`
- `ClanWarBand` where a specific source supports one
- `FieldLevy`
- `HomeDefenseLevy`

Attach proposed formations such as `HoplitePhalanx` through a claim with `confidence: "medium"` or `"low"`, rather than asserting that every early Roman army used that formation.
## Manipular legion
Polybius provides the clearest contemporary-adjacent organizational snapshot. His standard legion contained 4,200 infantry, increased to 5,000 in emergencies, plus 300 citizen cavalry. The infantry was divided into 1,200 *hastati*, 1,200 *principes*, 600 *triarii*, and the remainder—normally 1,200—classified as *velites*.[^6][^7][^8]
### Legion hierarchy
```text
Roman Legion
├── Infantry
│   ├── Velites: normally 1,200, distributed among the maniples
│   ├── Hastati: 10 maniples × 120 = 1,200
│   ├── Principes: 10 maniples × 120 = 1,200
│   └── Triarii: 10 maniples × 60 = 600
└── Citizen cavalry: 300
    └── 10 turmae × 30
```

The legion therefore had **30 heavy-infantry maniples**, ten in each of the three lines. A maniple contained two centuries and had two centurions and two *optiones*; when both centurions were present, the senior commanded the right half and the junior the left, while either could command the whole maniple if the other was absent. The *velites* should not be modeled as ten independent “velite maniples,” because Polybius says they were distributed among the other companies.[^9][^7]

| Component | Nominal strength | Count per legion | Immediate subdivision | Officers |
|---|---:|---:|---|---|
| Hastati | 1,200 | 10 maniples | 2 centuries per maniple | 2 centurions and 2 *optiones* per maniple |
| Principes | 1,200 | 10 maniples | 2 centuries per maniple | 2 centurions and 2 *optiones* per maniple |
| Triarii | 600 | 10 maniples | 2 half-sized centuries per maniple | 2 centurions and 2 *optiones* per maniple |
| Velites | Normally 1,200 | Distributed | Attached across maniples | No parallel maniple hierarchy described |
| Citizen cavalry | 300 | 10 *turmae* | 3 groups of ten in each *turma* | 3 *decuriones* per *turma* |

Polybius says the *triarii* remained fixed at 600 when an enlarged legion increased the other classes proportionally. This is best represented with a `StrengthRule` node rather than assuming that every legion instance had the same actual headcount.[^7]
### Tactical relationships
The *hastati*, *principes*, and *triarii* were simultaneously:

- **Troop categories**, based principally on age and experience.
- **Battle lines**, with the *hastati* forward, *principes* behind, and *triarii* in reserve.
- **Administrative groupings**, each divided into ten maniples.

These meanings should be separate nodes or labels. `Hastati` is not a single historical unit containing every *hastatus* who ever served; it is a `TroopCategory` and `BattleLineRole` instantiated separately in each legion or battle deployment.

Livy’s description has the *hastati* engage first, retire through intervals if unsuccessful, and yield the fight to the *principes*, with the *triarii* held behind them. The familiar checkerboard or *quincunx* reconstruction is plausible, but the exact spacing and mechanics remain debated; represent `DEPLOYED_AS` and `SUPPORTED_BY` relationships as battle-specific claims rather than permanent containment.[^10][^11]
### Cavalry
The 300 citizen cavalrymen were divided into ten *turmae* of about 30. Each *turma* selected three *decuriones*, the first acting as its commander. A *decuria* or ten-man grouping may be modeled beneath the *turma*, but its precise tactical autonomy should not be overstated.[^12][^13]

```text
Legionary cavalry contingent
└── 10 Turmae
    └── approximately 30 cavalrymen
        └── 3 Decuriones, one senior
```
## The consular army
A legion was not normally the entire Roman field force. Polybius’s standard consular army comprised **two Roman legions** plus allied forces, while each legion had six military tribunes. A useful graph distinction is therefore:[^9][^6]

- `ArmyInstance`: the complete force under a magistrate or promagistrate.
- `LegionInstance`: one Roman citizen formation within that army.
- `AlliedWingInstance`: a contingent or collection of contingents supplied by Italian allies.
- `AuxiliaryContingentInstance`: non-Italian or specialist forces serving under treaty, client, mercenary, or ad hoc arrangements.

```text
Consular Army
├── Roman Legion I
├── Roman Legion II
├── Right allied wing (ala dextra)
├── Left allied wing (ala sinistra)
├── Allied extraordinarii
├── Staff, train, specialists, and servants
└── Additional contingents as the campaign required
```
### Italian allies
The *socii* were structurally essential rather than optional “extras.” Polybius says allied infantry normally equaled the Roman infantry and allied cavalry was three times the Roman cavalry. Twelve Roman *praefecti sociorum* organized the allies, selected approximately one-fifth of their infantry and one-third of their cavalry as *extraordinarii*, and divided the remainder into right and left wings.[^14][^15][^16]

| Allied formation | Function | Relationship to army |
|---|---|---|
| `AlaDextra` | Allied right wing | Assigned to a particular field army |
| `AlaSinistra` | Allied left wing | Assigned to a particular field army |
| `PeditesExtraordinarii` | Selected allied infantry | Directly available to the commander |
| `EquitesExtraordinarii` | Selected allied cavalry | Directly available to the commander |
| `CommunityContingent` | Men supplied by an allied polity | Contributed to an *ala* or another grouping |

Do not model an *ala* as merely the permanent subordinate of one legion. The evidence is better represented as an army-level allied wing assembled for a campaign. Also distinguish Republican allied *alae* from the later Imperial cavalry regiment bearing the same term.
## Command structure
Republican command was a network of **legal authority, assignment, and temporary delegation**, not a timeless modern rank ladder.

| Level or function | Typical office | Graph interpretation |
|---|---|---|
| Field army | Consul, praetor, dictator, proconsul, or propraetor | Person holds magistracy and receives an `ArmyCommand` assignment grounded in *imperium* |
| Legion supervision | Six military tribunes | Rotating or task-based command; not six permanent battalion commanders |
| Maniple/century | Centurion | Unit command tied to a specific legion and levy |
| Deputy/rear officer | *Optio* | Attached to a centurion or century/maniple |
| Allied organization | *Praefectus sociorum* | Roman officer assigned to allied forces |
| Cavalry squadron | *Decurio* | Officer assignment within a *turma* |
| Finance and supply | Quaestor | Army finance, pay, deductions, and train administration |
| Delegated senior command | *Legatus* | Assignment from a magistrate; increasingly prominent in larger late-Republican commands |

Military tribunes were versatile staff officers whose legion leadership could rotate in pairs rather than fixed commanders of permanent subunits. The quaestor was principally a financial magistrate and, in an overseas command, supervised military funds, pay, equipment deductions, and the train. These should be modeled as `OfficeHolding` and `CommandAssignment` events connecting a person, office, commander, force, dates, legal basis, and source.[^17]
## Cohort transition
The replacement of the maniple by the cohort was gradual. Archaeological and literary evidence indicates that cohorts existed before Marius and were used in second-century campaigning, especially in Spain; manipular and cohortal organization could overlap because a cohort could group several maniples. By the opening decades of the first century BCE, the cohort had become the standard legionary tactical unit.[^18][^19][^20]
### Avoid the Marian switch
A simple `Marius INTRODUCED CohortSystem in 107 BCE` edge would encode an outdated model. Modern research finds little evidence for a comprehensive package of “Marian reforms,” and emphasizes longer-term organizational change plus the growing importance of non-Italian auxiliaries. No ancient source actually says that Marius invented the cohort, and the cohort was in use before his northern campaigns.[^21][^22][^19]

Marius can still be connected to well-supported actions or associations:

- Recruitment of volunteers without the conventional property qualification for the Jugurthine command.
- Intensive training and logistical practices associated with his armies.
- Strong use of cohortal formations.
- Adoption or elevation of the legionary eagle as a common legion standard, which Cambridge’s account associates with his German campaigns.[^23]

Each should be its own source-backed claim rather than part of one monolithic `MarianReform` fact.
## Late Republic
### Cohortal legion
The secure high-level pattern is:

```text
Late-Republican Legion
└── 10 Cohorts
    └── Centuries
        └── Tent or mess groups, where evidenced
```

A conventional nominal reconstruction gives a cohort six centuries and roughly 480 men, producing about 4,800 legionaries at full paper strength. Actual campaign strengths were often lower, and the precise development of century size is not fully documented. The enlarged, five-century first cohort familiar from the Principate should not be made a default Late-Republican feature; scholarship on cohort formation specifically distinguishes the late-Republican legion from the later enlarged first cohort.[^24][^25]

Model nominal organization separately from observed strength:

```text
(:UnitType {name:'Cohort'})
(:EstablishmentPattern {nominalCenturies:6, nominalStrength:480})
(:UnitInstance {name:'Caesar Legio X, 58 BCE'})
(:StrengthObservation {estimatedStrength:..., date:..., basis:...})
```

The late-Republican legion no longer deployed separate *hastati*, *principes*, *triarii*, and *velites* as Polybian troop classes. Legionaries were more uniformly equipped heavy infantry, while cavalry, archers, slingers, and other light troops were increasingly supplied as allied, client, mercenary, or auxiliary contingents.[^20][^26]
### Social War breakpoint
The Social War was a major institutional boundary. Citizenship was extended to Italian communities south of the Po, politically integrating communities that had formerly supplied allied wings. Afterward, Italians could be recruited into citizen legions, while separate Italian *alae* disappeared and non-Italian forces increasingly furnished cavalry and specialist light infantry.[^20][^27]

This recommends a graph transition:

```text
Pre-88 BCE:
AlliedCommunity -> CONTRIBUTED_CONTINGENT -> AlliedWing

Post-88 BCE:
MunicipalCommunity -> RECRUITED_INTO -> CitizenLegion
NonItalianCommunity -> CONTRIBUTED_CONTINGENT -> AuxiliaryForce
```

Do not delete pre-Social War relationships when modeling the later state. Give each `RecruitmentRegime` and `ContributionArrangement` a validity interval.
### Unit identity
Middle-Republican legions were generally raised for campaigns and disbanded rather than maintained as permanent institutions. During the late civil wars, commanders increasingly retained, replenished, numbered, and cultivated durable identities for their legions; Caesar inherited or raised identifiable formations such as VII, VIII, IX, X, XI, and others.[^28][^29]

The model therefore needs two different identity layers:

- `LegionInstance`: a historically particular formation with continuity through time.
- `LegionDesignation`: a number, title, epithet, or commander-specific designation valid during a stated interval.

Do not use `number: 10` as a globally unique legion identifier. Different commanders and periods could use the same numeral, and continuity sometimes involved disbandment, reconstitution, amalgamation, or transfer.
## Supporting components
### Auxiliaries
`Auxilia` is an umbrella category, not one standardized Republican unit type. Middle-Republican Rome already employed substantial non-Italian manpower, while late-Republican armies drew auxiliaries from Gaul, Numidia, Spain, Greece, Crete, Asia Minor, and elsewhere.[^26][^30]

Useful subtypes include:

- `AuxiliaryCavalryContingent`
- `SlingerContingent`
- `ArcherContingent`
- `LightInfantryContingent`
- `NavalMarineContingent`
- `ClientKingContingent`
- `LocalLevy`

Record the supplying community, commander, legal or diplomatic basis, campaign, ethnic or geographic attribution as stated by the source, and whether the label is ancient or modern.
### Engineers and artillery
Republican legions had substantial construction and siege capabilities, but this does not require inventing a permanent modern “engineering battalion.” Model engineering as a capability, duty, specialist role, or task detachment unless a source identifies a formal unit. By Caesar’s era, engineering work was performed by trained legionaries and specialists detailed according to skill rather than necessarily by a separate standing corps.[^31]
### Train and noncombatants
Army organization extended beyond combat units: servants, enslaved attendants, pack animals, merchants, contractors, medical personnel, craftsmen, and baggage accompanied forces. These should not automatically be counted in legionary combat strength. Use `SupportGroup`, `ServantGroup`, `PackTrain`, and `CampFollowerPopulation` with explicit counting rules.
### Navy boundary
The Republican navy is best treated as a related service graph, not nested under every army. Rome created naval magistracies and small squadrons in the late fourth century BCE, depended heavily on *socii navales*, and raised large campaign fleets during the Punic Wars. Connect `FleetInstance`, `Squadron`, `ShipInstance`, `Crew`, and `MarineDetachment` to common `Campaign`, `Commander`, `Polity`, and `Source` nodes.[^32]
## Neo4j ontology
### Core node labels
| Label | Meaning | Example |
|---|---|---|
| `OrganizationModel` | Abstract structural pattern | `Polybian manipular legion` |
| `UnitType` | Reusable class of military unit | `Maniple`, `Cohort`, `Turma` |
| `UnitInstance` | Particular historical formation | `Legio X under Caesar` |
| `ForceInstance` | Army or task force containing several units | `Caesar's Gallic field army, 58 BCE` |
| `TroopCategory` | Personnel class or battlefield role | `Hastati`, `Velites` |
| `BattleLineRole` | Position/function in a deployment | `First line`, `Reserve` |
| `Office` | Constitutional or military office | `Consul`, `Military Tribune` |
| `Person` | Historical individual | `Gaius Marius` |
| `CommandAssignment` | Time-bounded person–office–unit linkage | Marius commanding an army in 104 BCE |
| `RecruitmentRegime` | Rules governing eligibility and levy | Property-qualified citizen levy |
| `EstablishmentPattern` | Nominal composition and strength | 10 maniples of 120 *hastati* |
| `StrengthObservation` | Actual or estimated strength at a date | Caesar’s reported effective strength |
| `Event` | Battle, levy, reform, transfer, mutiny, disbandment | Social War |
| `Place` | Recruitment, station, battle, or origin location | Rome, Numidia |
| `Polity` | Rome, allied community, client kingdom | Massilia, Numidia |
| `Source` | Ancient text, inscription, archaeology, scholarship | Polybius, *Histories* 6 |
| `Claim` | Reified historical assertion | “Cohorts used in Spain before Marius” |
| `Period` | Analytical interval | Middle Republic |
### Relationship types
| Relationship | Domain → range | Purpose |
|---|---|---|
| `INSTANCE_OF` | `UnitInstance` → `UnitType` | Separates historical entities from classes |
| `USES_MODEL` | unit or force → `OrganizationModel` | Time-bounded structural assignment |
| `HAS_COMPONENT_RULE` | model → `EstablishmentPattern` | Nominal composition |
| `COMPONENT_TYPE` | pattern → `UnitType` | Type governed by a composition rule |
| `SUBUNIT_OF` | unit instance → unit/force instance | Actual historical containment |
| `GROUPS` | cohort/model → maniple or century type | Abstract aggregation |
| `HAS_TROOP_CATEGORY` | unit/model → `TroopCategory` | Personnel class within a structure |
| `DEPLOYED_AS` | unit instance → `BattleLineRole` | Battle-specific role |
| `COMMANDED_THROUGH` | unit → `CommandAssignment` | Avoids timeless person-to-unit command edges |
| `HOLDS_OFFICE` | person → `OfficeHolding` | Constitutional career data |
| `ASSIGNED_TO` | command assignment → unit/force | Contextual command |
| `CONTRIBUTED_BY` | contingent → polity | Origin and obligation |
| `RECRUITED_UNDER` | soldier/unit → recruitment regime | Eligibility context |
| `PARTICIPATED_IN` | unit/force → event | Campaign and battle history |
| `OBSERVED_STRENGTH` | unit → strength observation | Actual estimates separate from paper establishment |
| `SUPPORTED_BY_SOURCE` | claim → source | Provenance |
| `ASSERTS_SUBJECT` | claim → entity | Claim subject |
| `ASSERTS_OBJECT` | claim → entity/value node | Claim object |
| `PRECEDES` | organization model → organization model | Chronological sequence without asserting instantaneous replacement |
## Claim-centered pattern
Neo4j supports properties on relationships, but an intermediate node is preferable when a fact connects several entities or carries substantial context. Neo4j’s own modeling guidance recommends intermediary nodes for relationship-like facts involving dates, roles, and shared context.[^33][^34]

For example, do not store only:

```cypher
(marius:Person)-[:COMMANDED]->(legion:UnitInstance)
```

Use:

```cypher
(marius:Person)-[:SUBJECT_OF]->(a:CommandAssignment)
(a)-[:ASSIGNED_TO]->(army:ForceInstance)
(a)-[:IN_ROLE]->(:Office {name:'Consul'})
(a)-[:AUTHORIZED_BY]->(:ImperiumGrant)
(a)-[:DURING]->(:Campaign)
(a)-[:SUPPORTED_BY_SOURCE]->(:Source)
```

Recommended properties on `CommandAssignment` are `validFrom`, `validTo`, `datePrecision`, `certainty`, `status`, and `notes`. This pattern permits concurrent commands, temporary detachments, disputed dates, and differences between formal authority and operational control.
### Structural assertions
Use a `CompositionClaim` or general `Claim` node when composition varies by period or source:

```cypher
(model:OrganizationModel)-[:HAS_COMPOSITION_CLAIM]->(c:CompositionClaim)
(c)-[:PARENT_TYPE]->(legion:UnitType)
(c)-[:CHILD_TYPE]->(maniple:UnitType)
(c)-[:APPLIES_TO_CATEGORY]->(hastati:TroopCategory)
(c)-[:SUPPORTED_BY_SOURCE]->(polybius:Source)
```

Suggested properties:

```text
quantityMin
quantityMax
quantityTypical
nominalStrengthMin
nominalStrengthMax
validFromYear
validToYear
datePrecision
certainty
interpretiveStatus
sourcePassage
```

Store BCE years as astronomical integers if computation matters (`-149` for 150 BCE), but also retain a display form and date precision. A full date should not be fabricated when only a century or approximate phase is known.
## Minimal schema
```cypher
CREATE CONSTRAINT unit_type_id IF NOT EXISTS
FOR (n:UnitType) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT unit_instance_id IF NOT EXISTS
FOR (n:UnitInstance) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT model_id IF NOT EXISTS
FOR (n:OrganizationModel) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT person_id IF NOT EXISTS
FOR (n:Person) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT source_id IF NOT EXISTS
FOR (n:Source) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT claim_id IF NOT EXISTS
FOR (n:Claim) REQUIRE n.id IS UNIQUE;

CREATE INDEX unit_dates IF NOT EXISTS
FOR (n:UnitInstance) ON (n.validFromYear, n.validToYear);

CREATE INDEX claim_dates IF NOT EXISTS
FOR (n:Claim) ON (n.validFromYear, n.validToYear);
```

Neo4j uniqueness constraints prevent duplicate values for constrained properties and should back stable identifiers rather than names. Names, Latin forms, translated labels, and source-specific spellings belong in appellation nodes or arrays because they are not globally unique.[^35][^36]
## Seed model
```cypher
MERGE (polybian:OrganizationModel {
  id:'orgmodel:roman-polybian-legion',
  name:'Polybian manipular legion',
  validFromYear:-290,
  validToYear:-130,
  datePrecision:'approximate'
})

MERGE (legion:UnitType {id:'unittype:legion', name:'Legion'})
MERGE (maniple:UnitType {id:'unittype:maniple', name:'Maniple'})
MERGE (century:UnitType {id:'unittype:tactical-century', name:'Tactical century'})
MERGE (turma:UnitType {id:'unittype:turma', name:'Turma'})
MERGE (hastati:TroopCategory {id:'troop:hastati', name:'Hastati'})
MERGE (principes:TroopCategory {id:'troop:principes', name:'Principes'})
MERGE (triarii:TroopCategory {id:'troop:triarii', name:'Triarii'})
MERGE (velites:TroopCategory {id:'troop:velites', name:'Velites'})
MERGE (polybius:Source {
  id:'source:polybius-histories-6',
  author:'Polybius',
  title:'Histories',
  passage:'6.19-42',
  sourceType:'ancient literary'
})

MERGE (polybian)-[:DESCRIBES_STRUCTURE_OF]->(legion)
MERGE (maniple)-[:SUBTYPE_OF]->(century)
MERGE (polybian)-[:HAS_TROOP_CATEGORY]->(hastati)
MERGE (polybian)-[:HAS_TROOP_CATEGORY]->(principes)
MERGE (polybian)-[:HAS_TROOP_CATEGORY]->(triarii)
MERGE (polybian)-[:HAS_TROOP_CATEGORY]->(velites)

CREATE (c1:Claim:CompositionClaim {
  id:'claim:polybian-hastati-maniples',
  quantityTypical:10,
  unitStrengthTypical:120,
  validFromYear:-290,
  validToYear:-130,
  certainty:'high for Polybius snapshot; period bounds approximate'
})
CREATE (polybian)-[:HAS_COMPOSITION_CLAIM]->(c1)
CREATE (c1)-[:PARENT_TYPE]->(legion)
CREATE (c1)-[:CHILD_TYPE]->(maniple)
CREATE (c1)-[:APPLIES_TO_CATEGORY]->(hastati)
CREATE (c1)-[:SUPPORTED_BY_SOURCE]->(polybius);
```

The sample deliberately treats the date range as approximate and the numerical composition as a sourced model. It should not generate 30 physical maniple nodes unless a particular historical legion instance is being reconstructed.
## Query patterns
### Structure valid in a year
```cypher
MATCH (m:OrganizationModel)-[:HAS_COMPOSITION_CLAIM]->(c:CompositionClaim)
WHERE c.validFromYear <= $year
  AND (c.validToYear IS NULL OR $year <= c.validToYear)
OPTIONAL MATCH (c)-[:PARENT_TYPE]->(parent:UnitType)
OPTIONAL MATCH (c)-[:CHILD_TYPE]->(child:UnitType)
OPTIONAL MATCH (c)-[:APPLIES_TO_CATEGORY]->(cat:TroopCategory)
RETURN m.name, parent.name, child.name, cat.name,
       c.quantityTypical, c.unitStrengthTypical, c.certainty;
```
### Reconstruct an army
```cypher
MATCH (army:ForceInstance {id:$armyId})
MATCH path=(u:UnitInstance)-[:SUBUNIT_OF*1..5]->(army)
RETURN path;
```

Add validity predicates to every containment assignment if the army changed during a campaign. Neo4j’s time-based versioning guidance recommends `validFrom` and `validTo` intervals when point-in-time snapshots and historical traversals are required.[^37]
### Find disagreements
```cypher
MATCH (subject)<-[:ASSERTS_SUBJECT]-(c:Claim)-[:SUPPORTED_BY_SOURCE]->(s:Source)
WHERE c.predicate = $predicate
WITH subject, collect({claim:c, source:s}) AS positions
WHERE size(positions) > 1
RETURN subject, positions;
```

This is particularly valuable for early-Republic structures, cohort chronology, the strength of late-Republic centuries, and claims attributed to Marius.
## Modeling rules
1. **Never make “Roman Army” one unit node.** Use it as a concept or institution connected to many force and unit instances.
2. **Separate type from instance.** `Cohort` is a type; “first cohort of Caesar’s Legio X in 52 BCE” is an instance.
3. **Separate nominal from actual strength.** Establishment tables are not headcounts.
4. **Reify command.** Person-to-unit command requires office, dates, authority, and source.
5. **Reify disputed composition.** Early and transitional structures should be claims, not unconditional edges.
6. **Permit overlapping models.** Maniples and cohorts coexist during the transition.
7. **Distinguish homonyms.** Census century, tactical century, Republican allied *ala*, and Imperial cavalry *ala* are different concepts.
8. **Do not back-project Imperial organization.** The double-strength first cohort, permanent legionary legate, standardized auxiliary regiments, and fully documented eight-man *contubernium* belong primarily to later systems unless specific Republican evidence supports them.
9. **Preserve provenance at passage level.** “Polybius 6” is useful; “Polybius 6.21–26” is better.
10. **Use uncertainty explicitly.** Store confidence, date precision, interpretive status, and competing claims.
## Recommended first implementation
Begin with four organization models:

- `EarlyRepublicanLevyModel`
- `PolybianManipularLegionModel`
- `TransitionalManipleCohortModel`
- `LateRepublicanCohortalLegionModel`

Populate the Polybian model first because its structure is the best documented. Then add one consular army template with two citizen legions, two allied wings, and the *extraordinarii*. Finally, instantiate two test cases—one army from the Second Punic War and one Caesarian field army—to verify that the schema handles radically different recruitment, subordinate formations, command assignments, and unit continuity without changing the ontology.

The decisive design choice is to model **change and evidence**, not merely hierarchy. A static tree can represent Polybius’s legion, but only a temporal claim graph can represent the Republican army across five centuries without turning reconstructions, temporary arrangements, and later Imperial conventions into false timeless facts.

---

## References

1. [The historical period covered by the Roman Republic is a long](https://rksmvv.ac.in/wp-content/uploads/2021/04/Harriet_I._Flower_The_Cambridge_Companion_to_the-Roman-RepublicBookFi.pdf) - There can be little doubt, however, that the exam- ple of Sulla, who marched on Rome with his army a...

2. [[PDF] Introduction - Assets - Cambridge University Press](https://assets.cambridge.org/97811070/93577/excerpt/9781107093577_excerpt.pdf)

3. [Dionysius' Roman Antiquities — Book IV Chapters 1‑23](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Dionysius_of_Halicarnassus/4A*.html) - Of these he formed eighty centuries, whom he ordered to be armed with Argolic bucklers, with spears,...

4. [Early Roman army](https://en.wikipedia.org/wiki/Early_Roman_army) - It is likely that the hoplite element was deployed in a Greek-style phalanx formation in large set-p...

5. [The Republican Roman army - Corvinus](https://corvinus.nl/2016/02/13/the-republican-roman-army/) - Livius tells us that the single line phalanx formation has been abandoned in favour of the manipular...

6. [The Histories of Polybius Book Six translated by Evelyn S. ...](https://www.yorku.ca/inpar/polybius_six.pdf) - He gives the necessary orders to the Tribunes, they to the cavalry officers and centurions, and thes...

7. [Polybius 6.19-42](https://www.thelatinlibrary.com/historians/polyb/polybius5.html) - 24 From each of the classes except the youngest they elect ten centurions according to merit, and th...

8. [Republican Virtues: Merits and Morals in Polybius' ...](https://www.mdpi.com/2409-9252/6/1/1) - Two maniples were dedicated to keeping the ground in Athens are the result of their bad constitution...

9. [Polybius • Histories — Book 6](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Polybius/6*.html) - Part of a complete English translation of Polybius. In each maniple the first tent at either end is ...

10. [Livy - The History of Rome - Book 8](http://www.swartzentrover.com/cotor/e-books/misc/Livy/HOR_08.htm) - There were generally four legions enrolled, consisting each of 5000 men, and 300 cavalry were assign...

11. [LIVY, History of Rome 8](https://www.loebclassics.com/abstract/livy-history_rome_8/1926/pb_LCL191.33.xml?result=68&rskey=Cdw7QQ&print) - When an army had been marshalled in this fashion, the hastati were the first of all to engage. If th...

12. [Turma](https://en.wikipedia.org/wiki/Turma) - A turma was a cavalry unit in the Roman army of the Republic and Empire. In the Byzantine Empire, it...

13. [Roman cavalry - Wikipedia](https://en.wikipedia.org/wiki/Roman_cavalry)

14. [POLYBIUS, The Histories | Loeb Classical ...](https://www.loebclassics.com/view/polybius-histories/2010/pb_LCL138.365.xml?print=&readMode=recto) - The total number of allied infantry is usually equal to that of the Romans, while the cavalry are th...

15. [Polybius Histories](https://pace.biblico.it/polybius-histories-split_loeb?book=6&chapter=26&chapter_to=26) - The total number of allied infantry is usually equal to that of the Romans, while the cavalry are th...

16. [Rome at the End of the Punic Wars [History, Book 6]](https://sourcebooks.web.fordham.edu/ancient/polybius6.asp) - The whole infantry of the allies is usually the same in number with that of the Romans; but the cava...

17. [Collections: How to Roman Republic 101, Part IIIa](https://acoup.blog/2023/08/11/collections-how-to-roman-republic-101-part-iiia-starting-down-the-path-of-honors/) - The other key function of the military tribunes was to be part of a commanders consilium, a council ...

18. [Roman army of the mid-Republic](https://en.wikipedia.org/wiki/Roman_army_of_the_mid-Republic) - The Roman army of the mid-Republic, also called the manipular Roman army or the Polybian army, refer...

19. [Collections: The Marian Reforms Weren't a Thing](https://acoup.blog/2023/06/30/collections-the-marian-reforms-werent-a-thing/) - As it turns out, Marius initiated almost none of these reforms, some of these supposed reforms didn'...

20. [en.wikipedia.org · wiki · Roman_army_of_the_late_RepublicRoman army of the late Republic - Wikipedia](https://en.wikipedia.org/wiki/Roman_army_of_the_late_Republic)

21. [The transformation of the Roman army in the last decades of ...](https://www.taylorfrancis.com/chapters/oa-edit/10.4324/9781351063500-16/transformation-roman-army-last-decades-republic-fran%C3%A7ois-gauthier) - by F Gauthier · 2019 · Cited by 24 — Gaius Marius introduced the most important change in late Repub...

22. [Tactical Reform in the Late Roman Republic](https://www.jstor.org/stable/45019313) - by MJ TAYLOR · 2019 · Cited by 20 — This article discusses the organizational and tactical changes i...

23. [5 - The Spiral of Violence (104–80 BCE) - Cambridge University Press](https://www.cambridge.org/core/books/rome-and-the-making-of-a-world-state-150-bce20-ce/spiral-of-violence-10480-bce/38567A53DDAAAF43D30F5AE8E7943E2F) - Rome and the Making of a World State, 150 BCE–20 CE - April 2018

24. [The Roman Army in Detail: The Problem of the First Cohort](https://www.academia.edu/30802577/The_Roman_Army_in_Detail_The_Problem_of_the_First_Cohort) - One of the facts we know about the Roman imperial legion is that it was divided into ten cohorts. Ni...

25. [The Legion Formation](https://www.karwansaraypublishers.com/en-us/blogs/gary-brueggemans-the-roman-army-ancient-warfare/legion_formations_update) - Caesar mentions that. He found the ridge to be between 150 and 170 meters wide. it would hold about ...

26. [Auxiliaries in the Social War](https://journals.ub.uni-heidelberg.de/index.php/deimos/article/view/110452/108314) - Abstract: The Social War deprived Rome of many of its Italian allies. The recourse to auxiliaries th...

27. [Social War | Roman Republic, Conflict & Causes](https://www.britannica.com/event/Social-War-Roman-history) - Social War, (90–89 bc), rebellion waged by ancient Rome's Italian allies (socii) who, denied the Rom...

28. [List of Roman legions](https://imperiumromanum.pl/en/roman-army/units-of-roman-army/roman-legion/list-of-roman-legions/) - VICTRIX – a legion founded by Julius Caesar in 58 BCE Gifted with the title Victrix – “The Conqueror...

29. [Caesar's legions](https://www.livius.org/articles/person/caesar/legions/) - Light red indicates a normal serving unit; dark red a veteran legion; grey means that it sides with ...

30. [Gauthier, F. 2019. “Auxiliaries and War Financing in the ...](https://www.academia.edu/40753436/Gauthier_F_2019_Auxiliaries_and_War_Financing_in_the_Republic_Journal_of_Ancient_History_7_251_268_Sample_page_) - Recent research indicates that non-Italian soldiers notably contributed to the Republic's war effort...

31. [Roman Legions: Structure and Ranks](https://www.roman-britain.co.uk/military/the-structure-and-soldiers-of-the-roman-army/structure-and-ranks-of-a-legion/) - Immunis was a soldier immune from common drudgery due to specialist skills such as engineers, artill...

32. [Roman navy](https://en.wikipedia.org/wiki/Roman_navy) - Thus in 261 BC, the Roman Senate set out to construct a fleet of 100 quinqueremes ... Subsequently, ...

33. [Modeling designs - Getting Started](https://neo4j.com/docs/getting-started/data-modeling/modeling-designs/) - Intermediary nodes are nodes that contain data that need to be in the graph but don't seem to fit ne...

34. [Adding Intermediate Nodes | Graph Data Modeling ...](https://graphacademy.neo4j.com/courses/modeling-fundamentals/8-adding-intermediate-nodes) - Intermediate nodes allow you to add context and additional information to relationships, making your...

35. [Constraints - Cypher Manual](https://neo4j.com/docs/cypher-manual/current/schema/constraints/) - Property uniqueness constraints: ensure that the combined property values are unique for all nodes w...

36. [Create constraints - Cypher Manual](https://neo4j.com/docs/cypher-manual/current/schema/constraints/create-constraints/) - Property uniqueness constraints ensure that the property values are unique for all nodes with a spec...

37. [Versioning - Getting Started](https://neo4j.com/docs/getting-started/data-modeling/versioning/) - This page gives an overview of the different ways you could model data in order to keep track of cha...

