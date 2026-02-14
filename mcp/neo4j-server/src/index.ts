#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { Neo4jConnection, Neo4jConfig } from "./neo4j-connection.js";

// Configuration from environment variables
const config: Neo4jConfig = {
  uri: process.env.NEO4J_URI || "bolt://localhost:7687",
  username: process.env.NEO4J_USERNAME || "neo4j",
  password: process.env.NEO4J_PASSWORD || "password",
  database: process.env.NEO4J_DATABASE || "neo4j",
};

let connection: Neo4jConnection;

// Initialize Neo4j connection
async function initializeConnection() {
  connection = new Neo4jConnection(config);
  const isConnected = await connection.testConnection();
  if (!isConnected) {
    console.error("Failed to connect to Neo4j");
    process.exit(1);
  }
  console.error("Connected to Neo4j");
}

// Define tools
const tools: Tool[] = [
  {
    name: "run_cypher_query",
    description:
      "Execute a Cypher query against Neo4j (READ-ONLY). Use this to query the graph and retrieve information.",
    inputSchema: {
      type: "object" as const,
      properties: {
        query: {
          type: "string",
          description: "The Cypher query to execute",
        },
        params: {
          type: "object",
          description: "Optional parameters for the Cypher query",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "run_cypher_mutation",
    description:
      "Execute a Cypher mutation against Neo4j (CREATE, UPDATE, DELETE). Use this to modify the graph.",
    inputSchema: {
      type: "object" as const,
      properties: {
        query: {
          type: "string",
          description: "The Cypher mutation to execute",
        },
        params: {
          type: "object",
          description: "Optional parameters for the Cypher mutation",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "get_schema",
    description: "Get the current Neo4j schema including labels, relationship types, and properties.",
    inputSchema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
];

// Create MCP server
const server = new Server(
  {
    name: "neo4j-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {},
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const toolName = (request as any).params.name;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const toolArgs = (request as any).params.arguments || {};

  switch (toolName) {
    case "run_cypher_query": {
      const query = toolArgs.query as string;
      const params = (toolArgs.params || {}) as Record<string, unknown>;
      try {
        const results = await connection.runQuery(query, params);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(results, null, 2),
            },
          ],
        };
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `Error executing query: ${error instanceof Error ? error.message : String(error)}`,
            },
          ],
          isError: true,
        };
      }
    }

    case "run_cypher_mutation": {
      const query = toolArgs.query as string;
      const params = (toolArgs.params || {}) as Record<string, unknown>;
      try {
        const results = await connection.runMutation(query, params);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(results, null, 2),
            },
          ],
        };
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `Error executing mutation: ${error instanceof Error ? error.message : String(error)}`,
            },
          ],
          isError: true,
        };
      }
    }

    case "get_schema": {
      try {
        const labelsResult = await connection.runQuery("CALL db.labels()");
        const rtypeResult = await connection.runQuery("CALL db.relationshipTypes()");
        const schema = {
          labels: labelsResult.map((r) => typeof r === "object" && r !== null && "label" in r ? (r as Record<string, unknown>).label : r),
          relationshipTypes: rtypeResult.map((r) => typeof r === "object" && r !== null && "relationshipType" in r ? (r as Record<string, unknown>).relationshipType : r),
        };
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(schema, null, 2),
            },
          ],
        };
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `Error fetching schema: ${error instanceof Error ? error.message : String(error)}`,
            },
          ],
          isError: true,
        };
      }
    }

    default:
      return {
        content: [
          {
            type: "text",
            text: `Unknown tool: ${toolName}`,
          },
        ],
        isError: true,
      };
  }
});

// Main server startup
async function main() {
  await initializeConnection();

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Neo4j MCP Server running");
}

process.on("SIGINT", async () => {
  console.error("Shutting down...");
  await connection.close();
  process.exit(0);
});

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
