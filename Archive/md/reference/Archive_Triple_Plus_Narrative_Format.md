# Triple + Narrative Summary Format

## Format: Subject → Relationship → Object → Narrative Summary

Expanding the triple format to include a 4th component: a narrative summary that provides context, source attribution, and human-readable explanation.

---

## Structure

### Standard Format

```
Subject → Relationship → Object → Narrative Summary
```

### JSON Format

```json
{
  "source": {
    "label": "Osci",
    "id": "Q...",
    "type": "Ethnic Group"
  },
  "relationship": "SPOKE_LANGUAGE",
  "target": {
    "label": "Oscan language",
    "id": "Q...",
    "type": "Language"
  },
  "narrative": {
    "summary": "The Osci were an Italic people who spoke the Oscan language, which was also spoken by the Samnites of Southern Italy.",
    "source_text": "They spoke the Oscan language, also spoken by the Samnites of Southern Italy.",
    "source": "https://en.wikipedia.org/wiki/Osci",
    "confidence": 0.98,
    "temporal": null,
    "spatial": "Campania and Latium adiectum"
  }
}
```

---

## Examples from Osci Wikipedia Page

### 1. Language Relationship

**Triple:**
```
Osci → SPOKE_LANGUAGE → Oscan language
```

**With Narrative:**
```json
{
  "source": {"label": "Osci", "id": "Q...", "type": "Ethnic Group"},
  "relationship": "SPOKE_LANGUAGE",
  "target": {"label": "Oscan language", "id": "Q...", "type": "Language"},
  "narrative": {
    "summary": "The Osci spoke the Oscan language, which was also spoken by the Samnites of Southern Italy.",
    "source_text": "They spoke the Oscan language, also spoken by the Samnites of Southern Italy.",
    "source": "https://en.wikipedia.org/wiki/Osci",
    "confidence": 0.98
  }
}
```

---

### 2. Diplomatic Appeal

**Triple:**
```
Sidicini → APPEALED_TO → Campania
```

**With Narrative:**
```json
{
  "source": {"label": "Sidicini", "id": "Q...", "type": "Ethnic Group"},
  "relationship": "APPEALED_TO",
  "target": {"label": "Campania", "id": "Q...", "type": "Organization"},
  "narrative": {
    "summary": "In 343 BC, when the Samnites made an unprovoked attack upon the Sidicini, the Sidicini appealed to Campania for military assistance and received it.",
    "source_text": "The Samnites in 343 BC 'made an unprovoked attack upon the Sidicini', who appealed to Campania for military assistance and received it.",
    "source": "https://en.wikipedia.org/wiki/Osci",
    "confidence": 0.98,
    "temporal": "343 BC",
    "context": "Following unprovoked Samnite attack"
  }
}
```

---

### 3. Complex Military Action

**Triple:**
```
Romans → SACKED → Satricum
```

**With Narrative:**
```json
{
  "source": {"label": "Romans", "id": "Q...", "type": "Organization"},
  "relationship": "SACKED",
  "target": {"label": "Satricum", "id": "Q...", "type": "City"},
  "narrative": {
    "summary": "During the final revolt of the Volsci, around 346 BC, the Romans sacked and levelled Satricum, selling the remaining 4,000 fighting men into slavery.",
    "source_text": "During the final revolt of the Volsci, the Romans had sacked and levelled Satricum about 346 BC and had sold the remaining 4,000 fighting men into slavery.",
    "source": "https://en.wikipedia.org/wiki/Osci",
    "confidence": 0.95,
    "temporal": "346 BC",
    "context": "During final revolt of Volsci",
    "related_actions": ["LEVELLED Satricum", "SOLD_INTO_SLAVERY 4,000 men"]
  }
}
```

---

### 4. Cultural Assimilation

**Triple:**
```
Osci → ASSIMILATED_TO → Roman culture
```

**With Narrative:**
```json
{
  "source": {"label": "Osci", "id": "Q...", "type": "Ethnic Group"},
  "relationship": "ASSIMILATED_TO",
  "target": {"label": "Roman culture", "id": "Q...", "type": "Culture"},
  "narrative": {
    "summary": "After the Second Samnite War, during which the Osci lost their sovereignty when the Romans secured the border tribes, the Oscans assimilated quickly to Roman culture.",
    "source_text": "Their sovereignty was finally lost during the Second Samnite War when, prior to invading Samnium, the Romans found it necessary to secure the border tribes. After the war, the Oscans assimilated quickly to Roman culture.",
    "source": "https://en.wikipedia.org/wiki/Osci",
    "confidence": 0.95,
    "temporal": "After Second Samnite War (304 BC)",
    "context": "Following loss of sovereignty"
  }
}
```

---

## Narrative Summary Components

### Required Fields

1. **summary** (string): Human-readable narrative summarizing the relationship
   - Should be 1-3 sentences
   - Include key context (temporal, spatial, causal)
   - Preserve nuance and qualifications

### Optional Fields

2. **source_text** (string): Exact excerpt from source
3. **source** (string): Source URL or citation
4. **confidence** (float): LLM confidence score (0.0-1.0)
5. **temporal** (string): Time period, date, or event reference
6. **spatial** (string): Geographic context
7. **context** (string): Additional contextual information
8. **outcome** (string): Result or consequence
9. **related_actions** (array): Other actions in same context

---

## Benefits of Narrative Summary

### 1. **Context Preservation**
- Captures nuance lost in simple triple
- Preserves temporal/spatial context
- Maintains causal sequences

### 2. **Human Readability**
- Makes graph queries understandable
- Supports narrative generation
- Enables fact-checking

### 3. **Source Attribution**
- Links back to original text
- Supports citation and verification
- Enables fact provenance

### 4. **LLM Validation**
- Can validate extraction accuracy
- Supports reasoning about relationships
- Enables narrative-based queries

---

## Neo4j Storage Recommendation

Store narrative as **relationship property** for simplicity:

```cypher
CREATE (osci:EthnicGroup {id: "Q...", label: "Osci"})
CREATE (oscan:Language {id: "Q...", label: "Oscan language"})
CREATE (osci)-[r:SPOKE_LANGUAGE {
  narrative_summary: "The Osci were an Italic people who spoke the Oscan language...",
  source_text: "They spoke the Oscan language...",
  source: "https://en.wikipedia.org/wiki/Osci",
  confidence: 0.98
}]->(oscan)
```

---

## Updated LLM Extraction Format

```json
{
  "entities": [...],
  "triples": [
    {
      "source": {"label": "Osci", "id": "Q...", "type": "Ethnic Group"},
      "relationship": "SPOKE_LANGUAGE",
      "target": {"label": "Oscan language", "id": "Q...", "type": "Language"},
      "narrative": {
        "summary": "The Osci spoke the Oscan language, which was also spoken by the Samnites of Southern Italy.",
        "source_text": "They spoke the Oscan language, also spoken by the Samnites of Southern Italy.",
        "source": "https://en.wikipedia.org/wiki/Osci",
        "confidence": 0.98
      }
    }
  ]
}
```

---

## Query Examples

### Find relationships with narrative:
```cypher
MATCH (source)-[r:SPOKE_LANGUAGE]->(target)
WHERE r.narrative_summary CONTAINS "Italic people"
RETURN source, r, target, r.narrative_summary
```

### Find facts by source:
```cypher
MATCH (source)-[r]->(target)
WHERE r.source = "https://en.wikipedia.org/wiki/Osci"
RETURN source, type(r) as relationship, target, r.narrative_summary
```
