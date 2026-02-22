# Quick Start: Neo4j MCP in Cursor

## ✅ Status: MCP Server is Built and Ready!

The Neo4j MCP server has been successfully compiled and is ready to use.

---

## 🚀 3-Step Setup

### Step 1: Configure Cursor

Add this configuration to Cursor. Choose **ONE** method:

#### **Method A: Cursor Settings UI** (Easiest)
1. Press `Ctrl+,` (Settings)
2. Search for "mcp"
3. Click "Edit in settings.json"
4. Add the configuration below

#### **Method B: Direct JSON Edit**
1. Press `Ctrl+Shift+P`
2. Type "Preferences: Open User Settings (JSON)"
3. Add the configuration below

#### **Configuration to Add:**

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

**Note:** If you already have other settings, just add the `"mcp.servers"` section to your existing JSON.

---

### Step 2: Restart Cursor

**Important:** You MUST restart Cursor completely for MCP to load:

1. Close ALL Cursor windows
2. Wait 3 seconds
3. Reopen Cursor
4. Wait 10 seconds for MCP initialization

---

### Step 3: Test the Connection

In the Cursor chat, try any of these:

```
@neo4j RETURN 'MCP is working!' AS status
```

Or:

```
Query Neo4j and show me all node labels
```

Or:

```
@neo4j MATCH (n) RETURN labels(n) as type, count(*) as count
```

---

## ✅ Expected Result

If working correctly, you should see:
- The query executes
- Results are displayed
- No connection errors

---

## 🔧 Troubleshooting

### "MCP server neo4j not found"

**Solution:** Make sure you:
1. Added the configuration to Cursor settings (Step 1)
2. Restarted Cursor completely (Step 2)
3. Waited 10 seconds after opening

### "Connection refused to bolt://localhost:7687"

**Solution:** 
1. Open Neo4j Desktop
2. Start your database
3. Verify it's running on port 7687

### "Authentication failed"

**Solution:** Update the password in your MCP configuration:
- Current password in config: `Chrystallum`
- Change it if your Neo4j password is different

---

## 📋 Configuration Reference

### For Local Neo4j Desktop:
```json
"NEO4J_URI": "bolt://localhost:7687",
"NEO4J_USERNAME": "neo4j",
"NEO4J_PASSWORD": "Chrystallum"
```

### For Neo4j Aura Cloud:
```json
"NEO4J_URI": "neo4j+s://e504e285.databases.neo4j.io",
"NEO4J_USERNAME": "neo4j",
"NEO4J_PASSWORD": "G-HkO6oAp3n-DIbP0Y7uqbmVeudLEHrwYWGmFNhJ5QA"
```

---

## 📚 Example Queries

Once connected, try these queries:

### Get database schema
```
@neo4j CALL db.labels()
```

### Count all nodes
```
@neo4j MATCH (n) RETURN count(n) as total_nodes
```

### Find all Person nodes
```
@neo4j MATCH (p:Person) RETURN p.name, p.qid LIMIT 10
```

### Search for places
```
@neo4j MATCH (place:Place) WHERE place.label CONTAINS 'Rome' RETURN place.label, place.pleiades_id
```

### Get temporal periods
```
@neo4j MATCH (period:Period) RETURN period.label, period.start_year, period.end_year ORDER BY period.start_year LIMIT 20
```

---

## 🎯 What This Enables

With MCP configured, you can:
- ✅ Query your knowledge graph directly in chat
- ✅ Ask natural language questions about your data
- ✅ Create/update nodes and relationships
- ✅ Explore schema and data structure
- ✅ Debug Cypher queries interactively

---

## 📁 Files Created

- `mcp/neo4j-server/` - The MCP server (already built)
- `CURSOR_MCP_SETUP.md` - Detailed setup guide
- `CURSOR_MCP_QUICK_START.md` - This file
- `mcp-config.json` - Example configuration
- `test_mcp_connection.bat` - Connection test script

---

**Last Updated:** 2026-02-19  
**Status:** Ready to use!




