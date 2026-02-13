# LLM Extraction Experiment: Osci Wikipedia Page

## Goal
Extract facts from Wikipedia text and map them to our Neo4j relationship schema as Subject-Predicate-Object triples.

---

## Example Facts Extracted from Osci Wikipedia Page

### 1. Ethnic Group Identification

**Source Text:**
> "The **Osci** (also called **Oscans**, **Opici**, **Opsci**, **Obsci**, **Opicans**) were an Italic people of Campania and Latium adiectum before and during Roman times."

**Triple Extraction:**

```json
{
  "entities": [
    {
      "id": "Q...",  // Wikidata QID for Osci (if exists) or generate Chrystallum ID
      "label": "Osci",
      "type": "Ethnic Group",  // NEW entity type needed
      "qid": "Q...",
      "alias": ["Oscans", "Opici", "Opsci", "Obsci", "Opicans"]
    },
    {
      "id": "Q515",  // Campania
      "label": "Campania",
      "type": "Region"
    },
    {
      "id": "Q...",  // Latium adiectum
      "label": "Latium adiectum",
      "type": "Region"
    }
  ],
  "triples": [
    {
      "source_label": "Osci",
      "source_id": "Q...",
      "relationship": "LOCATED_IN",
      "relationship_type": "LOCATED_IN",
      "target_label": "Campania",
      "target_id": "Q515",
      "confidence": 0.95
    },
    {
      "source_label": "Osci",
      "source_id": "Q...",
      "relationship": "LOCATED_IN",
      "relationship_type": "LOCATED_IN",
      "target_label": "Latium adiectum",
      "target_id": "Q...",
      "confidence": 0.95
    }
  ]
}
```

---

### 2. Language Relationship

**Source Text:**
> "They spoke the Oscan language, also spoken by the Samnites of Southern Italy."

**Triple Extraction:**

```json
{
  "entities": [
    {
      "id": "Q...",  // Oscan language
      "label": "Oscan language",
      "type": "Language"
    },
    {
      "id": "Q...",  // Samnites
      "label": "Samnites",
      "type": "Ethnic Group"
    }
  ],
  "triples": [
    {
      "source_label": "Osci",
      "source_id": "Q...",
      "relationship": "SPOKE_LANGUAGE",  // NEW relationship needed
      "relationship_type": "SPOKE_LANGUAGE",
      "target_label": "Oscan language",
      "target_id": "Q...",
      "confidence": 0.98
    },
    {
      "source_label": "Samnites",
      "source_id": "Q...",
      "relationship": "SPOKE_LANGUAGE",
      "relationship_type": "SPOKE_LANGUAGE",
      "target_label": "Oscan language",
      "target_id": "Q...",
      "confidence": 0.98
    }
  ]
}
```

---

### 3. Military Conflict Participation

**Source Text:**
> "During the final revolt of the Volsci, the Romans had sacked and levelled Satricum about 346 BC... The Aurunci chose this moment to send a marauding expedition against the Romans."

**Triple Extraction:**

