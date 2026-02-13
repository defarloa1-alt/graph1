

---

## Minimally Required Backbone Policy

- **Every entity in Chrystallum must have at least one authoritative identifier:**
    
    - **Preferably a FAST ID** (for history, biography, topics, events, etc.)
        
    - **Or a Wikidata QID** where FAST is unavailable or the entity is new/crucial but not covered yet
        

## Rationale

- **FAST and Wikidata together cover nearly all real-world, well-attested entities.**
    
- For edge cases (rare, emerging, or hyper-local entities not in FAST or Wikidata), provisionally allow:
    
    - A local authority ID OR
        
    - Just a canonical label and description, but flag for review/mapping when upstream vocabularies evolve.
        

---

## Suggested Documentation Language

> **Backbone Assignment Requirement:**  
> Every record in the knowledge graph must carry at least one authoritative backbone identifier—either a FAST ID (preferred) or Wikidata QID (if not available in FAST).
> 
> - If both exist, both should be assigned.
>     
> - If neither exists, the entity must be flagged for curation and future mapping.
>     

---

## Why This Works

- Keeps the system robust, interoperable, and immediately useful for most applications.
    
- Avoids unnecessary complexity by not requiring both (unless present).
    
- Reduces friction for new/exotic entities without official subject authority.
    
- Ensures long-term maintainability and upgrade/federation paths.
    

---

**In summary:**

- **At least one** of [FAST, Wikidata QID] is required for all entities—both if possible, just one if that’s all there is, and provision for local or "to-be-curated" tags in rare exceptions.
    

This balances rigor and flexibility for scaling Chrystallum across domains.