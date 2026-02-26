---
id: "entity-mapping-2026-02-24"
status: "todo"
priority: "high"
assignee: null
dueDate: null
created: "2026-02-24T13:12:27.277Z"
modified: "2026-02-24T13:12:27.277Z"
completedAt: null
labels: ["Core"]
order: "a6"
---
# Entity mapping

1. Add a mapping in entity\_[cipher.py](http://cipher.py) from PERSON → Human, PLACE → Place, etc.


1) Update cluster\_[assignment.py](http://assignment.py) to use classify_entity_type and create typed nodes instead of generic :Entity.


1. Update prepare_neo4j_with\_[ciphers.py](http://ciphers.py) and import_entities_with\_[parameters.py](http://parameters.py) to create typed labels.


1) Adjust any consumers (e.g. link_entities_to\_[subjects.py](http://subjects.py)) to work with typed nodes.