```json
{
  "entities": [
    {
      "id": "Q...",  // Volsci
      "label": "Volsci",
      "type": "Ethnic Group"
    },
    {
      "id": "Q...",  // Romans (as ethnic group or state)
      "label": "Romans",
      "type": "Organization"  // or "Ethnic Group"?
    },
    {
      "id": "Q...",  // Satricum
      "label": "Satricum",
      "type": "City"
    },
    {
      "id": "Q...",  // Aurunci
      "label": "Aurunci",
      "type": "Ethnic Group"
    },
    {
      "id": "Q...",  // Revolt of Volsci (event)
      "label": "Revolt of Volsci",
      "type": "Rebellion",
      "start_time": "346 BC"
    }
  ],
  "triples": [
    {
      "source_label": "Romans",
      "source_id": "Q...",
      "relationship": "SACKED",
      "relationship_type": "SACKED",
      "target_label": "Satricum",
      "target_id": "Q...",
      "confidence": 0.95,
      "temporal": "346 BC"
    },
    {
      "source_label": "Romans",
      "source_id": "Q...",
      "relationship": "LEVELLED",  // NEW relationship needed
      "relationship_type": "LEVELLED",
      "target_label": "Satricum",
      "target_id": "Q...",
      "confidence": 0.95,
      "temporal": "346 BC"
    },
    {
      "source_label": "Volsci",
      "source_id": "Q...",
      "relationship": "REBELLED",  // Need to check if exists
      "relationship_type": "REBELLED",
      "target_label": "Romans",
      "target_id": "Q...",
      "confidence": 0.90,
      "temporal": "346 BC"
    },
    {
      "source_label": "Aurunci",
      "source_id": "Q...",
      "relationship": "FOUGHT_IN",
      "relationship_type": "FOUGHT_IN",
      "target_label": "Marauding expedition against Romans",
      "target_id": "Q...",
      "confidence": 0.85,
      "temporal": "346 BC"
    }
  ]
}
```

---

### 4. Diplomatic Relationships

**Source Text:**
> "The Samnites in 343 BC 'made an unprovoked attack upon the Sidicini', who appealed to Campania for military assistance and received it. After losing two battles and being penned within Capua, the Campanians offered themselves to Rome with tears and prostrations in the Senate House. The Senate accepted the offer and granted assistance..."

**Triple Extraction:**

```json
{
  "entities": [
    {
      "id": "Q...",  // Samnites
      "label": "Samnites",
      "type": "Ethnic Group"
    },
    {
      "id": "Q...",  // Sidicini
      "label": "Sidicini",
      "type": "Ethnic Group"
    },
    {
      "id": "Q...",  // Campania (region or organization?)
      "label": "Campania",
      "type": "Organization"
    },
    {
      "id": "Q...",  // Campanians
      "label": "Campanians",
      "type": "Ethnic Group"
    },
    {
      "id": "Q...",  // Rome (Senate)
      "label": "Rome",
      "type": "Organization"
    },
    {
      "id": "Q...",  // Capua
      "label": "Capua",
      "type": "City"
    },
    {
      "id": "Q...",  // Battle events
      "label": "Battle with Samnites (343 BC)",
      "type": "Battle",
      "start_time": "343 BC"
    }
  ],
  "triples": [
    {
      "source_label": "Samnites",
      "source_id": "Q...",
      "relationship": "FOUGHT_IN",
      "relationship_type": "FOUGHT_IN",
      "target_label": "Attack on Sidicini",
      "target_id": "Q...",
      "confidence": 0.95,
      "temporal": "343 BC"
    },
    {
      "source_label": "Sidicini",
      "source_id": "Q...",
      "relationship": "APPEALED_TO",  // NEW relationship needed
      "relationship_type": "APPEALED_TO",
      "target_label": "Campania",
      "target_id": "Q...",
      "confidence": 0.98,
      "temporal": "343 BC"
    },
    {
      "source_label": "Campanians",
      "source_id": "Q...",
      "relationship": "OFFERED_SELF_TO",  // NEW relationship needed
      "relationship_type": "OFFERED_SELF_TO",
      "target_label": "Rome",
      "target_id": "Q...",
      "confidence": 0.98,
      "temporal": "343 BC"
    },
    {
      "source_label": "Rome",
      "source_id": "Q...",
      "relationship": "ACCEPTED_OFFER",  // NEW relationship needed
      "relationship_type": "ACCEPTED_OFFER",
      "target_label": "Campanians",
      "target_id": "Q...",
      "confidence": 0.98,
      "temporal": "343 BC"
    },
    {
      "source_label": "Campanians",
      "source_id": "Q...",
      "relationship": "LOCATED_IN",
      "relationship_type": "LOCATED_IN",
      "target_label": "Capua",
      "target_id": "Q...",
      "confidence": 0.95,
      "temporal": "343 BC"
    },
    {
      "source_label": "Campanians",
      "source_id": "Q...",
      "relationship": "DEFEATED_BY",
      "relationship_type": "DEFEATED_BY",
      "target_label": "Samnites",
      "target_id": "Q...",
      "confidence": 0.90,
      "temporal": "343 BC"
    }
  ]
}
```

