Write-Host "🧹 Clean Git & Deploy" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Yellow

# Clean git lock files
Write-Host "[1] Cleaning git lock files..." -ForegroundColor Green
Remove-Item -Force .git\index.lock -ErrorAction SilentlyContinue
Remove-Item -Force .git\HEAD.lock -ErrorAction SilentlyContinue
Remove-Item -Force .git\refs\heads\*.lock -ErrorAction SilentlyContinue

# Check git status
Write-Host "[2] Checking git status..." -ForegroundColor Green
git status

# Add all files
Write-Host "[3] Adding files..." -ForegroundColor Green
git add --all

# Commit with timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$commitMsg = "Update RunPod worker - $timestamp"
Write-Host "[4] Committing: $commitMsg" -ForegroundColor Green
git commit -m "$commitMsg"

# Push to GitHub
Write-Host "[5] Pushing to GitHub..." -ForegroundColor Green
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 GitHub Actions will now:" -ForegroundColor Cyan
    Write-Host "   • Build Docker image from /runpod/" -ForegroundColor White
    Write-Host "   • Push to: ghcr.io/discoharam/slice-lemonade:latest" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Manual RunPod update required:" -ForegroundColor Yellow
    Write-Host "1. Wait ~2 minutes for build" -ForegroundColor Gray
    Write-Host "2. Go to: https://www.runpod.io/console/serverless" -ForegroundColor Gray
    Write-Host "3. Edit 'Slice Lemonade' template" -ForegroundColor Gray
    Write-Host "4. Update Docker image to:" -ForegroundColor Green
    Write-Host "   ghcr.io/discoharam/slice-lemonade:latest" -ForegroundColor Green
    Write-Host "5. Save template" -ForegroundColor Gray
    Write-Host "6. Go to: https://www.runpod.io/console/endpoints" -ForegroundColor Gray
    Write-Host "7. Find endpoint: 8y3bd1tz05fj3p" -ForegroundColor Gray
    Write-Host "8. Click 'Refresh'" -ForegroundColor Gray
    Write-Host "9. Wait 3-5 minutes for workers" -ForegroundColor Gray
} else {
    Write-Host "❌ Git push failed" -ForegroundColor Red
}