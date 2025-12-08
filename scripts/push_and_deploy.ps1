Write-Host "🚀 Quick GitHub Push & Deploy" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Yellow

# Step 1: Commit changes
Write-Host "[1] Committing changes..." -ForegroundColor Green
git add .
$commitMsg = Read-Host "Commit message (or press Enter for 'Update RunPod worker')"
if ([string]::IsNullOrWhiteSpace($commitMsg)) { $commitMsg = "Update RunPod worker" }
git commit -m $commitMsg

# Step 2: Push to GitHub
Write-Host "[2] Pushing to GitHub..." -ForegroundColor Green
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git push failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Changes pushed to GitHub" -ForegroundColor Green
Write-Host ""
Write-Host "📊 GitHub Actions will automatically:" -ForegroundColor Cyan
Write-Host "1. Build new Docker image" -ForegroundColor White
Write-Host "2. Push to GHCR: ghcr.io/YOUR_USERNAME/slice-lemonade:latest" -ForegroundColor White
Write-Host "3. Update RunPod endpoint (requires manual refresh)" -ForegroundColor White
Write-Host ""
Write-Host "📋 NEXT STEPS (Manual):" -ForegroundColor Yellow
Write-Host "1. Wait 2-3 minutes for build to complete" -ForegroundColor White
Write-Host "2. Go to: https://www.runpod.io/console/serverless" -ForegroundColor White
Write-Host "3. Update template with new image" -ForegroundColor White
Write-Host "4. Refresh endpoint: 8y3bd1tz05fj3p" -ForegroundColor White
Write-Host "5. Wait 3-5 minutes for workers to update" -ForegroundColor White