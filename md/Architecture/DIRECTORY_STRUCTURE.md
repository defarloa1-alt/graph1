# Chrystallum Directory Structure

## Complete Reorganized Structure

```
graph 3/
├── 📚 docs/                          # Human documentation
│   ├── architecture/                  # Architecture specifications
│   ├── guides/                        # How-to guides
│   ├── examples/                      # Example analyses
│   └── reference/                     # Reference materials
│
├── 💬 prompts/                        # LLM prompts & instruction templates
│   ├── system/                        # System prompts (ready to use)
│   │   ├── extraction_agent.txt
│   │   └── person_research_agent.txt
│   ├── guides/                        # Extraction instruction guides
│   │   ├── temporal_extraction.md
│   │   └── geographic_extraction.md
│   └── templates/                     # Prompt loading utilities
│       └── load_prompts.py
│
├── 📊 data/                           # All data files
│   ├── schemas/                       # Schema definitions (JSON)
│   │   ├── chrystallum_schema.json
│   │   ├── cypher_template_library.json
│   │   └── cypher_templates.json
│   ├── backbone/                      # Backbone data (CSV)
│   │   ├── temporal/                  # Temporal backbone
│   │   │   ├── Temporal/time_periods.csv
│   │   │   ├── year_nodes.csv
│   │   │   └── period_*.csv
│   │   ├── geographic/                # Geographic backbone
│   │   │   ├── stable_geographic_features.csv
│   │   │   └── region_place_mapping.csv
│   │   └── relations/                 # Relations backbone
│   │       ├── canonical_relationship_types.csv
│   │       └── neo4j_entity_hierarchy.csv
│   └── reference/                     # Reference data
│
├── 🐍 scripts/                        # All Python & batch scripts
│   ├── setup/                         # Initial setup scripts
│   │   ├── test_connection.bat
│   │   └── test_neo4j_connection.py
│   ├── schema/                        # Schema management
│   │   └── consolidate_schema.py
│   ├── backbone/                      # Backbone import/management
│   │   ├── temporal/                  # Temporal scripts
│   │   │   ├── *.py
│   │   │   └── *.bat
│   │   ├── geographic/                # Geographic scripts
│   │   │   ├── *.py
│   │   │   └── *.bat
│   │   └── relations/                 # Relations scripts
│   │       └── *.py
│   ├── utils/                         # Utility scripts
│   └── maintenance/                   # Maintenance scripts
│
├── 🔷 cypher/                         # All Cypher scripts
│   ├── setup/                         # Setup/initialization
│   │   ├── import_periods_to_neo4j.cypher
│   │   ├── import_places_to_neo4j.cypher
│   │   └── ...
│   ├── queries/                       # Query examples
│   │   ├── example_queries.cypher
│   │   ├── QUICK_GRAPH_VISUALIZATION.cypher
│   │   └── ...
│   └── maintenance/                   # Maintenance queries
│       └── MIGRATE_*.cypher
│
├── 🔧 config/                         # Configuration
│   ├── paths.py                       # Python path configuration
│   └── paths.bat                      # Batch path configuration
│
├── 📋 examples/                       # Code examples
│   └── Roman Republic/
│
├── 🏛️ backbone/                       # Backbone modules (if needed)
├── 📦 modules/                        # Code modules (if any)
├── 🧪 tests/                          # Tests (if any)
│
└── [Legacy directories - still exist for backward compatibility]
    ├── temporal/                      # Will be removed after migration
    ├── relations/                     # Will be removed after migration
    ├── Reference/                     # Will be removed after migration
    └── Docs/                          # Will be removed after migration
```

## Migration Status

### ✅ Completed
- ✅ Created new directory structure
- ✅ Copied data files (CSV, JSON) to `data/`
- ✅ Copied scripts to `scripts/backbone/`
- ✅ Copied Cypher files to `cypher/`
- ✅ Copied documentation to `docs/`
- ✅ Copied prompts to `prompts/`
- ✅ Path configuration system created
- ✅ Backward compatibility maintained

### ⏳ Pending (Optional)
- ⏳ Update Python scripts to use `config.paths`
- ⏳ Update batch files to use `config\paths.bat`
- ⏳ Remove legacy directories after verification

## Usage

### Loading Data Files
```python
from config.paths import Paths

# Use helper methods
taxonomy = Paths.temporal_taxonomy()
geo_csv = Paths.geo_features()
relationships = Paths.canonical_relationships()
```

### Loading Prompts
```python
from prompts.templates.load_prompts import get_extraction_agent_prompt

prompt = get_extraction_agent_prompt()
```

### Accessing Scripts
```python
from config.paths import SCRIPTS_DIR

script_path = SCRIPTS_DIR / "backbone" / "temporal" / "import_periods.py"
```

## Path Configuration

The system maintains backward compatibility:
- **Legacy mode (default)**: Checks old locations first
- **New mode**: Uses new locations only
- **Hybrid mode**: Checks new first, falls back to old

Set environment variable: `CHRYSTALLUM_PATH_MODE=new`

## See Also

- `config/README.md` - Path configuration usage
- `prompts/README.md` - Prompt directory usage
- `MIGRATION_PATH_CONFIG.md` - Migration strategy
- `REORGANIZATION_COMPLETE.md` - Reorganization summary


