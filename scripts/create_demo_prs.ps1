# Create GitHub pull requests from seeded demo branches.
# Prerequisites: gh CLI authenticated, remote origin configured, branches pushed.
#
# Usage:
#   git push -u origin main
#   git push origin 'pr/*'
#   .\scripts\create_demo_prs.ps1

$ErrorActionPreference = "Stop"
$branches = git branch --list "pr/*" | ForEach-Object { $_.Trim().TrimStart("* ") }

if ($branches.Count -eq 0) {
    Write-Error "No pr/* branches found. Run scripts/seed_pr_branches.py first."
}

foreach ($branch in $branches) {
    $existing = gh pr list --head $branch --json number --jq '.[0].number' 2>$null
    if ($existing) {
        Write-Host "PR already exists for $branch (#$existing)"
        continue
    }

    $title = git log -1 --format=%s $branch
    gh pr create --base main --head $branch --title $title --body @"
Synthetic demo PR for SentinelFlow live-mode evaluation.

Branch: ``$branch``
Ground truth: see ``eval/pr-ground-truth.yaml``
"@
    Write-Host "Created PR for $branch"
}

Write-Host "`nDone. Update eval/pr-ground-truth.yaml pr_number fields:"
Write-Host "  gh pr list --json number,headRefName --jq '.[] | {number, branch: .headRefName}'"
