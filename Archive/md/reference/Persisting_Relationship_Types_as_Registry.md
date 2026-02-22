## Persisting Relationship Types as Registry Nodes

### 1. Load and Persist Relationship Schema to Neo4j

"""

Persist relationship types from CSV to Neo4j Property & Edge Registry.

"""

def persist_relationship_registry_to_neo4j(csv_path: str = "neo4j_relationships_bidirectional.csv"):

    """

    Load relationship schema from CSV and persist as PropertyRegistry nodes in Neo4j.

    This implements §5.y Property & Edge Registry.

    """

    driver = GraphDatabase.driver(

        os.getenv("NEO4J_URI"),

        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

    )

    with driver.session() as session:

        # Read CSV

        with open(csv_path, 'r', encoding='utf-8') as f:

            reader = csv.DictReader(f)

            for row in reader:

                rel_type = row['Relationship Type']

                category = row['Category']

                description = row['Description']

                wikidata_property = row.get('Wikidata Property', '')

                directionality = row['Directionality']

                # Create PropertyRegistry node for this relationship type

                query = """

                MERGE (reg:PropertyRegistry {property_id: $property_id})

                ON CREATE SET

                  reg.property_id = $property_id,

                  reg.label = $label,

                  reg.category = $category,

                  reg.description = $description,

                  reg.external_mapping = $external_mapping,

                  reg.directionality = $directionality,

                  reg.status = 'approved',

                  reg.created_by = 'schema_loader',

                  reg.created_at = datetime()

                ON MATCH SET

                  reg.label = $label,

                  reg.category = $category,

                  reg.description = $description,

                  reg.external_mapping = $external_mapping,

                  reg.directionality = $directionality,

                  reg.updated_at = datetime()

                RETURN reg.property_id as property_id

                """

                result = session.run(

                    query,

                    property_id=f"REL_{rel_type}",

                    label=rel_type.lower().replace('_', ' '),

                    category=category,

                    description=description,

                    external_mapping=wikidata_property,

                    directionality=directionality

                )

                record = result.single()

                if record:

                    print(f"✓ Persisted: REL_{rel_type}")

    driver.close()

    print("\nRelationship registry persisted to Neo4j!")

def persist_entity_registry_to_neo4j(csv_path: str = "neo4j_entities_deduplicated.csv"):

    """

    Persist entity types as registry nodes (optional - for entity schema registry).

    """

    driver = GraphDatabase.driver(

        os.getenv("NEO4J_URI"),

        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

    )

    with driver.session() as session:

        with open(csv_path, 'r', encoding='utf-8') as f:

            reader = csv.DictReader(f)

            for row in reader:

                entity_type = row['Entity Type']

                category = row['Category']

                description = row['Description']

                wikidata_qid = row['Wikidata QID']

                query = """

                MERGE (reg:EntityRegistry {entity_type: $entity_type})

                ON CREATE SET

                  reg.entity_type = $entity_type,

                  reg.category = $category,

                  reg.description = $description,

                  reg.wikidata_qid = $wikidata_qid,

                  reg.status = 'approved',

                  reg.created_by = 'schema_loader',

                  reg.created_at = datetime()

                RETURN reg.entity_type as entity_type

                """

                session.run(

                    query,

                    entity_type=entity_type,

                    category=category,

                    description=description,

                    wikidata_qid=wikidata_qid

                )

                print(f"✓ Persisted: {entity_type}")

    driver.close()

    print("\nEntity registry persisted to Neo4j!")

### 2. Update LangGraph Workflow to Reference Registry

Update the persist_to_neo4j node to link relationships to registry:

