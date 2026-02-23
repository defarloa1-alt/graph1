param(
    [string]$Python = "python",
    [string]$Uri = $(if ($env:NEO4J_URI) { $env:NEO4J_URI } else { "bolt://127.0.0.1:7687" }),
    [string]$User = $(if ($env:NEO4J_USER) { $env:NEO4J_USER } else { "neo4j" }),
    [string]$Password = $(if ($env:NEO4J_PASSWORD) { $env:NEO4J_PASSWORD } else { "Chrystallum" })
)

$ErrorActionPreference = "Stop"

$schemaDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $schemaDir "run_qid_pipeline.ps1"

& $runner `
    -PeriodQid "Q17167" `
    -PeriodLabel "Roman Republic" `
    -PeriodStart "-0510" `
    -PeriodEnd "-0027" `
    -EventQid "Q193304" `
    -EventLabel "Battle of Actium" `
    -EventDate "-0031-09-02" `
    -EventType "battle" `
    -PlaceQid "Q41747" `
    -PlaceLabel "Actium" `
    -PlaceType "place" `
    -ModernCountry "Greece" `
    -ResetEntities `
    -LegacyRomanClean `
    -Python $Python `
    -Uri $Uri `
    -User $User `
    -Password $Password

Write-Host "Roman Republic Q17167 pipeline complete."
