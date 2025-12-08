Write-Host "SLICE LEMONADE: Pushing Robust Handler Fixes" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Yellow

if (Test-Path .git\index.lock) { Remove-Item .git\index.lock -Force }

git add .

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$msg = "fix: Add lazy loading fallback to handler.py - " + $timestamp
git commit -m $msg

Write-Host "Pushing to GitHub..." -ForegroundColor Green
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS: Handler updated." -ForegroundColor Green
    Write-Host "1. Wait for GitHub Build." -ForegroundColor Cyan
    Write-Host "2. REFRESH RunPod endpoint to apply logic." -ForegroundColor Yellow
} else {
    Write-Host "ERROR: Git push failed." -ForegroundColor Red
}
