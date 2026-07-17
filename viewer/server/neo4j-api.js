import express from "express";
import cors from "cors";
import neo4j from "neo4j-driver";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.join(__dirname, "../../.env") });

const app = express();
app.use(cors());
app.use(express.json());

// Neo4j connection
let driver;
let session;

try {
  const uri = process.env.NEO4J_URI || "bolt://localhost:7687";
  const user = process.env.NEO4J_USER || "neo4j";
  const password = process.env.NEO4J_PASSWORD || "password";

  console.log(`Connecting to Neo4j at ${uri}...`);
  driver = neo4j.driver(uri, neo4j.auth.basic(user, password));

  // Verify connection
  driver.getServerInfo().then(() => {
    console.log("Neo4j connection established successfully");
  }).catch(err => {
    console.error("Failed to connect to Neo4j:", err.message);
  });
} catch (error) {
  console.error("Error initializing Neo4j driver:", error);
}

// Helper to convert Neo4j types to plain JavaScript
function convertNeo4jValue(value) {
  if (value === null || value === undefined) {
    return value;
  }
  
  // Handle Neo4j Integer
  if (value && typeof value === 'object' && value.constructor && value.constructor.name === 'Integer') {
    return value.toNumber();
  }
  
  // Handle Neo4j Node
  if (value && value.properties) {
    const converted = {};
    Object.keys(value.properties).forEach(key => {
      converted[key] = convertNeo4jValue(value.properties[key]);
    });
    if (value.labels) converted.labels = value.labels;
    if (value.identity) converted.identity = value.identity.toString();
    return converted;
  }
  
  // Handle Neo4j Relationship
  if (value && value.type) {
    return {
      type: value.type,
      properties: value.properties ? convertNeo4jValue(value.properties) : {},
      start: value.start ? value.start.toString() : null,
      end: value.end ? value.end.toString() : null,
    };
  }
  
  // Handle objects recursively
  if (typeof value === 'object' && !Array.isArray(value)) {
    const converted = {};
    Object.keys(value).forEach(key => {
      converted[key] = convertNeo4jValue(value[key]);
    });
    return converted;
  }
  
  // Handle arrays recursively
  if (Array.isArray(value)) {
    return value.map(convertNeo4jValue);
  }
  
  return value;
}

// Helper to execute Cypher query
async function executeQuery(cypher, params = {}) {
  const session = driver.session();
  try {
    const result = await session.run(cypher, params);
    
    // Convert Neo4j result to plain objects
    const records = result.records.map(record => {
      const obj = {};
      record.keys.forEach(key => {
        obj[key] = convertNeo4jValue(record.get(key));
      });
      return obj;
    });

    return {
      records,
      summary: {
        counters: result.summary.counters,
        resultAvailableAfter: result.summary.resultAvailableAfter?.toNumber() || 0,
        resultConsumedAfter: result.summary.resultConsumedAfter?.toNumber() || 0,
      },
    };
  } catch (error) {
    throw error;
  } finally {
    await session.close();
  }
}

// API Routes

// Health check
app.get("/api/health", (req, res) => {
  res.json({ status: "ok", neo4jConnected: !!driver });
});

// Get database stats
app.get("/api/stats", async (req, res) => {
  try {
    const queries = [
      "MATCH (n) RETURN count(n) as totalEntities",
      "MATCH (n) RETURN DISTINCT labels(n)[0] as type, count(*) as count",
    ];

    const [totalResult, typesResult] = await Promise.all(
      queries.map(q => executeQuery(q))
    );

    const stats = {
      totalEntities: totalResult.records[0]?.totalEntities || 0,
      entityTypes: {},
    };

    typesResult.records.forEach(record => {
      if (record.type) {
        stats.entityTypes[record.type] = record.count;
      }
    });

    res.json(stats);
  } catch (error) {
    console.error("Stats query error:", error);
    res.status(500).json({ error: error.message });
  }
});

// Execute arbitrary Cypher query
app.post("/api/query", async (req, res) => {
  try {
    const { cypher, params = {} } = req.body;

    if (!cypher) {
      return res.status(400).json({ error: "Cypher query is required" });
    }

    console.log("Executing query:", cypher);
    console.log("With params:", params);

    const result = await executeQuery(cypher, params);
    res.json(result);
  } catch (error) {
    console.error("Query execution error:", error);
    res.status(500).json({ 
      error: error.message,
      code: error.code 
    });
  }
});

// Search entities by label
app.get("/api/entities/search", async (req, res) => {
  try {
    const { q, type, limit = 50 } = req.query;

    let cypher = "MATCH (n)";
    const params = {};

    if (type && type !== "all") {
      cypher += `:${type}`;
    }

    if (q) {
      cypher += " WHERE n.label CONTAINS $query";
      params.query = q;
    }

    cypher += ` RETURN n LIMIT ${parseInt(limit)}`;

    const result = await executeQuery(cypher, params);
    res.json(result);
  } catch (error) {
    console.error("Search error:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get entity by QID or cipher
app.get("/api/entities/:id", async (req, res) => {
  try {
    const { id } = req.params;
    
    const cypher = `
      MATCH (n)
      WHERE n.qid = $id OR n.entity_cipher = $id
      RETURN n
      LIMIT 1
    `;

    const result = await executeQuery(cypher, { id });
    
    if (result.records.length === 0) {
      return res.status(404).json({ error: "Entity not found" });
    }

    res.json(result.records[0]);
  } catch (error) {
    console.error("Get entity error:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get entity relationships
app.get("/api/entities/:id/relationships", async (req, res) => {
  try {
    const { id } = req.params;
    const { limit = 100 } = req.query;
    
    const cypher = `
      MATCH (n)-[r]-(m)
      WHERE n.qid = $id OR n.entity_cipher = $id
      RETURN type(r) as relType, r, m
      LIMIT ${parseInt(limit)}
    `;

    const result = await executeQuery(cypher, { id });
    res.json(result);
  } catch (error) {
    console.error("Get relationships error:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get recent entities
app.get("/api/entities/recent", async (req, res) => {
  try {
    const { limit = 50, type } = req.query;
    
    let cypher = "MATCH (n";
    if (type && type !== "all") {
      cypher += `:${type}`;
    }
    cypher += `) RETURN n ORDER BY n.created_at DESC LIMIT ${parseInt(limit)}`;

    const result = await executeQuery(cypher);
    res.json(result);
  } catch (error) {
    console.error("Get recent entities error:", error);
    res.status(500).json({ error: error.message });
  }
});

// Graceful shutdown
process.on("SIGINT", async () => {
  console.log("\nShutting down gracefully...");
  if (driver) {
    await driver.close();
  }
  process.exit(0);
});

const PORT = process.env.NEO4J_API_PORT || 3001;

app.listen(PORT, () => {
  console.log(`Neo4j API server running on http://localhost:${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/api/health`);
});