---

### 5. Conquest and Subjugation

**Source Text:**
> "The Osci kept their independence by playing one state against another, especially the Romans and Samnites. Their sovereignty was finally lost during the Second Samnite War when, prior to invading Samnium, the Romans found it necessary to secure the border tribes. After the war, the Oscans assimilated quickly to Roman culture."

**Triple Extraction:**

```json
{
  "entities": [
    {
      "id": "Q...",  // Second Samnite War
      "label": "Second Samnite War",
      "type": "War",
      "start_time": "326 BC",
      "end_time": "304 BC"
    },
    {
      "id": "Q...",  // Samnium
      "label": "Samnium",
      "type": "Region"
    }
  ],
  "triples": [
    {
      "source_label": "Osci",
      "source_id": "Q...",
      "relationship": "SUBJUGATED_BY",  // NEW relationship needed
      "relationship_type": "SUBJUGATED_BY",
      "target_label": "Romans",
      "target_id": "Q...",
      "confidence": 0.95,
      "temporal": "Second Samnite War"
    },
    {
      "source_label": "Osci",
      "source_id": "Q...",
      "relationship": "LOST_SOVEREIGNTY",  // NEW relationship needed
      "relationship_type": "LOST_SOVEREIGNTY",
      "target_label": "Second Samnite War",
      "target_id": "Q...",
      "confidence": 0.95,
      "temporal": "Second Samnite War"
    },
    {
      "source_label": "Osci",
      "source_id": "Q...",
      "relationship": "ASSIMILATED_TO",  // NEW relationship needed
      "relationship_type": "ASSIMILATED_TO",
      "target_label": "Roman culture",
      "target_id": "Q...",
      "confidence": 0.95,
      "temporal": "After Second Samnite War"
    },
    {
      "source_label": "Romans",
      "source_id": "Q...",
      "relationship": "FOUGHT_IN",
      "relationship_type": "FOUGHT_IN",
      "target_label": "Second Samnite War",
      "target_id": "Q...",
      "confidence": 0.98
    }
  ]
}
```

---

### 6. Economic Actions

**Source Text:**
> "Sold the remaining 4,000 fighting men into slavery... Taking the town, they beheaded the Aurunci officers, sold the Pometians into slavery, levelled the buildings and put the land up for sale."

**Triple Extraction:**

```json
{
  "triples": [
    {
      "source_label": "Romans",
      "source_id": "Q...",
      "relationship": "SOLD_INTO_SLAVERY",  // NEW relationship needed
      "relationship_type": "SOLD_INTO_SLAVERY",
      "target_label": "4,000 fighting men",
      "target_id": "Q...",
      "quantity": 4000,
      "confidence": 0.95,
      "temporal": "346 BC"
    },
    {
      "source_label": "Romans",
      "source_id": "Q...",
      "relationship": "SOLD_INTO_SLAVERY",
      "relationship_type": "SOLD_INTO_SLAVERY",
      "target_label": "Pometians",
      "target_id": "Q...",
      "confidence": 0.95
    },
    {
      "source_label": "Romans",
      "source_id": "Q...",
      "relationship": "EXECUTED",  // Already exists
      "relationship_type": "EXECUTED",
      "target_label": "Aurunci officers",
      "target_id": "Q...",
      "method": "beheaded",
      "confidence": 0.95
    }
  ]
}
```

---

### 7. Geographic and Settlement

