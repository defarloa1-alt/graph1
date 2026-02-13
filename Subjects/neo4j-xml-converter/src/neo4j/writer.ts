import { Driver, Session } from 'neo4j-driver';
import { NodeData } from '../types';

export class Neo4jWriter {
    private driver: Driver | null = null;
    private session: Session | null = null;

    constructor(private uri: string, private user: string, private password: string) {}

    public async connect(): Promise<void> {
        this.driver = Driver.create(this.uri, { auth: { username: this.user, password: this.password } });
        this.session = this.driver.session();
    }

    public async writeNode(data: NodeData): Promise<void> {
        if (!this.session) {
            throw new Error('Session is not established. Call connect() first.');
        }

        const query = `
            CREATE (n:Node {id: $id, name: $name, type: $type})
        `;

        await this.session.run(query, {
            id: data.id,
            name: data.name,
            type: data.type,
        });
    }

    public async close(): Promise<void> {
        if (this.session) {
            await this.session.close();
        }
        if (this.driver) {
            await this.driver.close();
        }
    }
}