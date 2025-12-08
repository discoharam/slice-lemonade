# Slice Lemonade - RunPod Deployment Script (PowerShell)

param(
    [string]$GitHubUsername,
    [string]$GitHubToken,
    [string]$ImageTag = "latest",
    [switch]$SkipBuild = $false
)

Write-Host "🚀 Slice Lemonade Deployment to RunPod" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Yellow

# Check parameters
if (-not $GitHubUsername -or -not $GitHubToken) {
    Write-Host "❌ Missing GitHub credentials!" -ForegroundColor Red
    Write-Host "Usage: .\deploy_runpod.ps1 -GitHubUsername YOUR_USERNAME -GitHubToken YOUR_TOKEN [-ImageTag TAG] [-SkipBuild]" -ForegroundColor Yellow
    exit 1
}

# Configuration
$RepoName = "slice-lemonade"
$ImageName = "ghcr.io/$GitHubUsername/$RepoName"
$FullImageName = "$ImageName`:$ImageTag"
$RunPodEndpoint = "8y3bd1tz05fj3p"

Write-Host "📦 Repository: $RepoName" -ForegroundColor Gray
Write-Host "🐳 Image: $FullImageName" -ForegroundColor Gray
Write-Host "🎯 RunPod Endpoint: $RunPodEndpoint" -ForegroundColor Gray

# Step 1: Build Docker Image
if (-not $SkipBuild) {
    Write-Host "`n[1] Building Docker image..." -ForegroundColor Green
    
    Set-Location "runpod"
    
    try {
        Write-Host "   Running docker build..." -ForegroundColor Gray
        docker build -t $RepoName:$ImageTag .
        
        if ($LASTEXITCODE -ne 0) {
            throw "Docker build failed"
        }
        
        Write-Host "   ✅ Build successful" -ForegroundColor Green
        
        # Tag for GitHub Container Registry
        Write-Host "   Tagging image..." -ForegroundColor Gray
        docker tag $RepoName:$ImageTag $FullImageName
        
        if ($LASTEXITCODE -ne 0) {
            throw "Docker tag failed"
        }
        
        Write-Host "   ✅ Image tagged" -ForegroundColor Green
        
    } catch {
        Write-Host "   ❌ Build failed: $_" -ForegroundColor Red
        exit 1
    } finally {
        Set-Location ".."
    }
}

# Step 2: Login to GitHub Container Registry
Write-Host "`n[2] Logging in to GitHub Container Registry..." -ForegroundColor Green

try {
    # Create credential file
    $credential = "$GitHubUsername`:$GitHubToken"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($credential)
    $encodedCredential = [Convert]::ToBase64String($bytes)
    
    # Login using credentials
    docker login ghcr.io -u $GitHubUsername --password-stdin <<< $GitHubToken
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker login failed"
    }
    
    Write-Host "   ✅ Logged in successfully" -ForegroundColor Green
    
} catch {
    Write-Host "   ❌ Login failed: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Push to GitHub Container Registry
Write-Host "`n[3] Pushing image to GitHub Container Registry..." -ForegroundColor Green

try {
    Write-Host "   Pushing $FullImageName..." -ForegroundColor Gray
    docker push $FullImageName
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker push failed"
    }
    
    Write-Host "   ✅ Image pushed successfully" -ForegroundColor Green
    
} catch {
    Write-Host "   ❌ Push failed: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Verify Image in GitHub Container Registry
Write-Host "`n[4] Verifying image..." -ForegroundColor Green

try {
    # Get image digest
    $manifest = docker manifest inspect $FullImageName 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Image verified in GHCR" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Image might not be immediately available (wait 1-2 minutes)" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "   ⚠️  Verification failed (might be OK): $_" -ForegroundColor Yellow
}

# Step 5: Update RunPod Template (Manual)
Write-Host "`n[5] Manual RunPod Update Required:" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Go to: https://www.runpod.io/console/serverless" -ForegroundColor Gray
Write-Host "2. Find template for Slice Lemonade" -ForegroundColor Gray
Write-Host "3. Click 'Edit' and update Docker image to:" -ForegroundColor Gray
Write-Host "   $FullImageName" -ForegroundColor Green
Write-Host "4. Save template" -ForegroundColor Gray
Write-Host ""
Write-Host "OR if using existing endpoint:" -ForegroundColor Gray
Write-Host "1. Go to: https://www.runpod.io/console/endpoints" -ForegroundColor Gray
Write-Host "2. Find endpoint: $RunPodEndpoint" -ForegroundColor Gray
Write-Host "3. Click 'Refresh' to deploy new handler" -ForegroundColor Gray
Write-Host ""

# Step 6: Wait and Verify
Write-Host "`n[6] After refresh, wait 3-5 minutes and verify:" -ForegroundColor Cyan
Write-Host "   - All workers show 'Healthy'" -ForegroundColor Gray
Write-Host "   - Version is 'Latest'" -ForegroundColor Gray
Write-Host "   - Test with small audio file" -ForegroundColor Gray
Write-Host ""

# Step 7: Test Endpoint
Write-Host "`n[7] Testing endpoint (optional)..." -ForegroundColor Green

$testScript = @"
# Test the endpoint with PowerShell
`$headers = @{
    "Authorization" = "Bearer YOUR_RUNPOD_API_KEY"
    "Content-Type" = "application/json"
}

`$payload = @{
    input = @{
        test = "echo"
        timestamp = (Get-Date).ToString("o")
    }
} | ConvertTo-Json

`$url = "https://api.runpod.ai/v2/$RunPodEndpoint/run"
try {
    `$response = Invoke-RestMethod -Uri `$url -Method Post -Headers `$headers -Body `$payload
    Write-Host "✅ Endpoint is responding" -ForegroundColor Green
} catch {
    Write-Host "❌ Endpoint test failed" -ForegroundColor Red
}
"@

Write-Host "   Test script saved to: test_endpoint.ps1" -ForegroundColor Gray
$testScript | Out-File -FilePath "test_endpoint.ps1" -Encoding UTF8

# Summary
Write-Host "`n🎉 Deployment Summary:" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Yellow
Write-Host "✅ Image built and pushed: $FullImageName" -ForegroundColor Green
Write-Host "🔑 GitHub: $GitHubUsername" -ForegroundColor Gray
Write-Host "🎯 RunPod Endpoint: $RunPodEndpoint" -ForegroundColor Gray
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Update RunPod template/endpoint with new image" -ForegroundColor Gray
Write-Host "   2. Refresh endpoint and wait for workers" -ForegroundColor Gray
Write-Host "   3. Test with small file first" -ForegroundColor Gray
Write-Host "   4. Monitor logs for 'MP3 COMPRESSED' or multi-format messages" -ForegroundColor Gray
Write-Host ""

Write-Host "🍋 Slice Lemonade deployment complete!" -ForegroundColor Green