

// Agent discovers "Columbus" - check if entity exists

// Option 1: Check by QID (if known)

MATCH (entity {id: "Q1312"})  // QID for Christopher Columbus

RETURN entity.id, entity.label, entity.id_type

// Option 2: Check by label

MATCH (entity {label: "Christopher Columbus"})

RETURN entity.id, entity.label, entity.id_type

// Option 3: Check by label + type (more specific)

MATCH (entity:Person {label: "Christopher Columbus"})

RETURN entity.id, entity.label

// Option 4: Fuzzy label match (if exact match not found)

MATCH (entity)

WHERE entity.label CONTAINS "Columbus"

RETURN entity.id, entity.label, entity.id_type

// Option 5: Check by content_hash (for deduplication)

MATCH (entity {content_hash: "abc123..."})

RETURN entity.id, entity.content_hash

## Agent Workflow

1. Agent encounters "Columbus" during extraction

2. Query the graph:
    
       MATCH (entity)
    
       WHERE entity.id = "Q1312" 
    
          OR entity.label = "Christopher Columbus"
    
          OR (entity.label CONTAINS "Columbus" AND entity:Person)
    
       RETURN entity
    

3. If exists: use existing entity (don't create duplicate)

4. If not exists: create new entity

This prevents duplicates without a registry or tracking who created what.

## For Implementation

Your LangChain agents need a Neo4j tool like:

- check_entity_exists(entity_label, qid=None, entity_type=None)

- Returns: existing node if found, None if not

- Then agent decides: use existing or create new

This is enough for the deduplication use case.