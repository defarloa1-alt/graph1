# PowerShell script to start both the Neo4j API server and Vite dev server

Write-Host "Starting Neo4j Graph Explorer..." -ForegroundColor Green
Write-Host ""

# Check if server dependencies are installed
if (-not (Test-Path "server/node_modules")) {
    Write-Host "Installing server dependencies..." -ForegroundColor Yellow
    Set-Location server
    npm install
    Set-Location ..
}

# Check if viewer dependencies are installed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing viewer dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host ""
Write-Host "Starting servers..." -ForegroundColor Green
Write-Host "  - Neo4j API: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  - Vite Dev:  http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
Write-Host ""

# Start both servers
$apiServer = Start-Process -FilePath "node" -ArgumentList "server/neo4j-api.js" -PassThru -NoNewWindow
$viteServer = Start-Process -FilePath "npm" -ArgumentList "run dev" -PassThru -NoNewWindow

# Wait for Ctrl+C
try {
    while ($true) {
        Start-Sleep -Seconds 1
        if ($apiServer.HasExited -or $viteServer.HasExited) {
            Write-Host "One of the servers stopped unexpectedly" -ForegroundColor Red
            break
        }
    }
}
finally {
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    Stop-Process -Id $apiServer.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $viteServer.Id -Force -ErrorAction SilentlyContinue
}
