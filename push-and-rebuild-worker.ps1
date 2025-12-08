Write-Host "SLICE LEMONADE: Pushing Worker Fixes" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Yellow

# 1. Clean git lock files
if (Test-Path .git\index.lock) { Remove-Item .git\index.lock -Force }

# 2. Add files
git add .

# 3. Commit
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$msg = "fix: Update download_model.py with correct Demucs API - " + $timestamp
git commit -m $msg

# 4. Push
Write-Host "Pushing to GitHub..." -ForegroundColor Green
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS: Fixes pushed." -ForegroundColor Green
    Write-Host "Please monitor the GitHub Action for build success." -ForegroundColor Cyan
    Write-Host "Once built, REFRESH your RunPod endpoint." -ForegroundColor Yellow
} else {
    Write-Host "ERROR: Git push failed." -ForegroundColor Red
}
