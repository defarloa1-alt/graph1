# Fix UTF-8 encoding artifacts - Simple version
# Replace literal "â†'" with "→"

$files = Get-ChildItem -Path . -Include *.md -Recurse -File | Where-Object { $_.FullName -notmatch '\\\.git\\|\\node_modules\\' }
$filesFixed = 0
$totalReplacements = 0

Write-Host "Scanning for encoding artifacts..."
Write-Host ""

foreach ($file in $files) {
    try {
        $content = Get-Content $file.FullName -Raw -Encoding UTF8
        
        # Check if file contains the artifact
        if ($content.Contains("â†'")) {
            # Count occurrences
            $count = ([regex]::Matches($content, [regex]::Escape("â†'"))).Count
            
            # Replace
            $newContent = $content.Replace("â†'", "→")
            
            # Write back
            Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8 -NoNewline
            
            $relativePath = Resolve-Path $file.FullName -Relative
            Write-Host "Fixed $count instances in: $relativePath"
            
            $filesFixed++
            $totalReplacements += $count
        }
    }
    catch {
        Write-Host "Error processing $($file.FullName): $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "Files fixed: $filesFixed"
Write-Host "Total replacements: $totalReplacements"
Write-Host "========================================"
