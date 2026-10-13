# Roman Republican Institutions and Military Hierarchies for Neo4j

## Executive overview

The Roman Republic should not be represented as one timeless constitutional or military hierarchy. It is better modeled as a set of **institutions, offices, organizational patterns, powers, and assignments whose validity changes over time**. The central constitutional domains were the Roman people acting through several assemblies, annually elected magistrates, the Senate, plebeian institutions, provincial commands, and public priestly colleges. Polybius’s mid-Republican description usefully presents consuls, Senate, and people as mutually dependent centers of power, but it is a description of a particular historical configuration rather than a constitution valid without change from 509 to 27 BCE.[^1][^2][^3]

The military requires the same approach. The early levy, the Polybian manipular army, the long maniple-to-cohort transition, and the late-Republican cohortal army should be separate `OrganizationalPattern` nodes. The navy was even less institutionally continuous: Republican fleets were commonly raised for campaigns, commanded by magistrates or promagistrates, and staffed heavily by maritime allies; the permanent territorial fleets and standardized hierarchy familiar from the Principate should not be projected backward.[^4][^5][^6]

The recommended graph architecture therefore separates:

- `Institution`: Senate, *comitia centuriata*, consulship, College of Pontiffs, a province.
- `OfficeType`: consul, praetor, censor, tribune of the plebs, proconsul.
- `RoleType`: presiding officer, army commander, judge, treasury supervisor, ship captain.
- `PowerType`: *imperium*, *potestas*, *intercessio*, *coercitio*, *auspicium*, *sacrosanctitas*.
- `OrganizationalPattern`: Polybian manipular legion, transitional legion, late-Republican cohortal legion.
- `UnitType`: legion, *ala sociorum*, cohort, maniple, century, *turma*, fleet, squadron, ship.
- Reified temporal assertions: `OfficeTenure`, `CommandAssignment`, `CompositionClaim`, `PowerGrant`, and `InstitutionalState`.

This prevents a person from simply being connected to “Rome” as `HELD_ROLE`, or a legion from being permanently connected to ten cohorts irrespective of date and evidence.

## Period framework

Use periods as navigational aids, not hard ontological containers. Institutional change was asynchronous, and boundaries are often conventional or disputed.

| Suggested period | Approximate dates | Political configuration | Military configuration |
|---|---:|---|---|
| Early Republic | traditionally 509–367 BCE | Developing chief magistracy; patrician-plebeian conflict; creation or differentiation of tribunate, quaestorship, censorship, and alternative consular tribunes | Citizen levy; probable heavy-infantry/phalanx phase; evidence is late and reconstructive |
| Institutional consolidation | 367–287 BCE | Restored consulship, separate praetorship and curule aedileship; plebeian access expands; plebiscites become generally binding by 287 | Transition toward manipular organization, conventionally associated with fourth- and early-third-century warfare |
| Middle Republic | 287–133 BCE | Mature Senate–magistrates–assemblies system; expanding provincial administration; standing criminal courts begin in 149 | Polybian manipular legion; paired Roman legions and allied wings in a consular army; large campaign fleets during major wars |
| Late-Republic transition | 133–82 BCE | Tribunician legislation and political conflict; extraordinary commands grow; Social War transforms the citizen body | Maniples and cohorts overlap; increasing non-Italian auxiliaries; avoid a single “Marian reform” event |
| Sullan settlement | 82–70 BCE | Expanded Senate and permanent courts, regulated *cursus honorum*, weakened tribunate | Cohortal organization increasingly normal; provincial/promagisterial commands central |
| Restored late Republic | 70–49 BCE | Tribunician powers restored; large provincial and extraordinary commands coexist with ordinary offices | Cohort as principal tactical unit; legates increasingly exercise delegated legion-level commands |
| Dictatorship and civil war | 49–44 BCE | Caesar accumulates consulship, dictatorship, proconsular and tribunician powers | Personal multi-legion field armies and campaign fleets |
| Triumviral Republic | 43–32/27 BCE | Legally constituted *triumviri rei publicae constituendae* override ordinary institutions while those institutions continue formally | Large dynastic armies and fleets; transition toward the Augustan settlement |

The early chronology deserves an explicit uncertainty flag. Ancient historians’ narratives of the first Republic were written centuries later, and even the original title and shape of the chief magistracy are debated. Britannica, for example, notes both the traditional replacement of kingship by two annual magistrates and the early use of the title *praetor*, while the chief magistracy alternated between consuls and consular tribunes from 444 to 367 BCE.[^7]

## Constitutional graph

### Constitutional core

At the mature Republic’s core were three interacting domains rather than modern executive, legislative, and judicial branches. Magistrates initiated and implemented public action; the people elected magistrates, enacted laws, and exercised important judicial and war-and-peace powers; the Senate coordinated finance, foreign affairs, provincial and military policy through decrees, prestige, and continuity. Polybius emphasizes that each domain depended upon and could obstruct the others.[^2][^8][^1]

Model the following top-level institutions:

| Institution | Institutional kind | Principal associated roles or functions | Important relationships |
|---|---|---|---|
| *Populus Romanus* | Corporate political community | Sovereign electorate, legislator, public court, ratifier of war/peace and agreements | `CONSTITUTED_ASSEMBLY`, `ELECTED`, `ENACTED`, `RATIFIED` |
| Senate | Deliberative council | Policy deliberation, finance and treasury control, foreign relations, provincial assignments, military supply, investigations, triumphal authorization | `ISSUED_DECREE`, `ADVISED`, `ALLOCATED_PROVINCE`, `AUTHORIZED_EXPENDITURE` |
| Magistracies | Public-office system | Convening, proposal, administration, jurisdiction, command, religious action | `OFFICE_IN_SYSTEM`, `EXERCISED_POWER`, `PRESIDED_OVER` |
| Popular assemblies | Decision institutions | Elections, legislation, adjudication, war/peace decisions; competence differs by assembly | `ELECTED_OFFICE`, `PASSED_MEASURE`, `HEARD_APPEAL` |
| Plebeian institutions | Status-based civic institutions | Protection of plebeians, plebeian elections and resolutions, tribunician veto and legislation | `ELECTED_TRIBUNE`, `PASSED_PLEBISCITE`, `INTERCEDED_AGAINST` |
| Public priesthoods | Sacral-public institutions | Maintenance of *pax deorum*, ritual law, auspices, calendars, sacred texts, public rites | `AUTHORIZED_RITE`, `INTERPRETED_AUSPICES`, `SUPERVISED_CULT` |
| Provinces and commands | Territorial/functional assignments | Jurisdiction, taxation supervision, military command, diplomacy and administration | `ASSIGNED_AS_PROVINCIA`, `GOVERNED_BY`, `COMMANDED_IN` |
| Public courts | Judicial institutions | Ad hoc or standing inquiry into specified offenses | `PRESIDED_BY`, `HAD_JURISDICTION_OVER`, `DREW_JURORS_FROM` |

Do not represent the Senate as a modern legislature. Formally, legislation required a magistrate’s proposal and a popular vote, while the Senate’s *senatus consulta* were advisory decrees; in practice its continuity, control of resources, collective experience, and political authority made it the Republic’s central policy institution.[^9][^10][^11]

### Popular institutions

The several assemblies were different organizations of the citizen body, not “houses” in a bicameral legislature. A citizen might belong simultaneously to a curia, century, and tribe, with collective votes counted by unit rather than by a simple total of individual ballots.[^10]

