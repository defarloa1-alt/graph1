// Migrate the clean-start Entity hierarchy from `kind` properties to
// additive Neo4j subtype labels. Run the preflight first.
//
// This migration does not touch Year nodes or any relationships.

// Preflight: this must return zero before the migration is applied.
MATCH (node:Entity)
WHERE node.kind IS NULL
   OR NOT node.kind IN [
     "Person", "Place", "Event", "Group", "Work", "Object", "Period",
     "Office", "Concept", "Polity", "Type", "Other"
   ]
RETURN node.id AS entityId, node.kind AS kind;

MATCH (node:Entity {kind: "Person"})
SET node:Person
REMOVE node.kind
RETURN count(node) AS migratedPersons;

MATCH (node:Entity {kind: "Place"})
SET node:Place
REMOVE node.kind
RETURN count(node) AS migratedPlaces;

MATCH (node:Entity {kind: "Event"})
SET node:Event
REMOVE node.kind
RETURN count(node) AS migratedEvents;

MATCH (node:Entity {kind: "Group"})
SET node:Group
REMOVE node.kind
RETURN count(node) AS migratedGroups;

MATCH (node:Entity {kind: "Work"})
SET node:Work
REMOVE node.kind
RETURN count(node) AS migratedWorks;

MATCH (node:Entity {kind: "Object"})
SET node:Object
REMOVE node.kind
RETURN count(node) AS migratedObjects;

MATCH (node:Entity {kind: "Period"})
SET node:Period
REMOVE node.kind
RETURN count(node) AS migratedPeriods;

MATCH (node:Entity {kind: "Office"})
SET node:Office
REMOVE node.kind
RETURN count(node) AS migratedOffices;

MATCH (node:Entity {kind: "Concept"})
SET node:Concept
REMOVE node.kind
RETURN count(node) AS migratedConcepts;

MATCH (node:Entity {kind: "Polity"})
SET node:Polity
REMOVE node.kind
RETURN count(node) AS migratedPolities;

MATCH (node:Entity {kind: "Type"})
SET node:Type
REMOVE node.kind
RETURN count(node) AS migratedTypes;

MATCH (node:Entity {kind: "Other"})
SET node:Other
REMOVE node.kind
RETURN count(node) AS migratedOther;

// Actium-specific subtype property from the reviewed vertical slice.
MATCH (node:Entity:Event {id: "chr:entity:battle-of-actium"})
SET node.eventType = "battle"
RETURN node;

// Postflight: both result sets must be empty.
MATCH (node:Entity)
WHERE node.kind IS NOT NULL
RETURN node.id AS residualEntityId, node.kind AS residualKind;

MATCH (node:Entity)
WHERE NOT any(subtype IN [
  "Person", "Place", "Event", "Group", "Work", "Object", "Period",
  "Office", "Concept", "Polity", "Type", "Other"
] WHERE subtype IN labels(node))
RETURN node.id AS untypedEntityId, labels(node) AS labels;
