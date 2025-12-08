# Slice Lemonade - Secure Deployment Script for GitHub Container Registry

param(
    [string]$GitHubUsername,
    [string]$GitHubToken,
    [string]$ImageTag = "latest",
    [switch]$SkipBuild = $false,
    [switch]$SkipSecurityCheck = $false
)

Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "🚀 Slice Lemonade SECURE Deployment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host ""

# Security check function
function Test-Security {
    Write-Host "🔒 SECURITY CHECKS:" -ForegroundColor Cyan
    
    # Check for exposed API keys in backend
    $backendEnv = "backend/.env"
    if (Test-Path $backendEnv) {
        $content = Get-Content $backendEnv -Raw
        $patterns = @(
            @{Pattern = "RUNPOD_API_KEY=rpa_"; Message = "⚠️  Backend .env contains hardcoded RunPod API key!"},
            @{Pattern = "RUNPOD_API_KEY=your_runpod_api_key_here"; Message = "❌ Backend .env has placeholder API key!"},
            @{Pattern = "SECRET_KEY=generate_a_secure_random_key_here"; Message = "❌ Backend .env has placeholder SECRET_KEY!"}
        )
        
        foreach ($pattern in $patterns) {
            if ($content -match $pattern.Pattern) {
                Write-Host $pattern.Message -ForegroundColor Red
                return $false
            }
        }
        
        Write-Host "✅ Backend .env looks secure" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Backend .env file not found" -ForegroundColor Yellow
    }
    
    # Check for duplicate static directory
    if (Test-Path "backend/static") {
        Write-Host "⚠️  Duplicate static directory found at backend/static" -ForegroundColor Yellow
        Write-Host "   Consider removing with: Remove-Item -Recurse -Force backend/static" -ForegroundColor Gray
    }
    
    Write-Host ""
    return $true
}

# Check parameters
if (-not $GitHubUsername -or -not $GitHubToken) {
    Write-Host "❌ Missing GitHub credentials!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\deploy_ghcr.ps1 -GitHubUsername YOUR_USERNAME -GitHubToken YOUR_TOKEN" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  [-ImageTag TAG]    Default: latest" -ForegroundColor White
    Write-Host "  [-SkipBuild]       Skip Docker build" -ForegroundColor White
    Write-Host "  [-SkipSecurityCheck] Skip security checks" -ForegroundColor White
    exit 1
}

# Run security checks
if (-not $SkipSecurityCheck) {
    if (-not (Test-Security)) {
        Write-Host ""
        Write-Host "❌ SECURITY CHECKS FAILED!" -ForegroundColor Red
        Write-Host "Please fix security issues before deployment." -ForegroundColor Yellow
        Write-Host "Use -SkipSecurityCheck to bypass (not recommended)" -ForegroundColor Red
        exit 1
    }
}

# Configuration
$RepoName = "slice-lemonade"
$ImageName = "ghcr.io/$GitHubUsername/$RepoName"
$FullImageName = "${ImageName}:${ImageTag}"
$RunPodEndpoint = "8y3bd1tz05fj3p"

Write-Host "📦 Configuration:" -ForegroundColor Green
Write-Host "  Repository:    $RepoName" -ForegroundColor Gray
Write-Host "  Image:         $FullImageName" -ForegroundColor Gray
Write-Host "  RunPod Endpoint: $RunPodEndpoint" -ForegroundColor Gray
Write-Host ""

# Step 1: Build Docker Image
if (-not $SkipBuild) {
    Write-Host "[1] Building Docker image..." -ForegroundColor Green
    
    Set-Location "runpod"
    
    try {
        Write-Host "  Running docker build..." -ForegroundColor Gray
        docker build -t "${RepoName}:${ImageTag}" .
        
        if ($LASTEXITCODE -ne 0) {
            throw "Docker build failed"
        }
        
        Write-Host "  ✅ Build successful" -ForegroundColor Green
        
        # Tag for GitHub Container Registry
        Write-Host "  Tagging image..." -ForegroundColor Gray
        docker tag "${RepoName}:${ImageTag}" $FullImageName
        
        if ($LASTEXITCODE -ne 0) {
            throw "Docker tag failed"
        }
        
        Write-Host "  ✅ Image tagged" -ForegroundColor Green
        
    } catch {
        Write-Host "  ❌ Build failed: $_" -ForegroundColor Red
        exit 1
    } finally {
        Set-Location ".."
    }
}

# Step 2: Login to GitHub Container Registry
Write-Host ""
Write-Host "[2] Logging in to GitHub Container Registry..." -ForegroundColor Green

