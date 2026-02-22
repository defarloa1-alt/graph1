# Federation Score Model - Simplified (2026-02-19)

**Status:** Current implementation spec  
**Supersedes:** FEDERATION_SCORE_MODEL_2026-02-19.md (over-complicated)

---

## 🎯 **Objective**

Score each entity by how well it's federated with **actual available authorities**.

---

## 📊 **Federation Sources (What We Actually Have)**

### **For Places:**
1. **Pleiades ID** - Always present (source file) ✅
2. **Wikidata QID** - 2,458 of 41,993 places (5.9%) ✅
3. **Temporal signal** - min_date/max_date on all places ✅

### **For Periods:**
1. **PeriodO ID** - All 1,077 periods have this ✅
2. **Wikidata QID** - Some periods have this
3. **Temporal signal** - start_year/end_year ✅

---

## 🔢 **Simplified Scoring Formula**

### **For Places (100 points total):**

```
federation_score = qid_score + temporal_score + pleiades_score

1. Pleiades ID present: +30 points (always yes)
2. Wikidata QID present: +50 points
3. Temporal signal present: +20 points

Maximum: 100 points
Minimum: 50 points (pleiades + temporal, no QID)
```

### **For Periods (100 points total):**

```
federation_score = qid_score + temporal_score + periodo_score

1. PeriodO ID present: +40 points (always yes)
2. Wikidata QID present: +40 points
3. Temporal signal present: +20 points

Maximum: 100 points
Minimum: 60 points (periodo + temporal, no QID)
```

---

## 🏆 **Federation States**