**Source Text:**
> "In 335, the Romans sent a consular army under Marcus Valerius Corvus to lay siege to Cales. Informed by an escaped prisoner... that the enemy were all drunk and sleeping, Corvus took the city in a night-time rout and garrisoned it. The Senate voted to send 2,500 colonists, to whom enemy land was distributed."

**Triple Extraction:**

```json
{
  "entities": [
    {
      "id": "Q...",  // Marcus Valerius Corvus
      "label": "Marcus Valerius Corvus",
      "type": "Human"
    },
    {
      "id": "Q...",  // Cales
      "label": "Cales",
      "type": "City"
    },
    {
      "id": "Q...",  // Siege of Cales
      "label": "Siege of Cales",
      "type": "Siege",
      "start_time": "335 BC"
    }
  ],
  "triples": [
    {
      "source_label": "Romans",
      "source_id": "Q...",
      "relationship": "BESIEGED",
      "relationship_type": "BESIEGED",
      "target_label": "Cales",
      "target_id": "Q...",
      "confidence": 0.98,
      "temporal": "335 BC"
    },
    {
      "source_label": "Marcus Valerius Corvus",
      "source_id": "Q...",
      "relationship": "COMMANDED",
      "relationship_type": "COMMANDED",
      "target_label": "Roman consular army",
      "target_id": "Q...",
      "confidence": 0.95,
      "temporal": "335 BC"
    },
    {
      "source_label": "Romans",
      "source_id": "Q...",
      "relationship": "CONQUERED",
      "relationship_type": "CONQUERED",
      "target_label": "Cales",
      "target_id": "Q...",
      "confidence": 0.95,
      "temporal": "335 BC"
    },
    {
      "source_label": "Romans",
      "source_id": "Q...",
      "relationship": "GARRISONED",  // NEW relationship needed
      "relationship_type": "GARRISONED",
      "target_label": "Cales",
      "target_id": "Q...",
      "confidence": 0.95,
      "temporal": "335 BC"
    },
    {
      "source_label": "Romans",
      "source_id": "Q...",
      "relationship": "DISTRIBUTED_LAND_TO",  // NEW relationship needed
      "relationship_type": "DISTRIBUTED_LAND_TO",
      "target_label": "2,500 colonists",
      "target_id": "Q...",
      "quantity": 2500,
      "confidence": 0.95,
      "temporal": "335 BC"
    }
  ]
}
```

---

## Summary: Relationship Types Used

### ✅ Already in Schema:
- LOCATED_IN
- SACKED / SACKED_BY
- FOUGHT_IN
- DEFEATED_BY
- BESIEGED / BESIEGED_BY
- CONQUERED / CONQUERED_BY
- EXECUTED / EXECUTED_BY
- COMMANDED

### ❌ Missing (High Priority):
- SPOKE_LANGUAGE / LANGUAGE_OF
- ASSIMILATED_TO / ASSIMILATED
- APPEALED_TO / RECEIVED_APPEAL_FROM
- OFFERED_SELF_TO / RECEIVED_OFFER_FROM
- ACCEPTED_OFFER / OFFER_ACCEPTED_BY
- SUBJUGATED / SUBJUGATED_BY
- LOST_SOVEREIGNTY / GAINED_SOVEREIGNTY_OVER
- LEVELLED / LEVELLED_BY
- SOLD_INTO_SLAVERY / SOLD_INTO_SLAVERY_BY
- GARRISONED / GARRISONED_BY
- DISTRIBUTED_LAND_TO / LAND_DISTRIBUTED_BY

### ❓ Need to Check:
- REBELLED / REBELLED_AGAINST (need to verify if exists)

---

## LLM Output Format Recommendation

The LLM should output structured JSON with:
1. **Entities array**: All unique entities mentioned
2. **Triples array**: Subject-Predicate-Object relationships
3. **Metadata**: Confidence scores, temporal information, quantities

This format allows:
- Entity deduplication before Neo4j insertion
- Relationship validation against schema
- Confidence-based filtering
- Temporal property assignment

