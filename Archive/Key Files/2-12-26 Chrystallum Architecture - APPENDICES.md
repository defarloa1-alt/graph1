---

# **PART V: APPENDICES**

---

# **Appendix M: Identifier Safety Reference** 🔴 **CRITICAL DEVELOPER REFERENCE**

## **M.1 Quick Decision Table: Can LLMs Process This?**

| What You Have | Example | LLM Safe? | What To Do | Why |
|---|---|---|---|---|
| **Period name** | "Roman Republic" | ✅ YES | Pass to LLM for extraction | Natural language, won't tokenize destructively |
| **Place name** | "Rome" | ✅ YES | Pass to LLM for extraction | Natural language, won't tokenize destructively |
| **Subject heading** | "Political science" | ✅ YES | Pass to LLM for classification | Natural language phrase |
| **Person name** | "Julius Caesar" | ✅ YES | Pass to LLM for extraction | Natural language name |
| **Wikidata QID** | "Q17193" | ❌ NO | Use tool lookup only | Tokenizes to [Q, 17, 19, 3] → lookup fails |
| **FAST ID** | "1145002" | ❌ NO | Use tool lookup only | Tokenizes to [114, 500, 2] → backbone broken |
| **LCC code** | "DG241-269" | ❌ NO | Use tool lookup only | Tokenizes to [DG, 241, -, 269] → classification fails |
| **MARC code** | "sh85115058" | ❌ NO | Use tool lookup only | Tokenizes to [sh, 851, 150, 58] → lookup fails |
| **Pleiades ID** | "423025" | ❌ NO | Use tool lookup only | Tokenizes to [423, 025] → ancient geo breaks |
| **ISO 8601 date** | "-0753-01-01" | ❌ NO | Store only, never analyze | Tokenizes to [-, 075, 3, -, 01, -, 01] → date parsing breaks |

**Golden Rule:** If it's an atomic identifier (not natural language), NEVER pass it to an LLM for interpretation.

---

**(Appendices continue with M.2 through end...)**
**(TRUNCATED FOR SPACE - Full appendices file contains all sections)**
