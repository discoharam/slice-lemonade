# Slice Lemonade - RunPod Test Script (PowerShell)
Write-Host "🔧 Testing RunPod Connection..." -ForegroundColor Cyan

cd backend

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "Copy .env.example to .env and add your RunPod API key" -ForegroundColor Yellow
    exit
}

# Load environment variables
$envVars = @{}
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]*)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$key] = $value
        [Environment]::SetEnvironmentVariable($key, $value)
    }
}

$apiKey = $envVars['RUNPOD_API_KEY']
$endpointId = $envVars['RUNPOD_ENDPOINT_ID']

Write-Host "🔑 API Key: $($apiKey.Substring(0, [Math]::Min(10, $apiKey.Length)))..." -ForegroundColor Yellow
Write-Host "📡 Endpoint ID: $endpointId" -ForegroundColor Yellow

if (-not $apiKey -or -not $endpointId) {
    Write-Host "❌ Missing API key or endpoint ID!" -ForegroundColor Red
    exit
}

# Test endpoint connection
try {
    $headers = @{
        "Authorization" = "Bearer $apiKey"
        "Content-Type" = "application/json"
    }
    
    $url = "https://api.runpod.ai/v2/$endpointId"
    Write-Host "🌐 Testing connection to: $url" -ForegroundColor Gray
    
    $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers -TimeoutSec 10
    
    Write-Host "✅ Endpoint is accessible!" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor Gray
    Write-Host "   Workers: $($response.workers.total)" -ForegroundColor Gray
    Write-Host "   Template: $($response.template.docker_image)" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ Connection error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "   HTTP Status: $statusCode" -ForegroundColor Yellow
        
        # Try to read error response
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $errorBody = $reader.ReadToEnd()
            $reader.Close()
            Write-Host "   Error body: $errorBody" -ForegroundColor Yellow
        } catch {
            Write-Host "   Could not read error body" -ForegroundColor Yellow
        }
    }
}

# Test with a small audio file
Write-Host "`n🧪 Testing with actual audio file..." -ForegroundColor Cyan

$testFile = "static/uploads/test_short.wav"
if (-not (Test-Path $testFile)) {
    Write-Host "❌ Test file not found: $testFile" -ForegroundColor Red
    Write-Host "   Create a short test WAV file first" -ForegroundColor Yellow
} else {
    try {
        $audioBytes = [System.IO.File]::ReadAllBytes($testFile)
        $audioBase64 = [Convert]::ToBase64String($audioBytes)
        
        $payload = @{
            input = @{
                audio_data = $audioBase64
                file_name = "test_short.wav"
                quality = "medium"
                output_format = "mp3"
            }
        } | ConvertTo-Json -Depth 10

        $url = "https://api.runpod.ai/v2/$endpointId/run"
        Write-Host "📤 Sending test audio (size: $($audioBytes.Length) bytes)..." -ForegroundColor Gray
        
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $payload -TimeoutSec 30
        
        Write-Host "✅ Test job submitted!" -ForegroundColor Green
        Write-Host "   Job ID: $($response.id)" -ForegroundColor Gray
        
        # Poll for completion
        Write-Host "⏳ Polling for job completion..." -ForegroundColor Yellow
        
        $jobId = $response.id
        $statusUrl = "https://api.runpod.ai/v2/$endpointId/status/$jobId"
        
        $completed = $false
        for ($i = 1; $i -le 20; $i++) {
            Start-Sleep -Seconds 5
            
            try {
                $status = Invoke-RestMethod -Uri $statusUrl -Method Get -Headers $headers -TimeoutSec 10
                Write-Host "   Poll $i : Status = $($status.status)" -ForegroundColor Gray
                
                if ($status.status -eq "COMPLETED") {
                    Write-Host "✅ Job completed!" -ForegroundColor Green
                    
                    # Analyze response structure
                    Write-Host "📦 Response Analysis:" -ForegroundColor Cyan
                    if ($status.output) {
                        Write-Host "   Output type: $($status.output.GetType().Name)" -ForegroundColor Gray
                        if ($status.output -is [PSCustomObject]) {
                            $outputKeys = $status.output.PSObject.Properties.Name
                            Write-Host "   Output keys: $($outputKeys -join ', ')" -ForegroundColor Gray
                            
                            # Check for double nesting
                            if ($outputKeys -contains "output") {
                                Write-Host "   ⚠️  Detected 'output' key in output (double nesting)" -ForegroundColor Yellow
                                $innerKeys = $status.output.output.PSObject.Properties.Name
                                Write-Host "   Inner output keys: $($innerKeys -join ', ')" -ForegroundColor Gray
                            }
                            
                            if ($outputKeys -contains "stems") {
                                Write-Host "   ✅ Found 'stems' key!" -ForegroundColor Green
                                $stemKeys = $status.output.stems.PSObject.Properties.Name
                                Write-Host "   Stem keys: $($stemKeys -join ', ')" -ForegroundColor Gray
                            }
                        }
                    } else {
                        Write-Host "   ❌ No output in response" -ForegroundColor Red
                    }
                    
                    $completed = $true
                    break
                }
                elseif ($status.status -eq "FAILED") {
                    Write-Host "❌ Job failed: $($status.error)" -ForegroundColor Red
                    break
                }
            } catch {
                Write-Host "   Poll error: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
        
        if (-not $completed) {
            Write-Host "❌ Polling timeout after 100 seconds" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "❌ Job test failed: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $statusCode = $_.Exception.Response.StatusCode.value__
            Write-Host "   HTTP Status: $statusCode" -ForegroundColor Yellow
        }
    }
}

Write-Host "`n📋 Summary:" -ForegroundColor Cyan
Write-Host "   1. Check handler returns 'stems' key at top level" -ForegroundColor Gray
Write-Host "   2. Verify no double nesting in response" -ForegroundColor Gray
Write-Host "   3. Ensure response size < 10MB" -ForegroundColor Gray
Write-Host "   4. Test with backend after updating handler" -ForegroundColor Gray