@echo off
REM Simple batch file to run the navigation tool

if "%1"=="" (
    REM Interactive mode
    powershell -ExecutionPolicy Bypass -File navigate-url.ps1
) else if "%1"=="-loop" (
    REM Loop mode
    powershell -ExecutionPolicy Bypass -File navigate-url.ps1 -Loop
) else if "%1"=="-help" (
    REM Help
    powershell -ExecutionPolicy Bypass -File navigate-url.ps1 -Help
) else (
    REM URL provided
    powershell -ExecutionPolicy Bypass -File navigate-url.ps1 -Url "%1"
)
