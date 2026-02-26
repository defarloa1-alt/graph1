# Enable Neo4j MCP Server in Cursor

## Method 1: Cursor Settings UI

1. Open Cursor Settings (Ctrl+,)
2. Search for "MCP" or "Model Context Protocol"
3. Click "Edit in settings.json"
4. Add this configuration:

```json
{
  "mcp": {
    "servers": {
      "neo4j": {
        "command": "node",
        "args": ["c:\\Projects\\Graph1\\mcp\\neo4j-server\\dist\\index.js"],
        "env": {
          "NEO4J_URI": "neo4j+s://f7b612a3.databases.neo4j.io",
          "NEO4J_USERNAME": "neo4j",
          "NEO4J_PASSWORD": "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM",
          "NEO4J_DATABASE": "neo4j"
        }
      }
    }
  }
}
```

5. Restart Cursor
6. The MCP server will now be available!

## Method 2: Global Settings File

Create/edit: `%USERPROFILE%\.cursor\mcp_settings.json`

```json
{
  "mcpServers": {
    "neo4j-mcp-server": {
      "command": "node",
      "args": ["c:\\Projects\\Graph1\\mcp\\neo4j-server\\dist\\index.js"],
      "env": {
        "NEO4J_URI": "neo4j+s://f7b612a3.databases.neo4j.io",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM",
        "NEO4J_DATABASE": "neo4j"
      }
    }
  }
}
```

## Verify It's Working

After configuration, in a NEW chat:

1. Type: "What's in my Neo4j database?"
2. The AI should use the `get_schema` and `run_cypher_query` tools
3. You'll see results directly from Neo4j

## Why This Works

- The MCP server acts as a bridge between Cursor AI and Neo4j
- It provides tools: `run_cypher_query`, `run_cypher_mutation`, `get_schema`
- Other chats with this configured can query Neo4j directly
- Once you add this, ALL your chats in this workspace will have Neo4j access

## Security Note

**WARNING:** The password is visible in the config. For production:
1. Use environment variables instead
2. Or store in a secure credential manager
3. Or use `.env` file (not committed to git)
