# Session Tracking Guide

**Purpose:** Track which chat session made each change for impact analysis and conflict detection.

---

## How It Works

### Session IDs

Each chat session gets a unique Session ID that:
- Persists across multiple turns in the same session
- Is automatically generated when first needed
- Format: `SESSION_YYYYMMDD_HHMMSS_HASH` (e.g., `SESSION_20251212_143045_a3f2b1c4`)
- Stored in `.chat_session_id` (git-ignored)

### Using Session Tracking

#### 1. Get Your Session ID

```python
from scripts.utils.session_tracker import get_session_id

session_id = get_session_id()
print(f"My session ID: {session_id}")
```

#### 2. Log a Change

```python
from scripts.utils.session_tracker import log_change

log_change(
    session_id=session_id,
    description="Added new relationship types for discovery schema",
    object_changed="canonical_relationship_types.csv",
    files_affected=["relations/canonical_relationship_types.csv"],
    change_type="Schema",
    dependencies=["SESSION_20251212_140000_abc123"],  # Optional: other sessions this depends on
    notes="Added 42 new relationships"  # Optional: additional context
)
```

#### 3. Check Impact Before Making Changes

**Example:** Before modifying `canonical_relationship_types.csv`, check what other sessions have done:

```python
from scripts.utils.session_tracker import analyze_impact, get_session_id

session_id = get_session_id()
impact = analyze_impact(session_id, "canonical_relationship_types.csv")

print(f"Related changes found: {impact['total_related']}")
print(f"Sessions that modified this: {impact['sessions_affected']}")
if impact['warning']:
    print("⚠️ WARNING: Other sessions have modified this object recently!")
    for change in impact['related_changes']:
        print(f"  - {change['datetime']} by {change['session']}: {change['description']}")
```

#### 4. Get Recent Changes from Other Sessions

```python
from scripts.utils.session_tracker import get_recent_changes, get_session_id

session_id = get_session_id()
recent = get_recent_changes(days=7, exclude_session=session_id)

print(f"Found {len(recent)} changes from other sessions in last 7 days:")
for change in recent:
    print(f"  - [{change['session']}] {change['description']}")
```

---

## Impact Analysis Workflow

### Before Making a Change

1. **Get your session ID**
2. **Analyze impact** on the object you're changing
3. **Review related changes** from other sessions
4. **Check for conflicts** or dependencies
5. **Make your change**
6. **Log the change** with session ID

### Example: Adding New Relationships

```python
from scripts.utils.session_tracker import *

# Step 1: Get session ID
session_id = get_session_id()

# Step 2: Check impact
impact = analyze_impact(session_id, "canonical_relationship_types.csv")
if impact['total_related'] > 0:
    print(f"⚠️ {impact['total_related']} recent changes to this file:")
    for change in impact['related_changes']:
        print(f"  - {change['session']}: {change['description']}")

# Step 3: Make your change (add relationships to CSV, etc.)
# ... your code here ...

# Step 4: Log the change
log_change(
    session_id=session_id,
    description="Added Typological and Evolution relationship categories",
    object_changed="canonical_relationship_types.csv",
    files_affected=["relations/canonical_relationship_types.csv"],
    change_type="Schema",
    dependencies=impact['sessions_affected'] if impact['total_related'] > 0 else None
)
```

---

## Benefits

### 1. Conflict Detection
- See what other sessions modified before you change the same object
- Identify potential conflicts early

### 2. Dependency Tracking
- Understand what changes your work depends on
- Track the sequence of related changes

### 3. Impact Analysis
- Review LLMs can see what changed and who changed it
- Understand the context of modifications

### 4. Session Attribution
- Know which chat session created each feature
- Track contributions across multiple sessions

---

## Changelog Format

The changelog now includes Session ID in every entry:

```
| DateTime | Session ID | Description | Object Changed | Files Affected | Type |
|----------|------------|-------------|----------------|----------------|------|
| 2025-12-12 14:30 | SESSION_20251212_143045_a3f2b1c4 | Added new relationships | canonical_relationship_types.csv | relations/canonical_relationship_types.csv | Schema |
```

---

## Session ID Lifecycle

1. **New Chat Session Starts**
   - No `.chat_session_id` file exists
   - First call to `get_session_id()` creates a new one
   - Session ID persists for the duration of the chat session

2. **Subsequent Turns in Same Session**
   - `.chat_session_id` file exists
   - `get_session_id()` returns the same ID
   - All changes in this session use the same ID

3. **New Chat Session (Different Window/Tab)**
   - Either no `.chat_session_id` or user wants new session
   - Can force new session: `get_session_id(force_new=True)`
   - Gets a new unique Session ID

---

## Integration with AI Agents

### For Review LLMs

When reviewing changes, an LLM can:

1. Read the changelog
2. Identify which session made which changes
3. Analyze impact of current changes on previous sessions
4. Detect conflicts or dependencies
5. Provide recommendations

### Example Review Prompt

```
Review the changelog and analyze:
1. What changes were made by session SESSION_20251212_143045_a3f2b1c4?
2. Do these changes conflict with changes from SESSION_20251212_140000_abc123?
3. What dependencies exist between these sessions?
4. Are there any breaking changes?
```

---

## Best Practices

1. **Always check impact before changing shared objects**
   - Especially schema files (CSVs, JSON)
   - Check `CHANGELOG.md` manually or use `analyze_impact()`

2. **Log all significant changes**
   - Schema modifications
   - Code changes that affect behavior
   - Documentation updates that change workflows

3. **Use dependency tracking**
   - If your change depends on another session's work, list it
   - Helps reviewers understand the sequence

4. **Be specific in descriptions**
   - Clear, concise descriptions help impact analysis
   - Include counts, types, or key details

5. **Review recent changes from other sessions**
   - Before starting work, check what changed recently
   - Avoid working on objects others just modified

