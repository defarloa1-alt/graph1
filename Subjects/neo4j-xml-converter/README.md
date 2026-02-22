# Neo4j XML Converter

This project is designed to convert XML files into Neo4j nodes. It provides a structured way to parse XML data and store it in a Neo4j database.

## Project Structure

```
neo4j-xml-converter
├── src
│   ├── index.ts          # Entry point of the application
│   ├── xml
│   │   └── parser.ts     # XML parsing logic
│   ├── neo4j
│   │   └── writer.ts     # Neo4j database writing logic
│   └── types
│       └── index.ts      # Type definitions
├── package.json          # NPM configuration
├── tsconfig.json         # TypeScript configuration
└── README.md             # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd neo4j-xml-converter
   ```

2. **Install dependencies:**
   ```
   npm install
   ```

3. **Configure Neo4j connection:**
   Update the connection settings in `src/neo4j/writer.ts` to match your Neo4j database credentials.

4. **Run the application:**
   ```
   npm start
   ```

## Usage

- Place your XML files in the designated directory.
- The application will parse the XML files and convert the data into nodes in the Neo4j database.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.