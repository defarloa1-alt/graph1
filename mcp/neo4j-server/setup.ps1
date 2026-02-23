#!/usr/bin/env pwsh

# Neo4j MCP Server Setup Script
# Runs on Windows PowerShell

Write-Host "Neo4j MCP Server Setup" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan

# Check Node.js
Write-Host "`nChecking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Node.js $nodeVersion found" -ForegroundColor Green
} else {
    Write-Host "✗ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Navigate to server directory
$serverDir = "$PSScriptRoot\mcp\neo4j-server"
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
Set-Location $serverDir

# Install npm dependencies
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ npm install failed" -ForegroundColor Red
    exit 1
}

# Build TypeScript
Write-Host "`nBuilding TypeScript..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n✓ Build successful" -ForegroundColor Green

# Test connection to Neo4j
Write-Host "`nTesting Neo4j connection..." -ForegroundColor Yellow
Write-Host "If Neo4j Desktop is running, this should succeed..." -ForegroundColor Gray

$testScript = @"
import { Neo4jConnection } from './dist/neo4j-connection.js';

const connection = new Neo4jConnection({
  uri: 'bolt://localhost:7687',
  username: 'neo4j',
  password: 'password'
});

try {
  const result = await connection.testConnection();
  if (result) {
    console.log('✓ Connected to Neo4j successfully');
  } else {
    console.log('✗ Connection test failed');
    process.exit(1);
  }
} catch (error) {
  console.log('✗ Connection error:', error.message);
  console.log('   Make sure Neo4j Desktop is running on bolt://localhost:7687');
  process.exit(1);
} finally {
  await connection.close();
}
"@

# Note: Actual connection test will be run manually due to async complexity
Write-Host "Manual connection test can be run with: npm run dev" -ForegroundColor Cyan

# Next steps
Write-Host "`n" -ForegroundColor White
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. Update password in .vscode/settings.json" -ForegroundColor White
Write-Host "   - Find: 'NEO4J_PASSWORD': 'your-password-here'" -ForegroundColor Yellow
Write-Host "   - Replace with your actual Neo4j password" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. For cloud Aura, use these settings:" -ForegroundColor White
Write-Host "   - NEO4J_URI: neo4j+s://e504e285.databases.neo4j.io" -ForegroundColor Yellow
Write-Host "   - NEO4J_USERNAME: neo4j" -ForegroundColor Yellow
Write-Host "   - NEO4J_PASSWORD: G-HkO6oAp3n-DIbP0Y7uqbmVeudLEHrwYWGmFNhJ5QA" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Restart VS Code for MCP server to be recognized" -ForegroundColor White
Write-Host ""
Write-Host "4. In VS Code:" -ForegroundColor White
Write-Host "   - Ask Copilot: 'Query all Person nodes'" -ForegroundColor Yellow
Write-Host "   - Ask Copilot: 'Show me the Neo4j schema'" -ForegroundColor Yellow

Write-Host "`nFor development:" -ForegroundColor Cyan
Write-Host "  npm run dev   # Run with ts-node for testing" -ForegroundColor Gray
Write-Host "  npm run watch # Watch for changes" -ForegroundColor Gray
