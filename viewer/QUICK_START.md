# Neo4j Graph Explorer - Quick Start

## What We Built

A modern React-based UI for exploring your Chrystallum knowledge graph! The application includes:

- **Search & Filter**: Find entities by label, QID, or property content
- **Entity Details**: View comprehensive information about each entity
- **Relationship Browser**: Explore connections between entities
- **Real-time Stats**: See database statistics at a glance
- **Modern UI**: Clean, responsive interface with intuitive navigation

## Architecture

```
┌─────────────────────────┐
│   React Frontend        │  Port 5173
│   (Vite Dev Server)     │  
└───────────┬─────────────┘
            │ /api/* requests
            ↓
┌─────────────────────────┐
│   Express API Server    │  Port 3001
│   (Neo4j Driver)        │  
└───────────┬─────────────┘
            │ Bolt/Neo4j
            ↓
┌─────────────────────────┐
│   Neo4j Database        │  
│   (Your Aura Instance)  │  
└─────────────────────────┘
```

## Prerequisites

Make sure your `.env` file at the project root has these variables:

```env
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

## Starting the Application

### Simple Method (One Command)

```bash
cd viewer
npm run dev:all
```

This will start both:
- Neo4j API server on http://localhost:3001
- Vite dev server on http://localhost:5173

Then open your browser to: **http://localhost:5173**

The Neo4j Explorer will be the default active tab.

### Manual Method (Two Terminals)

If you prefer to see separate logs:

**Terminal 1:**
```bash
cd viewer
npm run dev:api
```

**Terminal 2:**
```bash
cd viewer
npm run dev
```

## Using the Explorer

### 1. Initial View
When you first load the app, you'll see:
- Search controls in the left sidebar
- Database stats (total entities)
- Filters for entity type and federation score

### 2. Searching

**Search by Label:**
- Default mode
- Type any text (e.g., "Roman", "Republic")
- Shows entities whose labels contain your query

**Search by QID:**
- Select "QID" from dropdown
- Enter exact QID (e.g., "Q17167")
- Returns exact match

**Search by Property:**
- Select "Property Content"
- Search within property values
- Useful for finding entities with specific characteristics

### 3. Filtering

- **Entity Type**: CONCEPT, PERSON, PLACE, EVENT, PERIOD, WORK
- **Federation Score**: Slider from 0-20 (higher = more authority IDs)

### 4. Viewing Details

Click any entity in the search results to see:
- Full name and description
- Wikidata link
- Entity cipher (internal ID)
- All properties
- Connected relationships
- Creation metadata

### 5. Exploring Relationships

In the entity detail view:
- See all connected entities
- Relationship types (INSTANCE_OF, PART_OF, etc.)
- Click "View" to navigate to connected entities

## Example Queries

Try these to test the system:

1. **Find Roman Republic:**
   - Search Type: QID
   - Query: `Q17167`

2. **Find all periods:**
   - Entity Type: PERIOD
   - Click Search (empty query shows recent)

3. **High authority entities:**
   - Min Federation Score: 10+
   - Click Search

## Troubleshooting

### "Failed to connect to Neo4j"
- Check your `.env` file
- Verify Neo4j Aura instance is running
- Test connection: `npm run dev:api` and watch for connection message

### "Query failed"
- Ensure API server is running (port 3001)
- Check browser console for details
- Verify Neo4j has imported entities

### No search results
- Check if entities are imported: Run in Neo4j Browser:
  ```cypher
  MATCH (n) RETURN count(n) as total
  ```
- Try removing filters
- Use empty search to see recent entities

## What's Next?

The UI is fully functional! You can:

1. **Browse your 2,600+ imported entities**
2. **Search and filter by various criteria**
3. **Explore entity relationships**
4. **View comprehensive entity details**

### Future Enhancements

Ideas for expansion:
- Visual graph visualization (D3.js, Cytoscape)
- Batch operations (approve/reject candidates)
- Export functionality (CSV, JSON)
- Entity editing interface
- SCA traversal monitoring
- Federation authority details

## Files Created

```
viewer/
├── components/
│   └── Neo4jExplorer.jsx           # Main React component
├── server/
│   ├── neo4j-api.js                # Express API server
│   └── package.json                # Server dependencies
├── main.jsx                        # Updated with Neo4j Explorer
├── vite.config.js                  # Updated proxy config
├── start-dev.ps1                   # Windows startup script
├── start-dev.sh                    # Mac/Linux startup script
├── NEO4J_EXPLORER_README.md        # Detailed documentation
└── QUICK_START.md                  # This file
```

## Support

For detailed information:
- Full docs: `NEO4J_EXPLORER_README.md`
- Project context: `../AI_CONTEXT.md`
- API reference: Check `server/neo4j-api.js` for all endpoints

Enjoy exploring your knowledge graph! 🚀