| Institution | Membership/organization | Core competencies | Presiding role | Temporal notes |
|---|---|---|---|---|
| *Comitia curiata* | Citizens organized by 30 curiae; later often represented procedurally by lictors | Archaic electoral and legal functions; later *lex curiata de imperio*, adoptions, wills, and sacral matters | Consul, praetor, or appropriate magistrate | Politically central in the archaic system; predominantly formal/sacral in the mature Republic |
| *Comitia centuriata* | Citizens organized by centuries and census class | Elect consuls, praetors, and censors; major trials/appeals; legislation; decisions concerning war | Consul or praetor | Military and census structure gave wealthier centuries structural priority; functions evolved over time |
| *Comitia tributa populi* | Entire people organized by territorial tribes | Elect quaestors, curule aediles, and some lesser magistrates; legislation and fines/judicial business | Consul, praetor, or curule aedile depending on business | Must be distinguished from the plebeian council even though both voted by tribes |
| *Concilium plebis* | Plebeians organized by tribes; patricians excluded | Elect tribunes and plebeian aediles; pass *plebiscita*; hear matters brought by plebeian officials | Tribune of the plebs or plebeian aedile | Emerged from the Conflict of the Orders; by the *lex Hortensia* of 287 BCE, plebiscites bound the whole citizen body |
| *Contio* | Informal public meeting, not a voting assembly | Hear speeches, debate and receive notice of proposals | A magistrate or tribune with convening authority | Model as a meeting/event type, not as a legislative institution |

The centuriate assembly elected magistrates with *imperium* and censors, while the tribal institutions elected lower magistrates; the people also passed or rejected laws and made key decisions about war, peace, alliances, and treaties. Keep `ComitiaTributa` and `ConciliumPlebis` as distinct nodes even when a source loosely calls both a “tribal assembly.”[^12][^8][^11]

### Ordinary magistracies

An office is not a role and a role is not a power. For example, `Consul` is an `OfficeType`; “president of the Senate,” “commander of an army,” and “proposer of legislation” are `RoleType` nodes; *imperium* and *ius agendi cum populo* are `PowerType` nodes. This makes it possible to model changes in competence without inventing a new consulship.

| Office type | Selection and normal term | Associated roles | Powers/attributes to model | Key temporal qualifications |
|---|---|---|---|---|
| Consul | Two elected by *comitia centuriata*; normally annual | Chief ordinary magistrate, Senate convener/president, assembly convener, legislative proposer, diplomat, levy authority, field commander | *Imperium*, *potestas*, auspices, coercive power, mutual *intercessio* | Primarily generals in much of the Republic; provincial command often continued afterward through prorogation |
| Praetor | Elected by *comitia centuriata*; annual | Judge/jurisdictional magistrate, substitute civil executive, army commander, provincial governor, court president | Lesser *imperium* than consul, jurisdiction, edict, convening powers | Separate urban praetorship traditionally created in 367/366; peregrine praetor added around 242; numbers expanded with provinces and courts |
| Censor | Two elected by *comitia centuriata* periodically; tenure normally up to 18 months | Census taker, classifier of citizens, reviewer of Senate/equestrian order, public-morals supervisor, public-contract administrator | Censorial *potestas* but no military *imperium* | Created traditionally in 443; office held intermittently rather than annually |
| Quaestor | Elected, normally annual | Treasury officer, military paymaster, financial assistant to consul or governor, provincial financial officer | Financial and administrative *potestas* | Two elected from 447 in the traditional chronology, four from 421; numbers later grew, reaching twenty under Sulla |
| Curule aedile | Two elected by tribal assembly; annual | Urban administration, markets, grain and public order, temples/buildings, games | Curule *potestas*, limited jurisdiction and fines | Created in the settlement of 367/366; patrician association weakened over time |
| Plebeian aedile | Two elected by *concilium plebis*; annual | Assistant to tribunes, plebeian records and cult, later urban markets, provisions, buildings and games | Plebeian *potestas* | Origin linked to the early plebeian organization; functions increasingly overlap with curule aediles |
| Tribune of the plebs | Ten plebeians elected by *concilium plebis*; annual | Protector of citizens/plebeians, convener of plebeian council and Senate, legislative proposer, political prosecutor | Sacrosanctity, *auxilium*, *intercessio*, coercive and convening powers | Powers grew during the Conflict of the Orders, were sharply curtailed by Sulla, and restored in stages by 70 BCE |
| Lesser boards (*vigintisexviri* and predecessors) | Elected or appointed depending on board and period | Minting, roads, prisons/executions, judicial assistance, colonial/land assignments | Board-specific delegated authority | Model each board separately; do not treat “minor magistrate” as one office |

Consuls commanded armies, convened the Senate and assemblies, executed public decisions, and represented the state abroad, while each could block the other. Praetors combined jurisdiction with potential military and provincial command; quaestors handled treasury and campaign finances; censors conducted the census, revised status lists, and contracted public works.[^13][^14][^15][^16][^7]

### Extraordinary offices

| Office or commission | Trigger/selection | Associated roles | Graph treatment |
|---|---|---|---|
| Dictator | Traditionally nominated for a specified emergency under formal authorization; normally expected to complete the task or leave office within six months | Supreme emergency commander or task-specific commissioner | One `OfficeType`, but every tenure must link to a `Causa` such as war, elections, or constitutional settlement; Sulla’s and Caesar’s dictatorships require distinct institutional states |
| *Magister equitum* | Appointed by dictator | Deputy commander and second office in the dictatorship | Link to the dictator’s tenure with `DEPUTY_TO`; do not treat as an autonomous standing magistracy |
| Interrex | Successive short appointments when regular elections could not be held | Conduct elections and restore ordinary magistracy | Model each very short tenure; link to an `InterregnumEvent` |
| *Decemviri legibus scribundis* | Special ten-man board, 451–449 BCE in tradition | Draft and publish laws; temporarily replace normal chief magistrates | `ExtraordinaryCommission` tied to the Twelve Tables episode |
| Consular tribunes | Elected in years using this alternative system, 444–367 BCE | Exercise consular power, especially command | Office title and powers should be separate; do not label holders “consuls” |
| *Tresviri rei publicae constituendae* | Created by *lex Titia* in 43 BCE and renewed | Reconstitute the state, appoint magistrates and governors, legislate, command, override ordinary authorities | Legal extraordinary commission, unlike the informal “First Triumvirate”; model 43–38 and renewal as separate `InstitutionalState` records |

The Second Triumvirate was a formal five-year commission created by law in 43 BCE, renewed in 37, and endowed with powers superior to ordinary magistrates; ordinary offices nevertheless continued beneath it. This is a strong case for modeling **concurrent authority layers**, not replacing all ordinary institutions with one “Triumvirate government” node.[^17][^18]

### Promagistrates and provinces

A *provincia* was originally a sphere of assigned responsibility and only gradually became a durable territorial administrative unit. Model both senses with `AssignmentScope`, permitting a `ProvincialAssignment` to target a territory, war, fleet, judicial function, or combined command.

