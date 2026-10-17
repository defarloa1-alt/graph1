# Chrystallum Revised Architecture

**Status:** Clean-start working architecture

## 1. The central idea

==Chrystallum should be a small evidence graph before it becomes an elaborate==
==research platform.==

The graph has three questions to answer:

```text
What is this?
What is it about?
Why do we believe this connection?
```

Those questions map to three core concepts:

```text
Entity
Subject
Assertion
```

### Entity

An entity is a thing that the graph discusses:

- a person;
- an event;
- a place;
- an organization or group;
- an object;
- a work;
- a period;
- a local analytical object when no external entity is sufficient.

An entity has a stable Chrystallum ID. External identifiers such as Wikidata
QIDs are authority links, not the local primary key.

### Subject

==A subject is a body of knowledge about one or more entities. It is not the==
==historical thing itself.==

Examples:

```text
Entity:       Battle of Actium
Subject:      Knowledge and literature about the Battle of Actium

Entity:       Roman aqueduct infrastructure
Subject:      Roman aqueducts as a historical and technological topic
```

The same label may be displayed for an entity and a subject, but the graph
must keep the node types distinct.

### Assertion

An assertion says that a relationship exists or that a value applies. It may
be imported from a source, proposed by an agent, accepted by a curator, or
computed from other information.

Assertions carry the context needed to understand them:

- source;
- retrieval time;
- status;
- confidence or evidence assessment;
- temporal qualification when relevant;
- spatial qualification when relevant;
- actor or process that created the assertion.

## 2. The minimal architecture

```text
Question or source mention
        ↓
Candidate entity or subject
        ↓
Local node
        ↓
Authority links and source observations
        ↓
Assertion
        ↓
Review or acceptance
        ↓
Durable graph
```

==This is deliberately smaller than the previous SCA/SFA architecture. Agents==
==may be introduced later, but the graph model must not depend on them.==

The agent system is an orchestration layer around this graph, not another
semantic layer inside it. Its job is to plan work, propose changes, validate
them, and commit only approved changes through a controlled write path.

## 3. External authorities

External systems have useful but limited roles:

| System | Use in the revised graph |
|---|---|
| Wikidata | Entity discovery, multilingual labels, candidate relationships, routing |
| LCSH | Bibliographic subject access |
| FAST | Faceted bibliographic subject access |
| LCC | Classification correspondence |
| Pleiades | Ancient places and qualified locations |
| PeriodO | Scholarly period definitions |
| VIAF/LCNAF/GND | Person and organization authority control |
| Domain vocabularies | Specialized objects, materials, texts, or inscriptions |

Wikidata is a useful federation hub, not the local ontology and not the final
authority for every historical claim.

When a QID exists:

```text
Wikidata entity
    → discover authority IDs
    → retrieve relevant specialist records
    → preserve source observation
    → create or update a local assertion
```

When a QID does not exist, the system may query a specialist authority
directly or create a local node with an explicit provisional status.

The federation profile must be selected for the inquiry's domain. A Roman
Republic inquiry and a Mesoamerican inquiry may share global services such as
Wikidata and bibliographic authorities while using different place,
language, manuscript, archaeological, and source-perspective providers.

## 4. Temporal context

Dates are not ordinary labels. A date connects an entity to a temporal model.

The revised graph uses the existing temporal year backbone as its initial
temporal infrastructure:

```text
Entity
  └─ occurred in / active in / valid in
        └─ Year node
```

The temporal backbone is not itself a periodization system. A year node does
not prove that an entity belongs to the Roman Republic, the Hellenistic
period, or any other scholarly period. Those are separate assertions that may
be added later and must identify their source or method.

## 5. What is intentionally not in the core yet

The following are deferred until a concrete use case proves they are needed:

- eighteen permanently instantiated facet agents;
- a universal upper ontology;
- automatic creation of every authority hierarchy;
- recursive family or event expansion;
- a separate node for every intermediate workflow state;
- unrestricted agent writes;
- a full CIDOC CRM operational schema;
- a requirement that every local node have a Wikidata QID;
- a requirement that every subject have an exact LCSH or FAST match.

This is not a rejection of those ideas. It is a sequencing decision.

Domain-specific packs are also deferred. They should be added only after the
core graph works across one small example and a second domain can demonstrate
that the stable model is portable.

## 6. Architectural invariants

1. Local IDs remain stable when external authorities change.
2. A label is not an identity.
3. An entity is not the same thing as a subject about that entity.
4. A source observation is not automatically an accepted historical claim.
5. Missing external data does not mean that a fact is false.
6. Qualified relationships must not be flattened when context changes their meaning.
7. Every durable write must be safe to retry.
8. Proposed information and accepted information must remain distinguishable.
9. Temporal dates and scholarly period definitions must remain distinct.
10. ==New complexity must be justified by a query, workflow, or interoperability need.==
11. The front-door agent plans and routes but does not create durable knowledge.
12. Specialist agents propose; deterministic validation and commit services write.
13. Prompt, schema, policy, and mapping versions must be recorded for every
    accepted change.

## 7. Plain-language example

For a question about the Battle of Actium:

```text
Create or reuse the event entity.
Create or reuse a subject about the event.
Link the event to the temporal year 31 BCE.
Resolve relevant people and places only as needed.
Record authority links as source-backed assertions.
Add claims about participation, location, or significance with evidence.
```

The first version does not need to build every family relationship, every
archaeological site, every period definition, or every facet branch before it
can answer the basic question.
