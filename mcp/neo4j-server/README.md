# Neo4j MCP Server

Model Context Protocol (MCP) server for Neo4j that enables GitHub Copilot and other MCP clients to query and modify your Chrystallum knowledge graph.

## Features

- **Read Queries**: Execute Cypher `MATCH` queries to retrieve data
- **Mutations**: Execute Cypher `CREATE`, `MERGE`, `SET`, `DELETE` operations
- **Schema Inspection**: Retrieve available labels and relationship types
- **Type Serialization**: Automatic conversion of Neo4j types to JSON

## Setup

### 1. Install Dependencies

```bash
cd mcp/neo4j-server
npm install
```

### 2. Build

```bash
npm run build
```

### 3. Configure VS Code

Add to `.vscode/settings.json`:

```json
{
  "[copilot]": {
    "mcpServers": {
      "neo4j": {
        "command": "node",
        "args": ["C:\\Projects\\Graph1\\mcp\\neo4j-server\\dist\\index.js"],
        "env": {
          "NEO4J_URI": "bolt://localhost:7687",
          "NEO4J_USERNAME": "neo4j",
          "NEO4J_PASSWORD": "your-password",
          "NEO4J_DATABASE": "neo4j"
        }
      }
    }
  }
}
```

Or use environment variables from `Environment/Neo4j-e504e285-Created-2025-12-01.txt` for cloud setup.

## Usage

Once configured, you can ask Copilot:

- "Query all Person nodes"
- "Show me the schema"
- "Find all claims about Caesar"
- "Create a new Event node"

## Environment Variables

- `NEO4J_URI`: Connection URI (default: `bolt://localhost:7687`)
- `NEO4J_USERNAME`: Username (default: `neo4j`)
- `NEO4J_PASSWORD`: Password (required)
- `NEO4J_DATABASE`: Database name (default: `neo4j`)

## Available Tools

### run_cypher_query

Execute a READ-ONLY Cypher query.

```json
{
  "query": "MATCH (n:Person) RETURN n LIMIT 10",
  "params": {}
}
```

### run_cypher_mutation

Execute a Cypher mutation (CREATE, UPDATE, DELETE).

```json
{
  "query": "CREATE (n:SubjectConcept {id: 'test_001'}) RETURN n",
  "params": {}
}
```

### get_schema

Retrieve the current Neo4j schema.

```json
{}
```

## Development

```bash
npm run dev          # Run with ts-node
npm run watch        # Watch for changes
npm run build        # Build TypeScript
```

## Troubleshooting

### Connection refused
- Check if Neo4j Desktop is running
- Verify `NEO4J_URI` is correct (typically `bolt://localhost:7687`)
- Check credentials in config

### Module not found errors
- Run `npm install` in `mcp/neo4j-server/`
- Ensure Node.js >= 18 is installed

### VS Code doesn't see MCP server
- Restart VS Code
- Check `.vscode/settings.json` syntax
- View MCP Server logs in VS Code output panel