| Office/role | Source of authority | Associated roles | Relationships |
|---|---|---|---|
| Proconsul | Prorogued or specially granted consular *imperium* | Provincial governor, senior judge, army/fleet commander, diplomatic representative | `HELD_PROMAGISTRACY`, `ASSIGNED_PROVINCIA`, `COMMANDED_FORCE` |
| Propraetor | Prorogued praetorian *imperium* | Governor, judge, commander | Same pattern with lower rank/prestige, not necessarily less practical autonomy |
| Provincial quaestor | Election plus assignment to governor/province | Treasury and revenue officer, paymaster, deputy under some conditions | `ASSISTED_GOVERNOR`, `ADMINISTERED_FINANCE` |
| Legate (*legatus*) | Delegation by Senate, magistrate, promagistrate, or special law | Envoy, adviser, subordinate field commander, legion commander in late-Republican usage | Reify `Delegation` because authority derives from a principal and a mission |
| Prefect (*praefectus*) | Appointment/delegation | Commander or administrator of a specified body, district, fleet, cavalry, camp, or technical function | Require a subtype or governed object; never infer duties from the bare title |

Republican governors were normally consuls, praetors, proconsuls, or propraetors and combined jurisdiction with military command; provincial staffs could include quaestors and legates. The graph should therefore allow one tenure to carry several roles simultaneously rather than creating a modern “civil governor” separate from “military commander.”[^19]

### Senate roles

The Senate itself held institutional functions, while individuals held positions or situational roles within it.

- `Senator`: membership status, normally long-term but reviewable by censors.
- `PrincepsSenatus`: precedence and the privilege of speaking first, not a head of government.
- `PresidingMagistrate`: consul, praetor, or tribune who validly convened a particular meeting.
- `FirstSpeaker`: context-specific order in a meeting.
- `CommitteeMember`, `Envoy`, or `Legate`: temporary assignments authorized through a decree.
- `TriumphApplicant` and `TriumphAwardee`: roles in a process, not offices.

The Senate regulated treasury disbursement, foreign embassies, Italian investigations, military supply, prorogation, and triumphs in Polybius’s account, while the assemblies retained legally decisive electoral, legislative, and judicial functions. Represent those actions as event or decision nodes rather than timeless edges such as `(Senate)-[:CONTROLLED]->(ForeignPolicy)`.[^20][^1][^2]

### Courts and justice

Before standing courts, criminal jurisdiction could involve magistrates, popular trials, the Senate, or special inquiries. The first permanent criminal court, the *quaestio de repetundis*, was established in 149 BCE for provincial extortion; additional standing courts later covered electoral corruption, treason, homicide, poisoning, public violence, and misuse of public funds, commonly under praetorian presidents.[^21][^22]

Recommended nodes and roles:

- `CourtType`: popular trial, *quaestio extraordinaria*, *quaestio perpetua*.
- `CourtInstance`: a specific tribunal in a year or case.
- `JurisdictionType`: extortion, bribery, treason, homicide, forgery, violence.
- `CourtPresident`: usually a praetor or assigned *iudex quaestionis*.
- `Prosecutor`, `Defendant`, `Patron/Advocate`, `Juror`, `Witness`.
- `JuryEligibilityRule`: senators, equestrians, *tribuni aerarii*, or a mixed panel, each with dates and authorizing law.

Do not encode “the Senate controlled the courts” as a permanent fact. Jury composition changed repeatedly, including senatorial, equestrian, Sullan senatorial, and post-70 mixed arrangements.[^22][^21]

### Public religion

Roman public religion was constitutional infrastructure: magistrates needed valid auspices and rites, and priestly authorities preserved and interpreted sacral rules. The major colleges and roles should therefore be connected to public decisions, assemblies, wars, treaties, calendars, and prodigy responses rather than isolated in a “religion” subgraph.

| Institution | Roles to associate | Principal functions |
|---|---|---|
| College of Pontiffs | Pontifex maximus, pontiff, *rex sacrorum*, flamens, Vestals | Supervise public and private sacred law, calendar and ritual practice; advise magistrates |
| College of Augurs | Augur | Interpret auspices; assess whether public acts were religiously valid |
| *Decemviri/Quindecimviri sacris faciundis* | Keeper/interpreter of Sibylline books | Consult sacred books at Senate’s direction; recommend rites and oversee adopted cults |
| *Tresviri/Septemviri epulones* | Epulo | Organize sacred banquets and festival ritual |
| Fetial college | Fetial, *pater patratus* | Ritual procedure for demands, declarations of war, and treaties |
| Arval Brethren and other sodalities | College member, ritual officer | Specialized public cult observance |

The College of Pontiffs comprised the pontifex maximus, other pontiffs, *rex sacrorum*, flamens, and Vestals; the other great colleges included augurs, keepers of the Sibylline books, and epulones. A priesthood may be held concurrently with a magistracy, so use an independent `ReligiousTenure` rather than making priesthood a subtype of political career stage.[^23][^24]

## Political changes over time

### Early differentiation

The early Republic should be modeled as a series of institutional claims rather than as a finished constitution appearing in 509 BCE. Traditional chronology places the plebeian tribunate around 494, elected quaestors in 447, censorship in 443, consular tribunes intermittently from 444 to 367, and the separate praetorship and curule aedileship in 367/366.[^25][^26][^7]

Use `certainty`, `datePrecision`, `sourceTradition`, and `scholarlyStatus` on the associated claim nodes. A traditional foundation date can coexist with a claim that an office developed gradually.

### Mature Republic

After 287 BCE, the institutions often treated as the “classic” Republic were in place: annual collegial magistracies, assemblies with differentiated electoral competence, a politically dominant Senate, plebeian legislation binding the whole community, and an expanding system of prorogued commands. Polybius’s Book 6 is an especially valuable snapshot of this system in the age of the Hannibalic War, not an exhaustive constitutional code.[^3][^1]

Expansion produced new provinces, more praetors and quaestors, longer commands, and permanent judicial institutions. The graph should treat each numerical expansion or competence change as an `InstitutionalState`, for example `(Praetorship)-[:HAS_STATE]->(:InstitutionalState {count: 2, validFrom: -242, ...})`, instead of overwriting a single `count` property.[^16]

### Sullan and post-Sullan states

Sulla’s legislation of 82–80 BCE expanded the Senate, increased quaestors and praetors, made the quaestorship a route to automatic senatorial entry, regularized the office sequence, reorganized standing courts, and restricted the tribunate. Scholars agree on the broad changes while continuing to debate their exact purpose and the completeness of the surviving reconstruction.[^27][^28]

Model at least three separate states:

- `SullanSettlement` (82/81–75 BCE): restricted tribunate and senatorial juries.
- `PartialRestoration` (75–70 BCE): staged erosion of restrictions.
- `RestoredTribunateAndMixedJuries` (from 70 BCE): tribunician powers restored and senatorial monopoly over juries ended.[^29][^22]

### Dictatorship and triumvirate

Late-Republican actors accumulated powers that normally belonged to different offices. Caesar, for example, could be dictator, consul, proconsul, and holder of tribunician powers at overlapping times; these should be independent tenure or grant nodes joined to the same person and bounded by dates.[^30]

The *tresviri rei publicae constituendae* were a formal magistracy, while the “First Triumvirate” was an informal political alliance. Use `PoliticalAlliance` for the latter and `ExtraordinaryCommission` plus `OfficeTenure` for the former.[^18][^17]

## Army hierarchy

### Modeling principle

Separate **organizational type**, **historical force**, and **command appointment**:

- `UnitType`: abstract legion, maniple, cohort, century.
- `OrganizationalPattern`: a dated template saying which unit types compose another.
- `MilitaryUnit`: an attested legion, allied wing, cohort, fleet, or ship.
- `CompositionClaim`: a source-backed assertion that a parent contained a number of child units in a context.
- `CommandAssignment`: a person commanded a force in a role, for a campaign and interval, under a superior or legal grant.

