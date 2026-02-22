# Event Node Schema (Simple)

**Date:** January 16, 2026  
**Status:** Initial schema for converted Period entries  
**Purpose:** Simple Event structure for periods that are better modeled as events

---

## Node Label

```cypher
:Event
```

---

## Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q193547" | Wikidata ID |
| `label` | string | text | "Reign of Terror" | Event name (displays in graph) |
| `start_year` | integer | year | 1793 | Start year |
| `end_year` | integer | year | 1794 | End year |

---

## Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `start_date_iso` | string | ISO 8601 | "1793-09-05" | Precise start date |
| `end_date_iso` | string | ISO 8601 | "1794-07-28" | Precise end date |
| `location_qid` | string | Q[0-9]+ | "Q142" | Where it occurred |
| `event_type` | string | text | "political_crisis" | Type classification |
| `granularity` | string | enum | "composite" | atomic/composite/period_event |
| `description` | string | text | "Period of violence..." | Event description |
| `cidoc_crm_class` | string | E[0-9]+_[A-Z] | "E5_Event" | CIDOC-CRM class |
| `unique_id` | string | pattern | "EVENT_Q193547" | System identifier |

---

## Template

```cypher
CREATE (e:Event {
  qid: 'Q193547',
  label: 'Reign of Terror',
  start_year: 1793,
  end_year: 1794,
  start_date_iso: '1793-09-05',
  end_date_iso: '1794-07-28',
  location_qid: 'Q142',
  event_type: 'political_crisis',
  granularity: 'composite',
  description: 'Period of violence during the French Revolution',
  cidoc_crm_class: 'E5_Event',
  unique_id: 'EVENT_Q193547'
})
```

---

## Relationships

### From Event
- `(Event)-[:OCCURRED_IN]->(Period)` - Event occurred during period
- `(Event)-[:LOCATED_IN]->(Place)` - Event occurred at place
- `(Event)-[:PART_OF]->(Event)` - Event is part of larger event
- `(Event)-[:PRECEDED_BY]->(Event)` - Sequential events
- `(Event)-[:FOLLOWED_BY]->(Event)` - Sequential events

### To Event
- `(Person)-[:PARTICIPATED_IN]->(Event)` - Person participated
- `(Period)-[:CONTAINS_EVENT]->(Event)` - Period contains event

---

## Notes

- This is a **simplified Event schema** for converted Period entries
- Full Event schema with TGAR (Trigger-Goal-Action-Result) structure exists elsewhere
- These converted events can be enhanced later with full TGAR properties
- Start/end years are required for temporal queries
- CIDOC-CRM class should be `E5_Event` or subclass (E7_Activity, E6_Destruction, etc.)

