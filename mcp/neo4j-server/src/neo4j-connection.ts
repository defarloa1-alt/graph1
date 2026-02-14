import * as neo4j from "neo4j-driver";

export interface Neo4jConfig {
  uri: string;
  username: string;
  password: string;
  database?: string;
}

export class Neo4jConnection {
  private driver: neo4j.Driver;
  private database: string;

  constructor(config: Neo4jConfig) {
    this.driver = neo4j.driver(config.uri, neo4j.auth.basic(config.username, config.password));
    this.database = config.database || "neo4j";
  }

  async runQuery(cypher: string, params: Record<string, unknown> = {}): Promise<unknown[]> {
    const session = this.driver.session({
      database: this.database,
    });

    try {
      const result = await session.run(cypher, params);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return result.records.map((record: any) => {
        const obj: Record<string, unknown> = {};
        record.keys.forEach((key: string) => {
          obj[key] = this.serializeValue(record.get(key));
        });
        return obj;
      });
    } finally {
      await session.close();
    }
  }

  async runMutation(cypher: string, params: Record<string, unknown> = {}): Promise<unknown[]> {
    const session = this.driver.session({
      database: this.database,
    });

    try {
      const result = await session.run(cypher, params);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return result.records.map((record: any) => {
        const obj: Record<string, unknown> = {};
        record.keys.forEach((key: string) => {
          obj[key] = this.serializeValue(record.get(key));
        });
        return obj;
      });
    } finally {
      await session.close();
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private serializeValue(value: any): unknown {
    if (value === null || value === undefined) {
      return value;
    }

    // Handle Neo4j Node
    if (value.constructor.name === "Node") {
      return {
        _type: "Node",
        id: value.identity.toString(),
        labels: value.labels,
        properties: value.properties,
      };
    }

    // Handle Neo4j Relationship
    if (value.constructor.name === "Relationship") {
      return {
        _type: "Relationship",
        id: value.identity.toString(),
        type: value.type,
        properties: value.properties,
        start: value.start.toString(),
        end: value.end.toString(),
      };
    }

    // Handle Neo4j Path
    if (value.constructor.name === "Path") {
      return {
        _type: "Path",
        start: this.serializeValue(value.start),
        end: this.serializeValue(value.end),
        segments: value.segments.map((seg: unknown) => ({
          start: this.serializeValue(seg),
          relationship: this.serializeValue(
            typeof seg === "object" && seg !== null && "relationship" in seg
              ? (seg as Record<string, unknown>).relationship
              : null
          ),
          end: this.serializeValue(
            typeof seg === "object" && seg !== null && "end" in seg
              ? (seg as Record<string, unknown>).end
              : null
          ),
        })),
      };
    }

    // Handle Neo4j Integer
    if (value.constructor.name === "Integer" || neo4j.isInt(value)) {
      return typeof value.toNumber === "function" ? value.toNumber() : value;
    }

    // Handle arrays
    if (Array.isArray(value)) {
      return value.map((item) => this.serializeValue(item));
    }

    // Handle objects
    if (typeof value === "object") {
      const obj: Record<string, unknown> = {};
      for (const [key, val] of Object.entries(value)) {
        obj[key] = this.serializeValue(val);
      }
      return obj;
    }

    return value;
  }

  async testConnection(): Promise<boolean> {
    try {
      const results = await this.runQuery("RETURN 'Neo4j connected' as status");
      return results.length > 0;
    } catch {
      return false;
    }
  }

  async close(): Promise<void> {
    await this.driver.close();
  }
}