Nominal strengths belong on `EstablishmentClaim`, not on `UnitType`, because actual strengths varied and even ancient descriptions may idealize. Polybius gives 4,200 infantry and 300 cavalry as the ordinary legion, rising to 5,000 infantry in danger; those figures describe his levy system and should not become universal legion properties.[^31][^1]

### Early citizen levy

Evidence for the earliest Republican army is sparse and retrospective. A cautious hierarchy is:

```text
Roman political community
└── chief magistrate(s) with imperium
    └── annual citizen levy / field army
        ├── heavy infantry body, probably phalanx-like in some phases
        ├── lighter or less wealthy infantry
        └── citizen cavalry
```

The early heavy infantry is often reconstructed as Greek-style hoplites fighting in a phalanx, but this should be encoded as a medium- or low-confidence `OrganizationalClaim`, not a fully specified unit tree. Avoid projecting Polybius’s 30-maniple legion, Caesar’s ten cohorts, or imperial legionary ranks into the fifth century BCE.[^32][^33]

Suggested role types are `LevyCommander`, `ChiefMagistrateCommander`, `Infantryman`, `Cavalryman`, and possibly `Centurion`, but early uses of “century” may be civic, census, or military and should not automatically imply a later tactical century.

### Manipular system

For the third and much of the second century BCE, use the following Polybian hierarchy:

```text
Consular army
├── Consul — overall commander
├── Quaestor — finance and pay
├── Roman Legion A
│   ├── 6 military tribunes
│   ├── Hastati: 10 maniples
│   │   └── each maniple: 2 centuries, 2 centurions, 2 optiones, standards
│   ├── Principes: 10 maniples
│   │   └── each maniple: 2 centuries
│   ├── Triarii: 10 maniples
│   │   └── each maniple: 2 centuries
│   ├── Velites distributed among maniples
│   └── Legionary cavalry: 10 turmae
│       └── each turma: 3 decurions, with the first commanding
├── Roman Legion B — same pattern
├── Right allied wing (dextera ala)
├── Left allied wing (sinistra ala)
├── Allied extraordinarii
└── 12 praefecti sociorum — allied command cadre
```

Polybius assigns six military tribunes to each legion and makes them subordinate to the consuls. In each heavy-infantry maniple, two centurions command its two halves/centuries, each with an *optio*; the legion’s 300 cavalry are divided into ten *turmae* with three decurions each.[^34][^1]

The nominal troop distribution for a 4,200-infantry legion is:

| Component | Nominal personnel | Subdivision |
|---|---:|---|
| Velites | 1,200 | Distributed among the maniples rather than forming a fourth line of ten independent maniples |
| Hastati | 1,200 | 10 maniples; 20 centuries |
| Principes | 1,200 | 10 maniples; 20 centuries |
| Triarii | 600 | 10 maniples; 20 centuries |
| Citizen cavalry | 300 | 10 *turmae* |

These figures derive from Polybius’s idealized levy description. A maniple is therefore best represented as containing two `CenturySlot` entities while its establishment strength depends on troop class: the hastati and principes maniples are nominally larger than triarii maniples.[^1]

### Allied hierarchy

The allied component was not merely “auxiliary troops attached to a legion.” A standard Polybian consular army paired the Roman legions with Italian allied contingents organized into right and left wings; allied infantry was usually comparable in number to Roman infantry and allied cavalry substantially more numerous. Selected allied troops formed the *extraordinarii*, located near and directly useful to the consul.[^35][^31]

Recommended hierarchy:

```text
Consular army
└── Allied contingent
    ├── 12 praefecti sociorum
    ├── Right ala sociorum
    │   ├── allied infantry cohorts/contingents
    │   └── allied cavalry turmae/contingents
    ├── Left ala sociorum
    │   ├── allied infantry cohorts/contingents
    │   └── allied cavalry turmae/contingents
    └── Extraordinarii
        ├── selected infantry
        └── selected cavalry
```

Use `ContingentContribution` to connect an allied community to the force, with required/provided numbers, unit form, commander, campaign, and source. This preserves the distinction between the political relationship `Rome—ALLY_OF—Community` and the military fact that a particular community supplied troops in a particular year.

### Maniple-to-cohort transition

Do not create a `MarianReform` event that instantaneously replaces every maniple with a cohort in 107 BCE. Modern scholarship finds little evidence for a comprehensive reform package by Marius; cohorts appear before him, particularly in Spanish warfare and allied organization, and the change was gradual.[^5][^36][^37]

Use overlapping pattern validity:

| Pattern | Suggested validity | Modeling note |
|---|---|---|
| `ManipularLegionPattern` | approximately fourth century–late second century BCE | High confidence for the Polybian second-century description; lower at both chronological edges |
| `CohortAsOperationalGrouping` | at least later third/second century BCE | Cohorts may group maniples or allied contingents without abolishing manipular substructure |
| `TransitionalLegionPattern` | approximately 140s–90s BCE | Both maniple and cohort terminology/organization may be valid depending on army and source |
| `CohortalLegionPattern` | increasingly dominant from Social War/first century BCE | Cohort is the main tactical subdivision; do not assume Augustan first-cohort arrangements |

This overlap can be represented with competing `CompositionClaim` nodes carrying `context`, `confidence`, and citations rather than mutually exclusive global start/end dates.

### Late-Republican cohortal army

A safe late-Republican hierarchy is:

```text
Field army / provincial army
├── magistrate or promagistrate with imperium
│   ├── quaestor — finance/logistics
│   ├── legates — delegated commands and staff functions
│   ├── military tribunes — senior officers/staff, variable operational role
│   └── prefects — appointed commanders of specified components/functions
├── legion
│   ├── 10 cohorts, as the normal tactical model
│   │   └── centuries
│   │       ├── centurion
│   │       ├── optio
│   │       ├── signifer and other junior/specialist posts
│   │       └── legionaries
│   └── senior centurions, including primus pilus in attested usage
├── cavalry contingents
├── auxiliary infantry, archers, slingers, and specialists
└── allied/client contingents
```

The commander of the whole army remained a magistrate or promagistrate whose authority arose from *imperium*. Legates acted under delegated authority and increasingly received individual legion commands in commanders such as Caesar’s armies; military tribunes continued but should not be forced into the standardized imperial hierarchy.[^38][^39]

Avoid importing these mainly imperial features into the Republican template without case-specific evidence:

- A permanent `legatus legionis` as the universal formal commander of every legion.
- One senatorial *tribunus laticlavius* plus five equestrian *tribuni angusticlavii*.
- A permanent *praefectus castrorum* as third in command.
- A double-strength first cohort and exactly 59 centurions.
- Fixed long-service professional careers, permanent bases, and Augustan discharge terms.

The late Republic moved toward cohortal tactics and longer service in prolonged campaigns, but full institutional professionalization and standardized permanent service belong principally to the Augustan settlement.[^40][^5]

### Army role vocabulary

