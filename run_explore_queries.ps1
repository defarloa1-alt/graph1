# PowerShell script to run explore queries against Neo4j
# Usage: .\run_explore_queries.ps1

$NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
$NEO4J_USER = "neo4j"
$NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

# Read the Cypher file
$queries = Get-Content "explore_imported_entities.cypher" -Raw

# Split by semicolons (each query ends with ;)
$queryList = $queries -split ";"

Write-Host "Found $($queryList.Count) queries to execute" -ForegroundColor Green
Write-Host "Note: Run these manually in Neo4j Browser or use Python driver" -ForegroundColor Yellow
Write-Host "`nNeo4j Browser URL: https://f7b612a3.databases.neo4j.io:7473/browser/" -ForegroundColor Cyan
