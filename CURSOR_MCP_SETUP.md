# Neo4j MCP Server Setup for Cursor IDE

## Status
✅ MCP Server is **built and ready** (compiled at `mcp/neo4j-server/dist/`)

## Configuration for Cursor

Cursor IDE uses MCP (Model Context Protocol) servers differently than VS Code. Here's how to set it up:

### Option 1: User Settings (Recommended)

1. **Open Cursor Settings**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Preferences: Open User Settings (JSON)"
   - Press Enter

2. **Add MCP Configuration**
   Add this to your settings JSON:

```json
{
  "mcp.servers": {
    "neo4j": {
      "command": "node",
      "args": ["C:\\Projects\\Graph1\\mcp\\neo4j-server\\dist\\index.js"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "Chrystallum",
        "NEO4J_DATABASE": "neo4j"
      }
    }
  }
}
```

3. **Restart Cursor**
   - Close all Cursor windows
   - Reopen Cursor
   - Wait 5-10 seconds for MCP initialization

### Option 2: Global MCP Config File

Create/edit this file:
```
%APPDATA%\Cursor\User\mcp-settings.json
```

With the same content as above.

### Option 3: Workspace Settings

Create `.vscode/settings.json` in your project (Cursor reads this too):

```json
{
  "mcp.servers": {
    "neo4j": {
      "command": "node",
      "args": ["C:\\Projects\\Graph1\\mcp\\neo4j-server\\dist\\index.js"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "Chrystallum",
        "NEO4J_DATABASE": "neo4j"
      }
    }
  }
}
```

## Testing the Connection

Once configured and Cursor is restarted, try:

### Method 1: Using @neo4j mention
```
@neo4j RETURN 'MCP is working!' AS status
```

### Method 2: Ask in chat
```
Query the Neo4j database and show me all labels
```

### Method 3: Use the resource list
Run the tool `list_mcp_resources` to see if neo4j appears.

## Available Cypher Queries

Once connected, you can run queries like:

```cypher
// Get schema
CALL db.labels()

// Count nodes by type
MATCH (n) RETURN labels(n) as type, count(*) as count

// Find specific entities
MATCH (p:Person) RETURN p LIMIT 10

// Search places
MATCH (place:Place) WHERE place.label CONTAINS 'Rome' RETURN place
```

## Troubleshooting

### MCP server not loading
1. Check that Node.js is installed: `node --version` (should be 18+)
2. Verify build completed: Check `mcp/neo4j-server/dist/index.js` exists
3. Check Cursor output panel for errors

### Connection refused to Neo4j
1. Ensure Neo4j Desktop is running
2. Check the URI is correct: `bolt://localhost:7687`
3. Verify credentials match your Neo4j instance

### Wrong password error
Update the password in your configuration to match your Neo4j instance.

For **Neo4j Aura Cloud** instead of local:
```json
{
  "NEO4J_URI": "neo4j+s://e504e285.databases.neo4j.io",
  "NEO4J_USERNAME": "neo4j",
  "NEO4J_PASSWORD": "G-HkO6oAp3n-DIbP0Y7uqbmVeudLEHrwYWGmFNhJ5QA",
  "NEO4J_DATABASE": "neo4j"
}
```

## Rebuilding After Changes

If you modify the MCP server source code:

```bash
cd C:\Projects\Graph1\mcp\neo4j-server
npm run build
```

Then restart Cursor.

## Architecture

```
┌─────────────────────────────────────────────┐
│  Cursor IDE                                  │
│  - Chat interface                            │
│  - @neo4j mentions                          │
└────────────────────┬────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │ MCP Protocol (stdio)    │
        └────────────┬────────────┘
                     │
┌────────────────────▼────────────────────────┐
│  Neo4j MCP Server (Node.js)                 │
│  Location: mcp/neo4j-server/dist/index.js  │
│  Tools: query, mutation, schema             │
└────────────────────┬────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │ Neo4j Driver (Bolt)     │
        └────────────┬────────────┘
                     │
┌────────────────────▼────────────────────────┐
│  Neo4j Database                             │
│  URI: bolt://localhost:7687                 │
│  Database: neo4j                            │
│  Password: Chrystallum                      │
└─────────────────────────────────────────────┘
```

## Next Steps

1. Configure MCP in Cursor settings (one of the 3 options above)
2. Restart Cursor completely
3. Test with: `@neo4j RETURN 'MCP is working!' AS status`
4. Start querying your knowledge graph!

---

**Date Created:** 2026-02-19
**Status:** Ready to use - just needs Cursor configuration




