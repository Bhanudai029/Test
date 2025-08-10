# Quick PowerShell test commands for Facebook Browser API
# Run these one by one to test your API

Write-Host "Facebook Browser API - Quick Test Commands" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Change this to your actual Render URL when known
$apiUrl = Read-Host "Enter your API URL (e.g., https://facebook-browser-lite.onrender.com)"

if (-not $apiUrl) {
    $apiUrl = "http://localhost:10000"
    Write-Host "Using default: $apiUrl" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Testing API at: $apiUrl" -ForegroundColor Green
Write-Host ""

# Test 1: Health Check
Write-Host "1. Health Check:" -ForegroundColor Yellow
Write-Host "   Command: Invoke-WebRequest -Uri `"$apiUrl/health`" -Method GET" -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "$apiUrl/health" -Method GET -ErrorAction Stop
    Write-Host "   ✅ Health check passed!" -ForegroundColor Green
    $response.Content | ConvertFrom-Json | ConvertTo-Json
} catch {
    Write-Host "   ❌ Health check failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 2: Visit Zuck (GET endpoint)
Write-Host "2. Visit Zuck (GET endpoint):" -ForegroundColor Yellow
Write-Host "   Command: Invoke-WebRequest -Uri `"$apiUrl/api/visit/zuck`" -Method GET" -ForegroundColor Gray
Write-Host "   Press Enter to run this test..." -ForegroundColor Gray
Read-Host
try {
    $response = Invoke-WebRequest -Uri "$apiUrl/api/visit/zuck" -Method GET -TimeoutSec 30 -ErrorAction Stop
    Write-Host "   ✅ Success!" -ForegroundColor Green
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   Initial URL: $($data.initial_url)" -ForegroundColor Cyan
    Write-Host "   Final URL:   $($data.final_url)" -ForegroundColor Cyan
    if ($data.final_url -like "*photo*" -and $data.final_url -like "*fbid*") {
        Write-Host "   🎯 Photo URL detected - API is working!" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 3: Visit Marketplace
Write-Host "3. Visit Marketplace (GET endpoint):" -ForegroundColor Yellow
Write-Host "   Command: Invoke-WebRequest -Uri `"$apiUrl/api/visit/marketplace`" -Method GET" -ForegroundColor Gray
Write-Host "   Press Enter to run this test..." -ForegroundColor Gray
Read-Host
try {
    $response = Invoke-WebRequest -Uri "$apiUrl/api/visit/marketplace" -Method GET -TimeoutSec 30 -ErrorAction Stop
    Write-Host "   ✅ Success!" -ForegroundColor Green
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   Final URL: $($data.final_url)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 4: POST endpoint
Write-Host "4. POST endpoint test:" -ForegroundColor Yellow
$body = @{url = "facebook.com/abestoflife"} | ConvertTo-Json
Write-Host "   Command: Invoke-WebRequest -Uri `"$apiUrl/navigate`" -Method POST -Body `$body -ContentType `"application/json`"" -ForegroundColor Gray
Write-Host "   Press Enter to run this test..." -ForegroundColor Gray
Read-Host
try {
    $response = Invoke-WebRequest -Uri "$apiUrl/navigate" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30 -ErrorAction Stop
    Write-Host "   ✅ POST endpoint works!" -ForegroundColor Green
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   Final URL: $($data.final_url)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Test complete!" -ForegroundColor Green
Write-Host ""
Write-Host "You can also open these URLs in your browser:" -ForegroundColor Yellow
Write-Host "  $apiUrl/" -ForegroundColor Cyan
Write-Host "  $apiUrl/health" -ForegroundColor Cyan
Write-Host "  $apiUrl/api/visit/zuck" -ForegroundColor Cyan
Write-Host "  $apiUrl/api/visit/marketplace" -ForegroundColor Cyan
