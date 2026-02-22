# Fix UTF-8 encoding artifacts in Markdown files
# Replaces â†' with →

$targetPattern = [char]0xE2 + [char]0x86 + [char]0x92  # â†' (malformed)
$replacement = [char]0x2192  # → (correct arrow)

$files = Get-ChildItem -Path . -Include *.md -Recurse -File
$totalFixed = 0
$filesFixed = 0

Write-Host "Scanning for encoding artifacts (â†' → →)..."
Write-Host ""

foreach ($file in $files) {
    try {
        $content = Get-Content $file.FullName -Raw -Encoding UTF8
        
        if ($content -match [regex]::Escape($targetPattern)) {
            $originalLength = $content.Length
            $newContent = $content -replace [regex]::Escape($targetPattern), $replacement
            
            # Count how many replacements were made
            $replacements = ($content.Length - $newContent.Length) / ($targetPattern.Length - $replacement.ToString().Length)
            
            Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8 -NoNewline
            
            $relativePath = Resolve-Path $file.FullName -Relative
            Write-Host "Fixed $replacements instances in: $relativePath"
            
            $totalFixed += $replacements
            $filesFixed++
        }
    }
    catch {
        Write-Host "Error processing $($file.FullName): $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "Total files fixed: $filesFixed"
Write-Host "Total replacements: $totalFixed"
Write-Host "========================================"