| RoleType | Normal bearer/context | Commands or serves | Modeling caution |
|---|---|---|---|
| `ArmyCommander` | Consul, dictator, praetor, proconsul, propraetor, or special commander | Whole army/provincia | Legal authority comes from an office or special grant |
| `Legate` | Senator delegated by a commander or Senate | Detachment, legion, wing, mission, or staff function | A relationship of delegation, not one fixed rank |
| `MilitaryTribune` | Elected or appointed officer | Legion-level command/administration; role changes over time | Do not merge with tribune of the plebs |
| `PraefectusSociorum` | Roman officer appointed over allies | Allied wings/contingents | Polybian system; not an imperial auxiliary prefect |
| `Centurion` | Professional or experienced unit officer | Century and, through seniority, maniple/cohort functions | Grades and precedence vary by period |
| `Optio` | Deputy chosen under centurion/decurion | Assists unit commander and rear-rank control | Represent as deputy assignment to a command slot |
| `Decurion` | Cavalry officer | Portion of a *turma*; senior decurion commands the whole in Polybius | Do not automatically equate Republican and imperial grades |
| `Signifer/Vexillarius` | Standard bearer | Standard and associated administrative/morale function | Terminology is source- and period-sensitive |
| `Legionary`, `Velite`, `Hastatus`, `Princeps`, `Triarius` | Soldier roles/classes | Rank and file | The latter four belong especially to the manipular pattern |
| `Auxiliary/AlliedCommander` | Local leader, prefect, or Roman delegate | Non-legionary contingent | Preserve citizenship and political source of contingent |

## Navy hierarchy

### Institutional development

The Republican navy was a succession of mobilized fleets, allied contributions, ships, and commands rather than a continuous service matching the later imperial fleets. Maritime allies and Greek or Italian communities supplied much of the shipping and personnel, and naval operations generally supported wider land campaigns.[^4]

Early naval administration is disputed. Livy’s tradition associates *duumviri navales classis ornandae reficiendaeque causa* with the late fourth century, while older scholarship posited naval quaestors in 267; more recent work disputes whether a distinct office of *quaestores classici* existed at all. Encode the propositions as competing claims rather than selecting one silently.[^41][^42][^43]

### Campaign fleet hierarchy

A defensible Republican hierarchy is:

```text
Roman state / campaign command
└── magistrate or promagistrate with imperium
    ├── legate or praefectus classis — delegated fleet command when appointed
    └── classis — campaign fleet
        ├── squadron/division
        │   └── navarchus — squadron commander in common reconstruction
        └── ship
            ├── trierarchus — ship commander/captain
            ├── gubernator — pilot/helmsman
            ├── celeusta — rowing officer
            ├── proreta — bow/lookout officer
            ├── centurion — commands embarked fighting personnel or military complement
            ├── epibatae / marines
            ├── remiges — rowers
            └── sailors and specialists
```

Republican high command normally belonged to a serving consul, praetor, or promagistrate; experienced legates and prefects could exercise delegated fleet or squadron command. Evidence for lower naval ranks is uneven and relationships among *navarchus*, *trierarchus*, and shipboard centurion are not always clear, so the graph should use `commandDomain` values such as `fleet`, `squadron`, `ship-nautical`, and `ship-combat` instead of forcing every ship into one unqualified chain.[^44][^45][^6]

### Parallel shipboard chains

A ship has at least two functional hierarchies:

