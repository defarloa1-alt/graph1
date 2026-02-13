# Path Configuration System

Centralized path management for Chrystallum codebase. This system allows path changes to be made in one place and supports gradual migration from legacy to new directory structure.

## Files

- **`paths.py`** - Python path configuration module
- **`paths.bat`** - Batch file path configuration
- **`README.md`** - This file

## Purpose

During directory reorganization, this configuration system:

1. **Provides backward compatibility** - Works with both old and new directory structures
2. **Centralizes path management** - Change paths in one place
3. **Supports gradual migration** - Migrate files incrementally without breaking everything
4. **Enables validation** - Easy to check which paths are used where

## Usage

### Python Scripts

```python
# Option 1: Use helper methods (recommended)
from config.paths import Paths

taxonomy_csv = Paths.temporal_taxonomy()
geo_csv = Paths.geo_features()
relationships_csv = Paths.canonical_relationships()

# Option 2: Use base directories
from config.paths import DATA_DIR, get_data_path

custom_csv = get_data_path("backbone", "temporal", "my_file.csv")
# Or
custom_csv = DATA_DIR / "backbone" / "temporal" / "my_file.csv"

# Option 3: Use legacy fallback automatically
from config.paths import Paths
csv_path = Paths.temporal_taxonomy()  # Checks both new and legacy locations
```

### Batch Files

```batch
@echo off
REM Source the path configuration
call config\paths.bat

REM Use predefined variables
echo Using taxonomy: %TAXONOMY_CSV%
python import_periods.py "%TAXONOMY_CSV%"

REM Or use base directories
if exist "%DATA_BACKBONE_DIR%\temporal\time_periods.csv" (
    echo Found in new location
) else (
    echo Using legacy: %LEGACY_TEMPORAL_DATA%
)
```

## Migration Modes

Set environment variable `CHRYSTALLUM_PATH_MODE` to control behavior:

- **`legacy`** (default): Check legacy paths first, fallback to new
- **`new`**: Use new paths only (after migration complete)
- **`hybrid`**: Check new paths first, fallback to legacy

### Example (Python)

```python
import os
os.environ['CHRYSTALLUM_PATH_MODE'] = 'new'  # Force new structure
from config.paths import Paths
```

### Example (Batch)

```batch
set CHRYSTALLUM_PATH_MODE=new
call config\paths.bat
```

## Migration Strategy

### Phase 1: Setup (Current)
- ✅ Create path configuration files
- ✅ Use `legacy` mode (default)
- ✅ All existing code continues to work

### Phase 2: Gradual Migration
- Update scripts to use `config.paths` or `config\paths.bat`
- Copy files to new locations (keep old locations)
- Test that both old and new paths work

### Phase 3: Cutover
- Set `CHRYSTALLUM_PATH_MODE=new`
- Remove old directory structure
- Remove legacy path fallbacks

## Available Path Helpers

### Python (`Paths` class)

- `Paths.temporal_taxonomy()` - Temporal/time_periods.csv
- `Paths.year_nodes()` - year_nodes.csv
- `Paths.geo_features()` - stable_geographic_features.csv
- `Paths.region_place_mapping()` - region_place_mapping.csv
- `Paths.canonical_relationships()` - canonical_relationship_types.csv
- `Paths.entity_hierarchy()` - neo4j_entity_hierarchy.csv
- `Paths.schema_json()` - chrystallum_schema.json
- `Paths.cypher_template_library()` - cypher_template_library.json
- `Paths.cypher_templates()` - cypher_templates.json

### Batch (Predefined Variables)

- `%TAXONOMY_CSV%` - Temporal/time_periods.csv
- `%YEAR_NODES_CSV%` - year_nodes.csv
- `%GEO_FEATURES_CSV%` - stable_geographic_features.csv
- `%REGION_PLACE_CSV%` - region_place_mapping.csv
- `%CANONICAL_REL_CSV%` - canonical_relationship_types.csv
- `%ENTITY_HIERARCHY_CSV%` - neo4j_entity_hierarchy.csv
- `%SCHEMA_JSON%` - chrystallum_schema.json

### Base Directories

**Python:**
- `DATA_DIR` - `data/`
- `SCRIPTS_DIR` - `scripts/`
- `CYPHER_DIR` - `cypher/`
- `DOCS_DIR` - `docs/`

**Batch:**
- `%DATA_DIR%` - `data\`
- `%SCRIPTS_DIR%` - `scripts\`
- `%CYPHER_DIR%` - `cypher\`
- `%DOCS_DIR%` - `docs\`

## Example: Migrating a Script

### Before (hardcoded path):

```python
script_dir = Path(__file__).parent
csv_path = script_dir / 'Temporal/time_periods.csv'
```

### After (using config):

```python
from config.paths import Paths

csv_path = Paths.temporal_taxonomy()
```

### Or with custom path:

```python
from config.paths import get_data_path

csv_path = get_data_path("backbone", "temporal", "Temporal/time_periods.csv")
```

## Testing

To test path configuration:

```python
from config.paths import Paths

# Check if paths resolve
taxonomy = Paths.temporal_taxonomy()
print(f"Taxonomy path: {taxonomy}")
print(f"Exists: {taxonomy.exists()}")
```

## See Also

- `scan_paths.py` - Scan codebase for hardcoded paths that need updating
- Migration plan in main project documentation