try {
    # Login using echo (PowerShell compatible)
    $GitHubToken | docker login ghcr.io -u $GitHubUsername --password-stdin
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker login failed"
    }
    
    Write-Host "  ✅ Logged in successfully" -ForegroundColor Green
    
} catch {
    Write-Host "  ❌ Login failed: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Push to GitHub Container Registry
Write-Host ""
Write-Host "[3] Pushing image to GitHub Container Registry..." -ForegroundColor Green

try {
    Write-Host "  Pushing ${FullImageName}..." -ForegroundColor Gray
    docker push $FullImageName
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker push failed"
    }
    
    Write-Host "  ✅ Image pushed successfully" -ForegroundColor Green
    
} catch {
    Write-Host "  ❌ Push failed: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Verify Image
Write-Host ""
Write-Host "[4] Verifying image..." -ForegroundColor Green

try {
    # Try to inspect the manifest
    docker manifest inspect $FullImageName 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Image verified in GHCR" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Image might not be immediately available (wait 1-2 minutes)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠️  Verification failed (might be OK): $_" -ForegroundColor Yellow
}

# Step 5: Manual RunPod Update Instructions
Write-Host ""
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "[5] MANUAL RUNPOD UPDATE REQUIRED" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option A - Update Template:" -ForegroundColor White
Write-Host "  1. Go to: https://www.runpod.io/console/serverless" -ForegroundColor Gray
Write-Host "  2. Find template for Slice Lemonade" -ForegroundColor Gray
Write-Host "  3. Click 'Edit' and update Docker image to:" -ForegroundColor Gray
Write-Host "     $FullImageName" -ForegroundColor Green
Write-Host "  4. Save template" -ForegroundColor Gray
Write-Host ""
Write-Host "Option B - Refresh Existing Endpoint:" -ForegroundColor White
Write-Host "  1. Go to: https://www.runpod.io/console/endpoints" -ForegroundColor Gray
Write-Host "  2. Find endpoint: $RunPodEndpoint" -ForegroundColor Gray
Write-Host "  3. Click 'Refresh' to deploy new handler" -ForegroundColor Gray
Write-Host ""
Write-Host "Wait 3-5 minutes after refresh for workers to update." -ForegroundColor Yellow

# Step 6: Create Updated Test Script
Write-Host ""
Write-Host "[6] Creating updated test script..." -ForegroundColor Green

$testScriptContent = @'
# Test RunPod Endpoint Connection
$headers = @{
    "Authorization" = "Bearer YOUR_RUNPOD_API_KEY_HERE"  # ⚠️ Replace with your key
    "Content-Type" = "application/json"
}

$payload = @{
    input = @{
        audio_data = "dGVzdCBhdWRpbyBkYXRh"  # "test audio data" in base64
        file_name = "test.wav"
        quality = "high"
        output_format = "mp3"
    }
} | ConvertTo-Json

$url = "https://api.runpod.ai/v2/8y3bd1tz05fj3p/run"

try {
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $payload
    Write-Host "✅ Endpoint is responding" -ForegroundColor Green
    Write-Host "   Job ID: $($response.id)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📊 To check status:" -ForegroundColor Cyan
    Write-Host "   Get: https://api.runpod.ai/v2/8y3bd1tz05fj3p/status/$($response.id)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Endpoint test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test backend locally
Write-Host ""
Write-Host "🔧 Testing backend locally:" -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method Get
    Write-Host "✅ Backend is healthy: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend health check failed" -ForegroundColor Red
}
'@

$testScriptContent | Out-File -FilePath "test_deployment.ps1" -Encoding UTF8
Write-Host "  ✅ Test script created: test_deployment.ps1" -ForegroundColor Green

# Create cleanup script
Write-Host ""
Write-Host "[7] Creating cleanup script..." -ForegroundColor Green

$cleanupContent = @'
# Cleanup old files (dry run)
python backend/cleanup.py --dry-run

# To actually cleanup:
# python backend/cleanup.py --max-age 24 --max-files 50
'@

$cleanupContent | Out-File -FilePath "run_cleanup.ps1" -Encoding UTF8
Write-Host "  ✅ Cleanup script created: run_cleanup.ps1" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "🎉 SECURE DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ Image: $FullImageName" -ForegroundColor Green
Write-Host "🔑 GitHub: $GitHubUsername" -ForegroundColor Gray
Write-Host "🎯 RunPod Endpoint: $RunPodEndpoint" -ForegroundColor Gray
Write-Host ""
Write-Host "📋 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "  1. Update backend/.env with new secure keys" -ForegroundColor Gray
Write-Host "  2. Update RunPod template/endpoint with new image" -ForegroundColor Gray
Write-Host "  3. Refresh endpoint and wait for workers" -ForegroundColor Gray
Write-Host "  4. Test with small file first" -ForegroundColor Gray
Write-Host "  5. Run cleanup periodically: .\run_cleanup.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "🔒 SECURITY REMINDERS:" -ForegroundColor Yellow
Write-Host "  • Rotate exposed API key immediately" -ForegroundColor Red
Write-Host "  • Never commit .env files to Git" -ForegroundColor Red
Write-Host "  • Use environment variables in production" -ForegroundColor Red
Write-Host ""
Write-Host "🍋 Slice Lemonade deployment complete!" -ForegroundColor Green