| State | Score | Meaning |
|-------|-------|---------|
| **FS0_UNFEDERATED** | 0-39 | No federation (shouldn't happen with our data) |
| **FS1_BASE** | 40-59 | Single authority only |
| **FS2_FEDERATED** | 60-79 | Multiple authorities |
| **FS3_WELL_FEDERATED** | 80-100 | Wikidata + source authority + temporal |

---

## 🔑 **Federation Cipher Key**

**Simplified format:**

### **For Places:**
```
<qid>|<pleiades_id>|<min_date>|<max_date>
```

**Examples:**
```
Q41|520998|-657|2025              (Constantinople - fully federated)
NULL|295353|-30|300               (Thalefsa - no QID yet)
Q13687|462236|-750|2025           (Enna - has QID)
```

### **For Periods:**
```
<qid>|<periodo_id>|<start_year>|<end_year>
```

**Examples:**
```
Q17167|romano.roman_republic.1|-509|-27    (Roman Republic)
NULL|periodo.p0abcd|-2000|-1500             (No QID)
```

---

## 📈 **Score Calculation Examples**

### **Example 1: Place WITH Wikidata QID**

**Place:** 'Ir David/Wadi Hilweh
- pleiades_id: 714055238 → **+30 points**
- qid: Q1218 → **+50 points**
- min_date: -1000, max_date: 2025 → **+20 points**
- **Total: 100 points → FS3_WELL_FEDERATED**

### **Example 2: Place WITHOUT Wikidata QID**

**Place:** Thalefsa
- pleiades_id: 295353 → **+30 points**
- qid: NULL → **+0 points**
- min_date: -30, max_date: 300 → **+20 points**
- **Total: 50 points → FS1_BASE**

### **Example 3: Period WITH Wikidata QID**

**Period:** Roman Republic
- periodo_id: romano.roman_republic.1 → **+40 points**
- qid: Q17167 → **+40 points**
- start_year: -509, end_year: -27 → **+20 points**
- **Total: 100 points → FS3_WELL_FEDERATED**

---

## 💻 **Implementation**

### **Python Module:**

```python
class FederationScorer:
    """Simple federation scorer based on actual available authorities"""
    
    def score_place(self, place_node: dict) -> dict:
        """
        Score a Place node.
        
        Args:
            place_node: dict with properties from Neo4j
        
        Returns:
            {
                'federation_score': int (0-100),
                'federation_state': str (FS0-FS3),
                'federation_cipher_key': str,
                'has_qid': bool,
                'has_temporal': bool
            }
        """
        score = 0
        
        # Pleiades (always present)
        if place_node.get('pleiades_id'):
            score += 30
        
        # Wikidata
        has_qid = bool(place_node.get('qid'))
        if has_qid:
            score += 50
        
        # Temporal
        has_temporal = bool(place_node.get('min_date') or place_node.get('max_date'))
        if has_temporal:
            score += 20
        
        # Determine state
        if score >= 80:
            state = 'FS3_WELL_FEDERATED'
        elif score >= 60:
            state = 'FS2_FEDERATED'
        elif score >= 40:
            state = 'FS1_BASE'
        else:
            state = 'FS0_UNFEDERATED'
        
        # Generate cipher
        qid = place_node.get('qid') or 'NULL'
        pleiades = place_node.get('pleiades_id') or 'NULL'
        min_date = str(place_node.get('min_date')) if place_node.get('min_date') else 'NULL'
        max_date = str(place_node.get('max_date')) if place_node.get('max_date') else 'NULL'
        cipher = f"{qid}|{pleiades}|{min_date}|{max_date}"
        
        return {
            'federation_score': score,
            'federation_state': state,
            'federation_cipher_key': cipher,
            'has_qid': has_qid,
            'has_temporal': has_temporal
        }
    
    def score_period(self, period_node: dict) -> dict:
        """
        Score a Period node.
        
        Args:
            period_node: dict with properties from Neo4j
        
        Returns:
            Same structure as score_place
        """
        score = 0
        
        # PeriodO (always present for our periods)
        if period_node.get('authority') == 'PeriodO' or period_node.get('periodo_id'):
            score += 40
        
        # Wikidata
        has_qid = bool(period_node.get('qid'))
        if has_qid:
            score += 40
        
        # Temporal
        has_temporal = bool(period_node.get('start_year') or period_node.get('start'))
        if has_temporal:
            score += 20
        
        # Determine state
        if score >= 80:
            state = 'FS3_WELL_FEDERATED'
        elif score >= 60:
            state = 'FS2_FEDERATED'
        elif score >= 40:
            state = 'FS1_BASE'
        else:
            state = 'FS0_UNFEDERATED'
        
        # Generate cipher
        qid = period_node.get('qid') or 'NULL'
        periodo = period_node.get('periodo_id') or period_node.get('authority_uri') or 'NULL'
        start = str(period_node.get('start_year') or period_node.get('start') or 'NULL')
        end = str(period_node.get('end_year') or period_node.get('end') or 'NULL')
        cipher = f"{qid}|{periodo}|{start}|{end}"
        
        return {
            'federation_score': score,
            'federation_state': state,
            'federation_cipher_key': cipher,
            'has_qid': has_qid,
            'has_temporal': has_temporal
        }
```

---

## 📋 **Expected Distributions**

### **Places (41,993 total):**

| State | Score | Estimated Count | Percentage |
|-------|-------|----------------|------------|
| FS3_WELL_FEDERATED | 80-100 | ~2,458 | 5.9% (have QID) |
| FS2_FEDERATED | 60-79 | 0 | 0% |
| FS1_BASE | 40-59 | ~39,535 | 94.1% (no QID) |
| FS0_UNFEDERATED | 0-39 | 0 | 0% |

### **Periods (1,077 total):**

| State | Score | Estimated Count | Percentage |
|-------|-------|----------------|------------|
| FS3_WELL_FEDERATED | 80-100 | ? | TBD (depends on QID coverage) |
| FS2_FEDERATED | 60-79 | ~1,077 | ~100% (all have PeriodO + temporal) |
| FS1_BASE | 40-59 | 0 | 0% |
| FS0_UNFEDERATED | 0-39 | 0 | 0% |

---

## ✅ **Summary**

**Federation sources that matter:**
1. ✅ **Wikidata QID** (qid)
2. ✅ **Pleiades ID** (pleiades_id) - for places
3. ✅ **PeriodO ID** (periodo_id) - for periods
4. ✅ **Temporal signal** (min_date/max_date or start/end)

**NOT included** (over-complicated, not worth it):
- ❌ GeoNames (can add later if needed)
- ❌ TGN (minimal coverage)
- ❌ Complex 5-dimension scoring
- ❌ Spatial quality metrics

**Simple = Better**

---

**Ready to implement this simplified scorer?**

**Next:** Build the FederationScorer module and score all your nodes!
