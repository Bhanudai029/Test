#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Facebook Browser Navigation Tool
.DESCRIPTION
    Navigate to any URL using the browser automation API with ESC + 7xTAB + ENTER sequence
.EXAMPLE
    .\navigate-url.ps1
    Interactive mode - prompts for URL input
.EXAMPLE
    .\navigate-url.ps1 -Url "facebook.com/zuck"
    Direct navigation with URL parameter
.EXAMPLE
    .\navigate-url.ps1 -ApiUrl "http://localhost:10000"
    Use a different API server
#>

param(
    [Parameter(Position=0)]
    [string]$Url = "",
    
    [Parameter()]
    [string]$ApiUrl = "",
    
    [Parameter()]
    [switch]$Loop = $false,
    
    [Parameter()]
    [switch]$Help = $false
)

# Show help if requested
if ($Help) {
    Write-Host @"

Facebook Browser Navigation Tool
=================================

This tool navigates to any URL and performs the following key sequence:
  1. Press ESC (to close popups)
  2. Press TAB 7 times (to navigate to target element)
  3. Press ENTER (to activate the element)

Usage:
------
  .\navigate-url.ps1                    # Interactive mode
  .\navigate-url.ps1 "facebook.com/zuck" # Direct navigation
  .\navigate-url.ps1 -Loop              # Continuous mode
  
Parameters:
-----------
  -Url <string>     : URL to navigate to
  -ApiUrl <string>  : API server URL (default: auto-detect)
  -Loop             : Keep running for multiple URLs
  -Help             : Show this help message

Examples:
---------
  .\navigate-url.ps1 "facebook.com/marketplace"
  .\navigate-url.ps1 -ApiUrl "http://localhost:10000"
  .\navigate-url.ps1 -Loop

"@
    exit 0
}

