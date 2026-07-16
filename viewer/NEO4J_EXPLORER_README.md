# Neo4j Graph Explorer

A modern React UI for browsing and searching the Chrystallum knowledge graph stored in Neo4j.

## Features

- **Entity Search**: Search by label, QID, or property content
- **Advanced Filters**: Filter by entity type, federation score, and facets
- **Entity Details**: View comprehensive entity information including all properties
- **Relationship Explorer**: Browse and navigate entity relationships
- **Real-time Stats**: Database statistics and entity counts
- **Direct Wikidata Links**: Quick access to source Wikidata entries

## Architecture

### Frontend (React + Vite)
- Location: `viewer/`
- Main component: `viewer/components/Neo4jExplorer.jsx`
- Port: `http://localhost:5173`

### Backend API (Express + Neo4j Driver)
- Location: `viewer/server/`
- Main file: `viewer/server/neo4j-api.js`
- Port: `http://localhost:3001`

## Setup

### Prerequisites

1. Node.js 18+ installed
2. Neo4j database running (local or Aura)
3. Environment variables configured in `.env` file at project root:

```env
NEO4J_URI=bolt://localhost:7687
# or for Neo4j Aura:
# NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io

NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### Installation

```bash
cd viewer

# Install frontend dependencies
npm install

# Install backend dependencies
cd server
npm install
cd ..
```

## Running the Application

### Option 1: Using the startup script (recommended)

**Windows (PowerShell):**
```powershell
./start-dev.ps1
```

**Mac/Linux:**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

### Option 2: Manual start (two terminals)

**Terminal 1 - Backend API:**
```bash
cd viewer/server
npm start
```

**Terminal 2 - Frontend:**
```bash
cd viewer
npm run dev
```

### Access the application

Open your browser to: `http://localhost:5173`

The Neo4j Explorer tab will be active by default.

## API Endpoints

The backend server provides these endpoints:

- `GET /api/health` - Health check
- `GET /api/stats` - Database statistics
- `POST /api/query` - Execute arbitrary Cypher queries
- `GET /api/entities/search` - Search entities
- `GET /api/entities/:id` - Get entity by QID or cipher
- `GET /api/entities/:id/relationships` - Get entity relationships
- `GET /api/entities/recent` - Get recently added entities

## Usage Guide

### Searching Entities

1. **By Label**: Enter any text to search entity labels (e.g., "Roman Republic")
2. **By QID**: Select "QID" search type and enter exact QID (e.g., "Q17167")
3. **By Property**: Search within property content for specific terms

### Filtering Results

- **Entity Type**: Filter by CONCEPT, PERSON, PLACE, EVENT, PERIOD, or WORK
- **Federation Score**: Use the slider to filter by minimum authority coverage
- **Facet**: Filter by specific 18-facet classification (future feature)

### Viewing Entity Details

Click any entity in the search results to view:
- Full label and description
- Entity type and QID
- Entity cipher (for internal graph navigation)
- Federation score
- All properties in formatted view
- Connected relationships
- Metadata (creation date, status, etc.)

### Exploring Relationships

In the entity detail view, the Relationships section shows:
- Relationship type (e.g., INSTANCE_OF, PART_OF)
- Connected entity label and QID
- Quick "View" button to navigate to connected entities

## Troubleshooting

### Backend Connection Issues

If you see "Failed to connect to Neo4j" errors:

1. Verify Neo4j is running:
   ```bash
   # For local Neo4j
   neo4j status
   ```

2. Check your `.env` file has correct credentials

3. Test connection manually:
   ```bash
   cd viewer/server
   node neo4j-api.js
   ```

### Frontend API Errors

If search returns "Query failed" errors:

1. Ensure the backend server is running on port 3001
2. Check browser console for detailed error messages
3. Verify the Vite proxy is configured correctly in `vite.config.js`

### Empty Results

If searches return no results:

1. Verify entities are imported in Neo4j:
   ```cypher
   MATCH (n) RETURN count(n) as total
   ```

2. Check entity properties match search criteria
3. Try adjusting filters (set Entity Type to "All")

## Development

### Project Structure

```
viewer/
├── components/
│   └── Neo4jExplorer.jsx     # Main React component
├── server/
│   ├── neo4j-api.js           # Express API server
│   └── package.json           # Server dependencies
├── main.jsx                   # React app entry point
├── vite.config.js             # Vite configuration
├── start-dev.ps1              # Windows startup script
├── start-dev.sh               # Mac/Linux startup script
└── package.json               # Frontend dependencies
```

### Adding New Features

1. **New API Endpoints**: Add to `server/neo4j-api.js`
2. **UI Components**: Add to `components/` directory
3. **Cypher Queries**: Modify queries in `Neo4jExplorer.jsx`

### Database Schema

Expected Neo4j node properties:
- `qid`: Wikidata QID (e.g., "Q17167")
- `label`: Human-readable entity name
- `entity_cipher`: Unique content-addressable identifier
- `entity_type`: Entity classification (CONCEPT, PERSON, etc.)
- `entity_id`: Internal entity ID
- `federation_score`: Number of external authority IDs
- `properties_count`: Number of properties
- `property_summary`: Text summary of all properties
- `status`: Processing status (candidate, validated, etc.)
- `description`: Entity description
- `created_at`: Timestamp of import

## Next Steps

Potential enhancements:

1. **Graph Visualization**: Add D3.js or Cytoscape.js for interactive graph visualization
2. **Batch Operations**: Bulk entity approval/rejection
3. **Export Functions**: Export search results to CSV/JSON
4. **Advanced Filters**: Add facet-based filtering
5. **Entity Editing**: UI for updating entity properties
6. **Traversal Visualization**: Show the SCA discovery process visually
7. **Federation Details**: Expand to show all external authority IDs

## Support

For issues or questions:
- Check the main project README at `C:\Projects\Graph1\README.md`
- Review Neo4j import logs in `output/` directory
- Consult `AI_CONTEXT.md` for architectural decisions
