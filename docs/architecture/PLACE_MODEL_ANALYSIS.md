# Place Model - Current vs Correct Architecture

**Date:** 2026-02-19  
**Issue:** Current implementation doesn't match architecture specification

---

## ❌ **Current Implementation (WRONG)**

```cypher
(:Place {pleiades_id: "295353", label: "Thalefsa"})
  -[:HAS_NAME]->(:PlaceName {name_attested: "Thalefsa", language: "la"})
  -[:HAS_NAME]->(:PlaceName {name_attested: "Θάλεφσα", language: "grc"})
```

**Problem:**
- Place name changes over time (Byzantium → Constantinople → Istanbul)
- Place boundaries change over time (expansion, contraction)
- Current model conflates all time periods into one Place node
- Cannot represent: "This place was called X during period Y"

---

## ✅ **Correct Architecture (FROM SPEC)**

### **From ARCHITECTURE_ONTOLOGY.md Section 3.1.2:**

**Three-tier model:**

```cypher
// Tier 1: Stable geographic identity (abstract)
(:Place {
  place_id: "plc_295353",
  pleiades_id: "295353",
  lat: 36.63831,           // Modern/primary coordinates
  long: 2.336182
})

// Tier 2: Time-scoped instantiation (concrete)
(:PlaceVersion {
  pver_id: "pver_295353_01",
  label: "Thalefsa (Roman Period)",
  start_date: "-30",       // When this version/name was valid
  end_date: "300",
  authority: "Pleiades",
  confidence: 0.85
})
  -[:VERSION_OF]->(:Place)

// Tier 3: Names for this version
(:PlaceName {
  name_id: "name_295353_01",
  name_attested: "Thalefsa",
  language: "la"
})
  <-[:HAS_NAME]-(:PlaceVersion)
```

### **Benefits:**

1. **Temporal Accuracy:**
   - "Constantinople" valid 330-1453 CE
   - "Istanbul" valid 1453 CE-present
   - Can query: "What was this place called in year 1000?"

2. **Boundary Changes:**
   - Roman Syria (province boundaries)
   - Byzantine Syria (different boundaries)
   - Same location, different extents over time

3. **Authority Tracking:**
   - Different sources may define different versions
   - Pleiades version vs TGN version vs modern
   - Each PlaceVersion has confidence score

4. **SFA Claim Model:**
   - SFAs propose claims about **PlaceVersion** (time-scoped)
   - Not about abstract Place (timeless)
   - Example: "Battle occurred at Byzantium (Greek Period)" vs "Constantinople (Byzantine Period)"

---

## 🔍 **What Architecture Says**

**From Section 3.1.2.1 PlaceVersion:**

> **Purpose:** Represents time-scoped and authority-scoped instantiation of a place (e.g., "Roman Province of Syria, 1st Century CE").

**Required Properties:**
- `pver_id` - Unique version identifier
- `label` - Temporal description
- `start_date`, `end_date` - When this version was valid
- `authority` - Source of definition
- `confidence` - Authority confidence

**Required Edges:**
- `VERSION_OF` → Place (links to stable identity)
- `HAS_GEOMETRY` → Geometry (spatial representation for this version)

**Optional Edges:**
- `BROADER_THAN` → PlaceVersion (administrative hierarchy)
- `NARROWER_THAN` → PlaceVersion

**Usage Pattern:**
```cypher
(:Event)-[:TOOK_PLACE_AT]->(:PlaceVersion)-[:VERSION_OF]->(:Place)
```

---

## 🛠️ **Current State Analysis**

### **What We Have:**
```
41,993 Place nodes
38,321 PlaceName nodes
42,111 HAS_NAME relationships (Place → PlaceName)
```

### **What We SHOULD Have:**
```
41,993 Place nodes (stable identities)
??? PlaceVersion nodes (time-scoped versions)
38,321 PlaceName nodes
??? PlaceVersion → Place (VERSION_OF)
42,111 PlaceVersion → PlaceName (HAS_NAME)
```

---

## 💡 **The Fix**

### **Option A: Retrofit Current Data**

1. **Create default PlaceVersion for each Place:**
   - One PlaceVersion per Place
   - Inherit temporal bounds from Place (min_date, max_date)
   - Label = Place label + authority
   - Authority = "Pleiades"

2. **Rewire PlaceName relationships:**
   - Change: `(:Place)-[:HAS_NAME]->(:PlaceName)`
   - To: `(:PlaceVersion)-[:HAS_NAME]->(:PlaceName)`

3. **Add VERSION_OF links:**
   - `(:PlaceVersion)-[:VERSION_OF]->(:Place)`

### **Option B: Future Enhancement**

1. **Keep current structure for now** (works for basic queries)
2. **Add PlaceVersion layer** when we need:
   - Multiple temporal versions per place
   - Authority-specific versions
   - Complex boundary changes

3. **Gradually migrate:**
   - Start with high-value places (Rome, Constantinople, etc.)
   - Build out as needed

---

## 🎯 **Recommendation**

**For now (MVP):**
- ✅ Keep current Place → PlaceName (works for 95% of use cases)
- ✅ Document the limitation
- ✅ Plan PlaceVersion migration for Phase 2

**Why:**
- Most ancient places don't have complex name/boundary evolution
- Places with multiple versions (Constantinople, etc.) are <1% of corpus
- Can add PlaceVersion layer without breaking existing data

**When to add PlaceVersion:**
- When loading entities/events that need time-specific place references
- When SFAs start proposing claims about places
- When we need to represent "This place during this period"

---

## ❓ **Your Decision**

**Option A:** Retrofit now (add PlaceVersion layer to current data) - **~2 hours**  
**Option B:** Keep as-is, add PlaceVersion later when needed - **document limitation**  
**Option C:** Selective retrofit (add PlaceVersion only for major places like Rome, Constantinople) - **~30 min**

**Which do you prefer?**

---

**My recommendation:** Option B for now (document limitation, add later), OR Option C (selective retrofit for major places only)
