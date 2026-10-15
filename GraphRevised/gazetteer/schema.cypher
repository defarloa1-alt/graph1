// The gazetteer's schema (27-GAZETTEER.md): the ninth core label, Location.
// Applied by the loader with --apply, before any Location is written.

CREATE CONSTRAINT location_id_unique IF NOT EXISTS
FOR (node:Location)
REQUIRE node.id IS UNIQUE;

CREATE CONSTRAINT location_system_identifier_unique IF NOT EXISTS
FOR (node:Location)
REQUIRE (node.system, node.identifier) IS UNIQUE;

CREATE POINT INDEX location_point IF NOT EXISTS
FOR (node:Location)
ON (node.location);
