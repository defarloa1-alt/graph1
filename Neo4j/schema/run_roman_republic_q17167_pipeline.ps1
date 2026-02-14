param(
    [string]$Python = "python",
    [string]$Uri = $(if ($env:NEO4J_URI) { $env:NEO4J_URI } else { "bolt://127.0.0.1:7687" }),
    [string]$User = $(if ($env:NEO4J_USER) { $env:NEO4J_USER } else { "neo4j" }),
    [string]$Password = $(if ($env:NEO4J_PASSWORD) { $env:NEO4J_PASSWORD } else { "Chrystallum" })
)

$ErrorActionPreference = "Stop"

$schemaDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $schemaDir "run_cypher_file.py"

$orderedFiles = @(
    "16_roman_republic_q17167_reset.cypher",
    "09_core_pipeline_pilot_seed.cypher",
    "11_event_period_claim_seed.cypher",
    "13_claim_label_backfill.cypher",
    "14_claim_promotion_seed.cypher",
    "10_core_pipeline_pilot_verify.cypher",
    "12_event_period_claim_verify.cypher",
    "15_claim_promotion_verify.cypher"
)

foreach ($file in $orderedFiles) {
    $path = Join-Path $schemaDir $file
    Write-Host "Running $file"
    & $Python $runner $path --uri $Uri --user $User --password $Password
    if ($LASTEXITCODE -ne 0) {
        throw "Pipeline failed while running $file (exit code: $LASTEXITCODE)"
    }
}

Write-Host "Roman Republic Q17167 pipeline complete."
