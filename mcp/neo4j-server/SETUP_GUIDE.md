# Neo4j MCP Server Setup for VS Code / GitHub Copilot

This guide shows how to:
1. Build and configure the Neo4j MCP server
2. Connect it to VS Code / GitHub Copilot
3. Test the connection

## Prerequisites

- **Node.js 18+**: [Download here](https://nodejs.org/)
- **Neo4j Desktop running locally** OR **Neo4j Aura cloud access**
- **VS Code** with GitHub Copilot extension

## Step 1: Build the Server

```bash
cd C:\Projects\Graph1\mcp\neo4j-server
npm install
npm run build
```

Expected output:
```
> neo4j-mcp-server@1.0.0 build
> tsc

(no errors)
```

## Step 2: Update VS Code Configuration

The MCP server is already configured in `.vscode/settings.json`, but you need to set your password.

**For Local Neo4j Desktop:**

1. Open `.vscode/settings.json`
2. Find the section:
   ```json
   "env": {
       "NEO4J_URI": "bolt://localhost:7687",
       "NEO4J_USERNAME": "neo4j",
       "NEO4J_PASSWORD": "your-password-here",
       "NEO4J_DATABASE": "neo4j"
   }
   ```
3. Replace `"your-password-here"` with your actual Neo4j password
4. Save the file

**For Neo4j Aura Cloud:**

1. Open `.vscode/settings.json`
2. Update the env section:
   ```json
   "env": {
       "NEO4J_URI": "neo4j+s://e504e285.databases.neo4j.io",
       "NEO4J_USERNAME": "neo4j",
       "NEO4J_PASSWORD": "G-HkO6oAp3n-DIbP0Y7uqbmVeudLEHrwYWGmFNhJ5QA",
       "NEO4J_DATABASE": "neo4j"
   }
   ```
3. Save the file

## Step 3: Verify the Build

Check that the compiled files exist:

```bash
dir C:\Projects\Graph1\mcp\neo4j-server\dist
```

You should see:
- `dist/index.js`
- `dist/neo4j-connection.js`
- `dist/index.d.ts`
- `dist/neo4j-connection.d.ts`

## Step 4: Restart VS Code

The MCP server won't be loaded until you restart VS Code.

1. Close all VS Code windows
2. Reopen VS Code
3. Wait 5 seconds for initialization

## Step 5: Test with Copilot

In the VS Code chat, ask Copilot:

```
Query the Neo4j database and show me all Person nodes
```

Or:

```
Show me the Neo4j schema
```

You should see the MCP server executing Cypher queries.

## Troubleshooting

### "MCP server didn't respond"

**Causes:**
1. Neo4j is not running (for local setup)
2. Wrong password in settings.json
3. Port 7687 is not accessible
4. Wrong URI in settings

**Fix:**
```bash
# Check if Neo4j is running
netstat -ano | findstr "7687"

# If nothing, start Neo4j Desktop
# If something, check the password in settings.json
```

### "Cannot find module @modelcontextprotocol/sdk"

**Fix:**
```bash
cd C:\Projects\Graph1\mcp\neo4j-server
npm install
npm run build
```

### VS Code doesn't load the MCP server

**Fix:**
1. Check `.vscode/settings.json` syntax (must be valid JSON)
2. Check the command path:
   ```json
   "args": ["C:\\Projects\\Graph1\\mcp\\neo4j-server\\dist\\index.js"]
   ```
3. Restart VS Code completely (close and reopen)
4. Open VS Code output: View → Output → Select "Neo4j MCP Server" dropdown

### Connection refused to localhost:7687

**Fix:**
1. Ensure Neo4j Desktop is running
2. Ensure you're not behind a corporate firewall
3. Check Neo4j Desktop port settings:
   - Open Neo4j Desktop
   - Look for "Bolt" port (should be 7687)
   - If different, update settings.json

## Available Tools

Once connected, Copilot can use these tools:

### 1. run_cypher_query
Execute a READ-ONLY Cypher query

Example:
```
Copilot: "Search for all SubjectConcept nodes with FAST ID 'fst01411640'"
```

### 2. run_cypher_mutation
Execute a CREATE/UPDATE/DELETE mutation

Example:
```
Copilot: "Create a new Person node for Julius Caesar"
```

### 3. get_schema
Retrieve Neo4j labels and relationship types

Example:
```
Copilot: "Show me the Neo4j schema"
```

## Development

If you're modifying the MCP server code:

```bash
cd C:\Projects\Graph1\mcp\neo4j-server

# Watch for changes and rebuild
npm run watch

# Or in another terminal, run in dev mode
npm run dev
```

## Architecture

```
┌─────────────────────────────────────────────┐
│  VS Code + GitHub Copilot                   │
└────────────────────┬────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │ MCP Protocol            │
        │ (stdio transport)        │
        └────────────┬────────────┘
                     │
┌────────────────────▼────────────────────────┐
│  Neo4j MCP Server                           │
│  - Tool definitions                         │
│  - Cypher execution                         │
│  - Type serialization                       │
└────────────────────┬────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │ Neo4j Driver            │
        │ (bolt protocol)         │
        └────────────┬────────────┘
                     │
┌────────────────────▼────────────────────────┐
│  Neo4j Instance                             │
│  - Local: bolt://localhost:7687             │
│  - Cloud: neo4j+s://e504e285.databases...   │
└─────────────────────────────────────────────┘
```

## Next Steps

1. **Commit the MCP server to Git:**
   ```bash
   cd C:\Projects\Graph1
   git add mcp/neo4j-server/
   git commit -m "Add Neo4j MCP server for GitHub Copilot"
   git push
   ```

2. **Update AI_CONTEXT.md** to document MCP is now available:
   ```
   MCP Server: Neo4j MCP server configured for VS Code (2026-02-14)
   Location: mcp/neo4j-server/
   Status: Build complete, awaiting password configuration
   ```

3. **Create MCP prompts** in `md/Agents/` for specialized Cypher queries

4. **Build MCP tools** for common operations:
   - Query specific node types
   - Validate Cypher schemas
   - Generate entity proposals