| Domain | Superior role | Subordinate roles | Function |
|---|---|---|---|
| Command | *Trierarchus* | Whole ship’s complement | Overall responsibility for vessel/mission |
| Navigation | *Gubernator* | Lookouts, bow officer, sailors | Steering, navigation, seamanship |
| Propulsion | *Celeusta* | Rowers (*remiges*) | Coordinate rowing rhythm and effort |
| Combat | Centurion or appointed marine commander | Marines/*epibatae*, missile troops, soldiers | Boarding, defense, and fighting ashore |
| Administration/technical | Pay/clerical and specialist personnel | Carpenters, medical and maintenance specialists | Sustain ship and crew |

An inscription summarized in modern scholarship lists a Republican command with a legate over the whole fleet, a *nauarchos* over a squadron, and ship personnel including *trierarchos*, *gubernator*, *keleustes/celeusta*, *proreus/proreta*, doctor, marines, and rowers. This is preferable to borrowing a fully standardized imperial naval table.[^45]

### Naval unit vocabulary

| UnitType | Definition | Parent | Commander role |
|---|---|---|---|
| `Classis` | Fleet assembled for a campaign, sea area, or commander | State, army, or provincial command | Magistrate/promagistrate; delegated fleet prefect or legate |
| `FleetDivision` | Tactical or administrative division | Fleet | Legate, prefect, or other appointed officer |
| `Squadron` | Group of ships; number varies | Fleet/division | *Navarchus* where attested or reconstructed |
| `Warship` | Individual fighting vessel | Squadron/fleet | *Trierarchus* or named captain |
| `Transport` | Troop, horse, or supply vessel | Convoy/fleet | Captain/shipmaster |
| `MarineDetachment` | Embarked fighting unit | Ship | Centurion or other military officer |
| `Crew` | Nautical and rowing complement | Ship | Ship commander with functional subordinates |

Do not create permanent Republican counterparts of the fleets at Misenum and Ravenna; those standing praetorian fleets belong to Augustus’s post-Republican settlement.[^46][^44]

## Recommended Neo4j schema

### Core labels

```text
:Polity
:Institution
:Assembly
:Council
:Magistracy
:PriestlyCollege
:CourtSystem
:Province
:OfficeType
:RoleType
:PowerType
:Person
:OfficeTenure
:ReligiousTenure
:PowerGrant
:Delegation
:InstitutionalState
:OrganizationalPattern
:UnitType
:MilitaryUnit
:CommandAssignment
:CompositionClaim
:EstablishmentClaim
:Event
:Law
:Decision
:Source
:Assertion
:Period
:Place
```

Multiple labels are useful: `(:Institution:Assembly {key:'comitia_centuriata'})` and `(:Institution:Magistracy {key:'consulship'})`. Avoid labels such as `:Consul` or `:Centurion` on people; a person can occupy multiple, overlapping, or disputed roles.

### Structural relationships

```text
(:Institution)-[:PART_OF]->(:Polity)
(:OfficeType)-[:OFFICE_OF]->(:Institution)
(:OfficeType)-[:MAY_EXERCISE]->(:PowerType)
(:OfficeType)-[:MAY_PERFORM]->(:RoleType)
(:Assembly)-[:ELECTS_OFFICE]->(:OfficeType)
(:PriestlyCollege)-[:CONTAINS_OFFICE]->(:OfficeType)
(:OrganizationalPattern)-[:HAS_COMPONENT_TYPE]->(:UnitType)
(:MilitaryUnit)-[:INSTANCE_OF]->(:UnitType)
(:MilitaryUnit)-[:SUBUNIT_OF]->(:MilitaryUnit)
(:InstitutionalState)-[:STATE_OF]->(:Institution)
```

These edges express taxonomy or broadly stable structure. Historical facts needing dates, sources, qualifiers, quantities, or competing interpretations should be nodes.

### Reified assertions

```text
(:Person)-[:SUBJECT_OF]->(:OfficeTenure)-[:FOR_OFFICE]->(:OfficeType)
(:OfficeTenure)-[:WITHIN_INSTITUTION]->(:Institution)
(:OfficeTenure)-[:AUTHORIZED_BY]->(:ElectionOrAppointment)
(:OfficeTenure)-[:CARRIED_ROLE]->(:RoleType)
(:OfficeTenure)-[:HELD_POWER]->(:PowerGrant)

(:Person)-[:SUBJECT_OF]->(:CommandAssignment)
(:CommandAssignment)-[:COMMANDED]->(:MilitaryUnit)
(:CommandAssignment)-[:AS_ROLE]->(:RoleType)
(:CommandAssignment)-[:DERIVED_FROM]->(:OfficeTenure|:Delegation|:Law)
(:CommandAssignment)-[:UNDER_COMMAND_OF]->(:CommandAssignment)

(:CompositionClaim)-[:PARENT_TYPE]->(:UnitType)
(:CompositionClaim)-[:CHILD_TYPE]->(:UnitType)
(:CompositionClaim)-[:VALID_IN_PATTERN]->(:OrganizationalPattern)
(:CompositionClaim)-[:SUPPORTED_BY]->(:Source)
```

`UNDER_COMMAND_OF` between command assignments is safer than a timeless `(Centurion)-[:REPORTS_TO]->(Tribune)` relationship. It can represent Caesar delegating a legion to a legate, a consul commanding two legions in Polybius’s pattern, or a navarch operating under a fleet prefect.

### Essential properties

Every temporal assertion should support:

```text
validFromYear       integer | null   // astronomical signed year or project convention
validToYear         integer | null
startPrecision      'exact'|'year'|'range'|'circa'|'traditional'|'unknown'
endPrecision        same vocabulary
certainty           0.0..1 or controlled term
status              'attested'|'reconstructed'|'traditional'|'disputed'|'deprecated'
contextKey          string           // war, province, army, source passage, constitutional settlement
assertionKey        stable string
```

Every sourced claim should also connect to a source and, ideally, a passage:

```text
(:Assertion)-[:SUPPORTED_BY]->(:SourcePassage)
(:SourcePassage)-[:PASSAGE_OF]->(:Source)
(:Assertion)-[:CONTRADICTED_BY]->(:SourcePassage)
(:Assertion)-[:ALTERNATIVE_TO]->(:Assertion)
```

This is particularly important for early Republican chronology, naval offices, numerical establishments, and the cohort transition.

### Example Cypher

```cypher
MERGE (rome:Polity {key:'roman_republic'})
MERGE (senate:Institution:Council {key:'roman_senate'})
MERGE (senate)-[:PART_OF]->(rome)

MERGE (consulship:Institution:Magistracy {key:'consulship'})
MERGE (consulship)-[:PART_OF]->(rome)
MERGE (consul:OfficeType {key:'consul'})
MERGE (consul)-[:OFFICE_OF]->(consulship)

MERGE (armyCommander:RoleType {key:'army_commander'})
MERGE (senatePresider:RoleType {key:'senate_presider'})
MERGE (imperium:PowerType {key:'imperium'})
MERGE (consul)-[:MAY_PERFORM]->(armyCommander)
MERGE (consul)-[:MAY_PERFORM]->(senatePresider)
MERGE (consul)-[:MAY_EXERCISE]->(imperium)
```

```cypher
MERGE (pattern:OrganizationalPattern {key:'polybian_manipular_legion'})
SET pattern.validFromYear = -300,
    pattern.validToYear = -100,
    pattern.startPrecision = 'range',
    pattern.endPrecision = 'range',
    pattern.status = 'reconstructed'

MERGE (legion:UnitType {key:'legion'})
MERGE (maniple:UnitType {key:'maniple'})
MERGE (century:UnitType {key:'century'})

CREATE (c1:CompositionClaim {
  assertionKey:'polybian_legion_30_heavy_maniples',
  quantity:30,
  certainty:0.95,
  status:'attested_ideal'
})
MERGE (c1)-[:PARENT_TYPE]->(legion)
MERGE (c1)-[:CHILD_TYPE]->(maniple)
MERGE (c1)-[:VALID_IN_PATTERN]->(pattern)

CREATE (c2:CompositionClaim {
  assertionKey:'polybian_maniple_2_centuries',
  quantity:2,
  certainty:0.95,
  status:'attested_ideal'
})
MERGE (c2)-[:PARENT_TYPE]->(maniple)
MERGE (c2)-[:CHILD_TYPE]->(century)
MERGE (c2)-[:VALID_IN_PATTERN]->(pattern)
```

```cypher
MATCH (caesar:Person {key:'gaius_julius_caesar'}),
      (proconsul:OfficeType {key:'proconsul'}),
      (imperium:PowerType {key:'imperium'}),
      (armyCommander:RoleType {key:'army_commander'}),
      (army:MilitaryUnit {key:'caesars_gaul_army'})
CREATE (t:OfficeTenure {
  assertionKey:'caesar_proconsular_tenure_gaul',
  validFromYear:-58,
  validToYear:-50,
  status:'attested'
})
CREATE (caesar)-[:SUBJECT_OF]->(t)
CREATE (t)-[:FOR_OFFICE]->(proconsul)
CREATE (pg:PowerGrant {key:'caesar_gaul_imperium', validFromYear:-58, validToYear:-50})
CREATE (t)-[:HELD_POWER]->(pg)-[:POWER_TYPE]->(imperium)
CREATE (cmd:CommandAssignment {validFromYear:-58, validToYear:-50})
CREATE (caesar)-[:SUBJECT_OF]->(cmd)
CREATE (cmd)-[:AS_ROLE]->(armyCommander)
CREATE (cmd)-[:COMMANDED]->(army)
CREATE (cmd)-[:DERIVED_FROM]->(pg)
```

The exact dates in the final example should be sourced and adjusted to the project’s date convention; its purpose is to demonstrate separation of tenure, power grant, and command.

## Controlled vocabularies

### Power types

At minimum include:

- `imperium_domesticum`
- `imperium_militiae`
- `potestas`
- `intercessio_collegial`
- `intercessio_tribunician`
- `coercitio`
- `ius_agendi_cum_populo`
- `ius_agendi_cum_plebe`
- `ius_agendi_cum_senatu`
- `iurisdictio`
- `auspicium`
- `sacrosanctitas`
- `provocatio_protection`
- `censorial_review`

A source may use *imperium* broadly, while the exercise of command differs inside Rome, outside the *pomerium*, and within an assigned *provincia*. Model scope on `PowerGrant` rather than creating one universal binary property.[^47][^48]

### Selection mechanisms

- `popular_election`
- `plebeian_election`
- `nomination`
- `appointment`
- `cooptation`
- `sortition`
- `prorogation`
- `special_lex`
- `senatorial_decree`
- `delegation`
- `ex_officio`

This allows the graph to distinguish an elected consul, a dictator nominated under emergency procedure, a legate delegated by a commander, and a proconsul whose *imperium* was prorogued.

### Confidence rules

| Evidence condition | Suggested status | Suggested confidence behavior |
|---|---|---|
| Contemporary inscription or securely dated law | `attested` | High, while still separating text from interpretation |
| Polybius describing his observed mid-Republican system | `attested_ideal` | High for the described norm, not necessarily every army |
| Livian foundation story centuries earlier | `traditional` | Preserve exact claim but lower historical confidence |
| Modern reconstruction from several sources | `reconstructed` | Record scholar, method, and competing reconstruction |
| Major scholarly disagreement | `disputed` | Store parallel assertions; do not collapse to one fact |
| Common older view rejected or heavily qualified today | `deprecated_interpretation` | Retain for historiography, excluded from default factual views |

The “Marian reforms” package is the clearest example of the last two categories: preserve it as a historiographical claim, but make gradual cohort development the default model.[^36][^37][^5]

## Implementation sequence

1. Create authority nodes for institutions, office types, role types, power types, unit types, and organizational patterns.
2. Add periodized `InstitutionalState` nodes for office counts, eligibility, method of selection, and competencies.
3. Load office-holding through `OfficeTenure`, never direct person labels.
4. Build the Polybian military template first because it has the strongest detailed Republican description.[^34][^1]
5. Add the early and transitional army as lower-confidence, overlapping patterns.
6. Build the Republican navy around campaign fleets, delegated command, squadrons, ships, and parallel shipboard functions.
7. Add specific historical armies and fleets only when sources attest their composition or command.
8. Attach all contested dates, numerical establishments, and hierarchy edges to source-backed claims.
9. Create derived query views for “constitution in year X” and “military hierarchy in campaign Y” instead of storing a single canonical tree.

Useful target queries include:

```cypher
// Offices and powers valid in a selected year
MATCH (o:OfficeType)-[:OFFICE_OF]->(i:Institution)
OPTIONAL MATCH (i)<-[:STATE_OF]-(s:InstitutionalState)
WHERE s.validFromYear <= $year
  AND (s.validToYear IS NULL OR s.validToYear >= $year)
OPTIONAL MATCH (o)-[:MAY_EXERCISE]->(p:PowerType)
RETURN i, o, collect(DISTINCT p) AS powers, collect(DISTINCT s) AS states;
```

```cypher
// Source-backed military template for a selected year
MATCH (pat:OrganizationalPattern)<-[:VALID_IN_PATTERN]-(c:CompositionClaim)
WHERE pat.validFromYear <= $year
  AND pat.validToYear >= $year
MATCH (c)-[:PARENT_TYPE]->(parent:UnitType),
      (c)-[:CHILD_TYPE]->(child:UnitType)
OPTIONAL MATCH (c)-[:SUPPORTED_BY]->(src:SourcePassage)
RETURN pat, parent, child, c.quantity, c.certainty, collect(src);
```

```cypher
// Actual chain of command for a campaign
MATCH path=(top:CommandAssignment)-[:UNDER_COMMAND_OF*0..]->(sub:CommandAssignment)
WHERE top.contextKey = $campaignKey
RETURN path;
```

## Principal cautions

- Do not model the Republic as a modern separation-of-powers constitution; the same magistrate could initiate legislation, administer policy, judge, take auspices, and command troops.[^9][^3]
- Do not collapse all assemblies into one `RomanAssembly`; their membership rules, presiding authorities, voting units, and competencies differ.
- Do not make the Senate a legislature or give it direct, timeless command of armies. Its influence often operated through finance, decrees, assignments, prorogation, and political authority.[^2][^1]
- Do not equate an office with all roles ever performed by its holders; roles depend on date, assignment, place, and context.
- Do not treat *provincia* only as a territorial province.
- Do not treat the Polybian establishment as the actual strength of every legion.
- Do not turn Marius into a single reform event replacing maniples with cohorts.[^5][^36]
- Do not project the Augustan legionary hierarchy or permanent fleets backward into the Republic.
- Do not force shipboard navigation, propulsion, and combat into one simplistic reporting line when ancient evidence leaves relationships uncertain.[^44][^45]
- Do not discard traditional or superseded interpretations; retain them as claim nodes with status and provenance so the graph can represent historiography as well as a preferred reconstruction.

## Recommended canonical trees

For a default visualization, expose three political layers and four military templates:

```text
ROMAN REPUBLIC
├── Roman People
│   ├── Comitia Curiata
│   ├── Comitia Centuriata
│   ├── Comitia Tributa
│   └── Concilium Plebis
├── Magistracies
│   ├── Ordinary: consul, praetor, censor, quaestor, aediles, tribune
│   ├── Extraordinary: dictator, magister equitum, interrex, commissions
│   └── Extended/delegated: proconsul, propraetor, legate, prefect
├── Senate
├── Public Courts
├── Public Priesthoods
└── Provinces and Assigned Commands
```

```text
MILITARY PATTERNS
├── Early citizen levy — low-resolution reconstructed hierarchy
├── Polybian consular army — two legions + two allied wings + extraordinarii
├── Transitional army — overlapping maniple and cohort claims
├── Late-Republican field army — commander + legions + cohorts + centuries + auxiliaries
└── Republican campaign fleet — high commander + fleet + squadron + ship + parallel crew functions
```

These should be generated views from dated assertions. The graph’s authoritative layer should remain a network of offices, roles, powers, commands, composition claims, sources, and temporal states rather than the displayed trees themselves.

---

## References

1. [Polybius • Histories — Book 6](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Polybius/6*.html) - Thus, owing to the extreme severity and inevitableness of the penalty, the night watches of the Roma...

2. [The Histories (ca. 167-146 BC)](https://constitutioncenter.org/the-constitution/historic-document-library/detail/polybius-the-histories-ca-167-146-bc) - The consul, when he leaves with his army invested with the powers I mentioned, appears indeed to hav...

3. [7 Polybius Comes to Rome - Oxford Academic](https://academic.oup.com/book/62526/chapter/559633514) - The consuls possessed no authority that was needed for the operation of civilian government, and so ...

4. [The Roman Republican Navy: From the Sixth Century to 167 BC ...](https://bmcr.brynmawr.edu/2009/2009.04.31/)

5. [The transformation of the Roman army in the last decades of ...](https://www.taylorfrancis.com/chapters/oa-edit/10.4324/9781351063500-16/transformation-roman-army-last-decades-republic-fran%C3%A7ois-gauthier) - by F Gauthier · 2019 · Cited by 24 — Gaius Marius introduced the most important change in late Repub...

6. [Praefectus Classis (Smith's Dictionary, 1875)](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/secondary/SMIGRA*/Praefectus_Classis.html) - In ancient Rome, praefectus classis was the title of a fleet commander: the brief article in Smith's...

