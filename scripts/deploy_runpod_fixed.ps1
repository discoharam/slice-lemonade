param([string]$GitHubUsername,[string]$GitHubToken,[string]$ImageTag="latest",[switch]$SkipBuild=$false)
Write-Host "🚀 Slice Lemonade RunPod Deployment"-ForegroundColor Cyan
Write-Host "="*40 -ForegroundColor Yellow
if(-not$GitHubUsername-or-not$GitHubToken){
    Write-Host "❌ Missing GitHub credentials!"-ForegroundColor Red
    Write-Host "Usage:.\deploy_runpod_fixed.ps1 -GitHubUsername USER -GitHubToken TOKEN" -ForegroundColor White
    exit 1}
$RepoName="slice-lemonade"
$ImageName="ghcr.io/$GitHubUsername/$RepoName"
$FullImageName="${ImageName}:${ImageTag}"
Write-Host "📦 Config:"-ForegroundColor Green
Write-Host "  Repository: $RepoName"-ForegroundColor Gray
Write-Host "  Image: $FullImageName"-ForegroundColor Gray
Write-Host "  RunPod Endpoint: 8y3bd1tz05fj3p"-ForegroundColor Gray
if(-not$SkipBuild){
    Write-Host "[1] Building Docker image..."-ForegroundColor Green
    Set-Location "runpod"
    try{
        Write-Host "  Building..."-ForegroundColor Gray
        docker build -t "${RepoName}:${ImageTag}" .
        if($LASTEXITCODE-ne0){throw "Docker build failed"}
        Write-Host "  ✅ Build successful"-ForegroundColor Green
        Write-Host "  Tagging..."-ForegroundColor Gray
        docker tag "${RepoName}:${ImageTag}" $FullImageName
        if($LASTEXITCODE-ne0){throw "Docker tag failed"}
        Write-Host "  ✅ Image tagged"-ForegroundColor Green
    }catch{
        Write-Host "  ❌ Build failed: $_"-ForegroundColor Red
        exit 1
    }finally{Set-Location ".."}}
Write-Host "[2] Logging in to GHCR..."-ForegroundColor Green
try{
    $GitHubToken|docker login ghcr.io -u $GitHubUsername --password-stdin
    if($LASTEXITCODE-ne0){throw "Docker login failed"}
    Write-Host "  ✅ Logged in"-ForegroundColor Green
}catch{
    Write-Host "  ❌ Login failed: $_"-ForegroundColor Red
    exit 1}
Write-Host "[3] Pushing to GHCR..."-ForegroundColor Green
try{
    Write-Host "  Pushing $FullImageName..."-ForegroundColor Gray
    docker push $FullImageName
    if($LASTEXITCODE-ne0){throw "Docker push failed"}
    Write-Host "  ✅ Image pushed"-ForegroundColor Green
}catch{
    Write-Host "  ❌ Push failed: $_"-ForegroundColor Red
    exit 1}
Write-Host "[4] Deployment Summary"-ForegroundColor Cyan
Write-Host "="*40 -ForegroundColor Yellow
Write-Host "✅ Image deployed: $FullImageName"-ForegroundColor Green
Write-Host ""
Write-Host "📋 MANUAL UPDATE REQUIRED:"-ForegroundColor Yellow
Write-Host "1. Go to: https://www.runpod.io/console/serverless"-ForegroundColor White
Write-Host "2. Edit Slice Lemonade template"-ForegroundColor White
Write-Host "3. Update Docker image to: $FullImageName"-ForegroundColor Green
Write-Host "4. Save template"-ForegroundColor White
Write-Host "5. Go to: https://www.runpod.io/console/endpoints"-ForegroundColor White
Write-Host "6. Find endpoint: 8y3bd1tz05fj3p"-ForegroundColor White
Write-Host "7. Click 'Refresh' and wait 3-5 minutes"-ForegroundColor White
Write-Host ""
Write-Host "🍋 Deployment script complete! Push to GitHub to trigger auto-build."-ForegroundColor Green