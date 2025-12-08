Write-Host "SLICE LEMONADE: Pushing Worker Fixes (Persistent Cache)" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Yellow

# 1. Clean git lock files
if (Test-Path .git\index.lock) { Remove-Item .git\index.lock -Force }

# 2. Add files
git add .

# 3. Commit
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$msg = "fix: Move cache to /workspace/models to fix startup crash - " + $timestamp
git commit -m $msg

# 4. Push
Write-Host "Pushing to GitHub..." -ForegroundColor Green
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS: Fixes pushed." -ForegroundColor Green
    Write-Host "1. Monitor GitHub Action" -ForegroundColor Cyan
    Write-Host "2. REFRESH RunPod endpoint when done" -ForegroundColor Yellow
} else {
    Write-Host "ERROR: Git push failed." -ForegroundColor Red
}
