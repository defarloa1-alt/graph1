# SubjectConcept QID-Canonical Migration Runner
# Run AFTER Step 1 (migrate_subject_concepts_to_qid_canonical.cypher) in Neo4j Browser
#
# Usage:
#   .\run_subj_rr_migration.ps1           # Steps 2 + 3 (load + cluster_assignment)
#   .\run_subj_rr_migration.ps1 -DryRun   # Dry run only
#   .\run_subj_rr_migration.ps1 -Cypher    # Generate Cypher files, no Neo4j write

param(
    [switch]$DryRun,
    [switch]$Cypher
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

Push-Location $ProjectRoot

Write-Host ""
Write-Host "=============================================="
Write-Host " SUBJ_RR MIGRATION - Steps 2 & 3"
Write-Host "=============================================="
Write-Host " Prerequisite: Step 1 (migrate Cypher) run in Neo4j Browser"
Write-Host ""

# Step 2: Load SubjectConcepts
Write-Host "[Step 2] Load QID-canonical SubjectConcepts..."
if ($Cypher) {
    python scripts/backbone/subject/load_subject_concepts_qid_canonical.py --cypher
} elseif ($DryRun) {
    python scripts/backbone/subject/load_subject_concepts_qid_canonical.py --dry-run
} else {
    python scripts/backbone/subject/load_subject_concepts_qid_canonical.py
}
if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }
Write-Host ""

# Step 3: Cluster assignment
Write-Host "[Step 3] Cluster assignment (Entity -> SubjectConcept edges)..."
$clusterArgs = @("-d", "output/backlinks", "-s", "output/backlinks/harvest_run_summary.json", "-o", "output/cluster_assignment")
if ($Cypher) { $clusterArgs += "--cypher" }
elseif ($DryRun) { $clusterArgs += "--dry-run" }
else { $clusterArgs += "--write" }
& python scripts/backbone/subject/cluster_assignment.py @clusterArgs
if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }

Write-Host ""
Write-Host "=============================================="
Write-Host " SUBJ_RR MIGRATION COMPLETE"
Write-Host "=============================================="
Write-Host " Run verification queries in Neo4j Browser (see docs/SUBJ_RR_MIGRATION_RUNBOOK.md)"
Write-Host ""

Pop-Location
