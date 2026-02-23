param(
    [Parameter(Mandatory = $true)][string]$PeriodQid,
    [Parameter(Mandatory = $true)][string]$PeriodLabel,
    [Parameter(Mandatory = $true)][string]$PeriodStart,
    [Parameter(Mandatory = $true)][string]$PeriodEnd,
    [Parameter(Mandatory = $true)][string]$EventQid,
    [Parameter(Mandatory = $true)][string]$EventLabel,
    [Parameter(Mandatory = $true)][string]$EventDate,
    [Parameter(Mandatory = $true)][string]$PlaceQid,
    [Parameter(Mandatory = $true)][string]$PlaceLabel,
    [string]$EventType = "event",
    [string]$PlaceType = "place",
    [string]$ModernCountry = "",
    [string]$Facet = "political",
    [string]$Source = "wikidata",
    [string]$PipelineVersion = "v1.0",
    [string]$AgentVersion = "v1.0",
    [switch]$ResetEntities,
    [switch]$LegacyRomanClean,
    [string]$Python = "python",
    [string]$Uri = $(if ($env:NEO4J_URI) { $env:NEO4J_URI } else { "bolt://127.0.0.1:7687" }),
    [string]$User = $(if ($env:NEO4J_USER) { $env:NEO4J_USER } else { "neo4j" }),
    [string]$Password = $(if ($env:NEO4J_PASSWORD) { $env:NEO4J_PASSWORD } else { "Chrystallum" })
)

$ErrorActionPreference = "Stop"

$schemaDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $schemaDir "run_qid_pipeline.py"

$argsList = @(
    $runner,
    "--period-qid=$PeriodQid",
    "--period-label=$PeriodLabel",
    "--period-start=$PeriodStart",
    "--period-end=$PeriodEnd",
    "--event-qid=$EventQid",
    "--event-label=$EventLabel",
    "--event-date=$EventDate",
    "--event-type=$EventType",
    "--place-qid=$PlaceQid",
    "--place-label=$PlaceLabel",
    "--place-type=$PlaceType",
    "--modern-country=$ModernCountry",
    "--facet=$Facet",
    "--source=$Source",
    "--pipeline-version=$PipelineVersion",
    "--agent-version=$AgentVersion",
    "--uri=$Uri",
    "--user=$User",
    "--password=$Password"
)

if ($ResetEntities) {
    $argsList += "--reset-entities"
}
if ($LegacyRomanClean) {
    $argsList += "--legacy-roman-clean"
}

& $Python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "QID pipeline failed (exit code: $LASTEXITCODE)"
}