# Function to display banner
function Show-Banner {
    Clear-Host
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         🌐 BROWSER NAVIGATION AUTOMATION TOOL 🌐            ║" -ForegroundColor Cyan
    Write-Host "║                                                              ║" -ForegroundColor Cyan
    Write-Host "║  Performs: ESC → TAB×7 → ENTER on any URL                   ║" -ForegroundColor Yellow
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

# Function to find API server
function Find-ApiServer {
    param([string]$PreferredUrl = "")
    
    if ($PreferredUrl) {
        Write-Host "Using specified API server: $PreferredUrl" -ForegroundColor Green
        return $PreferredUrl
    }
    
    Write-Host "🔍 Auto-detecting API server..." -ForegroundColor Yellow
    
    $serversToTry = @(
        "http://localhost:10000",
        "https://testingappbye.onrender.com",
        "https://facebook-browser-lite.onrender.com",
        "https://facebook-victory-14.onrender.com"
    )
    
    foreach ($server in $serversToTry) {
        Write-Host "  Checking $server..." -NoNewline
        try {
            $response = Invoke-RestMethod -Uri "$server/health" -Method Get -TimeoutSec 3 -ErrorAction Stop
            if ($response.status -eq "healthy") {
                Write-Host " ✅" -ForegroundColor Green
                Write-Host "Connected to: $server" -ForegroundColor Green
                return $server
            }
        }
        catch {
            Write-Host " ❌" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "⚠️  No API server found!" -ForegroundColor Red
    Write-Host "Please ensure the API is running:" -ForegroundColor Yellow
    Write-Host "  python app.py" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Function to format time
function Format-Time {
    param([double]$Seconds)
    
    if ($Seconds -lt 1) {
        return "{0:N0}ms" -f ($Seconds * 1000)
    }
    elseif ($Seconds -lt 60) {
        return "{0:N2}s" -f $Seconds
    }
    else {
        $minutes = [Math]::Floor($Seconds / 60)
        $remainingSeconds = $Seconds % 60
        return "{0}m {1:N1}s" -f $minutes, $remainingSeconds
    }
}

# Function to navigate to URL with dynamic timer
function Navigate-ToUrl {
    param(
        [string]$TargetUrl,
        [string]$ApiServer
    )
    
    # Validate URL
    if ([string]::IsNullOrWhiteSpace($TargetUrl)) {
        Write-Host "❌ URL cannot be empty!" -ForegroundColor Red
        return $null
    }
    
    # Prepare the request
    $body = @{
        url = $TargetUrl
    } | ConvertTo-Json
    
    Write-Host ""
    Write-Host "📍 Target URL: $TargetUrl" -ForegroundColor Cyan
    Write-Host "🚀 Starting navigation..." -ForegroundColor Yellow
    Write-Host ""
    
    # Start timer
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $timerJob = $null
    
    try {
        # Start background timer display
        $timerJob = Start-Job -ScriptBlock {
            param($StartTime)
            while ($true) {
                $elapsed = (Get-Date) - $StartTime
                $seconds = [Math]::Floor($elapsed.TotalSeconds)
                Write-Progress -Activity "Navigating" -Status "Time elapsed: $seconds seconds" -PercentComplete -1
                Start-Sleep -Milliseconds 500
            }
        } -ArgumentList (Get-Date)
        
        # Show dynamic timer
        $startTime = Get-Date
        $timerRunning = $true
        
        # Make the API request in a separate runspace to allow timer updates
        $powerShell = [powershell]::Create()
        $powerShell.AddScript({
            param($ApiServer, $Body)
            Invoke-RestMethod -Uri "$ApiServer/navigate" -Method Post -Body $Body -ContentType "application/json" -TimeoutSec 60
        }).AddArgument($ApiServer).AddArgument($body)
        
        $handle = $powerShell.BeginInvoke()
        
        # Display timer while waiting
        while (-not $handle.IsCompleted) {
            $elapsed = (Get-Date) - $startTime
            $seconds = [Math]::Floor($elapsed.TotalSeconds)
            Write-Host "`r   ⏳ Navigating... ($seconds`s)" -NoNewline -ForegroundColor Yellow
            Start-Sleep -Milliseconds 100
        }
        
        # Get the result
        $response = $powerShell.EndInvoke($handle)
        $powerShell.Dispose()
        
        $stopwatch.Stop()
        $totalTime = Format-Time -Seconds ($stopwatch.ElapsedMilliseconds / 1000)
        
        # Clear the timer line
        Write-Host "`r                                                  `r" -NoNewline
        
        if ($response.success) {
            Write-Host "✅ Navigation successful! (Time: $totalTime)" -ForegroundColor Green
            Write-Host ""
            Write-Host "📊 Results:" -ForegroundColor Cyan
            Write-Host "─────────────────────────────────────────────────" -ForegroundColor DarkGray
            Write-Host "  🔗 Initial URL: " -NoNewline -ForegroundColor Yellow
            Write-Host $response.initial_url
            Write-Host "  🎯 Final URL:   " -NoNewline -ForegroundColor Green
            Write-Host $response.final_url -ForegroundColor Cyan
            
            if ($response.page_title) {
                Write-Host "  📄 Page Title:  " -NoNewline -ForegroundColor Yellow
                Write-Host $response.page_title
            }
            
            # Check if it's a photo URL
            if ($response.final_url -match "photo" -and $response.final_url -match "fbid") {
                Write-Host ""
                Write-Host "  📸 Photo URL detected!" -ForegroundColor Magenta
            }
            
            Write-Host "─────────────────────────────────────────────────" -ForegroundColor DarkGray
            
            # Copy to clipboard if available
            try {
                Set-Clipboard -Value $response.final_url -ErrorAction SilentlyContinue
                Write-Host ""
                Write-Host "📋 Final URL copied to clipboard!" -ForegroundColor Green
            }
            catch {
                # Clipboard not available
            }
            
            return $response
        }
        else {
            Write-Host "❌ Navigation failed! (Time: $totalTime)" -ForegroundColor Red
            if ($response.error) {
                Write-Host "   Error: $($response.error)" -ForegroundColor Red
            }
            return $null
        }
    }
    catch {
        $stopwatch.Stop()
        $totalTime = Format-Time -Seconds ($stopwatch.ElapsedMilliseconds / 1000)
        Write-Host "`r                                                  `r" -NoNewline
        Write-Host "❌ Error during navigation! (Time: $totalTime)" -ForegroundColor Red
        Write-Host "   Error: $_" -ForegroundColor Red
        return $null
    }
    finally {
        # Clean up timer job
        if ($timerJob) {
            Stop-Job -Job $timerJob -ErrorAction SilentlyContinue
            Remove-Job -Job $timerJob -ErrorAction SilentlyContinue
        }
    }
}

# Function to get URL input
function Get-UrlInput {
    Write-Host ""
    Write-Host "Enter URL to navigate to:" -ForegroundColor Yellow
    Write-Host "Examples:" -ForegroundColor DarkGray
    Write-Host "  • facebook.com/zuck" -ForegroundColor DarkGray
    Write-Host "  • facebook.com/marketplace" -ForegroundColor DarkGray
    Write-Host "  • https://www.facebook.com/groups/123456" -ForegroundColor DarkGray
    Write-Host "  • any-website.com/page" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "URL: " -NoNewline -ForegroundColor Cyan
    $inputUrl = Read-Host
    
    return $inputUrl
}

# Main execution
Show-Banner

# Find or use specified API server
$apiServer = Find-ApiServer -PreferredUrl $ApiUrl

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""

# Main loop
do {
    # Get URL from parameter or user input
    if ($Url) {
        $targetUrl = $Url
        $Url = "" # Clear for next iteration if in loop mode
    }
    else {
        $targetUrl = Get-UrlInput
    }
    
    # Check for exit commands
    if ($targetUrl -in @("exit", "quit", "q", "")) {
        if ($Loop) {
            Write-Host ""
            Write-Host "👋 Goodbye!" -ForegroundColor Yellow
            break
        }
        elseif ([string]::IsNullOrWhiteSpace($targetUrl)) {
            continue
        }
    }
    
    # Navigate to the URL
    $result = Navigate-ToUrl -TargetUrl $targetUrl -ApiServer $apiServer
    
    if ($Loop) {
        Write-Host ""
        Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "Press Enter to navigate to another URL, or type 'exit' to quit" -ForegroundColor Yellow
        $continue = Read-Host
        if ($continue -in @("exit", "quit", "q")) {
            Write-Host "👋 Goodbye!" -ForegroundColor Yellow
            break
        }
        Write-Host ""
        Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
    }
    
} while ($Loop)

Write-Host ""
Write-Host "✨ Done!" -ForegroundColor Green
Write-Host ""
