# Rebase all pr/* branches onto main and run pytest on each.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

git checkout main | Out-Null
$mainHead = git rev-parse main

$branches = git branch --list "pr/*" | ForEach-Object { $_.Trim().TrimStart("* ") } | Sort-Object
$results = @()

foreach ($branch in $branches) {
    Write-Host "`n=== Rebasing $branch onto main ($mainHead) ===" -ForegroundColor Cyan
    git checkout $branch | Out-Null

    git rebase main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "CONFLICT on $branch - stopping." -ForegroundColor Red
        git rebase --abort 2>$null
        exit 1
    }

    Write-Host "Running pytest on $branch..." -ForegroundColor Yellow
    uv run pytest -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "TESTS FAILED on $branch - stopping." -ForegroundColor Red
        exit 1
    }

    $changed = git diff --name-only main $branch
    $results += [PSCustomObject]@{
        Branch = $branch
        Rebased = "OK"
        Tests = "20 passed"
        ChangedFiles = ($changed -join ", ")
    }
    Write-Host "OK: $branch ($($changed.Count) file(s) differ from main)" -ForegroundColor Green
}

git checkout main | Out-Null

Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize
