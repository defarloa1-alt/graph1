# LCC Subject Taxonomy Configuration Guide

This directory contains configuration files and documentation for the Library of Congress Classification (LCC) subject taxonomy integration.

## Directory Structure

```
deployment/config/subject_taxonomy/
├── README.md                    # This file
├── lcc_schema.sql              # Database schema (PostgreSQL)
├── sample_data/                # Sample LCC data files
│   ├── sample_lcc_entries.csv  # Example CSV format
│   └── sample_lcc_entries.json # Example JSON format
├── config/                     # Configuration files
│   ├── database.env           # Database connection settings
│   └── etl_config.yaml        # ETL process configuration
└── docs/                      # Additional documentation
    ├── lcc_format_guide.md    # LCC data format specification
    └── api_integration.md     # API integration guide
```

## Quick Start

### 1. Database Setup

1. Ensure PostgreSQL is running
2. Set database connection in environment:

```bash
export LCC_DATABASE_URL="postgresql://user:password@localhost:5432/federated_graph"
```

### 2. Run ETL Process

```bash
# Navigate to framework root
cd /path/to/federated-graph-framework

# Run LCC file parser to generate consolidated data
python lcc_file_parser.py

# Run ETL to load data into database
python scripts/load_lcc_taxonomy.py
```

### 3. Verify Installation

```bash
# Test subject taxonomy bundle
python subject_taxonomy_bundle.py
```

## Data Format Specification

### CSV Format Expected

The ETL process expects CSV files with the following structure:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| class_code | String | LCC classification code | "QA76.9.A25" |
| label | String | Human-readable description | "Computer algorithms" |
| parent_code | String | Parent classification code | "QA76.9" |
| description | Text | Detailed description | "Detailed study of..." |
| range_start | Numeric | Start of numeric range | 76.9 |
| range_end | Numeric | End of numeric range | 76.95 |
| notes | Text | Additional notes | "See also..." |

### JSON Format

```json
{
  "class_code": "QA76.9.A25",
  "label": "Computer algorithms",
  "parent_code": "QA76.9",
  "description": "Study of algorithmic approaches...",
  "level": 2,
  "source_file": "LCC_Q2024OUT.xlsx",
  "metadata": {
    "range_start": 76.9,
    "range_end": 76.95,
    "notes": "Cross-referenced with..."
  }
}
```

## ETL Process

### Command Line Usage

```bash
# Basic ETL run
python scripts/load_lcc_taxonomy.py

# ETL with custom data file
python scripts/load_lcc_taxonomy.py --data-file custom_lcc_data.json

# ETL with specific version
python scripts/load_lcc_taxonomy.py --version "2024_Q3_RELEASE"

# ETL with batch processing
python scripts/load_lcc_taxonomy.py --batch-size 500
```

### Idempotent Loading

The ETL script is designed to be idempotent:
- Existing records are updated rather than duplicated
- Failed runs can be safely restarted
- Version tracking prevents duplicate imports

### Validation Rules

1. **Class Code Format**: Must match LCC patterns (e.g., "A", "QA76", "QA76.9.A25")
2. **Hierarchy Consistency**: Parent codes must exist before children
3. **Unique Codes**: Each class_code must be unique within the taxonomy
4. **Label Requirements**: All entries must have non-empty labels

## Bundle Integration

### Loading in Application

```python
from subject_taxonomy_bundle import create_subject_taxonomy_bundle

# Create bundle with database connection
bundle = create_subject_taxonomy_bundle(
    database_url="postgresql://user:pass@localhost/db"
)

# Use in application
results = bundle.search_by_label("computer science")
children = bundle.get_children("QA76")
```

### Startup Integration

Add to your application startup:

```python
# In your main application initialization
def initialize_app():
    # ... other initialization ...
    
    # Load subject taxonomy
    global subject_taxonomy
    subject_taxonomy = create_subject_taxonomy_bundle()
    
    if not subject_taxonomy.subject_vertices:
        logger.warning("Subject taxonomy not loaded - run ETL process")
    else:
        logger.info(f"Loaded {len(subject_taxonomy.subject_vertices)} subject classifications")
```

## Refresh Procedures

### Manual Refresh

```python
# Refresh from database
bundle.refresh()
```

### Scheduled Refresh

Add to your application's scheduled tasks:

```python
# Refresh every 24 hours
@scheduled_task(hours=24)
def refresh_subject_taxonomy():
    global subject_taxonomy
    success = subject_taxonomy.refresh()
    if success:
        logger.info("Subject taxonomy refreshed successfully")
    else:
        logger.error("Failed to refresh subject taxonomy")
```

## Configuration Options

### Environment Variables

- `LCC_DATABASE_URL`: PostgreSQL connection string
- `LCC_ETL_BATCH_SIZE`: ETL batch processing size (default: 1000)
- `LCC_AUTO_REFRESH`: Enable automatic refresh (default: true)
- `LCC_CACHE_TIMEOUT`: Search cache timeout in seconds (default: 3600)

### Database Configuration

Recommended PostgreSQL settings for optimal performance:

```sql
-- Increase shared memory for large taxonomies
shared_buffers = 256MB

-- Optimize for read-heavy workloads
effective_cache_size = 1GB

-- Index maintenance
maintenance_work_mem = 64MB
```

## Monitoring and Maintenance

### Health Checks

```python
def check_taxonomy_health():
    stats = bundle.statistics
    
    checks = {
        'vertices_loaded': stats['total_vertices'] > 0,
        'graph_connected': stats.get('is_connected', False),
        'search_index_built': stats['search_keywords'] > 0
    }
    
    return all(checks.values()), checks
```

### Performance Monitoring

Key metrics to monitor:
- Search response time
- Memory usage of loaded taxonomy
- Database query performance
- Cache hit rates

### Log Analysis

Search for these log patterns:
- `"Taxonomy loaded successfully"` - Successful initialization
- `"Failed to load taxonomy"` - Loading errors
- `"Refreshing subject taxonomy"` - Refresh operations

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify PostgreSQL is running
   - Check connection string format
   - Confirm database exists

2. **No Data Loaded**
   - Run ETL process: `python scripts/load_lcc_taxonomy.py`
   - Check source files in `/Projects/Subjects/source/`
   - Verify file permissions

3. **Search Not Working**
   - Check if search indexes were built
   - Verify vocabulary is in expected format
   - Review search query format

4. **Performance Issues**
   - Add database indexes on frequently queried fields
   - Increase PostgreSQL memory settings
   - Consider taxonomy data size vs. available RAM

### Debug Commands

```bash
# Check database schema
python -c "from lcc_database_schema import LCCDatabaseManager; m=LCCDatabaseManager(); print(m.get_statistics())"

# Validate consolidated data
python -c "import json; data=json.load(open('consolidated_lcc_data.json')); print(f'Records: {len(data)}')"

# Test bundle loading
python -c "from subject_taxonomy_bundle import create_subject_taxonomy_bundle; b=create_subject_taxonomy_bundle(); print(b.statistics)"
```

## Contributing

### Adding New Data Sources

1. Update `lcc_file_parser.py` to handle new file formats
2. Add validation rules for new data patterns
3. Update database schema if needed
4. Add tests for new parsing logic

### Extending Functionality

1. Add new search algorithms in `subject_taxonomy_bundle.py`
2. Implement additional relationship types
3. Add caching mechanisms for better performance
4. Create API endpoints for external access

---

**Last Updated**: September 30, 2025  
**Version**: 2.0  
**Maintainer**: Federated Graph Framework Team