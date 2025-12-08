# Debug Backend Response Structure
Write-Host "🔍 Debugging Backend Response Structure" -ForegroundColor Cyan

# Simulate a backend response
$mockResponse = @{
    job_id = "test-123"
    status = "completed"
    stems = @{
        vocals = @{
            formats = @{
                mp3 = "/api/download/test-123/vocals?format=mp3"
                wav = "/api/download/test-123/vocals?format=wav"
            }
            primary = "mp3"
        }
        drums = @{
            formats = @{
                mp3 = "/api/download/test-123/drums?format=mp3"
                wav = "/api/download/test-123/drums?format=wav"
            }
            primary = "mp3"
        }
        bass = @{
            formats = @{
                mp3 = "/api/download/test-123/bass?format=mp3"
                wav = "/api/download/test-123/bass?format=wav"
            }
            primary = "mp3"
        }
        other = @{
            formats = @{
                mp3 = "/api/download/test-123/other?format=mp3"
                wav = "/api/download/test-123/other?format=wav"
            }
            primary = "mp3"
        }
    }
    stems_count = 4
    primary_format = "mp3"
    quality = "high"
    note = "Audio separation completed - 4 stems available"
}

Write-Host "✅ Mock response created" -ForegroundColor Green
Write-Host "`n📊 Response Structure:" -ForegroundColor Yellow
Write-Host ($mockResponse | ConvertTo-Json -Depth 4)