Write-Host "SLICE LEMONADE: Pushing Worker Changes" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Yellow

# 1. Clean git lock files
Write-Host "[1/4] Cleaning git lock files..." -ForegroundColor Gray
if (Test-Path .git\index.lock) { Remove-Item .git\index.lock -Force }

# 2. Add files
Write-Host "[2/4] Staging changes..." -ForegroundColor Green
git add .

# 3. Commit
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$msg = "build: Rebuild worker with pre-loaded model - " + $timestamp
Write-Host "[3/4] Committing: $msg" -ForegroundColor Green
git commit -m $msg

# 4. Push
Write-Host "[4/4] Pushing to GitHub..." -ForegroundColor Green
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS: Changes pushed to GitHub." -ForegroundColor Green
    Write-Host "GitHub Actions will now build the new Docker image." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "MANUAL STEPS:" -ForegroundColor Yellow
    Write-Host "1. Go to https://www.runpod.io/console/endpoints"
    Write-Host "2. Click REFRESH on your endpoint"
    Write-Host "3. Wait 5 minutes"
} else {
    Write-Host ""
    Write-Host "ERROR: Git push failed." -ForegroundColor Red
}