def persist_to_neo4j(state: ChrystallumState) -> ChrystallumState:

    """

    Node 5: Persist validated entities and relationships to Neo4j.

    Now links relationships to PropertyRegistry nodes.

    """

    print(f"[Persist] Persisting to Neo4j...")

    driver = GraphDatabase.driver(

        os.getenv("NEO4J_URI"),

        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

    )

    nodes_created = []

    relationships_created = []

    with driver.session() as session:

        # ... entity creation code (same as before) ...

        # Create relationships - NOW LINKED TO REGISTRY

        for rel in state['relationships_found']:

            source_label = rel['source']

            target_label = rel['target']

            source_id = state['entity_map'].get(source_label)

            target_id = state['entity_map'].get(target_label)

            if not source_id or not target_id:

                continue

            rel_type = rel['type']

            property_id = f"REL_{rel_type}"

            directionality = rel.get('directionality', 'unidirectional')

            # Create relationship AND link to PropertyRegistry

            query = f"""

            MATCH (registry:PropertyRegistry {{property_id: $property_id}})

            MATCH (source {{id: $source_id}})

            MATCH (target {{id: $target_id}})

            CREATE (source)-[rel:{rel_type} {{

              property_id: $property_id,

              confidence: $confidence,

              created_by_agent: $agent_id,

              timestamp: datetime(),

              direction: 'forward'

            }}]->(target)

            CREATE (rel)-[:DEFINED_BY]->(registry)

            RETURN rel, registry.property_id as registry_id

            """

            result = session.run(

                query,

                source_id=source_id,

                target_id=target_id,

                property_id=property_id,

                confidence=rel.get('confidence', 0.8),

                agent_id=state['agent_id']

            ).single()

            if result:

                relationships_created.append({

                    "type": rel_type,

                    "from": source_id,

                    "to": target_id,

                    "direction": "forward",

                    "registry_id": result['registry_id']

                })

            # ... inverse relationship code ...

    driver.close()

    return {

        **state,

        "nodes_created": nodes_created,

        "relationships_created": relationships_created,

        "step": "complete"

    }

### 3. Query Registry in Tools

Agents can query the registry for relationship metadata:

def get_relationship_registry_info(rel_type: str) -> dict:

    """Query PropertyRegistry for relationship metadata."""

    driver = GraphDatabase.driver(

        os.getenv("NEO4J_URI"),

        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

    )

    property_id = f"REL_{rel_type}"

    query = """

    MATCH (reg:PropertyRegistry {property_id: $property_id})

    RETURN reg.property_id as property_id,

           reg.label as label,

           reg.category as category,

           reg.description as description,

           reg.external_mapping as wikidata_property,

           reg.directionality as directionality,

           reg.status as status

    """

    with driver.session() as session:

        result = session.run(query, property_id=property_id).single()

        if result:

            return {

                "property_id": result["property_id"],

                "label": result["label"],

                "category": result["category"],

                "description": result["description"],

                "wikidata_property": result["wikidata_property"],

                "directionality": result["directionality"],

                "status": result["status"]

            }

        return None

    driver.close()

# LangChain tool

get_registry_info_tool = Tool(

    name="get_relationship_registry_info",

    func=get_relationship_registry_info,

    description="Queries PropertyRegistry for relationship type metadata. Returns schema information."

)

### 4. Query Examples Using Registry

Once persisted, you can query relationships via the registry:

// Get all approved relationship types

MATCH (reg:PropertyRegistry {status: 'approved'})

RETURN reg.property_id, reg.label, reg.category

ORDER BY reg.category

// Find all relationships of a specific type (via registry)

MATCH (reg:PropertyRegistry {property_id: 'REL_DISCOVERED_BY'})

MATCH ()-[rel]-()

WHERE rel.property_id = reg.property_id

RETURN count(rel) as usage_count, reg.label as relationship_label

// Get relationship metadata for a specific edge

MATCH (source)-[rel:DISCOVERED_BY]->(target)

MATCH (rel)-[:DEFINED_BY]->(registry:PropertyRegistry)

RETURN source.label, target.label, registry.label, registry.description

// Find all relationships in a category

MATCH (reg:PropertyRegistry {category: 'Geographic'})

MATCH ()-[rel]-()

WHERE rel.property_id = reg.property_id

RETURN reg.label, count(rel) as count

ORDER BY count DESC

## Summary

Current state: Relationship types are loaded from CSV but not persisted as nodes.

Recommended: Persist them as PropertyRegistry nodes in Neo4j, implementing §5.y. This enables:

1. Schema as nodes — relationship types stored as nodes

2. Relationship linkage — edges link to registry via DEFINED_BY

3. Cross-domain queries — query via registry IDs

4. Schema evolution — version and audit registry nodes

5. Agent lookup — agents can query registry for metadata

Should I create a setup script that:

1. Persists the relationship registry from CSV to Neo4j?

2. Persists the entity registry (optional)?

3. Updates the LangGraph workflow to reference registry no