# PowerShell script to run explore queries against Neo4j
# Usage: .\scripts\run_explore_queries.ps1
# Credentials: set NEO4J_URI / NEO4J_USERNAME / NEO4J_PASSWORD in environment or .env — never hardcode.
Set-Location (Join-Path $PSScriptRoot "..")

$NEO4J_URI = $env:NEO4J_URI
$NEO4J_USER = if ($env:NEO4J_USERNAME) { $env:NEO4J_USERNAME } else { $env:NEO4J_USER }
$NEO4J_PASSWORD = $env:NEO4J_PASSWORD

if (-not $NEO4J_URI -or -not $NEO4J_PASSWORD) {
  Write-Host "Set NEO4J_URI and NEO4J_PASSWORD (and NEO4J_USERNAME) before running." -ForegroundColor Red
  exit 1
}

$queries = Get-Content "Cypher/queries/explore_imported_entities.cypher" -Raw
$queryList = $queries -split ";"

Write-Host "Found $($queryList.Count) queries to execute" -ForegroundColor Green
Write-Host "Note: Run these manually in Neo4j Browser or use Python driver" -ForegroundColor Yellow
Write-Host "`nURI: $NEO4J_URI" -ForegroundColor Cyan
