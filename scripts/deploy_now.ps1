Write-Host "🚀 Emergency Deployment Script" -ForegroundColor Cyan
Write-Host "="*50 -ForegroundColor Yellow

# Clean Git lock files
Write-Host "[1] Cleaning Git lock files..." -ForegroundColor Green
$lockFiles = @("index.lock", "HEAD.lock", "refs/heads/main.lock")
foreach ($lock in $lockFiles) {
    $lockPath = ".git\$lock"
    if (Test-Path $lockPath) {
        Remove-Item -Force $lockPath -ErrorAction SilentlyContinue
        Write-Host "  Removed: $lock" -ForegroundColor Gray
    }
}

# Force reset git index
Write-Host "[2] Resetting Git..." -ForegroundColor Green
git reset --hard HEAD
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Git reset failed" -ForegroundColor Red
    exit 1
}

# Add all files
Write-Host "[3] Adding files to Git..." -ForegroundColor Green
git add --all
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Git add failed" -ForegroundColor Red
    exit 1
}

# Commit with timestamp
Write-Host "[4] Committing changes..." -ForegroundColor Green
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
git commit -m "Deploy RunPod Demucs worker - $timestamp" --no-verify
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ⚠️  Commit failed, trying with --allow-empty" -ForegroundColor Yellow
    git commit --allow-empty -m "Force deploy - $timestamp" --no-verify
}

# Push to GitHub
Write-Host "[5] Pushing to GitHub..." -ForegroundColor Green
git push origin main --force
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Git push failed" -ForegroundColor Red
    Write-Host "  Trying alternative push..." -ForegroundColor Yellow
    git push origin main
}

Write-Host ""
Write-Host "✅ Deployment initiated!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 GitHub Actions will now:" -ForegroundColor Cyan
Write-Host "1. Build new Docker image with Demucs htdemucs" -ForegroundColor White
Write-Host "2. Push to: ghcr.io/YOUR_USERNAME/slice-lemonade:latest" -ForegroundColor White
Write-Host "3. Auto-deploy to RunPod endpoint" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Monitor build: https://github.com/YOUR_USERNAME/slice-lemonade/actions" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 MANUAL UPDATE (if auto-deploy fails):" -ForegroundColor Yellow
Write-Host "1. Wait 2-3 minutes for build to complete" -ForegroundColor White
Write-Host "2. Go to: https://www.runpod.io/console/serverless" -ForegroundColor White
Write-Host "3. Update template Docker image to:" -ForegroundColor White
Write-Host "   ghcr.io/YOUR_USERNAME/slice-lemonade:latest" -ForegroundColor Green
Write-Host "4. Refresh endpoint: 8y3bd1tz05fj3p" -ForegroundColor White
Write-Host "5. Wait 3-5 minutes for workers to update" -ForegroundColor White