# Setup Neo4j MCP Server Environment Variables
# Run this before starting Cursor

$env:NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
$env:NEO4J_USERNAME = "neo4j"
$env:NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"
$env:NEO4J_DATABASE = "neo4j"

Write-Host "✅ Environment variables set!" -ForegroundColor Green
Write-Host "NEO4J_URI: $env:NEO4J_URI" -ForegroundColor Cyan

# Test the MCP server
Write-Host "`nTesting MCP server..." -ForegroundColor Yellow
cd "c:\Projects\Graph1\mcp\neo4j-server"
npm run start
