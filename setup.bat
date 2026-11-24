<# :
@echo off
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-Expression ([System.IO.File]::ReadAllText('%~f0'))"
exit /b
#>

# Pure PowerShell code starts here
Write-Host "Running from PowerShell inside a Batch file!" -ForegroundColor Green
Get-Date