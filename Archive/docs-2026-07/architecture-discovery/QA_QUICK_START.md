# QA Quick Start - Neo4j Testing

**Your Mission:** Test the Neo4j entity import (300 entities with ciphers)

---

## ⚡ **5-Minute Quick Test**

Run these 4 commands in order:

### 1. **Connection Test**
```
"Get the Neo4j schema"
```
✅ Should show: `Entity` label

### 2. **Count Test**
```
"How many Entity nodes are there?"
```
✅ Expected: ~300 entities

### 3. **Seed Entity Test**
```
"Show me entity Q17167"
```
✅ Expected: Roman Republic with entity_cipher "ent_sub_Q17167"

### 4. **Data Quality Test**
```
"Are there any entities missing critical properties like entity_cipher, qid, or label?"
```
✅ Expected: None (0 entities with missing data)

---

## 📋 **Full Test Suite** (30 mins)

Copy-paste these commands one at a time:

```
1. "Get the Neo4j schema"
2. "How many Entity nodes are there?"
3. "Show me a breakdown of entities by type"
4. "Show me entity Q17167 with all its properties"
5. "Check if all entity ciphers are unique"
6. "What's the distribution of federation scores?"
7. "Show me the top 20 entities by federation score"
8. "Find entities with missing critical properties"
9. "Find all entities with 'Rome' in the label"
10. "Show me the top 10 entities by property count"
```

---

## 🔑 **Neo4j Access**

**URI:** `neo4j+s://f7b612a3.databases.neo4j.io`  
**User:** `neo4j`  
**Password:** `K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM`

You have MCP access - just ask questions naturally!

---

## ✅ **Pass Criteria**

All tests PASS if:
- [x] Can connect to Neo4j
- [x] 200-350 entities exist
- [x] Q17167 (Roman Republic) found
- [x] All ciphers are unique
- [x] No missing critical properties

---

## 📊 **Expected Results**

| Test | Expected Result |
|------|----------------|
| Entity Count | ~300 |
| Entity Types | SUBJECTCONCEPT, PLACE, EVENT, CONCEPT, PERSON |
| Federation Scores | Range 1-5 |
| Missing Properties | 0 |
| Duplicate Ciphers | 0 |

---

## 🐛 **Known Limitations**

- ⚠️ No relationships yet (only nodes)
- ⚠️ Only 10 entities have FacetedEntity nodes (Tier 2 ciphers)
- ⚠️ No Claims layer yet

---

## 📝 **Report Format**

After testing, report:
```
Tests Run: [X/10]
Passed: [X]
Failed: [X]
Issues: [List any problems]
Status: [APPROVED / NEEDS FIXES]
```

---

**Full Details:** See `QA_HANDOFF_NEO4J_TESTING.md`