7. [Ancient Rome - Republic, Senate, Patricians | Britannica](https://www.britannica.com/place/ancient-Rome/Early-centuries-of-the-Roman-Republic) - Ancient Rome - Republic, Senate, Patricians: The ancient historians depicted Rome’s first six kings ...

8. [Polybius 6.11-18](http://www.thelatinlibrary.com/historians/polyb/polybius4.html) - 12 The consuls, previous to leading out their legions, exercise authority in Rome over all public af...

9. [The Constitution of the Roman Republic: A Political Economy Perspective](https://chicagounbound.uchicago.edu/cgi/viewcontent.cgi?article=1496&context=law_and_economics)

10. [Schema of Roman Government](https://faculty.washington.edu/alain/CLAS.HSTAM330/RomGov.html) - elected for one-year terms; all had imperium or right to command an army Aediles, tribunes and quaes...

11. [Roman Constitution](https://www.worldhistory.org/Roman_Constitution/) - Assemblies · comitia curiata – responsible for the appointment of magistrates and priests and the co...

12. [Roman Republic | Definition, Dates, History, Government ...](https://www.britannica.com/place/Roman-Republic) - Its government consisted of the Senate and four assemblies: the Comitia Curiata, the Comitia Centuri...

13. [The Roman Quaestor (Smith's Dictionary, 1875)](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/secondary/SMIGRA*/Quaestor.html) - The quaestores classici were officers entrusted with the care of the public money. It is established...

14. [Consul | Magistrates, Duties & Powers](https://www.britannica.com/topic/consul-ancient-Roman-official) - Consuls, however, were in a very real sense the heads of state. They commanded the army, convened an...

15. [Cursus honorum](https://en.wikipedia.org/wiki/Cursus_honorum) - The cursus honorum was the sequential order of public offices held by aspiring politicians in the Ro...

16. [Praetor | Magistrate, Law & Jurisdiction](https://www.britannica.com/topic/praetor) - Praetor, in ancient Rome, a judicial officer who had broad authority in cases of equity, was respons...

17. [Second Triumvirate](https://en.wikipedia.org/wiki/Second_Triumvirate) - It was formally constituted by law on 27 November 43 BC with a term of five years; it was renewed in...

18. [Lex Titia](https://en.wikipedia.org/wiki/Lex_Titia) - The lex Titia was a Roman law passed on 27 November 43 BC that established the Triumvirate of Octavi...

19. [Province | Origins, Administration & Expansion](https://www.britannica.com/topic/province-ancient-Roman-government) - Governors were either consuls or praetors, and these were called proconsuls and propraetors when the...

20. [The Histories of Polybius Book Six translated by Evelyn S. ...](https://www.yorku.ca/inpar/polybius_six.pdf) - As for the Roman constitution, it had three elements, each of them possessing sovereign powers: and ...

21. [Quaestio perpetua](https://en.wikipedia.org/wiki/Quaestio_perpetua) - A quaestio perpetua (also judicia publica) was a permanent jury court in the Roman Republic and earl...

22. [The Roman Extortion Court (quaestio de repetundis)](https://dcc.dickinson.edu/cicero-veres/roman-extortion-court) - The first such permanent criminal court or tribunal (quaestio perpetua) was the quaestio de repetund...

23. [College of Pontiffs](https://en.wikipedia.org/wiki/College_of_Pontiffs) - The other colleges were the augures (who read omens), the quindecimviri sacris faciundis ("fifteen m...

24. [LacusCurtius • Pontifex (Smith's Dictionary, 1875)](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/secondary/SMIGRA*/Pontifex.html) - The Roman pontiffs formed the most illustrious among the great colleges of priests. after his electi...

25. [Roman Republic – Timelines - BcResources.net](https://bcresources.net/5142000-rom-rep509-027-1p7-5yr-tml-bcrx/) - Roman Republic – Timelines: a set of two timelines, covering Rome's Early Republic (509–264 BCE) and...

26. [Roman Government](https://www.worldhistory.org/Roman_Government/) - Western Civilization is forever indebted to the people of ancient Greece and Rome. Among the numerou...

27. [Constitutional reforms of Sulla](https://en.wikipedia.org/wiki/Constitutional_reforms_of_Sulla) - The constitutional reforms of Sulla were a series of laws enacted by Lucius Cornelius Sulla (the Rom...

28. [RETHINKING SULLA: THE CASE OF THE ROMAN SENATE*](https://www.cambridge.org/core/journals/classical-quarterly/article/rethinking-sulla-the-case-of-the-roman-senate/E8279E6E2F5C921D90772A5E63D6F4C3) - by C Steel · 2014 · Cited by 67 — Cornelius Sulla's election to the dictatorship in 82 b.c. He respo...

29. [Sulla's Dictatorship, 82-79 BC](https://web.ics.purdue.edu/~rauhn/Hist_416/Caesar_05/Sulla_dict.htm) - 3. Sulla enlarged the Senate, selected 300 non senators for the senate, lifting its number to 600. H...

30. [Roman Republic](https://en.wikipedia.org/wiki/Roman_Republic) - offices of praetor and curule aediles, Lateranus became the first plebeian consul in 366 BC; Stolo f...

31. [LacusCurtius • The Roman Army (Smith's Dictionary, 1875)](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/secondary/SMIGRA*/Exercitus.html) - The legion for many centuries was composed exclusively of Roman citizens. it consisted of 3000 infan...

32. [Early Roman army](https://en.wikipedia.org/wiki/Early_Roman_army) - The early Roman army was deployed by ancient Rome during its Regal Era and into the early Republic a...

33. [How the Roman legions changed throughout their 1000 ...](https://www.historyskills.com/classroom/year-7/roman-legions-evolution/) - Those early conflicts prompted Rome to move away from the rigid Greek phalanx to the more flexible m...

34. [Polybius 6.19-42](https://www.thelatinlibrary.com/historians/polyb/polybius5.html) - 19 After electing the consuls, they appoint military tribunes, fourteen from those who have seen fiv...

35. [LacusCurtius • The Roman Camp (Smith's Dictionary, 1875)](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/secondary/SMIGRA*/Castra.html) - Each legion is calculated at 4200 infantry and 300 cavalry, the Socii furnished an equal number of i...

36. [Collections: The Marian Reforms Weren't a Thing](https://acoup.blog/2023/06/30/collections-the-marian-reforms-werent-a-thing/) - the Roman army changed during the Late Republic. We have evidence for only a handful of citizenship ...

37. [Marian reforms](https://en.wikipedia.org/wiki/Marian_reforms) - It was commonly believed that Marius changed the soldiers' socio-economic background by allowing cit...

38. [Polybius](https://eaglesanddragonspublishing.com/tag/polybius/) - Each tribune in the legions could select ten centurions who chose their own seconds. The most senior...

39. [Imperial Roman army](https://en.wikipedia.org/wiki/Imperial_Roman_army) - Each cohort was under the command of a military tribune, normally a former chief centurion of a legi...

40. [Legionary Reforms – Marius & the Roman Army](https://resmilitares.com/en/legionary-reforms-how-gaius-marius/) - Explore the truth behind the Roman legionary reforms of Marius, cohorts, equipment, eagle standard, ...

41. ["Duumuiri nauales" and the Navy of the Roman Republic](https://www.jstor.org/stable/23800302) - by CJ Dart · 2012 · Cited by 22 — The quaestores classici, set up in 267 BCE, were responsible for o...

42. [The quaestorship in the Roman Republic](https://bmcr.brynmawr.edu/2020/2020.04.39/) - quaestores classici (“naval quaestors”) were appointed in 267 to oversee shipbuilding—with evidence ...

43. [ROME AT SEA: THE BEGINNINGS OF ROMAN NAVAL ...](https://www.cambridge.org/core/journals/greece-and-rome/article/rome-at-sea-the-beginnings-of-roman-naval-power/F7E12E81A2E03D4C3F032CB82F335C5F) - by WV Harris · 2017 · Cited by 35 — Romans showed that they were eager to fight at sea as of 267 bec...

44. [Roman navy](https://en.wikipedia.org/wiki/Roman_navy) - The naval forces of the ancient Roman state (Latin: classis, lit. 'fleet' ) were instrumental in the...

45. [The Evolution of the Roman Imperial Fleets - WarHistory.org](https://warhistory.org/article/the-evolution-of-the-roman-imperial-fleets) - Like the ancient Israelis, who felt concern for those “who went down to the sea in ships” (Ps 107.23...

46. [Roman Warfare, Ships and Medicine](https://jmvh.org/article/roman-warfare-ships-and-medicine/) - by CN Westphalen · Cited by 6 — From c100 BCE, Roman legions were reorganised into 10 cohorts of 400...

47. [(PDF) Imperium, potestas, and the pomerium in the Roman ...](https://www.academia.edu/27484093/Imperium_potestas_and_the_pomerium_in_the_Roman_Republic) - Potestas is common to all magistrates, imperium pertain to magisterial authority, potestas is the ci...

48. [Authority in Ancient Rome: Auctoritas, Potestas, Imperium, ...](https://www.worldhistory.org/article/1472/authority-in-ancient-rome-auctoritas-potestas-impe/) - Potestas was legal power belonging to the various roles of political offices. There was also auctori...

