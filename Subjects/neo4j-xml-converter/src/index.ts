import { XmlParser } from './xml/parser';
import { Neo4jWriter } from './neo4j/writer';
import fs from 'fs';
import path from 'path';

const xmlDirectory = path.join(__dirname, 'xml');
const xmlFiles = fs.readdirSync(xmlDirectory).filter(file => file.endsWith('.xml'));

async function main() {
    const parser = new XmlParser();
    const writer = new Neo4jWriter();

    await writer.connect();

    for (const file of xmlFiles) {
        const filePath = path.join(xmlDirectory, file);
        const xmlData = parser.parseXml(filePath);
        const nodeData = parser.extractData(xmlData);
        await writer.writeNode(nodeData);
    }

    console.log('All XML files have been processed and nodes created in Neo4j.');
}

main().catch(error => {
    console.error('Error processing XML files:', error);
});